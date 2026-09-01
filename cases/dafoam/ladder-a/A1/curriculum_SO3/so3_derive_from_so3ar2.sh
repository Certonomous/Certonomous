#!/usr/bin/env bash
# =============================================================================
# SO-3 DERIVATION FROM SO-3aR2 -- the MECHANICAL half, recorded so it is
# reproducible rather than described.
#
# SO-3aR2 is the GRADIENT rung and it is CLOSED: item verdict GATE FAIL, rows
# {PATCHED: PASS, SHIPPED: GATE FAIL}, graded
# 2026-08-31T23:02:21Z at
# /home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient/SO3aR2_grade_20260831T230221Z.json
# SO-3 is the OPTIMISATION rung that SO-3aR2's gradient makes admissible
# (`SO3_MULTIPOINT_SCOPE_MEMO.md` section 5 item 2: "SO-3 proper is its
# optimisation rung").  It is a DIFFERENT ITEM, not an edit: SO-3aR2's frozen
# document and instruments are NEVER rewritten by this script -- it READS them
# and WRITES a new tree.
#
# THE ID IS SANAA'S OWN.  Standing directives 2026-08-27T16:54Z section 4,
# verbatim: "SO-3 Multipoint (2-3 Mach/alpha) weighted objective."  No successor
# suffix is derived, because SO-3 is not a successor of anything -- SO-3a,
# SO-3aR and SO-3aR2 were the gradient sub-rung SO-3 required.
#
# This script performs ONLY the item-token rename plus the ONE run-root suffix
# change, which is anchored to the ALREADY-RENAMED self token so it cannot reach
# a grandparent citation.  Every SUBSTANTIVE delta (the optimiser, the C-188
# cap-frame repair, the manifest age guard, the stall abort, the endpoint FD
# arms, the section 9 gating, the margin-to-floor report, the re-pinning) is
# applied AFTER this script by named edits.
#
# THE RENAME RULES, in this order:
#   1. SO-3aR2 -> SO-3     (prose self-reference; hyphen form)
#   2. SO3aR2  -> SO3      (item token: run-root name, artefact names, dir name)
#   3. SO3AR2  -> SO3      (shell/marker tokens: SO3AR2_XF, SO3AR2_X_WRITTEN ...)
#   4. so3ar2  -> so3      (file names: so3ar2_grade.py -> so3_grade.py)
#   5. CURRICULUM-SO3-a1-naca0012-alpha-multipoint-gradient
#        -> CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation
#      ANCHORED ON `CURRICULUM-SO3-` WITH ITS TRAILING HYPHEN.  The unanchored
#      form `-alpha-multipoint-gradient` also occurs inside
#      `CURRICULUM-SO3a-...` and `CURRICULUM-SO3aR-...`, which are the
#      GRANDPARENT and PARENT run roots and hold closed, graded records.  An
#      unanchored rule would have falsified both, which is the SO-3aR falsified-
#      citation failure exactly.  `CURRICULUM-SO3-` cannot match
#      `CURRICULUM-SO3a-` because character 15 is a hyphen in one and `a` in the
#      other.
# Rules 1-4 are disjoint in case or in the hyphen and sed does not rescan its
# own output within a single -e chain in a way that could let one consume
# another: rule 1's output carries a hyphen rules 2-4 cannot produce, and rules
# 2/3/4 differ in case at characters 3-5.
#
# WHAT IT MUST NOT TOUCH, asserted below rather than hoped for:
#   * every PARENT and GRANDPARENT citation -- `SO-3aR` not followed by `2`,
#     `SO-3a` not followed by `R`, `so3ar_`, `so3a_`, `CURRICULUM-SO3a-`,
#     `CURRICULUM-SO3aR-`.  All three are different items with different run
#     roots and standing verdicts.
#   * every SIBLING citation -- SO-1a, SO-1b, SO-1bR, SO-1c, SO-2a, SO-2M, D4,
#     D6, D6R, D13, D15, D16, D19, W3 and the tutorial checkout.
#
# AND THE THING A RENAME CANNOT DO, stated here because this family has paid for
# it twice: A MECHANICAL RENAME MOVES TOKENS; IT CANNOT MAKE PROSE TRUE.  Every
# md5 pin in the derived tree is STALE THE INSTANT THIS SCRIPT RUNS, because the
# rename rewrites the very bytes the pins pin (the SO-2M first-arm failure).  And
# every path, directory and artefact NAME the derived prose cites must be
# re-checked against the disk (the SO-3aR falsified-citation failure, which
# SO-3aR2 inherited and did not repair -- see so3_run_arm.sh's G-ROOT.2 block).
# `so3_pin_census.py` and `so3_path_census.py` do both, and this script REFUSES
# to declare success until it has invalidated every pin it copied.
# =============================================================================
set -u
SRC=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3aR2
DST=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO3
[ -d "$SRC" ] || { echo "ABORT parent absent: $SRC"; exit 2; }
mkdir -p "$DST"

