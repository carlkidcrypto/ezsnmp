import unittest
import faulthandler
from ezsnmp import Session

faulthandler.enable()


class IntegerDataTypesTestBase(unittest.TestCase):
    """Base class for integer datatype tests with different SNMP versions."""
    
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

    def test_converted_value_integer(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on ifNumber OID
        Then: INTEGER types should be converted to Python's native int
        """
        result = self.snmp_session.get(
            [
                "IF-MIB::ifNumber.0",  # This OID returns a simple integer
            ]
        )
        self.assertGreater(len(result), 0, "No results returned for INTEGER OID")

        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest("No such instance for INTEGER with OID: 'IF-MIB::ifNumber.0'")

        # Ensure the type is correctly identified as INTEGER
        self.assertEqual(result[0].type, "INTEGER", "SNMP data type is not INTEGER")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, int, "Converted value is not an integer")

    def test_converted_value_integer_with_text(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on ifAdminStatus OID with a value like 'up(1)'
        Then: INTEGER value with descriptive text should be correctly parsed and converted to numeric type
        """
        result = self.snmp_session.get(
            [
                "IF-MIB::ifAdminStatus.1",  # OID with a value like 'up(1)'
            ]
        )
        self.assertGreater(len(result), 0, "No results returned for INTEGER with text OID")

        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest("No such instance for INTEGER with OID: 'IF-MIB::ifAdminStatus.1'")

        # Ensure the type is correctly identified as INTEGER
        self.assertEqual(result[0].type, "INTEGER", "SNMP data type is not INTEGER")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, int, "Converted value is not an integer")
        self.assertEqual(converted_value, 1, "Converted value is incorrect")

    def test_converted_value_negative_integer(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on tcpMaxConn OID with a value of -1
        Then: Negative INTEGER should be converted to standard Python int
        """
        result = self.snmp_session.get(
            [
                "RFC1213-MIB::tcpMaxConn.0",  # OID with a value of -1
            ]
        )
        self.assertGreater(len(result), 0, "No results returned for negative INTEGER OID")

        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest(
                "No such instance for INTEGER with OID: 'RFC1213-MIB::tcpMaxConn.0'"
            )

        # Ensure the type is correctly identified as INTEGER
        self.assertEqual(result[0].type, "INTEGER", "SNMP data type is not INTEGER")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, int, "Converted value is not an integer")
        self.assertEqual(converted_value, -1, "Converted value is incorrect")

    def test_converted_value_gauge32(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on ifSpeed OID
        Then: Gauge32 type should be converted to standard Python int with value 10000000
        """
        result = self.snmp_session.get(
            [
                "IF-MIB::ifSpeed.1",  # OID with a Gauge32 value
            ]
        )
        self.assertGreater(len(result), 0, "No results returned for Gauge32 OID")

        # Ensure the type is correctly identified as Gauge32
        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest("No such instance for Gauge32 with OID: 'IF-MIB::ifSpeed.1'")

        self.assertEqual(result[0].type, "Gauge32", "SNMP data type is not Gauge32")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, int, "Converted value is not an integer")
        self.assertEqual(converted_value, 10000000, "Converted value is incorrect")

    def test_converted_value_gauge32_with_units(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on ipSystemStatsRefreshRate OID with value like '60000 milli-seconds'
        Then: Gauge32 value with text and units should be correctly parsed to int value 60000
        """
        result = self.snmp_session.get(
            [
                "IP-MIB::ipSystemStatsRefreshRate.ipv4",  # OID with value like '60000 milli-seconds'
            ]
        )
        self.assertGreater(len(result), 0, "No results returned for Gauge32 with units OID")

        # Ensure the type is correctly identified as Gauge32
        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest(
                "No such instance for Gauge32 with OID: 'IP-MIB::ipSystemStatsRefreshRate.ipv4'"
            )

        self.assertEqual(result[0].type, "Gauge32", "SNMP data type is not Gauge32")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, int, "Converted value is not an integer")
        self.assertEqual(converted_value, 60000, "Converted value is incorrect")


# Create concrete test classes for each SNMP version
class TestIntegerDatatypesV1(IntegerDataTypesTestBase):
    """Test integer data types using SNMP version 1."""
    version = "1"


class TestIntegerDatatypesV2c(IntegerDataTypesTestBase):
    """Test integer data types using SNMP version 2c."""
    version = "2c"


class TestIntegerDatatypesV3(IntegerDataTypesTestBase):
    """Test integer data types using SNMP version 3."""
    version = "3"


class TestIntegerDatatypesV1Int(IntegerDataTypesTestBase):
    """Test integer data types using SNMP version 1 (integer)."""
    version = 1


class TestIntegerDatatypesV2Int(IntegerDataTypesTestBase):
    """Test integer data types using SNMP version 2 (integer)."""
    version = 2


class TestIntegerDatatypesV3Int(IntegerDataTypesTestBase):
    """Test integer data types using SNMP version 3 (integer)."""
    version = 3


if __name__ == '__main__':
    unittest.main()
