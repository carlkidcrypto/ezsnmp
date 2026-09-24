"""Unit tests for .github/scripts/generate_release_notes.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

# Dynamically import generate_release_notes from .github/scripts/
_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "generate_release_notes.py"
spec = importlib.util.spec_from_file_location(
    "generate_release_notes", str(_SCRIPT_PATH)
)
gen_mod = importlib.util.module_from_spec(spec)
sys.modules["generate_release_notes"] = gen_mod
spec.loader.exec_module(gen_mod)

clean_title = gen_mod.clean_title
rewrite_to_natural_language = gen_mod.rewrite_to_natural_language
categorize_item = gen_mod.categorize_item
parse_semver = gen_mod.parse_semver
determine_base_tag = gen_mod.determine_base_tag
parse_existing_prs = gen_mod.parse_existing_prs
synthesize_summary = gen_mod.synthesize_summary
build_release_notes = gen_mod.build_release_notes


def test_clean_title():
    raw1 = "✨ Fix memory leak in session (#123) by @carlkidcrypto in https://github.com/carlkidcrypto/ezsnmp/pull/123"
    assert clean_title(raw1) == "Fix memory leak in session"

    raw2 = "[docs] Update documentation for SNMPv3 #456"
    assert clean_title(raw2) == "[docs] Update documentation for SNMPv3"


def test_rewrite_to_natural_language_prefixes_and_verbs():
    # Conventional commit prefixes stripped and verb conjugated
    assert (
        rewrite_to_natural_language("feat(session): add timeout option")
        == "Adds timeout option"
    )
    assert (
        rewrite_to_natural_language("fix: resolve crash on null pointer")
        == "Resolves crash on null pointer"
    )
    assert (
        rewrite_to_natural_language("chore(deps): bump urllib3 from 1.26 to 2.0")
        == "Bumps urllib3 from 1.26 to 2.0"
    )
    assert (
        rewrite_to_natural_language("[coverage-autofix-py] improve branch coverage")
        == "Improves branch coverage"
    )

    # Past tense verbs conjugated to 3rd person singular present
    assert (
        rewrite_to_natural_language("Fixed segfault in snmpwalk")
        == "Fixes segfault in snmpwalk"
    )
    assert (
        rewrite_to_natural_language("Added support for Python 3.14")
        == "Adds support for Python 3.14"
    )
    assert (
        rewrite_to_natural_language("Updated dependencies in requirements.txt")
        == "Updates dependencies in requirements.txt"
    )

    # Prefix with noun gets inferred active verb
    assert (
        rewrite_to_natural_language("fix: memory leak in walk")
        == "Fixes memory leak in walk"
    )
    assert (
        rewrite_to_natural_language("feat: timeout parameter")
        == "Adds timeout parameter"
    )

    # Already third person present unchanged
    assert (
        rewrite_to_natural_language("Adds support for Net-SNMP 5.9")
        == "Adds support for Net-SNMP 5.9"
    )


def test_categorize_item():
    # Dependencies
    assert categorize_item("Bump certifi from 2024.1 to 2024.2", []) == "Dependencies"
    assert (
        categorize_item(
            "Update packages",
            ["requirements.txt", "requirements-dev.txt"],
        )
        == "Dependencies"
    )

    # CI / Workflows (priority over docs)
    assert (
        categorize_item(
            "Update release workflow",
            [".github/workflows/auto_release_notes.md"],
        )
        == "CI / Workflows"
    )
    assert categorize_item("ci: improve test matrix", []) == "CI / Workflows"

    # Documentation
    assert (
        categorize_item("docs: update session guide", ["docs/session.rst"])
        == "Documentation"
    )
    assert categorize_item("Fix typo in readme", ["README.md"]) == "Documentation"

    # Tests
    assert (
        categorize_item(
            "Add test for get_bulk error handling",
            ["python_tests/test_session_get.py"],
        )
        == "Tests"
    )
    assert categorize_item("test: verify mib loading", []) == "Tests"

    # Containers / Packaging
    assert (
        categorize_item("Build wheels for arm64", ["setup.py", "pyproject.toml"])
        == "Containers / Packaging"
    )
    assert (
        categorize_item("Update Docker test image", ["docker/Dockerfile"])
        == "Containers / Packaging"
    )

    # Core Library / Bug Fixes / Features
    assert (
        categorize_item("Fix memory leak in session", ["ezsnmp/src/session.c"])
        == "Bug Fixes"
    )
    assert (
        categorize_item("Add support for custom context", ["ezsnmp/session.py"])
        == "Features / Enhancements"
    )
    assert (
        categorize_item("Refactor session initialization", ["ezsnmp/session.py"])
        == "Runtime / Core Library"
    )

    # Chores / Misc
    assert categorize_item("misc cleanups", ["LICENSE"]) == "Chores / Misc"


def test_parse_semver():
    assert parse_semver("v2.4.0") == (2, 4, 0, 1, "")
    assert parse_semver("v2.5.0a1") == (2, 5, 0, 0, "a1")
    assert parse_semver("1.0.0") == (1, 0, 0, 1, "")
    assert parse_semver("invalid-tag") is None


def test_determine_base_tag_priority_1_override():
    rel = {
        "tag_name": "v2.4.0",
        "prerelease": False,
        "body": "Some body\n<!-- BASE_TAG: v2.3.0-custom -->\nMore text",
    }
    base = determine_base_tag(rel, [], set())
    assert base == "v2.3.0-custom"


def test_determine_base_tag_priority_2_stable():
    releases = [
        {"tag_name": "v2.0.0", "prerelease": False},
        {"tag_name": "v2.1.0", "prerelease": False},
        {"tag_name": "v2.2.0a1", "prerelease": True},
        {"tag_name": "v2.2.0b1", "prerelease": True},
        {"tag_name": "v2.2.0", "prerelease": False},
    ]
    # For v2.2.0 (stable), the base must skip prereleases and pick v2.1.0
    base = determine_base_tag(releases[-1], releases, set())
    assert base == "v2.1.0"


def test_determine_base_tag_priority_3_prerelease():
    releases = [
        {"tag_name": "v2.0.0", "prerelease": False},
        {"tag_name": "v2.1.0a1", "prerelease": True},
        {"tag_name": "v2.1.0a2", "prerelease": True},
    ]
    # For v2.1.0a2 (prerelease), base picks the immediately preceding release
    base = determine_base_tag(releases[-1], releases, set())
    assert base == "v2.1.0a1"


def test_determine_base_tag_priority_4_semver_fallback():
    current_rel = {"tag_name": "v2.4.0", "prerelease": False, "body": ""}
    # No earlier releases in the releases API list, but git tags exist
    git_tags = {"v1.0.0", "v2.0.0", "v2.3.0", "v2.4.0", "v3.0.0"}
    base = determine_base_tag(current_rel, [current_rel], git_tags)
    assert base == "v2.3.0"


def test_parse_existing_prs():
    body = (
        "* Add timeout option by @carlkidcrypto in"
        " https://github.com/carlkidcrypto/ezsnmp/pull/101\n* Fix leak by"
        " @contributor in https://github.com/carlkidcrypto/ezsnmp/pull/102\n"
    )
    git_commits = {
        "hash1": {
            "title": "feat: add timeout option (#101)",
            "files": ["ezsnmp/session.py"],
        },
        "hash2": {
            "title": "fix: fix leak (#102)",
            "files": ["ezsnmp/src/session.c"],
        },
    }
    prs, seen = parse_existing_prs(body, git_commits)
    assert seen == {"101", "102"}
    assert len(prs) == 2
    assert prs[0]["pr"] == "101"
    assert prs[0]["files"] == ["ezsnmp/session.py"]
    assert prs[1]["pr"] == "102"
    assert prs[1]["files"] == ["ezsnmp/src/session.c"]


def test_synthesize_summary():
    categories = {
        "Features / Enhancements": ["- Adds feature (#1)"],
        "Bug Fixes": ["- Fixes bug (#2)"],
        "Runtime / Core Library": [],
        "Tests": [],
        "Containers / Packaging": [],
        "CI / Workflows": [],
        "Documentation": [],
        "Dependencies": [],
        "Chores / Misc": [],
    }
    summary = synthesize_summary(categories, is_prerelease=False)
    assert "release focuses on features and enhancements and bug fixes" in summary

    summary_with_ctx = synthesize_summary(
        categories,
        is_prerelease=True,
        additional_context="Includes extra docs.",
    )
    assert "prerelease focuses on" in summary_with_ctx
    assert summary_with_ctx.endswith("Includes extra docs.")


def test_build_release_notes():
    release = {
        "tag_name": "v2.4.0",
        "prerelease": False,
        "body": (
            "* Add timeout option by @carlkidcrypto in"
            " https://github.com/carlkidcrypto/ezsnmp/pull/101\n"
        ),
    }
    git_commits: dict[str, dict[str, Any]] = {
        "aaa111122223333444455556666777788889999": {
            "title": "Add timeout option (#101)",
            "files": ["ezsnmp/session.py"],
        },
        "bbb111122223333444455556666777788889999": {
            "title": "fix: memory leak in walk (#102)",
            "files": ["ezsnmp/src/session.c"],
        },
    }
    notes = build_release_notes(release, "v2.3.0", git_commits)

    assert "Compared to: v2.3.0" in notes
    assert "pip install ezsnmp==2.4.0" in notes
    assert "https://pypi.org/project/ezsnmp/2.4.0/" in notes
    assert "## Features / Enhancements" in notes
    assert "- Adds timeout option (#101)" in notes
    assert "## Bug Fixes" in notes
    assert "- Fixes memory leak in walk (#102)" in notes
    assert (
        "**Full Changelog**:"
        " https://github.com/carlkidcrypto/ezsnmp/compare/v2.3.0...v2.4.0" in notes
    )


def test_build_release_notes_non_version_tag():
    release = {
        "tag_name": "custom_build",
        "prerelease": False,
        "body": "",
    }
    notes = build_release_notes(release, "repository root", {})
    # Should omit Install / Upgrade if not a valid version
    assert "## Install / Upgrade" not in notes
    assert "Compared to: repository root" in notes
    assert (
        "**Full Changelog**:"
        " https://github.com/carlkidcrypto/ezsnmp/commits/custom_build" in notes
    )
