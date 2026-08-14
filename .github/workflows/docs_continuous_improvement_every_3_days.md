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
timeout-minutes: 45
engine:
  id: copilot
  model: claude-sonnet-4.6
---

# Documentation Continuous Improvement

Review and improve repository documentation gradually over time.

## Scope

Audit and improve:

- README.rst
- docs/**
- HOWTOAI.rst
- inline docstrings in Python files under ezsnmp/**
- comments/doc text in interface/docs-related files where clearly incorrect or missing

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

## Pull Request

If changes are made, create or update one PR:

- Branch: automation/docs-continuous-improvement
- Base: main
- Title style: [docs-improvement] <short summary>

PR body must include:

- Files updated
- Types of improvements (typos, clarifications, docstrings, etc.)
- Any follow-up documentation gaps discovered


## Scripts And Tools

As you develope scripts and tools to better do you job place them in the following location.
`.github/scripts/SCRIPTS_WITH_GOOD_NAMES_GO_HERE.py`

The scripts shall:

- Be written in python3
- Be maintained and updated as needed to help you better accomplish your job
- Modular and maintainable by both a human and Agent as needed
- Be well documented via python3 doc strings and function strings.