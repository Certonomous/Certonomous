#!/bin/bash
# HLPW6 feasibility probe: measured memory + throughput ladder for the
# OpenFOAM v2606 RANS stack, on the same box that would run the workshop case.
# Usage: run_ladder.sh <tagbase> <nx> <ny> <nz> <incompressible|compressible> [nranks] [iters]
set -u
BASE=/home/ubuntu/certonomous-runs/hlpw6-memory-probe
TAG=$1; NX=$2; NY=$3; NZ=$4; MODE=$5; NR=${6:-14}; IT=${7:-20}
CASE=$BASE/case_$TAG
OUT=$BASE/logs/measurements.jsonl
MW="python3 $BASE/memwatch.py"
if [ "$MODE" = compressible ]; then SOLVER=rhoSimpleFoam; else SOLVER=simpleFoam; fi

rm -rf "$CASE"
python3 "$BASE/make_case.py" "$CASE" "$NX" "$NY" "$NZ" "$MODE" || exit 1
sed -i "s/^endTime         20;/endTime         $IT;/" "$CASE/system/controlDict"
sed -i "s/^numberOfSubdomains 14;/numberOfSubdomains $NR;/" "$CASE/system/decomposeParDict"

run() { # run <stagetag> <timeout_s> <shell command>
  echo "=== $TAG/$1 ==="
  $MW --tag "$TAG/$1" --out "$OUT" --cwd "$CASE" --timeout "$2" \
      --log "$BASE/logs/${TAG}_$1.log" -- \
      openfoam2606 -c "cd $CASE && $3"
}

run blockMesh      1800 "blockMesh"
run checkMesh      1800 "checkMesh -constant"
run solve_serial   5400 "$SOLVER"
rm -rf "$CASE"/[1-9]* 2>/dev/null
run decomposePar   3600 "decomposePar -force"
run "solve_np$NR"  5400 "mpirun --oversubscribe -np $NR $SOLVER -parallel"
rm -rf "$CASE"/processor* "$CASE"/[1-9]* 2>/dev/null
echo "=== $TAG done ==="
