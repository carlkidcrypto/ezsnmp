import pytest

from ezsnmp import snmptable as top_level_snmptable
from ezsnmp.exceptions import GenericError, ParseError
from ezsnmp.netsnmp import snmptable


def test_top_level_export():
    """Test that snmptable is exported at the top-level ezsnmp package."""
    assert top_level_snmptable is snmptable


def test_help_raises_parse_error():
    """Test that -h raises ParseError."""
    with pytest.raises(ParseError):
        snmptable(["-h"])


def test_version_raises_parse_error():
    """Test that -V raises ParseError."""
    with pytest.raises(ParseError):
        snmptable(["-V"])


def test_missing_table_name_raises_parse_error():
    """Test that missing table OID raises ParseError."""
    with pytest.raises(ParseError):
        snmptable(["-v", "2c", "-c", "public", "localhost"])


def test_too_many_args_raises_parse_error():
    """Test that extra positional arguments raise ParseError."""
    with pytest.raises(ParseError):
        snmptable(["-v", "2c", "-c", "public", "localhost", "IF-MIB::ifTable", "extra"])


def test_invalid_c_option_raises_parse_error():
    """Test that an unknown -C sub-option raises ParseError."""
    with pytest.raises(ParseError):
        snmptable(["-CZ", "-v", "2c", "-c", "public", "localhost", "IF-MIB::ifTable"])


def test_invalid_cw_zero_raises_parse_error():
    """Test that -Cw 0 raises ParseError."""
    with pytest.raises(ParseError):
        snmptable(
            ["-Cw", "0", "-v", "2c", "-c", "public", "localhost", "IF-MIB::ifTable"]
        )


def test_invalid_cc_too_small_raises_parse_error():
    """Test that -Cc 2 raises ParseError."""
    with pytest.raises(ParseError):
        snmptable(
            ["-Cc", "2", "-v", "2c", "-c", "public", "localhost", "IF-MIB::ifTable"]
        )


def test_invalid_cr_zero_raises_parse_error():
    """Test that -Cr 0 raises ParseError."""
    with pytest.raises(ParseError):
        snmptable(
            ["-Cr", "0", "-v", "2c", "-c", "public", "localhost", "IF-MIB::ifTable"]
        )


def test_unknown_oid_raises_generic_error():
    """Test that an unknown MIB::OID raises GenericError."""
    with pytest.raises(GenericError):
        snmptable(
            ["-v", "2c", "-c", "public", "localhost", "NONEXISTENT-MIB::doesNotExist"]
        )


def test_non_table_oid_raises_parse_error():
    """Test that a scalar OID raises ParseError."""
    with pytest.raises(ParseError):
        snmptable(["-v", "2c", "-c", "public", "localhost", "SNMPv2-MIB::sysDescr.0"])


def test_headers_only_if_table():
    """Test -Ch headers-only output for IF-MIB::ifTable."""
    result = snmptable(
        ["-Ch", "-v", "2c", "-c", "public", "localhost:11161", "IF-MIB::ifTable"]
    )
    assert len(result) == 1
    assert "ifIndex" in result[0]
    assert "ifDescr" in result[0]


def test_headers_only_brief_and_delimiter():
    """Test -Ch -Cb -Ci -Cl -Cf , formatting options."""
    result = snmptable(
        [
            "-Ch",
            "-Cb",
            "-Ci",
            "-Cl",
            "-Cf",
            ",",
            "-v",
            "2c",
            "-c",
            "public",
            "localhost:11161",
            "IF-MIB::ifTable",
        ]
    )
    assert len(result) == 1
    assert "index," in result[0]
    assert "Index" in result[0]
    assert "ifIndex" not in result[0]


def test_debug_flag_does_not_leak_across_calls():
    """Test that -d output does not leak into subsequent snmptable calls."""
    debug_result = snmptable(
        ["-d", "-Ch", "-v", "2c", "-c", "public", "localhost:11161", "IF-MIB::ifTable"]
    )
    assert len(debug_result) == 1
    assert "IF-MIB::ifIndex i" in debug_result[0]

    clean_result = snmptable(
        [
            "-Ch",
            "-Cb",
            "-Ci",
            "-Cl",
            "-Cf",
            ",",
            "-v",
            "2c",
            "-c",
            "public",
            "localhost:11161",
            "IF-MIB::ifTable",
        ]
    )
    assert len(clean_result) == 1
    assert "ifIndex" not in clean_result[0]


def test_missing_option_args_raise_parse_error():
    """Test that missing arguments for -Cw, -Cc, -Cf, -Cr raise ParseError."""
    for flag in ("-Cw", "-Cc", "-Cf", "-Cr"):
        with pytest.raises(ParseError):
            snmptable([flag])


def test_headers_only_width_options():
    """Test -Ch with -Cw and -Cc formatting options."""
    result = snmptable(
        [
            "-Ch",
            "-Cc",
            "12",
            "-Cw",
            "30",
            "-v",
            "2c",
            "-c",
            "public",
            "localhost:11161",
            "IF-MIB::ifTable",
        ]
    )
    assert len(result) == 1
    assert "ifIndex" in result[0]
