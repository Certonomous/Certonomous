#!/usr/bin/env bash
# ===========================================================================
# d6r2c_dec4_run_arm.sh -- LAUNCHER for the SUCCESSOR to D6R2C after-item 8
# ===========================================================================
#
# Registered by PREREGISTRATION_AFTER_ITEM8_R2.md sections 5, 8, 9 and 11, and
# IN THE SAME COMMIT, BEFORE ANY CONTAINER STARTS (CLAUDE.md rule 2).
#
# A FORK of d6r2c_after_run_arm.sh, taken from its WORKING-TREE bytes at md5
# c4433db6b60f9c695d785a871a6d3c7d on 2026-09-13.  THAT IS NOT THE md5
# PREREGISTRATION_AFTER_ITEMS.md ADDENDUM 4 A4.5 records (fa58d4829295c6b97e647
# e0a3aa5c422): a peer was mid-edit on the FM5 arm ids at the time.  The
# difference was INSPECTED AND NOT REVERTED (CLAUDE.md rule 10), it is disclosed
# here rather than absorbed, and the successor forks from the bytes that were on
# disk because those are the bytes that were read.  d6r2c_after_run_arm.sh is
# NOT edited by this fork and keeps launching arm FM5 under its own document.
#
# WHAT CHANGED, EXHAUSTIVELY:
#   B1 -- ONE ARM, DEC4, and no fresh-mesh arm.  Item 9 is not registered here.
#   B2 -- the pins point at the successor instruments d6r2c_dec4_decomp.py and
#         d6r2c_dec4_grade.py.  THE FROZEN OPTIMISATION RUNSCRIPT IS PINNED
#         UNCHANGED at 2f2ae43a627146cf8e0f065b035ada4b: the widened incidence
#         bound is an ANALYSIS bound and never touched the optimisation, and
#         this pin is how a reader checks that rather than believing it.
#   B3 -- the registered cap is 416.919 core-min (3.00x the prediction of
#         138.973), derived in the registration's section 8.
#
# DERIVED from cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_run_arm.sh.  The
# G-ROOT.1/2/3 guards, the image digest pin, G-FREEZE, G-COLD, the age datum,
# the delivered-core sampler, the checkpoint rotator and the ledger row are that
# file's design, carried here.  THE REGISTERED DIFFERENCES, and no others:
#
#   A1 -- A NEW RUN ROOT.  The D6R2C root holds the GRADED O_mp artefacts that
#         O_mp_GRADE.json cites by path, and G4/G5 are age-datum and ownership
#         gates over that directory.  It is added to FORBIDDEN_ROOTS here -- the
#         same move the parent made for D6R2, for the same reason.
#   A2 -- THE GRADER IS PINNED TOO.  G-FREEZE covers d6r2c_after_grade.py as
#         well as the producers.  The parent could not pin its own grader
#         because its own grader did not exist (ADDENDUM 3, L-579).
#   A3 -- TWO ARMS, DEC and FM, and FM runs in THREE PHASES in one container.
#   A4 -- NO OPTIMISER.  Neither arm runs IPOPT or an adjoint, so there is no
#         iteration budget, no hot start and no kill-and-resume machinery here.
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call.  Every step
# gates explicitly with `|| { echo ABORT...; exit N; }`.
set -uo pipefail

ITEM=D6R2C-AFTER8-R2
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER8R2-a2-wing-decomposition-retrimmed
AFTER_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER-a2-wing-decomposition-and-freshmesh
PARENT_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable
BASE="${BASE:-$REGISTERED_BASE}"
SRC=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C
FAMILY_DIR=/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing
SURFACE_SRC=/home/ubuntu/certonomous-runs/A2-mach-wing/surfaceMesh.cgns

# ---- the registered md5 pins (PREREGISTRATION_AFTER_ITEMS.md section 11) ----
MD5_RUNSCRIPT=2f2ae43a627146cf8e0f065b035ada4b
MD5_GENWINGMESH=dab5e959187ab2e2bfb4e2c0ded0feb6
MD5_SURFACE=3050ea454c2d0304bafa2c1a80c53b76
MD5_EVALS=2c0b8143caad198cd2e21d8047986aa3
MD5_BASE_POINTS=0fb1935a9b8781b73ac4ccb136e3ec68
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35

