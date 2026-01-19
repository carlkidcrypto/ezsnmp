#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# --- Downloads a specific version of the Net-SNMP repository, removing old copies first ---
# Usage:
#   ./download_netsnmp.sh <version> [--no-remove]
# Example:
#   ./download_netsnmp.sh 5.9
#   ./download_netsnmp.sh 5.9 --no-remove
# ----------------------------------------------------------------------------------------

# 1. Validate that a version number was provided
if [[ -z "$1" ]]; then
    echo "Error: No version specified." >&2
    echo "Usage: $0 <net-snmp-version> [--no-remove]" >&2
    echo "Supported versions are: 5.6, 5.7, 5.8, 5.9" >&2
    exit 1
fi

VERSION="$1"
NO_REMOVE=false
if [[ "$2" == "--no-remove" ]]; then
    NO_REMOVE=true
fi
TAG=""

# 2. Map the input version to the specific hardcoded git tag
case "$VERSION" in
  "5.6")
    TAG="v5.6.2.1"
    ;;
  "5.7")
    TAG="v5.7.3"
    ;;
  "5.8")
    TAG="v5.8.1.rc1"
    ;;
  "5.9")
    TAG="v5.9.4"
    ;;
  *)
    echo "Error: Unsupported version '$VERSION'." >&2
    echo "Please use one of the supported versions: 5.6, 5.7, 5.8, 5.9" >&2
    exit 1
    ;;
esac

# 3. Define other variables
REPO_DIR="net-snmp-$VERSION"
REPO_URL="https://github.com/net-snmp/net-snmp.git"

echo "Configuring Net-SNMP version $VERSION..."
echo "Target tag: $TAG"

# 4. Handle existing directory
if [ -d "$REPO_DIR" ]; then
    if [[ "$NO_REMOVE" == true ]]; then
        echo "Directory '$REPO_DIR' already exists, skipping download."
        exit 0
    else
        echo "Removing existing directory '$REPO_DIR'..."
        rm -rf "$REPO_DIR"
    fi
fi

# 5. Clone the repository and check out the specific tag
# We use --depth 1 for a shallow clone, as we only need the code at this specific tag.
echo "Cloning repository into '$REPO_DIR'..."
git clone --branch "$TAG" --depth 1 "$REPO_URL" "$REPO_DIR"

echo "Successfully downloaded Net-SNMP (tag: $TAG) into '$REPO_DIR'."
echo "Done."