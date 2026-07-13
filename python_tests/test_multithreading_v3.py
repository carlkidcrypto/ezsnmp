"""
Test for SNMPv3 multithreading/multi-device scenarios.

This test validates that the fix for the usmStatsNotInTimeWindows issue works correctly
when connecting to multiple devices (or simulated devices with different engine IDs)
using the same security username.

Related issue: https://github.com/carlkidcrypto/ezsnmp/issues/[BUG] snmpv3 usmStatsNotInTimeWindows
"""

import os
import shutil
import socket
import subprocess
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Thread

import pytest
from ezsnmp.session import Session
from platform_compat import is_des_supported

SYSTEM_DESCRIPTION_OID = "1.3.6.1.2.1.1.1.0"
SNMP_ENGINE_ID_OID = "1.3.6.1.6.3.10.2.1.1.0"
SECOND_AGENT_ENGINE_ID = "ezsnmp-issue-56-second-agent"


def _allocate_udp_port():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_second_agent(process, session_args, port, timeout=10):
    probe_args = dict(session_args)
    probe_args["hostname"] = "127.0.0.1"
    probe_args["port_number"] = str(port)
    probe_args["timeout"] = "0.2"
    probe_args["retries"] = "0"
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            break

        try:
            engine_id = _get_engine_id(Session(**probe_args))
            if engine_id and process.poll() is None:
                return True, None
        except Exception as error:
            # The socket can be bound before the SNMPv3 user is ready. Retry
            # until the agent answers an authenticated request or exits.
            last_error = error

        time.sleep(0.05)

    return False, last_error


def _capture_process_output(stream, output_lines):
    for line in stream:
        output_lines.append(line)


def _stop_process(process):
    if process.poll() is None:
        try:
            process.terminate()
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        process.wait(timeout=5)