FILES="so3ar2_chain_driver.sh so3ar2_run_arm.sh so3ar2_xf.py so3ar2_grade.py \
so3ar2_runScript.py so3ar2_aggregate_memory.py so3ar2_stop_marker.sh \
so3ar2_xf_selftest.py so3ar2_decomposeParDict so3ar2_pin_census.py"

# ---- PARENT MD5s CAPTURED BEFORE THE READ, so the derivation names the exact
# ---- bytes it derived from.  A derivation from unnamed bytes is not a
# ---- derivation.
echo "SO3_DERIVE parent_md5s:"
for f in $FILES; do
  [ -f "$SRC/$f" ] || { echo "ABORT parent file absent: $SRC/$f"; exit 2; }
  echo "  $(md5sum "$SRC/$f")"
done

N=0
for f in $FILES; do
  g=$(printf '%s' "$f" | sed 's/^so3ar2_/so3_/')
  sed -e 's/SO-3aR2/SO-3/g' \
      -e 's/SO3aR2/SO3/g' \
      -e 's/SO3AR2/SO3/g' \
      -e 's/so3ar2/so3/g' \
      -e 's#CURRICULUM-SO3-a1-naca0012-alpha-multipoint-gradient#CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation#g' \
      "$SRC/$f" > "$DST/$g" || { echo "ABORT sed failed on $f"; exit 2; }
  if [ -x "$SRC/$f" ]; then chmod +x "$DST/$g"; fi
  N=$((N+1))
done
echo "SO3_DERIVE renamed=$N"

# ---- the reference OpenFOAM bytes the comparator's selftest requires.  They are
# ---- GITIGNORED and are copied, not renamed: they are REAL LOGS FROM SO-1a's
# ---- run root and their names are quotations, not item tokens.
mkdir -p "$DST/reference"
REFN=0
for r in REAL_SO1a_MESH_checkMesh.log REAL_SO1a_X-S_arm.log; do
  if [ -f "$SRC/reference/$r" ]; then
    cp -a "$SRC/reference/$r" "$DST/reference/$r" || { echo "ABORT reference copy $r"; exit 2; }
    REFN=$((REFN+1))
  else
    echo "  reference absent in parent (NOT copied, NOT claimed): $r"
  fi
done
echo "SO3_DERIVE reference_copied=$REFN"

FAIL=0

# ---- THE NEGATIVE ASSERTION.  Every citation that must survive is counted on
# ---- BOTH sides and compared; a count that moved means the rename ate a
# ---- quotation.  The PARENT and GRANDPARENT tokens are first because they are
# ---- the ones a careless rule set eats.
for tok in 'so3ar_' 'so3a_' 'CURRICULUM-SO3a-' 'CURRICULUM-SO3aR-' \
           'SO-1a' 'SO-1b' 'SO-1bR' 'SO-1c' 'SO-2a' 'so2a_' 'SO-2M' \
           'D4S_' 'D6R' 'D13' 'D15' 'D16' 'D19' 'W3' 'NACA0012' 'dafoam-tutorials'; do
  a=0; b=0
  for f in $FILES; do
    g=$(printf '%s' "$f" | sed 's/^so3ar2_/so3_/')
    # `grep -c` EXITS 1 ON A ZERO COUNT and would kill an && chain or a set -e
    # shell; `grep -o | wc -l` always exits 0 through the pipe's last stage.
    a=$((a + $(grep -o -- "$tok" "$SRC/$f" 2>/dev/null | wc -l)))
    b=$((b + $(grep -o -- "$tok" "$DST/$g" 2>/dev/null | wc -l)))
  done
  if [ "$a" -ne "$b" ]; then echo "  RENAME ATE A CITATION $tok parent=$a child=$b"; FAIL=1
  else echo "  citation intact $tok n=$a"; fi
done

# ---- `SO-3aR` NOT FOLLOWED BY `2` is the PARENT; `SO-3a` NOT FOLLOWED BY `R`
# ---- is the GRANDPARENT.  Counted separately, because a bare grep for either
# ---- would also count this item's own renamed token.
a=0; b=0
for f in $FILES; do
  g=$(printf '%s' "$f" | sed 's/^so3ar2_/so3_/')
  a=$((a + $(grep -oE 'SO-3aR[^2]' "$SRC/$f" 2>/dev/null | wc -l)))
  b=$((b + $(grep -oE 'SO-3aR[^2]' "$DST/$g" 2>/dev/null | wc -l)))
done
if [ "$a" -ne "$b" ]; then echo "  RENAME ATE A PARENT CITATION SO-3aR parent=$a child=$b"; FAIL=1
else echo "  citation intact SO-3aR(not-2) n=$a"; fi

a=0; b=0
for f in $FILES; do
  g=$(printf '%s' "$f" | sed 's/^so3ar2_/so3_/')
  a=$((a + $(grep -oE 'SO-3a[^R]' "$SRC/$f" 2>/dev/null | wc -l)))
  b=$((b + $(grep -oE 'SO-3a[^R]' "$DST/$g" 2>/dev/null | wc -l)))
