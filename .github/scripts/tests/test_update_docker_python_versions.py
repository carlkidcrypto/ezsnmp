"""Unit tests for .github/scripts/update_docker_python_versions.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Dynamically import update_docker_python_versions from .github/scripts/
_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "update_docker_python_versions.py"
)
spec = importlib.util.spec_from_file_location(
    "update_docker_python_versions", str(_SCRIPT_PATH)
)
mod = importlib.util.module_from_spec(spec)
sys.modules["update_docker_python_versions"] = mod
spec.loader.exec_module(mod)

version_key = mod.version_key
fetch_available_versions = mod.fetch_available_versions
discover_tracked_versions = mod.discover_tracked_versions
build_replacement_map = mod.build_replacement_map
target_files = mod.target_files
apply_replacements = mod.apply_replacements
main = mod.main


def test_version_key():
    assert version_key("3.10.1") == (3, 10, 1)
    assert version_key("3.9.15") < version_key("3.10.2")
    assert version_key("3.14.7") < version_key("3.14.8")


def test_fetch_available_versions_single_page():
    mock_tags = [
        {"ref": "refs/tags/v3.10.1"},
        {"ref": "refs/tags/v3.10.2"},
        {"ref": "refs/tags/v3.11.0a1"},  # Pre-release ignored
        {"ref": "refs/tags/v3.11.0rc1"},  # Pre-release ignored
        {"ref": "refs/tags/v3.12.0"},
        {"ref": "refs/heads/main"},  # Non-tag ignored
    ]
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(mock_tags).encode("utf-8")
    mock_response.headers = {}
    mock_response.__enter__.return_value = mock_response

    with patch.object(mod, "urlopen", return_value=mock_response):
        versions = fetch_available_versions()

    assert versions == ["3.10.1", "3.10.2", "3.12.0"]


def test_fetch_available_versions_pagination():
    page1 = [{"ref": "refs/tags/v3.10.1"}]
    page2 = [{"ref": "refs/tags/v3.10.2"}]

    resp1 = MagicMock()
    resp1.read.return_value = json.dumps(page1).encode("utf-8")
    resp1.headers = {
        "Link": '<https://api.github.com/repos/python/cpython/git/refs/tags?page=2>; rel="next"'
    }
    resp1.__enter__.return_value = resp1

    resp2 = MagicMock()
    resp2.read.return_value = json.dumps(page2).encode("utf-8")
    resp2.headers = {}
    resp2.__enter__.return_value = resp2

    with patch.object(mod, "urlopen", side_effect=[resp1, resp2]) as mock_urlopen:
        versions = fetch_available_versions()
        assert mock_urlopen.call_count == 2

    assert versions == ["3.10.1", "3.10.2"]


def test_fetch_available_versions_with_auth_tokens(monkeypatch):
    mock_tags = [{"ref": "refs/tags/v3.12.1"}]
    resp = MagicMock()
    resp.read.return_value = json.dumps(mock_tags).encode("utf-8")
    resp.headers = {}
    resp.__enter__.return_value = resp

    # Test GITHUB_TOKEN
    monkeypatch.setenv("GITHUB_TOKEN", "token_123")
    monkeypatch.delenv("GH_TOKEN", raising=False)
    with patch.object(mod, "urlopen", return_value=resp) as mock_urlopen:
        fetch_available_versions()
        req = mock_urlopen.call_args[0][0]
        assert req.headers["Authorization"] == "Bearer token_123"

    # Test GH_TOKEN fallback
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("GH_TOKEN", "token_456")
    with patch.object(mod, "urlopen", return_value=resp) as mock_urlopen:
        fetch_available_versions()
        req = mock_urlopen.call_args[0][0]
        assert req.headers["Authorization"] == "Bearer token_456"


def test_fetch_available_versions_empty_raises():
    resp = MagicMock()
    resp.read.return_value = json.dumps([]).encode("utf-8")
    resp.headers = {}
    resp.__enter__.return_value = resp

    with patch.object(mod, "urlopen", return_value=resp):
        with pytest.raises(RuntimeError, match="No CPython versions were discovered"):
            fetch_available_versions()


def test_discover_tracked_versions(tmp_path):
    f1 = tmp_path / "Dockerfile.1"
    f1.write_text(
        "ARG PYTHON_BUILD_VERSION=3.10.5\nARG PYTHON_SYSTEM_VERSION=3.11.2 # comment",
        encoding="utf-8",
    )
    f2 = tmp_path / "Dockerfile.2"
    f2.write_text(
        "ARG PYTHON_MAX_VERSION=3.12.4\nARG PYTHON_BUILD_VERSION=3.10.5",
        encoding="utf-8",
    )

    tracked = discover_tracked_versions([f1, f2])
    assert tracked == ["3.10.5", "3.11.2", "3.12.4"]


def test_discover_tracked_versions_empty_raises(tmp_path):
    f1 = tmp_path / "Dockerfile.empty"
    f1.write_text("FROM ubuntu:24.04\nRUN apt-get update", encoding="utf-8")

    with pytest.raises(
        RuntimeError, match="No Dockerfile Python ARG versions were found"
    ):
        discover_tracked_versions([f1])


def test_build_replacement_map():
    current = ["3.10.10", "3.11.5", "3.12.1"]
    available = ["3.10.10", "3.10.15", "3.11.5", "3.12.1", "3.12.8", "3.13.0"]

    replacements = build_replacement_map(current, available)
    assert replacements == {
        "3.10.10": "3.10.15",
        "3.11.5": "3.11.5",
        "3.12.1": "3.12.8",
    }


def test_build_replacement_map_missing_minor_raises():
    current = ["3.9.1"]
    available = ["3.10.1", "3.11.1"]

    with pytest.raises(
        RuntimeError, match="No published CPython releases found for 3.9"
    ):
        build_replacement_map(current, available)


def test_apply_replacements(tmp_path):
    test_file = tmp_path / "Dockerfile"
    test_file.write_text(
        "ARG PYTHON_BUILD_VERSION=3.10.10\nARG PYTHON_OTHER_VERSION=3.11.5",
        encoding="utf-8",
    )

    replacements = {"3.10.10": "3.10.15", "3.11.5": "3.11.5"}

    # write=False should report True (changed) but not modify disk
    assert apply_replacements(test_file, replacements, write=False) is True
    assert (
        test_file.read_text(encoding="utf-8")
        == "ARG PYTHON_BUILD_VERSION=3.10.10\nARG PYTHON_OTHER_VERSION=3.11.5"
    )

    # write=True should modify disk
    assert apply_replacements(test_file, replacements, write=True) is True
    assert (
        test_file.read_text(encoding="utf-8")
        == "ARG PYTHON_BUILD_VERSION=3.10.15\nARG PYTHON_OTHER_VERSION=3.11.5"
    )

    # Running again with same replacements should report False (no change)
    assert apply_replacements(test_file, replacements, write=True) is False


def test_target_files():
    mock_dockerfiles = [Path("/repo/docker/ubuntu/Dockerfile")]
    with (
        patch(
            "pathlib.Path.glob",
            return_value=[Path("/repo/docker/ubuntu/README.rst")],
        ),
    ):
        targets = target_files(mock_dockerfiles)
        assert mock_dockerfiles[0] in targets
        assert Path("/repo/docker/ubuntu/README.rst") in targets
        assert any("download_build_cache.sh" in str(p) for p in targets)


def test_main_with_updates(tmp_path, monkeypatch, capsys):
    dockerfile = tmp_path / "docker" / "test" / "Dockerfile"
    dockerfile.parent.mkdir(parents=True)
    dockerfile.write_text("ARG PYTHON_MAX_VERSION=3.10.1\n", encoding="utf-8")

    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "discover_tracked_versions", lambda dfs: ["3.10.1"])
    monkeypatch.setattr(mod, "fetch_available_versions", lambda: ["3.10.1", "3.10.5"])
    monkeypatch.setattr(mod, "target_files", lambda dfs: [dockerfile])

    # Test dry-run (--write omitted)
    monkeypatch.setattr(sys, "argv", ["update_docker_python_versions.py"])
    exit_code = main()
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "update available -> 3.10.5" in out
    assert "Would update files:" in out
    assert "3.10.1" in dockerfile.read_text(encoding="utf-8")

    # Test with --write
    monkeypatch.setattr(sys, "argv", ["update_docker_python_versions.py", "--write"])
    exit_code = main()
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Updated files:" in out
    assert "3.10.5" in dockerfile.read_text(encoding="utf-8")

    # Test up-to-date
    exit_code = main()
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "All tracked Docker Python versions are already current." in out
