#!/usr/bin/env bash
# =============================================================================
# Curriculum D19T -- THE CHAIN.
#
#   MESH -> T08 -> T10 -> T12 -> XT10 -> grade
#
# SEQUENTIAL, ONE ARM AT A TIME, ON ONE REGISTERED CPUSET.  The arms are not
# independent measurements of independent things: T08 is the reproduction
# control for T10 and T12, and all three are compared against XT10's adjoint.
# Running them concurrently would let contention on a shared core change the
# very thing being measured -- the wall-clock at which a primal crosses its
# tolerance -- so the chain is serial by registration, not by convenience.
#
# THE RUN ROOT MUST NOT EXIST WHEN THIS STARTS.  That is asserted BY EXECUTION
# here, immediately before the first arm, and the assertion is echoed.  A run
# root that already exists could carry a `0/` or a time directory from an
# earlier attempt, which is exactly what the age guard exists to refuse.
# =============================================================================
set -u

ITEM=D19T
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D19T-a1-naca0012-shape7-primal-tightening
HERE="$(cd "$(dirname "$0")" && pwd)"
IMG=dafoam-idwarp-rot:v1
D19R_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau
ARMS="MESH T08 T10 T12 XT10"
ITEM_CEILING_CORE_MIN=18.0

STAGE="${1:-run}"

# ---- THE ABSENCE ASSERT, BY EXECUTION -------------------------------------
if [ "$STAGE" = "assert-absent" ] || [ "$STAGE" = "run" ]; then
  if [ -e "$BASE" ]; then
    echo "D19T_ROOT_PRESENT $BASE EXISTS -- the pre-registration's absence assert FAILS."
    echo "  This is a REFUSAL, not a prompt to delete it.  An existing root may carry a"
    echo "  0/ or a time directory from an earlier attempt, and rule 4's age guard exists"
    echo "  precisely because that case is not distinguishable after the fact."
    exit 3
  fi
  echo "D19T_ROOT_ABSENT_ASSERTED $BASE does not exist at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  [ "$STAGE" = "assert-absent" ] && exit 0
fi

# ---- STAGING: the case, the producer, and NOTHING from a sibling's outputs --
mkdir -p "$BASE" || { echo "ABORT mkdir $BASE"; exit 4; }
test -d "$D19R_ROOT/base" || { echo "ABORT D19R's base/ is not where the freeze says"; exit 4; }
cp -a "$D19R_ROOT/base" "$BASE/base" || { echo "ABORT base copy"; exit 4; }
cp "$D19R_ROOT/d19r_runScript.py" "$BASE/" || { echo "ABORT producer copy"; exit 4; }
GOT=$(md5sum < "$BASE/d19r_runScript.py" | cut -d' ' -f1)
test "$GOT" = "a5e18503ea29d0e37c3cf1668533cd34" || { echo "ABORT producer md5 $GOT"; exit 4; }
echo "D19T_STAGED base/ and d19r_runScript.py (md5 $GOT, D19R's producer BORROWED UNEDITED)"

# ---- the arms, in order, stopping on the first failure ---------------------
for ARM in $ARMS; do
  echo "=== D19T ARM $ARM ==="
  BASE="$BASE" bash "$HERE/d19t_run_arm.sh" "$ARM" "$IMG"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "D19T_CHAIN_STOPPED arm=$ARM rc=$rc -- the chain does NOT continue past a failed arm."
    echo "  A later arm launched on a failed predecessor would produce a number with no"
    echo "  defensible provenance.  The chain reports the stop; it does not route around it."
    exit "$rc"
  fi
  # ---- THE ITEM CEILING, CHECKED AFTER EVERY ARM -------------------------
  TOTAL=$(awk -F'core_min=' '/^ARM=/{split($2,a," ");s+=a[1]}END{printf "%.3f", s}' "$BASE/ledger.txt")
  OVER=$(python3 -c "print('YES' if $TOTAL > $ITEM_CEILING_CORE_MIN else 'NO')")
  echo "D19T_ITEM_SPEND after $ARM: $TOTAL core-min of ceiling $ITEM_CEILING_CORE_MIN (over=$OVER)"
  if [ "$OVER" = "YES" ]; then
    echo "D19T_ITEM_CEILING_EXCEEDED $TOTAL > $ITEM_CEILING_CORE_MIN -- CLAUDE.md rule 12:"
    echo "  the run STOPS and does not get a new budget."
    exit 9
  fi
done

echo "=== D19T GRADE ==="
OUT="$BASE/D19T_grade_$(date -u +%Y%m%dT%H%M%SZ).out"
python3 "$HERE/d19t_grade.py" --root "$BASE" --cpuset 5,13 \
  --digest sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35 \
  --so-md5 85f59e87253e0a71a813f64ca6e4c425 2>&1 | tee "$OUT"
echo "D19T_CHAIN_DONE grade stdout at $OUT"
