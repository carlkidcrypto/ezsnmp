from __future__ import unicode_literals

from typing import Optional, Tuple, overload

import re

# This regular expression is used to extract the index from an OID
# We attempt to extract the index from an OID (e.g. sysDescr.0
# or .iso.org.dod.internet.mgmt.mib-2.system.sysContact.0)
OID_INDEX_RE = re.compile(
    r"""(
            \.?\d+(?:\.\d+)*              # numeric OID
            |                             # or
            (?:\w+(?:[-:]*\w+)+)          # regular OID
            |                             # or
            (?:\.?iso(?:\.\w+[-:]*\w+)+)  # fully qualified OID
        )
        \.?(.*)                           # OID index
     """,
    re.VERBOSE,
)

# This regular expression takes something like 'SNMPv2::mib-2.17.7.1.4.3.1.2.300'
# and splits it into 'SNMPv2::mib-2' and '17.7.1.4.3.1.2.300'
OID_INDEX_RE2 = re.compile(r"^([^\.]+::[^\.]+)\.(.*)$")


@overload
def normalize_oid(oid: str, oid_index: str) -> Tuple[str, str]: ...


@overload
def normalize_oid(oid: str, oid_index: Optional[str]) -> Tuple[str, str]: ...


@overload
def normalize_oid(oid=None, oid_index=None) -> Tuple[None, None]: ...


def normalize_oid(
    oid: Optional[str] = None, oid_index: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Ensures that the index is set correctly given an OID definition.

    :param oid: the OID to normalize
    :param oid_index: the OID index to normalize
    """

    # Determine the OID index from the OID if not specified
    if oid_index is None and oid is not None:
        first_match = OID_INDEX_RE.match(oid)
        second_match = OID_INDEX_RE2.match(oid)

        if second_match:
            oid, oid_index = second_match.group(1, 2)

        elif first_match:
            oid, oid_index = first_match.group(1, 2)

        elif oid == ".":
            oid = "."
            oid_index = ""

    return oid, oid_index
