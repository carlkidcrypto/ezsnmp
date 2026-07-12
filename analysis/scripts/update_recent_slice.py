#!/usr/bin/env python3
"""Regenerate the recent_N slice CSV from the canonical overview CSV.

Agent notes
-----------
``recent_20.csv`` is a *derived* convenience view, not a primary data source.
Do NOT append to it directly.  Whenever new rows are added to overview.csv (by
``collect_integration_test_history.py``), run this script to rebuild the slice
with the updated top-N entries.

The slice is always the N most-recent rows by the ``updated_at`` column, which
is already sorted newest-first in overview.csv.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"

CSV_OVERVIEW = DATA_DIR / "integration_test_results_history_overview.csv"
CSV_RECENT_TMPL = "integration_test_results_history_recent_{n}.csv"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the recent_N slice CSV from overview.csv"
    )
    parser.add_argument(
        "--n",
        type=int,
        default=20,
        help="Number of most-recent rows to include (default: 20)",
    )
    parser.add_argument(
        "--overview",
        default=str(CSV_OVERVIEW),
        help=f"Path to overview CSV (default: {CSV_OVERVIEW})",
    )
    parser.add_argument(
        "--out",
        default=None,
        help=(
            "Output CSV path.  Defaults to "
            "data/integration_test_results_history_recent_<N>.csv "
            "next to the overview file."
        ),
    )
    args = parser.parse_args()

    overview_path = Path(args.overview)
    if not overview_path.exists():
        print(f"ERROR: overview CSV not found: {overview_path}")
        return 1

    with overview_path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    # overview.csv is already sorted newest-first; take first N rows
    recent = rows[: args.n]

    if args.out:
        out_path = Path(args.out)
    else:
        out_name = CSV_RECENT_TMPL.format(n=args.n)
        out_path = overview_path.parent / out_name

    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(recent)

    print(
        f"Written: {out_path}"
        f" ({len(recent)} rows, newest-{args.n} slice from {len(rows)} total)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
