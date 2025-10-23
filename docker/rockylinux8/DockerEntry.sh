#!/bin/bash -e

echo "Installing Python dependencies..."
rm -drf ezsnmp.egg-info/ build/ dist/
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
