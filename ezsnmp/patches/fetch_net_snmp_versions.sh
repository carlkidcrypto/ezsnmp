#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# --- Downloads a specific version of the Net-SNMP repository, removing old copies first ---
# Usage:
#   ./fetch_net_snmp_versions.sh <version> [--no-remove]
# Example:
#   ./fetch_net_snmp_versions.sh 5.10
#   ./fetch_net_snmp_versions.sh 5.11 --no-remove
# ----------------------------------------------------------------------------------------

# 1. Validate that a version number was provided
if [[ -z "$1" ]]; then
    echo "Error: No version specified." >&2
    echo "Usage: $0 <net-snmp-version> [--no-remove]" >&2
    echo "Net-SNMP 5.10 or newer is supported." >&2
    exit 1
fi

VERSION="$1"
if [[ ! "$VERSION" =~ ^([0-9]+)\.([0-9]+)(\.([0-9]+))?$ ]]; then
    echo "Error: Invalid Net-SNMP version '$VERSION'." >&2
    exit 1
fi
MAJOR=$((10#${BASH_REMATCH[1]}))
MINOR=$((10#${BASH_REMATCH[2]}))
if (( MAJOR < 5 || (MAJOR == 5 && MINOR < 10) )); then
    echo "Error: Net-SNMP 5.10 or newer is supported." >&2
    exit 1
fi

NO_REMOVE=false
if [[ "$2" == "--no-remove" ]]; then
    NO_REMOVE=true
fi

# Net-SNMP 5.10 currently uses a prerelease tag; later versions use v<version>.
if [[ "$VERSION" == "5.10" ]]; then
    TAG="v5.10.pre2"
else
    TAG="v${VERSION}"
fi

# 3. Define other variables
REPO_DIR="net-snmp-$VERSION"
REPO_URL="https://github.com/net-snmp/net-snmp.git"

echo "Configuring Net-SNMP version $VERSION..."
echo "Target tag: $TAG"

# 4. Handle existing directory
if [[ -d "$REPO_DIR" ]]; then
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