#!/bin/bash
# autograde_k2g.sh -- K2g L3 autograder.  Runs INSIDE the detached session that
# `resume_k2g.sh` created with setsid, immediately after the solver's own rc has
# been captured, so it is parented to init and survives the fleet, a supervisor
# ending and an ssh close (Sanaa's 2026-09-12 directive items 9 and 11).
#
# IT GRADES NOTHING ITSELF.  It runs the FROZEN instruments in the FROZEN order
# registered at K2g_PREREGISTRATION.md section 9, and prints what they print.
#
#   1. rule 4, all six clauses         -- mark_done_k2f.py   (frozen, unedited)
#   2. the cross-check the resume EARNED -- the dp_tile/dp_return function-object
#      value of DP_module at endTime against the frozen reader's value on the
#      same fields.  The function objects are a MONITOR channel and never a
#      grading input; this check is what makes them an INDEPENDENT CONTROL on
#      the reader instead of a second path to the same number.
#   3. the gate                        -- analyse_k2g.py --grade (frozen)
#
# EXIT MAP: whatever the comparator returns.  0 OK, 1 GATE FAIL, 2 REFUSE,
# 3 NOT A RESULT.  NO VERDICT MAY BE READ FROM AN EXIT CODE: the verdict is the
# word the comparator prints.
set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO=/home/ubuntu/Certonomous
K2F="$REPO/verification/runs/F14-cooling-ladder/K2f_runs"
CASE="$HERE/K2f_L3"

echo "=== autograde_k2g $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

echo "--- 1. rule 4, six clauses, on the frozen instrument ---"
python3 "$K2F/mark_done_k2f.py" "$CASE"; MD=$?
echo "mark_done_k2f rc=$MD"

echo "--- 2. CONTROL: function-object DP_module vs the frozen reader at endTime ---"
CASE="$CASE" HERE="$HERE" python3 - <<'PYX'
import os, sys
sys.path.insert(0, os.environ["HERE"])
case = os.environ["CASE"]
import foam_patch_reader as FR
try:
    hi, _ = FR.area_average(case, 2000, "p_rgh", "tile")
    lo, _ = FR.area_average(case, 2000, "p_rgh", "return")
except Exception as exc:                       # noqa: BLE001
    print("  reader could not read endTime: %s" % exc); sys.exit(0)
reader = hi - lo
def fo(name):
    root = os.path.join(case, "postProcessing", name)
    if not os.path.isdir(root):
        return None
    for sub in sorted(os.listdir(root)):
        f = os.path.join(root, sub, "surfaceFieldValue.dat")
        if os.path.exists(f):
            for line in open(f, errors="replace"):
                if line.startswith("#"):
                    continue
                p = line.split()
                if len(p) >= 2 and int(float(p[0])) == 2000:
                    return float(p[1])
    return None
a, b = fo("dp_tile"), fo("dp_return")
print("  frozen reader DP_module = %.12g m2/s2" % reader)
if a is None or b is None:
    print("  function-object value ABSENT -- the control could not be run, and an "
          "unrun control is reported as unrun, never as a pass")
else:
    print("  function object  DP_module = %.12g m2/s2" % (a - b))
    d = abs(reader - (a - b))
    print("  |difference| = %.3g  -- %s" % (d, "AGREE" if d < 1e-6 else
          "DISAGREE: TWO INDEPENDENT READERS OF THE SAME FIELD DO NOT AGREE. "
          "This is a finding about the reader and must be triaged before the "
          "gate value is believed."))
PYX

echo "--- 3. the gate, on the frozen comparator ---"
cd "$HERE"
python3 "$HERE/analyse_k2g.py" --grade --json "$HERE/K2g_GATE.json"; AG=$?
echo "analyse_k2g rc=$AG  (0 OK, 1 GATE FAIL, 2 REFUSE, 3 NOT A RESULT --"
echo " the VERDICT is the word printed above, never this number)"
exit $AG
