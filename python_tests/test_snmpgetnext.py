import pytest

from ezsnmp.exceptions import GenericError, ParseError
from ezsnmp.netsnmp import snmpgetnext


def test_regular(netsnmp_args):
    """Test snmpgetnext returns the next OID after sysDescr.0."""
    netsnmp_args = netsnmp_args + ["sysDescr.0"]
    res = snmpgetnext(netsnmp_args, "testing_getnext")
    assert res is not None
    assert len(res) > 0
    assert res[0].oid != ""


def test_invalid_version():
    """Test snmpgetnext raises ParseError for an invalid SNMP version."""
    args = ["-v", "999", "-c", "public", "localhost:11161", "sysDescr.0"]
    with pytest.raises(ParseError):
        snmpgetnext(args, "testing_getnext_invalid_version")


def test_unknown_oid(netsnmp_args):
    """Test snmpgetnext raises GenericError for an unknown OID."""
    with pytest.raises(GenericError):
        netsnmp_args = netsnmp_args + ["doesnotexistoid12345"]
        snmpgetnext(netsnmp_args, "testing_getnext_unknown_oid")
