#!/usr/bin/env python3
"""Audit ezsnmp documentation for common issues.

This script scans documentation files (*.rst) and Python docstrings under
``ezsnmp/`` for a set of known issues:

- References to ``datatypes.py`` (does not exist; the Python-accessible
  datatypes come from the SWIG-generated ``datatypes.i`` interface).
- References to ``bulkwalk()`` instead of the correct ``bulk_walk()``.
- References to ``bulkget()`` instead of the correct ``bulk_get()``.
- References to ``getnext()`` instead of the correct ``get_next()``.

The script prints a summary of issues found, with file and line information, and
exits with a non-zero status code if any issues are detected so it can be used
in CI pipelines.

Usage::

    python3 .github/scripts/audit_docs.py [--fix]

Options:
    --fix   Attempt to automatically fix the issues in-place (uses simple
            string replacement; review changes before committing).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ── Repository root ────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]

# ── Patterns to check ─────────────────────────────────────────────────────────

# Each entry: (description, regex_pattern, suggested_replacement_or_None)
CHECKS: list[tuple[str, re.Pattern[str], str | None]] = [
    (
        "Reference to non-existent 'datatypes.py'",
        re.compile(r"\bdatatypes\.py\b"),
        "datatypes.i",
    ),
    (
        "Incorrect method name 'bulkwalk()' (should be 'bulk_walk()')",
        re.compile(r"\bbulkwalk\(\)"),
        "bulk_walk()",
    ),
    (
        "Incorrect method name 'bulkget()' (should be 'bulk_get()')",
        re.compile(r"\bbulkget\(\)"),
        "bulk_get()",
    ),
    (
        "Incorrect method name 'getnext()' (should be 'get_next()')",
        re.compile(r"\bgetnext\(\)"),
        "get_next()",
    ),
]

# ── File discovery ─────────────────────────────────────────────────────────────


def collect_files() -> list[Path]:
    """Return all documentation and Python source files to audit.

    :return: Sorted list of Path objects to audit.
    :rtype: list[Path]
    """
    patterns = [
        "**/*.rst",
        "ezsnmp/**/*.py",
        ".github/scripts/*.py",
    ]
    # This script is excluded to avoid false positives from its own pattern strings.
    this_script = Path(__file__).resolve()
    files: set[Path] = set()
    for pattern in patterns:
        for path in REPO_ROOT.glob(pattern):
            # Skip generated/vendored directories and this script itself.
            if path.resolve() == this_script:
                continue
            parts = path.parts
            if any(
                p in parts
                for p in ("__pycache__", ".git", "docs", "doxygen_docs_build")
            ):
                continue
            files.add(path)
    return sorted(files)


# ── Audit logic ───────────────────────────────────────────────────────────────


def audit_file(path: Path) -> list[tuple[int, str, str, str | None]]:
    """Audit a single file for documentation issues.

    :param path: Path to the file to audit.
    :type path: Path
    :return: List of ``(line_number, description, matched_text, replacement)``
             tuples for each issue found.
    :rtype: list[tuple[int, str, str, str | None]]
    """
    issues: list[tuple[int, str, str, str | None]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return issues

    for lineno, line in enumerate(text.splitlines(), start=1):
        for description, pattern, replacement in CHECKS:
            match = pattern.search(line)
            if match:
                issues.append((lineno, description, match.group(), replacement))
    return issues


def fix_file(path: Path) -> int:
    """Apply automatic fixes to a file in-place.

    Only issues with a defined replacement string are fixed.

    :param path: Path to the file to fix.
    :type path: Path
    :return: Number of replacements made.
    :rtype: int
    """
    try:
        original = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0

    updated = original
    count = 0
    for _description, pattern, replacement in CHECKS:
        if replacement is None:
            continue
        new_text, n = pattern.subn(replacement, updated)
        updated = new_text
        count += n

    if count:
        path.write_text(updated, encoding="utf-8")
    return count


# ── Entry point ───────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    """Run the documentation audit.

    :param argv: Argument list (defaults to ``sys.argv[1:]``).
    :type argv: list[str] or None
    :return: Exit code: 0 if no issues found, 1 otherwise.
    :rtype: int
    """
    parser = argparse.ArgumentParser(
        description="Audit ezsnmp documentation for common issues."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues in-place where a replacement is defined.",
    )
    args = parser.parse_args(argv)

    files = collect_files()
    total_issues = 0

    for path in files:
        if args.fix:
            n = fix_file(path)
            if n:
                rel = path.relative_to(REPO_ROOT)
                print(f"  FIXED {n} issue(s) in {rel}")
        else:
            issues = audit_file(path)
            if issues:
                rel = path.relative_to(REPO_ROOT)
                print(f"\n{rel}:")
                for lineno, description, matched, replacement in issues:
                    suggestion = f" → replace with '{replacement}'" if replacement else ""
                    print(f"  Line {lineno:4d}: {description}{suggestion}")
                    print(f"             found: {matched!r}")
                total_issues += len(issues)

    if not args.fix:
        if total_issues:
            print(f"\n{total_issues} issue(s) found. Run with --fix to auto-correct.")
            return 1
        else:
            print("No documentation issues found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
