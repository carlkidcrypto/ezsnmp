#!/usr/bin/env python3

import os
from subprocess import check_output, CalledProcessError, run
from sys import argv, platform
from shlex import split as s_split
from setuptools import setup, Extension
from re import search
from setuptools.command.build_ext import build_ext


# Install Helpers
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


# Define SWIG targets and the custom build command
# ---------------------------------------------------------------------------

# Define which .i files should be converted to which .cpp files
# Paths are updated to reflect the 'ezsnmp/interface/' directory.
swig_targets = [
    ("ezsnmp/interface/datatypes.i", "ezsnmp/src/ezsnmp_datatypes.cpp"),
    ("ezsnmp/interface/exceptionsbase.i", "ezsnmp/src/ezsnmp_exceptionsbase.cpp"),
    ("ezsnmp/interface/netsnmpbase.i", "ezsnmp/src/ezsnmp_netsnmpbase.cpp"),
    ("ezsnmp/interface/sessionbase.i", "ezsnmp/src/ezsnmp_sessionbase.cpp"),
]


class SwigBuildExt(build_ext):
    """
    Custom build_ext command to run SWIG before building the C++ extensions.
    """

    def run(self):
        print("--- Running SWIG to generate wrapper code ---")

        # Base SWIG command, updated with arguments from development.rst
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

        # Add all include directories to the SWIG command
        # We grab them from the first extension, as they are the same for all.
        for inc_dir in self.extensions[0].include_dirs:
            swig_command.append(f"-I{inc_dir}")

        # Also add the interface directory to the include path for SWIG
        swig_command.append("-Iezsnmp/interface")

        # Run SWIG for each target
        for interface_file, wrapper_file in swig_targets:
            command = swig_command + ["-o", wrapper_file, interface_file]
            print(f"Executing: {' '.join(command)}")
            try:
                run(command, check=True)
            except (CalledProcessError, FileNotFoundError):
                print(f"Error: SWIG execution failed for {interface_file}.")
                print("Please ensure that SWIG is installed and in your system's PATH.")
                exit(1)

        print("--- SWIG processing complete ---")
        # After SWIG has run, proceed with the original build process
        super().run()


# ---------------------------------------------------------------------------


# Determine if a base directory has been provided with the --basedir option
basedir = None
in_tree = False
compile_args = ["-std=c++17"]
link_args = []
system_netsnmp_version = check_output("net-snmp-config --version", shell=True).decode()
homebrew_version = None
homebrew_netsnmp_version = None
homebrew_openssl_version = None
macports_version = None
macports_netsnmp_version = None
macports_openssl_version = None
libs = []
libdirs = []
incdirs = []

for arg in argv:
    if arg.startswith("--debug"):
        compile_args.extend(["-Wall", "-O0", "-g"])
    elif arg.startswith("--basedir="):
        basedir = arg.split("=")[1]
        in_tree = True


# If a base directory has been provided, we use it
if in_tree:
    base_cmd = "{0}/net-snmp-config {{{0}}}".format(basedir)
    libs_cmd = base_cmd.format("--build-lib-dirs {0}".format(basedir))
    incl_cmd = base_cmd.format("--build-includes {0}".format(basedir))

    netsnmp_libs = check_output(base_cmd.format("--libs"), shell=True).decode()
    libdirs = check_output(libs_cmd, shell=True).decode()
    incdirs = check_output(incl_cmd, shell=True).decode()

    libs = [flag[2:] for flag in s_split(netsnmp_libs) if flag[:2] == "-l"]
    libdirs = [flag[2:] for flag in s_split(libdirs) if flag[:2] == "-L"]
    incdirs = [flag[2:] for flag in s_split(incdirs) if flag[:2] == "-I"]

