#!/usr/bin/env bash
# =============================================================================
# A3FL2 MANDATORY PRE-FLIGHT EXERCISE -- the A3FL1 lesson made a gate.
#
# A3FL1 (curriculum_A3FL1, frozen 865e7c71) was FROZEN and LAUNCHED with an
# INVALID daOption (`KSPCalcSingularVal`), and ALL THREE legs died rc=1 at
# config-install time on `pyDAFoam Error: Option 'KSPCalcSingularVal' is not a
# valid PYDAFOAM option` -- a CONFOUNDED NOT A RESULT, ~4.2 core-min wasted, that
# a five-minute smoke would have caught BEFORE the freeze.  A3FL2 therefore
# REQUIRES this exercise to go GREEN before the graded arm is frozen.
#
# WHAT IT DOES: runs EACH of the three legs' configs (the SAME nd / natural
# ordering deltas the graded launcher applies -- nd-only, NO KSPCalcSingularVal)
# in the ONE pinned container, FAR ENOUGH to
#   (a) INSTALL the config (decomposePar + pyDAFoam construction),
#   (b) confirm the daOptions are ACCEPTED (no `not a valid PYDAFOAM option`),
#   (c) reach the FIRST solver iterations (primal + adjoint start),
# via a SMOKE OVERRIDE: gmresMaxIters -> 30 (tiny adjoint cap) and the primal
# controlDict endTime -> 25 (a few outer iters), with a short per-leg deadline
# (180 s).  compute_totals then RETURNS (rc=0) without full convergence -- enough
# to prove the config is valid and nd is accepted.
#
# THIS SCRIPT MEASURES.  IT DOES NOT GRADE AND IT DOES NOT FREEZE.
#   * It does NOT invoke a3fl2_grade.py, does NOT stage it, does NOT read the
#     PERMISSION line, has NO G-FREEZE limb.  The freeze is the graded launcher's
#     discipline, not a measurement's.  It declares NO gate verdict -- only GREEN
#     (config valid, nd accepted) or a per-leg failure the supervisor fixes
#     PRE-FREEZE.
#   * It runs in a SEPARATE exercise root (NOT the graded run root), so nothing it
#     writes touches the graded arm's age guard (rule 4).
#
# SELF-DETACH under setsid (the proven pattern): the plain command re-execs THIS
# script under setsid, fully detached; the exercise's rc/verdict is captured
# INSIDE the child by `docker inspect .State.ExitCode` per leg and the
# A3FL2_EXERCISE_DONE marker -- NOT by the parent's `exit 0` (L "setsid parent
# returns zero").  The `docker run -d` containers survive fleet death.
#
# COST (rule 12): three smokes, each capped at 180 s wall x 4 ranks = 12 core-min
# ceiling; predicted ~10-15 core-min total (option validation + a few primal iters +
# a 30-iter adjoint).  Every smoke is a CPU run far under $25 (pre-authorised).
# =============================================================================
set -u

# --- SELF-DETACH (operational; the proven setsid pattern) --------------------
if [ -z "${A3FL2_EXERCISE_DETACHED:-}" ]; then
  export A3FL2_EXERCISE_DETACHED=1
  A3FL2_EXERCISE_OUT="/home/ubuntu/certonomous-runs/a3fl2_exercise_launch_$(date -u +%Y%m%dT%H%M%SZ)_$$.out"
  export A3FL2_EXERCISE_OUT
  setsid bash "$0" "$@" > "$A3FL2_EXERCISE_OUT" 2>&1 < /dev/null &
  echo "A3FL2_EXERCISE_DETACHED child_pid=$! launch_out=$A3FL2_EXERCISE_OUT"
  echo "  MEASUREMENT ONLY -- no grading, no freeze; per-leg rc via docker inspect,"
  echo "  GREEN/failure via the A3FL2_EXERCISE_DONE marker (not this exit 0)."
  exit 0
fi
# re-exec'd child: record the script's OWN final rc to the launch OUT at the end.
trap '_pf_rc=$?; echo "EXERCISE_RC=$_pf_rc" >> "${A3FL2_EXERCISE_OUT:-/dev/null}"' EXIT

