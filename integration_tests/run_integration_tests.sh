#!/bin/bash

# --- Script Usage and Input Validation ---

show_help() {
	cat << EOF
Usage: $0 [OPTIONS]

Run integration tests for ezsnmp project.

Options:
  -h, --help            Show this help message and exit
  --preserve-logs       Preserve previous test logs in a timestamped folder
                        instead of deleting them

Examples:
  $0                    # Run all integration tests
  $0 --preserve-logs    # Run all tests and preserve old logs

Available Tests:
  - test_file_descriptors.py     File descriptor handling tests
  - test_snmp_get.py             SNMP get operations (2,4,8,16,32 workers)
  - test_snmp_walk.py            SNMP walk operations (2,4,8,16,32 workers)
  - test_snmp_bulkwalk.py        SNMP bulkwalk operations (2,4,8,16,32 workers)

EOF
	exit 0
}

PRESERVE_LOGS=0

# Parse command line arguments
while [[ $# -gt 0 ]]; do
	case $1 in
		-h|--help)
			show_help
			;;
		--preserve-logs)
			PRESERVE_LOGS=1
			shift
			;;
		*)
			echo "ERROR: Unknown option: $1"
			echo ""
			echo "Run '$0 --help' for usage information."
			exit 1
			;;
	esac
done

# --- Handle Previous Logs ---
if [ ${PRESERVE_LOGS} -eq 1 ]; then
	# Check if there are any existing test_results directories to preserve
	HAS_LOGS=0
	if compgen -G "test_results_*/" > /dev/null; then
		HAS_LOGS=1
	fi
	
	if [ ${HAS_LOGS} -eq 1 ]; then
		echo "Preserving previous logs..."
		for dir in test_results_*; do
			if [ -d "$dir" ]; then
				# Extract timestamp from directory name
				OLD_TIMESTAMP=$(echo "$dir" | sed 's/test_results_//')
				# Create new directory name with previous_results prefix
				PREV_DIR="previous_results_${OLD_TIMESTAMP}"
				echo "  - Moving: $dir -> $PREV_DIR"
				mv "$dir" "$PREV_DIR"
			fi
		done
		echo "Previous logs preserved."
	else
		echo "No previous logs found to preserve."
	fi
else
	echo "Removing previous logs..."
	rm -rf test_results_*/
fi
echo "--------------------------------------------------"

# --- Create output directory with timestamp ---
TIMESTAMP=$(date +%m_%d_%y_%H_%M_%S_%3N)
OUTPUT_DIR="test_results_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "Starting Integration Tests"
echo "Output directory: $OUTPUT_DIR"
echo "Started at: $(date)"
echo "=========================================="

# --- Run file descriptor tests ---
echo ""
echo "[$(date +%H:%M:%S)] Running file descriptor tests..."
START_TIME=$(date +%s)
python3 test_file_descriptors.py 2>&1 | tee "$OUTPUT_DIR/test_file_descriptors.log"
TEST_EXIT_CODE=$?
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

if [ $TEST_EXIT_CODE -eq 0 ]; then
	echo "[$(date +%H:%M:%S)] PASS: File descriptor tests completed successfully (${DURATION}s)"
else
	echo "[$(date +%H:%M:%S)] FAIL: File descriptor tests failed (${DURATION}s)"
fi

# --- Run SNMP get tests ---
echo ""
echo "[$(date +%H:%M:%S)] Running SNMP get tests..."
for i in 2 4 8 16 32; do
	echo "  - [$(date +%H:%M:%S)] test_snmp_get.py with $i processes"
	START_TIME=$(date +%s)
	python3 test_snmp_get.py "$i" process 2>&1 | tee "$OUTPUT_DIR/test_snmp_get_${i}_process.log"
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME))
	echo "    Completed in ${DURATION}s"
	
	echo "  - [$(date +%H:%M:%S)] test_snmp_get.py with $i threads"
	START_TIME=$(date +%s)
	python3 test_snmp_get.py "$i" thread 2>&1 | tee "$OUTPUT_DIR/test_snmp_get_${i}_thread.log"
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME))
	echo "    Completed in ${DURATION}s"
done
echo "[$(date +%H:%M:%S)] COMPLETED: SNMP get tests"

# --- Run SNMP walk tests ---
echo ""
echo "[$(date +%H:%M:%S)] Running SNMP walk tests..."
for i in 2 4 8 16 32; do
	echo "  - [$(date +%H:%M:%S)] test_snmp_walk.py with $i processes"
	START_TIME=$(date +%s)
	python3 test_snmp_walk.py "$i" process 2>&1 | tee "$OUTPUT_DIR/test_snmp_walk_${i}_process.log"
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME))
	echo "    Completed in ${DURATION}s"
	
	echo "  - [$(date +%H:%M:%S)] test_snmp_walk.py with $i threads"
	START_TIME=$(date +%s)
	python3 test_snmp_walk.py "$i" thread 2>&1 | tee "$OUTPUT_DIR/test_snmp_walk_${i}_thread.log"
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME))
	echo "    Completed in ${DURATION}s"
done
echo "[$(date +%H:%M:%S)] COMPLETED: SNMP walk tests"

# --- Run SNMP bulkwalk tests ---
echo ""
echo "[$(date +%H:%M:%S)] Running SNMP bulkwalk tests..."
for i in 2 4 8 16 32; do
	echo "  - [$(date +%H:%M:%S)] test_snmp_bulkwalk.py with $i processes"
	START_TIME=$(date +%s)
	python3 test_snmp_bulkwalk.py "$i" process 2>&1 | tee "$OUTPUT_DIR/test_snmp_bulkwalk_${i}_process.log"
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME))
	echo "    Completed in ${DURATION}s"
	
	echo "  - [$(date +%H:%M:%S)] test_snmp_bulkwalk.py with $i threads"
	START_TIME=$(date +%s)
	python3 test_snmp_bulkwalk.py "$i" thread 2>&1 | tee "$OUTPUT_DIR/test_snmp_bulkwalk_${i}_thread.log"
	END_TIME=$(date +%s)
	DURATION=$((END_TIME - START_TIME))
	echo "    Completed in ${DURATION}s"
done
echo "[$(date +%H:%M:%S)] COMPLETED: SNMP bulkwalk tests"

echo ""
echo "=========================================="
echo "All Integration Tests Completed"
echo "Ended at: $(date)"
echo "Results saved to: $OUTPUT_DIR"
echo "=========================================="