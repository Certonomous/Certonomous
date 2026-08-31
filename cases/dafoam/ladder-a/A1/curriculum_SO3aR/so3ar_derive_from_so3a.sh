#!/usr/bin/env bash
# =============================================================================
# SO-3aR DERIVATION FROM SO-3a -- the MECHANICAL half, recorded so it is
# reproducible rather than described.
#
# SO-3a died at its second arm on 2026-08-31T18:43:21Z with item verdict
# NOT A RESULT.  Its gates are CLOSED (first compute happened), so SO-3aR is a
# SUCCESSOR and not an edit: SO-3a's frozen documents and instruments are NEVER
# rewritten by this script -- it READS them and WRITES a new tree.
#
# This script performs ONLY the item-token rename.  Every SUBSTANTIVE delta
# (the producer pin, the by-role pin census, the re-pinning) is applied AFTER
# this script by named edits, and each is enumerated in
# `PREREGISTRATION.md` AMENDMENT-free section "WHAT IS NEW".
#
# THE RENAME RULES, in this order.  They are case-disjoint, so no rule can
# consume another's output:
#   1. SO-3a  -> SO-3aR   (prose self-reference; hyphen form)
#   2. SO3a   -> SO3aR    (item token: run-root name, artefact names, dir name)
#   3. SO3A   -> SO3AR    (shell/marker tokens: SO3A_XF, SO3A_X_WRITTEN, ...)
#   4. so3a   -> so3ar    (file names: so3a_grade.py -> so3ar_grade.py)
# Rule 1 runs first so that rule 2 cannot see `SO-3a`; rules 2/3/4 differ in
# case at the third character and cannot match each other's output.
#
# WHAT IT MUST NOT TOUCH, asserted below rather than hoped for: every
# reference to SO-1a, SO-1b, SO-1bR, SO-1c, SO-2a, D4, D6, D6R, D13, D15, D16,
# W3 and the tutorial checkout.  Those are QUOTATIONS from other items and a
# rename that moved one would be a falsified citation.
# =============================================================================
set -u
SRC=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3a
DST=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR
[ -d "$SRC" ] || { echo "ABORT parent absent: $SRC"; exit 2; }
mkdir -p "$DST"

FILES="so3a_chain_driver.sh so3a_run_arm.sh so3a_xf.py so3a_grade.py \
so3a_runScript.py so3a_aggregate_memory.py so3a_stop_marker.sh \
so3a_groot5_selftest.sh so3a_xf_selftest.py so3a_decomposeParDict"

# ---- PARENT MD5s CAPTURED BEFORE THE READ, so the derivation names the exact
# ---- bytes it derived from.  A derivation from unnamed bytes is not a
# ---- derivation.
echo "SO3AR_DERIVE parent_md5s:"
for f in $FILES; do
  [ -f "$SRC/$f" ] || { echo "ABORT parent file absent: $SRC/$f"; exit 2; }
  echo "  $(md5sum "$SRC/$f")"
done

N=0
for f in $FILES; do
  g=$(printf '%s' "$f" | sed 's/^so3a_/so3ar_/')
  sed -e 's/SO-3a/SO-3aR/g' -e 's/SO3a/SO3aR/g' -e 's/SO3A/SO3AR/g' -e 's/so3a/so3ar/g' \
      "$SRC/$f" > "$DST/$g" || { echo "ABORT sed failed on $f"; exit 2; }
  [ -x "$SRC/$f" ] && chmod +x "$DST/$g"
  N=$((N+1))
done
echo "SO3AR_DERIVE renamed=$N"

# ---- THE NEGATIVE ASSERTION.  Every sibling-item citation must survive the
# ---- rename byte for byte.  Counted on BOTH sides and compared; a count that
# ---- moved means the rename ate a quotation.
FAIL=0
for tok in 'SO-1a' 'SO-1b' 'SO-1bR' 'SO-1c' 'SO-2a' 'so2a_' 'so1b' 'so1br' \
           'D4S_' 'D6R' 'D15' 'D16' 'W3' 'NACA0012' 'dafoam-tutorials'; do
  a=0; b=0
  for f in $FILES; do
    g=$(printf '%s' "$f" | sed 's/^so3a_/so3ar_/')
    a=$((a + $(grep -o -- "$tok" "$SRC/$f" | wc -l)))
    b=$((b + $(grep -o -- "$tok" "$DST/$g" | wc -l)))
  done
  if [ "$a" -ne "$b" ]; then echo "  RENAME ATE A CITATION $tok parent=$a child=$b"; FAIL=1
  else echo "  citation intact $tok n=$a"; fi
done

# ---- THE POSITIVE ASSERTION.  Not one `so3a`/`SO3a`/`SO3A`/`SO-3a` token may
# ---- survive in the child.  A rename that half-fired leaves a file writing
# ---- into the PARENT's run root, which is the worst outcome available here.
LEFT=0
for f in $FILES; do
  g=$(printf '%s' "$f" | sed 's/^so3a_/so3ar_/')
  n=$(grep -oE 'so3a[^r]|SO3a[^R]|SO3A[^R]|SO-3a[^R]' "$DST/$g" | wc -l)
  [ "$n" -eq 0 ] || { echo "  PARENT TOKEN SURVIVED in $g: $n"; LEFT=$((LEFT+n)); }
done
[ "$LEFT" -eq 0 ] && echo "  no parent token survives in any derived file" || FAIL=1

[ "$FAIL" -eq 0 ] && echo "SO3AR_DERIVE OK" || echo "SO3AR_DERIVE FAILED"
exit "$FAIL"
