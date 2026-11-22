---
# Shared import: standard safe-outputs and permissions for draft-PR-creating gh-aw workflows.
permissions:
  actions: read
  contents: read
  copilot-requests: write
safe-outputs:
  noop:
    report-as-issue: true
  create-pull-request:
    labels: [automated-pr]
    draft: true
    preserve-branch-name: true
    if-no-changes: "ignore"
---

## Automated Pull Request Output Rules

- Create or update at most **one** draft Pull Request per workflow run.
- Do not open a PR if no meaningful changes were produced; emit `noop` with a brief summary instead.
- Include a concise summary of changes and validation commands executed in the PR body.
