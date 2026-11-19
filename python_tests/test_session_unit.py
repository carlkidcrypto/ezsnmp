"""
Unit tests for Session that require no SNMP daemon and make no network calls.
Covers: constructor validation, repr/str, to_dict, close, context manager,
        __del__, property setters, IPv6 hostname parsing.
"""

import unittest.mock

import pytest

from ezsnmp.session import Session
from ezsnmp.exceptions import ParseError
import faulthandler

faulthandler.enable()


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_invalid_hostname_and_port_number(version):

    with pytest.raises(ParseError):
        Session(hostname="localhost:162", port_number="163", version=version)


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_hostname_and_port_number_split(version):

    session = Session(hostname="localhost:162", version=version)
    assert session.hostname == "localhost"
    assert session.port_number == "162"


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_address(version):

    session = Session(hostname="2001:db8::", version=version)
    assert session.hostname == "2001:db8::"


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_address_and_port_number(version):

    session = Session(
        hostname="fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa",
        port_number="162",
        version=version,
    )
    assert session.hostname == "fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa"
    assert session.port_number == "162"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_address_and_port_number_split(version):

    session = Session(hostname="[2001:db8::]:161", version=version)
    assert session.hostname == "[2001:db8::]"
    assert session.port_number == "161"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_address_with_protocol_and_port_number_split(version):

    session = Session(hostname="udp6:[2001:db8::]:162", version=version)
    assert session.hostname == "udp6:[2001:db8::]"
    assert session.port_number == "162"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_address_with_protocol(version):

    session = Session(hostname="udp6:[2001:db8::]", version=version)
    assert session.hostname == "udp6:[2001:db8::]"
    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_ipv6_invalid_hostname_and_port_number(version):

    with pytest.raises(ParseError):
        Session(
            hostname="[fd5d:12c9:2201:1:bc9c:f8ff:fe5c:57fa]:161",
            port_number="162",
            version=version,
        )


def test_session_update():

    s = Session(version="3")
    assert s.version == "3"

    s.version = "1"
    assert s.version == "1"

    del s


def test_session_repr_masks_community():
    """Test __repr__ includes hostname/version but masks non-empty community."""
    s = Session(
        hostname="testhost", port_number="161", version="2c", community="public"
    )
    r = repr(s)
    assert "testhost" in r
    assert "2c" in r
    assert "public" not in r
    assert "***" in r
    del s


def test_session_repr_empty_community():
    """Test __repr__ shows empty string when community is explicitly empty."""
    s = Session(hostname="testhost", version="3", community="")
    r = repr(s)
    assert "testhost" in r
    assert "***" not in r
    del s


def test_session_str():
    """Test __str__ returns a human-readable representation with host and version."""
    s = Session(hostname="testhost", port_number="161", version="2c")
    text = str(s)
    assert "testhost" in text
    assert "2c" in text
    del s


def test_session_str_default_port():
    """Test __str__ shows 'default' when no port is specified."""
    s = Session(hostname="testhost", version="1")
    text = str(s)
    assert "default" in text
    del s


def test_session_to_dict_required_keys():
    """Test to_dict() contains all required keys."""
    s = Session(version="2c", community="public")
    d = s.to_dict()
    for key in [
        "hostname",
        "port_number",
        "version",
        "community",
        "auth_protocol",
        "auth_passphrase",
        "security_engine_id",
        "context_engine_id",
        "security_level",
        "context",
        "security_username",
        "privacy_protocol",
        "privacy_passphrase",
        "boots_time",
        "retries",
        "timeout",
    ]:
        assert key in d, f"Missing key: {key}"
    del s


def test_session_to_dict_community_masked():
    """Test to_dict() masks a non-empty community string with '***'."""
    s = Session(version="2c", community="public")
    d = s.to_dict()
    assert d["community"] == "***"
    del s


def test_session_to_dict_empty_community():
    """Test to_dict() returns empty string for an explicitly empty community."""
    s = Session(version="3", community="")
    d = s.to_dict()
    assert d["community"] == ""
    del s


def test_session_to_dict_passphrases_masked():
    """Test to_dict() masks non-empty auth and privacy passphrases."""
    s = Session(
        version="3",
        auth_protocol="MD5",
        auth_passphrase="secret_auth",
        privacy_protocol="AES",
        privacy_passphrase="secret_priv",
        security_level="authPriv",
        security_username="testuser",
    )
    d = s.to_dict()
    assert d["auth_passphrase"] == "***"
    assert d["privacy_passphrase"] == "***"
    del s


def test_session_to_dict_empty_passphrases():
    """Test to_dict() returns empty string when passphrases are not set."""
    s = Session(version="3")
    d = s.to_dict()
    assert d["auth_passphrase"] == ""
    assert d["privacy_passphrase"] == ""
    del s


def test_session_close_marks_closed():
    """Test that explicit close() marks the session as closed."""
    s = Session(version="3")
    assert not s._closed
    s.close()
    assert s._closed
    del s


def test_session_close_idempotent():
    """Test that calling close() multiple times does not raise an error."""
    s = Session(version="3")
    s.close()
    s.close()
    del s


