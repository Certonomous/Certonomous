#!/usr/bin/env bash
# launch_crm_wb.sh RUNDIR RANKS [ENDTIME]
#
# CRM wing-body (D8G) parallel launcher. Invoked ONLY by the queue runner -- a hand launch is
# not a case (Sanaa, run instructions item 19).
#
# NO TIMEOUT, NO CLOCK CHECK, NO SPEND CHECK ANYWHERE IN THIS FILE. Sanaa has ruled four times
# that no run is stopped by a time or budget cap (directive #17). The registered cap is a
# GRADING condition: crossing it makes the row NOT A RESULT; it never kills the solver.
#
# The rc is captured INSIDE this wrapper, around the solver itself, never around a setsid or
# mpirun parent -- `setsid timeout cmd` exits 0 for every outcome (lab lesson).
set -u
RUNDIR="$1"; RANKS="$2"; ENDTIME="${3:-}"
cd "$RUNDIR" || { echo "no rundir $RUNDIR"; exit 64; }

[ "$(id -u)" -eq 0 ] && { echo "REFUSE: running as root"; exit 65; }

source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1

if [ -n "$ENDTIME" ]; then
  foamDictionary -entry endTime -set "$ENDTIME" system/controlDict >/dev/null || exit 66
fi

# The mesh must already carry the registered patch types and no defaultFaces; a level that
# failed the acceptance test never reaches here.
if grep -q defaultFaces constant/polyMesh/boundary 2>/dev/null; then
  echo "REFUSE: defaultFaces present -- level failed the registered acceptance test"; exit 67
fi

if [ ! -d processor0 ]; then
  echo "REFUSE: not decomposed"; exit 68
fi

echo "START $(date -u +%Y-%m-%dT%H:%M:%SZ) ranks=$RANKS endTime=$(foamDictionary -entry endTime -value system/controlDict)"
mpirun -np "$RANKS" rhoSimpleFoam -parallel >> log.rhoSimpleFoam 2>&1
RC=$?
echo "RC=$RC" > RC.txt
echo "END $(date -u +%Y-%m-%dT%H:%M:%SZ) rc=$RC"
exit $RC
