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
# stays cell), writes lever_echo.txt, and runs the leg to completion INSIDE A
# DAFoam DOCKER CONTAINER (the PROVEN D6RF10 pattern, d6rf10_run_arm.sh:420-446):
# `docker run -d` (detached, NO --rm so the container survives fleet death),
# decomposePar + mpirun compute_totals run INSIDE the container (DAFoam / OpenFOAM
# / PETSc live there, NEVER on the host), the memory cap is the container's own
# `--memory=22g` (enforces prereg §6), the deadline is a `timeout -k` INSIDE the
# container, and the leg rc is read from `docker inspect .State.ExitCode` (never
# `$?` of a setsid/timeout line -- the setsid-parent-returns-zero trap is avoided).
# THE DEFECT THIS REWORK CLOSES: the prior draft ran `mpirun -np 4 python
# runScript_a3fl1.py` DIRECTLY ON THE HOST, which has no DAFoam/OpenFOAM -- it
# would crash at `from dafoam.mphys import ...` (module absent on host) and the
# §6 --memory=22g cap was never enforced by the direct-mpirun path.  Both are
# fixed by running each leg in the DAFoam container the baseline A3 runs used
# (baseline logs: `/home/dafoamuser/mount/case`, `DAFoam v5.0.0`, OPENFOAM=2506).
# It appends the ledger .t0/.rc/.t1 rows.  CONTROL fully completes, THEN TEST runs;
# only AFTER BOTH legs finish is the A3FL1_LADDER_DONE marker written -- so the
# detached autograder keys on "both legs done", never on "both legs spawned" (the
# D6RF9-class premature-fire bug this FIX closes).  The two containers run
# SEQUENTIALLY (CONTROL polled to exit, THEN TEST) from the single setsid-detached
# orchestrator.
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
MEM_CAP="22g"; RANKS=4; KILL_GRACE_S=60

# ---- DAFoam TOOLCHAIN IDENTITY (DAFOAM_CHARTER §11) -- pinned by DIGEST, set at freeze ----
# §11: the free-conditioning-levers arm may differ from the A3 rung-3 baseline ONLY in
# the levers (§4), NEVER in the toolchain -- so the container image MUST be the SAME image
# the baseline A3-rung3 run executed under, pinned by DIGEST (sha256:...), never a version
# string.  This LANE COULD NOT DEFINITIVELY DETERMINE that digest, so both fields are
# PLACEHOLDERS and the digest-verify gate below REFUSES until the dafoam-supervisor pins
# them at freeze.  EVIDENCE ON RECORD (for the supervisor's check-1):
#   * TEST baseline  = A3-rung3-n52 (the rung-3 `-3` stagnation; peak 11.65 GiB; endTime
#     4000).  Its run dir carries NO launch/run_arm/drive script, and the DAFoam banner
#     (`DAFoam v5.0.0`, `Build _615aae61d7-20250627 OPENFOAM=2506`) is IDENTICAL across
#     every candidate image, so it cannot discriminate.  The STRONGEST evidence is
#     curriculum_A3R3PC/PREREGISTRATION.md G-11: the rung-3 baseline was the "shipped-mode
#     ... stock preconditioner path" with "the `dafoam-subpclu:v1` banner ABSENT", and G-13
#     treats the IDWarp-rotation arm as SEPARATE (bit-identical to "the shipped path").
#     That points to the SHIPPED image `dafoam/opt-packages:latest`
#     @ sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc -- but this
#     is INFERENCE from campaign prose, NOT a surviving launch artifact, so it is NOT pinned.
#   * CONTROL baseline = A3-rung2-n28-tpc1.  Its OWN lever_echo.txt + run_arm_a.sh EXPLICITLY
#     name `image=dafoam-subpclu:v1` @ sha256:ba2d16ab9d575ed3167abe31344aa58fb42fef1a8b27db60baeb505ab9413517
#     -- a DIFFERENT image from the TEST baseline's inferred SHIPPED path.
#   OPEN §11 QUESTION FOR THE SUPERVISOR: the two legs' baselines used DIFFERENT images, so a
#   single IMG cannot honour §11 toolchain identity for BOTH legs at once; the supervisor must
#   resolve which image each leg runs under (or accept the shipped path for both) at freeze.
#   (Candidate host digests: SHIPPED dafoam/opt-packages:latest 9d45679... ; PATCHED
#   dafoam-idwarp-rot:v1 2927768... ; dafoam-subpclu:v1 ba2d16ab... ; dafoam-subpclu:v2 8352629... .)
IMG="<SET_AT_FREEZE>"          # PLACEHOLDER -- supervisor sets the baseline A3-rung3 image tag at freeze (§11)
IMG_DIGEST="<PLACEHOLDER_AT_FREEZE>"   # PLACEHOLDER -- supervisor pins sha256:... of THAT image at freeze; digest-verify refuses on placeholder or drift

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

