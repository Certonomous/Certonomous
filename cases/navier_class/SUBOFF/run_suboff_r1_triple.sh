#!/bin/bash
# =====================================================================================
# SUBOFF R1 GRADED-TRIPLE LAUNCHER
#
# Runs the three REGISTERED graded levels of SUBOFF R1 -- reg_coarse, reg_medium,
# reg_fine -- per verification/campaign/SUBOFF_R1_PREREGISTRATION.md sections 4a, 5,
# 5a and 7.  It SOLVES ONLY.  It does not grade, does not freeze anything, does not
# write into the queue directory and does not touch the mesh.
#
# THIS SCRIPT DOES NOT AUTHORISE ITS OWN RUN.  The pre-registration freeze (sha) and
# the graded launch are the cfd supervisor's SUPERVISION_CHARTER section 3 check-4,
# taken personally.  Being executable is not being approved.
#
# -------------------------------------------------------------------------------------
# EVERY RULE BELOW EXISTS BECAUSE SOMETHING BROKE ON IT BEFORE.
# -------------------------------------------------------------------------------------
#
# (1) rc IS CAPTURED INSIDE THIS WRAPPER, NEVER AROUND A setsid LINE.
#     `setsid timeout cmd` exits 0 for EVERY outcome -- success, non-zero, SIGKILL,
#     timeout -- so an rc read by whoever launched this script is meaningless.  The rc
#     of simpleFoam is read on the line immediately after simpleFoam returns, INSIDE
#     this process, and written to the case's own `rc` sidecar, which is the ONLY thing
#     grade_suboff.read_rc() will accept (grade_suboff.py:171-180: an 'End' line is NOT
#     rc==0).  If the queue runner or a human wraps this script in setsid/timeout, that
#     outer rc is decoration; the sidecar is the record.
#
# (2) NOTHING IS DELETED.  There is no `rm -rf` in this file, per level or otherwise.
#     E1's SUP_BOOSTER launcher cleared each level's directory before running it, which
#     is precisely why pointing a successor at an existing run root would have destroyed
#     the evidence in it.  A dirty directory here is a REFUSAL, never a clearing.
#
# (3) 0/ IS CREATED BY THIS SCRIPT AT LAUNCH, FROM 0.orig/, AND IS NEVER PRE-STAGED.
#     grade_suboff.check_completion() dates the run by the mtime of `0/U` and refuses
#     any field at endTime that is not NEWER than it (standing rule 4's age guard,
#     grade_suboff.py:230-238).  A pre-staged 0/ dates the run to whenever somebody
#     staged it, which is exactly the hole the age guard exists to close.  `cp -r`
#     is used WITHOUT -p so the copies carry the launch time, and the copy is
#     explicitly re-stamped and verified below.
#
# (4) PROGRESS IS READ FROM ONE NAMED LOG ARTIFACT, NEVER A GLOB.
#     `grep` on this box is ugrep 7.8.4 (verified 2026-09-10), which is multi-threaded
#     and interleaves multi-file output: `grep '^Time = ' log.* | tail -1` was measured
#     at 21/30 correct on this box and 30/30 with the file named, and `-J1` / `--sort`
#     make it deterministically WRONG rather than merely unreliable (the 21/30 and 30/30
#     figures are the LAB's recorded measurement, relayed in the cfd-supervisor's brief;
#     this lane re-measured only that `grep --version` here IS ugrep 7.8.4, 2026-09-10).
#     Every read here names exactly one file:
#     `grep '^Time = ' "$CASE/log.simpleFoam" | tail -1`.
#     Related, and why exactly one log file is written per case: grade_suboff.primary_log()
#     globs `log.simpleFoam*` plus `log*simple*` and takes sorted(...)[-1], so a second
#     simpleFoam log in a case directory would silently change which log is graded.
#
# (5) NO GUARD IS AN `assert`.  Under `python3 -O` every assert is deleted, so a refusal
#     written as one is a refusal the runner accepts or declines by an interpreter flag.
#     This file is bash and every guard is an explicit `if ... ; then refuse ...; fi`.
#     `set -e` is deliberately NOT used: it would abort between simpleFoam returning and
#     its rc being written, losing exactly the record rule (1) exists to keep.
#
# (6) THE GRADER AND THE BUILDER ARE PINNED BY ABSOLUTE PATH and their sha256 is
#     recorded into each level's GRADE_PATH.txt at launch, so the grading path a later
#     verdict cites is the one that was on disk when the solve ran (rule 2's fixed
#     grading path).  This script does NOT run the grader: the grader diff-read is the
#     supervisor's check-1 and grading is a separate, deliberate act.  Pass --grade to
#     opt in explicitly.
#
# -------------------------------------------------------------------------------------
# THE CAP, AND THE ARITHMETIC THE TIMEOUTS ARE DERIVED FROM (rule 12).
# -------------------------------------------------------------------------------------
# The pre-registration registers ONE hard cap in section 7: 150 core-minutes for the
# WHOLE RUNG (triple + section-6 smoke + one rerun allowance).  A cap that covers the
# whole rung is NOT a per-level wall clock, so the per-level timeouts are DERIVED, not
# read off:
#
#   core-min = wall_s * ranks / 60          (the lab's unit, CLAUDE.md rule 12)
#   =>  wall_s = sub_cap_core_min * 60 / ranks
#
# ranks = 1 per level (section 5a: ~40k-202k-cell axisymmetric wedges; a 16-way split
# would leave ~2.5k cells/rank and be communication-bound, and core-min = wall_s*ranks,
# so serial is the CHEAPEST option in the lab's own unit).  Section 5a registers the
# per-level sub-caps at 1.5x the estimate:
#
#   level    cells     est. core-min   sub-cap   wall_s = sub_cap * 60 / 1
#   coarse    39,904        9.67          15        900
#   medium    89,784       21.76          33      1,980
#   fine     202,014       48.95          74      4,440
#   ------------------------------------------------------------------
#   sum of sub-caps                      122      7,320 s  ( = 122 core-min < 150 cap )
#
# The 28 core-min the sub-caps leave under the cap is the section-6 smoke (0.39
# registered) plus reserve.  BOTH are enforced: a level that hits its own wall timeout
# returns 124 and is recorded as a CAP BREACH for that level, AND a single global
# accumulator refuses to START a level whose sub-cap would take the rung past the ONE
# registered 150 core-min cap.  AN OVERRUN STOPS THE RUN; IT DOES NOT GET A NEW BUDGET.
# =====================================================================================

