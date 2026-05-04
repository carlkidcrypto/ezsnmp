---
name: Update Docker Net-SNMP Versions
concurrency:
  group: ${{ github.workflow }}
  cancel-in-progress: false
on:
  workflow_dispatch:
    inputs:
      include_prerelease:
        description: "Include pre-release Net-SNMP tags (pre/rc/beta/alpha)"
        required: false
        default: false
        type: boolean
  schedule: weekly on saturday
  skip-if-match:
    query: 'is:pr is:open head:automation/update-docker-netsnmp-versions label:dependencies label:docker label:automated-pr'
permissions:
  actions: read
  contents: read
safe-outputs:
  create-pull-request:
    title-prefix: "[docker-netsnmp-update] "
    labels: [dependencies, docker, automated-pr]
    draft: false
    preserve-branch-name: true
    if-no-changes: "ignore"
timeout-minutes: 45
engine:
  id: copilot
  model: auto
network:
  allowed: [defaults, github]
tools:
  edit:
  bash: true
---

# Update Docker Net-SNMP Patch Versions

Discover upstream Net-SNMP releases and update Docker-pinned Net-SNMP versions
with safe, track-aware rules.

## Schedule Behavior

- If triggered by `workflow_dispatch`, run immediately.
- If triggered by `schedule`, run once per Saturday using gh-aw fuzzy scheduling.

## Goals

- Track upstream Net-SNMP releases from the `net-snmp/net-snmp` source.
- Update only patch versions within currently pinned `major.minor` tracks.
- Avoid risky cross-track upgrades (example: do not auto-jump `5.7.x` to `5.9.x`).
- Default to stable releases only, excluding pre-release channels unless explicitly opted in.

## Steps

1. Discover currently pinned Net-SNMP versions in repository Docker assets:
   - Scan `docker/**/Dockerfile`, `docker/**/README.rst`, and `docker/cache/download_build_cache.sh`.
   - Extract explicit version strings from patterns like:
     - `net-snmp-<x.y.z>.tar.gz`
     - textual version mentions such as `Net-SNMP <x.y.z>`

2. Determine latest upstream versions for each detected `major.minor` track:
  - Use both upstream tags and releases data from `net-snmp/net-snmp`.
  - Normalize tags (for example strip a leading `v` if present) before version comparison.
  - Determine latest by semantic version first, and use release/tag date as tie-break context when needed.
  - By default, exclude pre-release tags and versions such as `.pre*`, `-rc*`, `-beta*`, `-alpha*` and release entries marked `prerelease=true`.
  - Only include pre-release channels when `workflow_dispatch` input `include_prerelease` is `true`.
   - Build a map such as:
     - track `5.7` -> latest upstream `5.7.z`
     - track `5.8` -> latest upstream `5.8.z`
     - track `5.9` -> latest upstream `5.9.z`

3. Apply safe updates:
   - For each pinned version, if a newer patch exists in the same track, update references.
   - Keep all edits strictly to Net-SNMP version references.
   - Update corresponding tarball names and directory names where versioned paths are used.

4. Validate impact:
   - Ensure replacements are consistent and no mixed-version references remain for files touched.
   - If no version bumps are needed, call the `noop` safe output tool with a message summarizing the current pinned versions and confirming they are already up to date.

5. If changes exist, create or update one PR using:
   - Branch: `automation/update-docker-netsnmp-versions`
   - Base: `main`
   - Title: `Update Docker Net-SNMP patch versions`
   - Commit message: `chore(docker): update Net-SNMP patch versions in Docker assets`

## Pull Request Body

Include:

- Upstream source checked (`net-snmp/net-snmp`)
- Selection mode used (`stable-only` or `include-prerelease`)
- Detected tracks and old/new patch versions per track
- Files changed
- Explicit note that only patch-level, same-track updates were performed

## Scope

- Restrict edits to Net-SNMP version references in Docker-related files.
- Keep default behavior on stable releases only unless `include_prerelease=true` was explicitly provided.
- Do not change Python versions, distro versions, workflow logic, or unrelated code.
- If upstream data is ambiguous or unavailable, call the `noop` safe output tool with an explanation of why no action was taken.
