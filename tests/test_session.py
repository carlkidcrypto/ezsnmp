import platform
import re
import pytest

from ezsnmp.session import Session


def test_session_invalid_snmp_version():
    with pytest.raises(ValueError):
        Session(version="4")


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_invalid_hostname(version):
    with pytest.raises(ValueError):
        session = Session(hostname="invalid", version=version)
        session.get("sysContact.0")


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_invalid_hostname_and_remote_port(version):
    with pytest.raises(ValueError):
        Session(hostname="localhost:162", remote_port="163", version=version)


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_hostname_and_remote_port_split(version):
    session = Session(hostname="localhost:162", version=version)
    assert session.hostname == "localhost"
    assert session.remote_port == "162"


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_invalid_port(version):
    with pytest.raises(ValueError):
        session = Session(
            remote_port="1234", version=version, timeout="0.2", retries="1"
        )
        session.get("sysContact.0")


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_address(version):
    session = Session(hostname="2001:db8::", version=version)
    assert session.hostname == "2001:db8::"
    assert session.connect_hostname == "2001:db8::"


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_address_and_remote_port(version):
    session = Session(
        hostname="fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa",
        remote_port="162",
        version=version,
    )
    assert session.hostname == "fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa"
    assert session.remote_port == "162"
    assert session.connect_hostname == "[fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa]:162"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_address_and_remote_port_split(version):
    session = Session(hostname="[2001:db8::]:161", version=version)
    assert session.hostname == "[2001:db8::]"
    assert session.remote_port == "161"
    assert session.connect_hostname == "[2001:db8::]:161"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_address_with_protocol_and_remote_port_split(version):
    session = Session(hostname="udp6:[2001:db8::]:162", version=version)
    assert session.hostname == "udp6:[2001:db8::]"
    assert session.remote_port == "162"
    assert session.connect_hostname == "udp6:[2001:db8::]:162"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_address_with_protocol(version):
    session = Session(hostname="udp6:[2001:db8::]", version=version)
    assert session.hostname == "udp6:[2001:db8::]"
    assert session.connect_hostname == "udp6:[2001:db8::]"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_is_not_ipv6(version):
    with pytest.raises(ValueError):
        Session(hostname="[foo::bar]:161", version=version)


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_invalid_hostname_and_remote_port(version):
    with pytest.raises(ValueError):
        Session(
            hostname="[fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa]:161",
            remote_port="162",
            version=version,
        )


def test_session_set_multiple_next(sess, reset_values):
    # Destroy succeeds even if no row exists
    sess.set(".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116", 6)
    success = sess.set_multiple(
        [
            (".1.3.6.1.6.3.12.1.2.1.2.116.101.115.116", ".1.3.6.1.6.1.1"),
            (".1.3.6.1.6.3.12.1.2.1.3.116.101.115.116", "1234"),
            (".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116", 4),
        ]
    )
    assert success

    res = sess.get_next(
        ["snmpTargetAddrTDomain", "snmpTargetAddrTAddress", "snmpTargetAddrRowStatus"]
    )

    assert res[0].oid == "snmpTargetAddrTDomain"
    assert res[0].index == "116.101.115.116"
    assert res[0].value == ".1.3.6.1.6.1.1"
    assert res[0].type == "OBJECTID"

    assert res[1].oid == "snmpTargetAddrTAddress"
    assert res[1].index == "116.101.115.116"
    assert res[1].value == "1234"
    assert res[1].type == "STRING"

    assert res[2].oid == "snmpTargetAddrRowStatus"
    assert res[2].index == "116.101.115.116"
    assert res[2].value == "3"
    assert res[2].type == "INTEGER"

    del sess


def test_session_set_clear(sess):
    res = sess.set(".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116", 6)
    assert res == 1

    res = sess.get_next(
        ["snmpTargetAddrTDomain", "snmpTargetAddrTAddress", "snmpTargetAddrRowStatus"]
    )

    assert res[0].oid == "snmpUnavailableContexts"
    assert res[0].index == "0"
    assert res[0].value == "0"
    assert res[0].type == "COUNTER"

    assert res[1].oid == "snmpUnavailableContexts"
    assert res[1].index == "0"
    assert res[1].value == "0"
    assert res[1].type == "COUNTER"

    assert res[2].oid == "snmpUnavailableContexts"
    assert res[2].index == "0"
    assert res[2].value == "0"
    assert res[2].type == "COUNTER"

    del sess


