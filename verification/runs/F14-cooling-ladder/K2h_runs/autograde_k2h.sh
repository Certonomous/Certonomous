#!/bin/bash
# AUTOGRADE + RENDER ON COMPLETION for K2h_L3, detached and parented to init.
#
# WHY THIS EXISTS AND IS NOT A CHECKLIST: "if a render step cannot run unattended
# it will not happen the next time nobody is awake", which is the same failure as
# an unarmed grader.  The run finishes near 04:00Z.  An agent watching it may not
# survive that long; this script does not care.
#
# IT NEVER TOUCHES THE SOLVER.  It waits for the solver pid to LEAVE the process
# table.  It sends no signal, arms no timeout and enforces no cap -- directive #17
# is explicit that no run is stopped by a time or budget cap.
#
# IT NEVER WRITES INTO THE GRADED TREE except its own clearly-named outputs
# beside the case; the renderer fingerprints both graded trees and PROVES them
# unchanged.
#
# ORDER, and it is section 10's order:
#   1. wait for the solver to exit
#   2. wait for .k2h_inner.sh to write STATUS (it captures rc INSIDE the wrapper;
#      `setsid timeout cmd` exits 0 for every outcome, so the rc that means
#      anything is the wrapper's, never setsid's) and to run reconstructPar
#   3. GRADE with the frozen path -- freeze re-verified, D-COMPLETE with the age
#      guard, rule 3's plant, D-STATIONARY, then G-DPBAR
#   4. RENDER, stamped with the verdict the comparator actually printed
#
# The render is driven by the comparator's own word.  It is NOT given a verdict
# chosen by whoever launches this, and `assert_stamp` refuses any word K2h_L3
# does not own.
set -u

REPO=/home/ubuntu/Certonomous
RUNS=$REPO/verification/runs/F14-cooling-ladder/K2h_runs
CASE=$RUNS/K2h_L3
PID=${1:?usage: autograde_k2h.sh <solver-pid>}
LOG=$RUNS/autograde.K2h_L3.out

exec >> "$LOG" 2>&1
echo "=============================================================="
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) autograde armed, watching pid $PID"

# ---- 1. wait for the solver to leave the process table ---------------------
while kill -0 "$PID" 2>/dev/null; do sleep 60; done
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) solver pid $PID has exited"

# ---- 2. let the wrapper finish reconstructPar and write STATUS -------------
# reconstructPar on 664,848 cells takes minutes, and grading before it lands
# would read the decomposed path and then the renderer would find no 112/.
for i in $(seq 1 120); do
  [ -f "$RUNS/STATUS.K2h_L3" ] && break
  sleep 30
done
if [ -f "$RUNS/STATUS.K2h_L3" ]; then
  echo "--- STATUS.K2h_L3 (rc is the WRAPPER's, not setsid's) ---"
  cat "$RUNS/STATUS.K2h_L3"
else
  echo "!! no STATUS.K2h_L3 after 60 min. GRADING ANYWAY -- the comparator"
  echo "   reports a missing rc as a D-COMPLETE failure rather than assuming one."
fi
echo "--- reconstructed times in the case root ---"
ls "$CASE" | grep -E '^[0-9]+(\.[0-9]+)?$' | sort -n | tr '\n' ' '; echo

# ---- 3. GRADE --------------------------------------------------------------
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) grading with the FROZEN path"
python3 "$RUNS/analyse_k2h.py" > "$RUNS/GRADE.K2h_L3.json" 2>"$RUNS/GRADE.K2h_L3.err"
GRC=$?
echo "comparator exit $GRC  (NO VERDICT MAY BE READ FROM AN EXIT CODE -- the"
echo "verdict is the word the comparator printed, and that word is read below)"
[ -s "$RUNS/GRADE.K2h_L3.err" ] && { echo "--- stderr ---"; cat "$RUNS/GRADE.K2h_L3.err"; }

VERDICT=$(python3 - "$RUNS/GRADE.K2h_L3.json" <<'PY'
import json, re, sys
txt = open(sys.argv[1]).read()
m = re.search(r"^\{.*?\n\}", txt, re.S)
try:
    print(json.loads(m.group(0))["verdict"])
except Exception:
    mm = re.search(r"^VERDICT: (.+)$", txt, re.M)
    print(mm.group(1).strip() if mm else "UNREADABLE")
PY
)
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERDICT: $VERDICT"
tail -6 "$RUNS/GRADE.K2h_L3.json"

# ---- 4. RENDER, stamped with the word the comparator printed ---------------
# REFUSED is not a verdict K2h_L3 owns and assert_stamp would refuse it, which is
# correct: a refusal means the grading path itself is not trustworthy, and a
# figure is not the place to discover that.
case "$VERDICT" in
  "PASS"|"GATE FAIL"|"NOT A RESULT")
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) rendering, stamped '$VERDICT'"
    xvfb-run -a /usr/bin/pvpython "$RUNS/render_k2h_l3.py" "$VERDICT"
    echo "renderer exit $?"
    ;;
  *)
    echo "NOT RENDERING. The comparator printed '$VERDICT', which is not a"
    echo "verdict this level owns. A figure carrying a word the grade record"
    echo "does not carry is worse than no figure: it travels further than the"
    echo "verdict does. Fix the grading path first."
    ;;
esac

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) autograde done"
