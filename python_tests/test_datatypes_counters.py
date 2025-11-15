import unittest
import faulthandler
from ezsnmp import Session

faulthandler.enable()


class CounterDataTypesTestBase(unittest.TestCase):
    """Base class for counter datatype tests with different SNMP versions."""
    
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

    def test_converted_value_counter32(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on ifInOctets OID
        Then: Counter32 type should be converted to standard Python int
        """
        result = self.snmp_session.get(
            [
                "IF-MIB::ifInOctets.1",  # OID with a large Counter32 value
            ]
        )
        self.assertGreater(len(result), 0, "No results returned for Counter32 OID")

        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest("No such instance for Counter32 with OID: 'IF-MIB::ifInOctets.1'")

        # Ensure the type is correctly identified as Counter32
        self.assertEqual(result[0].type, "Counter32", "SNMP data type is not Counter32")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, int, "Converted value is not an integer")

    def test_converted_value_counter64(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on ipSystemStatsHCInReceives OID
        Then: Counter64 type should be converted to Python int capable of holding 64-bit unsigned values
        """
        result = self.snmp_session.get(
            [
                "IP-MIB::ipSystemStatsHCInReceives.ipv4",  # OID with a Counter64 value
            ]
        )
        self.assertGreater(len(result), 0, "No results returned for Counter64 OID")

        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest(
                "No such instance for Counter64 with OID: 'IP-MIB::ipSystemStatsHCInReceives.ipv4'"
            )

        # Ensure the type is correctly identified as Counter64
        self.assertEqual(result[0].type, "Counter64", "SNMP data type is not Counter64")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, int, "Converted value is not an integer")


# Create concrete test classes for each SNMP version
class TestCounterDatatypesV1(CounterDataTypesTestBase):
    """Test counter data types using SNMP version 1."""
    version = "1"


class TestCounterDatatypesV2c(CounterDataTypesTestBase):
    """Test counter data types using SNMP version 2c."""
    version = "2c"


class TestCounterDatatypesV3(CounterDataTypesTestBase):
    """Test counter data types using SNMP version 3."""
    version = "3"


class TestCounterDatatypesV1Int(CounterDataTypesTestBase):
    """Test counter data types using SNMP version 1 (integer)."""
    version = 1


class TestCounterDatatypesV2Int(CounterDataTypesTestBase):
    """Test counter data types using SNMP version 2 (integer)."""
    version = 2


class TestCounterDatatypesV3Int(CounterDataTypesTestBase):
    """Test counter data types using SNMP version 3 (integer)."""
    version = 3


if __name__ == '__main__':
    unittest.main()
