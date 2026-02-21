#!/usr/bin/env bash
#
# Start a local snmpd daemon using Homebrew's net-snmp for running tests
# on macOS natively (outside of Docker).
#
# The daemon runs in the foreground on udp:127.0.0.1:11161 as configured
# in python_tests/snmpd.conf.  Press Ctrl+C to stop it.
#
# Usage:
#   ./start_homebrew_snmpd.sh            # foreground (default)
#   ./start_homebrew_snmpd.sh --daemon   # background (writes PID to .snmpd.pid)
#   ./start_homebrew_snmpd.sh --stop     # stop a backgrounded instance
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SNMPD_CONF="${SCRIPT_DIR}/snmpd.conf"
PID_FILE="${SCRIPT_DIR}/.snmpd.pid"

# ---------------------------------------------------------------------------
# Validate environment
# ---------------------------------------------------------------------------

# Must be macOS
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "Error: This script is intended for macOS only." >&2
    exit 1
fi

# Homebrew must be installed
if ! command -v brew &>/dev/null; then
    echo "Error: Homebrew is not installed." >&2
    echo "Install it from https://brew.sh" >&2
    exit 1
fi

# net-snmp must be installed via Homebrew
HOMEBREW_NET_SNMP_PREFIX="$(brew --prefix net-snmp 2>/dev/null || true)"
if [[ -z "${HOMEBREW_NET_SNMP_PREFIX}" ]] || [[ ! -d "${HOMEBREW_NET_SNMP_PREFIX}" ]]; then
    echo "Error: net-snmp is not installed via Homebrew." >&2
    echo "Install it with: brew install net-snmp" >&2
    exit 1
fi

SNMPD_BIN="${HOMEBREW_NET_SNMP_PREFIX}/sbin/snmpd"

if [[ ! -x "${SNMPD_BIN}" ]]; then
    echo "Error: snmpd binary not found at ${SNMPD_BIN}" >&2
    echo "Try reinstalling: brew reinstall net-snmp" >&2
    exit 1
fi

# snmpd.conf must exist
if [[ ! -f "${SNMPD_CONF}" ]]; then
    echo "Error: snmpd.conf not found at ${SNMPD_CONF}" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Handle --stop
# ---------------------------------------------------------------------------

if [[ "${1:-}" == "--stop" ]]; then
    if [[ ! -f "${PID_FILE}" ]]; then
        echo "No PID file found at ${PID_FILE}. Is snmpd running?" >&2
        exit 1
    fi
    PID="$(cat "${PID_FILE}")"
    if kill -0 "${PID}" 2>/dev/null; then
        echo "Stopping snmpd (PID ${PID})..."
        kill "${PID}"
        rm -f "${PID_FILE}"
        echo "Stopped."
    else
        echo "snmpd process ${PID} is not running. Cleaning up stale PID file."
        rm -f "${PID_FILE}"
    fi
    exit 0
fi

# ---------------------------------------------------------------------------
# Check if port 11161 is already in use
# ---------------------------------------------------------------------------

if lsof -i UDP:11161 -sTCP:LISTEN &>/dev/null 2>&1 || lsof -i UDP:11161 &>/dev/null 2>&1; then
    echo "Error: UDP port 11161 is already in use." >&2
    echo "Another snmpd may already be running. Check with:" >&2
    echo "  lsof -i UDP:11161" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Print info
# ---------------------------------------------------------------------------

echo "Homebrew net-snmp prefix: ${HOMEBREW_NET_SNMP_PREFIX}"
echo "snmpd binary:            ${SNMPD_BIN}"
echo "snmpd config:            ${SNMPD_CONF}"
echo "snmpd version:           $("${SNMPD_BIN}" -v 2>&1 | grep -m1 'version')"
echo "Listening on:            udp:127.0.0.1:11161"
echo ""

# ---------------------------------------------------------------------------
# Start snmpd
# ---------------------------------------------------------------------------

if [[ "${1:-}" == "--daemon" ]]; then
    # Background mode: snmpd forks itself, we record the PID
    "${SNMPD_BIN}" -C -c "${SNMPD_CONF}" -p "${PID_FILE}"
    sleep 1
    if [[ -f "${PID_FILE}" ]]; then
        echo "snmpd started in background (PID $(cat "${PID_FILE}"))"
        echo "Stop with: $0 --stop"
    else
        echo "Error: snmpd failed to start. Check the config and try foreground mode." >&2
        exit 1
    fi
else
    # Foreground mode (default)
    echo "Starting snmpd in foreground (Ctrl+C to stop)..."
    echo "---"
    exec "${SNMPD_BIN}" -f -C -c "${SNMPD_CONF}"
fi
