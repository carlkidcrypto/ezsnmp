""""
A module that contains global variables and functions that are used in the integration tests.
"""

from time import sleep
from random import uniform, randint
from ezsnmp.session import Session
from ezsnmp.exceptions import EzSNMPConnectionError, EzSNMPError
from os import getpid
from threading import get_native_id

import os
import sys

sys.path.insert(0, os.path.abspath("../tests/"))

from session_parameters import (
    SESS_V1_ARGS,
    SESS_V2_ARGS,
    SESS_V3_MD5_DES_ARGS,
    SESS_V3_SHA_AES_ARGS,
)

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

        elif request_type == "bulkwalk":
            test = sess.bulkwalk(".")

            # Access the result to ensure that the data is actually retrieved
            for item in test:
                if PRINT_SNMP_INFO:
                    print(f"\t{item.oid} - {item.value}")

            del test

    except EzSNMPConnectionError:
        # We bombarded the SNMP server with too many requests...
        print(
            f"\tEzSNMPConnectionError: Connection to the SNMP server was lost. For a worker with PID: {getpid()} and TID: {get_native_id()}"
        )

    except EzSNMPError as e:
        if str(e) == "USM unknown security name (no such user exists)":
            print(
                f"\tEzSNMPError: {e}. For a worker with PID: {getpid()} and TID: {get_native_id()}"
            )
