---
name: Coverage Autofix Every 3 Days
on:
  schedule:
    - cron: "0 9 */3 * *"
  workflow_dispatch:
  skip-if-match:
    query: 'is:pr is:open head:automation/coverage-autofix-every-3-days label:automated-pr'
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
    allowed: [coverage, tests, cpp, python]
    max: 4
timeout-minutes: 45
engine:
  id: copilot
  model: auto
network:
  allowed: [defaults, python]
tools:
  edit:
  bash: true
---

# Coverage Checks And Suggested Fixes

Run an end-to-end coverage health check for both Python and C++ tests, then
propose and implement minimal, safe fixes that improve coverage and reliability.

## Hard Requirements

- Focus only on this repository.
- Keep changes scoped and low-risk.
- Prefer tests first when improving coverage.
- Run coverage checks in both native and Dockerized environments for Python and C++.
- Dockerized checks must cover this distro set used by the repo workflows:
  almalinux10_netsnmp_5.9, archlinux_netsnmp_5.7, archlinux_netsnmp_5.8,
  archlinux_netsnmp_5.9, centos7_netsnmp_5.7, centos8_netsnmp_5.8,
  rockylinux8_netsnmp_5.8, rockylinux9_netsnmp_5.9.
- Do not open a new pull request if an open automation PR already exists for
  branch `automation/coverage-autofix-every-3-days`.
- If no meaningful change is needed, make no file edits and end cleanly.

## Coverage Check Procedure

1. Prepare Python dependencies and run Python tests with coverage:
   - `python -m pip install --upgrade pip`
   - `python -m pip install -r python_tests/requirements.txt`
   - `python -m pip install tox`
   - `tox -e py312`
   - Read coverage from `coverage.xml` when available.

2. Run C++ tests and coverage from `cpp_tests/` on Linux:
   - `meson setup build || true`
   - `ninja -C build`
   - `meson test -C build --print-errorlogs`
   - `lcov --capture --directory build --output-file coverage.info --ignore-errors mismatch,inconsistent || true`
   - If `coverage.info` exists, filter external/system paths before evaluating totals.

3. Run Dockerized Python tests and coverage across the distro set above.
  For each distro:
  - Pull `carlkidcrypto/ezsnmp_test_images:<distro>-latest`
  - Start a container with the repo mounted at `/ezsnmp`
  - Run Python tests in-container with at least `tox -e py312`
  - Collect and evaluate `coverage.xml` for that distro
  - Treat any per-distro Python test failure as actionable

4. Run Dockerized C++ tests and coverage across the same distro set.
  For each distro:
  - Run `docker/run_cpp_tests_in_all_dockers.sh <distro>`
  - Collect and evaluate `docker/test_outputs_<distro>/lcov_coverage.info`
  - Treat any per-distro C++ test failure as actionable

5. Determine if action is needed:
   - If Python or C++ coverage is below 99%, or tests reveal clear reliability
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

## Pull Request Output

When changes exist, create exactly one PR using this fixed branch name:

- Branch: `automation/coverage-autofix-every-3-days`
- Base: `main`
- Title style: `[coverage-autofix] <short summary>`
- PR body must include:
  - Native Python coverage before/after (if measurable)
  - Native C++ coverage before/after (if measurable)
  - Dockerized Python coverage before/after by distro (if measurable)
  - Dockerized C++ coverage before/after by distro (if measurable)
  - Summary of tests added/updated
  - Any limitations or follow-up recommendations

After creating the PR, attempt a best-effort follow-up label step:

- Add supplemental labels to the created PR when possible: `coverage`, `tests`,
  `cpp`, `python`.
- Treat this as non-critical metadata enrichment. If supplemental labeling fails,
  do not treat the run as a primary failure and do not abandon the created PR.

If no changes are required, report that coverage checks passed without actionable
improvements.
