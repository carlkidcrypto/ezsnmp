---
name: Update Net-SNMP Versions
intent: Keep repository-pinned Net-SNMP releases and the verified Linux source archive current without crossing supported version tracks.
concurrency:
  group: ${{ github.workflow }}
  job-discriminator: ${{ github.run_id }}
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
  copilot-requests: write
  actions: read
  contents: read
safe-outputs:
  noop:
    report-as-issue: true
  create-pull-request:
    title-prefix: "[docker-netsnmp-update] "
    labels: [dependencies, docker, automated-pr]
    draft: false
    preserve-branch-name: true
    if-no-changes: "ignore"
timeout-minutes: 15
max-ai-credits: 25
model: sonnet
engine:
  id: copilot
network:
  allowed: [defaults, github, api.github.com]
tools:
  edit:
  bash: true
---

# Update Net-SNMP Versions

Discover upstream Net-SNMP releases and update the repository's Docker image
pins and standalone Linux source-build pin with safe, track-aware rules.

## Schedule Behavior

- If triggered by `workflow_dispatch`, run immediately.
- If triggered by `schedule`, run once per Saturday using gh-aw fuzzy scheduling.

## Goals

- Track upstream Net-SNMP releases from `net-snmp/net-snmp`.
- Update only versions within currently pinned `major.minor` tracks.
- Include the Linux standalone source-build version and its verified archive
  checksum from `tools/prepare_linux_netsnmp.sh`.
- Avoid risky cross-track upgrades and never select a version below 5.10.
- Default to stable releases only, excluding pre-release channels unless explicitly opted in.

## Steps

1. Discover currently pinned Net-SNMP versions in Docker assets and the Linux source-build script (Bounded File Reads — Token Optimization):
   - Do **not** read Dockerfiles in full into context. Use targeted `grep -rn` to scan `docker/**/Dockerfile`, `docker/**/README.rst`, `docker/cache/download_build_cache.sh`, and `tools/prepare_linux_netsnmp.sh`.
   - Extract explicit version strings from patterns like:
     - `net-snmp-<x.y.z>.tar.gz`
     - textual version mentions such as `Net-SNMP <x.y.z>`
     - `NETSNMP_VERSION="<version>"` in `tools/prepare_linux_netsnmp.sh`
   - For the Linux source-build pin, also record its matching `EXPECTED_SHA256`.

2. Determine latest upstream versions for each detected `major.minor` track:
  - Use both upstream tags and releases data from `net-snmp/net-snmp`.
  - Normalize tags (for example strip a leading `v` if present) before version comparison.
  - Determine latest by semantic version first, and use release/tag date as tie-break context when needed.
  - By default, exclude pre-release tags and versions such as `.pre*`, `-rc*`, `-beta*`, `-alpha*` and release entries marked `prerelease=true`. A currently pinned prerelease is only the baseline; prefer a newer stable version in its same track when available.
  - Only include pre-release channels when `workflow_dispatch` input `include_prerelease` is `true`.
   - Build a map such as:
     - track `5.10` -> latest upstream `5.10.z`

3. Apply safe updates:
   - For each Docker-pinned version, update references only when a newer version exists in the same track.
   - For `tools/prepare_linux_netsnmp.sh`, update `NETSNMP_VERSION` only to a newer version in the same track and update `EXPECTED_SHA256` to the SHA-256 of that exact upstream archive.
   - Download the canonical upstream archive over HTTPS, restricting curl to HTTPS for both the initial and redirected URLs; calculate its checksum with `sha256sum`. Do not guess or copy a checksum from an unverified source.
   - Keep edits strictly to Net-SNMP version references and the corresponding Linux archive checksum. Update corresponding tarball names and directory names where versioned paths are used.

4. Validate impact:
   - Ensure all selected versions are at least 5.10 and replacements remain within their existing `major.minor` tracks.
   - For the Linux source-build script, ensure the version, archive URL, extracted directory, and checksum all refer to the same upstream release.
   - Ensure no mixed-version references remain in files touched.
   - If no version bumps are needed, call the `noop` safe output tool with a message summarizing the current pinned versions and confirming they are already up to date.

5. If changes exist, create or update one PR using:
   - Branch: `automation/update-docker-netsnmp-versions`
   - Base: `main`
   - Title: `Update Net-SNMP versions`
   - Commit message: `chore(netsnmp): update pinned Net-SNMP versions`

## Scope
 
- Restrict edits to Net-SNMP version references in Docker-related files and `NETSNMP_VERSION` / `EXPECTED_SHA256` in `tools/prepare_linux_netsnmp.sh`.
- Preserve the 5.10 minimum supported version.
- Keep default behavior on stable releases only unless `include_prerelease=true` was explicitly provided.
- Do not change Python versions, distro versions, patching logic, or unrelated code.
- If upstream data is ambiguous or unavailable, call the `noop` safe output tool with an explanation of why no action was taken.
- When creating the PR, refer to the `pull-request-guide` skill.

## skill: `pull-request-guide`
---
description: Required contents and formatting for the Docker Net-SNMP patch version update PR.
---

### Pull Request Body

Include:
- Upstream source checked (`net-snmp/net-snmp`)
- Selection mode used (`stable-only` or `include-prerelease`)
- Detected tracks and old/new patch versions per track
- Files changed
- Explicit note that only patch-level, same-track updates were performed