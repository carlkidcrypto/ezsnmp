---
name: Update Changelog
concurrency:
  group: ${{ github.workflow }}
  cancel-in-progress: false
on:
  release:
    types: [published]
  skip-if-match:
    query: 'is:pr is:open head:automation/update-changelog label:documentation label:automated-pr'
permissions:
  actions: read
  contents: read
safe-outputs:
  create-pull-request:
    title-prefix: "[changelog] "
    labels: [documentation, automated-pr]
    draft: false
    preserve-branch-name: true
    if-no-changes: "ignore"
timeout-minutes: 30
engine:
  id: copilot
  model: auto
network:
  allowed: [defaults, github]
tools:
  bash: true
---

# Smart Changelog Update

Generate and open a changelog update PR only when substantive changelog content has changed.

## Goals

- Keep `CHANGELOG.md` updated from git tags and commits using `git-chglog`.
- Avoid noise PRs when only timestamp/header differences would change.
- Keep one long-lived automation branch for easy updates.
- Produce a high-signal summary by analyzing commit titles/messages and PR titles.
- Be resilient to integrity filtering by relying on local git data for commit analysis.

## Steps

1. Prepare tooling and history:
   - Ensure full git history and tags are available.
   - Use local repository history for all commit analysis steps.
   - Do not call GitHub commit-reading APIs/tools (for example `list_commits`, `get_commit`) for changelog intelligence.
   - If `git-chglog` is missing, install it using the pre-built binary (fast — no compilation):
     ```
     curl -sSfL https://github.com/git-chglog/git-chglog/releases/download/v0.15.4/git-chglog_0.15.4_linux_amd64.tar.gz \
       | tar xz -C /usr/local/bin git-chglog
     ```
   - If the curl download fails, fall back to: `go install github.com/git-chglog/git-chglog/cmd/git-chglog@latest`
   - After installation, verify it works: `git-chglog --version`
   - **If git-chglog cannot be installed by either method, stop immediately with a clear error message. Do NOT attempt to re-implement changelog generation using Python, shell, or any other scripting language.**

2. Generate candidate changelog content:
   - `git-chglog --config .chglog/config.yml -o CHANGELOG.tmp`

3. Build commit intelligence context for summary quality:
   - Identify the current release tag from the triggering release.
   - Determine whether the triggering release is a prerelease (`prerelease: true|false`) from the GitHub release payload.
   - Select a comparison base using this priority order (first match wins):
     1) If the release body contains `<!-- BASE_TAG: <tag> -->`, use `<tag>`.
     2) For stable releases, use the most recent earlier stable release tag by publish date.
     3) For prereleases, use the most recent earlier release tag (stable or prerelease) by publish date.
     4) Fallback: choose the nearest lower semantic-version tag from git.
     5) Final fallback: use the repository root commit (`git rev-list --max-parents=0 HEAD`).
   - Validate that base and current are not equal; if equal, walk backward one more release/tag.
   - Extract commit titles from `<base>..<current>` using a **single** git command:
     - `git log <base>..<current> --pretty=format:"%s"`
   - If commit messages reference PRs or issue numbers, include those references in your reasoning.
   - Log the selected range: `Changelog range: <base>...<current>`.

4. Perform smart diff detection:
   - If `CHANGELOG.md` exists and starts with `Last Updated:`, compare against the old file with the first two lines removed.
   - Otherwise compare against the full existing file.
   - If no substantive difference exists, stop with no-op.

5. If substantive changes exist, build final `CHANGELOG.md`:
   - Add a header line: `Last Updated: <UTC timestamp>`
   - Add one blank line
   - Append the generated changelog body from `CHANGELOG.tmp`

6. Create or update a PR with:
   - Branch: `automation/update-changelog`
   - Base: `main`
   - Title: `Update CHANGELOG.md`
   - Commit message: `chore(docs): update changelog`

## Pull Request Body Requirements

Include:

- Trigger source (`release`, `push`, or `workflow_dispatch`)
- Whether a release tag triggered this run (if available)
- Explicit comparison range used (`<base>...<current>`)
- Summary of notable top-level sections changed in `CHANGELOG.md`
- A concise "What changed" summary derived from commit titles (from the single `git log` run above)
- Mention of notable PR numbers/issues inferred from commit messages when available
- A note that timestamp-only changes are filtered out

## Constraints

- Only modify `CHANGELOG.md`.
- Do not make unrelated code or workflow edits.
- If generation fails due to missing tags/history, report clearly and stop.
- Never choose a prerelease base for a stable release if an earlier stable release exists.
- Prefer meaningful, user-impacting summaries over dependency/CI churn when both are present.
- Never fail the run solely because external commit APIs are blocked by integrity filtering; fall back to local git history and continue.
- Never attempt to re-implement `git-chglog` in Python, shell, or any other language. If the tool cannot be installed, stop with a clear error.