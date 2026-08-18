#!/usr/bin/env bash
# run_controls.sh -- the four controls for rung K0. Run AFTER run_cases.sh.
#
# Each control is a claim this rung would otherwise be making on trust. Every
# one of them prints its ANCHOR READBACK before its measurement, because a plant
# keyed on something that is not there is a silent no-op and reads exactly like
# a pass.
#
#   C1  the g=0 twin's max|U| == 0 is a ZERO. Zeros need a positive readback
#       from the same extractor first, or a broken extractor passes as physics.
#   C2  the auditor vs a closed-form 1-D conduction answer.
#   C3  the auditor on unconverged snapshots (does it move at all?).
#   C3b the auditor against a PLANTED volumetric source of known power --
#       the positive control for its failure-detection path.
#   C4  the auditor's property path: halve Pr, every watt must exactly double.
#
# Exit codes of the auditor are read directly, never through a pipe: piping into
# head/tail/grep reports the PIPE's status, not the check's.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
# NOT `$HERE/../../../..`, and this is a defect class rather than a typo:
# a repository root reached by COUNTING `..` up from a path under a MOVING
# tree points somewhere else the moment the tree moves.  MOVE_MAP batch 7
# (R20) made this file one segment shallower, so four `..` reached
# `/home/ubuntu` instead of the repository.  There is no path literal here,
# so no prefix rewrite and no grep for `demo-output` reaches it.  Derived by
# SEARCHING for the marker instead, and it EXITS rather than carrying on
# with a root that is not there.
REPO="$HERE"
while [ "$REPO" != "/" ] && [ ! -f "$REPO/scripts/lab_paths.py" ]; do
    REPO="$(dirname "$REPO")"
done
if [ ! -f "$REPO/scripts/lab_paths.py" ]; then
    printf '%s\n' "cannot locate scripts/lab_paths.py above $HERE" >&2
    exit 2
fi
HB="$REPO/scripts/heat_balance.py"
AUD="$HERE/audit"
SCRATCH="${SCRATCH_DIR:-/tmp/thermal_k0_controls}"
mkdir -p "$AUD" "$SCRATCH"

fail=0
say() { printf '%s\n' "$*"; }
rule() { printf '%s\n' "----------------------------------------------------------------------"; }

# --------------------------------------------------------------------------
say "######## HEADLINE AUDITS (the two rungs themselves) ########"
for c in K0a_heated_box K0b_cavity_Ra1e5; do
    j="$AUD/$([ "$c" = K0a_heated_box ] && echo K0a_gon || echo K0b_gon).json"
    python3 "$HB" "$HERE/$c" --length 0.1 --tol 0.5 --json "$j" > "$AUD/$c.report.txt" 2>&1
    rc=$?
    say "  $c  auditor rc = $rc  -> $j"
    [ "$rc" -eq 0 ] || fail=1
    sed -n '/IMBALANCE/p;/Ra = /p;/BOUSSINESQ/p' "$AUD/$c.report.txt" | sed 's/^/    /'
done
rule

# --------------------------------------------------------------------------
say "######## C1  buoyancy is the sole driver of motion ########"
say "STEP 1 -- POSITIVE READBACK. Same extractor, g-ON case, run BEFORE the zero."
out=$(python3 "$HB" "$HERE/K0a_heated_box" --length 0.1 --tol 2.0 --quiet \
        --json "$AUD/K0a_gon.json"); rc=$?
say "  auditor rc = $rc"
UON=$(python3 -c "import json;print(json.load(open('$AUD/K0a_gon.json'))['U_max_magnitude_ms'])")
say "  READBACK: max|U| on the g-ON case = $UON m/s"
python3 -c "import sys;sys.exit(0 if float('$UON')>0.01 else 1)" || {
    say "  READBACK FAILED: extractor returned a small number on a case that must move."
    say "  C1 is VOID, not passed. Any zero measured below would be meaningless."
    fail=1; }

