#!/usr/bin/env python3
"""Reproduce and verify issue #1519 (per-Session open/close memory lifecycle).

Supports four modes matching GitHub issue #1519:
- open:   open and close a new Session each iteration without making a request
- get:    open a new Session, execute one SNMP GET, and close it each iteration
- walk:   open a new Session, execute one SNMP WALK, and close it each iteration
- shared: reuse a single Session for all SNMP WALK iterations
"""

from __future__ import annotations

import sys
from ezsnmp import Session


def rss_kib() -> int:
    """Return current resident set size (RSS) in KiB on Linux (/proc/self/statm)."""
    try:
        with open("/proc/self/statm", encoding="utf-8") as f:
            return int(f.read().split()[1]) * 4
    except OSError:
        return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "get"
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 16101

    kwargs = {
        "hostname": "127.0.0.1",
        "port_number": port,
        "version": 1,
        "community": "public",
        "timeout": 1,
        "retries": 0,
    }
    shared = Session(**kwargs) if mode == "shared" else None
    step = max(1, iterations // 4)

    for i in range(iterations + 1):
        if mode == "shared" and shared is not None:
            results = shared.walk(".1.3.6.1.2.1.1")
        elif mode == "walk":
            with Session(**kwargs) as s:
                results = s.walk(".1.3.6.1.2.1.1")
        elif mode == "get":
            with Session(**kwargs) as s:
                results = s.get([".1.3.6.1.2.1.1.1.0"])
        else:
            with Session(**kwargs):
                results = ()
        del results
        if i % step == 0:
            print(f"{mode:6s} iter={i:4d} rss={rss_kib()} KiB", flush=True)

    if shared is not None:
        shared.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
