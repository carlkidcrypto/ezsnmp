#!/bin/bash

# Define variables
URL="https://github.com/net-snmp/net-snmp/archive/refs/heads/master.zip"
ZIP_FILE="master.zip"
UNZIP_DIR="net-snmp-master"

# Check if the ZIP file already exists
if [ ! -f "$ZIP_FILE" ]; then
    # Download the source code
    echo "Downloading source code..."
    curl -L -o "$ZIP_FILE" "$URL"
else
    echo "ZIP file already exists, skipping download."
fi

# Unzip the downloaded file
if [ ! -d "$UNZIP_DIR" ]; then
    echo "Unzipping source code..."
    unzip "$ZIP_FILE"
else
    echo "Unzipped folder already exists, skipping unzip."
fi