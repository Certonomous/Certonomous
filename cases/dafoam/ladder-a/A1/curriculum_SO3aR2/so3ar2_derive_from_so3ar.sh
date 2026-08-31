#!/usr/bin/env bash
# =============================================================================
# SO-3aR2 DERIVATION FROM SO-3aR -- the MECHANICAL half, recorded so it is
# reproducible rather than described.
#
# SO-3aR died at its second arm on 2026-08-31T20:22:15Z with item verdict
# NOT A RESULT (chain_rc=1, 1.800 core-min, 2 of 5 declared arms executed).  Its
# gates are CLOSED (first compute happened), so SO-3aR2 is a SUCCESSOR and not an
# edit: SO-3aR's and SO-3a's frozen documents and instruments are NEVER rewritten
# by this script -- it READS them and WRITES a new tree.
#
# THE SUCCESSOR ID IS DERIVED FROM PRECEDENT ON DISK, NOT GUESSED.  The first
# successor of an item appends `R` (SO-1a->SO-1aR, SO-1b->SO-1bR, SO-1c->SO-1cR,
# SO-2M->SO-2MR, SO-3a->SO-3aR).  `SO-3aR` is taken, so this is a SECOND
# successor, and the family's second-successor precedent is D12 -> D12R -> D12R2
# (`cases/dafoam/curriculum_D12R2/PREREGISTRATION.md:1` and its section 0, which
# states in terms that it SUPERSEDES `curriculum_D12R`, which itself superseded
# `curriculum_D12`).  Appending `2` to the R-form is therefore the precedent, and
# the id is `SO-3aR2`.
#
# This script performs ONLY the item-token rename.  Every SUBSTANTIVE delta
# (the per-point run_directory fix, the collision leg, the relative plant, the
# re-pinning) is applied AFTER this script by named edits, each enumerated in
# `PREREGISTRATION.md` section "WHAT IS NEW".
#
# THE RENAME RULES, in this order.  They are disjoint in case or in the hyphen,
# so no rule can consume another's output, and sed does not rescan its own:
#   1. SO-3aR -> SO-3aR2   (prose self-reference; hyphen form)
#   2. SO3aR  -> SO3aR2    (item token: run-root name, artefact names, dir name)
#   3. SO3AR  -> SO3AR2    (shell/marker tokens: SO3AR_XF, SO3AR_X_WRITTEN, ...)
#   4. so3ar  -> so3ar2    (file names: so3ar_grade.py -> so3ar2_grade.py)
# Rule 1 requires the hyphen, which rules 2-4 cannot produce.  Rules 2/3/4 differ
# in case at characters 3-5 and cannot match each other's output.
#
# WHAT IT MUST NOT TOUCH, asserted below rather than hoped for:
#   * every GRANDPARENT citation -- `SO-3a` not followed by `R`, `so3a_`,
#     `CURRICULUM-SO3a-`.  SO-3a is a different item with a different run root
#     and a standing `NOT A RESULT` verdict; a rename that moved one of those
#     would falsify a citation into a closed record.
#   * every SIBLING citation -- SO-1a, SO-1b, SO-1bR, SO-1c, SO-2a, D4, D6, D6R,
#     D13, D15, D16, W3 and the tutorial checkout.
# =============================================================================
set -u
SRC=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR
DST=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR2
[ -d "$SRC" ] || { echo "ABORT parent absent: $SRC"; exit 2; }
mkdir -p "$DST"

FILES="so3ar_chain_driver.sh so3ar_run_arm.sh so3ar_xf.py so3ar_grade.py \
so3ar_runScript.py so3ar_aggregate_memory.py so3ar_stop_marker.sh \
so3ar_groot5_selftest.sh so3ar_xf_selftest.py so3ar_decomposeParDict \
so3ar_pin_census.py"

# ---- PARENT MD5s CAPTURED BEFORE THE READ, so the derivation names the exact
# ---- bytes it derived from.  A derivation from unnamed bytes is not a
# ---- derivation.
echo "SO3AR2_DERIVE parent_md5s:"
for f in $FILES; do
  [ -f "$SRC/$f" ] || { echo "ABORT parent file absent: $SRC/$f"; exit 2; }
  echo "  $(md5sum "$SRC/$f")"
done

