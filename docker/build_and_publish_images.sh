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
  echo "Usage: $0 <DOCKER_USERNAME> <DOCKER_ACCESS_TOKEN> [IMAGE_NAME] [--no-cache] [--prune] [--platform <TARGET_PLATFORM>] [--progress <PROGRESS_MODE>] [--ghcr-user <GHCR_USERNAME>] [--ghcr-token <GHCR_TOKEN>]"
  echo ""
  echo "  <DOCKER_USERNAME>: Your Docker Hub username."
  echo "  <DOCKER_ACCESS_TOKEN>: Your Docker Hub Personal Access Token (PAT)."
  echo "  [IMAGE_NAME]: Optional. Specify a single image directory (e.g., 'almalinux10') to build only that image."
  echo "                If omitted, all images in '${DOCKER_DIR}' will be built."
  echo "  [--no-cache]: Optional. Add this flag to force rebuild without using Docker cache."
  echo "  [--prune]: Optional. Add this flag to run 'docker system prune -af' before building (removes dangling images/containers)."
  echo "  [--platform <TARGET_PLATFORM>]: Optional. Build target platform (e.g., linux/amd64, linux/arm64)."
  echo "                                On Apple Silicon macOS, defaults to linux/amd64 for compatibility with legacy images."
  echo "  [--progress <PROGRESS_MODE>]: Optional. Docker build progress mode (auto, plain, tty). Default: plain."
  echo "  [--ghcr-user <GHCR_USERNAME>]: Optional. GitHub username for GitHub Container Registry (ghcr.io)."
  echo "  [--ghcr-token <GHCR_TOKEN>]: Optional. GitHub Personal Access Token (PAT) with 'write:packages' scope for ghcr.io."
  echo "                               Both --ghcr-user and --ghcr-token must be provided to enable GHCR publishing."
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
GHCR_USERNAME=""
GHCR_TOKEN=""
TARGET_PLATFORM=""
PROGRESS_MODE="plain"

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
    --platform)
      if [ -z "${2:-}" ] || [[ "$2" == --* ]]; then
        echo "ERROR: --platform requires a non-empty argument (e.g., linux/amd64)."
        exit 1
      fi
      TARGET_PLATFORM=$2
      shift 2
      ;;
    --progress)
      if [ -z "${2:-}" ] || [[ "$2" == --* ]]; then
        echo "ERROR: --progress requires a non-empty argument (auto, plain, tty)."
        exit 1
      fi
      PROGRESS_MODE=$2
      shift 2
      ;;
    --ghcr-user)
      if [ -z "${2:-}" ] || [[ "$2" == --* ]]; then
        echo "ERROR: --ghcr-user requires a non-empty username argument."
        exit 1
      fi
      GHCR_USERNAME=$2
      shift 2
      ;;
    --ghcr-token)
      if [ -z "${2:-}" ] || [[ "$2" == --* ]]; then
        echo "ERROR: --ghcr-token requires a non-empty token argument."
        exit 1
      fi
      GHCR_TOKEN=$2
      shift 2
      ;;
    *)
      TARGET_IMAGE=$1
      shift
      ;;
  esac
done

if [ -z "${TARGET_PLATFORM}" ]; then
  HOST_OS="$(uname -s 2>/dev/null || true)"
  HOST_ARCH="$(uname -m 2>/dev/null || true)"
  if [ "${HOST_OS}" = "Darwin" ] && [ "${HOST_ARCH}" = "arm64" ]; then
    TARGET_PLATFORM="linux/amd64"
    echo "Platform mode: Apple Silicon detected; defaulting to --platform ${TARGET_PLATFORM} for maximum image compatibility"
  fi
fi

if [ -n "${TARGET_PLATFORM}" ]; then
  echo "Build platform: ${TARGET_PLATFORM}"
fi
echo "Build progress mode: ${PROGRESS_MODE}"

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

# --- GitHub Container Registry Login (optional) ---

