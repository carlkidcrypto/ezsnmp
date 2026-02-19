#!/usr/bin/env python3

import argparse
import datetime
import multiprocessing
import os
from time import time

from ezsnmp.session import Session

SESS_V1_ARGS = {
    "version": "1",
    "hostname": "localhost",
    "port_number": "11161",
    "community": "public",
}
SESS_V2_ARGS = {
    "version": "2c",
    "hostname": "localhost",
    "port_number": "11161",
    "community": "public",
}
SESS_V3_MD5_DES_ARGS = {
    "version": "3",
    "hostname": "localhost",
    "port_number": "11161",
    "auth_protocol": "MD5",
    "security_level": "authPriv",
    "security_username": "initial_md5_des",
    "privacy_protocol": "DES",
    "privacy_passphrase": "priv_pass",
    "auth_passphrase": "auth_pass",
}
SESS_V3_MD5_AES_ARGS = {
    "version": "3",
    "hostname": "localhost",
    "port_number": "11161",
    "auth_protocol": "MD5",
    "security_level": "authPriv",
    "security_username": "initial_md5_aes",
    "privacy_protocol": "AES",
    "privacy_passphrase": "priv_pass",
    "auth_passphrase": "auth_pass",
}
SESS_V3_SHA_AES_ARGS = {
    "version": "3",
    "hostname": "localhost",
    "port_number": "11161",
    "auth_protocol": "SHA",
    "security_level": "authPriv",
    "security_username": "secondary_sha_aes",
    "privacy_protocol": "AES",
    "privacy_passphrase": "priv_second",
    "auth_passphrase": "auth_second",
}
SESS_V3_SHA_NO_PRIV_ARGS = {
    "version": "3",
    "hostname": "localhost",
    "port_number": "11161",
    "auth_protocol": "SHA",
    "security_level": "authNoPriv",
    "security_username": "secondary_sha_no_priv",
    "auth_passphrase": "auth_second",
}
SESS_V3_MD5_NO_PRIV_ARGS = {
    "version": "3",
    "hostname": "localhost",
    "port_number": "11161",
    "auth_protocol": "MD5",
    "security_level": "authNoPriv",
    "security_username": "initial_md5_no_priv",
    "auth_passphrase": "auth_pass",
}
SESS_TYPES = [
    SESS_V1_ARGS,
    SESS_V2_ARGS,
    SESS_V3_MD5_DES_ARGS,
    SESS_V3_MD5_AES_ARGS,
    SESS_V3_SHA_AES_ARGS,
    SESS_V3_SHA_NO_PRIV_ARGS,
    SESS_V3_MD5_NO_PRIV_ARGS,
]
SESS_TYPES_NAMES = [
    "SESS_V1_ARGS",
    "SESS_V2_ARGS",
    "SESS_V3_MD5_DES_ARGS",
    "SESS_V3_MD5_AES_ARGS",
    "SESS_V3_SHA_AES_ARGS",
    "SESS_V3_SHA_NO_PRIV_ARGS",
    "SESS_V3_MD5_NO_PRIV_ARGS",
]

TOTAL_CALLS = 100

GET_OIDS = ["sysUpTime.0", "sysContact.0", "sysLocation.0"]
GETNEXT_OIDS = ["sysUpTime.0", "sysContact.0", "sysLocation.0"]
BULK_OIDS = ["sysUpTime.0", "sysContact.0", "sysLocation.0"]
WALK_BASE_OID = "1.3.6.1.2.1.1"
SET_OID = ".1.3.6.1.2.1.1.6.0"

OPERATIONS = [
    "get",
    "get_next",
    "walk",
    "bulk_get",
    "bulk_walk",
    "set",
]


def count_open_fds():
    """Count open file descriptors for the current process (Linux only)."""
    fd_dir = f"/proc/{os.getpid()}/fd"
    try:
        return len(os.listdir(fd_dir))
    except Exception:
        return -1


def should_skip_operation(operation, sess_args):
    version = str(sess_args.get("version", ""))
    if operation in {"bulk_get", "bulk_walk"} and version == "1":
        return True
    return False


def run_operation(session, operation):
    if operation == "get":
        return session.get(GET_OIDS)
    if operation == "get_next":
        return session.get_next(GETNEXT_OIDS)
    if operation == "walk":
        return session.walk(WALK_BASE_OID)
    if operation == "bulk_get":
        return session.bulk_get(BULK_OIDS)
    if operation == "bulk_walk":
        return session.bulk_walk([WALK_BASE_OID])
    if operation == "set":
        current = session.get([SET_OID])
        current_value = current[0].value if current else ""
        return session.set([SET_OID, "s", current_value])
    raise ValueError(f"Unknown operation: {operation}")


