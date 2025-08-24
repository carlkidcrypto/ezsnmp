#!/bin/bash -e

echo "Installing Python dependencies..."
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r /ezsnmp/requirements.txt
python3.9 -m pip install -r /ezsnmp/python_tests/requirements.txt

echo "Building and installing ezsnmp with GCC Toolset 12..."
# Source the gcc-toolset-12 environment to set all necessary paths for the session
source /opt/rh/gcc-toolset-12/enable
# Explicitly set the C and C++ compilers for the build process
export CC=/opt/rh/gcc-toolset-12/root/usr/bin/gcc
export CXX=/opt/rh/gcc-toolset-12/root/usr/bin/g++
python3.9 -m pip install /ezsnmp/. --verbose

echo "Ensuring SNMP configuration directory exists..."
mkdir -p /etc/snmp

echo "Copying SNMP configuration..."
cp /ezsnmp/python_tests/snmpd.conf /etc/snmp/snmpd.conf

echo "Starting SNMP daemon..."
cd /usr/sbin
snmpd -f -C -c /etc/snmp/snmpd.conf
