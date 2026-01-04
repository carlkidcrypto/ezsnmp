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
  
  # Get the highest version number for today from local Docker image cache
  local highest_version=0
  
  # Check locally cached images to find the highest existing version for today
  # Note: This only checks local Docker cache, not Docker Hub
  # If local cache is out of sync with remote registry, versioning may be incorrect
  # For a more robust solution, we could query the Docker Hub registry API
  
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
  echo "Usage: $0 <DOCKER_USERNAME> <DOCKER_ACCESS_TOKEN> [IMAGE_NAME] [--no-cache] [--prune]"
  echo ""
  echo "  <DOCKER_USERNAME>: Your Docker Hub username."
  echo "  <DOCKER_ACCESS_TOKEN>: Your Docker Hub Personal Access Token (PAT)."
  echo "  [IMAGE_NAME]: Optional. Specify a single image directory (e.g., 'almalinux10') to build only that image."
  echo "                If omitted, all images in '${DOCKER_DIR}' will be built."
  echo "  [--no-cache]: Optional. Add this flag to force rebuild without using Docker cache."
  echo "  [--prune]: Optional. Add this flag to run 'docker system prune -af' before building (removes dangling images/containers)."
  echo ""
  echo "Images will be tagged with format: MM-DD-YYYY.N (e.g., 12-24-2025.1)"
  echo "The .N version increments per day for each image."
  exit 1
fi

USERNAME=$1
ACCESS_TOKEN=$2
TARGET_IMAGE=""
NO_CACHE=""
PRUNE_DOCKER=""

# Parse optional arguments
shift 2
while [ $# -gt 0 ]; do
  case $1 in
    --no-cache)
      NO_CACHE="--no-cache"
      echo "Build mode: --no-cache enabled (forcing clean rebuild)"
      shift
      ;;
    --prune)
      PRUNE_DOCKER=1
      echo "Docker prune mode: --prune enabled (will clean Docker before building)"
      shift
      ;;
    *)
      TARGET_IMAGE=$1
      shift
      ;;
  esac
done

# --- Docker Cleanup (if requested) ---

if [ -n "${PRUNE_DOCKER}" ]; then
  echo "Cleaning up Docker (removing dangling images, containers, and unused volumes)..."
  docker system prune -af || echo "WARNING: Docker prune had issues, but continuing..."
  echo "Docker cleanup complete."
  echo "--------------------------------------------------"
fi

# --- Docker Hub Login ---

echo "Attempting to log in to Docker Hub..."
if ! echo "${ACCESS_TOKEN}" | docker login -u "${USERNAME}" --password-stdin; then
  echo "ERROR: Docker login failed. Please check your username and token."
  exit 1
fi

echo "Successfully logged in to Docker Hub."
echo "--------------------------------------------------"

# --- Populate Python Tarball Cache ---

echo "Checking Python tarball cache..."
CACHE_SCRIPT="${DOCKER_DIR}/cache/download_build_cache.sh"
if [ -f "${CACHE_SCRIPT}" ]; then
  echo "Running cache download script..."
  bash "${CACHE_SCRIPT}"
  if [ $? -ne 0 ]; then
    echo "WARNING: Cache download script failed, but continuing (downloads may occur during build)..."
  fi
else
  echo "WARNING: Cache download script not found at ${CACHE_SCRIPT}"
  echo "Python tarballs will be downloaded during build if needed."
fi
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
  # Exclude test_outputs_* directories
  DISTROS_TO_BUILD=($(find "${DOCKER_DIR}" -mindepth 1 -maxdepth 1 -type d ! -name "test_outputs_*" -printf "%f\n"))
  echo "Mode: Building all found images (excluding test_outputs directories)."
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
  echo "    - Build Options: ${NO_CACHE}"

  # 1. Build the image using the distro-specific Dockerfile with repo-root context
  if docker build ${NO_CACHE} -f "${DOCKERFILE_PATH}" -t "${DATED_TAG}" -t "${LATEST_TAG}" "${CONTEXT_PATH}"; then
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