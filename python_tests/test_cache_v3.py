import unittest
from ezsnmp.session import Session
from ezsnmp.exceptions import TimeoutError
import faulthandler
from platform_compat import is_des_supported
from unittest_fixtures import BaseTestCase

faulthandler.enable()


class TestV3Caching(BaseTestCase):
    @unittest.skipIf(not is_des_supported(), "DES not supported on AlmaLinux 10+")
    def test_v3_not_caching_user(self):
        """
        Given an SNMPv3 session with MD5/DES authentication
        When the privacy passphrase is changed to an incorrect value
        Then subsequent SNMP operations should fail with TimeoutError
        """
        s = Session(**self.sess_v3_md5_des)
        self.assertEqual(s.args, (
            "-A",
            "auth_pass",
            "-a",
            "MD5",
            "-X",
            "priv_pass",
            "-x",
            "DES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "initial_md5_des",
            "-t",
            "5",
            "-v",
            "3",
            "localhost:11161",
        ))
        res = s.get("sysDescr.0")

        self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
        self.assertEqual(res[0].index, "0")
        self.assertEqual(res[0].type, "STRING")
        s.privacy_passphrase = "wrong_pass"
        self.assertEqual(s.privacy_passphrase, "wrong_pass")

        with self.assertRaises(TimeoutError):
            self.assertEqual(s.args, (
                "-A",
                "auth_pass",
                "-a",
                "MD5",
                "-X",
                "wrong_pass",
                "-x",
                "DES",
                "-r",
                "3",
                "-l",
                "authPriv",
                "-u",
                "initial_md5_des",
                "-t",
                "5",
                "-v",
                "3",
                "localhost:11161",
            ))
            res = s.get("sysDescr.0")

        d = dict(**self.sess_v3_md5_des)
        d["privacy_passphrase"] = "wrong_pass"
        s = Session(**d)
        self.assertEqual(s.privacy_passphrase, "wrong_pass")
        with self.assertRaises(TimeoutError):
            self.assertEqual(s.args, (
                "-A",
                "auth_pass",
                "-a",
                "MD5",
                "-X",
                "wrong_pass",
                "-x",
                "DES",
                "-r",
                "3",
                "-l",
                "authPriv",
                "-u",
                "initial_md5_des",
                "-t",
                "5",
                "-v",
                "3",
                "localhost:11161",
            ))
            res = s.get("sysDescr.0")

        s.privacy_passphrase = "priv_pass"
        self.assertEqual(s.privacy_passphrase, "priv_pass")
        self.assertEqual(s.args, (
            "-A",
            "auth_pass",
            "-a",
            "MD5",
            "-X",
            "priv_pass",
            "-x",
            "DES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "initial_md5_des",
            "-t",
            "5",
            "-v",
            "3",
            "localhost:11161",
        ))
        res = s.get("sysDescr.0")

        self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
        self.assertEqual(res[0].index, "0")
        self.assertEqual(res[0].type, "STRING")


if __name__ == '__main__':
    unittest.main()
