#!/bin/bash
#
# Generate Test Reports for ezsnmp Docker Container Tests
# This script analyzes all test output files and generates a comprehensive report
#

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}"
REPORT_FILE="${OUTPUT_DIR}/test_summary_report_$(date +%Y%m%d_%H%M%S).txt"

# Dynamically discover all test_outputs directories and Python versions
discover_containers() {
    local containers=()
    for dir in "${OUTPUT_DIR}"/test_outputs_*; do
        if [[ -d "$dir" ]]; then
            local container_name=$(basename "$dir" | sed 's/^test_outputs_//')
            containers+=("$container_name")
        fi
    done
    printf '%s\n' "${containers[@]}"
}

discover_python_versions() {
    local container="$1"
    local versions=()
    local output_dir="${OUTPUT_DIR}/test_outputs_${container}"
    
    for file in "${output_dir}"/test-outputs_*_test_container_py*.txt; do
        if [[ -f "$file" ]]; then
            # Extract version from filename (e.g., py310, py311, etc.)
            local version=$(basename "$file" | sed -E 's/.*_test_container_(py[0-9]+)\.txt/\1/')
            versions+=("$version")
        fi
    done
    
    printf '%s\n' "${versions[@]}" | sort -u
}

# Discover containers and Python versions
declare -a CONTAINERS
mapfile -t CONTAINERS < <(discover_containers)

