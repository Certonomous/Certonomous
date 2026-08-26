#!/usr/bin/env bash
# F15 -- LAUNCHER for the oblique shock reflection at M_inf = 2.9.
#
# FIRES NOTHING WITHOUT --prereg-commit.  `--preflight` runs every guard and
# every path resolution AND STOPS, at zero compute -- including refusing to run
# blockMesh, because a mesh gate that a mesher grades is FIRED the moment the
# mesher runs, and that is what closed the ONERA M6 ladder.
#
# `set -e` DOES NOT GATE IN THIS HARNESS.  Every assertion below carries an
# explicit `|| { echo ABORT ...; exit 1; }`.
#
# NO `rm -rf`, NO `rmtree`, ON A CASE DIRECTORY, ANYWHERE IN THIS FILE.  A
# pre-existing `0/` or numeric time directory is REFUSED, never deleted --
# F5c's launcher deletes what it should refuse and that is a forbidden shape in
# cfd's territory.
#
# THE CAP IS CHECKED INCREMENTALLY AFTER EACH LEVEL, in wall x ranks / 60, and
# the wall figure is OpenFOAM's `ClockTime`, NOT `ExecutionTime`: the latter
# excludes startup, meshing and sampling, and on F6d substituting it moved a
# calibration ratio from 0.998 to 1.0034 -- across 1.0, in the flattering
# direction.
set -u
set -o pipefail

CASE_SRC="/home/ubuntu/Certonomous/cases/F15_oblique_shock_reflection/case"
EXACT="/home/ubuntu/Certonomous/cases/F15_oblique_shock_reflection/exact_osr.py"
GRADER="/home/ubuntu/Certonomous/cases/F15_oblique_shock_reflection/grade_f15.py"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/F15_runs"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

CAP_CORE_MIN=200            # must equal grade_f15.py::CAP_CORE_MIN
END_TIME=10                 # must equal grade_f15.py::END_TIME

# name  nx  ny  ranks   -- DECOMPOSITION SEED IS A REQUIRED FIELD, recorded below
LEVELS=("coarse 200 50 1" "medium 400 100 1" "fine 800 200 1")
# projected SERIAL seconds per level from the lab-measured 1.03 us/cell/step
# (VMFL045/R2, ClockTime). Used ONLY by the pre-level projected-cap check.
declare -A PROJ_SERIAL_S=( [coarse]=100 [medium]=803 [fine]=6427 )
# DECOMPOSITION SEED -- AMENDMENT 1, 2026-08-26 (pre-first-compute).
#   `none`, identity decomposition. EVERY LEVEL RUNS SERIAL ON 1 RANK and
#   `decomposePar` IS NOT INVOKED AT ANY LEVEL. There is no partition and no RNG.
#   The struck 1/4/8 configuration would have changed the floating-point
#   summation order ACROSS the ladder, injecting a non-mesh difference into
#   exactly the level-to-level differences the observed-order fit consumes.
#   A grid-convergence ladder must differ ONLY in mesh. Wording matches F16.
DECOMP_METHOD="none"
DECOMP_SEED="none (identity decomposition: every level runs SERIAL on 1 rank and decomposePar is NOT invoked at any level; there is no partition and no RNG)"

PREREG_COMMIT=""
PREFLIGHT=0
for a in "$@"; do
  case "$a" in
    --preflight) PREFLIGHT=1 ;;
    --prereg-commit=*) PREREG_COMMIT="${a#*=}" ;;
    *) echo "ABORT: unknown argument $a"; exit 1 ;;
  esac
done

say() { printf '%s\n' "$*"; }

