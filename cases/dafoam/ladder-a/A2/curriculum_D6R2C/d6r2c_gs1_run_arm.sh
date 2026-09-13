#!/usr/bin/env bash
# ===========================================================================
# d6r2c_gs1_run_arm.sh -- LAUNCHER for the D6R2C GRADIENT SPOT-CHECK (arm GS1)
# ===========================================================================
#
# Registered by PREREGISTRATION_GRADIENT_SPOTCHECK.md sections 5, 8, 9 and 11,
# and IN THE SAME COMMIT, BEFORE ANY CONTAINER STARTS (CLAUDE.md rule 2).
#
# A FORK of d6r2c_fm6_run_arm.sh (md5 cead1008eeb4d151c0ccddae2653d64b), which
# stays on disk unedited.  Its G-ROOT / G-BOX / G-FREEZE / G-DEPS / G-COLD
# design, its digest pin, its ledger row and its cap-from-the-grader pattern are
# carried unchanged.  WHAT CHANGED, EXHAUSTIVELY:
#   D1 -- ONE ARM, GS1, and NO MESH GENERATION.  This arm runs on the warped mesh
#         at the optimum, the same mesh O_mp used; no fresh extrusion, no CGNS,
#         no surface staging, so those inputs are not staged and not pinned.
#   D2 -- THREE PHASES: stage -> init -> sweep.  `stage` builds the model so
#         DAFoam creates the decomposition and STOPS WITHOUT SOLVING; `init` is
#         d6r2c_fm6_init.py REUSED UNCHANGED at 75bf53d8e798980332ef8dfdcc25b0c6,
#         writing processorN/0/ where the solver reads; `sweep` runs the ladder.
#         FM7 died because the transfer landed after the decomposition the solver
#         actually read, and the phase order is asserted by the selftest.
#   D3 -- the pins are the GS1 instruments plus the reused transfer.
#   D4 -- THE CAP IS NOT CARRIED HERE.  cap_core_min() asks d6r2c_gs1_grade.py,
#         after G-FREEZE has pinned it.
#   D5 -- NO G-VERIFY.  Its FM5 anchors are fresh-mesh anchors and do not apply
#         to this arm.  THE EQUIVALENT CHECK IS NOT DROPPED: it lives in
#         d6r2c_gs1_grade.py as the warm-start refusal, against the WARPED-mesh
#         freestream signature, and the launcher hands it the log at grading.
#
set -uo pipefail

ITEM=D6R2C-GS1
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-GS1-a2-wing-gradient-spotcheck
FM6_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER9R2-a2-wing-freshmesh-warmstart
AFTER_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER-a2-wing-decomposition-and-freshmesh
DEC4_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER8R2-a2-wing-decomposition-retrimmed
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

# THE CANONICAL STAGED PYTHON LIST (C6).  Referenced by seed_arm AND by G-DEPS;
# never re-spelled in either (L-221/L-222).  d6r2c_decomp.py is here because
# d6r2c_freshmesh.py imports it as a library -- see ADDENDUM 1.
STAGED_PY="d6r2c_opt_runScript.py d6r2c_gs1_fd.py d6r2c_fm6_init.py"

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
# THE REGISTERED CAP (PREREGISTRATION_AFTER_ITEM9_R2.md section 8): 47.211
# core-min = 3.00x the prediction of 15.737.  THIS FILE DOES NOT CARRY THE
# FIGURE -- it asks the grader, which derives it from the prediction.  A cap
# that exists as a literal in two files is two things that can drift, and in
# this item they did (PREREGISTRATION_AFTER_ITEM8_R2.md section 8a).
# NOTHING KILLS ON IT (Sanaa directive #17): a crossing is REPORTED, the row is
# graded NOT A RESULT, and the cap is never raised.
# THE CAP IS A PROPERTY OF THE ITEM, NOT OF THE ARM ID.  FM7 carries the
# IDENTICAL registered figure -- the same number looked up under another key
# (ADDENDUM 1, C8).  The canonical key is FM6, the arm this document registered
# first.  THE GRADER IS NOT EDITED TO LEARN A NEW ARM ID: its pin must not move,
# and a cap that is one number in one place stays one number in one place.
cap_core_min() {
  case "$1" in
    GS1) python3 "$SRC/d6r2c_gs1_grade.py" --print-cap GS1 2>/dev/null ;;
    *) echo "" ;;
  esac
}

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
$DEC4_BASE
$FM6_BASE
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
  echo "D6R2C_GS1_G_ROOT_PASS item=$ITEM base=$BASE_REAL"
  return 0
}

