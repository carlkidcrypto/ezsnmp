""""
A module that contains global variables and functions that are used in the integration tests.
"""

from time import sleep
from random import uniform, randint
from ezsnmp.session import Session
from ezsnmp.exceptions import EzSNMPConnectionError, EzSNMPError

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
SESS_V3_MD5_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "MD5",
    "security_level": "authPriv",
    "security_username": "initial",
    "privacy_password": "priv_pass",
    "auth_password": "auth_pass",
}

SESS_V3_SHA_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "SHA",
    "security_level": "authPriv",
    "security_username": "secondary",
    "privacy_password": "priv_second",
    "auth_password": "auth_second",
}

SESS_TYPES = [SESS_V1_ARGS, SESS_V2_ARGS, SESS_V3_MD5_ARGS, SESS_V3_SHA_ARGS]
SESS_TYPES_NAMES = ["SESS_V1_ARGS", "SESS_V2_ARGS", "SESS_V3_MD5_ARGS", "SESS_V3_SHA_ARGS"]

# Print SNMP information
PRINT_SNMP_INFO = False


# Define a function that will be executed in a separate process or thread
def worker(request_type: str):
    try:
        # We sleep to not burden our SNMP Server
        sleep(uniform(0.0, 0.500))
        sess_type = randint(0, len(SESS_TYPES) - 1)
        sess = Session(**SESS_TYPES[sess_type])

        print(
            f"\tWorker using: sess_type - {SESS_TYPES_NAMES[sess_type]} with request_type - {request_type}"
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
        
        elif request_type == "bulkwalk":
            test = sess.bulkwalk(".")

            # Access the result to ensure that the data is actually retrieved
            for item in test:
                if PRINT_SNMP_INFO:
                    print(f"\t{item.oid} - {item.value}")

            del test

    except EzSNMPConnectionError:
        # We bombarded the SNMP server with too many requests...
        print("\tEzSNMPConnectionError: Connection to the SNMP server was lost.")

    except EzSNMPError as e:
        if str(e) == "USM unknown security name (no such user exists)":
            print("\tEzSNMPError: USM unknown security name (no such user exists)")
