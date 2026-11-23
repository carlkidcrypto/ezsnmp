#!/usr/bin/env python3
"""Scan Valgrind memcheck logs for native ezsnmp or Net-SNMP memory leaks."""

from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path

DEFAULT_MARKERS: tuple[str, ...] = (
    "netsnmp_init_mib_internals",
    "netsnmp_parse_args",
    "_sessionbase",
    "_netsnmpbase",
    "SessionBase::",
)

_BLOCK_SPLIT_RE = re.compile(r"\n==\d+==\s*\n")
_LOST_RE = re.compile(r"bytes in \d+ blocks are (?:definitely|indirectly) lost")


def find_native_leaks(
    log_text: str,
    markers: tuple[str, ...] = DEFAULT_MARKERS,
) -> list[str]:
    """Return all Valgrind record blocks matching *markers* (excluding one-time PyInit_/SWIG_mod_exec imports)."""
    leaked_blocks: list[str] = []
    for block in _BLOCK_SPLIT_RE.split(log_text):
        if (
            _LOST_RE.search(block)
            and "PyInit_" not in block
            and "SWIG_mod_exec" not in block
            and any(marker in block for marker in markers)
        ):
            leaked_blocks.append(block.strip())
    return leaked_blocks


def check_valgrind_log_files(patterns: list[str]) -> int:
    """Validate one or more Valgrind log file paths/globs and return a process exit code."""
    matched_files: list[Path] = []
    for pattern in patterns:
        expanded = sorted(Path(p) for p in glob.glob(pattern))
        if expanded:
            matched_files.extend(expanded)
        else:
            candidate = Path(pattern)
            if candidate.is_file():
                matched_files.append(candidate)

    if not matched_files:
        print(
            f"ERROR: No Valgrind log files matched: {patterns}",
            file=sys.stderr,
        )
        return 1

    all_leaks: list[tuple[Path, str]] = []
    for log_path in matched_files:
        text = log_path.read_text(encoding="utf-8", errors="replace")
        for block in find_native_leaks(text):
            all_leaks.append((log_path, block))

    if all_leaks:
        print(
            f"ERROR: Valgrind detected {len(all_leaks)} native ezsnmp/Net-SNMP memory leak block(s):",
            file=sys.stderr,
        )
        for log_path, block in all_leaks[:10]:
            print(f"[{log_path}]\n{block}\n---", file=sys.stderr)
        return 1

    print(
        f"Valgrind ezsnmp/Net-SNMP native leak check: PASS (0 matching leak blocks across {len(matched_files)} file(s))"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail if Valgrind memcheck logs contain native ezsnmp or Net-SNMP leaks."
    )
    parser.add_argument(
        "logs",
        nargs="*",
        default=["valgrind_*.out"],
        help="Valgrind log file paths or glob patterns (default: valgrind_*.out)",
    )
    args = parser.parse_args(argv)
    return check_valgrind_log_files(list(args.logs))


if __name__ == "__main__":
    raise SystemExit(main())