# ---- DAFoam TOOLCHAIN-IDENTITY gate (§11): pinned by DIGEST, verified before any leg ----
# Refuse while the image tag or digest is a placeholder; then read the image's REAL digest
# and refuse on drift (mirrors d6rf10_run_arm.sh:373-376).  (Never reached pre-freeze:
# G-FREEZE above aborts first; present so the fixpoint exists once frozen.)
case "$IMG" in *SET_AT_FREEZE*|"") gate_refuse "IMG is a placeholder -- supervisor pins the baseline A3-rung3 image tag at freeze (§11)." ;; esac
case "$IMG_DIGEST" in *PLACEHOLDER_AT_FREEZE*|"") gate_refuse "IMG_DIGEST is a placeholder -- supervisor pins sha256:... of the baseline A3-rung3 image at freeze (§11)." ;; esac
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
[ -n "$GOT_DIGEST" ] || gate_refuse "cannot read digest of $IMG (image absent or docker unavailable)."
[ "$GOT_DIGEST" = "$IMG_DIGEST" ] || gate_refuse "toolchain-identity drift: $IMG got=$GOT_DIGEST != frozen $IMG_DIGEST (§11)."
echo "A3FL1_TOOLCHAIN_IDENTITY_PASS img=$IMG digest=$GOT_DIGEST"   # pre-mkdir: stdout (ledger dir not yet created)

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
#   Runs the leg INSIDE the DAFoam DOCKER CONTAINER (the D6RF10 pattern), because
#   DAFoam (dafoam.mphys), OpenFOAM and PETSc live in the container, NEVER on the
#   host -- a host `python runScript_a3fl1.py` crashes at `from dafoam.mphys
#   import ...`.  The staged leg dir $d is bind-mounted at the baseline mount path
#   /home/dafoamuser/mount/case (the path the baseline A3 runs used, confirmed in
#   their logs), and INSIDE the container we `source loadDAFoam.sh`, `cd` to the
#   case, run `decomposePar -force` (needs the OpenFOAM env -- so it runs HERE, in
#   the container, NOT on the host), then `timeout -k mpirun ... compute_totals`.
#   `docker run -d` detaches; the memory cap is the container's own `--memory=22g`
#   (this is what enforces prereg §6); NO --rm, so the container SURVIVES fleet
#   death and its rc is read from `docker inspect .State.ExitCode` (never `$?` of a
#   setsid/timeout line -- the setsid-parent-returns-zero trap is avoided).  We
#   POLL `docker inspect .State.Running` until false, read the rc, then `docker
#   logs` the container's output into the leg log.  run_leg RETURNS ONLY AFTER the
#   container has exited, so CONTROL fully completes before TEST starts.  Writes
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
    echo "image=$IMG digest=$IMG_DIGEST mount=/home/dafoamuser/mount/case memcap=$MEM_CAP ranks=$RANKS"
  } > "$d/lever_echo.txt"
  # Strip any stale processor* carried in from the source mesh -- decomposePar runs
  # FRESH inside the container (DARhoSimpleCFoam refuses `Case is already decomposed`).
  rm -rf "$d"/processor* 2>/dev/null || true
  touch "$d/0"/* 2>/dev/null; date +%s > "$d/.t0"          # 0/ touched last -> age datum
  local dl=${DEADLINE_S[$LEG]}
  local stamp name
  stamp=$(date -u +%Y%m%dT%H%M%SZ)_$$
  name="a3fl1_${LEG}_${stamp}"
  # DAFoam container: decomposePar + mpirun compute_totals INSIDE (OpenFOAM env).
  # -d detaches; NO --rm (survives fleet death); rc from docker inspect below.
  sudo -n docker run -d --name "$name" \
      --user 0:0 --cpus="$RANKS" --memory="$MEM_CAP" --memory-swap="$MEM_CAP" --oom-score-adj=500 \
      -v "$d":/home/dafoamuser/mount/case "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && cd /home/dafoamuser/mount/case && \
       rm -rf processor* && decomposePar -force > log.decomposePar 2>&1 && \
       timeout -k $KILL_GRACE_S $dl mpirun --allow-run-as-root -np $RANKS python runScript_a3fl1.py -task compute_totals" \
      > /dev/null 2>&1 || { echo "125" > "$d/.rc"; date +%s > "$d/.t1"; echo "LEG=$LEG rc=125 (docker run -d failed to start)" >> "$LEDGER"; return; }
  # POLL until the container exits (the cap lives INSIDE the container; the kernel
  # -- not this loop -- is the verdict). run_leg blocks here until the leg finishes.
  while [ "$(sudo -n docker inspect --format '{{.State.Running}}' "$name" 2>/dev/null)" = "true" ]; do sleep 10; done
  local rc; rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$name" 2>/dev/null)
  [ -n "$rc" ] || rc=125
  sudo -n docker logs "$name" > "$d/a3fl1_$LEG.log" 2>&1   # capture stdout+stderr (no --rm: container kept for rc)
  sudo -n chown -R ubuntu:ubuntu "$d" 2>/dev/null || true  # container ran --user 0:0; restore ownership
  echo "$rc" > "$d/.rc"; date +%s > "$d/.t1"
  echo "LEG=$LEG rc=$rc name=$name t0=$(cat "$d/.t0") t1=$(cat "$d/.t1")" >> "$LEDGER"
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
