#!/bin/bash

for i in 2 4 8 16; do
    python3 test_snmp_get.py "$i" process
    python3 test_snmp_get.py "$i" thread
done

for i in 2 4 8 16; do
    python3 test_snmp_walk.py "$i" process
    python3 test_snmp_walk.py "$i" thread
done

for i in 2 4 8 16; do
    python3 test_snmp_bulkwalk.py "$i" process
    python3 test_snmp_bulkwalk.py "$i" thread
done