import platform
import unittest
from unittest_fixtures import BaseTestCase

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


class TestSessionInvalidVersion(unittest.TestCase):
    def test_session_invalid_snmp_version(self):
        with self.assertRaises(ParseError):
            sess = Session(version="4")
            sess.get("sysDescr.0")


class TestSessionInvalidHostname(unittest.TestCase):
    def test_session_invalid_hostname_v1(self):
        with self.assertRaises((ConnectionError, GenericError)):
            session = Session(hostname="invalid", version="1")
            session.get("sysContact.0")

    def test_session_invalid_hostname_v2c(self):
        with self.assertRaises((ConnectionError, GenericError)):
            session = Session(hostname="invalid", version="2c")
            session.get("sysContact.0")

    def test_session_invalid_hostname_v3(self):
        with self.assertRaises((ConnectionError, GenericError)):
            session = Session(hostname="invalid", version="3")
            session.get("sysContact.0")

    def test_session_invalid_hostname_v1_int(self):
        with self.assertRaises((ConnectionError, GenericError)):
            session = Session(hostname="invalid", version=1)
            session.get("sysContact.0")

    def test_session_invalid_hostname_v2_int(self):
        with self.assertRaises((ConnectionError, GenericError)):
            session = Session(hostname="invalid", version=2)
            session.get("sysContact.0")

    def test_session_invalid_hostname_v3_int(self):
        with self.assertRaises((ConnectionError, GenericError)):
            session = Session(hostname="invalid", version=3)
            session.get("sysContact.0")


class TestSessionHostnameAndPortParsing(unittest.TestCase):
    def test_session_invalid_hostname_and_port_number_v1(self):
        with self.assertRaises(ParseError):
            Session(hostname="localhost:162", port_number="163", version="1")

    def test_session_invalid_hostname_and_port_number_v2c(self):
        with self.assertRaises(ParseError):
            Session(hostname="localhost:162", port_number="163", version="2c")

    def test_session_invalid_hostname_and_port_number_v3(self):
        with self.assertRaises(ParseError):
            Session(hostname="localhost:162", port_number="163", version="3")

    def test_session_invalid_hostname_and_port_number_v1_int(self):
        with self.assertRaises(ParseError):
            Session(hostname="localhost:162", port_number="163", version=1)

    def test_session_invalid_hostname_and_port_number_v2_int(self):
        with self.assertRaises(ParseError):
            Session(hostname="localhost:162", port_number="163", version=2)

    def test_session_invalid_hostname_and_port_number_v3_int(self):
        with self.assertRaises(ParseError):
            Session(hostname="localhost:162", port_number="163", version=3)

    def test_session_hostname_and_port_number_split_v1(self):
        session = Session(hostname="localhost:162", version="1")
        self.assertEqual(session.hostname, "localhost")
        self.assertEqual(session.port_number, "162")

    def test_session_hostname_and_port_number_split_v2c(self):
        session = Session(hostname="localhost:162", version="2c")
        self.assertEqual(session.hostname, "localhost")
        self.assertEqual(session.port_number, "162")

    def test_session_hostname_and_port_number_split_v3(self):
        session = Session(hostname="localhost:162", version="3")
        self.assertEqual(session.hostname, "localhost")
        self.assertEqual(session.port_number, "162")

    def test_session_hostname_and_port_number_split_v1_int(self):
        session = Session(hostname="localhost:162", version=1)
        self.assertEqual(session.hostname, "localhost")
        self.assertEqual(session.port_number, "162")

    def test_session_hostname_and_port_number_split_v2_int(self):
        session = Session(hostname="localhost:162", version=2)
        self.assertEqual(session.hostname, "localhost")
        self.assertEqual(session.port_number, "162")

    def test_session_hostname_and_port_number_split_v3_int(self):
        session = Session(hostname="localhost:162", version=3)
        self.assertEqual(session.hostname, "localhost")
        self.assertEqual(session.port_number, "162")


