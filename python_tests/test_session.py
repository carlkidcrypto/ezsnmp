import platform
import pytest

from ezsnmp.session import Session
from ezsnmp.exceptions import (
    ConnectionError,
    ParseError,
    TimeoutError,
    PacketError,
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
def test_session_invalid_hostname_and_port_number(version):

    with pytest.raises(ParseError):
        Session(hostname="localhost:162", port_number="163", version=version)


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_hostname_and_port_number_split(version):

    session = Session(hostname="localhost:162", version=version)
    assert session.hostname == "localhost"
    assert session.port_number == "162"


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_invalid_port(version):

    with pytest.raises(TimeoutError):
        session = Session(
            port_number="1234", version=version, timeout="0.2", retries="1"
        )
        session.get("sysContact.0")


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_address(version):

    session = Session(hostname="2001:db8::", version=version)
    assert session.hostname == "2001:db8::"


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_address_and_port_number(version):

    session = Session(
        hostname="fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa",
        port_number="162",
        version=version,
    )
    assert session.hostname == "fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa"
    assert session.port_number == "162"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_address_and_port_number_split(version):

    session = Session(hostname="[2001:db8::]:161", version=version)
    assert session.hostname == "[2001:db8::]"
    assert session.port_number == "161"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_address_with_protocol_and_port_number_split(version):

    session = Session(hostname="udp6:[2001:db8::]:162", version=version)
    assert session.hostname == "udp6:[2001:db8::]"
    assert session.port_number == "162"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_address_with_protocol(version):

    session = Session(hostname="udp6:[2001:db8::]", version=version)
    assert session.hostname == "udp6:[2001:db8::]"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_is_not_ipv6(version):

    with pytest.raises((ConnectionError, GenericError)):
        sess = Session(hostname="[foo::bar]:161", version=version)
        sess.get("sysContact.0")


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_invalid_hostname_and_port_number(version):

    with pytest.raises(ParseError):
        Session(
            hostname="[fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa]:161",
            port_number="162",
            version=version,
        )


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


def test_session_bulk_get(sess):

    if sess.version == "1":
        with pytest.raises(PacketError):
            sess.bulk_get(
                [
                    "sysUpTime",
                    "sysORLastChange",
                    "sysORID",
                    "sysORDescr",
                    "sysORUpTime",
                ],
            )
    else:
        res = sess.bulk_get(
            ["sysUpTime", "sysORLastChange", "sysORID", "sysORDescr", "sysORUpTime"]
        )

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

        del sess


def test_session_get_invalid_instance(sess):

    # Sadly, SNMP v1 doesn't distuingish between an invalid instance and an
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


def test_session_walk(sess):

    res = sess.walk("system")

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

    del sess


def test_session_bulkwalk(sess):

    if sess.version == "1":
        with pytest.raises(PacketError):
            sess.bulk_walk("system")

    else:

        res = sess.bulk_walk(["system"])

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

    del sess


def test_session_walk_all(sess):

    res = sess.walk(".")

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

    del sess


def test_session_update():

    s = Session(version="3")
    assert s.version == "3"

    s.version = "1"
    assert s.version == "1"

    del s


def test_session_repr_masks_community():
    """Test __repr__ includes hostname/version but masks non-empty community."""
    s = Session(hostname="testhost", port_number="161", version="2c", community="public")
    r = repr(s)
    assert "testhost" in r
    assert "2c" in r
    assert "public" not in r
    assert "***" in r
    del s


def test_session_repr_empty_community():
    """Test __repr__ shows empty string when community is not set."""
    s = Session(hostname="testhost", version="3")
    r = repr(s)
    assert "testhost" in r
    assert "***" not in r
    del s


def test_session_str():
    """Test __str__ returns a human-readable representation with host and version."""
    s = Session(hostname="testhost", port_number="161", version="2c")
    text = str(s)
    assert "testhost" in text
    assert "2c" in text
    del s


def test_session_str_default_port():
    """Test __str__ shows 'default' when no port is specified."""
    s = Session(hostname="testhost", version="1")
    text = str(s)
    assert "default" in text
    del s


def test_session_to_dict_required_keys():
    """Test to_dict() contains all required keys."""
    s = Session(version="2c", community="public")
    d = s.to_dict()
    for key in [
        "hostname", "port_number", "version", "community",
        "auth_protocol", "auth_passphrase", "security_engine_id",
        "context_engine_id", "security_level", "context",
        "security_username", "privacy_protocol", "privacy_passphrase",
        "boots_time", "retries", "timeout",
    ]:
        assert key in d, f"Missing key: {key}"
    del s


def test_session_to_dict_community_masked():
    """Test to_dict() masks a non-empty community string with '***'."""
    s = Session(version="2c", community="public")
    d = s.to_dict()
    assert d["community"] == "***"
    del s


def test_session_to_dict_empty_community():
    """Test to_dict() returns empty string for an empty community."""
    s = Session(version="3")
    d = s.to_dict()
    assert d["community"] == ""
    del s


def test_session_to_dict_passphrases_masked():
    """Test to_dict() masks non-empty auth and privacy passphrases."""
    s = Session(
        version="3",
        auth_protocol="MD5",
        auth_passphrase="secret_auth",
        privacy_protocol="AES",
        privacy_passphrase="secret_priv",
        security_level="authPriv",
        security_username="testuser",
    )
    d = s.to_dict()
    assert d["auth_passphrase"] == "***"
    assert d["privacy_passphrase"] == "***"
    del s


def test_session_to_dict_empty_passphrases():
    """Test to_dict() returns empty string when passphrases are not set."""
    s = Session(version="3")
    d = s.to_dict()
    assert d["auth_passphrase"] == ""
    assert d["privacy_passphrase"] == ""
    del s


def test_session_close_marks_closed():
    """Test that explicit close() marks the session as closed."""
    s = Session(version="3")
    assert not s._closed
    s.close()
    assert s._closed
    del s


def test_session_close_idempotent():
    """Test that calling close() multiple times does not raise an error."""
    s = Session(version="3")
    s.close()
    s.close()
    del s


def test_session_context_manager_returns_self():
    """Test that the context manager returns the session itself."""
    with Session(version="3") as s:
        assert isinstance(s, Session)
        assert not s._closed
    assert s._closed


def test_session_context_manager_closes_on_exception():
    """Test that the context manager closes the session even when an exception is raised."""
    s_ref = None
    try:
        with Session(version="3") as s:
            s_ref = s
            raise ValueError("deliberate error")
    except ValueError:
        pass
    assert s_ref is not None
    assert s_ref._closed


def test_session_del_safe_when_closed():
    """Test that __del__ does not raise when session is already closed."""
    s = Session(version="3")
    s.close()
    s.__del__()
    del s


def test_session_del_safe_when_not_closed():
    """Test that __del__ closes the session if not already closed."""
    s = Session(version="3")
    assert not s._closed
    s.__del__()


def test_session_version_2_converts_to_2c():
    """Test that integer version 2 is converted to string '2c'."""
    s = Session(version=2)
    assert s.version == "2c"
    del s


def test_session_property_setters():
    """Test that key property setters update the underlying session state."""
    s = Session(version="3")
    s.retries = "5"
    assert s.retries == "5"
    s.timeout = "10"
    assert s.timeout == "10"
    s.community = "private"
    assert s.community == "private"
    s.auth_protocol = "SHA"
    assert s.auth_protocol == "SHA"
    s.security_username = "newuser"
    assert s.security_username == "newuser"
    del s


def test_session_set_max_repeaters_default():
    """Test that set_max_repeaters_to_num defaults to '10'."""
    s = Session(version="3")
    assert s.set_max_repeaters_to_num == "10"
    del s


def test_session_set_max_repeaters_custom():
    """Test that set_max_repeaters_to_num can be overridden at init time."""
    s = Session(version="3", set_max_repeaters_to_num=25)
    assert s.set_max_repeaters_to_num == "25"
    del s


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
