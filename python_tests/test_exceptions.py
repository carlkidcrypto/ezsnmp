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