class TestSessionInvalidPort(unittest.TestCase):
    def test_session_invalid_port_v1(self):
        with self.assertRaises(TimeoutError):
            session = Session(
                port_number="1234", version="1", timeout="0.2", retries="1"
            )
            session.get("sysContact.0")

    def test_session_invalid_port_v2c(self):
        with self.assertRaises(TimeoutError):
            session = Session(
                port_number="1234", version="2c", timeout="0.2", retries="1"
            )
            session.get("sysContact.0")

    def test_session_invalid_port_v3(self):
        with self.assertRaises(TimeoutError):
            session = Session(
                port_number="1234", version="3", timeout="0.2", retries="1"
            )
            session.get("sysContact.0")

    def test_session_invalid_port_v1_int(self):
        with self.assertRaises(TimeoutError):
            session = Session(
                port_number="1234", version=1, timeout="0.2", retries="1"
            )
            session.get("sysContact.0")

    def test_session_invalid_port_v2_int(self):
        with self.assertRaises(TimeoutError):
            session = Session(
                port_number="1234", version=2, timeout="0.2", retries="1"
            )
            session.get("sysContact.0")

    def test_session_invalid_port_v3_int(self):
        with self.assertRaises(TimeoutError):
            session = Session(
                port_number="1234", version=3, timeout="0.2", retries="1"
            )
            session.get("sysContact.0")


