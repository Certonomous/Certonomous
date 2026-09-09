#!/usr/bin/env bash
# =============================================================================
# A3FL1 §2ba LAUNCHER -- free-conditioning-levers arm (jacMatReOrdering:nd +
# KSPCalcSingularVal:1) for the ONERA-M6 rung-3 `-3` adjoint stagnation.
# -----------------------------------------------------------------------------
# DRAFT -- PERMISSION NOT_FROZEN.  This launcher REFUSES to stage or launch
# anything while the pre-registration reads NOT_FROZEN and while the frozen-
# instrument md5 pins are placeholders.  The dafoam-supervisor flips PERMISSION
# to FROZEN and sets GRADER_MD5 / PREREG_BLOB at check-1; only then does the
# G-FREEZE gate open.
#
# It stages each leg by copying the PINNED baseline runScript and applying the
# §4 delta (jacMatReOrdering natural->nd, KSPCalcSingularVal 0->1; adjStateOrdering
# stays cell), decomposePar -force from a pristine serial 0/, writes lever_echo.txt,
# launches under setsid with the §6 memory cap and the §8 deadline, and CAPTURES rc
# INSIDE the detached wrapper (never around the setsid line -- the
# setsid-parent-returns-zero trap).  It appends the ledger .t0/.rc/.t1 rows and,
# after both legs, an A3FL1_LADDER_DONE marker the detached autograder keys on.
# =============================================================================
set -u

PREREG=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/curriculum_A3FL1/A3FL1_PREREGISTRATION.md
GRADER=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/curriculum_A3FL1/a3fl1_grade.py
RUN_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-A3FL1-onera-m6-free-conditioning-levers
LEDGER="$RUN_ROOT/ledger.txt"

# ---- PINS (baseline runScripts are real; grader + prereg blob are set at freeze) ----
BASE_TEST=/home/ubuntu/certonomous-runs/A3-rung3-n52/runScript_rung3.py
BASE_TEST_MD5=1ec70293a56a2cf5a30a889a96832c06
BASE_CTRL=/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1/runScript_tpc1.py
BASE_CTRL_MD5=edc9e14be7297a442e16f43fdda94fcc
GRADER_MD5="<SET_AT_FREEZE>"          # PLACEHOLDER -- G-FREEZE refuses while unset
PREREG_BLOB="<SET_AT_FREEZE>"         # committed blob sha of the frozen prereg

# ---- source meshes (staged, never mutated in place) ----
SRC_TEST=/home/ubuntu/certonomous-runs/A3-rung3-n52          # 79,560 cells
SRC_CTRL=/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n28_42120   # 42,120 cells
declare -A DEADLINE_S=(["CONTROL"]=600 ["TEST"]=1800)   # §8: 452*1.25 -> 600 ; 1426*1.25 -> 1800
MEM_CAP="22g"; RANKS=4

# =============================================================================
# G-FREEZE GATE -- refuse unless the prereg reads FROZEN and every instrument pin is set.
# =============================================================================
gate_refuse() { echo "A3FL1 LAUNCH REFUSED: $1" >&2; exit 3; }

PERM=$(grep -m1 -oE 'PERMISSION:[[:space:]]*[A-Z_]+' "$PREREG" 2>/dev/null | grep -oE '[A-Z_]+$')
[ "$PERM" = "FROZEN" ] || gate_refuse "prereg PERMISSION='$PERM' (not FROZEN) -- G-FREEZE closed (DRAFT)."
case "$GRADER_MD5" in *SET_AT_FREEZE*|"") gate_refuse "GRADER_MD5 is a placeholder -- supervisor pins it at freeze." ;; esac
case "$PREREG_BLOB" in *SET_AT_FREEZE*|"") gate_refuse "PREREG_BLOB is a placeholder -- supervisor pins it at freeze." ;; esac

GOT_GRADER=$(md5sum "$GRADER" 2>/dev/null | cut -d' ' -f1)
[ "$GOT_GRADER" = "$GRADER_MD5" ] || gate_refuse "grader md5 drift: $GOT_GRADER != frozen $GRADER_MD5."
[ "$(md5sum "$BASE_TEST" | cut -d' ' -f1)" = "$BASE_TEST_MD5" ] || gate_refuse "TEST baseline runScript md5 drift."
[ "$(md5sum "$BASE_CTRL" | cut -d' ' -f1)" = "$BASE_CTRL_MD5" ] || gate_refuse "CONTROL baseline runScript md5 drift."

