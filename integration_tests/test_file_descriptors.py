#!/usr/bin/env python3

import os
import multiprocessing
from time import time, sleep
from random import randint, uniform
from ezsnmp.session import Session
import sys
import datetime

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

def count_open_fds():
    """Count open file descriptors for the current process (Linux only)."""
    fd_dir = f"/proc/{os.getpid()}/fd"
    try:
        return len(os.listdir(fd_dir))
    except Exception:
        return -1


def work_get_no_close(sess_args, sess_name):
    with open(log_file_path, "a+") as log_file:
        def log_print(*args, **kwargs):
            print(*args, **kwargs)
            print(*args, **kwargs, file=log_file)
            log_file.flush()

        log_print(f"Subprocess PID: {os.getpid()} [{sess_name}]")
        log_print(f"Subprocess PID: Open FDs before: {count_open_fds()} [{sess_name}]")

        for i in range(TOTAL_CALLS):
            session = Session(**sess_args)
            try:
                item = session.get(["sysUpTime.0", "sysContact.0", "sysLocation.0"])
                print(f"\t{item[0].oid} - {item[0].value}")
                print(f"\t{item[1].oid} - {item[1].value}")
                print(f"\t{item[2].oid} - {item[2].value}")
            except Exception as e:
                log_print(f"Error on iteration {i} for: {e}")

        log_print(f"Subprocess PID Open FDs after: {count_open_fds()} [{sess_name}]")


def work_get_close(sess_args, sess_name):
    with open(log_file_path, "a+") as log_file:
        def log_print(*args, **kwargs):
            print(*args, **kwargs)
            print(*args, **kwargs, file=log_file)
            log_file.flush()

        log_print(f"Subprocess PID: {os.getpid()} [{sess_name}]")
        log_print(f"Subprocess PID: Open FDs before: {count_open_fds()} [{sess_name}]")

        for i in range(TOTAL_CALLS):
            session = Session(**sess_args)
            try:
                item = session.get(["sysUpTime.0", "sysContact.0", "sysLocation.0"])
                print(f"\t{item[0].oid} - {item[0].value}")
                print(f"\t{item[1].oid} - {item[1].value}")
                print(f"\t{item[2].oid} - {item[2].value}")
            except Exception as e:
                log_print(f"Error on iteration {i} for: {e}")

            session.close()

        log_print(f"Subprocess PID Open FDs after: {count_open_fds()} [{sess_name}]")


if __name__ == "__main__":
    # Open a log file for writing all output
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
            # Test with work_get_no_close
            log_print(f"\nRunning work_get_no_close: {sess_name}")
            start_time = time()
            test_proc = multiprocessing.Process(target=work_get_no_close, args=(sess_args, sess_name))
            test_proc.start()
            test_proc.join()
            execution_time = time() - start_time

            log_print(f"Parent PID Open FDs after work_get_no_close [{sess_name}]: {count_open_fds()}")
            log_print(f"work_get_no_close [{sess_name}]: Total execution time: {execution_time} seconds")
            avg_time_per_call = execution_time / TOTAL_CALLS
            log_print(f"Average time per SNMP get call (no close) [{sess_name}]: {avg_time_per_call:.6f} seconds")

            # Test with work_get_close
            log_print(f"\nRunning work_get_close: {sess_name}")
            start_time = time()
            test_proc = multiprocessing.Process(target=work_get_close, args=(sess_args, sess_name))
            test_proc.start()
            test_proc.join()
            execution_time = time() - start_time

            log_print(f"Parent PID Open FDs after work_get_close [{sess_name}]: {count_open_fds()}")
            log_print(f"work_get_close [{sess_name}]: Total execution time: {execution_time} seconds")
            avg_time_per_call = execution_time / TOTAL_CALLS
            log_print(f"Average time per SNMP get call (with close) [{sess_name}]: {avg_time_per_call:.6f} seconds")