@pytest.fixture
def second_snmpd_port(tmp_path, sess_v3_md5_aes):
    """Run an isolated SNMPv3 agent with a stable, distinct engine ID."""
    snmpd = shutil.which("snmpd")
    if snmpd is None:
        pytest.skip("snmpd executable is unavailable")

    persistent_dir = tmp_path / "persistent"
    persistent_dir.mkdir()
    config_search_dir = tmp_path / "config-search"
    config_search_dir.mkdir()
    config_path = tmp_path / "snmpd.conf"
    persistent_config_path = persistent_dir / "snmpd.conf"
    port = _allocate_udp_port()
    username = sess_v3_md5_aes["security_username"]
    auth_protocol = sess_v3_md5_aes["auth_protocol"]
    auth_passphrase = sess_v3_md5_aes["auth_passphrase"]
    privacy_protocol = sess_v3_md5_aes["privacy_protocol"]
    privacy_passphrase = sess_v3_md5_aes["privacy_passphrase"]
    config_path.write_text(
        "\n".join(
            (
                f"agentAddress udp:127.0.0.1:{port}",
                f"engineID {SECOND_AGENT_ENGINE_ID}",
                f"rouser {username} priv",
                "",
            )
        ),
        encoding="utf-8",
    )
    persistent_config_path.write_text(
        f"createUser {username} {auth_protocol} {auth_passphrase}"
        f" {privacy_protocol} {privacy_passphrase}\n",
        encoding="utf-8",
    )
    persistent_config_path.chmod(0o600)

    environment = os.environ.copy()
    environment["SNMP_PERSISTENT_DIR"] = str(persistent_dir)
    environment["SNMPCONFPATH"] = str(config_search_dir)
    environment.pop("SNMP_PERSISTENT_FILE", None)
    process = None
    output_thread = None
    output_lines = deque(maxlen=200)
    try:
        try:
            process = subprocess.Popen(
                (snmpd, "-f", "-Lo", "-c", str(config_path)),
                cwd=Path(tmp_path),
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            output_thread = Thread(
                target=_capture_process_output,
                args=(process.stdout, output_lines),
                daemon=True,
            )
            output_thread.start()
        except FileNotFoundError:
            pytest.skip("snmpd executable became unavailable during launch")
        except OSError as error:
            pytest.fail(
                f"could not launch second snmpd: {error}",
                pytrace=False,
            )

        started, startup_error = _wait_for_second_agent(process, sess_v3_md5_aes, port)
        if not started:
            _stop_process(process)
            return_code = process.returncode
            output_thread.join(timeout=1)
            output = "".join(output_lines).strip()
            for secret in (auth_passphrase, privacy_passphrase):
                output = output.replace(secret, "<redacted>")
            details = f"; snmpd output: {output}" if output else ""
            probe_details = (
                f"; last probe error: {startup_error!r}"
                if startup_error is not None
                else ""
            )
            pytest.fail(
                "second snmpd did not answer an authenticated request"
                f" (exit code: {return_code}){probe_details}{details}",
                pytrace=False,
            )
        yield port
    finally:
        if process is not None:
            _stop_process(process)
        if output_thread is not None:
            output_thread.join(timeout=1)


def _get_system_description(session):
    result = session.get(SYSTEM_DESCRIPTION_OID)
    assert len(result) == 1
    assert result[0].value
    return result[0].value


def _get_engine_id(session):
    result = session.get(SNMP_ENGINE_ID_OID)
    assert len(result) == 1
    assert result[0].value
    return result[0].value


def _sessions_for_distinct_agents(session_args, second_agent_port, count=1):
    first_agent_args = dict(session_args)
    second_agent_args = dict(session_args)
    second_agent_args["hostname"] = "127.0.0.1"
    second_agent_args["port_number"] = str(second_agent_port)

    credential_keys = (
        "security_username",
        "security_level",
        "auth_protocol",
        "auth_passphrase",
        "privacy_protocol",
        "privacy_passphrase",
    )
    assert all(
        first_agent_args[key] == second_agent_args[key] for key in credential_keys
    )

    first_agent_sessions = [Session(**first_agent_args) for _ in range(count)]
    second_agent_sessions = [Session(**second_agent_args) for _ in range(count)]
    first_engine_id = _get_engine_id(first_agent_sessions[0])
    second_engine_id = _get_engine_id(second_agent_sessions[0])
    assert (
        first_engine_id != second_engine_id
    ), "the existing and second SNMP agents must expose distinct engine IDs"
    return first_agent_sessions, second_agent_sessions


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


def test_issue_56_repeated_alternating_v3_sessions(sess_v3_md5_aes, second_snmpd_port):
    """Issue #56: alternating calls must not corrupt shared SNMPv3 state."""
    first_sessions, second_sessions = _sessions_for_distinct_agents(
        sess_v3_md5_aes, second_snmpd_port
    )
    first_session = first_sessions[0]
    second_session = second_sessions[0]

    first_expected = _get_system_description(first_session)
    second_expected = _get_system_description(second_session)

    # Exercise both call orders repeatedly. Issue #56 reported that one ordering
    # could time out after another Session populated net-snmp's USM cache.
    call_order = (
        (first_session, first_expected),
        (second_session, second_expected),
        (second_session, second_expected),
        (first_session, first_expected),
    )
    for session, expected_value in call_order * 5:
        assert _get_system_description(session) == expected_value


def test_issue_56_concurrent_v3_sessions(sess_v3_md5_aes, second_snmpd_port):
    """Issue #56: concurrent calls on separate Sessions must remain successful."""
    worker_count = 4
    calls_per_worker = 5
    first_sessions, second_sessions = _sessions_for_distinct_agents(
        sess_v3_md5_aes, second_snmpd_port, count=worker_count // 2
    )
    sessions = [
        session for pair in zip(first_sessions, second_sessions) for session in pair
    ]
    expected_values = [_get_system_description(session) for session in sessions]
    start_barrier = Barrier(worker_count)

    def get_repeatedly(session):
        start_barrier.wait()
        return [_get_system_description(session) for _ in range(calls_per_worker)]

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results = list(executor.map(get_repeatedly, sessions))

    assert all(
        value == expected_value
        for expected_value, worker_results in zip(expected_values, results)
        for value in worker_results
    )
