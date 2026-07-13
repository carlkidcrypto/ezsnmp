"""
Test for SNMPv3 multithreading/multi-device scenarios.

This test validates that the fix for the usmStatsNotInTimeWindows issue works correctly
when connecting to multiple devices (or simulated devices with different engine IDs)
using the same security username.

Related issue: https://github.com/carlkidcrypto/ezsnmp/issues/[BUG] snmpv3 usmStatsNotInTimeWindows
"""

import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from ezsnmp.session import Session
from platform_compat import is_des_supported

SYSTEM_DESCRIPTION_OID = "1.3.6.1.2.1.1.1.0"


def _get_system_description(session):
    result = session.get(SYSTEM_DESCRIPTION_OID)
    assert len(result) == 1
    assert result[0].value
    return result[0].value


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
    res1 = s1.get(
        "1.3.6.1.2.1.1.1.0"
    )  # sysDescr.0 - using numeric OID for test reliability
    assert res1 is not None
    assert len(res1) > 0
    assert res1[0].value is not None

    # Create second session with same credentials (simulating different device with same username)
    s2 = Session(**sess_v3_md5_des)

    # Perform an operation with second session
    # Before fix: This could fail with usmStatsNotInTimeWindows
    # After fix: The cache is cleared before each operation, so it should work
    res2 = s2.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
    assert res2 is not None
    assert len(res2) > 0
    assert res2[0].value is not None

    # Alternate between sessions multiple times
    for i in range(3):
        res1_alt = s1.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
        assert res1_alt is not None

        res2_alt = s2.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
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
    res1 = s1.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
    assert res1 is not None

    # Destroy first session (in Python, just let it go out of scope)
    del s1

    # Small delay to ensure session cleanup
    time.sleep(0.1)

    # Create new session with same credentials
    s2 = Session(**sess_v3_md5_des)

    # This should work without usmStatsNotInTimeWindows error
    res2 = s2.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
    assert res2 is not None
    assert len(res2) > 0

    # Repeat the process
    del s2
    time.sleep(0.1)

    s3 = Session(**sess_v3_md5_des)
    res3 = s3.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
    assert res3 is not None


def test_issue_56_repeated_alternating_v3_sessions(sess_v3_md5_aes):
    """Issue #56: alternating calls must not corrupt shared SNMPv3 state."""
    first_session = Session(**sess_v3_md5_aes)
    second_session = Session(**sess_v3_md5_aes)

    expected_value = _get_system_description(first_session)

    # Exercise both call orders repeatedly. Issue #56 reported that one ordering
    # could time out after another Session populated net-snmp's USM cache.
    for session in (first_session, second_session, second_session, first_session) * 5:
        assert _get_system_description(session) == expected_value


def test_issue_56_concurrent_v3_sessions(sess_v3_md5_aes):
    """Issue #56: concurrent calls on separate Sessions must remain successful."""
    worker_count = 4
    calls_per_worker = 5
    sessions = [Session(**sess_v3_md5_aes) for _ in range(worker_count)]
    start_barrier = Barrier(worker_count)

    def get_repeatedly(session):
        start_barrier.wait()
        return [_get_system_description(session) for _ in range(calls_per_worker)]

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results = list(executor.map(get_repeatedly, sessions))

    expected_value = results[0][0]
    assert all(
        value == expected_value
        for worker_results in results
        for value in worker_results
    )
