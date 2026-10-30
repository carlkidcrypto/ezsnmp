==================================================
Fedora 42 with Net-SNMP 5.10 Docker Test Environment
==================================================

Overview
========

This Docker container provides a Fedora 42 environment with Net-SNMP 5.10 compiled from source and Python versions 3.11 through 3.15 for testing ezsnmp.

Key Features:

* Fedora 42 base image
* Net-SNMP 5.10 built from source
* Native GCC 14.x
* Python 3.11, 3.12, 3.13, 3.14, 3.15 (all built from source)
* Python virtual environment at ``/opt/venv`` (using Python 3.14)
* Pre-configured snmpd daemon running on container start
