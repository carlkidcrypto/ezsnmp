---
name: Sync Open PRs With Main
on:
  workflow_dispatch:
  schedule: daily
permissions:
  copilot-requests: write
  actions: read
  contents: read
  pull-requests: read
timeout-minutes: 15
max-ai-credits: 20
model: sonnet
imports:
  - carlkidcrypto/shared-workflows/shared/sync-open-prs.md@3538efdfabdbcf0ae956cfc5685fd4c21a59696b
---

# Sync Open Pull Requests With Main

Keep open pull requests in `carlkidcrypto/ezsnmp` current by merging the latest `main` branch into PR branches carrying the `auto-sync` label, following the shared sync workflow rules.

## Constraints

- Do not modify `main` directly.
- Only update open PR branches that have the `auto-sync` label applied by a maintainer.
- If a merge would change protected files, do not force the push; rely on protected-file fallback handling.