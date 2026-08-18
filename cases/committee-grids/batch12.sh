#!/bin/bash
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
cd "$R" || exit 1
for V in trans transu1; do
  bash "$R/run_case.sh" hex "$V" compressible 2.11 120 14 >> "$R/logs/batch12.txt" 2>&1
  echo "-- done hex $V $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch12.txt"
done
echo "BATCH12 COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch12.txt"
