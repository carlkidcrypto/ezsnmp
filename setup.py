#!/usr/bin/env python3

"""Build script for ezsnmp.

This script configures and builds the ezsnmp package, a blazingly fast Python SNMP library
based on Net-SNMP. It performs the following tasks:

1. Detects the system's Net-SNMP installation (system, Homebrew, or MacPorts)
2. Runs SWIG to generate C++ wrapper code from interface files (.i -> .cpp)
3. Compiles four C++ extension modules (_datatypes, _exceptionsbase, _netsnmpbase, _sessionbase)
4. Selects version-specific Net-SNMP source files based on detected version (5.6, 5.7, 5.8, or 5.9)

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
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from re import search
from shlex import split as s_split
from subprocess import CalledProcessError, check_output, run
from sys import argv, platform

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py as _build_py


def is_macports_installed():
    """
    Checks if MacPorts is installed on the system.

    Returns:
      str: The MacPorts version if installed, "" otherwise.
    """
    try:
        version_output = check_output("port version", shell=True).decode()
        match = search(r"Version:\s+(\d+\.\d+\.\d+)", version_output)
        if match:
            return match.group(1)
        else:
            return ""
    except CalledProcessError:
        return ""


def is_net_snmp_installed_macports():
    """
    Checks if any version of net-snmp is installed via MacPorts.

    Returns:
      str: The net-snmp version if installed, "" otherwise.
    """
    try:
        macports_output = check_output("port installed net-snmp", shell=True).decode()
        pattern = r"net-snmp @(\d+\.\d+\.\d+[_+a-zA-Z0-9]*) \(active\)"
        match = search(pattern, macports_output)
        if match:
            return match.group(1)
        else:
            return ""
    except CalledProcessError:
        return ""


def get_homebrew_info():
    """
    Checks if Homebrew is installed and retrieves its version.

    Returns:
      str: Homebrew version or None if Homebrew is not installed.
    """
    try:
        homebrew_version_output = check_output("brew --version", shell=True).decode()
        match = search(r"Homebrew (\d+\.\d+\.\d+)", homebrew_version_output)
        if match:
            return match.group(1)
        else:
            return None
    except CalledProcessError:
        return None


def get_homebrew_net_snmp_info():
    """
    Retrieves net-snmp and its OpenSSL dependency information from Homebrew.

    Returns:
      tuple or None: A 5-tuple (homebrew_version, net_snmp_version, openssl_version, libdirs, incdirs)
                     if net-snmp is installed via Homebrew, None otherwise (including when Homebrew
                     is not installed).
    """
    homebrew_version = get_homebrew_info()
    if not homebrew_version:
        return None

    try:
        brew_output = check_output("brew list net-snmp", shell=True).decode()
        lines = brew_output.splitlines()

        if not lines:
            return None

        # Extract net-snmp version (supports both /opt/homebrew and /usr/local paths)
        pattern = r"/(?:opt/homebrew|usr/local|home/linuxbrew/\.linuxbrew)/Cellar/net-snmp/(\d+\.\d+(?:\.\d+)*)/"
        match = search(pattern, lines[0])
        if not match:
            return None
        net_snmp_version = match.group(1)

        # Get include directory
        include_dir = next((l for l in lines if "include/net-snmp" in l), None)
        if not include_dir:
            return None
        # Use os.path.dirname twice to get the parent include directory
        # e.g., /path/to/formula/include/net-snmp/file.h -> /path/to/formula/include
        incdirs = [os.path.dirname(os.path.dirname(include_dir))]

        # Get library directory
        libdirs = []
        lib_ext = "dylib" if platform == "darwin" else "so"
        lib_file_name = f"libnetsnmp.{lib_ext}"
        lib_file_path = next((l for l in lines if f"lib/{lib_file_name}" in l), None)
        if lib_file_path:
            libdirs.append(os.path.dirname(lib_file_path))

        # Get OpenSSL dependency information
        # Use `brew deps` to find the openssl formula name (e.g., openssl@3)
        # and `brew --prefix` to resolve its install path. These are stable
        # CLI interfaces that work across Homebrew versions and platforms.
        deps_output = check_output("brew deps net-snmp", shell=True).decode()
        openssl_version = next(
            (
                line.strip()
                for line in deps_output.splitlines()
                if line.strip().startswith("openssl@")
            ),
            None,
        )
        if not openssl_version:
            return None

        openssl_path = (
            check_output(f"brew --prefix {openssl_version}", shell=True)
            .decode()
            .strip()
        )

        if openssl_path and os.path.isdir(openssl_path):
            libdirs.append(openssl_path + "/lib")
            incdirs.append(openssl_path + "/include")
        else:
            return None

        return homebrew_version, net_snmp_version, openssl_version, libdirs, incdirs

    except (CalledProcessError, IndexError, ValueError):
        return None


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


# Determine if a base directory has been provided with the --basedir option
def gather_build_configuration():
    basedir = None
    in_tree = False
    compile_args = ["-std=c++17"]
    link_args = []
    libs = []
    libdirs = []
    incdirs = []

    for arg in argv:
        if arg.startswith("--debug"):
            compile_args.extend(["-Wall", "-O0", "-g"])
        elif arg.startswith("--basedir="):
            basedir = arg.split("=", 1)[1]
            in_tree = True

    system_netsnmp_version = check_output(
        "net-snmp-config --version", shell=True
    ).decode()

    homebrew_version = None
    homebrew_netsnmp_version = None
    homebrew_openssl_version = None
    macports_version = None
    macports_netsnmp_version = None

    if in_tree:
        base_cmd = f"{basedir}/net-snmp-config {{}}"
        netsnmp_libs = check_output(base_cmd.format("--libs"), shell=True).decode()
        libdirs_raw = check_output(
            base_cmd.format(f"--build-lib-dirs {basedir}"), shell=True
        ).decode()
        incdirs_raw = check_output(
            base_cmd.format(f"--build-includes {basedir}"), shell=True
        ).decode()
        libs = [flag[2:] for flag in s_split(netsnmp_libs) if flag.startswith("-l")]
        libdirs = [flag[2:] for flag in s_split(libdirs_raw) if flag.startswith("-L")]
        incdirs = [flag[2:] for flag in s_split(incdirs_raw) if flag.startswith("-I")]
    else:
        netsnmp_libs = check_output("net-snmp-config --libs", shell=True).decode()
        pass_next = False
        for flag in s_split(netsnmp_libs):
            if pass_next:
                link_args.append(flag)
                pass_next = False
            elif flag in ("-framework",):
                link_args.append(flag)
                pass_next = True
            elif flag == "-flat_namespace":
                link_args.append(flag)
        libs = [flag[2:] for flag in s_split(netsnmp_libs) if flag.startswith("-l")]
        libdirs = [flag[2:] for flag in s_split(netsnmp_libs) if flag.startswith("-L")]
        incdirs = ["ezsnmp/include/"]

        homebrew_info = get_homebrew_net_snmp_info()
        if homebrew_info:
            (
                homebrew_version,
                homebrew_netsnmp_version,
                homebrew_openssl_version,
                temp_libdirs,
                temp_incdirs,
            ) = homebrew_info
            libdirs.extend(temp_libdirs)
            incdirs.extend(temp_incdirs)
        else:
            homebrew_version = get_homebrew_info()
            netsnmp_incdir = None
            for directory in libdirs:
                if "net-snmp" in directory:
                    netsnmp_incdir = directory.replace("lib", "include")
                    incdirs.append(netsnmp_incdir)
                    break
                elif "x86_64-linux-gnu" in directory:
                    netsnmp_incdir = "/usr/include/net-snmp"
                    incdirs.append(netsnmp_incdir)
                    break
        macports_version = is_macports_installed()
        macports_netsnmp_version = is_net_snmp_installed_macports()
        if macports_version and macports_netsnmp_version:
            for directory in libdirs:
                if "/opt/local/lib" in directory:
                    netsnmp_incdir = directory.replace("lib", "include")
                    incdirs.append(netsnmp_incdir)

    return {
        "basedir": basedir,
        "in_tree": in_tree,
        "compile_args": compile_args,
        "link_args": link_args,
        "libs": libs,
        "libdirs": libdirs,
        "incdirs": incdirs,
        "system_netsnmp_version": system_netsnmp_version.strip(),
        "homebrew_version": homebrew_version,
        "homebrew_netsnmp_version": homebrew_netsnmp_version,
        "homebrew_openssl_version": homebrew_openssl_version,
        "macports_version": macports_version,
        "macports_netsnmp_version": macports_netsnmp_version,
    }


def resolve_snmp_source_path(version_str: str) -> str:
    if version_str.startswith("5.6"):
        return "ezsnmp/src/net-snmp-5.6-final-patched"
    if version_str.startswith("5.7"):
        return "ezsnmp/src/net-snmp-5.7-final-patched"
    if version_str.startswith("5.8"):
        return "ezsnmp/src/net-snmp-5.8-final-patched"
    if version_str.startswith("5.9"):
        return "ezsnmp/src/net-snmp-5.9-final-patched"
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
