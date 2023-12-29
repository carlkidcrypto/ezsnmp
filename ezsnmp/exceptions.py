from __future__ import unicode_literals


class EzSNMPError(Exception):
    """The base Easy SNMP exception which covers all exceptions raised."""

    pass


class EzSNMPConnectionError(EzSNMPError):
    """Indicates a problem connecting to the remote host."""

    pass


class EzSNMPTimeoutError(EzSNMPConnectionError):
    """Raised when an SNMP request times out."""

    pass


class EzSNMPUnknownObjectIDError(EzSNMPError):
    """Raised when a nonexistent OID is requested."""

    pass


class EzSNMPNoSuchNameError(EzSNMPError):
    """
    Raised when an OID is requested which may be an invalid object name
    or invalid instance (only applies to SNMPv1).
    """

    pass


class EzSNMPNoSuchObjectError(EzSNMPError):
    """
    Raised when an OID is requested which may have some form of existence but
    is an invalid object name.
    """

    pass


class EzSNMPNoSuchInstanceError(EzSNMPError):
    """
    Raised when a particular OID index requested from Net-SNMP doesn't exist.
    """

    pass


class EzSNMPUndeterminedTypeError(EzSNMPError):
    """
    Raised when the type cannot be determined when setting the value of an OID.
    """

    pass
