import importlib.util
from pathlib import Path

import pytest


SETUP_PATH = Path(__file__).resolve().parents[1] / "setup.py"
SPEC = importlib.util.spec_from_file_location("ezsnmp_setup", SETUP_PATH)
SETUP_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SETUP_MODULE)


def test_resolve_windows_netsnmp_version_from_header(tmp_path, monkeypatch):
    monkeypatch.delenv("EZSNMP_NETSNMP_VERSION", raising=False)
    monkeypatch.delenv("NETSNMP_VERSION", raising=False)

    header_path = tmp_path / "net-snmp" / "net-snmp-config.h"
    header_path.parent.mkdir(parents=True)
    header_path.write_text('#define PACKAGE_VERSION "5.10.2"\n', encoding="utf-8")

    assert SETUP_MODULE.resolve_windows_netsnmp_version([str(tmp_path)]) == "5.10.2"


def test_gather_build_configuration_windows_uses_env_vars(tmp_path, monkeypatch):
    include_dir = tmp_path / "include"
    lib_dir = tmp_path / "lib"
    header_path = include_dir / "net-snmp" / "net-snmp-config.h"
    header_path.parent.mkdir(parents=True)
    header_path.write_text('#define PACKAGE_VERSION "5.9.4"\n', encoding="utf-8")
    lib_dir.mkdir()

    monkeypatch.setattr(SETUP_MODULE, "platform", "win32")
    monkeypatch.setattr(SETUP_MODULE, "argv", ["setup.py"])
    monkeypatch.setenv("EZSNMP_NETSNMP_INCLUDE_DIR", str(include_dir))
    monkeypatch.setenv("EZSNMP_NETSNMP_LIB_DIR", str(lib_dir))
    monkeypatch.delenv("EZSNMP_NETSNMP_LIBS", raising=False)

    cfg = SETUP_MODULE.gather_build_configuration()

    assert cfg["compile_args"] == ["/std:c++17", "/EHsc"]
    assert cfg["libdirs"] == [str(lib_dir)]
    assert cfg["incdirs"] == ["ezsnmp/include/", str(include_dir)]
    assert cfg["libs"] == ["netsnmp", "advapi32", "ws2_32", "kernel32", "user32"]
    assert cfg["system_netsnmp_version"] == "5.9.4"


def test_gather_build_configuration_windows_supports_dll_imports(tmp_path, monkeypatch):
    include_dir = tmp_path / "include"
    lib_dir = tmp_path / "lib"
    header_path = include_dir / "net-snmp" / "net-snmp-config.h"
    header_path.parent.mkdir(parents=True)
    header_path.write_text('#define PACKAGE_VERSION "5.10.1"\n', encoding="utf-8")
    lib_dir.mkdir()

    monkeypatch.setattr(SETUP_MODULE, "platform", "win32")
    monkeypatch.setattr(SETUP_MODULE, "argv", ["setup.py"])
    monkeypatch.setenv("EZSNMP_NETSNMP_INCLUDE_DIR", str(include_dir))
    monkeypatch.setenv("EZSNMP_NETSNMP_LIB_DIR", str(lib_dir))
    monkeypatch.setenv("EZSNMP_NETSNMP_USE_DLL", "1")

    cfg = SETUP_MODULE.gather_build_configuration()

    assert "/DNETSNMP_USE_DLL" in cfg["compile_args"]


def test_gather_build_configuration_windows_requires_paths(monkeypatch):
    monkeypatch.setattr(SETUP_MODULE, "platform", "win32")
    monkeypatch.setattr(SETUP_MODULE, "argv", ["setup.py"])
    monkeypatch.delenv("EZSNMP_NETSNMP_INCLUDE_DIR", raising=False)
    monkeypatch.delenv("EZSNMP_NETSNMP_INCLUDEDIR", raising=False)
    monkeypatch.delenv("NETSNMP_INCLUDE_DIR", raising=False)
    monkeypatch.delenv("NETSNMP_INCLUDEDIR", raising=False)
    monkeypatch.delenv("EZSNMP_NETSNMP_LIB_DIR", raising=False)
    monkeypatch.delenv("EZSNMP_NETSNMP_LIBDIR", raising=False)
    monkeypatch.delenv("NETSNMP_LIB_DIR", raising=False)
    monkeypatch.delenv("NETSNMP_LIBDIR", raising=False)

    with pytest.raises(RuntimeError, match="EZSNMP_NETSNMP_INCLUDE_DIR"):
        SETUP_MODULE.gather_build_configuration()
