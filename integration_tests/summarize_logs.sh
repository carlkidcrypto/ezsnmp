#!/usr/bin/env bash
set -euo pipefail

# summarize_logs.sh
# Summarize integration test logs under test_results_<timestamp>/
# Aggregates worker counters across all logs and prints per-file + total summary.

usage() {
  cat << EOF
Usage: $(basename "$0") [RESULTS_DIR]

Summarize integration test logs produced by run_integration_tests.sh.
If RESULTS_DIR is omitted, the latest test_results_* directory is used.

Outputs a CSV-like summary with per-file counters and overall totals.

Counters:
- connection_error_counter
- usm_unknown_security_name_counter
- err_gen_ku_key_counter
- netsnmp_parse_args_error_counter
- unknown_oid_error_counter
- no_hostname_specified_error_counter
- generic_error_counter

Examples:
  $(basename "$0")
  $(basename "$0") test_results_01_15_26_19_25_36_123
EOF
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi

# Determine results directory
RESULTS_DIR="${1:-}"
if [[ -z "$RESULTS_DIR" ]]; then
  # Pick latest by mtime
  mapfile -t dirs < <(ls -1dt test_results_*/ 2>/dev/null || true)
  if [[ ${#dirs[@]} -eq 0 ]]; then
    echo "ERROR: No test_results_* directories found." >&2
    exit 1
  fi
  RESULTS_DIR="${dirs[0]%/}"
fi

if [[ ! -d "$RESULTS_DIR" ]]; then
  echo "ERROR: Directory not found: $RESULTS_DIR" >&2
  exit 1
fi

shopt -s nullglob
LOG_FILES=("$RESULTS_DIR"/*.log)
if [[ ${#LOG_FILES[@]} -eq 0 ]]; then
  echo "ERROR: No .log files found in $RESULTS_DIR" >&2
  exit 1
fi

# Print header
printf "file,test,workers,mode,connection,usm_unknown_user,ku_key_error,parse_args_error,unknown_oid,no_hostname,generic\n"

overall_connection=0
overall_usm=0
overall_ku=0
overall_parse=0
overall_oid=0
overall_nohost=0
overall_generic=0

for f in "${LOG_FILES[@]}"; do
  # Derive test, workers, mode from filename if possible
  bn=$(basename "$f")
  test="unknown"
  workers="-"
  mode="-"
  if [[ "$bn" =~ ^test_snmp_get_([0-9]+)_(process|thread)\.log$ ]]; then
    test="get"
    workers="${BASH_REMATCH[1]}"
    mode="${BASH_REMATCH[2]}"
  elif [[ "$bn" =~ ^test_snmp_walk_([0-9]+)_(process|thread)\.log$ ]]; then
    test="walk"
    workers="${BASH_REMATCH[1]}"
    mode="${BASH_REMATCH[2]}"
  elif [[ "$bn" =~ ^test_snmp_bulkwalk_([0-9]+)_(process|thread)\.log$ ]]; then
    test="bulkwalk"
    workers="${BASH_REMATCH[1]}"
    mode="${BASH_REMATCH[2]}"
  elif [[ "$bn" == "test_file_descriptors.log" ]]; then
    test="file_descriptors"
    workers="-"
    mode="-"
  fi

  # Parse counters case-insensitively and sum across workers
  read -r connection usm ku parse oid nohost generic < <(
    awk '
      BEGIN { c=0; u=0; k=0; p=0; o=0; h=0; g=0; }
      {
        line=tolower($0);
        if (match(line, /connection_error_counter:[[:space:]]*([0-9]+)/, m)) c+=m[1];
        else if (match(line, /usm_unknown_security_name_counter:[[:space:]]*([0-9]+)/, m)) u+=m[1];
        else if (match(line, /err_gen_ku_key_counter:[[:space:]]*([0-9]+)/, m)) k+=m[1];
        else if (match(line, /netsnmp_parse_args_error_counter:[[:space:]]*([0-9]+)/, m)) p+=m[1];
        else if (match(line, /unknown_oid_error_counter:[[:space:]]*([0-9]+)/, m)) o+=m[1];
        else if (match(line, /no_hostname_specified_error_counter:[[:space:]]*([0-9]+)/, m)) h+=m[1];
        else if (match(line, /generic_error_counter:[[:space:]]*([0-9]+)/, m)) g+=m[1];
      }
      END { printf("%d %d %d %d %d %d %d\n", c,u,k,p,o,h,g); }
    ' "$f"
  )

  (( overall_connection += connection ))
  (( overall_usm += usm ))
  (( overall_ku += ku ))
  (( overall_parse += parse ))
  (( overall_oid += oid ))
  (( overall_nohost += nohost ))
  (( overall_generic += generic ))

  printf "%s,%s,%s,%s,%d,%d,%d,%d,%d,%d,%d\n" \
    "$bn" "$test" "$workers" "$mode" \
    "$connection" "$usm" "$ku" "$parse" "$oid" "$nohost" "$generic"

done

# Print totals row
printf "TOTAL,all,all,all,%d,%d,%d,%d,%d,%d,%d\n" \
  "$overall_connection" "$overall_usm" "$overall_ku" "$overall_parse" "$overall_oid" "$overall_nohost" "$overall_generic"
