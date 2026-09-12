#!/bin/bash
# M6I RUNG 4 -- BOUNDED (TVD) CONVECTION FOR THE WHOLE RUN.  ONE REGISTERED CHANGE.
#
# WHY, AND IT IS EVIDENCE AND NOT ORDERING (ADDENDUM 7 section A7.1):
#   L3_NORAMP ran the REGISTERED SECOND-ORDER SCHEMES FROM ITERATION 1, no ramp, on the
#   87.66-degree grid, and completed rc=0 with ZERO clipped cells and ZERO bounded nuTilda.
#   So `linearUpwind` under `limited corrected 0.33` at 87.7 deg is NOT unstable as such.
#   L1 and L2 died in STAGE 2 only, and L3 -- the level with NO SHOCK -- never died at all.
#   THE INSTABILITY REQUIRES A SHOCK: an UNBOUNDED second-order upwind scheme overshoots
#   across a captured shock, the overshoot drives T and nuTilda negative, and
#   sutherlandTransportI.H:120's sqrt(T) then raises SIGFPE.
#
# THE ONE CHANGE: every convective term moves from the UNBOUNDED `linearUpwind` to the
# BOUNDED TVD `limitedLinear(V) 1`, which is second-order where the solution is smooth and
# degrades to first-order ONLY at the discontinuity.  `div(phid,p)` stays `Gauss upwind`,
# which it already was.  RELAXATION, MODEL, MESH, CONDITION, BUDGET, BANDS AND CAPS ARE
# UNTOUCHED, and the 200-iteration first-order ramp is left exactly as registered -- it is
# NOT extended, because ADDENDUM 6 section A6.4 bars grading a first-order solution against
# bands that measure a shock.
#
# NOT APPLIED TO L3.  L3 has two completed, graded runs under the linearUpwind schemes and
# they are the record.  If L1 or L2 completes under this rung, L3 is RE-RUN under it too so
# the family is one configuration -- registered in ADDENDUM 8, not done here.
set -u
RUNS="$(cd "$(dirname "$0")" && pwd)"
for L in "${@:-L1 L2}"; do
  C="$RUNS/$L"
  [ -f "$C/system/fvSchemes" ] || { echo "$L: no fvSchemes"; exit 1; }
  python3 - "$C/system/fvSchemes" <<'PY'
import sys
p=sys.argv[1]; s=open(p).read()
old="""divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind limitedGrad;
    div(phi,e)      bounded Gauss linearUpwind limitedGrad;
    div(phi,K)      bounded Gauss linearUpwind limitedGrad;
    div(phi,Ekp)    bounded Gauss linearUpwind limitedGrad;
    div(phi,nuTilda) bounded Gauss upwind;"""
new="""divSchemes
{
    // RUNG 4, ADDENDUM 8: every convective term moves from the UNBOUNDED second-order
    // `linearUpwind` to the BOUNDED TVD `limitedLinear(V) 1` -- second order where the
    // solution is smooth, first order ONLY at the discontinuity.  This is the one
    // registered change, and it is the remedy the evidence names rather than the one the
    // pre-declaration happened to list first: L3_NORAMP proved the schemes stable at 87.7
    // deg WITHOUT a shock, and L1/L2 died only once a shock formed.
    default         none;
    div(phi,U)      bounded Gauss limitedLinearV 1;
    div(phi,e)      bounded Gauss limitedLinear 1;
    div(phi,K)      bounded Gauss limitedLinear 1;
    div(phi,Ekp)    bounded Gauss limitedLinear 1;
    div(phi,nuTilda) bounded Gauss limitedLinear 1;"""
assert old in s, p
s=s.replace(old,new)
open(p,"w").write(s)
print("  patched",p)
PY
  grep -q 'limitedLinearV 1' "$C/system/fvSchemes" || { echo "$L: TVD substitution did not read back"; exit 1; }
  # THE ASSERT READS CODE, NOT PROSE.  The first version of this line was
  #     grep -q 'linearUpwind' "$C/system/fvSchemes"
  # and it FIRED ON THE COMMENT THIS SCRIPT ITSELF INSERTS three lines above the schemes,
  # which contains the word `linearUpwind` while explaining its removal.  An assert that
  # matches its own documentation is not an assert.  Comment lines are stripped first.
  grep -v '^\s*//' "$C/system/fvSchemes" | grep -q 'linearUpwind' && { echo "$L: an unbounded linearUpwind term SURVIVED the substitution"; exit 1; }
  # the ramp file is NOT touched -- assert it still is the first-order ramp
  grep -q 'STARTUP RAMP ONLY' "$C/system/fvSchemes.startup" || { echo "$L: ramp banner missing"; exit 1; }
  grep -q 'div(phi,U)      bounded Gauss upwind;' "$C/system/fvSchemes.startup" || { echo "$L: ramp is not first-order any more"; exit 1; }
  echo "$L: rung 4 applied; ramp asserted unchanged and still first-order"
done
echo "RUNG 4 BUILT"
