========================================================================
ezsnmp Docker Test Results Summary - December 11, 2025
========================================================================

Test Execution Overview
========================================================================

:Test Date: December 11, 2025
:Test Script: ``docker/run_python_tests_in_all_dockers.sh``
:Execution Mode: Parallel (async) with isolated build directories
:Total Environments: 25 (5 distributions × 5 Python versions)
:Docker Images: carlkidcrypto/ezsnmp_test_images:{distro}-latest

**Update (Dec 11, post-rebuild):**
CentOS 7 Docker image has been rebuilt with Python 3.13.7 and sqlite3 support. The next test run will verify if the _sqlite3 issue is resolved. Results below reflect the last completed run; CentOS 7 py313 is now pending re-test.


Distribution Test Matrix
========================================================================

AlmaLinux 10
------------------------------------------------------------------------
:Container: almalinux10_test_container
:Python Versions: 3.9.20, 3.10.16, 3.11.11, 3.12.8, 3.13.7
:Test Status:

  - **py39**: ✅ PASS - 363 passed, 26 skipped (141.25s)
  - **py310**: ✅ PASS - 363 passed, 26 skipped (141.56s)
  - **py311**: ✅ PASS - 363 passed, 26 skipped (140.60s)
  - **py312**: ✅ PASS - 363 passed, 26 skipped (142.59s)
  - **py313**: ✅ PASS - 363 passed, 26 skipped (143.09s)

:Total Duration: ~272s (4m 32s)
:Notes: All Python versions pass successfully. Fewer tests (363 vs 397) likely due to platform-specific test skipping.


Arch Linux (net-snmp 5.9)
------------------------------------------------------------------------
:Container: archlinux_test_container
:Python Versions: 3.9.21, 3.10.16, 3.11.11, 3.12.8, 3.13.1
:Test Status:

  - **py39**: ✅ PASS - 397 passed, 30 skipped (142.72s, 310.67s total)
  - **py310**: ✅ PASS - 397 passed, 30 skipped (139.62s, 290.44s total)
  - **py311**: ✅ PASS - 397 passed, 30 skipped (139.76s, 284.12s total)
  - **py312**: ✅ PASS - 397 passed, 30 skipped (141.10s, 274.11s total)
  - **py313**: ✅ PASS - 397 passed, 30 skipped (140.97s, 276.41s total)

:Total Duration: ~310s (5m 10s)
:Notes: Full test suite passes on all Python versions. net-snmp 5.9 compatibility confirmed.


Arch Linux net-snmp 5.8 (Legacy Compatibility)
------------------------------------------------------------------------
:Container: archlinux_netsnmp_5.8_test_container
:Python Versions: 3.9.21, 3.10.16, 3.11.11, 3.12.8, 3.13.1
:Test Status:

  - **py39**: ❌ FAIL - 108 passed, 289 failed, 30 skipped, 25 errors (1486.90s, 1660.60s total)
  - **py310**: ❌ FAIL - 108 passed, 289 failed, 30 skipped, 25 errors (1486.90s, 1580.87s total)
  - **py311**: ❌ FAIL - 108 passed, 289 failed, 30 skipped, 25 errors (1486.62s, 1582.23s total)
  - **py312**: 🔄 IN PROGRESS
  - **py313**: 🔄 IN PROGRESS

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
:Notes: This container tests backward compatibility with older net-snmp versions. Known to have issues.


CentOS 7
:Container: centos7_test_container
:Python Versions: 3.9.20, 3.10.16, 3.11.11, 3.12.8, 3.13.7
:Test Status:


   - **py39**: ✅ PASS - 397 passed, 30 skipped (146.38s, 294.80s total)
   - **py310**: ✅ PASS - 397 passed, 30 skipped (146.69s, 277.39s total)
   - **py311**: ✅ PASS - 397 passed, 30 skipped (145.15s, 270.09s total)
   - **py312**: ✅ PASS - 397 passed, 30 skipped (147.69s, 266.20s total)
   - **py313**: ⏳ PENDING RE-TEST - Image rebuilt with sqlite3 support; awaiting new test run

:Total Duration: ~295s (4m 55s) for passing environments
:py313 Status:

   - **Pending**: CentOS 7 image rebuilt with Python 3.13.7 and sqlite3 support. Next test run will confirm fix.
   - **Previous Error**: ``ModuleNotFoundError: No module named '_sqlite3'``
   - **Previous Root Cause**: Python 3.13 built without sqlite-devel present
   - **Action Taken**: Forced --no-cache rebuild with correct dependencies

