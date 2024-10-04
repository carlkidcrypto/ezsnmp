import platform

import pytest
from ezsnmp import (
    snmpget,
    snmpset,
    snmpbulkget,
    snmpwalk,
    snmpbulkwalk,
)


def test_snmp_get_regular(netsnmp_args):
    netsnmp_args = netsnmp_args + ["sysDescr.0"]
    res = snmpget(netsnmp_args)

    assert platform.version() in res[0].value
    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert res[0].snmp_type == "OCTETSTR"


def test_snmp_get_tuple(netsnmp_args):

    netsnmp_args = netsnmp_args + ["sysDescr", "0"]
    res = snmpget(netsnmp_args)

    assert platform.version() in res[0].value
    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert res[0].snmp_type == "OCTETSTR"


def test_snmp_get_fully_qualified(netsnmp_args):
    netsnmp_args = netsnmp_args + [".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0"]
    res = snmpget(netsnmp_args)

    assert platform.version() in res[0].value
    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert res[0].snmp_type == "OCTETSTR"


def test_snmp_get_fully_qualified_tuple(netsnmp_args):
    res = snmpget(
        (".iso.org.dod.internet.mgmt.mib-2.system.sysDescr", "0"), netsnmp_args
    )

    assert platform.version() in res[0].value
    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert res[0].snmp_type == "OCTETSTR"


def test_snmp_get_numeric(netsnmp_args):
    res = snmpget(".1.3.6.1.2.1.1.1.0", netsnmp_args)

    assert platform.version() in res[0].value
    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert res[0].snmp_type == "OCTETSTR"


def test_snmp_get_numeric_no_leading_dot(netsnmp_args):
    res = snmpget("1.3.6.1.2.1.1.1.0", netsnmp_args)

    assert platform.version() in res[0].value
    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert res[0].snmp_type == "OCTETSTR"


def test_snmp_get_numeric_tuple(netsnmp_args):
    res = snmpget((".1.3.6.1.2.1.1.1", "0"), netsnmp_args)

    assert platform.version() in res[0].value
    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert res[0].snmp_type == "OCTETSTR"


def test_snmp_get_unknown(netsnmp_args):
    with pytest.raises():
        snmpget("sysDescripto.0", netsnmp_args)


def test_snmp_get_invalid_instance(netsnmp_args):
    # Sadly, SNMP v1 doesn't distuingish between an invalid instance and an
    # invalid object ID, instead it excepts with noSuchName
    if netsnmp_args["version"] == 1:
        with pytest.raises():
            snmpget("sysContact.1", netsnmp_args)
    else:
        res = snmpget("sysContact.1", netsnmp_args)
        assert res[0].snmp_type == "NOSUCHINSTANCE"


def test_snmp_get_invalid_object(netsnmp_args):
    if netsnmp_args["version"] == 1:
        with pytest.raises():
            snmpget("iso", netsnmp_args)
    else:
        res = snmpget("iso", netsnmp_args)
        assert res[0].snmp_type == "NOSUCHOBJECT"


def test_snmp_set_string(netsnmp_args, request, reset_values):
    res = snmpget(("sysLocation", "0"), netsnmp_args)
    assert res[0].oid == "sysLocation"
    assert res[0].oid_index == "0"
    assert res[0].value != "my newer location"
    assert res[0].snmp_type == "OCTETSTR"

    success = snmpset(("sysLocation", "0"), "my newer location", netsnmp_args)
    assert success

    res = snmpget(("sysLocation", "0"), netsnmp_args)
    assert res[0].oid == "sysLocation"
    assert res[0].oid_index == "0"
    assert res[0].value == "my newer location"
    assert res[0].snmp_type == "OCTETSTR"


def test_snmp_set_string_long_type(netsnmp_args, reset_values):
    res = snmpget(("sysLocation", "0"), netsnmp_args)
    assert res[0].oid == "sysLocation"
    assert res[0].oid_index == "0"
    assert res[0].value != "my newer location"
    assert res[0].snmp_type == "OCTETSTR"

    success = snmpset(
        ("sysLocation", "0"), "my newer location", "OCTETSTR", netsnmp_args
    )
    assert success

    res = snmpget(("sysLocation", "0"), netsnmp_args)
    assert res[0].oid == "sysLocation"
    assert res[0].oid_index == "0"
    assert res[0].value == "my newer location"
    assert res[0].snmp_type == "OCTETSTR"


