"""
Additional tests to improve coverage for specific edge cases.
"""

import pytest
import faulthandler
from ezsnmp import Session

faulthandler.enable()


# Note: walk and bulk_walk tests are already covered in other test files


def test_context_engine_id_getter(sess_v3_md5_des):
    """Test context_engine_id property getter."""
    sess = Session(**sess_v3_md5_des)

    # Get context_engine_id
    engine_id = sess.context_engine_id
    # Engine ID might be empty or a hex string
    assert isinstance(engine_id, str) or engine_id is None


def test_context_getter(sess_v3_md5_des):
    """Test context property getter."""
    sess = Session(**sess_v3_md5_des)

    # Get context
    context = sess.context
    assert isinstance(context, str) or context is None


def test_boots_time_getter(sess_v3_md5_des):
    """Test boots_time property getter."""
    sess = Session(**sess_v3_md5_des)

    # Get boots_time
    boots_time = sess.boots_time
    assert boots_time is not None


def test_security_engine_id_getter(sess_v3_md5_des):
    """Test security_engine_id property getter."""
    sess = Session(**sess_v3_md5_des)

    # Get security_engine_id
    engine_id = sess.security_engine_id
    assert isinstance(engine_id, str) or engine_id is None
