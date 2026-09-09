#!/usr/bin/env bash
# =============================================================================
# A3FL2 §2ba LAUNCHER -- the nd-only free-conditioning-lever arm for the
# ONERA-M6 rung-3 `-3` adjoint stagnation.  THREE legs, ALL under ONE pinned image.
#
# SUCCESSOR to the CONFOUNDED A3FL1 (curriculum_A3FL1, frozen 865e7c71, NOT A
# RESULT | config-install crash: all 3 legs rc=1 on `pyDAFoam Error: Option
# 'KSPCalcSingularVal' is not a valid PYDAFOAM option`).  A3FL2 DROPS that invalid
# top-level daOption ENTIRELY.  The ONLY lever is `jacMatReOrdering: natural -> nd`
# INSIDE `adjEqnOption` (a placement confirmed valid -- A3FL1's crash was solely the
# top-level KSPCalcSingularVal option, never nd).
# -----------------------------------------------------------------------------
# DRAFT -- PERMISSION NOT_FROZEN.  This launcher REFUSES to stage or launch
# anything while the pre-registration reads NOT_FROZEN and while the frozen-
# instrument md5 / image-digest pins are placeholders.  The dafoam-supervisor
# flips PERMISSION to FROZEN and sets GRADER_MD5 / PREREG_BLOB / IMG / IMG_DIGEST
# at check-1 -- and ONLY after a GREEN pre-flight exercise (a3fl2_exercise.sh, the
# A3FL1 lesson: never freeze a graded arm whose config-install has not been shown
# to be ACCEPTED).  Only then does the G-FREEZE gate open.
#
# THE THREE LEGS (run SEQUENTIALLY, in this order, in the detached child's
# foreground -- each fully completes before the next starts):
#   1. CONTROL     = rung-2 (SRC A3-rung2-n28-tpc1, runScript_tpc1.py), apply_delta:
#                    jacMatReOrdering natural->nd ONLY.  Purpose: does `nd` BREAK a
#                    converging solve?  Cheap.  600 s.
#   2. BASELINE_R3 = rung-3 (SRC A3-rung3-n52, runScript_rung3.py), apply_delta_baseline:
#                    a PURE COPY of the baseline runScript -- NATURAL ordering
#                    UNCHANGED, NO nd, NOTHING added.  Purpose: REPRODUCE the `-3`
#                    stagnation under the arm's OWN pinned image -- the fresh natural
#                    reference that makes the arm section-11-clean BY MEASUREMENT.
#                    Expected: STAGNATION.  1800 s.
#   3. TEST_R3     = rung-3 (SRC A3-rung3-n52, runScript_rung3.py), apply_delta:
#                    jacMatReOrdering natural->nd ONLY.  Purpose: does `nd` clear the
#                    stagnation?  1800 s.
#
# WHY SELF-CONTAINED (the section-11 rationale, resolved): the historical rung-3
# baseline's image was NOT preserved (inferred subpclu:v1, not a surviving launch
# artifact).  Rather than argue the historical image, this arm CARRIES ITS OWN rung-3
# NATURAL baseline leg (BASELINE_R3) under the SAME pinned image the nd TEST_R3 leg
# uses -- so the historical unpinned image is IRRELEVANT and the nd attribution is
# section-11-clean BY MEASUREMENT (Sanaa's exhaustion rule: measured, not argued).
# ALL THREE legs run under the ONE pinned image, so toolchain identity holds trivially.
#
# Each leg runs to completion INSIDE A DAFoam DOCKER CONTAINER (the PROVEN D6RF10
# pattern): `docker run -d` (detached, NO --rm so the container survives fleet death),
# decomposePar + mpirun compute_totals run INSIDE the container (DAFoam / OpenFOAM /
# PETSc live there, NEVER on the host), the memory cap is the container's own
# `--memory=22g` (enforces prereg §6), the deadline is a `timeout -k` INSIDE the
# container, and the leg rc is read from `docker inspect .State.ExitCode` (never `$?`
# of a setsid/timeout line -- the setsid-parent-returns-zero trap is avoided).
# A3FL2_LADDER_DONE is written ONLY AFTER ALL THREE legs finish -- so the detached
# autograder keys on "all legs done", never on "legs spawned".
# =============================================================================
set -u

