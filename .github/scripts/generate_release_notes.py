#!/usr/bin/env python3
"""Generate and update GitHub release notes for ezsnmp.

This script automates the generation of high-signal, human-readable release
notes for tagged ezsnmp releases, following the specification in
``.github/workflows/auto_release_notes.md``.

It deterministically:
1. Identifies release context (tag, prerelease status, PyPI version).
2. Resolves the appropriate base tag according to semantic priority rules.
3. Extracts and categorizes commit history and pull request references into
   standard themes based on file paths and conventional prefixes.
4. Generates a formatted release note matching the ezsnmp template.
5. Optionally patches the GitHub release via the GitHub CLI (gh).

Usage:
    # Process a single release tag (dry-run):
    python3 .github/scripts/generate_release_notes.py --tag v2.4.0

    # Process and publish a single release tag:
    python3 .github/scripts/generate_release_notes.py --tag v2.4.0 --publish

    # Process the latest published release:
    python3 .github/scripts/generate_release_notes.py --latest --publish

    # Backfill all existing releases (chronological order):
    python3 .github/scripts/generate_release_notes.py --backfill --publish
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPO = "carlkidcrypto/ezsnmp"

# Standard theme categories in priority display order
THEME_CATEGORIES = [
    "Features / Enhancements",
    "Bug Fixes",
    "Runtime / Core Library",
    "Tests",
    "Containers / Packaging",
    "CI / Workflows",
    "Documentation",
    "Dependencies",
    "Chores / Misc",
]


def run_cmd(
    cmd: list[str],
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> str:
    """Run a subprocess command and return stdout."""
    effective_env = os.environ.copy()
    if env:
        effective_env.update(env)
    if "/opt/homebrew/bin" not in effective_env.get("PATH", ""):
        effective_env["PATH"] = f"/opt/homebrew/bin:{effective_env.get('PATH', '')}"

    res = subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        env=effective_env,
    )
    if check and res.returncode != 0:
        raise RuntimeError(
            f"Command failed (exit {res.returncode}): {' '.join(cmd)}\nStderr: {res.stderr}"
        )
    return res.stdout.strip()


def ensure_git_tags(repo_root: Path = REPO_ROOT) -> None:
    """Ensure git tags are fetched, handling shallow repositories gracefully."""
    try:
        is_shallow = run_cmd(
            ["git", "rev-parse", "--is-shallow-repository"],
            cwd=repo_root,
            check=False,
        )
        if is_shallow.strip() == "true":
            run_cmd(
                ["git", "fetch", "--tags", "--unshallow"],
                cwd=repo_root,
                check=False,
            )
        else:
            run_cmd(["git", "fetch", "--tags"], cwd=repo_root, check=False)
    except Exception:
        pass


def fetch_all_releases(repo: str = DEFAULT_REPO) -> list[dict[str, Any]]:
    """Fetch all releases from GitHub API using the gh CLI."""
    stdout = run_cmd(["gh", "api", f"repos/{repo}/releases?per_page=100"], check=True)
    return json.loads(stdout)


def clean_title(title: str) -> str:
    """Clean emojis, trailing PR author metadata, and issue numbers."""
    # Strip leading non-alphanumeric / non-bracket characters (e.g. emojis)
    t = re.sub(r"^[^\w\s\[\(]+\s*", "", title)
    # Strip trailing "by @... in https://..."
    t = re.sub(r"\s+by\s+@.*?in\s+https://github\.com/[^\s]+", "", t)
    # Strip trailing PR references (#123) or #123
    t = re.sub(r"\s*\(#\d+\)", "", t)
    t = re.sub(r"\s*#\d+$", "", t)
    return t.strip()


def rewrite_to_natural_language(title: str) -> str:
    """Rewrite terse commit or PR titles into natural language with active verbs."""
    t = clean_title(title)

    # Detect conventional prefix before stripping
    prefix_match = re.match(
        r"^(feat|fix|docs|test|tests|chore|ci|refactor|style|build|perf)(?:\([\w-]+\))?:\s*",
        t,
        flags=re.IGNORECASE,
    )
    prefix = prefix_match.group(1).lower() if prefix_match else ""

    # Detect bracket tag like [docs], [coverage-autofix-py]
    bracket_match = re.match(r"^\[([\w-]+)\]\s*", t)
    bracket_tag = bracket_match.group(1).lower() if bracket_match else ""

    t = re.sub(r"^\[[\w-]+\]\s*", "", t)
    t = re.sub(
        r"^(feat|fix|docs|test|tests|chore|ci|refactor|style|build|perf)(?:\([\w-]+\))?:\s*",
        "",
        t,
        flags=re.IGNORECASE,
    )
    t = t.strip()
    if not t:
        return title

    # Ensure capitalized
    t = t[0].upper() + t[1:]

    # Conjugate leading verb to 3rd person singular active
    verb_replacements: list[tuple[str, str]] = [
        (r"^(?:Add|Added)\b", "Adds"),
        (r"^(?:Fix|Fixed)\b", "Fixes"),
        (r"^(?:Update|Updated)\b", "Updates"),
        (r"^(?:Improve|Improved)\b", "Improves"),
        (r"^(?:Remove|Removed)\b", "Removes"),
        (r"^(?:Allow|Allowed)\b", "Allows"),
        (r"^(?:Support|Supported)\b", "Supports"),
        (r"^(?:Ensure|Ensured)\b", "Ensures"),
        (r"^(?:Refactor|Refactored)\b", "Refactors"),
        (r"^(?:Resolve|Resolved)\b", "Resolves"),
        (r"^(?:Prevent|Prevented)\b", "Prevents"),
        (r"^(?:Enable|Enabled)\b", "Enables"),
        (r"^(?:Disable|Disabled)\b", "Disables"),
        (r"^(?:Bump|Bumped)\b", "Bumps"),
        (r"^(?:Upgrade|Upgraded)\b", "Upgrades"),
        (r"^(?:Move|Moved)\b", "Moves"),
        (r"^(?:Clean|Cleaned)\b", "Cleans"),
        (r"^(?:Serialize|Serialized)\b", "Serializes"),
        (r"^(?:Handle|Handled)\b", "Handles"),
        (r"^(?:Align|Aligned)\b", "Aligns"),
        (r"^(?:Scope|Scoped)\b", "Scopes"),
        (r"^(?:Split|Splitted)\b", "Splits"),
        (r"^(?:Drop|Dropped)\b", "Drops"),
        (r"^(?:Harden|Hardened)\b", "Hardens"),
        (r"^(?:Correct|Corrected)\b", "Corrects"),
        (r"^(?:Introduce|Introduced)\b", "Introduces"),
        (r"^(?:Include|Included)\b", "Includes"),
        (r"^(?:Switch|Switched)\b", "Switches"),
        (r"^(?:Standardize|Standardized)\b", "Standardizes"),
        (r"^(?:Migrate|Migrated)\b", "Migrates"),
        (r"^(?:Optimize|Optimized)\b", "Optimizes"),
        (r"^(?:Configure|Configured)\b", "Configures"),
        (r"^(?:Adopt|Adopted)\b", "Adopts"),
    ]
    conjugated = False
    for pattern, replacement in verb_replacements:
        if re.search(pattern, t):
            t = re.sub(pattern, replacement, t)
            conjugated = True
            break

    # If no leading verb was matched, infer active verb from commit prefix/tag
    if not conjugated:
        known_active = (
            "Adds",
            "Fixes",
            "Updates",
            "Improves",
            "Removes",
            "Allows",
            "Supports",
            "Ensures",
            "Refactors",
            "Resolves",
            "Prevents",
            "Enables",
            "Disables",
            "Bumps",
            "Upgrades",
            "Moves",
            "Cleans",
            "Serializes",
            "Handles",
            "Aligns",
            "Scopes",
            "Splits",
            "Drops",
            "Hardens",
            "Corrects",
            "Introduces",
            "Includes",
            "Switches",
            "Standardizes",
            "Migrates",
            "Optimizes",
            "Configures",
            "Adopts",
        )
        if not any(t.startswith(f"{v} ") for v in known_active):
            first_char_lower = t[0].lower() + t[1:]
            if prefix == "fix":
                t = f"Fixes {first_char_lower}"
            elif prefix == "feat":
                t = f"Adds {first_char_lower}"
            elif prefix in ("docs",) or bracket_tag == "docs":
                t = f"Updates {first_char_lower}"
            elif prefix in ("test", "tests"):
                t = f"Adds {first_char_lower}"

    return t


def categorize_item(title: str, files: list[str]) -> str:
    """Categorize an item into one of the 9 standard themes."""
    title_lower = title.lower()

    # 1. Dependencies
    if (
        any(
            title_lower.startswith(p)
            for p in ["bump", "chore(deps)", "deps:", "chore(deps-dev)"]
        )
        or "dependabot" in title_lower
    ):
        return "Dependencies"
    if files and all(
        f
        in (
            "requirements.txt",
            "requirements-dev.txt",
            "python_tests/requirements.txt",
        )
        for f in files
    ):
        return "Dependencies"

    # 2. CI / Workflows (check before docs so .github/workflows/*.md isn't marked doc)
    if files and all(f.startswith(".github/") for f in files):
        return "CI / Workflows"
    if any(
        title_lower.startswith(p)
        for p in ["ci", "workflow", "workflows", "action", "actions"]
    ):
        return "CI / Workflows"

    # 3. Documentation
    if files and all(
        (f.startswith(("docs/", "sphinx_docs_build/")) or f.endswith((".rst", ".md")))
        and not f.startswith(".github/")
        for f in files
    ):
        return "Documentation"
    if any(title_lower.startswith(p) for p in ["docs", "doc:"]):
        return "Documentation"

    # 4. Tests
    if files and all(
        f.startswith(
            ("cpp_tests/", "python_tests/", "integration_tests/", "cml_tests/")
        )
        for f in files
    ):
        return "Tests"
    if any(title_lower.startswith(p) for p in ["test", "tests"]):
        return "Tests"

    # 5. Containers / Packaging
    if (
        files
        and any(
            f.startswith(("docker/", "Formula/"))
            or f
            in (
                "setup.py",
                "setup.cfg",
                "pyproject.toml",
                "build_utils.py",
                "Dockerfile",
            )
            for f in files
        )
        and not any(f.startswith("ezsnmp/src/") for f in files)
    ):
        return "Containers / Packaging"
    if any(
        title_lower.startswith(p)
        for p in [
            "docker",
            "packaging",
            "wheel",
            "cibuildwheel",
            "formula",
            "homebrew",
            "pypi",
        ]
    ):
        return "Containers / Packaging"

    # 6. Core Library / Bug Fixes / Features
    touches_core = any(f.startswith(("ezsnmp/src/", "ezsnmp/")) for f in files)
    is_bug = any(
        w in title_lower
        for w in [
            "fix",
            "bug",
            "patch",
            "error",
            "leak",
            "segfault",
            "overflow",
            "crash",
            "regression",
            "resolve",
            "prevent",
        ]
    )
    is_feat = any(
        w in title_lower
        for w in [
            "feat",
            "add",
            "support",
            "implement",
            "new",
            "allow",
            "introduce",
            "option",
        ]
    )

    if touches_core:
        if is_bug:
            return "Bug Fixes"
        elif is_feat:
            return "Features / Enhancements"
        return "Runtime / Core Library"

    if is_bug:
        return "Bug Fixes"
    if is_feat:
        return "Features / Enhancements"

    return "Chores / Misc"


def parse_semver(tag: str) -> tuple[int, int, int, int, str] | None:
    """Parse a version tag into (major, minor, patch, is_stable, prerelease_suffix)."""
    m = re.match(r"^v?(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:[.-]?([a-zA-Z0-9.-]+))?$", tag)
    if not m:
        return None
    major = int(m.group(1))
    minor = int(m.group(2) or 0)
    patch = int(m.group(3) or 0)
    suffix = m.group(4) or ""
    is_stable = 1 if not suffix else 0
    return (major, minor, patch, is_stable, suffix)


def determine_base_tag(
    current_release: dict[str, Any],
    all_chronological_releases: list[dict[str, Any]],
    git_tags: set[str],
) -> str:
    """Determine the base tag according to the priority rules in auto_release_notes.md."""
    body = current_release.get("body") or ""

    # Priority 1: Explicit override marker
    override_match = re.search(r"<!--\s*BASE_TAG:\s*([^\s]+)\s*-->", body)
    if override_match:
        base = override_match.group(1).strip()
        print(f"Selected base for {current_release['tag_name']}: {base}")
        return base

    current_tag = current_release["tag_name"]
    is_prerelease = current_release.get("prerelease", False)

    # Find position of current release in chronological list
    idx = -1
    for i, r in enumerate(all_chronological_releases):
        if r["tag_name"] == current_tag:
            idx = i
            break

    if idx > 0:
        prior_releases = all_chronological_releases[:idx]
        if not is_prerelease:
            # Priority 2: Stable release -> most recent earlier stable release
            for prev in reversed(prior_releases):
                if not prev.get("prerelease", False):
                    candidate = prev["tag_name"]
                    if candidate != current_tag:
                        print(f"Selected base for {current_tag}: {candidate}")
                        return candidate
        else:
            # Priority 3: Prerelease -> most recent earlier release (stable or prerelease)
            candidate = prior_releases[-1]["tag_name"]
            if candidate != current_tag:
                print(f"Selected base for {current_tag}: {candidate}")
                return candidate

    # Priority 4: Fallback to nearest lower semver git tag if available
    curr_semver = parse_semver(current_tag)
    if curr_semver and git_tags:
        candidates: list[tuple[tuple[int, int, int, int, str], str]] = []
        for t in git_tags:
            if t == current_tag:
                continue
            t_semver = parse_semver(t)
            if t_semver and t_semver < curr_semver:
                candidates.append((t_semver, t))
        if candidates:
            candidates.sort(key=lambda c: (c[0][0], c[0][1], c[0][2], c[0][3], c[0][4]))
            base = candidates[-1][1]
            print(f"Selected base for {current_tag}: {base}")
            return base

    # Priority 5: Final fallback to repository root commit
    try:
        root_commit = run_cmd(["git", "rev-list", "--max-parents=0", "HEAD"])
        if root_commit:
            base = root_commit.splitlines()[0]
            print(f"Selected base for {current_tag}: {base}")
            return base
    except Exception:
        pass

    print(f"Selected base for {current_tag}: repository root")
    return "repository root"


def extract_git_commits(base_tag: str, current_tag: str) -> dict[str, dict[str, Any]]:
    """Extract commits and touched file paths between base_tag and current_tag."""
    if base_tag.startswith("repository root") or len(base_tag) == 40:
        cmd = ["git", "log", current_tag, "--name-only", "--format=COMMIT:%H%x09%s"]
    else:
        cmd = [
            "git",
            "log",
            f"{base_tag}..{current_tag}",
            "--name-only",
            "--format=COMMIT:%H%x09%s",
        ]

    try:
        log_out = run_cmd(cmd)
    except Exception:
        return {}

    commits: dict[str, dict[str, Any]] = {}
    current_hash: str | None = None
    for line in log_out.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("COMMIT:"):
            parts = line[len("COMMIT:") :]
            if "\t" in parts:
                h, s = parts.split("\t", 1)
            else:
                h, s = parts, ""
            current_hash = h
            commits[h] = {"title": s, "files": []}
        elif current_hash:
            commits[current_hash]["files"].append(line)

    return commits


def parse_existing_prs(
    body: str, git_commits: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, Any]], set[str]]:
    """Parse PR numbers and titles from GitHub default release note lines."""
    prs: list[dict[str, Any]] = []
    seen: set[str] = set()

    for line in body.splitlines():
        m = re.match(
            r"^\*\s*(?:[^\w\s\[\(]+\s*)?(.*?)\s+by\s+@.*?in\s+https://github\.com/[^/]+/[^/]+/pull/(\d+)",
            line,
        )
        if m:
            title, pr_num = m.group(1), m.group(2)
            if pr_num not in seen:
                seen.add(pr_num)
                matched_files: list[str] = []
                for _, cdata in git_commits.items():
                    if (
                        f"(#{pr_num})" in cdata["title"]
                        or f"#{pr_num}" in cdata["title"]
                    ):
                        matched_files.extend(cdata["files"])
                prs.append(
                    {
                        "title": title,
                        "pr": pr_num,
                        "files": list(set(matched_files)),
                    }
                )

    return prs, seen


def synthesize_summary(
    categories: dict[str, list[str]],
    is_prerelease: bool,
    additional_context: str = "",
) -> str:
    """Synthesize a 1-2 sentence human-readable executive summary."""
    highlights: list[str] = []
    if categories["Features / Enhancements"]:
        highlights.append("features and enhancements")
    if categories["Bug Fixes"]:
        highlights.append("bug fixes")
    if categories["Runtime / Core Library"]:
        highlights.append("runtime core improvements")
    if categories["Containers / Packaging"]:
        highlights.append("packaging and build infrastructure")
    if categories["Tests"]:
        highlights.append("test coverage expansion")
    if categories["Documentation"]:
        highlights.append("documentation updates")
    if categories["Dependencies"] or categories["CI / Workflows"]:
        highlights.append("routine CI and dependency maintenance")

    if not highlights:
        highlights = ["maintenance updates and stability improvements"]

    if len(highlights) == 1:
        hl_str = highlights[0]
    elif len(highlights) == 2:
        hl_str = f"{highlights[0]} and {highlights[1]}"
    else:
        hl_str = f"{', '.join(highlights[:-1])}, and {highlights[-1]}"

    release_type = "prerelease" if is_prerelease else "release"
    summary = f"This {release_type} focuses on {hl_str} across the ezsnmp package."
    if additional_context:
        summary = f"{summary} {additional_context.strip()}"
    return summary


def build_release_notes(
    release: dict[str, Any],
    base_tag: str,
    git_commits: dict[str, dict[str, Any]],
    additional_context: str = "",
    repo: str = DEFAULT_REPO,
) -> str:
    """Build formatted release notes markdown adhering to the release-notes-template."""
    tag = release["tag_name"]
    is_prerelease = release.get("prerelease", False)
    pypi_version = tag[1:] if tag.startswith("v") else tag
    has_valid_pypi = bool(re.match(r"^\d+(\.\d+)*", pypi_version))
    pypi_url = f"https://pypi.org/project/ezsnmp/{pypi_version}/"
    raw_body = release.get("body") or ""

    parsed_prs, seen_pr_numbers = parse_existing_prs(raw_body, git_commits)

    # Collect uncovered git commits (excluding merge commits)
    uncovered_commits: list[dict[str, Any]] = []
    for h, cdata in git_commits.items():
        s = cdata["title"]
        if s.startswith("Merge branch") or s.startswith("Merge pull request"):
            continue
        pr_match = re.search(r"#(\d+)", s)
        if pr_match and pr_match.group(1) in seen_pr_numbers:
            continue
        uncovered_commits.append({"title": s, "hash": h[:7], "files": cdata["files"]})

    # Combine items
    items: list[dict[str, Any]] = []
    for pr in parsed_prs:
        items.append(
            {
                "title": pr["title"],
                "ref": f"(#{pr['pr']})",
                "files": pr["files"],
            }
        )
    for uc in uncovered_commits:
        pr_match = re.search(r"\(#(\d+)\)", uc["title"])
        if pr_match:
            ref = f"(#{pr_match.group(1)})"
        else:
            hash_match = re.search(r"#(\d+)", uc["title"])
            if hash_match:
                ref = f"(#{hash_match.group(1)})"
            else:
                ref = f"({uc['hash']})"
        items.append(
            {
                "title": uc["title"],
                "ref": ref,
                "files": uc["files"],
            }
        )

    categories: dict[str, list[str]] = {cat: [] for cat in THEME_CATEGORIES}
    for item in items:
        cat = categorize_item(item["title"], item["files"])
        rewritten = rewrite_to_natural_language(item["title"])
        entry = f"- {rewritten} {item['ref']}"
        categories[cat].append(entry)

    # Deduplicate dependencies
    categories["Dependencies"] = list(dict.fromkeys(categories["Dependencies"]))

    summary = synthesize_summary(categories, is_prerelease, additional_context)

    lines: list[str] = [
        summary,
        "",
        f"Compared to: {base_tag}",
        "",
    ]

    if has_valid_pypi:
        lines.extend(
            [
                "## Install / Upgrade",
                "",
                "```bash",
                f"pip install ezsnmp=={pypi_version}",
                "```",
                "",
                f"Or browse this release on PyPI: {pypi_url}",
                "",
            ]
        )
    else:
        print(
            f"Skipping Install / Upgrade section for {tag}: could not derive valid PyPI version",
            file=sys.stderr,
        )

    for cat_name in THEME_CATEGORIES:
        entries = categories[cat_name]
        if entries:
            lines.append(f"## {cat_name}")
            for entry in entries:
                lines.append(entry)
            lines.append("")

    lines.append("---")
    if (
        base_tag == "repository root"
        or base_tag.startswith("repository root")
        or len(base_tag) == 40
    ):
        lines.append(f"**Full Changelog**: https://github.com/{repo}/commits/{tag}")
    else:
        lines.append(
            f"**Full Changelog**: https://github.com/{repo}/compare/{base_tag}...{tag}"
        )

    return "\n".join(lines).strip() + "\n"


def patch_github_release(release_id: int, body: str, repo: str = DEFAULT_REPO) -> bool:
    """Update release body on GitHub using gh api."""
    payload = json.dumps({"body": body})
    cmd = [
        "gh",
        "api",
        "-X",
        "PATCH",
        f"repos/{repo}/releases/{release_id}",
        "--input",
        "-",
    ]
    effective_env = os.environ.copy()
    if "/opt/homebrew/bin" not in effective_env.get("PATH", ""):
        effective_env["PATH"] = f"/opt/homebrew/bin:{effective_env.get('PATH', '')}"

    res = subprocess.run(
        cmd,
        input=payload,
        capture_output=True,
        text=True,
        env=effective_env,
    )
    if res.returncode != 0:
        print(
            f"Error patching release {release_id}: {res.stderr}",
            file=sys.stderr,
        )
        return False
    return True


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Generate and update ezsnmp GitHub release notes."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tag", help="Process a specific release tag (e.g. v2.4.0).")
    group.add_argument(
        "--latest",
        action="store_true",
        help="Process the most recently published release.",
    )
    group.add_argument(
        "--backfill",
        action="store_true",
        help="Process all releases in chronological order (oldest first).",
    )

    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish the updated notes to GitHub (default is dry-run).",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Path to save the generated release note markdown (or '-' for stdout).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to save generated notes (for batch/backfill).",
    )
    parser.add_argument(
        "--additional-context",
        default="",
        help="Optional additional context to incorporate into the notes.",
    )
    parser.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help=f"GitHub repository (default: {DEFAULT_REPO}).",
    )

    args = parser.parse_args()

    ensure_git_tags()

    print(f"Fetching releases for {args.repo}...")
    all_releases = fetch_all_releases(args.repo)
    if not all_releases:
        print("No releases found.", file=sys.stderr)
        return 1

    chronological = list(reversed(all_releases))
    git_tags_raw = run_cmd(["git", "tag"])
    git_tags = set(git_tags_raw.splitlines())

    targets: list[tuple[dict[str, Any], str]] = []

    if args.tag:
        matching = [r for r in all_releases if r["tag_name"] == args.tag]
        if not matching:
            print(f"Release tag not found: {args.tag}", file=sys.stderr)
            return 1
        rel = matching[0]
        base_tag = determine_base_tag(rel, chronological, git_tags)
        targets.append((rel, base_tag))

    elif args.latest:
        rel = all_releases[0]
        base_tag = determine_base_tag(rel, chronological, git_tags)
        targets.append((rel, base_tag))

    elif args.backfill:
        for r in chronological:
            base_tag = determine_base_tag(r, chronological, git_tags)
            targets.append((r, base_tag))

    print(f"Processing {len(targets)} release(s)...")

    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    successes = 0
    for idx, (rel, base_tag) in enumerate(targets, 1):
        tag = rel["tag_name"]
        rel_id = rel["id"]
        body = rel.get("body") or ""

        if "<!-- PROTECTED -->" in body:
            print(f"[{idx}/{len(targets)}] Skipping {tag}: marked <!-- PROTECTED -->")
            continue

        print(
            f"[{idx}/{len(targets)}] Generating notes for {tag} (Base: {base_tag})..."
        )
        git_commits = extract_git_commits(base_tag, tag)
        notes = build_release_notes(
            rel,
            base_tag,
            git_commits,
            additional_context=args.additional_context,
            repo=args.repo,
        )

        if args.output_file and len(targets) == 1:
            if args.output_file == "-":
                sys.stdout.write(notes)
            else:
                Path(args.output_file).write_text(notes, encoding="utf-8")
                print(f"  Wrote notes to {args.output_file}")
        elif args.output_dir:
            out_path = args.output_dir / f"{tag}.md"
            out_path.write_text(notes, encoding="utf-8")
            print(f"  Wrote notes to {out_path}")

        if args.publish:
            print(f"  Publishing release notes for {tag} (ID: {rel_id})...")
            if patch_github_release(rel_id, notes, args.repo):
                print(f"  ✓ Published {tag}")
                successes += 1
            else:
                print(f"  ✗ Failed to publish {tag}", file=sys.stderr)
            time.sleep(1.0)
        else:
            successes += 1
            if len(targets) == 1 and not args.output_file:
                print("\n" + "=" * 40)
                print(notes)
                print("=" * 40 + "\n")

    print(f"Completed: {successes}/{len(targets)} release(s) processed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
