#!/usr/bin/env bash
# F17 -- LAUNCHER for Kovasznay flow (simpleFoam, steady, Re = 40, three-level ladder).
#
# FIRES NOTHING WITHOUT --prereg-commit.  `--preflight` runs every guard and
# every path resolution AND STOPS at zero compute, INCLUDING refusing to run
# blockMesh -- a gate a mesher grades is FIRED the moment the mesher runs.
#
# `set -e` DOES NOT GATE IN THIS HARNESS.  Every assertion carries an explicit
# `|| { echo ABORT ...; exit 1; }`.
#
# NO `rm -rf`, NO `rmtree`, ON A CASE DIRECTORY, ANYWHERE IN THIS FILE.  A
# pre-existing `0/` or numeric time directory is REFUSED, never deleted
# (here and again inside build_f17.py).
#
# THE CAP IS CHECKED INCREMENTALLY AFTER EACH LEVEL, in ClockTime x ranks / 60,
# and PROJECTED before each level from this invocation's own box probe.
#
# L-342: RC.txt, box probes and MESH_LINE.txt are written by THIS shell, in
# the same process that ran the solver, never by an attached poller.
set -u
set -o pipefail

ROOT="/home/ubuntu/Certonomous/cases/F17_kovasznay"
CASE_SRC="$ROOT/case"
EXACT="$ROOT/exact_f17.py"
BUILD="$ROOT/build_f17.py"
GRADER="$ROOT/grade_f17.py"
FIO="$ROOT/foam_io_f17.py"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/F17_runs"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

CAP_CORE_MIN=40             # must equal grade_f17.py::CAP_CORE_MIN
END_TIME=4000               # SIMPLE iterations; must equal controlDict endTime

# name  nx  ny  ranks
LEVELS=("coarse 48 32 1" "medium 96 64 1" "fine 192 128 1")
# projected SERIAL seconds per level at 3.55 us/cell/iteration -- a rate read
# from one lab record of a DIFFERENT case (FPE_DIAG BL1: 3520 cells, 2000
# iterations, ClockTime 25 s, serial), applied here; DERIVED, NOT MEASURED on
# this case.  Used ONLY by the pre-level projected-cap check.
declare -A PROJ_SERIAL_S=( [coarse]=22 [medium]=88 [fine]=350 )
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
         "$CASE_SRC/constant/transportProperties" "$CASE_SRC/constant/turbulenceProperties" \
         "$CASE_SRC/system/fvSchemes" "$CASE_SRC/system/fvSolution" \
         "$CASE_SRC/system/blockMeshDict.template" "$CASE_SRC/system/controlDict" \
         "$EXACT" "$BUILD" "$GRADER" "$FIO" "$FOAM_BASHRC"; do
  [ -f "$f" ] || { echo "ABORT: required file does not exist: $f"; exit 1; }
done
say "PATHS RESOLVED against disk in this invocation: 13 files, 4 directories."

# --------------------------------------------------------------------------
# THE INSTRUMENT MUST BE GREEN BEFORE ANY COMPUTE
# --------------------------------------------------------------------------
python3 "$EXACT" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: exact_f17.py --selftest did not pass; the closed form has not been shown to satisfy the equations the solver integrates and NOTHING may be launched against it"; exit 1; }
python3 "$GRADER" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: grade_f17.py --selftest did not pass; the grading path is not established"; exit 1; }
python3 -O "$GRADER" --selftest > /dev/null 2>&1
[ $? -eq 2 ] || { echo "ABORT: grade_f17.py did not exit 2 under python3 -O; the -O refusal is not armed"; exit 1; }
say "INSTRUMENT GREEN: exact_f17 and grade_f17 selftests pass; grade_f17 exits 2 under -O."

CAP_GRADER=$(grep -E '^CAP_CORE_MIN' "$GRADER" | head -1 | sed -E 's/^CAP_CORE_MIN[[:space:]]*=[[:space:]]*([0-9.]+).*/\1/')
python3 -c "import sys; sys.exit(0 if abs(float('$CAP_GRADER') - $CAP_CORE_MIN) < 1e-9 else 1)" \
  || { echo "ABORT: launcher cap $CAP_CORE_MIN disagrees with grade_f17.py CAP_CORE_MIN $CAP_GRADER"; exit 1; }
say "CAP AGREES between launcher and grader: $CAP_CORE_MIN core-minutes."

python3 - "$CASE_SRC/constant/transportProperties" "$CASE_SRC/system/controlDict" "$END_TIME" <<'PY' \
  || { echo "ABORT: nu on disk disagrees with exact_f17.NU, or controlDict endTime is not the registered value"; exit 1; }
import re, sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F17_kovasznay")
import exact_f17 as EX
tp = open(sys.argv[1]).read()
m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
if not m or abs(float(m.group(1)) - EX.NU) > 1e-15:
    sys.exit(1)
cd = open(sys.argv[2]).read()
m = re.search(r"^\s*endTime\s+([0-9]+)\s*;", cd, re.M)
sys.exit(0 if m and int(m.group(1)) == int(sys.argv[3]) == EX.N_ITER else 1)
PY
say "nu ON DISK AGREES with exact_f17.NU; controlDict endTime == registered $END_TIME."

