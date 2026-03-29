#!/usr/bin/env python3
"""Analyze historical Valgrind PR comments and flag likely memory leaks.

This script scans pull request comments created by `github-actions[bot]` that
contain the ezsnmp Homebrew Valgrind report marker, extracts leak-related
metrics, and writes both markdown and JSON summaries.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE = "https://api.github.com"
COMMENT_MARKER = "<!-- ezsnmp-homebrew-valgrind -->"

LEAK_PATTERNS = {
    "definitely": re.compile(r"definitely\s+lost:\s*([0-9,]+)\s+bytes", re.IGNORECASE),
    "indirectly": re.compile(r"indirectly\s+lost:\s*([0-9,]+)\s+bytes", re.IGNORECASE),
    "possibly": re.compile(r"possibly\s+lost:\s*([0-9,]+)\s+bytes", re.IGNORECASE),
}

ROW_PATTERN = re.compile(
    r"^\|\s*(3\.\d{2,})\s*\|\s*([^\n]*?)\s*\|\s*ubuntu-latest\s*\|$",
    re.MULTILINE,
)


@dataclass
class LeakRecord:
    pr_number: int
    pr_url: str
    pr_updated_at: str
    comment_url: str
    python_version: str
    definitely_lost_bytes: int
    indirectly_lost_bytes: int
    possibly_lost_bytes: int
    evidence_excerpt: str

    @property
    def has_leak(self) -> bool:
        return any(
            value > 0
            for value in (
                self.definitely_lost_bytes,
                self.indirectly_lost_bytes,
                self.possibly_lost_bytes,
            )
        )


def _parse_iso8601(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _to_int(raw: str | None) -> int:
    if not raw:
        return 0
    return int(raw.replace(",", ""))


def _api_get(token: str, url: str) -> Any:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ezsnmp-valgrind-history-agent",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API call failed ({exc.code}) for {url}\n{body}"
        ) from exc


def _iter_pull_requests(token: str, repository: str, max_prs: int) -> Iterable[dict]:
    fetched = 0
    page = 1
    while fetched < max_prs:
        params = urlencode(
            {
                "state": "all",
                "sort": "updated",
                "direction": "desc",
                "per_page": 100,
                "page": page,
            }
        )
        url = f"{API_BASE}/repos/{repository}/pulls?{params}"
        prs = _api_get(token, url)
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
        url = f"{API_BASE}/repos/{repository}/issues/{issue_number}/comments?{params}"
        comments = _api_get(token, url)
        if not isinstance(comments, list) or not comments:
            break
        for comment in comments:
            yield comment
        page += 1


def _extract_records(pr: dict, comment: dict) -> list[LeakRecord]:
    body = comment.get("body", "") or ""
    records: list[LeakRecord] = []

    for match in ROW_PATTERN.finditer(body):
        py_ver = match.group(1)
        row_text = match.group(2)

        definite = _to_int(_find_match("definitely", row_text))
        indirect = _to_int(_find_match("indirectly", row_text))
        possible = _to_int(_find_match("possibly", row_text))

        excerpt = re.sub(r"\s+", " ", row_text).strip()
        if len(excerpt) > 200:
            excerpt = f"{excerpt[:197]}..."

        records.append(
            LeakRecord(
                pr_number=pr["number"],
                pr_url=pr["html_url"],
                pr_updated_at=pr["updated_at"],
                comment_url=comment["html_url"],
                python_version=py_ver,
                definitely_lost_bytes=definite,
                indirectly_lost_bytes=indirect,
                possibly_lost_bytes=possible,
                evidence_excerpt=excerpt,
            )
        )

    return records


def _find_match(kind: str, text: str) -> str | None:
    pattern = LEAK_PATTERNS[kind]
    match = pattern.search(text)
    return match.group(1) if match else None


def _format_fix_suggestions(records: list[LeakRecord]) -> list[str]:
    has_definite = any(r.definitely_lost_bytes > 0 for r in records)
    has_indirect = any(r.indirectly_lost_bytes > 0 for r in records)
    has_possible = any(r.possibly_lost_bytes > 0 for r in records)

    suggestions: list[str] = []
    if has_definite:
        suggestions.append(
            "Trace allocation/free pairs in the C++ extension boundary. Focus on missing `free`/`delete` and Python reference count balancing (`Py_INCREF` vs `Py_DECREF`)."
        )
    if has_indirect:
        suggestions.append(
            "Inspect object ownership trees: indirectly lost bytes usually indicate parent allocations were leaked. Add RAII wrappers or smart pointers for nested allocations."
        )
    if has_possible:
        suggestions.append(
            "Review pointer arithmetic and buffer lifetime handling. Possibly lost bytes often come from shifted pointers or overwritten base pointers before deallocation."
        )

    if not suggestions:
        suggestions.append("No actionable leak signatures found in analyzed comments.")
    return suggestions


def _build_markdown(
    repository: str,
    analyzed_prs: int,
    analyzed_comments: int,
    leak_records: list[LeakRecord],
    since: datetime,
) -> str:
    lines = [
        "# Valgrind PR History Report",
        "",
        f"Repository: `{repository}`",
        f"Lookback window started: `{since.isoformat()}`",
        f"PRs analyzed: `{analyzed_prs}`",
        f"Valgrind bot comments analyzed: `{analyzed_comments}`",
        "",
    ]

    if leak_records:
        lines.append("## Result")
        lines.append("")
        lines.append(
            "Potential memory leaks were detected in historical PR Valgrind comments."
        )
        lines.append("")

        lines.append("## Leaks Found")
        lines.append("")
        lines.append("| PR | Python | Definite | Indirect | Possible | Evidence |")
        lines.append("| --- | --- | ---: | ---: | ---: | --- |")
        for record in leak_records:
            lines.append(
                "| "
                f"#{record.pr_number} ({record.pr_url}) | "
                f"{record.python_version} | "
                f"{record.definitely_lost_bytes} | "
                f"{record.indirectly_lost_bytes} | "
                f"{record.possibly_lost_bytes} | "
                f"{record.evidence_excerpt} |"
            )

        lines.append("")
        lines.append("## Suggested Fixes")
        lines.append("")
        for item in _format_fix_suggestions(leak_records):
            lines.append(f"- {item}")
    else:
        lines.append("## Result")
        lines.append("")
        lines.append(
            "No leak signatures were found in the analyzed historical Valgrind PR comments."
        )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "- This report only analyzes `github-actions[bot]` comments containing the Homebrew Valgrind marker."
    )
    lines.append(
        "- Leak detection is based on non-zero `definitely lost`, `indirectly lost`, or `possibly lost` bytes."
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    repository = os.getenv("GITHUB_REPOSITORY", "").strip()
    max_prs = int(os.getenv("MAX_PRS", "1000"))
    lookback_days = int(os.getenv("LOOKBACK_DAYS", "0"))

    if not token:
        print("Missing GITHUB_TOKEN", file=sys.stderr)
        return 2
    if not repository:
        print("Missing GITHUB_REPOSITORY", file=sys.stderr)
        return 2

    since = (
        datetime.now(timezone.utc) - timedelta(days=lookback_days)
        if lookback_days > 0
        else datetime.min.replace(tzinfo=timezone.utc)
    )

    analyzed_prs = 0
    analyzed_comments = 0
    all_records: list[LeakRecord] = []

    for pr in _iter_pull_requests(token, repository, max_prs=max_prs):
        updated_at = _parse_iso8601(pr["updated_at"])
        if lookback_days > 0 and updated_at < since:
            continue

        analyzed_prs += 1
        issue_number = pr["number"]

        for comment in _iter_issue_comments(
            token, repository, issue_number=issue_number
        ):
            author = ((comment.get("user") or {}).get("login") or "").strip()
            body = comment.get("body", "") or ""
            if author != "github-actions[bot]":
                continue
            if COMMENT_MARKER not in body:
                continue

            analyzed_comments += 1
            all_records.extend(_extract_records(pr, comment))

    leak_records = [record for record in all_records if record.has_leak]

    markdown_report = _build_markdown(
        repository=repository,
        analyzed_prs=analyzed_prs,
        analyzed_comments=analyzed_comments,
        leak_records=leak_records,
        since=since,
    )

    report_path = Path("valgrind-pr-history-report.md")
    report_path.write_text(markdown_report, encoding="utf-8")

    json_path = Path("valgrind-pr-history-report.json")
    json_path.write_text(
        json.dumps(
            {
                "repository": repository,
                "analyzed_prs": analyzed_prs,
                "analyzed_comments": analyzed_comments,
                "lookback_days": lookback_days,
                "leak_records": [asdict(record) for record in leak_records],
                "suggested_fixes": _format_fix_suggestions(leak_records),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(markdown_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
