from re import search
from subprocess import check_output, CalledProcessError


class MacPorts:
    def __init__():
        pass

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