if [ "$PREFLIGHT" = "1" ]; then
  say ""
  say "PREFLIGHT ONLY -- ZERO COMPUTE. blockMesh was NOT run. build_f17.py was NOT called."
  say "decomposition method: $DECOMP_METHOD"
  say "decomposition seed:   $DECOMP_SEED"
  for L in "${LEVELS[@]}"; do
    set -- $L
    say "  level $1: $2 x $3 x 1 cells, $END_TIME iterations, ranks $4, target $RUN_ROOT/$1"
    [ -e "$RUN_ROOT/$1/0" ] && say "    NOTE: $RUN_ROOT/$1/0 EXISTS -- a real launch would REFUSE here."
  done
  [ -e "$RUN_ROOT" ] && say "  NOTE: run root $RUN_ROOT EXISTS." || say "  run root $RUN_ROOT is ABSENT (rule-2 absence condition holds)."
  exit 0
fi

[ -n "$PREREG_COMMIT" ] \
  || { echo "ABORT: --prereg-commit=<sha> is required. Rule 2: the gate, threshold, cap and label are committed BEFORE the solver starts."; exit 1; }
git -C /home/ubuntu/Certonomous cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "ABORT: $PREREG_COMMIT is not a commit in this repository"; exit 1; }

# --------------------------------------------------------------------------
# AMENDMENT 1, 2026-08-26, PRE-FIRST-COMPUTE (rule 2 sec.2b; changes NO gate,
# threshold, cap or label).  CONDITION, CHECKED IN THE WRITING INVOCATION:
# `test -e verification/runs/F17_runs` -> ABSENT; no RC.txt, log.* or numeric
# time directory under cases/F17_kovasznay/.  DEFECT: `set -u` (line 20) was
# in force at this source line, and the OpenFOAM bashrc reads an unbound
# WM_PROJECT_DIR at its line 184, so the launcher shell DIED HERE with no ABORT
# line -- the face that killed F16 attempt 1 today (STATUS.F16.attempt1 rc=1
# 15:56:10Z; L-339).  --preflight returns 0 because it stops before this line
# and check_launcher_can_launch.py does not see this face.  Found by the cfd
# supervisor's check-1 read of feab0ad7.  REPAIR: drop -u around the source
# only, and restore it immediately after.  Driven: `set -u; set +u; . bashrc
# || ABORT; set -u; which simpleFoam blockMesh` resolves both binaries.
# --------------------------------------------------------------------------
set +u
# shellcheck disable=SC1090
. "$FOAM_BASHRC" || { echo "ABORT: could not source $FOAM_BASHRC"; exit 1; }
set -u
command -v simpleFoam > /dev/null || { echo "ABORT: simpleFoam not on PATH after sourcing"; exit 1; }
command -v blockMesh  > /dev/null || { echo "ABORT: blockMesh not on PATH after sourcing"; exit 1; }

mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
SPENT=0

for L in "${LEVELS[@]}"; do
  set -- $L
  NAME=$1; NX=$2; NY=$3; RANKS=$4
  CD="$RUN_ROOT/$NAME"
  # ---- THE GUARD. REFUSE, NEVER DELETE. --------------------------------
  if [ -e "$CD/0" ]; then
    echo "ABORT: $CD/0 already exists. Standing rule 4's age guard dates every"
    echo "       endTime field against this case's own 0/U, and a pre-existing 0/"
    echo "       destroys that. REFUSED, not deleted."
    exit 1
  fi
  while IFS= read -r d; do
    echo "ABORT: $CD already holds numeric time directory $(basename "$d"). REFUSED, not deleted."; exit 1
  done < <(find "$CD" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?' 2>/dev/null)

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

  # ---- BUILD: templating, blockMesh, checkMesh (gates), 0/C, 0/U LAST ----
  python3 "$BUILD" "$CD" --level "$NAME" > "$CD/log.build" 2>&1 \
    || { echo "ABORT: build_f17.py failed at level $NAME; see $CD/log.build"; exit 1; }
  [ -f "$CD/0/U" ] || { echo "ABORT: build did not leave $CD/0/U"; exit 1; }
  [ -f "$CD/MESH_LINE.txt" ] || { echo "ABORT: build did not leave $CD/MESH_LINE.txt"; exit 1; }
  say "level $NAME built: $(cat "$CD/MESH_LINE.txt")"

  say "level $NAME runs SERIAL on $RANKS rank: decomposePar NOT invoked. Decomposition seed: $DECOMP_SEED"
  simpleFoam -case "$CD" > "$CD/log.simpleFoam" 2>&1
  RC=$?
  echo "$RC" > "$CD/RC.txt"
  probe_box "$NAME-post" "$CD/box_after.txt" > /dev/null
  [ "$RC" -eq 0 ] || { echo "ABORT: simpleFoam exited $RC at level $NAME (rc recorded in $CD/RC.txt). A crash is a FINDING until triage says otherwise; it is not retried here."; exit 1; }

  CLOCK=$(grep "ClockTime = " "$CD/log.simpleFoam" | tail -1 | sed 's/.*ClockTime = \([0-9][0-9]*\) s.*/\1/')
  [ -n "$CLOCK" ] || { echo "ABORT: no ClockTime in $CD/log.simpleFoam; the cap cannot be checked and an unchecked cap is not a cap"; exit 1; }
  SPENT=$(python3 -c "print($SPENT + $CLOCK * $RANKS / 60.0)")
  say "level $NAME COMPLETE: ClockTime ${CLOCK}s x $RANKS ranks -> cumulative $SPENT core-min of $CAP_CORE_MIN"
  say "  QUANTISATION: ClockTime has INTEGER-SECOND resolution: +/- $(python3 -c "print(0.5*$RANKS/60.0)") core-min per level."
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
