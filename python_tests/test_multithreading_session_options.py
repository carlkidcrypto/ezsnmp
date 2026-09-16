from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, BrokenBarrierError

from ezsnmp.session import Session

TEST_OID = ".1.3.6.1.2.1.1.5.0"
EXPECTED_NUMERIC_OID = ".1.3.6.1.2.1.1.5"


def _is_dotted_numeric_oid(oid):
    return oid.startswith(".") and oid.count(".") >= 5 and "::" not in oid


def test_print_oids_numerically_isolated_across_threads():
    iterations = 10
    start_barrier = Barrier(2)
    finish_barrier = Barrier(2)

    def collect_oids(print_oids_numerically):
        session = Session(
            hostname="localhost",
            port_number="11161",
            version="2c",
            community="public",
            load_mibs="ALL",
            print_oids_numerically=print_oids_numerically,
        )
        observed = []
        for _ in range(iterations):
            try:
                start_barrier.wait(timeout=10)
            except BrokenBarrierError as error:
                raise TimeoutError("worker start barrier timed out") from error
            observed.append(session.get(TEST_OID)[0].oid)
            try:
                finish_barrier.wait(timeout=10)
            except BrokenBarrierError as error:
                raise TimeoutError("worker finish barrier timed out") from error
        return observed

    with ThreadPoolExecutor(max_workers=2) as executor:
        textual_future = executor.submit(collect_oids, False)
        numeric_future = executor.submit(collect_oids, True)

    assert numeric_future.result() == [EXPECTED_NUMERIC_OID] * iterations
    assert all(
        not _is_dotted_numeric_oid(oid) for oid in textual_future.result()
    ), textual_future.result()
