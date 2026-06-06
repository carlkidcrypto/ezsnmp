import pytest

from ezsnmp.exceptions import PacketError, ParseError
from ezsnmp.netsnmp import snmpbulkget


def test_regular(netsnmp_args):
    if netsnmp_args[1] == "1":
        with pytest.raises(PacketError):
            netsnmp_args = netsnmp_args + [
                "sysUpTime",
                "sysORLastChange",
                "sysORID",
                "sysORDescr",
                "sysORUpTime",
            ]
            snmpbulkget(netsnmp_args, "testing_value")
    else:
        netsnmp_args = netsnmp_args + [
            "sysUpTime",
            "sysORLastChange",
            "sysORID",
            "sysORDescr",
            "sysORUpTime",
        ]
        res = snmpbulkget(netsnmp_args, "testing_value")

        assert len(res) == 50

        # Checking if "sysUpTimeInstance" is in "oid" is enough. The preamble
        # changes per OS system
        # "DISMAN-EVENT-MIB::sysUpTimeInstance" MacOS
        # "DISMAN-EXPRESSION-MIB::sysUpTimeInstance" Linux
        assert "sysUpTimeInstance" in res[0].oid
        assert res[0].index == ""
        assert res[0].type == "Timeticks"

        assert res[4].oid == "SNMPv2-MIB::sysORUpTime"
        assert res[4].index == "1"
        assert res[4].type == "Timeticks"


# Issue #655: separated -Cr/-Cn args should raise ParseError, not crash
def test_separated_cr_raises_parse_error():
    """When -Cr and its number are separate args, ParseError should be raised
    instead of the process being killed by exit(1)."""
    args = ["-v", "2c", "-c", "public", "-Cr", "1", "localhost:11161", "sysORDescr"]
    with pytest.raises(ParseError, match="No number given for -Cr option"):
        snmpbulkget(args, "testing_separated_cr")


def test_separated_cn_raises_parse_error():
    """When -Cn and its number are separate args, ParseError should be raised
    instead of the process being killed by exit(1)."""
    args = [
        "-v",
        "2c",
        "-c",
        "public",
        "-Cn",
        "1",
        "localhost:11161",
        "sysDescr.0",
        "sysORDescr",
    ]
    with pytest.raises(ParseError, match="No number given for -Cn option"):
        snmpbulkget(args, "testing_separated_cn")
