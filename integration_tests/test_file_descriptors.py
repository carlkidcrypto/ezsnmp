#!/usr/bin/env python3

import os
import multiprocessing
from time import time, sleep
from random import randint, uniform
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
MAX_RETRIES = 25
PRINT_SNMP_INFO = False


def count_open_fds():
    """Count open file descriptors for the current process (Linux only)."""
    fd_dir = f"/proc/{os.getpid()}/fd"
    try:
        return len(os.listdir(fd_dir))
    except Exception:
        return -1  # Not available


def work_get_no_close():
    print(f"Subprocess PID: {os.getpid()}")
    print(f"Subprocess PID: Open FDs before: {count_open_fds()}")

    for i in range(100):
        session = Session(**SESS_V2_ARGS)
        try:
            item = session.get(["sysUpTime.0", "sysContact.0", "sysLocation.0"])
            print(f"\t{item[0].oid} - {item[0].value}")
            print(f"\t{item[1].oid} - {item[1].value}")
            print(f"\t{item[2].oid} - {item[2].value}")
        except Exception as e:
            print(f"Error on iteration {i} for: {e}")

    print(f"Subprocess PID Open FDs after: {count_open_fds()}")

def work_get_close():
    print(f"Subprocess PID: {os.getpid()}")
    print(f"Subprocess PID: Open FDs before: {count_open_fds()}")

    for i in range(100):
        session = Session(**SESS_V2_ARGS)
        try:
            item = session.get(["sysUpTime.0", "sysContact.0", "sysLocation.0"])
            print(f"\t{item[0].oid} - {item[0].value}")
            print(f"\t{item[1].oid} - {item[1].value}")
            print(f"\t{item[2].oid} - {item[2].value}")
        except Exception as e:
            print(f"Error on iteration {i} for: {e}")
        
        session.close()

    print(f"Subprocess PID Open FDs after: {count_open_fds()}")

if __name__ == "__main__":
    print(f"Parent PID: {os.getpid()}")
    print(f"Parent PID: Open FDs before: {count_open_fds()}")

    # Test with work_get_no_close
    print("\nRunning work_get_no_close:")
    start_time = time()
    test_proc = multiprocessing.Process(target=work_get_no_close)
    test_proc.start()
    test_proc.join()
    execution_time = time() - start_time

    print(f"Parent PID Open FDs after work_get_no_close: {count_open_fds()}")
    print(f"work_get_no_close: Total execution time: {execution_time} seconds")
    avg_time_per_call = execution_time / 100
    print(f"Average time per SNMP get call (no close): {avg_time_per_call:.6f} seconds")

    # Test with work_get_close
    print("\nRunning work_get_close:")
    start_time = time()
    test_proc = multiprocessing.Process(target=work_get_close)
    test_proc.start()
    test_proc.join()
    execution_time = time() - start_time

    print(f"Parent PID Open FDs after work_get_close: {count_open_fds()}")
    print(f"work_get_close: Total execution time: {execution_time} seconds")
    avg_time_per_call = execution_time / 100
    print(f"Average time per SNMP get call (with close): {avg_time_per_call:.6f} seconds")
