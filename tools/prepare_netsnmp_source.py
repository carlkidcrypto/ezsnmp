#!/usr/bin/env python3
"""Provision the pinned Net-SNMP 5.10 source tree via shallow git submodule/clone or verified archive."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NETSNMP_REPO_URL = "https://github.com/net-snmp/net-snmp.git"
NETSNMP_VERSION = "5.10.rc1"
NETSNMP_TAG = f"v{NETSNMP_VERSION}"
NETSNMP_ARCHIVE_URL = (
    f"https://github.com/net-snmp/net-snmp/archive/refs/tags/{NETSNMP_TAG}.tar.gz"
)
NETSNMP_EXPECTED_SHA256 = (
    "009cbda7879b1c75cee01df9f4eab2797df47c6c5f90b70aed3e51dce89d8e76"
)
ALLOWED_TAGS: dict[str, tuple[str, str, str]] = {
    NETSNMP_TAG: (NETSNMP_TAG, NETSNMP_VERSION, NETSNMP_EXPECTED_SHA256),
    NETSNMP_VERSION: (NETSNMP_TAG, NETSNMP_VERSION, NETSNMP_EXPECTED_SHA256),
}


def _is_valid_netsnmp_tree(path: Path) -> bool:
    return (path / "configure").is_file() and (path / "include" / "net-snmp").is_dir()


def _resolve_safe_tag(tag: str) -> tuple[str, str, str]:
    resolved = ALLOWED_TAGS.get(tag.strip())
    if resolved is None:
        raise ValueError(
            f"Unsupported Net-SNMP tag {tag!r}; allowed values: {sorted(ALLOWED_TAGS)}"
        )
    return resolved


def _resolve_safe_dest(target_dir: Path | None) -> Path:
    vendored = (REPO_ROOT / "third_party" / "net-snmp").resolve()
    if target_dir is None:
        return vendored
    resolved = target_dir.resolve()
    if not resolved.is_relative_to(REPO_ROOT.resolve()):
        raise ValueError(
            f"Target directory {resolved} must remain within repository root {REPO_ROOT.resolve()}"
        )
    return resolved


def _download_and_extract_archive(
    dest: Path,
    version: str = NETSNMP_VERSION,
    expected_sha256: str = NETSNMP_EXPECTED_SHA256,
) -> Path:
    archive_url = (
        f"https://github.com/net-snmp/net-snmp/archive/refs/tags/v{version}.tar.gz"
    )
    with tempfile.TemporaryDirectory(prefix="ezsnmp-netsnmp-src-") as tmp_dir:
        tmp_path = Path(tmp_dir)
        archive_path = tmp_path / f"v{version}.tar.gz"
        urllib.request.urlretrieve(archive_url, archive_path)
        if expected_sha256:
            digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
            if digest != expected_sha256:
                raise RuntimeError(
                    f"Net-SNMP archive SHA256 mismatch: expected {expected_sha256}, got {digest}"
                )
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=tmp_path)
        extracted = tmp_path / f"net-snmp-{version}"
        if not _is_valid_netsnmp_tree(extracted):
            raise RuntimeError(
                f"Extracted Net-SNMP archive at {extracted} is missing configure/headers"
            )
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(extracted), str(dest))
    return dest


def ensure_netsnmp_source(
    target_dir: Path | None = None,
    tag: str = NETSNMP_TAG,
    expected_sha256: str = NETSNMP_EXPECTED_SHA256,
) -> Path:
    """Locate third_party/net-snmp or shallow-clone pinned Net-SNMP 5.10 tag into third_party/net-snmp."""
    env_dir = os.environ.get("EZSNMP_NETSNMP_SOURCE_DIR", "").strip()
    if env_dir:
        cand = Path(env_dir).resolve()
        if _is_valid_netsnmp_tree(cand):
            return cand

    safe_tag, safe_version, default_sha256 = _resolve_safe_tag(tag)
    vendored = (REPO_ROOT / "third_party" / "net-snmp").resolve()
    dest = _resolve_safe_dest(target_dir)
    if _is_valid_netsnmp_tree(dest):
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    git_bin = shutil.which("git")
    if git_bin:
        gitmodules_file = REPO_ROOT / ".gitmodules"
        if dest == vendored and gitmodules_file.is_file():
            try:
                subprocess.run(
                    [
                        git_bin,
                        "-C",
                        str(REPO_ROOT),
                        "submodule",
                        "update",
                        "--init",
                        "--depth",
                        "1",
                        "--",
                        "third_party/net-snmp",
                    ],
                    check=True,
                )
                if _is_valid_netsnmp_tree(dest):
                    return dest
            except subprocess.CalledProcessError:
                pass

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                if dest.exists():
                    shutil.rmtree(dest, ignore_errors=True)
                subprocess.run(
                    [
                        git_bin,
                        "clone",
                        "--depth",
                        "1",
                        f"--branch={safe_tag}",
                        "--",
                        NETSNMP_REPO_URL,
                        str(dest),
                    ],
                    check=True,
                )
                if _is_valid_netsnmp_tree(dest):
                    return dest
            except subprocess.CalledProcessError:
                if attempt == max_retries:
                    break
                time.sleep(2 * attempt)

    return _download_and_extract_archive(
        dest=dest,
        version=safe_version,
        expected_sha256=expected_sha256 or default_sha256,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ensure pinned Net-SNMP 5.10 source tree is available under third_party/net-snmp."
    )
    parser.add_argument(
        "--tag",
        default=NETSNMP_TAG,
        choices=sorted(ALLOWED_TAGS.keys()),
    )
    args = parser.parse_args(argv)

    resolved = ensure_netsnmp_source(tag=args.tag)
    print(f"Net-SNMP 5.10 source ready ({args.tag}): {resolved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
