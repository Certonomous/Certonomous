#!/usr/bin/env bash
# D4S-F3SR ENDPOINT-ARM STAGING -- D4S-F3S's `d4s_f3s_stage_arm.sh`
# (md5 f0d0dd3689db27239f1d1d60d429ef77, frozen at 8dfb4598) with the
# D4S-F3S-AGE-DEF-1 repair and nothing else.  Sources, steps (a)-(f), the
# mesh assertions and the instrument md5 asserts are that file's bytes.
#   F-S : /home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin/O -> <ROOT>/F-S
#   F-P : /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O         -> <ROOT>/F-P
#
# ===========================================================================
# D4S-F3S-AGE-DEF-1 -- THE DEFECT THIS FILE EXISTS NOT TO REPEAT.
#
# D4S-F3S graded 19 of 20 readings PASS and was recorded NOT A RESULT on ONE
# limb: G1's age clause, n_stale = 1, on `OptView.hst`.  `OptView.hst` is a
# STAGED INPUT of this item and never a product -- the predecessor's stager
# copied it with `cp -a` (:61 "mtime semantics = cp -a, PRESERVE", :63) and
# the item re-runs no optimiser.  A FILE THAT IS NEVER PRODUCED CAN NEVER
# POST-DATE THE LAUNCH, so the clause was unsatisfiable by construction.  The
# entry was inherited from the optimiser-arm shape, where D5's SOLVER_ARTEFACTS
# uses the same file CORRECTLY because there it genuinely is a product.
#
# The predecessor's 26/26 grader selftest could not catch it: its fixture
# CREATED `OptView.hst` fresh (`d4s_f3s_grade.py:599-601`) against a datum
# pinned at epoch 1000000000, so real staging semantics were never exercised.
# A PASSING SELFTEST IS WHAT MAKES THIS CLASS DANGEROUS.
#
# THE REPAIR IS THREE THINGS, and all three are in this file:
#   (1) SIBLING PROTECTION, step (d2).  `rm -f` the staged carry-over of this
#       item's own registered artefacts and the foreign datum, so a source
#       tree that ever acquires one cannot hand it to the run as a product.
#       Pattern: so1b_run_arm.sh:415, av1r_run_arm.sh:331.
#   (2) THE AGE REFERENCE IS TOUCHED LAST, step (g) -- after the copy, after
#       the rm, after the D4-DEF-6 drop -- and the datum is read FROM IT.
#       Pattern: so1b:431/432, av1r:352/353, d5_run_arm.sh:298/299.
#       REGISTERED DEPARTURE FROM THE SIBLINGS: they touch `0/` and read
#       `0/U`.  THIS ITEM MAY NOT.  pyDAFoam writes the primal end state back
#       into the time-0 directory at run end (DAFOAM_CHARTER.md section 6), and
#       it was MEASURED doing so in the predecessor's own arm --
#       CURRICULUM-D4S-F3S-a2-wing-cdmin/F-S/processor0/0/U.gz carries mtime
#       1787839098, 619 s AFTER that arm's staging datum 1787838479.  No
#       OpenFOAM field in this tree is safe as an immutable datum, so the
#       reference is a DEDICATED SENTINEL, `.d4s_f3sr_age_ref`, that nothing
#       in the container writes; its mtime is also frozen into an integer file
#       so a later rewrite of anything cannot move the recorded datum.
#   (3) THE STAGED-INPUT MANIFEST, step (h).  Every file this item carries in
#       and does not produce is named HERE, in the run root, with the source
#       path, the source md5 and both mtimes -- so the grader's exclusion is
#       CHECKED AGAINST DISK rather than trusted, and checked in the OPPOSITE
#       direction (a staged input must be NOT NEWER than the datum; a product
#       must be STRICTLY NEWER; the two clauses are complementary and
#       jointly exhaustive over the registered files).
# ===========================================================================
#
# Step (f) -- drop arm O's OUTPUT pseudo-time directories from the COPY
# (D4-DEF-6) -- is applied to BOTH arms (both are F3-class arms).
# The reference mesh is asserted UNDEFORMED against the SOURCE ITEM's own base/.
# NO GATE, THRESHOLD, BAND, CAP OR LABEL MOVES.  `set -e` does not gate at the
# top level; every step gates explicitly.
set -uo pipefail
ARM="${1:-}"
case "$ARM" in F-S|F-P) ;; *) echo "ABORT usage: d4s_f3sr_stage_arm.sh <F-S|F-P>"; exit 64 ;; esac
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3SR-a2-wing-cdmin
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE_D4=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D4
case "$ARM" in
  F-S) SRC_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin ;;
  F-P) SRC_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin ;;