GHCR_REPO_PATH=""
if [ -n "${GHCR_USERNAME}" ] && [ -n "${GHCR_TOKEN}" ]; then
  echo "Attempting to log in to GitHub Container Registry (ghcr.io)..."
  if ! echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USERNAME}" --password-stdin; then
    echo "ERROR: GHCR login failed. Please check your GitHub username and token."
    docker logout
    exit 1
  fi
  GHCR_REPO_PATH="ghcr.io/${GHCR_USERNAME}/ezsnmp_test_images"
  echo "Successfully logged in to GitHub Container Registry."
  echo "GHCR images will be published to: ${GHCR_REPO_PATH}"
elif [ -n "${GHCR_USERNAME}" ] || [ -n "${GHCR_TOKEN}" ]; then
  echo "WARNING: Both --ghcr-user and --ghcr-token must be provided to publish to GHCR. Skipping."
else
  echo "INFO: GHCR credentials not provided. Skipping GitHub Container Registry publishing."
fi
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
  # Exclude non-image directories (test outputs, caches, previous results, etc.)
  DISTROS_TO_BUILD=($(find "${DOCKER_DIR}" \
    -mindepth 1 -maxdepth 1 -type d \
    ! -name "test_outputs*" \
    ! -name "previous_results*" \
    ! -name "test-results*" \
    ! -name "cache" \
    ! -name "__pycache__" \
    -exec basename {} \;))
  echo "Mode: Building all found images (excluding test_outputs*, test-results*, previous_results*, and cache directories)."
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
  if [ -n "${TARGET_PLATFORM}" ]; then
    echo "    - Platform: ${TARGET_PLATFORM}"
  fi
  echo "    - Progress: ${PROGRESS_MODE}"

  # Compute GHCR tags if GHCR publishing is enabled
  GHCR_DATED_TAG=""
  GHCR_LATEST_TAG=""
  BUILD_TAGS="-t ${DATED_TAG} -t ${LATEST_TAG}"
  if [ -n "${GHCR_REPO_PATH}" ]; then
    VERSION_SUFFIX="${DATED_TAG#${DOCKER_REPO_PATH}:${DISTRO_NAME}-}"
    GHCR_DATED_TAG="${GHCR_REPO_PATH}:${DISTRO_NAME}-${VERSION_SUFFIX}"
    GHCR_LATEST_TAG="${GHCR_REPO_PATH}:${DISTRO_NAME}-latest"
    BUILD_TAGS="${BUILD_TAGS} -t ${GHCR_DATED_TAG} -t ${GHCR_LATEST_TAG}"
    echo "    - GHCR Dated Tag: ${GHCR_DATED_TAG}"
    echo "    - GHCR Latest Tag: ${GHCR_LATEST_TAG}"
  fi

  # 1. Build the image using the distro-specific Dockerfile with repo-root context
  BUILD_CMD=(docker build --progress "${PROGRESS_MODE}")
  if [ -n "${NO_CACHE}" ]; then
    BUILD_CMD+=("${NO_CACHE}")
  fi
  if [ -n "${TARGET_PLATFORM}" ]; then
    BUILD_CMD+=(--platform "${TARGET_PLATFORM}")
  fi
  BUILD_CMD+=(-f "${DOCKERFILE_PATH}")
  read -r -a TAG_ARGS <<< "${BUILD_TAGS}"
  BUILD_CMD+=("${TAG_ARGS[@]}" "${CONTEXT_PATH}")

  if "${BUILD_CMD[@]}"; then
    echo "    - Build successful."
  else
    echo "ERROR: Docker build failed for ${DISTRO_NAME}."
    continue # Skip pushing if the build failed
  fi

    # 2. Push both the dated and latest tags to Docker Hub
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

    # 3. Push to GitHub Container Registry if enabled
    if [ -n "${GHCR_REPO_PATH}" ]; then
        for tag in "${GHCR_DATED_TAG}" "${GHCR_LATEST_TAG}"; do
            if docker push "${tag}"; then
                echo "    - Pushed GHCR tag: ${tag}"
            else
                echo "ERROR: Docker push failed for GHCR tag ${tag}."
            fi
        done
    fi

    echo "--------------------------------------------------"

done

# --- Cleanup ---

echo "All specified images processed."
echo "Logging out of Docker Hub..."
docker logout

if [ -n "${GHCR_REPO_PATH}" ]; then
  echo "Logging out of GitHub Container Registry..."
  docker logout ghcr.io
fi

echo "Script finished."