from __future__ import unicode_literals
import pytest
from ezsnmp.session import Session
from ezsnmp.exceptions import EzSNMPConnectionError
from time import sleep
import concurrent.futures
import multiprocessing

NUM_PROCESSORS = multiprocessing.cpu_count()

print(f"Number of processors: {NUM_PROCESSORS}")


@pytest.mark.parametrize("workers", [1, NUM_PROCESSORS / 2, NUM_PROCESSORS])
@pytest.mark.parametrize("jobs", [NUM_PROCESSORS])
def test_session_threaded(sess_args, workers, jobs):
    def do_work(sess_args):

        try:
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
            # Let the client rest. We bombarded it with too many requets...
            sleep(0.250)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(do_work, sess_args) for _ in range(jobs)]
        for future in futures:
            future.result()
