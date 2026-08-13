"""
Unit tests for ezsnmp.session.Session that cover early-return branches
in get and get_next methods.

These tests verify the None / empty-list short-circuit paths that return
an empty tuple without reaching the underlying C layer.
No live SNMP agent is required.

Note: SWIG-generated class attributes (SessionBase methods) are read-only
and cannot be patched with unittest.mock.patch.object at the class level.
Exception-propagation branches in walk, bulk_walk, bulk_get and set are
therefore covered by the integration test suite (which runs against a live
SNMP daemon) rather than here.
"""

import pytest
import faulthandler

faulthandler.enable()

from ezsnmp.session import Session


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_session():
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