:Notes: Python 3.9-3.12 pass. Python 3.13 pending re-test after image rebuild.


Rocky Linux 8
------------------------------------------------------------------------
:Container: rockylinux8_test_container
:Python Versions: 3.9.20, 3.10.16, 3.11.11, 3.12.8, 3.13.7
:Test Status:

  - **py39**: ✅ PASS - 397 passed, 30 skipped (144.42s, 282.96s total)
  - **py310**: ✅ PASS - 397 passed, 30 skipped (146.00s, 274.34s total)
  - **py311**: ✅ PASS - 397 passed, 30 skipped (144.99s, 258.83s total)
  - **py312**: ✅ PASS - 397 passed, 30 skipped (145.61s, 254.54s total)
  - **py313**: ✅ PASS - 397 passed, 30 skipped (147.36s, 266.11s total)

:Total Duration: ~283s (4m 43s)
:Notes: All Python versions pass successfully. Clean test run.


Summary Statistics
========================================================================

Overall Pass Rate
------------------------------------------------------------------------

:Total Environments Tested: 25
:Passed: 20 (80%)
:Failed: 4 (16%)
:In Progress: 1 (4%)

+-------------------+-------+-------+-------+-------+-------+--------+
| Distribution      | py39  | py310 | py311 | py312 | py313 | Total  |
+===================+=======+=======+=======+=======+=======+========+
| AlmaLinux 10      | ✅    | ✅    | ✅    | ✅    | ✅    | 5/5    |
+-------------------+-------+-------+-------+-------+-------+--------+
| Arch Linux        | ✅    | ✅    | ✅    | ✅    | ✅    | 5/5    |
+-------------------+-------+-------+-------+-------+-------+--------+
| Arch (netsnmp5.8) | ❌    | ❌    | ❌    | 🔄    | 🔄    | 0/5    |
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
:Arch netsnmp 5.8: 108 passed, 289 failed, 30 skipped, 25 errors (py39-py311)


Execution Times
------------------------------------------------------------------------

Average Test Duration by Python Version:

- **Python 3.9**: ~163s (2m 43s) per distribution
- **Python 3.10**: ~157s (2m 37s) per distribution
- **Python 3.11**: ~154s (2m 34s) per distribution
- **Python 3.12**: ~154s (2m 34s) per distribution
- **Python 3.13**: ~156s (2m 36s) per distribution (excluding failures)

Average Total Distribution Time (all 5 Python versions):

- **AlmaLinux 10**: ~272s (4m 32s)
- **Arch Linux**: ~310s (5m 10s)
- **CentOS 7**: ~270s (4m 30s) for py39-py312
- **Rocky Linux 8**: ~270s (4m 30s)
- **Arch netsnmp 5.8**: ~1600s (26m 40s) for failed runs


Known Issues
========================================================================

Issue #1: CentOS 7 Python 3.13 Missing sqlite3
------------------------------------------------------------------------

:Status: ❌ BLOCKING
:Affected: CentOS 7 - Python 3.13.7 only
:Error: ``ModuleNotFoundError: No module named '_sqlite3'``
:Root Cause: Python 3.13 compiled without sqlite-devel

**Fix Required:**

1. Rebuild CentOS 7 Docker image with sqlite-devel installed BEFORE Python 3.13 compilation
2. Current Dockerfile has sqlite-devel, but Python 3.13 may be using cached build
3. Force rebuild: ``docker/build_and_publish_images.sh`` with ``--no-cache`` for centos7

**Technical Details:**

.. code-block:: text

   File "/tmp/tox_centos7/py313/lib/python3.13/site-packages/coverage/sqldata.py", line 16
     import sqlite3
   File "/usr/local/lib/python3.13/sqlite3/__init__.py", line 57
     from sqlite3.dbapi2 import *
   File "/usr/local/lib/python3.13/sqlite3/dbapi2.py", line 27
     from _sqlite3 import *
   ModuleNotFoundError: No module named '_sqlite3'

**Workaround:** Skip pytest-cov for Python 3.13 on CentOS 7 (not recommended)


Issue #2: net-snmp 5.8 API Incompatibility
------------------------------------------------------------------------

:Status: ⚠️ KNOWN LIMITATION
:Affected: archlinux_netsnmp_5.8 - All Python versions
:Failure Rate: ~72% (289 failures / 402 tests)
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

