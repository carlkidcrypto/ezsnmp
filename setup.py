#!/usr/bin/env python3

from subprocess import check_output, CalledProcessError
from sys import argv, platform, exit
from shlex import split as s_split
from setuptools import setup, Extension
from re import search
import json


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


def enable_legacy_support(version):
    """
    Helper to check if the detected Net-SNMP version is supported (5.6, 5.7, 5.8)

    Returns:
      bool: True if version matches 5.6, 5.7, or 5.8 (optionally with dot or suffix).
    """
    return bool(search(r"^5\.(6|7|8)(\.|$|\..*)", version or ""))


# Determine if a base directory has been provided with the --basedir option
basedir = None
in_tree = False
compile_args = ["-std=c++17"]
link_args = []

# Initialize these to empty lists, they will be populated
# either by in-tree logic or net-snmp-config
libs = []
libdirs = []
incdirs = []

# Flags for debugging output (initialized to None for clarity)
system_netsnmp_version = None
homebrew_version = None
homebrew_netsnmp_version = None
homebrew_openssl_version = None
macports_version = None
macports_netsnmp_version = None
macports_openssl_version = None


for arg in argv:
    if arg.startswith("--debug"):
        compile_args.extend(["-Wall", "-O0", "-g"])
    elif arg.startswith("--basedir="):
        basedir = arg.split("=")[1]
        in_tree = True


# If a base directory has been provided, we use it (for in-tree build)
if in_tree:
    print("Building in-tree with --basedir:", basedir)
    base_cmd = f"{basedir}/net-snmp-config"
    try:
        # Get CFLAGS (include paths)
        netsnmp_cflags = (
            check_output(f"{base_cmd} --cflags", shell=True).decode().strip()
        )
        for flag in s_split(netsnmp_cflags):
            if flag.startswith("-I"):
                incdirs.append(flag[2:])

        # Get LIBS (library names and paths)
        netsnmp_libs_output = (
            check_output(f"{base_cmd} --libs", shell=True).decode().strip()
        )
        for flag in s_split(netsnmp_libs_output):
            if flag.startswith("-L"):
                libdirs.append(flag[2:])
            elif flag.startswith("-l"):
                libs.append(flag[2:])
            # Handle framework flags for macOS (relevant for in-tree if it links frameworks)
            elif flag == "-framework":
                # The next flag is the framework name, append it to link_args
                # This needs careful handling if s_split doesn't keep them together
                # For simplicity, assuming it's handled by the general link_args append
                pass
            else:
                # Add other link args like -flat_namespace or framework names
                link_args.append(flag)

    except CalledProcessError as e:
        print(f"Error running net-snmp-config for in-tree build at {basedir}: {e}")
        print(
            "Please ensure net-snmp-config is available and executable in the specified basedir."
        )
        exit(1)

