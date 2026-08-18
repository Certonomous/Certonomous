#!/bin/bash
# Requeue of the two variants whose first attempt aborted in setup rather than
# in the physics: wdpois (missing yPsi solver entry) and nothing else.
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
cd "$R" || exit 1
while pgrep -f "bash batch6.sh|bash batch7.sh|bash batch8.sh" > /dev/null; do sleep 20; done
bash "$R/run_case.sh" hybrid wdpois incompressible 2.11 120 14 >> "$R/logs/batch9.txt" 2>&1
echo "BATCH9 COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch9.txt"
