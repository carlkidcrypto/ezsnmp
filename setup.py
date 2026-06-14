#!/usr/bin/env python3

"""Build script for ezsnmp.

This script configures and builds the ezsnmp package, a blazingly fast Python SNMP library
based on Net-SNMP. It performs the following tasks:

1. Detects the system's Net-SNMP installation (system, Homebrew, or MacPorts)
2. Runs SWIG to generate C++ wrapper code from interface files (.i -> .cpp)
3. Compiles four C++ extension modules (_datatypes, _exceptionsbase, _netsnmpbase, _sessionbase)
4. Selects version-specific Net-SNMP source files based on detected version (5.7, 5.8, 5.9, or 5.10)

Command-line options:
    --debug         Enable debug compilation flags (-Wall -O0 -g)
    --basedir=PATH  Use in-tree Net-SNMP build from specified directory

Requirements:
    - Net-SNMP library and headers (via system package manager, Homebrew, or MacPorts)
    - SWIG 4.x for generating Python bindings
    - C++17 compatible compiler
    - setuptools and wheel
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from subprocess import run, CalledProcessError
from sys import path, platform
from setuptools import setup, Extension
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.build_ext import build_ext
import time

setup_dir = str(Path(globals().get("__file__", "setup.py")).resolve().parent)
if setup_dir not in path:
    path.insert(0, setup_dir)
from build_utils import gather_build_configuration


swig_targets = [
    ("ezsnmp/interface/datatypes.i", "ezsnmp/src/ezsnmp_datatypes.cpp"),
    ("ezsnmp/interface/exceptionsbase.i", "ezsnmp/src/ezsnmp_exceptionsbase.cpp"),
    ("ezsnmp/interface/netsnmpbase.i", "ezsnmp/src/ezsnmp_netsnmpbase.cpp"),
    ("ezsnmp/interface/sessionbase.i", "ezsnmp/src/ezsnmp_sessionbase.cpp"),
]


class SwigBuildExt(build_ext):
    """Custom build_ext: run SWIG on interface files before compiling extensions."""

    def _run_swig_command(self, swig_command, interface_file, wrapper_file):
        start_time = time.perf_counter()
        print(f"\t[PROFILE] SWIG start for {interface_file} at {start_time:.6f}")
        command = swig_command + ["-o", wrapper_file, interface_file]
        try:
            run(command, check=True)
            end_time = time.perf_counter()
            delta = end_time - start_time
            print(
                f"\t[PROFILE] SWIG end for {interface_file} at {end_time:.6f} (delta: {delta:.6f}s)"
            )
            return True, interface_file, None
        except (CalledProcessError, FileNotFoundError):
            end_time = time.perf_counter()
            delta = end_time - start_time
            print(
                f"\t[PROFILE] SWIG failed for {interface_file} at {end_time:.6f} (delta: {delta:.6f}s)"
            )
            return False, interface_file, f"SWIG failed for {interface_file}"

    def run(self):
        print("------- Running SWIG to generate wrapper code -------")
        swig_command = [
            "swig",
            "-c++",  # Force C++ code generation
            "-python",  # Generate Python bindings
            "-builtin",  # Use native Python data types
            "-threads",  # Add thread support
            "-doxygen",  # Convert Doxygen comments to pydoc
            "-std=c++17",  # Specify C++17 standard
            "-outdir",  # Specify output directory for the .py module
            "ezsnmp/.",
        ]

        for inc_dir in self.extensions[0].include_dirs:
            swig_command.append(f"-I{inc_dir}")
        swig_command.append("-Iezsnmp/interface")

        max_workers = min(len(swig_targets), os.cpu_count() or 1)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    self._run_swig_command, swig_command, interface_file, wrapper_file
                )
                for interface_file, wrapper_file in swig_targets
            ]
            for future in as_completed(futures):
                success, interface_file, error_msg = future.result()
                if not success:
                    raise RuntimeError(
                        f"{error_msg}. Ensure SWIG is installed and on PATH."
                    )
        print("------- SWIG processing complete -------")
        super().run()


class BuildEverythingWithSwig(_build_py):
    """Run build_ext first so SWIG outputs .py wrappers before packaging."""

    def run(self):
        self.run_command("build_ext")
        super().run()


def resolve_snmp_source_path(version_str: str) -> str:
    if version_str.startswith("5.6"):
        if platform == "darwin":
            raise RuntimeError(
                f"Net-SNMP version {version_str} is no longer supported. "
                "On macOS, the system-provided Net-SNMP (5.6.x) is not supported. "
                "Please install a supported version via Homebrew "
                "(`brew install net-snmp`) or MacPorts "
                "(`sudo port install net-snmp`)."
            )
        raise RuntimeError(
            f"Net-SNMP version {version_str} is no longer supported. "
            "Please upgrade to Net-SNMP 5.7 or later."
        )
    if version_str.startswith("5.7"):
        return "ezsnmp/src/net-snmp-5.7-final-patched"
    if version_str.startswith("5.8"):
        return "ezsnmp/src/net-snmp-5.8-final-patched"
    if version_str.startswith("5.9"):
        return "ezsnmp/src/net-snmp-5.9-final-patched"
    if version_str.startswith("5.10"):
        return "ezsnmp/src/net-snmp-5.10-final-patched"
    raise RuntimeError(f"Unsupported net-snmp version: {version_str}")


def build_extensions(cfg: dict):
    version_str = cfg["system_netsnmp_version"]
    snmp_source_path = resolve_snmp_source_path(version_str)
    netsnmp_versioned_sources = [
        f"{snmp_source_path}/snmpbulkget.cpp",
        f"{snmp_source_path}/snmpgetnext.cpp",
        f"{snmp_source_path}/snmpbulkwalk.cpp",
        f"{snmp_source_path}/snmpget.cpp",
        f"{snmp_source_path}/snmpwalk.cpp",
        f"{snmp_source_path}/snmpset.cpp",
        f"{snmp_source_path}/snmptrap.cpp",
    ]
    netsnmpbase_sources = [
        "ezsnmp/src/ezsnmp_netsnmpbase.cpp",  # Generated by SWIG
        "ezsnmp/src/exceptionsbase.cpp",
        "ezsnmp/src/datatypes.cpp",
        "ezsnmp/src/helpers.cpp",
        "ezsnmp/src/thread_safety.cpp",
    ] + netsnmp_versioned_sources
    sessionbase_sources = [
        "ezsnmp/src/ezsnmp_sessionbase.cpp",  # Generated by SWIG
        "ezsnmp/src/exceptionsbase.cpp",
        "ezsnmp/src/datatypes.cpp",
        "ezsnmp/src/sessionbase.cpp",
        "ezsnmp/src/helpers.cpp",
        "ezsnmp/src/thread_safety.cpp",
    ] + netsnmp_versioned_sources
    compile_args = cfg["compile_args"]
    link_args = cfg["link_args"]
    libdirs = cfg["libdirs"]
    incdirs = cfg["incdirs"]
    libs = cfg["libs"]
    return [
        Extension(
            name="ezsnmp/_datatypes",
            sources=[
                "ezsnmp/src/ezsnmp_datatypes.cpp",  # Generated by SWIG
                "ezsnmp/src/datatypes.cpp",
            ],
            library_dirs=libdirs,
            include_dirs=incdirs,
            libraries=libs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        ),
        Extension(
            name="ezsnmp/_exceptionsbase",
            sources=[
                "ezsnmp/src/ezsnmp_exceptionsbase.cpp",  # Generated by SWIG
                "ezsnmp/src/exceptionsbase.cpp",
            ],
            library_dirs=libdirs,
            include_dirs=incdirs,
            libraries=libs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        ),
        Extension(
            name="ezsnmp/_netsnmpbase",
            sources=netsnmpbase_sources,
            library_dirs=libdirs,
            include_dirs=incdirs,
            libraries=libs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        ),
        Extension(
            name="ezsnmp/_sessionbase",
            sources=sessionbase_sources,
            library_dirs=libdirs,
            include_dirs=incdirs,
            libraries=libs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        ),
    ]


def debug_print(cfg: dict):
    for k, v in cfg.items():
        display_value = v if v else "None"
        print(f"{k}: {display_value}")


def main():
    cfg = gather_build_configuration()
    debug_print(cfg)
    extensions = build_extensions(cfg)
    print(
        f"Using SNMP sources from: {resolve_snmp_source_path(cfg['system_netsnmp_version'])}"
    )
    setup(
        ext_modules=extensions,
        cmdclass={"build_ext": SwigBuildExt, "build_py": BuildEverythingWithSwig},
    )


if __name__ == "__main__":
    main()
