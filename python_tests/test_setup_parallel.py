import os
import threading
import time
from pathlib import Path
from setuptools import Distribution, Extension

import pytest

import build_utils
import setup as ezsnmp_setup


def test_resolve_build_jobs_defaults_to_cpus_minus_one(monkeypatch):
    monkeypatch.delenv("EZSNMP_BUILD_JOBS", raising=False)
    assert build_utils.resolve_build_jobs(cpu_count=8) == 7
    assert build_utils.resolve_build_jobs(cpu_count=4) == 3
    assert build_utils.resolve_build_jobs(cpu_count=1) == 1


def test_resolve_build_jobs_honors_explicit_parallel(monkeypatch):
    monkeypatch.delenv("EZSNMP_BUILD_JOBS", raising=False)
    assert build_utils.resolve_build_jobs(explicit_jobs=True, cpu_count=6) == 5
    assert build_utils.resolve_build_jobs(explicit_jobs=2, cpu_count=6) == 2


def test_resolve_build_jobs_env_override_and_validation(monkeypatch):
    monkeypatch.setenv("EZSNMP_BUILD_JOBS", "4")
    assert build_utils.resolve_build_jobs(explicit_jobs=2, cpu_count=8) == 4

    monkeypatch.setenv("EZSNMP_BUILD_JOBS", "auto")
    assert build_utils.resolve_build_jobs(explicit_jobs=2, cpu_count=6) == 5

    monkeypatch.setenv("EZSNMP_BUILD_JOBS", "0")
    with pytest.raises(ValueError, match="must be >= 1"):
        build_utils.resolve_build_jobs(cpu_count=4)

    monkeypatch.setenv("EZSNMP_BUILD_JOBS", "not-an-int")
    with pytest.raises(ValueError, match="expected a positive integer"):
        build_utils.resolve_build_jobs(cpu_count=4)


def test_is_up_to_date_tracks_timestamps_and_missing_files(tmp_path):
    inp = tmp_path / "input.cpp"
    out = tmp_path / "output.o"

    assert not build_utils.is_up_to_date([], [str(inp)])
    inp.write_text("int x = 1;\n", encoding="utf-8")
    assert not build_utils.is_up_to_date([str(out)], [str(inp)])

    out.write_text("obj", encoding="utf-8")
    now = time.time()
    os.utime(inp, (now - 10, now - 10))
    os.utime(out, (now, now))
    assert build_utils.is_up_to_date([str(out)], [str(inp)])

    os.utime(inp, (now + 5, now + 5))
    assert not build_utils.is_up_to_date([str(out)], [str(inp)])


def test_is_python_independent_source():
    assert build_utils.is_python_independent_source("ezsnmp/src/datatypes.cpp")
    assert build_utils.is_python_independent_source(
        "ezsnmp/src/net-snmp-5.9-final-patched/snmpwalk.cpp"
    )
    assert not build_utils.is_python_independent_source(
        "ezsnmp/src/ezsnmp_sessionbase.cpp"
    )


def test_windows_debug_configuration_adds_fs_flag(tmp_path, monkeypatch):
    include_dir = tmp_path / "include"
    lib_dir = tmp_path / "lib"
    header_path = include_dir / "net-snmp" / "net-snmp-config.h"
    header_path.parent.mkdir(parents=True)
    header_path.write_text('#define PACKAGE_VERSION "5.9.4"\n', encoding="utf-8")
    lib_dir.mkdir()

    monkeypatch.setattr(build_utils, "platform", "win32")
    monkeypatch.setattr(build_utils, "argv", ["setup.py", "--debug"])
    monkeypatch.setenv("EZSNMP_NETSNMP_INCLUDE_DIR", str(include_dir))
    monkeypatch.setenv("EZSNMP_NETSNMP_LIB_DIR", str(lib_dir))

    cfg = build_utils.gather_build_configuration()
    assert "/Zi" in cfg["compile_args"]
    assert "/FS" in cfg["compile_args"]


