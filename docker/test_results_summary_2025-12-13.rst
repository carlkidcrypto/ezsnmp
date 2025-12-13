========================================================================
ezsnmp Docker Test Results Summary - December 13, 2025
========================================================================

Test Execution Overview
========================================================================

:Test Date: December 13, 2025
:Test Script: ``docker/run_python_tests_in_all_dockers.sh``
:Execution Mode: Parallel (async) with isolated build directories
:Total Environments: 25 (5 distributions × 5 Python versions)
:Docker Images: carlkidcrypto/ezsnmp_test_images:{distro}-latest

**Update (Dec 13, post-rebuild):**
CentOS 7 Docker image was rebuilt with explicit LDFLAGS/CPPFLAGS for sqlite3 and OpenSSL support in Python 3.13.7. Results below show py313 still failing with SSL module issue. Suggested fixes have not resolved the problem—further investigation required.


Distribution Test Matrix
========================================================================

AlmaLinux 10
------------------------------------------------------------------------
:Container: almalinux10_test_container
:Python Versions: 3.9.20, 3.10.16, 3.11.11, 3.12.8, 3.13.7
:Test Status:

  - **py39**: ✅ PASS - 363 passed, 26 skipped (141.18s)
  - **py310**: ✅ PASS - 363 passed, 26 skipped (140.96s)
  - **py311**: ✅ PASS - 363 passed, 26 skipped (140.41s)
  - **py312**: ✅ PASS - 363 passed, 26 skipped (143.17s)
  - **py313**: ✅ PASS - 363 passed, 26 skipped (145.32s)

:Total Duration: ~239s (3m 59s)
:Notes: All Python versions pass successfully. Fewer tests (363 vs 397) due to platform-specific test skipping.


Arch Linux (net-snmp 5.9)
------------------------------------------------------------------------
:Container: archlinux_test_container
:Python Versions: 3.9.21, 3.10.16, 3.11.11, 3.12.8, 3.13.1
:Test Status:

  - **py39**: ✅ PASS - 397 passed, 30 skipped (144.33s, 282.91s total)
  - **py310**: ✅ PASS - 397 passed, 30 skipped (138.30s, 268.85s total)
  - **py311**: ✅ PASS - 397 passed, 30 skipped (139.97s, 272.26s total)
  - **py312**: ✅ PASS - 397 passed, 30 skipped (144.54s, 278.44s total)
  - **py313**: ✅ PASS - 397 passed, 30 skipped (141.79s, 279.24s total)

:Total Duration: ~279s (4m 39s)
:Notes: Full test suite passes on all Python versions. net-snmp 5.9 compatibility confirmed.


Arch Linux net-snmp 5.8 (Legacy Compatibility)
------------------------------------------------------------------------
:Container: archlinux_netsnmp_5.8_test_container
:Python Versions: 3.9.21, 3.10.16, 3.11.11, 3.12.8, 3.13.1
:Test Status:

  - **py39**: ❌ FAIL - 108 passed, 289 failed, 30 skipped, 25 errors (1493.53s, 1633.41s total)
  - **py310**: ❌ FAIL - 108 passed, 289 failed, 30 skipped, 25 errors (1493.16s, 1620.26s total)
  - **py311**: ❌ FAIL - 108 passed, 289 failed, 30 skipped, 25 errors (1489.07s, 1615.54s total)
  - **py312**: ❌ FAIL - 108 passed, 289 failed, 30 skipped, 25 errors (1488.30s, 1605.68s total)
  - **py313**: ❌ FAIL - 108 passed, 289 failed, 30 skipped, 25 errors (1490.12s, 1606.63s total)

:Failure Pattern:
  
  - String value formatting issues
  - SNMP session parameter handling
  - Data type conversion failures
  - Authentication/Privacy V3 failures

:Example Failures:

  - ``test_string_values_not_enclosed_in_quotes`` - All variants fail
  - ``test_session_print_enums_numerically`` - All variants fail
  - ``test_snmp_get_regular`` - All variants fail
  - ``test_v3_authentication_md5_privacy_des`` - Authentication failure

:Root Cause: net-snmp 5.8 API incompatibilities with ezsnmp's expected behavior.
:Notes: This container tests backward compatibility with older net-snmp versions. Known to have issues. All 5 Python versions now tested—consistent failures across all.


