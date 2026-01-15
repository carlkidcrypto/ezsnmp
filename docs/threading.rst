Concurrency in EzSnmp: Threading vs Multiprocessing
====================================================

Overview
--------

EzSnmp supports concurrent SNMP operations through both threading and multiprocessing, but with important limitations due to the underlying Net-SNMP C library.

**TL;DR**: Use **multiprocessing** for production workloads. Threading has significant limitations due to Net-SNMP's architecture.

Threading Limitations
---------------------

⚠️ **Important**: The underlying Net-SNMP C library has significant threading limitations due to extensive use of global state. While EzSnmp provides thread-safety protections, these cannot fully compensate for Net-SNMP's architecture.

Known Threading Issues
~~~~~~~~~~~~~~~~~~~~~~

1. **MIB Parser Corruption**: The MIB parsing subsystem uses global state that can become corrupted under concurrent access
2. **OID Cache Contention**: OID-to-name resolution uses a shared cache that may produce incorrect results
3. **File Descriptor Conflicts**: Persistent storage and file operations may fail with "Bad file descriptor" errors
4. **Memory Corruption**: Internal data structures may be corrupted, leading to segmentation faults

These issues occur even with mutex protection because Net-SNMP's internal code paths access shared state without synchronization.

Limited Thread Support
~~~~~~~~~~~~~~~~~~~~~~~

While basic threading works for simple scenarios, **production workloads should use multiprocessing** (see below).

If you must use threading:

.. code-block:: python

    from ezsnmp import Session
    import threading

    # Works for simple cases, but may fail under load
    def worker():
        # Create a new session per thread
        session = Session(hostname='localhost', community='public', version=2)
        try:
            result = session.get('sysDescr.0')
            print(result.value)
        finally:
            session.close()

    # Keep concurrency low (≤4 threads) to reduce failures
    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

**Limitations**:
- Expect occasional failures under high concurrency (>4 threads)
- MIB parsing errors may occur
- SNMPv3 operations are more likely to fail
- Not recommended for production use

Multiprocessing (✅ Recommended)
---------------------------------

✅ **Recommended Approach**: EzSnmp is fully multiprocess-safe and this is the **recommended way** to achieve concurrency.

Each process has its own independent copy of the Net-SNMP library state, eliminating all race conditions and data corruption issues:

.. code-block:: python

    from multiprocessing import Process, Queue
    from ezsnmp import Session
    import os

    def worker(queue, worker_id):
        """Worker process that performs SNMP operations."""
        session = Session(hostname='localhost', community='public', version=2)
        try:
            result = session.get('sysDescr.0')
            queue.put({
                'worker_id': worker_id,
                'pid': os.getpid(),
                'value': result.value
            })
        finally:
            session.close()

    # Create a queue for collecting results
    results = Queue()
    
    # Spawn worker processes (can safely use many)
    processes = [
        Process(target=worker, args=(results, i))
        for i in range(20)  # High concurrency works perfectly
    ]
    
    for p in processes:
        p.start()
    
    for p in processes:
        p.join()
    
    # Collect results
    while not results.empty():
        result = results.get()
        print(f"Worker {result['worker_id']} (PID {result['pid']}): {result['value']}")

**Advantages**:
- ✅ **Reliable**: No race conditions or corruption issues
- ✅ **Scalable**: Can use many processes without failures
- ✅ **Production-ready**: Tested and stable
- ✅ **True Parallelism**: No GIL limitations

**Use Cases**:
- Polling multiple devices
- Bulk SNMP operations
- Production monitoring systems
- Any scenario requiring high reliability

Implementation Details
----------------------

EzSnmp provides thread-safety protections, but these are limited by Net-SNMP's architecture:

1. **Per-Instance Mutexes**: Each ``SessionBase`` object has its own mutex protecting instance state

2. **Global Net-SNMP Mutex**: A global mutex serializes critical Net-SNMP operations:
   - Library initialization
   - MIB parsing
   - Session creation/destruction
   - SNMPv3 user cache access

3. **GIL Release**: SWIG bindings release the Python GIL during C++ calls for parallelism

**Limitations**: Despite these protections, Net-SNMP's internal code paths access shared global state without locks, causing the threading issues described above. Multiprocessing avoids these issues entirely by giving each process its own Net-SNMP state.

