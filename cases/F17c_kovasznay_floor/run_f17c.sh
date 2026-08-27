#!/usr/bin/env bash
# F17c -- LAUNCHER for Kovasznay flow, Re = 40, on F17b's THREE LEVELS UNCHANGED
# (192x128 / 384x256 / 768x512, simpleFoam, steady) with the ITERATIVE FLOOR
# DERIVED FROM THIS LADDER (L-346) instead of inherited from F17.
#
# EXACTLY ONE THING DIFFERS FROM F17b: the per-level iteration count, 4,000 /
# 8,000 / 48,000 against F17b's single inherited 4,000.
#
# THE CAP IS ALSO ENFORCED INSIDE A LEVEL (`timeout` on the remaining cap),
# because 93.6 % of this ladder sits in ONE level and a between-levels check
# cannot stop an overrun that happens inside it (rule 12).  The meshes, the case
# dictionaries, the discretisation model, both bands and every Class C
# tolerance are F17b's, unchanged.
#
# FIRES NOTHING WITHOUT --prereg-commit.  `--preflight` runs every guard and
# every path resolution AND STOPS at zero compute, INCLUDING refusing to run
# blockMesh -- a gate a mesher grades is FIRED the moment the mesher runs.
#
# `set -e` DOES NOT GATE IN THIS HARNESS (L-314).  Every assertion carries an
# explicit `|| { echo ABORT ...; exit N; }`.
#
# NO `rm -rf`, NO `rmtree`, ON A CASE DIRECTORY, ANYWHERE IN THIS FILE.  A
# pre-existing run root, `0/` or numeric time directory is REFUSED, never
# deleted (here and again inside build_f17c.py).
#
# THE PRE-SPEND PROJECTOR IS proj_f17c.py AND IS NOT THE INLINE FORM.  F17b's
# own `PROJ_SERIAL_S / min(ranks, free_cores) * ranks` read /proc at the moment
# each level started and inflated on a busy box; that is L-349 and it is gone.
# proj_f17c.py takes every input as an argument, reads no clock, no /proc and
# no disk, and its halt path is driven BOTH WAYS by --selftest on injected
# numbers.
#
# L-342: RC.txt, box probes and MESH_LINE.txt are written by THIS shell, in the
# same process that ran the solver, never by an attached poller.  The queue
# runner detaches THIS script; RC is captured on the line after the solver
# returns, inside that detached process, never around a setsid line whose
# parent exits 0 for every outcome.
set -u
set -o pipefail

ROOT="/home/ubuntu/Certonomous/cases/F17c_kovasznay_floor"
CASE_SRC="$ROOT/case"
EXACT="$ROOT/exact_f17c.py"
BUILD="$ROOT/build_f17c.py"
GRADER="$ROOT/grade_f17c.py"
FIO="$ROOT/foam_io_f17c.py"
PROJ="$ROOT/proj_f17c.py"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/F17c_runs"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

CAP_CORE_MIN=370            # must equal grade_f17c.py::CAP_CORE_MIN; 1.4942x the
                            # 247.62 core-min point estimate proj_f17c.py computes.
WRITE_EVERY=100             # must equal exact_f17c.WRITE_EVERY

# name  nx  ny  ranks  iterations      <- iterations are PER LEVEL (L-346)
LEVELS=("coarse 192 128 1 4000" "medium 384 256 1 8000" "fine 768 512 1 48000")
DECOMP_METHOD="none"
DECOMP_SEED="none (identity decomposition: every level runs SERIAL on 1 rank, decomposePar is NOT invoked at any level, there is no partition and no RNG. Contrast F6a attempt 3, where scotch drew a different partition between invocations and moved a convergence verdict)"

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

