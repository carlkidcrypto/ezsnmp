===================================================
Rocky Linux 9 with Net-SNMP 5.10 Docker Test Environment
===================================================

Overview
========

This Docker image provides a testing environment based on Rocky Linux 9 with:

* **Base OS**: Rocky Linux 9
* **GCC**: gcc-toolset-13 (g++ 13.x, exceeds g++ 9.5 minimum)
* **Python Versions**: 3.10, 3.11, 3.12, 3.13, 3.14 (all from source builds)
* **Virtual Environment**: /opt/venv (Python 3.14 with all project dependencies pre-installed)
* **Net-SNMP**: 5.10 (built from source)
* **C++ Testing**: Full g++ 13 support for cpp_tests with coverage reporting
* **Python Testing**: Full support for python_tests with coverage reporting
* **Image Size**: Optimized to minimal size through consolidated RUN statements and cache cleanup

Building
========

To build the image locally:

.. code-block:: bash

    cd docker/rockylinux9_netsnmp_5.10
    docker-compose build

Running
=======

To run the container with automatic setup:

.. code-block:: bash

    cd docker/rockylinux9_netsnmp_5.10
    ./go_docker.sh

Or manually:

.. code-block:: bash

    docker-compose up -d
    docker exec -it rockylinux9_netsnmp_5.10_snmp_container /bin/bash

Testing
=======

Inside the container, run tests with:

.. code-block:: bash

    # Python tests
    cd /ezsnmp
    python_tests/requirements.txt  # Already installed in venv
    pytest python_tests/

    # C++ tests
    cd /ezsnmp/cpp_tests
    ./get_test_coverage.sh

Python Versions
===============

All Python versions are compiled from source:

* Python 3.10.22
* Python 3.11.17
* Python 3.12.15
* Python 3.13.17
* Python 3.14.9 (default venv)

Gcc Toolset
===========

Rocky Linux 9 uses gcc-toolset-13 which provides:

* GCC 13.x compiler suite
* Support for modern C++ features
* Full compatibility with C++17/C++20 standards

The toolset is automatically configured in the PATH.
