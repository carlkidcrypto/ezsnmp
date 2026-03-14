#!/usr/bin/env python3
"""Update Docker-related Python patch versions to the latest published releases."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.request import urlopen


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_FTP_INDEX = "https://www.python.org/ftp/python/"
ARG_VERSION_PATTERN = re.compile(r"^(ARG\s+PYTHON_[A-Z0-9_]+_VERSION=)(\d+\.\d+\.\d+)(\s*(?:#.*)?)$", re.MULTILINE)
FTP_VERSION_PATTERN = re.compile(r'href="(\d+\.\d+\.\d+)/"')


def version_key(version: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in version.split("."))


def fetch_available_versions() -> list[str]:
    with urlopen(PYTHON_FTP_INDEX, timeout=30) as response:
        html = response.read().decode("utf-8")

    versions = {match.group(1) for match in FTP_VERSION_PATTERN.finditer(html)}
    if not versions:
        raise RuntimeError("No CPython versions were discovered from the python.org FTP index")
    return sorted(versions, key=version_key)


def discover_tracked_versions(dockerfiles: list[Path]) -> list[str]:
    tracked_versions: set[str] = set()
    for dockerfile in dockerfiles:
        content = dockerfile.read_text(encoding="utf-8")
        tracked_versions.update(match.group(2) for match in ARG_VERSION_PATTERN.finditer(content))

    if not tracked_versions:
        raise RuntimeError("No Dockerfile Python ARG versions were found")

    return sorted(tracked_versions, key=version_key)


def build_replacement_map(current_versions: list[str], available_versions: list[str]) -> dict[str, str]:
    replacements: dict[str, str] = {}
    for current_version in current_versions:
        minor = ".".join(current_version.split(".")[:2])
        candidates = [version for version in available_versions if version.startswith(f"{minor}.")]
        if not candidates:
            raise RuntimeError(f"No published CPython releases found for {minor}")

        latest = max(candidates, key=version_key)
        replacements[current_version] = latest

    return replacements


def target_files() -> list[Path]:
    dockerfiles = sorted(REPO_ROOT.glob("docker/**/Dockerfile"))
    readmes = sorted(REPO_ROOT.glob("docker/**/README.rst"))
    cache_script = REPO_ROOT / "docker/cache/download_build_cache.sh"
    return dockerfiles + readmes + [cache_script]


def apply_replacements(path: Path, replacements: dict[str, str], write: bool) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = original

    for old_version, new_version in replacements.items():
        if old_version == new_version:
            continue
        updated = updated.replace(old_version, new_version)

    if updated == original:
        return False

    if write:
        path.write_text(updated, encoding="utf-8")

    return True


def main() -> int:
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
    for path in target_files():
        if apply_replacements(path, replacements, write=args.write):
            changed_files.append(path)

    print("Tracked Python patch versions:")
    for old_version, new_version in replacements.items():
        status = "up-to-date" if old_version == new_version else f"update available -> {new_version}"
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