#!/bin/bash
# The HLPW6 hardened configuration, byte for byte, on a DPW5 grid.
#
# This is the only configuration that has ever completed a committee-grid solve
# in this lab (HLPW6_solve_hardened.log, 120 iterations, exit 0, 04:50:45Z). It
# is FIRST ORDER in convection and is carried here as a control, not as a
# result: a first-order solve is not a submission-quality solve. The question it
# answers is narrow and important -- does the thing that rescued HLPW6 also
# rescue the harder grid, or is DPW5 hybrid beyond it?
#
# The dictionaries are lifted verbatim from the HLPW6 case rather than retyped,
# and apply_variant.py prints their md5 so the two runs can be shown to have
# used the same bytes.
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
export PATH="$FOAM_APPBIN:$PATH"
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
H=/home/ubuntu/certonomous-runs/hlpw6-memory-probe
G=${1:-hybrid}; IT=${2:-120}; NP=${3:-14}
TAG="${G}_hardenedHLPW6_incompressible_a2.11"
C="$R/run_$TAG"
echo "=== $TAG start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
rm -rf "$C"; mkdir -p "$C/constant/polyMesh"
cp -l "$R/case_$G/constant/polyMesh"/{points,faces,owner,neighbour,boundary} \
      "$C/constant/polyMesh/" || exit 1
python3 "$R/make_dpw5_case.py" "$C" incompressible 2.11 base "$IT" "$NP" || exit 1
python3 "$R/apply_variant.py" "$H/case_HLPW6" "$C" || exit 1
( cd "$C" && decomposePar -force > "$R/logs/${TAG}_decompose.log" 2>&1 ) || exit 1
python3 "$R/memwatch.py" --tag "$TAG" --out "$R/measurements.jsonl" --cwd "$C" \
    --log "$R/logs/${TAG}_solve.log" --timeout 5400 -- mpirun -np "$NP" simpleFoam -parallel
echo "--- iterations: $(grep -c '^Time = ' "$R/logs/${TAG}_solve.log")"
echo "=== $TAG end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
