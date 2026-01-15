=======
Integration Tests
=======

A collection of scripts developed to help test real life usage scenarios.

Available Tests
---------------

test_snmp_bulkwalk.py
~~~~~~~~~~~~~~~~~~~~~

Tests SNMP bulk walk operations with multiple threads or processes.

Usage:

.. code:: bash

    python3 test_snmp_bulkwalk.py <num_workers> <thread|process>

Examples:

.. code:: bash

    # Run with 8 threads
    python3 test_snmp_bulkwalk.py 8 thread
    
    # Run with 4 processes
    python3 test_snmp_bulkwalk.py 4 process

test_snmp_get.py
~~~~~~~~~~~~~~~~

Tests SNMP get operations with multiple threads or processes.

Usage:

.. code:: bash

    python3 test_snmp_get.py <num_workers> <thread|process>

Examples:

.. code:: bash

    # Run with 8 threads
    python3 test_snmp_get.py 8 thread
    
    # Run with 4 processes
    python3 test_snmp_get.py 4 process

test_snmp_walk.py
~~~~~~~~~~~~~~~~~

Tests SNMP walk operations with multiple threads or processes.

Usage:

.. code:: bash

    python3 test_snmp_walk.py <num_workers> <thread|process>

Examples:

.. code:: bash

    # Run with 8 threads
    python3 test_snmp_walk.py 8 thread
    
    # Run with 4 processes
    python3 test_snmp_walk.py 4 process

test_file_descriptors.py
~~~~~~~~~~~~~~~~~~~~~~~~~

Tests file descriptor handling and management during SNMP operations.

Usage:

.. code:: bash

    python3 test_file_descriptors.py

This test runs automatically without additional parameters.

All Tests
---------

To run all integration tests, use:

.. code:: bash

    bash run_integration_tests.sh
    