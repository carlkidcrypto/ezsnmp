import pytest

from ezsnmp.exceptions import GenericError, ParseError, UndeterminedTypeError
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


def test_missing_object_name(netsnmp_args, capfd):
    """Test snmpset raises GenericError for missing object name without stdio noise."""
    with pytest.raises(GenericError) as exc_info:
        snmpset(netsnmp_args, "testing_snmpset_missing_object")
    assert "Missing object name" in str(exc_info.value)
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_missing_type_and_value(netsnmp_args, capfd):
    """Test snmpset raises GenericError for missing type and value without stdio noise."""
    args = netsnmp_args + ["sysLocation.0"]
    with pytest.raises(GenericError) as exc_info:
        snmpset(args, "testing_snmpset_missing_type_value")
    assert "Needs type and value" in str(exc_info.value)
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_missing_value(netsnmp_args, capfd):
    """Test snmpset raises GenericError for missing value without stdio noise."""
    args = netsnmp_args + ["sysLocation.0", "s"]
    with pytest.raises(GenericError) as exc_info:
        snmpset(args, "testing_snmpset_missing_value")
    assert "Needs value" in str(exc_info.value)
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_bad_object_type(netsnmp_args, capfd):
    """Test snmpset raises UndeterminedTypeError for bad object type without stdio noise."""
    args = netsnmp_args + ["sysLocation.0", "z", "val"]
    with pytest.raises(UndeterminedTypeError) as exc_info:
        snmpset(args, "testing_snmpset_bad_type")
    assert "Bad object type" in str(exc_info.value)
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""
