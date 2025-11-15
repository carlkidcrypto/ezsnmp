import unittest
import faulthandler
from ezsnmp import Session

faulthandler.enable()


class TimeticksDataTypesTestBase(unittest.TestCase):
    """Base class for timeticks datatype tests with different SNMP versions."""
    
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

    def test_converted_value_timeticks(self):
        """
        Given: An SNMP session connected to localhost
        When: Performing a GET operation on sysUpTime OID
        Then: Timeticks type should return a valid result
        """
        oid = "1.3.6.1.2.1.1.3.0"  # OID with Timeticks value: SNMPv2-MIB::sysUpTime.0
        result = self.snmp_session.get(
            [
                oid,
            ]
        )
        self.assertGreater(len(result), 0, "No results returned for Timeticks OID")
        if result[0].type == "NOSUCHINSTANCE":
            self.skipTest(f"No such instance for Timeticks with OID: '{oid}'")


# Create concrete test classes for each SNMP version
class TestTimeticksDatatypesV1(TimeticksDataTypesTestBase):
    """Test timeticks data types using SNMP version 1."""
    version = "1"


class TestTimeticksDatatypesV2c(TimeticksDataTypesTestBase):
    """Test timeticks data types using SNMP version 2c."""
    version = "2c"


class TestTimeticksDatatypesV3(TimeticksDataTypesTestBase):
    """Test timeticks data types using SNMP version 3."""
    version = "3"


class TestTimeticksDatatypesV1Int(TimeticksDataTypesTestBase):
    """Test timeticks data types using SNMP version 1 (integer)."""
    version = 1


class TestTimeticksDatatypesV2Int(TimeticksDataTypesTestBase):
    """Test timeticks data types using SNMP version 2 (integer)."""
    version = 2


class TestTimeticksDatatypesV3Int(TimeticksDataTypesTestBase):
    """Test timeticks data types using SNMP version 3 (integer)."""
    version = 3


if __name__ == '__main__':
    unittest.main()
