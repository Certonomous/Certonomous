#!/bin/bash
# Core-minute cost of the real HLPW6 TC1 coarse grid vs MPI rank count.
# A core-minute is wall-seconds x ranks / 60 (COMPUTE_BUDGET_CHARTER.md S2), so
# the rank count that minimises wall time is not necessarily the one that
# minimises the charge. This measures both.
set -u
BASE=/home/ubuntu/certonomous-runs/hlpw6-memory-probe
CASE=$BASE/case_HLPW6
OUT=$BASE/logs/measurements.jsonl
IT=${1:-40}

sed -i "s/^endTime         [0-9]*;/endTime         $IT;/" "$CASE/system/controlDict"

for NR in 1 4 8 14; do
  rm -rf "$CASE"/processor* "$CASE"/[1-9]* 2>/dev/null
  if [ "$NR" = 1 ]; then
    CMD="simpleFoam"
  else
    sed -i "s/^numberOfSubdomains [0-9]*;/numberOfSubdomains $NR;/" "$CASE/system/decomposeParDict"
    openfoam2606 -c "cd $CASE && decomposePar -force" > /dev/null 2>&1 || exit 1
    CMD="mpirun --oversubscribe -np $NR simpleFoam -parallel"
  fi
  python3 "$BASE/memwatch.py" --tag "HLPW6/ranksweep_np${NR}_${IT}it" --out "$OUT" \
      --timeout 7200 --log "$BASE/logs/HLPW6_ranksweep_np${NR}.log" \
      -- openfoam2606 -c "cd $CASE && $CMD"
done
rm -rf "$CASE"/processor* "$CASE"/[1-9]* 2>/dev/null
echo "=== rank sweep done ==="
