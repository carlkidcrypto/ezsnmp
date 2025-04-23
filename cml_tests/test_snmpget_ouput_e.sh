#!/bin/bash

# Log file name
LOG_FILE="snmp_ifAdminStatus.log"

# Number of iterations
ITERATIONS=100

# SNMP parameters
COMMUNITY="public"
VERSION="1"
HOST="localhost"
PORT="11161"
OID="ifAdminStatus.1"

# Clear the log file or create it if it doesn't exist
> "$LOG_FILE"

# Loop for the specified number of iterations
for i in $(seq 1 $ITERATIONS); do
    # Log the current iteration to the console
    echo "Executing iteration $i of $ITERATIONS..."

    # Run the first snmpget command and append the output to the log file
    snmpget -c "$COMMUNITY" -v "$VERSION" -O e "$HOST:$PORT" "$OID" >> "$LOG_FILE"

    # Append a newline for readability
    echo "" >> "$LOG_FILE"

    # Run the second snmpget command and append the output to the log file
    snmpget -c "$COMMUNITY" -v "$VERSION" "$HOST:$PORT" "$OID" >> "$LOG_FILE"

    # Append a newline for readability
    echo "" >> "$LOG_FILE"
done

echo "SNMP commands executed and logged to $LOG_FILE"

# Error checking: Count occurrences of specific SNMP responses in the log file
UP_COUNT=$(grep -c "IF-MIB::ifAdminStatus.1 = INTEGER: up(1)" "$LOG_FILE")
INTEGER_ONE_COUNT=$(grep -c "IF-MIB::ifAdminStatus.1 = INTEGER: 1" "$LOG_FILE")

# Display the counts
echo "Occurrences of 'IF-MIB::ifAdminStatus.1 = INTEGER: up(1)': $UP_COUNT"
echo "Occurrences of 'IF-MIB::ifAdminStatus.1 = INTEGER: 1': $INTEGER_ONE_COUNT"

# Check if there were any errors during the SNMP commands
if [[ $UP_COUNT -eq 0 && $INTEGER_ONE_COUNT -eq 0 ]]; then
    echo "Error: No valid SNMP responses found in the log file."
    exit 1
fi