probe_box() {   # $1 = label, $2 = destination file.  INFRASTRUCTURE ONLY (L-342):
                # nothing this function returns enters any projection or any cap
                # arithmetic.  It is recorded so a later reader can see the box.
  local L1 MEMKB NP
  L1=$(awk '{print $1}' /proc/loadavg)
  MEMKB=$(awk '/^MemAvailable/{print $2}' /proc/meminfo)
  NP=$(nproc)
  printf 'label=%s\nload1=%s\nnproc=%s\nMemAvailable_kB=%s\nutc=%s\nUSED_BY=nothing -- INFRASTRUCTURE observation only (L-342); proj_f17c.py reads no box state\n' \
    "$1" "$L1" "$NP" "$MEMKB" "$(date -u +%FT%TZ)" > "$2"
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
         "$CASE_SRC/system/blockMeshDict.template" "$CASE_SRC/system/controlDict.template" \
         "$EXACT" "$BUILD" "$GRADER" "$FIO" "$PROJ" "$FOAM_BASHRC"; do
  [ -f "$f" ] || { echo "ABORT: required file does not exist: $f"; exit 1; }
done
say "PATHS RESOLVED against disk in this invocation: 14 files, 4 directories."

# --------------------------------------------------------------------------
# THE INSTRUMENT MUST BE GREEN BEFORE ANY COMPUTE
# --------------------------------------------------------------------------
python3 "$EXACT" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: exact_f17c.py --selftest did not pass; the closed form has not been shown to satisfy the equations the solver integrates and NOTHING may be launched against it"; exit 1; }
python3 "$GRADER" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: grade_f17c.py --selftest did not pass; the grading path is not established"; exit 1; }
python3 -O "$GRADER" --selftest > /dev/null 2>&1
[ $? -eq 2 ] || { echo "ABORT: grade_f17c.py did not exit 2 under python3 -O; the -O refusal is not armed"; exit 1; }
python3 "$PROJ" --selftest > /dev/null 2>&1 \
  || { echo "ABORT: proj_f17c.py --selftest did not pass; the pre-spend halt path is not established in both directions"; exit 1; }
python3 -O "$PROJ" --selftest > /dev/null 2>&1
[ $? -eq 2 ] || { echo "ABORT: proj_f17c.py did not exit 2 under python3 -O"; exit 1; }
say "INSTRUMENT GREEN: exact_f17c, grade_f17c and proj_f17c selftests pass; grade_f17c and proj_f17c exit 2 under -O."

CAP_GRADER=$(grep -E '^CAP_CORE_MIN' "$GRADER" | head -1 | sed -E 's/^CAP_CORE_MIN[[:space:]]*=[[:space:]]*([0-9.]+).*/\1/')
python3 -c "import sys; sys.exit(0 if abs(float('$CAP_GRADER') - $CAP_CORE_MIN) < 1e-9 else 1)" \
  || { echo "ABORT: launcher cap $CAP_CORE_MIN disagrees with grade_f17c.py CAP_CORE_MIN $CAP_GRADER"; exit 1; }
say "CAP AGREES between launcher and grader: $CAP_CORE_MIN core-minutes."

# nu on disk, writeInterval, AND the per-level iteration counts -- the launcher's
# LEVELS table must agree with the frozen registration in exact_f17c.ITERS, or
# the run would be graded against a floor it did not use.  That disagreement is
# the F17b defect in a new dress and it is checked here, before any compute.
python3 - "$CASE_SRC/constant/transportProperties" "$CASE_SRC/system/controlDict.template" \
         "$WRITE_EVERY" "coarse:4000" "medium:8000" "fine:48000" <<'PY' \
  || { echo "ABORT: nu on disk disagrees with exact_f17c.NU, or controlDict.template is not the registered template, or the launcher's per-level iteration counts disagree with exact_f17c.ITERS"; exit 1; }
import re, sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F17c_kovasznay_floor")
import exact_f17c as EX
tp = open(sys.argv[1]).read()
m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
if not m or abs(float(m.group(1)) - EX.NU) > 1e-15:
    sys.exit(1)
cd = open(sys.argv[2]).read()
if not re.search(r"^\s*endTime\s+__ENDTIME__\s*;", cd, re.M):
    sys.exit(1)
mw = re.search(r"^\s*writeInterval\s+([0-9]+)\s*;", cd, re.M)
if not mw or int(mw.group(1)) != int(sys.argv[3]) != EX.WRITE_EVERY:
    sys.exit(1)
for spec in sys.argv[4:]:
    name, n = spec.split(":")
    if EX.n_iter(name) != int(n):
        sys.exit(1)
sys.exit(0)
PY
say "nu ON DISK AGREES with exact_f17c.NU; controlDict.template carries __ENDTIME__ and writeInterval $WRITE_EVERY; the launcher's per-level counts 4000/8000/48000 AGREE with exact_f17c.ITERS."

if [ "$PREFLIGHT" = "1" ]; then
  say ""
  say "PREFLIGHT ONLY -- ZERO COMPUTE. blockMesh was NOT run. build_f17c.py was NOT called."
  say "decomposition method: $DECOMP_METHOD"
  say "decomposition seed:   $DECOMP_SEED"
  for L in "${LEVELS[@]}"; do
    set -- $L
    say "  level $1: $2 x $3 x 1 cells, $5 iterations (DERIVED, L-346), ranks $4, target $RUN_ROOT/$1"
  done
  if [ -e "$RUN_ROOT" ]; then
    say "  NOTE: run root $RUN_ROOT EXISTS -- a real launch REFUSES at exit 3."
  else
    say "  run root $RUN_ROOT is ABSENT (rule-2 absence condition holds)."
  fi
  exit 0
fi

[ -n "$PREREG_COMMIT" ] \
  || { echo "ABORT: --prereg-commit=<sha> is required. Rule 2: the gate, threshold, cap and label are committed BEFORE the solver starts."; exit 1; }
git -C /home/ubuntu/Certonomous cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "ABORT: $PREREG_COMMIT is not a commit in this repository"; exit 1; }