esac
SRC="$SRC_ROOT/O"
DST="$BASE/$ARM"
EV="$BASE/${ARM}_STAGING_EVIDENCE.txt"
# THE REGISTERED PRODUCTS of this item's own run -- the age-checked set.
# Identical, name for name, to d4s_f3sr_grade.py's ARTEFACTS and to the
# launcher's G-COLD list.  A name here is a name the run MUST create.
PRODUCTS="d4_endpoint_dvs.json d4_endpoint_dvs_PHYSICAL.json d4_endpoint_dvs_DRIVERSCALED.json d4_major_history.json d4s_f3s_fd_endpoint.json d4s_f3s_fd_endpoint.jsonl d4s_f3s_accept.jsonl"
# THE REGISTERED STAGED INPUTS -- carried in, never produced, EXCLUDED FROM
# THE AGE CLAUSE BY NAME and gated by the INVERSE clause instead.
STAGED_INPUTS="OptView.hst opt_IPOPT.txt"
test -d "$BASE" || { echo "ABORT run root $BASE absent -- the chain driver creates it"; exit 5; }
: > "$EV"
say() { echo "$*" | tee -a "$EV"; }
say "D4SF3SR_STAGE_$ARM utc=$(date -u +%Y%m%dT%H%M%SZ) base=$BASE src=$SRC"
say "D4SF3SR_STAGE_$ARM REGISTERED_PRODUCTS=[$PRODUCTS]"
say "D4SF3SR_STAGE_$ARM REGISTERED_STAGED_INPUTS=[$STAGED_INPUTS]"

# ---- G-ROOT.1: this item's root only; the source root must be one of the two named
test "$(realpath -m "$BASE")" = "/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3SR-a2-wing-cdmin" || { say "ABORT G-ROOT.1"; exit 3; }
test "$(realpath -m "$SRC_ROOT")" != "$(realpath -m "$BASE")" || { say "ABORT G-ROOT.2 source equals this root"; exit 3; }

# ---- (a) COPY, NEVER MOVE.  Source must exist and must survive. ----------
test -d "$SRC" || { say "ABORT (a) source $SRC absent"; exit 5; }
test -f "$SRC/OptView.hst" || { say "ABORT (a) $SRC/OptView.hst absent -- no endpoint to read"; exit 5; }
test -f "$SRC/.d4_age_datum" || { say "ABORT (a) $SRC carries no .d4_age_datum -- not a graded arm O"; exit 5; }
test ! -e "$DST" || { say "ABORT (a) destination $DST already exists -- refusing to overwrite evidence"; exit 5; }
NSRC0=$(find "$SRC" | wc -l); OB=$(stat -c '%Y %s' "$SRC/OptView.hst")
say "D4SF3SR_STAGE_$ARM (a) OK src=$SRC entries=$NSRC0 OptView.hst=[$OB] dst=$DST does not exist"

# ---- (b) THE ANSWER FILES MUST NOT PRE-EXIST in the source. ---------------
# WIDENED (D4S-F3S-AGE-DEF-1): the predecessor's pattern list is kept verbatim
# and EVERY registered product name is added to it, so the assertion covers
# exactly the set the age clause will grade.  Nothing is removed.
N=$(find "$SRC" \( -name 'd4_endpoint_dvs*.json' -o -name 'd4_accept_primal.json' -o -name 'd4_fd_endpoint.json*' -o -name 'd4s_f3s_*' -o -name 'd4_major_history.json' \) 2>/dev/null | wc -l)
say "D4SF3SR_STAGE_$ARM (b) ASSERTION: count of pre-existing answer files under $SRC = $N (required 0)"
[ "$N" -eq 0 ] || { say "ABORT (b) an answer file exists in the source"; exit 5; }
# and the INVERSE assertion, which the predecessor did not make: every
# registered STAGED INPUT must be PRESENT in the source, or it is not a staged
# input and the exclusion below would be excusing an absence.
for si in $STAGED_INPUTS; do
  test -f "$SRC/$si" || { say "ABORT (b) registered staged input $si ABSENT from the source $SRC -- the exclusion would excuse an absence"; exit 5; }