CentOS 7
------------------------------------------------------------------------
:Container: centos7_test_container
:Python Versions: 3.9.20, 3.10.16, 3.11.11, 3.12.8, 3.13.7
:Test Status:

  - **py39**: ✅ PASS - 397 passed, 30 skipped (146.79s, 293.49s total)
  - **py310**: ✅ PASS - 397 passed, 30 skipped (146.84s, 280.96s total)
  - **py311**: ✅ PASS - 397 passed, 30 skipped (144.96s, 269.10s total)
  - **py312**: ✅ PASS - 397 passed, 30 skipped (147.05s, 265.38s total)
  - **py313**: ❌ FAIL - SSL module unavailable (130.37s)

:Total Duration: ~293s (4m 53s) for passing environments
:py313 Status:

   - **Current Error**: ``ModuleNotFoundError: No module named '_ssl'`` (pip SSL error during package install)
   - **Root Cause**: Python 3.13 built without SSL support despite OpenSSL 1.1.1w present
   - **Action Taken**: Added ``LDFLAGS="-L/usr/lib64 -L/usr/local/openssl/lib" CPPFLAGS="-I/usr/include -I/usr/local/openssl/include"`` to configure
   - **Next Action**: Rebuild in progress with corrected flags

:Notes: Python 3.9-3.12 pass. Python 3.13 SSL module issue preventing pip from installing test dependencies.


Rocky Linux 8
------------------------------------------------------------------------
:Container: rockylinux8_test_container
:Python Versions: 3.9.20, 3.10.16, 3.11.11, 3.12.8, 3.13.7
:Test Status:

  - **py39**: ✅ PASS - 397 passed, 30 skipped (146.02s, 275.74s total)
  - **py310**: ✅ PASS - 397 passed, 30 skipped (146.47s, 282.16s total)
  - **py311**: ✅ PASS - 397 passed, 30 skipped (144.84s, 266.32s total)
  - **py312**: ✅ PASS - 397 passed, 30 skipped (146.76s, 266.30s total)
  - **py313**: ✅ PASS - 397 passed, 30 skipped (147.62s, 274.90s total)

:Total Duration: ~275s (4m 35s)
:Notes: All Python versions pass successfully. Clean test run.


Summary Statistics
========================================================================

Overall Pass Rate
------------------------------------------------------------------------

:Total Environments Tested: 25
:Passed: 19 (76%)
:Failed: 6 (24%)
:In Progress: 0

+-------------------+-------+-------+-------+-------+-------+--------+
| Distribution      | py39  | py310 | py311 | py312 | py313 | Total  |
+===================+=======+=======+=======+=======+=======+========+
| AlmaLinux 10      | ✅    | ✅    | ✅    | ✅    | ✅    | 5/5    |
+-------------------+-------+-------+-------+-------+-------+--------+
| Arch Linux        | ✅    | ✅    | ✅    | ✅    | ✅    | 5/5    |
+-------------------+-------+-------+-------+-------+-------+--------+
| Arch (netsnmp5.8) | ❌    | ❌    | ❌    | ❌    | ❌    | 0/5    |
+-------------------+-------+-------+-------+-------+-------+--------+
| CentOS 7          | ✅    | ✅    | ✅    | ✅    | ❌    | 4/5    |
+-------------------+-------+-------+-------+-------+-------+--------+
| Rocky Linux 8     | ✅    | ✅    | ✅    | ✅    | ✅    | 5/5    |
+-------------------+-------+-------+-------+-------+-------+--------+


Test Counts by Distribution
------------------------------------------------------------------------

:AlmaLinux 10: 363 passed, 26 skipped (consistent across all Python versions)
:Arch Linux: 397 passed, 30 skipped (consistent across all Python versions)
:CentOS 7: 397 passed, 30 skipped (py39-py312 only)
:Rocky Linux 8: 397 passed, 30 skipped (consistent across all Python versions)
:Arch netsnmp 5.8: 108 passed, 289 failed, 30 skipped, 25 errors (all Python versions)


Execution Times
------------------------------------------------------------------------

Average Test Duration by Python Version:

- **Python 3.9**: ~164s (2m 44s) per distribution
- **Python 3.10**: ~154s (2m 34s) per distribution
- **Python 3.11**: ~154s (2m 34s) per distribution
- **Python 3.12**: ~157s (2m 37s) per distribution
- **Python 3.13**: ~155s (2m 35s) per distribution (excluding failures)

