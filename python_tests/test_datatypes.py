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
    assert isinstance(value, str), "Returned value is not a string"
    assert not (
        (value.startswith('"') and value.endswith('"'))
        or (value.startswith("'") and value.endswith("'"))
    ), "String value is enclosed in quotes"
