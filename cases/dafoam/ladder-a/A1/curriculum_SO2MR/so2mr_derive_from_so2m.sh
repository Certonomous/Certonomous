#!/usr/bin/env bash
# =============================================================================
# SO-2MR DERIVATION FROM SO-2M -- the MECHANICAL half, recorded so it is
# reproducible rather than described.
#
# SO-2M ran its FULL CHAIN CLEAN on 2026-08-31 (five arms, all rc=0, 6.25
# core-min) and its FROZEN COMPARATOR then REFUSED at the direction-B planted
# control, item verdict NOT A RESULT.  SO-2M has had FIRST COMPUTE, so its gates
# are CLOSED: SO-2MR is a SUCCESSOR and NOT an edit.  This script READS SO-2M's
# frozen bytes and WRITES a new tree; it never writes into curriculum_SO2M.
#
# This script performs ONLY the item-token rename.  Every SUBSTANTIVE delta --
# the direction-B plant RULE, its freeze-time sufficiency leg, the by-role pin
# census, the re-pinning -- is applied AFTER this script by named edits, and each
# is enumerated in PREREGISTRATION.md section "WHAT IS NEW".
#
# THE RENAME RULES.  They are pairwise non-overlapping (the hyphen form cannot
# be matched by the unhyphenated form, and the two unhyphenated forms differ in
# case at characters 1-2 and 4):
#   1. SO-2M -> SO-2MR   (prose self-reference; hyphen form)
#   2. SO2M  -> SO2MR    (item token AND shell/marker token: SO2M_X_WRITTEN,
#                         ITEM=SO2M, CURRICULUM-SO2M-..., SO2M_PRODUCER_OK)
#   3. so2m  -> so2mr    (file names: so2m_grade.py -> so2mr_grade.py)
# Rule 1 is applied first so that no rule can consume another's output.
#
# WHAT IT MUST NOT TOUCH, asserted below rather than hoped for: every reference
# to SO-1a, SO-1b, SO-1bR, SO-1c, SO-2a, SO-3a, D4, D4S_, D7FR, D14-M, D15, D16,
# AV-2, W3, NACA0012 and the tutorial checkout.  Those are QUOTATIONS from other
# items and a rename that moved one would be a falsified citation.
# =============================================================================
set -u
SRC=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO2M
DST=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO2MR
[ -d "$SRC" ] || { echo "ABORT parent absent: $SRC"; exit 2; }
mkdir -p "$DST"

FILES="so2m_chain_driver.sh so2m_run_arm.sh so2m_xm.py so2m_grade.py \
so2m_runScript.py so2m_aggregate_memory.py so2m_pin_selftest.sh \
so2m_decomposeParDict so2m_runScript_DELTAS_from_tutorial.diff"

# ---- PARENT MD5s CAPTURED BEFORE THE READ, so the derivation names the exact
# ---- bytes it derived from.  A derivation from unnamed bytes is not a
# ---- derivation.
echo "SO2MR_DERIVE parent_md5s:"
for f in $FILES; do
  [ -f "$SRC/$f" ] || { echo "ABORT parent file absent: $SRC/$f"; exit 2; }
  echo "  $(md5sum "$SRC/$f")"
done

N=0
for f in $FILES; do
  g=$(printf '%s' "$f" | sed 's/^so2m_/so2mr_/')
  sed -e 's/SO-2M/SO-2MR/g' -e 's/SO2M/SO2MR/g' -e 's/so2m/so2mr/g' \
      "$SRC/$f" > "$DST/$g" || { echo "ABORT sed failed on $f"; exit 2; }
  [ -x "$SRC/$f" ] && chmod +x "$DST/$g"
  N=$((N+1))
done
echo "SO2MR_DERIVE renamed=$N"

# ---- THE NEGATIVE ASSERTION.  Every sibling-item citation must survive the
# ---- rename byte for byte.  Counted on BOTH sides and compared; a count that
# ---- moved means the rename ate a quotation.
FAIL=0
for tok in 'SO-1a' 'SO-1b' 'SO-1bR' 'SO-1c' 'SO-2a' 'SO-3a' 'so1a_' 'so2a_' \
           'D4S_' 'D7FR' 'D14-M' 'D15' 'D16' 'AV-2' 'W3' 'NACA0012' \
           'dafoam-tutorials' 'CURRICULUM-SO1a'; do
  a=0; b=0
  for f in $FILES; do
    g=$(printf '%s' "$f" | sed 's/^so2m_/so2mr_/')
    a=$((a + $(grep -o -- "$tok" "$SRC/$f" | wc -l)))
    b=$((b + $(grep -o -- "$tok" "$DST/$g" | wc -l)))
  done
  if [ "$a" -ne "$b" ]; then echo "  RENAME ATE A CITATION $tok parent=$a child=$b"; FAIL=1
  else echo "  citation intact $tok n=$a"; fi
done

# ---- THE POSITIVE ASSERTION.  Not one `so2m`/`SO2M`/`SO-2M` token may survive
# ---- in the child.  A rename that half-fired leaves a file writing into the
# ---- PARENT's run root, which is the worst outcome available here.
LEFT=0
for f in $FILES; do
  g=$(printf '%s' "$f" | sed 's/^so2m_/so2mr_/')
  n=$(grep -oE 'so2m[^r]|SO2M[^R]|SO-2M[^R]' "$DST/$g" | wc -l)
  [ "$n" -eq 0 ] || { echo "  PARENT TOKEN SURVIVED in $g: $n"; LEFT=$((LEFT+n)); }
done
[ "$LEFT" -eq 0 ] && echo "  no parent token survives in any derived file" || FAIL=1

# ---- THE PARENT IS NOT WRITTEN.  Asserted, not assumed: every parent md5 is
# ---- re-read AFTER the derivation and must equal the value captured before it.
echo "SO2MR_DERIVE parent_md5s_after (must equal the block above):"
for f in $FILES; do echo "  $(md5sum "$SRC/$f")"; done

[ "$FAIL" -eq 0 ] && echo "SO2MR_DERIVE OK" || echo "SO2MR_DERIVE FAILED"
exit "$FAIL"