# --------------------------------------------------------------------------
# THE RUN ROOT MUST NOT EXIST.  Exit 3, and NOTHING IS DELETED.
# --------------------------------------------------------------------------
if [ -e "$RUN_ROOT" ]; then
  echo "ABORT: run root $RUN_ROOT already exists."
  echo "       Rule 2's absence condition and rule 4's age guard both key on this"
  echo "       tree being created by THIS launch. REFUSED, not deleted, not reused."
  exit 3
fi

# --------------------------------------------------------------------------
# `set -u` is in force and the OpenFOAM bashrc reads an unbound WM_PROJECT_DIR
# at its line 184, which kills the launcher shell with no ABORT line (L-339,
# and the face that killed F16 attempt 1).  Drop -u around the source only.
# --------------------------------------------------------------------------
set +u
# shellcheck disable=SC1090
. "$FOAM_BASHRC" || { echo "ABORT: could not source $FOAM_BASHRC"; exit 1; }
set -u
command -v simpleFoam > /dev/null || { echo "ABORT: simpleFoam not on PATH after sourcing"; exit 1; }
command -v blockMesh  > /dev/null || { echo "ABORT: blockMesh not on PATH after sourcing"; exit 1; }

mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
SPENT=0
COMPLETED='[]'

for L in "${LEVELS[@]}"; do
  set -- $L
  NAME=$1; NX=$2; NY=$3; RANKS=$4; ITERS=$5
  CD="$RUN_ROOT/$NAME"
  CELL_ITERS=$(python3 -c "print($NX * $NY * $ITERS)")

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

  # ---- PRE-SPEND PROJECTION.  Every input is an argument; proj_f17c.py reads
  #      no clock, no /proc and no disk.  The box probe below is recorded and
  #      is NOT consulted by it (L-342, L-349).
  probe_box "$NAME-pre" "$CD/box_before.txt"
  PROJ_OUT=$(python3 "$PROJ" --level "$NAME" --spent "$SPENT" --cap "$CAP_CORE_MIN" --completed "$COMPLETED")
  PROJ_RC=$?
  say "level $NAME: $PROJ_OUT"
  if [ "$PROJ_RC" -eq 3 ]; then
    echo "HALT BEFORE SPENDING: level $NAME is PROJECTED to cross the registered"
    echo "      cap of $CAP_CORE_MIN core-min. The cap is NOT raised. Levels not"
    echo "      launched stay PENDING (CLAUDE.md rule 12)."
    exit 3
  fi
  [ "$PROJ_RC" -eq 0 ] || { echo "ABORT: proj_f17c.py returned $PROJ_RC (refusal, not a halt)"; exit 1; }

  # ---- BUILD: templating, blockMesh, checkMesh (gates), 0/C, 0/U LAST ----
  python3 "$BUILD" "$CD" --level "$NAME" > "$CD/log.build" 2>&1 \
    || { echo "ABORT: build_f17c.py failed at level $NAME; see $CD/log.build"; exit 1; }
  [ -f "$CD/0/U" ] || { echo "ABORT: build did not leave $CD/0/U"; exit 1; }
  [ -f "$CD/MESH_LINE.txt" ] || { echo "ABORT: build did not leave $CD/MESH_LINE.txt"; exit 1; }
  # the endTime this level will actually run to, read back from what was WRITTEN
  WROTE=$(sed -nE 's/^[[:space:]]*endTime[[:space:]]+([0-9]+)[[:space:]]*;.*/\1/p' "$CD/system/controlDict" | head -1)
  [ "$WROTE" = "$ITERS" ] \
    || { echo "ABORT: level $NAME wrote endTime '$WROTE' but the registration says $ITERS. The floor that runs must be the floor that was registered -- that identity is the whole of L-346."; exit 1; }
  say "level $NAME built: $(cat "$CD/MESH_LINE.txt"); endTime read back from the WRITTEN controlDict = $WROTE"

  say "level $NAME runs SERIAL on $RANKS rank: decomposePar NOT invoked. Decomposition seed: $DECOMP_SEED"

  # ---- THE CAP IS ENFORCED *INSIDE* THE LEVEL, NOT ONLY BETWEEN LEVELS. -----
  # CLAUDE.md rule 12: "an overrun STOPS the run; it does not get a new budget."
  # F17b's cap was checked only after each level returned, which is adequate
  # when the longest level is 1,174 wall s and vacuous when it is a projected
  # 14,056.  93.6 % of this ladder's spend sits inside ONE level, so a
  # between-levels check would let the fine level overrun the cap by any factor
  # at all before anything noticed.  The whole remaining cap, converted to wall
  # seconds at this level's rank count, is handed to `timeout`.  A kill leaves
  # an INCOMPLETE level, which rule 4 refuses and the grader reports as NOT A
  # RESULT -- that is the correct outcome of an overrun, not a defect.
  ALLOW_S=$(python3 -c "import math; print(int(math.floor(($CAP_CORE_MIN - $SPENT) * 60.0 / $RANKS)))") \
    || { echo "ABORT: could not compute the remaining-cap wall allowance"; exit 1; }
  [ "$ALLOW_S" -gt 0 ] 2>/dev/null \
    || { echo "HALT: the registered cap of $CAP_CORE_MIN core-min leaves no wall-clock allowance for level $NAME (spent $SPENT). The cap is NOT raised."; exit 3; }
  printf 'level=%s remaining_cap_core_min=%s ranks=%s wall_allowance_s=%s utc=%s\n' \
    "$NAME" "$(python3 -c "print($CAP_CORE_MIN - $SPENT)")" "$RANKS" "$ALLOW_S" "$(date -u +%FT%TZ)" \
    > "$CD/CAP_ALLOWANCE.txt"
  say "level $NAME wall allowance from the REMAINING cap: ${ALLOW_S}s (timeout kills the solver at that point; the cap is never raised)"

  timeout --signal=TERM --kill-after=60 "${ALLOW_S}s" simpleFoam -case "$CD" > "$CD/log.simpleFoam" 2>&1
  RC=$?
  echo "$RC" > "$CD/RC.txt"
  probe_box "$NAME-post" "$CD/box_after.txt"
  if [ "$RC" -eq 124 ] || [ "$RC" -eq 137 ]; then
    echo "HALT: LEVEL $NAME WAS STOPPED BY THE REGISTERED CAP after ${ALLOW_S} wall s"
    echo "      (timeout rc $RC, recorded in $CD/RC.txt). An overrun STOPS the run; it"
    echo "      does not get a new budget (CLAUDE.md rule 12). The level is INCOMPLETE,"
    echo "      rule 4 refuses it, and levels not launched stay PENDING. NOTHING DELETED."
    exit 3
  fi
  [ "$RC" -eq 0 ] || { echo "ABORT: simpleFoam exited $RC at level $NAME (rc recorded in $CD/RC.txt). A crash is a FINDING until triage says otherwise; it is not retried here."; exit 1; }

  CLOCK=$(grep "ClockTime = " "$CD/log.simpleFoam" | tail -1 | sed 's/.*ClockTime = \([0-9][0-9]*\) s.*/\1/')
  [ -n "$CLOCK" ] || { echo "ABORT: no ClockTime in $CD/log.simpleFoam; the cap cannot be checked and an unchecked cap is not a cap"; exit 1; }
  SPENT=$(python3 -c "print($SPENT + $CLOCK * $RANKS / 60.0)")
  COMPLETED=$(python3 -c "
import json
c = json.loads('''$COMPLETED''')
c.append(dict(name='$NAME', cell_iters=$CELL_ITERS, clock_s=float($CLOCK), ranks=$RANKS))
print(json.dumps(c))")
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
