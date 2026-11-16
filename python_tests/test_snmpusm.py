import pytest

from ezsnmp import snmpusm as top_level_snmpusm
from ezsnmp.exceptions import ParseError, TimeoutError
from ezsnmp.netsnmp import snmpusm


def test_top_level_export():
    """Test that snmpusm is exported at the top-level ezsnmp package."""
    assert top_level_snmpusm is snmpusm


def test_help_raises_parse_error():
    """Test that -h raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-h"])


def test_version_raises_parse_error():
    """Test that -V raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-V"])


def test_invalid_option_raises_parse_error():
    """Test that an unknown option raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-Z", "localhost", "delete", "testuser"])


def test_invalid_c_flag_raises_parse_error():
    """Test that an unknown -C sub-option raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-CX", "-v", "2c", "-c", "public", "localhost", "delete", "testuser"])


def test_bad_cp_option_no_arg_raises_parse_error():
    """Test that -Cp without an argument raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-Cp"])


def test_bad_ce_option_no_arg_raises_parse_error():
    """Test that -CE without an argument raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-CE"])


def test_bad_ce_option_invalid_hex_raises_parse_error():
    """Test that -CE with invalid hex raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(
            [
                "-CE",
                "ZZZZ",
                "-v",
                "2c",
                "-c",
                "public",
                "localhost",
                "delete",
                "testuser",
            ]
        )


def test_missing_operation_raises_parse_error():
    """Test that missing USM command raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-v", "2c", "-c", "public", "localhost"])


def test_unknown_command_raises_parse_error():
    """Test that an unknown USM command raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-v", "2c", "-c", "public", "localhost", "invalidcmd"])


def test_create_missing_user_raises_parse_error():
    """Test that create without a user raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-v", "2c", "-c", "public", "localhost", "create"])


def test_delete_missing_user_raises_parse_error():
    """Test that delete without a user raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-v", "2c", "-c", "public", "localhost", "delete"])


def test_activate_missing_user_raises_parse_error():
    """Test that activate without a user raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-v", "2c", "-c", "public", "localhost", "activate"])


def test_deactivate_missing_user_raises_parse_error():
    """Test that deactivate without a user raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-v", "2c", "-c", "public", "localhost", "deactivate"])


def test_clone_from_missing_user_raises_parse_error():
    """Test that cloneFrom without a user raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-v", "2c", "-c", "public", "localhost", "cloneFrom"])


def test_clone_from_missing_source_user_raises_parse_error():
    """Test that cloneFrom without a source user raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(["-v", "2c", "-c", "public", "localhost", "cloneFrom", "newuser"])


def test_passwd_short_new_pass_raises_parse_error():
    """Test that passwd with a short new passphrase raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(
            ["-v", "2c", "-c", "public", "localhost", "passwd", "oldpass123", "short"]
        )


def test_passwd_short_old_pass_raises_parse_error():
    """Test that passwd with a short old passphrase raises ParseError."""
    with pytest.raises(ParseError):
        snmpusm(
            ["-v", "2c", "-c", "public", "localhost", "passwd", "short", "newpass123"]
        )


def test_unreachable_host_raises_timeout_error():
    """Test that an unreachable host raises TimeoutError."""
    with pytest.raises(TimeoutError):
        snmpusm(
            [
                "-v",
                "2c",
                "-c",
                "public",
                "-r",
                "0",
                "-t",
                "1",
                "127.0.0.1:19999",
                "delete",
                "testuser",
            ]
        )
