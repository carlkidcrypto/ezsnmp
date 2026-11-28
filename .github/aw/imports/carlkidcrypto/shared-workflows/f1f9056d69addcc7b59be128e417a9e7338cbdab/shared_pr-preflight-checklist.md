## Pre-PR Preflight Checklist

Before committing, pushing, or opening/updating a Pull Request:

- **No direct `main` commits**: Verify `git rev-parse --abbrev-ref HEAD` is a feature/fix branch in a dedicated worktree — never commit directly to `main`.
- **Helper script placement**: Place non-trivial workflow scripts under `.github/scripts/` (never `.github/script/` or large inline YAML `run:` blocks).
- **Syntax & formatting validation**:
  - Run `yamllint` on `.github/workflows/` (excluding `*.lock.yml` and `agentics-maintenance.yml`).
  - Run `actionlint` on `.github/workflows/` (with `shellcheck` enabled when available).
  - Run `black --check` on all modified or added `.py` files.
- **Unpushed-commit check**: Confirm `git log origin/<branch>..HEAD` is empty before handing off or concluding a PR update.
- **2-pass PR MAIL / review comment replies**:
  1. Query **both** GraphQL `reviewThreads` (for unresolved inline review comments) **and** REST `pulls/<N>/comments` + `issues/<N>/comments` so no comment is missed.
  2. Reply to every addressed thread via `gh api repos/<owner>/<repo>/pulls/<N>/comments -F in_reply_to=<comment_id> -f body="Addressed in commit \`<sha>\`: <summary>"`.
