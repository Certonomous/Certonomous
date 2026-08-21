#!/bin/bash
# Detached extension runner for one T1b attempt-2 case (disclosed continuation
# of NOT-A-RESULT rows): resume the solve from latestTime to the raised
# endTime, appending to a NEW log (log.solve.ext1 -- log.solve is untouched),
# then write STATUS3.<case> in the T1b pool format (rc= wall= checkMesh_rc=),
# mirroring STATUS2.  checkMesh is re-run into log.checkMesh.ext1 so the
# original log.checkMesh is not truncated.
source /usr/lib/openfoam/openfoam2606/etc/bashrc
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"
cd "$HERE/$CASE" || { echo "rc=127 wall=0 checkMesh_rc=127" > "$HERE/STATUS3.$CASE"; exit 127; }
checkMesh > log.checkMesh.ext1 2>&1
CMRC=$?
T0=$(date +%s)
buoyantBoussinesqSimpleFoam >> log.solve.ext1 2>&1
RC=$?
T1=$(date +%s)
echo "rc=$RC wall=$((T1-T0)) checkMesh_rc=$CMRC" > "$HERE/STATUS3.$CASE"