done
if [ "$a" -ne "$b" ]; then echo "  RENAME ATE A GRANDPARENT CITATION SO-3a parent=$a child=$b"; FAIL=1
else echo "  citation intact SO-3a(not-R) n=$a"; fi

# ---- THE POSITIVE ASSERTION.  Not one bare `so3ar2`/`SO3aR2`/`SO3AR2`/`SO-3aR2`
# ---- token may survive in the child.  A rename that half-fired leaves a file
# ---- writing into the PARENT's run root -- and that root holds a graded,
# ---- closed record.
LEFT=0
for f in $FILES; do
  g=$(printf '%s' "$f" | sed 's/^so3ar2_/so3_/')
  n=$(grep -oE 'so3ar2|SO3aR2|SO3AR2|SO-3aR2' "$DST/$g" 2>/dev/null | wc -l)
  if [ "$n" -ne 0 ]; then echo "  PARENT TOKEN SURVIVED in $g: $n"; LEFT=$((LEFT+n)); fi
done
if [ "$LEFT" -eq 0 ]; then echo "  no parent token survives in any derived file"; else FAIL=1; fi

# ---- THE RUN ROOT ASSERTION.  The derived tree must address ITS OWN root and
# ---- must not carry the parent's or grandparent's gradient-rung root as its
# ---- own BASE.  Counted, not eyeballed.
# ---- SCOPED TO THE DERIVED FILES, NEVER TO A GLOB.  This script LIVES in $DST
# ---- and SPELLS both root names in its own rule 5, so a `$DST/so3_*.sh` glob
# ---- counts THIS FILE and the assertion fires on its own source.  It did, on
# ---- the first drive: n=3, all three inside this script.  A check whose subject
# ---- includes the checker is not a check.
DERIVED=""
for f in $FILES; do DERIVED="$DERIVED $DST/$(printf '%s' "$f" | sed 's/^so3ar2_/so3_/')"; done
OWN=$(grep -ho 'CURRICULUM-SO3-a1-naca0012-alpha-multipoint-optimisation' $DERIVED 2>/dev/null | wc -l)
STALE=$(grep -ho 'CURRICULUM-SO3-a1-naca0012-alpha-multipoint-gradient' $DERIVED 2>/dev/null | wc -l)
echo "  own run root cited n=$OWN ; stale gradient-suffix self root n=$STALE"
if [ "$OWN" -lt 1 ] || [ "$STALE" -ne 0 ]; then echo "  RUN ROOT ASSERTION FAILED"; FAIL=1; fi

# ---- THE PIN INVALIDATION.  EVERY md5 constant copied by this script names the
# ---- PARENT's bytes and is therefore WRONG for the child, by construction.
# ---- This script refuses to report success while any of them still equals a
# ---- parent value: they are rewritten to a fail-closed sentinel that CANNOT be
# ---- an md5 (it is not 32 hex), so `md5sum -c` FAILS CLOSED, and they are set
# ---- for real only after the last substantive edit, all together.
# ---- SO-2M lost its first arm to exactly the opposite choice: three md5 pins
# ---- inherited through an item-token rename were stale the instant the rename
# ---- ran, and they LOOKED like pins.
SENT='UNSET-PIN-SET-AFTER-THE-LAST-EDIT-FAILS-CLOSED'
STALEPINS=0
for g in so3_chain_driver.sh so3_run_arm.sh so3_xf.py; do
  [ -f "$DST/$g" ] || continue
  n=$(grep -cE '^(MD5_[A-Z_]+|PRODUCER_MD5|MD5)=[0-9a-f]{32}' "$DST/$g" 2>/dev/null || true)
  # `grep -c` returns 1 and prints 0 on no match; `|| true` keeps the chain alive
  # and the printed 0 is the value we want.
  STALEPINS=$((STALEPINS + n))
  sed -i -E "s/^(MD5_[A-Z_]+)=[0-9a-f]{32}/\\1=$SENT/" "$DST/$g"
  sed -i -E "s/^(PRODUCER_MD5) *= *\"[0-9a-f]{32}\"/\\1 = \"$SENT\"/" "$DST/$g"
done
echo "  stale parent pins found and INVALIDATED to a fail-closed sentinel: $STALEPINS"
REMAIN=$(grep -hcE '^(MD5_[A-Z_]+)=[0-9a-f]{32}' "$DST"/so3_chain_driver.sh "$DST"/so3_run_arm.sh 2>/dev/null | paste -sd+ | bc 2>/dev/null || echo 0)
if [ "${REMAIN:-0}" -ne 0 ]; then echo "  A PARENT PIN SURVIVED INVALIDATION: $REMAIN"; FAIL=1; fi

if [ "$FAIL" -eq 0 ]; then echo "SO3_DERIVE OK"; else echo "SO3_DERIVE FAILED"; fi
exit "$FAIL"
