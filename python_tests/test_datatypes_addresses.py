import unittest
import faulthandler
from ezsnmp import Session

faulthandler.enable()


class AddressDataTypesTestBase(unittest.TestCase):
    """Base class for IP and network address datatype tests with different SNMP versions."""
    
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

    def test_converted_value_ipaddress(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a WALK operation on ipAdEntAddr OID
        Then: IpAddress type should be preserved as a string
        """
        result = self.snmp_session.walk("RFC1213-MIB::ipAdEntAddr")
        self.assertGreater(len(result), 0, "No results returned for IpAddress OID walk")

        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest(
                "No such instance for IpAddress with OID: 'RFC1213-MIB::ipAdEntAddr'"
            )

        # Ensure the type is correctly identified as IpAddress
        self.assertEqual(result[0].type, "IpAddress", "SNMP data type is not IpAddress")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, str, "Converted value is not a string")

    def test_converted_value_network_address(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a WALK operation on atNetAddress OID
        Then: Network Address type should be preserved as a string
        """
        result = self.snmp_session.walk("RFC1213-MIB::atNetAddress")
        if not result:
            self.skipTest("No results returned for Network Address OID (atNetAddress)")

        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest(
                "No such instance for Network Address with OID: 'RFC1213-MIB::atNetAddress'"
            )

        # Ensure the type is correctly identified as Network Address
        self.assertEqual(result[0].type, "Network Address", "SNMP data type is not Network Address")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, str, "Converted value is not a string")


# Create concrete test classes for each SNMP version
class TestAddressDatatypesV1(AddressDataTypesTestBase):
    """Test IP and network address data types using SNMP version 1."""
    version = "1"


class TestAddressDatatypesV2c(AddressDataTypesTestBase):
    """Test IP and network address data types using SNMP version 2c."""
    version = "2c"


class TestAddressDatatypesV3(AddressDataTypesTestBase):
    """Test IP and network address data types using SNMP version 3."""
    version = "3"


class TestAddressDatatypesV1Int(AddressDataTypesTestBase):
    """Test IP and network address data types using SNMP version 1 (integer)."""
    version = 1


class TestAddressDatatypesV2Int(AddressDataTypesTestBase):
    """Test IP and network address data types using SNMP version 2 (integer)."""
    version = 2


class TestAddressDatatypesV3Int(AddressDataTypesTestBase):
    """Test IP and network address data types using SNMP version 3 (integer)."""
    version = 3


if __name__ == '__main__':
    unittest.main()
