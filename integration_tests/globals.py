""""
A module that contains global variables and functions that are used in the integration tests.
"""

from time import sleep
from random import uniform, randint
from ezsnmp.session import Session
from ezsnmp.exceptions import EzSNMPConnectionError, EzSNMPError
from os import getpid
from threading import get_native_id

SESS_V1_ARGS = {
    "version": 1,
    "hostname": "localhost",
    "remote_port": 11161,
    "community": "public",
}

SESS_V2_ARGS = {
    "version": 2,
    "hostname": "localhost",
    "remote_port": 11161,
    "community": "public",
}

SESS_V3_MD5_DES_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "MD5",
    "security_level": "authPriv",
    "security_username": "initial_md5_des",
    "privacy_protocol": "DES",
    "privacy_password": "priv_pass",
    "auth_password": "auth_pass",
}

SESS_V3_MD5_AES_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "MD5",
    "security_level": "authPriv",
    "security_username": "initial_md5_aes",
    "privacy_protocol": "AES",
    "privacy_password": "priv_pass",
    "auth_password": "auth_pass",
}

SESS_V3_SHA_AES_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "SHA",
    "security_level": "authPriv",
    "security_username": "secondary_sha_aes",
    "privacy_protocol": "AES",
    "privacy_password": "priv_second",
    "auth_password": "auth_second",
}

SESS_V3_SHA_NO_PRIV_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "SHA",
    "security_level": "authNoPriv",
    "security_username": "secondary_sha_no_priv",
    "auth_password": "auth_second",
}

SESS_V3_MD5_NO_PRIV_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "MD5",
    "security_level": "auth_without_privacy",
    "security_username": "initial_md5_no_priv",
    "auth_password": "auth_pass",
}


SESS_TYPES = [SESS_V1_ARGS, SESS_V2_ARGS, SESS_V3_MD5_DES_ARGS, SESS_V3_SHA_AES_ARGS]
SESS_TYPES_NAMES = [
    "SESS_V1_ARGS",
    "SESS_V2_ARGS",
    "SESS_V3_MD5_DES_ARGS",
    "SESS_V3_SHA_AES_ARGS",
]

# Print SNMP information
PRINT_SNMP_INFO = False


# Define a function that will be executed in a separate process or thread
def worker(request_type: str):
    are_we_done = False
    connection_error_counter = 0
    usm_unknown_security_name_counter = 0
    while are_we_done != True:
        try:
            # We sleep to not burden our SNMP Server
            sleep(uniform(0.0, 0.250))
            sess_type = randint(0, len(SESS_TYPES) - 1)
            sess = Session(**SESS_TYPES[sess_type])

            print(
                f"\tWorker using: sess_type - {SESS_TYPES_NAMES[sess_type]} with request_type - {request_type}. With PID: {getpid()} and TID: {get_native_id()}"
            )

            if request_type == "get":
                test = sess.get(
                    [("sysUpTime", "0"), ("sysContact", "0"), ("sysLocation", "0")]
                )

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

            elif request_type == "bulkwalk" and sess.version != 1:
                test = sess.bulkwalk(".")

                # Access the result to ensure that the data is actually retrieved
                for item in test:
                    if PRINT_SNMP_INFO:
                        print(f"\t{item.oid} - {item.value}")

                del test
            
            del sess
            are_we_done = True
            print(f"\tFor a worker with PID: {getpid()} and TID: {get_native_id()}")
            print(f"\t\tconnection_error_counter: {connection_error_counter}")
            print(f"\t\tusm_unknown_security_name_counter: {usm_unknown_security_name_counter}")

        except EzSNMPConnectionError:
            # We bombarded the SNMP server with too many requests...
            # print(
            #     f"\tEzSNMPConnectionError: Connection to the SNMP server was lost. For a worker with PID: {getpid()} and TID: {get_native_id()}"
            # )
            connection_error_counter += 1

        except EzSNMPError as e:
            if str(e) == "USM unknown security name (no such user exists)":
                # print(
                #     f"\tEzSNMPError: {e}. For a worker with PID: {getpid()} and TID: {get_native_id()}"
                # )
                usm_unknown_security_name_counter +=1
            
            else:
                raise e
