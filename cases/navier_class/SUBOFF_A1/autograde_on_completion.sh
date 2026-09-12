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

# rc=80 IS NOT A COMPLETION AND MUST NOT BE GRADED AS ONE.  It is solve_level.sh's
# memory refusal, and since 2026-09-12 the L2 launcher RE-ARMS on it and archives the
# attempt -- so an rc=80 seen here is TRANSIENT BY CONSTRUCTION and grading it would
# burn this one-shot grader on an attempt that is about to be retried.  The terminal
# case is the launcher's RETRIES_EXHAUSTED marker, which IS graded, so an L2 that never
# starts still ends as a recorded BLOCKED rather than as silence.
EXHAUSTED="$ROOT/SOLVE_L2_RETRIES_EXHAUSTED.txt"
N=0; NBLOCKED=0
while true; do
  if [ -f "$CASE/solve_rc" ]; then
    RC=$(cat "$CASE/solve_rc")
    if [ "$RC" != "80" ]; then break; fi
    NBLOCKED=$((NBLOCKED+1))
    [ $((NBLOCKED % 10)) -eq 1 ] && say "SAW solve_rc=80 (memory refusal, sighting $NBLOCKED). NOT grading: the launcher re-arms on this and archives the attempt. Continuing to wait."
  fi
  if [ -f "$EXHAUSTED" ]; then
    say "RETRIES EXHAUSTED marker present -- the BLOCKED is now TERMINAL and IS graded."
    RC=80; break
  fi
  N=$((N+1))
  [ $((N % 60)) -eq 1 ] && say "WAITING solve_rc absent (reading $N). Not a cap; just waiting."
  sleep 60
done
say "PROCEEDING TO GRADE rc=$RC after $N readings ($NBLOCKED memory refusals seen and skipped)."

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
