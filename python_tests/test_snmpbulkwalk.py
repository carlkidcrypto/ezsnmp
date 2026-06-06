import platform

import pytest

from ezsnmp.exceptions import PacketError, ParseError
from ezsnmp.netsnmp import snmpbulkwalk


def test_regular(netsnmp_args):
    if netsnmp_args[1] == "1":
        with pytest.raises(PacketError):
            netsnmp_args = netsnmp_args + ["system"]
            snmpbulkwalk(netsnmp_args, "testing_value")

    else:
        netsnmp_args = netsnmp_args + ["system"]
        res = snmpbulkwalk(netsnmp_args, "testing_value")
        assert len(res) >= 7

        assert platform.version() in res[0].value
        assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
        assert res[4].value == platform.node()
        assert res[5].value == "my original location"


def test_res(netsnmp_args):
    if netsnmp_args[1] == "1":
        with pytest.raises(PacketError):
            netsnmp_args = netsnmp_args + ["system"]
            snmpbulkwalk(netsnmp_args, "testing_value")
    else:
        netsnmp_args = netsnmp_args + ["system"]
        res = snmpbulkwalk(netsnmp_args, "testing_value")

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


def test_non_sequential_oids(netsnmp_args):
    if platform.system() != "Darwin":
        if netsnmp_args[1] == "1":
            with pytest.raises(PacketError):
                netsnmp_args = netsnmp_args + [
                    "NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24"
                ]
                snmpbulkwalk(netsnmp_args, "testing_value")
        else:
            netsnmp_args = netsnmp_args + [
                "NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24"
            ]
            res = snmpbulkwalk(netsnmp_args, "testing_value")

            assert len(res) == 2

            assert res[0].oid == "NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24"
            assert res[0].type == "INTEGER"
            assert res[0].index == "4"
            # Don't verify the value, this always changes
            # assert res[0].value == "expired(5)"

            assert res[1].oid == "NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24"
            assert res[1].type == "INTEGER"
            assert res[1].index == "7"
            # Don't verify the value, this always changes
            # assert res[1].value == "expired(5)"

    else:
        assert True


def test_separated_cr_raises_parse_error():
    """When -Cr and its number are separate args, ParseError should be raised
    instead of the process being killed by exit(1)."""
    args = ["-v", "2c", "-c", "public", "-Cr", "5", "localhost:11161", "sysORDescr"]
    with pytest.raises(ParseError, match="No number given for -Cr option"):
        snmpbulkwalk(args, "testing_separated_cr")


def test_separated_cn_raises_parse_error():
    """When -Cn and its number are separate args, ParseError should be raised
    instead of the process being killed by exit(1)."""
    args = ["-v", "2c", "-c", "public", "-Cn", "2", "localhost:11161", "sysORDescr"]
    with pytest.raises(ParseError, match="No number given for -Cn option"):
        snmpbulkwalk(args, "testing_separated_cn")
