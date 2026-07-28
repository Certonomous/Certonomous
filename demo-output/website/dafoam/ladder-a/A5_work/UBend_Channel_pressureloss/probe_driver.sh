#!/bin/bash
set -e
source /home/dafoamuser/dafoam/loadDAFoam.sh
for pair in "0.0 base" "1e-4 p1e4" "-1e-4 m1e4" "1e-3 p1e3" "-1e-3 m1e3" "1e-2 p1e2" "-1e-2 m1e2"; do
  delta=$(echo $pair | cut -d' ' -f1)
  tag=$(echo $pair | cut -d' ' -f2)
  echo "=== PROBE tag=$tag delta=$delta ==="
  rm -rf processor*
  mpirun -np 4 --allow-run-as-root python runScript.py -task probe -probeIdx 0 -probeDelta $delta
done
