#!/bin/bash -e

# Formatting `sudo apt install shfmt && shfmt -w run_tests_in_all_dockers.sh`
sudo chown "$USER" /var/run/docker.sock

# --- Configuration ---
DOCKER_REPO_PATH="carlkidcrypto/ezsnmp_test_images"
# Path to the root of the ezsnmp repository (current working directory)
HOST_SOURCE_PATH=$(realpath "$(pwd)/../")
CONTAINER_WORK_DIR="/ezsnmp"

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
	# Test all images by finding directories in the current folder (excluding test_outputs_* folders).
	DISTROS_TO_TEST=($(find . -mindepth 1 -maxdepth 1 -type d -not -name '.' -not -name 'test_outputs_*' -printf "%f\n"))
	echo "Mode: Testing all found images."
fi

echo "Images to test: ${DISTROS_TO_TEST[*]}"
echo "--------------------------------------------------"

# --- Test Loop (parallelized) ---
rm -f -- *.xml *.txt *.info
rm -rf test_outputs_*/
for DISTRO_NAME in "${DISTROS_TO_TEST[@]}"; do

	# Create output directory for this distribution
	OUTPUT_DIR="test_outputs_${DISTRO_NAME}"
	mkdir -p "${OUTPUT_DIR}"

	FULL_IMAGE_TAG="${DOCKER_REPO_PATH}:${DISTRO_NAME}-latest"
	CONTAINER_NAME="${DISTRO_NAME}_test_container"
	# The entry script path must be adjusted for the container mount, which is always /ezsnmp/docker/[distro]/...
	ENTRY_SCRIPT_PATH="/ezsnmp/docker/${DISTRO_NAME}/DockerEntry.sh"

	echo ">>> Launching C++ tests for distribution: ${DISTRO_NAME} (async)"
	echo "    - Target Image: ${FULL_IMAGE_TAG}"
	echo "    - Output Directory: ${OUTPUT_DIR}"

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

		# 3. Run cpp tests using meson in an isolated workdir
		echo "    - [${DISTRO_NAME}] Executing meson tests..."
		docker exec -t "$CONTAINER_NAME" bash -c "
			set -e;
			export PATH=/usr/local/bin:/opt/rh/gcc-toolset-11/root/usr/bin:/opt/rh/devtoolset-11/root/usr/bin:\$PATH;
			export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64:\$LD_LIBRARY_PATH;
			WORK_DIR=/tmp/ezsnmp_${DISTRO_NAME};
			ARTIFACT_DIR=/tmp/artifacts_${DISTRO_NAME};
			rm -rf \$WORK_DIR \$ARTIFACT_DIR;
			mkdir -p \$WORK_DIR \$ARTIFACT_DIR;
			# Copy source to isolated directory, excluding build artifacts and venvs
			cd /ezsnmp && tar --exclude='*.egg-info' --exclude='build' --exclude='dist' --exclude='.tox' --exclude='__pycache__' --exclude='*.pyc' --exclude='.coverage*' --exclude='python3.*venv' --exclude='*.venv' --exclude='venv' -cf - . 2>/dev/null | (cd \$WORK_DIR && tar xf -);
			cd \$WORK_DIR/cpp_tests;
			rm -drf build/ *.info *.txt *.xml || true;
			meson setup build/ > \$ARTIFACT_DIR/meson-setup.log 2>&1;
			ninja -C build/ -j \$(nproc) > \$ARTIFACT_DIR/ninja-build.log 2>&1;
			ninja -C build/ -j \$(nproc) test > \$ARTIFACT_DIR/test-outputs.txt 2>&1;
			lcov --capture --directory build --output-file coverage.info --rc geninfo_unexecuted_blocks=1 --ignore-errors mismatch,empty || true;
			lcov --remove coverage.info '*/13/bits/*' '*/13/ext/*' --output-file updated_coverage.info --ignore-errors mismatch,empty || true;
			# Gather artifacts
			cp coverage.info \$ARTIFACT_DIR/coverage.info || true;
			cp updated_coverage.info \$ARTIFACT_DIR/updated_coverage.info || true;
			cp build/meson-logs/testlog.xml \$ARTIFACT_DIR/test-results.xml || true;
			exit 0;
		"

		# 4. Copy artifacts from the container to host.
		if docker cp "$CONTAINER_NAME:/tmp/artifacts_${DISTRO_NAME}/." "${OUTPUT_DIR}" > /dev/null 2>&1; then
			echo "    - [${DISTRO_NAME}] Artifacts copied to ${OUTPUT_DIR}"
		else
			echo "      ! [${DISTRO_NAME}] Warning: failed to copy artifacts"
		fi

		# 5. Cleanup container
		echo "    - [${DISTRO_NAME}] Cleaning up container"
		docker stop "$CONTAINER_NAME" > /dev/null 2>&1
		docker rm "$CONTAINER_NAME" > /dev/null 2>&1

		END_TIME=$(date +%s)
		TOTAL_DURATION=$((END_TIME - START_TIME))
		echo "    - [${DISTRO_NAME}] COMPLETED (Total time: ${TOTAL_DURATION}s)"
	) &

done

# Wait for all background jobs to complete
echo ""
echo "Waiting for all distributions to complete testing..."
wait

echo "--------------------------------------------------"

echo "All specified images tested."
