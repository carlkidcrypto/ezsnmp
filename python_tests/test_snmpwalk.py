import platform

import pytest

from ezsnmp.exceptions import GenericError, ParseError
from ezsnmp.netsnmp import snmpwalk


def test_res(netsnmp_args):
    netsnmp_args = netsnmp_args + ["system"]
    res = snmpwalk(netsnmp_args, "testing_value")

    assert len(res) >= 7

    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert platform.version() in res[0].value
    assert res[0].type == "STRING"

    assert res[3].oid == "SNMPv2-MIB::sysContact"
    assert res[3].index == "0"
    assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res[3].type == "STRING"

    assert res[4].oid == "SNMPv2-MIB::sysName"
    assert res[4].index == "0"
    assert res[4].value == platform.node()
    assert res[4].type == "STRING"

    assert res[5].oid == "SNMPv2-MIB::sysLocation"
    assert res[5].index == "0"
    assert res[5].value == "my original location"
    assert res[5].type == "STRING"


def test_unknown(netsnmp_args):
    with pytest.raises(GenericError):
        netsnmp_args = netsnmp_args + ["systemo123"]
        snmpwalk(netsnmp_args, "testing_value")


def test_invalid_version():
    """Test snmpwalk raises ParseError for an invalid SNMP version."""
    args = ["-v", "999", "-c", "public", "localhost:11161", "system"]
    with pytest.raises(ParseError):
        snmpwalk(args, "testing_snmpwalk_invalid_version")