done
say "D4SF3SR_STAGE_$ARM (b) OK -- all registered staged inputs present in the source, no registered product present"

# ---- (c) THE REFERENCE MESH IS THE UNDEFORMED ONE (source item's own base/)
MB=$(md5sum "$SRC_ROOT/base/constant/polyMesh/points.gz" | cut -d' ' -f1)
MS=$(md5sum "$SRC/constant/polyMesh/points.gz" | cut -d' ' -f1)
say "D4SF3SR_STAGE_$ARM (c) reference mesh md5 base=$MB src=$MS"
test "$MB" = "$MS" || { say "ABORT (c) $SRC carries a DEFORMED reference mesh"; exit 5; }
test "$MB" = "0fb1935a9b8781b73ac4ccb136e3ec68" || { say "ABORT (c) reference mesh is not D4's registered mesh (0fb1935a...)"; exit 5; }
say "D4SF3SR_STAGE_$ARM (c) OK -- undeformed reference mesh 0fb1935a..., both rows share it"

# ---- (d) COPY with mtime semantics PINNED --------------------------------
say "D4SF3SR_STAGE_$ARM (d) mtime semantics = cp -a, PRESERVE"
cp -a "$SRC" "$DST" || { say "ABORT (d) copy failed"; exit 4; }
say "D4SF3SR_STAGE_$ARM (d) copied; arm O age datum carried over = $(cat "$DST/.d4_age_datum")"
NSRC1=$(find "$SRC" | wc -l); OA=$(stat -c '%Y %s' "$SRC/OptView.hst")
test "$NSRC0" = "$NSRC1" && test "$OB" = "$OA" || { say "ABORT (a) SOURCE CHANGED during the copy: $NSRC0 -> $NSRC1, OptView [$OB] -> [$OA]"; exit 5; }
say "D4SF3SR_STAGE_$ARM (a) POST-COPY: source intact ($NSRC1 entries, OptView.hst [$OA])"

# ---- (d2) SIBLING PROTECTION -- REPAIR (1).  so1b:415 / av1r:331. --------
# Remove from the COPY every carry-over that could later be mistaken for a
# product of this run, and the foreign datum.  Recorded before removal.
NRM=0
for f in $PRODUCTS d4s_f3s_cmd.sh d4s_f3sr_cmd.sh .d4_age_datum .d4s_f3s_age_ref .d4s_f3sr_age_ref; do
  if [ -e "$DST/$f" ]; then
    say "D4SF3SR_STAGE_$ARM (d2) CARRY-OVER REMOVED name=$f mtime=$(stat -c '%Y' "$DST/$f") md5=$(md5sum "$DST/$f" 2>/dev/null | cut -d' ' -f1)"
    rm -f "$DST/$f" || { say "ABORT (d2) cannot remove carry-over $f"; exit 4; }
    NRM=$((NRM+1))
  fi
done
rm -f "$DST"/.d4s_f3s_stage_*_copy_epoch "$DST"/.d4s_f3sr_stage_*_copy_epoch 2>/dev/null
rm -f "$DST"/d4s_f3s_primal_*.log 2>/dev/null
say "D4SF3SR_STAGE_$ARM (d2) sibling protection: $NRM named carry-overs removed from the copy"
for f in $PRODUCTS; do
  test -e "$DST/$f" && { say "ABORT (d2) registered product $f SURVIVES in the copy"; exit 5; }
done
test -n "$(ls "$DST"/d4s_f3s_primal_* 2>/dev/null)" && { say "ABORT (d2) primal captures survive in the copy"; exit 5; }
say "D4SF3SR_STAGE_$ARM (d2) VERIFIED: zero registered products and zero primal captures remain in $DST"

# ---- (e) stage the FROZEN instruments into the run root, md5-asserted -----
( cd "$CASE_D4" && md5sum -c d4_repair_instruments.md5 ) >> "$EV" 2>&1 || { say "ABORT (e) repair-instrument md5 in $CASE_D4"; exit 4; }
cp -a "$CASE_D4/d4_repair_instruments.md5" "$BASE/" || { say "ABORT (e) cannot stage md5 list"; exit 4; }
for f in d4_endpoint_locus.py d4_endpoint_physical.py d4_accept_primal.py d4_accept_compare.py; do
  cp -a "$CASE_D4/$f" "$BASE/$f" || { say "ABORT (e) cannot stage $f"; exit 4; }
