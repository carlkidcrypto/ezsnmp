"""Unit tests for python_tests/normalize_coverage_paths.py."""

import importlib.util
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Dynamically import normalize_coverage_paths from python_tests/
_SCRIPT_PATH = Path(__file__).resolve().parent / "normalize_coverage_paths.py"
spec = importlib.util.spec_from_file_location(
    "normalize_coverage_paths", str(_SCRIPT_PATH)
)
normalize_mod = importlib.util.module_from_spec(spec)
sys.modules["normalize_coverage_paths"] = normalize_mod
spec.loader.exec_module(normalize_mod)

normalize_filename = normalize_mod.normalize_filename
normalize_coverage_tree = normalize_mod.normalize_coverage_tree
normalize_coverage_file = normalize_mod.normalize_coverage_file
collect_target_files = normalize_mod.collect_target_files


def test_normalize_filename_hostedtoolcache_absolute():
    fn = "/opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/site-packages/ezsnmp/session.py"
    assert normalize_filename(fn) == "ezsnmp/session.py"


def test_normalize_filename_hostedtoolcache_relative():
    fn = "opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/site-packages/ezsnmp/datatypes.py"
    assert normalize_filename(fn) == "ezsnmp/datatypes.py"


def test_normalize_filename_docker_venv():
    fn = "/tmp/venv_py311/lib/python3.11/site-packages/ezsnmp/sessionbase.py"
    assert normalize_filename(fn) == "ezsnmp/sessionbase.py"


def test_normalize_filename_dist_packages():
    fn = "/usr/local/lib/python3.10/dist-packages/ezsnmp/exceptions.py"
    assert normalize_filename(fn) == "ezsnmp/exceptions.py"


def test_normalize_filename_shadow_dir():
    fn = "_ezsnmp/session.py"
    assert normalize_filename(fn) == "ezsnmp/session.py"


def test_normalize_filename_nested_ezsnmp():
    fn = "/home/runner/work/ezsnmp/ezsnmp/ezsnmp/session.py"
    assert normalize_filename(fn) == "ezsnmp/session.py"


def test_normalize_filename_already_normalized():
    fn = "ezsnmp/__init__.py"
    assert normalize_filename(fn) == "ezsnmp/__init__.py"


def test_normalize_filename_windows_separators():
    fn = r"C:\hostedtoolcache\windows\Python\3.11.0\x64\Lib\site-packages\ezsnmp\session.py"
    assert normalize_filename(fn) == "ezsnmp/session.py"


def test_normalize_coverage_tree():
    sample_xml = """<?xml version="1.0" ?>
<coverage version="7.16.1" lines-valid="10" lines-covered="9">
    <sources>
        <source>/opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/site-packages</source>
    </sources>
    <packages>
        <package name=".opt.hostedtoolcache.Python.3.11.16.x64.lib.python3.11.site-packages.ezsnmp">
            <classes>
                <class name="__init__.py" filename="/opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/site-packages/ezsnmp/__init__.py">
                    <lines>
                        <line number="1" hits="1"/>
                    </lines>
                </class>
                <class name="session.py" filename="opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/site-packages/ezsnmp/session.py">
                    <lines>
                        <line number="1" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""
    tree = ET.ElementTree(ET.fromstring(sample_xml))
    modified, total = normalize_coverage_tree(tree)

    assert total == 2
    assert modified == 2

    root = tree.getroot()
    sources = [s.text for s in root.iter("source")]
    assert sources == ["."]

    classes = {c.attrib["name"]: c.attrib["filename"] for c in root.iter("class")}
    assert classes["__init__.py"] == "ezsnmp/__init__.py"
    assert classes["session.py"] == "ezsnmp/session.py"

    packages = [p.attrib["name"] for p in root.iter("package")]
    assert packages == ["ezsnmp"]


def test_normalize_coverage_file_in_place():
    sample_xml = """<?xml version="1.0" ?>
<coverage version="7.16.1">
    <sources><source></source></sources>
    <packages>
        <package name="ezsnmp">
            <classes>
                <class name="session.py" filename="/tmp/venv_py312/lib/python3.12/site-packages/ezsnmp/session.py">
                    <lines><line number="1" hits="1"/></lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""
    with tempfile.NamedTemporaryFile(suffix=".xml", mode="w", delete=False) as tf:
        tf.write(sample_xml)
        tf_path = Path(tf.name)

    try:
        assert normalize_coverage_file(tf_path) is True

        tree = ET.parse(tf_path)
        root = tree.getroot()
        cls = next(root.iter("class"))
        assert cls.attrib["filename"] == "ezsnmp/session.py"
        src = next(root.iter("source"))
        assert src.text == "."
    finally:
        tf_path.unlink(missing_ok=True)
