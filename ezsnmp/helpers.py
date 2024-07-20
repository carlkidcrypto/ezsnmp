from __future__ import unicode_literals

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
OID_INDEX_RE2 = re.compile(r"^(\w+::(?:\w+-\d+)(?:\.\d+)+)\.(\d+)$")

# This regular expression takes something like 'nsCacheTimeout.1.3.6.1.2.1'
# and splits it into 'nsCacheTimeout.1.3.6.1.2' and '1'
OID_INDEX_RE3 = re.compile(r"^([A-Z|a-z].*)\.(\d+)$")


def normalize_oid(oid, oid_index=None):
    """
    Ensures that the index is set correctly given an OID definition.

    :param oid: the OID to normalize
    :param oid_index: the OID index to normalize
    """

    # Determine the OID index from the OID if not specified
    if oid_index is None and oid is not None:
        first_match = OID_INDEX_RE.match(oid)
        second_match = OID_INDEX_RE2.match(oid)
        thrid_match = OID_INDEX_RE3.match(oid)

        if thrid_match:
            oid, oid_index = thrid_match.group(1, 2)

        elif second_match:
            oid, oid_index = second_match.group(1, 2)

        elif first_match:
            oid, oid_index = first_match.group(1, 2)

        elif oid == ".":
            oid = "."
            oid_index = ""

    return oid, oid_index
