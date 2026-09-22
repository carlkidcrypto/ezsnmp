---
name: Docs Continuous Improvement Every 3 Days
on:
  workflow_dispatch:
  schedule: every 3 days
  skip-if-match:
    query: 'is:pr is:open head:automation/docs-continuous-improvement label:documentation label:automated-pr'
permissions:
  copilot-requests: write
  actions: read
  contents: read
safe-outputs:
  create-pull-request:
    title-prefix: "[docs-improvement] "
    labels: [documentation, automated-pr]
    draft: true
    preserve-branch-name: true
    if-no-changes: "ignore"
timeout-minutes: 15
max-ai-credits: 25
model: claude-sonnet-5
engine:
  id: copilot
---

# Documentation Continuous Improvement

Review and improve repository documentation gradually over time.

## Scope

Audit and improve:

- `README.rst`
- `docs/**`
- `HOWTOAI.rst`
- inline docstrings in Python files under `ezsnmp/**`
- comments/doc text in interface/docs-related files where clearly incorrect or missing

## Hard Requirements & Scope Limits (Token Optimization)

- **Single-Target Scope**: Limit each run to at most 1–2 documentation files or 1 Python module's docstrings (1–3 focused improvements maximum). Do not attempt a repo-wide audit in a single run.
- **Bounded file reads**: Files larger than 20 KB must **not** be read in full. Use targeted `grep`, `head`, `tail`, or line-range views.
- **Turn Budget**: Complete inspection and edits within 10–12 turns. If no clear improvements are found, stop cleanly without editing.

## Goals

- Fix typos, grammar, and broken wording
- Fix inaccurate or misleading statements
- Improve clarity where current text could cause user confusion
- Add or correct missing/incorrect Python docstrings for public functions/classes
- Keep edits small and focused each run (no massive rewrites)

## Constraints

- Do not change API behavior or runtime logic; documentation-only edits
- Avoid changing generated artifacts
- If no meaningful improvements are found, do not edit files
- When opening the PR, consult the `pull-request-guide` skill.

## skill: `pull-request-guide`
---
description: Conventions and required body contents for documentation improvement PRs.
---

### Pull Request Output

When changes are made, create or update one PR:
- Branch: `automation/docs-continuous-improvement`
- Base: `main`
- Title style: `[docs-improvement] <short summary>`

PR body must include:
- Files updated
- Types of improvements (typos, clarifications, docstrings, etc.)
- Any follow-up documentation gaps discovered