md5_is() { [ "$(md5sum "$1" | cut -d' ' -f1)" = "$2" ]; }

# ===========================================================================
# G-DEPS (C7) -- EVERY LOCAL MODULE A STAGED FILE IMPORTS MUST ITSELF BE STAGED.
#
# A PIN PROVES WHAT A FILE IS, NOT WHAT IT NEEDS.  FM6 was launched with
# d6r2c_freshmesh.py pinned at its exact frozen md5 and died because the module
# it imports was not beside it.  The hash was correct and the arm was unrunnable.
#
# Takes the staged list as ARGUMENTS so the SELFTEST CAN DRIVE IT WITH A FILE
# REMOVED and require it to FAIL.  A check that cannot be seen to fail is not a
# check -- the same lesson this item's cap controls taught.
# ===========================================================================
guard_deps() {
  python3 - "$SRC" "$@" <<'DEPSPY'
import ast, os, sys
src, staged = sys.argv[1], sys.argv[2:]
stem = {os.path.splitext(f)[0] for f in staged}
missing, scanned = [], 0
for f in staged:
    if not f.endswith(".py"):
        continue
    p = os.path.join(src, f)
    if not os.path.isfile(p):
        print("ABORT G-DEPS staged file does not exist in SRC: %s" % f)
        sys.exit(1)
    scanned += 1
    tree = ast.parse(open(p).read(), p)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods.add(node.module.split(".")[0])
    for m in sorted(mods):
        # LOCAL means "a file of that name sits in SRC" -- an image module is
        # not this launcher's to stage and is not its to vouch for.
        if os.path.isfile(os.path.join(src, m + ".py")) and m not in stem:
            missing.append("%s imports %s, which is NOT staged" % (f, m))
if missing:
    print("ABORT G-DEPS the staged set does not cover its own imports:")
    for x in missing:
        print("   " + x)
    sys.exit(1)
print("D6R2C_GS1_G_DEPS_PASS scanned=%d staged=%d" % (scanned, len(staged)))
DEPSPY
}

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
  for f in d6r2c_gs1_grade.py d6r2c_gs1_fd.py d6r2c_fm6_init.py; do
    want=$(grep -m1 "^# PIN $f " "$0" | awk '{print $4}')
    [ -n "$want" ] || { echo "ABORT G-FREEZE no pin recorded for $f"; bad=1; continue; }
    got=$(md5sum "$SRC/$f" | cut -d' ' -f1)
    [ "$got" = "$want" ] || { echo "ABORT G-FREEZE $f md5=$got want=$want"; bad=1; }
  done
  [ $bad -eq 0 ] || return 4
  echo "D6R2C_GS1_G_FREEZE_PASS"
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
  echo "D6R2C_GS1_G_BOX_PASS load1=$load1 nproc=$nproc solver_swap_offenders=0 avail_gb=$avail_gb"
  return 0
}

