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
# COST (rule 12) -- AMENDED 2026-09-10, PRE-COMPUTE, per A3FL2_PREREGISTRATION.md AMENDMENT A1.
# Condition checked: the exercise root /home/ubuntu/certonomous-runs/A3FL2-PREFLIGHT-EXERCISE
# DID NOT EXIST when the amendment was written (verified 2026-09-10T03:52Z), so NO compute had
# run and rule 2's pre-compute amendment clause applies.
# SUPERSEDED figures: most-likely ~10-15 core-min under a 36 core-min ceiling.  Both were
# mpirun-only and BOTH TOO LOW:
#   * 36 = 3 x 180 s x 4 / 60 excluded the 30 s KILL_GRACE_S and the MEASURED ~21 s per-leg
#     container-start / decomposePar / pyDAFoam staging span (all three A3FL1 legs, same image,
#     same case, same 4 ranks:
#     /home/ubuntu/certonomous-runs/CURRICULUM-A3FL1-onera-m6-free-conditioning-levers/ledger.txt);
#   * ~10-15 ignored the MANDATORY pre-GMRES adjoint work each R3 leg does BEFORE the 30-iteration
#     gmresMaxIters smoke cap can apply: on this exercise's own rung-3 source case at 4 ranks
#     (/home/ubuntu/certonomous-runs/A3-rung3-n52/rung3_stage1.log) the primal ends at
#     ExecutionTime 30.97 s (:809) and the dRdWTPC preconditioner assembly runs 49.24 s (:847) ->
#     149.84 s (:861) -- ~119 s of adjoint setup + assembly that the smoke override does NOT
#     shrink, against a 180 s deadline.  Both R3 legs may therefore run to the deadline.
# REGISTERED NOW: most-likely ~34 core-min; HARD CEILING 48 core-min = ceil(3 x (180 + 30 + 21)
# x 4 / 60 = 46.2).  Derived $ at $0.0513/core-h: ~$0.029 most-likely, $0.041 at the ceiling --
# DERIVED, NOT MEASURED (the box cannot read its own billing, COMPUTE_BUDGET_CHARTER §5).  Far
# under the $25/run pre-authorisation.
# THE CEILING IS NOW ENFORCED IN THIS FILE -- it was not before (there was no core-min accounting
# and no cap logic anywhere; DEADLINE_S was the only limiter and it is per-leg wall, not a
# cumulative budget).  Enforcement = per-leg wall -> core-min row in the LEDGER, a running
# cumulative, an IN-LEG budget stop sized from the remaining budget, and a CUMULATIVE CAP-STOP
# that ABORTS the remaining legs.  rule 12: an overrun STOPS the run; it does not get a new budget.
# A budget abort is marked DISTINCTLY (stop_cause / CAP_STOP lines) so it can never be mistaken
# for the config failure the GREEN criterion is about.  THE GREEN CRITERION IS UNTOUCHED.
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

# ---- REGISTERED COST CEILING AND ITS ENFORCING INSTRUMENT (rule 12; A3FL2_PREREGISTRATION.md
# ---- AMENDMENT A1, 2026-09-10, pre-compute).  core-min = wall_s x RANKS / 60.
# ---- 48 = ceil(3 x (DEADLINE_S 180 + KILL_GRACE_S 30 + 21 s measured staging) x RANKS / 60 = 46.2).
# ---- Pattern mirrored from curriculum_D6RF10/d6rf10_run_arm.sh (CUMULATIVE_HARD_STOP_CORE_MIN),
# ---- with ONE deliberate difference: the crossing test is `>=` not `>`, because a leg stopped
# ---- exactly AT the ceiling has already exhausted the budget and the next leg would get a
# ---- zero-second wall allowance anyway.
EXERCISE_CAP_CORE_MIN=48     # HARD ceiling, cumulative across all three legs. NEVER raised in-flight.
CUM_CORE_MIN=0               # running cumulative, core-min
CAP_STOPPED=no               # set yes on a crossing -> remaining legs are NOT RUN (budget abort)

# ---- the ONE pinned image (MEASURED as the rung-1/rung-2 ladder image; present on host).
# ---- This is a MEASUREMENT toolchain pin (not a freeze pin): the exercise runs BEFORE the
# ---- freeze, so it carries the real digest and REFUSES on drift, mirroring the D6RF10 exercise.
IMG="dafoam-subpclu:v1"
IMG_DIGEST="sha256:ba2d16ab9d575ed3167abe31344aa58fb42fef1a8b27db60baeb505ab9413517"