say "STEP 2 -- the zero. g=0 twin."
grep -n '^value' "$HERE/K0a_heated_box_g0/constant/g" | sed 's/^/  plant readback: /'
out=$(python3 "$HB" "$HERE/K0a_heated_box_g0" --length 0.1 --tol 2.0 --quiet \
        --json "$AUD/K0a_g0.json"); rc=$?
UOFF=$(python3 -c "import json;print(json.load(open('$AUD/K0a_g0.json'))['U_max_magnitude_ms'])")
say "  max|U| on the g=0 twin = $UOFF m/s   (auditor rc = $rc)"
rule

# --------------------------------------------------------------------------
say "######## C2  auditor vs CLOSED-FORM conduction ########"
out=$(python3 "$HB" "$HERE/K0b_cavity_g0" --length 0.1 --tol 0.5 \
        --selftest-conduction 1.093066 --json "$AUD/K0b_g0_calibration.json"); rc=$?
printf '%s\n' "$out" | sed -n '/CALIBRATION/,$p' | sed 's/^/  /'
say "  auditor rc = $rc"
[ "$rc" -eq 0 ] || fail=1
rule

# --------------------------------------------------------------------------
say "######## C3  auditor on UNCONVERGED snapshots ########"
for t in 10 20 50 100 500; do
    [ -d "$HERE/K0b_cavity_Ra1e5/$t" ] || { say "  t=$t  (no snapshot)"; continue; }
    python3 "$HB" "$HERE/K0b_cavity_Ra1e5" --time "$t" --length 0.1 --tol 0.5 \
        --quiet --json "$AUD/K0b_t$t.json" >/dev/null 2>&1; rc=$?
    python3 -c "
