#!/bin/bash
set -e

# Versions to process
versions=("5.7" "5.8" "5.9" "5.10")

# Step 1: Download all net-snmp versions 5.7 - 5.10 in parallel
echo "##### Downloading net-snmp versions... #####"
for version in "${versions[@]}"; do
    echo "Fetching version $version..."
    ./fetch_net_snmp_versions.sh "$version" --no-remove &
done
wait  # Wait for all background jobs to finish

# Step 2: Generate patches for 5.9 and 5.10 directly from master_src (no modifications needed).
#
# master_src tracks the net-snmp upstream master branch and is used as the template for
# all C++ modifications. Upstream master removed netsnmp_cleanup_session() from snmpget,
# snmpset, and snmptrap, but kept it in snmpbulkget, snmpbulkwalk, snmpgetnext, snmpwalk.
#
# Both 5.9 and 5.10 are close enough to master that we can use master_src directly:
# - 5.10 (v5.10.pre2): The only diff vs master is the 3 removed cleanup calls, which
#   master_src already reflects correctly.
# - 5.9 (v5.9.4): Using master_src ensures 5.9 inherits the same cleanup decisions as
#   upstream master, keeping the codebase consistent across all versions.
#
# The "cleanup hack" below (Step 3-4) is only for 5.7/5.8, which are significantly
# older and benefit from having ALL netsnmp_cleanup_session() calls removed to avoid
# compatibility issues in the C++ wrapper context.
echo "##### Making patches for versions 5.9, 5.10... #####"
./make_patches.sh 5.9
./make_patches.sh 5.10

# Step 3: Backup master_src and remove all instances of netsnmp_cleanup_session(&session);
# This temporary modification generates "cleaner" patches for older versions (5.7, 5.8)
# that remove ALL cleanup session calls (including those still in upstream master for
# snmpbulkget, snmpbulkwalk, snmpgetnext, snmpwalk).
echo "##### Backing up master_src... #####"
cp -r master_src master_src_backup

echo "##### Removing netsnmp_cleanup_session(&session); from master_src... #####"
for file in master_src/*.cpp; do
    sed -i '/netsnmp_cleanup_session(&session);/d' "$file"
done

# Step 4: Run make_patches on 5.7 and 5.8 (older versions needing the full cleanup hack)
# 5.9 and 5.10 were already patched in Step 2 using unmodified master_src.
echo "##### Making patches for versions needing the cleanup hack... #####"
for version in "${versions[@]}"; do
    [[ "$version" == "5.9" || "$version" == "5.10" ]] && continue
    ./make_patches.sh "$version" &
done
wait  # Wait for all make_patches jobs to finish

# Step 5: Revert removal of netsnmp_cleanup_session(&session);
echo "##### Restoring master_src from backup... #####"
rm -rf master_src
mv master_src_backup master_src

# Step 6: Apply patches on all versions in parallel
echo "##### Applying patches for versions ${versions[*]}... #####"
for version in "${versions[@]}"; do
    ./apply_patches.sh "$version" &
done
wait  # Wait for all apply_patches jobs to finish

# Step 7: Run clang-format
echo "##### Running clang-format on entire repository... #####"
cd "$(dirname "$0")/../.."
find . -iname '*.h' -o -iname '*.cpp' | xargs clang-format-20 -i --style=file:.clang-format

echo "##### All tasks completed successfully. #####"