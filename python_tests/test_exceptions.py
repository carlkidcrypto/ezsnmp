"""
Tests to achieve 100% coverage for exception handling and error paths.
"""

import pytest
import faulthandler
from ezsnmp import Session
from ezsnmp.exceptions import (
    GenericError,
    ConnectionError,
    NoSuchInstanceError,
    NoSuchNameError,
    NoSuchObjectError,
    PacketError,
    ParseError,
    TimeoutError,
    UndeterminedTypeError,
    UnknownObjectIDError,
    _handle_error,
)

faulthandler.enable()


# Test all exception classes can be instantiated
def test_generic_error():
    """Test GenericError exception can be raised and caught."""
    with pytest.raises(GenericError) as exc_info:
        raise GenericError("Test generic error")
    assert "Test generic error" in str(exc_info.value)


def test_connection_error():
    """Test ConnectionError exception can be raised and caught."""
    with pytest.raises(ConnectionError) as exc_info:
        raise ConnectionError("Test connection error")
    assert "Test connection error" in str(exc_info.value)


def test_no_such_instance_error():
    """Test NoSuchInstanceError exception can be raised and caught."""
    with pytest.raises(NoSuchInstanceError) as exc_info:
        raise NoSuchInstanceError("Test no such instance error")
    assert "Test no such instance error" in str(exc_info.value)


def test_no_such_name_error():
    """Test NoSuchNameError exception can be raised and caught."""
    with pytest.raises(NoSuchNameError) as exc_info:
        raise NoSuchNameError("Test no such name error")
    assert "Test no such name error" in str(exc_info.value)


def test_no_such_object_error():
    """Test NoSuchObjectError exception can be raised and caught."""
    with pytest.raises(NoSuchObjectError) as exc_info:
        raise NoSuchObjectError("Test no such object error")
    assert "Test no such object error" in str(exc_info.value)


def test_packet_error():
    """Test PacketError exception can be raised and caught."""
    with pytest.raises(PacketError) as exc_info:
        raise PacketError("Test packet error")
    assert "Test packet error" in str(exc_info.value)


def test_parse_error():
    """Test ParseError exception can be raised and caught."""
    with pytest.raises(ParseError) as exc_info:
        raise ParseError("Test parse error")
    assert "Test parse error" in str(exc_info.value)


def test_timeout_error():
    """Test TimeoutError exception can be raised and caught."""
    with pytest.raises(TimeoutError) as exc_info:
        raise TimeoutError("Test timeout error")
    assert "Test timeout error" in str(exc_info.value)


def test_undetermined_type_error():
    """Test UndeterminedTypeError exception can be raised and caught."""
    with pytest.raises(UndeterminedTypeError) as exc_info:
        raise UndeterminedTypeError("Test undetermined type error")
    assert "Test undetermined type error" in str(exc_info.value)


def test_unknown_object_id_error():
    """Test UnknownObjectIDError exception can be raised and caught."""
    with pytest.raises(UnknownObjectIDError) as exc_info:
        raise UnknownObjectIDError("Test unknown object ID error")
    assert "Test unknown object ID error" in str(exc_info.value)


def test_packet_error_null_response_message():
    """Test PacketError with the specific NULL response message from snmp_check_null_response."""
    msg = "received NULL response from snmp_synch_response"
    with pytest.raises(PacketError) as exc_info:
        raise PacketError(msg)
    assert msg in str(exc_info.value)


def test_packet_error_is_subclass_of_generic_error():
    """Test PacketError is a subclass of GenericError."""
    with pytest.raises(GenericError):
        raise PacketError("received NULL response from snmp_synch_response")


# ---------------------------------------------------------------------------
# Direct tests for _handle_error() – each branch is exercised by creating a
# mock exception whose class name contains the C++ type-name token that
# _handle_error() looks for via `str(type(e))`.
# ---------------------------------------------------------------------------


class ConnectionErrorBase(Exception):
    """Mock for the C++ ConnectionErrorBase SWIG wrapper."""


class GenericErrorBase(Exception):
    """Mock for the C++ GenericErrorBase SWIG wrapper."""


class NoSuchInstanceErrorBase(Exception):
    """Mock for the C++ NoSuchInstanceErrorBase SWIG wrapper."""


