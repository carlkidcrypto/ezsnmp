import pytest

from ezsnmp.session import Session
import faulthandler
from ezsnmp import Session

faulthandler.enable()


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_string_values_not_enclosed_in_quotes(version):
    """
    Test to ensure string values returned by get/walk operations are not enclosed in quotes.
    """
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

    result = session.get(
        [
            ".1.3.6.1.2.1.1.1.0",
        ]
    )  # System
    assert len(result) > 0, "No results returned from SNMP get operation"
    value = result[0].value

    # Ensure the value is a string and not enclosed in quotes
    print(f"Value: {value}")
    assert isinstance(value, str), "Returned value is not a string"
    assert not (
        (value.startswith('"') and value.endswith('"'))
        or (value.startswith("'") and value.endswith("'"))
    ), "String value is enclosed in quotes"

@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_converted_value_integer(version):
    """
    Test to ensure string values are converted to converted_value which attempts to
    convert the string to a more appropriate type.
    
    In this case, we expect INTEGER types to be converted to int.
    """
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

    result = session.get(
        [
            "SNMPv2-MIB::sysUpTime.0",
        ]
    )

    assert isinstance(result[0].converted_value, int)

@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_converted_value_hex_string(version):
    """
    Test to ensure string values are converted to converted_value which attempts to
    convert the string to a more appropriate type.
    
    In this case, we expect Hex-STRING types to be converted to a bytearray.
    """
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

    result = session.get(
        [
            "SNMP-FRAMEWORK-MIB::snmpEngineID.0",
        ]
    )

    print(f"Converted Value: {result[0].converted_value} - {type(result[0].converted_value)} -  {result[0].converted_value.hex()}")
    print(f"Type: {result[0].type}")
    print(f"Oid: {result[0].oid}")
    print(f"Value: {result[0].value}")
    assert isinstance(result[0].converted_value, bytes)