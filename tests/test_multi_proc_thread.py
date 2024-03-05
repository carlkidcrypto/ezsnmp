from __future__ import unicode_literals
import pytest
from ezsnmp.session import Session
from ezsnmp.exceptions import EzSNMPConnectionError
from time import sleep
from random import uniform, randint
import concurrent.futures
import multiprocessing
from .conftest import SESS_V1_ARGS, SESS_V2_ARGS, SESS_V3_ARGS

NUM_PROCESSORS = multiprocessing.cpu_count()

print(f"\nNumber of processors: {NUM_PROCESSORS}")


@pytest.mark.parametrize(
    "workers", [1, int(NUM_PROCESSORS / 2), NUM_PROCESSORS, 2 * NUM_PROCESSORS]
)
@pytest.mark.parametrize(
    "jobs", [1, int(NUM_PROCESSORS / 2), NUM_PROCESSORS, 2 * NUM_PROCESSORS]
)
def test_session_threaded(sess_args, workers, jobs):
    def do_work(sess_args):

        try:
            sleep(uniform(0.0, 0.250))
            sess = Session(**sess_args)
            res = sess.get(
                [("sysUpTime", "0"), ("sysContact", "0"), ("sysLocation", "0")]
            )

            assert len(res) == 3

            assert res[0].oid == "sysUpTimeInstance"
            assert res[0].oid_index == ""
            assert int(res[0].value) > 0
            assert res[0].snmp_type == "TICKS"

            assert res[1].oid == "sysContact"
            assert res[1].oid_index == "0"
            assert res[1].value == "G. S. Marzot <gmarzot@marzot.net>"
            assert res[1].snmp_type == "OCTETSTR"

            assert res[2].oid == "sysLocation"
            assert res[2].oid_index == "0"
            assert res[2].value == "my original location"
            assert res[2].snmp_type == "OCTETSTR"

        except EzSNMPConnectionError:
            # We bombarded the SNMP server with too many requets...
            pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(do_work, sess_args) for _ in range(jobs)]
        for future in futures:
            future.result()


class Worker:
    def __init__(self, sess_args):
        self.sess_args = sess_args

    def __call__(self, _):
        try:
            sleep(uniform(0.0, 0.250))
            sess = Session(**self.sess_args)
            res = sess.get(
                [("sysUpTime", "0"), ("sysContact", "0"), ("sysLocation", "0")]
            )

            assert len(res) == 3

            assert res[0].oid == "sysUpTimeInstance"
            assert res[0].oid_index == ""
            assert int(res[0].value) > 0
            assert res[0].snmp_type == "TICKS"

            assert res[1].oid == "sysContact"
            assert res[1].oid_index == "0"
            assert res[1].value == "G. S. Marzot <gmarzot@marzot.net>"
            assert res[1].snmp_type == "OCTETSTR"

            assert res[2].oid == "sysLocation"
            assert res[2].oid_index == "0"
            assert res[2].value == "my original location"
            assert res[2].snmp_type == "OCTETSTR"

        except EzSNMPConnectionError:
            # We bombarded the SNMP server with too many requets...
            pass


@pytest.mark.parametrize(
    "workers", [1, int(NUM_PROCESSORS / 2), NUM_PROCESSORS, 2 * NUM_PROCESSORS]
)
@pytest.mark.parametrize(
    "jobs", [1, int(NUM_PROCESSORS / 2), NUM_PROCESSORS, 2 * NUM_PROCESSORS]
)
def test_session_multiprocess(sess_args, workers, jobs):
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        sess_types = [SESS_V1_ARGS, SESS_V2_ARGS, SESS_V3_ARGS]
        sess_type = randint(0, 2)
        worker = Worker(sess_types[sess_type])
        futures = [executor.submit(worker, sess_args) for _ in range(jobs)]
        for future in futures:
            future.result()
