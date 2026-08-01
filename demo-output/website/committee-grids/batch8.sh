#!/bin/bash
# The relaxation axis, queued behind batch6 and batch7.
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
cd "$R" || exit 1
while pgrep -f "bash batch6.sh|bash batch7.sh" > /dev/null; do sleep 20; done
for V in crawl crawl3 crawl2; do
  bash "$R/run_case.sh" hybrid "$V" incompressible 2.11 120 14 >> "$R/logs/batch8.txt" 2>&1
  echo "-- done $V $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch8.txt"
done
echo "BATCH8 COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch8.txt"
