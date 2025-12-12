#!/bin/bash -e

# Formatting `sudo apt install shfmt && shfmt -w run_tests_in_all_dockers.sh`
# Try to fix docker socket permissions, but don't fail if we can't
sudo chown "$USER" /var/run/docker.sock 2>/dev/null || true

# --- Cleanup function for Ctrl+C ---
cleanup() {
	echo ""
	echo "Caught interrupt signal - cleaning up..."
	# Kill all background jobs
	kill $(jobs -p) 2>/dev/null || true
	# Stop and remove any test containers
	for DISTRO in almalinux10 archlinux archlinux_netsnmp_5.8 centos7 rockylinux8; do
		docker stop "${DISTRO}_test_container" 2>/dev/null || true
		docker rm -f "${DISTRO}_test_container" 2>/dev/null || true
	done
	echo "Cleanup complete. Exiting."
	exit 130
}

# Set trap for Ctrl+C (SIGINT) and SIGTERM
trap cleanup SIGINT SIGTERM

# --- Configuration ---
DOCKER_REPO_PATH="carlkidcrypto/ezsnmp_test_images"
# Path to the root of the ezsnmp repository (current working directory)
HOST_SOURCE_PATH=$(realpath "$(pwd)/../")
CONTAINER_WORK_DIR="/ezsnmp"
TOX_PYTHON_VERSION=("py39" "py310" "py311" "py312" "py313")

# --- Script Usage and Input Validation ---

