#!/usr/bin/env bash
# T25RF -- build ONE arm of the UNGATED numerics feasibility probe.
#
# Registered at docs/campaigns/T-family/T25RF_FEASIBILITY_NOTE.md, committed
# BEFORE any T25RF compute.  THIS RUNG HAS NO GATE AND PRODUCES NO VERDICT.
#
# The mesh is COPIED from the already-built, already-checked T25R_L1 case.
# build_t25R.py IS NOT RUN: it is modified-unstaged versus its committed blob
# and is under a live rule-6 referral.  This script never writes into
# T25R_L1, T25R_L2 or T25R_L2_DT025 -- they are evidence of the 04:09Z
# divergence and are read-only here.
#
# Usage: build_arm_t25RF.sh <ARM>      ARM in A0 A1 A2 A3

set -u
ARM="${1:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$(cd "$HERE/../T25R_MODULE_runs/T25R_L1" && pwd)"
D="$HERE/$ARM"

case "$ARM" in A0|A1|A2|A3) ;; *) echo "ABORT: arm must be A0|A1|A2|A3"; exit 1;; esac
[ -d "$SRC/constant/coolant/polyMesh" ] || { echo "ABORT: no source mesh"; exit 1; }
[ -d "$D" ] && { echo "ABORT: $D already exists -- an arm is built once"; exit 1; }

mkdir -p "$D" || { echo "ABORT: mkdir"; exit 1; }

# --- inputs only.  No time dirs, no logs, no postProcessing from the source. --
cp -a "$SRC/constant" "$D/constant" || { echo "ABORT: copy constant"; exit 1; }
cp -a "$SRC/system"   "$D/system"   || { echo "ABORT: copy system";   exit 1; }
cp -a "$SRC/0.orig"   "$D/0.orig"   || { echo "ABORT: copy 0.orig";   exit 1; }
[ -e "$D/0" ] && { echo "ABORT: a 0 dir was copied -- refusing"; exit 1; }

# --- endTime 30 s at deltaT 0.5 = 60 steps (note section 2). -----------------
sed -i 's/^endTime         900;/endTime         30;/' "$D/system/controlDict" \
  || { echo "ABORT: endTime edit"; exit 1; }
grep -q '^endTime         30;' "$D/system/controlDict" \
  || { echo "ABORT: endTime edit did not take"; exit 1; }

# --- SANAA'S 2026-09-01 04:20Z VOLUMETRIC LOADS (note section 2). ------------
# 1.0e5 W/m3 for 0 <= t < 60 s ; 2.5e4 W/m3 for t >= 60 s.
# NOT T25R_L1's frozen 70000/2800 -- probing those would prove the wrong thing.
python3 - "$D/constant/module/fvOptions" <<'PY' || { echo "ABORT: fvOptions edit"; exit 1; }
import re, sys
p = sys.argv[1]
s = open(p).read()
old = """            (
                (  0.000  70000.000000)
                ( 59.999  70000.000000)
                ( 60.000  2800.000000)
                (900.000  2800.000000)
            );"""
new = """            (
                (  0.000  100000.000000)
                ( 59.999  100000.000000)
                ( 60.000   25000.000000)
                (900.000   25000.000000)
            );"""
assert old in s, "source table not found verbatim -- refusing to guess"
s = s.replace(old, new)
banner = """// *** T25RF PROBE -- LOADS REPLACED, DELIBERATELY AND ON THE RECORD. ***
// Sanaa's 2026-09-01 04:20Z volumetric loads, per
// docs/campaigns/T-family/T25RF_FEASIBILITY_NOTE.md section 2:
//   0 <= t < 60 s : 1.0e5 W/m3   (takeoff)
//   t >= 60 s     : 2.5e4 W/m3   (cruise)
// The comment block below is INHERITED FROM T25R_L1 AND ITS ARITHMETIC IS
// STALE -- it describes the 70000/2800 basis this file no longer carries.
// It is left in place unedited rather than rewritten, so that the provenance
// of this copy is legible.  THE TABLE, NOT THE COMMENT, IS WHAT RUNS.
// This probe's endTime is 30 s, so it sits entirely in the takeoff branch.
"""
s = s.replace("// THE TAKEOFF PULSE", banner + "\n// THE TAKEOFF PULSE", 1)
open(p, "w").write(s)
print("fvOptions: loads set to 1.0e5 / 2.5e4 W/m3")
PY
grep -q "100000.000000" "$D/constant/module/fvOptions" \
  || { echo "ABORT: load edit did not take"; exit 1; }
# The stale 70000/2800 arithmetic survives ON PURPOSE in the inherited comment
# block (see the banner).  Only the TABLE matters, so only the TABLE is checked:
# a `grep 70000` over the whole file matches the comment and is a false alarm.
sed -n '/explicit    table/,/);/p' "$D/constant/module/fvOptions" \
  | grep -qE '(70000|2800\.)' \
  && { echo "ABORT: an old load survived in the TABLE ITSELF"; exit 1; }
