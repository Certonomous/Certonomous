#!/usr/bin/env bash
# M6I GRADED LEVEL LAUNCHER v3 -- usage: launch_m6i_v3.sh <RUNDIR> <RANKS>
#
# v3 ADDS INSTRUMENTATION ONLY.  NO NUMERICS, NO SCHEME, NO RELAXATION, NO BUDGET AND NO
# DICTIONARY VALUE CHANGES.  Everything the solver computes is byte-for-byte v2's.
#
# WHY v3 EXISTS: M6I-R1-L1-TVD stopped at iteration 844 with rc = 1 -- NOT 136, so no SIGFPE
# -- mid-iteration, after a complete GAMG line, with the physics healthy (LimitedCells 0 at
# both bounds, UnlimitedTmin 184.3 K / Tmax 339.6 K, p max 234,754 = 2.3x freestream, worst
# nuTilda 0.0212).  mpirun printed NO signal report and NO FOAM FATAL.  THE CAUSE IS
# UNDETERMINED, and an undetermined cause recurs.  v3 makes a recurrence diagnosable:
#   (1) the solver's STDERR goes to ITS OWN FILE, so an MPI-level message cannot be lost
#       interleaved in a 1.4 MB stdout that four ranks are writing to at once;
#   (2) on any non-zero rc the wrapper writes FAILURE_CONTEXT.<n>.txt -- rc, UTC, free, df,
#       loadavg, solver/process counts, a dmesg attempt for the OOM killer, and the tails of
#       both solver streams -- CAPTURED AT THE MOMENT OF FAILURE, when it is still true.
# NOTHING HERE IS DISCARDED TO /dev/null on any solver or environment stream.
#
# ORIGINAL v2 HEADER FOLLOWS, UNCHANGED:
# M6I GRADED LEVEL LAUNCHER v2 -- usage: launch_m6i_v2.sh <RUNDIR> <RANKS>
#
# WRITTEN AS A NEW FILE, NOT AN EDIT OF v1, on this team's own standing rule: bash reads a
# script incrementally by byte offset while it runs, so editing a live launcher can resume
# the interpreter mid-token.  Precondition checked before writing: `pgrep -x rhoSimpleFoam`
# returned 0 live solvers.  v1 stays on disk as the record of attempts 1 and 2.
#
# WHAT v2 ADDS AND WHY: a TWO-STAGE robust startup (Sanaa's CRM instruction section 6 for
# pressure-based compressible with the transonic option).
#   STAGE 1  first 200 iterations with system/fvSchemes.startup (every convective term
#            first-order upwind) and system/fvSolution.startup (tighter relaxation).
#   STAGE 2  the REGISTERED second-order fvSchemes and fvSolution, restored BYTE-IDENTICALLY
#            with md5 asserted on both sides, from the stage-1 checkpoint to endTime.
# THE GRADED ANSWER IS PRODUCED BY THE REGISTERED SCHEMES.  The ramp only gets the solution
# off a uniform cold start without the pressure excursion that killed attempts 1 and 2.
#
# endTime is moved by this script and ONLY between the two stages.  The registered value is
# read from the case's own controlDict first, a pristine copy is kept as
# system/controlDict.registered, and the final state is asserted md5-identical to it, so a
# crash between the stages cannot leave a truncated budget committed.
#
# Every rc is captured INSIDE this wrapper from the process itself.  NO CAP KILLS THIS RUN:
# no timeout, no clock check, no spend check anywhere below (Sanaa directive #17).
set -u

RUNDIR="${1:?usage: launch_m6i_v2.sh <RUNDIR> <RANKS>}"
RANKS="${2:?ranks}"
STARTUP_ITERS=200

cd "$RUNDIR" || exit 3
exec >> LAUNCH.log 2>&1
echo "=== M6I launch v2  $(date -u +%FT%TZ)  rundir=$RUNDIR ranks=$RANKS"
fail() { echo "REFUSE: $*"; echo "REFUSED" > RC.txt; exit 2; }

[ -d constant/polyMesh ] || fail "no polyMesh"
[ -d 0.orig ] || fail "no 0.orig"
[ -f system/fvSchemes.startup ]  || fail "no system/fvSchemes.startup -- v2 requires the ramp"
[ -f system/fvSolution.startup ] || fail "no system/fvSolution.startup"
[ -f constant/fvOptions ]        || fail "no constant/fvOptions -- the temperature bound is not optional"
grep -q 'limitTemperature' constant/fvOptions || fail "constant/fvOptions carries no limitTemperature"

RESUME=no
if [ -d processor0 ]; then
  LATEST=$(find processor0 -maxdepth 1 -type d -regextype posix-extended \
           -regex '.*/[0-9]+(\.[0-9]+)?$' -printf '%f\n' 2>/dev/null | sort -g | tail -1)
  if [ -n "${LATEST:-}" ] && [ "$(python3 -c "print(1 if float('${LATEST}')>0 else 0)")" = "1" ]; then
    RESUME=yes; echo "RESUME: processor0 holds a checkpoint at t=$LATEST"
  fi
