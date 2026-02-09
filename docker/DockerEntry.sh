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

# Optional allocator preload (useful for unstable libc allocators)
if [ -n "$EZSNMP_LD_PRELOAD" ]; then
    if [ -n "$LD_PRELOAD" ]; then
        export LD_PRELOAD="$EZSNMP_LD_PRELOAD:$LD_PRELOAD"
    else
        export LD_PRELOAD="$EZSNMP_LD_PRELOAD"
    fi
fi

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
cp /ezsnmp/configs/snmpd.conf /etc/snmp/snmpd.conf

echo "Starting SNMP daemon..."

# Disable glibc malloc checking to avoid false positives with Net-SNMP
export MALLOC_CHECK_=0
export MALLOC_PERTURB_=0

# Setup logging directory
LOG_DIR="/var/log/ezsnmp"
mkdir -p "$LOG_DIR"
SNMPD_LOG="$LOG_DIR/snmpd.log"
SNMPD_ERROR_LOG="$LOG_DIR/snmpd_error.log"

# Check if snmpd exists and is executable
if [ ! -x "/usr/sbin/snmpd" ] && [ ! -x "/usr/bin/snmpd" ]; then
    echo "ERROR: snmpd not found or not executable"
    echo "Searching for snmpd..."
    find / -name snmpd -type f 2>/dev/null || echo "snmpd binary not found on system"
    exit 1
fi

# Try to find snmpd
SNMPD_PATH=$(which snmpd 2>/dev/null || find /usr -name snmpd -type f 2>/dev/null | head -1)
if [ -z "$SNMPD_PATH" ]; then
    echo "ERROR: Could not locate snmpd binary"
    exit 1
fi

echo "Found snmpd at: $SNMPD_PATH"
echo "Logging snmpd output to: $SNMPD_LOG"
echo "Logging snmpd errors to: $SNMPD_ERROR_LOG"

# Get snmpd version for debugging
echo "SNMP daemon version:" | tee -a "$SNMPD_LOG"
"$SNMPD_PATH" -v 2>&1 | tee -a "$SNMPD_LOG"
echo "---" | tee -a "$SNMPD_LOG"

# Verify configuration file
echo "Verifying snmpd configuration:" | tee -a "$SNMPD_LOG"
if [ -f /etc/snmp/snmpd.conf ]; then
    echo "Configuration file exists at /etc/snmp/snmpd.conf" | tee -a "$SNMPD_LOG"
    echo "Configuration file size: $(stat -c%s /etc/snmp/snmpd.conf) bytes" | tee -a "$SNMPD_LOG"
    echo "First 10 lines of configuration:" | tee -a "$SNMPD_LOG"
    head -10 /etc/snmp/snmpd.conf | tee -a "$SNMPD_LOG"
else
    echo "ERROR: Configuration file not found!" | tee -a "$SNMPD_LOG" "$SNMPD_ERROR_LOG"
fi
echo "---" | tee -a "$SNMPD_LOG"

# Log startup timestamp
echo "Starting snmpd at: $(date)" | tee -a "$SNMPD_LOG"
echo "Command: $SNMPD_PATH -f -C -c /etc/snmp/snmpd.conf" | tee -a "$SNMPD_LOG"
echo "---" | tee -a "$SNMPD_LOG"

cd /usr/sbin 2>/dev/null || cd /usr/bin 2>/dev/null || cd /

# Start snmpd with output redirected to log files
# -f = foreground, -C = don't read default config locations, -c = use specific config
"$SNMPD_PATH" -f -C -c /etc/snmp/snmpd.conf >> "$SNMPD_LOG" 2>> "$SNMPD_ERROR_LOG"
