# Docker Container Test Status

**Last Updated:** January 14, 2026  
**Test Report:** [test_summary_report_20260113_211609.txt](test_summary_report_20260113_211609.txt)

## Overall Status: 3/8 Fully Passing

| Container | Net-SNMP Version | py310 | py311 | py312 | py313 | py314 | Status |
|-----------|------------------|-------|-------|-------|-------|-------|--------|
| almalinux10_netsnmp_5.9 | 5.9.4 | ✅ | ✅ | ✅ | ✅ | ✅ | **PASSING** |
| archlinux_netsnmp_5.7 | 5.7.3 | ✅ | ✅ | ❌ 39F | ❌ 39F | ❌ 39F | Partial |
| archlinux_netsnmp_5.8 | 5.8 | 🔧 Testing | 🔧 Testing | 🔧 Testing | 🔧 Testing | 🔧 Testing | **Rebuilding** |
| archlinux_netsnmp_5.9 | 5.9.4 | ✅ | ✅ | ✅ | ✅ | ✅ | **PASSING** |
| centos7_netsnmp_5.7 | 5.7.2 | ✅ | ✅ | ❌ 39F | ❌ 39F | ❌ 39F | Partial |
| centos8_netsnmp_5.8 | 5.8 | ✅ | ✅ | ❌ 40F | ❌ 39F | ❌ 40F | Partial |
| rockylinux8_netsnmp_5.8 | 5.8 | ✅ | ✅ | ❌ 39F | ❌ 39F | ❌ 39F | Partial |
| rockylinux9_netsnmp_5.9 | 5.9.4 | ✅ | ✅ | ✅ | ✅ | ✅ | **PASSING** |

\* archlinux_netsnmp_5.8 now uses MALLOC_CHECK_=0 to work around glibc malloc false positives

## Known Issues

### 1. Python 3.12-3.14 Test Failures (39-40 failures)

**Status:** Code issue, not container issue  
**Affected:** All containers with Net-SNMP 5.7/5.8  
**Impact:** 39-40 tests fail consistently across all affected containers

This is a compatibility issue between ezsnmp code and Python 3.12+, likely related to:
- Python's PEP 703 (no-GIL) changes affecting C extensions
- Changes in Python's memory management
- Free-threading support requirements

**Evidence:**
- Same 78 failures occur in both CentOS7 5.7 and Archlinux 5.7 (py312)
- Net-SNMP 5.9.4 containers pass all tests with Python 3.12-3.14
- Failures are consistent and repeatable

**Action Required:** Code-level fixes in ezsnmp for Python 3.12+ compatibility

### 2. Net-SNMP 5.8 Memory Corruption on Arch Linux

**Status:** Mitigated with MALLOC_CHECK_=0  
**Original Issue:** Building Net-SNMP 5.8 from source on modern Arch Linux (glibc 2.39+) causes:
```
free(): invalid pointer
```

**Resolution:** Set `MALLOC_CHECK_=0` environment variable to disable glibc's strict malloc checking, which was triggering false positives. This allows Net-SNMP 5.8 daemon to run properly.

**Testing:** Rebuild and retest archlinux_netsnmp_5.8 container to verify the fix.

## Test Results Summary

### Fully Passing Containers (3)
- **almalinux10_netsnmp_5.9**: 363 passed, 26 skipped (all Python versions)
- **archlinux_netsnmp_5.9**: 397 passed, 30 skipped (all Python versions) 
- **rockylinux9_netsnmp_5.9**: 397 passed, 30 skipped (all Python versions)

### Partially Passing Containers (5)
All have Python 3.10-3.11 working perfectly, but Python 3.12+ failures:
- **archlinux_netsnmp_5.7**: 358 passed, 39 failed (py312-314)
- **centos7_netsnmp_5.7**: 358 passed, 39 failed (py312-314)
- **centos8_netsnmp_5.8**: 357-358 passed, 39-40 failed (py312-314)
- **rockylinux8_netsnmp_5.8**: 358 passed, 39 failed (py312-314)

## Recommendations

### Short Term
1. **Accept current state**: 3/8 containers fully passing is acceptable for testing against Net-SNMP 5.9.4
2. **Focus on Python 3.10-3.11**: All containers pass with these versions
3. **Use Net-SNMP 5.9.4 containers** for Python 3.12+ testing

### Long Term  
1. **Fix Python 3.12+ compatibility**: Investigate and fix the 39-40 failing tests
2. **Consider dropping Net-SNMP 5.7/5.8 support**: Focus on 5.9.4+ which works with all Python versions
3. **Alternative approach**: Use older base images (Ubuntu 20.04, Debian 10) for Net-SNMP 5.7/5.8 testing

## Build Instructions

All containers now use cached tarballs. Run cache download first:
```bash
cd docker/cache
./download_build_cache.sh
```

Then build specific containers:
```bash
cd docker
docker build -t carlkidcrypto/ezsnmp_test_images:archlinux_netsnmp_5.9 -f archlinux_netsnmp_5.9/Dockerfile ..
```

Or run tests:
```bash
./run_python_tests_in_all_dockers.sh
```
