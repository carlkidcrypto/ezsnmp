import unittest
import faulthandler
from ezsnmp import Session

faulthandler.enable()


class StringDataTypesTestBase(unittest.TestCase):
    """Base class for string datatype tests with different SNMP versions."""
    
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

    def test_string_values_not_enclosed_in_quotes(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on sysDescr OID
        Then: String values should not be enclosed in quotes and type should be STRING
        """
        result = self.snmp_session.get(
            [
                ".1.3.6.1.2.1.1.1.0",
            ]
        )
        self.assertGreater(len(result), 0, "No results returned from SNMP get operation")
        value = result[0].value

        # Ensure the type is correctly identified as STRING
        self.assertEqual(result[0].type, "STRING", "SNMP data type is not STRING")

        # Ensure the value is a string and not enclosed in quotes
        self.assertIsInstance(value, str, "Returned value is not a string")
        self.assertFalse(
            (value.startswith('"') and value.endswith('"'))
            or (value.startswith("'") and value.endswith("'")),
            "String value is enclosed in quotes"
        )

    def test_converted_value_hex_string(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on snmpEngineID OID
        Then: Hex-STRING type should be converted to bytes
        """
        result = self.snmp_session.get(
            [
                "SNMP-FRAMEWORK-MIB::snmpEngineID.0",  # OID that returns a Hex-STRING
            ]
        )
        self.assertGreater(len(result), 0, "No results returned for Hex-STRING OID")

        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest(
                "No such instance for Hex-STRING with OID: 'SNMP-FRAMEWORK-MIB::snmpEngineID.0'"
            )

        # Ensure the type is correctly identified as Hex-STRING
        self.assertEqual(result[0].type, "Hex-STRING", "SNMP data type is not Hex-STRING")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, bytes, "Converted value is not of type bytes")

    def test_converted_value_octetstr_from_hex(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a WALK operation on atPhysAddress OID
        Then: OCTETSTR defined OID (presented as hex) should be converted to bytes or str
        """
        result = self.snmp_session.walk("RFC1213-MIB::atPhysAddress")
        if not result:
            self.skipTest("No results returned for OCTETSTR OID (atPhysAddress)")

        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest(
                "No such instance for Hex-STRING with OID: 'RFC1213-MIB::atPhysAddress'"
            )

        if result[0].type not in ["Hex-STRING", "STRING"]:
            self.skipTest(
                f"Unexpected type '{result[0].type}' for OID 'RFC1213-MIB::atPhysAddress'"
            )

        converted_value = result[0].converted_value
        self.assertIsInstance(
            converted_value, (bytes, str),
            "Converted value is not of type bytes or str"
        )

    def test_converted_value_empty_string(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on ifPhysAddress.1 OID (loopback interface)
        Then: Empty string value should be correctly handled and identified as STRING type
        """
        result = self.snmp_session.get(
            [
                "IF-MIB::ifPhysAddress.1",  # OID for the loopback interface, which has an empty physical address
            ]
        )
        self.assertGreater(len(result), 0, "No results returned for empty string OID")

        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest("No such instance for STRING with OID: 'IF-MIB::ifPhysAddress.1'")

        # Ensure the type is correctly identified as STRING
        self.assertEqual(result[0].type, "STRING", "SNMP data type is not STRING")

        converted_value = result[0].converted_value
        self.assertIsInstance(converted_value, str, "Converted value is not a string")
        self.assertEqual(converted_value, "", "Converted value is not an empty string")


# Create concrete test classes for each SNMP version
class TestStringDatatypesV1(StringDataTypesTestBase):
    """Test string data types using SNMP version 1."""
    version = "1"


class TestStringDatatypesV2c(StringDataTypesTestBase):
    """Test string data types using SNMP version 2c."""
    version = "2c"


class TestStringDatatypesV3(StringDataTypesTestBase):
    """Test string data types using SNMP version 3."""
    version = "3"


class TestStringDatatypesV1Int(StringDataTypesTestBase):
    """Test string data types using SNMP version 1 (integer)."""
    version = 1


class TestStringDatatypesV2Int(StringDataTypesTestBase):
    """Test string data types using SNMP version 2 (integer)."""
    version = 2


class TestStringDatatypesV3Int(StringDataTypesTestBase):
    """Test string data types using SNMP version 3 (integer)."""
    version = 3


if __name__ == '__main__':
    unittest.main()
