import platform
import unittest
import faulthandler
from ezsnmp.netsnmp import (
    snmpget,
    snmpset,
    snmpbulkget,
    snmpwalk,
    snmpbulkwalk,
)

from ezsnmp.exceptions import GenericError, PacketError
from unittest_fixtures import BaseTestCase

faulthandler.enable()


class TestNetSNMP(BaseTestCase):
    def test_snmp_get_regular(self):
        """
        Given netsnmp parameters for various SNMP versions
        When performing a regular snmpget on sysDescr.0
        Then the result should contain the system description
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                args = netsnmp_args + ["sysDescr.0"]
                res = snmpget(args, "testing_value")

                self.assertIn(platform.version(), res[0].value)
                self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
                self.assertEqual(res[0].index, "0")
                self.assertEqual(res[0].type, "STRING")


    def test_snmp_get_fully_qualified(self):
        """
        Given netsnmp parameters for various SNMP versions
        When performing a snmpget with a fully qualified OID
        Then the result should normalize to SNMPv2-MIB::sysDescr
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                args = netsnmp_args + [".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0"]
                res = snmpget(args, "testing_value")

                self.assertIn(platform.version(), res[0].value)
                self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
                self.assertEqual(res[0].index, "0")
                self.assertEqual(res[0].type, "STRING")

    def test_snmp_get_numeric(self):
        """
        Given netsnmp parameters for various SNMP versions
        When performing a snmpget with a numeric OID
        Then the result should normalize to SNMPv2-MIB::sysDescr
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                args = netsnmp_args + [".1.3.6.1.2.1.1.1.0"]
                res = snmpget(args, "testing_value")

                self.assertIn(platform.version(), res[0].value)
                self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
                self.assertEqual(res[0].index, "0")
                self.assertEqual(res[0].type, "STRING")

    def test_snmp_get_numeric_no_leading_dot(self):
        """
        Given netsnmp parameters for various SNMP versions
        When performing a snmpget with a numeric OID
        Then the result should normalize to SNMPv2-MIB::sysDescr
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                args = netsnmp_args + ["1.3.6.1.2.1.1.1.0"]
                res = snmpget(args, "testing_value")

                self.assertIn(platform.version(), res[0].value)
                self.assertEqual(res[0].oid, "SNMPv2-MIB::sysDescr")
                self.assertEqual(res[0].index, "0")
                self.assertEqual(res[0].type, "STRING")

    def test_snmp_get_unknown(self):
        """
        Given netsnmp parameters for various SNMP versions
        When performing a snmpget on an unknown OID
        Then it should raise a GenericError
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                with self.assertRaises(GenericError):
                    args = netsnmp_args + ["sysDescripto.0"]
                    snmpget(args, "testing_value")

    def test_snmp_get_invalid_instance(self):
        """
        Given netsnmp parameters for various SNMP versions
        When performing a snmpget on an invalid instance
        Then it should raise NoSuchInstanceError
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                if netsnmp_args[1] == "1":
                    if platform.system() != "Darwin":
                        with self.assertRaises(PacketError):
                            args = netsnmp_args + ["sysContact.1"]
                            snmpget(args, "testing_value")
                else:
                    args = netsnmp_args + ["sysContact.1"]
                    res = snmpget(args, "testing_value")
                    self.assertEqual(res[0].type, "NOSUCHINSTANCE")

    def test_snmp_get_invalid_object(self):
        """
        Given netsnmp parameters for various SNMP versions
        When performing a snmpget on an invalid object
        Then it should raise NoSuchObjectError
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                if netsnmp_args[1] == "1":
                    with self.assertRaises(PacketError):
                        args = netsnmp_args + ["iso"]
                        snmpget(args, "testing_value")
                else:
                    args = netsnmp_args + ["iso"]
                    res = snmpget(args, "testing_value")
                    self.assertEqual(res[0].type, "NOSUCHOBJECT")

    def test_snmp_set_string(self):
        """
        Given netsnmp parameters for various SNMP versions
        When performing a snmpset with a string value
        Then the value should be set successfully
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                self.addCleanup(self.reset_snmp_values)
                
                args_1 = netsnmp_args + ["sysLocation.0"]
                res = snmpget(args_1, "testing_value")
                self.assertEqual(res[0].oid, "SNMPv2-MIB::sysLocation")
                self.assertEqual(res[0].index, "0")
                self.assertNotEqual(res[0].value, "my newer location")
                self.assertEqual(res[0].type, "STRING")

                args_2 = netsnmp_args + ["sysLocation.0", "s", "my newer location"]
                success = snmpset(args_2, "testing_value")
                self.assertTrue(success)

                res = snmpget(args_1, "testing_value")
                self.assertEqual(res[0].oid, "SNMPv2-MIB::sysLocation")
                self.assertEqual(res[0].index, "0")
                self.assertEqual(res[0].value, "my newer location")
                self.assertEqual(res[0].type, "STRING")

    def test_snmp_set_integer(self):
        """
        Given netsnmp parameters for various SNMP versions
        When performing a snmpset with an integer value
        Then the value should be set successfully
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                self.addCleanup(self.reset_snmp_values)
                
                args_1 = netsnmp_args + ["nsCacheTimeout.1.3.6.1.2.1.2.2", "i", "65"]
                success = snmpset(args_1, "testing_value")
                self.assertTrue(success)

                args_2 = netsnmp_args + ["nsCacheTimeout.1.3.6.1.2.1.2.2"]
                res = snmpget(args_2, "testing_value")
                self.assertEqual(res[0].oid, "NET-SNMP-AGENT-MIB::nsCacheTimeout.1.3.6.1.2.1.2")
                self.assertEqual(res[0].index, "2")
                self.assertEqual(res[0].value, "65")
                self.assertEqual(res[0].type, "INTEGER")


    def test_snmpbulkget(self):
        """
        Given netsnmp parameters (excluding SNMPv1 which doesn't support bulk)
        When performing a snmpbulkget operation
        Then it should return multiple results
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                if netsnmp_args[1] == "1":
                    with self.assertRaises(PacketError):
                        args = netsnmp_args + [
                            "sysUpTime",
                            "sysORLastChange",
                            "sysORID",
                            "sysORDescr",
                            "sysORUpTime",
                        ]
                        snmpbulkget(args, "testing_value")
                else:
                    args = netsnmp_args + [
                        "sysUpTime",
                        "sysORLastChange",
                        "sysORID",
                        "sysORDescr",
                        "sysORUpTime",
                    ]
                    res = snmpbulkget(args, "testing_value")

                    self.assertEqual(len(res), 50)

                    self.assertIn("sysUpTimeInstance", res[0].oid)
                    self.assertEqual(res[0].index, "")
                    self.assertEqual(res[0].type, "Timeticks")

                    self.assertEqual(res[4].oid, "SNMPv2-MIB::sysORUpTime")
                    self.assertEqual(res[4].index, "1")
                    self.assertEqual(res[4].type, "Timeticks")

    def test_snmpwalk(self):
        """
        Given netsnmp parameters (excluding SNMPv1 for bulkwalk)
        When performing a snmpbulkwalk on the system tree
        Then it should return all system MIB variables
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                if netsnmp_args[1] == "1":
                    with self.assertRaises(PacketError):
                        args = netsnmp_args + ["system"]
                        res = snmpbulkwalk(args, "testing_value")
                else:
                    args = netsnmp_args + ["system"]
                    res = snmpbulkwalk(args, "testing_value")
                    self.assertGreaterEqual(len(res), 7)

                    self.assertIn(platform.version(), res[0].value)
                    self.assertEqual(res[3].value, "G. S. Marzot <gmarzot@marzot.net>")
                    self.assertEqual(res[4].value, platform.node())
                    self.assertEqual(res[5].value, "my original location")

    def test_snmp_walk_res(self):
        """
        Given netsnmp parameters for various SNMP versions
        When performing a snmpwalk on the system tree
        Then it should return all system MIB variables with correct types
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                args = netsnmp_args + ["system"]
                res = snmpwalk(args, "testing_value")

                self.assertGreaterEqual(len(res), 7)

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

    def test_snmp_bulkwalk_res(self):
        """
        Given netsnmp parameters (excluding SNMPv1 which doesn't support bulk)
        When performing a snmpbulkwalk on the system tree
        Then it should return all system MIB variables with correct types
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                if netsnmp_args[1] == "1":
                    with self.assertRaises(PacketError):
                        args = netsnmp_args + ["system"]
                        snmpbulkwalk(args, "testing_value")
                else:
                    args = netsnmp_args + ["system"]
                    res = snmpbulkwalk(args, "testing_value")

                    self.assertGreaterEqual(len(res), 7)

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

    def test_snmp_walk_unknown(self):
        """
        Given netsnmp parameters for various SNMP versions
        When performing a snmpwalk on an unknown OID
        Then it should raise a GenericError
        """
        for netsnmp_args in self.netsnmp_params:
            with self.subTest(netsnmp=netsnmp_args):
                with self.assertRaises(GenericError):
                    args = netsnmp_args + ["systemo123"]
                    snmpwalk(args, "testing_value")

    def test_snmp_bulkwalk_non_sequential_oids(self):
        """
        Given netsnmp parameters (excluding SNMPv1 and macOS)
        When performing a snmpbulkwalk on non-sequential OIDs
        Then it should return the correct results
        """
        if platform.system() != "Darwin":
            for netsnmp_args in self.netsnmp_params:
                with self.subTest(netsnmp=netsnmp_args):
                    if netsnmp_args[1] == "1":
                        with self.assertRaises(PacketError):
                            args = netsnmp_args + [
                                "NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24"
                            ]
                            snmpbulkwalk(args, "testing_value")
                    else:
                        args = netsnmp_args + [
                            "NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24"
                        ]
                        res = snmpbulkwalk(args, "testing_value")

                        self.assertEqual(len(res), 2)

                        self.assertEqual(res[0].oid, "NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24")
                        self.assertEqual(res[0].type, "INTEGER")
                        self.assertEqual(res[0].index, "4")

                        self.assertEqual(res[1].oid, "NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24")
                        self.assertEqual(res[1].type, "INTEGER")
                        self.assertEqual(res[1].index, "7")
        else:
            self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
