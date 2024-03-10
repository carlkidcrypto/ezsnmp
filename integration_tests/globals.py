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
SESS_V3_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "security_level": "authPriv",
    "security_username": "initial",
    "privacy_password": "priv_pass",
    "auth_password": "auth_pass",
}

SESS_TYPES = [SESS_V1_ARGS, SESS_V2_ARGS, SESS_V3_ARGS]

# Print SNMP information
PRINT_SNMP_INFO = False


# Define a function that will be executed in a separate process or thread
def worker(request_type: str):
    try:
        sleep(uniform(0.0, 0.250))
        sess_type = randint(0, 2)
        sess = Session(**SESS_TYPES[sess_type])

        print(
            f"\tWorker using: sess_type - {sess_type} with request_type - {request_type}"
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

    except EzSNMPConnectionError:
        # We bombarded the SNMP server with too many requests...
        print("\tEzSNMPConnectionError: Connection to the SNMP server was lost.")

    except EzSNMPError as e:
        if str(e) == "USM unknown security name (no such user exists)":
            print("\tEzSNMPError: USM unknown security name (no such user exists)")
