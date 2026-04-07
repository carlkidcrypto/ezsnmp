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

# The script now accepts 0 or more arguments (optional image names).
# No arguments = test all, one or more arguments = test only those specified
if [ $# -eq 1 ] && [ "$1" == "--help" ]; then
	echo "Usage: $0 [IMAGE_NAME1] [IMAGE_NAME2] ..."
	echo ""
	echo "  [IMAGE_NAMEx]: Optional. Specify one or more image tags (e.g., 'centos7_netsnmp_5.7 archlinux_netsnmp_5.7')"
	echo "                 to test only those distributions."
	echo "                 If omitted, all distribution directories will be tested."
	echo ""
	echo "Examples:"
	echo "  $0                                    # Test all distributions"
	echo "  $0 centos7_netsnmp_5.7                # Test only CentOS 7"
	echo "  $0 centos7_netsnmp_5.7 archlinux_netsnmp_5.7  # Test only net-snmp 5.7 containers"
	exit 0
fi

# --- Determine Images to Test ---

# We assume the images are tagged the same as the folder names in the current directory.
if [ $# -gt 0 ]; then
	# Test only the specified images
	DISTROS_TO_TEST=()
	for TARGET_IMAGE in "$@"; do
		if [ ! -d "${TARGET_IMAGE}" ]; then
			echo "ERROR: Specified image directory '${TARGET_IMAGE}' does not exist in the current folder."
			echo "Available directories:"
			ls -d */ 2>/dev/null | grep -v "^cache/" | sed 's|/||' || echo "  (none found)"
			exit 1
		fi
		DISTROS_TO_TEST+=("${TARGET_IMAGE}")
	done
	echo "Mode: Testing specified images: ${DISTROS_TO_TEST[*]}"
else
	# Test all images by finding directories in the current folder that contain a Dockerfile.
	DISTROS_TO_TEST=()
	while IFS= read -r DOCKERFILE_PATH; do
		DIR_NAME=$(basename "$(dirname "$DOCKERFILE_PATH")")
		DISTROS_TO_TEST+=("$DIR_NAME")
	done < <(find . -mindepth 2 -maxdepth 2 -type f -name 'Dockerfile' -print)
	echo "Mode: Testing all found images."
fi

echo "Images to test: ${DISTROS_TO_TEST[*]}"
echo "--------------------------------------------------"

# Clean any previous top-level outputs
rm -f -- *.xml *.txt *.info

# --- Test Loop ---
for DISTRO_NAME in "${DISTROS_TO_TEST[@]}"; do

	FULL_IMAGE_TAG="${DOCKER_REPO_PATH}:${DISTRO_NAME}-latest"
	CONTAINER_NAME="${DISTRO_NAME}_test_container"
	# The entry script path is now common across all distributions
	ENTRY_SCRIPT_PATH="/usr/local/bin/DockerEntry.sh"

	echo ">>> Running tests for distribution: ${DISTRO_NAME}"
	echo "    - Target Image: ${FULL_IMAGE_TAG}"

	# Cleanup any existing container with the same name
	if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
		docker stop "$CONTAINER_NAME"
	fi
	docker rm -f "$CONTAINER_NAME"

	# 1. Pull the image
	echo "    - Pulling image..."
	GHCR_IMAGE_TAG="ghcr.io/${DOCKER_REPO_PATH}:${DISTRO_NAME}-latest"
	if docker pull "${FULL_IMAGE_TAG}"; then
		echo "    - Pulled from Docker Hub: ${FULL_IMAGE_TAG}"
	elif docker pull "${GHCR_IMAGE_TAG}"; then
		echo "    - Docker Hub unavailable; pulled from GHCR: ${GHCR_IMAGE_TAG}"
		docker tag "${GHCR_IMAGE_TAG}" "${FULL_IMAGE_TAG}"
	else
		echo "ERROR: Docker pull failed for ${DISTRO_NAME} from both Docker Hub and GHCR. Skipping tests."
		continue
	fi

	# 2. Start the container
	echo "    - Starting container: ${CONTAINER_NAME} and daemon..."
	echo "      * Using host source path: $HOST_SOURCE_PATH"
	# The command runs the entry script in the background and uses 'tail' as the foreground process
	if ! docker run -d \
		--name "${CONTAINER_NAME}" \
		-v "$HOST_SOURCE_PATH:$CONTAINER_WORK_DIR" \
		-v "$HOST_SOURCE_PATH/ezsnmp/src:/ezsnmp/src:ro" \
		-v "$HOST_SOURCE_PATH/ezsnmp/include:/ezsnmp/include:ro" \
		"${FULL_IMAGE_TAG}" \
		/bin/bash -c "${ENTRY_SCRIPT_PATH} false & tail -f /dev/null"; then
		echo "ERROR: Docker run failed for ${DISTRO_NAME}. Skipping tests."
		continue
	fi

	# 3. Run cpp tests using meson
	echo "    - Executing meson tests..."
	docker exec -t -e ASAN_OPTIONS='halt_on_error=0' -e UBSAN_OPTIONS='halt_on_error=0' -e MSAN_OPTIONS='halt_on_error=0' "$CONTAINER_NAME" bash -c "
		cd /ezsnmp/cpp_tests;
		rm -drf build/ *.info *.txt *.xml;
		# Set PKG_CONFIG_PATH for systems with netsnmp in non-standard location (e.g., archlinux_netsnmp_5.8)
		export PKG_CONFIG_PATH=\"/usr/lib/pkgconfig:/usr/local/lib/pkgconfig:\${PKG_CONFIG_PATH}\"
		# Ensure a known-good meson (from PyPI) is used instead of the system-installed one.
		# On Arch Linux the pacman meson uses '#!/usr/bin/env python3' which resolves to the
		# venv Python 3.14 (injected via ENV PATH in the Dockerfile). That custom-built Python
		# cannot find the pacman meson site-packages and segfaults. Installing meson via pip
		# puts /opt/venv/bin/meson first on PATH, which runs cleanly under the venv Python.
		pip install --quiet --upgrade 'meson>=1.3,<2' 2>&1 || true;
		if ! meson setup build/ -Dstrict_warnings=true -Dcheck_unreachable_code=true -Dwarning_level=3 -Dwerror=true; then
		  echo 'Meson strict options not supported in this container; retrying with portable warning flags only.';
		  rm -rf build/;
		  meson setup build/ -Dwarning_level=3 -Dwerror=true;
		fi;
		ninja -C build/ -j \$(nproc); 
		GTEST_OUTPUT='xml:/ezsnmp/cpp_tests/test-results.xml' meson test -C build/ --verbose > test-outputs.txt 2>&1;
		
		# Coverage collection: prefer geninfo with explicit ignore-errors, then fall back to lcov.
		# Use version-agnostic options to bypass mismatched lines/inconsistent gcov output across distros.
		# The entire fallback chain is wrapped in a group and piped through grep -v to suppress
		# known-harmless but extremely noisy warnings on legacy containers (e.g. CentOS 7 devtoolset-11),
		# specifically the thousands of lines about devtoolset system-header .gcov entries that geninfo
		# tries to match back to .gcno records, and 'Overlong record' gcno format quirks.
		# Run collection from build/ so relative source paths like ../../ezsnmp/src/... resolve correctly
		# on older lcov/geninfo versions that do not support extra path remap options.
		# Wrapping with '|| true' ensures the group always exits 0 so filtering doesn't mask real failures.
		{
		  (cd build && geninfo . --output-filename ../coverage.info \
		         --base-directory /ezsnmp/cpp_tests/build \
		         --ignore-errors mismatch \
		         --ignore-errors inconsistent \
		         --ignore-errors gcov \
		         --ignore-errors source \
		         --rc geninfo_unexecuted_blocks=1 \
		         --rc geninfo_gcov_all_blocks=0) 2>&1 || \
		  (cd build && lcov --capture --directory . --output-file ../coverage.info \
		       --base-directory /ezsnmp/cpp_tests/build \
		       --ignore-errors mismatch,inconsistent,gcov,usage) 2>&1 || \
		  (cd build && lcov --capture --directory . --output-file ../coverage.info \
		       --base-directory /ezsnmp/cpp_tests/build) 2>&1 || true
		} | grep -v -E \
		    'cannot find an entry for.*\.gcov in \.gcno file|Overlong record at end of file'
		
		# Ensure coverage.info exists for next step
		if [ ! -f coverage.info ]; then
		  touch coverage.info
		fi

		normalize_coverage_paths() {
		  sed -i -E 's#^SF:(\./)?\.\./ezsnmp/src/#SF:/ezsnmp/ezsnmp/src/#' "$1" 2>/dev/null || true
		}

		# Some older gcov/lcov combinations emit relative SF paths; normalize them for Codecov.
		normalize_coverage_paths coverage.info
		
		# Strip system/third-party paths if coverage exists and has content
		if [ -f coverage.info ] && [ -s coverage.info ]; then
		  lcov --remove coverage.info '/usr/*' '/opt/*' '*/bits/*' '*/ext/*' '*/gtest/*' '*/googletest/*' '*/site-packages/*' --output-file updated_coverage.info 2>/dev/null || cp coverage.info updated_coverage.info
		else
		  touch updated_coverage.info
		fi

		normalize_coverage_paths updated_coverage.info
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

	# 4.5. Extract snmpd logs for debugging
	echo "    - Extracting snmpd logs..."
	docker exec "$CONTAINER_NAME" bash -c "
		if [ -d /var/log/ezsnmp ]; then
			cat /var/log/ezsnmp/snmpd.log 2>/dev/null || echo 'No snmpd.log found';
			echo '--- SNMPD ERRORS ---';
			cat /var/log/ezsnmp/snmpd_error.log 2>/dev/null || echo 'No snmpd_error.log found';
		else
			echo 'Log directory /var/log/ezsnmp not found';
		fi
	" > "${OUT_DIR}/snmpd_logs.txt" 2>&1
	echo "    - Logs saved to: ${OUT_DIR}/snmpd_logs.txt"

	# 5. Cleanup container
	echo "    - Cleaning up container: $CONTAINER_NAME"
	docker stop "$CONTAINER_NAME"
	docker rm "$CONTAINER_NAME"

	echo "--------------------------------------------------"

done

echo "All specified images tested."