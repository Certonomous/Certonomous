#!/usr/bin/env bash
# F19 -- LAUNCHER for the Sod shock tube (rhoCentralFoam, transient, three-level
# ladder).  Lineage: cases/F18_taylor_green/run_f18.sh.
#
# FIRES NOTHING WITHOUT --prereg-commit.  `--preflight` runs every guard and
# every path resolution AND STOPS at zero compute, INCLUDING refusing to run
# blockMesh -- a gate a mesher grades is FIRED the moment the mesher runs.
#
# `set -e` DOES NOT GATE IN THIS HARNESS.  Every assertion carries an explicit
# `|| { echo ABORT ...; exit 1; }`.  `set -u` is DROPPED around the OpenFOAM
# bashrc source only (L-339: the bashrc reads an unbound WM_PROJECT_DIR at its
# line 184 and would kill this shell silently; F16 attempt 1, 2026-08-26).
#
# NO `rm -rf`, NO `rmtree`, ON A CASE DIRECTORY, ANYWHERE IN THIS FILE.  A
# pre-existing `0/` or numeric time directory in the RUN ROOT or in a LEVEL
# directory is REFUSED, never deleted (here and again inside build_f19.py).
#
# THE CAP IS CHECKED INCREMENTALLY AFTER EACH LEVEL, in ClockTime x ranks / 60,
# and PROJECTED before each level from this invocation's own box probe.
#
# L-342: RC.txt, box probes and MESH_LINE.txt are written by THIS shell, in
# the same process that ran the solver, never by an attached poller.
set -u
set -o pipefail

ROOT="/home/ubuntu/Certonomous/cases/F19_SOD"
CASE_SRC="$ROOT/case"
EXACT="$ROOT/exact_f19.py"
BUILD="$ROOT/build_f19.py"
GRADER="$ROOT/grade_f19.py"
FIO="$ROOT/foam_io_f19.py"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/F19_SOD_runs"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
SOLVER="rhoCentralFoam"

CAP_CORE_MIN=5              # must equal grade_f19.py::CAP_CORE_MIN
END_TIME=0.2                # t_end; must equal controlDict.template endTime and exact_f19.T_END

# name  N  steps  ranks
LEVELS=("coarse 400 1000 1" "medium 800 2000 1" "fine 1600 4000 1")
# projected SERIAL seconds per level from 0.75 us/cell-step + 0.4 ms/step,
# DERIVED from two lab rhoCentralFoam records of DIFFERENT cases on this box:
# verification/runs/F15_runs/{coarse,medium,fine}/log.rhoCentralFoam (10k/40k/160k
# cells: 0.74/0.70/0.69 us/cell-step) and verification/runs/F4_runs/successor_2026-08-26/
# runs/cyl/M*/{coarse,medium,fine}/log.rhoCentralFoam (1k/4k/16k cells: 0.98/0.66/0.65
# us/cell-step; the 1k-cell rows expose ~0.3-0.4 ms/step fixed overhead).  NOT MEASURED
# on this case.  Used ONLY by the pre-level projected-cap check.
declare -A PROJ_SERIAL_S=( [coarse]=1 [medium]=2 [fine]=7 )
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