def test_session_context_manager_returns_self():
    """Test that the context manager returns the session itself."""
    with Session(version="3") as s:
        assert isinstance(s, Session)
        assert not s._closed
    assert s._closed


def test_session_context_manager_closes_on_exception():
    """Test that the context manager closes the session even when an exception is raised."""
    s_ref = None
    try:
        with Session(version="3") as s:
            s_ref = s
            raise ValueError("deliberate error")
    except ValueError:
        pass
    assert s_ref is not None
    assert s_ref._closed


def test_session_del_safe_when_closed():
    """Test that __del__ does not raise when session is already closed."""
    s = Session(version="3")
    s.close()
    s.__del__()
    del s


def test_session_del_safe_when_not_closed():
    """Test that __del__ closes the session if not already closed."""
    s = Session(version="3")
    assert not s._closed
    s.__del__()


def test_session_del_safe_when_no_closed_attr():
    """Test that __del__ is safe when _closed attribute doesn't exist."""
    s = Session(version="3")
    del s._closed
    # __del__ calls hasattr(self, "_closed") first; must not raise
    s.__del__()


def test_session_del_swallows_close_exception():
    """Test that __del__ swallows exceptions raised by close()."""
    s = Session(version="3")
    with unittest.mock.patch.object(
        s, "close", side_effect=Exception("simulated close failure")
    ):
        # Must not propagate the exception
        s.__del__()


def test_session_to_dict_optional_prop_attribute_error():
    """Test that to_dict() sets None for optional props that raise AttributeError.

    Uses a subclass to avoid SWIG metaclass interference that occurs when
    unittest.mock.patch.object attempts to restore a class-level property on a
    SWIG-generated base class (the setter is invoked with the class as ``self``
    instead of an instance, causing a TypeError).
    """

    class _BrokenLoadMibsSession(Session):
        @property
        def load_mibs(self):
            raise AttributeError("not implemented")

        @load_mibs.setter
        def load_mibs(self, value):
            # Delegate to base-class setter so __init__ can write the default value
            super()._set_load_mibs(value)

    s = _BrokenLoadMibsSession(version="3")
    d = s.to_dict()
    assert d["load_mibs"] is None


def test_session_version_2_converts_to_2c():
    """Test that integer version 2 is converted to string '2c'."""
    s = Session(version=2)
    assert s.version == "2c"
    del s


def test_session_property_setters():
    """Test that key property setters update the underlying session state."""
    s = Session(version="3")
    s.retries = "5"
    assert s.retries == "5"
    s.timeout = "10"
    assert s.timeout == "10"
    s.community = "private"
    assert s.community == "private"
    s.auth_protocol = "SHA"
    assert s.auth_protocol == "SHA"
    s.security_username = "newuser"
    assert s.security_username == "newuser"
    del s


def test_session_property_setters_extended():
    """Test additional property setters not covered by the basic setter test."""
    s = Session(version="3")

    s.hostname = "newhost"
    assert s.hostname == "newhost"

    s.port_number = "1234"
    assert s.port_number == "1234"

    s.version = "2c"
    assert s.version == "2c"

    s.auth_passphrase = "auth_pass"
    assert s.auth_passphrase == "auth_pass"

    s.security_engine_id = "engine123"
    assert s.security_engine_id == "engine123"

    s.context_engine_id = "ctx_engine"
    assert s.context_engine_id == "ctx_engine"

    s.security_level = "authNoPriv"
    assert s.security_level == "authNoPriv"

    s.context = "mycontext"
    assert s.context == "mycontext"

    s.privacy_protocol = "AES"
    assert s.privacy_protocol == "AES"

    s.privacy_passphrase = "priv_pass"
    assert s.privacy_passphrase == "priv_pass"

    s.boots_time = "1,100"
    assert s.boots_time == "1,100"

    s.load_mibs = "RFC1213-MIB"
    assert s.load_mibs == "RFC1213-MIB"

    s.mib_directories = "/usr/share/snmp/mibs"
    assert s.mib_directories == "/usr/share/snmp/mibs"

    s.print_enums_numerically = True
    assert s.print_enums_numerically is True

    s.print_full_oids = True
    assert s.print_full_oids is True

    s.print_oids_numerically = True
    assert s.print_oids_numerically is True

    s.print_timeticks_numerically = True
    assert s.print_timeticks_numerically is True

    s.set_max_repeaters_to_num = "20"
    assert s.set_max_repeaters_to_num == "20"

    del s