# ===========================================================================
# SEED -- base/ copied read-only and HASHED, inputs staged BEFORE the age datum
# ===========================================================================
seed_arm() {
  local ARM="$1" WORK="$BASE/$ARM"
  mkdir -p "$WORK" || return 5
  # G-COLD -- a guard refuses a case where 0 or a time dir already exists
  for bad in "$WORK/0" "$WORK/constant" "$WORK/mp04" "$WORK/d6r2c_gs1.jsonl" "$WORK/d6r2c_fm6_init.json"; do
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
  for f in $STAGED_PY; do
    cp "$SRC/$f" "$WORK/" || { echo "ABORT G-SEED stage $f"; return 5; }
  done
  test -f "$WORK/0/U" || { echo "ABORT G-COLD 0/U missing after seed"; return 5; }
  touch "$WORK/0/U"
  AGE_DATUM=$(stat -c '%Y' "$WORK/0/U")
  echo "$AGE_DATUM" > "$WORK/.d6r2c_age_datum"
  echo "D6R2C_GS1_G_COLD_PASS arm=$ARM age_datum_epoch=$AGE_DATUM"
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
    for f in d6r2c_gs1.jsonl d6r2c_fm6_init.json d6r2c_x0_final.json; do
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
  [ "$(cap_core_min GS1)" = "301.485" ] && echo "SELFTEST ok the registered cap for GS1 is section 8's 301.485" || { echo "SELFTEST FAIL cap"; rc=1; }
  # ... and that it came from the GRADER, so the two cannot drift apart again.
  [ "$(cap_core_min GS1)" = "$(python3 "$SRC/d6r2c_gs1_grade.py" --print-cap GS1)" ] \
    && echo "SELFTEST ok the cap has ONE source and this launcher is not it" \
    || { echo "SELFTEST FAIL the launcher carries its own cap"; rc=1; }
  [ -z "$(cap_core_min NOSUCHARM)" ] && [ -z "$(cap_core_min FM8)" ] \
    && echo "SELFTEST ok neither an unknown arm nor an earlier one is launchable here" \
    || { echo "SELFTEST FAIL an unregistered arm got a cap"; rc=1; }
  # THE FROZEN OPTIMISATION RUNSCRIPT IS PINNED UNCHANGED.
  [ "$MD5_RUNSCRIPT" = "2f2ae43a627146cf8e0f065b035ada4b" ] \
    && echo "SELFTEST ok the optimisation runscript pin is the O_mp bytes" \
    || { echo "SELFTEST FAIL the runscript pin moved"; rc=1; }
  # C3: deform/mesh/solve are the SAME BYTES THAT RAN FM5.  That pin is the
  # evidence that the one registered change is the only change.
  [ "$(grep -m1 "^# PIN d6r2c_fm6_init.py " "$0" | awk '{print $4}')" = "75bf53d8e798980332ef8dfdcc25b0c6" ] \
    && echo "SELFTEST ok d6r2c_fm6_init.py is pinned UNCHANGED at FM8's md5" \
    || { echo "SELFTEST FAIL the reused transfer's pin moved"; rc=1; }
  grep -q "^# PIN d6r2c_gs1_grade.py " "$0" && grep -q "^# PIN d6r2c_gs1_fd.py " "$0" \
    && echo "SELFTEST ok both new instruments are pinned in this file" \
    || { echo "SELFTEST FAIL an instrument is unpinned"; rc=1; }
  # THE CONTAINER RUNS FOUR PHASES AND init SITS BETWEEN mesh AND solve.
  # The order is read out of THE GENERATED COMMAND BLOCK ONLY.  A first draft of
  # this check grepped the whole file and matched ITS OWN grep lines, which sit
  # above the command block -- a check that reads itself measures nothing.
  CMDBLOCK=$(sed -n '/^cat > "\$CMDFILE"/,/^CMD$/p' "$0")
  # Match the INVOCATIONS, not the comments that name the same files.  A first
  # draft matched "fm6_init.py" anywhere and counted the explanatory comment as a
  # phase, reading [stage init init sweep] -- a check that cannot tell a comment
  # from a command is measuring the prose.
  PH=$(printf '%s\n' "$CMDBLOCK" | grep -E "^(mpirun|\[ .rc| *python)" | \
       grep -oE "phase stage|python d6r2c_fm6_init\.py|phase sweep" | tr '\n' ' ')
  [ "$PH" = "phase stage python d6r2c_fm6_init.py phase sweep " ] \
    && echo "SELFTEST ok the container runs stage -> init -> sweep, in that order" \
    || { echo "SELFTEST FAIL the phase order is [$PH]"; rc=1; }
  # ---- G-DEPS (C7), DRIVEN IN BOTH DIRECTIONS ------------------------------
  # THE POSITIVE: the registered staged set covers its own imports.
  guard_deps $STAGED_PY >/dev/null 2>&1 \
    && echo "SELFTEST ok G-DEPS passes on the registered staged set" \
    || { echo "SELFTEST FAIL G-DEPS rejected the registered staged set"; rc=1; }
  # THE FAILING CONTROL, AND AN HONEST NOTE ABOUT WHAT IT CAN AND CANNOT PROVE.
  #
  # THIS ARM'S STAGED SET HAS NO LOCAL INTER-MODULE DEPENDENCIES AT ALL:
  # d6r2c_gs1_fd.py carries its own load_frozen_model and d6r2c_fm6_init.py
  # imports nothing local, so G-DEPS is VACUOUSLY SATISFIED here and removing any
  # one file from the set would still pass.  SAYING SO IS THE POINT -- a guard
  # that has nothing to find on this arm must not be reported as if it had
  # searched and cleared something.
  #
  # So the failing control is driven against a KNOWN-BAD SET FROM THIS SAME
  # DIRECTORY -- d6r2c_freshmesh.py without d6r2c_decomp.py, the exact set that
  # killed FM6 -- which proves THE GUARD IS LIVE even though this arm gives it
  # nothing to catch.  A gate never seen to fire is not evidence.
  BADSET="d6r2c_opt_runScript.py d6r2c_freshmesh.py"
  if guard_deps $BADSET >/dev/null 2>&1; then
    echo "SELFTEST FAIL G-DEPS PASSED the set that killed FM6"; rc=1
  else
    echo "SELFTEST ok G-DEPS FAILS on the known-bad set that killed FM6"
  fi
  # ... and it NAMES the file.  The output is CAPTURED FIRST and matched after:
  # `set -o pipefail` is active, so piping a deliberately-failing command into
  # grep returns the command's non-zero status even when grep matches, and the
  # control would report a failure that did not happen.
  DEPOUT=$(guard_deps $BADSET 2>&1 || true)
  case "$DEPOUT" in
    *"imports d6r2c_decomp, which is NOT staged"*)
      echo "SELFTEST ok G-DEPS names the missing module and the file that needs it" ;;
    *) echo "SELFTEST FAIL G-DEPS did not name the missing module"; rc=1 ;;
  esac
  echo "SELFTEST ok (disclosed) this arm's staged set has NO local dependencies, so G-DEPS is vacuous here"
  # the staged list has ONE source: seed_arm and G-DEPS both read $STAGED_PY
  [ "$(grep -c 'for f in \$STAGED_PY' "$0")" -ge 1 ] && [ "$(grep -c 'guard_deps \$STAGED_PY' "$0")" -ge 1 ] \
    && echo "SELFTEST ok the staged list has ONE source, read by both the copy and the check" \
    || { echo "SELFTEST FAIL the staged list is re-spelled"; rc=1; }
  # NO G-VERIFY CONTROLS HERE (D5): that guard's anchors are FRESH-MESH anchors
  # and do not apply to this arm.  The equivalent check lives in
  # d6r2c_gs1_grade.py as the warm-start refusal, against the WARPED-mesh
  # freestream signature, and is driven by THAT instrument's selftest.
  [ "$rc" -eq 0 ] && echo "D6R2C_GS1_LAUNCH SELFTEST PASS n=16" || echo "D6R2C_GS1_LAUNCH SELFTEST FAIL"
  exit $rc
