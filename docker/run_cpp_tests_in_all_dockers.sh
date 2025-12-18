#!/bin/bash -e

# Formatting `sudo apt install shfmt && shfmt -w run_cpp_tests_in_all_dockers.sh`
# Try to fix docker socket permissions, but don't fail if we can't
sudo chown "$USER" /var/run/docker.sock 2>/dev/null || true

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

# --- Test Loop ---
# Clean any previous top-level outputs
rm -f -- *.xml *.txt *.info
for DISTRO_NAME in "${DISTROS_TO_TEST[@]}"; do

	FULL_IMAGE_TAG="${DOCKER_REPO_PATH}:${DISTRO_NAME}-latest"
	CONTAINER_NAME="${DISTRO_NAME}_test_container"
	# The entry script path must be adjusted for the container mount, which is always /ezsnmp/docker/[distro]/...
	ENTRY_SCRIPT_PATH="/ezsnmp/docker/${DISTRO_NAME}/DockerEntry.sh"

	echo ">>> Running tests for distribution: ${DISTRO_NAME}"
	echo "    - Target Image: ${FULL_IMAGE_TAG}"

	# Cleanup any existing container with the same name
	if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
		docker stop "$CONTAINER_NAME"
	fi
	docker rm -f "$CONTAINER_NAME"

	# 1. Pull the image
	echo "    - Pulling image..."
	if ! docker pull "${FULL_IMAGE_TAG}"; then
		echo "ERROR: Docker pull failed for ${DISTRO_NAME}. Skipping tests."
		continue
	fi

	# 2. Start the container
	echo "    - Starting container: ${CONTAINER_NAME} and daemon..."
	echo "      * Using host source path: $HOST_SOURCE_PATH"
	# The command runs the entry script in the background and uses 'tail' as the foreground process
	if ! docker run -d \
		--name "${CONTAINER_NAME}" \
		-v "$HOST_SOURCE_PATH:$CONTAINER_WORK_DIR" \
		"${FULL_IMAGE_TAG}" \
		/bin/bash -c "${ENTRY_SCRIPT_PATH} false & tail -f /dev/null"; then
		echo "ERROR: Docker run failed for ${DISTRO_NAME}. Skipping tests."
		continue
	fi

	# 3. Run cpp tests using meson
	echo "    - Executing meson tests..."
	docker exec -t "$CONTAINER_NAME" bash -c "
		cd /ezsnmp/cpp_tests;
		rm -drf build/ *.info *.txt *.xml;
		# Set PKG_CONFIG_PATH for systems with netsnmp in non-standard location (e.g., archlinux_netsnmp_5.8)
		export PKG_CONFIG_PATH=\"/usr/lib/pkgconfig:/usr/local/lib/pkgconfig:\${PKG_CONFIG_PATH}\"
		meson setup build/; 
		ninja -C build/ -j \$(nproc); 
		GTEST_OUTPUT='xml:/ezsnmp/cpp_tests/test-results.xml' meson test -C build/ > test-outputs.txt 2>&1;
		# Coverage collection: tolerate lcov option differences across distros
		LCOV_BASE=\"lcov --capture --directory build/ --output-file coverage.info --rc geninfo_unexecuted_blocks=1\"
		\${LCOV_BASE} --ignore-errors inconsistent,empty,mismatch || \${LCOV_BASE} --ignore-errors empty || \${LCOV_BASE} || true
		if [ -f coverage.info ]; then
			lcov --remove coverage.info '*/bits/*' '*/ext/*' --output-file updated_coverage.info --ignore-errors unused,empty,mismatch || cp coverage.info updated_coverage.info
		fi
		exit 0;
	"

	# 4. Copy artifacts from the container to host into per-distro folder
	OUT_DIR="./test_outputs_${DISTRO_NAME}"
	mkdir -p "$OUT_DIR"
	rm -f "${OUT_DIR}"/*.xml "${OUT_DIR}"/*.txt "${OUT_DIR}"/*.info 2>/dev/null || true

	echo "    - Saving artifacts to ${OUT_DIR}"
	if [ -f ../cpp_tests/test-results.xml ]; then
		mv ../cpp_tests/test-results.xml "${OUT_DIR}/test-results.xml"
	else
		echo "      ! Warning: test-results.xml not found for $CONTAINER_NAME"
		touch "${OUT_DIR}/test-results.xml"
	fi

	if [ -f ../cpp_tests/test-outputs.txt ]; then
		mv ../cpp_tests/test-outputs.txt "${OUT_DIR}/test-outputs.txt"
	else
		echo "      ! Warning: test-outputs.txt not found for $CONTAINER_NAME"
		touch "${OUT_DIR}/test-outputs.txt"
	fi

	if [ -f ../cpp_tests/updated_coverage.info ]; then
		mv ../cpp_tests/updated_coverage.info "${OUT_DIR}/lcov_coverage.info"
	else
		echo "      ! Warning: updated_coverage.info not found for $CONTAINER_NAME"
		touch "${OUT_DIR}/lcov_coverage.info"
	fi

	# 5. Cleanup container
	echo "    - Cleaning up container: $CONTAINER_NAME"
	docker stop "$CONTAINER_NAME"
	docker rm "$CONTAINER_NAME"

	echo "--------------------------------------------------"

done

echo "All specified images tested."