class TestSessionIPv6(unittest.TestCase):
    def test_session_ipv6_address_v1(self):
        session = Session(hostname="2001:db8::", version="1")
        self.assertEqual(session.hostname, "2001:db8::")

    def test_session_ipv6_address_v2c(self):
        session = Session(hostname="2001:db8::", version="2c")
        self.assertEqual(session.hostname, "2001:db8::")

    def test_session_ipv6_address_v3(self):
        session = Session(hostname="2001:db8::", version="3")
        self.assertEqual(session.hostname, "2001:db8::")

    def test_session_ipv6_address_v1_int(self):
        session = Session(hostname="2001:db8::", version=1)
        self.assertEqual(session.hostname, "2001:db8::")

    def test_session_ipv6_address_v2_int(self):
        session = Session(hostname="2001:db8::", version=2)
        self.assertEqual(session.hostname, "2001:db8::")

    def test_session_ipv6_address_v3_int(self):
        session = Session(hostname="2001:db8::", version=3)
        self.assertEqual(session.hostname, "2001:db8::")

    def test_session_ipv6_address_and_port_number_v1(self):
        session = Session(
            hostname="fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa",
            port_number="162",
            version="1",
        )
        self.assertEqual(session.hostname, "fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_and_port_number_v2c(self):
        session = Session(
            hostname="fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa",
            port_number="162",
            version="2c",
        )
        self.assertEqual(session.hostname, "fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_and_port_number_v3(self):
        session = Session(
            hostname="fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa",
            port_number="162",
            version="3",
        )
        self.assertEqual(session.hostname, "fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_and_port_number_v1_int(self):
        session = Session(
            hostname="fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa",
            port_number="162",
            version=1,
        )
        self.assertEqual(session.hostname, "fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_and_port_number_v2_int(self):
        session = Session(
            hostname="fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa",
            port_number="162",
            version=2,
        )
        self.assertEqual(session.hostname, "fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_and_port_number_v3_int(self):
        session = Session(
            hostname="fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa",
            port_number="162",
            version=3,
        )
        self.assertEqual(session.hostname, "fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_and_port_number_split_v1(self):
        session = Session(hostname="[2001:db8::]:161", version="1")
        self.assertEqual(session.hostname, "[2001:db8::]")
        self.assertEqual(session.port_number, "161")
        del session

    def test_session_ipv6_address_and_port_number_split_v2c(self):
        session = Session(hostname="[2001:db8::]:161", version="2c")
        self.assertEqual(session.hostname, "[2001:db8::]")
        self.assertEqual(session.port_number, "161")
        del session

    def test_session_ipv6_address_and_port_number_split_v3(self):
        session = Session(hostname="[2001:db8::]:161", version="3")
        self.assertEqual(session.hostname, "[2001:db8::]")
        self.assertEqual(session.port_number, "161")
        del session

    def test_session_ipv6_address_and_port_number_split_v1_int(self):
        session = Session(hostname="[2001:db8::]:161", version=1)
        self.assertEqual(session.hostname, "[2001:db8::]")
        self.assertEqual(session.port_number, "161")
        del session

    def test_session_ipv6_address_and_port_number_split_v2_int(self):
        session = Session(hostname="[2001:db8::]:161", version=2)
        self.assertEqual(session.hostname, "[2001:db8::]")
        self.assertEqual(session.port_number, "161")
        del session

    def test_session_ipv6_address_and_port_number_split_v3_int(self):
        session = Session(hostname="[2001:db8::]:161", version=3)
        self.assertEqual(session.hostname, "[2001:db8::]")
        self.assertEqual(session.port_number, "161")
        del session

    def test_session_ipv6_address_with_protocol_and_port_number_split_v1(self):
        session = Session(hostname="udp6:[2001:db8::]:162", version="1")
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_with_protocol_and_port_number_split_v2c(self):
        session = Session(hostname="udp6:[2001:db8::]:162", version="2c")
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_with_protocol_and_port_number_split_v3(self):
        session = Session(hostname="udp6:[2001:db8::]:162", version="3")
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_with_protocol_and_port_number_split_v1_int(self):
        session = Session(hostname="udp6:[2001:db8::]:162", version=1)
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_with_protocol_and_port_number_split_v2_int(self):
        session = Session(hostname="udp6:[2001:db8::]:162", version=2)
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_with_protocol_and_port_number_split_v3_int(self):
        session = Session(hostname="udp6:[2001:db8::]:162", version=3)
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        self.assertEqual(session.port_number, "162")
        del session

    def test_session_ipv6_address_with_protocol_v1(self):
        session = Session(hostname="udp6:[2001:db8::]", version="1")
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        del session

    def test_session_ipv6_address_with_protocol_v2c(self):
        session = Session(hostname="udp6:[2001:db8::]", version="2c")
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        del session

    def test_session_ipv6_address_with_protocol_v3(self):
        session = Session(hostname="udp6:[2001:db8::]", version="3")
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        del session

    def test_session_ipv6_address_with_protocol_v1_int(self):
        session = Session(hostname="udp6:[2001:db8::]", version=1)
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        del session

    def test_session_ipv6_address_with_protocol_v2_int(self):
        session = Session(hostname="udp6:[2001:db8::]", version=2)
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        del session

    def test_session_ipv6_address_with_protocol_v3_int(self):
        session = Session(hostname="udp6:[2001:db8::]", version=3)
        self.assertEqual(session.hostname, "udp6:[2001:db8::]")
        del session

    def test_session_ipv6_is_not_ipv6_v1(self):
        with self.assertRaises((ConnectionError, GenericError)):
            sess = Session(hostname="[foo::bar]:161", version="1")
            sess.get("sysContact.0")

    def test_session_ipv6_is_not_ipv6_v2c(self):
        with self.assertRaises((ConnectionError, GenericError)):
            sess = Session(hostname="[foo::bar]:161", version="2c")
            sess.get("sysContact.0")

    def test_session_ipv6_is_not_ipv6_v3(self):
        with self.assertRaises((ConnectionError, GenericError)):
            sess = Session(hostname="[foo::bar]:161", version="3")
            sess.get("sysContact.0")

    def test_session_ipv6_is_not_ipv6_v1_int(self):
        with self.assertRaises((ConnectionError, GenericError)):
            sess = Session(hostname="[foo::bar]:161", version=1)
            sess.get("sysContact.0")

    def test_session_ipv6_is_not_ipv6_v2_int(self):
        with self.assertRaises((ConnectionError, GenericError)):
            sess = Session(hostname="[foo::bar]:161", version=2)
            sess.get("sysContact.0")

    def test_session_ipv6_is_not_ipv6_v3_int(self):
        with self.assertRaises((ConnectionError, GenericError)):
            sess = Session(hostname="[foo::bar]:161", version=3)
            sess.get("sysContact.0")

    def test_session_ipv6_invalid_hostname_and_port_number_v1(self):
        with self.assertRaises(ParseError):
            Session(
                hostname="[fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa]:161",
                port_number="162",
                version="1",
            )

    def test_session_ipv6_invalid_hostname_and_port_number_v2c(self):
        with self.assertRaises(ParseError):
            Session(
                hostname="[fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa]:161",
                port_number="162",
                version="2c",
            )

    def test_session_ipv6_invalid_hostname_and_port_number_v3(self):
        with self.assertRaises(ParseError):
            Session(
                hostname="[fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa]:161",
                port_number="162",
                version="3",
            )

    def test_session_ipv6_invalid_hostname_and_port_number_v1_int(self):
        with self.assertRaises(ParseError):
            Session(
                hostname="[fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa]:161",
                port_number="162",
                version=1,
            )

    def test_session_ipv6_invalid_hostname_and_port_number_v2_int(self):
        with self.assertRaises(ParseError):
            Session(
                hostname="[fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa]:161",
                port_number="162",
                version=2,
            )

    def test_session_ipv6_invalid_hostname_and_port_number_v3_int(self):
        with self.assertRaises(ParseError):
            Session(
                hostname="[fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa]:161",
                port_number="162",
                version=3,
            )


class TestSessionWithMultipleConfigurations(BaseTestCase):
    def _test_with_sess(self, sess):
        res = sess.set([".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116", "i", "6"])
        self.assertEqual(res[0].oid, "SNMP-TARGET-MIB::snmpTargetAddrRowStatus")
        self.assertEqual(res[0].index, "'test'")
        self.assertEqual(res[0].value, "destroy(6)")
        self.assertEqual(res[0].type, "INTEGER")

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

        self.assertEqual(res[0].oid, "SNMP-TARGET-MIB::snmpTargetAddrTDomain")
        self.assertEqual(res[0].index, "'test'")
        self.assertEqual(res[0].value, "SNMPv2-TM::snmpUDPDomain")
        self.assertEqual(res[0].type, "OID")
        self.assertEqual(res[1].oid, "SNMP-TARGET-MIB::snmpTargetAddrTAddress")
        self.assertEqual(res[1].index, "'test'")
        self.assertEqual(res[1].value, '"1234"')
        self.assertEqual(res[1].type, "STRING")
        self.assertEqual(res[2].oid, "SNMP-TARGET-MIB::snmpTargetAddrRowStatus")
        self.assertEqual(res[2].index, "'test'")
        self.assertEqual(res[2].value, "createAndGo(4)")
        self.assertEqual(res[2].type, "INTEGER")

        res = sess.get_next(
            ["snmpTargetAddrTDomain", "snmpTargetAddrTAddress", "snmpTargetAddrRowStatus"]
        )

        self.assertEqual(res[0].oid, "SNMP-TARGET-MIB::snmpTargetAddrTDomain")
        self.assertEqual(res[0].index, "'test'")
        self.assertEqual(res[0].value, "SNMPv2-TM::snmpUDPDomain")
        self.assertEqual(res[0].type, "OID")

        self.assertEqual(res[1].oid, "SNMP-TARGET-MIB::snmpTargetAddrTAddress")
        self.assertEqual(res[1].index, "'test'")
        self.assertEqual(res[1].value, '"1234"')
        self.assertEqual(res[1].type, "STRING")

        self.assertEqual(res[2].oid, "SNMP-TARGET-MIB::snmpTargetAddrRowStatus")
        self.assertEqual(res[2].index, "'test'")
        self.assertEqual(res[2].value, "notReady(3)")
        self.assertEqual(res[2].type, "INTEGER")

    def test_session_set_multiple_next_v1(self):
        sess = Session(**self.sess_params[0])
        self.addCleanup(self.reset_snmp_values)
        self._test_with_sess(sess)
        del sess

    def test_session_set_multiple_next_v2(self):
        sess = Session(**self.sess_params[1])
        self.addCleanup(self.reset_snmp_values)
        self._test_with_sess(sess)
        del sess

    def test_session_set_multiple_next_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self.addCleanup(self.reset_snmp_values)
            self._test_with_sess(sess)
            del sess

    def test_session_set_multiple_next_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self.addCleanup(self.reset_snmp_values)
            self._test_with_sess(sess)
            del sess

    def test_session_set_multiple_next_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self.addCleanup(self.reset_snmp_values)
            self._test_with_sess(sess)
            del sess

    def _test_set_clear(self, sess):
        res = sess.set([".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116", "i", "6"])
        self.assertEqual(res[0].oid, "SNMP-TARGET-MIB::snmpTargetAddrRowStatus")
        self.assertEqual(res[0].index, "'test'")
        self.assertEqual(res[0].value, "destroy(6)")
        self.assertEqual(res[0].type, "INTEGER")

        res = sess.get_next(
            ["snmpTargetAddrTDomain", "snmpTargetAddrTAddress", "snmpTargetAddrRowStatus"]
        )

        self.assertEqual(res[0].oid, "SNMP-TARGET-MIB::snmpUnavailableContexts")
        self.assertEqual(res[0].index, "0")
        self.assertEqual(res[0].value, "0")
        self.assertEqual(res[0].type, "Counter32")

        self.assertEqual(res[1].oid, "SNMP-TARGET-MIB::snmpUnavailableContexts")
        self.assertEqual(res[1].index, "0")
        self.assertEqual(res[1].value, "0")
        self.assertEqual(res[1].type, "Counter32")

        self.assertEqual(res[2].oid, "SNMP-TARGET-MIB::snmpUnavailableContexts")
        self.assertEqual(res[2].index, "0")
        self.assertEqual(res[2].value, "0")
        self.assertEqual(res[2].type, "Counter32")

    def test_session_set_clear_v1(self):
        sess = Session(**self.sess_params[0])
        self._test_set_clear(sess)
        del sess

    def test_session_set_clear_v2(self):
        sess = Session(**self.sess_params[1])
        self._test_set_clear(sess)
        del sess

    def test_session_set_clear_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self._test_set_clear(sess)
            del sess

    def test_session_set_clear_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self._test_set_clear(sess)
            del sess

    def test_session_set_clear_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self._test_set_clear(sess)
            del sess

    def _test_session_get(self, sess):
        for oid in ["sysUpTime.0", "sysContact.0", "sysLocation.0"]:
            res = sess.get(oid)
            if oid == "sysUpTime.0":
                self.assertIn("sysUpTimeInstance", res[0].oid)
                self.assertEqual(res[0].index, "")
                self.assertEqual(res[0].type, "Timeticks")
            elif oid == "sysContact.0":
                self.assertEqual(res[0].oid, "SNMPv2-MIB::sysContact")
                self.assertEqual(res[0].index, "0")
                self.assertEqual(res[0].value, "G. S. Marzot <gmarzot@marzot.net>")
                self.assertEqual(res[0].type, "STRING")
            elif oid == "sysLocation.0":
                self.assertEqual(res[0].oid, "SNMPv2-MIB::sysLocation")
                self.assertEqual(res[0].index, "0")
                self.assertEqual(res[0].value, "my original location")
                self.assertEqual(res[0].type, "STRING")

    def test_session_get_v1(self):
        sess = Session(**self.sess_params[0])
        self._test_session_get(sess)
        del sess

    def test_session_get_v2(self):
        sess = Session(**self.sess_params[1])
        self._test_session_get(sess)
        del sess

    def test_session_get_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self._test_session_get(sess)
            del sess

    def test_session_get_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self._test_session_get(sess)
            del sess

    def test_session_get_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self._test_session_get(sess)
            del sess

    def _test_session_get_next(self, sess):
        res = sess.get_next(["sysUpTime.0", "sysContact.0", "sysLocation.0"])

        self.assertEqual(res[0].oid, "SNMPv2-MIB::sysContact")
        self.assertEqual(res[0].index, "0")
        self.assertEqual(res[0].value, "G. S. Marzot <gmarzot@marzot.net>")
        self.assertEqual(res[0].type, "STRING")

        self.assertEqual(res[1].oid, "SNMPv2-MIB::sysName")
        self.assertEqual(res[1].index, "0")
        self.assertEqual(res[1].value, platform.node())
        self.assertEqual(res[1].type, "STRING")

        self.assertEqual(res[2].oid, "SNMPv2-MIB::sysORLastChange")
        self.assertEqual(res[2].index, "0")
        self.assertEqual(res[2].type, "Timeticks")

    def test_session_get_next_v1(self):
        sess = Session(**self.sess_params[0])
        self._test_session_get_next(sess)
        del sess

    def test_session_get_next_v2(self):
        sess = Session(**self.sess_params[1])
        self._test_session_get_next(sess)
        del sess

    def test_session_get_next_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self._test_session_get_next(sess)
            del sess

    def test_session_get_next_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self._test_session_get_next(sess)
            del sess

    def test_session_get_next_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self._test_session_get_next(sess)
            del sess

    def _test_session_set(self, sess):
        res = sess.get("sysLocation.0")
        self.assertEqual(res[0].value, "my original location")

        success = sess.set(["sysLocation.0", "s", "my newer location"])
        self.assertTrue(success)

        res = sess.get("sysLocation.0")
        self.assertEqual(res[0].value, "my newer location")

    def test_session_set_v1(self):
        sess = Session(**self.sess_params[0])
        self.addCleanup(self.reset_snmp_values)
        self._test_session_set(sess)
        del sess

    def test_session_set_v2(self):
        sess = Session(**self.sess_params[1])
        self.addCleanup(self.reset_snmp_values)
        self._test_session_set(sess)
        del sess

    def test_session_set_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self.addCleanup(self.reset_snmp_values)
            self._test_session_set(sess)
            del sess

    def test_session_set_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self.addCleanup(self.reset_snmp_values)
            self._test_session_set(sess)
            del sess

    def test_session_set_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self.addCleanup(self.reset_snmp_values)
            self._test_session_set(sess)
            del sess

    def _test_session_set_multiple(self, sess):
        res = sess.get(["sysLocation.0", "nsCacheTimeout.1.3.6.1.2.1.2.2"])
        self.assertNotEqual(res[0].value, "my newer location")
        self.assertNotEqual(res[1].value, "160")

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
        self.assertTrue(success)

        res = sess.get(["sysLocation.0", "nsCacheTimeout.1.3.6.1.2.1.2.2"])
        self.assertEqual(res[0].value, "my newer location")
        self.assertEqual(res[1].value, "160")

    def test_session_set_multiple_v1(self):
        sess = Session(**self.sess_params[0])
        self.addCleanup(self.reset_snmp_values)
        self._test_session_set_multiple(sess)
        del sess

    def test_session_set_multiple_v2(self):
        sess = Session(**self.sess_params[1])
        self.addCleanup(self.reset_snmp_values)
        self._test_session_set_multiple(sess)
        del sess

    def test_session_set_multiple_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self.addCleanup(self.reset_snmp_values)
            self._test_session_set_multiple(sess)
            del sess

    def test_session_set_multiple_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self.addCleanup(self.reset_snmp_values)
            self._test_session_set_multiple(sess)
            del sess

    def test_session_set_multiple_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self.addCleanup(self.reset_snmp_values)
            self._test_session_set_multiple(sess)
            del sess

    def test_session_bulk_get_v1(self):
        sess = Session(**self.sess_params[0])
        with self.assertRaises(PacketError):
            sess.bulk_get(
                [
                    "sysUpTime",
                    "sysORLastChange",
                    "sysORID",
                    "sysORDescr",
                    "sysORUpTime",
                ],
            )
        del sess

    def _test_session_bulk_get(self, sess):
        res = sess.bulk_get(
            ["sysUpTime", "sysORLastChange", "sysORID", "sysORDescr", "sysORUpTime"]
        )

        self.assertIn("sysUpTimeInstance", res[0].oid)
        self.assertEqual(res[0].index, "")
        self.assertEqual(res[0].type, "Timeticks")

        self.assertEqual(res[4].oid, "SNMPv2-MIB::sysORUpTime")
        self.assertEqual(res[4].index, "1")
        self.assertEqual(res[4].type, "Timeticks")

    def test_session_bulk_get_v2(self):
        sess = Session(**self.sess_params[1])
        self._test_session_bulk_get(sess)
        del sess

    def test_session_bulk_get_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self._test_session_bulk_get(sess)
            del sess

    def test_session_bulk_get_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self._test_session_bulk_get(sess)
            del sess

    def test_session_bulk_get_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self._test_session_bulk_get(sess)
            del sess

    def test_session_get_invalid_instance_v1(self):
        sess = Session(**self.sess_params[0])
        with self.assertRaises(PacketError):
            sess.get("sysDescr.100")
        del sess

    def _test_session_get_invalid_instance(self, sess):
        res = sess.get("sysDescr.100")
        self.assertEqual(res[0].type, "NOSUCHINSTANCE")

    def test_session_get_invalid_instance_v2(self):
        sess = Session(**self.sess_params[1])
        self._test_session_get_invalid_instance(sess)
        del sess

    def test_session_get_invalid_instance_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self._test_session_get_invalid_instance(sess)
            del sess

    def test_session_get_invalid_instance_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self._test_session_get_invalid_instance(sess)
            del sess

    def test_session_get_invalid_instance_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self._test_session_get_invalid_instance(sess)
            del sess

    def test_session_get_invalid_object_v1(self):
        sess = Session(**self.sess_params[0])
        with self.assertRaises(PacketError):
            sess.get("iso")
        del sess

    def _test_session_get_invalid_object(self, sess):
        res = sess.get("iso")
        self.assertEqual(res[0].type, "NOSUCHOBJECT")

    def test_session_get_invalid_object_v2(self):
        sess = Session(**self.sess_params[1])
        self._test_session_get_invalid_object(sess)
        del sess

    def test_session_get_invalid_object_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self._test_session_get_invalid_object(sess)
            del sess

    def test_session_get_invalid_object_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self._test_session_get_invalid_object(sess)
            del sess

    def test_session_get_invalid_object_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self._test_session_get_invalid_object(sess)
            del sess

    def _test_session_walk(self, sess):
        res = sess.walk("system")

        self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
        self.assertEqual(res[0].index, "0")
        self.assertIn(platform.version(), res[0].value)
        self.assertEqual(res[0].type, "STRING")

        self.assertEqual(res[3].oid, "SNMPv2-MIB::sysContact")
        self.assertEqual(res[3].index, "0")
        self.assertEqual(res[3].value, "G. S. Marzot <gmarzot@marzot.net>")
        self.assertEqual(res[3].type, "STRING")

        self.assertEqual(res[4].oid, "SNMPv2-MIB::sysName")
        self.assertEqual(res[4].index, "0")
        self.assertEqual(res[4].value, platform.node())
        self.assertEqual(res[4].type, "STRING")

        self.assertEqual(res[5].oid, "SNMPv2-MIB::sysLocation")
        self.assertEqual(res[5].index, "0")
        self.assertEqual(res[5].value, "my original location")
        self.assertEqual(res[5].type, "STRING")

    def test_session_walk_v1(self):
        sess = Session(**self.sess_params[0])
        self._test_session_walk(sess)
        del sess

    def test_session_walk_v2(self):
        sess = Session(**self.sess_params[1])
        self._test_session_walk(sess)
        del sess

    def test_session_walk_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self._test_session_walk(sess)
            del sess

    def test_session_walk_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self._test_session_walk(sess)
            del sess

    def test_session_walk_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self._test_session_walk(sess)
            del sess

    def test_session_bulkwalk_v1(self):
        sess = Session(**self.sess_params[0])
        with self.assertRaises(PacketError):
            sess.bulk_walk("system")
        del sess

    def _test_session_bulkwalk(self, sess):
        res = sess.bulk_walk(["system"])

        self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
        self.assertEqual(res[0].index, "0")
        self.assertIn(platform.version(), res[0].value)
        self.assertEqual(res[0].type, "STRING")

        self.assertEqual(res[3].oid, "SNMPv2-MIB::sysContact")
        self.assertEqual(res[3].index, "0")
        self.assertEqual(res[3].value, "G. S. Marzot <gmarzot@marzot.net>")
        self.assertEqual(res[3].type, "STRING")

        self.assertEqual(res[4].oid, "SNMPv2-MIB::sysName")
        self.assertEqual(res[4].index, "0")
        self.assertEqual(res[4].value, platform.node())
        self.assertEqual(res[4].type, "STRING")

        self.assertEqual(res[5].oid, "SNMPv2-MIB::sysLocation")
        self.assertEqual(res[5].index, "0")
        self.assertEqual(res[5].value, "my original location")
        self.assertEqual(res[5].type, "STRING")

    def test_session_bulkwalk_v2(self):
        sess = Session(**self.sess_params[1])
        self._test_session_bulkwalk(sess)
        del sess

    def test_session_bulkwalk_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self._test_session_bulkwalk(sess)
            del sess

    def test_session_bulkwalk_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self._test_session_bulkwalk(sess)
            del sess

    def test_session_bulkwalk_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self._test_session_bulkwalk(sess)
            del sess

    def _test_session_walk_all(self, sess):
        res = sess.walk(".")

        self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
        self.assertEqual(res[0].index, "0")
        self.assertIn(platform.version(), res[0].value)
        self.assertEqual(res[0].type, "STRING")

        self.assertEqual(res[3].oid, "SNMPv2-MIB::sysContact")
        self.assertEqual(res[3].index, "0")
        self.assertEqual(res[3].value, "G. S. Marzot <gmarzot@marzot.net>")
        self.assertEqual(res[3].type, "STRING")

        self.assertEqual(res[4].oid, "SNMPv2-MIB::sysName")
        self.assertEqual(res[4].index, "0")
        self.assertEqual(res[4].value, platform.node())
        self.assertEqual(res[4].type, "STRING")

        self.assertEqual(res[5].oid, "SNMPv2-MIB::sysLocation")
        self.assertEqual(res[5].index, "0")
        self.assertEqual(res[5].value, "my original location")
        self.assertEqual(res[5].type, "STRING")

    def test_session_walk_all_v1(self):
        sess = Session(**self.sess_params[0])
        self._test_session_walk_all(sess)
        del sess

    def test_session_walk_all_v2(self):
        sess = Session(**self.sess_params[1])
        self._test_session_walk_all(sess)
        del sess

    def test_session_walk_all_v3_des(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[2])
            self._test_session_walk_all(sess)
            del sess

    def test_session_walk_all_v3_aes1(self):
        if len(self.sess_params) > 2:
            sess = Session(**self.sess_params[3 if len(self.sess_params) > 4 else 2])
            self._test_session_walk_all(sess)
            del sess

    def test_session_walk_all_v3_aes2(self):
        if len(self.sess_params) > 3:
            sess = Session(**self.sess_params[-1])
            self._test_session_walk_all(sess)
            del sess


class TestSessionUpdate(unittest.TestCase):
    def test_session_update(self):
        s = Session(version="3")
        self.assertEqual(s.version, "3")

        s.version = "1"
        self.assertEqual(s.version, "1")

        del s


if __name__ == '__main__':
    unittest.main()
