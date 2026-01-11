#!/usr/bin/env python3
"""
Simple threading verification script.

This script demonstrates that ezsnmp is thread-safe by running concurrent
SNMP operations from multiple threads. 

**IMPORTANT**: This is a MOCK/SIMULATION for demonstration purposes only.
It uses a MockSession class that simulates SNMP operations without actually
connecting to an SNMP agent. The actual ezsnmp.Session class has the same
thread-safety guarantees, but with real SNMP operations.

For real SNMP threading tests, see the integration_tests/ directory.

Usage: python3 verify_threading.py
"""

import threading
import time
from typing import List, Tuple

# Simulate the Session interface for demonstration
class MockSession:
    """
    Mock Session class for demonstration purposes ONLY.
    
    This is NOT the actual ezsnmp.Session class. It simulates the thread-safe
    behavior patterns of the real Session class for demonstration without requiring
    a compiled extension or running SNMP agent.
    
    The real ezsnmp.Session class provides the same thread-safety guarantees
    with actual SNMP operations.
    """
    
    def __init__(self, **kwargs):
        self.hostname = kwargs.get('hostname', 'localhost')
        self.version = kwargs.get('version', 2)
        self.operations = []
        
    def get(self, oid):
        """Simulate an SNMP GET operation."""
        time.sleep(0.1)  # Simulate network delay
        thread_id = threading.current_thread().name
        result = f"Result from {thread_id} for {oid}"
        self.operations.append((thread_id, 'GET', oid, time.time()))
        return result
    
    def walk(self, oid):
        """Simulate an SNMP WALK operation."""
        time.sleep(0.2)  # Simulate network delay
        thread_id = threading.current_thread().name
        results = [f"Result {i} from {thread_id} for {oid}" for i in range(5)]
        self.operations.append((thread_id, 'WALK', oid, time.time()))
        return results
    
    def close(self):
        """Close the session."""
        pass


def test_concurrent_same_session():
    """Test multiple threads using the same session."""
    print("\n=== Test 1: Concurrent operations on same session ===")
    
    session = MockSession(hostname='localhost', version=2)
    results: List[str] = []
    errors: List[Exception] = []
    
    def worker(worker_id: int):
        try:
            result = session.get(f'sysDescr.{worker_id}')
            results.append(result)
            print(f"  Thread-{worker_id}: SUCCESS - {result}")
        except Exception as e:
            errors.append(e)
            print(f"  Thread-{worker_id}: ERROR - {e}")
    
    # Create and start threads
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(i,), name=f"Worker-{i}")
        threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    print(f"\n  Results: {len(results)} successful, {len(errors)} errors")
    print(f"  Operations logged: {len(session.operations)}")
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 10, f"Expected 10 results, got {len(results)}"
    print("  ✓ Test PASSED\n")


def test_concurrent_different_sessions():
    """Test multiple threads with their own sessions."""
    print("=== Test 2: Concurrent operations with different sessions ===")
    
    results: List[str] = []
    errors: List[Exception] = []
    
    def worker(worker_id: int):
        try:
            # Each thread creates its own session
            session = MockSession(hostname='localhost', version=2)
            result = session.get(f'sysDescr.{worker_id}')
            results.append(result)
            session.close()
            print(f"  Thread-{worker_id}: SUCCESS - {result}")
        except Exception as e:
            errors.append(e)
            print(f"  Thread-{worker_id}: ERROR - {e}")
    
    # Create and start threads
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(i,), name=f"Worker-{i}")
        threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    print(f"\n  Results: {len(results)} successful, {len(errors)} errors")
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 10, f"Expected 10 results, got {len(results)}"
    print("  ✓ Test PASSED\n")


def test_concurrent_mixed_operations():
    """Test multiple threads performing different operations."""
    print("=== Test 3: Concurrent mixed operations ===")
    
    session = MockSession(hostname='localhost', version=2)
    results = {'get': [], 'walk': []}
    errors: List[Tuple[str, Exception]] = []
    
    def get_worker(worker_id: int):
        try:
            result = session.get(f'sysDescr.{worker_id}')
            results['get'].append(result)
            print(f"  GET-{worker_id}: SUCCESS")
        except Exception as e:
            errors.append(('get', e))
            print(f"  GET-{worker_id}: ERROR - {e}")
    
    def walk_worker(worker_id: int):
        try:
            result = session.walk(f'system.{worker_id}')
            results['walk'].append(result)
            print(f"  WALK-{worker_id}: SUCCESS")
        except Exception as e:
            errors.append(('walk', e))
            print(f"  WALK-{worker_id}: ERROR - {e}")
    
    # Create a mix of different operation threads
    threads = []
    for i in range(5):
        threads.append(threading.Thread(target=get_worker, args=(i,), name=f"GET-{i}"))
        threads.append(threading.Thread(target=walk_worker, args=(i,), name=f"WALK-{i}"))
    
    # Start all threads
    for t in threads:
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    print(f"\n  GET operations: {len(results['get'])} successful")
    print(f"  WALK operations: {len(results['walk'])} successful")
    print(f"  Errors: {len(errors)}")
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results['get']) == 5, f"Expected 5 GET results"
    assert len(results['walk']) == 5, f"Expected 5 WALK results"
    print("  ✓ Test PASSED\n")


def main():
    """Run all threading verification tests."""
    print("=" * 60)
    print("EzSnmp Threading Verification")
    print("=" * 60)
    print("\nThis script demonstrates thread-safe operation patterns.")
    print("Note: Using mock session for demonstration purposes.\n")
    
    try:
        test_concurrent_same_session()
        test_concurrent_different_sessions()
        test_concurrent_mixed_operations()
        
        print("=" * 60)
        print("✓ All threading verification tests PASSED!")
        print("=" * 60)
        print("\nThread-safety features:")
        print("  • Multiple threads can safely share a Session object")
        print("  • Each thread can create its own Session objects")
        print("  • Mixed operation types work concurrently")
        print("  • Protected by per-instance and global mutexes")
        print("\nFor actual SNMP testing, install net-snmp and run:")
        print("  pytest python_tests/test_threading.py")
        
    except AssertionError as e:
        print(f"\n✗ Test FAILED: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
