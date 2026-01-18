#!/bin/bash
set -e

# Versions to process
versions=("5.6" "5.7" "5.8" "5.9")

# Step 1: Download all net-snmp versions 5.6 - 5.9 in parallel
echo "##### Downloading net-snmp versions... #####"
for version in "${versions[@]}"; do
    echo "Fetching version $version..."
    ./fetch_net_snmp_versions.sh "$version" --no-remove &
done
wait  # Wait for all background jobs to finish

# Step 2: Call make_patches.sh on 5.9 first
echo "##### Making patches for version 5.9... #####"
./make_patches.sh 5.9

# Step 3: Backup master_src and remove all instances of netsnmp_cleanup_session(&session);
echo "##### Backing up master_src... #####"
cp -r master_src master_src_backup

echo "##### Removing netsnmp_cleanup_session(&session); from master_src... #####"
for file in master_src/*.cpp; do
    sed -i '/netsnmp_cleanup_session(&session);/d' "$file"
done

# Step 4: Run make_patches on 5.6-5.8 in parallel
echo "##### Making patches for versions 5.6, 5.7, 5.8... #####"
for version in 5.6 5.7 5.8; do
    ./make_patches.sh "$version" &
done
wait  # Wait for all make_patches jobs to finish

# Step 5: Apply patches on 5.6-5.9 in parallel
echo "##### Applying patches for versions 5.6, 5.7, 5.8, 5.9... #####"
for version in 5.6 5.7 5.8 5.9; do
    ./apply_patches.sh "$version" &
done
wait  # Wait for all apply_patches jobs to finish

# Step 6: Revert removal of netsnmp_cleanup_session(&session);
echo "##### Restoring master_src from backup... #####"
rm -rf master_src
mv master_src_backup master_src

# Step 7: Run clang-format
echo "##### Running clang-format on entire repository... #####"
cd ../../
find . -iname '*.h' -o -iname '*.cpp' | xargs clang-format-20 -i --style=file:.clang-format

echo "##### All tasks completed successfully. #####"