====================================================
Arch Linux with Net-SNMP 5.10 Docker Test Environment
====================================================

Overview
========

This Docker container provides an Arch Linux environment with Net-SNMP 5.10 compiled from source and Python versions 3.10 through 3.14 for testing ezsnmp.

Key Features:

* Arch Linux latest base image
* Net-SNMP 5.10 built from source
* Native GCC toolchain
* Python 3.10, 3.11, 3.12, 3.13, 3.14
* Python virtual environment at ``/opt/venv`` (using Python 3.14)
* Pre-configured snmpd daemon running on container start
