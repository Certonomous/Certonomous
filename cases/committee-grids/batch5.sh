#!/bin/bash
# Diagnosis ladder, sequential at 14 ranks, 120 iterations.
#
# 120 is not arbitrary: it is the exact length of the HLPW6 hardened first-order
# run that is this lab's only completed committee-grid solve
# (hlpw6-memory-probe/logs/HLPW6_solve_hardened.log, 04:50:45Z), so "survives
# 120" is measured against a criterion that already exists rather than one
# invented for this ladder. The baseline dies at iteration 11.
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
cd "$R" || exit 1
run() { bash "$R/run_case.sh" hybrid "$1" incompressible 2.11 120 14 >> "$R/logs/batch5.txt" 2>&1; }
for V in limlin uncorr prod linupV base_sa pcg slow nonorth6 combo upwind1; do run "$V"; done
echo "BATCH5 COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch5.txt"
