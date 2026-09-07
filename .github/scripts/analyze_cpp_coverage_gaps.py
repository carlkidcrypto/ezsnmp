#!/usr/bin/env python3
"""Analyze C++ source files to identify potential coverage gaps.

This script performs static analysis of C++ source and test files to surface
branch patterns (if/else, switch/case, throw) that may lack corresponding test
coverage. It also cross-references existing shim test files against the known
shim map in meson.build to detect missing shim combinations.

Usage:
    python3 .github/scripts/analyze_cpp_coverage_gaps.py [--repo-root PATH]

Output is written to stdout in a human-readable report format.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class BranchInfo(NamedTuple):
    """Holds information about a conditional branch detected in a source file."""

    file: str
    line: int
    kind: str  # "if", "else", "switch", "case", "throw", "return"
    snippet: str  # first 80 chars of the line


class ShimGap(NamedTuple):
    """Describes a missing shim test combination."""

    operation: str
    suffix: str
    expected_file: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BRANCH_PATTERN = re.compile(
    r"""
    ^\s*                             # optional leading whitespace
    (?:
        (?P<if>if\s*\()              # if (
      | (?P<else>}\s*else\b)        # } else
      | (?P<switch>switch\s*\()     # switch (
      | (?P<case>case\s+\S)         # case <label>
      | (?P<throw>throw\s+\S)       # throw <expr>
    )
    """,
    re.VERBOSE,
)


def _find_branches(source_path: Path) -> list[BranchInfo]:
    """Return a list of branch-like statements found in *source_path*."""
    results: list[BranchInfo] = []
    try:
        lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return results

    for lineno, line in enumerate(lines, start=1):
        m = BRANCH_PATTERN.match(line)
        if m is None:
            continue
        kind = next(k for k, v in m.groupdict().items() if v is not None)
        results.append(BranchInfo(str(source_path), lineno, kind, line.strip()[:80]))
    return results


def _count_tests_for(test_file: Path) -> int:
    """Return the number of TEST / TEST_F / TEST_P macros in *test_file*."""
    if not test_file.exists():
        return 0
    text = test_file.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r"\bTEST(?:_F|_P)?\s*\(", text))


def _shim_test_path(cpp_tests_dir: Path, operation: str, suffix: str) -> Path:
    """Return expected path for a shim test file."""
    return cpp_tests_dir / f"test_{operation}{suffix}_shim.cpp"


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------


def analyze_source_branches(src_files: list[Path]) -> dict[str, list[BranchInfo]]:
    """Map each source file path to its detected branch list."""
    return {str(f): _find_branches(f) for f in src_files}


def find_shim_gaps(
    cpp_tests_dir: Path, shim_map: dict[str, list[str]]
) -> list[ShimGap]:
    """Return shim combinations present in *shim_map* but missing on disk."""
    gaps: list[ShimGap] = []
    for op, suffixes in shim_map.items():
        for suffix in suffixes:
            expected = _shim_test_path(cpp_tests_dir, op, suffix)
            if not expected.exists():
                gaps.append(ShimGap(op, suffix, str(expected)))
    return gaps


def summarize_test_counts(cpp_tests_dir: Path) -> dict[str, int]:
    """Return a dict mapping test file stem to test-macro count."""
    return {
        f.name: _count_tests_for(f) for f in sorted(cpp_tests_dir.glob("test_*.cpp"))
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_report(
    branch_map: dict[str, list[BranchInfo]],
    shim_gaps: list[ShimGap],
    test_counts: dict[str, int],
) -> None:
    """Write a human-readable coverage gap report to stdout."""
    sep = "-" * 72

    print("=" * 72)
    print("C++ Coverage Gap Analysis Report")
    print("=" * 72)

    # --- Source branch counts ---
    print("\n## Branch counts per source file\n")
    total = 0
    for src, branches in sorted(branch_map.items()):
        n = len(branches)
        total += n
        print(f"  {Path(src).name:<45s}  {n:>4d} branch-like statements")
    print(f"\n  {'TOTAL':<45s}  {total:>4d}")

    # --- Shim gaps ---
    print(f"\n{sep}")
    print("## Missing shim tests (in meson map but no .cpp file on disk)\n")
    if shim_gaps:
        for gap in shim_gaps:
            print(f"  MISSING: test_{gap.operation}{gap.suffix}_shim.cpp")
    else:
        print("  None – all shim combinations have a corresponding .cpp file.")

    # --- Test counts ---
    print(f"\n{sep}")
    print("## Test macro counts per test file\n")
    for name, count in sorted(test_counts.items(), key=lambda kv: kv[0]):
        marker = "  " if count > 0 else "  [EMPTY] "
        print(f"{marker}{name:<60s}  {count:>4d} test(s)")

    # --- Notable source-level branches ---
    print(f"\n{sep}")
    print("## Notable branches in core source files (helpers.cpp, sessionbase.cpp)\n")
    notable = {
        "helpers.cpp",
        "sessionbase.cpp",
        "datatypes.cpp",
        "exceptionsbase.cpp",
        "thread_safety.cpp",
    }
    for src, branches in sorted(branch_map.items()):
        if Path(src).name not in notable:
            continue
        throw_branches = [b for b in branches if b.kind == "throw"]
        if not throw_branches:
            continue
        print(f"  {Path(src).name} — throw statements:")
        for b in throw_branches:
            print(f"    line {b.line:4d}: {b.snippet}")

    print(f"\n{sep}")
    print("## Recommendations\n")
    print("  1. Ensure every 'throw' statement in core source files has a shim test.")
    print("  2. Review snmptrap SNMPv1 path (NETSNMP_DISABLE_SNMPV1 guard).")
    print("  3. Validate that branch counts decrease after adding new tests.")
    print("=" * 72)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Run the coverage gap analysis and print a report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to the repository root (default: current directory).",
    )
    args = parser.parse_args(argv)

    repo = Path(args.repo_root).resolve()
    src_dir = repo / "ezsnmp" / "src"
    cpp_tests_dir = repo / "cpp_tests"

    # Core source files (exclude versioned net-snmp sub-directories)
    core_src_files = [f for f in src_dir.glob("*.cpp") if f.is_file()]
    core_header_files = list((repo / "ezsnmp" / "include").glob("*.h"))

    # Shim map mirrors what meson.build declares so gaps are visible early
    shim_map: dict[str, list[str]] = {
        "snmpwalk": [
            "_timeout",
            "_nosuchname",
            "_get_and_print",
            "_with_data",
            "_parse_args",
            "_stat_error",
            "_order",
        ],
        "snmpbulkwalk": [
            "_timeout",
            "_nosuchname",
            "_get_and_print",
            "_with_data",
            "_parse_args",
            "_stat_error",
            "_order",
        ],
        "snmpbulkget": ["_nosuchname", "_timeout", "_parse_args", "_stat_error"],
        "snmpget": ["_timeout", "_parse_args", "_stat_error", "_errindex"],
        "snmpgetnext": ["_timeout", "_parse_args", "_stat_error", "_errindex"],
        "snmpset": ["", "_timeout", "_parse_args", "_stat_error", "_addvar"],
        "snmptrap": ["_parse_args", "_null", "_stat_error", "_v1_branch"],
    }

    branch_map = analyze_source_branches(core_src_files + core_header_files)
    shim_gaps = find_shim_gaps(cpp_tests_dir, shim_map)
    test_counts = summarize_test_counts(cpp_tests_dir)

    print_report(branch_map, shim_gaps, test_counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
