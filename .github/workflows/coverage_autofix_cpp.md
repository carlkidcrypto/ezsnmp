---
name: Coverage Autofix C++
on:
  schedule:
    - cron: "0 9 */3 * *"
  workflow_dispatch:
  skip-if-match:
    query: 'is:pr is:open head:automation/coverage-autofix-cpp label:automated-pr'
permissions:
  actions: read
  contents: read
safe-outputs:
  create-pull-request:
    title-prefix: "[coverage-autofix] "
    labels: [automated-pr]
    draft: true
    preserve-branch-name: true
    if-no-changes: "ignore"
  add-labels:
    target: "*"
    allowed: [coverage, tests, cpp]
    max: 4
timeout-minutes: 45
engine:
  id: copilot
  model: claude-opus-4.8
network:
  allowed: [defaults]
tools:
  edit:
  bash: true
---

# C++ Coverage Checks And Suggested Fixes

Run an end-to-end coverage health check for C++ tests, then
propose and implement minimal, safe fixes that improve coverage and reliability.

## Hard Requirements

- Focus only on this repository.
- Keep changes scoped and low-risk.
- Prefer tests first when improving coverage.
- Run coverage checks in native environment.
- Do not open a new pull request if an open automation PR already exists for
  branch `automation/coverage-autofix-cpp`.
- If no meaningful change is needed, make no file edits and end cleanly.

## Coverage Check Procedure

1. Run C++ tests and coverage from `cpp_tests/` on Linux:
   - `meson setup build || true`
   - `ninja -C build`
   - `meson test -C build --print-errorlogs`
   - `lcov --capture --directory build --output-file coverage.info --ignore-errors mismatch,inconsistent || true`
   - If `coverage.info` exists, filter external/system paths before evaluating totals.

2. Determine if action is needed:
   - If C++ coverage is below 99%, or tests reveal clear reliability
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

### C++ — clang-format

Run `clang-format` on every C++ source or header file that was added or modified.
Do **not** run clang-format on SWIG interface files (`.i` files under
`ezsnmp/interface/`).

```
clang-format -i <modified_cpp_or_header_files>
```

If no C++ files were changed, skip this sub-step.

Commit any formatting changes as part of the same PR branch before opening the
pull request.

## Pull Request Output

When changes exist, create exactly one PR using this fixed branch name:

- Branch: `automation/coverage-autofix-cpp`
- Base: `main`
- Title style: `[coverage-autofix-cpp] <short summary>`
- PR body must include:
  - Native C++ coverage before/after (if measurable)
  - Summary of tests added/updated
  - Any limitations or follow-up recommendations

After creating the PR, attempt a best-effort follow-up label step:

- Add supplemental labels to the created PR when possible: `coverage`, `tests`,
  `cpp`.
- Treat this as non-critical metadata enrichment. If supplemental labeling fails,
  do not treat the run as a primary failure and do not abandon the created PR.

If no changes are required, report that coverage checks passed without actionable
improvements.
