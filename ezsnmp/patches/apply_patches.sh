#!/bin/bash

# --- Script to apply custom final patches and move them to a final directory ---
#
# Usage:
#   1. Start with a fresh, clean 'net-snmp-X.X' source directory.
#   2. Place this script next to the source and the patch directories.
#   3. Run it with the version number(s).
#
# Example:
#   ./apply_patches.sh 5.6 5.7 5.8 5.9
#   ./apply_patches.sh 5.6 5.9
#   ./apply_patches.sh 5.6
# --------------------------------------------------------------------

# 1. Validate that at least one version number was provided
if [[ $# -eq 0 ]]; then
    echo "Error: No version specified." >&2
    echo "Usage: $0 <net-snmp-version> [<net-snmp-version> ...]" >&2
    echo "Example: $0 5.6 5.8" >&2
    exit 1
fi

# 2. Check for dos2unix command
if ! command -v dos2unix &> /dev/null; then
    echo "Error: 'dos2unix' command not found." >&2
    exit 1
fi

# 3. Loop over all provided versions
for VERSION in "$@"; do
    # --- Define paths at the top for clarity ---
    SOURCE_DIR="./net-snmp-${VERSION}"
    FINAL_DEST_DIR="../src/net-snmp-${VERSION}-final-patched"
    REJECTS_DIR="../patch-rejects"

    # Convert paths to absolute paths before changing directories.
    FINAL_DEST_DIR=$(realpath "${FINAL_DEST_DIR}")
    REJECTS_DIR=$(realpath "${REJECTS_DIR}")
    PATCH_DIR="../net-snmp-${VERSION}-patches"

    # Check that the required directories exist
    if [[ ! -d "$SOURCE_DIR" ]]; then
        echo "Error: Source directory not found: ${SOURCE_DIR}" >&2
        continue
    fi

    # Create the destination directories if they don't exist
    echo "Ensuring destination directory exists: ${FINAL_DEST_DIR}"
    mkdir -p "${FINAL_DEST_DIR}"

    echo "Ensuring rejects directory exists: ${REJECTS_DIR}"
    mkdir -p "${REJECTS_DIR}"

    # Use the same list of tools
    tools=(
        "snmpwalk" "snmpget" "snmpset" "snmptrap"
        "snmpbulkwalk" "snmpbulkget" "snmpgetnext"
    )

    # Change into the source directory to apply patches correctly
    cd "${SOURCE_DIR}"

    # --- NEW: Clean up stale reject files inside the source directory ---
    echo "Cleaning up stale rejects inside $(pwd)..."
    find . -type f -name "*.rej" -delete

    if [[ ! -d "$PATCH_DIR" ]]; then
        echo "Error: Patch directory not found at ${PATCH_DIR}" >&2
        cd ..
        continue
    fi

    echo "Applying final patches and moving files for version ${VERSION}..."

    for tool in "${tools[@]}"; do
        patch_file="${PATCH_DIR}/${tool}-${VERSION}.patch"
        original_c_file="apps/${tool}.c"

        if [[ ! -f "$patch_file" ]] || [[ ! -f "$original_c_file" ]]; then
            echo "   -- Skipping ${tool}: Required file(s) not found."
            continue
        fi
        
        dos2unix "${patch_file}" &> /dev/null
        dos2unix "${original_c_file}" &> /dev/null

        echo "   -> Patching ${tool}.c..."

        # The -p2 flag strips the first two components (e.g., './net-snmp-5.6/')
        patch -p2 < "${patch_file}"

        # Check for and move any reject files, handling potential name collisions
        reject_file="${original_c_file}.rej"
        if [[ -f "$reject_file" ]]; then
            base_reject_name="${tool}-${VERSION}"
            final_reject_path="${REJECTS_DIR}/${base_reject_name}.rej"
            
            # If a reject file with the same name exists, append a counter
            counter=1
            while [[ -f "$final_reject_path" ]]; do
                final_reject_path="${REJECTS_DIR}/${base_reject_name}-${counter}.rej"
                ((counter++))
            done

            # Use ##*/ to get just the filename for the log message
            echo "   !! Patch failed. Moving reject file to ${REJECTS_DIR}/${final_reject_path##*/}"
            mv "$reject_file" "$final_reject_path"
        fi

        echo "   -> Moving and renaming to ${FINAL_DEST_DIR}/${tool}.cpp"
        # 'mv' now uses the correct, absolute path for the destination
        mv "${original_c_file}" "${FINAL_DEST_DIR}/${tool}.cpp"
    done

    echo "Restoring original source files..."
    for tool in "${tools[@]}"; do
        git restore "apps/${tool}.c"
    done

    # Go back to the original directory
    cd ..

    echo "Done for version ${VERSION}."
done

echo "All done."
