---
# Shared import: core configuration and prompt instructions for auto_release_notes.md workflows.
permissions:
  actions: read
  contents: read
  copilot-requests: write
safe-outputs:
  noop:
    report-as-issue: true
  update-release:
timeout-minutes: 20
max-ai-credits: 40
model: sonnet
engine:
  id: copilot
network:
  allowed: [defaults, github, python]
tools:
  github:
    mode: gh-proxy
    toolsets: [repos]
  bash: true
---

## Auto Update Release Notes Core Workflow

When a release is published (or `workflow_dispatch` is triggered), generate and update its GitHub release notes body using commit history, PR references, and grouped themes:

1. **Protected Release Guard**: Skip any release whose body contains `<!-- PROTECTED -->`.
2. **Deterministic Helper Execution**:
   - Single release (`release: published`):
     ```bash
     mkdir -p /tmp/gh-aw/agent
     python3 .github/scripts/generate_release_notes.py --tag "${{ github.event.release.tag_name }}" --output-file /tmp/gh-aw/agent/release_notes.md
     ```
   - Full backfill (`backfill_all: true`):
     ```bash
     python3 .github/scripts/generate_release_notes.py --backfill --publish
     ```
3. **Theme Grouping & PyPI Link**: Group changes into standard categories (Features / Enhancements, Bug Fixes, API / Core Library, Tests, Packaging, CI / Workflows, Documentation, Dependencies, Chores / Misc), include the PyPI install snippet when applicable, and update the release via `update_release`.
