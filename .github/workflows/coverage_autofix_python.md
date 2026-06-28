---
name: Coverage Autofix Python
on:
  schedule:
    - cron: "0 9 */3 * *"
  workflow_dispatch:
  skip-if-match:
    query: 'is:pr is:open head:automation/coverage-autofix-python label:automated-pr'
permissions:
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
  model: claude-opus-4.8
network:
  allowed: [defaults, python]
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
- Run coverage checks in native environment.
- Do not open a new pull request if an open automation PR already exists for
  branch `automation/coverage-autofix-python`.
- If no meaningful change is needed, make no file edits and end cleanly.

## Coverage Check Procedure

1. Prepare Python dependencies and run Python tests with coverage:
   - `python -m pip install --upgrade pip`
   - `python -m pip install -r python_tests/requirements.txt`
   - `python -m pip install .`
   - `pytest -v -s -n auto --dist loadfile --junitxml=test-results.xml --cov=ezsnmp --cov-report=term-missing --cov-report=xml:coverage.xml --cov-config=.coveragerc python_tests/`
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
  - Native Python coverage before/after (if measurable)
  - Summary of tests added/updated
  - Any limitations or follow-up recommendations

After creating the PR, attempt a best-effort follow-up label step:

- Add supplemental labels to the created PR when possible: `coverage`, `tests`,
  `python`.
- Treat this as non-critical metadata enrichment. If supplemental labeling fails,
  do not treat the run as a primary failure and do not abandon the created PR.

If no changes are required, report that coverage checks passed without actionable
improvements.