CASES_DIR=/home/ubuntu/Certonomous/cases/navier_class/SUBOFF
RUNS_DIR=/home/ubuntu/Certonomous/verification/runs/navier_class/SUBOFF

# Pinned by absolute path (rule (6) above).
GRADER="$CASES_DIR/grade_suboff.py"
BUILDER="$CASES_DIR/build_suboff.py"
PREREG=/home/ubuntu/Certonomous/verification/campaign/SUBOFF_R1_PREREGISTRATION.md
OPENFOAM_BASHRC=/usr/lib/openfoam/openfoam2606/etc/bashrc

# Registered in section 5a / section 7.  Transcribed, not invented.
ENDTIME_REGISTERED=2500
DELTAT_REGISTERED=1
RANKS=1
CAP_COREMIN_REGISTERED=150.0
CAP_CORESEC_REGISTERED=9000            # 150 * 60 / 1 rank

LEVELS=(coarse medium fine)            # coarse -> fine, the registered order
declare -A CASEOF=( [coarse]="$RUNS_DIR/reg_coarse" \
                    [medium]="$RUNS_DIR/reg_medium" \
                    [fine]="$RUNS_DIR/reg_fine" )
declare -A SUBCAP_COREMIN=( [coarse]=15 [medium]=33 [fine]=74 )
declare -A TIMEOUT_S=( [coarse]=900 [medium]=1980 [fine]=4440 )   # sub_cap * 60 / RANKS

USED_CORESEC=0
DO_GRADE=0
PROGRESS="$RUNS_DIR/PROGRESS.R1_triple.txt"

say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$PROGRESS"; }

refuse() {
  echo "REFUSED: $*" >&2
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] REFUSED: $*" >> "$PROGRESS" 2>/dev/null
  exit 2
}

for arg in "$@"; do
  case "$arg" in
    --grade) DO_GRADE=1 ;;
    --help|-h) sed -n '1,95p' "$0"; exit 0 ;;
    *) refuse "unknown argument '$arg' -- this launcher takes only --grade" ;;
  esac
done

# -------------------------------------------------------------------------------------
# PREFLIGHT.  Everything that can refuse, refuses BEFORE any level starts, so a rung is
# never left half-run because level 3 was going to be rejected anyway.
# -------------------------------------------------------------------------------------
if [ ! -f "$GRADER" ];  then refuse "pinned grader missing: $GRADER"; fi
if [ ! -f "$BUILDER" ]; then refuse "pinned builder missing: $BUILDER"; fi
if [ ! -f "$PREREG" ];  then refuse "pre-registration missing: $PREREG"; fi
if [ ! -f "$OPENFOAM_BASHRC" ]; then refuse "OpenFOAM bashrc missing: $OPENFOAM_BASHRC"; fi

