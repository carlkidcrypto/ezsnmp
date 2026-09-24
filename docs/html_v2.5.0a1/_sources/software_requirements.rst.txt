Software Requirements
=====================

This document defines the software requirements for EzSnmp. Each requirement is identified by a
unique feature-grouped ID in the format ``[PREFIX-nn]``, where the prefix indicates the feature
area:

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

[SNMP-01] The system shall provide a Python library (installable via pip) for performing SNMP
operations against network agents.

[SNMP-02] The system shall support SNMP protocol versions 1, 2c, and 3.

[SNMP-03] The system shall implement SNMP GET operations to retrieve the value of a single specified
OID.

[SNMP-04] The system shall implement SNMP GETNEXT operations to retrieve the next OID in the MIB
tree relative to a specified OID.

[SNMP-05] The system shall implement SNMP WALK operations to traverse and retrieve all OIDs in a
subtree.

[SNMP-06] The system shall implement SNMP BULKGET operations (SNMPv2c/v3 only) to retrieve multiple
OIDs in a single request.

[SNMP-07] The system shall implement SNMP BULKWALK operations (SNMPv2c/v3 only) to efficiently
traverse MIB subtrees using GETBULK PDUs.

[SNMP-08] The system shall implement SNMP SET operations to write a value to a specified OID on an
agent.

[SNMP-09] The system shall implement SNMP TRAP sending capability.

Python API
~~~~~~~~~~

[API-01] The system shall expose a high-level ``Session`` class that encapsulates all SNMP session
parameters and supports GET, GETNEXT, WALK, BULKGET, BULKWALK, and SET operations as named methods.

[API-02] The ``Session`` class shall support use as a Python context manager (``with`` statement) to
automatically release resources on exit.

[API-03] The system shall expose low-level functional wrappers (``snmpget``, ``snmpgetnext``,
``snmpwalk``, ``snmpbulkget``, ``snmpbulkwalk``, ``snmpset``, ``snmptrap``) that accept raw Net-SNMP
CLI-style argument lists.

[API-04] Each SNMP operation shall return results as a sequence of ``Result`` objects containing the
following fields: ``oid``, ``index``, ``type``, ``value``, and ``converted_value``.

[API-05] The ``converted_value`` field of a ``Result`` object shall contain a Python-native typed
value (``int``, ``float``, ``str``, ``bytes``, etc.) derived from the SNMP type string and raw value
string.

Session Configuration
~~~~~~~~~~~~~~~~~~~~~

[CFG-01] The system shall support SNMPv3 authentication protocols: MD5, SHA, SHA-224, SHA-256,
SHA-384, and SHA-512.

[CFG-02] The system shall support SNMPv3 privacy (encryption) protocols: DES, AES, AES-192, and
AES-256.

[CFG-03] The system shall support SNMPv3 security levels: ``noAuthNoPriv``, ``authNoPriv``, and
``authPriv``.

[CFG-04] The system shall accept configurable session parameters including hostname, port number,
community string, authentication passphrase, privacy passphrase, security username, context,
security engine ID, context engine ID, boots/time, retries, timeout, MIB list, and MIB directory
paths.

[CFG-05] The system shall support configurable output formatting options including: print OIDs
numerically, print full OIDs, print enums numerically, print timeticks as numeric integers, and
print OCTET STRINGs as hex strings.

[CFG-06] The system shall support configuring the max-repeaters value used in BULKGET and BULKWALK
operations.

[CFG-07] The system shall support loading custom MIB files and searching user-specified MIB
directory paths at session creation time.

Error Handling
~~~~~~~~~~~~~~

[ERR-01] The system shall raise typed Python exceptions corresponding to distinct SNMP error
conditions: ``ConnectionError``, ``GenericError``, ``NoSuchInstanceError``, ``NoSuchNameError``,
``NoSuchObjectError``, ``PacketError``, ``ParseError``, ``TimeoutError``, ``UndeterminedTypeError``,
and ``UnknownObjectIDError``.

[ERR-02] All exception types shall inherit from a common ``GenericError`` base class.

[ERR-03] The system shall handle all internal operational, parsing, parameter validation, and Net-
SNMP CLI-style errors across all core C++ operations (``snmpget``, ``snmpgetnext``, ``snmpwalk``,
``snmpbulkget``, ``snmpbulkwalk``, ``snmpset``, and ``snmptrap``) by throwing typed C++ exceptions
(such as ``GenericErrorBase``, ``ParseErrorBase``, or ``PacketErrorBase``) that propagate directly
into Python exceptions, eliminating calls to ``printf``, ``fprintf(stderr, ...)``, and process
``exit()``.