N=0
for f in $FILES; do
  g=$(printf '%s' "$f" | sed 's/^so3ar_/so3ar2_/')
  sed -e 's/SO-3aR/SO-3aR2/g' -e 's/SO3aR/SO3aR2/g' -e 's/SO3AR/SO3AR2/g' -e 's/so3ar/so3ar2/g' \
      "$SRC/$f" > "$DST/$g" || { echo "ABORT sed failed on $f"; exit 2; }
  [ -x "$SRC/$f" ] && chmod +x "$DST/$g"
  N=$((N+1))
done
echo "SO3AR2_DERIVE renamed=$N"

# ---- the reference OpenFOAM bytes the comparator's selftest requires.  They are
# ---- GITIGNORED (`.gitignore:270`, `cases/dafoam/**/*.log`) and are copied, not
# ---- renamed: they are REAL LOGS FROM SO-1a's run root and their names are
# ---- quotations, not item tokens.
mkdir -p "$DST/reference"
for r in REAL_SO1a_MESH_checkMesh.log REAL_SO1a_X-S_arm.log; do
  [ -f "$SRC/reference/$r" ] || { echo "ABORT reference absent: $SRC/reference/$r"; exit 2; }
  cp -a "$SRC/reference/$r" "$DST/reference/$r" || { echo "ABORT reference copy $r"; exit 2; }
done
echo "SO3AR2_DERIVE reference_copied=2"

# ---- THE NEGATIVE ASSERTION.  Every citation that must survive is counted on
# ---- BOTH sides and compared; a count that moved means the rename ate a
# ---- quotation.  The GRANDPARENT tokens are first because they are the ones a
# ---- careless rule set would eat.
FAIL=0
for tok in 'so3a_' 'CURRICULUM-SO3a-' 'SO-1a' 'SO-1b' 'SO-1bR' 'SO-1c' 'SO-2a' 'so2a_' \
           'D4S_' 'D6R' 'D15' 'D16' 'W3' 'NACA0012' 'dafoam-tutorials'; do
  a=0; b=0
  for f in $FILES; do
    g=$(printf '%s' "$f" | sed 's/^so3ar_/so3ar2_/')
    a=$((a + $(grep -o -- "$tok" "$SRC/$f" | wc -l)))
    b=$((b + $(grep -o -- "$tok" "$DST/$g" | wc -l)))
  done
  if [ "$a" -ne "$b" ]; then echo "  RENAME ATE A CITATION $tok parent=$a child=$b"; FAIL=1
  else echo "  citation intact $tok n=$a"; fi
done

# ---- `SO-3a` NOT FOLLOWED BY `R` is the grandparent and must survive; counted
# ---- separately because a bare `SO-3a` grep would also count `SO-3aR2`.
a=0; b=0
for f in $FILES; do
  g=$(printf '%s' "$f" | sed 's/^so3ar_/so3ar2_/')
  a=$((a + $(grep -oE 'SO-3a[^R]' "$SRC/$f" | wc -l)))
  b=$((b + $(grep -oE 'SO-3a[^R]' "$DST/$g" | wc -l)))
done
if [ "$a" -ne "$b" ]; then echo "  RENAME ATE A GRANDPARENT CITATION SO-3a parent=$a child=$b"; FAIL=1
else echo "  citation intact SO-3a(not-R) n=$a"; fi

# ---- THE POSITIVE ASSERTION.  Not one bare `so3ar`/`SO3aR`/`SO3AR`/`SO-3aR`
# ---- token may survive in the child.  A rename that half-fired leaves a file
# ---- writing into the PARENT's run root, which is the worst outcome available
# ---- here -- and the parent's run root holds a graded, closed record.
LEFT=0
for f in $FILES; do
  g=$(printf '%s' "$f" | sed 's/^so3ar_/so3ar2_/')
  n=$(grep -oE 'so3ar[^2]|SO3aR[^2]|SO3AR[^2]|SO-3aR[^2]' "$DST/$g" | wc -l)
  [ "$n" -eq 0 ] || { echo "  PARENT TOKEN SURVIVED in $g: $n"; LEFT=$((LEFT+n)); }
done
[ "$LEFT" -eq 0 ] && echo "  no parent token survives in any derived file" || FAIL=1

[ "$FAIL" -eq 0 ] && echo "SO3AR2_DERIVE OK" || echo "SO3AR2_DERIVE FAILED"
exit "$FAIL"
