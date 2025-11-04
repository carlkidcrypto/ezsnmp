==================
EzSnmp Source Code
==================

Overview
========
This directory contains the core EzSnmp library source code, including Python modules,
C++ implementations, SWIG interface files, and header files.

Directory Structure
===================

``include/``
------------
Contains C++ header files (.h) for the library:

* ``datatypes.h`` - Data type definitions for SNMP variables and results
* ``exceptionsbase.h`` - Base exception classes for error handling
* ``helpers.h`` - Helper functions and utilities
* ``sessionbase.h`` - Core SNMP session management

``interface/``
--------------
Contains SWIG interface files (.i) that define the Python/C++ bindings:

* ``datatypes.i`` - Data type interface definitions
* ``exceptionsbase.i`` - Exception interface definitions
* ``netsnmpbase.i`` - Net-SNMP base functionality interface
* ``sessionbase.i`` - Session management interface
* ``snmpget.i``, ``snmpset.i``, ``snmpwalk.i``, etc. - SNMP operation interfaces

``src/``
--------
Contains C++ implementation files (.cpp):

* ``datatypes.cpp`` - Data type implementation
* ``exceptionsbase.cpp`` - Exception handling implementation
* ``helpers.cpp`` - Helper function implementations
* ``sessionbase.cpp`` - SNMP session implementation
* ``snmpget.cpp``, ``snmpset.cpp``, ``snmpwalk.cpp``, etc. - SNMP operation implementations

``patches/``
------------
Contains patch files for modifying Net-SNMP application code to integrate with EzSnmp.

Python Modules
==============
The root of this directory also contains Python modules:

* ``__init__.py`` - Package initialization and exports
* ``session.py`` - Python Session class wrapper
* ``exceptions.py`` - Python exception classes
* Generated SWIG wrapper files (``*_wrap.cpp``, ``*.py``)

Building the Library
====================
The library is built using setuptools and SWIG. For detailed build instructions,
see the `Development Guide <../sphinx_docs_build/source/development.rst>`_.

Quick build:

.. code-block:: bash

    # From repository root
    python3 -m pip install .

Development build (editable):

.. code-block:: bash

    # From repository root
    python3 -m pip install -e .

SWIG Interface Files
====================
The SWIG interface files in ``interface/`` are used to generate Python bindings
for the C++ code. To regenerate the SWIG wrappers:

.. code-block:: bash

    swig -c++ -python -builtin -threads -doxygen -std=c++17 \\
         -outdir ezsnmp/. -o ezsnmp/src/ezsnmp_netsnmpbase.cpp \\
         ezsnmp/interface/netsnmpbase.i

For complete SWIG build commands, see the `Development Guide <../sphinx_docs_build/source/development.rst>`_.

Documentation
=============
The C++ code is documented using Doxygen-style comments. The documentation is
generated and integrated with Sphinx via the Breathe extension.

To view the generated documentation, visit the `EzSnmp Documentation <http://carlkidcrypto.github.io/ezsnmp/>`_.

Related Documentation
=====================
* `Main README <../README.rst>`_
* `Development Guide <../sphinx_docs_build/source/development.rst>`_
* `API Documentation <../sphinx_docs_build/source/modules.rst>`_
* `SWIG Interface Documentation <../sphinx_docs_build/source/swig_interface_files.rst>`_
