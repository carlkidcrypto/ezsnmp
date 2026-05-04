---
name: Triage Incoming Bug Reports
on:
  workflow_dispatch:
  issues:
    types: [opened, edited, reopened]
permissions:
  actions: read
  contents: read
  issues: read
safe-outputs:
  add-comment:
    target: triggering
    hide-older-comments: true
  add-labels:
    target: triggering
    allowed: [bug, needs-info, triaged]
  remove-labels:
    target: triggering
    allowed: [needs-info]
timeout-minutes: 20
engine:
  id: copilot
  model: auto
network:
  allowed: [defaults, github]
tools:
  bash: true
---

# Bug Report Intake Triage

Triage incoming bug reports and ensure required fields from the bug template are present and filled.

## Gate

Only run triage logic when all conditions are true:

- The event is for an issue (not a PR).
- The issue has the `bug` label or the title starts with `[BUG]`.

If not a bug report, post no comment and do no label changes.

## Required Sections

Validate these required template sections are present and meaningfully filled (not placeholders, not empty, not unchanged example text):

1. EzSNMP release version OR commit number
2. Operating System and Version
3. Python 3 Version
4. Net-SNMP Library Version
5. Describe the bug
6. To Reproduce (concrete reproducible steps)
7. Expected behavior
8. Additional context (logs, stack trace, debugger output, or explicit statement that none is available)

Treat the report as incomplete if values are placeholders such as:

- `[e.g. ...]`
- `...`
- `N/A` with no explanation in critical fields
- unchanged template examples

## Creative Triage Output

Compute a simple **Intake Score** from 0-8 based on the required sections above.

Then do exactly one of these paths:

### Path A: Incomplete Report (score < 8)

1. Add label `needs-info`.
2. Remove label `triaged` if present.
3. Add one concise triage comment that includes:
   - Intake score (`x/8`)
   - A checkbox list of missing or weak sections
   - A copy-paste reporter checklist asking for exact missing details
   - A friendly note that triage will continue automatically after they edit the issue

### Path B: Complete Report (score = 8)

1. Remove label `needs-info` if present.
2. Add label `triaged`.
3. Add one concise triage comment that includes:
   - Intake score (`8/8`)
   - A short summary of environment and reproduction signal quality
   - A note that the issue is ready for technical investigation

## Constraints

- Do not modify issue title/body.
- Do not close issues.
- Keep comments factual and brief.
- Avoid duplicate comments: rely on `hide-older-comments: true` and post only one fresh status comment per run.