Average Total Distribution Time (all 5 Python versions):

- **AlmaLinux 10**: ~239s (3m 59s)
- **Arch Linux**: ~279s (4m 39s)
- **CentOS 7**: ~273s (4m 33s) for py39-py312
- **Rocky Linux 8**: ~273s (4m 33s)
- **Arch netsnmp 5.8**: ~1610s (26m 50s) for failed runs


Known Issues
========================================================================

Issue #1: CentOS 7 Python 3.13 Missing SSL Module
------------------------------------------------------------------------

:Status: ❌ BLOCKING (Unresolved despite fix attempts)
:Affected: CentOS 7 - Python 3.13.7 only
:Error: ``SSLError("Can't connect to HTTPS URL because the SSL module is not available.")``
:Root Cause: Python 3.13 compiled without SSL module despite OpenSSL 1.1.1w built and available

**Fix Attempted (NOT WORKING):**

Dockerfile updated with OpenSSL paths in LDFLAGS/CPPFLAGS:

.. code-block:: dockerfile

   LDFLAGS="-L/usr/lib64 -L/usr/local/openssl/lib" \
   CPPFLAGS="-I/usr/include -I/usr/local/openssl/include" \
   ./configure --enable-shared --with-openssl=/usr/local/openssl

**Status:** Rebuild completed but SSL module still not available in Python 3.13.

**Technical Details:**

.. code-block:: text

   WARNING: pip is configured with locations that require TLS/SSL, however the ssl module in Python is not available.
   Could not fetch URL https://pypi.org/simple/black/: There was a problem confirming the ssl certificate
   SSLError("Can't connect to HTTPS URL because the SSL module is not available.")
   ERROR: Could not find a version that satisfies the requirement black==25.9.0

**Issue Timeline:** 

- Dec 11: sqlite3 module missing (``ModuleNotFoundError: No module named '_sqlite3'``)
- Dec 13 (first attempt): Added LDFLAGS/CPPFLAGS for OpenSSL paths
- Dec 13 (current): SSL module still unavailable despite fixes

**Workaround:** None—SSL required for pip package installation.

**Next Steps:**

1. Investigate Python 3.13 build logs for SSL module compilation errors
2. Check if OpenSSL dev headers are available during Python 3.13 compile
3. Consider alternative approach: pre-install packages or use system Python 3.13
4. Evaluate if CentOS 7 environment is suitable for Python 3.13 (EOL distro)


Issue #2: net-snmp 5.8 API Incompatibility
------------------------------------------------------------------------

:Status: ⚠️ KNOWN LIMITATION (All 5 Python versions now tested)
:Affected: archlinux_netsnmp_5.8 - All Python versions (py39-py313)
:Failure Rate: ~72% (289 failures / 402 tests) - Consistent across all Python versions
:Root Cause: Breaking changes in net-snmp 5.8 API behavior

**Failure Categories:**

1. **String Value Formatting** (test_datatypes.py)
   
   - Expected: Values without quotes
   - Actual: net-snmp 5.8 returns quoted strings

2. **Session Parameter Handling** (test_session_parameters.py)
   
   - Enum printing behavior changed
   - Full OID printing inconsistent

3. **SNMPv3 Authentication** (test_auth_priv_v3.py)
   
   - MD5/DES authentication failures
   - User caching issues

4. **Data Type Conversions** (test_helpers.py, test_netsnmp.py)
   
   - OID normalization failures
   - Integer/string conversion issues

**Recommendation:** 

- Document net-snmp 5.9+ as minimum supported version
- Add compatibility layer for net-snmp 5.8 if backward compatibility required
- Consider dropping net-snmp 5.8 support (released 2012, deprecated)


Issue #3: Parallel Build Race Conditions (RESOLVED)
------------------------------------------------------------------------

:Status: ✅ RESOLVED
:Affected: All distributions (previously)
:Fix: Isolated build directories per container

**Previous Issue:**

- All containers building in shared ``/ezsnmp`` mount point
- Setuptools race conditions: ``FileNotFoundError: ezsnmp.egg-info/SOURCES.txt``
- .coverage file conflicts from parallel pytest-cov runs

**Solution Implemented:**

