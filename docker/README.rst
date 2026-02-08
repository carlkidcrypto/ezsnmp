====================================
Docker Hub Images For Ezsnmp Testing
====================================

Overview
========

This project uses pre-built Docker images hosted on Docker Hub for running unit tests across various Linux distributions. This ensures a consistent and reproducible testing environment. The following distributions are supported:

* **almalinux10** - AlmaLinux 10 Kitten (preview) with Python 3.10-3.14, g++ 14.x (3.10-3.11 from source)
* **archlinux** - Arch Linux (latest) with Python 3.10-3.14, g++ 14.x (3.10-3.12 from source)
* **archlinux_netsnmp_5.8** - Arch Linux with net-snmp 5.8 for compatibility testing, g++ 14.x (3.10-3.12 from source)
* **centos7** - CentOS 7 with devtoolset-11 (g++ 11.2.1), Python 3.10-3.14 all from source (OpenSSL 1.1.1w built to enable SSL)
* **centos8** - CentOS 8 (EOL) with gcc-toolset-11 (g++ 11.x), Python 3.10-3.14 all from source
* **rockylinux8** - Rocky Linux 8 with gcc-toolset-11 (g++ 11.3.1), Python 3.10-3.14 (3.10, 3.13 from source)
* **rockylinux9** - Rocky Linux 9 with gcc-toolset-13 (g++ 13.x), Python 3.10-3.14 all from source

All images support:

* **g++ 9.5 or higher** for C++ compilation
* **Python 3.10, 3.11, 3.12, 3.13, 3.14** (source builds provided where distro lacks versions)
* **Virtual environment at /opt/venv** (Python 3.14 or latest available) with both ``requirements.txt`` and ``python_tests/requirements.txt`` pre-installed
* **Both cpp_tests and python_tests** test suites
* **Optimized for minimal image size** (combined RUNs, cache cleanup, removal of build artifacts)
* **Perl JSON modules** (perl-json-xs, perl-cpanel-json-xs) for improved coverage report handling

The base repository for these images is: **carlkidcrypto/ezsnmp\_test\_images** https://hub.docker.com/r/carlkidcrypto/ezsnmp_test_images

----------------------------------------------------------------------

Test Report Generation
======================

A comprehensive test report generation script is available to analyze all test results across containers and Python versions.

**Usage:**

.. code-block:: bash

    cd docker
    ./generate_test_reports.sh

**Features:**

* Analyzes test results for all container/Python version combinations
* Detects build failures, crashes, and test failures
* Checks SNMP daemon logs for errors
* Generates both console output and timestamped report file
* Color-coded status indicators (green=pass, red=fail, yellow=warning)
* Identifies specific issues and provides recommendations

**Output:**

The script generates a comprehensive report saved to ``test_summary_report_YYYYMMDD_HHMMSS.txt`` containing:

* Summary by container and Python version
* SNMP daemon version and error status
* Detailed test results (passed/failed/skipped/errors)
* Overall statistics
* Known issues and recommendations

----------------------------------------------------------------------

Python Tarball Caching System
==============================

To significantly speed up Docker image builds and reduce bandwidth usage, this project uses a local caching system for Python source tarballs.

**How It Works:**

1. Python source tarballs (*.tgz) are downloaded once to ``docker/cache/``
2. Dockerfiles use ``COPY`` instead of ``wget`` to copy from the cache
3. The build script automatically populates the cache before building images

**Setup:**

Before building images, populate the cache by running:

.. code-block:: bash

    cd docker/cache
    ./download_build_cache.sh

Or simply run the main build script, which automatically calls the cache script:

.. code-block:: bash

    cd docker
    ./build_and_publish_images.sh <username> <token>

**Benefits:**

* **Faster builds**: No repeated downloads across different containers
* **Bandwidth savings**: Each Python version downloaded only once (~25MB each)
* **Offline capability**: Once cached, builds work without internet (for Python sources)
* **Better reliability**: Reduces dependency on external network during builds

**Maintenance:**

When updating Python versions in Dockerfiles:

1. Update ``PYTHON_*_VERSION`` ARGs in Dockerfiles
2. Update ``PYTHON_VERSIONS`` array in ``docker/cache/download_build_cache.sh``
3. Run the download script to fetch new versions
4. Old versions can be manually removed from ``docker/cache/`` if no longer needed

