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
  noop:
    report-as-issue: true
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
timeout-minutes: 20
max-ai-credits: 60
model: sonnet
engine:
  id: copilot
network:
  allowed: [defaults, containers, app.codecov.io, python, api.codecov.io, dev-tools]
tools:
  edit:
  bash: true
imports:
  - shared/codecov-coverage.md
---

# Python Coverage Checks And Suggested Fixes

Run an end-to-end coverage health check for Python tests, then
propose and implement minimal, safe fixes that improve coverage and reliability.

## Hard Requirements

- Focus only on this repository.
- Keep changes scoped and low-risk. Limit each run to at most 1 target test file (1–3 focused test cases).
- Prefer tests first when improving coverage.
- Do not open a new pull request if an open automation PR already exists for
  branch `automation/coverage-autofix-python`.
- If no meaningful change is needed, make no file edits and end cleanly.
- **Bounded file reads (Token Optimization)**:
  Files larger than 20 KB must **not** be read in full. Use targeted `grep`, `head`,
  `tail`, or line-range views. Avoid dumping full source or test files into context.

## Coverage Check Procedure

1. Use Codecov to identify coverage gaps:
   - Start with the pre-fetched Codecov data in `/tmp/gh-aw/agent/codecov/summary.md`
     (see "Codecov Coverage Data" below). Use the `Component python_code` section (Python
     Code, combining the `python-native` and `python-docker` flags); it lists every
     Python file under `ezsnmp/` with missed lines and their line numbers
     (dashboard: https://app.codecov.io/gh/carlkidcrypto/ezsnmp).
   - The C++ extension is not built in this sandbox, so you cannot run the Python test
     suite locally. That is expected: author tests statically for the missed lines that
     Codecov reports (read the code with bounded `sed -n` ranges, mirror the style of the
     closest existing test in `python_tests/`), and rely on CI to verify them.
   - If Codecov is unreachable or does not return data, inspect Python files under `ezsnmp/`
     and tests under `python_tests/` using targeted `grep` to identify untested branches,
     error handling paths, or missing test coverage.
   - Inability to build the extension or run tests locally is expected and is **not** a
     reason to skip: author the test statically and let CI/Codecov verify it. Only if Codecov
     reports no missed lines in testable files, or no test can be reasonably authored within
     10–12 turns, call `noop` explaining exactly which Codecov gaps you evaluated and why
     each was not actionable.

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
- When creating the pull request, consult the `pull-request-guide` skill.

## skill: `pull-request-guide`
---
description: Formatting rules, PR creation conventions, checklist items, and supplemental labels.
---

### Formatting Step (Required before PR)

Run `black` on every Python file that was added or modified:
```bash
pip install black
black <modified_python_files>
```
If no Python files were changed, skip this sub-step.

### Pull Request Output

When changes exist, create exactly one PR using this fixed branch name:
- Branch: `automation/coverage-autofix-python`
- Base: `main`
- Title style: `[coverage-autofix-py] <short summary>`
- PR body must include:
  - Summary of tests added/updated
  - A note that coverage verification must be performed by the reviewer via Codecov/CI.
  - Any limitations or follow-up recommendations

### Human Verification Task

Since local Docker-based verification is unavailable, you MUST create a task in the PR (e.g., as a checklist item or a comment) explicitly requesting the human reviewer to verify that the coverage has actually increased in the resulting CI run before merging.

After creating the PR, attempt a best-effort follow-up label step:
- Add supplemental labels: `coverage`, `tests`, `python`.
- Treat this as non-critical metadata enrichment. If labeling fails, do not treat the run as a failure.