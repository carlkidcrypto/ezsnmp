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


def test_load_mibs_getter(sess_v2):
    """Test load_mibs property getter."""
    sess = Session(**sess_v2)

    # Get load_mibs (should be empty string by default)
    load_mibs = sess.load_mibs
    assert isinstance(load_mibs, str)

    # Test setter and getter
    sess.load_mibs = "IF-MIB:IP-MIB"
    assert sess.load_mibs == "IF-MIB:IP-MIB"


def test_mib_directories_getter(sess_v2):
    """Test mib_directories property getter."""
    sess = Session(**sess_v2)

    # Get mib_directories (should be empty string by default)
    mib_directories = sess.mib_directories
    assert isinstance(mib_directories, str)

    # Test setter and getter
    sess.mib_directories = "/usr/share/snmp/mibs"
    assert sess.mib_directories == "/usr/share/snmp/mibs"


def test_print_enums_numerically_getter(sess_v2):
    """Test print_enums_numerically property getter."""
    # Create session with print_enums_numerically=True
    sess_args = sess_v2.copy()
    sess_args["print_enums_numerically"] = True
    sess = Session(**sess_args)

    # Get print_enums_numerically
    assert sess.print_enums_numerically is True

    # Test setter and getter
    sess.print_enums_numerically = False
    assert sess.print_enums_numerically is False


def test_print_full_oids_getter(sess_v2):
    """Test print_full_oids property getter."""
    # Create session with print_full_oids=True
    sess_args = sess_v2.copy()
    sess_args["print_full_oids"] = True
    sess = Session(**sess_args)

    # Get print_full_oids
    assert sess.print_full_oids is True

    # Test setter and getter
    sess.print_full_oids = False
    assert sess.print_full_oids is False


def test_print_oids_numerically_getter(sess_v2):
    """Test print_oids_numerically property getter."""
    # Create session with print_oids_numerically=True
    sess_args = sess_v2.copy()
    sess_args["print_oids_numerically"] = True
    sess = Session(**sess_args)

    # Get print_oids_numerically
    assert sess.print_oids_numerically is True

    # Test setter and getter
    sess.print_oids_numerically = False
    assert sess.print_oids_numerically is False


def test_print_timeticks_numerically_getter(sess_v2):
    """Test print_timeticks_numerically property getter."""
    # Create session with print_timeticks_numerically=True
    sess_args = sess_v2.copy()
    sess_args["print_timeticks_numerically"] = True
    sess = Session(**sess_args)

    # Get print_timeticks_numerically
    assert sess.print_timeticks_numerically is True

    # Test setter and getter
    sess.print_timeticks_numerically = False
    assert sess.print_timeticks_numerically is False


def test_set_max_repeaters_to_num_getter(sess_v2):
    """Test set_max_repeaters_to_num property getter."""
    sess = Session(**sess_v2)

    # Get set_max_repeaters_to_num (default should be "10")
    max_repeaters = sess.set_max_repeaters_to_num
    assert isinstance(max_repeaters, str)

    # Test setter and getter
    sess.set_max_repeaters_to_num = "20"
    assert sess.set_max_repeaters_to_num == "20"