GRADER_SHA=$(sha256sum "$GRADER"  | cut -d' ' -f1)
BUILDER_SHA=$(sha256sum "$BUILDER" | cut -d' ' -f1)
PREREG_SHA=$(sha256sum "$PREREG"  | cut -d' ' -f1)

for L in "${LEVELS[@]}"; do
  C="${CASEOF[$L]}"
  if [ ! -d "$C" ];                       then refuse "$L: registered run root absent: $C"; fi
  if [ ! -d "$C/0.orig" ];                then refuse "$L: no 0.orig/ to copy 0/ from in $C"; fi
  if [ ! -f "$C/0.orig/U" ];              then refuse "$L: 0.orig/U missing in $C -- the age guard needs 0/U"; fi
  if [ ! -d "$C/constant/polyMesh" ];     then refuse "$L: no constant/polyMesh in $C -- mesh not built"; fi
  if [ ! -f "$C/system/controlDict" ];    then refuse "$L: no system/controlDict in $C"; fi

  # RULE 4 / age-guard PRE-LAUNCH GUARD.  A dirty directory is REFUSED, NEVER CLEARED
  # (rule (2) above).  Anything here means somebody already ran, or staged, this level.
  if [ -e "$C/0" ];               then refuse "$L: $C/0 already exists -- 0/ must be created BY THIS LAUNCHER at launch (age guard). Refusing; nothing is deleted. Inspect it, do not clear it."; fi
  if [ -e "$C/rc" ];              then refuse "$L: $C/rc exists -- this level has already been launched. Refusing; nothing is deleted."; fi
  if [ -e "$C/log.simpleFoam" ];  then refuse "$L: $C/log.simpleFoam exists -- this level has already been launched. Refusing; nothing is deleted."; fi
  if [ -e "$C/postProcessing" ];  then refuse "$L: $C/postProcessing exists -- this level already holds forceCoeffs output. Refusing; nothing is deleted."; fi
  DIRTY=$(find "$C" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]*)?' -printf '%f ')
  if [ -n "$DIRTY" ]; then refuse "$L: $C already holds numeric time director(ies): $DIRTY -- standing rule 4: a run is never launched into a tree that already holds an answer. Refusing; nothing is deleted."; fi

  # The registered solver config must be ON DISK before the solve, not asserted after.
  ET=$(grep -m1 -oE '^endTime[[:space:]]+[0-9.eE+-]+' "$C/system/controlDict" | grep -oE '[0-9.eE+-]+$')
  DT=$(grep -m1 -oE '^deltaT[[:space:]]+[0-9.eE+-]+'  "$C/system/controlDict" | grep -oE '[0-9.eE+-]+$')
  if [ "$ET" != "$ENDTIME_REGISTERED" ]; then refuse "$L: controlDict endTime is '$ET', not the section-5a registered $ENDTIME_REGISTERED. 50 is the SMOKE default and a graded run at 50 is NOT A RESULT by truncation."; fi
  if [ "$DT" != "$DELTAT_REGISTERED" ];  then refuse "$L: controlDict deltaT is '$DT', not the registered $DELTAT_REGISTERED -- rule-4 clause 5 (ExecutionTime count == round(endTime/deltaT)) is written for the unit step."; fi
  if grep -q 'residualControl' "$C/system/fvSolution"; then refuse "$L: system/fvSolution contains residualControl -- section 5 requires a HARD stop with NO early exit; with it, last==endTime is unreachable and the level can never complete."; fi
done

# The global cap must be able to cover the sub-caps this run intends to spend.
PLANNED=0
for L in "${LEVELS[@]}"; do PLANNED=$(( PLANNED + SUBCAP_COREMIN[$L] )); done
if [ "$PLANNED" -gt 150 ]; then refuse "planned sub-caps total ${PLANNED} core-min > the ONE registered cap ${CAP_COREMIN_REGISTERED} (section 7). An overrun stops the run; it does not get a new budget."; fi

# OpenFOAM environment.  USER is set defensively: the queue daemon's launch env has had
# USER unset before (L-501), which sends FOAM_USER_APPBIN to a directory that does not
# exist.  simpleFoam is a stock FOAM_APPBIN binary so this is belt-and-braces, not a fix.
if [ -z "${USER:-}" ]; then export USER=ubuntu; fi
# shellcheck disable=SC1090
. "$OPENFOAM_BASHRC" > /dev/null 2>&1
if ! command -v simpleFoam > /dev/null 2>&1; then refuse "simpleFoam not on PATH after sourcing $OPENFOAM_BASHRC"; fi
SIMPLEFOAM_BIN=$(command -v simpleFoam)