# =============================================================================
# SELF-DETACH (the PROVEN D6RF10 self-detach pattern).
# FIRST ENTRY (sentinel A3FL2_DETACHED unset): re-exec THIS script ONCE under setsid,
# fully detached (own session, stdin </dev/null, stdout+stderr -> a launch OUT that
# lives OUTSIDE the run root so the rule-4 age guard is NOT tripped by it), echo the
# child pid + OUT path, and exit 0.  That parent `exit 0` is ONLY the detach spawn --
# it is NOT a run verdict (L "setsid parent returns zero"): the ladder's real rc is
# captured INSIDE the detached child by each leg's .rc and the A3FL2_LADDER_DONE line.
#   RE-EXEC'd CHILD (sentinel set): runs the real body -- G-FREEZE gate, digest verify,
#   age guard, staging, and the THREE legs run SEQUENTIALLY IN THE FOREGROUND of this
#   detached orchestrator (no per-leg setsid), so each leg fully completes before the
#   next starts and A3FL2_LADDER_DONE is written ONLY after ALL THREE have finished.
#   An EXIT trap writes a final LADDER_RC=<rc> to the launch OUT (it fires on every
#   exit, incl. the G-FREEZE rc 3 while NOT_FROZEN -- the correct signal nothing ran).
# =============================================================================
if [ -z "${A3FL2_DETACHED:-}" ]; then
  export A3FL2_DETACHED=1
  A3FL2_LAUNCH_OUT="/home/ubuntu/certonomous-runs/a3fl2_launch_$(date -u +%Y%m%dT%H%M%SZ)_$$.out"
  export A3FL2_LAUNCH_OUT
  setsid bash "$0" "$@" > "$A3FL2_LAUNCH_OUT" 2>&1 < /dev/null &
  echo "A3FL2_DETACHED child_pid=$! launch_out=$A3FL2_LAUNCH_OUT"
  echo "  orchestrator now under setsid (survives shell/fleet death); CONTROL -> BASELINE_R3 -> TEST_R3"
  echo "  run SEQUENTIALLY in the child's foreground; ladder rc is captured inside the"
  echo "  child (leg .rc + A3FL2_LADDER_DONE), not by this exit 0."
  exit 0
fi
# re-exec'd child: record the script's OWN final rc to the launch OUT at the end.
trap '_a3fl2_rc=$?; echo "LADDER_RC=$_a3fl2_rc" >> "${A3FL2_LAUNCH_OUT:-/dev/null}"' EXIT

PREREG=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/curriculum_A3FL2/A3FL2_PREREGISTRATION.md
GRADER=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/curriculum_A3FL2/a3fl2_grade.py
RUN_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-A3FL2-onera-m6-free-conditioning-levers
LEDGER="$RUN_ROOT/ledger.txt"

# ---- PINS (baseline runScripts are real; grader + prereg blob + image are set at freeze) ----
BASE_TEST=/home/ubuntu/certonomous-runs/A3-rung3-n52/runScript_rung3.py       # BASELINE_R3 + TEST_R3
BASE_TEST_MD5=1ec70293a56a2cf5a30a889a96832c06
BASE_CTRL=/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1/runScript_tpc1.py   # CONTROL
BASE_CTRL_MD5=edc9e14be7297a442e16f43fdda94fcc
GRADER_MD5="<SET_AT_FREEZE>"    # supervisor pins md5(a3fl2_grade.py) at freeze; G-FREEZE verifies against it
PREREG_BLOB="<SET_AT_FREEZE>"   # supervisor pins git hash-object of the FROZEN A3FL2_PREREGISTRATION.md

# ---- source meshes (staged, never mutated in place) ----
SRC_CTRL=/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1     # 42,120 cells (rung 2)
SRC_R3=/home/ubuntu/certonomous-runs/A3-rung3-n52            # 79,560 cells (rung 3; BOTH R3 legs)
declare -A DEADLINE_S=(["CONTROL"]=600 ["BASELINE_R3"]=1800 ["TEST_R3"]=1800)   # §8: 452*1.25->600 ; 1426*1.25->1800
MEM_CAP="22g"; RANKS=4; KILL_GRACE_S=60