sed -n '/explicit    table/,/);/p' "$D/constant/module/fvOptions" \
  | grep -q "25000.000000" \
  || { echo "ABORT: the cruise load is not in the table"; exit 1; }

# --- ARM NUMERICS -----------------------------------------------------------
COOL="$D/system/coolant/fvSolution"
TOP="$D/system/fvSolution"

case "$ARM" in
A0)
  # As registered.  Relaxation on outer sweeps 1-4 only (UFinal/hFinal have no
  # entry and OpenFOAM keyword regexes match in FULL), nOuterCorrectors 5.
  # Nothing is changed.  This arm asks only whether the 04:09Z crash reproduces
  # under the NEW loads.
  ;;
A1|A2)
  # FINAL-SWEEP RELAXATION.  fvMatrix::relax() resolves its key through
  # GeometricField::select(bool) which appends "Final" on the last outer sweep
  # (fvMatrix.C:1249, GeometricField.C:1179), and "(U|h|k|omega)" does not
  # match UFinal.  The Final keys are therefore written EXPLICITLY.
  python3 - "$COOL" <<'PY' || { echo "ABORT: relaxation edit"; exit 1; }
import sys
p = sys.argv[1]
s = open(p).read()
start = s.index("relaxationFactors")
end = s.index("// ****", start)
new = """relaxationFactors
{
    // T25RF PROBE ARM.  The FINAL outer sweep is relaxed TOO, which is the
    // one thing T25R_L1 did not do.  fvMatrix::relax() looks up "UFinal" and
    // "hFinal" on sweep nOuterCorrectors-1 and T25R_L1's dict had no such
    // keys, so momentum and energy ran UNRELAXED on that sweep at Co ~ 1600.
    // OpenFOAM keyword regexes match in FULL: "(U|h|k|omega)" does NOT match
    // "UFinal".  Every Final key is therefore written out explicitly.
    //
    // CONSEQUENCE, STATED RATHER THAN HIDDEN: with the final sweep relaxed,
    // the last-sweep initial residual is no longer the unrelaxed convergence
    // measure T25R section 3.5 relied on.  Any registration adopting these
    // numerics owes a replacement measure.
    fields
    {
        p_rgh       0.3;
        p_rghFinal  0.3;
    }
    equations
    {
        U           0.7;
        UFinal      0.7;
        h           0.7;
        hFinal      0.7;
        k           0.7;
        kFinal      0.7;
        omega       0.7;
        omegaFinal  0.7;
    }
}

"""
open(p, "w").write(s[:start] + new + s[end:])
print("coolant fvSolution: final-sweep relaxation written")
PY
  grep -q "UFinal      0.7;" "$COOL" || { echo "ABORT: UFinal missing"; exit 1; }
  grep -q "p_rghFinal  0.3;" "$COOL" || { echo "ABORT: p_rghFinal missing"; exit 1; }
  ;;
A3)
  # DEPARTURE ARM.  frozenFlow was DECLINED BY NAME at T25R section 3.3.  It is
  # tried here only because A1 and A2 did not hold, and if it is the only thing
  # that runs that is a finding to be DISCLOSED, never adopted quietly.
  python3 - "$COOL" <<'PY' || { echo "ABORT: frozenFlow edit"; exit 1; }
import sys
p = sys.argv[1]
s = open(p).read()
assert "frozenFlow IS AVAILABLE" in s
s = s.replace("""PIMPLE
{
    momentumPredictor true;""", """PIMPLE
{
    // *** T25RF ARM A3 -- DEPARTURE. ***  T25R section 3.3 DECLINED frozenFlow
    // by name as a stronger approximation than its quasi-steady framing.  It is
    // switched on here ONLY because arms A1 and A2 did not hold, and reaching
    // it is itself the finding.
    frozenFlow      true;
    momentumPredictor true;""", 1)
open(p, "w").write(s)
print("coolant fvSolution: frozenFlow true (DEPARTURE)")
PY
  grep -q "frozenFlow      true;" "$COOL" || { echo "ABORT: frozenFlow missing"; exit 1; }
  ;;
esac

if [ "$ARM" = "A2" ]; then
  sed -i 's/^    nOuterCorrectors 5;/    nOuterCorrectors 10;/' "$TOP" \
    || { echo "ABORT: nOuterCorrectors edit"; exit 1; }
  grep -q "nOuterCorrectors 10;" "$TOP" \
    || { echo "ABORT: nOuterCorrectors edit did not take"; exit 1; }
fi

echo "BUILT $ARM at $D"
echo "  endTime      : $(grep -m1 '^endTime' "$D/system/controlDict")"
echo "  load table   : $(grep -c '100000.000000' "$D/constant/module/fvOptions") rows at 1.0e5 W/m3"
echo "  nOuterCorr   : $(grep -m1 -E '^    nOuterCorrectors' "$TOP")"
echo "  relaxation   : $(sed -n '/^relaxationFactors/,/^}/p' "$COOL" \
                        | grep -cE '(UFinal|hFinal|p_rghFinal)') Final relaxation keys"
echo "  frozenFlow   : $(grep -c 'frozenFlow      true;' "$COOL")"
