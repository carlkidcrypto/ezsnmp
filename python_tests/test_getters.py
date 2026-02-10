"""
Additional tests to improve coverage for specific edge cases.
"""

import pytest
import faulthandler
from ezsnmp import Session

faulthandler.enable()


# Note: walk and bulk_walk tests are already covered in other test files


def test_session_default_constructed_getters_do_not_crash():
    """
    Regression test for GitHub issue #656.

    Calling inherited C++ getters like _get_context() directly on a
    default-constructed Session must not segfault.  Before the fix,
    Session.__init__() did not call super().__init__(), leaving the SWIG
    C++ 'this' pointer uninitialised and causing a segmentation fault.
    """
    s = Session()

    # These are the low-level C++ getters inherited via SWIG.
    # Each one would segfault before the fix.
    assert s._get_hostname() == "localhost"
    assert isinstance(s._get_port_number(), str)
    assert s._get_version() == "3"
    assert s._get_community() == "public"
    assert isinstance(s._get_auth_protocol(), str)
    assert isinstance(s._get_auth_passphrase(), str)
    assert isinstance(s._get_security_engine_id(), str)
    assert isinstance(s._get_context_engine_id(), str)
    assert isinstance(s._get_security_level(), str)
    assert isinstance(s._get_context(), str)
    assert isinstance(s._get_security_username(), str)
    assert isinstance(s._get_privacy_protocol(), str)
    assert isinstance(s._get_privacy_passphrase(), str)
    assert isinstance(s._get_boots_time(), str)
    assert s._get_retries() == "3"
    assert s._get_timeout() == "1"
    assert isinstance(s._get_load_mibs(), str)
    assert isinstance(s._get_mib_directories(), str)
    assert isinstance(s._get_print_enums_numerically(), bool)
    assert isinstance(s._get_print_full_oids(), bool)
    assert isinstance(s._get_print_oids_numerically(), bool)
    assert isinstance(s._get_print_timeticks_numerically(), bool)
    assert isinstance(s._get_set_max_repeaters_to_num(), str)
    args = s._get_args()
    assert isinstance(args, (list, tuple))
    assert len(args) > 0

    del s


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
