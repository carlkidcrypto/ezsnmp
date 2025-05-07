#!/bin/bash

# Define variables
SUBMODULE_DIR="net-snmp"

# Check if the submodule directory exists
if [ ! -d "$SUBMODULE_DIR" ]; then
    echo "Initializing and updating Git submodule..."
    git submodule add https://github.com/net-snmp/net-snmp.git "$SUBMODULE_DIR"
    git submodule update --init --recursive
else
    echo "Submodule already exists, updating..."
    git submodule update --remote --recursive
fi