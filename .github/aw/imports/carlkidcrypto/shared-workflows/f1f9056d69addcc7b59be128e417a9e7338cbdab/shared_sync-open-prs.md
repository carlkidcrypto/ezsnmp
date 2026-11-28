---
# Shared import: core configuration and prompt instructions for sync_open_prs_with_main.md workflows.
permissions:
  copilot-requests: write
  actions: read
  contents: read
  pull-requests: read
safe-outputs:
  noop:
    report-as-issue: true
  create-issue:
    labels: [auto-sync]
  push-to-pull-request-branch:
    target: "*"
    required-labels: [auto-sync]
    protected-files: fallback-to-issue
    if-no-changes: "ignore"
timeout-minutes: 15
max-ai-credits: 20
model: sonnet
engine:
  id: copilot
checkout:
  fetch-depth: 0
  fetch: ["*"]
---

## Sync Open Pull Requests With Main

Keep open pull requests current by merging the latest `main` branch into PR branches carrying the `auto-sync` label:

1. Find all open pull requests in this repository that carry the `auto-sync` label.
2. For each qualifying PR:
   - Skip if the PR comes from a fork without push permission or lacks the `auto-sync` label.
   - Checkout the PR branch locally (`git fetch origin && git checkout <branch>` or `git checkout -b <branch> origin/<branch>`).
   - Attempt to merge `origin/main` into the PR branch (`chore: merge main into PR branch`).
   - **Emit at most one `push_to_pull_request_branch` safe output per run** — process the first eligible PR and stop immediately.
3. If a merge conflict or push tool failure occurs, skip that PR and continue to the next one (do **not** call `report_incomplete`).
4. If no open PRs require syncing, call `noop` with a concise explanation. Keep total execution within 10–12 turns.
