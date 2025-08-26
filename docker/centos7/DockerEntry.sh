#!/bin/bash -e

# # Explicitly set the C and C++ compilers for the build process
# export CC=/opt/rh/gcc-toolset-8/root/usr/bin/gcc
# export CXX=/opt/rh/gcc-toolset-8/root/usr/bin/g++

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