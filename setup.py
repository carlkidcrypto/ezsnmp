#!/usr/bin/env python3

from subprocess import check_output, CalledProcessError
from sys import argv, platform
from shlex import split as s_split
from setuptools import setup, Extension
from re import search


# Install Helpers
def is_macports_installed():
    """
    Checks if MacPorts is installed on the system.

    Returns:
      str: The MacPorts version if installed, "" otherwise.
    """
    try:
        # Check if the `port` command is available and get the version
        version_output = check_output("port version", shell=True).decode()
        # Extract version using regex. It'll match something like: Version: `2.10.5`.
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
        # Use `port installed` to check for the package
        macports_output = check_output("port installed net-snmp", shell=True).decode()
        # Use regex to match and extract the version
        pattern = r"net-snmp @(\d+\.\d+\.\d+[_+a-zA-Z0-9]*) \(active\)"
        match = search(pattern, macports_output)
        if match:
            return match.group(1)
        else:
            return ""
    except CalledProcessError:
        return ""


# Determine if a base directory has been provided with the --basedir option
basedir = None
in_tree = False
compile_args = ["-std=c++17", "-Werror"]
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
        # Note from GCC manual:
        #       If you use multiple -O options, with or without level numbers,
        #       the last such option is the one that is effective.
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
    # macOS-specific
    has_arg = ("-framework",)
    for flag in s_split(netsnmp_libs):
        if pass_next:
            link_args.append(flag)
            pass_next = False
        elif flag in has_arg:  # -framework CoreFoundation
            link_args.append(flag)
            pass_next = True
        elif flag == "-flat_namespace":
            link_args.append(flag)
            pass_next = False

    libs = [flag[2:] for flag in s_split(netsnmp_libs) if flag[:2] == "-l"]
    libdirs = [flag[2:] for flag in s_split(netsnmp_libs) if flag[:2] == "-L"]
    incdirs = ["ezsnmp/include/"]

    try:
        # Check if brew is installed via: `brew --version` it should return something like: `Homebrew 4.4.5`
        homebrew_version = check_output("brew --version", shell=True).decode()
        if search(r"Homebrew (\d+\.\d+\.\d+)", homebrew_version):
            # Check if net-snmp is installed via Brew
            try:
                brew = check_output(
                    "brew list net-snmp 2>/dev/null", shell=True
                ).decode()
                lines = brew.splitlines()
                # extract brew version here...
                pattern = r"/opt/homebrew/Cellar/net-snmp/(\d+\.\d+\.\d+)/"
                match = search(pattern, lines[0])
                if match:
                    version = match.group(1)
                    homebrew_netsnmp_version = version

                temp_include_dir = list(
                    filter(lambda l: "include/net-snmp" in l, lines)
                )[0]
                temp_incdirs = []
                temp_libdirs = []
                temp_incdirs.append(
                    temp_include_dir[: temp_include_dir.index("include/net-snmp") + 7]
                )

                if platform == "darwin":
                    lib_dir = list(
                        filter(lambda l: "lib/libnetsnmp.dylib" in l, lines)
                    )[0]
                    temp_libdirs.append(
                        lib_dir[: lib_dir.index("lib/libnetsnmp.dylib") + 3]
                    )

                # The homebrew version also depends on the Openssl keg
                brew = check_output("brew info net-snmp", shell=True).decode()
                homebrew_openssl_version = list(
                    filter(
                        lambda o: "openssl" in o,
                        *map(
                            str.split,
                            filter(
                                lambda l: "openssl" in l,
                                str(brew.replace("'", "")).split("\n"),
                            ),
                        ),
                    )
                )[0]

                brew = check_output(
                    "brew info {0}".format(homebrew_openssl_version), shell=True
                ).decode()
                temp = brew.split("\n")
                # As of 06/04/2024 brew info openssl spits out lines. the fifth one is what we care about
                # This works for now, but we need a better solution
                # ==> openssl@3: stable 3.3.0 (bottled)
                # Cryptography and SSL/TLS Toolkit
                # https://openssl.org/
                # Installed
                # /opt/homebrew/Cellar/openssl@3/3.3.0 (6,977 files, 32.4MB) *
                # Poured from bottle using the formulae.brew.sh API on 2024-06-04 at 21:17:37
                # From: https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/o/openssl@3.rb
                # License: Apache-2.0
                # ...
                # print(temp)
                temp_path = str(temp[4].split("(")[0]).strip()

                temp_libdirs.append(temp_path + "/lib")
                temp_incdirs.append(temp_path + "/include")

                libdirs = libdirs + temp_libdirs
                incdirs = incdirs + temp_incdirs

            except CalledProcessError:
                print("A brew command failed...")

    except CalledProcessError:
        homebrew_version = None
        print("Homebrew is not installed...")

        # Add in system includes instead of Homebrew ones
        netsnmp_incdir = None
        for dir in libdirs:
            # MacOS
            if "net-snmp" in dir:
                netsnmp_incdir = dir.replace("lib", "include")
                incdirs = incdirs + [netsnmp_incdir]
                break

            # Linux
            elif "x86_64-linux-gnu" in dir:
                netsnmp_incdir = "/usr/include/net-snmp"
                incdirs = incdirs + [netsnmp_incdir]
                break

    macports_version = is_macports_installed()
    macports_netsnmp_version = is_net_snmp_installed_macports()
    # macports_openssl_version = is_openssl_installed_macports()

    if macports_version and macports_netsnmp_version:
        for dir in libdirs:
            if "/opt/local/lib" in dir:
                netsnmp_incdir = dir.replace("lib", "include")
                incdirs = incdirs + [netsnmp_incdir]

