from subprocess import check_output, CalledProcessError
from sys import argv, platform, exit
from shlex import split as s_split

import sysconfig
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as BuildCommand
from setuptools.command.test import test as TestCommand
import setuptools.command.build as build
from setuptools import dist

# Determine if a base directory has been provided with the --basedir option
basedir = None
in_tree = False
# Add compiler flags if debug is set
compile_args = ["-std=c++17", "-Wunused-function", "-fpermissive"]
link_args = []
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
    incdirs = []

    if platform == "darwin":  # OS X
        # Check if net-snmp is installed via Brew
        try:
            brew = check_output("brew list net-snmp 2>/dev/null", shell=True).decode()
            lines = brew.splitlines()
            include_dir = list(filter(lambda l: "include/net-snmp" in l, lines))[0]
            incdirs.append(include_dir[: include_dir.index("include/net-snmp") + 7])
            lib_dir = list(filter(lambda l: "lib/libnetsnmp.dylib" in l, lines))[0]
            libdirs.append(lib_dir[: lib_dir.index("lib/libnetsnmp.dylib") + 3])
            # The homebrew version also depends on the Openssl keg
            brew = check_output("brew info net-snmp", shell=True).decode()
            openssl_ver = list(
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
                "brew info {0}".format(openssl_ver), shell=True
            ).decode()
            temp = brew.split("\n")
            # As of 01/02/2024 brew info openssl spits out lines. the fourth one is what we care about
            # ==> openssl@3: stable 3.2.0 (bottled)
            # Cryptography and SSL/TLS Toolkit
            # https://openssl.org/
            # /opt/homebrew/Cellar/openssl@3/3.2.0_1 (6,805 files, 31.9MB) *     <-- THIS IS THE ONE WE WANT
            # Poured from bottle using the formulae.brew.sh API on 2023-12-16 at 21:41:39
            # From: https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/o/openssl@3.rb
            # License: Apache-2.0
            # ==> Dependencies
            # Required: ca-certificates ✔
            # ==> Caveats
            # A CA file has been bootstrapped using certificates from the system
            # keychain. To add additional certificates, place .pem files in
            # /opt/homebrew/etc/openssl@3/certs

            # and run
            # /opt/homebrew/opt/openssl@3/bin/c_rehash
            # ==> Analytics
            # install: 428,659 (30 days), 1,304,159 (90 days), 3,175,965 (365 days)
            # install-on-request: 59,856 (30 days), 182,474 (90 days), 518,964 (365 days)
            # build-error: 4,875 (30 days)
            temp_path = str(temp[3].split("(")[0]).strip()

            libdirs.append(temp_path + "/lib")
            incdirs.append(temp_path + "/include")

            print(f"libdirs: {libdirs}")
            print(f"incdirs: {incdirs}")
            print(f"openssl_ver: {openssl_ver}")

        except CalledProcessError:
            print("A brew command failed...")
            pass

print(f"in_tree: {in_tree}")
print(f"compile_args: {compile_args}")
print(f"link_args: {link_args}")
print(f"platform: {platform}")


# Setup the py.test class for use with the test command
class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.pytest_args)
        exit(errno)


class RelinkLibraries(BuildCommand):
    """Fix dylib path for macOS

    Depending on system configuration and Brew setup, interface.so may get linked to
    the wrong dylib file (prioritizing the system's 5.6.2.1 over brew's 5.8+). This
    will change the path if net-snmp is installed via `brew`.

    Non-brew installations and non-macOS systems will not be affected.
    """

    def run(self):
        BuildCommand.run(self)
        if platform == "darwin":  # Newer Net-SNMP dylib may not be linked to properly
            try:
                brew = check_output(
                    "brew list net-snmp 2>/dev/null", shell=True
                ).decode()
            except CalledProcessError:
                return
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
            prefix = (
                check_output("net-snmp-config --prefix", shell=True).decode().strip()
            )
            _ = check_output(
                "install_name_tool -change {0} {1} {2}/ezsnmp/interface{3}".format(
                    linked, lib_dir, b.build_platlib, ext
                ),
                shell=True,
            )


setup(
    tests_require=["pytest-cov", "pytest-sugar", "pytest"],
    cmdclass={"test": PyTest, "build_ext": RelinkLibraries},
    ext_modules=[
        Extension(
            "ezsnmp.interface",
            ["ezsnmp/interface.cpp"],
            library_dirs=libdirs,
            include_dirs=incdirs,
            libraries=libs,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        )
    ],
)