def test_linux_gather_skips_missing_brew_shells(monkeypatch):
    for variable in (
        "EZSNMP_NETSNMP_CONFIG",
        "EZSNMP_OPENSSL_INCLUDE_DIR",
        "EZSNMP_OPENSSL_LIB_DIR",
        "OPENSSL_INCLUDE_DIR",
        "OPENSSL_LIB_DIR",
    ):
        monkeypatch.delenv(variable, raising=False)
    called_commands = []

    def fake_check_output(command, **kwargs):
        called_commands.append(command)
        if command == "net-snmp-config --version":
            return b"5.9.4\n"
        if command == "net-snmp-config --libs":
            return b"-L/usr/lib/x86_64-linux-gnu -lnetsnmp\n"
        raise AssertionError(f"Unexpected shell probe: {command}")

    monkeypatch.setattr(build_utils, "platform", "linux")
    monkeypatch.setattr(build_utils, "argv", ["setup.py"])
    monkeypatch.setattr(build_utils, "check_output", fake_check_output)
    monkeypatch.setattr(build_utils, "_default_check_output", fake_check_output)
    monkeypatch.setattr(build_utils, "which", lambda binary: None)

    cfg = build_utils.gather_build_configuration()
    assert cfg["system_netsnmp_version"] == "5.9.4"
    assert cfg["homebrew_version"] is None
    assert called_commands == ["net-snmp-config --version", "net-snmp-config --libs"]


class _DummyCompiler:
    compiler_type = "unix"
    compiler_so_cxx = ["g++", "-O3", "-fPIC"]

    def __init__(self, compile_delay=0.0):
        self.initialized = False
        self.init_thread = None
        self.compiled_sources = []
        self.linked_targets = []
        self.lock = threading.Lock()
        self.compile_delay = compile_delay
        self.macros = []
        self.include_dirs = []

    def initialize(self):
        self.initialized = True
        self.init_thread = threading.get_ident()

    def object_filenames(self, source_filenames, strip_dir=False, output_dir=""):
        return [
            os.path.join(output_dir, f"{os.path.splitext(src)[0]}.o")
            for src in source_filenames
        ]

    def detect_language(self, sources):
        return "c++"

    def compile(
        self,
        sources,
        output_dir=None,
        macros=None,
        include_dirs=None,
        debug=False,
        extra_postargs=None,
        depends=None,
    ):
        if self.compile_delay:
            time.sleep(self.compile_delay)
        objs = self.object_filenames(sources, output_dir=output_dir or "")
        for src, obj in zip(sources, objs):
            os.makedirs(os.path.dirname(obj), exist_ok=True)
            Path(obj).write_text(f"compiled:{src}", encoding="utf-8")
            with self.lock:
                self.compiled_sources.append((src, list(extra_postargs or [])))
        return objs

    def link_shared_object(self, objects, output_filename, **kwargs):
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        Path(output_filename).write_text(",".join(objects), encoding="utf-8")
        self.linked_targets.append((output_filename, list(objects)))


