#!/bin/bash
# Diagnosis ladder. Order is deliberate: the two controls that test the
# mechanism (hex, prism -- same nodes, different topology) come first, then the
# single-axis numerics departures in the order they were predicted to matter.
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
cd "$R" || exit 1
run() { bash "$R/run_case.sh" "$@" >> "$R/logs/batch1.txt" 2>&1; }

run hex    base      incompressible 2.11 200 14
run prism  base      incompressible 2.11 200 14
run hybrid nonorth2  incompressible 2.11 200 14
run hybrid limlin    incompressible 2.11 200 14
run hybrid linupV    incompressible 2.11 200 14
run hybrid pcg       incompressible 2.11 200 14
run hybrid slow      incompressible 2.11 200 14
run hybrid upwind1   incompressible 2.11 200 14
echo "BATCH1 COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch1.txt"
