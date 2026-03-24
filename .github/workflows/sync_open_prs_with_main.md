---
name: Sync Open PRs With Main
on:
  workflow_dispatch:
  schedule: daily
permissions:
  actions: read
  contents: read
  pull-requests: read
safe-outputs:
  push-to-pull-request-branch:
    target: "*"
    labels: [auto-sync]
    protected-files: fallback-to-issue
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
   - **Only emit one `push_to_pull_request_branch` safe output per run** — process the first eligible PR and stop. Do not queue multiple push outputs in a single execution.
3. If merge succeeds and produces changes, push to that PR branch.
4. If merge conflict occurs, skip that PR and continue others.
5. If no PR branches can be updated, emit a no-op result.

## Constraints

- Do not modify main directly.
- Only update open PR branches that have the `auto-sync` label applied by a maintainer.
- Do not push to PRs without the `auto-sync` label — they are intentionally excluded.
- If a merge would change protected files, do not force the push; rely on protected-file fallback handling.
- Keep commit messages clear, e.g.:
  - chore: merge main into PR branch
