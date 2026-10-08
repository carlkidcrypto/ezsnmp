---
name: Auto Update Release Notes
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  job-discriminator: ${{ github.run_id }}
  cancel-in-progress: false
on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      backfill_all:
        description: 'Backfill release notes for ALL existing releases'
        required: false
        default: 'false'
      additional_context:
        description: 'Optional extra context or instructions to incorporate when generating release notes (e.g. "PyPI link format was fixed in this push")'
        required: false
        default: ''
permissions:
  actions: read
  contents: read
  copilot-requests: write
safe-outputs:
  update-release:
timeout-minutes: 20
max-ai-credits: 40
model: claude-sonnet-5
engine:
  id: copilot
network:
  allowed: [defaults, github, python]
tools:
  bash: true
---

# Auto Update Release Notes

When a new release is published, generate and update its release notes body on GitHub using commit history, PR references, and grouped themes.

## Goals

- Produce high-signal, human-readable release notes for every tagged release.
- Group changes into themes (bug fixes, features, CI/workflows, docs, dependencies, tests, etc.).
- Reference PR numbers and issue numbers where discoverable from commit messages.
- Include a PyPI install link for the released version.
- Fully overwrite the release body with the generated notes — no content from the previous body is preserved.
- Skip any release whose body contains the exact marker `<!-- PROTECTED -->` — these are manually curated and must never be touched.
- When triggered manually with `backfill_all: true`, reformat ALL existing releases to the same standard (respecting the skip marker).

## Steps

0. **Token & AIC Optimization (Helper Script)**:
   Use the deterministic helper script `.github/scripts/generate_release_notes.py` to minimize token consumption and AI Credit (AIC) usage. The script automatically executes base tag resolution, commit range extraction, theme grouping into the 9 categories, active verb title formatting, PyPI version linking, and skip-protected checks.

   - If triggered by `release: published`:
     Determine the published tag name from the release event, then execute:
     ```bash
     mkdir -p /tmp/gh-aw/agent
     python3 .github/scripts/generate_release_notes.py --tag <tag_name> --output-file /tmp/gh-aw/agent/release_notes.md
     ```
     (Pass `--additional-context "<context>"` if `additional_context` input is provided).
     Review `/tmp/gh-aw/agent/release_notes.md` and use the `update_release` tool (or run with `--publish`) to update the release.

   - If triggered by `workflow_dispatch` with `backfill_all: true`:
     Execute:
     ```bash
     python3 .github/scripts/generate_release_notes.py --backfill --publish
     ```
     (Append `--additional-context "<context>"` if `additional_context` input is provided).

   - If triggered by `workflow_dispatch` with `backfill_all: false` or unset:
     Execute:
     ```bash
     python3 .github/scripts/generate_release_notes.py --latest --publish
     ```
     (Append `--additional-context "<context>"` if `additional_context` input is provided).

   The steps below document the underlying deterministic specification implemented by the helper script:

1. Identify the release context:
   - Determine the tag name from the release being processed.
  - Determine whether the release is a prerelease from the GitHub release object (`prerelease: true|false`).
   - Derive the PyPI version string by stripping a leading `v` from the tag name (e.g., `v1.2.3` → `1.2.3`). If the tag contains no leading `v`, use the tag as-is.
   - Construct the PyPI URL: `https://pypi.org/project/ezsnmp/<pypi_version>/`
  - Determine a **base tag** using the following priority order (first match wins):
    1) If the release body contains an explicit override marker `<!-- BASE_TAG: <tag> -->`, use `<tag>` as base.
    2) If the current release is **stable** (`prerelease=false`), use the most recent earlier **stable** release tag by publish date.
    3) If the current release is **prerelease** (`prerelease=true`), use the most recent earlier release tag (stable or prerelease) by publish date.
    4) Fallback: use semantic-version sorting from git tags and pick the nearest lower version tag.
    5) Final fallback: use the repository root commit from `git rev-list --max-parents=0 HEAD`.
  - Validate that base and current are different; if equal, walk backward one more release/tag.
  - Log the selected base clearly: `Selected base for <current_tag>: <base_tag_or_root_commit>`.

2. Extract commits in the release range (Batching — Token Optimization):
  - Run a single batched git command: `git log <base_tag_or_root>..<current_tag> --name-only --format="COMMIT:%H%x09%s"`
  - Use the changed-file paths to improve categorization and identify user-facing changes (e.g. `ezsnmp/src/`, `ezsnmp/session.py`) vs process-only changes (`.github/workflows/`).
  - Collect PR numbers referenced (`(#NNN)`, `#NNN`, `Closes #NNN`, `Fixes #NNN`).
  - Collect issue numbers referenced using the same patterns.
  - Avoid running per-commit `git log` or `git show` commands in loops.

