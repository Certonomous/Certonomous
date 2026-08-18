#!/bin/bash
# Diagnosis ladder, take two: sequential, 14 ranks, 120 iterations, ordered so
# the hypotheses most likely to be right are tested first.
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
cd "$R" || exit 1
run() { bash "$R/run_case.sh" hybrid "$1" incompressible 2.11 120 14 >> "$R/logs/batch6.txt" 2>&1; }
for V in uncorr potinit prod potprod pcap wdpois base_sa linupV nonorth6 pcg slow combo upwind1; do
  run "$V"
  echo "-- done $V $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch6.txt"
done
echo "BATCH6 COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch6.txt"