say "SUBOFF R1 graded triple -- PREFLIGHT PASSED on all three levels."
say "  endTime=$ENDTIME_REGISTERED deltaT=$DELTAT_REGISTERED ranks=$RANKS cap=${CAP_COREMIN_REGISTERED} core-min (section 7, registered)"
say "  grader  $GRADER  sha256 $GRADER_SHA"
say "  builder $BUILDER sha256 $BUILDER_SHA"
say "  prereg  $PREREG  sha256 $PREREG_SHA"
say "  simpleFoam $SIMPLEFOAM_BIN"

# -------------------------------------------------------------------------------------
# THE LEVELS.
# -------------------------------------------------------------------------------------
OVERALL=0
for L in "${LEVELS[@]}"; do
  C="${CASEOF[$L]}"
  TO="${TIMEOUT_S[$L]}"
  SUB="${SUBCAP_COREMIN[$L]}"

  # ONE registered cap, checked BEFORE the level starts.  Refuses rather than truncates.
  WOULD=$(( USED_CORESEC + SUB * 60 / RANKS ))
  if [ "$WOULD" -gt "$CAP_CORESEC_REGISTERED" ]; then
    say "CAP STOP: starting $L (sub-cap ${SUB} core-min) would take the rung to $(( WOULD / 60 )) core-min, past the ONE registered ${CAP_COREMIN_REGISTERED}. STOPPING. An overrun does not get a new budget."
    echo "cap_coremin_registered=$CAP_COREMIN_REGISTERED used_coresec=$USED_CORESEC stopped_before=$L" > "$RUNS_DIR/CAP_STOP.R1_triple.txt"
    OVERALL=3
    break
  fi

  # 0/ IS CREATED HERE, AT LAUNCH, FROM 0.orig/ -- never pre-staged (rule (3) above).
  # cp WITHOUT -p, so the copies carry the launch time; then re-stamped and verified.
  cp -r "$C/0.orig" "$C/0"
  CPRC=$?
  if [ "$CPRC" -ne 0 ]; then refuse "$L: cp -r 0.orig -> 0 failed rc=$CPRC in $C"; fi
  touch "$C/0"/*
  if [ ! -f "$C/0/U" ]; then refuse "$L: 0/U absent after the copy -- the age guard has nothing to date the run by"; fi
  ZERO_EPOCH=$(stat -c %Y "$C/0/U")
  say "$L: 0/ created from 0.orig/ at epoch $ZERO_EPOCH ($(date -u -d @"$ZERO_EPOCH" +%Y-%m-%dT%H:%M:%SZ)); the age guard dates this run from here."

  # Grading-path record, written per level BEFORE the solve.
  {
    echo "grader  $GRADER  sha256 $GRADER_SHA"
    echo "builder $BUILDER sha256 $BUILDER_SHA"
    echo "prereg  $PREREG  sha256 $PREREG_SHA"
    echo "launched_utc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "endTime $ENDTIME_REGISTERED deltaT $DELTAT_REGISTERED ranks $RANKS"
    echo "subcap_core_min $SUB  wall_timeout_s $TO  (= subcap * 60 / ranks)"
    echo "cap_core_min_registered $CAP_COREMIN_REGISTERED (section 7)"
    echo "NOT GRADED BY THIS LAUNCHER unless --grade was passed."
  } > "$C/GRADE_PATH.txt"

  say "$L: launching simpleFoam in $C -- timeout ${TO}s (sub-cap ${SUB} core-min at ranks $RANKS)"
  T0=$(date +%s)

  # ---- THE SOLVE.  rc IS READ ON THE NEXT LINE, INSIDE THIS PROCESS. ----------------
  ( cd "$C" && timeout "${TO}s" simpleFoam -case "$C" ) > "$C/log.simpleFoam" 2>&1
  RC=$?
  T1=$(date +%s)
  # ---- rc CAPTURED.  Write it to the sidecar the grader reads, immediately. ---------
  # T1 is taken BEFORE the write and the flush: a bare `sync` flushes every filesystem
  # on the box and was MEASURED adding 13 s to a 0 s stub run here on 2026-09-10, i.e.
  # it would have inflated the level's recorded core-minutes with somebody else's I/O.
  # The flush is targeted at this level's own two files instead.
  printf 'rc=%d\n' "$RC" > "$C/rc"
  WALL=$(( T1 - T0 ))
  CORESEC=$(( WALL * RANKS ))
  USED_CORESEC=$(( USED_CORESEC + CORESEC ))

  {
    echo "level=$L"
    echo "case=$C"
    echo "rc=$RC"
    echo "rc_captured=inside_this_wrapper"
    echo "wall_s=$WALL"
    echo "ranks=$RANKS"
    echo "core_min=$(awk -v w=$WALL -v r=$RANKS 'BEGIN{printf "%.3f", w*r/60}')"
    echo "subcap_core_min=$SUB"
    echo "wall_timeout_s=$TO"
    echo "cap_core_min_registered=$CAP_COREMIN_REGISTERED"
    echo "used_core_min_so_far=$(awk -v c=$USED_CORESEC 'BEGIN{printf "%.3f", c/60}')"
    echo "zero_dir_epoch=$ZERO_EPOCH"
    echo "endTime_registered=$ENDTIME_REGISTERED"
    echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$C/STATUS.R1_$L"
  sync "$C/rc" "$C/STATUS.R1_$L" 2>/dev/null

  # PROGRESS -- ONE NAMED LOG ARTIFACT, NEVER A GLOB (rule (4) above).
  LASTTIME=$(grep '^Time = ' "$C/log.simpleFoam" | tail -1)
  NEXEC=$(grep -c '^ExecutionTime' "$C/log.simpleFoam")
  ENDLINE=$(grep -c '^End' "$C/log.simpleFoam")
  say "$L: rc=$RC wall=${WALL}s core-min=$(awk -v w=$WALL -v r=$RANKS 'BEGIN{printf "%.2f", w*r/60}') used=$(awk -v c=$USED_CORESEC 'BEGIN{printf "%.2f", c/60}')/${CAP_COREMIN_REGISTERED}"
  say "$L: last '$LASTTIME' ; ExecutionTime lines=$NEXEC (registered $ENDTIME_REGISTERED) ; End lines=$ENDLINE"

  if [ "$RC" -eq 124 ]; then
    say "$L: CAP BREACH -- simpleFoam hit its ${TO}s wall timeout (sub-cap ${SUB} core-min). The level is STOPPED at the core-minutes spent and gets NO new budget. rc=124 is in the sidecar; the level is NOT complete and is NOT gradeable."
    echo "level=$L rc=124 wall_timeout_s=$TO subcap_core_min=$SUB" > "$C/CAP_BREACH.txt"
    OVERALL=4
  elif [ "$RC" -ne 0 ]; then
    say "$L: rc=$RC -- recorded, not softened. The level is NOT complete and is NOT gradeable. A crash is a FINDING until the supervisor's check-3 triage says otherwise."
    OVERALL=5
  fi

  if [ "$USED_CORESEC" -gt "$CAP_CORESEC_REGISTERED" ]; then
    say "CAP STOP: the rung has spent $(awk -v c=$USED_CORESEC 'BEGIN{printf "%.2f", c/60}') core-min, past the ONE registered ${CAP_COREMIN_REGISTERED}. STOPPING before any further level."
    echo "cap_coremin_registered=$CAP_COREMIN_REGISTERED used_coresec=$USED_CORESEC stopped_after=$L" > "$RUNS_DIR/CAP_STOP.R1_triple.txt"
    OVERALL=3
    break
  fi
done

say "TRIPLE FINISHED with launcher status $OVERALL; total spent $(awk -v c=$USED_CORESEC 'BEGIN{printf "%.2f", c/60}') core-min of the registered ${CAP_COREMIN_REGISTERED}."
say "Rule-12 estimate-vs-actual calibration against section 5a (80.38 core-min predicted for the triple) is OWED as a row in docs/COST_CALIBRATION.md."

if [ "$DO_GRADE" -eq 1 ]; then
  if [ "$OVERALL" -ne 0 ]; then
    say "--grade was passed but the triple did not finish clean (status $OVERALL). NOT grading: a level that is not complete is not gradeable, and the grader would refuse anyway."
  else
    say "GRADING with the pinned grader $GRADER (sha256 $GRADER_SHA)."
    python3 "$GRADER" --coarse "${CASEOF[coarse]}" --medium "${CASEOF[medium]}" --fine "${CASEOF[fine]}"
    GRC=$?
    say "grade_suboff.py rc=$GRC"
    exit "$GRC"
  fi
else
  say "NOT GRADED (grading is a separate, deliberate act; the grader diff-read is the supervisor's check-1). To grade the finished triple with the pinned grader:"
  say "  python3 $GRADER --coarse ${CASEOF[coarse]} --medium ${CASEOF[medium]} --fine ${CASEOF[fine]}"
fi

exit "$OVERALL"
