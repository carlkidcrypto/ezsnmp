import platform
import pytest

from ezsnmp.session import Session
import faulthandler

faulthandler.enable()


def test_session_invalid_snmp_version():
    with pytest.raises(RuntimeError):
        sess = Session(version="4")
        sess.get("sysDescr.0")


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_invalid_hostname(version):
    with pytest.raises(RuntimeError):
        session = Session(hostname="invalid", version=version)
        session.get("sysContact.0")


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_invalid_hostname_and_port_number(version):
    with pytest.raises(RuntimeError):
        Session(hostname="localhost:162", port_number="163", version=version)


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_hostname_and_port_number_split(version):
    session = Session(hostname="localhost:162", version=version)
    assert session.hostname == "localhost"
    assert session.port_number == "162"


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_invalid_port(version):
    with pytest.raises(RuntimeError):
        session = Session(
            port_number="1234", version=version, timeout="0.2", retries="1"
        )
        session.get("sysContact.0")


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_address(version):
    session = Session(hostname="2001:db8::", version=version)
    assert session.hostname == "2001:db8::"


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_address_and_port_number(version):
    session = Session(
        hostname="fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa",
        port_number="162",
        version=version,
    )
    assert session.hostname == "fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa"
    assert session.port_number == "162"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_address_and_port_number_split(version):
    session = Session(hostname="[2001:db8::]:161", version=version)
    assert session.hostname == "[2001:db8::]"
    assert session.port_number == "161"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_address_with_protocol_and_port_number_split(version):
    session = Session(hostname="udp6:[2001:db8::]:162", version=version)
    assert session.hostname == "udp6:[2001:db8::]"
    assert session.port_number == "162"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_address_with_protocol(version):
    session = Session(hostname="udp6:[2001:db8::]", version=version)
    assert session.hostname == "udp6:[2001:db8::]"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_is_not_ipv6(version):
    with pytest.raises(RuntimeError):
        sess = Session(hostname="[foo::bar]:161", version=version)
        sess.get("sysContact.0")


@pytest.mark.parametrize("version", ["1", "2c", "3"])
def test_session_ipv6_invalid_hostname_and_port_number(version):
    with pytest.raises(RuntimeError):
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
    assert res[1].value == '"1234"'
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
    assert res[1].value == '"1234"'
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
    assert res[0].value != "my newer location"

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
        with pytest.raises(RuntimeError):
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
        with pytest.raises(RuntimeError):
            sess.get("sysDescr.100")
    else:
        res = sess.get("sysDescr.100")
        assert res[0].type == "NOSUCHINSTANCE"


def test_session_get_invalid_object(sess):
    if sess.version == "1":
        with pytest.raises(RuntimeError):
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
        with pytest.raises(RuntimeError):
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