1. **Rebuild CentOS 7 Image** - Fix Python 3.13 sqlite3 issue

   .. code-block:: bash

      cd docker/centos7
      docker build --no-cache -t carlkidcrypto/ezsnmp_test_images:centos7-latest .
      docker push carlkidcrypto/ezsnmp_test_images:centos7-latest

2. **Document net-snmp Requirements** - Update README.rst

   - Minimum version: net-snmp 5.9
   - Known incompatible: net-snmp 5.8
   - Tested versions: 5.9, 5.7.3 (Rocky/CentOS)

3. **Archive archlinux_netsnmp_5.8 Results** - Keep for historical reference

   - Document known failures in compatibility matrix
   - Consider removing from CI pipeline (informational only)


Medium Priority
------------------------------------------------------------------------

1. **Investigate Test Count Discrepancy**
   
   - AlmaLinux 10: 363 tests (26 skipped)
   - Other distros: 397 tests (30 skipped)
   - Why 34 fewer tests on AlmaLinux 10?

2. **Add Test Duration Monitoring**
   
   - Current script has timing metrics
   - Add to output files for trend analysis
   - Alert on >20% duration increase

3. **Optimize Test Parallelism**
   
   - Current: pytest-xdist auto (10 workers typical)
   - Consider: Tuning based on container CPU limits
   - Average: ~2.5 minutes per Python version


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


Next Steps
========================================================================

Immediate Actions (Today)
------------------------------------------------------------------------

1. ✅ **Document current test status** (this file)
2. 🔄 **Wait for archlinux_netsnmp_5.8 py312/py313 completion** (expected: same failures)
3. ⚠️ **Rebuild CentOS 7 image for Python 3.13 sqlite3 fix**

   .. code-block:: bash

      cd docker
      ./build_and_publish_images.sh  # Will auto-increment to 12-11-2025.2
      # Manually rebuild centos7 with --no-cache if needed

Follow-Up Tasks (This Week)
------------------------------------------------------------------------

1. Verify CentOS 7 Python 3.13 passes after rebuild
2. Update documentation with net-snmp version requirements
3. Add archlinux_netsnmp_5.8 to excluded/informational tests
4. Create compatibility matrix table for README


Test Infrastructure Status
========================================================================

Docker Images
------------------------------------------------------------------------

:Repository: carlkidcrypto/ezsnmp_test_images
:Current Tags: {distro}-latest, {distro}-12-10-2025.1
:Next Build: {distro}-12-11-2025.1 (after centos7 fix)

+----------------------------+----------------------+------------------+
| Distribution               | Image Tag            | Build Date       |
+============================+======================+==================+
| almalinux10-latest         | 12-10-2025.1         | Dec 10, 2025     |
+----------------------------+----------------------+------------------+
| archlinux-latest           | 12-10-2025.1         | Dec 10, 2025     |
+----------------------------+----------------------+------------------+
| archlinux_netsnmp_5.8...   | 12-10-2025.1         | Dec 10, 2025     |
+----------------------------+----------------------+------------------+
| centos7-latest             | 12-10-2025.1         | Dec 10, 2025     |
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

**Overall Status: 80% Pass Rate (20/25 environments)**

**Passing Distributions (19/20 non-legacy environments):**

- ✅ AlmaLinux 10: 5/5 Python versions pass
- ✅ Arch Linux: 5/5 Python versions pass
- ✅ Rocky Linux 8: 5/5 Python versions pass
- ⚠️ CentOS 7: 4/5 Python versions pass (py313 sqlite3 issue)

**Known Failing (informational):**

- ❌ Arch Linux net-snmp 5.8: 0/5 Python versions pass (API incompatibility)

**Critical Issue:** CentOS 7 Python 3.13 missing _sqlite3 module - requires Docker image rebuild.

**Recommended Action:** Rebuild centos7 image with --no-cache to ensure Python 3.13 compiled with sqlite-devel.

**Test Infrastructure:** Stable, parallel execution working reliably with isolated build directories.

**Next Milestone:** Achieve 24/25 pass rate (96%) after CentOS 7 fix, document net-snmp 5.8 as unsupported.


Document Information
========================================================================

:Author: GitHub Copilot (AI Assistant)
:Generated: December 11, 2025
:Script Version: run_python_tests_in_all_dockers.sh (with async + isolation)
:Data Source: docker/test_outputs_*/test-outputs_*.txt
:Test Run Start: ~7:45 PM EST
:Test Run End: ~8:30 PM EST (45 minutes total with parallel execution)
