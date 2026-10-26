import build_utils
from subprocess import CalledProcessError

import pytest


@pytest.mark.parametrize(
    ("product_version", "expected_target"),
    [
        ("10.15.7", "10.15"),
        ("11.7.10", "11.0"),
        ("15.6.1", "15.0"),
        ("26.0", "26.0"),
    ],
)
def test_resolve_macos_deployment_target(product_version, expected_target):
    assert (
        build_utils.resolve_macos_deployment_target(product_version) == expected_target
    )


def test_resolve_macos_deployment_target_rejects_invalid_values():
    with pytest.raises(ValueError, match="Unsupported macOS version string"):
        build_utils.resolve_macos_deployment_target("Tahoe")


@pytest.fixture
def homebrew_outputs(monkeypatch):
    for variable in (
        "EZSNMP_NETSNMP_CONFIG",
        "EZSNMP_OPENSSL_INCLUDE_DIR",
        "EZSNMP_OPENSSL_LIB_DIR",
        "OPENSSL_INCLUDE_DIR",
        "OPENSSL_LIB_DIR",
    ):
        monkeypatch.delenv(variable, raising=False)
    outputs = {
        "brew --version": "Homebrew 7.0.9\n",
        "brew list net-snmp": (
            "/opt/homebrew/Cellar/net-snmp/5.9.5.2_2/bin/net-snmp-config\n"
            "/opt/homebrew/Cellar/net-snmp/5.9.5.2_2/include/net-snmp/net-snmp-config.h\n"
            "/opt/homebrew/Cellar/net-snmp/5.9.5.2_2/lib/libnetsnmp.dylib\n"
        ),
        "brew info net-snmp": "Required: openssl@4 ✔, pcre2 ✔\n",
        "brew --prefix openssl@4": "/opt/homebrew/opt/openssl@4\n",
        "net-snmp-config --version": "5.9.5.2\n",
        "net-snmp-config --libs": (
            "-L/custom/lib -L/opt/homebrew/Cellar/net-snmp/5.9.5.2_2/lib "
            "-lnetsnmp -lcrypto -flat_namespace -framework CoreFoundation"
        ),
    }

    def check_output(command, **kwargs):
        result = outputs[command]
        if isinstance(result, Exception):
            raise result
        return result.encode()

    monkeypatch.setattr(build_utils, "platform", "darwin")
    monkeypatch.setattr(build_utils, "argv", ["setup.py"])
    monkeypatch.setattr(build_utils, "check_output", check_output)
    monkeypatch.setattr(build_utils.os.path, "isdir", lambda path: True)
    monkeypatch.setattr(build_utils.os.path, "isfile", lambda path: False)
    monkeypatch.setattr(build_utils, "is_macports_installed", lambda: "")
    monkeypatch.setattr(build_utils, "is_net_snmp_installed_macports", lambda: "")
    return outputs


@pytest.mark.parametrize("prefix", ["/opt/homebrew", "/usr/local", "/custom/homebrew"])
@pytest.mark.parametrize("version", ["5.9.4", "5.9.5.2_2"])
@pytest.mark.parametrize("openssl", ["openssl@3", "openssl@4"])
def test_homebrew_openssl_discovery(homebrew_outputs, prefix, version, openssl):
    netsnmp_prefix = f"{prefix}/Cellar/net-snmp/{version}"
    openssl_prefix = f"{prefix}/opt/{openssl}"
    homebrew_outputs["brew list net-snmp"] = (
        f"{netsnmp_prefix}/bin/net-snmp-config\n"
        f"{netsnmp_prefix}/include/net-snmp/net-snmp-config.h\n"
        f"{netsnmp_prefix}/lib/libnetsnmp.dylib\n"
    )
    homebrew_outputs["brew info net-snmp"] = f"Required: {openssl} ✔, pcre2 ✔\n"
    homebrew_outputs[f"brew --prefix {openssl}"] = openssl_prefix + "\n"

    assert build_utils.get_homebrew_net_snmp_info() == (
        "7.0.9",
        version.split("_")[0],
        openssl,
        [f"{netsnmp_prefix}/lib", f"{openssl_prefix}/lib"],
        [f"{netsnmp_prefix}/include", f"{openssl_prefix}/include"],
    )


