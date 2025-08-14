#!/bin/bash

# --- Initializes or updates a Net-SNMP submodule for a specific version ---
# Usage:
#   ./init_and_update_submodule.sh <version>
# Example:
#   ./init_and_update_submodule.sh 5.9
# --------------------------------------------------------------------------

# 1. Validate that a version number was provided
if [[ -z "$1" ]]; then
    echo "Error: No version specified." >&2
    echo "Usage: $0 <net-snmp-version>" >&2
    echo "Supported versions are: 5.6, 5.7, 5.8, 5.9" >&2
    exit 1
fi

VERSION="$1"
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
SUBMODULE_DIR="net-snmp-$VERSION"
REPO_URL="https://github.com/net-snmp/net-snmp.git"

echo "Configuring Net-SNMP version $VERSION..."
echo "Target tag: $TAG"

# 4. Check if the submodule directory already exists
if [ ! -d "$SUBMODULE_DIR" ]; then
    # If it doesn't exist, add it and check out the specific tag
    echo "Initializing new submodule in '$SUBMODULE_DIR'..."
    git submodule add --name "$SUBMODULE_DIR" "$REPO_URL" "$SUBMODULE_DIR"

    if [ $? -ne 0 ]; then
        echo "Error: Failed to add submodule." >&2
        exit 1
    fi

    # Navigate into the new submodule directory to check out the tag
    echo "Checking out tag '$TAG'..."
    (cd "$SUBMODULE_DIR" && git checkout "$TAG")

    if [ $? -ne 0 ]; then
        echo "Error: Failed to checkout tag '$TAG'. It may not exist." >&2
        git submodule deinit -f "$SUBMODULE_DIR" >/dev/null
        git rm -f "$SUBMODULE_DIR" >/dev/null
        rm -rf ".git/modules/$SUBMODULE_DIR"
        exit 1
    fi

    git add .gitmodules "$SUBMODULE_DIR"
    echo "Submodule for version $VERSION initialized successfully."
    echo "Remember to commit these changes to your main project."

else
    # If it already exists, just ensure it's on the correct tag
    echo "Submodule '$SUBMODULE_DIR' already exists."
    echo "Fetching and checking out tag '$TAG'..."
    (
      cd "$SUBMODULE_DIR" && \
      git fetch --tags && \
      git checkout "$TAG"
    )
    git add "$SUBMODULE_DIR"
    echo "Submodule updated to tag '$TAG'."
fi

# Finally, ensure any nested submodules are initialized and updated
git submodule update --init --recursive "$SUBMODULE_DIR"

echo "Done."