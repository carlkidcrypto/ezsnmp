"""
Unit tests for ezsnmp.session.Session that cover exception-handling branches
in walk, bulk_walk, get, get_next, bulk_get, and set methods.

These tests mock the SessionBase parent methods to raise C++ error types,
verifying that Session correctly propagates them via _handle_error().
No live SNMP agent is required.
"""

import unittest.mock
import pytest
import faulthandler

faulthandler.enable()

from ezsnmp.session import Session
from ezsnmp.exceptions import (
    ConnectionError,
    GenericError,
    PacketError,
    TimeoutError,
)

# ---------------------------------------------------------------------------
# Mock C++ base exception types
# ---------------------------------------------------------------------------


class ConnectionErrorBase(Exception):
    pass


class GenericErrorBase(Exception):
    pass


class PacketErrorBase(Exception):
    pass


class TimeoutErrorBase(Exception):
    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_session():
    return Session(version="3")


# ---------------------------------------------------------------------------
# walk()
# ---------------------------------------------------------------------------


def test_session_walk_propagates_exception():
    """Session.walk() maps a C++ exception to the corresponding Python exception."""
    s = make_session()
    with unittest.mock.patch.object(
        type(s).__bases__[0],
        "walk",
        side_effect=ConnectionErrorBase("walk failed"),
    ):
        with pytest.raises(ConnectionError) as exc_info:
            s.walk(".")
    assert "walk failed" in str(exc_info.value)
    del s


def test_session_walk_propagates_generic():
    s = make_session()
    with unittest.mock.patch.object(
        type(s).__bases__[0],
        "walk",
        side_effect=GenericErrorBase("generic walk"),
    ):
        with pytest.raises(GenericError):
            s.walk("1.3.6.1")
    del s


# ---------------------------------------------------------------------------
# bulk_walk()
# ---------------------------------------------------------------------------


def test_session_bulk_walk_propagates_exception():
    s = make_session()
    with unittest.mock.patch.object(
        type(s).__bases__[0],
        "bulk_walk",
        side_effect=PacketErrorBase("bulk walk failed"),
    ):
        with pytest.raises(PacketError) as exc_info:
            s.bulk_walk(["1.3.6.1"])
    assert "bulk walk failed" in str(exc_info.value)
    del s


def test_session_bulk_walk_finally_resets_max_repeaters():
    """Even when an exception is raised, set_max_repeaters_to_num is reset to ''."""
    s = make_session()
    with unittest.mock.patch.object(
        type(s).__bases__[0],
        "bulk_walk",
        side_effect=GenericErrorBase("err"),
    ):
        with pytest.raises(GenericError):
            s.bulk_walk(["1.3.6.1"])
    assert s.set_max_repeaters_to_num == ""
    del s


def test_session_bulk_walk_none_oids():
    """bulk_walk with oids=None should not raise immediately (None → [])."""
    s = make_session()
    sentinel = object()
    with unittest.mock.patch.object(
        type(s).__bases__[0], "bulk_walk", return_value=sentinel
    ):
        result = s.bulk_walk(None)
    assert result is sentinel
    del s


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


def test_session_get_none_returns_empty_tuple():
    """get(None) returns an empty tuple without hitting the C layer."""
    s = make_session()
    assert s.get(None) == ()
    del s


def test_session_get_empty_list_returns_empty_tuple():
    """get([]) returns an empty tuple without hitting the C layer."""
    s = make_session()
    assert s.get([]) == ()
    del s


def test_session_get_propagates_exception():
    s = make_session()
    with unittest.mock.patch.object(
        type(s).__bases__[0],
        "get",
        side_effect=TimeoutErrorBase("get timed out"),
    ):
        with pytest.raises(TimeoutError) as exc_info:
            s.get(["1.3.6.1.2.1.1.1.0"])
    assert "get timed out" in str(exc_info.value)
    del s


# ---------------------------------------------------------------------------
# get_next()
# ---------------------------------------------------------------------------


def test_session_get_next_none_returns_empty_tuple():
    s = make_session()
    assert s.get_next(None) == ()
    del s


def test_session_get_next_empty_list_returns_empty_tuple():
    s = make_session()
    assert s.get_next([]) == ()
    del s


def test_session_get_next_propagates_exception():
    s = make_session()
    with unittest.mock.patch.object(
        type(s).__bases__[0],
        "get_next",
        side_effect=ConnectionErrorBase("getnext failed"),
    ):
        with pytest.raises(ConnectionError) as exc_info:
            s.get_next(["1.3.6.1.2.1.1.1.0"])
    assert "getnext failed" in str(exc_info.value)
    del s


# ---------------------------------------------------------------------------
# bulk_get()
# ---------------------------------------------------------------------------


def test_session_bulk_get_propagates_exception():
    s = make_session()
    with unittest.mock.patch.object(
        type(s).__bases__[0],
        "bulk_get",
        side_effect=GenericErrorBase("bulk get error"),
    ):
        with pytest.raises(GenericError) as exc_info:
            s.bulk_get(["1.3.6.1"])
    assert "bulk get error" in str(exc_info.value)
    del s


def test_session_bulk_get_finally_resets_max_repeaters():
    """set_max_repeaters_to_num is reset to '' in the finally block even on exception."""
    s = make_session()
    with unittest.mock.patch.object(
        type(s).__bases__[0],
        "bulk_get",
        side_effect=PacketErrorBase("err"),
    ):
        with pytest.raises(PacketError):
            s.bulk_get(["1.3.6.1"])
    assert s.set_max_repeaters_to_num == ""
    del s


def test_session_bulk_get_none_oids():
    """bulk_get with oids=None (→ []) should call super().bulk_get([])."""
    s = make_session()
    sentinel = object()
    with unittest.mock.patch.object(
        type(s).__bases__[0], "bulk_get", return_value=sentinel
    ):
        result = s.bulk_get(None)
    assert result is sentinel
    del s


# ---------------------------------------------------------------------------
# set()
# ---------------------------------------------------------------------------


def test_session_set_none_returns_result():
    """set(None) → [] → calls super().set([]) and returns its result."""
    s = make_session()
    sentinel = object()
    with unittest.mock.patch.object(type(s).__bases__[0], "set", return_value=sentinel):
        result = s.set(None)
    assert result is sentinel
    del s


def test_session_set_propagates_exception():
    s = make_session()
    with unittest.mock.patch.object(
        type(s).__bases__[0],
        "set",
        side_effect=PacketErrorBase("set failed"),
    ):
        with pytest.raises(PacketError) as exc_info:
            s.set(["1.3.6.1", "i", "42"])
    assert "set failed" in str(exc_info.value)
    del s