RANKS=4
CPUSET=2,3,4,5
MEM_LIMIT=20g
MEM_FOOTPRINT_GB=17
RUN_UID=1000; RUN_GID=1000; EXTRA_GID=1002
CKPT_INTERVAL_S=1800

# ADDENDUM 1 (2026-09-13): DEC2 and FM2 are the RE-RUN ids after the staging
# defect.  THEY INHERIT THE IDENTICAL REGISTERED FIGURES -- 968.1 and 618.0, the
# same numbers looked up under another key.  NO NEW THRESHOLD IS INVENTED, none
# is raised and none is reduced.  The crashed DEC row keeps its directory and is
# never re-seeded (G-COLD, seed_arm) and never re-graded.
#
# ADDENDUM 2 (2026-09-13): DEC3 and FM3 are the RE-RUN ids after the scaler
# defect.  THE SAME RULE APPLIES AND IS APPLIED THE SAME WAY -- 968.1 and 618.0,
# THE IDENTICAL REGISTERED FIGURES looked up under a third key.  NO NEW THRESHOLD
# IS INVENTED, none is raised and none is reduced.  DEC2 keeps its directory and
# its NOT A RESULT row, is never re-seeded and is never re-graded, exactly as DEC.
#
# ADDENDUM 3 (2026-09-13): FM4 is the RE-RUN id after the two item-9 producer
# defects (cgnsutilities `.X` vs `.coords`, and H1 fed the block-structured
# array instead of the registered unique node set).  IT INHERITS THE IDENTICAL
# REGISTERED FIGURE 618.0 under a fourth key.  NO NEW THRESHOLD IS INVENTED.
# FM3 keeps its directory and its NOT A RESULT row, as FM2 and FM do.
# THE REGISTERED CAP (PREREGISTRATION_AFTER_ITEM8_R2.md sections 8 and 8a).
# 416.919 core-min = 3.00x the prediction of 138.973.  NOTHING KILLS ON IT
# (Sanaa directive #17, 2026-09-12): a crossing is REPORTED and the row is
# graded NOT A RESULT, and the cap is never raised.
#
# THIS FILE NO LONGER CARRIES THE FIGURE.  It ASKS THE GRADER, which derives it
# from the registered prediction.  In the first draft this function held 416.919
# and d6r2c_dec4_grade.py held 407.303, from a superseded cost model, and NOTHING
# COMPARED THEM -- a cap that exists as a literal in two files is two things that
# can drift.  The canonical value is CALLED, never re-spelled (L-221/L-222), the
# same discipline this launcher's guard_box already applies to swap_offenders().
cap_core_min() { python3 "$SRC/d6r2c_dec4_grade.py" --print-cap "$1" 2>/dev/null; }

# ===========================================================================
# G-ROOT.1 -- BASE must be THIS item's registered run root, normalised
# ===========================================================================
guard_root() {
  local BASE_REAL REG_REAL forb
  BASE_REAL=$(realpath -m "$1"); REG_REAL=$(realpath -m "$REGISTERED_BASE")
  if [ "$BASE_REAL" != "$REG_REAL" ]; then
    echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
    echo "  given: $BASE_REAL"; echo "  registered: $REG_REAL"; return 3
  fi
  # G-ROOT.2 -- the roots this file must NEVER write.  THE D6R2C ROOT IS FIRST
  # and is the reason the list exists here: it holds the GRADED O_mp artefacts
  # that O_mp_GRADE.json cites by path, and this item reads them, never writes.
  local FORBIDDEN="$PARENT_BASE
$AFTER_BASE
/home/ubuntu/certonomous-runs/CURRICULUM-D6R2-a2-wing-multipoint-transonic
/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint
/home/ubuntu/certonomous-runs/A2-mach-wing
/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing"
  while IFS= read -r forb; do
    [ -z "$forb" ] && continue
    if [ "$BASE_REAL" = "$(realpath -m "$forb")" ]; then
      echo "ABORT G-ROOT.2 BASE resolves to a root this item must never write: $forb"; return 3
    fi
  done <<< "$FORBIDDEN"
  # G-ROOT.3 -- the ledger must belong to this item and to no other
  if [ -f "$1/ledger.txt" ]; then
    local FOREIGN
    FOREIGN=$(grep -a "^ITEM=" "$1/ledger.txt" 2>/dev/null | grep -av "^ITEM=$ITEM$" | head -1)
    if [ -n "$FOREIGN" ]; then
      echo "ABORT G-ROOT.3 ledger at $1/ledger.txt carries another item: $FOREIGN"; return 3
    fi
  fi
  echo "D6R2C_DEC4_G_ROOT_PASS item=$ITEM base=$BASE_REAL"
  return 0
}

