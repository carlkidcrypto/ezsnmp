#!/usr/bin/env python3

from subprocess import check_output, CalledProcessError, run
from sys import argv, platform
from shlex import split as s_split
from setuptools import setup, Extension
from re import search

# Import build_ext to subclass it
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

    try:
        homebrew_version = check_output("brew --version", shell=True).decode()
        if search(r"Homebrew (\d+\.\d+\.\d+)", homebrew_version):
            try:
                brew = check_output(
                    "brew list net-snmp 2>/dev/null", shell=True
                ).decode()
                lines = brew.splitlines()
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
            name="ezsnmp._datatypes",
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
            name="ezsnmp._exceptionsbase",
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
            name="ezsnmp._netsnmpbase",
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