class NoSuchNameErrorBase(Exception):
    """Mock for the C++ NoSuchNameErrorBase SWIG wrapper."""


class NoSuchObjectErrorBase(Exception):
    """Mock for the C++ NoSuchObjectErrorBase SWIG wrapper."""


class PacketErrorBase(Exception):
    """Mock for the C++ PacketErrorBase SWIG wrapper."""


class ParseErrorBase(Exception):
    """Mock for the C++ ParseErrorBase SWIG wrapper."""


class TimeoutErrorBase(Exception):
    """Mock for the C++ TimeoutErrorBase SWIG wrapper."""


class UndeterminedTypeErrorBase(Exception):
    """Mock for the C++ UndeterminedTypeErrorBase SWIG wrapper."""


class UnknownObjectIDErrorBase(Exception):
    """Mock for the C++ UnknownObjectIDErrorBase SWIG wrapper."""


def test_handle_error_maps_connection_error_base():
    """_handle_error converts ConnectionErrorBase → ConnectionError."""
    with pytest.raises(ConnectionError) as exc_info:
        _handle_error(ConnectionErrorBase("conn failed"))
    assert "conn failed" in str(exc_info.value)


def test_handle_error_maps_generic_error_base():
    """_handle_error converts GenericErrorBase → GenericError."""
    with pytest.raises(GenericError) as exc_info:
        _handle_error(GenericErrorBase("generic failure"))
    assert "generic failure" in str(exc_info.value)


def test_handle_error_maps_no_such_instance_error_base():
    """_handle_error converts NoSuchInstanceErrorBase → NoSuchInstanceError."""
    with pytest.raises(NoSuchInstanceError) as exc_info:
        _handle_error(NoSuchInstanceErrorBase("no such instance"))
    assert "no such instance" in str(exc_info.value)


def test_handle_error_maps_no_such_name_error_base():
    """_handle_error converts NoSuchNameErrorBase → NoSuchNameError."""
    with pytest.raises(NoSuchNameError) as exc_info:
        _handle_error(NoSuchNameErrorBase("no such name"))
    assert "no such name" in str(exc_info.value)


def test_handle_error_maps_no_such_object_error_base():
    """_handle_error converts NoSuchObjectErrorBase → NoSuchObjectError."""
    with pytest.raises(NoSuchObjectError) as exc_info:
        _handle_error(NoSuchObjectErrorBase("no such object"))
    assert "no such object" in str(exc_info.value)


def test_handle_error_maps_packet_error_base():
    """_handle_error converts PacketErrorBase → PacketError."""
    with pytest.raises(PacketError) as exc_info:
        _handle_error(PacketErrorBase("bad packet"))
    assert "bad packet" in str(exc_info.value)


def test_handle_error_maps_parse_error_base():
    """_handle_error converts ParseErrorBase → ParseError."""
    with pytest.raises(ParseError) as exc_info:
        _handle_error(ParseErrorBase("parse failed"))
    assert "parse failed" in str(exc_info.value)


def test_handle_error_maps_timeout_error_base():
    """_handle_error converts TimeoutErrorBase → TimeoutError."""
    with pytest.raises(TimeoutError) as exc_info:
        _handle_error(TimeoutErrorBase("timed out"))
    assert "timed out" in str(exc_info.value)


def test_handle_error_maps_undetermined_type_error_base():
    """_handle_error converts UndeterminedTypeErrorBase → UndeterminedTypeError."""
    with pytest.raises(UndeterminedTypeError) as exc_info:
        _handle_error(UndeterminedTypeErrorBase("undetermined type"))
    assert "undetermined type" in str(exc_info.value)


def test_handle_error_maps_unknown_object_id_error_base():
    """_handle_error converts UnknownObjectIDErrorBase → UnknownObjectIDError."""
    with pytest.raises(UnknownObjectIDError) as exc_info:
        _handle_error(UnknownObjectIDErrorBase("unknown OID"))
    assert "unknown OID" in str(exc_info.value)


def test_handle_error_reraises_unknown_exceptions():
    """_handle_error re-raises exceptions whose type name matches none of the known C++ bases."""

    class SomeUnrelatedError(Exception):
        pass

    original = SomeUnrelatedError("unrecognised error")
    with pytest.raises(SomeUnrelatedError) as exc_info:
        _handle_error(original)
    assert exc_info.value is original
