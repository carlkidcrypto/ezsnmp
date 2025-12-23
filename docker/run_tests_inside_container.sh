#!/bin/bash -e

# Script to run tox tests inside a Docker container
# This script is meant to be executed inside the container via docker exec

# Parameters
DISTRO_NAME="$1"
TOX_PY="$2"
OUTPUT_FILE="$3"

if [ -z "$DISTRO_NAME" ] || [ -z "$TOX_PY" ] || [ -z "$OUTPUT_FILE" ]; then
	echo "ERROR: Missing required parameters"
	echo "Usage: $0 <DISTRO_NAME> <TOX_PY> <OUTPUT_FILE>"
	exit 1
fi

# Set up environment variables
export PATH=/usr/local/bin:/opt/rh/gcc-toolset-11/root/usr/bin:/opt/rh/devtoolset-11/root/usr/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64:$LD_LIBRARY_PATH
export WORK_DIR=/tmp/ezsnmp_${DISTRO_NAME}
export TOX_WORK_DIR=/tmp/tox_${DISTRO_NAME}

# Copy source to isolated directory, excluding build artifacts and venvs
rm -rf "$WORK_DIR" "$TOX_WORK_DIR"
mkdir -p "$WORK_DIR"
cd /ezsnmp && tar --exclude='*.egg-info' --exclude='build' --exclude='dist' --exclude='.tox' --exclude='__pycache__' --exclude='*.pyc' --exclude='.coverage*' --exclude='python3.*venv' --exclude='*.venv' --exclude='venv' -cf - . 2>/dev/null | (cd "$WORK_DIR" && tar xf -)

# Run tox tests
cd "$WORK_DIR"
python3 -m pip install tox > /dev/null 2>&1
tox -e "$TOX_PY" --workdir "$TOX_WORK_DIR" > /ezsnmp/"$OUTPUT_FILE" 2>&1

exit 0
