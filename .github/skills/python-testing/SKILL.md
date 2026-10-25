---
name: python-testing
description: Use when authoring, running, or debugging pytest test suites in python_tests/, measuring test coverage, or testing with a live Net-SNMP daemon.
---

# Python Testing Guide (ezsnmp)

Use this skill when developing, executing, or debugging Python unit tests and integration tests in `python_tests/` for `ezsnmp`.

## 1. Environment & Prerequisites

- **Virtual Environment**: Use an activated Python virtual environment (`source .venv/bin/activate` or `./python3.12.venv/bin/activate` for local development).
- **Supported Python Versions**: Python 3.10, 3.11, 3.12, 3.13, and 3.14.
- **Dependencies**: Ensure test dependencies are installed:
  ```bash
  pip install -r python_tests/requirements.txt
  ```

---

## 2. Live SNMP Daemon Configuration

Many tests in `python_tests/` validate live SNMP operations against a local `snmpd` daemon:

- **Configuration File**: `python_tests/snmpd.conf` (or `/etc/snmp/snmpd.conf` inside containers).
- **Starting Daemon Manually (if required for local execution)**:
  ```bash
  sudo /usr/sbin/snmpd -f -C -c python_tests/snmpd.conf -Lo
  ```
  *(In Docker containers, `docker/DockerEntry.sh` launches and monitors `snmpd` automatically).*
- **Verifying Daemon**:
  ```bash
  netstat -tulpn | grep 161 || ss -tulpn | grep 161
  ```

---

## 3. Running Tests

### A. Local Execution
Run tests using pytest in your active virtual environment:

```bash
# Run a single test module
pytest python_tests/test_session_unit.py

# Run a specific test function
pytest python_tests/test_session_unit.py -k "test_session_get"

# Run with verbose output and coverage
pytest --cov=ezsnmp --cov-report=term-missing python_tests/
```

### B. Dockerized Multi-Distro Execution
To run Python tests across all supported Linux distributions (AlmaLinux 10, Arch Linux, Fedora 42, Rocky Linux 9):

```bash
cd docker

# Run all distributions
./run_python_tests_in_all_dockers.sh

# Run specific distribution
./run_python_tests_in_all_dockers.sh almalinux10_netsnmp_5.10
```

---

## 4. Test Design & Coverage Requirements

1. **Target 100% Coverage**: All new or modified Python code in `ezsnmp/` must have accompanying tests in `python_tests/`.
2. **Session Cleanup**: Always close or delete `Session` objects at the end of tests or use context fixtures to prevent socket/file descriptor leaks.
3. **Module Size**: Keep test modules focused (~500 lines). If a test module exceeds 1,000 lines, split into thematic modules (e.g. `test_session_get.py`, `test_session_walk.py`).
4. **Skip Rules**: Skipping tests via `@pytest.mark.skip` or `pytest.skip()` should be a last resort, used only when an OS or platform strictly lacks an underlying capability.
5. **Formatting**: Always format test files with Black:
   ```bash
   black python_tests/
   ```
