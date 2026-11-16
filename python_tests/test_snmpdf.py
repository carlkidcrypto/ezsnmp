import socket
import pytest

from ezsnmp import snmpdf as top_level_snmpdf
from ezsnmp.exceptions import GenericError, ParseError, TimeoutError
from ezsnmp.netsnmp import snmpdf


def _is_test_snmpd_available() -> bool:
    try:
        snmpdf(["-v", "2c", "-c", "public", "-t", "1", "-r", "0", "localhost:11161"])
        return True
    except (TimeoutError, GenericError):
        return False


def test_top_level_export():
    """Test that snmpdf is exported at the top-level ezsnmp package."""
    assert top_level_snmpdf is snmpdf


def test_invalid_c_option_raises_parse_error():
    """Test that an unknown -C sub-option raises ParseError."""
    with pytest.raises(ParseError):
        snmpdf(["-CZ", "-v", "2c", "-c", "public", "localhost:11161"])


def test_invalid_option_raises_parse_error():
    """Test that an unknown option raises ParseError."""
    with pytest.raises(ParseError):
        snmpdf(["-Z", "-v", "2c", "-c", "public", "localhost:11161"])


def test_help_raises_parse_error():
    """Test that -h raises ParseError."""
    with pytest.raises(ParseError):
        snmpdf(["-h"])


def test_version_raises_parse_error():
    """Test that -V raises ParseError."""
    with pytest.raises(ParseError):
        snmpdf(["-V"])


def test_missing_host_raises_parse_error():
    """Test that empty arguments raise ParseError."""
    with pytest.raises(ParseError):
        snmpdf([])


def test_extra_argument_raises_parse_error():
    """Test that an extra positional argument raises ParseError."""
    with pytest.raises(ParseError):
        snmpdf(["-v", "2c", "-c", "public", "localhost:11161", "extra_arg"])


def test_timeout_raises_timeout_error():
    """Test that an unreachable port raises TimeoutError."""
    with pytest.raises(TimeoutError):
        snmpdf(["-v", "2c", "-c", "public", "-t", "1", "-r", "0", "127.0.0.1:19999"])


def test_invalid_hostname_raises_generic_error():
    """Test that an unresolvable hostname raises GenericError."""
    with pytest.raises(GenericError):
        snmpdf(
            [
                "-v",
                "2c",
                "-c",
                "public",
                "-t",
                "1",
                "-r",
                "0",
                "nonexistent.invalid.host.example:161",
            ]
        )


def test_live_snmpdf_default():
    """Test live snmpdf default output against localhost:11161 when snmpd is running."""
    if not _is_test_snmpd_available():
        pytest.skip("Test snmpd not running on localhost:11161")
    result = snmpdf(["-v", "2c", "-c", "public", "localhost:11161"])
    assert len(result) >= 2
    assert "Description" in result[0]
    assert "Size (kB)" in result[0]
    assert "Used%" in result[0]


def test_live_snmpdf_human_binary():
    """Test live snmpdf -Ch output against localhost:11161 when snmpd is running."""
    if not _is_test_snmpd_available():
        pytest.skip("Test snmpd not running on localhost:11161")
    result = snmpdf(["-Ch", "-v", "2c", "-c", "public", "localhost:11161"])
    assert len(result) >= 2
    assert "Description" in result[0]
    assert "Size" in result[0]
    assert "Size (kB)" not in result[0]


def test_live_snmpdf_human_si():
    """Test live snmpdf -CH output against localhost:11161 when snmpd is running."""
    if not _is_test_snmpd_available():
        pytest.skip("Test snmpd not running on localhost:11161")
    result = snmpdf(["-CH", "-v", "2c", "-c", "public", "localhost:11161"])
    assert len(result) >= 2
    assert "Description" in result[0]
    assert "Size" in result[0]