INVALID_OPT_RE='not a valid PYDAFOAM option'   # the EXACT A3FL1 crash string this exercise guards against

abort() { echo "A3FL2_EXERCISE_ABORT: $1" >&2; exit 3; }

# ---- the core-min accounting instrument needs python3 (same dependency d6rf10_run_arm.sh carries).
# ---- Refuse BEFORE the exercise root is created: a run with no cost instrument is a run with an
# ---- unenforced cap, which rule 12 does not allow.
command -v python3 > /dev/null 2>&1 || abort "python3 absent: the core-min accounting / cap-stop instrument cannot run."

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
echo "A3FL2_EXERCISE_START $(date -u +%FT%TZ) img=$IMG@$GOT_DIGEST gmresMaxIters=$SMOKE_GMRES_MAXITERS primal_endTime=$SMOKE_PRIMAL_ENDTIME deadline_s=$DEADLINE_S kill_grace_s=$KILL_GRACE_S ranks=$RANKS cap_core_min=$EXERCISE_CAP_CORE_MIN most_likely_core_min=34" >> "$LEDGER"

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
  # ---- CUMULATIVE CAP-STOP, CHECKED FIRST (rule 12): a previous leg exhausted the registered
  # ---- ceiling, so this leg is NOT RUN.  This is a BUDGET ABORT, NOT a config failure; the
  # ---- distinction is carried by .stop_cause and the CAP_STOP ledger/DONE lines.  The GREEN
  # ---- criterion is untouched -- a leg that never ran simply has no rc=0, so GREEN cannot be
  # ---- claimed, which is correct: the exercise did not prove the config.
  if [ "$CAP_STOPPED" = "yes" ]; then
    mkdir -p "$d" 2> /dev/null || true
    echo "CAP_STOP_NOT_RUN" > "$d/.rc"
    echo "CAP_STOP_NOT_RUN" > "$d/.stop_cause"
    echo "SMOKE=$LEG rc=CAP_STOP_NOT_RUN delta=$DELTA wall_s=0 core_min=0 cumulative_core_min=$CUM_CORE_MIN cap_core_min=$EXERCISE_CAP_CORE_MIN cause=BUDGET_NOT_CONFIG note=leg_not_run_cumulative_cap_stop" >> "$LEDGER"
    return
  fi
  local T0 T1 WALL CM BUDGET_STOP_S NOW budget_stopped=no
  T0=$(date -u +%s)      # covers staging + container: everything this leg costs
  cp -a "$SRC" "$d"
  case "$DELTA" in
    nd)      apply_delta          "$BASE" "$d/runScript_a3fl2.py" ;;
    natural) apply_delta_baseline "$BASE" "$d/runScript_a3fl2.py" ;;
    *)       abort "run_smoke: unknown DELTA '$DELTA' for $LEG" ;;
  esac
  smoke_override "$d"
  rm -rf "$d"/processor* 2>/dev/null || true
  local stamp name; stamp=$(date -u +%Y%m%dT%H%M%SZ)_$$; name="a3fl2_ex_${LEG}_${stamp}"
  # ---- IN-LEG BUDGET STOP (rule 12): the REMAINING budget expressed as this leg's wall ceiling
  # ---- at RANKS ranks.  Without it the cumulative cap could only be observed AFTER a runaway leg
  # ---- had already spent it (decomposePar and container start are NOT covered by the container's
  # ---- own `timeout`).  On the expected path this never binds: leg 1 gets 720 s, leg 2 ~639 s,
  # ---- leg 3 ~438 s, all far above the registered 231 s per-leg span.
  BUDGET_STOP_S=$(python3 -c "print(max(0, int(($EXERCISE_CAP_CORE_MIN - $CUM_CORE_MIN)*60.0/$RANKS)))")
  sudo -n docker run -d --name "$name" \
      --user 0:0 --cpus="$RANKS" --memory="$MEM_CAP" --memory-swap="$MEM_CAP" --oom-score-adj=500 \
      -v "$d":/home/dafoamuser/mount/case "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && cd /home/dafoamuser/mount/case && \
       rm -rf processor* && decomposePar -force > log.decomposePar 2>&1 && \
       timeout -k $KILL_GRACE_S $DEADLINE_S mpirun --allow-run-as-root -np $RANKS python runScript_a3fl2.py -task compute_totals" \
      > /dev/null 2>&1 || {
        T1=$(date -u +%s); WALL=$((T1-T0))
        CM=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
        CUM_CORE_MIN=$(python3 -c "print(round($CUM_CORE_MIN + $CM,3))")
        echo "SMOKE=$LEG rc=125 delta=$DELTA wall_s=$WALL core_min=$CM cumulative_core_min=$CUM_CORE_MIN cap_core_min=$EXERCISE_CAP_CORE_MIN note=docker_run_-d_failed_to_start" >> "$LEDGER"
        echo "125" > "$d/.rc"; return; }
  # ---- POLL until the container exits, WITH the in-leg budget stop.  The container's own
  # ---- `timeout -k 30 180` bounds mpirun only; this bounds the WHOLE leg against the budget.
  while [ "$(sudo -n docker inspect --format '{{.State.Running}}' "$name" 2>/dev/null)" = "true" ]; do
    NOW=$(date -u +%s)
    if [ "$((NOW-T0))" -ge "$BUDGET_STOP_S" ]; then
      budget_stopped=yes
      echo "A3FL2_EXERCISE_BUDGET_STOP leg=$LEG elapsed_s=$((NOW-T0)) leg_wall_ceiling_s=$BUDGET_STOP_S cumulative_core_min_before_leg=$CUM_CORE_MIN cap_core_min=$EXERCISE_CAP_CORE_MIN action=STOP_CONTAINER cause=BUDGET_NOT_CONFIG" >> "$LEDGER"
      sudo -n docker stop -t 10 "$name" > /dev/null 2>&1 || true
      break
    fi
    sleep 5
  done
  local rc; rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$name" 2>/dev/null); [ -n "$rc" ] || rc=125
  sudo -n docker logs "$name" > "$d/a3fl2_ex_$LEG.log" 2>&1
  sudo -n chown -R ubuntu:ubuntu "$d" 2>/dev/null || true
  echo "$rc" > "$d/.rc"
  if [ "$budget_stopped" = "yes" ]; then echo "BUDGET_STOP" > "$d/.stop_cause"; fi
  local invalid=no traceback=no
  grep -qE "$INVALID_OPT_RE" "$d/a3fl2_ex_$LEG.log" 2>/dev/null && invalid=yes
  grep -qE 'Traceback \(most recent call last\)' "$d/a3fl2_ex_$LEG.log" 2>/dev/null && traceback=yes
  # ---- per-leg wall -> core-min accounting + running cumulative (rule 12) ----
  T1=$(date -u +%s); WALL=$((T1-T0))
  CM=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
  CUM_CORE_MIN=$(python3 -c "print(round($CUM_CORE_MIN + $CM,3))")
  echo "SMOKE=$LEG rc=$rc delta=$DELTA invalid_option=$invalid traceback=$traceback wall_s=$WALL core_min=$CM cumulative_core_min=$CUM_CORE_MIN cap_core_min=$EXERCISE_CAP_CORE_MIN budget_stopped=$budget_stopped log=$d/a3fl2_ex_$LEG.log" >> "$LEDGER"
  # ---- CUMULATIVE CAP-STOP (rule 12): overrun stops the run; it does not get a new budget.
  # ---- Mirrors d6rf10_run_arm.sh's D6RF10_CUMULATIVE_HARD_STOP; here it ABORTS the legs that
  # ---- have not yet started (checked at the top of run_smoke), and is marked BUDGET_NOT_CONFIG
  # ---- so it can never be read as the invalid-daOption failure this exercise guards against.
  if [ "$(python3 -c "print(1 if $CUM_CORE_MIN >= $EXERCISE_CAP_CORE_MIN else 0)")" = "1" ]; then
    CAP_STOPPED=yes
    echo "A3FL2_EXERCISE_CUMULATIVE_CAP_STOP cumulative_core_min=$CUM_CORE_MIN >= cap_core_min=$EXERCISE_CAP_CORE_MIN action=ABORT_REMAINING_LEGS cause=BUDGET_NOT_CONFIG" >> "$LEDGER"
  fi
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
BUDGET_ABORTED_LEGS=no    # yes if ANY leg was stopped in flight or never run for BUDGET reasons
{
  echo "A3FL2_EXERCISE_DONE $(date -u +%FT%TZ)"
  echo "purpose: prove config installs, daOptions ACCEPTED (no '$INVALID_OPT_RE'), first solver iterations reached."
  echo "smoke overrides: gmresMaxIters=$SMOKE_GMRES_MAXITERS primal_endTime=$SMOKE_PRIMAL_ENDTIME deadline_s=$DEADLINE_S (MEASUREMENT ONLY; graded arm does NEITHER)"
  echo "----- per-leg -----"
} > "$DONE"
for LEG in CONTROL BASELINE_R3 TEST_R3; do
  d="$EXERCISE_ROOT/$LEG"; L="$d/a3fl2_ex_$LEG.log"
  rc=$(cat "$d/.rc" 2>/dev/null); [ -n "$rc" ] || rc=NO_RC
  stopcause=$(cat "$d/.stop_cause" 2>/dev/null); [ -n "$stopcause" ] || stopcause=none
  invalid=no; traceback=no
  [ -f "$L" ] && grep -qE "$INVALID_OPT_RE" "$L" && invalid=yes
  [ -f "$L" ] && grep -qE 'Traceback \(most recent call last\)' "$L" && traceback=yes
  echo ">>> $LEG  rc=$rc  invalid_option=$invalid  traceback=$traceback  stop_cause=$stopcause  log=$L" >> "$DONE"
  { [ "$rc" = "0" ] && [ "$invalid" = "no" ]; } || GREEN=no
  [ "$stopcause" = "none" ] || BUDGET_ABORTED_LEGS=yes
