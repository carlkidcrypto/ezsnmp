"""
A module that contains global variables and functions that are used in the integration tests.
"""

from random import randint, uniform
from ezsnmp.session import Session
from os import getpid
from threading import get_native_id
from time import sleep

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

# Print SNMP information
PRINT_SNMP_INFO = False


# Define a function that will be executed in a separate process or thread
def worker(request_type: str):
    are_we_done = False
    connection_error_counter = 0
    usm_unknown_security_name_counter = 0
    err_gen_ku_key_counter = 0
    netsnmp_parse_args_error_counter = 0
    unknown_oid_error_counter = 0
    no_hostname_specified_error_counter = 0
    generic_error_counter = 0

    while are_we_done != True:
        try:
            # Give our SNMPD server some varing breathing room...
            sleep(uniform(0.0, 2.5))

            sess_type = randint(0, len(SESS_TYPES) - 1)
            sess = Session(**SESS_TYPES[sess_type])

            print(
                f"\tWorker using: sess_type - {SESS_TYPES_NAMES[sess_type]} with request_type - {request_type}. With PID: {getpid()} and TID: {get_native_id()}"
            )

            if request_type == "get":
                test = sess.get(["sysUpTime.0", "sysContact.0", "sysLocation.0"])

                # Access the result to ensure that the data is actually retrieved
                for item in test:
                    if PRINT_SNMP_INFO:
                        print(f"\t{item.oid} - {item.value}")

                del test

            elif request_type == "walk":
                test = sess.walk(".")

                # Access the result to ensure that the data is actually retrieved
                for item in test:
                    if PRINT_SNMP_INFO:
                        print(f"\t{item.oid} - {item.value}")

                del test

            elif request_type == "bulkwalk" and sess.version != "1":
                test = sess.bulk_walk(".")

                # Access the result to ensure that the data is actually retrieved
                for item in test:
                    if PRINT_SNMP_INFO:
                        print(f"\t{item.oid} - {item.value}")

                del test

            del sess
            are_we_done = True

        except Exception as e:

            msg = str(e).lower()

            if (
                "timeout: no response from" in msg
                or "resource temporarily unavailable" in msg
                or "unknown host" in msg
            ):
                connection_error_counter += 1

                if connection_error_counter >= MAX_RETRIES:
                    are_we_done = True

            elif "usm unknown security name (no such user exists)" in msg:
                usm_unknown_security_name_counter += 1

                if usm_unknown_security_name_counter >= MAX_RETRIES:
                    are_we_done = True

            elif (
                "error generating a key (ku) from the supplied authentication pass phrase"
                in msg
            ):
                err_gen_ku_key_counter += 1

                if err_gen_ku_key_counter >= MAX_RETRIES:
                    are_we_done = True

            elif "netsnmp_parse_args_error" in msg:

                netsnmp_parse_args_error_counter += 1

                if netsnmp_parse_args_error_counter >= MAX_RETRIES:
                    are_we_done = True

            elif "unknown object identifier" in msg:
                unknown_oid_error_counter += 1

                if unknown_oid_error_counter >= MAX_RETRIES:
                    are_we_done = True

            elif "no hostname specified" in msg:
                no_hostname_specified_error_counter += 1

                if no_hostname_specified_error_counter >= MAX_RETRIES:
                    are_we_done = True

            else:
                # Count any unexpected error without aborting the worker loop
                generic_error_counter += 1
                # Helpful context for debugging
                try:
                    print(f"sess.args: {sess.args}")
                except Exception:
                    pass
                if generic_error_counter >= MAX_RETRIES:
                    are_we_done = True

    print(f"\tFor a worker with PID: {getpid()} and TID: {get_native_id()}")
    print(f"\t\tconnection_error_counter: {connection_error_counter}")
    print(f"\t\tusm_unknown_security_name_counter: {usm_unknown_security_name_counter}")
    print(f"\t\terr_gen_ku_key_counter: {err_gen_ku_key_counter}")
    print(f"\t\tnetsnmp_parse_args_error_counter: {netsnmp_parse_args_error_counter}")
    print(f"\t\tunknown_oid_error_counter: {unknown_oid_error_counter}")
    print(
        f"\t\tno_hostname_specified_error_counter: {no_hostname_specified_error_counter}"
    )
    print(f"\t\tgeneric_error_counter: {generic_error_counter}")