fi
if [ "$RESUME" = "no" ]; then
  [ -e RC.txt ] && { echo "REFUSE: RC.txt exists and there is no checkpoint to resume from"; exit 2; }
  EXTRA=$(find . -maxdepth 1 -type d -regextype posix-extended -regex '\./[0-9]+(\.[0-9]+)?' \
          ! -name 0 -printf '%f ' 2>/dev/null)
  [ -n "$EXTRA" ] && fail "time directories already present ($EXTRA); age-guard precondition broken"
fi

set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc > log.env 2>&1; ENV_RC=$?; set -u
if [ "$ENV_RC" -ne 0 ] || ! command -v rhoSimpleFoam >/dev/null 2>&1; then
    cat log.env; fail "OpenFOAM env did not load (rc=$ENV_RC)"
fi

# ---- assert the registered dictionary, never rewrite it -------------------
grep -qE '^application +rhoSimpleFoam;' system/controlDict || fail "application is not rhoSimpleFoam"
grep -qE '^purgeWrite +2;'              system/controlDict || fail "purgeWrite is not 2"
grep -qE '^writeInterval +200;'         system/controlDict || fail "writeInterval is not the registered 200"
grep -qE 'RASModel +SpalartAllmaras;'   constant/turbulenceProperties || fail "model is not SpalartAllmaras"
grep -qE 'transonic +yes;'              system/fvSolution || fail "transonic is not yes"
grep -qE '\{ p 1; U 0.7; e 0.7; nuTilda 0.7; \}' system/fvSolution \
  || fail "relaxationFactors.equations.p is not 1 -- pEqn.H:36 needs it for diagonal dominance"

N=$(grep -cE '^endTime +[0-9]+;' system/controlDict)
[ "$N" = "1" ] || fail "expected exactly 1 endTime line, found $N"
ET=$(grep -oE '^endTime +[0-9]+;' system/controlDict | grep -oE '[0-9]+')
[ -f system/controlDict.registered ] || cp system/controlDict system/controlDict.registered
CD_MD5=$(md5sum < system/controlDict.registered)
echo "registered endTime=$ET writeInterval=200 purgeWrite=2 SA transonic=yes equations.p=1"

set_endtime () {
  sed -i -E "s/^endTime +[0-9]+;/endTime         ${1};/" system/controlDict
  grep -qE "^endTime +${1};" system/controlDict || fail "endTime -> $1 did not read back"
  echo "endTime set to $1 (read back OK)"
}
restore_controlDict () {
  cp system/controlDict.registered system/controlDict
  [ "$(md5sum < system/controlDict)" = "$CD_MD5" ] || fail "controlDict restore is not byte-identical"
  echo "controlDict restored byte-identically (endTime $ET)"
}

run_stage () {   # run_stage <logfile>
  local LOG="$1"
  date -u +%FT%TZ >> SOLVE_START_UTC.txt
  local T0=$(date +%s)
  # v3: STDERR TO ITS OWN FILE.  v2 merged it into a stdout that four ranks write
  # concurrently; an MPI-level message emitted as a rank dies can be lost or interleaved
  # there, and on L1 at iteration 844 mpirun's rc=1 arrived with no message at all.
  local ERRLOG="${LOG}.stderr"
  mpirun -np "$RANKS" rhoSimpleFoam -parallel > "$LOG" 2> "$ERRLOG" &
  local MP=$!
  local PIDS="" ART=""
  for _ in $(seq 1 120); do
    [ -z "$PIDS" ] && PIDS=$(pgrep -P "$MP" -x rhoSimpleFoam 2>/dev/null | tr '\n' ' ')
    [ -z "$ART" ]  && ART=$(grep -m1 '^ExecutionTime' "$LOG" 2>/dev/null)
    [ -n "$PIDS" ] && [ -n "$ART" ] && break
    kill -0 "$MP" 2>/dev/null || break
    sleep 2
  done
  { if [ -n "$PIDS" ] && [ -n "$ART" ]; then
      echo "launched: true"; echo "witness_a_solver_pids: $PIDS"; echo "witness_b_first_artifact: $ART"
    else
      echo "launched: false"; echo "reason: pids='${PIDS:-NONE}' artifact='${ART:-NONE}'"
    fi
    echo "mpirun_pid: $MP  (NOT a witness -- alive in every outcome)"
    echo "stage_log: $LOG   utc: $(date -u +%FT%TZ)"; } >> LAUNCHED.txt
  wait "$MP"; STAGE_RC=$?
  # v3: capture the box's state AT THE MOMENT OF FAILURE, while it is still true.
  if [ "$STAGE_RC" != "0" ]; then
    local n=1; while [ -e "FAILURE_CONTEXT.$n.txt" ]; do n=$((n+1)); done
    { echo "=== M6I FAILURE CONTEXT  utc=$(date -u +%FT%TZ)  rc=$STAGE_RC  log=$LOG"
      echo "--- last solver Time line ---"; grep -E '^Time = ' "$LOG" 2>/dev/null | tail -1
      echo "--- solver STDERR (its own stream, v3) ---"; tail -40 "$ERRLOG" 2>/dev/null
      echo "(empty above means the solver wrote nothing to stderr)"
      echo "--- free -g ---"; free -g
      echo "--- df -h on the run tree ---"; df -h .
      echo "--- loadavg / cpu count ---"; cat /proc/loadavg; nproc
      echo "--- solver processes alive ---"; pgrep -c -x rhoSimpleFoam; pgrep -c -x simpleFoam
      echo "--- dmesg tail (OOM killer); may be unreadable without privilege ---"
      dmesg 2>&1 | tail -25 || echo "(dmesg not readable -- OOM can be NEITHER CONFIRMED NOR EXCLUDED from here)"
      echo "--- last 40 lines of the solver stdout ---"; tail -40 "$LOG" 2>/dev/null
    } > "FAILURE_CONTEXT.$n.txt" 2>&1
    echo "wrote FAILURE_CONTEXT.$n.txt"
  fi
  local W=$(( $(date +%s) - T0 ))
  echo "$W" >> WALL_SECONDS_SOLVE.txt
  awk -v w="$W" -v r="$RANKS" 'BEGIN{printf "%.2f\n", w*r/60.0}' >> CORE_MINUTES.txt
  echo "stage $LOG rc=$STAGE_RC wall=${W}s core-min=$(tail -1 CORE_MINUTES.txt)"
}

