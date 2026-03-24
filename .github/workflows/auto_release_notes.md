---
name: Auto Update Release Notes
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
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
permissions:
  actions: read
  contents: read
safe-outputs:
  update-release:
timeout-minutes: 60
engine:
  id: copilot
  model: auto
network:
  allowed: [defaults, github]
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

0. Determine the run mode:
   - If triggered by `release: published`, process only the triggering release tag.
   - If triggered by `workflow_dispatch` with `backfill_all: true`, fetch all releases via the GitHub API and process each one in chronological order (oldest first). For each release, follow steps 1–5 below.
   - If triggered by `workflow_dispatch` with `backfill_all: false` or unset, stop with a message explaining that `backfill_all` must be set to `true` for manual runs.

1. Identify the release context:
   - Determine the tag name from the release being processed.
   - Derive the PyPI version string by stripping a leading `v` from the tag name (e.g., `v1.2.3` → `1.2.3`). If the tag contains no leading `v`, use the tag as-is.
   - Construct the PyPI URL: `https://pypi.org/project/ezsnmp/<pypi_version>/`
   - Determine the previous tag by running: `git tag --sort=-version:refname | grep -v "^<current_tag>$" | head -1`
   - If no previous tag exists, use the first commit as the base: `git rev-list --max-parents=0 HEAD`

2. Extract commits in the release range:
   - Run: `git log <previous_tag>..<current_tag> --pretty=format:"%H %s"` to get commit hashes and titles.
   - For each commit, also retrieve the full message body with: `git log -1 --pretty=format:"%b" <hash>`
   - Collect any PR numbers referenced (patterns: `(#NNN)`, `#NNN`, `Closes #NNN`, `Fixes #NNN`, `Resolves #NNN`).
   - Collect any issue numbers referenced using the same patterns.

3. Group commits into themes. Use these categories (add others if clearly needed):
   - **Features / Enhancements** — new functionality or improvements to existing features.
   - **Bug Fixes** — corrections to defects.
   - **Tests** — additions or updates to test suites (cpp_tests/, python_tests/, integration_tests/).
   - **CI / Workflows** — changes under `.github/workflows/` or build pipeline configuration.
   - **Documentation** — changes to docs, README, CHANGELOG, rst files.
   - **Dependencies** — version bumps, lockfile updates, requirements changes.
   - **Chores / Misc** — refactoring, code style, tooling, or anything that does not fit above.

   Infer category from the conventional commit prefix if present (`feat:`, `fix:`, `test:`, `ci:`, `docs:`, `chore:`, `build:`, `deps:`), otherwise infer from the commit title wording.

4. Build the release notes body:
   - Start with a brief one- or two-sentence summary of what this release contains, derived from the grouped themes.
   - Add a PyPI install block immediately after the summary (see format below).
   - List each non-empty group as a markdown section `## <Theme>`, with bullet points for each commit.
   - Each bullet point format: `- <commit title> (<#PR or short hash>)`
   - If PR numbers are available, link them in the format `(#NNN)`.
   - If no commits fall in a category, omit that section entirely.
   - End with a **Full Changelog** line: `**Full Changelog**: https://github.com/carlkidcrypto/ezsnmp/compare/<previous_tag>...<current_tag>`

5. Update the GitHub release:
   - Before writing, fetch the current release body via the GitHub API.
   - If the body contains the exact string `<!-- PROTECTED -->` anywhere, skip this release entirely and log: `Skipping <tag>: marked <!-- PROTECTED -->`.
   - Otherwise, fully overwrite the release body using the GitHub API.
   - Endpoint: `PATCH /repos/carlkidcrypto/ezsnmp/releases/<release_id>`
   - Set the `body` field to the generated release notes. Do not carry over any previous content.

## Release Notes Body Format

```
<One or two sentence summary of the release.>

## Install / Upgrade

```bash
pip install ezsnmp==<pypi_version>
```

Or browse this release on PyPI: https://pypi.org/project/ezsnmp/<pypi_version>/

## Features / Enhancements
- <commit title> (#PR or short hash)

## Bug Fixes
- <commit title> (#PR or short hash)

## Tests
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
**Full Changelog**: https://github.com/carlkidcrypto/ezsnmp/compare/<previous_tag>...<current_tag>
```

## Constraints

- Always fully overwrite the release body. Never append to or merge with existing content.
- Never modify a release whose body contains `<!-- PROTECTED -->`. Log the skip and move on.
- In `release: published` mode, only update the body of the triggering release.
- In `workflow_dispatch` backfill mode, update all releases returned by the GitHub API (except those with `<!-- PROTECTED -->).
- Do not push commits or open PRs.
- Do not modify any files in the repository.
- If tag history is unavailable or the commit range is empty, write a minimal note stating the release was published with the PyPI link and stop.
- Omit empty theme sections from the output.
- If the PyPI version string cannot be derived from the tag, skip the Install / Upgrade section for that release and note it in the job log.
- Process backfill releases serially to avoid GitHub API rate limits; add a short delay between requests if throttling is detected.
