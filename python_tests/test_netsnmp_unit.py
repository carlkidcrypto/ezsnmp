"""
Unit tests for ezsnmp.netsnmp module that cover exception-handling branches
without requiring a live SNMP agent.

Each wrapper function in netsnmp.py has a try/except that calls _handle_error(e)
when the underlying C function raises. These tests mock the C functions to raise
and verify that the Python exceptions are propagated correctly.
"""

import unittest.mock
import pytest
import faulthandler

faulthandler.enable()

import ezsnmp.netsnmp as netsnmp_module
from ezsnmp.exceptions import (
    ConnectionError,
    GenericError,
    NoSuchInstanceError,
    NoSuchNameError,
    NoSuchObjectError,
    PacketError,
    ParseError,
    TimeoutError,
    UndeterminedTypeError,
    UnknownObjectIDError,
)

# ---------------------------------------------------------------------------
# Mock C++ base exception types (mirror the pattern in test_exceptions.py)
# ---------------------------------------------------------------------------


class ConnectionErrorBase(Exception):
    pass


class GenericErrorBase(Exception):
    pass


class PacketErrorBase(Exception):
    pass


# ---------------------------------------------------------------------------
# snmpget
# ---------------------------------------------------------------------------


def test_snmpget_success():
    """snmpget returns the result from the underlying C function on success."""
    sentinel = object()
    with unittest.mock.patch.object(
        netsnmp_module, "netsnmp_snmpget", return_value=sentinel
    ):
        result = netsnmp_module.snmpget([])
    assert result is sentinel


def test_snmpget_propagates_exception():
    """snmpget maps a C++ exception to the corresponding Python exception."""
    with unittest.mock.patch.object(
        netsnmp_module,
        "netsnmp_snmpget",
        side_effect=ConnectionErrorBase("conn failed"),
    ):
        with pytest.raises(ConnectionError) as exc_info:
            netsnmp_module.snmpget([])
    assert "conn failed" in str(exc_info.value)


def test_snmpget_propagates_generic_exception():
    """snmpget re-raises unrecognised exceptions unchanged."""

    class SomeError(Exception):
        pass

    with unittest.mock.patch.object(
        netsnmp_module,
        "netsnmp_snmpget",
        side_effect=SomeError("oops"),
    ):
        with pytest.raises(SomeError):
            netsnmp_module.snmpget([])


# ---------------------------------------------------------------------------
# snmpgetnext
# ---------------------------------------------------------------------------


def test_snmpgetnext_success():
    sentinel = object()
    with unittest.mock.patch.object(
        netsnmp_module, "netsnmp_snmpgetnext", return_value=sentinel
    ):
        result = netsnmp_module.snmpgetnext([])
    assert result is sentinel


def test_snmpgetnext_propagates_exception():
    with unittest.mock.patch.object(
        netsnmp_module,
        "netsnmp_snmpgetnext",
        side_effect=GenericErrorBase("generic"),
    ):
        with pytest.raises(GenericError) as exc_info:
            netsnmp_module.snmpgetnext([])
    assert "generic" in str(exc_info.value)


# ---------------------------------------------------------------------------
# snmpwalk
# ---------------------------------------------------------------------------


def test_snmpwalk_success():
    sentinel = object()
    with unittest.mock.patch.object(
        netsnmp_module, "netsnmp_snmpwalk", return_value=sentinel
    ):
        result = netsnmp_module.snmpwalk([])
    assert result is sentinel


def test_snmpwalk_propagates_exception():
    with unittest.mock.patch.object(
        netsnmp_module,
        "netsnmp_snmpwalk",
        side_effect=PacketErrorBase("bad packet"),
    ):
        with pytest.raises(PacketError) as exc_info:
            netsnmp_module.snmpwalk([])
    assert "bad packet" in str(exc_info.value)


# ---------------------------------------------------------------------------
# snmpbulkget
# ---------------------------------------------------------------------------


def test_snmpbulkget_success():
    sentinel = object()
    with unittest.mock.patch.object(
        netsnmp_module, "netsnmp_snmpbulkget", return_value=sentinel
    ):
        result = netsnmp_module.snmpbulkget([])
    assert result is sentinel


def test_snmpbulkget_propagates_exception():
    with unittest.mock.patch.object(
        netsnmp_module,
        "netsnmp_snmpbulkget",
        side_effect=ConnectionErrorBase("bulk get failed"),
    ):
        with pytest.raises(ConnectionError) as exc_info:
            netsnmp_module.snmpbulkget([])
    assert "bulk get failed" in str(exc_info.value)


# ---------------------------------------------------------------------------
# snmpbulkwalk
# ---------------------------------------------------------------------------


def test_snmpbulkwalk_success():
    sentinel = object()
    with unittest.mock.patch.object(
        netsnmp_module, "netsnmp_snmpbulkwalk", return_value=sentinel
    ):
        result = netsnmp_module.snmpbulkwalk([])
    assert result is sentinel


def test_snmpbulkwalk_propagates_exception():
    with unittest.mock.patch.object(
        netsnmp_module,
        "netsnmp_snmpbulkwalk",
        side_effect=GenericErrorBase("bulk walk failed"),
    ):
        with pytest.raises(GenericError) as exc_info:
            netsnmp_module.snmpbulkwalk([])
    assert "bulk walk failed" in str(exc_info.value)


# ---------------------------------------------------------------------------
# snmpset
# ---------------------------------------------------------------------------


def test_snmpset_success():
    sentinel = object()
    with unittest.mock.patch.object(
        netsnmp_module, "netsnmp_snmpset", return_value=sentinel
    ):
        result = netsnmp_module.snmpset([])
    assert result is sentinel


def test_snmpset_propagates_exception():
    with unittest.mock.patch.object(
        netsnmp_module,
        "netsnmp_snmpset",
        side_effect=PacketErrorBase("set failed"),
    ):
        with pytest.raises(PacketError) as exc_info:
            netsnmp_module.snmpset([])
    assert "set failed" in str(exc_info.value)


# ---------------------------------------------------------------------------
# snmptrap
# ---------------------------------------------------------------------------


def test_snmptrap_success():
    sentinel = object()
    with unittest.mock.patch.object(
        netsnmp_module, "netsnmp_snmptrap", return_value=sentinel
    ):
        result = netsnmp_module.snmptrap([])
    assert result is sentinel


def test_snmptrap_propagates_exception():
    with unittest.mock.patch.object(
        netsnmp_module,
        "netsnmp_snmptrap",
        side_effect=ConnectionErrorBase("trap failed"),
    ):
        with pytest.raises(ConnectionError) as exc_info:
            netsnmp_module.snmptrap([])
    assert "trap failed" in str(exc_info.value)
