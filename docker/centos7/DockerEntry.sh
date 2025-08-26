#!/bin/bash -e

# Activate the newer GCC 8 compiler toolset using its full path
echo "Enabling GCC 8 toolset..."
source /opt/rh/devtoolset-8/enable

# Now the pip install commands will use g++ version 8
echo "Installing Python dependencies..."
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r /ezsnmp/requirements.txt
python3.9 -m pip install -r /ezsnmp/python_tests/requirements.txt
python3.9 -m pip install /ezsnmp/. --verbose

echo "Ensuring SNMP configuration directory exists..."
mkdir -p /etc/snmp

echo "Copying SNMP configuration..."
cp /ezsnmp/python_tests/snmpd.conf /etc/snmp/snmpd.conf

echo "Starting SNMP daemon..."
cd /usr/sbin
snmpd -f -C -c /etc/snmp/snmpd.conf