#!/usr/bin/env bash
# M6I GRADED LEVEL LAUNCHER  --  usage: launch_m6i.sh <RUNDIR> <RANKS>
#
#   Registration: verification/campaign/M6I_R1_SOLVE_PREREGISTRATION.md
#   Graded against the 14 Cp/shock bands FROZEN AT 4c931d97c
#   (verification/campaign/A3_M6_AGARD_CP_VALIDATION_PREREGISTRATION.md +
#    scripts/grade_m6_agard_cp.py).  THIS SCRIPT CHANGES NOTHING IN EITHER.
#   endTime is NOT an argument: it is whatever the case's own controlDict was
#   built with, so the launcher cannot move a registered budget.
#
# THE rc DISCIPLINE: `setsid timeout cmd` exits 0 for EVERY outcome.  Every rc here is
# captured INSIDE this wrapper from the process itself, never from the exit status of
# whatever launched it and never inferred from an `End` line.
#
# THE LAUNCH-WITNESS DISCIPLINE: `launched: true` needs two witnesses FROM THE CHILD --
# a live rhoSimpleFoam pid (never mpirun's, which is alive in every outcome) and a first
# `^ExecutionTime` line, which only the solver emits.
#
# RESUME (Sanaa 2026-09-12 ~21:25Z: "make sure now that we are able to resume all runs").
#   A rundir that already holds decomposed processor fields at a time > 0 RESUMES from
#   the latest checkpoint: 0/ is NOT restaged, decomposePar is NOT re-run, the solver
#   log is APPENDED to as log.rhoSimpleFoam.resume.<n>, and controlDict's
#   `startFrom latestTime` does the rest.  NOTHING IS EVER DELETED to clear a state.
#
# NO CAP KILLS THIS RUN (Sanaa directive #17, 2026-09-12).  There is no timeout, no
# spend check and no clock check anywhere below.  The cap is REGISTERED; a crossing is
# graded NOT A RESULT by the grader, not enforced by a wrapper.
set -u

RUNDIR="${1:?usage: launch_m6i.sh <RUNDIR> <RANKS>}"
RANKS="${2:?ranks}"

cd "$RUNDIR" || exit 3
exec >> LAUNCH.log 2>&1
echo "=== M6I launch  $(date -u +%FT%TZ)  rundir=$RUNDIR ranks=$RANKS"

fail() { echo "REFUSE: $*"; echo "REFUSED" > RC.txt; exit 2; }

[ -d constant/polyMesh ] || fail "no polyMesh"
[ -d 0.orig ] || fail "no 0.orig"

# ---- is this a RESUME? ----------------------------------------------------
RESUME=no
if [ -d processor0 ]; then
  LATEST=$(find processor0 -maxdepth 1 -type d -regextype posix-extended \
           -regex '.*/[0-9]+(\.[0-9]+)?$' -printf '%f\n' 2>/dev/null | sort -g | tail -1)
  if [ -n "${LATEST:-}" ] && [ "$(python3 -c "print(1 if float('${LATEST}')>0 else 0)")" = "1" ]; then
    RESUME=yes
    echo "RESUME: processor0 holds a checkpoint at t=$LATEST; startFrom latestTime will pick it up"
  fi
fi

if [ "$RESUME" = "no" ]; then
  [ -e RC.txt ] && { echo "REFUSE: RC.txt exists and there is no checkpoint to resume from"; exit 2; }
  EXTRA=$(find . -maxdepth 1 -type d -regextype posix-extended -regex '\./[0-9]+(\.[0-9]+)?' \
          ! -name 0 -printf '%f ' 2>/dev/null)
  [ -n "$EXTRA" ] && fail "time directories already present ($EXTRA); age-guard precondition broken"
fi

MESH_MD5=$(cat constant/polyMesh/points constant/polyMesh/faces \
               constant/polyMesh/owner constant/polyMesh/neighbour | md5sum | cut -d' ' -f1)
echo "mesh md5: $MESH_MD5"

# ---- OpenFOAM env: stderr CAPTURED, never discarded -----------------------
set +u
source /usr/lib/openfoam/openfoam2606/etc/bashrc > log.env 2>&1
ENV_RC=$?
set -u
if [ "$ENV_RC" -ne 0 ] || ! command -v rhoSimpleFoam >/dev/null 2>&1; then
    echo "----- captured output of etc/bashrc (log.env) -----"; cat log.env
    fail "OpenFOAM env did not load (source rc=$ENV_RC, rhoSimpleFoam not on PATH)"
fi
echo "OpenFOAM env OK: $(command -v rhoSimpleFoam)"

# ---- assert the registered dictionary, never rewrite it -------------------
grep -qE '^application +rhoSimpleFoam;' system/controlDict || fail "controlDict application is not rhoSimpleFoam"
grep -qE '^purgeWrite +2;'            system/controlDict || fail "purgeWrite is not 2"
grep -qE '^writeInterval +200;'       system/controlDict || fail "writeInterval is not the registered 200"
grep -qE 'RASModel +SpalartAllmaras;' constant/turbulenceProperties || fail "turbulence model is not SpalartAllmaras"
grep -qE 'transonic +yes;'            system/fvSolution || fail "transonic is not yes"
ET=$(grep -oE '^endTime +[0-9]+;' system/controlDict | grep -oE '[0-9]+')
echo "registered endTime=$ET writeInterval=200 purgeWrite=2 model=SpalartAllmaras transonic=yes"

