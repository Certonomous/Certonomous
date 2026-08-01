#!/bin/bash
# The two potential-flow-initialised variants, re-run after the missing
# div(div(phi,U)) scheme entry was added. Queued to start only once batch6 has
# finished so the box is not shared.
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
cd "$R" || exit 1
while pgrep -f "bash batch6.sh" > /dev/null; do sleep 20; done
for V in potinit potprod; do
  bash "$R/run_case.sh" hybrid "$V" incompressible 2.11 120 14 >> "$R/logs/batch7.txt" 2>&1
  echo "-- done $V $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch7.txt"
done
echo "BATCH7 COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch7.txt"
