#!/usr/bin/env python3

from subprocess import check_output, CalledProcessError
from sys import argv, platform
from shlex import split as s_split
from setuptools import setup, Extension
from re import search

from macports import MacPorts
from homebrew import HomeBrew


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

    homebrew = HomeBrew()
    # Make HomeBrew() getters return None or "" if libdirs or incdirs aren't found.
    if homebrew.libdirs and homebrew.incdirs:
        libdirs = homebrew.libdirs
        incdirs = homebrew.incdirs
        homebrew_version = homebrew.homebrew_version
        homebrew_netsnmp_version = homebrew.homebrew_netsnmp_version
        homebrew_openssl_version = homebrew.homebrew_openssl_version

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

        macports = MacPorts()
        macports_version = macports.is_macports_installed()
        macports_netsnmp_version = macports.is_net_snmp_installed_macports()
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
# print(f"macports_openssl_version: {macports_openssl_version}")
print(f"libs: {libs}")
print(f"libdirs: {libdirs}")
print(f"incdirs: {incdirs}")

setup(
    ext_modules=[
        Extension(
            name="ezsnmp/_netsnmp",
            sources=[
                "ezsnmp/src/ezsnmp_netsnmp.cpp",
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
    ],
)
