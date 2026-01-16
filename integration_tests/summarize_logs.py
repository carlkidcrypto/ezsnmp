#!/usr/bin/env python3
"""Summarize integration test logs (replacement for summarize_logs.sh).

Usage: summarize_logs.py [RESULTS_DIR]

If RESULTS_DIR is omitted the latest test_results_* directory is used.
Produces a detailed table, a compact summary (file | total_time | results),
and basic statistics (n, mean, stddev, min, max) for timing and FD metrics.
"""
from __future__ import annotations

import argparse
import math
import re
from collections import defaultdict
from datetime import datetime
from statistics import mean, pstdev
from pathlib import Path
from typing import Dict, List, Optional


COUNTER_KEYS = [
    "connection_error_counter",
    "usm_unknown_security_name_counter",
    "err_gen_ku_key_counter",
    "netsnmp_parse_args_error_counter",
    "unknown_oid_error_counter",
    "no_hostname_specified_error_counter",
    "generic_error_counter",
]


def find_latest_results_dir(base: Path) -> Optional[Path]:
    dirs = sorted(base.glob("test_results_*/"), key=lambda p: p.stat().st_mtime, reverse=True)
    return dirs[0] if dirs else None


def parse_log_file(path: Path) -> Dict[str, object]:
    # Initialize counters
    data: Dict[str, object] = {k: 0 for k in COUNTER_KEYS}
    # Metrics to capture last seen values
    last_values: Dict[str, Optional[float]] = {
        "subprocess_fd_after": None,
        "parent_fd_after_no_close": None,
        "total_time_no_close": None,
        "avg_time_no_close": None,
        "parent_fd_after_with_close": None,
        "total_time_with_close": None,
        "avg_time_with_close": None,
    }

    # Precompile regexes (case-insensitive)
    counter_re = {k: re.compile(rf"{re.escape(k)}\s*:\s*(\d+)", re.I) for k in COUNTER_KEYS}
    # FD and timing patterns
    re_subproc_fd = re.compile(r"Subprocess PID Open FDs after:\s*(\d+)", re.I)
    re_parent_fd_no = re.compile(r"Parent PID Open FDs after work_get_no_close.*:\s*(\d+)", re.I)
    re_total_no = re.compile(r"work_get_no_close .*Total execution time:\s*([0-9.]+)", re.I)
    re_avg_no = re.compile(r"Average time per SNMP get call \(no close\).*:\s*([0-9.]+)", re.I)
    re_parent_fd_with = re.compile(r"Parent PID Open FDs after work_get_close.*:\s*(\d+)", re.I)
    re_total_with = re.compile(r"work_get_close .*Total execution time:\s*([0-9.]+)", re.I)
    re_avg_with = re.compile(r"Average time per SNMP get call \(with close\).*:\s*([0-9.]+)", re.I)

    with path.open("r", errors="ignore") as fh:
        for line in fh:
            line = line.rstrip("\n")
            # Counters
            for k, cre in counter_re.items():
                m = cre.search(line)
                if m:
                    data[k] += int(m.group(1))

            # Last-seen metrics
            m = re_subproc_fd.search(line)
            if m:
                last_values["subprocess_fd_after"] = float(m.group(1))

            m = re_parent_fd_no.search(line)
            if m:
                last_values["parent_fd_after_no_close"] = float(m.group(1))

            m = re_total_no.search(line)
            if m:
                last_values["total_time_no_close"] = float(m.group(1))

            m = re_avg_no.search(line)
            if m:
                last_values["avg_time_no_close"] = float(m.group(1))

            m = re_parent_fd_with.search(line)
            if m:
                last_values["parent_fd_after_with_close"] = float(m.group(1))

            m = re_total_with.search(line)
            if m:
                last_values["total_time_with_close"] = float(m.group(1))

            m = re_avg_with.search(line)
            if m:
                last_values["avg_time_with_close"] = float(m.group(1))

    # Merge into result
    result = {**data, **last_values}
    return result