done
( cd "$BASE" && md5sum -c d4_repair_instruments.md5 ) >> "$EV" 2>&1 || { say "ABORT (e) repair-instrument md5 in $BASE"; exit 4; }
say "D4SF3SR_STAGE_$ARM (e) OK -- frozen D4-DEF-4 repair instruments identical to curriculum_D4"
# the producer and the extractor come from the source item's run root (both items carry the same frozen bytes)
( cd "$HERE" && md5sum -c d4s_f3sr_instruments.md5 ) >> "$EV" 2>&1 || { say "ABORT (e) instrument md5 in $HERE"; exit 4; }
cp -a "$HERE/d4s_f3sr_instruments.md5" "$HERE/d4s_f3s_fd_endpoint.py" "$HERE/d4s_f3s_accept.py" "$BASE/" || { say "ABORT (e) cannot stage this item's instruments"; exit 4; }
cp -a "$SRC_ROOT/d4_opt_runScript.py" "$SRC_ROOT/d4_extract_endpoint.py" "$BASE/" || { say "ABORT (e) cannot stage producer/extractor"; exit 4; }
echo "2906d52a5dbed2bacbaeaf85a37d3fe8  $BASE/d4_opt_runScript.py" | md5sum -c - >> "$EV" 2>&1 || { say "ABORT (e) producer md5"; exit 4; }
echo "ee7d3c99fd716da23779cb651961918e  $BASE/d4_extract_endpoint.py" | md5sum -c - >> "$EV" 2>&1 || { say "ABORT (e) extractor md5"; exit 4; }
( cd "$BASE" && md5sum -c d4s_f3sr_instruments.md5 ) >> "$EV" 2>&1 || { say "ABORT (e) instrument md5 in $BASE"; exit 4; }
say "D4SF3SR_STAGE_$ARM (e) OK -- producer 2906d52a..., extractor ee7d3c99..., this item's instruments per d4s_f3sr_instruments.md5"

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
say "D4SF3SR_STAGE_$ARM (f) removed $NREM arm-O output directories from the COPY"
[ "$NREM" -gt 0 ] || { say "ABORT (f) removed ZERO directories -- a repair that removes nothing is a no-op"; exit 5; }
NLEFT=$(find "$DST" -maxdepth 2 -type d -regextype posix-extended -regex '.*/(processor[0-9]+/)?[0-9]+\.[0-9]+' ! -name '0' 2>/dev/null | wc -l)
say "D4SF3SR_STAGE_$ARM (f) pseudo-time directories remaining under $DST = $NLEFT (required 0)"
[ "$NLEFT" -eq 0 ] || { say "ABORT (f) pseudo-time directories survive"; exit 5; }
test -f "$DST/processor0/0/U.gz" || { say "ABORT (f) the START-TIME FIELDS were removed"; exit 5; }
test -f "$DST/OptView.hst" || { say "ABORT (f) OptView.hst removed"; exit 5; }
test -f "$DST/dRdWColoring_4.bin" || { say "ABORT (f) colouring removed -- the arm would be repriced"; exit 5; }
test -f "$DST/constant/polyMesh/points.gz" || { say "ABORT (f) reference mesh removed"; exit 5; }
NSRCT=$(ls -d "$SRC"/processor0/[0-9]*/ 2>/dev/null | wc -l)
say "D4SF3SR_STAGE_$ARM (f) SOURCE INTACT assertion: time directories under $SRC/processor0 = $NSRCT (required > 1)"
[ "$NSRCT" -gt 1 ] || { say "ABORT (f) the source tree lost its time directories"; exit 5; }
# the inherited decomposition is the registered input (D4-SHIPPED Addendum 2e A2e.2 (b)); record its identity
for p in 0 1 2 3; do
  say "D4SF3SR_STAGE_$ARM (g0) processor$p polyMesh md5 $(cat "$DST/processor$p/constant/polyMesh/owner.gz" "$DST/processor$p/constant/polyMesh/neighbour.gz" "$DST/processor$p/constant/polyMesh/faces.gz" "$DST/processor$p/constant/polyMesh/points.gz" | md5sum | cut -c1-12)"
done

