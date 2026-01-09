#!/bin/bash -e

# Formatting `sudo apt install shfmt && shfmt -w run_python_tests_in_all_dockers.sh`
# Try to fix docker socket permissions (best-effort, non-interactive)
if [ "$(id -u)" -eq 0 ]; then
	chown "${SUDO_USER:-$USER}" /var/run/docker.sock 2>/dev/null || true
else
	echo "Note: not root; skipping docker.sock permission adjustment."
fi

# --- Cleanup function for Ctrl+C ---
CLEANUP_IN_PROGRESS=0
cleanup() {
	# Prevent multiple simultaneous cleanup attempts
	if [ $CLEANUP_IN_PROGRESS -eq 1 ]; then
		return
	fi
	CLEANUP_IN_PROGRESS=1
	
	# Disable the trap to prevent recursive calls
	trap - SIGINT SIGTERM
	
	echo ""
	echo "Caught interrupt signal - cleaning up..."
	
	# Kill all background jobs forcefully
	jobs -p | xargs -r kill -9 2>/dev/null || true
	
	# Stop and remove any test containers forcefully
	# Dynamically discover all potential test containers
	while IFS= read -r DOCKERFILE_PATH; do
		DISTRO=$(basename "$(dirname "$DOCKERFILE_PATH")")
		docker kill "${DISTRO}_test_container" 2>/dev/null || true
		docker rm -f "${DISTRO}_test_container" 2>/dev/null || true
	done < <(find . -mindepth 2 -maxdepth 2 -type f -name 'Dockerfile' -printf '%p\n' 2>/dev/null || true)
	
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
TOX_PYTHON_VERSION=("py310" "py311" "py312" "py313" "py314")

# --- Script Usage and Input Validation ---

show_help() {
	cat << EOF
Usage: $0 [OPTIONS] [IMAGE_NAME]

Run Python tests in Docker containers for ezsnmp project.

Options:
  -h, --help            Show this help message and exit
  --preserve-logs       Preserve previous test logs in a timestamped folder
                        instead of deleting them

Arguments:
  IMAGE_NAME           Optional. Specify a single image tag to test only that
                       distribution (e.g., 'almalinux10_netsnmp_5.9', 
                       'archlinux_netsnmp_5.7', 'centos7_netsnmp_5.7').
                       If omitted, all distribution directories will be tested.

Examples:
  $0                                           # Test all distributions
  $0 --preserve-logs                           # Test all, preserve old logs
  $0 almalinux10_netsnmp_5.9                   # Test only AlmaLinux 10
  $0 archlinux_netsnmp_5.7 --preserve-logs     # Test Arch Linux 5.7, preserve logs

Available Distributions:
EOF
	# List available distributions by finding Dockerfiles
	while IFS= read -r DOCKERFILE_PATH; do
		DIR_NAME=$(basename "$(dirname "$DOCKERFILE_PATH")")
		echo "  - $DIR_NAME"
	done < <(find . -mindepth 2 -maxdepth 2 -type f -name 'Dockerfile' -printf '%p\n' 2>/dev/null | sort)
	exit 0
}

TARGET_IMAGE=""
PRESERVE_LOGS=0

# Parse arguments
while [ $# -gt 0 ]; do
	case $1 in
		-h|--help)
			show_help
			;;
		--preserve-logs)
			PRESERVE_LOGS=1
			shift
			;;
		*)
			if [ -z "${TARGET_IMAGE}" ]; then
				TARGET_IMAGE=$1
				shift
			else
				echo "ERROR: Unknown argument or multiple image names specified: $1"
				echo ""
				echo "Run '$0 --help' for usage information."
				exit 1
			fi
			;;
	esac
done

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
	# Test all images by finding directories in the current folder that contain a Dockerfile.
	DISTROS_TO_TEST=()
	while IFS= read -r DOCKERFILE_PATH; do
		DIR_NAME=$(basename "$(dirname "$DOCKERFILE_PATH")")
		DISTROS_TO_TEST+=("$DIR_NAME")
	done < <(find . -mindepth 2 -maxdepth 2 -type f -name 'Dockerfile' -printf '%p\n')
	echo "Mode: Testing all found images."
fi

echo "Images to test: ${DISTROS_TO_TEST[*]}"
echo "--------------------------------------------------"