def test_snmp_set_string_short_type(netsnmp_args, reset_values):
    res = snmpget(("sysLocation", "0"), netsnmp_args)
    assert res[0].oid == "sysLocation"
    assert res[0].oid_index == "0"
    assert res[0].value != "my newer location"
    assert res[0].snmp_type == "OCTETSTR"

    success = snmpset(("sysLocation", "0"), "my newer location", "s", netsnmp_args)
    assert success

    res = snmpget(("sysLocation", "0"), netsnmp_args)
    assert res[0].oid == "sysLocation"
    assert res[0].oid_index == "0"
    assert res[0].value == "my newer location"
    assert res[0].snmp_type == "OCTETSTR"


def test_snmp_set_integer(netsnmp_args, reset_values):
    success = snmpset(("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), 65, netsnmp_args)
    assert success

    res = snmpget(("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), netsnmp_args)
    assert res[0].oid == "nsCacheTimeout"
    assert res[0].oid_index == "1.3.6.1.2.1.2.2"
    assert res[0].value == "65"
    assert res[0].snmp_type == "INTEGER"


def test_snmp_set_integer_long_type(netsnmp_args, reset_values):
    success = snmpset(
        ("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), 65, "INTEGER", netsnmp_args
    )
    assert success

    res = snmpget(("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), netsnmp_args)
    assert res[0].oid == "nsCacheTimeout"
    assert res[0].oid_index == "1.3.6.1.2.1.2.2"
    assert res[0].value == "65"
    assert res[0].snmp_type == "INTEGER"


def test_snmp_set_integer_short_type(netsnmp_args, reset_values):
    success = snmpset(("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), 65, "i", netsnmp_args)
    assert success

    res = snmpget(("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), netsnmp_args)
    assert res[0].oid == "nsCacheTimeout"
    assert res[0].oid_index == "1.3.6.1.2.1.2.2"
    assert res[0].value == "65"
    assert res[0].snmp_type == "INTEGER"


def test_snmpbulkget(netsnmp_args):
    if netsnmp_args["version"] == 1:
        with pytest.raises():
            snmpbulkget(
                [
                    "sysUpTime",
                    "sysORLastChange",
                    "sysORID",
                    "sysORDescr",
                    "sysORUpTime",
                ],
                2,
                8,
                netsnmp_args
            )
    else:
        res = snmpbulkget(
            ["sysUpTime", "sysORLastChange", "sysORID", "sysORDescr", "sysORUpTime"],
            2,
            8,
            netsnmp_args
        )

        assert len(res) == 26

        assert res[0].oid == "sysUpTimeInstance"
        assert res[0].oid_index == ""
        assert int(res[0].value) > 0
        assert res[0].snmp_type == "TICKS"

        assert res[4].oid == "sysORUpTime"
        assert res[4].oid_index == "1"
        assert int(res[4].value) >= 0
        assert res[4].snmp_type == "TICKS"


def test_snmpwalk(netsnmp_args):
    res = snmpwalk("system", netsnmp_args)
    assert len(res) >= 7

    assert platform.version() in res[0].value
    assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res[4].value == platform.node()
    assert res[5].value == "my original location"


def test_snmp_walk_res(netsnmp_args):
    res = snmpwalk("system", netsnmp_args)

    assert len(res) >= 7

    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert platform.version() in res[0].value
    assert res[0].snmp_type == "OCTETSTR"

    assert res[3].oid == "sysContact"
    assert res[3].oid_index == "0"
    assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res[3].snmp_type == "OCTETSTR"

    assert res[4].oid == "sysName"
    assert res[4].oid_index == "0"
    assert res[4].value == platform.node()
    assert res[4].snmp_type == "OCTETSTR"

    assert res[5].oid == "sysLocation"
    assert res[5].oid_index == "0"
    assert res[5].value == "my original location"
    assert res[5].snmp_type == "OCTETSTR"


def test_snmp_bulkwalk_res(netsnmp_args):
    if netsnmp_args["version"] == 1:
        with pytest.raises():
            snmpbulkwalk("system", netsnmp_args)
    else:
        res = snmpbulkwalk("system", netsnmp_args)

        assert len(res) >= 7

        assert res[0].oid == "sysDescr"
        assert res[0].oid_index == "0"
        assert platform.version() in res[0].value
        assert res[0].snmp_type == "OCTETSTR"

        assert res[3].oid == "sysContact"
        assert res[3].oid_index == "0"
        assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
        assert res[3].snmp_type == "OCTETSTR"

        assert res[4].oid == "sysName"
        assert res[4].oid_index == "0"
        assert res[4].value == platform.node()
        assert res[4].snmp_type == "OCTETSTR"

        assert res[5].oid == "sysLocation"
        assert res[5].oid_index == "0"
        assert res[5].value == "my original location"
        assert res[5].snmp_type == "OCTETSTR"


def test_snmp_walk_unknown(netsnmp_args):
    with pytest.raises():
        snmpwalk("systemo", netsnmp_args)
