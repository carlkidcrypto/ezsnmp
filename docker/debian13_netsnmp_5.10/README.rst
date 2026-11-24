==================================================
Debian 13 with Net-SNMP 5.10 Docker Test Environment
==================================================

Overview
========

This Docker container provides a Debian 13 (Trixie) environment with Net-SNMP 5.10 compiled from source and Python versions 3.11 through 3.15 for testing ezsnmp (including Valgrind memory leak verification).

Key Features:

* Debian 13 (Trixie) base image
* Net-SNMP 5.10 built from source
* GCC 14.x (system-provided) and Valgrind
* Python 3.11, 3.12, 3.13, 3.14, 3.15
* Python virtual environment at ``/opt/venv`` (using Python 3.14)
* Pre-configured snmpd daemon running on container start
