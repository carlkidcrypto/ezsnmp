---
name: Coverage Autofix C++
on:
  schedule:
    - cron: "0 9 */3 * *"
  workflow_dispatch:
  skip-if-match:
    query: 'is:pr is:open head:automation/coverage-autofix-cpp label:automated-pr'
permissions:
  copilot-requests: write
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
  model: claude-sonnet-4.6
network:
  allowed: [defaults, containers]
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
- Run coverage checks inside a Docker container (the ezsnmp C++ extension
  requires net-snmp headers, meson, ninja, and lcov, which are only reliably
  available in the pre-built Docker test images).
- Do not open a new pull request if an open automation PR already exists for
  branch `automation/coverage-autofix-cpp`.
- If no meaningful change is needed, make no file edits and end cleanly.

## Coverage Check Procedure

1. Run C++ tests with coverage inside a pre-built Docker container that has
   all required tools (meson, ninja, lcov, net-snmp headers) included.

   The `archlinux_netsnmp_5.9-latest` image is used here because it is the
   same distribution and net-snmp version used throughout the repository's CI
   test matrix; it always refers to the latest published build of that image.

   a. Pull the test image (try Docker Hub first, fall back to GHCR):
      ```
      docker pull carlkidcrypto/ezsnmp_test_images:archlinux_netsnmp_5.9-latest || \
        docker pull ghcr.io/carlkidcrypto/ezsnmp_test_images:archlinux_netsnmp_5.9-latest
      ```

   b. Run the cpp tests using the existing helper script inside the `docker/`
      directory. The script handles starting the container with the repository
      bind-mounted at `/ezsnmp`, running meson/ninja/lcov inside it, and saving
      coverage artifacts to `docker/test_outputs_archlinux_netsnmp_5.9/`:
      ```
      cd docker/
      chmod +x run_cpp_tests_in_all_dockers.sh
      ./run_cpp_tests_in_all_dockers.sh archlinux_netsnmp_5.9
      ```

   - Coverage output is written to
     `docker/test_outputs_archlinux_netsnmp_5.9/lcov_coverage.info`.
   - Test results are in
     `docker/test_outputs_archlinux_netsnmp_5.9/test-results.xml`.

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
