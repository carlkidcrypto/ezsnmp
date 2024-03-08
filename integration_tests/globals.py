""""
A module that contains global variables and functions that are used in the integration tests.
"""

from time import sleep
from random import uniform, randint
from ezsnmp.session import Session
from ezsnmp.exceptions import EzSNMPConnectionError

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
            del test

        elif request_type == "walk":
            test = sess.walk(".")
            del test

    except EzSNMPConnectionError:
        # We bombarded the SNMP server with too many requests...
        pass
