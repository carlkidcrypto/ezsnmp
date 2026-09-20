import pytest

from ezsnmp.exceptions import ConnectionError, GenericError, ParseError
from ezsnmp.netsnmp import snmptrap


def test_parse_error_unknown_flag():
    """Test that snmptrap with an unknown -C flag raises ParseError."""
    args = [
        "-v",
        "2c",
        "-c",
        "public",
        "-Cz",
        "localhost:11162",
        "",
        ".1.3.6.1.6.3.1.1.5.1",
        "0",
    ]
    with pytest.raises(ParseError):
        snmptrap(args)


def test_basic_v2c():
    """Test that snmptrap sends a basic V2c trap successfully (returns 0).

    UDP is fire-and-forget; snmp_send succeeds even without a listening trap receiver.
    """
    args = [
        "-v",
        "2c",
        "-c",
        "public",
        "localhost:11162",
        "",  # sysUpTime: empty uses current uptime
        ".1.3.6.1.6.3.1.1.5.1",  # SNMPv2-MIB::snmpTraps.coldStart
    ]
    result = snmptrap(args)
    assert result == 0


def test_unknown_host():
    """Test that snmptrap raises an error for an unknown host.

    Depending on the OS and net-snmp version, DNS resolution failure for an
    unknown host raises either ConnectionError or GenericError.  Both are
    acceptable outcomes; the important thing is that an exception is raised.
    """
    args = [
        "-v",
        "2c",
        "-c",
        "public",
        "nonexistenthost.invalid:11162",
        "",
        ".1.3.6.1.6.3.1.1.5.1",
    ]
    with pytest.raises((ConnectionError, GenericError)):
        snmptrap(args)


def test_invalid_version():
    """Test that snmptrap raises ParseError for an invalid SNMP version."""
    args = [
        "-v",
        "999",
        "-c",
        "public",
        "localhost:11162",
        "",
        ".1.3.6.1.6.3.1.1.5.1",
    ]
    with pytest.raises(ParseError):
        snmptrap(args)


def test_v2c_with_varbind():
    """Test that snmptrap sends a V2c trap with an additional varbind successfully."""
    args = [
        "-v",
        "2c",
        "-c",
        "public",
        "localhost:11162",
        "",  # sysUpTime
        ".1.3.6.1.6.3.1.1.5.4",  # SNMPv2-MIB::snmpTraps.linkUp
        "SNMPv2-MIB::sysDescr.0",  # OID
        "s",  # type: string
        "test link up",  # value
    ]
    result = snmptrap(args)
    assert result == 0
