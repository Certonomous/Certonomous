#!/usr/bin/env bash
# F16 -- LAUNCHER for Stokes' second problem (oscillating wall).
#
# FIRES NOTHING WITHOUT --prereg-commit.  `--preflight` runs every guard and
# every path resolution AND STOPS at zero compute, INCLUDING refusing to run
# blockMesh -- a gate a mesher grades is FIRED the moment the mesher runs.
#
# `set -e` DOES NOT GATE IN THIS HARNESS.  Every assertion carries an explicit
# `|| { echo ABORT ...; exit 1; }`.
#
# NO `rm -rf`, NO `rmtree`, ON A CASE DIRECTORY, ANYWHERE IN THIS FILE.  A
# pre-existing `0/` or numeric time directory is REFUSED, never deleted.
#
# THE CAP IS CHECKED INCREMENTALLY AFTER EACH LEVEL, in ClockTime x ranks / 60.
# NOT ExecutionTime: it excludes startup, meshing and sampling, and on F6d that
# substitution moved a calibration ratio across 1.0 in the flattering direction.
set -u
set -o pipefail

ROOT="/home/ubuntu/Certonomous/cases/F16_stokes_second_problem"
CASE_SRC="$ROOT/case"
EXACT="$ROOT/exact_stokes.py"
GRADER="$ROOT/grade_f16.py"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/F16_runs"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

CAP_CORE_MIN=20             # must equal grade_f16.py::CAP_CORE_MIN
END_TIME=40                 # 40 periods; must equal grade_f16.py END_TIME

# name  ny  steps-per-period  ranks
LEVELS=("coarse 56 400 1" "medium 112 800 1" "fine 224 1600 1")
# projected SERIAL seconds per level at 0.6 ms/step -- an ESTIMATE WITH NO
# MEASURED HISTORY, exactly as the pre-registration cost_basis says. Used ONLY
# by the pre-level projected-cap check.
declare -A PROJ_SERIAL_S=( [coarse]=10 [medium]=20 [fine]=39 )
# DECOMPOSITION SEED: REQUIRED FIELD, recorded explicitly.
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
# PATH RESOLUTION against the disk IN THIS INVOCATION
# --------------------------------------------------------------------------
for p in "$CASE_SRC" "$CASE_SRC/0" "$CASE_SRC/constant" "$CASE_SRC/system"; do
  [ -d "$p" ] || { echo "ABORT: required directory does not exist: $p"; exit 1; }
done
for f in "$CASE_SRC/0/U.template" "$CASE_SRC/0/p" \
         "$CASE_SRC/constant/transportProperties" \
         "$CASE_SRC/system/fvSchemes" "$CASE_SRC/system/fvSolution" \
         "$CASE_SRC/system/blockMeshDict.template" \
         "$CASE_SRC/system/controlDict.template" \
         "$EXACT" "$GRADER" "$FOAM_BASHRC"; do
  [ -f "$f" ] || { echo "ABORT: required file does not exist: $f"; exit 1; }
done
say "PATHS RESOLVED against disk in this invocation: 10 files, 4 directories."

# --------------------------------------------------------------------------
# THE INSTRUMENT MUST BE GREEN BEFORE ANY COMPUTE
# --------------------------------------------------------------------------
python3 "$EXACT" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: exact_stokes.py --selftest did not pass; the closed form has not been shown to satisfy the equations the solver integrates and NOTHING may be launched against it"; exit 1; }
python3 "$GRADER" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: grade_f16.py --selftest did not pass; the grading path is not established"; exit 1; }
python3 -O "$GRADER" --selftest > /dev/null 2>&1
[ $? -eq 2 ] || { echo "ABORT: grade_f16.py did not exit 2 under python3 -O; the -O refusal is not armed"; exit 1; }
say "INSTRUMENT GREEN: exact_stokes and grade_f16 selftests pass; grade_f16 exits 2 under -O."

# The value only, never a trailing comment (see run_f15.sh for the defect this
# shape replaces).
CAP_GRADER=$(grep -E '^CAP_CORE_MIN' "$GRADER" | head -1 | sed -E 's/^CAP_CORE_MIN[[:space:]]*=[[:space:]]*([0-9.]+).*/\1/')
python3 -c "import sys; sys.exit(0 if abs(float('$CAP_GRADER') - $CAP_CORE_MIN) < 1e-9 else 1)" \
  || { echo "ABORT: launcher cap $CAP_CORE_MIN disagrees with grade_f16.py CAP_CORE_MIN $CAP_GRADER"; exit 1; }