[ERR-04] The system shall provide centralized C++ error helper functions
(``throw_type_value_error``, ``throw_missing_value_error``, ``throw_generic_error_from_snmp``) to
ensure consistent exception types, error messages, and exception dispatch across all Net-SNMP CLI
wrapper implementations.

Non-Functional Requirements
----------------------------

Thread Safety
~~~~~~~~~~~~~

[THREAD-01] The system shall be thread-safe; concurrent SNMP operations from multiple Python threads
shall not corrupt Net-SNMP global state.

[THREAD-02] The system shall use reference counting and mutexes to initialize Net-SNMP
(``init_snmp``) only on the first operation and shut it down (``snmp_shutdown``) only after all
operations in all threads have completed.

[THREAD-03] The system shall isolate per-session output formatting configurations across concurrent
SNMP operations in multi-threaded environments using thread-local storage (``FormattingScope``).
Output formatting options (such as ``print_enums_numerically``, ``print_full_oids``,
``print_oids_numerically``, ``print_timeticks_numerically``, and ``print_hex_strings``) shall be
applied to Net-SNMP default store flags atomically under ``g_netsnmp_mib_mutex`` only during in-
memory variable and OID string rendering (``print_variable_to_string`` and
``print_objid_to_string``). Coarse mutex locks shall not be held across network I/O
(``snmp_sess_synch_response``), allowing concurrent SNMPv1 and SNMPv2c operations to execute
simultaneously across threads without serialization.

[THREAD-04] The system shall serialize SNMPv3 operations and setter mutations using a dedicated
mutex (``g_snmp_v3_operation_mutex``) to safely remove cached USM users
(``remove_v3_user_from_cache``) before and after operations, preventing race conditions and engine
time cache corruption across concurrent SNMPv3 sessions without serializing SNMPv1 or SNMPv2c
operations.

Build and Distribution
~~~~~~~~~~~~~~~~~~~~~~

[BUILD-01] The C++ core shall be built as a Python extension module using SWIG 4.5.0 to auto-
generate Python ↔ C++ bindings.

[BUILD-02] The build system shall support Net-SNMP versions 5.7, 5.8, 5.9, and 5.10 by applying per-
version source patches to the upstream Net-SNMP CLI tool sources.

[BUILD-03] The system shall support Python versions 3.10, 3.11, 3.12, 3.13, and 3.14.

[BUILD-04] The system shall support Homebrew (macOS) and MacPorts (macOS) as Net-SNMP installation
sources for source builds.

[BUILD-05] Windows wheel builds shall build Net-SNMP from source via a dedicated composite GitHub
Action (``perl Configure`` + ``nmake``) rather than relying on a pre-packaged Net-SNMP distribution,
since none is available for MSVC.

[BUILD-06] The Windows Net-SNMP source build shall apply the following compatibility patches before
compilation:

- Replace ``snmp_openssl.c`` direct ``ASN1_STRING`` member access with the ``ASN1_STRING_*``
  accessor functions, since OpenSSL 3.0 made ``ASN1_STRING`` opaque.
- Replace the ``<openssl/ossl_typ.h>`` include in ``scapi.h`` with ``<openssl/types.h>``, since
  OpenSSL 3.5 removed the deprecated forwarding header.
- Guard the unconditional ``#define inline __inline`` in the generated ``net-snmp-config.h`` with
  ``#ifndef __cplusplus``, since MSVC's C++ standard library forbids macroizing the ``inline``
  keyword. This patch shall be applied after ``perl Configure`` runs (Configure regenerates this
  file from a template) and shall tolerate CRLF line endings.

[BUILD-07] The Net-SNMP single-session API (``snmp_sess_open``, ``snmp_sess_close``,
``snmp_sess_synch_response``, ``snmp_sess_error``) shall be treated by ezsnmp's C++ wrapper code as
returning/accepting an opaque handle whose concrete pointer type differs across supported Net-SNMP
versions (``void *`` in 5.7-5.9, ``struct session_list *`` in 5.10). Wrapper code shall store this
handle as ``void *`` and apply an explicit ``static_cast<struct session_list *>`` at each call site
that requires it, so the same source compiles unmodified against every supported version.

