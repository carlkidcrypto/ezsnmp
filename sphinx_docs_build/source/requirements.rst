Software Requirements
=====================

This document defines the software requirements for EzSnmp. Each requirement is
identified by a unique feature-grouped ID in the format ``[PREFIX-nn]``, where the
prefix indicates the feature area:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Prefix
     - Feature Area
   * - ``SNMP``
     - Core SNMP protocol operations
   * - ``API``
     - Python API surface (Session class, functional wrappers, Result type)
   * - ``CFG``
     - Session configuration and output formatting
   * - ``ERR``
     - Exception and error handling
   * - ``THREAD``
     - Thread safety
   * - ``BUILD``
     - Build system and SWIG bindings
   * - ``WHEELS``
     - Binary wheel distribution and packaging
   * - ``TEST``
     - Testing and code coverage
   * - ``QUAL``
     - Code quality and static analysis
   * - ``DOCS``
     - Documentation
   * - ``CICD``
     - CI/CD pipelines and maintenance automation

Functional Requirements
-----------------------

SNMP Operations
~~~~~~~~~~~~~~~

[SNMP-01] The system shall provide a Python library (installable via pip) for performing SNMP operations against network agents.

[SNMP-02] The system shall support SNMP protocol versions 1, 2c, and 3.

[SNMP-03] The system shall implement SNMP GET operations to retrieve the value of a single specified OID.

[SNMP-04] The system shall implement SNMP GETNEXT operations to retrieve the next OID in the MIB tree relative to a specified OID.

[SNMP-05] The system shall implement SNMP WALK operations to traverse and retrieve all OIDs in a subtree.

[SNMP-06] The system shall implement SNMP BULKGET operations (SNMPv2c/v3 only) to retrieve multiple OIDs in a single request.

[SNMP-07] The system shall implement SNMP BULKWALK operations (SNMPv2c/v3 only) to efficiently traverse MIB subtrees using GETBULK PDUs.

[SNMP-08] The system shall implement SNMP SET operations to write a value to a specified OID on an agent.

[SNMP-09] The system shall implement SNMP TRAP sending capability.

Python API
~~~~~~~~~~

[API-01] The system shall expose a high-level ``Session`` class that encapsulates all SNMP session parameters and supports GET, GETNEXT, WALK, BULKGET, BULKWALK, and SET operations as named methods.

[API-02] The ``Session`` class shall support use as a Python context manager (``with`` statement) to automatically release resources on exit.

[API-03] The system shall expose low-level functional wrappers (``snmpget``, ``snmpgetnext``, ``snmpwalk``, ``snmpbulkget``, ``snmpbulkwalk``, ``snmpset``, ``snmptrap``) that accept raw Net-SNMP CLI-style argument lists.

[API-04] Each SNMP operation shall return results as a sequence of ``Result`` objects containing the following fields: ``oid``, ``index``, ``type``, ``value``, and ``converted_value``.

[API-05] The ``converted_value`` field of a ``Result`` object shall contain a Python-native typed value (``int``, ``float``, ``str``, ``bytes``, etc.) derived from the SNMP type string and raw value string.

Session Configuration
~~~~~~~~~~~~~~~~~~~~~

[CFG-01] The system shall support SNMPv3 authentication protocols: MD5, SHA, SHA-224, SHA-256, SHA-384, and SHA-512.

[CFG-02] The system shall support SNMPv3 privacy (encryption) protocols: DES, AES, AES-192, and AES-256.

[CFG-03] The system shall support SNMPv3 security levels: ``noAuthNoPriv``, ``authNoPriv``, and ``authPriv``.

[CFG-04] The system shall accept configurable session parameters including hostname, port number, community string, authentication passphrase, privacy passphrase, security username, context, security engine ID, context engine ID, boots/time, retries, timeout, MIB list, and MIB directory paths.

[CFG-05] The system shall support configurable output formatting options including: print OIDs numerically, print full OIDs, print enums numerically, print timeticks as numeric integers, and print OCTET STRINGs as hex strings.

