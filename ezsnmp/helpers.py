from __future__ import unicode_literals

from .exceptions import EzSNMPError

def normalize_oid(oid=None, oid_index=None):
    """
    Ensures that the index is set correctly given an OID definition.

    :param oid: the OID to normalize
    :param oid_index: the OID index to normalize
    """

    # Determine the OID index from the OID if not specified
    if oid_index is None and oid is not None:
        # We attempt to extract the index from an OID (e.g. sysDescr.0
        # or .iso.org.dod.internet.mgmt.mib-2.system.sysContact.0 or
        # SNMPv2::mib-2.17.7.1.4.3.1.2.300)
        if "." not in oid:
            oid = oid
            oid_index = ""
            return oid, oid_index

        subidentifiers = str(oid).split(".")
        print(f"oid: {oid}")
        print(f"oid_index: {oid_index}")
        print(subidentifiers)

        if "::" not in oid and any(c.isalpha() for c in oid):
            oid_index = subidentifiers.pop()
            oid = ".".join(subidentifiers)

        elif "::" not in oid and not any(c.isalpha() for c in oid):
            oid_index = ""
            oid = oid

        elif "::" in oid:
            oid_index = subidentifiers[1]
            oid = subidentifiers[0]

    return oid, oid_index