def test_session_get(sess):
    for oid in ["sysUpTime.0", "sysContact.0", "sysLocation.0"]:
        res = sess.get(oid)
        if oid == "sysUpTime.0":
            assert res[0].oid == "DISMAN-EVENT-MIB::sysUpTimeInstance"
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


def test_session_get_use_numeric(sess):
    sess.use_numeric = True
    res = sess.get("sysContact.0")

    assert res[0].oid == ".1.3.6.1.2.1.1.4"
    assert res[0].index == "0"
    assert res[0].value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res[0].type == "STRING"

    del sess


def test_session_get_use_sprint_value(sess):
    sess.use_sprint_value = True
    res = sess.get("sysUpTimeInstance")

    assert res[0].oid == "sysUpTimeInstance"
    assert res[0].index == ""
    assert re.match(r"^\d+:\d+:\d+:\d+\.\d+$", res[0].value)
    assert res[0].type == "Timeticks"

    del sess


def test_session_get_use_enums(sess):
    sess.use_enums = True
    res = sess.get("ifAdminStatus.1")

    assert res[0].oid == "ifAdminStatus"
    assert res[0].index == "1"
    assert res[0].value == "up"
    assert res[0].type == "INTEGER"

    del sess


def test_session_get_next(sess):
    res = sess.get_next([("sysUpTime", "0"), ("sysContact", "0"), ("sysLocation", "0")])

    assert res[0].oid == "sysContact"
    assert res[0].index == "0"
    assert res[0].value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res[0].type == "STRING"

    assert res[1].oid == "sysName"
    assert res[1].index == "0"
    assert res[1].value == platform.node()
    assert res[1].type == "STRING"

    assert res[2].oid == "sysORLastChange"
    assert res[2].index == "0"
    assert int(res[2].value) >= 0
    assert res[2].type == "Timeticks"

    del sess


def test_session_set(sess, reset_values):
    res = sess.get(("sysLocation", "0"))
    assert res[0].value != "my newer location"

    success = sess.set(("sysLocation", "0"), "my newer location")
    assert success

    res = sess.get(("sysLocation", "0"))
    assert res[0].value == "my newer location"

    del sess


def test_session_set_multiple(sess, reset_values):
    res = sess.get(["sysLocation.0", "nsCacheTimeout.1.3.6.1.2.1.2.2"])
    assert res[0].value != "my newer location"
    assert res[1].value != "160"

    success = sess.set_multiple(
        [
            ("sysLocation.0", "my newer location"),
            (("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), 160),
        ]
    )
    assert success

    res = sess.get(["sysLocation.0", "nsCacheTimeout.1.3.6.1.2.1.2.2"])
    assert res[0].value == "my newer location"
    assert res[1].value == "160"

    del sess


def test_session_bulk_get(sess):  # noqa
    if sess.version == "1":
        with pytest.raises(ValueError):
            sess.bulk_get(
                [
                    "sysUpTime",
                    "sysORLastChange",
                    "sysORID",
                    "sysORDescr",
                    "sysORUpTime",
                ],
                2,
                8,
            )
    else:
        res = sess.bulk_get(
            ["sysUpTime", "sysORLastChange", "sysORID", "sysORDescr", "sysORUpTime"],
            2,
            8,
        )

        assert res[0].oid == "sysUpTimeInstance"
        assert res[0].index == ""
        assert int(res[0].value) > 0
        assert res[0].type == "Timeticks"

        assert res[4].oid == "sysORUpTime"
        assert res[4].index == "1"
        assert int(res[4].value) >= 0
        assert res[4].type == "Timeticks"

        del sess


def test_session_get_invalid_instance(sess):
    # Sadly, SNMP v1 doesn't distuingish between an invalid instance and an
    # invalid object ID, instead it excepts with noSuchName
    if sess.version == "1":
        with pytest.raises(ValueError):
            sess.get("sysDescr.100")
    else:
        res = sess.get("sysDescr.100")
        assert res[0].type == "NOSUCHINSTANCE"


def test_session_get_invalid_object(sess):
    if sess.version == "1":
        with pytest.raises(ValueError):
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
        # @todo, we need to bubble up those *_perror functions. Right now they print to stderr/stdout.
        # with pytest.raises(EzSNMPError):
        # sess.bulkwalk("system")
        assert 1 == 2
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
