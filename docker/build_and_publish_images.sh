#!/bin/bash
set -euo pipefail

# --- Configuration ---
DOCKER_DIR="."
DOCKER_REPO_PATH="carlkidcrypto/ezsnmp_test_images"

# --- Script Usage and Input Validation ---

if [ $# -lt 2 ]; then
  echo "Usage: $0 <DOCKER_USERNAME> <DOCKER_ACCESS_TOKEN>"
  echo ""
  echo "  <DOCKER_USERNAME>: Your Docker Hub username."
  echo "  <DOCKER_ACCESS_TOKEN>: Your Docker Hub Personal Access Token (PAT)."
  exit 1
fi

USERNAME=$1
ACCESS_TOKEN=$2

# --- Docker Hub Login ---

echo "Attempting to log in to Docker Hub..."
echo "${ACCESS_TOKEN}" | docker login -u "${USERNAME}" --password-stdin

if [ $? -ne 0 ]; then
  echo "ERROR: Docker login failed. Please check your username and token."
  exit 1
fi

echo "Successfully logged in to Docker Hub."
echo "--------------------------------------------------"

# --- Build and Push Loop ---

# Find all directories inside the DOCKER_DIR
for DISTRO_NAME in $(find "${DOCKER_DIR}" -mindepth 1 -maxdepth 1 -type d -printf "%f\n"); do
    
    CONTEXT_PATH="${DOCKER_DIR}/${DISTRO_NAME}"
    FULL_IMAGE_TAG="${DOCKER_REPO_PATH}:${DISTRO_NAME}"

    echo ">>> Processing image: ${DISTRO_NAME}"
    echo "    - Context Path: ${CONTEXT_PATH}"
    echo "    - Target Tag: ${FULL_IMAGE_TAG}"

    # 1. Build the image
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