[BUILD-08] C++ extension modules shall be declared using dotted Python package notation (for example
``ezsnmp._datatypes``), not path-separator notation, since the latter produces an invalid exported
``PyInit_`` symbol name under MSVC.

[BUILD-09] The per-version Net-SNMP CLI source patches under ``ezsnmp/patches/`` shall be
regenerated from ``ezsnmp/patches/master_src`` (the canonical template) whenever that template
changes, using cross-platform scripts (``do_all_that_stuff.sh``, ``make_patches.sh``,
``apply_patches.sh``) that detect available POSIX or GNU utilities (``sed``/``gsed``,
``patch``/``gpatch``) to generate diffs and produce the checked-in ``ezsnmp/src/net-snmp-*-final-
patched`` sources on macOS, Linux, and other UNIX-like systems.

[BUILD-10] The Windows Net-SNMP source build shall additionally patch ``include/net-
snmp/library/lcd_time.h`` to add the ``NETSNMP_IMPORT`` decoration to the ``free_enginetime``
declaration, since that function otherwise lacks the export decoration and is silently omitted from
``netsnmp.dll``'s export table (unlike POSIX shared libraries, which export it implicitly). ezsnmp's
C++ wrapper code calls this function directly when removing a cached SNMPv3 USM user.

[BUILD-11] The repository shall maintain an official Homebrew formula (``Formula/ezsnmp.rb``)
supporting local source builds and installation of ezsnmp into Homebrew Python environments,
automatically configured against Homebrew-installed Net-SNMP and OpenSSL dependencies.

Binary Wheels
~~~~~~~~~~~~~

[WHEELS-01] The system shall be installable on Linux (x86_64 and aarch64), macOS (arm64), and
Windows (AMD64, x86, and ARM64) via pre-built binary wheels distributed on PyPI.

[WHEELS-02] Windows wheels shall support AMD64, x86, and ARM64 native architectures and bundle all
required Net-SNMP and OpenSSL DLLs so that no separate Net-SNMP installation is required.

[WHEELS-03] The Windows wheel build shall pass the Net-SNMP include directory, the OpenSSL include
directory, and the OpenSSL library directory to the Python extension compiler and linker, since
ezsnmp's own C++ sources transitively include Net-SNMP headers that reference OpenSSL types, and the
generated ``net-snmp-config.h`` embeds ``#pragma comment(lib, ...)`` directives requiring
``libcrypto.lib``/``libssl.lib`` to be resolvable on the linker's library path.

Testing
~~~~~~~

[TEST-01] The system shall provide a Python unit test suite (pytest) covering session operations,
SNMP functional wrappers, data types, exceptions, authentication/privacy variants, multithreading,
caching, logging, and platform-specific setup.

[TEST-02] The system shall provide a C++ unit test suite (Google Test) covering the C++ core
components, incorporating backwards-compatibility fallback mechanisms (such as
``EZSNMP_SKIP_TEST_AND_RETURN``) to support older Google Test distributions (< 1.10.0, e.g. on
CentOS 7 and Rocky Linux 8) where ``GTEST_SKIP()`` is not available.

[TEST-03] The system shall provide integration tests that run against a live SNMP agent and validate
real GET, WALK, and BULKWALK operations.

[TEST-04] The system shall maintain code coverage reporting for both Python and C++ components via
Codecov across all CI test workflows, including Codecov Test Analytics for tracking test suite
duration and failure trends.

[TEST-05] The test infrastructure shall provide coverage path normalization utilities
(``python_tests/normalize_coverage_paths.py``) to reconcile differing source file paths between
Docker container mount points and host workspaces prior to uploading coverage reports to Codecov.

[TEST-06] Dockerized test matrices running Python test suites across supported Linux distributions
and Python versions shall partition tests into consolidated logical test groups (such as session
operations, walk operations, SNMP ops, and core utilities) ensuring 100% test file coverage across
all test files without exceeding workflow matrix limits.

[TEST-07] The integration test runner (``integration_tests/run_integration_tests.sh``) shall enforce
cooldown pauses (such as 1-second delays) between distinct test phases (such as between GET, WALK,
and BULKWALK tests) to allow sockets and simulated SNMP agent daemons to settle, preventing false-
positive socket exhaustion and timeout errors under high-concurrency multi-process and multi-
threaded test runs.