# Otherwise, we use the system-installed or Homebrew/MacPorts SNMP libraries via net-snmp-config primarily
else:
    print("Building using system/package manager installed Net-SNMP.")
    try:
        # First, try to get all flags directly from net-snmp-config
        netsnmp_cflags = (
            check_output("net-snmp-config --cflags", shell=True).decode().strip()
        )
        netsnmp_libs_output = (
            check_output("net-snmp-config --libs", shell=True).decode().strip()
        )

        # Parse cflags for include directories
        for flag in s_split(netsnmp_cflags):
            if flag.startswith("-I"):
                incdirs.append(flag[2:])

        # Parse libs for libraries and library directories
        pass_next_framework = False
        for flag in s_split(netsnmp_libs_output):
            if pass_next_framework:
                link_args.append(flag)  # Add the framework name (e.g., CoreFoundation)
                pass_next_framework = False
            elif flag.startswith("-L"):
                libdirs.append(flag[2:])
            elif flag.startswith("-l"):
                libs.append(flag[2:])
            elif flag == "-framework":  # Handle framework flags for macOS
                link_args.append(flag)
                pass_next_framework = True
            else:
                # Add other link args like -flat_namespace
                link_args.append(flag)

        # Append ezsnmp's own include directory if it's not already there
        # This is for ezsnmp's internal headers, not Net-SNMP's
        if "ezsnmp/include/" not in incdirs:
            incdirs.append("ezsnmp/include/")

        # Populate system_netsnmp_version for debugging output
        system_netsnmp_version = (
            check_output("net-snmp-config --version", shell=True).decode().strip()
        )

    except CalledProcessError as e:
        print(f"Error running net-snmp-config: {e}")
        print("Attempting to detect Homebrew/MacPorts as fallback for paths...")

        # Fallback logic if net-snmp-config fails or isn't found
        # This part of the original script is adapted to augment if net-snmp-config failed.

        # Homebrew detection
        try:
            homebrew_version = (
                check_output("brew --version", shell=True).decode().strip()
            )
            if search(r"Homebrew (\d+\.\d+\.\d+)", homebrew_version):
                try:
                    # Check if net-snmp is installed via Brew
                    brew_list_output = check_output(
                        "brew list net-snmp 2>/dev/null", shell=True
                    ).decode()
                    if brew_list_output:  # If net-snmp is listed
                        # Extract net-snmp version and paths from brew info
                        brew_info_netsnmp = check_output(
                            "brew info net-snmp", shell=True
                        ).decode()
                        match = search(
                            r"/opt/homebrew/Cellar/net-snmp/(\d+\.\d+\.\d+)/",
                            brew_info_netsnmp,
                        )
                        if match:
                            homebrew_netsnmp_version = match.group(1)
                            netsnmp_cellar_path = f"/opt/homebrew/Cellar/net-snmp/{homebrew_netsnmp_version}"
                            if f"{netsnmp_cellar_path}/include" not in incdirs:
                                incdirs.append(f"{netsnmp_cellar_path}/include")
                            if f"{netsnmp_cellar_path}/lib" not in libdirs:
                                libdirs.append(f"{netsnmp_cellar_path}/lib")
                            if "netsnmp" not in libs:  # Assuming default lib name
                                libs.append("netsnmp")

                        # Find OpenSSL dependency and add its paths
                        # Using brew info --json=v2 for more reliable path extraction
                        openssl_match = search(r"openssl(@\d+)?", brew_info_netsnmp)
                        if openssl_match:
                            homebrew_openssl_keg = openssl_match.group(0)
                            try:
                                openssl_info_json = check_output(
                                    f"brew info --json=v2 {homebrew_openssl_keg}",
                                    shell=True,
                                ).decode()
                                openssl_info = json.loads(openssl_info_json)
                                if openssl_info and openssl_info.get("formulae"):
                                    openssl_path = openssl_info["formulae"][0][
                                        "linked_keg_output"
                                    ]
                                    if f"{openssl_path}/lib" not in libdirs:
                                        libdirs.append(f"{openssl_path}/lib")
                                    if f"{openssl_path}/include" not in incdirs:
                                        incdirs.append(f"{openssl_path}/include")
                                    # Assuming openssl is linked as 'ssl' and 'crypto'
                                    if "ssl" not in libs:
                                        libs.append("ssl")
                                    if "crypto" not in libs:
                                        libs.append("crypto")
                            except (CalledProcessError, json.JSONDecodeError) as e:
                                print(f"Could not get OpenSSL info via brew json: {e}")

                except CalledProcessError as e:
                    print(f"Brew command failed during net-snmp/openssl detection: {e}")
            else:
                homebrew_version = (
                    None  # Reset if brew --version didn't match expected pattern
                )
        except CalledProcessError:
            homebrew_version = None
            print("Homebrew is not installed or brew command failed.")

        # MacPorts detection
        macports_version = is_macports_installed()
        macports_netsnmp_version = is_net_snmp_installed_macports()
        if macports_version and macports_netsnmp_version:
            # MacPorts typically installs to /opt/local/
            if "/opt/local/lib" not in libdirs:
                libdirs.append("/opt/local/lib")
            if "/opt/local/include" not in incdirs:
                incdirs.append("/opt/local/include")
            if "netsnmp" not in libs:  # Assuming default lib name
                libs.append("netsnmp")
            # If openssl is also installed via macports, its paths might be needed too
            # (Original script commented this out, but it's good to be comprehensive)
            # You might need to add similar logic for MacPorts OpenSSL if it's a separate dependency.


# Final check for empty lists if no method found libraries
if not libs and not libdirs and not incdirs:
    print(
        "\nERROR: No Net-SNMP libraries or include directories found after all attempts."
    )
    print(
        "Please ensure Net-SNMP is installed and discoverable by net-snmp-config, Homebrew, or MacPorts."
    )
    print("On macOS, you can usually install it via Homebrew: 'brew install net-snmp'")
    exit(1)


print(f"in_tree: {in_tree}")
print(f"compile_args: {compile_args}")
print(f"link_args: {link_args}")
print(f"platform: {platform}")
print(
    f"system_netsnmp_version: {str(system_netsnmp_version).strip() if system_netsnmp_version else 'Not detected'}"
)
print(
    f"homebrew_version: {str(homebrew_version).strip() if homebrew_version else 'Not detected'}"
)
print(
    f"homebrew_netsnmp_version: {homebrew_netsnmp_version if homebrew_netsnmp_version else 'Not detected'}"
)
print(
    f"homebrew_openssl_version: {homebrew_openssl_version if homebrew_openssl_version else 'Not detected'}"
)
print(
    f"macports_version: {str(macports_version).strip() if macports_version else 'Not detected'}"
)
print(
    f"macports_netsnmp_version: {macports_netsnmp_version if macports_netsnmp_version else 'Not detected'}"
)
print(
    f"macports_openssl_version: {macports_openssl_version if macports_openssl_version else 'Not detected'}"
)
print(f"libs: {libs}")
print(f"libdirs: {libdirs}")
print(f"incdirs: {incdirs}")

ENABLE_LEGACY_SUPPORT = enable_legacy_support(system_netsnmp_version)

# Define a macro for the C++ extensions to indicate if the package version is supported
define_macros = [("ENABLE_LEGACY_SUPPORT", int(ENABLE_LEGACY_SUPPORT))]

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
            define_macros=define_macros,
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
            define_macros=define_macros,
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
            define_macros=define_macros,
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
            define_macros=define_macros,
        ),
    ],
)