md5_is() { [ "$(md5sum "$1" | cut -d' ' -f1)" = "$2" ]; }

# ===========================================================================
# G-FREEZE -- the instruments that run ARE the frozen instruments.
# A2: THE GRADER IS PINNED TOO.
# ===========================================================================
guard_freeze() {
  local f got want bad=0
  md5_is "$SRC/d6r2c_opt_runScript.py" "$MD5_RUNSCRIPT" || {
    echo "ABORT G-FREEZE d6r2c_opt_runScript.py md5 mismatch"; bad=1; }
  md5_is "$PARENT_BASE/O_mp/d6r2c_evals.jsonl" "$MD5_EVALS" || {
    echo "ABORT G-FREEZE the inherited O_mp record md5 mismatch -- the artefact this"
    echo "  registration pinned is not the artefact on disk"; bad=1; }
  md5_is "$PARENT_BASE/base/constant/polyMesh/points.gz" "$MD5_BASE_POINTS" || {
    echo "ABORT G-FREEZE the base mesh points md5 mismatch"; bad=1; }
  # the three instruments this registration froze, pinned by the PREREGISTRATION
  for f in d6r2c_dec4_grade.py d6r2c_dec4_decomp.py; do
    want=$(grep -m1 "^# PIN $f " "$0" | awk '{print $4}')
    [ -n "$want" ] || { echo "ABORT G-FREEZE no pin recorded for $f"; bad=1; continue; }
    got=$(md5sum "$SRC/$f" | cut -d' ' -f1)
    [ "$got" = "$want" ] || { echo "ABORT G-FREEZE $f md5=$got want=$want"; bad=1; }
  done
  [ $bad -eq 0 ] || return 4
  echo "D6R2C_DEC4_G_FREEZE_PASS"
  return 0
}