done
# ---- COST (rule 12; registered in A3FL2_PREREGISTRATION.md AMENDMENT A1, 2026-09-10) ----
{
  echo "----- cost (rule 12) -----"
  echo "A3FL2_EXERCISE_CORE_MIN_TOTAL=$CUM_CORE_MIN cap_core_min=$EXERCISE_CAP_CORE_MIN most_likely_core_min=34 ranks=$RANKS"
  echo "derived_usd=$(python3 -c "print(round($CUM_CORE_MIN/60.0*0.0513,4))") at \$0.0513/core-h -- DERIVED, NOT MEASURED (the box cannot read its own billing, COMPUTE_BUDGET_CHARTER §5)"
  echo "A3FL2_EXERCISE_CAP_STOP=$CAP_STOPPED budget_aborted_legs=$BUDGET_ABORTED_LEGS"
} >> "$DONE"
# ---- CAUSE SEPARATION: a BUDGET abort is never a CONFIG failure.  This block is the ONLY place
# ---- the cap speaks in the DONE file; it does not enter, widen or soften the GREEN criterion.
if [ "$BUDGET_ABORTED_LEGS" = "yes" ]; then
  {
    echo "A3FL2_EXERCISE_CAP_STOPPED -- BUDGET ABORT, NOT A CONFIG FAILURE."
    echo "  The registered $EXERCISE_CAP_CORE_MIN core-min ceiling bound (cumulative $CUM_CORE_MIN core-min): a leg was"
    echo "  stopped in flight (stop_cause=BUDGET_STOP) and/or never run (rc=CAP_STOP_NOT_RUN)."
    echo "  Such a leg says NOTHING about the daOptions.  CONFIG evidence is invalid_option=yes ALONE."
    echo "  rule 12: an overrun STOPS the run; it does not get a new budget.  A re-run needs a"
    echo "  re-registered ceiling in the pre-registration, never a bigger number set in flight."
  } >> "$DONE"