def work_op_no_close(sess_args, sess_name, operation, log_file_path):
    with open(log_file_path, "a+") as log_file:

        def log_print(*args, **kwargs):
            print(*args, **kwargs)
            print(*args, **kwargs, file=log_file)
            log_file.flush()

        log_print(f"Subprocess PID: {os.getpid()} [{sess_name}] [{operation}]")
        log_print(
            f"Subprocess PID: Open FDs before: {count_open_fds()} [{sess_name}] [{operation}]"
        )

        if should_skip_operation(operation, sess_args):
            log_print(f"Skipping operation [{operation}] for [{sess_name}]")
            log_print(
                f"Subprocess PID Open FDs after: {count_open_fds()} [{sess_name}] [{operation}]"
            )
            return

        for i in range(TOTAL_CALLS):
            session = Session(**sess_args)
            try:
                run_operation(session, operation)
            except Exception as e:
                log_print(f"Error on iteration {i} for [{operation}]: {e}")

        log_print(
            f"Subprocess PID Open FDs after: {count_open_fds()} [{sess_name}] [{operation}]"
        )


def work_op_close(sess_args, sess_name, operation, log_file_path):
    with open(log_file_path, "a+") as log_file:

        def log_print(*args, **kwargs):
            print(*args, **kwargs)
            print(*args, **kwargs, file=log_file)
            log_file.flush()

        log_print(f"Subprocess PID: {os.getpid()} [{sess_name}] [{operation}]")
        log_print(
            f"Subprocess PID: Open FDs before: {count_open_fds()} [{sess_name}] [{operation}]"
        )

        if should_skip_operation(operation, sess_args):
            log_print(f"Skipping operation [{operation}] for [{sess_name}]")
            log_print(
                f"Subprocess PID Open FDs after: {count_open_fds()} [{sess_name}] [{operation}]"
            )
            return

        for i in range(TOTAL_CALLS):
            session = Session(**sess_args)
            try:
                run_operation(session, operation)
            except Exception as e:
                log_print(f"Error on iteration {i} for [{operation}]: {e}")

            session.close()

        log_print(
            f"Subprocess PID Open FDs after: {count_open_fds()} [{sess_name}] [{operation}]"
        )


if __name__ == "__main__":
    # Open a log file for writing all output
    # Optional CLI argument: first positional arg may be a path or a directory.
    # If it's a directory, write a consolidated 'snmp_fd_test_output.log' inside it.
    # Usage: python3 test_file_descriptors.py [LOG_PATH_OR_DIR]
    parser = argparse.ArgumentParser(description="SNMP FD test logger")
    parser.add_argument(
        "log",
        nargs="?",
        help="Path to log file or directory to place snmp_fd_test_output.log",
        default=None,
    )
    args = parser.parse_args()

    log_file_path = None
    if args.log:
        if os.path.isdir(args.log):
            log_file_path = os.path.join(args.log, "snmp_fd_test_output.log")
        else:
            log_file_path = args.log

    if not log_file_path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = f"snmp_fd_test_output_{timestamp}.log"

    with open(log_file_path, "a+") as log_file:

        def log_print(*args, **kwargs):
            print(*args, **kwargs)
            print(*args, **kwargs, file=log_file)
            log_file.flush()

        log_print(f"Parent PID: {os.getpid()}")
        parent_fds_before = count_open_fds()
        log_print(f"Parent PID: Open FDs before: {parent_fds_before}")

        for sess_args, sess_name in zip(SESS_TYPES, SESS_TYPES_NAMES):
            for operation in OPERATIONS:
                # Test with work_op_no_close
                log_print(f"\nRunning work_op_no_close: {operation} {sess_name}")
                start_time = time()
                test_proc = multiprocessing.Process(
                    target=work_op_no_close,
                    args=(sess_args, sess_name, operation, log_file_path),
                )
                test_proc.start()
                test_proc.join()
                execution_time = time() - start_time

                log_print(
                    "Parent PID Open FDs after work_op_no_close "
                    f"[{sess_name}] [{operation}]: {count_open_fds()}"
                )
                log_print(
                    "work_op_no_close "
                    f"[{sess_name}] [{operation}]: Total execution time: {execution_time} seconds"
                )
                avg_time_per_call = execution_time / TOTAL_CALLS
                log_print(
                    "Average time per SNMP call (no close) "
                    f"[{sess_name}] [{operation}]: {avg_time_per_call:.6f} seconds"
                )

                # Test with work_op_close
                log_print(f"\nRunning work_op_close: {operation} {sess_name}")
                start_time = time()
                test_proc = multiprocessing.Process(
                    target=work_op_close,
                    args=(sess_args, sess_name, operation, log_file_path),
                )
                test_proc.start()
                test_proc.join()
                execution_time = time() - start_time

                log_print(
                    "Parent PID Open FDs after work_op_close "
                    f"[{sess_name}] [{operation}]: {count_open_fds()}"
                )
                log_print(
                    "work_op_close "
                    f"[{sess_name}] [{operation}]: Total execution time: {execution_time} seconds"
                )
                avg_time_per_call = execution_time / TOTAL_CALLS
                log_print(
                    "Average time per SNMP call (with close) "
                    f"[{sess_name}] [{operation}]: {avg_time_per_call:.6f} seconds"
                )