# ===========================================================================
# BOX HYGIENE -- a LAUNCH PRECONDITION.  It refuses to START and never stops
# anything running (Sanaa item 18 read with her directive #17).
# ===========================================================================
guard_box() {
  local load1 nproc avail_gb swapoff
  load1=$(awk '{print $1}' /proc/loadavg); nproc=$(nproc)
  avail_gb=$(awk '/MemAvailable/{printf "%d", $2/1048576}' /proc/meminfo)
  awk -v l="$load1" -v n="$nproc" 'BEGIN{exit !(l>n)}' && {
    echo "ABORT G-BOX load1=$load1 > nproc=$nproc -- launch precondition, nothing is stopped"; return 3; }
  # ---- ADDENDUM 5 (2026-09-13): THE SWAP LIMB MEASURES WHAT HER ITEM 18 NAMES.
  # Sanaa's item 18: "swap use above zero FOR SOLVER JOBS is a defect."  The lab's
  # canonical implementation of that sentence is scripts/queue_runner.py
  # `swap_offenders()` (lines 915-943), which reads per-process VmSwap from
  # /proc/<pid>/status and counts SOLVER PROCESSES ONLY; gate E is defined at
  # line 102 as "any solver process has VmSwap > 0".
  #
  # THIS GUARD PREVIOUSLY READ `SwapTotal - SwapFree`, WHICH IS NOT THAT QUANTITY.
  # It counts a SwapCached slot that no process holds.  Measured 2026-09-13:
  # SwapTotal-SwapFree = 8 kB, SwapCached = 8 kB, 131 processes reporting VmSwap,
  # TOTAL 0 kB, NONE above zero, 551 GB available, load 43 of 96 -- and this guard
  # refused arm FM5 on it.
  #
  # THE THRESHOLD IS UNCHANGED AT > 0.  ONLY THE MEASURED QUANTITY MOVED.
  # The canonical function is CALLED, never re-spelled (L-221/L-222), so the two
  # cannot drift; and a guard that CANNOT MEASURE REFUSES rather than passing
  # quietly, which is the same discipline as dv_divisor_for().
  swapoff=$(python3 -c "
import sys
sys.path.insert(0, '/home/ubuntu/Certonomous/scripts')
from queue_runner import swap_offenders
for o in swap_offenders():
    print('%(pid)d %(name)s %(vmswap_kb)d' % o)
") || {
    echo "ABORT G-BOX cannot read the canonical swap gate (scripts/queue_runner.py"
    echo "  swap_offenders) -- a guard that cannot measure REFUSES rather than passes"; return 3; }
  if [ -n "$swapoff" ]; then
    echo "ABORT G-BOX solver processes holding swap (Sanaa item 18) -- launch precondition,"
    echo "  nothing is stopped.  THE OFFENDERS, NAMED:"
    echo "$swapoff" | while read -r p n k; do echo "    pid=$p name=$n VmSwap=${k} kB"; done
    return 3
  fi
  [ "$avail_gb" -lt "$MEM_FOOTPRINT_GB" ] && {
    echo "ABORT G-MEM MemAvailable=${avail_gb}G < declared footprint ${MEM_FOOTPRINT_GB}G"; return 3; }
  echo "D6R2C_DEC4_G_BOX_PASS load1=$load1 nproc=$nproc solver_swap_offenders=0 avail_gb=$avail_gb"
  return 0
}

# ===========================================================================
# SEED -- base/ copied read-only and HASHED, inputs staged BEFORE the age datum
# ===========================================================================
seed_arm() {
  local ARM="$1" WORK="$BASE/$ARM"
  mkdir -p "$WORK" || return 5
  # G-COLD -- a guard refuses a case where 0 or a time dir already exists
  for bad in "$WORK/0" "$WORK/constant" "$WORK/mp04" "$WORK/d6r2c_dec4.jsonl"; do
    [ -e "$bad" ] && { echo "ABORT G-COLD $bad exists"; return 5; }
  done
  cp -a "$PARENT_BASE/base/." "$WORK/" || return 5
  md5_is "$WORK/constant/polyMesh/points.gz" "$MD5_BASE_POINTS" || {
    echo "ABORT G-SEED the seeded mesh is not the registered base mesh"; return 5; }
  # ---- REPAIR 1 (ADDENDUM 1, 2026-09-13): THE THREE MULTIPOINT CASE COPIES ----
  # d6r2c_opt_runScript.py lines 7-8 register mp04/mp05/mp06 as "a full copy of
  # the case, staged by the launcher", and the parent d6r2c_run_arm.sh:195 does
  # exactly this loop.  The A1-A4 derivation dropped it, so prob.setup() died in
  # chdir('mp04') on all four ranks before one primal ran (arm DEC, stamp
  # 20260913T051014Z_1341011, graded NOT A RESULT, 0.533 core-min).
  # decomposePar is NOT run here -- THE PARENT DOES NOT RUN IT EITHER; DAFoam
  # decomposes inside the container, and the processor* assert below is the
  # parent's own G-COLD check that nothing pre-decomposed is staged.
  for mp in mp04 mp05 mp06; do
    cp -a "$PARENT_BASE/base" "$WORK/$mp" || { echo "ABORT G-SEED stage $mp"; return 5; }
    test -z "$(ls -d "$WORK/$mp"/processor* 2>/dev/null)" || {
      echo "ABORT G-COLD $mp processor* present"; return 5; }
    md5_is "$WORK/$mp/constant/polyMesh/points.gz" "$MD5_BASE_POINTS" || {
      echo "ABORT G-SEED $mp is not the registered base mesh"; return 5; }
  done
  # inputs, staged BEFORE the age datum so the age guard dates them as INPUTS
  cp "$PARENT_BASE/O_mp/d6r2c_evals.jsonl" "$WORK/d6r2c_evals_final.jsonl" || return 5
  cp "$PARENT_BASE/O_mp/d6r2c_x0.json"     "$WORK/d6r2c_x0_final.json"     || return 5
  cp "$SRC/d6r2c_opt_runScript.py" "$SRC/d6r2c_dec4_decomp.py" "$WORK/" || return 5
  test -f "$WORK/0/U" || { echo "ABORT G-COLD 0/U missing after seed"; return 5; }
  touch "$WORK/0/U"
  AGE_DATUM=$(stat -c '%Y' "$WORK/0/U")
  echo "$AGE_DATUM" > "$WORK/.d6r2c_age_datum"
  echo "D6R2C_DEC4_G_COLD_PASS arm=$ARM age_datum_epoch=$AGE_DATUM"
  return 0
}