# --------------------------------------------------------------------------
# PRE-FIRST-COMPUTE AMENDMENT, 2026-08-26.  Legal under rule 2 sec.2b: this
# changes NO gate, NO threshold, NO cap and NO label.  CONDITION AND HOW IT WAS
# CHECKED: neither run root existed when this was written --
#   verification/runs/F15_runs and verification/runs/F16_runs were both ABSENT,
#   and neither case tree held an RC.txt, a log.* or a numeric time directory.
# It adds four things, all of them STRENGTHENING what is already registered:
#   1. a per-level RC.txt, so a non-zero rc is visible and never swallowed;
#   2. a load and memory probe taken BY THIS INVOCATION before each level and
#      recorded beside it -- never a figure relayed from a message;
#   3. a PROJECTED cap check BEFORE each level, alongside the registered
#      post-level one.  The registered cap is unchanged at its frozen value.
#      The post-level check discovers a crossing only AFTER the core-minutes
#      have been spent; on a contended box that is how a cap gets blown and then
#      reported.  This halts before the spend instead.
#   4. ClockTime's INTEGER-SECOND resolution stated as a quantisation bound on
#      every actual, so no calibration ratio is quoted tighter than its input.
# --------------------------------------------------------------------------
probe_box() {   # $1 = label, $2 = destination file
  local L1 MEMKB NP FREE
  L1=$(awk '{print $1}' /proc/loadavg)
  MEMKB=$(awk '/^MemAvailable/{print $2}' /proc/meminfo)
  NP=$(nproc)
  FREE=$(python3 -c "print(max(0.5, $NP - $L1))")
  printf 'label=%s\nload1=%s\nnproc=%s\nfree_cores=%s\nMemAvailable_kB=%s\nutc=%s\n' \
    "$1" "$L1" "$NP" "$FREE" "$MEMKB" "$(date -u +%FT%TZ)" > "$2"
  echo "$FREE"
}

# --------------------------------------------------------------------------
# PATH RESOLUTION -- every path this file will write to or read from is
# resolved against the disk IN THIS INVOCATION.  The a1fbe127 reorg left ~140
# tracked scripts citing a dead demo-output/website tree, and both F6d's and
# F5c's launchers point at directories that no longer exist.
# --------------------------------------------------------------------------
for p in "$CASE_SRC" "$CASE_SRC/0" "$CASE_SRC/constant" "$CASE_SRC/system"; do
  [ -d "$p" ] || { echo "ABORT: required directory does not exist: $p"; exit 1; }
done
for f in "$CASE_SRC/0/U" "$CASE_SRC/0/p" "$CASE_SRC/0/T" \
         "$CASE_SRC/constant/thermophysicalProperties" \
         "$CASE_SRC/constant/turbulenceProperties" \
         "$CASE_SRC/system/fvSchemes" "$CASE_SRC/system/fvSolution" \
         "$CASE_SRC/system/blockMeshDict.template" \
         "$CASE_SRC/system/controlDict.template" \
         "$EXACT" "$GRADER" "$FOAM_BASHRC"; do
  [ -f "$f" ] || { echo "ABORT: required file does not exist: $f"; exit 1; }
done
say "PATHS RESOLVED against disk in this invocation: 12 files, 4 directories."

# --------------------------------------------------------------------------
# THE INSTRUMENT MUST BE GREEN BEFORE ANY COMPUTE
# --------------------------------------------------------------------------
python3 "$EXACT" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: exact_osr.py --selftest did not pass; the exact solution is not established and NOTHING may be launched against it"; exit 1; }
python3 "$GRADER" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: grade_f15.py --selftest did not pass; the grading path is not established"; exit 1; }
python3 -O "$GRADER" --selftest > /dev/null 2>&1
[ $? -eq 2 ] \
  || { echo "ABORT: grade_f15.py did not exit 2 under python3 -O; the -O refusal is not armed"; exit 1; }
say "INSTRUMENT GREEN: exact_osr and grade_f15 selftests pass; grade_f15 exits 2 under -O."

# The value only, never the trailing comment: an earlier draft used
# `sed 's/[^0-9.]//g'` and read "200.060" out of "200.0 ... 1.03 us/cell/step",
# then reported a disagreement that did not exist. STATE WHAT TWO THINGS YOU ARE
# COMPARING AND PROVE THEY ARE COMPARABLE BEFORE READING THE DIFFERENCE.
CAP_GRADER=$(grep -E '^CAP_CORE_MIN' "$GRADER" | head -1 | sed -E 's/^CAP_CORE_MIN[[:space:]]*=[[:space:]]*([0-9.]+).*/\1/')
python3 -c "import sys; sys.exit(0 if abs(float('$CAP_GRADER') - $CAP_CORE_MIN) < 1e-9 else 1)" \
  || { echo "ABORT: launcher cap $CAP_CORE_MIN disagrees with grade_f15.py CAP_CORE_MIN $CAP_GRADER"; exit 1; }
say "CAP AGREES between launcher and grader: $CAP_CORE_MIN core-minutes."

