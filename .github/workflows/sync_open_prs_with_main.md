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
  create-issue:
    labels: [auto-sync]
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
   - Checkout the PR branch locally: run `git fetch origin` and then `git checkout <branch-name>` (if the local branch already exists) or `git checkout -b <branch-name> origin/<branch-name>` (if it does not exist locally yet). This ensures the branch exists locally before pushing, which is required by the push tool.
   - Attempt to merge origin/main into the PR branch.
   - **Only emit one `push_to_pull_request_branch` safe output per run** — process the first eligible PR and stop. Do not queue multiple push outputs in a single execution.
3. If merge succeeds and produces changes, push to that PR branch.
4. If merge conflict occurs, skip that PR and continue to the next one.
5. If the `push_to_pull_request_branch` tool fails for any technical reason (e.g., branch not found locally, patch generation error, or other tool malfunction), skip that PR and continue to the next one. Do **not** call `report_incomplete` for push tool failures.
6. If no open PRs have the `auto-sync` label, or no PR branches can be updated (all are already up to date, have merge conflicts, or the push tool failed), call the `noop` tool with a brief explanation such as "No open PRs with auto-sync label found" or "All qualifying PRs are already up to date with main".

## Constraints

- Do not modify main directly.
- Only update open PR branches that have the `auto-sync` label applied by a maintainer.
- Do not push to PRs without the `auto-sync` label — they are intentionally excluded.
- If a merge would change protected files, do not force the push; rely on protected-file fallback handling.
- Keep commit messages clear, e.g.:
  - chore: merge main into PR branch
