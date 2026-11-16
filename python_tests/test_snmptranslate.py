import pytest

from ezsnmp import snmptranslate as top_level_snmptranslate
from ezsnmp.exceptions import GenericError, ParseError, UnknownObjectIDError
from ezsnmp.netsnmp import snmptranslate


def test_top_level_export():
    """Test that snmptranslate is exported at the top-level ezsnmp package."""
    assert top_level_snmptranslate is snmptranslate


def test_translate_to_numeric():
    """Test translating a symbolic OID to numeric format with -On."""
    result = snmptranslate(["-On", "SNMPv2-MIB::sysDescr.0"])
    assert result == (".1.3.6.1.2.1.1.1.0",)


def test_translate_from_numeric():
    """Test translating a numeric OID to symbolic format."""
    result = snmptranslate([".1.3.6.1.2.1.1.1.0"])
    assert len(result) == 1
    assert "sysDescr.0" in result[0]


def test_translate_full_oid():
    """Test translating a numeric OID to full symbolic path with -Of."""
    result = snmptranslate(["-Of", ".1.3.6.1.2.1.1.1.0"])
    assert result == (".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0",)


def test_translate_short_oid():
    """Test translating a numeric OID to short name with -Os."""
    result = snmptranslate(["-Os", ".1.3.6.1.2.1.1.1.0"])
    assert result == ("sysDescr.0",)


def test_translate_multiple_oids():
    """Test translating multiple OIDs in a single call."""
    result = snmptranslate(["-On", "SNMPv2-MIB::sysDescr.0", "SNMPv2-MIB::sysUpTime.0"])
    assert result == (".1.3.6.1.2.1.1.1.0", ".1.3.6.1.2.1.1.3.0")


def test_random_access():
    """Test random-access OID lookup with -IR."""
    result = snmptranslate(["-IR", "-On", "sysDescr.0"])
    assert result == (".1.3.6.1.2.1.1.1.0",)


def test_find_all_regex():
    """Test regex MIB object search with -TB."""
    result = snmptranslate(["-TB", "sysDescr"])
    assert len(result) >= 1
    assert any("sysDescr" in item for item in result)


def test_print_description():
    """Test printing MIB object description with -Td."""
    result = snmptranslate(["-Td", "SNMPv2-MIB::sysDescr.0"])
    assert len(result) == 1
    assert "sysDescr" in result[0]


def test_print_tree():
    """Test printing MIB subtree with -Tp."""
    result = snmptranslate(["-Tp", "SNMPv2-MIB::system"])
    assert len(result) == 1
    assert "system" in result[0]


def test_version_flag():
    """Test that -V returns the Net-SNMP version string."""
    result = snmptranslate(["-V"])
    assert len(result) == 1
    assert "NET-SNMP version:" in result[0]


def test_help_raises_parse_error():
    """Test that -h raises ParseError."""
    with pytest.raises(ParseError):
        snmptranslate(["-h"])


def test_invalid_option_raises_parse_error():
    """Test that an unknown option raises ParseError."""
    with pytest.raises(ParseError):
        snmptranslate(["-Z", "SNMPv2-MIB::sysDescr.0"])


def test_invalid_t_option_raises_parse_error():
    """Test that an unknown -T sub-option raises ParseError."""
    with pytest.raises(ParseError):
        snmptranslate(["-TX", "SNMPv2-MIB::sysDescr.0"])


def test_invalid_width_raises_parse_error():
    """Test that an invalid -w width raises ParseError."""
    with pytest.raises(ParseError):
        snmptranslate(["-w", "0", "SNMPv2-MIB::sysDescr.0"])


def test_missing_oid_raises_parse_error():
    """Test that empty arguments raise ParseError."""
    with pytest.raises(ParseError):
        snmptranslate([])


def test_stdin_dash_raises_parse_error():
    """Test that '-' stdin mode raises ParseError."""
    with pytest.raises(ParseError):
        snmptranslate(["-"])


def test_unknown_oid_raises_generic_error():
    """Test that an unknown MIB::OID raises GenericError."""
    with pytest.raises(GenericError):
        snmptranslate(["NONEXISTENT-MIB::doesNotExist.0"])


def test_unknown_random_access_oid_raises_unknown_object_id_error():
    """Test that an unknown -IR OID raises UnknownObjectIDError."""
    with pytest.raises(UnknownObjectIDError):
        snmptranslate(["-IR", "nonexistentObjectIdentifierXYZ"])
