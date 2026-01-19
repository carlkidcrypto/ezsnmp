CentOS 8 with net-snmp 5.8 Docker
======================================

Overview
========

This Docker image provides a testing environment based on CentOS 8 (EOL but stable) with:

* **Base OS**: CentOS 8 (leveraging vault.centos.org for EOL distro support)
* **GCC**: gcc-toolset-11 (g++ 11.x, exceeds g++ 9.5 minimum)
* **Python Versions**: 3.10, 3.11, 3.12, 3.13, 3.14 (all from source builds)
* **Virtual Environment**: /opt/venv (Python 3.14 with all project dependencies pre-installed)
* **net-snmp**: 5.8 (previous stable version)
* **C++ Testing**: Full g++ 11 support for cpp_tests with coverage reporting
* **Python Testing**: Full support for python_tests with coverage reporting
* **Image Size**: Optimized to minimal size through consolidated RUN statements and cache cleanup

Building
========

To build the image locally:

.. code-block:: bash

    cd docker/centos8_netsnmp_5.8
    docker-compose build

Running
=======

To run the container with automatic setup:

.. code-block:: bash

    cd docker/centos8_netsnmp_5.8
    ./go_docker.sh

Or manually:

.. code-block:: bash

    docker-compose up -d
    docker exec -it centos8_snmp_container /bin/bash

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

* Python 3.10.16
* Python 3.11.11
* Python 3.12.8
* Python 3.13.7
* Python 3.14.2 (default venv)

Gcc Toolset
===========

CentOS 8 uses gcc-toolset-11 which provides:

* GCC 11.x compiler suite
* Support for modern C++ features
* Full compatibility with C++17/C++20 standards

The toolset is automatically configured in the PATH.

Note on CentOS 8 EOL
====================

CentOS 8 reached end-of-life on December 31, 2021. This image uses vault.centos.org repositories to ensure package availability. This configuration provides backward compatibility testing for older environments that may still be in use.
