#!/usr/bin/env python3
"""Summarize integration test logs (replacement for summarize_logs.sh).

Usage: summarize_logs.py [RESULTS_DIR]

If RESULTS_DIR is omitted the latest test_results_* directory is used.
Produces a detailed table, a compact summary (file | total_time | results),
and basic statistics (n, mean, stddev, min, max) for timing and FD metrics.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from datetime import datetime, timezone
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
    dirs = sorted(
        base.glob("test_results_*/"), key=lambda p: p.stat().st_mtime, reverse=True
    )
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
        "total_time": None,
    }

    # Precompile regexes (case-insensitive)
    counter_re = {
        k: re.compile(rf"{re.escape(k)}\s*:\s*(\d+)", re.I) for k in COUNTER_KEYS
    }
    # FD and timing patterns
    re_subproc_fd = re.compile(r"Subprocess PID Open FDs after:\s*(\d+)", re.I)
    re_parent_fd_no = re.compile(
        r"Parent PID Open FDs after work_(get|op)_no_close.*:\s*(\d+)", re.I
    )
    re_total_no = re.compile(
        r"work_(get|op)_no_close .*Total execution time:\s*([0-9.]+)", re.I
    )
    re_avg_no = re.compile(
        r"Average time per SNMP (get )?call \(no close\).*:\s*([0-9.]+)", re.I
    )
    re_parent_fd_with = re.compile(
        r"Parent PID Open FDs after work_(get|op)_close.*:\s*(\d+)", re.I
    )
    re_total_with = re.compile(
        r"work_(get|op)_close .*Total execution time:\s*([0-9.]+)", re.I
    )
    re_avg_with = re.compile(
        r"Average time per SNMP (get )?call \(with close\).*:\s*([0-9.]+)", re.I
    )
    # Generic total execution time (any test harness)
    re_total_generic = re.compile(r"Total execution time:\s*([0-9.]+)\s*seconds", re.I)

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
                last_values["parent_fd_after_no_close"] = float(m.group(2))

            m = re_total_no.search(line)
            if m:
                last_values["total_time_no_close"] = float(m.group(2))

            m = re_avg_no.search(line)
            if m:
                last_values["avg_time_no_close"] = float(m.group(2))

            m = re_parent_fd_with.search(line)
            if m:
                last_values["parent_fd_after_with_close"] = float(m.group(2))

            m = re_total_with.search(line)
            if m:
                last_values["total_time_with_close"] = float(m.group(2))

            m = re_avg_with.search(line)
            if m:
                last_values["avg_time_with_close"] = float(m.group(2))

            m = re_total_generic.search(line)
            if m:
                # generic total time line (e.g. multi_process_snmp_get: ... Total execution time: 1.23 seconds)
                last_values["total_time"] = float(m.group(1))

    # Merge into result
    result = {**data, **last_values}
    return result


def parse_fd_operation_records(path: Path) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    running_re = re.compile(
        r"Running (work_op_no_close|work_op_close):\s*(\S+)\s+(\S+)", re.I
    )
    fd_before_re = re.compile(r"Subprocess PID:? Open FDs before:\s*(\d+)", re.I)
    fd_after_re = re.compile(r"Subprocess PID\s*Open FDs after:\s*(\d+)", re.I)
    exec_re = re.compile(r"Total execution time:\s*([0-9.]+)", re.I)
    avg_re = re.compile(r"Average time per SNMP call.*?:\s*([0-9.]+)", re.I)

    current_record: Optional[Dict[str, object]] = None
    with path.open("r", errors="ignore") as fh:
        for line in fh:
            line = line.rstrip("\n")
            running_match = running_re.search(line)
            if running_match:
                if current_record and "session" in current_record:
                    records.append(current_record)
                mode_raw, operation, sess = running_match.groups()
                current_record = {
                    "session": sess,
                    "operation": operation,
                    "mode": "no close" if "no_close" in mode_raw else "close",
                }
                continue

            if current_record is None:
                continue

            m = fd_before_re.search(line)
            if m:
                current_record["fd_before"] = int(m.group(1))

            m = fd_after_re.search(line)
            if m:
                current_record["fd_after"] = int(m.group(1))

            m = exec_re.search(line)
            if m:
                current_record["exec_time"] = float(m.group(1))

            m = avg_re.search(line)
            if m:
                current_record["avg_time"] = float(m.group(1))

    if current_record and "session" in current_record:
        records.append(current_record)

    return records


def aggregate_fd_records(records: List[Dict[str, object]]) -> List[List[str]]:
    grouped: Dict[tuple, Dict[str, List[float]]] = {}
    for rec in records:
        key = (rec.get("session", "-"), rec.get("operation", "-"), rec.get("mode", "-"))
        if key not in grouped:
            grouped[key] = {
                "fd_before": [],
                "fd_after": [],
                "exec_time": [],
                "avg_time": [],
            }
        for field in ["fd_before", "fd_after", "exec_time", "avg_time"]:
            if field in rec:
                grouped[key][field].append(float(rec[field]))

    rows: List[List[str]] = []
    for sess, operation, mode in sorted(grouped.keys()):
        g = grouped[(sess, operation, mode)]
        fb_vals = g["fd_before"]
        fa_vals = g["fd_after"]
        exec_vals = g["exec_time"]
        avg_vals = g["avg_time"]

        if fb_vals and fa_vals:
            fb = mean(fb_vals)
            fa = mean(fa_vals)
            leak = fa - fb
            fb_str = f"{fb:.0f}"
            fa_str = f"{fa:.0f}"
            leak_str = f"{leak:+.0f}"
        else:
            fb_str = fa_str = leak_str = "-"

        et = f"{mean(exec_vals):.3f}" if exec_vals else "-"
        at = f"{mean(avg_vals):.6f}" if avg_vals else "-"
        count = max(len(exec_vals), len(avg_vals), len(fb_vals), len(fa_vals))
        rows.append(
            [sess, operation, mode, str(count), fb_str, fa_str, leak_str, et, at]
        )

    return rows


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
    p.add_argument(
        "-o",
        "--output",
        help="Output .rst file path (defaults to results_dir/integration_summary.rst)",
    )
    args = p.parse_args()

    base = Path(__file__).resolve().parent
    results_dir = (
        Path(args.results_dir) if args.results_dir else find_latest_results_dir(base)
    )
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
    fd_op_records_all: List[Dict[str, object]] = []
    fd_op_records_by_file: Dict[str, List[Dict[str, object]]] = {}

    for lf in log_files:
        parsed = parse_log_file(lf)
        if lf.name.startswith("test_file_descriptors"):
            fd_records = parse_fd_operation_records(lf)
            fd_op_records_by_file[lf.name] = fd_records
            fd_op_records_all.extend(fd_records)
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
            "total_time",
        ]:
            v = parsed.get(mk)
            if v is not None:
                metrics_collections[mk].append(float(v))

        # Prepare display row
        # Prefer a generic total_time if present (some tests emit a single total time line)
        if parsed.get("total_time") is not None:
            total_time = float(parsed.get("total_time"))
        else:
            total_time = (parsed.get("total_time_no_close") or 0) + (
                parsed.get("total_time_with_close") or 0
            )
        results_str = ", ".join(
            f"{k.split('_')[0]}={parsed.get(k,0)}" for k in COUNTER_KEYS
        )
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
    file_filter = (
        args.results_dir
        if args.results_dir and args.results_dir.endswith(".log")
        else None
    )
    # Note: we added positional arg 'results_dir' earlier; allow user to pass a filename via --file
    # Re-parse args to check for optional --file
    # (we keep backward compatibility: if first positional was a file path, it's handled earlier)
    # Prepare RST output lines instead of printing directly
    out_lines: List[str] = []

    # Print per-file tables (accumulate into out_lines)
    for e in entries:
        if file_filter and file_filter not in e["file"]:
            continue
        out_lines.append("")
        out_lines.append(f"File: {e['file']}")
        out_lines.append("")
        per_headers = ["metric", "value"]
        per_rows = []
        # Counters
        per_rows.extend(
            [
                ["connection_error_counter", e.get("connection_error_counter", 0)],
                [
                    "usm_unknown_security_name_counter",
                    e.get("usm_unknown_security_name_counter", 0),
                ],
                ["err_gen_ku_key_counter", e.get("err_gen_ku_key_counter", 0)],
                [
                    "netsnmp_parse_args_error_counter",
                    e.get("netsnmp_parse_args_error_counter", 0),
                ],
                ["unknown_oid_error_counter", e.get("unknown_oid_error_counter", 0)],
                [
                    "no_hostname_specified_error_counter",
                    e.get("no_hostname_specified_error_counter", 0),
                ],
                ["generic_error_counter", e.get("generic_error_counter", 0)],
            ]
        )
        # FD and timing metrics: only include for the FD test file
        is_fd_file = e.get("file") == "test_file_descriptors.log"
        if is_fd_file:
            per_rows.extend(
                [
                    ["subprocess_fd_after", e.get("subprocess_fd_after") or 0],
                    [
                        "parent_fd_after_no_close",
                        e.get("parent_fd_after_no_close") or 0,
                    ],
                    [
                        "total_time_no_close",
                        f"{(e.get('total_time_no_close') or 0):.6f}",
                    ],
                    ["avg_time_no_close", f"{(e.get('avg_time_no_close') or 0):.6f}"],
                    [
                        "parent_fd_after_with_close",
                        e.get("parent_fd_after_with_close") or 0,
                    ],
                    [
                        "total_time_with_close",
                        f"{(e.get('total_time_with_close') or 0):.6f}",
                    ],
                    [
                        "avg_time_with_close",
                        f"{(e.get('avg_time_with_close') or 0):.6f}",
                    ],
                    ["total_time", f"{(e.get('total_time') or 0):.6f}"],
                    ["results", e.get("results")],
                ]
            )
        else:
            # Non-FD logs: include only total_time and results
            per_rows.extend(
                [
                    ["total_time", f"{(e.get('total_time') or 0):.6f}"],
                    ["results", e.get("results")],
                ]
            )
        out_lines.append("::")
        out_lines.append("")
        for line in format_table(per_rows, per_headers).splitlines():
            out_lines.append("    " + line)
        # Per-file statistics (min/max/avg/stddev) for selected metrics
        # Determine which stats to show: for FD test show timing/FD metrics, otherwise skip FD stats
        if is_fd_file:
            stats_metrics = [
                "total_time_no_close",
                "total_time_with_close",
                "avg_time_no_close",
                "avg_time_with_close",
                "subprocess_fd_after",
                "parent_fd_after_no_close",
                "parent_fd_after_with_close",
            ]
        else:
            stats_metrics = []
        stats_rows = []
        for m in stats_metrics:
            v = e.get(m)
            if v is None:
                continue
            s = compute_stats([float(v)])
            if s:
                stats_rows.append(
                    [
                        m,
                        s["n"],
                        f"{s['mean']:.6f}",
                        f"{s['sd']:.6f}",
                        f"{s['min']}",
                        f"{s['max']}",
                    ]
                )
        if stats_rows:
            out_lines.append("")
            out_lines.append("Per-file statistics:")
            out_lines.append("")
            out_lines.append("::")
            out_lines.append("")
            for line in format_table(
                stats_rows, ["metric", "n", "mean", "sd", "min", "max"]
            ).splitlines():
                out_lines.append("    " + line)
        else:
            out_lines.append("")
            out_lines.append("No per-file statistics available.")

        if is_fd_file:
            fd_records = fd_op_records_by_file.get(e["file"], [])
            fd_rows = aggregate_fd_records(fd_records)
            if fd_rows:
                out_lines.append("")
                out_lines.append("Per-operation FD summary:")
                out_lines.append("")
                out_lines.append("::")
                out_lines.append("")
                fd_headers = [
                    "session",
                    "operation",
                    "mode",
                    "count",
                    "fd_before",
                    "fd_after",
                    "fd_leak",
                    "exec_time",
                    "avg_time",
                ]
                for line in format_table(fd_rows, fd_headers).splitlines():
                    out_lines.append("    " + line)
            else:
                out_lines.append("")
                out_lines.append("No per-operation FD data available.")

    # End per-file loop
    stats_targets = {
        "total_time_no_close": metrics_collections.get("total_time_no_close", []),
        "total_time_with_close": metrics_collections.get("total_time_with_close", []),
        "avg_time_no_close": metrics_collections.get("avg_time_no_close", []),
        "avg_time_with_close": metrics_collections.get("avg_time_with_close", []),
        "subprocess_fd_after": metrics_collections.get("subprocess_fd_after", []),
        "parent_fd_after_no_close": metrics_collections.get(
            "parent_fd_after_no_close", []
        ),
        "parent_fd_after_with_close": metrics_collections.get(
            "parent_fd_after_with_close", []
        ),
    }
    # Aggregated summary (exclude FD test file)
    agg_entries = [e for e in entries if e["file"] != "test_file_descriptors.log"]
    if agg_entries:
        # Determine worker sizes and modes present
        import re as _re

        worker_set = set()
        modes = {"thread": [], "process": []}
        file_pat = _re.compile(r".*_(\d+)_(process|thread)\.log$")
        for e in agg_entries:
            m = file_pat.match(e["file"]) or file_pat.match(
                e["file"].replace(".log", "")
            )
            if m:
                workers = int(m.group(1))
                mode = m.group(2)
                worker_set.add(workers)
                modes.setdefault(mode, []).append((workers, e))

        workers_sorted = sorted(worker_set)

        # Build header: counter | total | threads | <n> threads... | process | <n> process ...
        header = ["counter", "total", "threads"]
        for w in workers_sorted:
            header.append(f"{w} threads")
        header.append("process")
        for w in workers_sorted:
            header.append(f"{w} process")

        # Precompute aggregates
        # total per counter
        total_per_counter = {k: 0 for k in COUNTER_KEYS}
        for e in agg_entries:
            for k in COUNTER_KEYS:
                total_per_counter[k] += int(e.get(k, 0) or 0)

        # mode totals and per-worker per-mode totals
        mode_totals = {
            "thread": {k: 0 for k in COUNTER_KEYS},
            "process": {k: 0 for k in COUNTER_KEYS},
        }
        per_worker_mode = {
            "thread": {w: {k: 0 for k in COUNTER_KEYS} for w in workers_sorted},
            "process": {w: {k: 0 for k in COUNTER_KEYS} for w in workers_sorted},
        }

        for e in agg_entries:
            m = file_pat.match(e["file"]) or file_pat.match(
                e["file"].replace(".log", "")
            )
            mode = None
            w = None
            if m:
                w = int(m.group(1))
                mode = m.group(2)
            for k in COUNTER_KEYS:
                v = int(e.get(k, 0) or 0)
                if mode:
                    mode_totals[mode][k] += v
                    if w in per_worker_mode[mode]:
                        per_worker_mode[mode][w][k] += v

        # Build rows
        agg_rows = []
        for k in COUNTER_KEYS:
            row = [k, total_per_counter[k]]
            # threads total
            row.append(mode_totals.get("thread", {}).get(k, 0))
            # per worker threads
            for w in workers_sorted:
                row.append(per_worker_mode.get("thread", {}).get(w, {}).get(k, 0))
            # process total
            row.append(mode_totals.get("process", {}).get(k, 0))
            for w in workers_sorted:
                row.append(per_worker_mode.get("process", {}).get(w, {}).get(k, 0))
            agg_rows.append(row)

        out_lines.append("")
        out_lines.append("Aggregated summary (excluding test_file_descriptors.log):")
        out_lines.append("")
        out_lines.append("::")
        out_lines.append("")
        for line in format_table(agg_rows, header).splitlines():
            out_lines.append("    " + line)
    else:
        out_lines.append("")
        out_lines.append("No entries to aggregate (all files filtered out).")

    if fd_op_records_all:
        out_lines.append("")
        out_lines.append("Aggregated FD summary (all FD logs):")
        out_lines.append("")
        out_lines.append("::")
        out_lines.append("")
        fd_headers = [
            "session",
            "operation",
            "mode",
            "count",
            "fd_before",
            "fd_after",
            "fd_leak",
            "exec_time",
            "avg_time",
        ]
        fd_rows = aggregate_fd_records(fd_op_records_all)
        for line in format_table(fd_rows, fd_headers).splitlines():
            out_lines.append("    " + line)

    # Additionally produce aggregated summaries per method (get, walk, bulkwalk, etc.)
    def extract_method(fname: str) -> str:
        # Remove trailing worker/mode pattern like _8_thread.log
        m = _re.sub(r"_\d+_(process|thread)\.log$", "", fname)
        m = m.replace(".log", "")
        if m.startswith("test_"):
            m = m[len("test_") :]
        key = m.lower()
        # Normalize into common method names
        if "bulkwalk" in key or ("bulk" in key and "walk" in key):
            return "bulkwalk"
        if "walk" in key:
            return "walk"
        if "getnext" in key:
            return "getnext"
        if "get" in key:
            return "get"
        if "set" in key:
            return "set"
        return key

    method_groups: Dict[str, List[dict]] = defaultdict(list)
    for e in agg_entries:
        method = extract_method(e["file"])
        method_groups[method].append(e)

    if method_groups:
        out_lines.append("")
        out_lines.append("Aggregated summary by method:")
        out_lines.append("")
        for method, group in sorted(method_groups.items()):
            out_lines.append(f"Method: {method}")
            out_lines.append("")
            # recompute workers and modes for this group
            worker_set = set()
            modes = {"thread": [], "process": []}
            file_pat = _re.compile(r".*_(\d+)_(process|thread)\.log$")
            for e in group:
                m = file_pat.match(e["file"]) or file_pat.match(
                    e["file"].replace(".log", "")
                )
                if m:
                    worker_set.add(int(m.group(1)))
                    modes.setdefault(m.group(2), []).append((int(m.group(1)), e))
            workers_sorted = sorted(worker_set)
            header = ["counter", "total", "threads"]
            for w in workers_sorted:
                header.append(f"{w} threads")
            header.append("process")
            for w in workers_sorted:
                header.append(f"{w} process")

            # compute total per counter for this method
            total_per_counter = {k: 0 for k in COUNTER_KEYS}
            for e in group:
                for k in COUNTER_KEYS:
                    total_per_counter[k] += int(e.get(k, 0) or 0)

            mode_totals = {
                "thread": {k: 0 for k in COUNTER_KEYS},
                "process": {k: 0 for k in COUNTER_KEYS},
            }
            per_worker_mode = {
                "thread": {w: {k: 0 for k in COUNTER_KEYS} for w in workers_sorted},
                "process": {w: {k: 0 for k in COUNTER_KEYS} for w in workers_sorted},
            }
            for e in group:
                m = file_pat.match(e["file"]) or file_pat.match(
                    e["file"].replace(".log", "")
                )
                mode = None
                w = None
                if m:
                    w = int(m.group(1))
                    mode = m.group(2)
                for k in COUNTER_KEYS:
                    v = int(e.get(k, 0) or 0)
                    if mode:
                        mode_totals[mode][k] += v
                        if w in per_worker_mode[mode]:
                            per_worker_mode[mode][w][k] += v

            agg_rows = []
            for k in COUNTER_KEYS:
                row = [k, total_per_counter[k]]
                row.append(mode_totals.get("thread", {}).get(k, 0))
                for w in workers_sorted:
                    row.append(per_worker_mode.get("thread", {}).get(w, {}).get(k, 0))
                row.append(mode_totals.get("process", {}).get(k, 0))
                for w in workers_sorted:
                    row.append(per_worker_mode.get("process", {}).get(w, {}).get(k, 0))
                agg_rows.append(row)

            out_lines.append("::")
            out_lines.append("")
            for line in format_table(agg_rows, header).splitlines():
                out_lines.append("    " + line)
            out_lines.append("")
    # test_file_descriptors.py results: compute FD-specific metrics (and include total_time aggregated across non-FD files)
    fd_entries = [
        e
        for e in entries
        if (
            "file_descriptors" in e["file"]
            or "fd_test" in e["file"]
            or e["file"] in ("test_file_descriptors.log", "snmp_fd_test_output.log")
        )
    ]
    fd_metrics = [
        "total_time_no_close",
        "total_time_with_close",
        "avg_time_no_close",
        "avg_time_with_close",
        # total_time will be computed across non-FD files (agg_entries)
        "total_time",
        "subprocess_fd_after",
        "parent_fd_after_no_close",
        "parent_fd_after_with_close",
    ]
    fd_stats_rows: List[List[object]] = []
    for m in fd_metrics:
        vals: List[float] = []
        if m == "total_time":
            # use agg_entries (non-FD) total_time values
            for e in agg_entries:
                v = e.get("total_time")
                if v is None:
                    continue
                try:
                    vals.append(float(v))
                except Exception:
                    pass
        else:
            for e in fd_entries:
                v = e.get(m)
                if v is None:
                    continue
                try:
                    vals.append(float(v))
                except Exception:
                    pass
        s = compute_stats(vals) if vals else None
        if s:
            fd_stats_rows.append(
                [
                    m,
                    s["n"],
                    f"{s['mean']:.6f}",
                    f"{s['sd']:.6f}",
                    f"{s['min']}",
                    f"{s['max']}",
                ]
            )
    if fd_stats_rows:
        out_lines.append("")
        out_lines.append("test_file_descriptors.py results:")
        out_lines.append("")
        out_lines.append("::")
        out_lines.append("")
        for line in format_table(
            fd_stats_rows, ["metric", "n", "mean", "sd", "min", "max"]
        ).splitlines():
            out_lines.append("    " + line)

    # Combined per-file statistics across all non-FD log files
    agg_metrics = [
        "total_time_no_close",
        "total_time_with_close",
        "avg_time_no_close",
        "avg_time_with_close",
        "total_time",
        "subprocess_fd_after",
        "parent_fd_after_no_close",
        "parent_fd_after_with_close",
    ]
    agg_stats_rows = []
    for m in agg_metrics:
        vals: List[float] = []
        for e in agg_entries:
            v = e.get(m)
            if v is None:
                continue
            try:
                vals.append(float(v))
            except Exception:
                pass
        s = compute_stats(vals) if vals else None
        if s:
            agg_stats_rows.append(
                [
                    m,
                    s["n"],
                    f"{s['mean']:.6f}",
                    f"{s['sd']:.6f}",
                    f"{s['min']}",
                    f"{s['max']}",
                ]
            )
    if agg_stats_rows:
        out_lines.append("")
        out_lines.append("Combined per-file statistics (excluding FD test files):")
        out_lines.append("")
        out_lines.append("::")
        out_lines.append("")
        for line in format_table(
            agg_stats_rows, ["metric", "n", "mean", "sd", "min", "max"]
        ).splitlines():
            out_lines.append("    " + line)

    # Total time breakdown by mode and worker to compare threads vs processes
    # Build mapping (mode, workers) -> list of total_time
    mode_worker_values: Dict[tuple, List[float]] = defaultdict(list)
    file_pat = _re.compile(r".*_(\d+)_(process|thread)\.log$")
    for e in agg_entries:
        m = file_pat.match(e["file"]) or file_pat.match(e["file"].replace(".log", ""))
        if m:
            w = int(m.group(1))
            mode = m.group(2)
            tt = e.get("total_time") or 0.0
            try:
                mode_worker_values[(mode, w)].append(float(tt))
            except Exception:
                pass

    if mode_worker_values:
        mw_rows = []
        for (mode, w), vals in sorted(
            mode_worker_values.items(), key=lambda x: (x[0][0], x[0][1])
        ):
            s = compute_stats(vals)
            if not s:
                continue
            mw_rows.append(
                [
                    mode,
                    w,
                    s["n"],
                    f"{s['mean']:.6f}",
                    f"{s['sd']:.6f}",
                    f"{s['min']}",
                    f"{s['max']}",
                ]
            )
        if mw_rows:
            out_lines.append("")
            out_lines.append(
                "Total time by mode and worker (excluding FD test files) for test_snmp_*.py tests:"
            )
            out_lines.append("")
            out_lines.append("::")
            out_lines.append("")
            for line in format_table(
                mw_rows, ["mode", "workers", "n", "mean", "sd", "min", "max"]
            ).splitlines():
                out_lines.append("    " + line)
    # write out_lines to the chosen output file
    out_path = (
        Path(args.output) if args.output else (results_dir / "integration_summary.rst")
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        fh.write("""Integration tests summary
===========================

Generated: %s

""" % datetime.now(timezone.utc).isoformat())
        fh.write("\n".join(out_lines))
    print(f"Summary written to {out_path}")


if __name__ == "__main__":
    main()