The cache directory is git-ignored (``*.tgz`` files) but the structure and download script are version controlled.

----------------------------------------------------------------------

Running a Container Locally
===========================

To run a specific distribution image locally, you must use the ``-d`` (detached) flag to keep the container running and mount your local source code into the container (typically at ``/ezsnmp``).

**1. Pull the Image (Optional, if not already cached):**

.. code-block:: bash

    sudo docker pull carlkidcrypto/ezsnmp_test_images:almalinux10-latest

**2. Run the Container and Start the Service:**

The command below runs the container, mounts the current directory (``$(pwd)``) to ``/ezsnmp`` inside the container, and runs the distribution-specific entry script (``DockerEntry.sh``). 

The ``DockerEntry.sh`` script accepts an optional parameter to control Python setup:
- **true** (default): Installs Python dependencies and builds the package
- **false**: Skips Python setup, only starts SNMP daemon (useful for faster container startup during testing)

.. code-block:: bash

    # Full setup with Python dependencies (default behavior)
    sudo docker run -d \
      --name "almalinux10_snmp_container" \
      -v "$(pwd):/ezsnmp" \
      carlkidcrypto/ezsnmp_test_images:almalinux10-latest \
      /bin/bash -c "/ezsnmp/docker/almalinux10/DockerEntry.sh & tail -f /dev/null"

    # Or skip Python setup for faster startup (daemon only)
    sudo docker run -d \
      --name "almalinux10_snmp_container" \
      -v "$(pwd):/ezsnmp" \
      carlkidcrypto/ezsnmp_test_images:almalinux10-latest \
      /bin/bash -c "/ezsnmp/docker/almalinux10/DockerEntry.sh false & tail -f /dev/null"

----------------------------------------------------------------------

Executing Unit Tests
====================

Once the container is running in detached mode, you can use ``docker exec`` to run your tests (e.g., using ``tox``) and copy the results back to your host machine.

**1. Run Tests Inside the Container:**

.. code-block:: bash

    # Execute tox for a specific environment (e.g., py312 on almalinux10)
    sudo docker exec -t almalinux10_snmp_container bash /ezsnmp/docker/run_tests_inside_container.sh \
      almalinux10 py312 test-outputs_almalinux10_py312.txt

**2. Copy Results to Host:**

.. code-block:: bash

    # Copy the results back to the current directory
    sudo docker cp almalinux10_snmp_container:/ezsnmp/test-outputs_almalinux10_py312.txt .

**3. Cleanup:**

Stop and remove the container once testing is complete:

.. code-block:: bash

    sudo docker stop almalinux10_snmp_container
    sudo docker rm almalinux10_snmp_container

----------------------------------------------------------------------

Helper Scripts
==============

The ``docker`` directory includes helper scripts for automated testing:

**run_tests_inside_container.sh**

A helper script designed to be executed inside Docker containers via ``docker exec``. It sets up the test environment, isolates the source code, and runs tox tests with the specified Python version.

.. code-block:: bash

  # Usage: run_tests_inside_container.sh <DISTRO_NAME> <TOX_PY> <OUTPUT_FILE>
  docker exec -t container_name bash /ezsnmp/docker/run_tests_inside_container.sh \
    almalinux10 py312 test-outputs_almalinux10_py312.txt

This script:

* Sets up the necessary environment variables (PATH, LD_LIBRARY_PATH)
* Creates isolated work directories for testing
* Copies source code while excluding build artifacts and virtual environments
* Installs and runs tox for the specified Python version
* Outputs results to the specified file in the ``/ezsnmp`` directory

**build_and_publish_images.sh**

Builds and publishes Docker images to Docker Hub.

.. code-block:: bash

  # Build and publish all distribution images
  ./build_and_publish_images.sh <docker_user> <docker_pat>

  # Build and publish a single distribution
  ./build_and_publish_images.sh <docker_user> <docker_pat> centos7

  # Build from scratch without using cache
  ./build_and_publish_images.sh <docker_user> <docker_pat> centos7 --no-cache

**run_python_tests_in_all_dockers.sh**

