#!/bin/bash
# T25R6a SEQUENTIAL DRIVER -- the four cases, ONE AT A TIME, NONE CONCURRENT.
#
# WHY THIS EXISTS AND WHY THE RUNG IS ONE QUEUE ENTRY AND NOT FOUR.
# Prereg section 10 step 4 registers the runs as sequential, on T25R5 Addendum
# D1.3's protocol.  That is not tidiness: THIS WHOLE RUNG IS A TIMING
# MEASUREMENT.  Two of these cases running at once would contaminate the very
# ExecutionTime ratios that G-T6a is computed from.  Four independent queue
# entries could be picked up on the same tick, so the sequence is enforced HERE,
# in one process, rather than hoped for from the scheduler.
#
# Registered order (prereg section 10 step 4): B0_L1, C5_L1, B0_L3, C5_L3.
# The baselines run FIRST at each level so a missing baseline is discovered
# before its arm spends anything.
set -o pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ORDER=(B0_L1 C5_L1 B0_L3 C5_L3)
declare -A TO=( [B0_L1]=396 [C5_L1]=396 [B0_L3]=2970 [C5_L3]=2970 )

echo "=== T25R6a SEQUENTIAL DRIVER -- registered order, none concurrent ==="
date -u +"start %Y-%m-%dT%H:%M:%SZ"

for RUN in "${ORDER[@]}"; do
  CASE="$HERE/$RUN"
  echo ""
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) launching $RUN (alone, timeout ${TO[$RUN]}s) ==="
  bash "$HERE/run_one_t25R6a.sh" --case-dir "$CASE" --timeout "${TO[$RUN]}" --ranks 2
  RC=$?
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) $RUN finished rc=$RC ==="
  # A cap stop (124) is a BOUND, not a disqualification (prereg 7.3): the
  # sequence CONTINUES so the remaining levels are still measured, and the
  # grader resolves the censoring.  A REFUSAL (80-96) is different: it means the
  # case was never eligible to run, and continuing would spend core-minutes on a
  # sequence whose premise already failed.
  if [ "$RC" -ne 0 ] && [ "$RC" -ne 124 ]; then
    echo "STOP: $RUN returned rc=$RC -- a launcher REFUSAL, not a cap stop."
    echo "      The remaining cases are NOT launched.  prereg 6.6: a third"
    echo "      attempt at something that has failed twice ESCALATES rather"
    echo "      than reruns."
    date -u +"end %Y-%m-%dT%H:%M:%SZ"
    exit "$RC"
  fi
done

echo ""
echo "=== SEQUENTIAL RUN COMPLETE -- completion markers ==="
python3 "$HERE/mark_done_t25R6a.py" --all
echo ""
echo "NOT GRADED HERE.  Grading is a separate, deliberate step:"
echo "  python3 $HERE/grade_t25R6a.py --grade"
date -u +"end %Y-%m-%dT%H:%M:%SZ"
