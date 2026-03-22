---
name: Sync Open PRs With Main
on:
  workflow_dispatch:
  schedule: daily on weekdays
permissions:
  actions: read
  contents: read
safe-outputs:
  push-to-pull-request-branch:
    target: "*"
    labels: [auto-sync]
    if-no-changes: "ignore"
timeout-minutes: 45
engine:
  id: copilot
  model: auto
checkout:
  fetch-depth: 0
  fetch: ["*"]
---

# Sync Open Pull Requests With Main

Keep open pull requests current by merging the latest main branch into PR branches.

## Workflow

1. Find all open pull requests in this repository that carry the `auto-sync` label.
2. For each qualifying PR:
   - Skip if PR comes from a fork without push permission.
   - Skip if PR does not have the `auto-sync` label.
   - Fetch main and the PR branch.
   - Attempt to merge origin/main into the PR branch.
3. If merge succeeds and produces changes, push to that PR branch.
4. If merge conflict occurs, skip that PR and continue others.
5. If no PR branches can be updated, emit a no-op result.

## Constraints

- Do not modify main directly.
- Only update open PR branches that have the `auto-sync` label applied by a maintainer.
- Do not push to PRs without the `auto-sync` label — they are intentionally excluded.
- Keep commit messages clear, e.g.:
  - chore: merge main into PR branch
