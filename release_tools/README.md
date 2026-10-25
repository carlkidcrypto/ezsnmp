# Release Tools

Standardized automation and validation utilities for managing releases, version bumps, and documentation checks across the repository.

## Overview

The `release_tools/` directory provides consistent, cross-platform release utilities for `ezsnmp` and serves as the template structure for all repositories in the `carlkidcrypto` ecosystem.

## Available Tools

### `bump_version.sh` (or `release.sh`)

Atomically bumps version strings across all tracked build, package, and documentation files.

- **Aliases**: `release_tools/release.sh` is a symlink to `bump_version.sh`.
- **Validation**: Supports both Semantic Versioning (`2.5.0b0`) and Calendar Versioning (`2026.10.18a0`).
- **Auto-detection**: Automatically extracts the current version from `setup.cfg` if omitted.
- **Safety checks**:
  - Ensures required target files contain the expected current version before making edits.
  - Checks after replacement that no stale references to the old version remain in tracked active files.
  - Leaves historical files (e.g. `CHANGELOG.md`) and deployment-managed files intact.

### Command-Line Usage

```bash
# Preview changes without modifying files
./release_tools/bump_version.sh --dry-run 2.5.0b0

# Bump version and automatically verify code formatting, docs (-W), and tests
./release_tools/bump_version.sh --verify 2.5.0b0

# Bump version directly
./release_tools/bump_version.sh 2.5.0b0

# Specify old version explicitly (if needed)
./release_tools/bump_version.sh 2.5.0b0 2.5.0a2
```

### Options

| Flag | Long Option | Description |
| :--- | :--- | :--- |
| `-n` | `--dry-run` | Shows files that would be modified without writing changes. |
| `-v` | `--verify` | Runs Black formatting check, Sphinx doc build with `-W` (zero warnings), and pytest. |
| `-h` | `--help` | Displays help message and examples. |

---

## Managed File Touchpoints

When running `bump_version.sh` in `ezsnmp`, the following files are synchronized:

1. `setup.cfg` &mdash; Python package distribution version (`version = <VER>`)
2. `cpp_tests/meson.build` &mdash; C++ test suite project version (`version: '<VER>'`)
3. `sphinx_docs_build/source/conf.py` &mdash; Sphinx documentation release variable (`release = "v<VER>"`)

### Excluded Files

The following files are intentionally excluded from manual/automated bump scripts because they are maintained by dedicated CI/CD workflows:
- `CHANGELOG.md` &mdash; Generated and maintained by `auto_change_log.md`
- `Formula/ezsnmp.rb` &mdash; Updated automatically post-tag by `homebrew_deploy.yml`
- `sphinx_docs_build/landing/source/index.rst` &mdash; Version matrix updated by `sphinx_build.yml`
- `docs/**` &mdash; Built HTML/static deployment artifacts

---

## Standard Release Checklist

1. **Create a release branch or worktree**:
   ```bash
   git checkout -b chore/bump-v2.5.0b0
   ```
2. **Execute version bump with verification**:
   ```bash
   ./release_tools/bump_version.sh --verify 2.5.0b0
   ```
3. **Inspect the git status and diff**:
   ```bash
   git diff
   ```
4. **Commit and push**:
   ```bash
   git commit -am "chore: bump version to 2.5.0b0"
   git push -u origin chore/bump-v2.5.0b0
   ```
5. **Open Pull Request**:
   - Open a PR targeting `main`.
   - Wait for maintainer review and merge.
