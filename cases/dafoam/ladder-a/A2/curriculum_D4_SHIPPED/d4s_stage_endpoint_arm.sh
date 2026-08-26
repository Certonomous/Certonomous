#!/usr/bin/env bash
# D4-SHIPPED ENDPOINT-ARM STAGING (PREREGISTRATION.md ADDENDUM 2d) -- D4's
# FROZEN F3/ACC staging path (`curriculum_D4/d4_stage_F3.sh`,
# `d4_stage_ACC.sh`), carried step for step, parameterised by ARM, with THIS
# item's run root as BASE and curriculum_D4 as the READ-ONLY source of the
# frozen D4-DEF-4 repair instruments (md5-asserted against the frozen
# `d4_repair_instruments.md5`).
#
# WHY THIS FILE EXISTS (D4S-LAUNCHER-DEF-4).  `d4s_run_arm.sh` mapped arm F3
# to WORK=$BASE/F3 "from arm O" while nothing in this launcher family created
# it, and its F3/ACC commands omitted the D4-DEF-4 repair step
# (`d4_endpoint_physical.py --age-datum`), so F3 would have differentiated at
# the DRIVER-SCALED endpoint -- the defect D4 arm F crashed on -- and ACC ran a
# second baseline `compute_totals` instead of the acceptance primal it was
# priced as.  The launcher's own guard refused F3 at :281 (rc=5, 0 core-min).
# Addendum 2d registers D4's frozen path for both arms; this is its staging
# half.  NO GATE, THRESHOLD, BAND, CAP OR LABEL MOVES.
#
#   F3  : copy O/ -> F3/, drop arm O's OUTPUT pseudo-time directories from the
#         COPY (D4-DEF-6: `renameSolution` collides on `0.0001` otherwise),
#         keep inputs + OptView.hst + dRdWColoring_4.bin; second datum
#         `.d4_stage_F3_copy_epoch`.
#   ACC : copy O/ -> ACC/ (no step (f), exactly as D4 did for its 45-s
#         acceptance primal); second datum `.d4_stage_ACC_copy_epoch`.
#
# The reference mesh is asserted UNDEFORMED (points.gz md5 == base/) so a copy
# of O/ cannot double-deform the wing -- eliminated by measurement, not assumed.
# `cp -a` PRESERVES mtimes: arm O's own datum keeps meaning what it meant, and
# the copy epoch is the STRICTLY LATER datum that dates this arm.
# COPY, NEVER MOVE: O/ is graded evidence and is asserted intact afterwards.
# A destination that already exists is REFUSED, never overwritten.
# `set -e` does NOT gate at the top level; every step gates explicitly.
set -uo pipefail
ARM="${1:-}"
case "$ARM" in F3|ACC) ;; *) echo "ABORT usage: d4s_stage_endpoint_arm.sh <F3|ACC>"; exit 64 ;; esac
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin
CASE_D4=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D4
SRC="$BASE/O"
DST="$BASE/$ARM"
EV="$BASE/${ARM}_STAGING_EVIDENCE.txt"
: > "$EV"
say() { echo "$*" | tee -a "$EV"; }
say "D4S_STAGE_$ARM utc=$(date -u +%Y%m%dT%H%M%SZ) base=$BASE"

# ---- G-ROOT.1: this item's root only (the D4-LAUNCHER-DEF-1 class) ----------
test "$(realpath -m "$BASE")" = "/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin" || { say "ABORT G-ROOT.1"; exit 3; }

# ---- (a) COPY, NEVER MOVE.  Source must exist and must survive. ----------
test -d "$SRC" || { say "ABORT (a) source $SRC absent"; exit 5; }
test -f "$SRC/OptView.hst" || { say "ABORT (a) $SRC/OptView.hst absent -- no endpoint to read"; exit 5; }
test ! -e "$DST" || { say "ABORT (a) destination $DST already exists -- refusing to overwrite evidence"; exit 5; }
say "D4S_STAGE_$ARM (a) OK src=$SRC exists, OptView.hst present, dst=$DST does not exist"

# ---- (b) THE ANSWER FILES MUST NOT PRE-EXIST in the source. ---------------
N=$(find "$SRC" \( -name 'd4_endpoint_dvs*.json' -o -name 'd4_accept_primal.json' -o -name 'd4_fd_endpoint.jsonl' -o -name 'd4_fd_endpoint.json*' \) 2>/dev/null | wc -l)
say "D4S_STAGE_$ARM (b) ASSERTION: count of pre-existing answer files under $SRC = $N (required 0)"
[ "$N" -eq 0 ] || { find "$SRC" \( -name 'd4_endpoint_dvs*.json' -o -name 'd4_accept_primal.json' -o -name 'd4_fd_endpoint.json*' \) | tee -a "$EV"; say "ABORT (b) an answer file exists BEFORE the arm that must produce it"; exit 5; }
say "D4S_STAGE_$ARM (b) OK"

# ---- (c) THE REFERENCE MESH IS THE UNDEFORMED ONE -------------------------
MB=$(md5sum "$BASE/base/constant/polyMesh/points.gz" | cut -d' ' -f1)
MS=$(md5sum "$SRC/constant/polyMesh/points.gz" | cut -d' ' -f1)
say "D4S_STAGE_$ARM (c) reference mesh md5 base=$MB src=$MS"
test "$MB" = "$MS" || { say "ABORT (c) $SRC carries a DEFORMED reference mesh -- staging from it would double-deform the wing"; exit 5; }
say "D4S_STAGE_$ARM (c) OK -- undeformed reference mesh, double-deformation confound eliminated by measurement"