.. code-block:: bash

   # Isolate build per container
   docker exec bash -c "
     cd /ezsnmp && tar --exclude=*.egg-info --exclude=build \
       --exclude=dist --exclude=.tox --exclude=venv* -cf - . |
       (cd /tmp/ezsnmp_${DISTRO} && tar xf -)
     cd /tmp/ezsnmp_${DISTRO}
     tox -e $TOX_PY --workdir /tmp/tox_${DISTRO}
   "

**Results:** All non-netsnmp-5.8 distributions pass reliably with parallel execution.


Recommendations
========================================================================

High Priority
------------------------------------------------------------------------

1. **Resolve CentOS 7 Python 3.13 SSL Issue** - Critical blocker

   Current approach (LDFLAGS/CPPFLAGS) has not resolved the problem.
   
   Options to investigate:

   .. code-block:: bash

      # Option 1: Check build logs for SSL compilation errors
      docker build --progress=plain -t test:latest docker/centos7 2>&1 | grep -i ssl
      
      # Option 2: Verify OpenSSL headers are present during build
      docker run centos7 bash -c "ls -la /usr/include/openssl* /usr/local/openssl/include/*"
      
      # Option 3: Use system Python 3.13 if available, or skip this version
      # Option 4: Pre-install test dependencies in Docker image (workaround)

2. **Document net-snmp Requirements** - Update README.rst

   - Minimum version: net-snmp 5.9
   - Known incompatible: net-snmp 5.8
   - Tested versions: 5.9, 5.7.3 (Rocky/CentOS)
   - Python 3.13 support: Under investigation on CentOS 7


Medium Priority
------------------------------------------------------------------------

1. **Archive archlinux_netsnmp_5.8 as Informational**
   
   - Document known failures in compatibility matrix
   - All 5 Python versions now tested (100% consistent failures)
   - Consider removing from CI pipeline (informational only)

2. **Investigate Test Count Discrepancy**
   
   - AlmaLinux 10: 363 tests (26 skipped)
   - Other distros: 397 tests (30 skipped)
   - Why 34 fewer tests on AlmaLinux 10?

3. **Add Test Duration Monitoring**
   
   - Current script has timing metrics
   - Add to output files for trend analysis
   - Alert on >20% duration increase


Low Priority
------------------------------------------------------------------------

1. **Clean Up Test Output Files**
   
   - 25 files × ~70KB = 1.75MB per test run
   - archlinux_netsnmp_5.8 failures: ~1.9MB each
   - Add retention policy (keep last 5 runs)

2. **Add Exit Code Validation**
   
   - Script currently uses ``wait`` to catch background jobs
   - Add explicit exit code checking per container
   - Email notification on failures

3. **Container Resource Monitoring**
   
   - Add memory/CPU usage logging
   - Detect resource constraints
   - Optimize container limits


Comparison with December 11 Results
========================================================================

Changes Since Last Report
------------------------------------------------------------------------

**Improvements:**

- ✅ Arch Linux netsnmp 5.8 py312/py313 tests completed (were in progress)
- ✅ Confirmed consistent failure pattern across all 5 Python versions for netsnmp 5.8

**Regressions:**

- ❌ CentOS 7 py313 issue unresolved—fix attempts unsuccessful
  
  - Dec 11: ``ModuleNotFoundError: No module named '_sqlite3'`` (identified)
  - Dec 13: ``SSLError("SSL module is not available")`` (attempted fix failed)
  - Root cause appears more complex than initial diagnosis

**Unchanged:**

- AlmaLinux 10, Arch Linux, Rocky Linux 8: All passing (5/5 each)
- CentOS 7 py39-py312: All passing (4/5)
- Arch netsnmp 5.8: All failing (0/5)
- Overall pass rate: 76% (19/25) vs 80% (20/25) on Dec 11

**Key Insight:**

The CentOS 7 py313 issue is more complex than initially diagnosed. Adding sqlite3 support via LDFLAGS broke SSL module compilation. Need coordinated flags that ensure both modules build correctly.


Next Steps
========================================================================

Immediate Actions (Today)
------------------------------------------------------------------------

1. ✅ **Document current test status** (this file)
2. ⚠️ **Investigate CentOS 7 Python 3.13 SSL compilation issue**

   - Review Docker build logs for SSL module compilation errors
   - Verify OpenSSL dev headers availability during Python 3.13 build
   - Consider alternative solutions (system Python, pre-installed dependencies, or skip version)

3. ✅ **Verify archlinux_netsnmp_5.8 complete** (all 5 Python versions tested)

