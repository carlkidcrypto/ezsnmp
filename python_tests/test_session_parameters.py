import platform
import unittest

from ezsnmp.session import Session
from ezsnmp.exceptions import ConnectionError, ParseError, TimeoutError, PacketError
import faulthandler

faulthandler.enable()


class TestSessionParameters(unittest.TestCase):

    def test_session_print_enums_numerically(self):
        """
        Given a Session configured with print_enums_numerically=True
        When querying ifAdminStatus.1
        Then the enum value should be numeric (1) not symbolic (up)
        """
        for version in ["1", "2c", "3", 1, 2, 3]:
            with self.subTest(version=version):
                if version == "3" or version == 3:
                    session = Session(
                        version=version,
                        hostname="localhost",
                        port_number="11161",
                        auth_protocol="SHA",
                        security_level="authPriv",
                        security_username="secondary_sha_aes",
                        privacy_protocol="AES",
                        privacy_passphrase="priv_second",
                        auth_passphrase="auth_second",
                        print_enums_numerically=True,
                        print_full_oids=False,
                        print_oids_numerically=False,
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-A",
                        "auth_second",
                        "-a",
                        "SHA",
                        "-X",
                        "priv_second",
                        "-x",
                        "AES",
                        "-r",
                        "3",
                        "-l",
                        "authPriv",
                        "-u",
                        "secondary_sha_aes",
                        "-t",
                        "1",
                        "-v",
                        "3",
                        "-O",
                        "e",
                        "localhost:11161",
                    ))

                else:
                    session = Session(
                        hostname="localhost:11161",
                        version=version,
                        print_enums_numerically=True,
                        print_full_oids=False,
                        print_oids_numerically=False,
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-c",
                        "public",
                        "-r",
                        "3",
                        "-t",
                        "1",
                        "-v",
                        "2c" if version == 2 else f"{version}",
                        "-O",
                        "e",
                        "localhost:11161",
                    ))

                res = session.get(["ifAdminStatus.1"])
                self.assertEqual(len(res), 1)
                self.assertEqual(res[0].oid, "IF-MIB::ifAdminStatus")
                self.assertEqual(res[0].value, "1")
                self.assertEqual(res[0].type, "INTEGER")
                self.assertEqual(res[0].index, "1")

                del session

    def test_session_print_full_oids(self):
        """
        Given a Session configured with print_full_oids=True
        When querying ifAdminStatus.1
        Then the OID should be fully qualified (.iso.org.dod...)
        """
        for version in ["1", "2c", "3", 1, 2, 3]:
            with self.subTest(version=version):
                if version == "3" or version == 3:
                    session = Session(
                        version=version,
                        hostname="localhost",
                        port_number="11161",
                        auth_protocol="SHA",
                        security_level="authPriv",
                        security_username="secondary_sha_aes",
                        privacy_protocol="AES",
                        privacy_passphrase="priv_second",
                        auth_passphrase="auth_second",
                        print_enums_numerically=False,
                        print_full_oids=True,
                        print_oids_numerically=False,
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-A",
                        "auth_second",
                        "-a",
                        "SHA",
                        "-X",
                        "priv_second",
                        "-x",
                        "AES",
                        "-r",
                        "3",
                        "-l",
                        "authPriv",
                        "-u",
                        "secondary_sha_aes",
                        "-t",
                        "1",
                        "-v",
                        "3",
                        "-O",
                        "f",
                        "localhost:11161",
                    ))

                else:
                    session = Session(
                        hostname="localhost:11161",
                        version=version,
                        print_enums_numerically=False,
                        print_full_oids=True,
                        print_oids_numerically=False,
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-c",
                        "public",
                        "-r",
                        "3",
                        "-t",
                        "1",
                        "-v",
                        "2c" if version == 2 else f"{version}",
                        "-O",
                        "f",
                        "localhost:11161",
                    ))

                res = session.get(["ifAdminStatus.1"])
                self.assertEqual(len(res), 1)
                self.assertEqual(
                    res[0].oid,
                    ".iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifAdminStatus"
                )
                self.assertEqual(res[0].value, "up(1)")
                self.assertEqual(res[0].type, "INTEGER")
                self.assertEqual(res[0].index, "1")

                del session

    def test_session_print_oids_numerically(self):
        """
        Given a Session configured with print_oids_numerically=True
        When querying ifAdminStatus.1
        Then the OID should be numeric (.1.3.6.1.2.1.2.2.1.7)
        """
        for version in ["1", "2c", "3", 1, 2, 3]:
            with self.subTest(version=version):
                if version == "3" or version == 3:
                    session = Session(
                        version=version,
                        hostname="localhost",
                        port_number="11161",
                        auth_protocol="SHA",
                        security_level="authPriv",
                        security_username="secondary_sha_aes",
                        privacy_protocol="AES",
                        privacy_passphrase="priv_second",
                        auth_passphrase="auth_second",
                        print_enums_numerically=False,
                        print_full_oids=False,
                        print_oids_numerically=True,
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-A",
                        "auth_second",
                        "-a",
                        "SHA",
                        "-X",
                        "priv_second",
                        "-x",
                        "AES",
                        "-r",
                        "3",
                        "-l",
                        "authPriv",
                        "-u",
                        "secondary_sha_aes",
                        "-t",
                        "1",
                        "-v",
                        "3",
                        "-O",
                        "n",
                        "localhost:11161",
                    ))

                else:
                    session = Session(
                        hostname="localhost:11161",
                        version=version,
                        print_enums_numerically=False,
                        print_full_oids=False,
                        print_oids_numerically=True,
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-c",
                        "public",
                        "-r",
                        "3",
                        "-t",
                        "1",
                        "-v",
                        "2c" if version == 2 else f"{version}",
                        "-O",
                        "n",
                        "localhost:11161",
                    ))

                res = session.get(["ifAdminStatus.1"])
                self.assertEqual(len(res), 1)
                self.assertEqual(res[0].oid, ".1.3.6.1.2.1.2.2.1.7")
                self.assertEqual(res[0].value, "up(1)")
                self.assertEqual(res[0].type, "INTEGER")
                self.assertEqual(res[0].index, "1")

                del session

    def test_session_print_options_all_set(self):
        """
        Given a Session with all print options enabled
        When querying ifAdminStatus.1
        Then the OID should be numeric and enum should be numeric
        """
        for version in ["1", "2c", "3", 1, 2, 3]:
            with self.subTest(version=version):
                if version == "3" or version == 3:
                    session = Session(
                        version=version,
                        hostname="localhost",
                        port_number="11161",
                        auth_protocol="SHA",
                        security_level="authPriv",
                        security_username="secondary_sha_aes",
                        privacy_protocol="AES",
                        privacy_passphrase="priv_second",
                        auth_passphrase="auth_second",
                        print_enums_numerically=True,
                        print_full_oids=True,
                        print_oids_numerically=True,
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-A",
                        "auth_second",
                        "-a",
                        "SHA",
                        "-X",
                        "priv_second",
                        "-x",
                        "AES",
                        "-r",
                        "3",
                        "-l",
                        "authPriv",
                        "-u",
                        "secondary_sha_aes",
                        "-t",
                        "1",
                        "-v",
                        "3",
                        "-O",
                        "e",
                        "-O",
                        "f",
                        "-O",
                        "n",
                        "localhost:11161",
                    ))

                else:
                    session = Session(
                        hostname="localhost:11161",
                        version=version,
                        print_enums_numerically=True,
                        print_full_oids=True,
                        print_oids_numerically=True,
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-c",
                        "public",
                        "-r",
                        "3",
                        "-t",
                        "1",
                        "-v",
                        "2c" if version == 2 else f"{version}",
                        "-O",
                        "e",
                        "-O",
                        "f",
                        "-O",
                        "n",
                        "localhost:11161",
                    ))

                res = session.get(["ifAdminStatus.1"])
                self.assertEqual(len(res), 1)
                self.assertEqual(res[0].oid, ".1.3.6.1.2.1.2.2.1.7")
                self.assertEqual(res[0].value, "1")
                self.assertEqual(res[0].type, "INTEGER")
                self.assertEqual(res[0].index, "1")

                del session

    def test_session_print_options_two_set_true_true_false(self):
        """
        Given a Session with print_enums_numerically and print_full_oids enabled
        When querying ifAdminStatus.1
        Then the OID should be fully qualified and enum should be numeric
        """
        for version in ["1", "2c", "3", 1, 2, 3]:
            with self.subTest(version=version):
                if version == "3" or version == 3:
                    session = Session(
                        version=version,
                        hostname="localhost",
                        port_number="11161",
                        auth_protocol="SHA",
                        security_level="authPriv",
                        security_username="secondary_sha_aes",
                        privacy_protocol="AES",
                        privacy_passphrase="priv_second",
                        auth_passphrase="auth_second",
                        print_enums_numerically=True,
                        print_full_oids=True,
                        print_oids_numerically=False,
                    )

                    args = session.args
                    self.assertEqual(args, (
                        "-A",
                        "auth_second",
                        "-a",
                        "SHA",
                        "-X",
                        "priv_second",
                        "-x",
                        "AES",
                        "-r",
                        "3",
                        "-l",
                        "authPriv",
                        "-u",
                        "secondary_sha_aes",
                        "-t",
                        "1",
                        "-v",
                        "3",
                        "-O",
                        "e",
                        "-O",
                        "f",
                        "localhost:11161",
                    ))

                else:
                    session = Session(
                        hostname="localhost:11161",
                        version=version,
                        print_enums_numerically=True,
                        print_full_oids=True,
                        print_oids_numerically=False,
                    )

                    args = session.args
                    self.assertEqual(args, (
                        "-c",
                        "public",
                        "-r",
                        "3",
                        "-t",
                        "1",
                        "-v",
                        "2c" if version == 2 else f"{version}",
                        "-O",
                        "e",
                        "-O",
                        "f",
                        "localhost:11161",
                    ))

                res = session.get(["ifAdminStatus.1"])
                self.assertEqual(len(res), 1)
                self.assertEqual(
                    res[0].oid,
                    ".iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifAdminStatus"
                )
                self.assertEqual(res[0].value, "1")
                self.assertEqual(res[0].type, "INTEGER")
                self.assertEqual(res[0].index, "1")

                del session

    def test_session_print_options_two_set_false_true_true(self):
        """
        Given a Session with print_full_oids and print_oids_numerically enabled
        When querying ifAdminStatus.1
        Then the OID should be numeric and enum should be symbolic
        """
        for version in ["1", "2c", "3", 1, 2, 3]:
            with self.subTest(version=version):
                if version == "3" or version == 3:
                    session = Session(
                        version=version,
                        hostname="localhost",
                        port_number="11161",
                        auth_protocol="SHA",
                        security_level="authPriv",
                        security_username="secondary_sha_aes",
                        privacy_protocol="AES",
                        privacy_passphrase="priv_second",
                        auth_passphrase="auth_second",
                        print_enums_numerically=False,
                        print_full_oids=True,
                        print_oids_numerically=True,
                    )

                    args = session.args
                    self.assertEqual(args, (
                        "-A",
                        "auth_second",
                        "-a",
                        "SHA",
                        "-X",
                        "priv_second",
                        "-x",
                        "AES",
                        "-r",
                        "3",
                        "-l",
                        "authPriv",
                        "-u",
                        "secondary_sha_aes",
                        "-t",
                        "1",
                        "-v",
                        "3",
                        "-O",
                        "f",
                        "-O",
                        "n",
                        "localhost:11161",
                    ))

                else:
                    session = Session(
                        hostname="localhost:11161",
                        version=version,
                        print_enums_numerically=False,
                        print_full_oids=True,
                        print_oids_numerically=True,
                    )

                    args = session.args
                    self.assertEqual(args, (
                        "-c",
                        "public",
                        "-r",
                        "3",
                        "-t",
                        "1",
                        "-v",
                        "2c" if version == 2 else f"{version}",
                        "-O",
                        "f",
                        "-O",
                        "n",
                        "localhost:11161",
                    ))

                res = session.get(["ifAdminStatus.1"])
                self.assertEqual(len(res), 1)
                self.assertEqual(res[0].oid, ".1.3.6.1.2.1.2.2.1.7")
                self.assertEqual(res[0].value, "up(1)")
                self.assertEqual(res[0].type, "INTEGER")
                self.assertEqual(res[0].index, "1")

                del session

    def test_session_print_options_two_set_true_false_true(self):
        """
        Given a Session with print_enums_numerically and print_oids_numerically enabled
        When querying ifAdminStatus.1
        Then the OID should be numeric and enum should be numeric
        """
        for version in ["1", "2c", "3", 1, 2, 3]:
            with self.subTest(version=version):
                if version == "3" or version == 3:
                    session = Session(
                        version=version,
                        hostname="localhost",
                        port_number="11161",
                        auth_protocol="SHA",
                        security_level="authPriv",
                        security_username="secondary_sha_aes",
                        privacy_protocol="AES",
                        privacy_passphrase="priv_second",
                        auth_passphrase="auth_second",
                        print_enums_numerically=True,
                        print_full_oids=False,
                        print_oids_numerically=True,
                    )

                    args = session.args
                    self.assertEqual(args, (
                        "-A",
                        "auth_second",
                        "-a",
                        "SHA",
                        "-X",
                        "priv_second",
                        "-x",
                        "AES",
                        "-r",
                        "3",
                        "-l",
                        "authPriv",
                        "-u",
                        "secondary_sha_aes",
                        "-t",
                        "1",
                        "-v",
                        "3",
                        "-O",
                        "e",
                        "-O",
                        "n",
                        "localhost:11161",
                    ))

                else:
                    session = Session(
                        hostname="localhost:11161",
                        version=version,
                        print_enums_numerically=True,
                        print_full_oids=False,
                        print_oids_numerically=True,
                    )

                    args = session.args
                    self.assertEqual(args, (
                        "-c",
                        "public",
                        "-r",
                        "3",
                        "-t",
                        "1",
                        "-v",
                        "2c" if version == 2 else f"{version}",
                        "-O",
                        "e",
                        "-O",
                        "n",
                        "localhost:11161",
                    ))

                res = session.get(["ifAdminStatus.1"])
                self.assertEqual(len(res), 1)
                self.assertEqual(res[0].oid, ".1.3.6.1.2.1.2.2.1.7")
                self.assertEqual(res[0].value, "1")
                self.assertEqual(res[0].type, "INTEGER")
                self.assertEqual(res[0].index, "1")

                del session

    def test_session_print_timeticks_numerically_set(self):
        """
        Given a Session with print_timeticks_numerically=True
        When querying sysUpTime.0
        Then the timeticks value should be purely numeric
        """
        for version in ["1", "2c", "3", 1, 2, 3]:
            with self.subTest(version=version):
                if version == "3" or version == 3:
                    session = Session(
                        version=version,
                        hostname="localhost",
                        port_number="11161",
                        auth_protocol="SHA",
                        security_level="authPriv",
                        security_username="secondary_sha_aes",
                        privacy_protocol="AES",
                        privacy_passphrase="priv_second",
                        auth_passphrase="auth_second",
                        print_timeticks_numerically=True,
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-A",
                        "auth_second",
                        "-a",
                        "SHA",
                        "-X",
                        "priv_second",
                        "-x",
                        "AES",
                        "-r",
                        "3",
                        "-l",
                        "authPriv",
                        "-u",
                        "secondary_sha_aes",
                        "-t",
                        "1",
                        "-v",
                        "3",
                        "-O",
                        "t",
                        "localhost:11161",
                    ))

                else:
                    session = Session(
                        hostname="localhost:11161",
                        version=version,
                        print_timeticks_numerically=True,
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-c",
                        "public",
                        "-r",
                        "3",
                        "-t",
                        "1",
                        "-v",
                        "2c" if version == 2 else f"{version}",
                        "-O",
                        "t",
                        "localhost:11161",
                    ))

                res_ticks = session.get(["sysUpTime.0"])
                self.assertEqual(len(res_ticks), 1)
                self.assertEqual(res_ticks[0].type, "Timeticks")
                self.assertTrue(res_ticks[0].value.isdigit())

                del session

    def test_session_print_timeticks_numerically_unset(self):
        """
        Given a Session with print_timeticks_numerically=False (default)
        When querying sysUpTime.0
        Then the timeticks value should be human-readable (not purely numeric)
        """
        for version in ["1", "2c", "3", 1, 2, 3]:
            with self.subTest(version=version):
                if version == "3" or version == 3:
                    session = Session(
                        version=version,
                        hostname="localhost",
                        port_number="11161",
                        auth_protocol="SHA",
                        security_level="authPriv",
                        security_username="secondary_sha_aes",
                        privacy_protocol="AES",
                        privacy_passphrase="priv_second",
                        auth_passphrase="auth_second",
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-A",
                        "auth_second",
                        "-a",
                        "SHA",
                        "-X",
                        "priv_second",
                        "-x",
                        "AES",
                        "-r",
                        "3",
                        "-l",
                        "authPriv",
                        "-u",
                        "secondary_sha_aes",
                        "-t",
                        "1",
                        "-v",
                        "3",
                        "localhost:11161",
                    ))

                else:
                    session = Session(
                        hostname="localhost:11161",
                        version=version,
                    )

                    args = session.args

                    self.assertEqual(args, (
                        "-c",
                        "public",
                        "-r",
                        "3",
                        "-t",
                        "1",
                        "-v",
                        "2c" if version == 2 else f"{version}",
                        "localhost:11161",
                    ))

                res_ticks = session.get(["sysUpTime.0"])
                self.assertEqual(len(res_ticks), 1)
                self.assertEqual(res_ticks[0].type, "Timeticks")
                self.assertFalse(res_ticks[0].value.isdigit())

                del session


if __name__ == '__main__':
    unittest.main()