# REFUSE, NEVER DELETE: a `0/` or numeric time directory as a direct child of $1.
refuse_if_answered() {
  local D="$1"
  if [ -e "$D/0" ]; then
    echo "ABORT: $D/0 already exists. Standing rule 4's age guard dates every"
    echo "       endTime field against this case's own 0/U, and a pre-existing 0/"
    echo "       destroys that. REFUSED, not deleted."
    exit 1
  fi
  while IFS= read -r d; do
    echo "ABORT: $D already holds numeric time directory $(basename "$d"). REFUSED, not deleted."; exit 1
  done < <(find "$D" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?' 2>/dev/null)
}

# --------------------------------------------------------------------------
# PATH RESOLUTION against the disk IN THIS INVOCATION
# --------------------------------------------------------------------------
for p in "$CASE_SRC" "$CASE_SRC/0" "$CASE_SRC/constant" "$CASE_SRC/system"; do
  [ -d "$p" ] || { echo "ABORT: required directory does not exist: $p"; exit 1; }
done
for f in "$CASE_SRC/0/U.template" "$CASE_SRC/0/p.template" "$CASE_SRC/0/T.template" \
         "$CASE_SRC/constant/thermophysicalProperties" "$CASE_SRC/constant/turbulenceProperties" \
         "$CASE_SRC/system/fvSchemes" "$CASE_SRC/system/fvSolution" \
         "$CASE_SRC/system/blockMeshDict.template" "$CASE_SRC/system/controlDict.template" \
         "$EXACT" "$BUILD" "$GRADER" "$FIO" "$FOAM_BASHRC"; do
  [ -f "$f" ] || { echo "ABORT: required file does not exist: $f"; exit 1; }
done
say "PATHS RESOLVED against disk in this invocation: 14 files, 4 directories."

# --------------------------------------------------------------------------
# THE INSTRUMENT MUST BE GREEN BEFORE ANY COMPUTE
# --------------------------------------------------------------------------
python3 "$EXACT" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: exact_f19.py --selftest did not pass; NOTHING may be launched against it"; exit 1; }
python3 "$GRADER" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: grade_f19.py --selftest did not pass; the grading path is not established"; exit 1; }
python3 -O "$GRADER" --selftest > /dev/null 2>&1
[ $? -eq 2 ] || { echo "ABORT: grade_f19.py did not exit 2 under python3 -O; the -O refusal is not armed"; exit 1; }
say "INSTRUMENT GREEN: exact_f19 and grade_f19 selftests pass; grade_f19 exits 2 under -O."

CAP_GRADER=$(grep -E '^CAP_CORE_MIN' "$GRADER" | head -1 | sed -E 's/^CAP_CORE_MIN[[:space:]]*=[[:space:]]*([0-9.]+).*/\1/')
python3 -c "import sys; sys.exit(0 if abs(float('$CAP_GRADER') - $CAP_CORE_MIN) < 1e-9 else 1)" \
  || { echo "ABORT: launcher cap $CAP_CORE_MIN disagrees with grade_f19.py CAP_CORE_MIN $CAP_GRADER"; exit 1; }
say "CAP AGREES between launcher and grader: $CAP_CORE_MIN core-minutes."

python3 - "$CASE_SRC/constant/thermophysicalProperties" "$CASE_SRC/system/controlDict.template" "$END_TIME" <<'PYCHK' \
  || { echo "ABORT: molWeight/Cp on disk disagree with exact_f19, or controlDict.template endTime is not the registered value"; exit 1; }
import re, sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F19_SOD")
import exact_f19 as EX
tp = open(sys.argv[1]).read()
m = re.search(r"molWeight\s+([0-9eE+\-.]+)\s*;", tp)
if not m or abs(float(m.group(1)) - EX.MOL_WEIGHT) > 1e-9:
    sys.exit(1)
m = re.search(r"\bCp\s+([0-9eE+\-.]+)\s*;", tp)
if not m or abs(float(m.group(1)) - EX.CP) > 1e-15:
    sys.exit(1)
cd = open(sys.argv[2]).read()
m = re.search(r"^\s*endTime\s+([0-9.]+)\s*;", cd, re.M)
sys.exit(0 if m and abs(float(m.group(1)) - float(sys.argv[3])) < 1e-12 and abs(EX.T_END - float(sys.argv[3])) < 1e-12 else 1)
PYCHK
say "molWeight AND Cp ON DISK AGREE with exact_f19 (R = 1, gamma = 1.4); controlDict.template endTime == registered $END_TIME."

if [ "$PREFLIGHT" = "1" ]; then
  say ""
  say "PREFLIGHT ONLY -- ZERO COMPUTE. blockMesh was NOT run. build_f19.py was NOT called."
  say "decomposition method: $DECOMP_METHOD"
  say "decomposition seed:   $DECOMP_SEED"
  for L in "${LEVELS[@]}"; do
    set -- $L
    say "  level $1: $2 x 1 x 1 cells, dt = $END_TIME/$3, ranks $4, target $RUN_ROOT/$1"
    [ -e "$RUN_ROOT/$1/0" ] && say "    NOTE: $RUN_ROOT/$1/0 EXISTS -- a real launch would REFUSE here."
  done
  [ -e "$RUN_ROOT" ] && say "  NOTE: run root $RUN_ROOT EXISTS." || say "  run root $RUN_ROOT is ABSENT (rule-2 absence condition holds)."
  exit 0
fi

[ -n "$PREREG_COMMIT" ] \
  || { echo "ABORT: --prereg-commit=<sha> is required. Rule 2: the gate, threshold, cap and label are committed BEFORE the solver starts."; exit 1; }
git -C /home/ubuntu/Certonomous cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "ABORT: $PREREG_COMMIT is not a commit in this repository"; exit 1; }