if [ "$RESUME" = "no" ]; then
  # ---- 0/ is created LAST before compute: it dates the run (rule 4 age guard)
  rm -rf 0 && cp -r 0.orig 0 || fail "could not stage 0/ from 0.orig"
  echo "0/ staged at $(date -u -d @$(stat -c %Y 0) +%FT%TZ) -- the age-guard baseline"
  # decomposeParDict is the case's own registered one: 4 hierarchical subdomains.
  NS=$(grep -oE '^numberOfSubdomains +[0-9]+;' system/decomposeParDict | grep -oE '[0-9]+')
  [ "$NS" = "$RANKS" ] || fail "decomposeParDict says $NS subdomains, launcher was given $RANKS"
  decomposePar -force > log.decomposePar 2>&1; DP_RC=$?
  echo "$DP_RC" > rc.decomposePar
  [ "$DP_RC" = "0" ] || fail "decomposePar rc=$DP_RC"
  echo "decomposePar rc=0 into $RANKS subdomains"
  SOLVELOG=log.rhoSimpleFoam
else
  n=1; while [ -e "log.rhoSimpleFoam.resume.$n" ]; do n=$((n+1)); done
  SOLVELOG="log.rhoSimpleFoam.resume.$n"
fi

# ---- THE GRADED SOLVE.  rc captured from the solver itself. ---------------
echo "$RANKS" > RANKS.txt
date -u +%FT%TZ >> SOLVE_START_UTC.txt
T0=$(date +%s)
mpirun -np "$RANKS" rhoSimpleFoam -parallel > "$SOLVELOG" 2>&1 &
MPIRUN_PID=$!

SOLVER_PIDS=""; FIRST_ART=""
for _ in $(seq 1 120); do
    [ -z "$SOLVER_PIDS" ] && SOLVER_PIDS=$(pgrep -P "$MPIRUN_PID" -x rhoSimpleFoam 2>/dev/null | tr '\n' ' ')
    [ -z "$FIRST_ART" ]   && FIRST_ART=$(grep -m1 '^ExecutionTime' "$SOLVELOG" 2>/dev/null)
    [ -n "$SOLVER_PIDS" ] && [ -n "$FIRST_ART" ] && break
    kill -0 "$MPIRUN_PID" 2>/dev/null || break
    sleep 2
done
if [ -n "$SOLVER_PIDS" ] && [ -n "$FIRST_ART" ]; then
    { echo "launched: true"
      echo "witness_a_solver_pids: $SOLVER_PIDS"
      echo "witness_b_first_artifact: $FIRST_ART"
      echo "mpirun_pid: $MPIRUN_PID   (NOT a witness -- alive in every outcome)"
      echo "resume: $RESUME   solve_log: $SOLVELOG"
      echo "utc: $(date -u +%FT%TZ)"; } > LAUNCHED.txt
else
    { echo "launched: false"
      echo "reason: witness_a_solver_pids='${SOLVER_PIDS:-NONE}' witness_b_first_artifact='${FIRST_ART:-NONE}'"
      echo "mpirun_pid: $MPIRUN_PID alive=$(kill -0 "$MPIRUN_PID" 2>/dev/null && echo yes || echo no)"
      echo "utc: $(date -u +%FT%TZ)"; } > LAUNCHED.txt
fi
cat LAUNCHED.txt

wait "$MPIRUN_PID"; SF_RC=$?
T1=$(date +%s); WALL=$((T1-T0))
echo "$WALL" >> WALL_SECONDS_SOLVE.txt
awk -v w="$WALL" -v r="$RANKS" 'BEGIN{printf "%.2f\n", w*r/60.0}' >> CORE_MINUTES.txt
echo "rhoSimpleFoam rc=$SF_RC wall=${WALL}s ranks=$RANKS core-min=$(tail -1 CORE_MINUTES.txt)"

# ---- reconstruct the latest time and extract Cp ---------------------------
if [ "$SF_RC" = "0" ]; then
  reconstructPar -latestTime > log.reconstructPar 2>&1; echo "$?" > rc.reconstructPar
  foamToVTK -latestTime -patches '(wing)' > log.foamToVTK 2>&1; echo "$?" > rc.foamToVTK
  VTP=$(find VTK -name 'wing*.vtp' 2>/dev/null | sort | tail -1)
  if [ -n "${VTP:-}" ]; then
    python3 "$(dirname "$0")/extract_cp_m6i.py" "$VTP" cp_extracted.json \
        > log.extract_cp 2>&1; echo "$?" > rc.extract_cp
  else
    echo "NO wing .vtp produced -- Cp extraction not attempted" > log.extract_cp
    echo "2" > rc.extract_cp
  fi
fi
echo "$SF_RC" > RC.txt
date -u +%FT%TZ > SOLVE_END_UTC.txt
echo "=== M6I launch finished rc=$SF_RC $(date -u +%FT%TZ)"
