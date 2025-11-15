import unittest
from ezsnmp import Session
from platform_compat import is_des_supported
from unittest_fixtures import BaseTestCase


class TestV3AuthenticationPrivacy(BaseTestCase):
    @unittest.skipIf(not is_des_supported(), "DES not supported on AlmaLinux 10+")
    def test_v3_authentication_md5_privacy_des(self):
        """
        Given an SNMPv3 session with MD5 authentication and DES privacy
        When performing a GET operation on sysDescr.0
        Then the session should successfully authenticate and return the system description
        """
        s = Session(**self.sess_v3_md5_des)

        self.assertEqual(s.auth_passphrase, "auth_pass")
        self.assertEqual(s.auth_protocol, "MD5")
        self.assertEqual(s.privacy_passphrase, "priv_pass")
        self.assertEqual(s.privacy_protocol, "DES")

        res = s.get("sysDescr.0")

        self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
        self.assertEqual(res[0].index, "0")
        self.assertEqual(res[0].type, "STRING")
        del s

    def test_v3_authentication_md5_privacy_aes(self):
        """
        Given an SNMPv3 session with MD5 authentication and AES privacy
        When performing a GET operation on sysDescr.0
        Then the session should successfully authenticate and return the system description
        """
        s = Session(**self.sess_v3_md5_aes)

        self.assertEqual(s.auth_passphrase, "auth_pass")
        self.assertEqual(s.auth_protocol, "MD5")
        self.assertEqual(s.privacy_passphrase, "priv_pass")
        self.assertEqual(s.privacy_protocol, "AES")

        res = s.get("sysDescr.0")

        self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
        self.assertEqual(res[0].index, "0")
        self.assertEqual(res[0].type, "STRING")
        del s

    def test_v3_authentication_sha_privacy_aes(self):
        """
        Given an SNMPv3 session with SHA authentication and AES privacy
        When performing a GET operation on sysDescr.0
        Then the session should successfully authenticate and return the system description
        """
        s = Session(**self.sess_v3_sha_aes)

        self.assertEqual(s.auth_passphrase, "auth_second")
        self.assertEqual(s.auth_protocol, "SHA")
        self.assertEqual(s.privacy_passphrase, "priv_second")
        self.assertEqual(s.privacy_protocol, "AES")

        res = s.get("sysDescr.0")

        self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
        self.assertEqual(res[0].index, "0")
        self.assertEqual(res[0].type, "STRING")
        del s

    def test_v3_authentication_sha_no_priv(self):
        """
        Given an SNMPv3 session with SHA authentication and no privacy protocol
        When performing a GET operation on sysDescr.0
        Then the session should successfully authenticate and return the system description
        """
        s = Session(**self.sess_v3_sha_no_priv)

        self.assertEqual(s.auth_passphrase, "auth_second")
        self.assertEqual(s.auth_protocol, "SHA")
        self.assertEqual(s.privacy_passphrase, "")
        self.assertEqual(s.privacy_protocol, "")

        res = s.get("sysDescr.0")

        self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
        self.assertEqual(res[0].index, "0")
        self.assertEqual(res[0].type, "STRING")
        del s

    def test_v3_authentication_md5_no_priv(self):
        """
        Given an SNMPv3 session with MD5 authentication and no privacy protocol
        When performing a GET operation on sysDescr.0
        Then the session should successfully authenticate and return the system description
        """
        s = Session(**self.sess_v3_md5_no_priv)

        self.assertEqual(s.auth_passphrase, "auth_pass")
        self.assertEqual(s.auth_protocol, "MD5")
        self.assertEqual(s.privacy_passphrase, "")
        self.assertEqual(s.privacy_protocol, "")

        res = s.get("sysDescr.0")

        self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
        self.assertEqual(res[0].index, "0")
        self.assertEqual(res[0].type, "STRING")
        del s


if __name__ == '__main__':
    unittest.main()
