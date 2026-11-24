---
name: Docs Continuous Improvement
on:
  workflow_dispatch:
  schedule: every 3 days
  skip-if-match:
    query: 'is:pr is:open head:automation/docs-continuous-improvement label:documentation label:automated-pr'
permissions:
  copilot-requests: write
  actions: read
  contents: read
timeout-minutes: 15
max-ai-credits: 25
model: sonnet
imports:
  - carlkidcrypto/shared-workflows/shared/docs-continuous-improvement-core.md@eeefdd5c0a594d59ae86a09437b2de9bb57618a3
  - carlkidcrypto/shared-workflows/shared/pr-preflight-checklist.md@eeefdd5c0a594d59ae86a09437b2de9bb57618a3
---

# Documentation Continuous Improvement

Review and improve repository documentation gradually over time following the shared documentation continuous improvement core rules.

## Scope

Audit and improve:

- `README.rst`
- `docs/**`
- `HOWTOAI.rst`
- inline docstrings in Python files under `ezsnmp/**`
- comments/doc text in interface/docs-related files where clearly incorrect or missing

## Goals

- Fix typos, grammar, and broken wording
- Fix inaccurate or misleading statements
- Improve clarity where current text could cause user confusion
- Add or correct missing/incorrect Python docstrings for public functions/classes
- Keep edits small and focused each run (no massive rewrites)
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