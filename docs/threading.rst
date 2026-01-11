Thread-Safety and Multiprocessing in EzSnmp
============================================

Overview
--------

As of version X.X.X, EzSnmp is both **thread-safe** and **multiprocess-safe**, allowing you to use it in concurrent programming scenarios without worrying about race conditions or data corruption.

Thread-Safety Guarantees
-------------------------

Session Object Thread-Safety
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each ``Session`` object can be safely used from multiple threads concurrently. The implementation uses per-instance mutexes to protect internal state:

.. code-block:: python

    from ezsnmp import Session
    import threading

    # Safe: Multiple threads using the same session
    session = Session(hostname='localhost', community='public', version=2)

    def worker():
        result = session.get('sysDescr.0')
        print(result.value)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

Independent Sessions
~~~~~~~~~~~~~~~~~~~~

Each thread can also create and manage its own ``Session`` objects independently:

.. code-block:: python

    def worker():
        # Each thread creates its own session
        session = Session(hostname='localhost', community='public', version=2)
        result = session.walk('system')
        session.close()

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

SNMPv3 Thread-Safety
~~~~~~~~~~~~~~~~~~~~

SNMPv3 authentication and user cache operations are protected by a global mutex, fixing issue #45:

.. code-block:: python

    # Safe: Concurrent SNMPv3 operations
    def v3_worker():
        session = Session(
            hostname='localhost',
            version=3,
            security_level='authPriv',
            security_username='myuser',
            auth_protocol='SHA',
            auth_passphrase='mypassword',
            privacy_protocol='AES',
            privacy_passphrase='mypassword'
        )
        result = session.get('sysDescr.0')
        session.close()

    threads = [threading.Thread(target=v3_worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

Multiprocess-Safety
-------------------

EzSnmp is fully multiprocess-safe. Each process has its own independent copy of the library state, so you can use ``multiprocessing`` without any special considerations:

.. code-block:: python

    from multiprocessing import Process
    from ezsnmp import Session

    def worker():
        session = Session(hostname='localhost', community='public', version=2)
        result = session.get('sysDescr.0')
        print(f"Process {os.getpid()}: {result.value}")
        session.close()

    processes = [Process(target=worker) for _ in range(5)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

Implementation Details
----------------------

The thread-safety implementation uses several techniques:

1. **Per-Instance Mutexes**: Each ``SessionBase`` object has its own mutex (``std::mutex``) protecting its internal state.

2. **Global Net-SNMP Mutex**: A global mutex protects Net-SNMP library operations that access shared state:
   
   - Library initialization (``init_snmp``)
   - MIB parsing operations
   - SNMPv3 user cache operations (``usm_get_userList``, ``usm_remove_user``)
   - Global error state (``snmp_errno``)

3. **GIL Release**: The SWIG bindings are generated with the ``-threads`` flag, which automatically releases the Python GIL (Global Interpreter Lock) during C++ function calls, allowing true parallel execution.

Performance Considerations
--------------------------

Thread-safety does come with some overhead due to mutex locking, but the impact is minimal:

- **Negligible overhead** for single-threaded use (mutex operations are very fast)
- **Improved throughput** in multi-threaded scenarios due to GIL release during I/O operations
- **No performance impact** on multiprocessing (processes don't share locks)

Best Practices
--------------

1. **Use Context Managers**: Always use the context manager (``with`` statement) to ensure proper cleanup:

   .. code-block:: python

       with Session(hostname='localhost', community='public', version=2) as session:
           result = session.get('sysDescr.0')

2. **Separate Sessions for Long-Running Operations**: For better concurrency, create separate sessions in each thread:

   .. code-block:: python

       def worker():
           with Session(hostname='localhost', community='public', version=2) as session:
               # Perform operations
               result = session.walk('interfaces')

3. **Connection Pooling**: If you need to make many requests, consider implementing a connection pool pattern:

   .. code-block:: python

       from queue import Queue
       import threading

       # Create a pool of sessions
       session_pool = Queue()
       for _ in range(5):
           session_pool.put(Session(hostname='localhost', community='public', version=2))

       def worker():
           session = session_pool.get()
           try:
               result = session.get('sysDescr.0')
               # Process result
           finally:
               session_pool.put(session)

4. **Error Handling**: Always handle exceptions in threaded code:

   .. code-block:: python

       import logging

       def worker():
           try:
               with Session(hostname='localhost', community='public', version=2) as session:
                   result = session.get('sysDescr.0')
           except Exception as e:
               logging.error(f"SNMP operation failed: {e}")

Known Limitations
-----------------

- **Net-SNMP Library**: The underlying Net-SNMP C library has some global state that cannot be eliminated. EzSnmp protects access to this state with mutexes.

- **MIB Parsing**: MIB parsing operations are serialized through the global mutex, which may be a bottleneck if you're constantly loading different MIBs from multiple threads.

Testing
-------

The thread-safety implementation is tested with:

- Concurrent operations on the same session
- Concurrent operations with multiple sessions
- Mixed operation types (GET, WALK, BULKWALK, SET)
- SNMPv3 authentication in multiple threads
- High concurrency stress tests (50+ concurrent threads)
- Multiprocessing tests

See ``python_tests/test_threading.py`` for the complete test suite.

Migration Guide
---------------

If you have existing code that uses EzSnmp, no changes are required! The thread-safety improvements are backward compatible:

**Before (Not Thread-Safe)**:

.. code-block:: python

    # This would have been unsafe in older versions
    session = Session(hostname='localhost', community='public', version=2)

    def worker():
        result = session.get('sysDescr.0')

    threads = [threading.Thread(target=worker) for _ in range(10)]
    # ... this could crash or produce incorrect results

**After (Thread-Safe)**:

.. code-block:: python

    # This is now safe!
    session = Session(hostname='localhost', community='public', version=2)

    def worker():
        result = session.get('sysDescr.0')

    threads = [threading.Thread(target=worker) for _ in range(10)]
    # ... this works correctly

Contributing
------------

If you find any thread-safety issues or have suggestions for improvement, please open an issue on GitHub: https://github.com/carlkidcrypto/ezsnmp/issues

References
----------

- Issue #45: v3 multi threading fails due to user cache
- SWIG Thread Support: https://swig.org/Doc4.0/Python.html#Python_multithreaded
- Python Threading: https://docs.python.org/3/library/threading.html
- Python Multiprocessing: https://docs.python.org/3/library/multiprocessing.html
