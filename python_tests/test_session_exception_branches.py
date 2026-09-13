"""
Unit tests for ezsnmp.session.Session that cover early-return branches
in get and get_next methods, None-normalisation branches in bulk_walk /
bulk_get / set, and the close() exception-propagation path.

These tests verify paths that return without reaching the underlying C layer
or that are reachable via instance-level mocking.  No live SNMP agent is
required.

Note: SWIG-generated class attributes (SessionBase methods) are read-only
and cannot be patched with unittest.mock.patch.object at the class level.
Exception-propagation branches in walk, bulk_walk, bulk_get and set that
exercise the C++ layer are therefore covered by the integration test suite
(which runs against a live SNMP daemon) rather than here.
"""

import unittest.mock

import pytest
import faulthandler

faulthandler.enable()

from ezsnmp.exceptions import ConnectionError
from ezsnmp.session import Session

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_session():
    """Return a default Session for unit testing (no live agent required)."""
    return Session(version="3")


# ---------------------------------------------------------------------------
# get() — early-return paths that never reach the C layer
# ---------------------------------------------------------------------------


def test_session_get_none_returns_empty_tuple():
    """get(None) returns an empty tuple without hitting the C layer."""
    with make_session() as s:
        assert s.get(None) == ()


def test_session_get_empty_list_returns_empty_tuple():
    """get([]) returns an empty tuple without hitting the C layer."""
    with make_session() as s:
        assert s.get([]) == ()


# ---------------------------------------------------------------------------
# get_next() — early-return paths that never reach the C layer
# ---------------------------------------------------------------------------


def test_session_get_next_none_returns_empty_tuple():
    """get_next(None) returns an empty tuple without hitting the C layer."""
    with make_session() as s:
        assert s.get_next(None) == ()


def test_session_get_next_empty_list_returns_empty_tuple():
    """get_next([]) returns an empty tuple without hitting the C layer."""
    with make_session() as s:
        assert s.get_next([]) == ()


# ---------------------------------------------------------------------------
# bulk_walk() — None normalisation branch (oids = [])
# ---------------------------------------------------------------------------


def test_session_bulk_walk_none_normalises_to_empty_list():
    """bulk_walk(None) normalises oids before calling the C layer."""
    captured_oids = []
    s = make_session()
    with unittest.mock.patch.object(s, "_bulk_walk", return_value=()) as bulk_walk:
        result = s.bulk_walk(None)
        captured_oids.extend(bulk_walk.call_args.args)
    assert result == ()
    assert captured_oids == [[]]
    s.close()


# ---------------------------------------------------------------------------
# bulk_get() — None normalisation branch (oids = [])
# ---------------------------------------------------------------------------


def test_session_bulk_get_none_normalisation():
    """bulk_get(None) converts None to [] before calling the C layer."""
    s = make_session()
    with unittest.mock.patch.object(s, "_bulk_get", return_value=()) as bulk_get:
        result = s.bulk_get(None)
    assert result == ()
    bulk_get.assert_called_once_with([])
    s.close()


# ---------------------------------------------------------------------------
# set() — None normalisation branch (oids = [])
# ---------------------------------------------------------------------------


def test_session_set_none_normalisation():
    """set(None) converts None to [] before calling the C layer."""
    s = make_session()
    with unittest.mock.patch.object(s, "_set", return_value=()) as set_method:
        result = s.set(None)
    assert result == ()
    set_method.assert_called_once_with([])
    s.close()


# ---------------------------------------------------------------------------
# close() — exception-propagation branch
# ---------------------------------------------------------------------------


def test_session_close_propagates_known_exception():
    """close() calls _handle_error when super()._close() raises a known C++ error.

    When _close() raises an exception whose class-name embeds a recognised
    C++ base name, _handle_error() converts it to the matching Python exception.
    This test covers the ``except Exception as e: _handle_error(e)`` branch
    inside Session.close().
    """

    class ConnectionErrorBase(Exception):
        """Mock for the C++ ConnectionErrorBase SWIG wrapper."""

    s = make_session()
    # Manually mark as not closed so the close() body is entered.
    s._closed = False

    with unittest.mock.patch.object(
        s, "_close_session", side_effect=ConnectionErrorBase("mock close failure")
    ):
        with pytest.raises(ConnectionError) as exc_info:
            s.close()
    assert "mock close failure" in str(exc_info.value)


def test_session_close_propagates_unknown_exception():
    """close() re-raises unrecognised exceptions via _handle_error.

    When _close() raises an exception whose class-name does not match any
    known C++ base, _handle_error re-raises it unchanged.
    """

    class SomeUnrelatedError(Exception):
        pass

    s = make_session()
    s._closed = False

    with unittest.mock.patch.object(
        s, "_close_session", side_effect=SomeUnrelatedError("unexpected")
    ):
        with pytest.raises(SomeUnrelatedError):
            s.close()
