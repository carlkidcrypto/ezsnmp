#!/bin/bash
set -euo pipefail

# --- Configuration ---
DOCKER_DIR="."
DOCKER_REPO_PATH="carlkidcrypto/ezsnmp_test_images"

# --- Helper Function to Generate Dated Tags ---
# Generates tags in format: MM-DD-YYYY.N where N increments per day
get_next_version() {
  local image_name=$1
  local today=$(date +%m-%d-%Y)
  local base_tag="${DOCKER_REPO_PATH}:${image_name}-${today}"
  
  # Get the highest version number for today from Docker Hub
  local highest_version=0
  
  # Try to list all tags for this repo and filter for today's tags
  # We'll use docker pull and check locally if images exist
  # For a more robust solution, we could query the registry API
  # but this approach is simpler and doesn't require auth to read tags
  
  # Check if any today's tags exist locally by trying to inspect them
  for version in {1..100}; do
    local tag="${base_tag}.${version}"
    if docker inspect "${tag}" &>/dev/null 2>&1; then
      highest_version=$version
    else
      # Stop checking after we find a gap
      break
    fi
  done
  
  # Increment for next version
  local next_version=$((highest_version + 1))
  echo "${base_tag}.${next_version}"
}

# --- Script Usage and Input Validation ---

if [ $# -lt 2 ]; then
  echo "Usage: $0 <DOCKER_USERNAME> <DOCKER_ACCESS_TOKEN> [IMAGE_NAME]"
  echo ""
  echo "  <DOCKER_USERNAME>: Your Docker Hub username."
  echo "  <DOCKER_ACCESS_TOKEN>: Your Docker Hub Personal Access Token (PAT)."
  echo "  [IMAGE_NAME]: Optional. Specify a single image directory (e.g., 'almalinux10') to build only that image."
  echo "                If omitted, all images in '${DOCKER_DIR}' will be built."
  echo ""
  echo "Images will be tagged with format: MM-DD-YYYY.N (e.g., 12-24-2025.1)"
  echo "The .N version increments per day for each image."
  exit 1
fi

USERNAME=$1
ACCESS_TOKEN=$2
TARGET_IMAGE=${3:-} # Optional 3rd argument, empty if not provided

# --- Docker Hub Login ---

echo "Attempting to log in to Docker Hub..."
if ! echo "${ACCESS_TOKEN}" | docker login -u "${USERNAME}" --password-stdin; then
  echo "ERROR: Docker login failed. Please check your username and token."
  exit 1
fi

echo "Successfully logged in to Docker Hub."
echo "--------------------------------------------------"

# --- Determine Images to Build ---

# We assume the images are tagged the same as the folder names in the current directory.
if [ -n "${TARGET_IMAGE}" ]; then
  # Build only the specified image
  if [ ! -d "${DOCKER_DIR}/${TARGET_IMAGE}" ]; then
    echo "ERROR: Specified image directory '${DOCKER_DIR}/${TARGET_IMAGE}' does not exist."
    docker logout
    exit 1
  fi
  DISTROS_TO_BUILD=("${TARGET_IMAGE}")
  echo "Mode: Building only the single image: ${TARGET_IMAGE}"
else
  # Build all images by finding directories in DOCKER_DIR
  DISTROS_TO_BUILD=($(find "${DOCKER_DIR}" -mindepth 1 -maxdepth 1 -type d -printf "%f\n"))
  echo "Mode: Building all found images."
fi

echo "Images to process: ${DISTROS_TO_BUILD[*]}"
echo "--------------------------------------------------"

# --- Build and Push Loop ---

for DISTRO_NAME in "${DISTROS_TO_BUILD[@]}"; do

  CONTEXT_PATH=".." # Build from repo root so we can COPY top-level files
  DOCKERFILE_PATH="${DOCKER_DIR}/${DISTRO_NAME}/Dockerfile"
  
  # Generate the dated version tag
  DATED_TAG=$(get_next_version "${DISTRO_NAME}")
  
  # Also tag with 'latest' for convenience
  LATEST_TAG="${DOCKER_REPO_PATH}:${DISTRO_NAME}-latest"

  echo ">>> Processing image: ${DISTRO_NAME}"
  echo "    - Context Path: ${CONTEXT_PATH}"
  echo "    - Dockerfile: ${DOCKERFILE_PATH}"
  echo "    - Dated Tag: ${DATED_TAG}"
  echo "    - Latest Tag: ${LATEST_TAG}"

  # 1. Build the image using the distro-specific Dockerfile with repo-root context
  if docker build -f "${DOCKERFILE_PATH}" -t "${DATED_TAG}" -t "${LATEST_TAG}" "${CONTEXT_PATH}"; then
    echo "    - Build successful."
  else
    echo "ERROR: Docker build failed for ${DISTRO_NAME}."
    continue # Skip pushing if the build failed
  fi

    # 2. Push both the dated and latest tags
    if docker push "${DATED_TAG}"; then
        echo "    - Pushed dated tag: ${DATED_TAG}"
    else
        echo "ERROR: Docker push failed for dated tag ${DATED_TAG}."
    fi
    
    if docker push "${LATEST_TAG}"; then
        echo "    - Pushed latest tag: ${LATEST_TAG}"
    else
        echo "ERROR: Docker push failed for latest tag ${LATEST_TAG}."
    fi
    
    echo "--------------------------------------------------"

done

# --- Cleanup ---

echo "All specified images processed."
echo "Logging out of Docker Hub..."
docker logout

echo "Script finished."