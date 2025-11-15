import unittest
import faulthandler
from unittest_fixtures import BaseTestCase
from ezsnmp.session import Session

faulthandler.enable()


class TestNormalizeOid(BaseTestCase):
    def test_normalize_oid_regular(self):
        """
        Given a Session with various SNMP version configurations
        When performing a GET with a regular OID format (sysContact.0)
        Then the OID should be normalized to MIB format with proper index
        """
        for sess_args in self.sess_params:
            with self.subTest(sess=sess_args):
                sess = Session(**sess_args)
                res = sess.get("sysContact.0")
                self.assertEqual(res[0].oid, "SNMPv2-MIB::sysContact")
                self.assertEqual(res[0].index, "0")
                del sess

    def test_normalize_oid_numeric(self):
        """
        Given a Session with various SNMP version configurations
        When performing a GET with a numeric OID (.1.3.6.1.2.1.1.1.0)
        Then the OID should be normalized to MIB format with proper index
        """
        for sess_args in self.sess_params:
            with self.subTest(sess=sess_args):
                sess = Session(**sess_args)
                res = sess.get(".1.3.6.1.2.1.1.1.0")
                self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
                self.assertEqual(res[0].index, "0")
                del sess

    def test_normalize_oid_full_qualified(self):
        """
        Given a Session with various SNMP version configurations
        When performing a GET with a fully qualified OID (.iso.org.dod...)
        Then the OID should be normalized to MIB format with proper index
        """
        for sess_args in self.sess_params:
            with self.subTest(sess=sess_args):
                sess = Session(**sess_args)
                res = sess.get(".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0")
                self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
                self.assertEqual(res[0].index, "0")
                del sess


if __name__ == '__main__':
    unittest.main()
