import platform

import pytest
from ezsnmp import (
    snmpget,
    snmpset,
    snmpbulkget,
    snmpwalk,
    snmpbulkwalk,
)

import faulthandler

faulthandler.enable()

def test_snmp_get_regular(netsnmp_args):
    netsnmp_args = netsnmp_args + ["sysDescr.0"]
    res = snmpget(netsnmp_args)

    assert platform.version() in res[0].value
    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"


def test_snmp_get_fully_qualified(netsnmp_args):
    netsnmp_args = netsnmp_args + [".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0"]
    res = snmpget(netsnmp_args)

    assert platform.version() in res[0].value
    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"


def test_snmp_get_numeric(netsnmp_args):
    netsnmp_args = netsnmp_args + [".1.3.6.1.2.1.1.1.0"]
    res = snmpget(netsnmp_args)

    assert platform.version() in res[0].value
    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"


def test_snmp_get_numeric_no_leading_dot(netsnmp_args):
    netsnmp_args = netsnmp_args + ["1.3.6.1.2.1.1.1.0"]
    res = snmpget(netsnmp_args)

    assert platform.version() in res[0].value
    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"


# def test_snmp_get_unknown(netsnmp_args):
#     with pytest.raises(RuntimeError):
#         netsnmp_args = netsnmp_args + ["sysDescripto.0"]
#         snmpget(netsnmp_args)


# def test_snmp_get_invalid_instance(netsnmp_args):
#     # Sadly, SNMP v1 doesn't distuingish between an invalid instance and an
#     # invalid object ID, instead it excepts with noSuchName
#     if netsnmp_args[1] == 1:
#         with pytest.raises(RuntimeError):
#             netsnmp_args = netsnmp_args + ["sysContact.1"]
#             snmpget(netsnmp_args)
#     else:
#         netsnmp_args = netsnmp_args + ["sysContact.1"]
#         res = snmpget(netsnmp_args)
#         assert res[0].type == "NOSUCHINSTANCE"


# def test_snmp_get_invalid_object(netsnmp_args):
#     if netsnmp_args[1] == 1:
#         with pytest.raises():
#             snmpget("iso", netsnmp_args)
#     else:
#         res = snmpget("iso", netsnmp_args)
#         assert res[0].type == "NOSUCHOBJECT"


def test_snmp_set_string(netsnmp_args, request, reset_values):
    netsnmp_args_1 = netsnmp_args + ["sysLocation.0"]
    res = snmpget(netsnmp_args_1)
    assert res[0].oid == "SNMPv2-MIB::sysLocation"
    assert res[0].index == "0"
    assert res[0].value != "my newer location"
    assert res[0].type == "STRING"

    netsnmp_args_2 = netsnmp_args + ["sysLocation.0", "s", "my newer location"]
    success = snmpset(netsnmp_args_2)
    assert success

    res = snmpget(netsnmp_args_1)
    assert res[0].oid == "SNMPv2-MIB::sysLocation"
    assert res[0].index == "0"
    assert res[0].value == "my newer location"
    assert res[0].type == "STRING"


def test_snmp_set_integer(netsnmp_args, reset_values):
    netsnmp_args_1 = netsnmp_args + ["nsCacheTimeout.1.3.6.1.2.1.2.2", "i", "65"]
    success = snmpset(netsnmp_args_1)
    assert success

    netsnmp_args_2 = netsnmp_args + ["nsCacheTimeout.1.3.6.1.2.1.2.2"]
    res = snmpget(netsnmp_args_2)
    assert res[0].oid == "NET-SNMP-AGENT-MIB::nsCacheTimeout"
    assert res[0].index == "1.3.6.1.2.1.2.2"
    assert res[0].value == "65"
    assert res[0].type == "INTEGER"


# def test_snmpbulkget(netsnmp_args):
#     if netsnmp_args[1] == 1:
#         with pytest.raises():
#             snmpbulkget(
#                 [
#                     "sysUpTime",
#                     "sysORLastChange",
#                     "sysORID",
#                     "sysORDescr",
#                     "sysORUpTime",
#                 ],
#                 2,
#                 8,
#                 netsnmp_args,
#             )
#     else:
#         res = snmpbulkget(
#             ["sysUpTime", "sysORLastChange", "sysORID", "sysORDescr", "sysORUpTime"],
#             2,
#             8,
#             netsnmp_args,
#         )

#         assert len(res) == 26

#         assert res[0].oid == "sysUpTimeInstance"
#         assert res[0].index == ""
#         assert int(res[0].value) > 0
#         assert res[0].type == "TICKS"

#         assert res[4].oid == "sysORUpTime"
#         assert res[4].index == "1"
#         assert int(res[4].value) >= 0
#         assert res[4].type == "TICKS"


# def test_snmpwalk(netsnmp_args):
#     res = snmpwalk("system", netsnmp_args)
#     assert len(res) >= 7

#     assert platform.version() in res[0].value
#     assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
#     assert res[4].value == platform.node()
#     assert res[5].value == "my original location"


# def test_snmp_walk_res(netsnmp_args):
#     res = snmpwalk("system", netsnmp_args)

#     assert len(res) >= 7

#     assert res[0].oid == "SNMPv2-MIB::sysDescr"
#     assert res[0].index == "0"
#     assert platform.version() in res[0].value
#     assert res[0].type == "STRING"

#     assert res[3].oid == "sysContact"
#     assert res[3].index == "0"
#     assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
#     assert res[3].type == "STRING"

#     assert res[4].oid == "sysName"
#     assert res[4].index == "0"
#     assert res[4].value == platform.node()
#     assert res[4].type == "STRING"

#     assert res[5].oid == "SNMPv2-MIB::sysLocation"
#     assert res[5].index == "0"
#     assert res[5].value == "my original location"
#     assert res[5].type == "STRING"


# def test_snmp_bulkwalk_res(netsnmp_args):
#     if netsnmp_args[1] == 1:
#         with pytest.raises():
#             snmpbulkwalk("system", netsnmp_args)
#     else:
#         res = snmpbulkwalk("system", netsnmp_args)

#         assert len(res) >= 7

#         assert res[0].oid == "SNMPv2-MIB::sysDescr"
#         assert res[0].index == "0"
#         assert platform.version() in res[0].value
#         assert res[0].type == "STRING"

#         assert res[3].oid == "sysContact"
#         assert res[3].index == "0"
#         assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
#         assert res[3].type == "STRING"

#         assert res[4].oid == "sysName"
#         assert res[4].index == "0"
#         assert res[4].value == platform.node()
#         assert res[4].type == "STRING"

#         assert res[5].oid == "SNMPv2-MIB::sysLocation"
#         assert res[5].index == "0"
#         assert res[5].value == "my original location"
#         assert res[5].type == "STRING"


# def test_snmp_walk_unknown(netsnmp_args):
#     with pytest.raises():
#         snmpwalk("systemo", netsnmp_args)