print(f"in_tree: {in_tree}")
print(f"compile_args: {compile_args}")
print(f"link_args: {link_args}")
print(f"platform: {platform}")
print(f"system_netsnmp_version: {str(system_netsnmp_version).strip()}")
print(f"homebrew_version: {str(homebrew_version).strip()}")
print(f"homebrew_netsnmp_version: {homebrew_netsnmp_version}")
print(f"homebrew_openssl_version: {homebrew_openssl_version}")
print(f"macports_version: {str(macports_version).strip()}")
print(f"macports_netsnmp_version: {macports_netsnmp_version}")
print(f"macports_openssl_version: {macports_openssl_version}")
print(f"libs: {libs}")
print(f"libdirs: {libdirs}")
print(f"incdirs: {incdirs}")

setup(
    ext_modules=[
        Extension(
            name="ezsnmp/_datatypes",
            sources=[
                "ezsnmp/src/ezsnmp_datatypes.cpp",
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
                "ezsnmp/src/ezsnmp_exceptionsbase.cpp",
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
            sources=[
                "ezsnmp/src/ezsnmp_netsnmpbase.cpp",
                "ezsnmp/src/exceptionsbase.cpp",
                "ezsnmp/src/datatypes.cpp",
                "ezsnmp/src/helpers.cpp",
                "ezsnmp/src/snmpbulkget.cpp",
                "ezsnmp/src/snmpgetnext.cpp",
                "ezsnmp/src/snmpbulkwalk.cpp",
                "ezsnmp/src/snmpget.cpp",
                "ezsnmp/src/snmpwalk.cpp",
                "ezsnmp/src/snmpset.cpp",
                "ezsnmp/src/snmptrap.cpp",
            ],
            library_dirs=libdirs,
            include_dirs=incdirs,
            libraries=libs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        ),
        Extension(
            name="ezsnmp/_sessionbase",
            sources=[
                "ezsnmp/src/ezsnmp_sessionbase.cpp",
                "ezsnmp/src/exceptionsbase.cpp",
                "ezsnmp/src/datatypes.cpp",
                "ezsnmp/src/sessionbase.cpp",
                "ezsnmp/src/helpers.cpp",
                "ezsnmp/src/snmpbulkget.cpp",
                "ezsnmp/src/snmpbulkwalk.cpp",
                "ezsnmp/src/snmpget.cpp",
                "ezsnmp/src/snmpgetnext.cpp",
                "ezsnmp/src/snmpwalk.cpp",
                "ezsnmp/src/snmpset.cpp",
                "ezsnmp/src/snmptrap.cpp",
            ],
            library_dirs=libdirs,
            include_dirs=incdirs,
            libraries=libs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        ),
    ],
)