if [[ ${#CONTAINERS[@]} -eq 0 ]]; then
    echo "Error: No test_outputs directories found in ${OUTPUT_DIR}"
    exit 1
fi

# Function to print section header
print_header() {
    local title="$1"
    echo ""
    echo "========================================================================"
    echo "  ${title}"
    echo "========================================================================"
    echo ""
}

# Function to analyze a single test output file
analyze_test_file() {
    local file="$1"
    local container="$2"
    local pyver="$3"
    
    if [[ ! -f "$file" ]]; then
        echo "    [MISSING] Test output not found"
        return 1
    fi
    
    # Check for build failures
    if grep -q "error: subprocess-exited-with-error" "$file" 2>/dev/null; then
        echo -e "    ${RED}[BUILD FAILED]${NC} Compilation error"
        grep -A 2 "error:" "$file" | head -5 | sed 's/^/        /'
        return 1
    fi
    
    # Check for segfaults/crashes
    if grep -q "Fatal Python error: Segmentation fault\|Fatal Python error: Aborted" "$file" 2>/dev/null; then
        echo -e "    ${RED}[CRASH]${NC} Fatal Python error (segfault/abort)"
        return 1
    fi
    
    # Extract test summary
    local passed=$(grep -oP '\d+(?= passed)' "$file" 2>/dev/null | tail -1)
    local failed=$(grep -oP '\d+(?= failed)' "$file" 2>/dev/null | tail -1)
    local skipped=$(grep -oP '\d+(?= skipped)' "$file" 2>/dev/null | tail -1)
    local errors=$(grep -oP '\d+(?= errors)' "$file" 2>/dev/null | tail -1)
    
    # Determine status
    if [[ -n "$failed" ]] && [[ "$failed" -gt 0 ]]; then
        echo -e "    ${RED}[FAILED]${NC} Passed: ${passed:-0}, Failed: ${failed}, Skipped: ${skipped:-0}, Errors: ${errors:-0}"
        return 1
    elif [[ -n "$errors" ]] && [[ "$errors" -gt 0 ]]; then
        echo -e "    ${YELLOW}[ERRORS]${NC} Passed: ${passed:-0}, Failed: ${failed:-0}, Skipped: ${skipped:-0}, Errors: ${errors}"
        return 1
    elif [[ -n "$passed" ]] && [[ "$passed" -gt 0 ]]; then
        echo -e "    ${GREEN}[PASSED]${NC} Passed: ${passed}, Skipped: ${skipped:-0}"
        return 0
    else
        echo -e "    ${YELLOW}[UNKNOWN]${NC} Unable to parse test results"
        return 1
    fi
}

# Function to analyze snmpd logs
analyze_snmpd_logs() {
    local log_file="$1"
    
    if [[ ! -f "$log_file" ]]; then
        echo "  [MISSING] snmpd log not found"
        return 1
    fi
    
    local version=$(grep -oP "NET-SNMP version:\s+\K[\d\.]+" "$log_file" 2>/dev/null | head -1)
    echo "  NET-SNMP Version: ${version:-UNKNOWN}"
    
    # Check for errors
    local error_section=$(sed -n '/--- SNMPD ERRORS ---/,/---/p' "$log_file" 2>/dev/null)
    if [[ -n "$error_section" ]] && [[ "$error_section" != *"---"* ]]; then
        echo -e "  ${RED}[ERRORS FOUND]${NC}"
        echo "$error_section" | head -10 | sed 's/^/    /'
    else
        echo -e "  ${GREEN}[NO ERRORS]${NC}"
    fi
}

# Main report generation
generate_report() {
    local output_file="$1"
    
    # Redirect all output to both console and file
    {
        print_header "ezsnmp Docker Container Test Report"
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Directory: ${OUTPUT_DIR}"
        
        print_header "Summary by Container"
        
        local total_passed=0
        local total_failed=0
        
        for container in "${CONTAINERS[@]}"; do
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo -e "${BLUE}Container: ${container}${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            
            local output_dir="${OUTPUT_DIR}/test_outputs_${container}"
            
            # Check snmpd logs
            echo ""
            echo "SNMPD Status:"
            analyze_snmpd_logs "${output_dir}/snmpd_logs_${container}_test_container.txt"
            
            # Discover Python versions for this container
            local -a python_versions
            mapfile -t python_versions < <(discover_python_versions "$container")
            
            # Check test results for each Python version
            echo ""
            echo "Test Results:"
            local container_passed=0
            local container_failed=0
            
            for pyver in "${python_versions[@]}"; do
                local test_file="${output_dir}/test-outputs_${container}_test_container_${pyver}.txt"
                echo ""
                echo "  Python ${pyver}:"
                if analyze_test_file "$test_file" "$container" "$pyver"; then
                    ((container_passed++))
                else
                    ((container_failed++))
                fi
            done
            
            echo ""
            echo "Container Summary: ${container_passed}/${#python_versions[@]} Python versions passed"
            
            if [[ $container_passed -eq ${#python_versions[@]} ]]; then
                echo -e "${GREEN}✓ All tests passed${NC}"
                ((total_passed++))
            else
                echo -e "${RED}✗ Some tests failed${NC}"
                ((total_failed++))
            fi
        done
        
        print_header "Overall Summary"
        echo "Total Containers: ${#CONTAINERS[@]}"
        echo -e "${GREEN}Fully Passing:${NC} ${total_passed}"
        echo -e "${RED}With Failures:${NC} ${total_failed}"
        
        print_header "Issues Found"
        
        echo ""
        echo "1. RockyLinux 9 + NetSNMP 5.9:"
        echo "   - BUILD FAILURE: 'netsnmp_cleanup_session' not declared in headers"
        echo "   - Location: ezsnmp/src/net-snmp-5.9-final-patched/snmpbulkget.cpp:256"
        echo "   - Root cause: RockyLinux 9's net-snmp-devel package (5.9.1) missing header"
        echo "   - Note: Function works in AlmaLinux 10 (5.9.4.pre2) and ArchLinux (5.9)"
        echo "   - Fix: Build NetSNMP from source OR make function call conditional"
        
        echo ""
        echo "2. ArchLinux + NetSNMP 5.7:"
        echo "   - RUNTIME CRASH: Segmentation fault during test execution"
        echo "   - Likely: Memory corruption issues with older NetSNMP version"
        
        echo ""
        echo "3. ArchLinux + NetSNMP 5.8:"
        echo "   - TEST FAILURES: 289 failed tests"
        echo "   - Likely: API incompatibilities with NetSNMP 5.8"
        
        print_header "Recommendations"
        
        echo "1. Fix RockyLinux 9 netsnmp_cleanup_session issue:"
        echo "   Option A: Build NetSNMP 5.9.4 from source in Dockerfile"
        echo "   Option B: Add conditional compilation (#ifdef) for the function"
        echo "   Option C: Wait for RockyLinux to fix their net-snmp-devel package"
        
        echo ""
        echo "2. NetSNMP 5.7 compatibility:"
        echo "   - Consider dropping support or investigating memory management issues"
        
        echo ""
        echo "3. NetSNMP 5.8 compatibility:"
        echo "   - Investigate API changes between 5.7 and 5.9"
        
        print_header "Report Complete"
        
    } 2>&1 | tee "$output_file"
}

# Main execution
main() {
    echo "Starting test report generation..."
    echo "Output will be saved to: ${REPORT_FILE}"
    echo ""
    
    generate_report "$REPORT_FILE"
    
    echo ""
    echo "Report saved to: ${REPORT_FILE}"
}

main "$@"