# ---- (d) COPY with mtime semantics PINNED and a second datum written ------
say "D4S_STAGE_$ARM (d) mtime semantics = cp -a, PRESERVE"
COPY_EPOCH=$(date -u +%s)
cp -a "$SRC" "$DST" || { say "ABORT (d) copy failed"; exit 4; }
echo "$COPY_EPOCH" > "$DST/.d4_stage_${ARM}_copy_epoch" || { say "ABORT (d) cannot write copy datum"; exit 4; }
say "D4S_STAGE_$ARM (d) copied, copy_epoch=$COPY_EPOCH written to .d4_stage_${ARM}_copy_epoch"
say "D4S_STAGE_$ARM (d) arm O age datum carried over = $(cat "$DST/.d4_age_datum" 2>/dev/null || echo ABSENT)"
test -f "$SRC/OptView.hst" || { say "ABORT (a) source lost OptView.hst after copy"; exit 5; }
test -f "$SRC/opt_IPOPT.txt" || { say "ABORT (a) source lost opt_IPOPT.txt after copy"; exit 5; }
say "D4S_STAGE_$ARM (a) POST-COPY: source intact"
N2=$(find "$DST" \( -name 'd4_endpoint_dvs*.json' -o -name 'd4_accept_primal.json' -o -name 'd4_fd_endpoint.jsonl' -o -name 'd4_fd_endpoint.json*' \) 2>/dev/null | wc -l)
say "D4S_STAGE_$ARM (b) POST-COPY assertion: answer files under $DST = $N2 (required 0)"
[ "$N2" -eq 0 ] || { say "ABORT (b) answer file appeared in destination"; exit 5; }

# ---- (e) stage the FROZEN D4-DEF-4 repair instruments into the run root ---
# Source is curriculum_D4, read-only; identity asserted against the frozen
# md5 list BEFORE the copy so a drifted instrument never reaches the root.
( cd "$CASE_D4" && md5sum -c d4_repair_instruments.md5 ) >> "$EV" 2>&1 || { say "ABORT (e) repair-instrument md5 in $CASE_D4"; exit 4; }
cp -a "$CASE_D4/d4_repair_instruments.md5" "$BASE/" || { say "ABORT (e) cannot stage md5 list"; exit 4; }
for f in d4_endpoint_locus.py d4_endpoint_physical.py d4_accept_primal.py d4_accept_compare.py; do
  cp -a "$CASE_D4/$f" "$BASE/$f" || { say "ABORT (e) cannot stage $f"; exit 4; }
  say "D4S_STAGE_$ARM (e) staged $f md5 $(md5sum "$BASE/$f" | cut -d' ' -f1)"
done
( cd "$BASE" && md5sum -c d4_repair_instruments.md5 ) >> "$EV" 2>&1 || { say "ABORT (e) repair-instrument md5 in $BASE"; exit 4; }
say "D4S_STAGE_$ARM (e) OK -- frozen repair instruments identical to curriculum_D4"

# ---- (f) F3 ONLY -- THE D4-DEF-6 REPAIR: drop ARM O's OUTPUT TIME DIRS ----
if [ "$ARM" = "F3" ]; then
  NREM=0
  for d in "$DST"/processor*/*/ "$DST"/*/; do
    b=$(basename "$d")
    case "$b" in 0|constant|system|0.orig|FFD|postProcessing|reports) continue ;; esac
    if echo "$b" | grep -qE '^[0-9]+(\.[0-9]+)?$'; then
      rm -rf "$d" || { say "ABORT (f) cannot remove $d"; exit 4; }
      NREM=$((NREM+1))
    fi
  done
  if [ -e "$DST/reports" ]; then rm -rf "$DST/reports" || { say "ABORT (f) cannot remove reports"; exit 4; }; NREM=$((NREM+1)); fi
  say "D4S_STAGE_$ARM (f) removed $NREM arm-O output directories from the COPY"
  [ "$NREM" -gt 0 ] || { say "ABORT (f) removed ZERO directories -- a repair that removes nothing is a no-op, not a repair"; exit 5; }
  NLEFT=$(find "$DST" -maxdepth 2 -type d -regextype posix-extended -regex '.*/(processor[0-9]+/)?[0-9]+\.[0-9]+' ! -name '0' 2>/dev/null | wc -l)
  say "D4S_STAGE_$ARM (f) pseudo-time directories remaining under $DST = $NLEFT (required 0)"
  [ "$NLEFT" -eq 0 ] || { say "ABORT (f) pseudo-time directories survive -- renameSolution will collide again"; exit 5; }
  test -f "$DST/processor0/0/U.gz" || { say "ABORT (f) the START-TIME FIELDS were removed -- the repair overreached"; exit 5; }
  test -f "$DST/OptView.hst" || { say "ABORT (f) OptView.hst removed -- no endpoint to read"; exit 5; }
  test -f "$DST/dRdWColoring_4.bin" || { say "ABORT (f) colouring removed -- the arm would be repriced"; exit 5; }
  test -f "$DST/constant/polyMesh/points.gz" || { say "ABORT (f) reference mesh removed"; exit 5; }
  NSRC=$(ls -d "$SRC"/processor0/[0-9]*/ 2>/dev/null | wc -l)
  say "D4S_STAGE_$ARM (f) SOURCE INTACT assertion: time directories under $SRC/processor0 = $NSRC (required > 1, arm O's evidence is NOT touched)"
  [ "$NSRC" -gt 1 ] || { say "ABORT (f) the source tree lost its time directories"; exit 5; }
  say "D4S_STAGE_$ARM (f) OK -- outputs dropped from the copy, inputs and source intact"
else
  say "D4S_STAGE_$ARM (f) not applied for ACC -- D4's acceptance primal ran on the unmodified copy (d4_stage_ACC.sh has no step (f))"
fi
say "D4S_STAGE_$ARM READY -- the launcher may now run arm $ARM in $DST"
exit 0
