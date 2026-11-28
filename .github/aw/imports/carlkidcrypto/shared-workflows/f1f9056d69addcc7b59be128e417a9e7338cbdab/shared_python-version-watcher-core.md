---
# Shared import: core configuration and prompt instructions for python_version_watcher.md workflows.
permissions:
  actions: read
  contents: read
  copilot-requests: write
safe-outputs:
  noop:
    report-as-issue: true
  create-pull-request:
    title-prefix: "[python-version] "
    labels: [automated-pr]
    draft: true
    preserve-branch-name: true
    if-no-changes: "ignore"
    protected-files: allowed
timeout-minutes: 15
max-ai-credits: 25
model: sonnet
engine:
  id: copilot
network:
  allowed:
    - defaults
    - devguide.python.org
tools:
  edit:
  bash: true
---

## Python Version Watcher Core Workflow

Monitor `https://devguide.python.org/versions/` for changes to actively supported Python versions (`bugfix`, `security`, or `prerelease`) versus `end-of-life`:

1. Fetch the Python versions table:
   ```bash
   curl -fsSL https://devguide.python.org/versions/ -o /tmp/gh-aw/agent/pyversions.html
   ```
2. Compare active versions against the repository's package metadata (`setup.cfg` / `pyproject.toml` `python_requires`, `[tool:black]` `target-version`, and PyPI classifiers) and CI workflow `python-version` matrices.
3. Open a single draft PR only when supported versions have changed; otherwise call `noop`.
