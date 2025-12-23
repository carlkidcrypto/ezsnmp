=========================
CentOS 7 Docker Image
=========================

Overview
========
This directory contains build resources for the **CentOS 7** test image. It is tailored for EzSnmp development and CI and now includes:

* devtoolset-11 (g++ 11.2.1)
* Python 3.9–3.13 built from source with OpenSSL 1.1.1w (enables SSL for pip)
* Virtual environment at ``/opt/venv`` pre-installed with project and test requirements
* net-snmp libraries/utilities for SNMP tests

Quick Build & Run
=================
Use the helper script (from this folder):

.. code-block:: bash

    ./go_docker.sh            # build + start detached
    ./go_docker.sh --clean    # prune then build + start

Manual Build (Repository Root Context)
-------------------------------------
Because the Dockerfile copies top-level files (``requirements.txt``, ``python_tests/requirements.txt``), the build context must be the repo root:

.. code-block:: bash

    docker build -f docker/centos7/Dockerfile -t local/centos7 ..

Starting an Interactive Container
---------------------------------
If already built (image tag ``carlkidcrypto/ezsnmp_test_images:centos7`` or locally):

.. code-block:: bash

    docker run -it --rm \
      -v "$(pwd):/ezsnmp" \
      --name centos7_snmp_container \
      local/centos7 /bin/bash

Activate the virtual environment:

.. code-block:: bash

    source /opt/venv/bin/activate
    python -V
    pip list

Extending the Image
-------------------
Add system packages or tools by editing ``Dockerfile`` then rebuild. Keep build context at repo root for consistency.

Directory Structure
===================
* **Dockerfile** – Python & OpenSSL source builds, venv provisioning
* **README.rst** – This documentation
* **go_docker.sh** – Local convenience build/run script
* **docker-compose.yml** – Compose file mounting the repo at ``/ezsnmp``
* **DockerEntry.sh** – Starts SNMP daemon & prepares environment

Python & SSL
============
CentOS 7 ships OpenSSL 1.0.2 (too old for Python 3.13). The Dockerfile builds OpenSSL 1.1.1w and configures each Python build with ``--with-openssl=/usr/local/openssl`` so the ``ssl`` module and pip work.

Virtual Environment
===================
Created with Python 3.13 at ``/opt/venv``; contains both:

* ``requirements.txt`` (project tooling)
* ``python_tests/requirements.txt`` (pytest, coverage, tox, etc.)

Contributing
============
Improvements welcome—open an issue or PR if you spot problems or want enhancements.