---
name: docker-test-environments
description: Use when building, running, debugging, or maintaining Docker test environments under docker/, executing multi-container test suites, or updating container dependencies.
---

# Docker Test Environments Guide (ezsnmp)

Use this skill when modifying Dockerfiles, running multi-OS containerized test suites, measuring cross-platform code coverage, or updating Python and Net-SNMP toolchains under `docker/` for `ezsnmp`.

## 1. Scope & Architecture

The `docker/` directory maintains reproducible test environments for various Linux distributions and Net-SNMP releases.

- **Primary Container Configurations**:
  - `almalinux10_netsnmp_5.10` (RHEL / Enterprise Linux 10 derivative)
  - `archlinux_netsnmp_5.10` (Rolling release Arch Linux)
  - `fedora42_netsnmp_5.10` (Modern Fedora with bleeding-edge GCC)
  - `rockylinux9_netsnmp_5.10` (RHEL / Enterprise Linux 9 derivative)
- **Docker Hub Repository**: `carlkidcrypto/ezsnmp_test_images`
- **Compiler Requirements**: All containers must provide **g++ 9.5 or higher** supporting C++17.
- **Python Version Matrix**: All containers must provide usable installations of **Python 3.11 through 3.15** (with associated development headers and isolated venvs).

---

## 2. Container Lifecycle & Execution Scripts

All multi-container operations are orchestrated via bash scripts located inside `docker/`. Always change into the `docker/` directory before executing these scripts:

```bash
cd docker
```

### Building and Publishing Images
Builds container images, tags them incrementally (`MM-DD-YYYY.N` / `-latest`), and publishes them to Docker Hub and GHCR:
```bash
./build_and_publish_images.sh
```

### Running Python Tests in All Containers
Runs pytest across published Docker containers, mounting the workspace and collecting individual JUnit/coverage outputs:
```bash
# Run across all published containers
./run_python_tests_in_all_dockers.sh

# Run on a specific container
./run_python_tests_in_all_dockers.sh almalinux10_netsnmp_5.10
```
- Tests run against each container's live Net-SNMP daemon launched via `docker/DockerEntry.sh`.
- Test outputs are logged to `test_outputs_<timestamp>/`.

### Running C++ Tests in All Containers
Runs Google Test suites via Meson/Ninja inside published containers:
```bash
# Run across all published containers
./run_cpp_tests_in_all_dockers.sh

# Run on a specific container
./run_cpp_tests_in_all_dockers.sh almalinux10_netsnmp_5.10
```
- Meson builds the test suite in a containerized build directory.
- Ninja executes tests and generates LCOV coverage data.

### Generating Consolidated Reports
Generates Markdown and text summaries from container test runs:
```bash
./generate_test_reports.sh
```
- Summaries are placed in `TEST_SUMMARY*.md`.

### Diagnosing Daemon Failures
If `snmpd` fails to start inside a container during tests, check logs using:
```bash
./check_snmpd_logs.sh <container_id_or_name>
```

---

## 3. Best Practices for Container Maintenance

1. **Minimal Image Size**:
   - Clean package manager caches within the same `RUN` step (e.g., `dnf clean all && rm -rf /var/cache/dnf`, `pacman -Scc --noconfirm`).
   - Remove temporary source tarballs after building custom packages.
2. **Coverage Dependencies**:
   - Ensure `lcov`, `gcov`, and `genhtml` are installed for C++ coverage.
   - Ensure `coverage` and `pytest-cov` are installed in all Python virtual environments.
3. **Reproducible Daemon Setup**:
   - Use `python_tests/snmpd.conf` as the standard configuration.
   - Container entrypoint (`docker/DockerEntry.sh`) must reliably initialize `snmpd` before invoking test suites.
4. **Target Linux Distros**:
   - Design scripts to be compatible with Ubuntu 24.04 LTS host environments while operating on RHEL, Fedora, and Arch guest containers.