3. Group commits into themes. Use these categories (add others if clearly needed):
   - **Features / Enhancements** — new functionality or improvements to existing features.
   - **Bug Fixes** — corrections to defects.
  - **Runtime / Core Library** — behavior changes in the main library implementation (C/C++ sources, Python API wrappers, parsing, memory/thread/session behavior).
   - **Tests** — additions or updates to test suites (cpp_tests/, python_tests/, integration_tests/).
  - **Containers / Packaging** — Docker images, publish flows, wheel/build/publish behavior.
   - **CI / Workflows** — changes under `.github/workflows/` or build pipeline configuration.
   - **Documentation** — changes to docs, README, CHANGELOG, rst files.
   - **Dependencies** — version bumps, lockfile updates, requirements changes.
   - **Chores / Misc** — refactoring, code style, tooling, or anything that does not fit above.

  Infer category from BOTH commit metadata and changed paths. Do not rely only on commit titles.
  Prefer path-based classification when title-based and path-based signals disagree.
  If a commit touches multiple areas, place it in the most user-impacting section and mention secondary impact in the bullet text.

4. Build the release notes body:
  - Start with a brief one- or two-sentence summary of what this release contains, derived from the grouped themes and emphasizing user-facing changes first.
  - Add a line after the summary: `Compared to: <base_tag_or_root_commit>`.
   - Add a PyPI install block immediately after the summary (see format below).
   - List each non-empty group as a markdown section `## <Theme>`, with bullet points for each commit.
  - Each bullet point format: `- <human-readable change summary> (<#PR or short hash>)`.
  - Rewrite terse commit titles into natural language when needed, and include impact words such as "fixes", "improves", "prevents", "adds", or "supports".
  - Keep CI/dependency churn concise; prioritize concrete runtime, API, reliability, compatibility, and test-coverage outcomes.
   - If PR numbers are available, link them in the format `(#NNN)`.
   - If no commits fall in a category, omit that section entirely.
  - End with a **Full Changelog** line: `**Full Changelog**: https://github.com/carlkidcrypto/ezsnmp/compare/<base_tag>...<current_tag>`.

5. Update the GitHub release:
   - Before writing, fetch the current release body via the GitHub API.
   - If the body contains the exact string `<!-- PROTECTED -->` anywhere, skip this release entirely and log: `Skipping <tag>: marked <!-- PROTECTED -->`.
   - Otherwise, fully overwrite the release body using the GitHub API.
   - Endpoint: `PATCH /repos/carlkidcrypto/ezsnmp/releases/<release_id>`
   - Set the `body` field to the generated release notes. Do not carry over any previous content.

## Constraints

- Always fully overwrite the release body. Never append to or merge with existing content.
- Never modify a release whose body contains `<!-- PROTECTED -->`. Log the skip and move on.
- In `release: published` mode, only update the body of the triggering release.
- In `workflow_dispatch` backfill mode, update all releases returned by the GitHub API (except those with `<!-- PROTECTED -->`).
- Do not push commits or open PRs.
- Do not modify any files in the repository.
- If tag/release history is unavailable or the commit range is empty, write a minimal note stating the release was published with the PyPI link and include the computed base context.
- Omit empty theme sections from the output.
- If the PyPI version string cannot be derived from the tag, skip the Install / Upgrade section for that release and note it in the job log.
- Process backfill releases serially to avoid GitHub API rate limits; add a short delay between requests if throttling is detected.
- Never choose a prerelease base for a stable release if an earlier stable release exists.
- Use repository-aware language: mention concrete components (SNMP ops, session lifecycle, thread safety, Docker matrix, docs publishing) when those areas changed.
- Consult the `release-notes-template` skill for the release notes Markdown format.

## skill: `release-notes-template`
---
description: Layout and markdown template for generating GitHub release notes.
---

### Release Notes Body Format

```markdown
<One or two sentence summary of the release.>

Compared to: <base_tag_or_root_commit>

## Install / Upgrade

```bash
pip install ezsnmp==<pypi_version>
```

Or browse this release on PyPI: https://pypi.org/project/ezsnmp/<pypi_version>/

## Features / Enhancements
- <commit title> (#PR or short hash)

## Bug Fixes
- <commit title> (#PR or short hash)

## Runtime / Core Library
- <commit title> (#PR or short hash)

## Tests
- <commit title> (#PR or short hash)

## Containers / Packaging
- <commit title> (#PR or short hash)

## CI / Workflows
- <commit title> (#PR or short hash)

## Documentation
- <commit title> (#PR or short hash)

## Dependencies
- <commit title> (#PR or short hash)

## Chores / Misc
- <commit title> (#PR or short hash)

---
**Full Changelog**: https://github.com/carlkidcrypto/ezsnmp/compare/<base_tag>...<current_tag>
```