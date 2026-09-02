#!/usr/bin/env bash
# VMFL007-R3 -- capped detached solver wrapper.
#
# Runs simpleFoam in an already-built case directory under a HARD wall-clock cap.
# The cap is enforced by `timeout`, not by anyone's judgement: rule 12 says an
# overrun stops the run, and a cap a human has to remember is not a cap.
#
# L-"setsid parent returns zero": `setsid timeout cmd` exits 0 for EVERY outcome,
# so the return code is captured INSIDE this wrapper, around the solver call, and
# never around the setsid line that launches the wrapper.
#
# Usage: run_capped.sh <caseDir> <capSeconds>
# Writes <caseDir>/RUN_RC.txt.  Never writes outside <caseDir>.
# NOTE: no `set -u` -- the OpenFOAM etc/bashrc dereferences unset variables and
# aborts the shell under nounset.
CASE=$1; CAP=$2

source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
cd "$CASE" || exit 3

T0=$(date +%s)
timeout --signal=TERM --kill-after=60 "$CAP" simpleFoam > log.simpleFoam 2>&1
RC=$?                       # <-- captured HERE, inside the wrapper
T1=$(date +%s)
WALL=$((T1-T0))

ITERS=$(grep -c 'ExecutionTime' log.simpleFoam)
ENDS=$(grep -c '^End' log.simpleFoam)
LAST=$(grep '^Time = ' log.simpleFoam | tail -1 | awk '{print $3}')
CAPPED=no
[ "$RC" = "124" ] && CAPPED="YES -- stopped by the cap, not by convergence"
{
  echo "case        = $CASE"
  echo "cap_s       = $CAP"
  echo "rc          = $RC"
  echo "capped      = $CAPPED"
  echo "iters       = $ITERS"
  echo "last_time   = $LAST"
  echo "End         = $ENDS"
  echo "wall_s      = $WALL"
  echo "ranks       = 1"
  echo "core_min    = $(python3 -c "print(f'{$WALL/60:.4f}')")"
  echo "finished_utc= $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > RUN_RC.txt