if [ "$PREFLIGHT" = "1" ]; then
  say ""
  say "PREFLIGHT ONLY -- ZERO COMPUTE.  blockMesh was NOT run: a mesh gate is"
  say "FIRED the moment the mesher runs, and that closed the M6 ladder."
  say "decomposition method: $DECOMP_METHOD"
  say "decomposition seed:   $DECOMP_SEED"
  for L in "${LEVELS[@]}"; do
    set -- $L
    say "  level $1: ${2}x${3} = $(( $2 * $3 )) cells, ranks $4, target $RUN_ROOT/$1"
    if [ -e "$RUN_ROOT/$1/0" ]; then
      say "    NOTE: $RUN_ROOT/$1/0 ALREADY EXISTS -- a real launch would REFUSE here."
    fi
  done
  exit 0
fi

[ -n "$PREREG_COMMIT" ] \
  || { echo "ABORT: --prereg-commit=<sha> is required. Rule 2: the gate, the threshold, the cap and the label are committed BEFORE the solver starts, and the grading path is fixed at that commit."; exit 1; }
git -C /home/ubuntu/Certonomous cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "ABORT: $PREREG_COMMIT is not a commit in this repository"; exit 1; }

# shellcheck disable=SC1090
. "$FOAM_BASHRC" || { echo "ABORT: could not source $FOAM_BASHRC"; exit 1; }
command -v rhoCentralFoam > /dev/null || { echo "ABORT: rhoCentralFoam not on PATH after sourcing"; exit 1; }
command -v blockMesh      > /dev/null || { echo "ABORT: blockMesh not on PATH after sourcing"; exit 1; }

mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
SPENT=0

