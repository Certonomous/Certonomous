#!/bin/bash
# SUBOFF A1b -- FIRE THE PRE-REGISTERED GRADER WHEN A LEVEL LANDS, WITH NO AGENT ALIVE.
#
# WHY IT EXISTS.  SOLVE_L1 needs ~32 h more at the measured rate and SOLVE_L2 is still
# behind its memory gate.  No lane and no supervisor will be alive when either lands.
# X4 of the pre-registration says the solver is setsid-detached with rc captured INSIDE
# the wrapper; the SAME argument applies to the grading, because a run that completes and
# is never graded produces no record -- the same loss by another route as an ungraded
# crash.
#
# 🔴 IT GRADES NOTHING.  It contains no gate, no threshold, no branch on any measured
# value.  It invokes GRADER_PINNED_<commit>.py -- a byte-for-byte copy of
# grade_suboff_a1.py as committed at the A1b pre-registration commit -- with the
# parameters fixed in the registration (endTime 3000, ranks 4, CT_REFERENCE.json).
# Adding a gate here would be choosing a gate after the answer; that is what rule 2 exists
# to stop.
#
# IT NEVER KILLS AND IT HAS NO CLOCK OR SPEND TRIGGER.  Sanaa has ruled three times that
# no run stops on budget or time.  The ONLY thing this wrapper waits on is the appearance
# of <case>/solve_rc, which solve_level.sh writes on every exit path including its
# refusals -- so a level that is BLOCKED on memory is RECORDED rather than left silent.
#
# IT WRITES NOTHING INTO THE CASE IT GRADES.  Output and scratch are siblings of the case
# directory, so the rule-4 age guard cannot be disturbed by the act of grading.
#
# rc IS CAPTURED INSIDE THIS WRAPPER.  `setsid timeout cmd` exits 0 for every outcome, so
# an rc captured around the setsid line is always a lie.
set -u
CASE="$1"; LEVEL="$2"; GRADER="$3"; EXPECT_SHA="$4"
ROOT=$(dirname "$CASE")
LOG="$ROOT/AUTOGRADE_$LEVEL.log"
OUT="$ROOT/GRADE_$LEVEL.json"
SCRATCH="$ROOT/GRADE_SCRATCH_$LEVEL"
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOG"; }
say "AUTOGRADE ARMED case=$CASE level=$LEVEL grader=$GRADER (NEVER KILLS; waits ONLY on solve_rc)"

N=0
while [ ! -f "$CASE/solve_rc" ]; do
  N=$((N+1))
  [ $((N % 60)) -eq 1 ] && say "WAITING solve_rc absent (reading $N). Not a cap; just waiting."
  sleep 60
done
RC=$(cat "$CASE/solve_rc")
say "SOLVE_RC APPEARED rc=$RC after $N readings."

# Rule 2: the file that grades must BE the file committed before the solver started.
GOT=$(sha256sum "$GRADER" | cut -d' ' -f1)
if [ "$GOT" != "$EXPECT_SHA" ]; then
  say "REFUSED: pinned grader sha256 $GOT != armed $EXPECT_SHA. THE GRADING PATH MOVED. Not grading with a changed instrument; this is a FINDING for the cfd-supervisor."
  echo "2" > "$ROOT/autograde_rc_$LEVEL"; exit 2
fi
say "GRADER SHA VERIFIED against the pre-registration commit blob."

mkdir -p "$SCRATCH"
python3 "$GRADER" \
  --case "$CASE" --level "$LEVEL" --end-time 3000 --ranks 4 \
  --ct-reference "$ROOT/CT_REFERENCE.json" \
  --scratch "$SCRATCH" --out "$OUT" >> "$LOG" 2>&1
GRC=$?
echo "$GRC" > "$ROOT/autograde_rc_$LEVEL"
say "GRADER EXIT rc=$GRC  report=$OUT"
if [ "$GRC" -eq 2 ]; then
  say "GRADER REFUSED (exit 2). Under rule 3 that is a PLANTED-CONTROL REFUSAL: the reader could not see its own plant, so no zero it reports would be evidence. NOT A RESULT."
fi
exit 0
