#!/usr/bin/env python3
"""Normalize file paths in Cobertura coverage XML reports for ezsnmp.

When tests run in CI (native Linux runners, Docker containers, tox, etc.),
Python imports ezsnmp from an installed location (e.g. site-packages) or
from a temporary shadowed directory (e.g. _ezsnmp). The coverage XML generated
by pytest-cov/coverage.py records these execution paths (for example:
`/opt/hostedtoolcache/Python/.../site-packages/ezsnmp/session.py` or
`/tmp/venv_*/lib/python*/site-packages/ezsnmp/session.py`).

Codecov cannot map these external/absolute paths to the repository tree.
This script normalizes all ezsnmp file paths in Cobertura XML files to
repository-relative paths (`ezsnmp/<filename>`) and normalizes `<sources>`
so Codecov and other reporting tools correctly attribute line coverage
to the repository source files.
"""

import glob
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple

# Pattern matching installed site-packages, dist-packages, or renamed ezsnmp directories
_RE_SITE_PACKAGES = re.compile(
    r"^(?:.*?[/\\])?(?:site-packages|dist-packages)[/\\]ezsnmp[/\\](.*)$"
)
_RE_SHADOW_EZSNMP = re.compile(r"^(?:.*?[/\\])?_ezsnmp[/\\](.*)$")
_RE_NESTED_EZSNMP = re.compile(r"^(?:.*?[/\\])?ezsnmp[/\\]ezsnmp[/\\](.*)$")
_RE_ABSOLUTE_EZSNMP = re.compile(r"^(?:[A-Za-z]:[/\\]|/|\\).*?[/\\]ezsnmp[/\\](.*)$")


def normalize_filename(filename: str) -> str:
    """Normalize a filename from coverage report to repository-relative `ezsnmp/...`.

    :param filename: Original filename attribute from Cobertura XML class.
    :return: Normalized repository-relative path.
    """
    # Normalize path separators
    normalized = filename.replace("\\", "/")

    # Check for shadowed _ezsnmp first (e.g. _ezsnmp/session.py or /ezsnmp/_ezsnmp/session.py)
    if "/_ezsnmp/" in normalized:
        return "ezsnmp/" + normalized.split("/_ezsnmp/")[-1]
    if normalized.startswith("_ezsnmp/"):
        return "ezsnmp/" + normalized.split("_ezsnmp/", 1)[1]

    # Check for site-packages / dist-packages
    m = _RE_SITE_PACKAGES.match(normalized)
    if m:
        return f"ezsnmp/{m.group(1)}"

    # Check for any path containing /ezsnmp/ (e.g. /home/runner/work/ezsnmp/ezsnmp/ezsnmp/session.py)
    if "/ezsnmp/" in normalized:
        return "ezsnmp/" + normalized.split("/ezsnmp/")[-1]

    # Already relative ezsnmp/<file>
    if normalized.startswith("ezsnmp/"):
        return normalized

    return normalized


def normalize_coverage_tree(tree: ET.ElementTree) -> Tuple[int, int]:
    """Normalize classes and sources in a Cobertura XML ElementTree.

    :param tree: Parsed XML ElementTree.
    :return: Tuple of (classes_modified, total_classes).
    """
    root = tree.getroot()

    # Normalize <sources> to point to current directory
    sources = root.find("sources")
    if sources is not None:
        sources.clear()
        source = ET.SubElement(sources, "source")
        source.text = "."
    else:
        sources = ET.SubElement(root, "sources")
        source = ET.SubElement(sources, "source")
        source.text = "."

    modified_count = 0
    total_count = 0

    # Normalize <class filename="...">
    for cls in root.iter("class"):
        total_count += 1
        orig_fn = cls.attrib.get("filename", "")
        new_fn = normalize_filename(orig_fn)
        if new_fn != orig_fn:
            cls.attrib["filename"] = new_fn
            modified_count += 1

    # Normalize <package name="...">
    for pkg in root.iter("package"):
        pkg_name = pkg.attrib.get("name", "")
        if "ezsnmp" in pkg_name:
            m = re.search(r"ezsnmp(?:\.(.*))?$", pkg_name)
            if m:
                sub = m.group(1)
                pkg.attrib["name"] = f"ezsnmp.{sub}" if sub else "ezsnmp"
            else:
                pkg.attrib["name"] = "ezsnmp"

    return modified_count, total_count


def normalize_coverage_file(file_path: Path) -> bool:
    """Normalize a single Cobertura XML coverage file in place.

    :param file_path: Path to the XML file.
    :return: True if the file was processed, False otherwise.
    """
    try:
        tree = ET.parse(file_path)
    except Exception as e:
        print(f"  [SKIP] Could not parse {file_path}: {e}")
        return False

    modified, total = normalize_coverage_tree(tree)

    # Write out with XML declaration
    try:
        tree.write(
            file_path,
            encoding="utf-8",
            xml_declaration=True,
        )
        print(f"  [OK] {file_path}: updated {modified}/{total} classes")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to write {file_path}: {e}")
        return False


def collect_target_files(args: List[str]) -> List[Path]:
    """Collect unique target XML files from arguments or default globs.

    :param args: Command line arguments (file paths or globs).
    :return: List of resolved Path objects for existing files.
    """
    targets: List[Path] = []
    seen = set()

    patterns = (
        args
        if args
        else [
            "coverage_*.xml",
            "coverage.xml",
            "docker/coverage_*.xml",
            "**/coverage_*.xml",
        ]
    )

    for pattern in patterns:
        matched = glob.glob(pattern, recursive=True)
        if not matched and os.path.isfile(pattern):
            matched = [pattern]
        for p in matched:
            resolved = Path(p).resolve()
            if resolved.is_file() and resolved not in seen:
                seen.add(resolved)
                targets.append(Path(p))

    return targets


def main() -> int:
    """CLI entry point."""
    print("Normalizing coverage XML paths for Codecov...")
    files = collect_target_files(sys.argv[1:])

    if not files:
        print("No coverage XML files found to normalize.")
        return 0

    success = 0
    for f in files:
        if normalize_coverage_file(f):
            success += 1

    print(f"Finished: normalized {success}/{len(files)} coverage file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