for L in "${LEVELS[@]}"; do
  set -- $L
  NAME=$1; NX=$2; NY=$3; RANKS=$4
  CD="$RUN_ROOT/$NAME"
  # ---- THE GUARD.  REFUSE, NEVER DELETE. -------------------------------
  if [ -e "$CD/0" ]; then
    echo "ABORT: $CD/0 already exists. A pre-existing 0/ means an earlier run"
    echo "       has already touched this directory, and standing rule 4's age"
    echo "       guard dates every field against this case's own 0/T. This"
    echo "       launcher REFUSES; it does not delete. Move it aside by hand or"
    echo "       choose another run root."
    exit 1
  fi
  for d in "$CD"/*; do
    b=$(basename "$d" 2>/dev/null)
    case "$b" in
      ''|'*') ;;
      *[!0-9.]*) ;;
      *) echo "ABORT: $CD already holds numeric time directory $b. REFUSED, not deleted."; exit 1 ;;
    esac
  done

  mkdir -p "$CD" || { echo "ABORT: cannot create $CD"; exit 1; }

  # ---- PROBE THIS BOX, IN THIS INVOCATION. Never a relayed figure. ------
  FREE=$(probe_box "$NAME-pre" "$CD/box_before.txt")
  PROJ=$(python3 -c "r=$RANKS; f=$FREE; print(${PROJ_SERIAL_S[$NAME]} / min(r, f) * r / 60.0)")
  say "level $NAME: free cores $FREE, ranks $RANKS -> PROJECTED $PROJ core-min (cumulative would be $(python3 -c "print($SPENT + $PROJ)") of $CAP_CORE_MIN)"
  python3 -c "import sys; sys.exit(0 if $SPENT + $PROJ <= $CAP_CORE_MIN else 1)" || {
    echo "HALT BEFORE SPENDING: level $NAME is PROJECTED to take $PROJ core-min"
    echo "      with only $FREE cores free against $RANKS ranks; cumulative"
    echo "      $(python3 -c "print($SPENT + $PROJ)") would cross the registered cap of $CAP_CORE_MIN."
    echo "      The cap is NOT raised and the level is NOT run. Levels not"
    echo "      launched stay PENDING. An overrun stops the run; it does not get"
    echo "      a new budget (CLAUDE.md rule 12). Contention, not the ladder, is"
    echo "      the binding constraint -- report it as a NAMED contention term."
    exit 3
  }

  mkdir -p "$CD/system" "$CD/constant" || { echo "ABORT: cannot create $CD"; exit 1; }
  cp "$CASE_SRC/constant/thermophysicalProperties" "$CD/constant/" || { echo "ABORT: copy failed"; exit 1; }
  cp "$CASE_SRC/constant/turbulenceProperties"     "$CD/constant/" || { echo "ABORT: copy failed"; exit 1; }
  cp "$CASE_SRC/system/fvSchemes" "$CASE_SRC/system/fvSolution" "$CD/system/" || { echo "ABORT: copy failed"; exit 1; }
  sed -e "s/__NX__/$NX/" -e "s/__NY__/$NY/" "$CASE_SRC/system/blockMeshDict.template" > "$CD/system/blockMeshDict" \
    || { echo "ABORT: blockMeshDict templating failed"; exit 1; }
  cp "$CASE_SRC/system/controlDict.template" "$CD/system/controlDict" || { echo "ABORT: copy failed"; exit 1; }
  grep -q "endTime         $END_TIME;" "$CD/system/controlDict" \
    || { echo "ABORT: controlDict endTime is not the registered $END_TIME"; exit 1; }

  blockMesh -case "$CD" > "$CD/log.blockMesh" 2>&1 \
    || { echo "ABORT: blockMesh failed at level $NAME; see $CD/log.blockMesh"; exit 1; }
  checkMesh -case "$CD" > "$CD/log.checkMesh" 2>&1 \
    || { echo "ABORT: checkMesh failed at level $NAME"; exit 1; }
  grep -q "Mesh OK" "$CD/log.checkMesh" \
    || { echo "ABORT: checkMesh did not report 'Mesh OK' at level $NAME"; exit 1; }

  # 0/ is written LAST, and 0/T last of all, because the age guard dates every
  # endTime field against 0/T (standing rule 4).
  mkdir -p "$CD/0" || { echo "ABORT: cannot create $CD/0"; exit 1; }
  cp "$CASE_SRC/0/U" "$CASE_SRC/0/p" "$CD/0/" || { echo "ABORT: copy failed"; exit 1; }
  cp "$CASE_SRC/0/T" "$CD/0/T" || { echo "ABORT: copy failed"; exit 1; }

  # AMENDMENT 1 forbids any parallel level. The parallel branch is REMOVED
  # rather than left unreachable: dead code in a launcher is the hazard class
  # the check_launcher_can_launch GLOB:76 caveat named. A registered rank count
  # other than 1 is now a REFUSAL, not a silently-taken other path.
  [ "$RANKS" -eq 1 ] || { echo "ABORT: level $NAME is registered with $RANKS ranks; AMENDMENT 1 registers 1 rank at every level and decomposePar is not invoked."; exit 1; }
  say "level $NAME runs SERIAL on 1 rank: decomposePar NOT invoked. Decomposition seed: $DECOMP_SEED"
  rhoCentralFoam -case "$CD" > "$CD/log.rhoCentralFoam" 2>&1
  RC=$?
  echo "$RC" > "$CD/RC.txt"
  probe_box "$NAME-post" "$CD/box_after.txt" > /dev/null
  [ "$RC" -eq 0 ] || { echo "ABORT: rhoCentralFoam exited $RC at level $NAME (rc recorded in $CD/RC.txt). A crash is a FINDING until triage says otherwise; it is not retried here."; exit 1; }

  # ---- INCREMENTAL CAP, ClockTime NOT ExecutionTime --------------------
  CLOCK=$(grep "ClockTime = " "$CD/log.rhoCentralFoam" | tail -1 | sed 's/.*ClockTime = \([0-9][0-9]*\) s.*/\1/')
  [ -n "$CLOCK" ] || { echo "ABORT: no ClockTime in $CD/log.rhoCentralFoam; the cap cannot be checked and an unchecked cap is not a cap"; exit 1; }
  SPENT=$(python3 -c "print($SPENT + $CLOCK * $RANKS / 60.0)")
  say "level $NAME COMPLETE: ClockTime ${CLOCK}s x $RANKS ranks -> cumulative $SPENT core-min of $CAP_CORE_MIN"
  say "  QUANTISATION: ClockTime has INTEGER-SECOND resolution, so this level's"
  say "  actual carries +/- $(python3 -c "print(0.5*$RANKS/60.0)") core-min of read-out quantisation alone."
  python3 -c "import sys; sys.exit(0 if $SPENT <= $CAP_CORE_MIN else 1)" || {
    echo "HALT: THE REGISTERED CAP OF $CAP_CORE_MIN CORE-MINUTES HAS BEEN CROSSED"
    echo "      at level $NAME; cumulative spend $SPENT core-min."
    echo "      An overrun STOPS the run. It does not get a new budget"
    echo "      (CLAUDE.md rule 12). Levels not yet launched stay PENDING and the"
    echo "      rung is reported at whatever it reached."
    exit 3
  }
done

say ""
say "ALL THREE LEVELS COMPLETE. Cumulative spend: $SPENT core-min of $CAP_CORE_MIN."
say "Grading is a SEPARATE invocation and is not run from here:"
say "  python3 $GRADER --prereg-commit=$PREREG_COMMIT"
