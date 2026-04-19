#!/bin/bash -e

# Script to run pytest tests inside a Docker container
# This script is meant to be executed inside the container via docker exec
# Note: Using -e flag for consistency with other scripts in the codebase

# Parameters
DISTRO_NAME="$1"
TOX_PY="$2"
OUTPUT_FILE="$3"

if [ -z "$DISTRO_NAME" ] || [ -z "$TOX_PY" ] || [ -z "$OUTPUT_FILE" ]; then
	echo "ERROR: Missing required parameters"
	echo "Usage: $0 <DISTRO_NAME> <PY_ENV> <OUTPUT_FILE>"
	exit 1
fi

# Set up environment variables
export PATH="/usr/local/bin:/opt/rh/gcc-toolset-11/root/usr/bin:/opt/rh/devtoolset-11/root/usr/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/lib:/usr/local/lib64:${LD_LIBRARY_PATH:-}"

# Derive the python binary name from the environment key (e.g., py310 -> python3.10)
PY_VER="${TOX_PY#py}"
PYTHON_BIN="python${PY_VER:0:1}.${PY_VER:1}"
VENV_DIR="/tmp/venv_${TOX_PY}_${DISTRO_NAME}"

# Create a venv with the requested Python version and install dependencies
rm -rf "$VENV_DIR"
"$PYTHON_BIN" -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --quiet -r /ezsnmp/python_tests/requirements.txt
cd /ezsnmp && "$VENV_DIR/bin/pip" install --quiet .

# Run pytest tests
"$VENV_DIR/bin/pytest" -v -s -n auto --dist loadfile \
	--junitxml=/ezsnmp/test-results.xml \
	--cov=ezsnmp --cov-report=term-missing \
	--cov-report=xml:/ezsnmp/coverage.xml \
	--cov-config=/ezsnmp/.coveragerc \
	/ezsnmp/python_tests/ > "/ezsnmp/$OUTPUT_FILE" 2>&1

exit 0
