#!/bin/bash

# --- Script to apply custom final patches and move them to a final directory ---
#
# Usage:
#   1. Start with a fresh, clean 'net-snmp-X.X' source directory.
#   2. Place this script next to the source and the patch directories.
#   3. Run it with the version number.
#
# Example:
#   ./apply_patches.sh 5.8
# --------------------------------------------------------------------

# 1. Validate that a version number was provided
if [[ -z "$1" ]]; then
    echo "Error: No version specified." >&2
    echo "Usage: $0 <net-snmp-version>" >&2
    echo "Example: $0 5.9" >&2
    exit 1
fi

VERSION="$1"

# --- Define paths at the top for clarity ---
SOURCE_DIR="./net-snmp-${VERSION}"
FINAL_DEST_DIR="../src/net-snmp-${VERSION}-final-patched"

if [[ "$VERSION" == "5.9" ]]; then
    PATCH_DIR="../net-snmp-${VERSION}-patches" # Adjusted for cd
else
    PATCH_DIR="../net-snmp-${VERSION}-final-patches" # Adjusted for cd
fi

# 2. Check that the required directories exist
if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "Error: Source directory not found: ${SOURCE_DIR}" >&2
    exit 1
fi

# 3. Create the final destination directory if it doesn't exist
echo "Ensuring destination directory exists: ${FINAL_DEST_DIR}"
mkdir -p "${FINAL_DEST_DIR}"

# 4. Check for dos2unix command
if ! command -v dos2unix &> /dev/null; then
    echo "Error: 'dos2unix' command not found." >&2
    exit 1
fi

# 5. Use the same list of tools
tools=(
    "snmpwalk" "snmpget" "snmpset" "snmptrap"
    "snmpbulkwalk" "snmpbulkget" "snmpgetnext"
)

# Change into the source directory to apply patches correctly
cd "${SOURCE_DIR}"

if [[ ! -d "$PATCH_DIR" ]]; then
    echo "Error: Patch directory not found at ${PATCH_DIR}" >&2
    cd ..
    exit 1
fi

echo "Applying final patches and moving files for version ${VERSION}..."

for tool in "${tools[@]}"; do
    patch_file="${PATCH_DIR}/${tool}-${VERSION}.patch"
    original_c_file="apps/${tool}.c"

    if [[ ! -f "$patch_file" ]] || [[ ! -f "$original_c_file" ]]; then
        echo "  -- Skipping ${tool}: Required file(s) not found."
        continue
    fi
    
    dos2unix "${patch_file}" &> /dev/null
    dos2unix "${original_c_file}" &> /dev/null

    echo "  -> Patching ${tool}.c..."
    # --- THIS IS THE MODIFIED LINE ---
    # The -p2 flag strips the first two components (e.g., './net-snmp-5.6/')
    patch -p2 < "${patch_file}"

    echo "  -> Moving and renaming to ${FINAL_DEST_DIR}/${tool}.cpp"
    mv "${original_c_file}" "${FINAL_DEST_DIR}/${tool}.cpp"
done

echo "Restoring original source files..."
for tool in "${tools[@]}"; do
    git restore "apps/${tool}.c"
done

# Go back to the original directory
cd ..

echo "Done. Patched files have been moved to ${FINAL_DEST_DIR}."