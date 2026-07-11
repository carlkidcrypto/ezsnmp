"""
Network tests for Session.set operations.
"""
import pytest

from ezsnmp.exceptions import PacketError
import faulthandler

faulthandler.enable()


def test_session_set_multiple_next(sess, reset_values):

    res = sess.set([".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116", "i", "6"])
    assert res[0].oid == "SNMP-TARGET-MIB::snmpTargetAddrRowStatus"
    assert res[0].index == "'test'"
    assert res[0].value == "destroy(6)"
    assert res[0].type == "INTEGER"

    res = sess.set(
        [
            ".1.3.6.1.6.3.12.1.2.1.2.116.101.115.116",
            "o",
            ".1.3.6.1.6.1.1",
            ".1.3.6.1.6.3.12.1.2.1.3.116.101.115.116",
            "s",
            "1234",
            ".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116",
            "i",
            "4",
        ]
    )

    assert res[0].oid == "SNMP-TARGET-MIB::snmpTargetAddrTDomain"
    assert res[0].index == "'test'"
    assert res[0].value == "SNMPv2-TM::snmpUDPDomain"
    assert res[0].type == "OID"
    assert res[1].oid == "SNMP-TARGET-MIB::snmpTargetAddrTAddress"
    assert res[1].index == "'test'"
    assert res[1].value == "1234"
    assert res[1].type == "STRING"
    assert res[2].oid == "SNMP-TARGET-MIB::snmpTargetAddrRowStatus"
    assert res[2].index == "'test'"
    assert res[2].value == "createAndGo(4)"
    assert res[2].type == "INTEGER"

    res = sess.get_next(
        ["snmpTargetAddrTDomain", "snmpTargetAddrTAddress", "snmpTargetAddrRowStatus"]
    )

    assert res[0].oid == "SNMP-TARGET-MIB::snmpTargetAddrTDomain"
    assert res[0].index == "'test'"
    assert res[0].value == "SNMPv2-TM::snmpUDPDomain"
    assert res[0].type == "OID"

    assert res[1].oid == "SNMP-TARGET-MIB::snmpTargetAddrTAddress"
    assert res[1].index == "'test'"
    assert res[1].value == "1234"
    assert res[1].type == "STRING"

    assert res[2].oid == "SNMP-TARGET-MIB::snmpTargetAddrRowStatus"
    assert res[2].index == "'test'"
    assert res[2].value == "notReady(3)"
    assert res[2].type == "INTEGER"

    del sess


def test_session_set_clear(sess):

    res = sess.set([".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116", "i", "6"])
    assert res[0].oid == "SNMP-TARGET-MIB::snmpTargetAddrRowStatus"
    assert res[0].index == "'test'"
    assert res[0].value == "destroy(6)"
    assert res[0].type == "INTEGER"

    res = sess.get_next(
        ["snmpTargetAddrTDomain", "snmpTargetAddrTAddress", "snmpTargetAddrRowStatus"]
    )

    assert res[0].oid == "SNMP-TARGET-MIB::snmpUnavailableContexts"
    assert res[0].index == "0"
    assert res[0].value == "0"
    assert res[0].type == "Counter32"

    assert res[1].oid == "SNMP-TARGET-MIB::snmpUnavailableContexts"
    assert res[1].index == "0"
    assert res[1].value == "0"
    assert res[1].type == "Counter32"

    assert res[2].oid == "SNMP-TARGET-MIB::snmpUnavailableContexts"
    assert res[2].index == "0"
    assert res[2].value == "0"
    assert res[2].type == "Counter32"

    del sess


def test_session_set(sess, reset_values):

    res = sess.get("sysLocation.0")
    assert res[0].value == "my original location"

    success = sess.set(["sysLocation.0", "s", "my newer location"])
    assert success

    res = sess.get("sysLocation.0")
    assert res[0].value == "my newer location"

    del sess


def test_session_set_multiple(sess, reset_values):

    res = sess.get(["sysLocation.0", "nsCacheTimeout.1.3.6.1.2.1.2.2"])
    assert res[0].value != "my newer location"
    assert res[1].value != "160"

    success = sess.set(
        [
            "sysLocation.0",
            "s",
            "my newer location",
            "nsCacheTimeout.1.3.6.1.2.1.2.2",
            "i",
            "160",
        ]
    )
    assert success

    res = sess.get(["sysLocation.0", "nsCacheTimeout.1.3.6.1.2.1.2.2"])
    assert res[0].value == "my newer location"
    assert res[1].value == "160"

    del sess


def test_session_set_none_oids(sess):
    """Test that Session.set(None) is treated same as empty list."""
    res = sess.set(None)
    assert res is not None
