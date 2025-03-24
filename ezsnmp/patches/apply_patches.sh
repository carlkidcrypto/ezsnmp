#!/bin/bash

# Apply the patches
echo "Applying patches..."
PATCH_DIR="$(pwd)"
NEW_FILES=()

for patch in "$PATCH_DIR"/*.patch; do
    echo "Applying $patch..."
    patched_files=$(patch -p1 --dry-run < "$patch" | grep "patching file" | awk '{print $3}' | tr -d "'")
    patch -p1 < "$patch"
    for file in $patched_files; do
        new_file_name="$(basename "$file" .c)"
        echo "Moving and renaming patched file $file to $PATCH_DIR/$new_file_name..."
        rm -f "$PATCH_DIR/$new_file_name"
        cp ./"$file" "$PATCH_DIR/$new_file_name"
        NEW_FILES+=("$new_file_name")
    done
done

# Move the new files to the src directory
SRC_DIR="$PATCH_DIR/../src"

echo "Moving new files to $SRC_DIR..."
mkdir -p "$SRC_DIR"

for new_file in "${NEW_FILES[@]}"; do
    echo "Moving $new_file to $SRC_DIR..."
    mv "$PATCH_DIR/$new_file" "$SRC_DIR/"
done

rm -drf ./src