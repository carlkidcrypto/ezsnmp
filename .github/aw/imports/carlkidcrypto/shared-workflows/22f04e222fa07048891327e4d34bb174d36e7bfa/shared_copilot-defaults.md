---
# Shared import: default Copilot engine, model, and bounded-read token optimization rules.
model: sonnet
engine:
  id: copilot
---

## Token & Context Optimization Defaults

- **Bounded File Reads**: Files larger than 20 KB must **not** be read in full. Use targeted `grep`, `head`, `tail`, or line-range (`sed -n '<start>,<end>p'`) views.
- **Deterministic Helpers First**: Prefer calling deterministic scripts under `.github/scripts/` (or `scripts/`) instead of running ad-hoc multi-turn shell exploration.
- **Strict Turn Budget**: Complete inspection, edits, and safe-output submission within the workflow's designated turn budget. If no actionable work is found, emit `noop` and exit immediately.