def test_homebrew_openssl_prefix_fallback(homebrew_outputs):
    homebrew_outputs["brew --prefix openssl@4"] = CalledProcessError(1, "brew")
    homebrew_outputs["brew info openssl@4"] = (
        "openssl@4: stable\n/opt/homebrew/Cellar/openssl@4/4.0.0 (files)\n"
    )

    info = build_utils.get_homebrew_net_snmp_info()

    assert info[3][-1] == "/opt/homebrew/Cellar/openssl@4/4.0.0/lib"
    assert info[4][-1] == "/opt/homebrew/Cellar/openssl@4/4.0.0/include"


@pytest.mark.parametrize("command", ["brew list net-snmp", "brew info net-snmp"])
def test_homebrew_discovery_failure_preserves_netsnmp_config(homebrew_outputs, command):
    homebrew_outputs[command] = CalledProcessError(1, command)

    cfg = build_utils.gather_build_configuration()

    assert cfg["incdirs"] == [
        "ezsnmp/include/",
        "/opt/homebrew/Cellar/net-snmp/5.9.5.2_2/include",
    ]
    assert cfg["libdirs"] == [
        "/custom/lib",
        "/opt/homebrew/Cellar/net-snmp/5.9.5.2_2/lib",
    ]
    assert cfg["libs"] == ["netsnmp", "crypto"]
    assert cfg["system_netsnmp_version"] == "5.9.5.2"


def test_gather_macos_configuration_preserves_flags_and_adds_openssl(homebrew_outputs):
    cfg = build_utils.gather_build_configuration()

    assert cfg["incdirs"] == [
        "ezsnmp/include/",
        "/opt/homebrew/Cellar/net-snmp/5.9.5.2_2/include",
        "/opt/homebrew/opt/openssl@4/include",
    ]
    assert cfg["libdirs"][0] == "/custom/lib"
    assert "/opt/homebrew/opt/openssl@4/lib" in cfg["libdirs"]
    assert cfg["libs"] == ["netsnmp", "crypto"]
    assert cfg["compile_args"] == ["-std=c++17"]
    assert cfg["link_args"] == ["-flat_namespace", "-framework", "CoreFoundation"]
    assert cfg["system_netsnmp_version"] == "5.9.5.2"


def test_gather_macos_configuration_uses_explicit_netsnmp_config(
    homebrew_outputs, monkeypatch
):
    configured_path = "/opt/homebrew/Cellar/ezsnmp/2.5.0/bin/net-snmp-config"
    homebrew_outputs[f"{configured_path} --version"] = "5.10.pre2\n"
    homebrew_outputs[f"{configured_path} --libs"] = (
        "-L/opt/homebrew/Cellar/ezsnmp/2.5.0/lib -lnetsnmp -lcrypto"
    )
    homebrew_outputs["brew list net-snmp"] = CalledProcessError(1, "brew list net-snmp")
    monkeypatch.setenv("EZSNMP_NETSNMP_CONFIG", configured_path)
    monkeypatch.setenv("EZSNMP_OPENSSL_INCLUDE_DIR", "/custom/openssl/include")
    monkeypatch.setenv("EZSNMP_OPENSSL_LIB_DIR", "/custom/openssl/lib")

    cfg = build_utils.gather_build_configuration()

    assert cfg["incdirs"] == ["ezsnmp/include/", "/custom/openssl/include"]
    assert cfg["libdirs"] == [
        "/custom/openssl/lib",
        "/opt/homebrew/Cellar/ezsnmp/2.5.0/lib",
    ]
    assert cfg["libs"] == ["netsnmp", "crypto"]
    assert cfg["system_netsnmp_version"] == "5.10.pre2"
    assert cfg["homebrew_netsnmp_version"] is None


@pytest.mark.parametrize("macports", [False, True])
def test_gather_macos_configuration_without_homebrew(
    homebrew_outputs, monkeypatch, macports
):
    homebrew_outputs["brew --version"] = CalledProcessError(127, "brew")
    homebrew_outputs["net-snmp-config --libs"] = "-L/opt/local/lib -lnetsnmp -lcrypto"
    if macports:
        monkeypatch.setattr(build_utils, "is_macports_installed", lambda: "2.10.0")
        monkeypatch.setattr(
            build_utils, "is_net_snmp_installed_macports", lambda: "5.9.4"
        )

    cfg = build_utils.gather_build_configuration()

    assert cfg["incdirs"] == (
        ["ezsnmp/include/", "/opt/local/include"] if macports else ["ezsnmp/include/"]
    )
    assert cfg["libdirs"] == ["/opt/local/lib"]
    assert cfg["system_netsnmp_version"] == ("5.9.4" if macports else "5.9.5.2")