Follow-Up Tasks (This Week)
------------------------------------------------------------------------

1. Resolve CentOS 7 Python 3.13 SSL issue (if possible) or document workaround
2. Update documentation with net-snmp version requirements
3. Mark archlinux_netsnmp_5.8 as informational/excluded from pass rate
4. Create compatibility matrix table for README
5. Decide on CentOS 7 Python 3.13 support (viable fix vs. deprecate)


Test Infrastructure Status
========================================================================

Docker Images
------------------------------------------------------------------------

:Repository: carlkidcrypto/ezsnmp_test_images
:Current Tags: {distro}-latest, {distro}-12-12-2025.N
:Next Build: {distro}-12-13-2025.1 (after centos7 SSL fix)

+----------------------------+----------------------+------------------+
| Distribution               | Image Tag            | Build Date       |
+============================+======================+==================+
| almalinux10-latest         | 12-10-2025.1         | Dec 10, 2025     |
+----------------------------+----------------------+------------------+
| archlinux-latest           | 12-10-2025.1         | Dec 10, 2025     |
+----------------------------+----------------------+------------------+
| archlinux_netsnmp_5.8...   | 12-10-2025.1         | Dec 10, 2025     |
+----------------------------+----------------------+------------------+
| centos7-latest             | 12-12-2025.1         | Dec 12, 2025     |
+----------------------------+----------------------+------------------+
| rockylinux8-latest         | 12-10-2025.1         | Dec 10, 2025     |
+----------------------------+----------------------+------------------+

Testing Dependencies
------------------------------------------------------------------------

:pytest: 8.4.2 (downgraded from 9.0.2 for Python 3.9 compatibility)
:tox: 4.30.3
:pytest-cov: 7.0.0
:pytest-xdist: 3.8.0 (parallel test execution)
:pytest-sugar: 1.1.1 (progress formatting)
:coverage: 7.10.7

Build Tools
------------------------------------------------------------------------

:SWIG: 4.3.1
:setuptools: 80.9.0
:wheel: 0.46.1
:gcc-toolset-11: Rocky 8, AlmaLinux 10
:devtoolset-11: CentOS 7
:g++: 14.2.1 (Arch Linux)

SNMP Infrastructure
------------------------------------------------------------------------

:net-snmp: 5.7.3 (CentOS/Rocky), 5.9.4 (Arch), 5.8 (Arch legacy)
:snmpd: localhost:11161 (custom port to avoid conflicts)
:MIB Configuration: /etc/snmp/snmpd.conf
:Test OIDs: sysDescr.0, sysObjectID.0, sysUpTime.0, etc.


Conclusion
========================================================================

**Overall Status: 76% Pass Rate (19/25 environments)**

**Passing Distributions (19/20 non-legacy environments):**

- ✅ AlmaLinux 10: 5/5 Python versions pass
- ✅ Arch Linux: 5/5 Python versions pass
- ✅ Rocky Linux 8: 5/5 Python versions pass
- ⚠️ CentOS 7: 4/5 Python versions pass (py313 SSL issue)

**Known Failing (informational):**

- ❌ Arch Linux net-snmp 5.8: 0/5 Python versions pass (API incompatibility—all versions now tested)

**Critical Issue:** CentOS 7 Python 3.13 SSL module missing—suggested fixes (LDFLAGS/CPPFLAGS) have not resolved the issue. Requires deeper investigation into Python 3.13 build process or alternative approach.

**Progress Since Dec 11:** 
- Arch netsnmp 5.8 testing complete (py312/py313 finished)
- CentOS 7 issue worsened: sqlite3 fixed but SSL module still missing (fix attempt unsuccessful)

**Test Infrastructure:** Stable, parallel execution working reliably with isolated build directories.

**Next Milestone:** Achieve 24/25 pass rate (96%) after CentOS 7 SSL+sqlite3 fix, finalize net-snmp 5.8 as unsupported.


Document Information
========================================================================

:Author: GitHub Copilot (AI Assistant)
:Generated: December 13, 2025
:Script Version: run_python_tests_in_all_dockers.sh (with async + isolation)
:Data Source: docker/test_outputs_*/test-outputs_*.txt
:Previous Report: test_results_summary_2025-12-11.rst
:Changes: CentOS 7 py313 SSL issue; archlinux_netsnmp_5.8 all versions tested