# ---- baseline runScripts (real, md5-verified -- inputs, not freeze pins) ----
BASE_TEST=/home/ubuntu/certonomous-runs/A3-rung3-n52/runScript_rung3.py       # BASELINE_R3 + TEST_R3
BASE_TEST_MD5=1ec70293a56a2cf5a30a889a96832c06
BASE_CTRL=/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1/runScript_tpc1.py   # CONTROL
BASE_CTRL_MD5=edc9e14be7297a442e16f43fdda94fcc
SRC_CTRL=/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1     # 42,120 cells (rung 2)
SRC_R3=/home/ubuntu/certonomous-runs/A3-rung3-n52            # 79,560 cells (rung 3; BOTH R3 legs)

# ---- MEASUREMENT-VARIANT run root -- SEPARATE from the graded run root, so nothing
# ---- here touches the graded age guard (rule 4).
EXERCISE_ROOT=/home/ubuntu/certonomous-runs/A3FL2-PREFLIGHT-EXERCISE
LEDGER="$EXERCISE_ROOT/exercise_ledger.txt"
DONE="$EXERCISE_ROOT/A3FL2_EXERCISE_DONE.txt"

# ---- smoke overrides (measurement only) ----
SMOKE_GMRES_MAXITERS=30      # tiny adjoint cap: the adjoint returns fast, whatever its reason
SMOKE_PRIMAL_ENDTIME=25      # a few primal outer iters -> reach first iterations, return rc=0 fast
DEADLINE_S=180               # short per-leg deadline (rule 12); a trip is a leg to fix PRE-FREEZE
MEM_CAP="22g"; RANKS=4; KILL_GRACE_S=30

# ---- the ONE pinned image (MEASURED as the rung-1/rung-2 ladder image; present on host).
# ---- This is a MEASUREMENT toolchain pin (not a freeze pin): the exercise runs BEFORE the
# ---- freeze, so it carries the real digest and REFUSES on drift, mirroring the D6RF10 exercise.
IMG="dafoam-subpclu:v1"
IMG_DIGEST="sha256:ba2d16ab9d575ed3167abe31344aa58fb42fef1a8b27db60baeb505ab9413517"

INVALID_OPT_RE='not a valid PYDAFOAM option'   # the EXACT A3FL1 crash string this exercise guards against

abort() { echo "A3FL2_EXERCISE_ABORT: $1" >&2; exit 3; }

# ---- md5-verify the baseline inputs (same runScripts the graded arm patches) ----
[ "$(md5sum "$BASE_TEST" | cut -d' ' -f1)" = "$BASE_TEST_MD5" ] || abort "rung-3 baseline runScript md5 drift."
[ "$(md5sum "$BASE_CTRL" | cut -d' ' -f1)" = "$BASE_CTRL_MD5" ] || abort "CONTROL baseline runScript md5 drift."

# ---- image identity by DIGEST (mirror the graded launcher's §11 gate) ----
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
[ -n "$GOT_DIGEST" ] || abort "cannot read digest of $IMG (image absent or docker unavailable)."
[ "$GOT_DIGEST" = "$IMG_DIGEST" ] || abort "toolchain-identity drift: $IMG got=$GOT_DIGEST != $IMG_DIGEST."

# ---- exercise-root guard: fresh dir, never the graded run root.  A re-run needs the prior
# ---- exercise root ARCHIVED by mv, not deleted here.
GRADED_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-A3FL2-onera-m6-free-conditioning-levers
[ "$(realpath -m "$EXERCISE_ROOT")" = "$(realpath -m "$GRADED_ROOT")" ] && abort "exercise root resolves to the GRADED run root -- measurement must not pollute it."
[ -e "$EXERCISE_ROOT" ] && abort "exercise root already exists ($EXERCISE_ROOT) -- archive the prior exercise by mv, do not reuse."
mkdir -p "$EXERCISE_ROOT" || abort "could not create exercise root."
echo "A3FL2_EXERCISE_START $(date -u +%FT%TZ) img=$IMG@$GOT_DIGEST gmresMaxIters=$SMOKE_GMRES_MAXITERS primal_endTime=$SMOKE_PRIMAL_ENDTIME deadline_s=$DEADLINE_S" >> "$LEDGER"

