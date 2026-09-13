#!/bin/bash
# D6R3 ARM P0 -- the BLOCKING precondition of PREREGISTRATION.md (R4) section 7a.
# One primal and one gradient on the PUBLISHED 579,072-cell mesh.  It closes the
# 41,760 -> 579,072 cell SCALE GAP: the cost anchors are measured at 41,760 and this item runs at
# 579,072, a factor 13.867 across which the adjoint's cost is NOT linear and NOT measured.
# Until P0 reads PASS every later arm is PENDING and section 7c is labelled UNTESTED.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
RANKS="${1:-72}"; CPUSET="${2:-0-71}"; MEMG="${3:-256}"
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085
"$HERE/d6r3_run_arm.sh" P0 "$RANKS" "$CPUSET" "$MEMG"
RC=$?
LOG=$(ls -t "$ROOT"/P0_*.log 2>/dev/null | head -1)
echo "=== P0 GATES ==="
MI=$(grep -c "Main iteration" "$LOG" 2>/dev/null || echo 0)
KSP=$(grep -c "KSP Residual" "$LOG" 2>/dev/null || echo 0)
echo "P0-G1 rc=$RC  Main iteration=$MI  KSP Residual=$KSP"
[ "$RC" -eq 0 ] && [ "$MI" -gt 0 ] && [ "$KSP" -gt 0 ] \
  && echo "P0-G1 PASS" \
  || echo "P0-G1 NOT A RESULT -- a run that never attempted a linear solve is not a fast adjoint"
echo "P0 RECORDS (R4 s7a): peak RSS; primalMinResTolDiff; the local-DV displacement axis; \
transonicPCOption in force; baseline yPlus -- see d6r3_run_record.json and the log"
grep -m3 "yPlus" "$LOG" 2>/dev/null | tail -1
exit $RC
