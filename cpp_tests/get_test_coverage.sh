#!/bin/bash

# Script to configure, build, and generate coverage reports for a Meson project

# Variables
BUILD_DIR="build"
COVERAGE_DIR="${BUILD_DIR}/../coverage_html"

# Check if lcov is installed
if ! command -v lcov &> /dev/null; then
  echo "lcov is not installed. Please install it (e.g., sudo apt install lcov)."
  exit 1
fi

# Determine number of cores
if command -v nproc &> /dev/null; then
  NPROC=$(nproc)
elif command -v sysctl &> /dev/null; then
  # MacOS
  NPROC=$(sysctl -n hw.ncpu)
else
  echo "Unable to determine number of cores. Using default of 4."
  NPROC=4
fi

# Clean up previous build and coverage data
echo "Cleaning up previous build and coverage data..."
rm -rf "$BUILD_DIR"
rm -rf coverage.info

# Compile the project
echo "Compiling the project..."
mkdir -p $BUILD_DIR
meson setup $BUILD_DIR
ninja -C "$BUILD_DIR" -j $NPROC

# Generate coverage data
echo "Generating coverage data..."
ninja -C "$BUILD_DIR" test -j $NPROC

# Capture coverage data with lcov
echo "Capturing coverage data with lcov..."
lcov --capture --directory "$BUILD_DIR" --output-file coverage.info --rc geninfo_unexecuted_blocks=1 --ignore-errors mismatch

# Remove unwanted coverage data
echo "Removing unwanted coverage data..."
lcov --remove coverage.info '/usr/include/*' '*/13/bits/*' '*/13/ext/*' '*/cpp_tests/*' --output-file updated_coverage.info

# Generate HTML coverage report
echo "Generating HTML coverage report..."
genhtml -o "$COVERAGE_DIR" updated_coverage.info

# Clean up coverage info file
echo "Cleaning up coverage info file..."
rm coverage.info
rm updated_coverage.info

echo "Coverage report generated in $COVERAGE_DIR/index.html"

echo "Done."
