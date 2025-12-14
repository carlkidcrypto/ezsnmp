====================================
Docker Hub Images For Ezsnmp Testing
====================================

Overview
========

This project uses pre-built Docker images hosted on Docker Hub for running unit tests across various Linux distributions. This ensures a consistent and reproducible testing environment. The following distributions are supported:

* **almalinux10** - AlmaLinux 10 Kitten (preview) with Python 3.9-3.13, g++ 14.x (3.9-3.11 from source)
* **archlinux** - Arch Linux (latest) with Python 3.9-3.13, g++ 14.x (3.9-3.12 from source)
* **archlinux_netsnmp_5.8** - Arch Linux with net-snmp 5.8 for compatibility testing, g++ 14.x (3.9-3.12 from source)
* **centos7** - CentOS 7 with devtoolset-11 (g++ 11.2.1), Python 3.9-3.13 all from source (OpenSSL 1.1.1w built to enable SSL)
* **rockylinux8** - Rocky Linux 8 with gcc-toolset-11 (g++ 11.3.1), Python 3.9-3.13 (3.10, 3.13 from source)

All images support:

* **g++ 9.5 or higher** for C++ compilation
* **Python 3.9, 3.10, 3.11, 3.12, 3.13** (source builds provided where distro lacks versions)
* **Virtual environment at /opt/venv** (Python 3.13 or latest available) with both ``requirements.txt`` and ``python_tests/requirements.txt`` pre-installed
* **Both cpp_tests and python_tests** test suites
* **Optimized for minimal image size** (combined RUNs, cache cleanup, removal of build artifacts)

The base repository for these images is: **carlkidcrypto/ezsnmp\_test\_images** https://hub.docker.com/r/carlkidcrypto/ezsnmp_test_images

----------------------------------------------------------------------

Running a Container Locally
===========================

To run a specific distribution image locally, you must use the ``-d`` (detached) flag to keep the container running and mount your local source code into the container (typically at ``/ezsnmp``).

**1. Pull the Image (Optional, if not already cached):**

.. code-block:: bash

    sudo docker pull carlkidcrypto/ezsnmp_test_images:almalinux10-latest

**2. Run the Container and Start the Service:**

The command below runs the container, mounts the current directory (``$(pwd)``) to ``/ezsnmp`` inside the container, exposes UDP port 161 (for SNMP communication), and runs the distribution-specific entry script (``DockerEntry.sh``). 

The ``DockerEntry.sh`` script accepts an optional parameter to control Python setup:
- **true** (default): Installs Python dependencies and builds the package
- **false**: Skips Python setup, only starts SNMP daemon (useful for faster container startup during testing)

.. code-block:: bash

    # Full setup with Python dependencies (default behavior)
    sudo docker run -d \
      --name "almalinux10_snmp_container" \
      -v "$(pwd):/ezsnmp" \
      -p 161/udp \
      carlkidcrypto/ezsnmp_test_images:almalinux10-latest \
      /bin/bash -c "/ezsnmp/docker/almalinux10/DockerEntry.sh"

    # Or skip Python setup for faster startup (daemon only)
    sudo docker run -d \
      --name "almalinux10_snmp_container" \
      -v "$(pwd):/ezsnmp" \
      -p 161/udp \
      carlkidcrypto/ezsnmp_test_images:almalinux10-latest \
      /bin/bash -c "/ezsnmp/docker/almalinux10/DockerEntry.sh false"

----------------------------------------------------------------------

Executing Unit Tests
====================

Once the container is running in detached mode, you can use ``docker exec`` to run your tests (e.g., using ``tox``) and copy the results back to your host machine.

**1. Run Tests Inside the Container:**

.. code-block:: bash

    # Execute tox for a default environment (e.g., on almalinux10)
    sudo docker exec -t almalinux10_snmp_container /bin/bash -c '
      cd /ezsnmp;
      rm -drf build/ ezsnmp.egg-info/ .tox/ dist/;
      python3 -m pip install tox;
      tox > test-outputs_almalinux10.txt 2>&1;
      mv test-results.xml test-results_almalinux10.xml;
    '

    # Example for a specific environment (like py312 on rockylinux8)
    sudo docker exec -t rockylinux8_snmp_container /bin/bash -c '
      cd /ezsnmp;
      rm -drf build/ ezsnmp.egg-info/ .tox/ dist/;
      python3 -m pip install tox;
      tox -e py312 > test-outputs_rockylinux8_py312.txt 2>&1;
      mv test-results.xml test-results_rockylinux8_py312.xml;
    '

**2. Copy Results to Host:**

.. code-block:: bash

    # Copy the results back to the current directory
    sudo docker cp almalinux10_snmp_container:/ezsnmp/test-results_almalinux10.xml .
    sudo docker cp almalinux10_snmp_container:/ezsnmp/test-outputs_almalinux10.txt .

**3. Cleanup:**

Stop and remove the container once testing is complete:

.. code-block:: bash

    sudo docker stop almalinux10_snmp_container
    sudo docker rm almalinux10_snmp_container

----------------------------------------------------------------------

Helper Scripts
==============

The ``docker`` directory includes helper scripts for automated testing:

**build_and_publish_images.sh**

Builds and publishes Docker images to Docker Hub.

.. code-block:: bash

  # Build and publish all distribution images
  ./build_and_publish_images.sh <docker_user> <docker_pat>

  # Build and publish a single distribution
  ./build_and_publish_images.sh <docker_user> <docker_pat> centos7

**run_python_tests_in_all_dockers.sh**

Runs Python tests across all distributions in parallel or a specific distribution.

.. code-block:: bash

  # Run tests in all distributions
  ./run_python_tests_in_all_dockers.sh

  # Run tests in a specific distribution only
  ./run_python_tests_in_all_dockers.sh almalinux10

Output files are organized in ``test_outputs_<distribution>/`` directories:

- ``test-results_<distribution>_test_container_<python_version>.xml``
- ``test-outputs_<distribution>_test_container_<python_version>.txt``

**run_cpp_tests_in_all_dockers.sh**

Runs C++ tests using Meson/Ninja and generates coverage reports.

.. code-block:: bash

  # Run C++ tests in all distributions
  ./run_cpp_tests_in_all_dockers.sh

  # Run C++ tests in a specific distribution
  ./run_cpp_tests_in_all_dockers.sh rockylinux8

Generates:

- ``test-results_<distribution>_test_container.xml`` - Test results in JUnit format
- ``test-outputs_<distribution>_test_container.txt`` - Test execution logs
- ``lcov_coverage_<distribution>_test_container.info`` - Code coverage data

**Note**: All scripts should be run from the ``docker`` directory and assume the repository root is mounted at ``/ezsnmp`` inside containers.

----

.. note::
   This content was generated by AI and reviewed by humans. Mistakes may still occur. PRs for corrections are welcome.