Why Threading Is Limited
~~~~~~~~~~~~~~~~~~~~~~~~~

**Official Net-SNMP Documentation on Threading:**

The Net-SNMP C library explicitly documents threading limitations:

1. **Net-SNMP FAQ** (http://www.net-snmp.org/docs/FAQ.html#Is_the_library_thread_safe_):
   
   *"The Net-SNMP library is not thread-safe... Applications using threads should only call the library from a single thread."*

2. **Net-SNMP README.thread** (included in Net-SNMP source distribution):
   
   *"The library is not thread-safe. It uses global variables for configuration, MIB parsing, and internal state management."*

3. **Net-SNMP Developer Mailing List** (http://www.net-snmp.org/lists/):
   
   Multiple discussions confirm: *"Net-SNMP was never designed for multi-threaded use"*

**Key Architectural Issues:**

- **Global MIB Tree**: A single shared data structure for all OID/name mappings
- **Parser State**: MIB file parsing uses global variables (not thread-safe)
- **Caching**: OID resolution caches are not protected by locks
- **File I/O**: Persistent storage and configuration file access uses process-global state
- **No Internal Locking**: Net-SNMP's internal code does not use mutexes or synchronization

**About Session API:**

While Net-SNMP documentation mentions using ``snmp_sess_init()`` and ``snmp_sess_open()`` for "better thread isolation," it explicitly states: *"Resource locking is not handled within the library, and is the responsibility of the main application."*

Even with session handles, the underlying MIB parser, OID cache, and configuration state remain process-global and thread-unsafe.

These architectural decisions cannot be changed without rewriting major portions of Net-SNMP.

Performance Considerations
--------------------------

**Multiprocessing**:
- ✅ Excellent throughput for I/O-bound SNMP operations
- ✅ Full CPU utilization across cores
- ⚠️ Higher memory usage (each process has its own Python interpreter)
- ⚠️ Process creation overhead (use process pools for many operations)

**Threading** (Limited Support):
- ⚠️ Unreliable under high concurrency
- ⚠️ Mutex contention reduces parallelism
- ✅ Lower memory footprint than multiprocessing
- ❌ Not recommended for production

Best Practices
--------------

1. **Use Multiprocessing for Production**: This is the reliable, tested approach:

   .. code-block:: python

       from multiprocessing import Pool
       from ezsnmp import Session

       def snmp_get(hostname):
           with Session(hostname=hostname, community='public', version=2) as session:
               return session.get('sysDescr.0').value

       # Process pool for efficient resource usage
       with Pool(processes=10) as pool:
           hosts = ['host1', 'host2', 'host3', ...]
           results = pool.map(snmp_get, hosts)

2. **Limit Thread Concurrency**: If you must use threading, keep concurrency low:

   .. code-block:: python

       import threading
       from concurrent.futures import ThreadPoolExecutor

       # Maximum 4 concurrent threads to reduce failures
       with ThreadPoolExecutor(max_workers=4) as executor:
           futures = [executor.submit(snmp_operation) for _ in range(10)]
           results = [f.result() for f in futures]

3. **Error Handling**: Always handle exceptions, especially in threaded code:

   .. code-block:: python

       import logging

       def safe_snmp_operation():
           try:
               with Session(hostname='localhost', community='public', version=2) as session:
                   return session.get('sysDescr.0')
           except Exception as e:
               logging.error(f"SNMP operation failed: {e}")
               return None

4. **Connection Pooling for Sequential Operations**: If operations are sequential, reuse sessions:

   .. code-block:: python

       # Good: Reuse session for multiple operations
       with Session(hostname='localhost', community='public', version=2) as session:
           for oid in oids_to_query:
               result = session.get(oid)
               process(result)

Known Limitations
-----------------

Threading Limitations (Due to Net-SNMP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Net-SNMP C library has fundamental threading limitations:

1. **Global State**: Extensive use of global variables for MIB parsing, OID caching, and configuration
2. **No Internal Locking**: Net-SNMP's internal code does not use mutexes or locks
3. **Shared Data Structures**: The MIB tree and OID cache are shared across all sessions
4. **File I/O Conflicts**: Configuration and persistent storage use process-global state

**Result**: Even with EzSnmp's thread-safety protections, high-concurrency threading will experience:
- MIB parser corruption
- OID resolution failures
- File descriptor errors
- Occasional segmentation faults

**Solution**: Use multiprocessing instead, which is fully reliable.

MIB Parsing
~~~~~~~~~~~~

MIB loading and parsing operations are serialized through a global mutex. If your application frequently loads different MIBs from multiple threads, this may be a bottleneck. Consider:
- Pre-loading all needed MIBs at startup
- Using multiprocessing if MIB loading is performance-critical

Testing
-------

Multiprocessing is thoroughly tested and reliable:

**Integration Tests** (✅ Passing)

The ``integration_tests/`` directory validates multiprocessing works correctly:

.. code-block:: bash

    # These tests pass reliably
    cd integration_tests
    python3 test_snmp_get.py 20 process      # 20 concurrent processes
    python3 test_snmp_walk.py 20 process
    python3 test_snmp_bulkwalk.py 20 process

**Threading Tests** (⚠️ Limited)

Threading tests may fail under high concurrency due to Net-SNMP limitations:

.. code-block:: bash

    # May fail with >4 threads
    python3 test_snmp_get.py 4 thread      # Usually works
    python3 test_snmp_get.py 10 thread     # May experience failures

**Test Coverage**:
- All SNMP versions (v1, v2c, v3) with various auth/priv protocols
- Multiple session configurations
- Real operations against running snmpd  
- Retry logic for transient network errors
- High-concurrency stress tests (multiprocessing only)

See ``integration_tests/README.rst`` for more details.

Migration Guide
---------------

Choosing Concurrency Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**For New Projects**: Use multiprocessing

.. code-block:: python

    from multiprocessing import Pool
    from ezsnmp import Session

    def query_device(hostname):
        with Session(hostname=hostname, community='public', version=2) as session:
            return session.walk('system')

    with Pool(processes=10) as pool:
        results = pool.map(query_device, device_list)

**For Existing Threading Code**: Migrate to multiprocessing or limit concurrency

**Option 1 - Migrate to Multiprocessing** (Recommended):

.. code-block:: python

    # Before (Threading - Unreliable)
    from threading import Thread
    
    threads = [Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # After (Multiprocessing - Reliable)
    from multiprocessing import Process
    
    processes = [Process(target=worker) for _ in range(20)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

**Option 2 - Limit Thread Concurrency** (if threading is required):

.. code-block:: python

    # Limit to 4 concurrent threads to reduce failures
    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(worker, items))

Backward Compatibility
~~~~~~~~~~~~~~~~~~~~~~

Existing single-threaded code continues to work without any changes. The concurrency improvements are additive and don't break existing functionality.

Contributing
------------

If you find issues or have suggestions for improvement, please open an issue on GitHub: https://github.com/carlkidcrypto/ezsnmp/issues

**Known Issues**:
- Threading reliability under high concurrency (Net-SNMP limitation)
- Multiprocessing is the recommended approach

References
----------

**Official Net-SNMP Documentation:**

- Net-SNMP FAQ - Thread Safety: http://www.net-snmp.org/docs/FAQ.html#Is_the_library_thread_safe_
- Net-SNMP README.thread: Included in Net-SNMP source distribution (explains session API limitations)
- Net-SNMP Mailing List Archives: https://sourceforge.net/p/net-snmp/mailman/
- Net-SNMP Source Code: https://github.com/net-snmp/net-snmp (shows global state usage)

**EzSnmp Documentation:**

- Issue #45: v3 multi threading fails due to user cache
- Integration Tests: https://github.com/carlkidcrypto/ezsnmp/tree/main/integration_tests

**Python Documentation:**

- Python Threading: https://docs.python.org/3/library/threading.html
- Python Multiprocessing: https://docs.python.org/3/library/multiprocessing.html
- SWIG Thread Support: https://swig.org/Doc4.0/Python.html#Python_multithreaded

Summary
-------

**Use Multiprocessing** ✅
- Reliable and production-ready
- High concurrency support  
- No race conditions or corruption
- Recommended for all production use cases

**Limit Threading** ⚠️
- Works for simple cases (≤4 threads)
- May fail under high concurrency
- Not recommended for production
- Use only when multiprocessing is not feasible
