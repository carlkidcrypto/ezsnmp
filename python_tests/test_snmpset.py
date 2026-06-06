import pytest

from ezsnmp.exceptions import ParseError
from ezsnmp.netsnmp import snmpget, snmpset


def test_string(netsnmp_args, request, reset_values):
    netsnmp_args_1 = netsnmp_args + ["sysLocation.0"]
    res = snmpget(netsnmp_args_1, "testing_value")
    assert res[0].oid == "SNMPv2-MIB::sysLocation"
    assert res[0].index == "0"
    assert res[0].value != "my newer location"
    assert res[0].type == "STRING"

    netsnmp_args_2 = netsnmp_args + ["sysLocation.0", "s", "my newer location"]
    success = snmpset(netsnmp_args_2, "testing_value")
    assert success

    res = snmpget(netsnmp_args_1, "testing_value")
    assert res[0].oid == "SNMPv2-MIB::sysLocation"
    assert res[0].index == "0"
    assert res[0].value == "my newer location"
    assert res[0].type == "STRING"


def test_integer(netsnmp_args, reset_values):
    netsnmp_args_1 = netsnmp_args + ["nsCacheTimeout.1.3.6.1.2.1.2.2", "i", "65"]
    success = snmpset(netsnmp_args_1, "testing_value")
    assert success

    netsnmp_args_2 = netsnmp_args + ["nsCacheTimeout.1.3.6.1.2.1.2.2"]
    res = snmpget(netsnmp_args_2, "testing_value")
    assert res[0].oid == "NET-SNMP-AGENT-MIB::nsCacheTimeout.1.3.6.1.2.1.2"
    assert res[0].index == "2"
    assert res[0].value == "65"
    assert res[0].type == "INTEGER"


def test_invalid_version():
    """Test snmpset raises ParseError for an invalid SNMP version."""
    args = ["-v", "999", "-c", "public", "localhost:11161", "sysLocation.0", "s", "x"]
    with pytest.raises(ParseError):
        snmpset(args, "testing_snmpset_invalid_version")