def test_gather_macos_in_tree_configuration_bypasses_homebrew(
    homebrew_outputs, monkeypatch
):
    monkeypatch.setattr(build_utils, "argv", ["setup.py", "--basedir=/custom"])
    homebrew_outputs.update(
        {
            "/custom/net-snmp-config --libs": "-lnetsnmp -lcrypto",
            "/custom/net-snmp-config --build-lib-dirs /custom": "-L/custom/lib",
            "/custom/net-snmp-config --build-includes /custom": "-I/custom/include",
            "brew --version": AssertionError("In-tree builds must not query Homebrew"),
        }
    )

    cfg = build_utils.gather_build_configuration()

    assert cfg["incdirs"] == ["/custom/include"]
    assert cfg["libdirs"] == ["/custom/lib"]


@pytest.mark.parametrize(
    ("output", "expected"),
    [
        ("Version: 2.10.0\n", "2.10.0"),
        ("Version: 2.12.7\n", "2.12.7"),
        ("Version: 3.0.0.1\n", "3.0.0.1"),
        ("invalid output", ""),
    ],
)
def test_is_macports_installed(monkeypatch, output, expected):
    monkeypatch.setattr(
        build_utils, "check_output", lambda *args, **kwargs: output.encode()
    )
    assert build_utils.is_macports_installed() == expected


def test_is_macports_installed_handles_error(monkeypatch):
    def raise_error(*args, **kwargs):
        raise CalledProcessError(1, "port version")

    monkeypatch.setattr(build_utils, "check_output", raise_error)
    assert build_utils.is_macports_installed() == ""


@pytest.mark.parametrize(
    ("output", "expected"),
    [
        ("  net-snmp @5.9.4 (active)\n", "5.9.4"),
        ("  net-snmp @5.9.4_1 (active)\n", "5.9.4_1"),
        (
            "The following ports are currently installed:\n"
            "  net-snmp @5.9.5.2_0+perl5_34+ssl (active)\n",
            "5.9.5.2_0+perl5_34+ssl",
        ),
        ("  net-snmp @5.10.0_1+ssl (active)\n", "5.10.0_1+ssl"),
        ("  net-snmp @5.9.4\n", ""),  # not active
        ("None of the specified ports are installed.\n", ""),
    ],
)
def test_is_net_snmp_installed_macports(monkeypatch, output, expected):
    monkeypatch.setattr(
        build_utils, "check_output", lambda *args, **kwargs: output.encode()
    )
    assert build_utils.is_net_snmp_installed_macports() == expected


def test_is_net_snmp_installed_macports_handles_error(monkeypatch):
    def raise_error(*args, **kwargs):
        raise CalledProcessError(1, "port installed net-snmp")

    monkeypatch.setattr(build_utils, "check_output", raise_error)
    assert build_utils.is_net_snmp_installed_macports() == ""


@pytest.mark.parametrize("macports_ver", ["5.9.4", "5.9.5.2_0+perl5_34+ssl"])
def test_gather_macos_configuration_with_macports_versions(
    homebrew_outputs, monkeypatch, macports_ver
):
    homebrew_outputs["brew --version"] = CalledProcessError(127, "brew")
    homebrew_outputs["net-snmp-config --libs"] = "-L/opt/local/lib -lnetsnmp -lcrypto"
    monkeypatch.setattr(build_utils, "is_macports_installed", lambda: "2.12.7")
    monkeypatch.setattr(
        build_utils, "is_net_snmp_installed_macports", lambda: macports_ver
    )

    cfg = build_utils.gather_build_configuration()

    assert cfg["incdirs"] == ["ezsnmp/include/", "/opt/local/include"]
    assert cfg["libdirs"] == ["/opt/local/lib"]
    assert cfg["system_netsnmp_version"] == macports_ver
