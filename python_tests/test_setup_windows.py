import build_utils

import pytest


def test_resolve_windows_netsnmp_version_from_header(tmp_path, monkeypatch):
    monkeypatch.delenv("EZSNMP_NETSNMP_VERSION", raising=False)
    monkeypatch.delenv("NETSNMP_VERSION", raising=False)

    header_path = tmp_path / "net-snmp" / "net-snmp-config.h"
    header_path.parent.mkdir(parents=True)
    header_path.write_text('#define PACKAGE_VERSION "5.10.2"\n', encoding="utf-8")

    assert build_utils.resolve_windows_netsnmp_version([str(tmp_path)]) == "5.10.2"


def test_resolve_windows_netsnmp_version_from_fallback_header_path(
    tmp_path, monkeypatch
):
    monkeypatch.delenv("EZSNMP_NETSNMP_VERSION", raising=False)
    monkeypatch.delenv("NETSNMP_VERSION", raising=False)

    header_path = tmp_path / "net-snmp-config.h"
    header_path.write_text('#define PACKAGE_VERSION "5.8.9"\n', encoding="utf-8")

    assert build_utils.resolve_windows_netsnmp_version([str(tmp_path)]) == "5.8.9"


def test_resolve_windows_netsnmp_version_requires_header_or_env(tmp_path, monkeypatch):
    monkeypatch.delenv("EZSNMP_NETSNMP_VERSION", raising=False)
    monkeypatch.delenv("NETSNMP_VERSION", raising=False)

    with pytest.raises(RuntimeError, match="Unable to determine the Net-SNMP version"):
        build_utils.resolve_windows_netsnmp_version([str(tmp_path)])


def test_split_env_list_supports_multiple_delimiters():
    assert build_utils.split_env_list("alpha;beta,gamma") == ["alpha", "beta", "gamma"]


def test_get_first_env_returns_first_available(monkeypatch):
    monkeypatch.delenv("EZSNMP_PRIMARY", raising=False)
    monkeypatch.setenv("EZSNMP_SECONDARY", "second")
    monkeypatch.setenv("EZSNMP_TERTIARY", "third")

    assert (
        build_utils.get_first_env(
            "EZSNMP_PRIMARY", "EZSNMP_SECONDARY", "EZSNMP_TERTIARY"
        )
        == "second"
    )


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "Yes", "on"])
def test_env_truthy_accepts_common_true_values(monkeypatch, value):
    monkeypatch.setenv("EZSNMP_BOOL", value)

    assert build_utils.env_truthy("EZSNMP_BOOL")


def test_env_truthy_uses_fallback_names(monkeypatch):
    monkeypatch.delenv("EZSNMP_BOOL_PRIMARY", raising=False)
    monkeypatch.setenv("EZSNMP_BOOL_FALLBACK", "true")

    assert build_utils.env_truthy("EZSNMP_BOOL_PRIMARY", "EZSNMP_BOOL_FALLBACK")


def test_gather_build_configuration_windows_uses_env_vars(tmp_path, monkeypatch):
    include_dir = tmp_path / "include"
    lib_dir = tmp_path / "lib"
    header_path = include_dir / "net-snmp" / "net-snmp-config.h"
    header_path.parent.mkdir(parents=True)
    header_path.write_text('#define PACKAGE_VERSION "5.9.4"\n', encoding="utf-8")
    lib_dir.mkdir()

    monkeypatch.setattr(build_utils, "platform", "win32")
    monkeypatch.setattr(build_utils, "argv", ["setup.py"])
    monkeypatch.setenv("EZSNMP_NETSNMP_INCLUDE_DIR", str(include_dir))
    monkeypatch.setenv("EZSNMP_NETSNMP_LIB_DIR", str(lib_dir))
    monkeypatch.delenv("EZSNMP_NETSNMP_LIBS", raising=False)

    cfg = build_utils.gather_build_configuration()

    assert cfg["compile_args"] == ["/std:c++17", "/EHsc"]
    assert cfg["libdirs"] == [str(lib_dir)]
    assert cfg["incdirs"] == ["ezsnmp/include/", str(include_dir)]
    assert cfg["libs"] == ["netsnmp", "advapi32", "ws2_32", "kernel32", "user32"]
    assert cfg["system_netsnmp_version"] == "5.9.4"


def test_gather_build_configuration_windows_uses_custom_library_list(
    tmp_path, monkeypatch
):
    include_dir = tmp_path / "include"
    lib_dir = tmp_path / "lib"
    header_path = include_dir / "net-snmp" / "net-snmp-config.h"
    header_path.parent.mkdir(parents=True)
    header_path.write_text('#define PACKAGE_VERSION "5.9.4"\n', encoding="utf-8")
    lib_dir.mkdir()

    monkeypatch.setattr(build_utils, "platform", "win32")
    monkeypatch.setattr(build_utils, "argv", ["setup.py"])
    monkeypatch.setenv("EZSNMP_NETSNMP_INCLUDE_DIR", str(include_dir))
    monkeypatch.setenv("EZSNMP_NETSNMP_LIB_DIR", str(lib_dir))
    monkeypatch.setenv("EZSNMP_NETSNMP_LIBS", "netsnmp_d;advapi32,ws2_32")

    cfg = build_utils.gather_build_configuration()

    assert cfg["libs"] == ["netsnmp_d", "advapi32", "ws2_32"]


def test_gather_build_configuration_windows_supports_dll_imports(tmp_path, monkeypatch):
    include_dir = tmp_path / "include"
    lib_dir = tmp_path / "lib"
    header_path = include_dir / "net-snmp" / "net-snmp-config.h"
    header_path.parent.mkdir(parents=True)
    header_path.write_text('#define PACKAGE_VERSION "5.10.1"\n', encoding="utf-8")
    lib_dir.mkdir()

    monkeypatch.setattr(build_utils, "platform", "win32")
    monkeypatch.setattr(build_utils, "argv", ["setup.py"])
    monkeypatch.setenv("EZSNMP_NETSNMP_INCLUDE_DIR", str(include_dir))
    monkeypatch.setenv("EZSNMP_NETSNMP_LIB_DIR", str(lib_dir))
    monkeypatch.setenv("EZSNMP_NETSNMP_USE_DLL", "1")

    cfg = build_utils.gather_build_configuration()

    assert "/DNETSNMP_USE_DLL" in cfg["compile_args"]


def test_gather_build_configuration_windows_requires_paths(monkeypatch):
    monkeypatch.setattr(build_utils, "platform", "win32")
    monkeypatch.setattr(build_utils, "argv", ["setup.py"])
    monkeypatch.delenv("EZSNMP_NETSNMP_INCLUDE_DIR", raising=False)
    monkeypatch.delenv("EZSNMP_NETSNMP_INCLUDEDIR", raising=False)
    monkeypatch.delenv("NETSNMP_INCLUDE_DIR", raising=False)
    monkeypatch.delenv("NETSNMP_INCLUDEDIR", raising=False)
    monkeypatch.delenv("EZSNMP_NETSNMP_LIB_DIR", raising=False)
    monkeypatch.delenv("EZSNMP_NETSNMP_LIBDIR", raising=False)
    monkeypatch.delenv("NETSNMP_LIB_DIR", raising=False)
    monkeypatch.delenv("NETSNMP_LIBDIR", raising=False)

    with pytest.raises(RuntimeError, match="EZSNMP_NETSNMP_INCLUDE_DIR"):
        build_utils.gather_build_configuration()