# ===========================================================================
# THE CHECKPOINT ROTATOR (Sanaa Checkpoints item 1; the parent's L6).
# Every CKPT_INTERVAL_S wall, the arm's record + design vector + the latest
# primal time from every mp0*/processor* are copied to ckpt/<UTC>/.  THE LAST
# TWO ARE KEPT and older ones purged.
# ===========================================================================
rotator() {
  local WORK="$1"
  while :; do
    sleep "$CKPT_INTERVAL_S"
    [ -d "$WORK" ] || return 0
    local D="$WORK/ckpt/$(date -u +%Y%m%dT%H%M%SZ)"
    mkdir -p "$D"
    for f in d6r2c_dec4.jsonl d6r2c_x0_final.json; do
      [ -f "$WORK/$f" ] && cp -a "$WORK/$f" "$D/" 2>/dev/null
    done
    for mp in "$WORK"/mp0*; do
      [ -d "$mp" ] || continue
      for pr in "$mp"/processor*; do
        [ -d "$pr" ] || continue
        local latest
        latest=$(ls -1d "$pr"/[0-9]* 2>/dev/null | sort -t/ -k1 | tail -1)
        [ -n "$latest" ] && { mkdir -p "$D/$(basename "$mp")/$(basename "$pr")"; \
          cp -a "$latest" "$D/$(basename "$mp")/$(basename "$pr")/" 2>/dev/null; }
      done
    done
    ls -1d "$WORK"/ckpt/* 2>/dev/null | sort | head -n -2 | xargs -r rm -rf
  done
}

# ===========================================================================
# MAIN
# ===========================================================================
ARM="${1:-}"; IMG="${2:-}"
if [ "$ARM" = "--selftest" ]; then
  rc=0
  guard_root /tmp/definitely-not-the-root >/dev/null 2>&1 && { echo "SELFTEST FAIL G-ROOT.1 accepted a wrong root"; rc=1; } || echo "SELFTEST ok G-ROOT.1 refuses a wrong root"
  BASE_SAVE=$REGISTERED_BASE; REGISTERED_BASE=$PARENT_BASE
  guard_root "$PARENT_BASE" >/dev/null 2>&1 && { echo "SELFTEST FAIL G-ROOT.2 accepted the GRADED parent root"; rc=1; } || echo "SELFTEST ok G-ROOT.2 refuses the graded parent root"
  REGISTERED_BASE=$BASE_SAVE
  guard_freeze >/dev/null 2>&1 && echo "SELFTEST ok G-FREEZE passes on the frozen tree" || { echo "SELFTEST FAIL G-FREEZE rejected the frozen tree"; guard_freeze; rc=1; }
  # EXTERNAL ANCHOR: section 8's literal, typed here as an ASSERTION, not a source.
  [ "$(cap_core_min DEC4)" = "416.919" ] && echo "SELFTEST ok the registered cap for DEC4 is section 8's 416.919" || { echo "SELFTEST FAIL cap"; rc=1; }
  # ... and that it came from the GRADER, so the two cannot drift apart again.
  [ "$(cap_core_min DEC4)" = "$(python3 "$SRC/d6r2c_dec4_grade.py" --print-cap DEC4)" ] \
    && echo "SELFTEST ok the cap has ONE source and this launcher is not it" \
    || { echo "SELFTEST FAIL the launcher carries its own cap"; rc=1; }
  [ -z "$(cap_core_min NOSUCHARM)" ] && echo "SELFTEST ok an unknown arm has no cap" || { echo "SELFTEST FAIL unknown arm got a cap"; rc=1; }
  [ -z "$(cap_core_min DEC3)" ] && [ -z "$(cap_core_min FM5)" ] \
    && echo "SELFTEST ok the earlier arms are NOT launchable from this document" \
    || { echo "SELFTEST FAIL an earlier arm is launchable here"; rc=1; }
  # THE FROZEN OPTIMISATION RUNSCRIPT IS PINNED UNCHANGED.  The widened incidence
  # bound is an ANALYSIS bound; if this pin ever moved, the claim that the
  # optimisation was untouched would be false, and this is where it is checked.
  [ "$MD5_RUNSCRIPT" = "2f2ae43a627146cf8e0f065b035ada4b" ] \
    && echo "SELFTEST ok the optimisation runscript pin is the O_mp bytes" \
    || { echo "SELFTEST FAIL the runscript pin moved"; rc=1; }
  grep -q "^# PIN d6r2c_dec4_grade.py " "$0" && grep -q "^# PIN d6r2c_dec4_decomp.py " "$0" \
    && echo "SELFTEST ok both successor instruments are pinned in this file" \
    || { echo "SELFTEST FAIL an instrument is unpinned"; rc=1; }
  # the count is the number of checks ACTUALLY DRIVEN above.
  [ "$rc" -eq 0 ] && echo "D6R2C_DEC4_LAUNCH SELFTEST PASS n=9" || echo "D6R2C_DEC4_LAUNCH SELFTEST FAIL"
  exit $rc
fi
test -n "$ARM" || { echo "ABORT usage: d6r2c_dec4_run_arm.sh DEC4 <image>  |  --selftest"; exit 64; }
case "$ARM" in DEC4) ;; *) echo "ABORT arm $ARM is not registered by this document"; exit 64 ;; esac
test -n "$IMG" || { echo "ABORT image required, pinned by digest"; exit 64; }
case "$IMG" in *"$IMG_PATCHED_DIGEST"*) ;; *) echo "ABORT G-IMG image is not the registered digest"; exit 4 ;; esac

guard_root "$BASE" || exit $?
guard_box || exit $?
guard_freeze || exit $?

# THE CAP IS READ ONLY NOW -- AFTER G-FREEZE HAS PINNED THE GRADER'S BYTES.
# The cap comes out of d6r2c_dec4_grade.py, so reading it before its md5 was
# checked would be trusting bytes this launcher had not yet verified.
CAP=$(cap_core_min "$ARM"); test -n "$CAP" || { echo "ABORT no registered cap for arm $ARM"; exit 64; }
echo "D6R2C_DEC4_CAP arm=$ARM cap_core_min=$CAP source=d6r2c_dec4_grade.py --print-cap"
LIVE=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d6r2c_dec4_${ARM}_" 2>/dev/null | head -3 | tr '\n' ',')
[ -n "$LIVE" ] && { echo "ABORT G-LIVE arm $ARM already running: $LIVE"; exit 3; }
mkdir -p "$BASE" && echo "ITEM=$ITEM" >> "$BASE/ledger.txt"
seed_arm "$ARM" || exit $?

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d6r2c_dec4_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

CMDFILE="$WORK/d6r2c_dec4_cmd.sh"
cat > "$CMDFILE" <<'CMD'
set -uo pipefail
echo "D6R2C_DEC4_DEADLINE_IN_CONTAINER_S: NONE"
rc=0
mpirun -np 4 python d6r2c_dec4_decomp.py --arm-dir "$PWD" \
    --runscript d6r2c_opt_runScript.py \
    --evals d6r2c_evals_final.jsonl --x0 d6r2c_x0_final.json || rc=$?
echo "D6R2C_DEC4_RC=$rc"
exit $rc
CMD
echo "D6R2C_DEC4_CMD arm=$ARM md5=$(md5sum "$CMDFILE" | cut -d' ' -f1)"

T0=$(date +%s)
sudo -n docker run -d --name "$NAME" \
    --user ${RUN_UID}:${RUN_GID} --group-add ${EXTRA_GID} -e HOME=/tmp \
    --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM_LIMIT --memory-swap=$MEM_LIMIT \
    --oom-score-adj=500 \
    -v "$BASE":/mnt -v "$PARENT_BASE":/mnt/parent:ro \
    -w "/mnt/$ARM" "$IMG" bash -lc \
    ". /home/dafoamuser/dafoam/loadDAFoam.sh && bash /mnt/$ARM/d6r2c_dec4_cmd.sh" \
    > /dev/null 2>&1 || { echo "ABORT docker run failed"; exit 6; }
echo "D6R2C_DEC4_LAUNCHED name=$NAME arm=$ARM uid=${RUN_UID}:${RUN_GID}+${EXTRA_GID} ranks=$RANKS cpuset=$CPUSET"

rotator "$WORK" &
ROT=$!
sudo -n docker wait "$NAME" > "$WORK/.arm_rc.txt" 2>/dev/null
RC=$(cat "$WORK/.arm_rc.txt" 2>/dev/null || echo 255)
kill "$ROT" 2>/dev/null
sudo -n docker logs "$NAME" > "$LOG" 2>&1
T1=$(date +%s)
WALL=$((T1 - T0))
CORE_MIN=$(awk -v w="$WALL" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60}')
ROOT_OWNED=$(find "$WORK" -newermt "@$(cat "$WORK/.d6r2c_age_datum")" \( -uid 0 -o -gid 0 \) 2>/dev/null | wc -l)
{
  echo "ITEM=$ITEM"
  echo "D6R2C_DEC4_ROW arm=$ARM name=$NAME rc=$RC wall_s=$WALL core_min=$CORE_MIN cap=$CAP root_owned=$ROOT_OWNED log=$LOG"
} >> "$BASE/ledger.txt"
awk -v c="$CORE_MIN" -v cap="$CAP" 'BEGIN{exit !(c>cap)}' && \
  echo "D6R2C_DEC4_CAP_CROSSED arm=$ARM core_min=$CORE_MIN cap=$CAP -- the row is graded NOT A RESULT and THE CAP IS NEVER RAISED" | tee -a "$BASE/ledger.txt"
echo "D6R2C_DEC4_DONE arm=$ARM rc=$RC core_min=$CORE_MIN cap=$CAP root_owned=$ROOT_OWNED"
echo "NOW GRADE:  python3 $SRC/d6r2c_dec4_grade.py --item 8R2 \\"
echo "              --arm-dir $WORK --datum-file $WORK/.d6r2c_age_datum \\"
echo "              --core-min $CORE_MIN --rc $RC"
exit 0

# ---------------------------------------------------------------------------
# THE REGISTERED md5 PINS.  G-FREEZE reads these lines out of this file.
# They are filled at the freeze commit and are what make the instruments that
# run the instruments that were frozen (PREREGISTRATION_AFTER_ITEM8_R2.md sec 11).
#
# THE OPTIMISATION RUNSCRIPT IS PINNED UNCHANGED at MD5_RUNSCRIPT above --
# 2f2ae43a627146cf8e0f065b035ada4b, the bytes O_mp ran.  The widened incidence
# bound is an ANALYSIS bound that lives in d6r2c_dec4_decomp.py and nowhere else;
# the runscript still carries lower=[U0, 0.0] at its line 280 and O_mp's
# GATE FAIL, its 24.732 % and its Jf/J0 = 0.752677 stand exactly as graded.
# PIN d6r2c_dec4_grade.py 4c23b6be959f74b3d840db70bd34e340
# PIN d6r2c_dec4_decomp.py a5f6023d5eec9b1315ef7f34e635bb29