# =============================================================================
# apply_delta / apply_delta_baseline -- IDENTICAL nd-only deltas to the graded launcher.
#   apply_delta:          jacMatReOrdering "natural"->"nd" ONLY (assert nd applied, no natural).
#   apply_delta_baseline: PURE COPY (assert natural present, nd absent).  NOTHING added.
# =============================================================================
apply_delta() {
  local src="$1" out="$2"
  sed -E 's/("jacMatReOrdering":[[:space:]]*)"natural"/\1"nd"/' "$src" > "$out"
  grep -q '"jacMatReOrdering": *"nd"' "$out" || abort "delta(nd): jacMatReOrdering nd not applied in $out"
  grep -q '"jacMatReOrdering": *"natural"' "$out" && abort "delta(nd): a natural ordering survived in $out"
}
apply_delta_baseline() {
  local src="$1" out="$2"
  cp "$src" "$out"
  grep -q '"jacMatReOrdering": *"natural"' "$out" || abort "delta(baseline): jacMatReOrdering is not natural in $out"
  grep -q '"jacMatReOrdering": *"nd"' "$out" && abort "delta(baseline): nd MUST NOT be present in the natural baseline $out"
}

# smoke_override <staged case dir> -- shrink the runScript's gmresMaxIters and the primal
# controlDict endTime so the smoke reaches the first solver iterations and returns rc=0 fast.
# This is a MEASUREMENT variant ONLY; the graded launcher does NEITHER of these.
smoke_override() {
  local d="$1"
  sed -i -E "s/(\"gmresMaxIters\":[[:space:]]*)[0-9]+/\1$SMOKE_GMRES_MAXITERS/" "$d/runScript_a3fl2.py"
  grep -qE "\"gmresMaxIters\":[[:space:]]*$SMOKE_GMRES_MAXITERS" "$d/runScript_a3fl2.py" || abort "smoke: gmresMaxIters override not applied in $d"
  if [ -f "$d/system/controlDict" ]; then
    sed -i -E "s/^endTime[[:space:]]+[0-9.eE+-]+;/endTime         $SMOKE_PRIMAL_ENDTIME;/" "$d/system/controlDict"
    grep -qE "^endTime[[:space:]]+$SMOKE_PRIMAL_ENDTIME;" "$d/system/controlDict" || abort "smoke: primal endTime override not applied in $d"
  fi
}

# =============================================================================
# run_smoke <LEG> <src mesh> <baseline runScript> <DELTA:nd|natural> -- one leg, one container.
#   Stages the leg (copy src, apply the leg's ordering delta, apply the smoke override), then
#   runs decomposePar + mpirun compute_totals INSIDE the pinned container with the short
#   deadline.  Captures rc via `docker inspect .State.ExitCode` (NOT $? of a timeout line),
#   greps the log for the A3FL1 invalid-option crash and for a Traceback, appends the ledger.
# =============================================================================
run_smoke() {
  local LEG="$1" SRC="$2" BASE="$3" DELTA="$4"
  local d="$EXERCISE_ROOT/$LEG"
  cp -a "$SRC" "$d"
  case "$DELTA" in
    nd)      apply_delta          "$BASE" "$d/runScript_a3fl2.py" ;;
    natural) apply_delta_baseline "$BASE" "$d/runScript_a3fl2.py" ;;
    *)       abort "run_smoke: unknown DELTA '$DELTA' for $LEG" ;;
  esac
  smoke_override "$d"
  rm -rf "$d"/processor* 2>/dev/null || true
  local stamp name; stamp=$(date -u +%Y%m%dT%H%M%SZ)_$$; name="a3fl2_ex_${LEG}_${stamp}"
  sudo -n docker run -d --name "$name" \
      --user 0:0 --cpus="$RANKS" --memory="$MEM_CAP" --memory-swap="$MEM_CAP" --oom-score-adj=500 \
      -v "$d":/home/dafoamuser/mount/case "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && cd /home/dafoamuser/mount/case && \
       rm -rf processor* && decomposePar -force > log.decomposePar 2>&1 && \
       timeout -k $KILL_GRACE_S $DEADLINE_S mpirun --allow-run-as-root -np $RANKS python runScript_a3fl2.py -task compute_totals" \
      > /dev/null 2>&1 || { echo "SMOKE=$LEG rc=125 (docker run -d failed to start)" >> "$LEDGER"; echo "125" > "$d/.rc"; return; }
  while [ "$(sudo -n docker inspect --format '{{.State.Running}}' "$name" 2>/dev/null)" = "true" ]; do sleep 5; done
  local rc; rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$name" 2>/dev/null); [ -n "$rc" ] || rc=125
  sudo -n docker logs "$name" > "$d/a3fl2_ex_$LEG.log" 2>&1
  sudo -n chown -R ubuntu:ubuntu "$d" 2>/dev/null || true
  echo "$rc" > "$d/.rc"
  local invalid=no traceback=no
  grep -qE "$INVALID_OPT_RE" "$d/a3fl2_ex_$LEG.log" 2>/dev/null && invalid=yes
  grep -qE 'Traceback \(most recent call last\)' "$d/a3fl2_ex_$LEG.log" 2>/dev/null && traceback=yes
  echo "SMOKE=$LEG rc=$rc delta=$DELTA invalid_option=$invalid traceback=$traceback log=$d/a3fl2_ex_$LEG.log" >> "$LEDGER"
}