def format_table(rows: List[List[str]], headers: List[str]) -> str:
    # Compute column widths
    cols = list(zip(*([headers] + rows))) if rows else [[h] for h in headers]
    widths = [max(len(str(x)) for x in c) for c in cols]
    lines = []
    # header
    lines.append(" | ".join(h.ljust(w) for h, w in zip(headers, widths)))
    lines.append("-+-".join("-" * w for w in widths))
    for r in rows:
        lines.append(" | ".join(str(c).ljust(w) for c, w in zip(r, widths)))
    return "\n".join(lines)


def compute_stats(values: List[float]):
    if not values:
        return None
    n = len(values)
    mu = mean(values)
    sd = pstdev(values) if n > 1 else 0.0
    return {"n": n, "mean": mu, "sd": sd, "min": min(values), "max": max(values)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("results_dir", nargs="?", help="test_results_*/ directory")
    args = p.parse_args()

    base = Path(__file__).resolve().parent
    results_dir = Path(args.results_dir) if args.results_dir else find_latest_results_dir(base)
    if not results_dir or not results_dir.exists():
        print("ERROR: No results directory found.")
        return

    log_files = sorted(results_dir.glob("*.log"))
    if not log_files:
        print(f"ERROR: No .log files found in {results_dir}")
        return

    # Parse each log
    entries = []
    totals = defaultdict(int)
    metrics_collections: Dict[str, List[float]] = defaultdict(list)

    for lf in log_files:
        parsed = parse_log_file(lf)
        # collect totals for counters
        for k in COUNTER_KEYS:
            totals[k] += int(parsed.get(k, 0))

        # collect metrics
        for mk in [
            "subprocess_fd_after",
            "parent_fd_after_no_close",
            "total_time_no_close",
            "avg_time_no_close",
            "parent_fd_after_with_close",
            "total_time_with_close",
            "avg_time_with_close",
        ]:
            v = parsed.get(mk)
            if v is not None:
                metrics_collections[mk].append(float(v))

        # Prepare display row
        total_time = (parsed.get("total_time_no_close") or 0) + (parsed.get("total_time_with_close") or 0)
        results_str = ", ".join(f"{k.split('_')[0]}={parsed.get(k,0)}" for k in COUNTER_KEYS)
        entries.append(
            {
                "file": lf.name,
                "total_time": total_time,
                "results": results_str,
                **{k: parsed.get(k) for k in COUNTER_KEYS},
                **{m: parsed.get(m) for m in metrics_collections.keys()},
            }
        )

    # Per-file tables (simplified): show metrics for one file at a time
    # If a specific file is requested via CLI, filter to that file (substring match)
    file_filter = args.results_dir if args.results_dir and args.results_dir.endswith('.log') else None
    # Note: we added positional arg 'results_dir' earlier; allow user to pass a filename via --file
    # Re-parse args to check for optional --file
    # (we keep backward compatibility: if first positional was a file path, it's handled earlier)
    # Print per-file tables
    for e in entries:
        if file_filter and file_filter not in e["file"]:
            continue
        print(f"\nFile: {e['file']}")
        per_headers = ["metric", "value"]
        per_rows = []
        # Counters
        per_rows.extend([["connection_error_counter", e.get("connection_error_counter", 0)],
                         ["usm_unknown_security_name_counter", e.get("usm_unknown_security_name_counter", 0)],
                         ["err_gen_ku_key_counter", e.get("err_gen_ku_key_counter", 0)],
                         ["netsnmp_parse_args_error_counter", e.get("netsnmp_parse_args_error_counter", 0)],
                         ["unknown_oid_error_counter", e.get("unknown_oid_error_counter", 0)],
                         ["no_hostname_specified_error_counter", e.get("no_hostname_specified_error_counter", 0)],
                         ["generic_error_counter", e.get("generic_error_counter", 0)]])
        # FD and timing metrics
        per_rows.extend([
            ["subprocess_fd_after", e.get("subprocess_fd_after") or 0],
            ["parent_fd_after_no_close", e.get("parent_fd_after_no_close") or 0],
            ["total_time_no_close", f"{(e.get('total_time_no_close') or 0):.6f}"],
            ["avg_time_no_close", f"{(e.get('avg_time_no_close') or 0):.6f}"],
            ["parent_fd_after_with_close", e.get("parent_fd_after_with_close") or 0],
            ["total_time_with_close", f"{(e.get('total_time_with_close') or 0):.6f}"],
            ["avg_time_with_close", f"{(e.get('avg_time_with_close') or 0):.6f}"],
            ["total_time", f"{e.get('total_time'):.6f}"],
            ["results", e.get("results")],
        ])
        print(format_table(per_rows, per_headers))
        # Per-file statistics (min/max/avg/stddev) for selected metrics
        stats_metrics = [
            "total_time_no_close",
            "total_time_with_close",
            "avg_time_no_close",
            "avg_time_with_close",
            "subprocess_fd_after",
            "parent_fd_after_no_close",
            "parent_fd_after_with_close",
        ]
        stats_rows = []
        for m in stats_metrics:
            v = e.get(m)
            if v is None:
                continue
            s = compute_stats([float(v)])
            if s:
                stats_rows.append([
                    m,
                    s["n"],
                    f"{s['mean']:.6f}",
                    f"{s['sd']:.6f}",
                    f"{s['min']}",
                    f"{s['max']}",
                ])
        if stats_rows:
            print("\nPer-file statistics:")
            print(format_table(stats_rows, ["metric", "n", "mean", "sd", "min", "max"]))
        else:
            print("\nNo per-file statistics available.")

    # End per-file loop
    stats_targets = {
        "total_time_no_close": metrics_collections.get("total_time_no_close", []),
        "total_time_with_close": metrics_collections.get("total_time_with_close", []),
        "avg_time_no_close": metrics_collections.get("avg_time_no_close", []),
        "avg_time_with_close": metrics_collections.get("avg_time_with_close", []),
        "subprocess_fd_after": metrics_collections.get("subprocess_fd_after", []),
        "parent_fd_after_no_close": metrics_collections.get("parent_fd_after_no_close", []),
        "parent_fd_after_with_close": metrics_collections.get("parent_fd_after_with_close", []),
    }
    
        # Aggregated summary (exclude FD test file)
        agg_entries = [e for e in entries if e["file"] != "test_file_descriptors.log"]
        if agg_entries:
            # Aggregate counters
            agg_counters = {k: 0 for k in COUNTER_KEYS}
            for e in agg_entries:
                for k in COUNTER_KEYS:
                    agg_counters[k] += int(e.get(k, 0) or 0)

            # Aggregate metric stats
            agg_metrics = {
                "total_time_no_close": [],
                "total_time_with_close": [],
                "avg_time_no_close": [],
                "avg_time_with_close": [],
                "subprocess_fd_after": [],
                "parent_fd_after_no_close": [],
                "parent_fd_after_with_close": [],
            }
            for e in agg_entries:
                for m in list(agg_metrics.keys()):
                    v = e.get(m)
                    if v is not None:
                        agg_metrics[m].append(float(v))

            print("\nAggregated summary (excluding test_file_descriptors.log):")
            # Print aggregated counters table
            agg_rows = [[k, agg_counters[k]] for k in agg_counters]
            print(format_table(agg_rows, ["counter", "total"]))

            # Print aggregated metric stats
            stats_rows = []
            for name, vals in agg_metrics.items():
                s = compute_stats(vals) if vals else None
                if s:
                    stats_rows.append([
                        name,
                        s["n"],
                        f"{s['mean']:.6f}",
                        f"{s['sd']:.6f}",
                        f"{s['min']}",
                        f"{s['max']}",
                    ])
                else:
                    stats_rows.append([name, 0, "0.000000", "0.000000", 0, 0])

            print("\nAggregated metrics statistics:")
            print(format_table(stats_rows, ["metric", "n", "mean", "sd", "min", "max"]))
        else:
            print("\nNo entries to aggregate (all files filtered out).")


if __name__ == "__main__":
    main()