import json; d=json.load(open('$AUD/K0b_t$t.json'))
print(f\"  t=$t\t imbalance={d['imbalance_pct']:.4f}%\t Qin={d['Q_in_W']:.6e} W\t rc=$rc\")"
done
rule

# --------------------------------------------------------------------------
say "######## C3b  PLANTED volumetric source, known power ########"
PLANT="$HERE/K0a_heated_box_source"
say "  ANCHOR READBACK 1 -- plant file present and names a source on T:"
if [ -f "$PLANT/constant/fvOptions" ]; then
    grep -nE 'scalarSemiImplicitSource|^\s+T\s+\(' "$PLANT/constant/fvOptions" | sed 's/^/    /'
else
    say "    ABSENT. The plant did not land. C3b is VOID."; fail=1
fi
say "  ANCHOR READBACK 2 -- the SOLVER actually read it (not just the file existing):"
if grep -qE 'Source: plantedHeatSource' "$PLANT/log.buoyantBoussinesqSimpleFoam"; then
    grep -nE 'Creating finite-volume options|Source: plantedHeatSource' \
        "$PLANT/log.buoyantBoussinesqSimpleFoam" | sed 's/^/    /'
else
    say "    the solver log does not mention the source. Plant was a NO-OP. C3b VOID."; fail=1
fi
say "  ANCHOR READBACK 3 -- the unplanted base case must show none of it:"
n=$(grep -cE 'plantedHeatSource' "$HERE/K0a_heated_box/log.buoyantBoussinesqSimpleFoam")
say "    occurrences in base case log: $n  (must be 0)"
[ "$n" -eq 0 ] || { say "    contrast broken. C3b VOID."; fail=1; }

out=$(python3 "$HB" "$PLANT" --length 0.1 --tol 2.0 --quiet \
        --json "$AUD/K0a_planted_source.json"); rc=$?
say "  auditor rc = $rc   (MUST be 1: a failing balance must be reported as failing)"
[ "$rc" -eq 1 ] || { say "  the auditor did NOT flag a case with 5 mW of unaccounted power."; fail=1; }
python3 -c "
import json; d=json.load(open('$AUD/K0a_planted_source.json')); P=5.0e-3
net=d['Q_net_W']
print(f\"  planted P                = {P:.9e} W\")
print(f\"  net boundary flux sum    = {net:.9e} W   (prediction: -P)\")
print(f\"  recovery error vs plant  = {100*(abs(net)-P)/P:+.4f} %\")
print(f\"  imbalance reported       = {d['imbalance_pct']:.4f} %\")"
rule

# --------------------------------------------------------------------------
say "######## C4  auditor PROPERTY path: halve Pr, every watt must double ########"
BASE="$HERE/K0b_cavity_Ra1e5"
MUT="$SCRATCH/K0b_Pr_halved"
rm -rf "$MUT"; mkdir -p "$MUT"
cp -r "$BASE/constant" "$BASE/system" "$MUT/"
LAST=$(ls -d "$BASE"/[0-9]* 2>/dev/null | sed 's#.*/##' | sort -g | tail -1)
cp -r "$BASE/$LAST" "$MUT/$LAST"
say "  mutant built from $BASE at time $LAST"

PRBASE=$(python3 -c "
import re;print(re.search(r'^\s*Pr\s+([^;]+);',open('$BASE/constant/transportProperties').read(),re.M).group(1))" 2>/dev/null)
if [ -z "${PRBASE:-}" ]; then
    say "  ANCHOR ABSENT: no 'Pr' keyword in the base transportProperties."
    say "  Halving a keyword that is not there is a silent no-op. C4 VOID."
    fail=1
else
    say "  ANCHOR READBACK 1 -- 'Pr' keyword present in base, value = $PRBASE"
    python3 - <<PY
import re
p="$MUT/constant/transportProperties"
t=open(p).read()
m=re.search(r'^(\s*Pr\s+)([^;]+);',t,re.M)
assert m, "anchor vanished in the copy"
new=float(m.group(2))/2.0
open(p,'w').write(t[:m.start()]+m.group(1)+repr(new)+";"+t[m.end():])
print(f"  mutation applied: Pr {m.group(2)} -> {new!r}")
PY
    say "  ANCHOR READBACK 2 -- the mutant file must DIFFER from the base:"
    if diff -q "$BASE/constant/transportProperties" "$MUT/constant/transportProperties" >/dev/null; then
        say "    files are IDENTICAL. The mutation did not land. C4 VOID."; fail=1
    else
        diff "$BASE/constant/transportProperties" "$MUT/constant/transportProperties" | sed 's/^/    /'
    fi
    python3 "$HB" "$MUT" --length 0.1 --tol 0.5 --quiet \
        --json "$AUD/K0b_Pr_halved.json" >/dev/null 2>&1; rc=$?
    if [ ! -f "$AUD/K0b_gon.json" ] || [ ! -f "$AUD/K0b_Pr_halved.json" ]; then
        say "  C4 VOID: an audit produced no JSON (base rc or mutant rc = $rc)."
        say "  This is NOT evidence about Pr -- it is a missing input."
        fail=1
    else
    python3 -c "
import json
b=json.load(open('$AUD/K0b_gon.json')); m=json.load(open('$AUD/K0b_Pr_halved.json'))
qb=[p for p in b['patches'] if p['patch']=='hotWall'][0]['Q_in_W']
qm=[p for p in m['patches'] if p['patch']=='hotWall'][0]['Q_in_W']
r=qm/qb
print(f'  Q_hotWall base   = {qb:.9e} W')
print(f'  Q_hotWall mutant = {qm:.9e} W')
print(f'  ratio            = {r:.6f}   (prediction: 2.000000)')
print(f'  error            = {100*(r-2.0)/2.0:+.5f} %')
import sys; sys.exit(0 if abs(r-2.0)/2.0 < 1e-3 else 1)"
    [ $? -eq 0 ] || { say "  C4 FAILED: watts did not double. The auditor is not reading Pr from the case."; fail=1; }
    fi
fi
rule

if [ "$fail" -eq 0 ]; then
    say "ALL CONTROLS BEHAVED AS REQUIRED (see THERMAL_K0_RESULTS.md for which"
    say "PREDICTIONS they matched -- behaving correctly and matching the predicted"
    say "number are different things and C3 did not match its prediction)."
else
    say "ONE OR MORE CONTROLS VOID OR FAILED -- see above."
fi
exit $fail
