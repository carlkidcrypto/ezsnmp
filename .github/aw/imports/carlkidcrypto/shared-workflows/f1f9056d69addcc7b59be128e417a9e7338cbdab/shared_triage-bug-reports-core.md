---
# Shared import: core configuration and prompt instructions for triage_incoming_bug_reports.md workflows.
permissions:
  actions: read
  contents: read
  issues: read
  pull-requests: read
  copilot-requests: write
safe-outputs:
  noop:
    report-as-issue: true
  add-comment:
    target: triggering
    hide-older-comments: true
  add-labels:
    target: triggering
    allowed: [bug, needs-info, triaged]
  remove-labels:
    target: triggering
    allowed: [needs-info]
timeout-minutes: 10
max-ai-credits: 15
model: sonnet
engine:
  id: copilot
network:
  allowed: [defaults, github, api.github.com]
tools:
  bash: false
  cli-proxy: false
  github:
    min-integrity: none
---

## Bug Report Intake Triage Core Rules

1. **Gate**: Run triage only when the triggering event is an issue (not a PR) that carries the `bug` label or whose title starts with `[BUG]`. Otherwise emit `noop` with no comment or label changes.
2. **Intake Evaluation**: Score the required bug template sections (version/commit, OS, runtime/library versions, bug description, reproduction steps, expected behavior, and logs/context). Treat unchanged template placeholders (`[e.g. ...]`, `...`, unexplained `N/A`) as incomplete.
3. **Paths**:
   - **Incomplete Report**: Add `needs-info`, remove `triaged` if present, and post one concise checklist comment requesting the missing sections.
   - **Complete Report**: Remove `needs-info` if present, add `triaged`, and post one concise readiness summary.
4. **Constraints**: Never modify issue titles/bodies or close issues. Complete evaluation within 3–5 turns.