Code Quality
~~~~~~~~~~~~

[QUAL-01] The system shall enforce Python code style using Black (line length 100, targeting all
supported Python versions).

[QUAL-02] The system shall enforce C++ code style using clang-format.

[QUAL-03] The system shall perform static security analysis on the codebase using CodeQL in CI.

[QUAL-04] The system shall perform memory safety analysis using Valgrind on Linux
(Homebrew/Linuxbrew) builds as part of CI.

[QUAL-05] The system shall run C++ tests compiled with LLVM/Clang sanitizers (including
AddressSanitizer, UndefinedBehaviorSanitizer, and MemorySanitizer) in CI and Docker test
environments to detect memory corruption, memory leaks, and undefined behavior.

Documentation
~~~~~~~~~~~~~

[DOCS-01] The system shall provide Sphinx-based HTML documentation including installation
instructions, API reference, and a development guide.

[DOCS-02] The documentation system shall maintain versioned documentation archives for each
published release, served alongside development documentation via GitHub Pages with an automated
version-selector landing page.

CI/CD and Maintenance
~~~~~~~~~~~~~~~~~~~~~

[CICD-01] The system shall publish release distributions to both PyPI and TestPyPI via CI workflows
triggered on release events.

[CICD-02] The system shall publish Docker images for use in testing across multiple Linux
distributions.

[CICD-03] The CHANGELOG shall be automatically generated and maintained by a CI workflow.

[CICD-04] The system shall automatically sync open pull requests with the main branch via a
scheduled CI workflow.

[CICD-05] The system shall monitor supported Python versions and raise alerts or auto-update when a
new supported version is added or an old one reaches end-of-life.

[CICD-06] The TestPyPI publishing workflow shall support manual triggering (``workflow_dispatch``)
in addition to push-triggered builds, and shall bypass the changed-files gate when manually
dispatched.

[CICD-07] CI steps that run platform-specific commands through a third-party wrapper action (for
example one that dispatches to a shell based on the runner OS) shall explicitly propagate the
wrapped command's exit code (for example ``if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }`` on
Windows/PowerShell) rather than relying on the wrapper to do so, since a PowerShell script invoked
via ``pwsh -command "& '{0}'"`` does not automatically surface a failed native command's
``$LASTEXITCODE`` as the process exit code, which would otherwise let a failing build report a
false-positive success.

[CICD-08] The system shall automatically update and deploy the official Homebrew formula
(``Formula/ezsnmp.rb``) with release tags, source tarball URLs, and SHA-256 checksums upon
publication of new releases.

[CICD-09] CI workflows shall utilize build caching for C++ compilation artifacts and Python
dependencies (pip and tox caches) with invalidation based on dependency file hashes, providing
fallback mechanisms to clean builds when incremental builds fail.

[CICD-10] All CI workflows utilizing matrix strategies (including Dockerized Python and C++ test
matrices, native test matrices, and integration test matrices) shall enforce that the total number
of matrix job combinations remains strictly below the GitHub Actions platform limit of 256 jobs per
matrix strategy:

- **Matrix Dimension Upper Bound**: For every workflow matrix strategy, the total Cartesian product
  of all dimensions (such as ``distributions`` × ``python_versions`` × ``test_groups``, accounting
  for any ``include`` or ``exclude`` rules) shall not exceed 256 jobs.
- **Future Additions & Re-Architecting**: Whenever future changes expand matrix dimensions—such as
  adding support for newer Python versions (e.g. Python 3.15+), new Linux distributions, or
  additional test suites—the workflow configuration shall be audited and kept strictly under the
  256-job limit. If any future addition would cause the product to reach or exceed 256 (for example,
  11 distributions × 6 Python versions × 4 test groups = 264 jobs), the workflow shall be re-
  partitioned (e.g. by consolidating test groups into fewer groups, splitting versions or
  distributions across separate workflow files, or using workflow dispatch/matrix chunking) so that
  all jobs can be scheduled and executed.
- **Test Coverage Guarantee**: Consolidation of matrix dimensions or test groups shall never reduce
  test coverage; all test files must continue to run across all matrix targets.
- **Downstream Safety Guards**: Downstream reporting and coverage aggregation jobs shall explicitly
  check for the existence of upstream test result and coverage artifacts before attempting uploads
  or posting comments, preventing empty coverage reports or missing JUnit XML warnings if upstream
  jobs are skipped or fail.
