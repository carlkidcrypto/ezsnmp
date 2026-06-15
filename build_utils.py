"""Build utility helpers for ezsnmp.

This module contains helper functions used by both setup.py and the test suite
to configure and query the build environment.  Keeping them here (rather than
inline in setup.py) avoids the need for tests to load setup.py via importlib,
which can trigger packaging-time side effects.
"""

import os
from pathlib import Path
from re import search
from shlex import split as s_split
from subprocess import check_output, CalledProcessError, DEVNULL
from sys import argv, platform

# ---------------------------------------------------------------------------
# macOS package-manager helpers
# ---------------------------------------------------------------------------


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
        brew_output = check_output(
            "brew list net-snmp", shell=True, stderr=DEVNULL
        ).decode()
        lines = brew_output.splitlines()

        if not lines:
            return None

        # Extract net-snmp version (supports both /opt/homebrew and /usr/local paths)
        pattern = r"/(?:opt/homebrew|usr/local|home/linuxbrew/\.linuxbrew)/Cellar/net-snmp/(\d+\.\d+(?:\.\d+)?)/"
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
        # Look for any OpenSSL version (e.g., openssl@3, openssl@1.1, etc.)
        brew_info_output = check_output("brew info net-snmp", shell=True).decode()
        openssl_version = next(
            (
                line.split()[0]
                for line in brew_info_output.splitlines()
                if "/openssl@" in line
            ),
            None,
        )
        if not openssl_version:
            return None

        openssl_info_output = check_output(
            f"brew info {openssl_version}", shell=True
        ).decode()
        openssl_lines = openssl_info_output.splitlines()

        # Find the installation path by looking for lines containing /Cellar/
        # This is more robust than using a magic index
        openssl_path = None
        for line in openssl_lines:
            if "/Cellar/" in line and openssl_version in line:
                # Extract the path before any parentheses or additional info
                openssl_path = line.split("(")[0].strip()
                break

        # Fallback to line 4 (index 4) if pattern not found (backward compatibility)
        if not openssl_path and len(openssl_lines) > 4:
            openssl_path = openssl_lines[4].split("(")[0].strip()

        if openssl_path:
            libdirs.append(openssl_path + "/lib")
            incdirs.append(openssl_path + "/include")
        else:
            return None

        return homebrew_version, net_snmp_version, openssl_version, libdirs, incdirs

    except (CalledProcessError, IndexError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Generic env-var helpers
# ---------------------------------------------------------------------------


def split_env_list(raw_value):
    """Split an environment variable value into a list of entries.

    Accepts semicolons, commas, and ``os.pathsep`` as delimiters.
    Empty entries (after stripping whitespace) are discarded.

    Returns:
      list[str]: Non-empty, whitespace-stripped entries, or an empty list
                 when *raw_value* is falsy.
    """
    if not raw_value:
        return []
    normalized_value = raw_value.replace(";", os.pathsep).replace(",", os.pathsep)
    return [
        entry.strip() for entry in normalized_value.split(os.pathsep) if entry.strip()
    ]


def env_truthy(*names):
    """Return True when the first matching environment variable holds a truthy string.

    Accepted truthy values (case-insensitive): ``"1"``, ``"true"``, ``"yes"``, ``"on"``.
    Falls back through *names* in order until a non-empty variable is found;
    returns False if all are unset or empty.

    Args:
      *names: One or more environment variable names to check in order.

    Returns:
      bool: True when the resolved value is truthy, False otherwise.
    """
    value = get_first_env(*names)
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_first_env(*names):
    """Return the value of the first non-empty environment variable.

    Iterates through *names* and returns the value of the first variable
    that is set and non-empty.

    Args:
      *names: One or more environment variable names to check in order.

    Returns:
      str or None: The first non-empty value found, or None if all are unset/empty.
    """
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


# ---------------------------------------------------------------------------
# Windows-specific build configuration
# ---------------------------------------------------------------------------


def resolve_windows_netsnmp_version(include_dirs):
    configured_version = get_first_env(
        "EZSNMP_NETSNMP_VERSION",
        "NETSNMP_VERSION",
    )
    if configured_version:
        return configured_version

    for include_dir in include_dirs:
        header_candidates = (
            Path(include_dir) / "net-snmp" / "net-snmp-config.h",
            Path(include_dir) / "net-snmp-config.h",
        )
        for header_path in header_candidates:
            if not header_path.is_file():
                continue
            match = search(
                r'#define\s+PACKAGE_VERSION\s+"([^"]+)"',
                header_path.read_text(encoding="utf-8", errors="ignore"),
            )
            if match:
                return match.group(1)

    raise RuntimeError(
        "Unable to determine the Net-SNMP version on Windows. "
        "Set EZSNMP_NETSNMP_VERSION (or NETSNMP_VERSION) or ensure "
        "net-snmp-config.h is available under the configured include directory."
    )


def gather_windows_build_configuration():
    include_dirs = split_env_list(
        get_first_env(
            "EZSNMP_NETSNMP_INCLUDE_DIR",
            "EZSNMP_NETSNMP_INCLUDEDIR",
            "NETSNMP_INCLUDE_DIR",
            "NETSNMP_INCLUDEDIR",
        )
    )
    library_dirs = split_env_list(
        get_first_env(
            "EZSNMP_NETSNMP_LIB_DIR",
            "EZSNMP_NETSNMP_LIBDIR",
            "NETSNMP_LIB_DIR",
            "NETSNMP_LIBDIR",
        )
    )

    if not include_dirs or not library_dirs:
        raise RuntimeError(
            "Windows builds require Net-SNMP headers and libraries to be configured. "
            "Set EZSNMP_NETSNMP_INCLUDE_DIR and EZSNMP_NETSNMP_LIB_DIR "
            "(or the NETSNMP_* equivalents) before building ezsnmp."
        )

    libraries = split_env_list(
        get_first_env("EZSNMP_NETSNMP_LIBS", "NETSNMP_LIBS")
    ) or ["netsnmp", "advapi32", "ws2_32", "kernel32", "user32"]
    compile_args = []

    if env_truthy("EZSNMP_NETSNMP_USE_DLL", "NETSNMP_USE_DLL"):
        compile_args.append("/DNETSNMP_USE_DLL")

    return {
        "compile_args": compile_args,
        "link_args": [],
        "libs": libraries,
        "libdirs": library_dirs,
        "incdirs": ["ezsnmp/include/"] + include_dirs,
        "system_netsnmp_version": resolve_windows_netsnmp_version(include_dirs),
        "homebrew_version": None,
        "homebrew_netsnmp_version": None,
        "homebrew_openssl_version": None,
        "macports_version": None,
        "macports_netsnmp_version": None,
    }


# ---------------------------------------------------------------------------
# Top-level build configuration
# ---------------------------------------------------------------------------


def gather_build_configuration():
    basedir = None
    in_tree = False
    compile_args = ["/std:c++17", "/EHsc"] if platform == "win32" else ["-std=c++17"]
    link_args = []
    libs = []
    libdirs = []
    incdirs = []

    for arg in argv:
        if arg.startswith("--debug"):
            compile_args.extend(
                ["/W3", "/Od", "/Zi"] if platform == "win32" else ["-Wall", "-O0", "-g"]
            )
        elif arg.startswith("--basedir="):
            basedir = arg.split("=", 1)[1]
            in_tree = True

    if platform == "win32":
        if in_tree:
            raise RuntimeError("--basedir is not supported for Windows builds.")
        windows_cfg = gather_windows_build_configuration()
        windows_cfg.update(
            {
                "basedir": basedir,
                "in_tree": in_tree,
                "compile_args": compile_args + windows_cfg["compile_args"],
            }
        )
        return windows_cfg

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
