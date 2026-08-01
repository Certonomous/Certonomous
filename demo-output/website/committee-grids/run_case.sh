#!/bin/bash
# run_case.sh <grid: hex|prism|hybrid> <variant> <incompressible|compressible>
#             <alphaDeg> <iters> <nranks>
# Builds a fresh case around a hardlinked copy of the named DPW5 polyMesh,
# decomposes it, and runs the solver under memwatch. Nothing is reused between
# runs except the mesh itself.
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
export PATH="$FOAM_APPBIN:$PATH"
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
G=$1; V=$2; M=$3; A=$4; IT=${5:-200}; NP=${6:-14}
TAG="${G}_${V}_${M}_a${A}"
C="$R/run_$TAG"
echo "=== $TAG  start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
rm -rf "$C"; mkdir -p "$C/constant/polyMesh"
cp -l "$R/case_$G/constant/polyMesh"/{points,faces,owner,neighbour,boundary} \
      "$C/constant/polyMesh/" || exit 1
python3 "$R/make_dpw5_case.py" "$C" "$M" "$A" "$V" "$IT" "$NP" || exit 1
( cd "$C" && decomposePar -force > "$R/logs/${TAG}_decompose.log" 2>&1 ) || {
    echo "decomposePar FAILED"; tail -20 "$R/logs/${TAG}_decompose.log"; exit 1; }
APP=$(grep -oP '(?<=^application     )\w+' "$C/system/controlDict")
python3 "$R/memwatch.py" --tag "$TAG" --out "$R/measurements.jsonl" --cwd "$C" \
    --log "$R/logs/${TAG}_solve.log" --timeout 5400 -- \
    mpirun -np "$NP" "$APP" -parallel
echo "--- exit / last iteration reached:"
grep -c "^Time = " "$R/logs/${TAG}_solve.log"
tail -5 "$R/logs/${TAG}_solve.log"
echo "=== $TAG  end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
