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
#   ./apply_patches.sh 5.9
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
FINAL_DEST_DIR="../src/net-snmp-${VERSION}-patched"

# Dynamically set PATCH_DIR based on the version number
if [[ "$VERSION" == "5.9" ]]; then
    # Version 5.9 uses the original, simpler path
    PATCH_DIR="./net-snmp-${VERSION}-patches"
else
    # Versions 5.6, 5.7, 5.8 use the new nested path
    PATCH_DIR="./net-snmp-${VERSION}-final-patches"
fi

# 2. Check that the required directories exist
if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "Error: Source directory not found: ${SOURCE_DIR}" >&2
    echo "Please run this script in the same directory as the source code." >&2
    exit 1
fi
if [[ ! -d "$PATCH_DIR" ]]; then
    echo "Error: Patch directory not found: ${PATCH_DIR}" >&2
    echo "Please ensure final patches for version ${VERSION} are available." >&2
    exit 1
fi

# 3. Create the final destination directory if it doesn't exist
echo "Ensuring destination directory exists: ${FINAL_DEST_DIR}"
mkdir -p "${FINAL_DEST_DIR}"

# 4. Check for dos2unix command
if ! command -v dos2unix &> /dev/null; then
    echo "Error: 'dos2unix' command not found, but is required to fix line endings." >&2
    echo "Please install it (e.g., 'sudo apt-get install dos2unix') and try again." >&2
    exit 1
fi

# 5. Use the same list of tools
tools=(
    "snmpwalk"
    "snmpget"
    "snmpset"
    "snmptrap"
    "snmpbulkwalk"
    "snmpbulkget"
    "snmpgetnext"
)

# 6. Loop through the tools, normalize, patch, and move
echo "Applying final patches and moving files for version ${VERSION} from ${PATCH_DIR}..."

for tool in "${tools[@]}"; do
    patch_file="${PATCH_DIR}/${tool}-${VERSION}.patch"
    original_c_file="${SOURCE_DIR}/apps/${tool}.c"

    # Skip if either the patch or the source file is missing
    if [[ ! -f "$patch_file" ]] || [[ ! -f "$original_c_file" ]]; then
        echo "  -- Skipping ${tool}: Required file(s) not found."
        continue
    fi

    # Normalize line endings for only the two files we are about to use
    dos2unix "${patch_file}" > /dev/null 2>&1
    dos2unix "${original_c_file}" > /dev/null 2>&1

    # Apply the patch to the original file
    echo "  -> Patching ${tool}.c..."
    patch "${original_c_file}" < "${patch_file}"

    # Move the patched .c file to its final destination with the new .cpp name
    echo "  -> Moving and renaming to ${FINAL_DEST_DIR}/${tool}.cpp"
    mv "${original_c_file}" "${FINAL_DEST_DIR}/${tool}.cpp"

done

echo "Restoring original source files in ${SOURCE_DIR}..."
cd "${SOURCE_DIR}"

for tool in "${tools[@]}"; do
    original_file_path="apps/${tool}.c"
    
    # We only need to try restoring it if its patch file existed.
    patch_file="../${PATCH_DIR}/${tool}-${VERSION}.patch"
    if [[ -f "${patch_file}" ]]; then
        echo "  -> Restoring ${original_file_path}"
        git restore "${original_file_path}"
    fi
done

cd ../

echo "Done. Patched files have been moved to ${FINAL_DEST_DIR}."