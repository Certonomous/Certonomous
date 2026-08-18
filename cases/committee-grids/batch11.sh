#!/bin/bash
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
cd "$R" || exit 1
while pgrep -f "bash batch6.sh|bash batch7.sh|bash batch8.sh|bash batch9.sh|bash batch10.sh" > /dev/null; do sleep 20; done
bash "$R/run_hardened_on_dpw5.sh" hybrid 120 14 >> "$R/logs/batch11.txt" 2>&1
echo "-- done hardened hybrid $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch11.txt"
bash "$R/run_hardened_on_dpw5.sh" prism 120 14 >> "$R/logs/batch11.txt" 2>&1
echo "BATCH11 COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch11.txt"
