#!/bin/bash
# run_hlpw6_variant.sh <variant> <alphaDeg> <iters> <nranks>
# Rebuild the HLPW6 TC1 case from its own generator (conditions, BCs, force
# patches -- unchanged from the original probe) and then overwrite only the
# numerics with the exact fvSchemes/fvSolution bytes that the named DPW5 run
# used. Nothing else differs from the run that diverged at iteration 16.
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
export PATH="$FOAM_APPBIN:$PATH"
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
H=/home/ubuntu/certonomous-runs/hlpw6-memory-probe
V=$1; A=${2:-10}; IT=${3:-200}; NP=${4:-14}
TAG="HLPW6_${V}_a${A}"
C="$R/run_$TAG"
echo "=== $TAG start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
rm -rf "$C"; mkdir -p "$C/constant/polyMesh"
cp -l "$H/case_HLPW6/constant/polyMesh"/{points,faces,owner,neighbour,boundary} \
      "$C/constant/polyMesh/" || exit 1
python3 "$H/make_hlpw6_case.py" "$C" incompressible "$A" "$IT" "$NP" || exit 1
python3 "$R/apply_variant.py" "$R/run_hybrid_${V}_incompressible_a2.11" "$C" || exit 1
( cd "$C" && decomposePar -force > "$R/logs/${TAG}_decompose.log" 2>&1 ) || {
    echo "decomposePar FAILED"; tail -20 "$R/logs/${TAG}_decompose.log"; exit 1; }
python3 "$R/memwatch.py" --tag "$TAG" --out "$R/measurements.jsonl" --cwd "$C" \
    --log "$R/logs/${TAG}_solve.log" --timeout 7200 -- \
    mpirun -np "$NP" simpleFoam -parallel
echo "--- iterations reached: $(grep -c '^Time = ' "$R/logs/${TAG}_solve.log")"
tail -4 "$R/logs/${TAG}_solve.log"
echo "=== $TAG end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