# ---- DAFoam TOOLCHAIN IDENTITY (DAFOAM_CHARTER §11) -- ONE image, pinned by DIGEST ----
# §11: the arm may differ from the rung-3 baseline ONLY in the lever (§4), NEVER in the
# toolchain.  BECAUSE THIS ARM IS SELF-CONTAINED (it carries its OWN rung-3 NATURAL baseline
# leg, BASELINE_R3, under the SAME image as the nd TEST_R3 leg), the historical rung-3
# baseline image is IRRELEVANT: all three legs run under ONE pinned image and §11 holds
# trivially.  The supervisor pins that ONE image at freeze:
#   dafoam-subpclu:v1 @ sha256:ba2d16ab9d575ed3167abe31344aa58fb42fef1a8b27db60baeb505ab9413517
#   -- MEASURED as the rung-1/rung-2 ladder image; present on the host.
# Both fields stay PLACEHOLDERS in this DRAFT; the digest-verify gate below REFUSES until the
# supervisor pins them at freeze, then reads the image's REAL digest and refuses on drift.
IMG="<SET_AT_FREEZE>"          # supervisor pins the ONE image tag (dafoam-subpclu:v1) at freeze (§11)
IMG_DIGEST="<PLACEHOLDER_AT_FREEZE>"   # supervisor pins sha256:ba2d16ab... at freeze; digest-verify refuses on drift

# =============================================================================
# G-FREEZE GATE -- refuse unless the prereg reads FROZEN and every instrument pin is set.
# =============================================================================
gate_refuse() { echo "A3FL2 LAUNCH REFUSED: $1" >&2; exit 3; }

PERM=$(grep -m1 -oE 'PERMISSION:[[:space:]]*[A-Z_]+' "$PREREG" 2>/dev/null | grep -oE '[A-Z_]+$')
[ "$PERM" = "FROZEN" ] || gate_refuse "prereg PERMISSION='$PERM' (not FROZEN) -- G-FREEZE closed (DRAFT)."
case "$GRADER_MD5" in *SET_AT_FREEZE*|"") gate_refuse "GRADER_MD5 is a placeholder -- supervisor pins it at freeze." ;; esac
case "$PREREG_BLOB" in *SET_AT_FREEZE*|"") gate_refuse "PREREG_BLOB is a placeholder -- supervisor pins it at freeze." ;; esac

GOT_GRADER=$(md5sum "$GRADER" 2>/dev/null | cut -d' ' -f1)
[ "$GOT_GRADER" = "$GRADER_MD5" ] || gate_refuse "grader md5 drift: $GOT_GRADER != frozen $GRADER_MD5."
[ "$(md5sum "$BASE_TEST" | cut -d' ' -f1)" = "$BASE_TEST_MD5" ] || gate_refuse "rung-3 baseline runScript md5 drift (BASELINE_R3+TEST_R3)."
[ "$(md5sum "$BASE_CTRL" | cut -d' ' -f1)" = "$BASE_CTRL_MD5" ] || gate_refuse "CONTROL baseline runScript md5 drift."

# ---- DAFoam TOOLCHAIN-IDENTITY gate (§11): ONE image, pinned by DIGEST, verified before any leg ----
case "$IMG" in *SET_AT_FREEZE*|"") gate_refuse "IMG is a placeholder -- supervisor pins the ONE image tag (dafoam-subpclu:v1) at freeze (§11)." ;; esac
case "$IMG_DIGEST" in *PLACEHOLDER_AT_FREEZE*|"") gate_refuse "IMG_DIGEST is a placeholder -- supervisor pins sha256:ba2d16ab... at freeze (§11)." ;; esac
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
[ -n "$GOT_DIGEST" ] || gate_refuse "cannot read digest of $IMG (image absent or docker unavailable)."
[ "$GOT_DIGEST" = "$IMG_DIGEST" ] || gate_refuse "toolchain-identity drift: $IMG got=$GOT_DIGEST != frozen $IMG_DIGEST (§11)."
echo "A3FL2_TOOLCHAIN_IDENTITY_PASS img=$IMG digest=$GOT_DIGEST (ONE image, all three legs)"   # pre-mkdir: stdout

