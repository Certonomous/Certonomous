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
# NOTE: `set -u` is NOT used around the OpenFOAM bashrc. Sourcing it under `set -u`
# aborts the shell with status 1 the moment it reads an unset variable, and if its stderr is
# redirected to /dev/null the launch dies leaving NO message at all -- which is exactly how
# this script failed its first launch (launcher_rc=1, empty launcher output, no RC.txt).
RUNDIR="$1"; RANKS="$2"; ENDTIME="${3:-}"
cd "$RUNDIR" || { echo "no rundir $RUNDIR"; exit 64; }

[ "$(id -u)" -eq 0 ] && { echo "REFUSE: running as root"; exit 65; }

source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>> launch.stderr || {
  echo "REFUSE: could not source the OpenFOAM environment"; exit 69; }
command -v rhoSimpleFoam >/dev/null || { echo "REFUSE: rhoSimpleFoam not on PATH after sourcing"; exit 70; }

# `foamDictionary -entry ... -set` REWRITES controlDict AND INLINES EVERY #include, freezing a
# snapshot of system/forces into it. That silently decoupled the run from the registered forces
# dictionary once already: later corrections to system/forces had no effect and the solver kept
# reading a stale copy. So endTime is set with sed on the single line, the #include is left
# intact, and the registered comparator entries are ASSERTED to survive.
if [ -n "$ENDTIME" ]; then
  sed -i -E "s/^([[:space:]]*endTime[[:space:]]+)[0-9.eE+-]+;/\1${ENDTIME};/" system/controlDict \
    || { echo "REFUSE: could not set endTime"; exit 66; }
  grep -qE "^[[:space:]]*endTime[[:space:]]+${ENDTIME};" system/controlDict \
    || { echo "REFUSE: endTime did not take"; exit 66; }
fi
grep -q '#include' system/controlDict \
  || { echo "REFUSE: controlDict lost its #include -- it has been rewritten and may hold a stale forces dict"; exit 71; }
for K in rhoInf Aref lRef CofR magUInf; do
  foamDictionary -entry "functions/forceCoeffs/$K" system/controlDict >/dev/null 2>> launch.stderr \
    || { echo "REFUSE: forceCoeffs is missing the registered entry $K"; exit 72; }
done

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
