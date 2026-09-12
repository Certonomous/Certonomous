#!/usr/bin/env bash
# D6R2 VERDICT BOUNDS -- the two charter limbs, printed in the SAME BLOCK the
# reader sees the number in.
#
# WHY THIS IS A SEPARATE FILE.  The grading path d6r2_grade.py is committed
# (c818f6524840a756be8bee941b66efb526222391) and a grading path is not moved
# after compute.  Nothing here touches it.  This appends to the autograde
# output AFTER that output is closed, and writes the same text to a sidecar
# beside D6R2_grade.json.
#
# WHY IT EXISTS AT ALL.  A caveat that lives only in the pre-registration is
# how the caveat gets lost: the number travels and the qualifier does not.
# dafoam-supervisor's ruling, 2026-09-12.
#
# It waits, it writes, it kills nothing.
B=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2-a2-wing-multipoint-transonic
AG="$B/D6R2_AUTOGRADE.out"
SIDE="$B/D6R2_VERDICT_BOUNDS.txt"

write_bounds() {
  cat <<'TXT'

================ D6R2 VERDICT BOUNDS -- READ THESE WITH THE NUMBER ================
GRADIENT UNVERIFIED -- the F_mp/FD family closed rc=1 on this case; the charter
requires an FD table beside every adjoint and there is none.
PATCHED ROW ONLY -- no shipped row, so this is not a verdict about DAFoam
(charter two-row rule).

WHAT THIS RUN MAY THEREFORE CLAIM, and nothing wider:
  - that the optimiser terminated itself at its registered budget of 25 majors;
  - that the composite multipoint objective J fell by the measured fraction printed
    above, against the frozen band Jf <= 0.90 x J0;
  - that the three lift constraints held at the final design within 1.0e-3.
  Those are statements about THIS OPTIMISER ON THIS PATCHED BUILD.

WHAT IT MAY NOT CLAIM, and both are foreclosed by measurement, not by caution:
  - that DAFoam's adjoint gradient is correct -- foreclosed by the FAILED FD family
    (D6RF3 F_mp, rc=1, /home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd);
  - that the design is genuinely optimal, or anything that is a verdict ABOUT DAFoam
    -- foreclosed by the missing shipped row.

Ruling: dafoam-supervisor, 2026-09-12, [lab-attributed]. Rule-2 departure on the
grading path (comparator not in the freeze) disclosed by the supervisor at bc3aa7ce2.
===================================================================================
TXT
}

# wait for the comparator to close its own block, then append into it
for i in $(seq 1 17280); do
  if [ -f "$AG" ] && grep -q 'D6R2_AUTOGRADE_END' "$AG" 2>/dev/null; then
    write_bounds >> "$AG"
    write_bounds > "$SIDE"
    echo "D6R2_BOUNDS_WRITTEN $(date -u +%Y-%m-%dT%H:%M:%SZ) into $AG and $SIDE" >> "$AG"
    exit 0
  fi
  sleep 10
done
write_bounds > "$SIDE"
echo "D6R2_BOUNDS_SIDECAR_ONLY autograde block never closed within 48 h" >> "$SIDE"