if [ "$RESUME" = "no" ]; then
  rm -rf 0 && cp -r 0.orig 0 || fail "could not stage 0/ from 0.orig"
  echo "0/ staged at $(date -u -d @$(stat -c %Y 0) +%FT%TZ) -- the age-guard baseline"
  NS=$(grep -oE '^numberOfSubdomains +[0-9]+;' system/decomposeParDict | grep -oE '[0-9]+')
  [ "$NS" = "$RANKS" ] || fail "decomposeParDict says $NS, launcher was given $RANKS"
  decomposePar -force > log.decomposePar 2>&1; DP=$?; echo "$DP" > rc.decomposePar
  [ "$DP" = "0" ] || fail "decomposePar rc=$DP"
  echo "decomposePar rc=0 into $RANKS subdomains"

  # ---------------- STAGE 1: the first-order ramp ----------------
  cp system/fvSchemes  system/fvSchemes.registered
  cp system/fvSolution system/fvSolution.registered
  SCH_MD5=$(md5sum < system/fvSchemes.registered); SOL_MD5=$(md5sum < system/fvSolution.registered)
  cp system/fvSchemes.startup  system/fvSchemes
  cp system/fvSolution.startup system/fvSolution
  grep -q 'STARTUP RAMP ONLY' system/fvSchemes || fail "startup fvSchemes did not read back"
  set_endtime "$STARTUP_ITERS"
  echo "--- STAGE 1: $STARTUP_ITERS iterations, first-order ramp ---"
  run_stage log.rhoSimpleFoam.startup
  S1_RC=$STAGE_RC; echo "$S1_RC" > rc.stage1

  cp system/fvSchemes.registered  system/fvSchemes
  cp system/fvSolution.registered system/fvSolution
  [ "$(md5sum < system/fvSchemes)"  = "$SCH_MD5" ] || fail "fvSchemes restore is not byte-identical"
  [ "$(md5sum < system/fvSolution)" = "$SOL_MD5" ] || fail "fvSolution restore is not byte-identical"
  echo "registered fvSchemes and fvSolution restored, md5 asserted on both sides"
  restore_controlDict
  [ "$S1_RC" = "0" ] || { echo "$S1_RC" > RC.txt; date -u +%FT%TZ > SOLVE_END_UTC.txt;
        echo "=== STAGE 1 FAILED rc=$S1_RC -- stage 2 not attempted"; exit 0; }
  SOLVELOG=log.rhoSimpleFoam
else
  restore_controlDict
  n=1; while [ -e "log.rhoSimpleFoam.resume.$n" ]; do n=$((n+1)); done
  SOLVELOG="log.rhoSimpleFoam.resume.$n"
fi

echo "$RANKS" > RANKS.txt
echo "--- STAGE 2: registered second-order schemes to endTime $ET ---"
run_stage "$SOLVELOG"
SF_RC=$STAGE_RC

if [ "$SF_RC" = "0" ]; then
  reconstructPar -latestTime > log.reconstructPar 2>&1; echo "$?" > rc.reconstructPar
  foamToVTK -latestTime -patches '(wing)' > log.foamToVTK 2>&1; echo "$?" > rc.foamToVTK
  VTP=$(find VTK -name 'wing*.vtp' 2>/dev/null | sort | tail -1)
  if [ -n "${VTP:-}" ]; then
    python3 "$(dirname "$0")/extract_cp_m6i.py" "$VTP" cp_extracted.json > log.extract_cp 2>&1
    echo "$?" > rc.extract_cp
  else
    echo "NO wing .vtp produced" > log.extract_cp; echo "2" > rc.extract_cp
  fi
fi
echo "$SF_RC" > RC.txt
date -u +%FT%TZ > SOLVE_END_UTC.txt
echo "=== M6I launch v2 finished rc=$SF_RC $(date -u +%FT%TZ)"
