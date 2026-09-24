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
    labels: [automated-pr, coverage, tests, cpp]
    draft: true
    preserve-branch-name: true
    if-no-changes: "ignore"
    allowed-files:
      - "cpp_tests/**"
      - "ezsnmp/src/**"
      - ".github/scripts/**"
    excluded-files:
      - ".github/workflows/**"
    protected-files: allowed
timeout-minutes: 20
max-ai-credits: 60
model: claude-sonnet-5
engine:
  id: copilot
network:
  allowed: [defaults, containers, dev-tools, python]
tools:
  edit:
  bash: true
---

# C++ Coverage Checks And Suggested Fixes

Run an end-to-end coverage health check for C++ tests, then
propose and implement minimal, safe fixes that improve coverage and reliability.

## Hard Requirements

- Focus only on this repository.
- Keep changes scoped and low-risk. Limit each run to at most 1 target test file (1–3 focused test cases).
- Prefer tests first when improving coverage.
- **Allowed file modification paths**: Author or modify files in `cpp_tests/**` (e.g. `cpp_tests/test_*.cpp`, `cpp_tests/meson.build`), `ezsnmp/src/**`, and reusable analysis scripts under `.github/scripts/`.
- **Reusable scripts and tools**: You may create or improve reusable analysis scripts under `.github/scripts/` (e.g. `analyze_cpp_coverage_gaps.py`) to identify coverage gaps so that the agent and workflow get smarter over time.
- **Prohibited paths**: NEVER author, modify, or commit workflow files in `.github/workflows/**`, workflow lock files, root configuration files (`pyproject.toml`, `setup.py`), or repository manifests.
- Do not open a new pull request if an open automation PR already exists for
  branch `automation/coverage-autofix-cpp`.
- If no meaningful change is needed, make no file edits and end cleanly.
- **Do not install compiler toolchains or compile tests locally**:
  The sandbox environment lacks sudo and required build tools for full C++ builds.
  Do **not** attempt to install gcc, g++, meson, ninja, lcov, gdb, or create conda
  environments to compile or run `cpp_tests` locally; doing so exhausts the workflow
  timeout and token budget. Inspect and author C++ tests statically.
- **Bounded file reads (Token Optimization)**:
  Files larger than 20 KB must **not** be read in full. Use targeted `grep`, `head`,
  `tail`, or line-range views. Avoid dumping full source or test files into context.

## Coverage Check Procedure

1. Use Codecov and static gap analysis to identify coverage gaps:
   - Check Codecov reports for the `main` branch (https://app.codecov.io/gh/carlkidcrypto/ezsnmp).
   - Leverage existing analysis scripts under `.github/scripts/` (e.g. `python3 .github/scripts/analyze_cpp_coverage_gaps.py`) to statically identify branch and shim coverage gaps.
   - If Codecov is unreachable or does not return data, inspect the C++ source files
     under `ezsnmp/src/` and existing tests under `cpp_tests/` using targeted `grep` and
     scripts under `.github/scripts/` to identify untested branches, error handling paths, or missing assertions.
   - If no actionable gaps are found or test additions cannot be safely verified within
     10–12 turns, call `report_incomplete` or exit cleanly without editing files.

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
- When creating the pull request, consult the `pull-request-guide` skill.

## skill: `pull-request-guide`
---
description: Formatting rules, PR creation conventions, checklist items, and supplemental labels.
---

### Formatting Step (Required before PR)

Run `clang-format` on every C++ source or header file that was added or modified:
```bash
clang-format -i <modified_cpp_or_header_files>
```
Do **not** run clang-format on SWIG interface files (`.i` files under `ezsnmp/interface/`).

### Pull Request Output

When changes exist, create exactly one PR using this fixed branch name:
- Branch: `automation/coverage-autofix-cpp`
- Base: `main`
- Title style: `[coverage-autofix-cpp] <short summary>`
- PR body must include:
  - Summary of tests added/updated
  - A note that coverage verification must be performed by the reviewer via Codecov/CI.
  - Any limitations or follow-up recommendations
- Labels (`automated-pr`, `coverage`, `tests`, `cpp`) are attached automatically by `create-pull-request`; do not make separate labeling calls.

### Human Verification Task

Since local Docker-based verification is unavailable, you MUST create a task in the PR (e.g., as a checklist item or a comment) explicitly requesting the human reviewer to verify that the coverage has actually increased in the resulting CI run before merging.
