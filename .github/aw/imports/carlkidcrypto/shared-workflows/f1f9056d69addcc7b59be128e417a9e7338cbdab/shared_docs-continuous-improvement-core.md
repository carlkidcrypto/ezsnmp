---
# Shared import: core configuration and prompt instructions for docs_continuous_improvement.md workflows.
permissions:
  copilot-requests: write
  actions: read
  contents: read
safe-outputs:
  noop:
    report-as-issue: true
  create-pull-request:
    title-prefix: "[docs-improvement] "
    labels: [documentation, automated-pr]
    draft: true
    preserve-branch-name: true
    if-no-changes: "ignore"
timeout-minutes: 15
max-ai-credits: 25
model: sonnet
engine:
  id: copilot
---

## Documentation Continuous Improvement Core Rules

- **Single-Target Scope**: Limit each run to at most 1–2 documentation files or 1 module's docstrings (1–3 focused improvements maximum). Never attempt a repository-wide rewrite in a single run.
- **Bounded File Reads**: Files larger than 20 KB must **not** be read in full; use targeted `grep`, `head`, `tail`, or line-range reads.
- **Turn Budget**: Complete inspection and edits within 10–12 turns. If no clear improvements are found, emit `noop` without modifying files.
- **Constraints**:
  - Do not change runtime logic or public API signatures; documentation and docstring edits only.
  - Do not modify generated build artifacts.
  - Run `.github/scripts/audit_docs.py` (when present) before finalizing edits.
