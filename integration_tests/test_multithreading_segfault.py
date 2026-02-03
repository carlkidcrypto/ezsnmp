"""
Test to reproduce SIGSEGV (Signal 11) issue in multi-threaded context.

This test creates multiple threads that perform SNMP operations concurrently
to stress-test the MIB tree access code and reproduce the segmentation fault
reported in issue #624.
"""

import pytest
from threading import Thread
from ezsnmp.session import Session
from integration_tests.globals import SESS_V2_ARGS
import time


def snmp_worker(thread_id, iterations=50):
    """
    Worker function that performs SNMP operations in a thread.
    
    Args:
        thread_id: Identifier for this thread
        iterations: Number of SNMP operations to perform
    """
    try:
        sess = Session(**SESS_V2_ARGS)
        
        for i in range(iterations):
            # Perform various SNMP operations that will trigger MIB tree access
            # These operations call print_variable_to_string and print_objid_to_string
            result = sess.get("sysDescr.0")
            assert result.oid == "SNMPv2-MIB::sysDescr"
            assert result.index == "0"
            
            result = sess.get("sysUpTime.0")
            assert result.oid == "DISMAN-EVENT-MIB::sysUpTimeInstance"
            
            # Walk operation also triggers MIB tree access
            results = sess.walk("system")
            assert len(results) > 0
            
    except Exception as e:
        print(f"Thread {thread_id} encountered error: {e}")
        raise


def test_multithreading_concurrent_snmp_operations():
    """
    Test concurrent SNMP operations from multiple threads.
    
    This test reproduces the conditions that can trigger SIGSEGV when
    MIB tree access functions are called without proper mutex protection.
    """
    num_threads = 10
    iterations_per_thread = 20
    
    threads = []
    
    # Create and start threads
    for i in range(num_threads):
        t = Thread(target=snmp_worker, args=(i, iterations_per_thread))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join(timeout=60)  # 60 second timeout per thread
        if t.is_alive():
            raise RuntimeError(f"Thread {t.name} did not complete within timeout")
        
    print(f"Successfully completed {num_threads} threads with {iterations_per_thread} iterations each")


def test_multithreading_rapid_session_creation():
    """
    Test rapid session creation and operations from multiple threads.
    
    This stresses the init_snmp and snmp_shutdown reference counting.
    """
    num_threads = 20
    
    def rapid_session_worker(thread_id):
        try:
            for i in range(5):
                sess = Session(**SESS_V2_ARGS)
                result = sess.get("sysDescr.0")
                assert result.oid == "SNMPv2-MIB::sysDescr"
                sess.close()
        except Exception as e:
            print(f"Thread {thread_id} encountered error: {e}")
            raise
    
    threads = []
    
    # Create and start threads
    for i in range(num_threads):
        t = Thread(target=rapid_session_worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join(timeout=30)
        if t.is_alive():
            raise RuntimeError(f"Thread {t.name} did not complete within timeout")
        
    print(f"Successfully completed {num_threads} threads with rapid session creation")


def test_multithreading_mixed_operations():
    """
    Test mixed SNMP operations (get, walk, bulkwalk) from multiple threads.
    
    This tests various code paths that access the MIB tree.
    """
    num_threads = 8
    
    def mixed_operations_worker(thread_id):
        try:
            sess = Session(**SESS_V2_ARGS)
            
            # Mix different operation types
            for i in range(10):
                if i % 3 == 0:
                    result = sess.get("sysDescr.0")
                    assert result.oid == "SNMPv2-MIB::sysDescr"
                elif i % 3 == 1:
                    results = sess.walk("system")
                    assert len(results) > 0
                else:
                    results = sess.bulkwalk("system")
                    assert len(results) > 0
                    
        except Exception as e:
            print(f"Thread {thread_id} encountered error: {e}")
            raise
    
    threads = []
    
    # Create and start threads
    for i in range(num_threads):
        t = Thread(target=mixed_operations_worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join(timeout=45)
        if t.is_alive():
            raise RuntimeError(f"Thread {t.name} did not complete within timeout")
        
    print(f"Successfully completed {num_threads} threads with mixed operations")


if __name__ == "__main__":
    # Run tests directly for manual testing
    print("Testing multi-threading concurrent SNMP operations...")
    test_multithreading_concurrent_snmp_operations()
    
    print("\nTesting multi-threading rapid session creation...")
    test_multithreading_rapid_session_creation()
    
    print("\nTesting multi-threading mixed operations...")
    test_multithreading_mixed_operations()
    
    print("\nAll multi-threading tests passed!")
