#!/bin/bash -e

source /home/$USERNAME/bin/activate

echo "Checking for sourced environment..."
python3 -m site --user-site

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip --user
python3 -m pip install -r /ezsnmp/requirements.txt --user
python3 -m pip install -r /ezsnmp/python_tests/requirements.txt --user
python3 -m pip install /ezsnmp/. --verbose --user

echo "Ensuring SNMP configuration directory exists..."
mkdir -p /etc/snmp

echo "Copying SNMP configuration..."
cp /ezsnmp/python_tests/snmpd.conf /etc/snmp/snmpd.conf

download-mibs

echo "Starting SNMP daemon with custom engine ID..."
CUSTOM_ENGINE_ID="0x8000000001020304"
cd /usr/sbin
snmpd -f -C -c /etc/snmp/snmpd.conf -I "$CUSTOM_ENGINE_ID"