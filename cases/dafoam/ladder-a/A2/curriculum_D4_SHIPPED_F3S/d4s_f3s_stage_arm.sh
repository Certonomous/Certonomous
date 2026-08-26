#!/usr/bin/env bash
# D4S-F3S ENDPOINT-ARM STAGING -- D4-SHIPPED's `d4s_stage_endpoint_arm.sh`
# (Addendum 2d; itself D4's frozen `d4_stage_F3.sh` step for step),
# parameterised by ROW: the SOURCE of arm F-S is D4-SHIPPED's graded `O/` and
# the source of arm F-P is curriculum_D4's graded `O/`.  Both sources are
# READ-ONLY EVIDENCE of other items (their roots are on this launcher's
# FORBIDDEN list): COPY, never move; source censused before and after.
#   F-S : /home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin/O -> <ROOT>/F-S
#   F-P : /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O         -> <ROOT>/F-P
# Step (f) -- drop arm O's OUTPUT pseudo-time directories from the COPY
# (D4-DEF-6) -- is applied to BOTH arms (both are F3-class arms).
# The reference mesh is asserted UNDEFORMED against the SOURCE ITEM's own base/.
# The frozen D4-DEF-4 repair instruments (curriculum_D4) and this item's two
# instruments are staged into the root, each md5-asserted before and after.
# NO GATE, THRESHOLD, BAND, CAP OR LABEL MOVES.  `set -e` does not gate at the
# top level; every step gates explicitly.
set -uo pipefail
ARM="${1:-}"
case "$ARM" in F-S|F-P) ;; *) echo "ABORT usage: d4s_f3s_stage_arm.sh <F-S|F-P>"; exit 64 ;; esac
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE_D4=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D4
case "$ARM" in
  F-S) SRC_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin ;;
  F-P) SRC_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin ;;
esac
SRC="$SRC_ROOT/O"
DST="$BASE/$ARM"
EV="$BASE/${ARM}_STAGING_EVIDENCE.txt"
test -d "$BASE" || { echo "ABORT run root $BASE absent -- the chain driver creates it"; exit 5; }
: > "$EV"
say() { echo "$*" | tee -a "$EV"; }
say "D4SF3S_STAGE_$ARM utc=$(date -u +%Y%m%dT%H%M%SZ) base=$BASE src=$SRC"

# ---- G-ROOT.1: this item's root only; the source root must be one of the two named
test "$(realpath -m "$BASE")" = "/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin" || { say "ABORT G-ROOT.1"; exit 3; }
test "$(realpath -m "$SRC_ROOT")" != "$(realpath -m "$BASE")" || { say "ABORT G-ROOT.2 source equals this root"; exit 3; }

# ---- (a) COPY, NEVER MOVE.  Source must exist and must survive. ----------
test -d "$SRC" || { say "ABORT (a) source $SRC absent"; exit 5; }
test -f "$SRC/OptView.hst" || { say "ABORT (a) $SRC/OptView.hst absent -- no endpoint to read"; exit 5; }
test -f "$SRC/.d4_age_datum" || { say "ABORT (a) $SRC carries no .d4_age_datum -- not a graded arm O"; exit 5; }
test ! -e "$DST" || { say "ABORT (a) destination $DST already exists -- refusing to overwrite evidence"; exit 5; }
NSRC0=$(find "$SRC" | wc -l); OB=$(stat -c '%Y %s' "$SRC/OptView.hst")
say "D4SF3S_STAGE_$ARM (a) OK src=$SRC entries=$NSRC0 OptView.hst=[$OB] dst=$DST does not exist"

# ---- (b) THE ANSWER FILES MUST NOT PRE-EXIST in the source. ---------------
N=$(find "$SRC" \( -name 'd4_endpoint_dvs*.json' -o -name 'd4_accept_primal.json' -o -name 'd4_fd_endpoint.json*' -o -name 'd4s_f3s_*' \) 2>/dev/null | wc -l)
say "D4SF3S_STAGE_$ARM (b) ASSERTION: count of pre-existing answer files under $SRC = $N (required 0)"
[ "$N" -eq 0 ] || { say "ABORT (b) an answer file exists in the source"; exit 5; }

# ---- (c) THE REFERENCE MESH IS THE UNDEFORMED ONE (source item's own base/)
MB=$(md5sum "$SRC_ROOT/base/constant/polyMesh/points.gz" | cut -d' ' -f1)
MS=$(md5sum "$SRC/constant/polyMesh/points.gz" | cut -d' ' -f1)
say "D4SF3S_STAGE_$ARM (c) reference mesh md5 base=$MB src=$MS"
test "$MB" = "$MS" || { say "ABORT (c) $SRC carries a DEFORMED reference mesh"; exit 5; }
test "$MB" = "0fb1935a9b8781b73ac4ccb136e3ec68" || { say "ABORT (c) reference mesh is not D4's registered mesh (0fb1935a...)"; exit 5; }
say "D4SF3S_STAGE_$ARM (c) OK -- undeformed reference mesh 0fb1935a..., both rows share it"