def test_swig_build_ext_deduplicates_sources_and_initializes_msvc_on_main_thread(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("EZSNMP_BUILD_JOBS", "3")
    monkeypatch.delenv("EZSNMP_OBJECT_CACHE_DIR", raising=False)

    inc_dir = tmp_path / "ezsnmp" / "include"
    src_dir = tmp_path / "ezsnmp" / "src"
    inc_dir.mkdir(parents=True)
    src_dir.mkdir(parents=True)
    (inc_dir / "datatypes.h").write_text("#pragma once\n", encoding="utf-8")

    files = {
        "ezsnmp/src/datatypes.cpp": "int dt = 1;\n",
        "ezsnmp/src/helpers.cpp": "int hp = 2;\n",
        "ezsnmp/src/ezsnmp_datatypes.cpp": "int swig_dt = 3;\n" * 20,
        "ezsnmp/src/ezsnmp_sessionbase.cpp": "int swig_sb = 4;\n" * 100,
    }
    now = time.time() - 5
    for rel, content in files.items():
        p = tmp_path / rel
        p.write_text(content, encoding="utf-8")
        os.utime(p, (now, now))
    os.utime(inc_dir / "datatypes.h", (now, now))

    exts = [
        Extension(
            "ezsnmp._datatypes",
            sources=["ezsnmp/src/ezsnmp_datatypes.cpp", "ezsnmp/src/datatypes.cpp"],
            include_dirs=["ezsnmp/include/"],
            extra_compile_args=["/Zi"],
        ),
        Extension(
            "ezsnmp._sessionbase",
            sources=[
                "ezsnmp/src/ezsnmp_sessionbase.cpp",
                "ezsnmp/src/datatypes.cpp",
                "ezsnmp/src/helpers.cpp",
            ],
            include_dirs=["ezsnmp/include/"],
            extra_compile_args=["/Zi"],
        ),
    ]

    dist = Distribution({"name": "ezsnmp", "ext_modules": exts})
    cmd = ezsnmp_setup.SwigBuildExt(dist)
    cmd.initialize_options()
    cmd.build_temp = str(tmp_path / "build" / "temp")
    cmd.build_lib = str(tmp_path / "build" / "lib")
    cmd.finalize_options()

    compiler = _DummyCompiler(compile_delay=0.01)
    compiler.compiler_type = "msvc"
    cmd.compiler = compiler

    main_tid = threading.get_ident()
    cmd.build_extensions()

    assert compiler.initialized is True
    assert compiler.init_thread == main_tid
    # 5 total source entries across 2 extensions -> deduplicated to 4 unique compiles!
    assert len(compiler.compiled_sources) == 4
    assert {src for src, _ in compiler.compiled_sources} == set(files.keys())
    # MSVC with /Zi automatically receives /FS to prevent PDB locking across threads
    for _, extra_args in compiler.compiled_sources:
        assert "/FS" in extra_args
    assert len(compiler.linked_targets) == 2

    # Incremental second run with unchanged files skips compilation and linking completely
    compiler.compiled_sources.clear()
    compiler.linked_targets.clear()
    cmd.build_extensions()
    assert compiler.compiled_sources == []
    assert compiler.linked_targets == []


def test_swig_build_ext_reuses_python_independent_object_cache(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cache_dir = tmp_path / "obj_cache"
    monkeypatch.setenv("EZSNMP_BUILD_JOBS", "2")
    monkeypatch.setenv("EZSNMP_OBJECT_CACHE_DIR", str(cache_dir))

    inc_dir = tmp_path / "ezsnmp" / "include"
    src_dir = tmp_path / "ezsnmp" / "src"
    inc_dir.mkdir(parents=True)
    src_dir.mkdir(parents=True)
    (inc_dir / "datatypes.h").write_text("#pragma once\n", encoding="utf-8")
    (src_dir / "datatypes.cpp").write_text("int dt = 1;\n", encoding="utf-8")
    (src_dir / "ezsnmp_datatypes.cpp").write_text("int swig = 2;\n", encoding="utf-8")

    def run_for_abi(abi_tag):
        ext = Extension(
            "ezsnmp._datatypes",
            sources=["ezsnmp/src/ezsnmp_datatypes.cpp", "ezsnmp/src/datatypes.cpp"],
            include_dirs=["ezsnmp/include/"],
        )
        dist = Distribution({"name": "ezsnmp", "ext_modules": [ext]})
        cmd = ezsnmp_setup.SwigBuildExt(dist)
        cmd.initialize_options()
        cmd.build_temp = str(tmp_path / "build" / f"temp.{abi_tag}")
        cmd.build_lib = str(tmp_path / "build" / f"lib.{abi_tag}")
        cmd.plat_name = "linux-x86_64"
        cmd.finalize_options()
        compiler = _DummyCompiler()
        cmd.compiler = compiler
        cmd.build_extensions()
        return [src for src, _ in compiler.compiled_sources]

    first_compiled = run_for_abi("cpython-311")
    assert set(first_compiled) == {
        "ezsnmp/src/datatypes.cpp",
        "ezsnmp/src/ezsnmp_datatypes.cpp",
    }

    # Second Python ABI in a fresh build_temp reuses datatypes.o from cache and only compiles SWIG wrapper!
    second_compiled = run_for_abi("cpython-312")
    assert second_compiled == ["ezsnmp/src/ezsnmp_datatypes.cpp"]


def test_is_netsnmp_5_10_or_newer():
    assert not build_utils.is_netsnmp_5_10_or_newer("")
    assert not build_utils.is_netsnmp_5_10_or_newer("5.8")
    assert not build_utils.is_netsnmp_5_10_or_newer("5.9.4.pre2")
    assert not build_utils.is_netsnmp_5_10_or_newer("5.9.5.2")
    assert build_utils.is_netsnmp_5_10_or_newer("5.10.rc1")
    assert build_utils.is_netsnmp_5_10_or_newer("5.10")
    assert build_utils.is_netsnmp_5_10_or_newer("5.11.0")


def test_ensure_netsnmp_5_10_configuration_upgrades_older_system_netsnmp(
    tmp_path, monkeypatch
):
    prefix = tmp_path / "third_party" / "net-snmp-install"
    bin_dir = prefix / "bin"
    inc_dir = prefix / "include"
    lib_dir = prefix / "lib"
    bin_dir.mkdir(parents=True)
    inc_dir.mkdir(parents=True)
    lib_dir.mkdir(parents=True)
    cfg_bin = bin_dir / "net-snmp-config"
    cfg_bin.write_text("#!/bin/sh\n", encoding="utf-8")
    cfg_bin.chmod(0o755)

    monkeypatch.setattr(build_utils, "platform", "linux")
    monkeypatch.setattr(build_utils, "argv", ["setup.py"])
    monkeypatch.delenv("EZSNMP_AUTO_BUILD_NETSNMP", raising=False)
    monkeypatch.setattr(
        build_utils,
        "ensure_vendored_netsnmp_install",
        lambda repo_root=None: str(cfg_bin),
    )

    def fake_check_output(command, **kwargs):
        if command == f"{cfg_bin} --version":
            return b"5.10.rc1\n"
        if command == f"{cfg_bin} --libs":
            return f"-L{lib_dir} -lnetsnmp -lcrypto\n".encode()
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(build_utils, "check_output", fake_check_output)

    old_cfg = {
        "in_tree": False,
        "compile_args": ["-std=c++17"],
        "link_args": [],
        "libs": ["netsnmp"],
        "libdirs": ["/usr/lib"],
        "incdirs": ["ezsnmp/include/"],
        "system_netsnmp_version": "5.9.4.pre2",
        "homebrew_version": None,
        "homebrew_netsnmp_version": None,
        "homebrew_openssl_version": None,
    }

    upgraded = build_utils.ensure_netsnmp_5_10_configuration(
        old_cfg, repo_root=tmp_path
    )
    assert upgraded["system_netsnmp_version"] == "5.10.rc1"
    assert str(inc_dir) in upgraded["incdirs"]
    assert str(lib_dir) in upgraded["libdirs"]
    assert f"-Wl,-rpath,{lib_dir}" in upgraded["link_args"]


def test_prepare_netsnmp_source_reuses_existing_valid_tree(tmp_path, monkeypatch):
    import sys

    tools_dir = str(Path(build_utils.__file__).resolve().parent / "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import prepare_netsnmp_source

    vendored = tmp_path / "net-snmp"
    (vendored / "include" / "net-snmp").mkdir(parents=True)
    (vendored / "configure").write_text("#!/bin/sh\n", encoding="utf-8")

    monkeypatch.setenv("EZSNMP_NETSNMP_SOURCE_DIR", str(vendored))
    resolved = prepare_netsnmp_source.ensure_netsnmp_source()
    assert resolved == vendored.resolve()

    assert prepare_netsnmp_source._resolve_safe_tag("v5.10.rc1")[0] == "v5.10.rc1"
    assert prepare_netsnmp_source._resolve_safe_tag("5.10.rc1")[0] == "v5.10.rc1"
    with pytest.raises(ValueError, match="Unsupported Net-SNMP tag"):
        prepare_netsnmp_source._resolve_safe_tag("--upload-pack=evil")
    with pytest.raises(ValueError, match="must remain within repository root"):
        prepare_netsnmp_source._resolve_safe_dest(Path("/tmp/outside-repo"))
