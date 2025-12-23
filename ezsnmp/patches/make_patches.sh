#!/bin/bash

# --- Script to create patch files for Net-SNMP applications ---
# Usage:
#   ./make_patches.sh <version>
# Example:
#   ./make_patches.sh 5.9
# ---------------------------------------------------------------

# 1. Validate that a version number was provided
if [[ -z "$1" ]]; then
    echo "Error: No version specified." >&2
    echo "Usage: $0 <net-snmp-version>" >&2
    echo "Example: $0 5.9" >&2
    exit 1
fi

VERSION="$1"
# Assumes the original source code is in a folder like 'net-snmp-5.9'
SOURCE_DIR="./net-snmp-${VERSION}"
TARGET_DIR="./master_src" # The directory with your modified C++ files

# 2. Check if the source directory actually exists
if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "Error: Source directory not found: ${SOURCE_DIR}" >&2
    echo "Please ensure the Net-SNMP source code for version ${VERSION} is in that folder." >&2
    exit 1
fi

# 3. List of tools to create patches for
tools=(
    "snmpwalk"
    "snmpget"
    "snmpset"
    "snmptrap"
    "snmpbulkwalk"
    "snmpbulkget"
    "snmpgetnext"
)

# 4. Loop through the tools and generate a versioned patch file for each
echo "Generating patches for Net-SNMP version ${VERSION}..."

for tool in "${tools[@]}"; do
    source_file="${SOURCE_DIR}/apps/${tool}.c"
    target_file="${TARGET_DIR}/${tool}.cpp"
    patch_file="${tool}-${VERSION}.patch"
    echo "source_file: ${source_file} ..."
    echo "target_file: ${target_file} ..."
    echo "patch_file: ${patch_file} ..."

    # Check that both the original and your modified file exist before diffing
    if [[ -f "$source_file" && -f "$target_file" ]]; then
        echo "  -> Creating ${patch_file}"
        mkdir -p "net-snmp-${VERSION}-patches"
        # Use --label to create headers compatible with the apply_patches.sh script (-p2)
        diff -aurw \
            --label "a/net-snmp-${VERSION}/apps/${tool}.c" \
            --label "b/net-snmp-${VERSION}/apps/${tool}.cpp" \
            "${source_file}" \
            "${target_file}" > "net-snmp-${VERSION}-patches/${patch_file}"
    else
        echo "  -- Skipping ${tool}: One or both files not found." >&2
    fi
done

echo "Done."