# Otherwise, we use the system-installed or Homebrew SNMP libraries
else:
    netsnmp_libs = check_output("net-snmp-config --libs", shell=True).decode()

    pass_next = False
    has_arg = ("-framework",)
    for flag in s_split(netsnmp_libs):
        if pass_next:
            link_args.append(flag)
            pass_next = False
        elif flag in has_arg:
            link_args.append(flag)
            pass_next = True
        elif flag == "-flat_namespace":
            link_args.append(flag)
            pass_next = False

    libs = [flag[2:] for flag in s_split(netsnmp_libs) if flag[:2] == "-l"]
    libdirs = [flag[2:] for flag in s_split(netsnmp_libs) if flag[:2] == "-L"]
    incdirs = ["ezsnmp/include/"]

    # Try to get Homebrew net-snmp information
    homebrew_info = get_homebrew_net_snmp_info()
    if homebrew_info:
        (
            homebrew_version,
            homebrew_netsnmp_version,
            homebrew_openssl_version,
            temp_libdirs,
            temp_incdirs,
        ) = homebrew_info
        libdirs = libdirs + temp_libdirs
        incdirs = incdirs + temp_incdirs
        print("Using Homebrew net-snmp installation...")
    else:
        # Check if Homebrew is installed to provide accurate status
        homebrew_version = get_homebrew_info()
        if homebrew_version:
            print("Homebrew is installed but net-snmp is not from Homebrew...")
        else:
            print("Homebrew is not installed...")

        # Fallback: try to find net-snmp include directories from library directories
        netsnmp_incdir = None
        for dir in libdirs:
            if "net-snmp" in dir:
                netsnmp_incdir = dir.replace("lib", "include")
                incdirs = incdirs + [netsnmp_incdir]
                break
            elif "x86_64-linux-gnu" in dir:
                netsnmp_incdir = "/usr/include/net-snmp"
                incdirs = incdirs + [netsnmp_incdir]
                break

    macports_version = is_macports_installed()
    macports_netsnmp_version = is_net_snmp_installed_macports()

    if macports_version and macports_netsnmp_version:
        for dir in libdirs:
            if "/opt/local/lib" in dir:
                netsnmp_incdir = dir.replace("lib", "include")
                incdirs = incdirs + [netsnmp_incdir]

# Determine which source files to use based on the Net-SNMP version
version_str = system_netsnmp_version.strip()
snmp_source_path = "ezsnmp/src"

if version_str.startswith("5.6"):
    snmp_source_path = "ezsnmp/src/net-snmp-5.6-final-patched"
elif version_str.startswith("5.7"):
    snmp_source_path = "ezsnmp/src/net-snmp-5.7-final-patched"
elif version_str.startswith("5.8"):
    snmp_source_path = "ezsnmp/src/net-snmp-5.8-final-patched"
elif version_str.startswith("5.9"):
    snmp_source_path = "ezsnmp/src/net-snmp-5.9-final-patched"
else:
    raise RuntimeError(f"Unsupported net-snmp version: {version_str}")

print(f"in_tree: {in_tree}")
print(f"compile_args: {compile_args}")
print(f"link_args: {link_args}")
print(f"platform: {platform}")
print(f"system_netsnmp_version: {str(system_netsnmp_version).strip()}")
print(f"homebrew_version: {homebrew_version if homebrew_version else 'None'}")
print(f"homebrew_netsnmp_version: {homebrew_netsnmp_version}")
print(f"homebrew_openssl_version: {homebrew_openssl_version}")
print(f"macports_version: {macports_version if macports_version else 'None'}")
print(f"macports_netsnmp_version: {macports_netsnmp_version}")
print(f"macports_openssl_version: {macports_openssl_version}")
print(f"libs: {libs}")
print(f"libdirs: {libdirs}")
print(f"incdirs: {incdirs}")
print(f"Using SNMP sources from: {snmp_source_path}")


# Define the source files for the extensions that depend on the Net-SNMP version
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
] + netsnmp_versioned_sources

sessionbase_sources = [
    "ezsnmp/src/ezsnmp_sessionbase.cpp",  # Generated by SWIG
    "ezsnmp/src/exceptionsbase.cpp",
    "ezsnmp/src/datatypes.cpp",
    "ezsnmp/src/sessionbase.cpp",
    "ezsnmp/src/helpers.cpp",
] + netsnmp_versioned_sources


setup(
    ext_modules=[
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
    ],
    # Tell setuptools to use your custom command
    cmdclass={
        "build_ext": SwigBuildExt,
    },
)
