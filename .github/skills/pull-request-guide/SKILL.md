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

Before pushing commits or creating a PR, run the following verification steps locally:

1. **Python Formatting**:
   ```bash
   /home/carlkidcrypto/Github/ezsnmp/python3.12.venv/bin/black --check .
   ```
2. **C++ Code Formatting**:
   ```bash
   clang-format --dry-run --Werror ezsnmp/src/net-snmp-5.10-final-patched/*.cpp cpp_tests/*.cpp
   ```
3. **Documentation Zero-Warning Build**:
   ```bash
   cd sphinx_docs_build/landing
   SPHINXBUILD=/home/carlkidcrypto/Github/ezsnmp/python3.12.venv/bin/sphinx-build make html SPHINXOPTS="-W"
   cd ../..
   ```
4. **Python Unit Tests**:
   ```bash
   /home/carlkidcrypto/Github/ezsnmp/python3.12.venv/bin/pytest python_tests/test_session_unit.py python_tests/test_exceptions.py
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

---

## 4. Staging Files & Safe Outputs Protection

- **Targeted Staging**:
  - Explicitly stage only intended modified target files (e.g., `git add ezsnmp/session.py python_tests/test_session.py`).
  - **Avoid blanket staging commands** like `git add -A` or `git add .`. Blanket commands can accidentally stage dynamically restored inline skills from `.github/skills/`, causing CI safe-output errors (`patch modifies files outside the allowed-files list`).
- **SonarQube Cloud Quality Gate**:
  - Automatic analysis reads `.sonarcloud.properties` on `main`. Ensure documentation exclusions (`sonar.exclusions=docs/**`) are respected so generated files do not fail the Quality Gate.

---

## 5. Opening Pull Requests

Push your branch and open the PR using the GitHub CLI:
```bash
git push -u origin <branch-name>
gh pr create --title "<type>(<scope>): <description>" --body "<summary_and_testing_details>"
```