Runs Python tests across all distributions in parallel or a specific distribution.

.. code-block:: bash

  # Run tests in all distributions
  ./run_python_tests_in_all_dockers.sh

  # Run tests in a specific distribution only
  ./run_python_tests_in_all_dockers.sh almalinux10

The script creates a separate output directory for each distribution in the ``docker/`` directory. For example, after running all tests, you'll see:

- ``test_outputs_almalinux10/``
- ``test_outputs_archlinux/``
- ``test_outputs_archlinux_netsnmp_5.8/``
- ``test_outputs_centos7/``
- ``test_outputs_rockylinux8/``

Each directory contains test results and outputs for all Python versions:

- ``test-results_<distribution>_test_container_<python_version>.xml``
- ``test-outputs_<distribution>_test_container_<python_version>.txt``

**run_cpp_tests_in_all_dockers.sh**

Runs C++ tests using Meson/Ninja and generates coverage reports.

.. code-block:: bash

  # Run C++ tests in all distributions
  ./run_cpp_tests_in_all_dockers.sh

  # Test only net-snmp 5.7 containers (useful for iterative debugging)
  ./run_cpp_tests_in_all_dockers.sh centos7_netsnmp_5.7 archlinux_netsnmp_5.7

  # Show help
  ./run_cpp_tests_in_all_dockers.sh --help

**Usage Modes:**

- **No arguments**: Tests all distributions (finds all directories with Dockerfiles)
- **One or more image names**: Tests only the specified distributions
- **--help**: Shows usage information and examples

Generates per-distribution output directories (``test_outputs_<distribution>/``):

- ``test-results.xml`` - Test results in JUnit format
- ``test-outputs.txt`` - Test execution logs and meson output
- ``lcov_coverage.info`` - Code coverage data (filtered to exclude system files)
- ``snmpd_logs.txt`` - SNMP daemon logs for debugging

**Coverage Collection Strategy**:

The script uses a multi-stage fallback approach for maximum compatibility across distributions:

1. **Primary**: Uses ``geninfo`` with explicit ignore-errors flags for mismatched gcov data
2. **Fallback 1**: Uses ``lcov --capture`` with ignore-errors if geninfo fails
3. **Fallback 2**: Uses basic ``lcov --capture`` without ignore-errors as last resort

This ensures coverage collection works across different versions of lcov/gcov, handling inconsistencies in gcov output formats between distributions.

**Note**: All scripts should be run from the ``docker`` directory and assume the repository root is mounted at ``/ezsnmp`` inside containers.

----------------------------------------------------------------------

SNMPD Debugging and Logs
=========================

The ``DockerEntry.sh`` script automatically captures snmpd daemon output for debugging purposes.

**Log Files:**

All snmpd logs are stored inside containers at:

- ``/var/log/ezsnmp/snmpd.log`` - Main snmpd output (startup info, version, config verification)
- ``/var/log/ezsnmp/snmpd_error.log`` - Error output from snmpd

**Automatic Log Collection:**

The test runner scripts automatically extract snmpd logs after test completion:

- Python tests: ``test_outputs_<distribution>/snmpd_logs_<distribution>_test_container.txt``
- C++ tests: ``test_outputs_<distribution>/snmpd_logs.txt``

**Manual Log Checking:**

To check logs from a running container, use the helper script:

.. code-block:: bash

  # List all running test containers
  ./check_snmpd_logs.sh

  # Check logs for a specific container
  ./check_snmpd_logs.sh archlinux_netsnmp_5.7_test_container

This script displays:

- snmpd output log (startup, version, configuration)
- snmpd error log (any daemon errors)
- snmpd process status
- Port listening status (verifies daemon is accepting connections)

**Troubleshooting snmpd Issues:**

If tests fail with timeout errors or "No Response" messages:

1. Check the snmpd logs for startup errors
2. Verify snmpd process is running: ``docker exec <container> ps aux | grep snmpd``
3. Check port binding: ``docker exec <container> netstat -tulpn | grep 161``
4. Review configuration: ``docker exec <container> cat /etc/snmp/snmpd.conf``

----

.. note::
   This content was generated by AI and reviewed by humans. Mistakes may still occur. PRs for corrections are welcome.