# Age guard (rule 4): the run root must NOT already exist -- 0/ is touched last at launch.
[ -e "$RUN_ROOT" ] && gate_refuse "run root already exists ($RUN_ROOT) -- age guard: refuse to reuse a dir."
mkdir -p "$RUN_ROOT"
echo "A3FL2_LAUNCH_START $(date -u +%FT%TZ) grader_md5=$GOT_GRADER prereg_blob=$PREREG_BLOB img=$IMG@$GOT_DIGEST" >> "$LEDGER"

# =============================================================================
# apply_delta <baseline runScript> <out>  -- the nd lever patch (CONTROL, TEST_R3).
#   THE ONLY CHANGE: jacMatReOrdering "natural" -> "nd" INSIDE adjEqnOption.  NOTHING
#   ELSE (no KSPCalcSingularVal -- that was A3FL1's invalid daOption, dropped).
#   Asserts nd applied and NO natural ordering survived.
# =============================================================================
apply_delta() {
  local src="$1" out="$2"
  sed -E 's/("jacMatReOrdering":[[:space:]]*)"natural"/\1"nd"/' "$src" > "$out"
  grep -q '"jacMatReOrdering": *"nd"' "$out" || gate_refuse "delta(nd): jacMatReOrdering nd not applied in $out"
  grep -q '"jacMatReOrdering": *"natural"' "$out" && gate_refuse "delta(nd): a natural ordering survived in $out"
}

# =============================================================================
# apply_delta_baseline <baseline runScript> <out>  -- the NATURAL baseline (BASELINE_R3).
#   A PURE COPY of the baseline runScript.  jacMatReOrdering STAYS "natural"; NOTHING is
#   added (no KSPCalcSingularVal, no nd).  Asserts natural PRESENT and nd ABSENT.  This is
#   the load-bearing difference from apply_delta.
# =============================================================================
apply_delta_baseline() {
  local src="$1" out="$2"
  cp "$src" "$out"
  grep -q '"jacMatReOrdering": *"natural"' "$out" || gate_refuse "delta(baseline): jacMatReOrdering is not natural in $out"
  grep -q '"jacMatReOrdering": *"nd"' "$out" && gate_refuse "delta(baseline): nd MUST NOT be present in the natural baseline $out"
}

