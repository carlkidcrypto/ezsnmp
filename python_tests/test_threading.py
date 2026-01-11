"""
Threading and multiprocessing tests for ezsnmp.

This module tests the thread-safety and multiprocess-safety of ezsnmp operations.
It ensures that:
1. Multiple threads can safely use the same Session object
2. Multiple threads can create and use their own Session objects
3. Multiple processes can use ezsnmp independently
4. SNMPv3 user cache is thread-safe (fixes issue #45)
"""

import pytest
import threading
import multiprocessing
import time
from session_parameters import SESS_V2_ARGS, SESS_V3_MD5_DES_ARGS
from ezsnmp import Session


class TestThreadSafety:
    """Test thread-safety of ezsnmp Session objects."""

    def test_concurrent_reads_same_session(self):
        """Test multiple threads reading from the same session concurrently."""
        session = Session(**SESS_V2_ARGS)
        results = []
        errors = []

        def worker():
            try:
                # Perform multiple SNMP operations
                result = session.get("sysDescr.0")
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads using the same session
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Verify all operations succeeded
        assert len(results) == 10

    def test_concurrent_reads_different_sessions(self):
        """Test multiple threads with their own sessions."""
        results = []
        errors = []

        def worker():
            try:
                # Each thread creates its own session
                session = Session(**SESS_V2_ARGS)
                result = session.get("sysDescr.0")
                results.append(result)
                session.close()
            except Exception as e:
                errors.append(e)

        # Create multiple threads with their own sessions
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Verify all operations succeeded
        assert len(results) == 10

    def test_concurrent_walk_operations(self):
        """Test multiple threads performing walk operations."""
        session = Session(**SESS_V2_ARGS)
        results = []
        errors = []

        def worker(oid):
            try:
                result = session.walk(oid)
                results.append(len(result))
            except Exception as e:
                errors.append(e)

        # Create threads performing different walk operations
        threads = []
        oids = ["system", "interfaces", "ip", "tcp", "udp"]
        for oid in oids:
            t = threading.Thread(target=worker, args=(oid,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Verify all operations returned results
        assert len(results) == 5
        assert all(count > 0 for count in results)

    def test_concurrent_mixed_operations(self):
        """Test multiple threads performing different SNMP operations."""
        session = Session(**SESS_V2_ARGS)
        results = {"get": [], "walk": [], "bulkwalk": []}
        errors = []

        def get_worker():
            try:
                result = session.get("sysDescr.0")
                results["get"].append(result)
            except Exception as e:
                errors.append(("get", e))

        def walk_worker():
            try:
                result = session.walk("system")
                results["walk"].append(len(result))
            except Exception as e:
                errors.append(("walk", e))

        def bulkwalk_worker():
            try:
                result = session.bulk_walk("interfaces")
                results["bulkwalk"].append(len(result))
            except Exception as e:
                errors.append(("bulkwalk", e))

        # Create a mix of different operation threads
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=get_worker))
            threads.append(threading.Thread(target=walk_worker))
            threads.append(threading.Thread(target=bulkwalk_worker))

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Verify all operations succeeded
        assert len(results["get"]) == 5
        assert len(results["walk"]) == 5
        assert len(results["bulkwalk"]) == 5

    @pytest.mark.skipif(
        not hasattr(Session(**SESS_V3_MD5_DES_ARGS), "security_username"),
        reason="SNMPv3 not available",
    )
    def test_snmpv3_concurrent_operations(self):
        """Test SNMPv3 operations with concurrent threads (issue #45)."""
        results = []
        errors = []

        def worker():
            try:
                # Each thread creates its own SNMPv3 session
                session = Session(**SESS_V3_MD5_DES_ARGS)
                result = session.get("sysDescr.0")
                results.append(result)
                session.close()
            except Exception as e:
                errors.append(e)

        # Create multiple threads with SNMPv3 sessions
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify no errors occurred (this was failing in issue #45)
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Verify all operations succeeded
        assert len(results) == 10

    def test_session_parameter_modification_thread_safety(self):
        """Test that modifying session parameters is thread-safe."""
        session = Session(**SESS_V2_ARGS)
        errors = []

        def modifier_worker(value):
            try:
                # Modify session parameters concurrently
                session.timeout = value
                session.retries = value
            except Exception as e:
                errors.append(e)

        def reader_worker():
            try:
                # Read while others are modifying
                result = session.get("sysDescr.0")
                return result
            except Exception as e:
                errors.append(e)

        # Create threads that modify and read concurrently
        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=modifier_worker, args=(i + 1,)))
            threads.append(threading.Thread(target=reader_worker))

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"


class TestMultiprocessing:
    """Test multiprocess-safety of ezsnmp."""

    def test_concurrent_processes_different_sessions(self):
        """Test multiple processes with their own sessions."""

        def worker(queue):
            try:
                session = Session(**SESS_V2_ARGS)
                result = session.get("sysDescr.0")
                queue.put(("success", result))
                session.close()
            except Exception as e:
                queue.put(("error", str(e)))

        # Create a queue for results
        queue = multiprocessing.Queue()

        # Create multiple processes
        processes = []
        for _ in range(5):
            p = multiprocessing.Process(target=worker, args=(queue,))
            processes.append(p)
            p.start()

        # Wait for all processes to complete
        for p in processes:
            p.join()

        # Collect results
        results = []
        errors = []
        while not queue.empty():
            status, data = queue.get()
            if status == "success":
                results.append(data)
            else:
                errors.append(data)

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Verify all operations succeeded
        assert len(results) == 5

    def test_multiprocess_walk_operations(self):
        """Test walk operations in multiple processes."""

        def worker(oid, queue):
            try:
                session = Session(**SESS_V2_ARGS)
                result = session.walk(oid)
                queue.put(("success", len(result)))
                session.close()
            except Exception as e:
                queue.put(("error", str(e)))

        # Create a queue for results
        queue = multiprocessing.Queue()

        # Create processes for different OIDs
        processes = []
        oids = ["system", "interfaces", "ip", "tcp", "udp"]
        for oid in oids:
            p = multiprocessing.Process(target=worker, args=(oid, queue))
            processes.append(p)
            p.start()

        # Wait for all processes to complete
        for p in processes:
            p.join()

        # Collect results
        results = []
        errors = []
        while not queue.empty():
            status, data = queue.get()
            if status == "success":
                results.append(data)
            else:
                errors.append(data)

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Verify all operations returned results
        assert len(results) == 5
        assert all(count > 0 for count in results)


class TestStressTest:
    """Stress tests to verify thread-safety under heavy load."""

    def test_high_concurrency_stress(self):
        """Stress test with many concurrent threads."""
        session = Session(**SESS_V2_ARGS)
        results = []
        errors = []

        def worker(thread_id):
            try:
                # Perform multiple operations per thread
                for _ in range(5):
                    result = session.get("sysDescr.0")
                    results.append((thread_id, result))
            except Exception as e:
                errors.append((thread_id, e))

        # Create many concurrent threads
        threads = []
        num_threads = 50
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Verify all operations succeeded
        assert len(results) == num_threads * 5

    @pytest.mark.slow
    def test_long_running_concurrent_operations(self):
        """Test thread-safety with long-running concurrent operations."""
        session = Session(**SESS_V2_ARGS)
        results = []
        errors = []

        def worker():
            try:
                # Perform multiple walks (long-running operations)
                for oid in ["system", "interfaces"]:
                    result = session.walk(oid)
                    results.append(len(result))
                    time.sleep(0.1)  # Simulate some processing
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # Verify all operations succeeded
        assert len(results) == 20  # 10 threads * 2 operations each
