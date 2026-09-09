#!/bin/bash
# UNGRADED SMOKE TEST for the STABILIZED own-family M6 config (DELTA A limitTemperature +
# DELTA B startup under-relaxation).  Development compute / method validation ONLY: it
# produces NO verdict, reads NO gate, grades NOTHING.  Its sole purpose is to prove the
# Time=1 SIGFPE clears and residuals descend over ~50 iterations on L2.  Serial (1 rank).
# Mirrors the pinned docker invocation of run_m6_own_family_triple.sh.  Rule 7: nothing under
# /home/ubuntu/certonomous-runs is written.
set +u; set +e

RR=/home/ubuntu/Certonomous/verification/runs/M6_OWN_FAMILY_runs
IMG=dafoam-idwarp-rot:v1
SMOKE="$RR/L2/smoke_stabilized"
MESH_SRC="$RR/L2/case/constant/polyMesh"
WRITER="$RR/write_m6_own_family_case_stabilized.py"
END=200
say(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }

# Fresh smoke dir each run (ungraded dev artifact; the age guard in the writer forbids a
# pre-existing 0/, so we start clean).
rm -rf "$SMOKE"; mkdir -p "$SMOKE/constant" || { echo "ABORT: mkdir"; exit 3; }
[ -d "$MESH_SRC" ] || { echo "ABORT: mesh source absent $MESH_SRC"; exit 3; }
cp -a -- "$MESH_SRC" "$SMOKE/constant/polyMesh" || { echo "ABORT: mesh copy"; exit 3; }
say "staged mesh -> $SMOKE/constant/polyMesh"

python3 "$WRITER" --level L2 --solve "$SMOKE" --ranks 1 --end-time "$END" \
    > "$SMOKE/log.write_case" 2>&1 || { echo "ABORT: stabilized writer failed"; cat "$SMOKE/log.write_case"; exit 3; }
say "stabilized case written (endTime $END, ranks 1); fvOptions + fvSolution deltas layered"

command -v docker >/dev/null 2>&1 || { echo "ABORT: docker not on PATH"; exit 5; }
docker image inspect "$IMG" >/dev/null 2>&1 || { echo "ABORT: image $IMG absent"; exit 7; }
HOST_GID=$(id -g)

say "launching serial rhoSimpleFoam in $IMG (trapFpe stays ON -- a real FPE would still crash)"
timeout -k 5s 900s docker run --rm -u 1002:1002 --group-add "$HOST_GID" \
    -v "$SMOKE":/case -w /case "$IMG" \
    bash -c 'set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; rhoSimpleFoam > log.rhoSimpleFoam 2>&1; echo "RC=$?" > RC_rhoSimpleFoam.txt' \
    > "$SMOKE/log.docker_client" 2>&1
OUTER=$?
INNER="ABSENT"; [ -f "$SMOKE/RC_rhoSimpleFoam.txt" ] && INNER=$(cut -d= -f2 "$SMOKE/RC_rhoSimpleFoam.txt")
say "docker outer rc=$OUTER  inner rhoSimpleFoam rc=$INNER"

echo "==== SMOKE VERDICT (ungraded) ===="
echo "outer_rc=$OUTER inner_rc=$INNER"
if grep -q "Foam::sigFpe\|Floating point exception" "$SMOKE/log.rhoSimpleFoam" 2>/dev/null; then
  echo "FPE_PRESENT=YES  (stabilization did NOT clear the crash)"
else
  echo "FPE_PRESENT=NO   (no SIGFPE / floating point exception in the log)"
fi
echo "-- last Time reached --"; grep -E "^Time = " "$SMOKE/log.rhoSimpleFoam" 2>/dev/null | tail -1
echo "-- End line present? --"; grep -c "^End" "$SMOKE/log.rhoSimpleFoam" 2>/dev/null
echo "done"
