"""
Network tests for Session.get and Session.get_next operations.
Also covers validation tests that exercise the get path (invalid version,
invalid hostname, invalid port, invalid IPv6).
"""

import platform

import pytest

from ezsnmp.session import Session
from ezsnmp.exceptions import (
    ConnectionError,
    PacketError,
    ParseError,
    TimeoutError,
    GenericError,
)
import faulthandler

faulthandler.enable()


def test_session_invalid_snmp_version():

    with pytest.raises(ParseError):
        sess = Session(version="4")
        sess.get("sysDescr.0")


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_invalid_hostname(version):

    with pytest.raises((ConnectionError, GenericError)):
        session = Session(hostname="invalid", version=version)
        session.get("sysContact.0")


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_invalid_port(version):

    with pytest.raises(TimeoutError):
        session = Session(
            port_number="1234", version=version, timeout="0.2", retries="1"
        )
        session.get("sysContact.0")


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_is_not_ipv6(version):

    with pytest.raises((ConnectionError, GenericError)):
        sess = Session(hostname="[foo::bar]:161", version=version)
        sess.get("sysContact.0")


def test_session_get(sess):

    for oid in ["sysUpTime.0", "sysContact.0", "sysLocation.0"]:
        res = sess.get(oid)
        if oid == "sysUpTime.0":
            # Checking if "sysUpTimeInstance" is in "oid" is enough. The preamble
            # changes per OS system
            # "DISMAN-EVENT-MIB::sysUpTimeInstance" MacOS
            # "DISMAN-EXPRESSION-MIB::sysUpTimeInstance" Linux
            assert "sysUpTimeInstance" in res[0].oid
            assert res[0].index == ""
            assert res[0].type == "Timeticks"

        elif oid == "sysContact.0":
            assert res[0].oid == "SNMPv2-MIB::sysContact"
            assert res[0].index == "0"
            assert res[0].value == "G. S. Marzot <gmarzot@marzot.net>"
            assert res[0].type == "STRING"
        elif oid == "sysLocation.0":
            assert res[0].oid == "SNMPv2-MIB::sysLocation"
            assert res[0].index == "0"
            assert res[0].value == "my original location"
            assert res[0].type == "STRING"

    del sess


def test_session_get_next(sess):

    res = sess.get_next(["sysUpTime.0", "sysContact.0", "sysLocation.0"])

    assert res[0].oid == "SNMPv2-MIB::sysContact"
    assert res[0].index == "0"
    assert res[0].value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res[0].type == "STRING"

    assert res[1].oid == "SNMPv2-MIB::sysName"
    assert res[1].index == "0"
    assert res[1].value == platform.node()
    assert res[1].type == "STRING"

    assert res[2].oid == "SNMPv2-MIB::sysORLastChange"
    assert res[2].index == "0"
    assert res[2].type == "Timeticks"

    del sess


def test_session_get_next_single_oid_string(sess):
    try:
        res = sess.get_next(".1.3.6.1.2.1.1.5.0")
    except TimeoutError:
        pytest.skip("SNMP agent is not reachable in this environment")

    assert len(res) == 1
    assert res[0].oid
    assert res[0].type


def test_session_get_next_single_oid_string_with_module_prefix(sess):
    try:
        res = sess.get_next("IF-MIB::ifDescr")
    except TimeoutError:
        pytest.skip("SNMP agent is not reachable in this environment")
    except GenericError as e:
        if "Unknown Object Identifier" in str(e):
            pytest.skip("IF-MIB is not available in this test environment")
        raise

    assert len(res) == 1
    assert res[0].oid
    assert res[0].type


def test_session_get_invalid_instance(sess):

    # Sadly, SNMP v1 doesn't distinguish between an invalid instance and an
    # invalid object ID, instead it excepts with noSuchName
    if sess.version == "1":
        with pytest.raises(PacketError):
            sess.get("sysDescr.100")
    else:
        res = sess.get("sysDescr.100")
        assert res[0].type in ["NOSUCHINSTANCE", "NOSUCHOBJECT"]


def test_session_get_invalid_object(sess):

    if sess.version == "1":
        with pytest.raises(PacketError):
            sess.get("iso")
    else:
        res = sess.get("iso")
        assert res[0].type == "NOSUCHOBJECT"


def test_session_get_none_oids(sess):
    """Test that Session.get(None) returns an empty tuple (None->[] early-return)."""
    res = sess.get(None)
    assert res == ()


def test_session_get_next_none_oids(sess):
    """Test that Session.get_next(None) returns an empty tuple (None->[] early-return)."""
    res = sess.get_next(None)
    assert res == ()


def test_string_values_no_surrounding_quotes(sess):
    """
    Test for issue #355: String values should not be enclosed in quotes.

    Some net-snmp versions/configurations return string values with surrounding
    quotes like '"LEDI Network TS"' instead of 'LEDI Network TS'. The C++ code
    in helpers.cpp strips these surrounding quotes.
    """
    # Test sysContact which is a STRING type
    res = sess.get("sysContact.0")
    assert res[0].type == "STRING"
    # Value should NOT start or end with a quote
    assert not res[0].value.startswith(
        '"'
    ), f"Value should not start with quote: {res[0].value}"
    assert not res[0].value.endswith(
        '"'
    ), f"Value should not end with quote: {res[0].value}"

    # Test sysLocation which is also a STRING type
    res = sess.get("sysLocation.0")
    assert res[0].type == "STRING"
    assert not res[0].value.startswith(
        '"'
    ), f"Value should not start with quote: {res[0].value}"
    assert not res[0].value.endswith(
        '"'
    ), f"Value should not end with quote: {res[0].value}"

    del sess
