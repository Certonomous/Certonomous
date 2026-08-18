#!/bin/bash
# The grid's own design regime, queued last. Everything else here is
# incompressible at 68 m/s -- the right control against the HLPW6 divergence,
# but not the condition DPW5's boundary layer was built for. These two runs put
# the same two grids at A6's measured freestream (M = 0.850, 295 m/s, 300 K,
# alpha 2.11) so the verdict does not rest on one flow regime, and so the
# committee grid meets this lab's own converged CRM result at the condition
# that result was obtained at.
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
cd "$R" || exit 1
while pgrep -f "bash batch6.sh|bash batch7.sh|bash batch8.sh|bash batch9.sh" > /dev/null; do sleep 20; done
for G in hex hybrid; do
  bash "$R/run_case.sh" $G base compressible 2.11 120 14 >> "$R/logs/batch10.txt" 2>&1
  echo "-- done $G compressible $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch10.txt"
done
echo "BATCH10 COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$R/logs/batch10.txt"