# =============================================================================
# run_leg <LEG> <src mesh> <baseline runScript> <DELTA:nd|natural>
#   Stages the leg (copy the src, apply the leg's delta), writes lever_echo.txt naming the
#   EXACT config, then runs the leg INSIDE the DAFoam DOCKER CONTAINER (the D6RF10 pattern),
#   because DAFoam (dafoam.mphys), OpenFOAM and PETSc live in the container, NEVER on the host.
#   The staged leg dir $d is bind-mounted at /home/dafoamuser/mount/case (the baseline A3 mount
#   path); INSIDE the container we source loadDAFoam.sh, cd to the case, decomposePar -force,
#   then `timeout -k mpirun ... compute_totals`.  `docker run -d` detaches; the memory cap is
#   the container's own --memory=22g (this is what enforces prereg §6); NO --rm, so the
#   container SURVIVES fleet death and its rc is read from `docker inspect .State.ExitCode`
#   (never `$?` of a setsid/timeout line).  run_leg RETURNS ONLY AFTER the container exits, so
#   each leg fully completes before the next.  Writes .t0/.rc/.t1 + the leg log; appends ledger.
# =============================================================================
run_leg() {
  local LEG="$1" SRC="$2" BASE="$3" DELTA="$4"
  local d="$RUN_ROOT/$LEG"
  cp -a "$SRC" "$d"
  case "$DELTA" in
    nd)      apply_delta          "$BASE" "$d/runScript_a3fl2.py" ;;
    natural) apply_delta_baseline "$BASE" "$d/runScript_a3fl2.py" ;;
    *)       gate_refuse "run_leg: unknown DELTA '$DELTA' for $LEG (want nd|natural)" ;;
  esac
  local ord_desc levers_desc
  if [ "$DELTA" = "nd" ]; then
    ord_desc="jacMatReOrdering nd (lever APPLIED)"
    levers_desc="jacMatReOrdering natural->nd ONLY; (adjStateOrdering cell held; NO KSPCalcSingularVal)"
  else
    ord_desc="jacMatReOrdering natural (baseline UNCHANGED -- pure copy, NO nd)"
    levers_desc="jacMatReOrdering natural (unchanged); NOTHING added (no KSPCalcSingularVal, no nd)"
  fi
  {
    echo "leg=$LEG"
    echo "config: $ord_desc"
    echo "levers: $levers_desc"
    echo "baseline=$BASE  src_mesh=$SRC"
    echo "declared_by=launcher (solver DAOption dump + KSP echo CONFIRM; declaration is never proof)"
    echo "image=$IMG digest=$IMG_DIGEST mount=/home/dafoamuser/mount/case memcap=$MEM_CAP ranks=$RANKS deadline_s=${DEADLINE_S[$LEG]}"
  } > "$d/lever_echo.txt"
  # Strip any stale processor* carried in from the source mesh -- decomposePar runs FRESH
  # inside the container (DARhoSimpleCFoam refuses `Case is already decomposed`).
  rm -rf "$d"/processor* 2>/dev/null || true
  touch "$d/0"/* 2>/dev/null; date +%s > "$d/.t0"          # 0/ touched last -> age datum
  local dl=${DEADLINE_S[$LEG]}
  local stamp name
  stamp=$(date -u +%Y%m%dT%H%M%SZ)_$$
  name="a3fl2_${LEG}_${stamp}"
  # DAFoam container: decomposePar + mpirun compute_totals INSIDE (OpenFOAM env).
  # -d detaches; NO --rm (survives fleet death); rc from docker inspect below.
  sudo -n docker run -d --name "$name" \
      --user 0:0 --cpus="$RANKS" --memory="$MEM_CAP" --memory-swap="$MEM_CAP" --oom-score-adj=500 \
      -v "$d":/home/dafoamuser/mount/case "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && cd /home/dafoamuser/mount/case && \
       rm -rf processor* && decomposePar -force > log.decomposePar 2>&1 && \
       timeout -k $KILL_GRACE_S $dl mpirun --allow-run-as-root -np $RANKS python runScript_a3fl2.py -task compute_totals" \
      > /dev/null 2>&1 || { echo "125" > "$d/.rc"; date +%s > "$d/.t1"; echo "LEG=$LEG rc=125 (docker run -d failed to start)" >> "$LEDGER"; return; }
  # POLL until the container exits (the cap lives INSIDE the container; the kernel -- not this
  # loop -- is the verdict). run_leg blocks here until the leg finishes.
  while [ "$(sudo -n docker inspect --format '{{.State.Running}}' "$name" 2>/dev/null)" = "true" ]; do sleep 10; done
  local rc; rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$name" 2>/dev/null)
  [ -n "$rc" ] || rc=125
  sudo -n docker logs "$name" > "$d/a3fl2_$LEG.log" 2>&1   # capture stdout+stderr (no --rm: container kept for rc)
  sudo -n chown -R ubuntu:ubuntu "$d" 2>/dev/null || true  # container ran --user 0:0; restore ownership
  echo "$rc" > "$d/.rc"; date +%s > "$d/.t1"
  echo "LEG=$LEG rc=$rc name=$name delta=$DELTA t0=$(cat "$d/.t0") t1=$(cat "$d/.t1")" >> "$LEDGER"
}

# CONTROL first (cheap; validates nd does not break a working solve), THEN BASELINE_R3
# (natural pure copy, reproduces the -3 wall under THIS image), THEN TEST_R3 (nd on rung 3).
# All SEQUENTIAL in the detached orchestrator's foreground: run_leg returns ONLY after its leg
# finishes, so each leg completes before the next, and A3FL2_LADDER_DONE is written ONLY after
# ALL THREE are done (the autograder keys on "all legs done", not "spawned").
run_leg CONTROL     "$SRC_CTRL" "$BASE_CTRL" nd
run_leg BASELINE_R3 "$SRC_R3"   "$BASE_TEST" natural
run_leg TEST_R3     "$SRC_R3"   "$BASE_TEST" nd
echo "A3FL2_LADDER_DONE $(date -u +%FT%TZ)" >> "$LEDGER"
echo "A3FL2 launcher finished ALL THREE legs (CONTROL -> BASELINE_R3 -> TEST_R3, sequential foreground); autograder keys on A3FL2_LADDER_DONE."