say "CAP AGREES between launcher and grader: $CAP_CORE_MIN core-minutes."

# nu on disk must be the nu the exact solution was derived from, or the case
# integrates one problem and is graded against another.
python3 - "$CASE_SRC/constant/transportProperties" <<'PY' \
  || { echo "ABORT: constant/transportProperties nu disagrees with exact_stokes.NU"; exit 1; }
import re, sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F16_stokes_second_problem")
import exact_stokes as EX
txt = open(sys.argv[1]).read()
m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", txt, re.M)
if not m:
    sys.exit(1)
sys.exit(0 if abs(float(m.group(1)) - EX.NU) <= 1e-18 else 1)
PY
say "nu ON DISK AGREES with the nu the exact solution was derived from."

if [ "$PREFLIGHT" = "1" ]; then
  say ""
  say "PREFLIGHT ONLY -- ZERO COMPUTE. blockMesh was NOT run."
  say "decomposition method: $DECOMP_METHOD"
  say "decomposition seed:   $DECOMP_SEED"
  for L in "${LEVELS[@]}"; do
    set -- $L
    say "  level $1: 1 x $2 x 1 cells, dt = 1/$3 s, ranks $4, target $RUN_ROOT/$1"
    [ -e "$RUN_ROOT/$1/0" ] && say "    NOTE: $RUN_ROOT/$1/0 EXISTS -- a real launch would REFUSE here."
  done
  exit 0
fi

[ -n "$PREREG_COMMIT" ] \
  || { echo "ABORT: --prereg-commit=<sha> is required. Rule 2: the gate, threshold, cap and label are committed BEFORE the solver starts."; exit 1; }
git -C /home/ubuntu/Certonomous cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "ABORT: $PREREG_COMMIT is not a commit in this repository"; exit 1; }

# shellcheck disable=SC1090
. "$FOAM_BASHRC" || { echo "ABORT: could not source $FOAM_BASHRC"; exit 1; }
command -v icoFoam   > /dev/null || { echo "ABORT: icoFoam not on PATH after sourcing"; exit 1; }
command -v blockMesh > /dev/null || { echo "ABORT: blockMesh not on PATH after sourcing"; exit 1; }

mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
SPENT=0

for L in "${LEVELS[@]}"; do
  set -- $L
  NAME=$1; NY=$2; NSTEP=$3; RANKS=$4
  CD="$RUN_ROOT/$NAME"
  # ---- THE GUARD. REFUSE, NEVER DELETE. --------------------------------
  if [ -e "$CD/0" ]; then
    echo "ABORT: $CD/0 already exists. Standing rule 4's age guard dates every"
    echo "       endTime field against this case's own 0/U, and a pre-existing 0/"
    echo "       destroys that. REFUSED, not deleted."
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
    echo "HALT BEFORE SPENDING: level $NAME is PROJECTED to cross the registered"
    echo "      cap of $CAP_CORE_MIN core-min. The cap is NOT raised. Levels not"
    echo "      launched stay PENDING (CLAUDE.md rule 12)."
    exit 3
  }

  mkdir -p "$CD/system" "$CD/constant" || { echo "ABORT: cannot create $CD"; exit 1; }
  cp "$CASE_SRC/constant/transportProperties" "$CD/constant/" || { echo "ABORT: copy failed"; exit 1; }
  cp "$CASE_SRC/system/fvSchemes" "$CASE_SRC/system/fvSolution" "$CD/system/" || { echo "ABORT: copy failed"; exit 1; }
  sed -e "s/__NY__/$NY/" "$CASE_SRC/system/blockMeshDict.template" > "$CD/system/blockMeshDict" \
    || { echo "ABORT: blockMeshDict templating failed"; exit 1; }
  DT=$(python3 -c "print(repr(1.0/$NSTEP))") || { echo "ABORT: dt computation failed"; exit 1; }
  sed -e "s/__DT__/$DT/" "$CASE_SRC/system/controlDict.template" > "$CD/system/controlDict" \
    || { echo "ABORT: controlDict templating failed"; exit 1; }
  grep -q "endTime         $END_TIME;" "$CD/system/controlDict" \
    || { echo "ABORT: controlDict endTime is not the registered $END_TIME"; exit 1; }

  blockMesh -case "$CD" > "$CD/log.blockMesh" 2>&1 \
    || { echo "ABORT: blockMesh failed at level $NAME; see $CD/log.blockMesh"; exit 1; }
  checkMesh -case "$CD" > "$CD/log.checkMesh" 2>&1 || { echo "ABORT: checkMesh failed at level $NAME"; exit 1; }
  grep -q "Mesh OK" "$CD/log.checkMesh" || { echo "ABORT: checkMesh did not report 'Mesh OK' at level $NAME"; exit 1; }

  # 0/ is written LAST, and 0/U last of all: the age guard dates every endTime
  # field against 0/U. The internalField is the EXACT SOLUTION AT t = 0,
  # cell centre by cell centre -- starting from rest would inject a startup
  # transient whose slowest mode decays at only nu*(pi/H)^2 = 0.158 1/s, the
  # same order as the discretisation error this case exists to measure.
  mkdir -p "$CD/0" || { echo "ABORT: cannot create $CD/0"; exit 1; }
  cp "$CASE_SRC/0/p" "$CD/0/p" || { echo "ABORT: copy failed"; exit 1; }
  python3 - "$CASE_SRC/0/U.template" "$CD/0/U" "$NY" <<'PY' \
    || { echo "ABORT: could not write the exact initial condition into 0/U"; exit 1; }
import sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F16_stokes_second_problem")
import exact_stokes as EX
tmpl, out, ny = sys.argv[1], sys.argv[2], int(sys.argv[3])
dy = EX.H / ny
vals = []
for i in range(ny):
    y = (i + 0.5) * dy
    vals.append("(%.17g 0 0)" % EX.u_exact(y, 0.0))
body = "%d\n(\n%s\n)\n" % (ny, "\n".join(vals))
open(out, "w").write(open(tmpl).read().replace("__INTERNALFIELD__", body))
PY

  say "level $NAME runs SERIAL on $RANKS rank: decomposePar NOT invoked. Decomposition seed: $DECOMP_SEED"
  icoFoam -case "$CD" > "$CD/log.icoFoam" 2>&1
  RC=$?
  echo "$RC" > "$CD/RC.txt"
  probe_box "$NAME-post" "$CD/box_after.txt" > /dev/null
  [ "$RC" -eq 0 ] || { echo "ABORT: icoFoam exited $RC at level $NAME (rc recorded in $CD/RC.txt). A crash is a FINDING until triage says otherwise; it is not retried here."; exit 1; }

  CLOCK=$(grep "ClockTime = " "$CD/log.icoFoam" | tail -1 | sed 's/.*ClockTime = \([0-9][0-9]*\) s.*/\1/')
  [ -n "$CLOCK" ] || { echo "ABORT: no ClockTime in $CD/log.icoFoam; the cap cannot be checked and an unchecked cap is not a cap"; exit 1; }
  SPENT=$(python3 -c "print($SPENT + $CLOCK * $RANKS / 60.0)")
  say "level $NAME COMPLETE: ClockTime ${CLOCK}s x $RANKS ranks -> cumulative $SPENT core-min of $CAP_CORE_MIN"
  say "  QUANTISATION: ClockTime has INTEGER-SECOND resolution, so this level's"
  say "  actual carries +/- $(python3 -c "print(0.5*$RANKS/60.0)") core-min of read-out quantisation alone."
  python3 -c "import sys; sys.exit(0 if $SPENT <= $CAP_CORE_MIN else 1)" || {
    echo "HALT: THE REGISTERED CAP OF $CAP_CORE_MIN CORE-MINUTES HAS BEEN CROSSED"
    echo "      at level $NAME; cumulative spend $SPENT core-min."
    echo "      An overrun STOPS the run. It does not get a new budget"
    echo "      (CLAUDE.md rule 12). Levels not launched stay PENDING."
    exit 3
  }
done

say ""
say "ALL THREE LEVELS COMPLETE. Cumulative spend: $SPENT core-min of $CAP_CORE_MIN."
say "Grading is a SEPARATE invocation:"
say "  python3 $GRADER --prereg-commit=$PREREG_COMMIT"
