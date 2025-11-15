import unittest
import faulthandler
from ezsnmp import Session

faulthandler.enable()


class OIDDataTypesTestBase(unittest.TestCase):
    """Base class for OID datatype tests with different SNMP versions."""
    
    version = None  # To be overridden by subclasses
    
    def setUp(self):
        """
        Given: A test requiring an SNMP session
        When: Setting up the test case
        Then: Create an SNMP session with the appropriate version
        """
        if self.version in ["3", 3]:
            self.snmp_session = Session(
                version=self.version,
                hostname="localhost",
                port_number="11161",
                auth_protocol="SHA",
                security_level="authPriv",
                security_username="secondary_sha_aes",
                privacy_protocol="AES",
                privacy_passphrase="priv_second",
                auth_passphrase="auth_second",
            )
        else:
            self.snmp_session = Session(
                hostname="localhost",
                port_number="11161",
                version="2c",
            )
    
    def tearDown(self):
        """
        Given: A completed test
        When: Tearing down the test case
        Then: Clean up the SNMP session
        """
        if hasattr(self, 'snmp_session'):
            del self.snmp_session

    def test_converted_value_oid(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on sysObjectID OID
        Then: OID type should be preserved as a string with expected value
        """
        result = self.snmp_session.get(
            [
                "SNMPv2-MIB::sysObjectID.0",  # OID that returns another OID
            ]
        )
        self.assertGreater(len(result), 0, "No results returned for OID type OID")

        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest("No such instance for OID with OID: 'SNMPv2-MIB::sysObjectID.0'")

        # Ensure the type is correctly identified as OID
        self.assertEqual(result[0].type, "OID", "SNMP data type is not OID")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, str, "Converted value is not a string")
        self.assertIn(converted_value, [
            "NET-SNMP-TC::linux",  # Ubuntu
            "NET-SNMP-MIB::netSnmpAgentOIDs.10",  # Almalinux, RockyLinux, ArchLinux
        ], "Converted value is incorrect")


# Create concrete test classes for each SNMP version
class TestOIDDatatypesV1(OIDDataTypesTestBase):
    """Test OID data types using SNMP version 1."""
    version = "1"


class TestOIDDatatypesV2c(OIDDataTypesTestBase):
    """Test OID data types using SNMP version 2c."""
    version = "2c"


class TestOIDDatatypesV3(OIDDataTypesTestBase):
    """Test OID data types using SNMP version 3."""
    version = "3"


class TestOIDDatatypesV1Int(OIDDataTypesTestBase):
    """Test OID data types using SNMP version 1 (integer)."""
    version = 1


class TestOIDDatatypesV2Int(OIDDataTypesTestBase):
    """Test OID data types using SNMP version 2 (integer)."""
    version = 2


class TestOIDDatatypesV3Int(OIDDataTypesTestBase):
    """Test OID data types using SNMP version 3 (integer)."""
    version = 3


if __name__ == '__main__':
    unittest.main()
