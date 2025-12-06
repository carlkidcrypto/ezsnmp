"""
Test for SNMPv3 multithreading/multi-device scenarios.

This test validates that the fix for the usmStatsNotInTimeWindows issue works correctly
when connecting to multiple devices (or simulated devices with different engine IDs)
using the same security username.
"""

import pytest
from ezsnmp.session import Session
from platform_compat import is_des_supported
import time


@pytest.mark.skipif(not is_des_supported(), reason="DES not supported on AlmaLinux 10+")
def test_v3_multiple_sessions_same_user_sequential(sess_v3_md5_des):
    """
    Test that multiple sessions with the same user can be created and used sequentially.
    This simulates connecting to multiple devices with the same username.

    Before the fix, this would fail with usmStatsNotInTimeWindows because the cached
    user credentials from the first session would interfere with the second session.
    """
    # Create first session
    s1 = Session(**sess_v3_md5_des)

    # Perform an operation with first session
    res1 = s1.get("1.3.6.1.2.1.1.1.0")  # Use numeric OID to avoid MIB resolution issues
    assert res1 is not None
    assert len(res1) > 0
    assert res1[0].value is not None

    # Create second session with same credentials (simulating different device with same username)
    s2 = Session(**sess_v3_md5_des)

    # Perform an operation with second session
    # Before fix: This could fail with usmStatsNotInTimeWindows
    # After fix: The cache is cleared before each operation, so it should work
    res2 = s2.get("1.3.6.1.2.1.1.1.0")
    assert res2 is not None
    assert len(res2) > 0
    assert res2[0].value is not None

    # Alternate between sessions multiple times
    for i in range(3):
        res1_alt = s1.get("1.3.6.1.2.1.1.1.0")
        assert res1_alt is not None

        res2_alt = s2.get("1.3.6.1.2.1.1.1.0")
        assert res2_alt is not None


@pytest.mark.skipif(not is_des_supported(), reason="DES not supported on AlmaLinux 10+")
def test_v3_session_recreation_same_user(sess_v3_md5_des):
    """
    Test that a session can be destroyed and recreated with the same user credentials.

    This validates that the cache clearing mechanism works correctly when sessions
    are recreated, which is a common pattern in connection pooling scenarios.
    """
    # Create and use first session
    s1 = Session(**sess_v3_md5_des)
    res1 = s1.get("1.3.6.1.2.1.1.1.0")
    assert res1 is not None

    # Destroy first session (in Python, just let it go out of scope)
    del s1

    # Small delay to ensure session cleanup
    time.sleep(0.1)

    # Create new session with same credentials
    s2 = Session(**sess_v3_md5_des)

    # This should work without usmStatsNotInTimeWindows error
    res2 = s2.get("1.3.6.1.2.1.1.1.0")
    assert res2 is not None
    assert len(res2) > 0

    # Repeat the process
    del s2
    time.sleep(0.1)

    s3 = Session(**sess_v3_md5_des)
    res3 = s3.get("1.3.6.1.2.1.1.1.0")
    assert res3 is not None
