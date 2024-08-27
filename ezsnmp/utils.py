from __future__ import unicode_literals, absolute_import
from typing import Optional, Union

import ipaddress
import string


def strip_non_printable(value: Optional[str]) -> Optional[str]:
    """
    Removes any non-printable characters and adds an indicator to the string
    when binary characters are fonud.

    :param value: the value that you wish to strip
    """
    if value is None:
        return None

    # Filter all non-printable characters
    # (note that we must use join to account for the fact that Python 3
    # returns a generator)
    printable_value = "".join(filter(lambda c: c in string.printable, value))

    if printable_value != value:
        if printable_value:
            printable_value += " "
        printable_value += "(contains binary)"

    return printable_value


def tostr(value: Union[str, int, float, None]) -> Optional[str]:
    """
    Converts any variable to a string or returns None if the variable
    contained None to begin with; this function currently supports None,
    unicode strings, byte strings and numbers.

    :param value: the value you wish to convert to a string
    """

    if value is None:
        return None
    elif isinstance(value, str):
        return value
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return value


def is_hostname_ipv6(hostname: str) -> bool:
    try:
        ipaddress.IPv6Address(hostname)
    except ipaddress.AddressValueError:
        return False
    else:
        return True
