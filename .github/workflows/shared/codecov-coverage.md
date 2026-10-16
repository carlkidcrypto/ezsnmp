---
# Shared import: pre-fetch Codecov coverage data for agentic coverage workflows.
# The fetch runs as a custom step before the agent (outside the agent firewall),
# so the agent always has Codecov data even if it cannot reach Codecov itself.
network:
  allowed:
    - app.codecov.io
    - api.codecov.io
steps:
  - name: Fetch Codecov coverage report
    env:
      CODECOV_BRANCH: main
      CODECOV_OUTPUT_DIR: /tmp/gh-aw/agent/codecov
    run: python3 .github/scripts/fetch_codecov_report.py
---

## Codecov Coverage Data (pre-fetched)

Codecov coverage for the `main` branch of this repository has already been downloaded
for you before this run started:

- `/tmp/gh-aw/agent/codecov/summary.md` — overall and per-flag totals, plus every file
  with missed or partial lines (with line numbers). **Read this first.**
- `/tmp/gh-aw/agent/codecov/report.json` and `report-<flag>.json` — raw Codecov report
  API responses (`line_coverage` entries are `[line, status]` where `0` = hit, `1` = miss,
  `2` = partial). Use `jq`/`python3` with targeted queries; do not dump them in full.

Rules for using this data:

- Treat the Codecov summary as the primary source of coverage gaps. Map each missed line
  back to the source with targeted `sed -n '<start>,<end>p' <file>` reads before writing tests.
- You may also query `https://api.codecov.io/api/v2/github/<owner>/repos/<repo>/report/?branch=main`
  directly if you need fresher or more specific data (e.g. `&path=<file>` or `&flag=<flag>`).
- Do **not** conclude "coverage could not be checked" when the summary contains data.
  If the summary lists missed lines in files you are allowed to test, you must attempt to
  cover at least one of them before deciding no change is needed.
- Only if the summary says Codecov data is unavailable should you fall back to local
  coverage runs or static gap analysis.
