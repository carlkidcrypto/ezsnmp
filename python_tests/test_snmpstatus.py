import pytest

from ezsnmp import snmpstatus as top_level_snmpstatus
from ezsnmp.exceptions import ParseError, TimeoutError
from ezsnmp.netsnmp import snmpstatus


def test_top_level_export():
    """Test that snmpstatus is exported at the top-level ezsnmp package."""
    assert top_level_snmpstatus is snmpstatus


def test_help_raises_parse_error():
    """Test that -h raises ParseError."""
    with pytest.raises(ParseError):
        snmpstatus(["-h"])


def test_version_raises_parse_error():
    """Test that -V raises ParseError."""
    with pytest.raises(ParseError):
        snmpstatus(["-V"])


def test_empty_args_raises_parse_error():
    """Test that empty arguments raise ParseError."""
    with pytest.raises(ParseError):
        snmpstatus([])


def test_invalid_option_raises_parse_error():
    """Test that an unknown CLI option raises ParseError."""
    with pytest.raises(ParseError):
        snmpstatus(["-Z", "localhost:11161"])


def test_invalid_c_option_raises_parse_error():
    """Test that an unknown -C sub-option raises ParseError."""
    with pytest.raises(ParseError):
        snmpstatus(["-CX", "-v", "2c", "-c", "public", "localhost:11161"])


def test_timeout_on_unreachable_host():
    """Test that an unreachable host raises TimeoutError."""
    with pytest.raises(TimeoutError):
        snmpstatus(
            ["-v", "2c", "-c", "public", "-t", "1", "-r", "0", "127.0.0.1:19999"]
        )


def test_dont_fix_pdus_option_accepted_before_timeout():
    """Test that -Cf is accepted before reaching TimeoutError on unreachable host."""
    with pytest.raises(TimeoutError):
        snmpstatus(
            ["-Cf", "-v", "2c", "-c", "public", "-t", "1", "-r", "0", "127.0.0.1:19999"]
        )