# ---- (g) THE AGE REFERENCE, TOUCHED LAST -- REPAIR (2). -------------------
# so1b:431 / av1r:352 / d5:298 touch `0/` and read `0/U`.  THIS ITEM MAY NOT:
# pyDAFoam writes the primal end state back into the time-0 directory at run
# end (DAFOAM_CHARTER.md section 6), MEASURED in the predecessor's own F-S arm
# (processor0/0/U.gz mtime 1787839098 vs staging datum 1787838479).  So the
# reference is a DEDICATED SENTINEL that nothing in the container writes, it is
# created and touched AFTER the copy, AFTER the rm and AFTER the (f) drop, and
# the integer is frozen into a second file so no later rewrite can move it.
AGE_REF=".d4s_f3sr_age_ref"
: > "$DST/$AGE_REF" || { say "ABORT (g) cannot create the age reference"; exit 5; }
touch "$DST/$AGE_REF" || { say "ABORT (g) cannot touch the age reference"; exit 5; }
AGE_DATUM=$(stat -c '%Y' "$DST/$AGE_REF")
[ -n "$AGE_DATUM" ] || { say "ABORT (g) age datum unreadable"; exit 5; }
echo "$AGE_DATUM" > "$DST/.d4s_f3sr_stage_${ARM}_copy_epoch" || { say "ABORT (g) cannot write copy datum"; exit 4; }
echo "$AGE_REF"    > "$DST/.d4s_f3sr_stage_${ARM}_age_ref"    || { say "ABORT (g) cannot write datum reference name"; exit 4; }
say "D4SF3SR_STAGE_$ARM (g) AGE DATUM $AGE_DATUM from $AGE_REF, TOUCHED LAST; frozen into .d4s_f3sr_stage_${ARM}_copy_epoch"
# THE DATUM MUST POST-DATE THE COPY.  Anything staged is at most as old as the
# copy; the datum is taken after it, so every staged file must be <= datum.
for si in $STAGED_INPUTS; do
  M=$(stat -c '%Y' "$DST/$si")
  [ "$M" -le "$AGE_DATUM" ] || { say "ABORT (g) staged input $si mtime $M is NEWER than the datum $AGE_DATUM -- it is not a staged input"; exit 5; }
done
say "D4SF3SR_STAGE_$ARM (g) VERIFIED: every registered staged input is NOT NEWER than the datum"

# ---- (h) THE STAGED-INPUT MANIFEST -- REPAIR (3). ------------------------
# The exclusion is REGISTERED, not silent: the grader reads this file, binds
# each excluded name to the SOURCE by md5, and applies the INVERSE age clause.
MAN="$DST/.d4s_f3sr_staged_inputs.json"
{
  printf '{"arm":"%s","src":"%s","age_datum":%s,"age_ref":"%s","staged_inputs":[' "$ARM" "$SRC" "$AGE_DATUM" "$AGE_REF"
  FIRST=1
  for si in $STAGED_INPUTS; do
    [ "$FIRST" = 1 ] || printf ','
    FIRST=0
    printf '{"name":"%s","src_md5":"%s","dst_md5":"%s","src_mtime":%s,"dst_mtime":%s,"produced_by_this_item":false}' \
      "$si" "$(md5sum "$SRC/$si" | cut -d' ' -f1)" "$(md5sum "$DST/$si" | cut -d' ' -f1)" \
      "$(stat -c '%Y' "$SRC/$si")" "$(stat -c '%Y' "$DST/$si")"
  done
  printf ']}\n'
} > "$MAN" || { say "ABORT (h) cannot write the staged-input manifest"; exit 4; }
python3 -c "
import json,sys
d=json.load(open('$MAN'))
bad=[r['name'] for r in d['staged_inputs'] if r['src_md5']!=r['dst_md5'] or r['dst_mtime']>d['age_datum']]
if bad:
    sys.stderr.write('manifest self-check failed: %r\n'%bad); sys.exit(1)
print('D4SF3SR_MANIFEST_OK n=%d age_datum=%d'%(len(d['staged_inputs']),d['age_datum']))
" >> "$EV" 2>&1 || { say "ABORT (h) staged-input manifest self-check FAILED"; exit 5; }
say "D4SF3SR_STAGE_$ARM (h) staged-input manifest written and self-checked: $(basename "$MAN")"
say "D4SF3SR_STAGE_$ARM READY -- the launcher may now run arm $ARM in $DST"
exit 0
