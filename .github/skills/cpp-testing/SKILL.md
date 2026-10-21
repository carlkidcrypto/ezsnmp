---
name: cpp-testing
description: Use when building, running, or debugging Google Test C++ test suites in cpp_tests/ using Meson and Ninja, or collecting LCOV coverage.
---

# C++ Testing Guide (ezsnmp)

Use this skill when developing, executing, or debugging C++ unit tests in `cpp_tests/` for `ezsnmp`.

## 1. Environment & Tools

- **Framework**: Google Test (GTest)
- **Build System**: Meson (>= 1.3.0) and Ninja
- **Compiler**: GCC / G++ (>= 9.5; project defaults to G++ 13/14)
- **Coverage Tool**: LCOV (`lcov`, `genhtml`, `geninfo`)
- **Required Packages**: `gtest`, `gtest-devel` (or subproject wrap), `meson`, `ninja-build`, `lcov`, `net-snmp-devel`.

---

## 2. Building and Running C++ Tests

Navigate to `cpp_tests/` to configure, build, and run tests:

```bash
cd cpp_tests

# 1. Setup Meson build directory with coverage enabled
meson setup build -Db_coverage=true

# 2. Compile tests using Ninja
ninja -C build

# 3. Execute tests via Ninja test runner
ninja -C build test

# Alternatively, execute the test binary directly for detailed GTest output:
./build/run_unit_tests
```

### Running with Sanitizers (ASAN / UBSAN)
When debugging memory or undefined behavior issues:

```bash
ASAN_OPTIONS='halt_on_error=0' UBSAN_OPTIONS='halt_on_error=0' ninja -C build test
```

### Rebuilding after Code Changes
```bash
# Clean compilation cache
ninja -C build clean
ninja -C build
```

---

## 3. Code Coverage Collection

To generate LCOV coverage reports:

```bash
cd cpp_tests

# Use project coverage helper script
./get_test_coverage.sh

# Or manual multi-step capture:
find build/ -name '*.gcda' -delete 2>/dev/null || true
ninja -C build test
lcov --capture --directory build --output-file coverage.info --ignore-errors mismatch,gcov
lcov --remove coverage.info '/usr/*' '*/subprojects/*' '*/include/gtest/*' --output-file coverage_filtered.info --ignore-errors unused
genhtml coverage_filtered.info --output-directory coverage_html
```

---

## 4. Dockerized Multi-Distro Execution

To run C++ tests across all supported Linux distributions (AlmaLinux 10, Arch Linux, Fedora 42, Rocky Linux 9):

```bash
cd docker

# Run across all distributions
./run_cpp_tests_in_all_dockers.sh

# Run in a specific distribution
./run_cpp_tests_in_all_dockers.sh almalinux10_netsnmp_5.9
```

---

## 5. Best Practices & Guidelines

1. **Target 100% Coverage**: Every C++ helper function and session branch must have unit test assertions.
2. **Platform Agnostic**: Ensure tests compile cleanly without GCC-specific or Clang-specific warnings.
3. **Live SNMP Daemon**: For live network operations, use the test SNMP daemon configured by `python_tests/snmpd.conf` on `localhost:161`.
4. **Mock vs Live Tests**: Distinguish pure unit tests (mocking Net-SNMP sessions) from integration tests (querying live daemon).