# `-u` dropped around the source ONLY (L-339; F16 attempt 1 died here silently).
set +u
# shellcheck disable=SC1090
. "$FOAM_BASHRC" || { echo "ABORT: could not source $FOAM_BASHRC"; exit 1; }
set -u
command -v "$SOLVER"  > /dev/null || { echo "ABORT: $SOLVER not on PATH after sourcing"; exit 1; }
command -v blockMesh  > /dev/null || { echo "ABORT: blockMesh not on PATH after sourcing"; exit 1; }

# ---- THE RUN-ROOT GUARD. REFUSE, NEVER DELETE. ------------------------------
[ -e "$RUN_ROOT" ] && refuse_if_answered "$RUN_ROOT"
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
SPENT=0

for L in "${LEVELS[@]}"; do
  set -- $L
  NAME=$1; NN=$2; NSTEP=$3; RANKS=$4
  CD="$RUN_ROOT/$NAME"
  # ---- THE LEVEL GUARD. REFUSE, NEVER DELETE. ------------------------------
  [ -e "$CD" ] && refuse_if_answered "$CD"
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

  # ---- BUILD: templating, blockMesh, checkMesh (gates), 0/C, 0/p, 0/T, 0/U LAST
  python3 "$BUILD" "$CD" --level "$NAME" > "$CD/log.build" 2>&1 \
    || { echo "ABORT: build_f19.py failed at level $NAME; see $CD/log.build"; exit 1; }
  [ -f "$CD/0/U" ] || { echo "ABORT: build did not leave $CD/0/U"; exit 1; }
  [ -f "$CD/MESH_LINE.txt" ] || { echo "ABORT: build did not leave $CD/MESH_LINE.txt"; exit 1; }
  say "level $NAME built: $(cat "$CD/MESH_LINE.txt")"

  say "level $NAME runs SERIAL on $RANKS rank: decomposePar NOT invoked. Decomposition seed: $DECOMP_SEED"
  "$SOLVER" -case "$CD" > "$CD/log.$SOLVER" 2>&1
  RC=$?
  echo "$RC" > "$CD/RC.txt"
  probe_box "$NAME-post" "$CD/box_after.txt" > /dev/null
  [ "$RC" -eq 0 ] || { echo "ABORT: $SOLVER exited $RC at level $NAME (rc recorded in $CD/RC.txt). A crash is a FINDING until triage says otherwise; it is not retried here."; exit 1; }

  CLOCK=$(grep "ClockTime = " "$CD/log.$SOLVER" | tail -1 | sed 's/.*ClockTime = \([0-9][0-9]*\) s.*/\1/')
  [ -n "$CLOCK" ] || { echo "ABORT: no ClockTime in $CD/log.$SOLVER; the cap cannot be checked and an unchecked cap is not a cap"; exit 1; }
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