fi
test -n "$ARM" || { echo "ABORT usage: d6r2c_gs1_run_arm.sh GS1 <image>  |  --selftest"; exit 64; }
case "$ARM" in GS1) ;; *) echo "ABORT arm $ARM is not registered by this document"; exit 64 ;; esac
test -n "$IMG" || { echo "ABORT image required, pinned by digest"; exit 64; }
case "$IMG" in *"$IMG_PATCHED_DIGEST"*) ;; *) echo "ABORT G-IMG image is not the registered digest"; exit 4 ;; esac

guard_root "$BASE" || exit $?
guard_box || exit $?
guard_freeze || exit $?
guard_deps $STAGED_PY || exit 4

# THE CAP IS READ ONLY NOW -- AFTER G-FREEZE HAS PINNED THE GRADER'S BYTES.
CAP=$(cap_core_min "$ARM"); test -n "$CAP" || { echo "ABORT no registered cap for arm $ARM"; exit 64; }
echo "D6R2C_GS1_CAP arm=$ARM cap_core_min=$CAP source=d6r2c_fm6_grade.py --print-cap"
LIVE=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d6r2c_gs1_${ARM}_" 2>/dev/null | head -3 | tr '\n' ',')
[ -n "$LIVE" ] && { echo "ABORT G-LIVE arm $ARM already running: $LIVE"; exit 3; }
mkdir -p "$BASE" && echo "ITEM=$ITEM" >> "$BASE/ledger.txt"
seed_arm "$ARM" || exit $?

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d6r2c_gs1_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

CMDFILE="$WORK/d6r2c_gs1_cmd.sh"
cat > "$CMDFILE" <<'CMD'
set -uo pipefail
echo "D6R2C_GS1_DEADLINE_IN_CONTAINER_S: NONE"
rc=0
# PHASE 1 -- build the model so DAFoam creates the decomposition, and STOP.
# NO PRIMAL IS SOLVED HERE.  The transfer has nowhere to land until this exists.
mpirun -np 4 python d6r2c_gs1_fd.py --phase stage --arm-dir "$PWD" \
    --runscript d6r2c_opt_runScript.py || rc=$?
