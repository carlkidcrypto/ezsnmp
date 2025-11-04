#!/bin/bash
set -euo pipefail

# --- Configuration ---
DOCKER_DIR="."
DOCKER_REPO_PATH="carlkidcrypto/ezsnmp_test_images"

# --- Script Usage and Input Validation ---

if [ $# -lt 2 ]; then
  echo "Usage: $0 <DOCKER_USERNAME> <DOCKER_ACCESS_TOKEN> [IMAGE_NAME]"
  echo ""
  echo "  <DOCKER_USERNAME>: Your Docker Hub username."
  echo "  <DOCKER_ACCESS_TOKEN>: Your Docker Hub Personal Access Token (PAT)."
  echo "  [IMAGE_NAME]: Optional. Specify a single image directory (e.g., 'almalinux10') to build only that image."
  echo "                If omitted, all images in '${DOCKER_DIR}' will be built."
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
    
    CONTEXT_PATH="${DOCKER_DIR}/${DISTRO_NAME}"
    FULL_IMAGE_TAG="${DOCKER_REPO_PATH}:${DISTRO_NAME}"

    echo ">>> Processing image: ${DISTRO_NAME}"
    echo "    - Context Path: ${CONTEXT_PATH}"
    echo "    - Target Tag: ${FULL_IMAGE_TAG}"

    # 1. Build the image
    # Note: Use a dedicated Dockerfile if it's not named 'Dockerfile'
    if docker build -t "${FULL_IMAGE_TAG}" "${CONTEXT_PATH}"; then
        echo "    - Build successful."
    else
        echo "ERROR: Docker build failed for ${DISTRO_NAME}."
        continue # Skip pushing if the build failed
    fi

    # 2. Push the image
    if docker push "${FULL_IMAGE_TAG}"; then
        echo "    - Push successful. Image is now available at ${FULL_IMAGE_TAG}"
    else
        echo "ERROR: Docker push failed for ${DISTRO_NAME}."
    fi
    
    echo "--------------------------------------------------"

done

# --- Cleanup ---

echo "All specified images processed."
echo "Logging out of Docker Hub..."
docker logout

echo "Script finished."