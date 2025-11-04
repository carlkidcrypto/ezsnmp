==========
C++ Tests
==========

Overview
========
This directory contains C++ unit tests for the EzSnmp library's native C++ components.
These tests validate the low-level SNMP operations and C++ class functionality.

Purpose
=======
The C++ tests ensure that:

* SessionBase class operations work correctly
* Exception handling in C++ layer functions properly
* Data type conversions between C++ and Python are accurate
* Net-SNMP library integration is stable
* Memory management is correct and leak-free

Test Components
===============
The tests in this directory cover:

* SNMP session management
* GET, SET, WALK, BULKGET, and BULKWALK operations
* Error handling and exception propagation
* Thread safety of C++ components
* SWIG interface bindings

Usage
=====
For detailed instructions on building and running C++ tests, please refer to the 
`Development Guide <../sphinx_docs_build/source/development.rst>`_.

Prerequisites
=============
To run these tests, you need:

* Meson and Ninja build tools
* Net-SNMP development libraries
* Google Test framework (or similar C++ testing framework)
* C++ compiler with C++17 support

Related Documentation
=====================
* `Main README <../README.rst>`_
* `Development Guide <../sphinx_docs_build/source/development.rst>`_
* `Python Tests <../python_tests/README.rst>`_
* `C++ Source Code <../ezsnmp/src/>`_
