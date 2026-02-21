import pytest
import faulthandler
from ezsnmp import Session

faulthandler.enable()

# Types returned when the agent does not support the requested OID.
# NOSUCHINSTANCE: the MIB subtree exists but the specific instance is absent.
# NOSUCHOBJECT:   the OID is not implemented by the agent at all (common on macOS).
_NOT_AVAILABLE_TYPES = {"NOSUCHINSTANCE", "NOSUCHOBJECT"}


def _skip_if_not_available(result, oid):
    """Skip the test if the agent does not expose the requested OID."""
    if result.type in _NOT_AVAILABLE_TYPES:
        pytest.skip(f"OID not available on this agent: '{oid}'")


# This fixture provides an SNMP session for different versions and configurations
@pytest.fixture(params=["1", "2c", "3", 1, 2, 3])
def snmp_session(request):
    """
    Fixture to create an SNMP session for various versions.
    """
    version = request.param
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
    else:
        session = Session(
            hostname="localhost",
            port_number="11161",
            version="2c",
        )
    return session


def test_string_values_not_enclosed_in_quotes(snmp_session):
    """
    Test to ensure string values returned by get/walk operations are not enclosed in quotes.
    This also tests a basic STRING type.
    """
    result = snmp_session.get(
        [
            ".1.3.6.1.2.1.1.1.0",
        ]
    )
    assert len(result) > 0, "No results returned from SNMP get operation"
    value = result[0].value

    # Ensure the type is correctly identified as STRING
    assert result[0].type == "STRING", "SNMP data type is not STRING"

    # Ensure the value is a string and not enclosed in quotes
    assert isinstance(value, str), "Returned value is not a string"
    assert not (
        (value.startswith('"') and value.endswith('"'))
        or (value.startswith("'") and value.endswith("'"))
    ), "String value is enclosed in quotes"


def test_converted_value_integer(snmp_session):
    """
    Test for a standard INTEGER type.
    We expect INTEGER types to be converted to Python's native int.
    """
    result = snmp_session.get(
        [
            "IF-MIB::ifNumber.0",  # This OID returns a simple integer
        ]
    )
    assert len(result) > 0, "No results returned for INTEGER OID"

    _skip_if_not_available(result[0], "IF-MIB::ifNumber.0")

    # Ensure the type is correctly identified as INTEGER
    assert result[0].type == "INTEGER", "SNMP data type is not INTEGER"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, int), "Converted value is not an integer"


def test_converted_value_integer_with_text(snmp_session):
    """
    Test that an INTEGER value with descriptive text (e.g., 'up(1)') is correctly
    parsed and converted to a numeric type.
    """
    result = snmp_session.get(
        [
            "IF-MIB::ifAdminStatus.1",  # OID with a value like 'up(1)'
        ]
    )
    assert len(result) > 0, "No results returned for INTEGER with text OID"

    _skip_if_not_available(result[0], "IF-MIB::ifAdminStatus.1")

    # Ensure the type is correctly identified as INTEGER
    assert result[0].type == "INTEGER", "SNMP data type is not INTEGER"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, int), "Converted value is not an integer"
    assert converted_value == 1, "Converted value is incorrect"


def test_converted_value_negative_integer(snmp_session):
    """
    Test for a negative INTEGER type.
    We expect a standard Python int.
    """
    result = snmp_session.get(
        [
            "RFC1213-MIB::tcpMaxConn.0",  # OID with a value of -1
        ]
    )
    assert len(result) > 0, "No results returned for negative INTEGER OID"

    _skip_if_not_available(result[0], "RFC1213-MIB::tcpMaxConn.0")

    # Ensure the type is correctly identified as INTEGER
    assert result[0].type == "INTEGER", "SNMP data type is not INTEGER"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, int), "Converted value is not an integer"
    assert converted_value == -1, "Converted value is incorrect"


def test_converted_value_counter32(snmp_session):
    """
    Test for a Counter32 type.
    We expect a standard Python int.
    """
    result = snmp_session.get(
        [
            "IF-MIB::ifInOctets.1",  # OID with a large Counter32 value
        ]
    )
    assert len(result) > 0, "No results returned for Counter32 OID"

    _skip_if_not_available(result[0], "IF-MIB::ifInOctets.1")

    # Ensure the type is correctly identified as Counter32
    assert result[0].type == "Counter32", "SNMP data type is not Counter32"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, int), "Converted value is not an integer"


def test_converted_value_counter64(snmp_session):
    """
    Test for a Counter64 type.
    We expect a standard Python int, capable of holding large 64-bit unsigned values.
    """
    result = snmp_session.get(
        [
            "IP-MIB::ipSystemStatsHCInReceives.ipv4",  # OID with a Counter64 value
        ]
    )
    assert len(result) > 0, "No results returned for Counter64 OID"

    _skip_if_not_available(result[0], "IP-MIB::ipSystemStatsHCInReceives.ipv4")

    # Ensure the type is correctly identified as Counter64
    assert result[0].type == "Counter64", "SNMP data type is not Counter64"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, int), "Converted value is not an integer"


def test_converted_value_gauge32(snmp_session):
    """
    Test for a Gauge32 type.
    We expect a standard Python int.
    """
    result = snmp_session.get(
        [
            "IF-MIB::ifSpeed.1",  # OID with a Gauge32 value
        ]
    )
    assert len(result) > 0, "No results returned for Gauge32 OID"

    _skip_if_not_available(result[0], "IF-MIB::ifSpeed.1")

    # Ensure the type is correctly identified as Gauge32
    assert result[0].type == "Gauge32", "SNMP data type is not Gauge32"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, int), "Converted value is not an integer"