# Age guard (rule 4): the run root must NOT already exist -- 0/ is touched last at launch.
[ -e "$RUN_ROOT" ] && gate_refuse "run root already exists ($RUN_ROOT) -- age guard: refuse to reuse a dir."
mkdir -p "$RUN_ROOT"
echo "A3FL1_LAUNCH_START $(date -u +%FT%TZ) grader_md5=$GOT_GRADER prereg_blob=$PREREG_BLOB" >> "$LEDGER"

# =============================================================================
# apply_delta <baseline runScript> <out>  -- the §4 lever patch, and NOTHING else.
#   jacMatReOrdering "natural" -> "nd" ; KSPCalcSingularVal off -> add top-level `"KSPCalcSingularVal": 1,`
#   (adjStateOrdering already "cell" in the baseline; unchanged.)
# =============================================================================
apply_delta() {
  local src="$1" out="$2"
  sed -E 's/("jacMatReOrdering":[[:space:]]*)"natural"/\1"nd"/' "$src" > "$out"
  grep -q '"jacMatReOrdering": *"nd"' "$out" || gate_refuse "delta: jacMatReOrdering nd not applied in $out"
  # KSPCalcSingularVal: inject as a top-level daOption if not already present.
  grep -q '"KSPCalcSingularVal"' "$out" || \
    sed -i -E 's/("transonicPCOption":[[:space:]]*1,)/"KSPCalcSingularVal": 1,\n    \1/' "$out"
  grep -q '"KSPCalcSingularVal": *1' "$out" || gate_refuse "delta: KSPCalcSingularVal 1 not applied in $out"
}

# =============================================================================
# run_leg <LEG> <src mesh> <baseline runScript> <gmresMaxIters cap>
#   Detached; rc captured INSIDE the wrapper.  Writes .t0/.rc/.t1 + the leg log.
# =============================================================================
run_leg() {
  local LEG="$1" SRC="$2" BASE="$3"
  local d="$RUN_ROOT/$LEG"
  cp -a "$SRC" "$d"
  apply_delta "$BASE" "$d/runScript_a3fl1.py"
  {
    echo "leg=$LEG"; echo "levers: jacMatReOrdering nd; KSPCalcSingularVal 1; (adjStateOrdering cell held)"
    echo "baseline=$BASE"; echo "declared_by=launcher (solver DAOption dump confirms)"
  } > "$d/lever_echo.txt"
  ( cd "$d" && rm -rf processor* && decomposePar -force > log.decomposePar 2>&1 ) || gate_refuse "$LEG decomposePar failed"
  touch "$d/0"/* 2>/dev/null; date +%s > "$d/.t0"          # 0/ touched last -> age datum
  local dl=${DEADLINE_S[$LEG]}
  setsid bash -c '
    d="$1"; ranks="$2"; mem="$3"; dl="$4"
    cd "$d"
    timeout "$dl" mpirun -np "$ranks" python runScript_a3fl1.py -task compute_totals > a3fl1_'"$LEG"'.log 2>&1
    rc=$?               # rc captured INSIDE the detached wrapper
    echo "$rc" > .rc; date +%s > .t1
    echo "LEG='"$LEG"' rc=$rc t0=$(cat .t0) t1=$(cat .t1)" >> '"$LEDGER"'
  ' _ "$d" "$RANKS" "$MEM_CAP" "$dl"
}

# CONTROL first (cheap, validates the levers do not break a working solve, fixes the
# KSPCalcSingularVal print-token format), THEN TEST.
run_leg CONTROL "$SRC_CTRL" "$BASE_CTRL"
run_leg TEST    "$SRC_TEST" "$BASE_TEST"
echo "A3FL1_LADDER_DONE $(date -u +%FT%TZ)" >> "$LEDGER"
echo "A3FL1 launcher finished staging+launch; autograder keys on A3FL1_LADDER_DONE."
