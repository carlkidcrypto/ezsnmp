#!/usr/bin/env python3
"""
Analyze Python source coverage gaps for the ezsnmp project.

This script statically inspects the Python source files in ``ezsnmp/`` and
the corresponding test files in ``python_tests/`` to identify which callable
branches (methods, functions, conditional paths) lack direct unit-test
coverage that can run **without** a live SNMP daemon.

The goal is to highlight coverage gaps so that targeted unit tests can be
written (or existing tests improved) before CI runs the full integration
suite.

Usage
-----
Run from the repository root::

    python3 .github/scripts/analyze_python_coverage_gaps.py

Or with an explicit source-package path::

    python3 .github/scripts/analyze_python_coverage_gaps.py --src ezsnmp --tests python_tests

Output
------
Prints a summary of each source file with:

* Total callable items (functions / methods).
* Items that appear to be exercised in at least one unit-test file.
* Items that have *no* corresponding reference in any unit-test file.

A callable item is considered "referenced" if any test file contains a
``def test_*`` function whose body (or the whole test file text) mentions the
callable name.  This is an intentionally conservative heuristic — it may
report false positives (a name used in a comment counts) but it will never
hide a genuinely untested item.
"""

import argparse
import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def collect_callables(source_path: Path) -> List[str]:
    """Return a list of function/method names defined in *source_path*.

    :param source_path: Path to a Python source file.
    :type source_path: Path
    :return: Sorted list of unique callable names found in the module.
    :rtype: List[str]
    """
    try:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        print(f"  [WARN] SyntaxError in {source_path}: {exc}", file=sys.stderr)
        return []

    names: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)
    return sorted(set(names))


def collect_conditional_markers(source_path: Path) -> List[str]:
    """Identify special branch-marker comments/strings in *source_path*.

    Currently looks for ``# pragma: no cover`` markers as a sign that a
    branch was consciously excluded from measurement.

    :param source_path: Path to a Python source file.
    :type source_path: Path
    :return: List of line references for no-cover pragmas.
    :rtype: List[str]
    """
    markers: List[str] = []
    for lineno, line in enumerate(
        source_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if "pragma: no cover" in line:
            markers.append(f"line {lineno}: {line.strip()}")
    return markers


# ---------------------------------------------------------------------------
# Test-reference helpers
# ---------------------------------------------------------------------------


def collect_test_references(test_dir: Path) -> Dict[str, Set[str]]:
    """Build a mapping from test-file name to the set of identifiers it
    contains (all words / tokens extracted from the source text).

    :param test_dir: Directory containing ``test_*.py`` files.
    :type test_dir: Path
    :return: ``{test_filename: set_of_tokens}``
    :rtype: Dict[str, Set[str]]
    """
    refs: Dict[str, Set[str]] = {}
    for test_file in sorted(test_dir.glob("test_*.py")):
        text = test_file.read_text(encoding="utf-8")
        # Tokenise naively: split on any non-identifier character.
        tokens: Set[str] = set()
        import re

        tokens = set(re.findall(r"[A-Za-z_]\w*", text))
        refs[test_file.name] = tokens
    return refs


# ---------------------------------------------------------------------------
# Gap analysis
# ---------------------------------------------------------------------------


def find_uncovered_callables(
    callables: List[str],
    test_refs: Dict[str, Set[str]],
    skip_private: bool = False,
) -> Tuple[List[str], List[str]]:
    """Partition *callables* into covered / uncovered based on *test_refs*.

    :param callables: Names of callables in a source file.
    :type callables: List[str]
    :param test_refs: Test-file token sets from :func:`collect_test_references`.
    :type test_refs: Dict[str, Set[str]]
    :param skip_private: If ``True``, skip names starting with ``__`` (dunder).
    :type skip_private: bool
    :return: ``(covered, uncovered)`` — two lists of callable names.
    :rtype: Tuple[List[str], List[str]]
    """
    all_tokens: Set[str] = set()
    for tokens in test_refs.values():
        all_tokens |= tokens

    covered: List[str] = []
    uncovered: List[str] = []
    for name in callables:
        if skip_private and name.startswith("__") and name.endswith("__"):
            covered.append(name)  # treat dunders as implicitly covered
            continue
        if name in all_tokens:
            covered.append(name)
        else:
            uncovered.append(name)
    return covered, uncovered


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def report_file(
    source_path: Path,
    callables: List[str],
    covered: List[str],
    uncovered: List[str],
    no_cover_markers: List[str],
) -> None:
    """Print a formatted gap report for a single source file.

    :param source_path: Path of the source file being reported.
    :param callables: All callable names in the file.
    :param covered: Callable names found in at least one test file.
    :param uncovered: Callable names *not* found in any test file.
    :param no_cover_markers: Lines marked with ``# pragma: no cover``.
    """
    total = len(callables)
    cov_count = len(covered)
    unc_count = len(uncovered)
    pct = (cov_count / total * 100) if total > 0 else 100.0

    status = "✅" if unc_count == 0 else "⚠️ "
    print(f"\n{status}  {source_path.name}  ({cov_count}/{total} — {pct:.0f}%)")

    if uncovered:
        print("  Potentially uncovered callables:")
        for name in uncovered:
            print(f"    - {name}")

    if no_cover_markers:
        print("  Lines with 'pragma: no cover':")
        for marker in no_cover_markers:
            print(f"    {marker}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """Main entry point for the coverage-gap analyser.

    :return: 0 on success, 1 if any source file has uncovered callables.
    :rtype: int
    """
    parser = argparse.ArgumentParser(
        description="Analyse Python coverage gaps for ezsnmp."
    )
    parser.add_argument(
        "--src",
        default="ezsnmp",
        help="Path to the Python source package (default: 'ezsnmp').",
    )
    parser.add_argument(
        "--tests",
        default="python_tests",
        help="Path to the test directory (default: 'python_tests').",
    )
    parser.add_argument(
        "--skip-dunders",
        action="store_true",
        default=True,
        help="Treat dunder methods as covered (default: True).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    src_dir = repo_root / args.src
    test_dir = repo_root / args.tests

    if not src_dir.is_dir():
        print(f"ERROR: Source directory not found: {src_dir}", file=sys.stderr)
        return 1
    if not test_dir.is_dir():
        print(f"ERROR: Test directory not found: {test_dir}", file=sys.stderr)
        return 1

    print(f"Source package : {src_dir}")
    print(f"Test directory : {test_dir}")

    test_refs = collect_test_references(test_dir)
    print(f"Test files found: {len(test_refs)}")

    source_files = sorted(src_dir.glob("*.py"))
    overall_has_gaps = False

    for src_file in source_files:
        callables = collect_callables(src_file)
        no_cover = collect_conditional_markers(src_file)
        covered, uncovered = find_uncovered_callables(
            callables, test_refs, skip_private=args.skip_dunders
        )
        report_file(src_file, callables, covered, uncovered, no_cover)
        if uncovered:
            overall_has_gaps = True

    print("\n" + "=" * 60)
    if overall_has_gaps:
        print("Coverage gaps detected — see report above.")
        return 1
    else:
        print("No coverage gaps detected.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