def test_converted_value_gauge32_with_units(snmp_session):
    """
    Test that a Gauge32 value with text and units is correctly parsed.
    """
    result = snmp_session.get(
        [
            "IP-MIB::ipSystemStatsRefreshRate.ipv4",  # OID with value like '60000 milli-seconds'
        ]
    )
    assert len(result) > 0, "No results returned for Gauge32 with units OID"

    _skip_if_not_available(result[0], "IP-MIB::ipSystemStatsRefreshRate.ipv4")

    # Ensure the type is correctly identified as Gauge32
    assert result[0].type == "Gauge32", "SNMP data type is not Gauge32"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, int), "Converted value is not an integer"
    assert converted_value == 60000, "Converted value is incorrect"


def test_converted_value_timeticks(snmp_session):
    """
    Test for a Timeticks type.
    We expect the numeric value of the ticks to be converted to an int.
    """

    oid = "1.3.6.1.2.1.1.3.0"  # OID with Timeticks value: SNMPv2-MIB::sysUpTime.0
    result = snmp_session.get(
        [
            oid,
        ]
    )
    assert len(result) > 0, "No results returned for Timeticks OID"
    _skip_if_not_available(result[0], oid)


def test_converted_value_hex_string(snmp_session):
    """
    Test that a Hex-STRING type is converted to a bytearray.
    """

    result = snmp_session.get(
        [
            "SNMP-FRAMEWORK-MIB::snmpEngineID.0",  # OID that returns a Hex-STRING
        ]
    )
    assert len(result) > 0, "No results returned for Hex-STRING OID"

    _skip_if_not_available(result[0], "SNMP-FRAMEWORK-MIB::snmpEngineID.0")

    # Ensure the type is correctly identified as Hex-STRING
    assert result[0].type == "Hex-STRING", "SNMP data type is not Hex-STRING"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, bytes), "Converted value is not of type bytes"


def test_converted_value_octetstr_from_hex(snmp_session):
    """
    Test that an OID explicitly defined as OCTETSTR (but presented as hex)
    is converted to a bytearray.
    """

    result = snmp_session.walk("RFC1213-MIB::atPhysAddress")
    if not result:
        pytest.skip("No results returned for OCTETSTR OID (atPhysAddress)")

    _skip_if_not_available(result[0], "RFC1213-MIB::atPhysAddress")

    if result[0].type not in ["Hex-STRING", "STRING"]:
        pytest.skip(
            f"Unexpected type '{result[0].type}' for OID 'RFC1213-MIB::atPhysAddress'"
        )

    converted_value = result[0].converted_value
    assert isinstance(
        converted_value, (bytes, str)
    ), "Converted value is not of type bytes or str"


def test_converted_value_oid(snmp_session):
    """
    Test that an OID type is preserved as a string.
    """
    result = snmp_session.get(
        [
            "SNMPv2-MIB::sysObjectID.0",  # OID that returns another OID
        ]
    )
    assert len(result) > 0, "No results returned for OID type OID"

    _skip_if_not_available(result[0], "SNMPv2-MIB::sysObjectID.0")

    # Ensure the type is correctly identified as OID
    assert result[0].type == "OID", "SNMP data type is not OID"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, str), "Converted value is not a string"
    assert converted_value in [
        "NET-SNMP-TC::linux",  # Ubuntu
        "NET-SNMP-MIB::netSnmpAgentOIDs.10",  # Almalinux, RockyLinux, ArchLinux
        "NET-SNMP-TC::unknown",  # macOS (Darwin)
    ], f"Unexpected sysObjectID value: {converted_value}"


def test_converted_value_ipaddress(snmp_session):
    """
    Test that an IpAddress type is preserved as a string.
    """

    result = snmp_session.walk("RFC1213-MIB::ipAdEntAddr")
    assert len(result) > 0, "No results returned for IpAddress OID walk"

    _skip_if_not_available(result[0], "RFC1213-MIB::ipAdEntAddr")

    # Ensure the type is correctly identified as IpAddress
    assert result[0].type == "IpAddress", "SNMP data type is not IpAddress"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, str), "Converted value is not a string"


def test_converted_value_network_address(snmp_session):
    """
    Test for the Network Address type.
    """

    result = snmp_session.walk("RFC1213-MIB::atNetAddress")
    if not result:
        pytest.skip("No results returned for Network Address OID (atNetAddress)")

    _skip_if_not_available(result[0], "RFC1213-MIB::atNetAddress")

    # Ensure the type is correctly identified as Network Address
    assert result[0].type == "Network Address", "SNMP data type is not Network Address"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, str), "Converted value is not a string"


def test_converted_value_empty_string(snmp_session):
    """
    Test that an empty string value is correctly handled.
    """
    result = snmp_session.get(
        [
            "IF-MIB::ifPhysAddress.1",  # OID for the loopback interface, which has an empty physical address
        ]
    )
    assert len(result) > 0, "No results returned for empty string OID"

    _skip_if_not_available(result[0], "IF-MIB::ifPhysAddress.1")

    # Ensure the type is correctly identified as STRING
    assert result[0].type == "STRING", "SNMP data type is not STRING"

    converted_value = result[0].converted_value
    assert isinstance(converted_value, str), "Converted value is not a string"
    assert converted_value == "", "Converted value is not an empty string"
