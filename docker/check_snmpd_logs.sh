#!/bin/bash
# Script to check snmpd logs from a running Docker container
# Usage: ./check_snmpd_logs.sh [container_name]
# If no container name is provided, will list all running ezsnmp containers

set -euo pipefail

CONTAINER_NAME="${1:-}"

if [ -z "$CONTAINER_NAME" ]; then
    echo "=== Running ezsnmp test containers ==="
    docker ps --filter "name=_test_container" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
    echo ""
    echo "Usage: $0 <container_name>"
    echo "Example: $0 archlinux_netsnmp_5.7_test_container"
    exit 0
fi

echo "=== Checking snmpd logs for container: $CONTAINER_NAME ==="
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "ERROR: Container '$CONTAINER_NAME' is not running"
    echo ""
    echo "Available containers:"
    docker ps --filter "name=_test_container" --format "{{.Names}}"
    exit 1
fi

echo "--- SNMPD OUTPUT LOG ---"
docker exec "$CONTAINER_NAME" bash -c "
    if [ -f /var/log/ezsnmp/snmpd.log ]; then
        cat /var/log/ezsnmp/snmpd.log
    else
        echo 'Log file not found: /var/log/ezsnmp/snmpd.log'
    fi
" 2>&1

echo ""
echo "--- SNMPD ERROR LOG ---"
docker exec "$CONTAINER_NAME" bash -c "
    if [ -f /var/log/ezsnmp/snmpd_error.log ]; then
        cat /var/log/ezsnmp/snmpd_error.log
    else
        echo 'Log file not found: /var/log/ezsnmp/snmpd_error.log'
    fi
" 2>&1

echo ""
echo "--- SNMPD PROCESS STATUS ---"
docker exec "$CONTAINER_NAME" bash -c "
    ps aux | grep snmpd | grep -v grep || echo 'No snmpd process found'
" 2>&1

echo ""
echo "--- SNMPD PORT LISTENING STATUS ---"
docker exec "$CONTAINER_NAME" bash -c "
    netstat -tulpn 2>/dev/null | grep snmpd || 
    ss -tulpn 2>/dev/null | grep snmpd || 
    echo 'Could not check listening ports (netstat/ss not available or no snmpd listening)'
" 2>&1

echo ""
echo "=== Log check complete ==="