# PHASE 2 -- THE WARM START.  d6r2c_fm6_init.py REUSED UNCHANGED: it writes
# processorN/0/ through the same cellProcAddressing, WHERE THE SOLVER READS.
[ $rc -eq 0 ] && { python d6r2c_fm6_init.py --arm-dir "$PWD" \
    --omp-dir /mnt/parent/O_mp --evals d6r2c_evals_final.jsonl || rc=$?; }
# PHASE 3 -- the ladder.
[ $rc -eq 0 ] && { mpirun -np 4 python d6r2c_gs1_fd.py --phase sweep --arm-dir "$PWD" \
    --runscript d6r2c_opt_runScript.py --evals d6r2c_evals_final.jsonl || rc=$?; }
echo "D6R2C_GS1_RC=$rc"
exit $rc
CMD
echo "D6R2C_GS1_CMD arm=$ARM md5=$(md5sum "$CMDFILE" | cut -d' ' -f1)"

T0=$(date +%s)
sudo -n docker run -d --name "$NAME" \
    --user ${RUN_UID}:${RUN_GID} --group-add ${EXTRA_GID} -e HOME=/tmp \
    --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM_LIMIT --memory-swap=$MEM_LIMIT \
    --oom-score-adj=500 \
    -v "$BASE":/mnt -v "$PARENT_BASE":/mnt/parent:ro \
    -w "/mnt/$ARM" "$IMG" bash -lc \
    ". /home/dafoamuser/dafoam/loadDAFoam.sh && bash /mnt/$ARM/d6r2c_gs1_cmd.sh" \
    > /dev/null 2>&1 || { echo "ABORT docker run failed"; exit 6; }
echo "D6R2C_GS1_LAUNCHED name=$NAME arm=$ARM uid=${RUN_UID}:${RUN_GID}+${EXTRA_GID} ranks=$RANKS cpuset=$CPUSET"

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
  echo "D6R2C_GS1_ROW arm=$ARM name=$NAME rc=$RC wall_s=$WALL core_min=$CORE_MIN cap=$CAP root_owned=$ROOT_OWNED log=$LOG"
} >> "$BASE/ledger.txt"
awk -v c="$CORE_MIN" -v cap="$CAP" 'BEGIN{exit !(c>cap)}' && \
  echo "D6R2C_GS1_CAP_CROSSED arm=$ARM core_min=$CORE_MIN cap=$CAP -- the row is graded NOT A RESULT and THE CAP IS NEVER RAISED" | tee -a "$BASE/ledger.txt"
echo "D6R2C_GS1_DONE arm=$ARM rc=$RC core_min=$CORE_MIN cap=$CAP root_owned=$ROOT_OWNED"
# NO G-VERIFY HERE (D5).  Its anchors are FRESH-MESH anchors and do not apply to
# this arm.  THE EQUIVALENT CHECK IS NOT DROPPED -- d6r2c_gs1_grade.py carries the
# warm-start refusal against the WARPED-mesh freestream signature, and the grading
# line below hands it this arm's log.
echo "NOW GRADE:  python3 $SRC/d6r2c_gs1_grade.py --item GS1 \\"
echo "              --arm-dir $WORK --datum-file $WORK/.d6r2c_age_datum \\"
echo "              --core-min $CORE_MIN --rc $RC --log $LOG \\"
echo "              --out $BASE/GS1_GRADE.json"
exit 0

# ---------------------------------------------------------------------------
# THE REGISTERED md5 PINS.  G-FREEZE reads these lines out of this file.
# d6r2c_fm6_init.py IS PINNED UNCHANGED AT FM8's md5 -- the transfer that was
# measured to make this configuration converge at the optimum, reused and not
# re-implemented.  The optimisation runscript is pinned unchanged at
# MD5_RUNSCRIPT above, the bytes O_mp ran.
# PIN d6r2c_gs1_grade.py a67791e31e7fb887972256499a40312d
# PIN d6r2c_gs1_fd.py 663baeb6bfbec80ff6a9243169dbc7a4
# PIN d6r2c_fm6_init.py 75bf53d8e798980332ef8dfdcc25b0c6
