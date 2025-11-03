#!/bin/bash -e

# --- 1. Define the option and process argument ---

# Default value is 'true' to run the Python code
RUN_PYTHON_CODE=true

# Check if an argument was passed and set the variable
if [ -n "$1" ]; then
    # Convert argument to lowercase and check if it's 'false', 'no', '0', etc.
    # We set RUN_PYTHON_CODE to 'false' only if the argument is explicitly 'false'
    # For simplicity, we can check for common "falsy" values.
    # For a simple true/false check, we just check if the first arg is 'false'
    if [[ "$1" =~ ^(false|no|0)$ ]]; then
        RUN_PYTHON_CODE=false
    fi
fi

# --- 2. Python Code Block (Conditional) ---

if [ "$RUN_PYTHON_CODE" = "true" ]; then
    echo "Starting Python setup (RUN_PYTHON_CODE=true)..."
    
    echo "Installing Python dependencies..."
    rm -drf ezsnmp.egg-info/ build/ dist/
    python3 -m pip install --upgrade pip
    python3 -m pip install -r /ezsnmp/requirements.txt
    python3 -m pip install -r /ezsnmp/python_tests/requirements.txt
    python3 -m pip install /ezsnmp/. --verbose
else
    echo "Skipping Python setup (RUN_PYTHON_CODE=false)..."
fi

# --- 3. SNMP Daemon Setup (Always Runs) ---

echo "Ensuring SNMP configuration directory exists..."
mkdir -p /etc/snmp

echo "Copying SNMP configuration..."
cp /ezsnmp/python_tests/snmpd.conf /etc/snmp/snmpd.conf

echo "Starting SNMP daemon..."
cd /usr/sbin
# The last command in a Docker entrypoint script should be the main process
exec snmpd -f -C -c /etc/snmp/snmpd.conf