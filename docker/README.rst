====================================
Docker Hub Images For Ezsnmp Testing
====================================

Overview
========

This project uses pre-built Docker images hosted on Docker Hub for running unit tests across various Linux distributions. This ensures a consistent and reproducible testing environment. The following distributions are supported:

* **almalinux10**
* **archlinux**
* **centos7**
* **rockylinux8**

The base repository for these images is: **carlkidcrypto/ezsnmp\_test\_images** https://hub.docker.com/r/carlkidcrypto/ezsnmp_test_images

----------------------------------------------------------------------

Running a Container Locally
===========================

To run a specific distribution image locally, you must use the ``-d`` (detached) flag to keep the container running and mount your local source code into the container (typically at ``/ezsnmp``).

**1. Pull the Image (Optional, if not already cached):**

.. code-block:: bash

    sudo docker pull carlkidcrypto/ezsnmp_test_images:almalinux10

**2. Run the Container and Start the Service:**

The command below runs the container, mounts the current directory (``$(pwd)``) to ``/ezsnmp`` inside the container, exposes UDP port 161 (for SNMP communication), and runs the distribution-specific entry script (``DockerEntry.sh``).

.. code-block:: bash

    # Use the /bin/bash -c "..." wrapper to execute the entry script
    # to keep the container alive by running
    # Replace 'almalinux10' with any supported distribution (e.g., 'rockylinux8').
    
    sudo docker run -d \
      --name "almalinux10_snmp_container" \
      -v "$(pwd):/ezsnmp" \
      -p 161/udp \
      carlkidcrypto/ezsnmp_test_images:almalinux10 \
      /bin/bash -c "/ezsnmp/docker/almalinux10/DockerEntry.sh"

----------------------------------------------------------------------

Executing Unit Tests
====================

Once the container is running in detached mode, you can use ``docker exec`` to run your tests (e.g., using ``tox``) and copy the results back to your host machine.

**1. Run Tests Inside the Container:**

.. code-block:: bash

    # Execute tox for a default environment (like on almalinux10)
    sudo docker exec -t almalinux10_snmp_container /bin/bash -c '
      tox > test-outputs_almalinux10.txt 2>&1;
      mv test-results.xml test-results_almalinux10.xml;
    '

    # Example for a specific environment (like py312 on rockylinux8)
    sudo docker exec -t rockylinux8_snmp_container /bin/bash -c '
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