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
# and runs the leg to completion under the §8 deadline IN THE FOREGROUND of a
# SINGLE detached orchestrator (self-detach ONCE at entry, the PROVEN D6RF10
# pattern), so rc is captured DIRECTLY -- there is no per-leg setsid and nothing
# wraps `$?` around a setsid line (the setsid-parent-returns-zero trap is avoided).
# It appends the ledger .t0/.rc/.t1 rows.  CONTROL fully completes, THEN TEST runs;
# only AFTER BOTH legs finish is the A3FL1_LADDER_DONE marker written -- so the
# detached autograder keys on "both legs done", never on "both legs spawned" (the
# D6RF9-class premature-fire bug this FIX closes).
# =============================================================================
set -u

# =============================================================================
# SELF-DETACH (adopts the PROVEN D6RF10 self-detach pattern, d6rf10_run_arm.sh
# lines ~78-89).  FIRST ENTRY (sentinel A3FL1_DETACHED unset): re-exec THIS
# script ONCE under setsid, fully detached (own session, stdin </dev/null,
# stdout+stderr -> a launch OUT that lives OUTSIDE the run root so the rule-4 age
# guard is NOT tripped by it), echo the child pid + OUT path, and exit 0.  That
# parent `exit 0` is ONLY the detach spawn -- it is NOT a run verdict (L "setsid
# parent returns zero"): the ladder's real rc/verdict is captured INSIDE the
# detached child by each leg's .rc and the A3FL1_LADDER_DONE ledger line.  There
# is deliberately NO `$?` wrapped around the setsid line.
#   RE-EXEC'd CHILD (sentinel set): runs the real body -- the G-FREEZE gate, the
#   age guard, staging, and the two legs run SEQUENTIALLY IN THE FOREGROUND of
#   this detached orchestrator (no per-leg setsid), so CONTROL fully completes
#   before TEST starts and A3FL1_LADDER_DONE is written ONLY after BOTH legs have
#   actually finished.  An EXIT trap writes a final LADDER_RC=<rc> to the launch
#   OUT (it fires on every exit, incl. the G-FREEZE rc 3 while NOT_FROZEN -- the
#   correct signal that nothing launched).
# =============================================================================
if [ -z "${A3FL1_DETACHED:-}" ]; then
  export A3FL1_DETACHED=1
  A3FL1_LAUNCH_OUT="/home/ubuntu/certonomous-runs/a3fl1_launch_$(date -u +%Y%m%dT%H%M%SZ)_$$.out"
  export A3FL1_LAUNCH_OUT
  setsid bash "$0" "$@" > "$A3FL1_LAUNCH_OUT" 2>&1 < /dev/null &
  echo "A3FL1_DETACHED child_pid=$! launch_out=$A3FL1_LAUNCH_OUT"
  echo "  orchestrator now under setsid (survives shell/fleet death); CONTROL then TEST"
  echo "  run SEQUENTIALLY in the child's foreground; ladder rc is captured inside the"
  echo "  child (leg .rc + A3FL1_LADDER_DONE), not by this exit 0."
  exit 0
fi
# re-exec'd child: record the script's OWN final rc to the launch OUT at the end.
trap '_a3fl1_rc=$?; echo "LADDER_RC=$_a3fl1_rc" >> "${A3FL1_LAUNCH_OUT:-/dev/null}"' EXIT

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
# run_leg <LEG> <src mesh> <baseline runScript>
#   FOREGROUND of the already-detached orchestrator (step-1 self-detach): the leg
#   runs to completion here and rc is captured DIRECTLY (`rc=$?` of the timeout
#   line), so there is NO per-leg setsid and the setsid-parent-returns-zero trap
#   cannot apply.  run_leg RETURNS ONLY AFTER the leg has finished.  Writes
#   .t0/.rc/.t1 + the leg log and appends the ledger row.
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
  # FOREGROUND run: the whole orchestrator is already detached (step-1 self-detach),
  # so the leg needs no further setsid.  rc is captured DIRECTLY from the timeout
  # line; run_leg blocks here until the leg finishes.
  ( cd "$d" && timeout "$dl" mpirun -np "$RANKS" python runScript_a3fl1.py -task compute_totals > "a3fl1_$LEG.log" 2>&1 )
  local rc=$?
  echo "$rc" > "$d/.rc"; date +%s > "$d/.t1"
  echo "LEG=$LEG rc=$rc t0=$(cat "$d/.t0") t1=$(cat "$d/.t1")" >> "$LEDGER"
}

# CONTROL first (cheap, validates the levers do not break a working solve, fixes the
# KSPCalcSingularVal print-token format), THEN TEST.  Both run SEQUENTIALLY IN THE
# FOREGROUND of the detached orchestrator: run_leg returns ONLY after its leg has
# finished, so CONTROL fully completes before TEST starts, and A3FL1_LADDER_DONE is
# written ONLY after BOTH legs are done (the autograder keys on "both legs done",
# never on "both legs spawned").
run_leg CONTROL "$SRC_CTRL" "$BASE_CTRL"
run_leg TEST    "$SRC_TEST" "$BASE_TEST"
echo "A3FL1_LADDER_DONE $(date -u +%FT%TZ)" >> "$LEDGER"
echo "A3FL1 launcher finished BOTH legs (CONTROL then TEST, sequential foreground); autograder keys on A3FL1_LADDER_DONE."
