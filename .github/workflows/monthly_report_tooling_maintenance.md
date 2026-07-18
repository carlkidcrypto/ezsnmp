---
name: Monthly Report Tooling Maintenance
on:
  workflow_dispatch:
  schedule:
    - cron: "0 9 1 * *"
  skip-if-match:
    query: 'is:pr is:open head:automation/monthly-report-tooling-maintenance label:automated-pr'
permissions:
  copilot-requests: write
  actions: read
  contents: read
  pull-requests: read
  issues: read
safe-outputs:
  create-pull-request:
    title-prefix: "[report-tooling] "
    labels: [automated-pr, documentation, ci]
    draft: true
    preserve-branch-name: true
    if-no-changes: "ignore"
timeout-minutes: 45
engine:
  id: copilot
  model: claude-sonnet-4.6
network:
  allowed: [defaults, github]
tools:
  edit:
  bash: true
---

# Monthly Report Tooling Maintenance

Review and maintain the repository's report-generation workflows, scripts, and
related documentation once per month.

## Scope

Use the existing report tooling and docs in this repository as the source of truth:

- `.github/workflows/valgrind_pr_history_report.yml`
- `.github/scripts/analyze_valgrind_pr_history.py`
- `.github/comment-valgrind-template.md`
- `.github/workflows/tests_homebrew.yml`
- `docker/generate_test_reports.sh`
- `docker/README.rst`
- `README.rst`

## Goals

- Keep report scripts and their documentation aligned.
- Fix small reliability issues in report tooling when they are directly discovered.
- Keep workflow and script changes small, safe, and focused.
- Open or update a single automation PR only when real changes are needed.

## Steps

1. Read the files in the Scope section before making changes.

2. Review the current Valgrind history report path:
   - Confirm `.github/workflows/valgrind_pr_history_report.yml` still matches the
     behavior of `.github/scripts/analyze_valgrind_pr_history.py`.
   - Run the existing analyzer script from the repository root with the current
     repository context:
     - `GITHUB_REPOSITORY=${GITHUB_REPOSITORY:-carlkidcrypto/ezsnmp} python .github/scripts/analyze_valgrind_pr_history.py`
   - Treat exit code `1` from this script as a report result meaning leak records
     were found, not as a workflow failure. Only treat missing credentials,
     missing repository context, syntax errors, or other unexpected exceptions as
     failures.
   - Use the generated `valgrind-pr-history-report.md` and
     `valgrind-pr-history-report.json` to inform whether any documentation or
     script wording is stale.

3. Review the Docker test summary path:
   - Read `docker/README.rst` and `docker/generate_test_reports.sh` together.
   - Run `docker/generate_test_reports.sh` only if one or more
     `docker/test_outputs_*` directories already exist in the working tree.
   - If no such directories exist, skip executing the Docker report script and
     only verify that the documentation accurately describes its prerequisites,
     filenames, and outputs.

4. Apply only minimal fixes that are directly justified by the review:
   - Documentation drift (wrong filenames, missing prerequisites, stale workflow
     descriptions, inaccurate output details).
   - Small script reliability fixes in the report tooling.
   - Small workflow fixes in `valgrind_pr_history_report.yml` when the workflow no
     longer matches the script it runs.

5. Do not make unrelated refactors, dependency upgrades, or formatting-only churn.

6. If no meaningful changes are needed, stop with a concise no-op summary.

7. If changes are needed, create or update one PR with:
   - Branch: `automation/monthly-report-tooling-maintenance`
   - Base: `main`
   - Title style: `[report-tooling] <short summary>`

## Pull Request Body

Include:

- The scripts, workflows, and docs reviewed
- Which files changed and why
- Whether the Valgrind history analyzer found leak signatures during the run
- Whether Docker `test_outputs_*` data was available for a local report run
- Any follow-up gaps that still need manual attention

## Constraints

- Use the existing repository scripts and documentation; do not replace them with
  new parallel tooling.
- Keep changes limited to report workflows, report scripts, and directly related
  documentation.
- Do not manually edit generated `.lock.yml` files.

## Scripts And Tools

As you develope scripts and tools to better do you job place them in the following location.
`.github/scripts/SCRIPTS_WITH_GOOD_NAMES_GO_HERE.py`

The scripts shall:

- Be written in python3
- Be maintained and updated as needed to help you better accomplish your job
- Modular and maintainable by both a human and Agent as needed
- Be well documented via python3 doc strings and function strings.