elif [ "$CAP_STOPPED" = "yes" ]; then
  {
    echo "A3FL2_EXERCISE_CAP_CROSSED_AT_END -- all three legs RAN; the cumulative crossed the"
    echo "  registered $EXERCISE_CAP_CORE_MIN core-min ceiling only after the last leg, so NOTHING was aborted."
    echo "  The overrun is REPORTED, not absorbed (rule 12 / COMPUTE_BUDGET_CHARTER §6); the verdict"
    echo "  below is decided by the GREEN criterion alone and is unaffected by this line."
  } >> "$DONE"
fi
if [ "$GREEN" = "yes" ]; then
  echo "A3FL2_EXERCISE_VERDICT=GREEN -- rc=0 on all three legs AND no '$INVALID_OPT_RE': config valid, nd accepted. The supervisor MAY now freeze the graded arm." >> "$DONE"
else
  echo "A3FL2_EXERCISE_VERDICT=NOT_GREEN -- at least one leg tripped (rc!=0 or invalid-option present). FIX the config PRE-FREEZE (the A3FL1 lesson); do NOT freeze." >> "$DONE"
fi
echo "A3FL2_EXERCISE_VERDICT=$GREEN $(date -u +%FT%TZ)" >> "$LEDGER"
echo "A3FL2_EXERCISE_COST core_min_total=$CUM_CORE_MIN cap_core_min=$EXERCISE_CAP_CORE_MIN most_likely_core_min=34 cap_stopped=$CAP_STOPPED budget_aborted_legs=$BUDGET_ABORTED_LEGS $(date -u +%FT%TZ)" >> "$LEDGER"
cat "$DONE"
exit 0
