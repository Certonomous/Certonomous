#!/bin/bash
# W3 channel-M: run all five closures, serial, identical numerics.
# kOmegaSST is re-run as a serial control so the act's 6-domain 0.3041 can be
# compared against a same-numerics member rather than assumed identical.
source /usr/lib/openfoam/openfoam2606/etc/bashrc 2>/dev/null || true
ROOT=/home/ubuntu/Certonomous/demo-output/website/campaign/W3_runs
run_one () {
  cd "$ROOT/$1" || exit 1
  potentialFoam -writephi > log.potentialFoam 2>&1
  simpleFoam              > log.simpleFoam    2>&1
  echo "$1 done rc=$?" >> "$ROOT/PROGRESS"
}
: > "$ROOT/PROGRESS"
for M in kOmegaSST kEpsilon kOmega realizableKE SpalartAllmaras; do
  run_one "$M" &
done
wait
echo "ALL DONE" >> "$ROOT/PROGRESS"