# ---- (d) COPY with mtime semantics PINNED and a second datum written ------
say "D4SF3S_STAGE_$ARM (d) mtime semantics = cp -a, PRESERVE"
COPY_EPOCH=$(date -u +%s)
cp -a "$SRC" "$DST" || { say "ABORT (d) copy failed"; exit 4; }
echo "$COPY_EPOCH" > "$DST/.d4s_f3s_stage_${ARM}_copy_epoch" || { say "ABORT (d) cannot write copy datum"; exit 4; }
say "D4SF3S_STAGE_$ARM (d) copied, copy_epoch=$COPY_EPOCH written to .d4s_f3s_stage_${ARM}_copy_epoch"
say "D4SF3S_STAGE_$ARM (d) arm O age datum carried over = $(cat "$DST/.d4_age_datum")"
NSRC1=$(find "$SRC" | wc -l); OA=$(stat -c '%Y %s' "$SRC/OptView.hst")
test "$NSRC0" = "$NSRC1" && test "$OB" = "$OA" || { say "ABORT (a) SOURCE CHANGED during the copy: $NSRC0 -> $NSRC1, OptView [$OB] -> [$OA]"; exit 5; }
say "D4SF3S_STAGE_$ARM (a) POST-COPY: source intact ($NSRC1 entries, OptView.hst [$OA])"

# ---- (e) stage the FROZEN instruments into the run root, md5-asserted -----
( cd "$CASE_D4" && md5sum -c d4_repair_instruments.md5 ) >> "$EV" 2>&1 || { say "ABORT (e) repair-instrument md5 in $CASE_D4"; exit 4; }
cp -a "$CASE_D4/d4_repair_instruments.md5" "$BASE/" || { say "ABORT (e) cannot stage md5 list"; exit 4; }
for f in d4_endpoint_locus.py d4_endpoint_physical.py d4_accept_primal.py d4_accept_compare.py; do
  cp -a "$CASE_D4/$f" "$BASE/$f" || { say "ABORT (e) cannot stage $f"; exit 4; }
done
( cd "$BASE" && md5sum -c d4_repair_instruments.md5 ) >> "$EV" 2>&1 || { say "ABORT (e) repair-instrument md5 in $BASE"; exit 4; }
say "D4SF3S_STAGE_$ARM (e) OK -- frozen D4-DEF-4 repair instruments identical to curriculum_D4"
# the producer and the extractor come from the source item's run root (both items carry the same frozen bytes)
( cd "$HERE" && md5sum -c d4s_f3s_instruments.md5 ) >> "$EV" 2>&1 || { say "ABORT (e) instrument md5 in $HERE"; exit 4; }
cp -a "$HERE/d4s_f3s_instruments.md5" "$HERE/d4s_f3s_fd_endpoint.py" "$HERE/d4s_f3s_accept.py" "$BASE/" || { say "ABORT (e) cannot stage this item's instruments"; exit 4; }
cp -a "$SRC_ROOT/d4_opt_runScript.py" "$SRC_ROOT/d4_extract_endpoint.py" "$BASE/" || { say "ABORT (e) cannot stage producer/extractor"; exit 4; }
echo "2906d52a5dbed2bacbaeaf85a37d3fe8  $BASE/d4_opt_runScript.py" | md5sum -c - >> "$EV" 2>&1 || { say "ABORT (e) producer md5"; exit 4; }
echo "ee7d3c99fd716da23779cb651961918e  $BASE/d4_extract_endpoint.py" | md5sum -c - >> "$EV" 2>&1 || { say "ABORT (e) extractor md5"; exit 4; }
( cd "$BASE" && md5sum -c d4s_f3s_instruments.md5 ) >> "$EV" 2>&1 || { say "ABORT (e) instrument md5 in $BASE"; exit 4; }
say "D4SF3S_STAGE_$ARM (e) OK -- producer 2906d52a..., extractor ee7d3c99..., this item's instruments per d4s_f3s_instruments.md5"

# ---- (f) THE D4-DEF-6 REPAIR: drop ARM O's OUTPUT TIME DIRS from the COPY -
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
say "D4SF3S_STAGE_$ARM (f) removed $NREM arm-O output directories from the COPY"
[ "$NREM" -gt 0 ] || { say "ABORT (f) removed ZERO directories -- a repair that removes nothing is a no-op"; exit 5; }
NLEFT=$(find "$DST" -maxdepth 2 -type d -regextype posix-extended -regex '.*/(processor[0-9]+/)?[0-9]+\.[0-9]+' ! -name '0' 2>/dev/null | wc -l)
say "D4SF3S_STAGE_$ARM (f) pseudo-time directories remaining under $DST = $NLEFT (required 0)"
[ "$NLEFT" -eq 0 ] || { say "ABORT (f) pseudo-time directories survive"; exit 5; }
test -f "$DST/processor0/0/U.gz" || { say "ABORT (f) the START-TIME FIELDS were removed"; exit 5; }
test -f "$DST/OptView.hst" || { say "ABORT (f) OptView.hst removed"; exit 5; }
test -f "$DST/dRdWColoring_4.bin" || { say "ABORT (f) colouring removed -- the arm would be repriced"; exit 5; }
test -f "$DST/constant/polyMesh/points.gz" || { say "ABORT (f) reference mesh removed"; exit 5; }
NSRCT=$(ls -d "$SRC"/processor0/[0-9]*/ 2>/dev/null | wc -l)
say "D4SF3S_STAGE_$ARM (f) SOURCE INTACT assertion: time directories under $SRC/processor0 = $NSRCT (required > 1)"
[ "$NSRCT" -gt 1 ] || { say "ABORT (f) the source tree lost its time directories"; exit 5; }
# the inherited decomposition is the registered input (D4-SHIPPED Addendum 2e A2e.2 (b)); record its identity
for p in 0 1 2 3; do
  say "D4SF3S_STAGE_$ARM (g) processor$p polyMesh md5 $(cat "$DST/processor$p/constant/polyMesh/owner.gz" "$DST/processor$p/constant/polyMesh/neighbour.gz" "$DST/processor$p/constant/polyMesh/faces.gz" "$DST/processor$p/constant/polyMesh/points.gz" | md5sum | cut -c1-12)"
done
say "D4SF3S_STAGE_$ARM READY -- the launcher may now run arm $ARM in $DST"
exit 0
