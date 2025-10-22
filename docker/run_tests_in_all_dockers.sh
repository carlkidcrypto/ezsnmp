#!/bin/bash
# Formatting `sudo apt install shfmt && shfmt -w run_tests_in_all_dockers.sh`
set -euo pipefail

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
	DISTROS_TO_TEST=(${TARGET_IMAGE})
	echo "Mode: Testing only the single image: ${TARGET_IMAGE}"
else
	# Test all images by finding directories in the current folder (excluding the current directory itself).
	DISTROS_TO_TEST=($(find . -mindepth 1 -maxdepth 1 -type d -not -name '.' -printf "%f\n"))
	echo "Mode: Testing all found images."
fi

echo "Images to test: ${DISTROS_TO_TEST[@]}"
echo "--------------------------------------------------"

# --- Test Loop ---
TEST_EXIT_CODE=0

for DISTRO_NAME in "${DISTROS_TO_TEST[@]}"; do

	FULL_IMAGE_TAG="${DOCKER_REPO_PATH}:${DISTRO_NAME}"
	CONTAINER_NAME="${DISTRO_NAME}_test_container"
	# The entry script path must be adjusted for the container mount, which is always /ezsnmp/docker/[distro]/...
	ENTRY_SCRIPT_PATH="/ezsnmp/docker/${DISTRO_NAME}/DockerEntry.sh"

	echo ">>> Running tests for distribution: ${DISTRO_NAME}"
	echo "    - Target Image: ${FULL_IMAGE_TAG}"

	# Cleanup any existing container with the same name
	if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
		docker stop $CONTAINER_NAME
	fi
	docker rm -f $CONTAINER_NAME

	# 1. Pull the image
	echo "    - Pulling image..."
	if ! docker pull "${FULL_IMAGE_TAG}"; then
		echo "ERROR: Docker pull failed for ${DISTRO_NAME}. Skipping tests."
		TEST_EXIT_CODE=1
		continue
	fi

	# 2. Start the container
	echo "    - Starting container: ${CONTAINER_NAME} and daemon..."
	echo "      * Using host source path: ${HOST_SOURCE_PATH}"
	# The command runs the entry script in the background and uses 'tail' as the foreground process
	if ! docker run -d \
		--name "${CONTAINER_NAME}" \
		-v "${HOST_SOURCE_PATH}:${CONTAINER_WORK_DIR}" \
		"${FULL_IMAGE_TAG}" \
		/bin/bash -c "${ENTRY_SCRIPT_PATH} & tail -f /dev/null"; then
		echo "ERROR: Docker run failed for ${DISTRO_NAME}. Skipping tests."
		TEST_EXIT_CODE=1
		continue
	fi

	# 3. Wait for SNMP daemon to start
	WAIT_TIME=240
	echo "    - Waiting for SNMP daemon to be ready (max ${WAIT_TIME}s)..."
	SNMP_READY=0
	for i in $(seq $WAIT_TIME -1 1); do
		if docker logs "${CONTAINER_NAME}" 2>&1 | grep -q "Starting SNMP daemon..."; then
			echo -ne "\n    - Container started successfully in $((WAIT_TIME - i)) seconds.\n"
			SNMP_READY=1
			break
		fi
		echo -ne "    - Waiting... $i seconds remaining\r"
		sleep 1
		if [ "$i" -eq 1 ] && [ "${SNMP_READY}" -eq 0 ]; then
			break # Break out of loop on final check if not ready
		fi
	done

	if [ "${SNMP_READY}" -eq 0 ]; then
		echo -ne "\nERROR: Timeout waiting for SNMP daemon to start in ${CONTAINER_NAME}. Skipping tests.\n"
		TEST_EXIT_CODE=1

		# Cleanup failed container start attempt
		docker stop "${CONTAINER_NAME}" >/dev/null 2>&1 || true
		docker rm "${CONTAINER_NAME}" >/dev/null 2>&1 || true
		continue
	fi

	# 4. Run tests using tox
	echo "    - Executing tox tests..."
	# Define a unique root directory inside the container's working directory
	UNIQUE_TOX_DIR="/ezsnmp/.tox_${DISTRO_NAME}"

	# Default single tox run for other distributions
	# ISSUE HERE THIS EXISTS IMEEDIATELY AFTER AND DOESNT WAIT FOR TOX TO FINIDH
	docker exec -t -i "${CONTAINER_NAME}" bash -c '
            rm -drf .tox;
            export TOX_ROOT=${UNIQUE_TOX_DIR};
            tox > test-outputs_${CONTAINER_NAME}.txt 2>&1;
            mv test-results.xml test-results_${CONTAINER_NAME}.xml;
        '
	# Copy artifacts from the container to host
	docker cp ${CONTAINER_NAME}:/ezsnmp/test-results_${CONTAINER_NAME}.xml .
	docker cp ${CONTAINER_NAME}:/ezsnmp/test-outputs_${CONTAINER_NAME}.txt .

	# 5. Copy results
	echo "    - Copying test artifacts back to host..."
	# Copy the whole mount directory content back
	# The trailing '.' is crucial here
	docker cp "${CONTAINER_NAME}":/ezsnmp/. "${HOST_SOURCE_PATH}"

	# 6. Cleanup container
	echo "    - Cleaning up container: ${CONTAINER_NAME}"
	docker stop "${CONTAINER_NAME}"
	docker rm "${CONTAINER_NAME}"

	echo "--------------------------------------------------"

done

# --- Cleanup ---

echo "All specified images tested."
# Docker Hub logout is removed.

# Exit with the overall test result
if [ "${TEST_EXIT_CODE}" -ne 0 ]; then
	echo "WARNING: One or more test suites failed."
	exit "${TEST_EXIT_CODE}"
else
	echo "SUCCESS: All test suites passed."
fi
