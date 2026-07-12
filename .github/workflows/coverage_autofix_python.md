---
name: Coverage Autofix Python
on:
  schedule:
    - cron: "0 9 */3 * *"
  workflow_dispatch:
  skip-if-match:
    query: 'is:pr is:open head:automation/coverage-autofix-python label:automated-pr'
permissions:
  copilot-requests: write
  actions: read
  contents: read
safe-outputs:
  create-pull-request:
    title-prefix: "[coverage-autofix-py] "
    labels: [automated-pr]
    draft: true
    preserve-branch-name: true
    if-no-changes: "ignore"
  add-labels:
    target: "*"
    allowed: [coverage, tests, python]
    max: 4
timeout-minutes: 45
engine:
  id: copilot
  model: claude-sonnet-4.6
network:
  allowed: [defaults, python, containers]
tools:
  edit:
  bash: true
---

# Python Coverage Checks And Suggested Fixes

Run an end-to-end coverage health check for Python tests, then
propose and implement minimal, safe fixes that improve coverage and reliability.

## Hard Requirements

- Focus only on this repository.
- Keep changes scoped and low-risk.
- Prefer tests first when improving coverage.
- Run coverage checks inside a Docker container (the ezsnmp package requires
  net-snmp C libraries to build its native C++ extension, which are only
  available in the pre-built Docker test images).
- Do not open a new pull request if an open automation PR already exists for
  branch `automation/coverage-autofix-python`.
- If no meaningful change is needed, make no file edits and end cleanly.

## Coverage Check Procedure

1. Run Python tests with coverage inside a pre-built Docker container that has
   net-snmp libraries included. The ezsnmp package cannot be installed in the
   native runner environment because its C++ extension requires `libsnmp-dev` /
   `net-snmp-devel`, which are only available in the Docker test images.

   a. Pull the test image (try Docker Hub first, fall back to GHCR):
      ```
      docker pull carlkidcrypto/ezsnmp_test_images:archlinux_netsnmp_5.9-latest || \
        docker pull ghcr.io/carlkidcrypto/ezsnmp_test_images:archlinux_netsnmp_5.9-latest
      ```

   b. Run tests inside the container with the repository bind-mounted at
      `/ezsnmp`. This starts `snmpd` in the background, installs the package,
      and runs pytest with coverage. Coverage output files are written back to
      the host working directory via the bind mount:
      ```
      docker run --rm \
        -v "$(pwd):/ezsnmp" \
        carlkidcrypto/ezsnmp_test_images:archlinux_netsnmp_5.9-latest \
        bash -c "
          export PATH=/usr/local/bin:$PATH
          export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64
          export MALLOC_CHECK_=0
          export MALLOC_PERTURB_=0
          mkdir -p /etc/snmp
          cp /ezsnmp/configs/snmpd.conf /etc/snmp/snmpd.conf
          snmpd -C -c /etc/snmp/snmpd.conf &
          sleep 2
          python3 -m venv /tmp/gh-aw/agent/venv
          /tmp/gh-aw/agent/venv/bin/pip install -q -r /ezsnmp/python_tests/requirements.txt
          cd /ezsnmp && /tmp/gh-aw/agent/venv/bin/pip install -q .
          /tmp/gh-aw/agent/venv/bin/pytest -v -s -n auto --dist loadfile \
            --junitxml=/ezsnmp/test-results.xml \
            --cov=ezsnmp --cov-report=term-missing \
            --cov-report=xml:/ezsnmp/coverage.xml \
            --cov-config=/ezsnmp/.coveragerc \
            /ezsnmp/python_tests/
        "
      ```

   - Read coverage from `coverage.xml` when available.

2. Determine if action is needed:
   - If Python coverage is below 99%, or tests reveal clear reliability
     gaps, create targeted fixes.
   - If current coverage looks healthy and no concrete improvement is justified,
     do not change code.

## Fix Strategy

- Prioritize:
  - Adding missing test coverage for uncovered branches/paths.
  - Fixing brittle tests.
  - Small correctness fixes discovered while writing tests.
- Avoid broad refactors or unrelated formatting churn.
- Keep commits coherent and reviewable.

## Formatting Step (Final, Required)

After all code and test changes are complete, run the project formatters on any
modified files before committing. This step is mandatory and must be the last
step before creating the PR.

### Python — black

Run `black` on every Python file that was added or modified:

```
pip install black
black <modified_python_files>
```

If no Python files were changed, skip this sub-step.

Commit any formatting changes as part of the same PR branch before opening the
pull request.

## Pull Request Output

When changes exist, create exactly one PR using this fixed branch name:

- Branch: `automation/coverage-autofix-python`
- Base: `main`
- Title style: `[coverage-autofix-py] <short summary>`
- PR body must include:
  - Docker-based Python coverage before/after (if measurable)
  - Summary of tests added/updated
  - Any limitations or follow-up recommendations

After creating the PR, attempt a best-effort follow-up label step:

- Add supplemental labels to the created PR when possible: `coverage`, `tests`,
  `python`.
- Treat this as non-critical metadata enrichment. If supplemental labeling fails,
  do not treat the run as a primary failure and do not abandon the created PR.

If no changes are required, report that coverage checks passed without actionable
improvements.
