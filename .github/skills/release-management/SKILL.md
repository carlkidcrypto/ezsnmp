---
name: release-management
description: Use when preparing a new release, bumping version numbers across ezsnmp build/doc files, running release verification, or opening release PRs.
---

# Release Management Guide (ezsnmp)

Use this skill when preparing a new version release for `ezsnmp`, bumping project version strings, verifying build and test integrity, and creating the release pull request.

## 1. Release Tools Overview

`ezsnmp` provides a standardized release bumping script in `release_tools/`:
- **Main Script**: `release_tools/bump_version.sh` (also aliased via symlink `release_tools/release.sh`).
- **Synchronized Files**: Atomically updates the version string across:
  - `setup.cfg` (`version = X.Y.Z`)
  - `cpp_tests/meson.build` (`project(..., version: 'X.Y.Z')`)
  - `sphinx_docs_build/source/conf.py` (`release = 'X.Y.Z'`)
  - `doxygen_docs_build/Doxyfile` (`PROJECT_NUMBER = "X.Y.Z"`)
  - `ezsnmp/__init__.py` (`__version__ = 'X.Y.Z'`)
- **Files Excluded from Manual Bumps**:
  - `CHANGELOG.md` (automatically maintained by the `auto_change_log.md` agentic workflow).
  - Homebrew formulas (`Formula/*.rb` — managed post-tag in CI).
  - Landing page docs and compiled HTML (`docs/**`).

---

## 2. Release Bumping Workflow

### Step 1: Create a Release Branch
Always branch off the latest `main`:
```bash
git checkout main
git pull origin main
git checkout -b chore/bump-v<version>
```
*Example: `git checkout -b chore/bump-v2.5.0`*

### Step 2: Bump and Verify
Use the `--verify` flag to automatically bump version strings and run verification checks (black formatting check, Sphinx zero-warning build, and pytest unit tests):
```bash
./release_tools/bump_version.sh --verify <version>
```
*Dry-run option:* To preview file modifications before writing changes:
```bash
./release_tools/bump_version.sh --dry-run <version>
```

### Step 3: Review Staged Changes
Confirm that only the expected files were modified:
```bash
git diff
```

### Step 4: Commit and Push
Create a standard release commit:
```bash
git add setup.cfg cpp_tests/meson.build sphinx_docs_build/source/conf.py doxygen_docs_build/Doxyfile ezsnmp/__init__.py
git commit -m "chore: bump version to <version>"
git push -u origin chore/bump-v<version>
```

### Step 5: Open Pull Request
Open a pull request for the maintainer:
```bash
gh pr create --title "chore: bump version to <version>" --body "Automated version bump to <version> with release_tools/bump_version.sh --verify."
```

---

## 3. Strict Merge Prohibition

- **Never merge the release PR**: PR merging and release tagging trigger automated PyPI publication (`build_and_publish_to_pypi.yml`) and Homebrew formula updates. Merging is strictly reserved for the repository maintainer (@carlkidcrypto).
