from __future__ import unicode_literals
import pytest
from ezsnmp.session import Session
from time import sleep
import concurrent.futures

@pytest.mark.parametrize("workers", [1, 8, 16])
@pytest.mark.parametrize("jobs", [16])
def test_session_threaded(sess_args, workers, jobs):
    def do_work(sess_args):
        sess = Session(**sess_args)
        res = sess.get([("sysUpTime", "0"), ("sysContact", "0"), ("sysLocation", "0")])

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

        sleep(0.100)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(do_work, sess_args) for _ in range(jobs)]
        for future in futures:
            future.result()
