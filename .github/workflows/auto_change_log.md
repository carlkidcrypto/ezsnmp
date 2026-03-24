---
name: Update Changelog
concurrency:
  group: ${{ github.workflow }}
  cancel-in-progress: false
on:
  release:
    types: [published]
  skip-if-match:
    query: 'is:pr is:open head:automation/update-changelog label:documentation label:automated-pr'
permissions:
  actions: read
  contents: read
safe-outputs:
  create-pull-request:
    title-prefix: "[changelog] "
    labels: [documentation, automated-pr]
    draft: false
    preserve-branch-name: true
    if-no-changes: "ignore"
timeout-minutes: 30
engine:
  id: copilot
  model: auto
network:
  allowed: [defaults, github]
tools:
  bash: true
---

# Smart Changelog Update

Generate and open a changelog update PR only when substantive changelog content has changed.

## Goals

- Keep `CHANGELOG.md` updated from git tags and commits using `git-chglog`.
- Avoid noise PRs when only timestamp/header differences would change.
- Keep one long-lived automation branch for easy updates.
- Produce a high-signal summary by analyzing commit titles/messages and PR titles.

## Steps

1. Prepare tooling and history:
   - Ensure full git history and tags are available.
   - If `git-chglog` is missing, install it with:
     - `go install github.com/git-chglog/git-chglog/cmd/git-chglog@latest`

2. Generate candidate changelog content:
   - `git-chglog --config .chglog/config.yml -o CHANGELOG.tmp`

3. Build commit intelligence context for summary quality:
  - Determine the comparison range using the latest reachable tag when possible.
  - Extract commit titles and full commit messages for the range.
  - If commit messages reference PRs or issue numbers, include those references in your reasoning.
  - Group changes into themes inferred from commit titles/messages (for example: bug fixes, CI/workflows, docs, dependencies, tests).

4. Perform smart diff detection:
   - If `CHANGELOG.md` exists and starts with `Last Updated:`, compare against the old file with the first two lines removed.
   - Otherwise compare against the full existing file.
   - If no substantive difference exists, stop with no-op.

5. If substantive changes exist, build final `CHANGELOG.md`:
   - Add a header line: `Last Updated: <UTC timestamp>`
   - Add one blank line
   - Append the generated changelog body from `CHANGELOG.tmp`

6. Create or update a PR with:
   - Branch: `automation/update-changelog`
   - Base: `main`
   - Title: `Update CHANGELOG.md`
   - Commit message: `chore(docs): update changelog`

## Pull Request Body Requirements

Include:

- Trigger source (`release`, `push`, or `workflow_dispatch`)
- Whether a release tag triggered this run (if available)
- Summary of notable top-level sections changed in `CHANGELOG.md`
- A concise, commit-driven "What changed" summary derived from commit titles/messages
- A "Grouped themes" section showing categorized changes inferred from commit text
- Mention of notable PR numbers/issues inferred from commit references when available
- A note that timestamp-only changes are filtered out

## Constraints

- Only modify `CHANGELOG.md`.
- Do not make unrelated code or workflow edits.
- If generation fails due to missing tags/history, report clearly and stop.