#!/usr/bin/env python3

from subprocess import check_output, CalledProcessError
from sys import argv, platform
from shlex import split as s_split

import sysconfig
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as BuildCommand
import setuptools.command.build as build
from setuptools import dist
from homebrew import HomeBrew

# Determine if a base directory has been provided with the --basedir option
basedir = None
in_tree = False
compile_args = ["-std=c++17", "-Werror"]
link_args = []
netsnmp_version = check_output("net-snmp-config --version", shell=True).decode()
homebrew_version = None

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

# Otherwise, we use the system-installed SNMP libraries
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

    # link_args += [flag for flag in s_split(netsnmp_libs) if flag[:2] == '-f']
    libs = [flag[2:] for flag in s_split(netsnmp_libs) if flag[:2] == "-l"]
    libdirs = [flag[2:] for flag in s_split(netsnmp_libs) if flag[:2] == "-L"]
    incdirs = ["ezsnmp/include/"]

    print(f"libs: {libs}")
    print(f"libdirs: {libdirs}")
    print(f"incdirs: {incdirs}")

    hb = HomeBrew(libdirs=libdirs, incdirs=incdirs)
    hb.check_brew_isinstalled()

print(f"in_tree: {in_tree}")
print(f"compile_args: {compile_args}")
print(f"link_args: {link_args}")
print(f"platform: {platform}")
print(f"netsnmp_version: {netsnmp_version}")
print(f"homebrew_version: {homebrew_version}")


class RelinkLibraries(BuildCommand):
    """Fix dylib path for macOS

    Depending on system configuration and Brew setup, interface.so may get linked to
    the wrong dylib file (prioritizing the system's 5.6.2.1 over brew's 5.8+). This
    will change the path if net-snmp is installed via `brew`.

    Non-brew installations and non-macOS systems will not be affected.
    """

    def __init__():
        pass

    def run(self):
        BuildCommand.run(self)
        if platform == "darwin":  # Newer Net-SNMP dylib may not be linked to properly
            try:
                brew = check_output(
                    "brew list net-snmp 2>/dev/null", shell=True
                ).decode()
            except CalledProcessError:
                return
            
            lines = hb.get_lines()
            lib_dir = list(filter(lambda l: "lib/libnetsnmp.dylib" in l, lines))[0]
            b = build.build(dist.Distribution())  # Dynamically determine build path
            b.finalize_options()
            ext = sysconfig.get_config_var("EXT_SUFFIX") or ".so"  # None for Python 2
            linked = (
                check_output(
                    (
                        "otool -L {0}/ezsnmp/interface{1} | "
                        r"egrep 'libnetsnmp\.' | "
                        "tr -s '\t' ' ' | "
                        "cut -d' ' -f2"
                    ).format(b.build_platlib, ext),
                    shell=True,
                )
                .decode()
                .strip()
            )

            if linked:
                # install_name_tool -change /opt/homebrew/opt/net-snmp/lib/libnetsnmp.40.dylib /opt/homebrew/Cellar/net-snmp/5.9.4/lib/libnetsnmp.dylib build/lib.macosx-10.9-universal2-cpython-39/ezsnmp/interface.cpython-39-darwin.so
                cmd_to_run = (
                    "install_name_tool -change {0} {1} {2}/ezsnmp/interface{3}".format(
                        linked, lib_dir, b.build_platlib, ext
                    )
                )

                print("cmd_to_run: ", cmd_to_run)
                _ = check_output(
                    cmd_to_run,
                    shell=True,
                )

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