# --- Handle Previous Logs ---
if [ ${PRESERVE_LOGS} -eq 1 ]; then
	# Check if there are any existing logs to preserve
	HAS_LOGS=0
	if compgen -G "*.xml" > /dev/null || compgen -G "*.txt" > /dev/null || \
	   compgen -G "../.coverage.*" > /dev/null || compgen -G "../test-outputs*.txt" > /dev/null || \
	   compgen -G "test_outputs_*/" > /dev/null; then
		HAS_LOGS=1
	fi
	
	if [ ${HAS_LOGS} -eq 1 ]; then
		TIMESTAMP=$(date +%m_%d_%y_%H_%M_%S_%3N)
		ARCHIVE_DIR="previous_results_${TIMESTAMP}"
		echo "Preserving previous logs to: ${ARCHIVE_DIR}"
		mkdir -p "${ARCHIVE_DIR}"
		[ -n "$(compgen -G "*.xml")" ] && mv -f *.xml "${ARCHIVE_DIR}/"
		[ -n "$(compgen -G "*.txt")" ] && mv -f *.txt "${ARCHIVE_DIR}/"
		[ -n "$(compgen -G "../.coverage.*")" ] && mv -f ../.coverage.* "${ARCHIVE_DIR}/"
		[ -n "$(compgen -G "../test-outputs*.txt")" ] && mv -f ../test-outputs*.txt "${ARCHIVE_DIR}/"
		[ -n "$(compgen -G "test_outputs_*/")" ] && mv -f test_outputs_*/ "${ARCHIVE_DIR}/"
		echo "Previous logs preserved."
	else
		echo "No previous logs found to preserve."
	fi
else
	echo "Removing previous logs..."
	rm -f -- *.xml *.txt ../.coverage.* ../test-outputs*.txt
	rm -rf test_outputs_*/
fi
echo "--------------------------------------------------"

# --- Test Loop ---
for DISTRO_NAME in "${DISTROS_TO_TEST[@]}"; do

	# Create output directory for this distribution
	OUTPUT_DIR="test_outputs_${DISTRO_NAME}"
	mkdir -p "${OUTPUT_DIR}"

	FULL_IMAGE_TAG="${DOCKER_REPO_PATH}:${DISTRO_NAME}-latest"
	CONTAINER_NAME="${DISTRO_NAME}_test_container"
	# The entry script path is now common across all distributions
	ENTRY_SCRIPT_PATH="/usr/local/bin/DockerEntry.sh"

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
		if ! docker pull "${FULL_IMAGE_TAG}" >/dev/null 2>&1; then
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
			/bin/bash -c "${ENTRY_SCRIPT_PATH} false & tail -f /dev/null" >/dev/null 2>&1; then
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
			echo "      * [${DISTRO_NAME}] Completed: $TOX_PY (${TOX_DURATION}s)" # 4. Copy artifacts from the container to the distribution's output folder
			if [ -f ../test-results.xml ]; then
				mv ../test-results.xml "${OUTPUT_DIR}/test-results_${CONTAINER_NAME}_${TOX_PY}.xml"
			else
				echo "      ! [${DISTRO_NAME}] Warning: test-results.xml not found for environment: $TOX_PY"
				touch "${OUTPUT_DIR}/test-results_${CONTAINER_NAME}_${TOX_PY}.xml"
			fi
			mv "../$OUTPUT_FILE" "${OUTPUT_DIR}/test-outputs_${CONTAINER_NAME}_${TOX_PY}.txt"
		done

		# 4.5. Extract snmpd logs for debugging
		echo "    - [${DISTRO_NAME}] Extracting snmpd logs..."
		docker exec "$CONTAINER_NAME" bash -c "
			if [ -d /var/log/ezsnmp ]; then
				cat /var/log/ezsnmp/snmpd.log 2>/dev/null || echo 'No snmpd.log found';
				echo '--- SNMPD ERRORS ---';
				cat /var/log/ezsnmp/snmpd_error.log 2>/dev/null || echo 'No snmpd_error.log found';
			else
				echo 'Log directory /var/log/ezsnmp not found';
			fi
		" > "${OUTPUT_DIR}/snmpd_logs_${CONTAINER_NAME}.txt" 2>&1
		echo "    - [${DISTRO_NAME}] Logs saved to: snmpd_logs_${CONTAINER_NAME}.txt"

		# 5. Cleanup container
		echo "    - [${DISTRO_NAME}] Cleaning up container"
		docker stop "$CONTAINER_NAME" 2>/dev/null
		docker rm "$CONTAINER_NAME" 2>/dev/null

		END_TIME=$(date +%s)
		TOTAL_DURATION=$((END_TIME - START_TIME))
		echo "    - [${DISTRO_NAME}] COMPLETED (Total time: ${TOTAL_DURATION}s)"
	) & # Run in background

done

# Wait for all background jobs to complete
echo ""
echo "Waiting for all distributions to complete testing..."
wait

echo "--------------------------------------------------"

echo "All specified images tested."
