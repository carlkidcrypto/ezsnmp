Software Requirements
=====================

This document defines the software requirements for EzSnmp. Each requirement is
identified by a unique ID in the format ``[ID-xxx]``.

Functional Requirements
-----------------------

SNMP Operations
~~~~~~~~~~~~~~~

[ID-001] The system shall provide a Python library (installable via pip) for performing SNMP operations against network agents.

[ID-002] The system shall support SNMP protocol versions 1, 2c, and 3.

[ID-003] The system shall implement SNMP GET operations to retrieve the value of a single specified OID.

[ID-004] The system shall implement SNMP GETNEXT operations to retrieve the next OID in the MIB tree relative to a specified OID.

[ID-005] The system shall implement SNMP WALK operations to traverse and retrieve all OIDs in a subtree.

[ID-006] The system shall implement SNMP BULKGET operations (SNMPv2c/v3 only) to retrieve multiple OIDs in a single request.

[ID-007] The system shall implement SNMP BULKWALK operations (SNMPv2c/v3 only) to efficiently traverse MIB subtrees using GETBULK PDUs.

[ID-008] The system shall implement SNMP SET operations to write a value to a specified OID on an agent.

[ID-009] The system shall implement SNMP TRAP sending capability.

Python API
~~~~~~~~~~

[ID-010] The system shall expose a high-level ``Session`` class that encapsulates all SNMP session parameters and supports GET, GETNEXT, WALK, BULKGET, BULKWALK, and SET operations as named methods.

[ID-011] The ``Session`` class shall support use as a Python context manager (``with`` statement) to automatically release resources on exit.

[ID-012] The system shall expose low-level functional wrappers (``snmpget``, ``snmpgetnext``, ``snmpwalk``, ``snmpbulkget``, ``snmpbulkwalk``, ``snmpset``, ``snmptrap``) that accept raw Net-SNMP CLI-style argument lists.

[ID-013] Each SNMP operation shall return results as a sequence of ``Result`` objects containing the following fields: ``oid``, ``index``, ``type``, ``value``, and ``converted_value``.

[ID-014] The ``converted_value`` field of a ``Result`` object shall contain a Python-native typed value (``int``, ``float``, ``str``, ``bytes``, etc.) derived from the SNMP type string and raw value string.

Session Configuration
~~~~~~~~~~~~~~~~~~~~~

[ID-015] The system shall support SNMPv3 authentication protocols: MD5, SHA, SHA-224, SHA-256, SHA-384, and SHA-512.

[ID-016] The system shall support SNMPv3 privacy (encryption) protocols: DES, AES, AES-192, and AES-256.

[ID-017] The system shall support SNMPv3 security levels: ``noAuthNoPriv``, ``authNoPriv``, and ``authPriv``.

[ID-018] The system shall accept configurable session parameters including hostname, port number, community string, authentication passphrase, privacy passphrase, security username, context, security engine ID, context engine ID, boots/time, retries, timeout, MIB list, and MIB directory paths.

[ID-019] The system shall support configurable output formatting options including: print OIDs numerically, print full OIDs, print enums numerically, print timeticks as numeric integers, and print OCTET STRINGs as hex strings.

[ID-020] The system shall support configuring the max-repeaters value used in BULKGET and BULKWALK operations.

[ID-041] The system shall support loading custom MIB files and searching user-specified MIB directory paths at session creation time.

Error Handling
~~~~~~~~~~~~~~

[ID-021] The system shall raise typed Python exceptions corresponding to distinct SNMP error conditions: ``ConnectionError``, ``GenericError``, ``NoSuchInstanceError``, ``NoSuchNameError``, ``NoSuchObjectError``, ``PacketError``, ``ParseError``, ``TimeoutError``, ``UndeterminedTypeError``, and ``UnknownObjectIDError``.

[ID-022] All exception types shall inherit from a common ``GenericError`` base class.

Non-Functional Requirements
----------------------------

Thread Safety
~~~~~~~~~~~~~

[ID-023] The system shall be thread-safe; concurrent SNMP operations from multiple Python threads shall not corrupt Net-SNMP global state.

[ID-024] The system shall use reference counting and mutexes to initialize Net-SNMP (``init_snmp``) only on the first operation and shut it down (``snmp_shutdown``) only after all operations in all threads have completed.

Build and Distribution
~~~~~~~~~~~~~~~~~~~~~~

[ID-025] The C++ core shall be built as a Python extension module using SWIG 4.4.1 to auto-generate Python ↔ C++ bindings.

[ID-026] The build system shall support Net-SNMP versions 5.7, 5.8, 5.9, and 5.10 by applying per-version source patches to the upstream Net-SNMP CLI tool sources.

[ID-027] The system shall be installable on Linux (x86_64 and aarch64), macOS (arm64), and Windows (AMD64) via pre-built binary wheels distributed on PyPI.

[ID-028] Windows wheels shall bundle all required Net-SNMP and OpenSSL DLLs so that no separate Net-SNMP installation is required.

[ID-029] The system shall support Python versions 3.10, 3.11, 3.12, 3.13, and 3.14.

[ID-042] The system shall support Homebrew (macOS) and MacPorts (macOS) as Net-SNMP installation sources for source builds.

Testing
~~~~~~~

[ID-030] The system shall provide a Python unit test suite (pytest) covering session operations, SNMP functional wrappers, data types, exceptions, authentication/privacy variants, multithreading, caching, logging, and platform-specific setup.

[ID-031] The system shall provide a C++ unit test suite (Google Test) covering the C++ core components.

[ID-032] The system shall provide integration tests that run against a live SNMP agent and validate real GET, WALK, and BULKWALK operations.

[ID-033] The system shall maintain code coverage reporting for both Python and C++ components via Codecov, with coverage data uploaded from all CI test workflows.

Code Quality
~~~~~~~~~~~~

[ID-034] The system shall enforce Python code style using Black (line length 100, targeting all supported Python versions).

[ID-035] The system shall enforce C++ code style using clang-format.

[ID-036] The system shall perform static security analysis on the codebase using CodeQL in CI.

[ID-037] The system shall perform memory safety analysis using Valgrind on macOS (Homebrew) builds as part of CI.

Documentation
~~~~~~~~~~~~~

[ID-038] The system shall provide Sphinx-based HTML documentation including installation instructions, API reference, and a development guide.

CI/CD and Maintenance
~~~~~~~~~~~~~~~~~~~~~

[ID-039] The system shall publish release distributions to both PyPI and TestPyPI via CI workflows triggered on release events.

[ID-040] The system shall publish Docker images for use in testing across multiple Linux distributions.

[ID-043] The CHANGELOG shall be automatically generated and maintained by a CI workflow.

[ID-044] The system shall automatically sync open pull requests with the main branch via a scheduled CI workflow.

[ID-045] The system shall monitor supported Python versions and raise alerts or auto-update when a new supported version is added or an old one reaches end-of-life.
