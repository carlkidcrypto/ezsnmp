#!/bin/bash
set -e

# Generic PATH discovery: check system defaults first, then common package managers
# (Homebrew on macOS Apple Silicon/Intel, Linuxbrew on Linux, MacPorts)
for bin_dir in \
    "/opt/homebrew/bin" \
    "/usr/local/bin" \
    "/home/linuxbrew/.linuxbrew/bin" \
    "/opt/local/bin"; do
    if [[ -d "$bin_dir" && ":$PATH:" != *":$bin_dir:"* ]]; then
        export PATH="$bin_dir:$PATH"
    fi
done

# If brew is installed, ensure its prefix bin is in PATH as well
if command -v brew >/dev/null 2>&1; then
    BREW_BIN="$(brew --prefix)/bin"
    if [[ -d "$BREW_BIN" && ":$PATH:" != *":$BREW_BIN:"* ]]; then
        export PATH="$BREW_BIN:$PATH"
    fi
fi

# Versions to process (defaults to 5.10; or pass versions as arguments, e.g. ./do_all_that_stuff.sh 5.10)
if [[ $# -gt 0 ]]; then
    versions=("$@")
else
    versions=("5.10")
fi

is_supported_version() {
    [[ "$1" =~ ^([0-9]+)\.([0-9]+)(\.([0-9]+))?$ ]] || return 1
    local major=$((10#${BASH_REMATCH[1]}))
    local minor=$((10#${BASH_REMATCH[2]}))
    (( major > 5 || (major == 5 && minor >= 10) ))
}

for version in "${versions[@]}"; do
    if ! is_supported_version "$version"; then
        echo "Error: Net-SNMP version '$version' is unsupported; use version 5.10 or newer." >&2
        exit 1
    fi
done

# Step 1: Download net-snmp versions in parallel
echo "##### Downloading net-snmp versions... #####"
for version in "${versions[@]}"; do
    echo "Fetching version $version..."
    ./fetch_net_snmp_versions.sh "$version" --no-remove &
done
wait  # Wait for all background jobs to finish

# Step 2: Generate patches directly from master_src
echo "##### Making patches for versions ${versions[*]}... #####"
for version in "${versions[@]}"; do
    ./make_patches.sh "$version"
done

# Step 3: Apply patches on all versions in parallel
echo "##### Applying patches for versions ${versions[*]}... #####"
for version in "${versions[@]}"; do
    ./apply_patches.sh "$version" &
done
wait  # Wait for all apply_patches jobs to finish

# Step 4: Run clang-format
echo "##### Running clang-format on entire repository... #####"
cd "$(dirname "$0")/../.."
CLANG_FORMAT=""
for cf in clang-format-20 clang-format-19 clang-format-18 clang-format-17 clang-format; do
    if command -v "$cf" >/dev/null 2>&1; then
        CLANG_FORMAT="$cf"
        break
    fi
done

if [[ -n "$CLANG_FORMAT" ]]; then
    echo "Formatting with $CLANG_FORMAT..."
    find . \( -iname '*.h' -o -iname '*.cpp' \) -exec "$CLANG_FORMAT" -i --style=file:.clang-format {} +
else
    echo "Notice: clang-format not found, skipping formatting." >&2
fi

echo "##### All tasks completed successfully. #####"