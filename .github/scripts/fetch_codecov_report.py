#!/usr/bin/env python3
"""Fetch Codecov coverage data for this repository and write an agent-friendly summary.

Runs as a pre-agent workflow step (outside the agent firewall) so agentic coverage
workflows can use real Codecov data without needing network access to Codecov.

Outputs (default directory: /tmp/gh-aw/agent/codecov):
  summary.md            Human/agent readable summary of totals and uncovered lines
  report.json, report-<flag>.json, report-component-<id>.json
                        Raw Codecov report API responses

Environment variables:
  GITHUB_REPOSITORY   owner/repo (required)
  CODECOV_BRANCH      Branch to query (default: main)
  CODECOV_FLAGS       Comma-separated flags to query. Default: all flags reported by Codecov.
  CODECOV_API_TOKEN   Optional Codecov API token (only needed for private repositories)
  CODECOV_OUTPUT_DIR  Output directory override

This script never fails the workflow: on any error it writes a summary describing the
problem and exits 0 so the agent can fall back to static analysis.

If a flag or component has no line data on the latest branch commit (for example because
its tests were skipped and Codecov carryforward did not apply), the newest recent commit
that does have line data is used instead and the summary says so.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.codecov.io/api/v2/github"
MAX_FILES = 60
MAX_LOOKBACK = 30


def api_get(url, token):
    headers = {"Accept": "application/json", "User-Agent": "gh-aw-codecov-fetch"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def compress_lines(lines):
    """Turn [1, 2, 3, 7, 9, 10] into '1-3, 7, 9-10'."""
    if not lines:
        return ""
    lines = sorted(lines)
    ranges = []
    start = prev = lines[0]
    for n in lines[1:]:
        if n == prev + 1:
            prev = n
            continue
        ranges.append(f"{start}-{prev}" if start != prev else f"{start}")
        start = prev = n
    ranges.append(f"{start}-{prev}" if start != prev else f"{start}")
    return ", ".join(ranges)


def summarize_report(report, label):
    totals = report.get("totals") or {}
    out = [f"### {label}", ""]
    out.append(
        f"- Overall coverage: **{totals.get('coverage', 'n/a')}%** "
        f"(lines={totals.get('lines', 'n/a')}, hits={totals.get('hits', 'n/a')}, "
        f"misses={totals.get('misses', 'n/a')}, partials={totals.get('partials', 'n/a')})"
    )
    commit = report.get("commit_file_url") or ""
    if commit:
        out.append(f"- Codecov commit view: {commit}")
    out.append("")

    gaps = []
    for f in report.get("files") or []:
        ftotals = f.get("totals") or {}
        if not ftotals.get("lines"):
            continue
        misses = [
            lc[0] for lc in f.get("line_coverage") or [] if len(lc) > 1 and lc[1] == 1
        ]
        partials = [
            lc[0] for lc in f.get("line_coverage") or [] if len(lc) > 1 and lc[1] == 2
        ]
        if not misses and not partials:
            continue
        gaps.append((f.get("name"), ftotals.get("coverage"), misses, partials))

    if not gaps:
        out.append("No files with missed or partial lines for this scope.")
        out.append("")
        return out

    gaps.sort(key=lambda g: (-(len(g[2]) + len(g[3])), g[0] or ""))
    out.append("| File | Coverage | Missed lines | Partial lines |")
    out.append("|---|---|---|---|")
    for name, cov, misses, partials in gaps[:MAX_FILES]:
        out.append(
            f"| `{name}` | {cov}% | {compress_lines(misses) or '-'} | {compress_lines(partials) or '-'} |"
        )
    if len(gaps) > MAX_FILES:
        out.append(f"| ... {len(gaps) - MAX_FILES} more files truncated | | | |")
    out.append("")
    return out


def has_line_data(report):
    """True if the report contains at least one file with measured lines."""
    for f in report.get("files") or []:
        if (f.get("totals") or {}).get("lines"):
            return True
    return False


def list_names(repo_url, endpoint, key, token, branch, notes):
    try:
        params = urllib.parse.urlencode({"branch": branch, "page_size": 100})
        data = api_get(f"{repo_url}/{endpoint}/?{params}", token)
    except Exception as exc:  # noqa: BLE001
        notes.append(f"Note: could not list Codecov {endpoint} ({exc}).")
        return []
    items = data.get("results") if isinstance(data, dict) else data
    return [i.get(key) for i in items or [] if i.get(key)]


def fetch_scope(repo_url, token, branch, scope_params, commits):
    """Fetch a report for the branch head; if it has no line data (e.g. the flag was not
    uploaded on the latest commit and carryforward did not apply), walk back through
    recent commits and return the newest report that has line data.

    Returns (report, sha_or_None, error_or_None).
    """
    params = {"branch": branch, **scope_params}
    url = f"{repo_url}/report/?{urllib.parse.urlencode(params)}"
    try:
        report = api_get(url, token)
    except urllib.error.HTTPError as exc:
        return None, None, f"Codecov API returned HTTP {exc.code} for {url}"
    except Exception as exc:  # noqa: BLE001
        return None, None, f"Codecov API request failed: {exc}"
    if has_line_data(report):
        return report, None, None

    for commit in commits[1 : MAX_LOOKBACK + 1]:
        sha = commit.get("commitid")
        if not sha:
            continue
        params = {"sha": sha, **scope_params}
        try:
            older = api_get(
                f"{repo_url}/report/?{urllib.parse.urlencode(params)}", token
            )
        except Exception:  # noqa: BLE001
            continue
        if has_line_data(older):
            return older, commit, None
    return report, None, None


def main():
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    branch = os.environ.get("CODECOV_BRANCH", "main")
    token = os.environ.get("CODECOV_API_TOKEN", "").strip()
    out_dir = os.environ.get("CODECOV_OUTPUT_DIR", "/tmp/gh-aw/agent/codecov")
    os.makedirs(out_dir, exist_ok=True)
    summary_path = os.path.join(out_dir, "summary.md")

    lines = [
        "# Codecov Coverage Report",
        "",
        f"- Repository: `{repo}`",
        f"- Branch: `{branch}`",
        f"- Dashboard: https://app.codecov.io/gh/{repo}/tree/{branch}",
        "- Line numbers refer to the file as of the commit noted for each section "
        "(the latest Codecov-processed commit on the branch unless stated otherwise).",
        "",
    ]

    if "/" not in repo:
        lines.append("ERROR: GITHUB_REPOSITORY is not set; could not query Codecov.")
        with open(summary_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        print("\n".join(lines))
        return 0

    owner, name = repo.split("/", 1)
    repo_url = (
        f"{API_BASE}/{urllib.parse.quote(owner)}/repos/{urllib.parse.quote(name)}"
    )
    notes = []

    flags_env = os.environ.get("CODECOV_FLAGS", "").strip()
    if flags_env:
        flags = [f.strip() for f in flags_env.split(",") if f.strip()]
    else:
        flags = list_names(repo_url, "flags", "flag_name", token, branch, notes)
    components = list_names(
        repo_url, "components", "component_id", token, branch, notes
    )

    commits = []
    try:
        params = urllib.parse.urlencode(
            {"branch": branch, "page_size": MAX_LOOKBACK + 1}
        )
        commits = api_get(f"{repo_url}/commits/?{params}", token).get("results") or []
    except Exception as exc:  # noqa: BLE001
        notes.append(
            f"Note: could not list recent commits ({exc}); no fallback lookup."
        )
    if notes:
        lines += notes + [""]

    scopes = [({}, "All flags (combined)", "report.json")]
    scopes += [
        ({"component_id": c}, f"Component `{c}`", f"report-component-{c}.json")
        for c in components
    ]
    scopes += [({"flag": f}, f"Flag `{f}`", f"report-{f}.json") for f in flags]

    success = False
    for scope_params, label, raw_name in scopes:
        report, fallback, error = fetch_scope(
            repo_url, token, branch, scope_params, commits
        )
        if error:
            lines += [f"### {label}", "", error, ""]
            continue
        success = True
        with open(os.path.join(out_dir, raw_name), "w", encoding="utf-8") as fh:
            json.dump(report, fh)
        section = summarize_report(report, label)
        if fallback:
            section.insert(
                2,
                f"- NOTE: the latest commit on `{branch}` has no line data for this scope, "
                f"so this section uses commit `{fallback.get('commitid', '')[:12]}` "
                f"({(fallback.get('timestamp') or '')[:10]}), the newest commit that has it. "
                "Line numbers refer to that commit; re-check them against the current source.",
            )
        elif not has_line_data(report):
            section.insert(
                2,
                f"- NOTE: no line data found for this scope in the last {MAX_LOOKBACK} "
                "commits; fall back to static gap analysis for it.",
            )
        lines += section

    if not success:
        lines.append(
            "Codecov data is unavailable for this repository. Fall back to local coverage "
            "runs or static gap analysis."
        )

    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"fetch_codecov_report: unexpected error: {exc}")
        sys.exit(0)
