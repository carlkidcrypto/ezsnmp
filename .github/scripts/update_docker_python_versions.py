#!/usr/bin/env python3
"""Update Docker-related Python patch versions to the latest published releases."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
GITHUB_CPYTHON_TAGS_URL = (
    "https://api.github.com/repos/python/cpython/git/refs/tags?per_page=100"
)
ARG_VERSION_PATTERN = re.compile(
    r"^(ARG\s+PYTHON_[A-Z0-9_]+_VERSION=)(\d+\.\d+\.\d+)(\s*(?:#.*)?)$", re.MULTILINE
)
TAG_VERSION_PATTERN = re.compile(r"refs/tags/v(\d+\.\d+\.\d+)$")
LINK_NEXT_PATTERN = re.compile(r'<([^>]+)>;\s*rel="next"')


def version_key(version: str) -> tuple[int, int, int]:
    """Convert a dotted Python version into a sortable integer tuple.

    :param version: The dotted CPython version string.
    :type version: str
    :return: A tuple suitable for semantic version ordering.
    :rtype: tuple[int, int, int]
    """
    return tuple(int(part) for part in version.split("."))


def fetch_available_versions() -> list[str]:
    """Fetch all published CPython final releases from the GitHub CPython repository.

    Uses the GitHub API tags endpoint (api.github.com) to enumerate all CPython
    release tags of the form ``vX.Y.Z`` (pre-release suffixes such as ``a``, ``b``,
    and ``rc`` are excluded).

    :return: All discovered CPython release versions, sorted by version.
    :rtype: list[str]
    :raises RuntimeError: If no version tags are discovered.
    """
    versions: set[str] = set()
    url: str | None = GITHUB_CPYTHON_TAGS_URL
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ezsnmp-update-docker-python-versions/1.0",
    }
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"

    while url:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=30) as response:
            tags = json.loads(response.read().decode("utf-8"))
            link_header = response.headers.get("Link", "")

        for tag in tags:
            ref = tag.get("ref", "")
            match = TAG_VERSION_PATTERN.match(ref)
            if match:
                versions.add(match.group(1))

        next_match = LINK_NEXT_PATTERN.search(link_header)
        url = next_match.group(1) if next_match else None

    if not versions:
        raise RuntimeError(
            "No CPython versions were discovered from the GitHub CPython repository"
        )
    return sorted(versions, key=version_key)


def discover_tracked_versions(dockerfiles: list[Path]) -> list[str]:
    """Collect the Python patch versions currently tracked by Dockerfile ARGs.

    :param dockerfiles: Dockerfiles that define `PYTHON_*_VERSION` build arguments.
    :type dockerfiles: list[pathlib.Path]
    :return: The unique tracked patch versions sorted in ascending order.
    :rtype: list[str]
    :raises RuntimeError: If no Dockerfile Python ARG versions are found.
    """
    tracked_versions: set[str] = set()
    for dockerfile in dockerfiles:
        content = dockerfile.read_text(encoding="utf-8")
        tracked_versions.update(
            match.group(2) for match in ARG_VERSION_PATTERN.finditer(content)
        )

    if not tracked_versions:
        raise RuntimeError("No Dockerfile Python ARG versions were found")

    return sorted(tracked_versions, key=version_key)


def build_replacement_map(
    current_versions: list[str], available_versions: list[str]
) -> dict[str, str]:
    """Map each tracked Python patch version to the latest published patch for its minor line.

    :param current_versions: The currently pinned Docker Python patch versions.
    :type current_versions: list[str]
    :param available_versions: All published CPython patch versions discovered upstream.
    :type available_versions: list[str]
    :return: A mapping from the current patch version to the latest available patch version.
    :rtype: dict[str, str]
    :raises RuntimeError: If an expected minor version line is missing upstream.
    """
    replacements: dict[str, str] = {}
    for current_version in current_versions:
        minor = ".".join(current_version.split(".")[:2])
        candidates = [
            version for version in available_versions if version.startswith(f"{minor}.")
        ]
        if not candidates:
            raise RuntimeError(f"No published CPython releases found for {minor}")

        latest = max(candidates, key=version_key)
        replacements[current_version] = latest

    return replacements


def target_files(dockerfiles: list[Path]) -> list[Path]:
    """Return every tracked file that should change when Docker Python patch versions change.

    :param dockerfiles: A list of Dockerfiles to include.
    :type dockerfiles: list[pathlib.Path]
    :return: Dockerfiles, Docker READMEs, and the cache download script.
    :rtype: list[pathlib.Path]
    """
    readmes = sorted(REPO_ROOT.glob("docker/**/README.rst"))
    cache_script = REPO_ROOT / "docker/cache/download_build_cache.sh"
    return dockerfiles + readmes + [cache_script]


def apply_replacements(path: Path, replacements: dict[str, str], write: bool) -> bool:
    """Apply version substitutions to a single tracked file.

    :param path: The file to inspect and optionally update.
    :type path: pathlib.Path
    :param replacements: Mapping of existing patch versions to replacement versions.
    :type replacements: dict[str, str]
    :param write: Whether to persist the updated content to disk.
    :type write: bool
    :return: `True` if the file content changed, otherwise `False`.
    :rtype: bool
    """
    original = path.read_text(encoding="utf-8")
    updated = original

    for old_version, new_version in sorted(
        replacements.items(), key=lambda item: len(item[0]), reverse=True
    ):
        if old_version == new_version:
            continue
        updated = updated.replace(old_version, new_version)

    if updated == original:
        return False

    if write:
        path.write_text(updated, encoding="utf-8")

    return True


def main() -> int:
    """Run the Docker Python patch version updater CLI.

    :return: Process exit status code.
    :rtype: int
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write file updates in place. Without this flag the script reports pending changes only.",
    )
    args = parser.parse_args()

    dockerfiles = sorted(REPO_ROOT.glob("docker/**/Dockerfile"))
    current_versions = discover_tracked_versions(dockerfiles)
    available_versions = fetch_available_versions()
    replacements = build_replacement_map(current_versions, available_versions)

    changed_files: list[Path] = []
    for path in target_files(dockerfiles):
        if apply_replacements(path, replacements, write=args.write):
            changed_files.append(path)

    print("Tracked Python patch versions:")
    for old_version, new_version in replacements.items():
        status = (
            "up-to-date"
            if old_version == new_version
            else f"update available -> {new_version}"
        )
        print(f"  {old_version}: {status}")

    if changed_files:
        action = "Updated" if args.write else "Would update"
        print(f"\n{action} files:")
        for path in changed_files:
            print(f"  {path.relative_to(REPO_ROOT)}")
    else:
        print("\nAll tracked Docker Python versions are already current.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - defensive CLI guard
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