# --- the three smokes (same order, same deltas as the graded arm) ---
run_smoke CONTROL     "$SRC_CTRL" "$BASE_CTRL" nd
run_smoke BASELINE_R3 "$SRC_R3"   "$BASE_TEST" natural
run_smoke TEST_R3     "$SRC_R3"   "$BASE_TEST" nd

# =============================================================================
# GREEN CRITERION (verbatim): rc=0 on ALL THREE legs AND `not a valid PYDAFOAM option`
# absent from EVERY leg log.  GREEN => config valid, nd accepted => the supervisor may
# freeze the graded arm.  Any leg tripping (rc!=0, or the invalid-option string present) =>
# NOT GREEN => the config is fixed PRE-FREEZE (the A3FL1 lesson).
# =============================================================================
GREEN=yes
{
  echo "A3FL2_EXERCISE_DONE $(date -u +%FT%TZ)"
  echo "purpose: prove config installs, daOptions ACCEPTED (no '$INVALID_OPT_RE'), first solver iterations reached."
  echo "smoke overrides: gmresMaxIters=$SMOKE_GMRES_MAXITERS primal_endTime=$SMOKE_PRIMAL_ENDTIME deadline_s=$DEADLINE_S (MEASUREMENT ONLY; graded arm does NEITHER)"
  echo "----- per-leg -----"
} > "$DONE"
for LEG in CONTROL BASELINE_R3 TEST_R3; do
  d="$EXERCISE_ROOT/$LEG"; L="$d/a3fl2_ex_$LEG.log"
  rc=$(cat "$d/.rc" 2>/dev/null); [ -n "$rc" ] || rc=NO_RC
  invalid=no; traceback=no
  [ -f "$L" ] && grep -qE "$INVALID_OPT_RE" "$L" && invalid=yes
  [ -f "$L" ] && grep -qE 'Traceback \(most recent call last\)' "$L" && traceback=yes
  echo ">>> $LEG  rc=$rc  invalid_option=$invalid  traceback=$traceback  log=$L" >> "$DONE"
  { [ "$rc" = "0" ] && [ "$invalid" = "no" ]; } || GREEN=no
done
if [ "$GREEN" = "yes" ]; then
  echo "A3FL2_EXERCISE_VERDICT=GREEN -- rc=0 on all three legs AND no '$INVALID_OPT_RE': config valid, nd accepted. The supervisor MAY now freeze the graded arm." >> "$DONE"
else
  echo "A3FL2_EXERCISE_VERDICT=NOT_GREEN -- at least one leg tripped (rc!=0 or invalid-option present). FIX the config PRE-FREEZE (the A3FL1 lesson); do NOT freeze." >> "$DONE"
fi
echo "A3FL2_EXERCISE_VERDICT=$GREEN $(date -u +%FT%TZ)" >> "$LEDGER"
cat "$DONE"
exit 0
