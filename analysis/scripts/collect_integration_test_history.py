#!/usr/bin/env python3
"""Collect integration-test history from GitHub PR comments.

This script scans pull request comments posted by ``github-actions[bot]`` that
contain the ``<!-- integration-test-summary -->`` marker, parses the embedded
performance and file-descriptor markdown tables, and writes the results to the
CSV files under ``analysis/data/`` and regenerates the
``analysis/integration_test_results_history.rst`` report.

Agent notes
-----------
The comment body format is produced by the ``pr-summary`` job in
.github/workflows/integration_tests.yml.  Key structural markers::

    <!-- integration-test-summary -->
    ## Integration Test Results ...

    <details>...<summary>Performance Details...</summary>

    #### Multi Process Tests
    | Operation | Workers | Min (s) | Max (s) | Avg (s) | StdDev |
    | Bulkwalk  | 2       | 0.903   | ...

    #### Multi Thread Tests
    | Operation | Workers | Min (s) | ...

    </details>

    ### File Descriptor Tests: No leaks detected

    <details>...<summary>FD Test Details...</summary>
    | Session | Operation | Mode | FD Leak | Exec (s) | Avg/Call (s) |
    | V1      | bulk_get  | close | N/A    | 0.058   | 0.000580    |

    </details>

GitHub overwrites these comments in-place on every CI run, so older comment
bodies are permanently lost.  The CSVs in analysis/data/ are the authoritative
long-term record.

Deduplication key: (pr_number, comment updated_at ISO timestamp).
In --mode=append the script skips rows already present in overview.csv.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Iterable
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# ── Constants ─────────────────────────────────────────────────────────────────

COMMENT_MARKER = "<!-- integration-test-summary -->"
BOT_AUTHOR = "github-actions[bot]"
API_BASE = "https://api.github.com"

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
REPORT_RST = SCRIPT_DIR.parent / "integration_test_results_history.rst"

CSV_OVERVIEW = DATA_DIR / "integration_test_results_history_overview.csv"
CSV_RECENT_TMPL = "integration_test_results_history_recent_{n}.csv"
CSV_PERF_RAW = DATA_DIR / "integration_test_results_history_performance_raw.csv"
CSV_FD_RAW = DATA_DIR / "integration_test_results_history_fd_raw.csv"
CSV_FD_STATUS = DATA_DIR / "integration_test_results_history_fd_status.csv"
CSV_FD_SUMMARY = DATA_DIR / "integration_test_results_history_fd_summary.csv"
CSV_MP_SUMMARY = DATA_DIR / "integration_test_results_history_multi_process_tests_summary.csv"
CSV_MT_SUMMARY = DATA_DIR / "integration_test_results_history_multi_thread_tests_summary.csv"

# ── GitHub API helpers ────────────────────────────────────────────────────────


def _api_get(token: str, url: str) -> Any:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"******",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ezsnmp-integration-test-history",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {exc.code} for {url}\n{body}") from exc


def _iter_pull_requests(token: str, repository: str, max_prs: int) -> Iterable[dict]:
    """Yield PR dicts newest-first, stopping after max_prs."""
    fetched = 0
    page = 1
    while fetched < max_prs:
        params = urlencode(
            {"state": "all", "sort": "updated", "direction": "desc",
             "per_page": 100, "page": page}
        )
        prs = _api_get(token, f"{API_BASE}/repos/{repository}/pulls?{params}")
        if not isinstance(prs, list) or not prs:
            break
        for pr in prs:
            yield pr
            fetched += 1
            if fetched >= max_prs:
                return
        page += 1


def _iter_issue_comments(
    token: str, repository: str, issue_number: int
) -> Iterable[dict]:
    page = 1
    while True:
        params = urlencode({"per_page": 100, "page": page})
        comments = _api_get(
            token,
            f"{API_BASE}/repos/{repository}/issues/{issue_number}/comments?{params}",
        )
        if not isinstance(comments, list) or not comments:
            break
        yield from comments
        page += 1


# ── Comment parsing ───────────────────────────────────────────────────────────

# Matches a markdown pipe-table data row (not a separator row of dashes).
_TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")
_SEPARATOR_RE = re.compile(r"^\|[-| :]+\|$")
_PERF_HEADING_RE = re.compile(r"####\s+(Multi (?:Process|Thread) Tests)", re.IGNORECASE)
_FD_STATUS_RE = re.compile(r"File Descriptor Tests[^:]*:\s*(.+?)(?:\n|$)", re.IGNORECASE)


def _parse_table_rows(lines: list, start: int) -> tuple:
    """Parse a markdown table starting at or after *start*.

    Returns (list_of_data_rows, index_after_table).
    Each data row is a list of stripped cell strings.
    """
    rows: list = []
    i = start
    in_table = False
    while i < len(lines):
        line = lines[i].strip()
        if _SEPARATOR_RE.match(line):
            in_table = True
            i += 1
            continue
        m = _TABLE_ROW_RE.match(line)
        if m:
            if in_table:
                cells = [c.strip() for c in line.split("|")[1:-1]]
                rows.append(cells)
        elif in_table:
            break
        i += 1
    return rows, i


def _strip_emoji(text: str) -> str:
    """Remove non-ASCII emoji / icon characters from a string."""
    return re.sub(r"[^\x00-\x7F]+", "", text).strip()


def _parse_comment(comment_body: str) -> dict:
    """Parse an integration-test-summary comment body.

    Returns a dict with keys:
        performance: list of dicts with keys category, operation, workers,
                     min_seconds, max_seconds, avg_seconds, stddev_seconds
        fd_rows:     list of dicts with keys session, operation, mode, fd_leak,
                     fd_leak_numeric, exec_seconds, avg_per_call_seconds, fd_status
        fd_status:   str e.g. "No leaks detected" or "3 potential leak(s)"
    """
    lines = comment_body.splitlines()
    result: dict = {"performance": [], "fd_rows": [], "fd_status": "Unavailable"}
    current_category: str | None = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Performance section headings like "#### Multi Process Tests"
        hm = _PERF_HEADING_RE.search(line)
        if hm:
            current_category = hm.group(1).strip()
            i += 1
            continue

        # Performance table header row
        if current_category and "| Operation |" in line and "| Workers |" in line:
            data_rows, i = _parse_table_rows(lines, i + 1)
            for row in data_rows:
                if len(row) >= 6:
                    try:
                        stddev_raw = _strip_emoji(row[5])
                        stddev = float(stddev_raw) if stddev_raw not in ("N/A", "") else None
                        result["performance"].append({
                            "category": current_category,
                            "operation": row[0],
                            "workers": int(row[1]),
                            "min_seconds": float(row[2]),
                            "max_seconds": float(row[3]),
                            "avg_seconds": float(row[4]),
                            "stddev_seconds": stddev,
                        })
                    except (ValueError, IndexError):
                        pass
            continue

        # FD status line e.g. "### File Descriptor Tests: No leaks detected"
        fdm = _FD_STATUS_RE.search(line)
        if fdm and "File Descriptor Tests" in line:
            result["fd_status"] = fdm.group(1).strip()

        # FD table header row
        if "| Session |" in line and "| Operation |" in line and "| Mode |" in line:
            data_rows, i = _parse_table_rows(lines, i + 1)
            fd_status_str = result.get("fd_status", "Unavailable")
            for row in data_rows:
                if len(row) >= 6:
                    raw_leak = _strip_emoji(row[3]).strip()
                    try:
                        leak_numeric: float | str = float(
                            re.sub(r"[^0-9.+-]", "", raw_leak)
                        )
                    except ValueError:
                        leak_numeric = ""
                    try:
                        exec_s = float(row[4]) if row[4] not in ("-", "") else None
                    except ValueError:
                        exec_s = None
                    try:
                        avg_s = float(row[5]) if row[5] not in ("-", "") else None
                    except ValueError:
                        avg_s = None
                    result["fd_rows"].append({
                        "session": _strip_emoji(row[0]),
                        "operation": row[1],
                        "mode": row[2],
                        "fd_leak": row[3],
                        "fd_leak_numeric": leak_numeric,
                        "exec_seconds": exec_s,
                        "avg_per_call_seconds": avg_s,
                        "fd_status": fd_status_str,
                    })
            continue

        i += 1

    return result


# ── CSV helpers ───────────────────────────────────────────────────────────────


def _load_seen_keys(path: Path) -> set:
    """Return (pr_number, updated_at) pairs already in overview.csv."""
    if not path.exists():
        return set()
    seen: set = set()
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                seen.add((int(row["pr_number"]), row["updated_at"]))
            except (KeyError, ValueError):
                pass
    return seen


def _load_existing_rows(path: Path) -> list:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(path: Path, fieldnames: list, rows: list) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ── Aggregation ───────────────────────────────────────────────────────────────


def _build_perf_summary(perf_rows: list, category: str) -> list:
    """Aggregate raw performance rows for *category* across all PR runs."""
    grouped: dict = defaultdict(list)
    for row in perf_rows:
        if row.get("category") != category:
            continue
        try:
            key = (row["operation"], int(row["workers"]))
            grouped[key].append(float(row["avg_seconds"]))
        except (KeyError, ValueError):
            pass

    summary = []
    for (op, workers), vals in sorted(grouped.items(), key=lambda x: (x[0][0], x[0][1])):
        summary.append({
            "Operation": op,
            "Workers": workers,
            "Runs": len(vals),
            "Min (s)": round(min(vals), 3),
            "Max (s)": round(max(vals), 3),
            "Avg (s)": round(mean(vals), 3),
            "StdDev (s)": round(stdev(vals), 3) if len(vals) > 1 else 0.0,
        })
    return summary


def _build_fd_summary(fd_rows: list) -> list:
    """Aggregate FD raw rows across all PR runs."""
    grouped: dict = {}
    for row in fd_rows:
        key = (row.get("session", ""), row.get("operation", ""), row.get("mode", ""))
        if key not in grouped:
            grouped[key] = {
                "fd_leak_numeric": [],
                "exec_seconds": [],
                "avg_per_call_seconds": [],
                "leak_warnings": 0,
            }
        g = grouped[key]
        try:
            val = float(row["fd_leak_numeric"])
            g["fd_leak_numeric"].append(val)
            if val > 0:
                g["leak_warnings"] += 1
        except (TypeError, ValueError):
            pass
        try:
            if row.get("exec_seconds") not in (None, "", "None"):
                g["exec_seconds"].append(float(row["exec_seconds"]))
        except (ValueError, TypeError):
            pass
        try:
            if row.get("avg_per_call_seconds") not in (None, "", "None"):
                g["avg_per_call_seconds"].append(float(row["avg_per_call_seconds"]))
        except (ValueError, TypeError):
            pass

    summary = []
    for (sess, op, mode), g in sorted(grouped.items()):
        leak_vals = g["fd_leak_numeric"]
        summary.append({
            "Session": sess,
            "Operation": op,
            "Mode": mode,
            "Runs": max(len(g["exec_seconds"]), len(g["fd_leak_numeric"]), 1),
            "Leak warnings": g["leak_warnings"],
            "Mean FD leak": round(mean(leak_vals), 2) if leak_vals else "",
            "Avg Exec (s)": (
                round(mean(g["exec_seconds"]), 6) if g["exec_seconds"] else ""
            ),
            "Avg Avg/Call (s)": (
                round(mean(g["avg_per_call_seconds"]), 6)
                if g["avg_per_call_seconds"] else ""
            ),
        })
    return summary


def _build_fd_status(overview_rows: list) -> list:
    counts: dict = defaultdict(int)
    for row in overview_rows:
        counts[row.get("fd_status", "Unavailable")] += 1
    return [{"Status": s, "Count": c} for s, c in sorted(counts.items())]


# ── RST report ────────────────────────────────────────────────────────────────


def _write_rst(
    overview_rows: list,
    perf_rows: list,
    fd_rows: list,
    generated_at: str,
) -> None:
    total = len(overview_rows)
    if not overview_rows:
        newest = oldest = "N/A"
    else:
        dates = [r.get("updated_at", "") for r in overview_rows]
        newest = max(dates)
        oldest = min(dates)

    perf_comments = len({str(r.get("pr_number")) for r in perf_rows})
    fd_comments = len({str(r.get("pr_number")) for r in fd_rows})

    lines = [
        "Integration Test Results History",
        "================================",
        "",
        "This report aggregates every currently recoverable successful PR comment tagged with",
        "``<!-- integration-test-summary -->``.",
        "",
        f"**Report generated:** ``{generated_at}``",
        "",
        "Notes",
        "-----",
        "",
        "* GitHub updates these PR comments in place, so older successful run bodies are overwritten.",
        f"* Accessible successful comment summaries found: ``{total}``.",
        "* ``Unavailable`` in the status CSV means the older comment body did not expose a"
        " file-descriptor status line.",
        "",
        "Dataset",
        "-------",
        "",
        f"* Comments analyzed: ``{total}``",
        f"* Newest PR update in sample: ``{newest}``",
        f"* Oldest PR update in sample: ``{oldest}``",
        f"* Performance rows parsed: ``{len(perf_rows)}``"
        f" ({perf_comments} comments with tabular performance data)",
        f"* File descriptor rows parsed: ``{len(fd_rows)}``"
        f" ({fd_comments} comments with tabular FD data)",
        "",
        "CSV files",
        "---------",
        "",
        "All CSV data files live under the ``data/`` sub-folder next to this report.",
        "",
        "* ``data/integration_test_results_history_overview.csv`` -- **complete** set: every"
        " recoverable",
        "  source comment found at report-generation time.  This is the",
        "  canonical record; append new rows here on every future update.",
        "* ``data/integration_test_results_history_recent_20.csv`` -- **convenience subset**:"
        " a fixed",
        "  window of the newest 20 entries, sliced from the overview at report-generation time.  The",
        "  number ``20`` is an arbitrary display cap, not a batch size.  If all recoverable"
        " comments fit",
        "  in 20 rows this file is smaller than the overview; once the dataset exceeds 20 entries"
        " these",
        "  files will diverge.  Regenerate this slice from the overview whenever a new batch is added.",
        "* ``data/integration_test_results_history_performance_raw.csv`` -- every parsed"
        " performance row",
        "* ``data/integration_test_results_history_fd_raw.csv`` -- every parsed file-descriptor row",
        "* ``data/integration_test_results_history_fd_status.csv`` -- file-descriptor status counts",
        "* ``data/integration_test_results_history_fd_summary.csv`` -- aggregated"
        " file-descriptor metrics",
        "* ``data/integration_test_results_history_multi_process_tests_summary.csv`` -- aggregated"
        " multi process tests performance metrics",
        "* ``data/integration_test_results_history_multi_thread_tests_summary.csv`` -- aggregated"
        " multi thread tests performance metrics",
        "",
        "Future Results",
        "--------------",
        "",
        "New integration-test runs should **append** rows to the existing CSVs in ``data/`` rather than",
        "regenerating from the full PR history.  This keeps the dataset growing incrementally and avoids",
        "re-fetching comment history that GitHub may have already overwritten.  To add a new result set:",
        "",
        "1. Run the analysis script against the latest PR comments.",
        "2. Append new rows (deduplicated by PR number / timestamp) to the relevant CSV files in ``data/``.",
        "3. Regenerate this ``.rst`` file with an updated **Report generated** timestamp and updated"
        " Dataset counts.",
        "4. Commit both the updated CSVs and the updated ``.rst`` to the ``analysis/`` folder.",
        "",
        "See ``analysis/scripts/README.rst`` for full script usage.",
        "",
        "Performance Details",
        "-------------------",
        "",
        "Multi Process Tests",
        "^^^^^^^^^^^^^^^^^^^",
        "",
        ".. csv-table:: Historical aggregate for multi process tests",
        "   :file: data/integration_test_results_history_multi_process_tests_summary.csv",
        "   :header-rows: 1",
        "",
        "Multi Thread Tests",
        "^^^^^^^^^^^^^^^^^^",
        "",
        ".. csv-table:: Historical aggregate for multi thread tests",
        "   :file: data/integration_test_results_history_multi_thread_tests_summary.csv",
        "   :header-rows: 1",
        "",
        "File Descriptor Tests",
        "---------------------",
        "",
        ".. csv-table:: File descriptor status counts",
        "   :file: data/integration_test_results_history_fd_status.csv",
        "   :header-rows: 1",
        "",
        ".. csv-table:: Aggregated file descriptor metrics",
        "   :file: data/integration_test_results_history_fd_summary.csv",
        "   :header-rows: 1",
        "",
        "Recent Successful Results",
        "-------------------------",
        "",
        ".. csv-table:: The newest 20 successful integration-test summary comments in the recoverable"
        " sample",
        "   :file: data/integration_test_results_history_recent_20.csv",
        "   :header-rows: 1",
        "",
    ]
    REPORT_RST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"RST report written to {REPORT_RST}")


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect integration-test history from GitHub PR comments."
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN", ""),
        help="GitHub personal access token (default: $GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", "carlkidcrypto/ezsnmp"),
        help="owner/repo (default: $GITHUB_REPOSITORY or carlkidcrypto/ezsnmp)",
    )
    parser.add_argument(
        "--max-prs",
        type=int,
        default=int(os.environ.get("MAX_PRS", "500")),
        help="Maximum number of PRs to scan newest-first (default: 500)",
    )
    parser.add_argument(
        "--mode",
        choices=["full", "append"],
        default="append",
        help=(
            "full: re-scan all PRs and overwrite CSVs from scratch. "
            "append: skip (pr_number, updated_at) pairs already in overview.csv (default: append)"
        ),
    )
    parser.add_argument(
        "--recent-n",
        type=int,
        default=20,
        help="Number of most-recent entries to include in the recent_N slice CSV (default: 20)",
    )
    parser.add_argument(
        "--no-rst",
        action="store_true",
        help="Skip regenerating the RST report",
    )
    args = parser.parse_args()

    if not args.token:
        print("ERROR: --token or $GITHUB_TOKEN is required", file=sys.stderr)
        return 2

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # In append mode load keys already present in overview.csv
    seen_keys: set = set()
    if args.mode == "append":
        seen_keys = _load_seen_keys(CSV_OVERVIEW)
        print(
            f"Append mode: {len(seen_keys)} rows already in overview.csv will be skipped"
        )

    new_overview: list = []
    new_perf: list = []
    new_fd: list = []
    pr_count = 0
    comment_count = 0

    for pr in _iter_pull_requests(args.token, args.repo, max_prs=args.max_prs):
        pr_number = pr["number"]
        pr_title = pr.get("title", "")
        pr_url = pr.get("html_url", "")
        pr_count += 1

        for comment in _iter_issue_comments(args.token, args.repo, pr_number):
            author = ((comment.get("user") or {}).get("login") or "").strip()
            body = comment.get("body", "") or ""
            if author != BOT_AUTHOR:
                continue
            if COMMENT_MARKER not in body:
                continue

            updated_at = comment.get("updated_at") or comment.get("created_at") or ""
            key = (pr_number, updated_at)
            if key in seen_keys:
                continue

            comment_url = comment.get("html_url", "")
            parsed = _parse_comment(body)
            fd_status = parsed.get("fd_status", "Unavailable")
            perf = parsed.get("performance", [])
            fd_rows_parsed = parsed.get("fd_rows", [])

            new_overview.append({
                "pr_number": pr_number,
                "pr_title": pr_title,
                "pr_url": pr_url,
                "comment_url": comment_url,
                "updated_at": updated_at,
                "performance_rows": len(perf),
                "fd_rows": len(fd_rows_parsed),
                "fd_status": fd_status,
            })

            for p in perf:
                new_perf.append({
                    "pr_number": pr_number,
                    "pr_title": pr_title,
                    "pr_url": pr_url,
                    "comment_url": comment_url,
                    "updated_at": updated_at,
                    **p,
                })

            for f in fd_rows_parsed:
                new_fd.append({
                    "pr_number": pr_number,
                    "pr_title": pr_title,
                    "pr_url": pr_url,
                    "comment_url": comment_url,
                    "updated_at": updated_at,
                    **f,
                })

            seen_keys.add(key)
            comment_count += 1

    print(f"Scanned {pr_count} PRs, found {comment_count} new integration-test comments")

    if not new_overview and args.mode == "append":
        print("No new data -- CSVs are already up to date")
        return 0

    # ── Combine existing + new ─────────────────────────────────────────────────
    if args.mode == "full":
        all_overview = new_overview
        all_perf = new_perf
        all_fd = new_fd
    else:
        all_overview = _load_existing_rows(CSV_OVERVIEW) + new_overview
        all_perf = _load_existing_rows(CSV_PERF_RAW) + new_perf
        all_fd = _load_existing_rows(CSV_FD_RAW) + new_fd

    # Sort overview newest-first and (re-)assign ranks
    all_overview.sort(key=lambda r: r.get("updated_at", ""), reverse=True)
    for i, row in enumerate(all_overview, 1):
        row["rank"] = i

    # ── Write CSVs ────────────────────────────────────────────────────────────
    overview_fields = [
        "rank", "pr_number", "pr_title", "pr_url", "comment_url",
        "updated_at", "performance_rows", "fd_rows", "fd_status",
    ]
    _write_csv(CSV_OVERVIEW, overview_fields, all_overview)
    print(f"Written: {CSV_OVERVIEW} ({len(all_overview)} rows)")

    recent_path = DATA_DIR / CSV_RECENT_TMPL.format(n=args.recent_n)
    _write_csv(recent_path, overview_fields, all_overview[: args.recent_n])
    print(
        f"Written: {recent_path}"
        f" ({min(len(all_overview), args.recent_n)} rows,"
        f" newest-{args.recent_n} slice)"
    )

    perf_fields = [
        "pr_number", "pr_title", "pr_url", "comment_url", "updated_at",
        "category", "operation", "workers", "min_seconds", "max_seconds",
        "avg_seconds", "stddev_seconds",
    ]
    _write_csv(CSV_PERF_RAW, perf_fields, all_perf)
    print(f"Written: {CSV_PERF_RAW} ({len(all_perf)} rows)")

    fd_fields = [
        "pr_number", "pr_title", "pr_url", "comment_url", "updated_at",
        "session", "operation", "mode", "fd_leak", "fd_leak_numeric",
        "exec_seconds", "avg_per_call_seconds", "fd_status",
    ]
    _write_csv(CSV_FD_RAW, fd_fields, all_fd)
    print(f"Written: {CSV_FD_RAW} ({len(all_fd)} rows)")

    _write_csv(CSV_FD_STATUS, ["Status", "Count"], _build_fd_status(all_overview))
    print(f"Written: {CSV_FD_STATUS}")

    _write_csv(
        CSV_FD_SUMMARY,
        [
            "Session", "Operation", "Mode", "Runs", "Leak warnings",
            "Mean FD leak", "Avg Exec (s)", "Avg Avg/Call (s)",
        ],
        _build_fd_summary(all_fd),
    )
    print(f"Written: {CSV_FD_SUMMARY}")

    perf_summary_fields = [
        "Operation", "Workers", "Runs", "Min (s)", "Max (s)", "Avg (s)", "StdDev (s)",
    ]
    _write_csv(
        CSV_MP_SUMMARY,
        perf_summary_fields,
        _build_perf_summary(all_perf, "Multi Process Tests"),
    )
    print(f"Written: {CSV_MP_SUMMARY}")

    _write_csv(
        CSV_MT_SUMMARY,
        perf_summary_fields,
        _build_perf_summary(all_perf, "Multi Thread Tests"),
    )
    print(f"Written: {CSV_MT_SUMMARY}")

    if not args.no_rst:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        _write_rst(all_overview, all_perf, all_fd, generated_at)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
