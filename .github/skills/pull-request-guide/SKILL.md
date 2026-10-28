---
name: pull-request-guide
description: Use when preparing, verifying, staging, opening, or updating Pull Requests in ezsnmp according to project git and review policies.
---

# Pull Request Guide (ezsnmp)

Use this skill when preparing code changes, running verification checks, staging files, creating conventional commits, and opening or updating pull requests for `ezsnmp`.

## 1. Strict Policies & Governance

- **STRICTLY DO NOT MERGE PULL REQUESTS**:
  - Pull request merging is **exclusively reserved for the repository maintainer (@carlkidcrypto)**.
  - Never run `gh pr merge`, `git merge <branch> main`, `--admin`, or `--squash`.
  - Your responsibility ends with opening the PR, ensuring all CI checks pass, and summarizing the changes for maintainer review.

---

## 2. Branching & Commit Conventions

- **Branch Naming**:
  - Features: `feat/<description>` or `feature/<description>`
  - Bug fixes: `fix/<description>`
  - Maintenance & Chore: `chore/<description>`
  - Documentation: `docs/<description>`
  - Release bumps: `chore/bump-v<version>`
- **Commit Messages**:
  - Follow Conventional Commits: `<type>(<scope>): <short summary>`.
  - Types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `ci`.
  - Make atomic, incremental commits. Never squash commits locally.

---

## 3. Pre-PR Verification Checklist

Before pushing commits or creating a PR, activate your local Python virtual environment (e.g. `source .venv/bin/activate` or `./python3.12.venv/bin/activate`) and run the following verification steps:

### Code Reuse

- Avoid duplicating logic across the repository in both production and test code. Prefer shared implementations and test helpers over repeated code, and review changes for duplication before considering them complete.
- Net-SNMP patch files under `ezsnmp/patches/` are exempt when their repeated or similar content reflects the upstream source being patched.

1. **Python Formatting**:
   ```bash
   black --check .
   ```
2. **C++ Code Formatting**:
   ```bash
   clang-format --dry-run --Werror ezsnmp/src/*.cpp ezsnmp/src/net-snmp-*-final-patched/*.cpp cpp_tests/*.cpp
   ```
3. **Documentation Zero-Warning Build**:
   ```bash
   cd sphinx_docs_build/landing
   make html SPHINXOPTS="-W"
   cd ../..
   ```
4. **Python Unit Tests**:
   ```bash
   pytest python_tests/test_session_unit.py python_tests/test_exceptions.py
   ```
5. **C++ Unit Tests** (if C++ or build files were modified):
   ```bash
   cd cpp_tests && meson setup builddir && meson compile -C builddir && meson test -C builddir -v
   cd ..
   ```
6. **Workflow Linting** (if workflow files were modified):
   ```bash
   yamllint -c .yamllint .github/workflows/*.yml
   ```
7. **Shell Script Validation** (if shell scripts were modified):
   ```bash
   shellcheck <modified-shell-script-paths>
   bash -n <modified-shell-script-paths>
   ```

### CI Failure and Timing Triage

- Inspect individual workflow jobs and their conclusions; a successful workflow can contain skipped test jobs due to changed-file filters.
- Compare job and step durations, logs, and artifacts to distinguish dependency-install time from build and test time.
- For platform-specific failures, compare the failing job's environment and commands with a successful equivalent before changing build flags. Do not infer a root cause from truncated configure output alone.
- When a Homebrew workflow rewrites a formula URL/checksum for a local source tarball, anchor the substitution to the top-level formula stanza so nested resource URLs/checksums remain intact.

---

## 4. Staging Files & Safe Outputs Protection

- **Targeted Staging**:
  - Explicitly stage only intended modified target files (e.g., `git add ezsnmp/session.py python_tests/test_session.py`).
  - **Avoid blanket staging commands** like `git add -A` or `git add .`. Blanket commands can accidentally stage dynamically restored inline skills from `.github/skills/`, causing CI safe-output errors (`patch modifies files outside the allowed-files list`).
- **SonarQube Cloud Quality Gate**:
  - Treat a passing SonarQube Cloud Quality Gate as required for every change. Do not consider verification complete until the analysis for the current PR/revision reports a passed gate.
  - If the gate fails, inspect the new-code findings and fix them before completing the task. If the finding details are inaccessible, request the rule and affected file/line instead of guessing or claiming success.
  - Automatic analysis reads `.sonarcloud.properties` on `main`. Ensure documentation exclusions (`sonar.exclusions=docs/**`) are respected so generated files do not fail the Quality Gate.

---

## 5. Opening Pull Requests

Push your branch and open the PR using the GitHub CLI:
```bash
git push -u origin <branch-name>
gh pr create --title "<type>(<scope>): <description>" --body "<summary_and_testing_details>"
```