def test_session_new_cli_options_defaults_and_setters():
    s = Session(hostname="localhost", version="2c", community="public")

    assert s.print_oid_suffix_only is False
    assert s.print_oid_module_name is False
    assert s.print_oid_ucd_style is False
    assert s.print_ascii_strings is False
    assert s.print_leading_zero_hex is False
    assert s.print_hex_text is False
    assert s.dont_breakdown_oids is False
    assert s.escape_quotes_in_indexes is False
    assert s.extended_index_format is False
    assert s.dont_print_units is False
    assert s.output_precision == ""
    assert s.regex_oid_matching is False
    assert s.ignore_display_hints is False
    assert s.dont_check_range is False
    assert s.random_access_oid is False
    assert s.read_ucd_style_oid is False
    assert s.oid_suffix == ""
    assert s.oid_prefix == ""
    assert s.mib_allow_underline is False
    assert s.mib_comment_to_eol is False
    assert s.mib_replace_with_latest is False
    assert s.non_repeaters == ""
    assert s.walk_dont_check_lexicographic is False
    assert s.walk_include_requested is False
    assert s.walk_dont_get_requested is False
    assert s.walk_end_oid == ""
    assert s.dont_fix_pdus is False

    s.print_oid_suffix_only = True
    assert s.print_oid_suffix_only is True
    s.print_oid_module_name = True
    assert s.print_oid_module_name is True
    s.print_oid_ucd_style = True
    assert s.print_oid_ucd_style is True
    s.print_ascii_strings = True
    assert s.print_ascii_strings is True
    s.print_leading_zero_hex = True
    assert s.print_leading_zero_hex is True
    s.print_hex_text = True
    assert s.print_hex_text is True
    s.dont_breakdown_oids = True
    assert s.dont_breakdown_oids is True
    s.escape_quotes_in_indexes = True
    assert s.escape_quotes_in_indexes is True
    s.extended_index_format = True
    assert s.extended_index_format is True
    s.dont_print_units = True
    assert s.dont_print_units is True
    s.output_precision = "%.2f"
    assert s.output_precision == "%.2f"

    s.regex_oid_matching = True
    assert s.regex_oid_matching is True
    s.ignore_display_hints = True
    assert s.ignore_display_hints is True
    s.dont_check_range = True
    assert s.dont_check_range is True
    s.random_access_oid = True
    assert s.random_access_oid is True
    s.read_ucd_style_oid = True
    assert s.read_ucd_style_oid is True
    s.oid_suffix = ".0"
    assert s.oid_suffix == ".0"
    s.oid_prefix = ".1.3.6"
    assert s.oid_prefix == ".1.3.6"

    s.mib_allow_underline = True
    assert s.mib_allow_underline is True
    s.mib_comment_to_eol = True
    assert s.mib_comment_to_eol is True
    s.mib_replace_with_latest = True
    assert s.mib_replace_with_latest is True

    s.non_repeaters = 2
    assert s.non_repeaters == "2"
    s.non_repeaters = "3"
    assert s.non_repeaters == "3"
    s.walk_dont_check_lexicographic = True
    assert s.walk_dont_check_lexicographic is True
    s.walk_include_requested = True
    assert s.walk_include_requested is True
    s.walk_dont_get_requested = True
    assert s.walk_dont_get_requested is True
    s.walk_end_oid = "1.3.6.1.2.1.2"
    assert s.walk_end_oid == "1.3.6.1.2.1.2"
    s.dont_fix_pdus = True
    assert s.dont_fix_pdus is True

    d = s.to_dict()
    assert d["output_precision"] == "%.2f"
    assert d["oid_suffix"] == ".0"
    assert d["oid_prefix"] == ".1.3.6"
    assert d["mib_allow_underline"] is True
    assert d["non_repeaters"] == "3"
    assert d["walk_end_oid"] == "1.3.6.1.2.1.2"
    assert d["dont_fix_pdus"] is True

    del s


def test_session_grouped_options_constructor():
    import warnings
    import pytest
    from ezsnmp import Session

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        s = Session(
            connection_options={
                "hostname": "127.0.0.1",
                "port_number": 1161,
                "version": 2,
                "community": "private",
                "retries": 4,
                "timeout": 2,
            },
            v3_options={
                "security_username": "bert",
                "context": "ctx1",
            },
            mib_and_output_options={
                "print_oids_numerically": True,
                "output_precision": "%.2f",
                "mib_allow_underline": True,
            },
            operation_options={
                "set_max_repeaters_to_num": 25,
                "non_repeaters": 2,
                "walk_end_oid": "1.3.6.1.2.1.2",
                "dont_fix_pdus": True,
            },
        )

    assert not [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert s.hostname == "127.0.0.1"
    assert s.port_number == "1161"
    assert s.version == "2c"
    assert s.community == "private"
    assert s.retries == "4"
    assert s.timeout == "2"
    assert s.security_username == "bert"
    assert s.context == "ctx1"
    assert s.print_oids_numerically is True
    assert s.output_precision == "%.2f"
    assert s.mib_allow_underline is True
    assert s._Session__set_max_repeaters_to_num == "25"
    assert s.set_max_repeaters_to_num == ""
    assert s.non_repeaters == "2"
    assert s.walk_end_oid == "1.3.6.1.2.1.2"
    assert s.dont_fix_pdus is True
    s.close()

    with pytest.warns(DeprecationWarning, match="deprecated"):
        legacy = Session(hostname="localhost", version=2, retries=5)
    assert legacy.hostname == "localhost"
    assert legacy.version == "2c"
    assert legacy.retries == "5"
    legacy.close()