[CFG-06] The system shall support configuring the max-repeaters value used in BULKGET and BULKWALK operations.

[CFG-07] The system shall support loading custom MIB files and searching user-specified MIB directory paths at session creation time.

Error Handling
~~~~~~~~~~~~~~

[ERR-01] The system shall raise typed Python exceptions corresponding to distinct SNMP error conditions: ``ConnectionError``, ``GenericError``, ``NoSuchInstanceError``, ``NoSuchNameError``, ``NoSuchObjectError``, ``PacketError``, ``ParseError``, ``TimeoutError``, ``UndeterminedTypeError``, and ``UnknownObjectIDError``.

[ERR-02] All exception types shall inherit from a common ``GenericError`` base class.

Non-Functional Requirements
----------------------------

Thread Safety
~~~~~~~~~~~~~

[THREAD-01] The system shall be thread-safe; concurrent SNMP operations from multiple Python threads shall not corrupt Net-SNMP global state.

[THREAD-02] The system shall use reference counting and mutexes to initialize Net-SNMP (``init_snmp``) only on the first operation and shut it down (``snmp_shutdown``) only after all operations in all threads have completed.

Build and Distribution
~~~~~~~~~~~~~~~~~~~~~~

[BUILD-01] The C++ core shall be built as a Python extension module using SWIG 4.4.1 to auto-generate Python ↔ C++ bindings.

[BUILD-02] The build system shall support Net-SNMP versions 5.7, 5.8, 5.9, and 5.10 by applying per-version source patches to the upstream Net-SNMP CLI tool sources.

[BUILD-03] The system shall support Python versions 3.10, 3.11, 3.12, 3.13, and 3.14.

[BUILD-04] The system shall support Homebrew (macOS) and MacPorts (macOS) as Net-SNMP installation sources for source builds.

Binary Wheels
~~~~~~~~~~~~~

[WHEELS-01] The system shall be installable on Linux (x86_64 and aarch64), macOS (arm64), and Windows (AMD64) via pre-built binary wheels distributed on PyPI.

[WHEELS-02] Windows wheels shall bundle all required Net-SNMP and OpenSSL DLLs so that no separate Net-SNMP installation is required.

Testing
~~~~~~~

[TEST-01] The system shall provide a Python unit test suite (pytest) covering session operations, SNMP functional wrappers, data types, exceptions, authentication/privacy variants, multithreading, caching, logging, and platform-specific setup.

[TEST-02] The system shall provide a C++ unit test suite (Google Test) covering the C++ core components.

[TEST-03] The system shall provide integration tests that run against a live SNMP agent and validate real GET, WALK, and BULKWALK operations.

[TEST-04] The system shall maintain code coverage reporting for both Python and C++ components via Codecov, with coverage data uploaded from all CI test workflows.

Code Quality
~~~~~~~~~~~~

[QUAL-01] The system shall enforce Python code style using Black (line length 100, targeting all supported Python versions).

[QUAL-02] The system shall enforce C++ code style using clang-format.

[QUAL-03] The system shall perform static security analysis on the codebase using CodeQL in CI.

[QUAL-04] The system shall perform memory safety analysis using Valgrind on macOS (Homebrew) builds as part of CI.

Documentation
~~~~~~~~~~~~~

[DOCS-01] The system shall provide Sphinx-based HTML documentation including installation instructions, API reference, and a development guide.

CI/CD and Maintenance
~~~~~~~~~~~~~~~~~~~~~

[CICD-01] The system shall publish release distributions to both PyPI and TestPyPI via CI workflows triggered on release events.

[CICD-02] The system shall publish Docker images for use in testing across multiple Linux distributions.

[CICD-03] The CHANGELOG shall be automatically generated and maintained by a CI workflow.

[CICD-04] The system shall automatically sync open pull requests with the main branch via a scheduled CI workflow.

[CICD-05] The system shall monitor supported Python versions and raise alerts or auto-update when a new supported version is added or an old one reaches end-of-life.
