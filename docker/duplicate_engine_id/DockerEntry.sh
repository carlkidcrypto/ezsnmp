#!/bin/bash -e

source /home/$USERNAME/.venv/bin/activate

echo "Checking for sourced environment..."
which python3

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip 
python3 -m pip install -r /ezsnmp/requirements.txt 
python3 -m pip install -r /ezsnmp/python_tests/requirements.txt 
python3 -m pip install /ezsnmp/. --verbose

echo "Starting SNMP daemon with custom engine ID..."
CUSTOM_ENGINE_ID="0x8000000001020304"
cd /usr/sbin
snmpd -f -C -c /ezsnmp/python_tests/snmpd.conf -I "$CUSTOM_ENGINE_ID"