# The script now only accepts 0 or 1 argument (the optional image name).
if [ $# -gt 1 ]; then
	echo "Usage: $0 [IMAGE_NAME]"
	echo ""
	echo "  [IMAGE_NAME]: Optional. Specify a single image tag (e.g., 'almalinux10') to test only that distribution."
	echo "                If omitted, all distribution directories will be tested."
	exit 1
fi

TARGET_IMAGE=${1:-} # Optional 1st argument

# --- Determine Images to Test ---

# We assume the images are tagged the same as the folder names in the current directory.
if [ -n "${TARGET_IMAGE}" ]; then
	# Test only the specified image. Use the current directory for path validation.
	if [ ! -d "${TARGET_IMAGE}" ]; then
		echo "ERROR: Specified image directory '${TARGET_IMAGE}' does not exist in the current folder. Cannot determine DockerEntry.sh path."
		exit 1
	fi
	DISTROS_TO_TEST=("${TARGET_IMAGE}")
	echo "Mode: Testing only the single image: ${TARGET_IMAGE}"
else
	# Test all images by finding directories in the current folder (excluding the current directory itself and test_outputs_* folders).
	DISTROS_TO_TEST=($(find . -mindepth 1 -maxdepth 1 -type d -not -name '.' -not -name 'test_outputs_*' -printf "%f\n"))
	echo "Mode: Testing all found images."
fi

echo "Images to test: ${DISTROS_TO_TEST[*]}"
echo "--------------------------------------------------"

# --- Test Loop ---
rm -f -- *.xml *.txt ../.coverage.* ../test-outputs*.txt
rm -rdf test_outputs_*/
for DISTRO_NAME in "${DISTROS_TO_TEST[@]}"; do

	# Create output directory for this distribution
	OUTPUT_DIR="test_outputs_${DISTRO_NAME}"
	mkdir -p "${OUTPUT_DIR}"

	FULL_IMAGE_TAG="${DOCKER_REPO_PATH}:${DISTRO_NAME}-latest"
	CONTAINER_NAME="${DISTRO_NAME}_test_container"
	# The entry script path must be adjusted for the container mount, which is always /ezsnmp/docker/[distro]/...
	ENTRY_SCRIPT_PATH="/ezsnmp/docker/${DISTRO_NAME}/DockerEntry.sh"

	echo ">>> Launching tests for distribution: ${DISTRO_NAME} (async)"
	echo "    - Target Image: ${FULL_IMAGE_TAG}"
	echo "    - Output Directory: ${OUTPUT_DIR}"

	# Run each distribution in the background
	(
		START_TIME=$(date +%s)
		# Cleanup any existing container with the same name
		docker stop "$CONTAINER_NAME" 2>/dev/null || true
		docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

		# 1. Pull the image
		echo "    - [${DISTRO_NAME}] Pulling image..."
		if ! docker pull "${FULL_IMAGE_TAG}" > /dev/null 2>&1; then
			echo "ERROR: [${DISTRO_NAME}] Docker pull failed. Skipping tests."
			exit 1
		fi
		echo "    - [${DISTRO_NAME}] Image pulled successfully"

		# 2. Start the container
		echo "    - [${DISTRO_NAME}] Starting container and daemon..."
		if ! docker run -d \
			--name "${CONTAINER_NAME}" \
			-v "$HOST_SOURCE_PATH:$CONTAINER_WORK_DIR" \
			"${FULL_IMAGE_TAG}" \
			/bin/bash -c "${ENTRY_SCRIPT_PATH} false & tail -f /dev/null" > /dev/null 2>&1; then
			echo "ERROR: [${DISTRO_NAME}] Docker run failed. Skipping tests."
			exit 1
		fi
		echo "    - [${DISTRO_NAME}] Container started successfully"

		# 3. Run tests using tox
		echo "    - [${DISTRO_NAME}] Executing tox tests..."
		for TOX_PYTHON_VERSION_ITERATOR in "${!TOX_PYTHON_VERSION[@]}"; do
			TOX_PY=${TOX_PYTHON_VERSION[$TOX_PYTHON_VERSION_ITERATOR]}
			TOX_START=$(date +%s)
			echo "      * [${DISTRO_NAME}] Running tox for environment: $TOX_PY"

		OUTPUT_FILE="test-outputs_${DISTRO_NAME}_${TOX_PY}.txt"
		
		docker exec -t "$CONTAINER_NAME" bash -c "
			export PATH=/usr/local/bin:/opt/rh/gcc-toolset-11/root/usr/bin:/opt/rh/devtoolset-11/root/usr/bin:\$PATH;
			export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64:\$LD_LIBRARY_PATH;
			export WORK_DIR=/tmp/ezsnmp_${DISTRO_NAME};
			export TOX_WORK_DIR=/tmp/tox_${DISTRO_NAME};
			# Copy source to isolated directory, excluding build artifacts and venvs
			rm -rf \$WORK_DIR \$TOX_WORK_DIR;
			mkdir -p \$WORK_DIR;
			cd /ezsnmp && tar --exclude='*.egg-info' --exclude='build' --exclude='dist' --exclude='.tox' --exclude='__pycache__' --exclude='*.pyc' --exclude='.coverage*' --exclude='python3.*venv' --exclude='*.venv' --exclude='venv' -cf - . 2>/dev/null | (cd \$WORK_DIR && tar xf -);
			cd \$WORK_DIR;
			python3 -m pip install tox > /dev/null 2>&1;
			tox -e $TOX_PY --workdir \$TOX_WORK_DIR > /ezsnmp/$OUTPUT_FILE 2>&1;
			exit 0;
		"
		TOX_END=$(date +%s)
		TOX_DURATION=$((TOX_END - TOX_START))
		echo "      * [${DISTRO_NAME}] Completed: $TOX_PY (${TOX_DURATION}s)"			# 4. Copy artifacts from the container to the distribution's output folder
			if [ -f ../test-results.xml ]; then
				mv ../test-results.xml "${OUTPUT_DIR}/test-results_${CONTAINER_NAME}_${TOX_PY}.xml"
			else
				echo "      ! [${DISTRO_NAME}] Warning: test-results.xml not found for environment: $TOX_PY"
				touch "${OUTPUT_DIR}/test-results_${CONTAINER_NAME}_${TOX_PY}.xml"
			fi
			mv "../$OUTPUT_FILE" "${OUTPUT_DIR}/test-outputs_${CONTAINER_NAME}_${TOX_PY}.txt"
		done

		# 5. Cleanup container
		echo "    - [${DISTRO_NAME}] Cleaning up container"
		docker stop "$CONTAINER_NAME" 2>/dev/null
		docker rm "$CONTAINER_NAME" 2>/dev/null

		END_TIME=$(date +%s)
		TOTAL_DURATION=$((END_TIME - START_TIME))
		echo "    - [${DISTRO_NAME}] COMPLETED (Total time: ${TOTAL_DURATION}s)"
	) &  # Run in background

done

# Wait for all background jobs to complete
echo ""
echo "Waiting for all distributions to complete testing..."
wait

echo "--------------------------------------------------"

echo "All specified images tested."
