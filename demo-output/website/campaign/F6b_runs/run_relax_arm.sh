#!/bin/bash
# One arm of the F6b relaxation-invariance check (L-47).
# Pre-registration: campaign/F6b_RELAXATION_INVARIANCE_PREREGISTRATION.md (ce0b14be)
# Usage: run_relax_arm.sh <ARM> <CPU>
set -u
ARM="$1"; CPU="$2"
BASE=/home/ubuntu/Certonomous/demo-output/website/campaign/F6b_runs
CASE="$BASE/medium_relax_$ARM"
LEDGER="$BASE/relax_invariance_ledger.txt"
LOG="$BASE/log.relax_$ARM"

{
  echo "=== ARM $ARM launched $(date -u +%Y-%m-%dT%H:%M:%SZ) cpu=$CPU pid=$$"
  echo "    case      $CASE"
  echo "    relax     $(tr -d ' \n' < <(sed -n '/^relaxationFactors/,/}/p' "$CASE/system/fvSolution"))"
  echo "    endTime   $(grep -m1 '^endTime' "$CASE/system/controlDict")"
  echo "    command   taskset -c $CPU openfoam2606 -c 'cd $CASE && simpleFoam'"
} >> "$LEDGER"

START=$(date +%s)
taskset -c "$CPU" openfoam2606 -c "cd $CASE && simpleFoam" > "$LOG" 2>&1
RC=$?
END=$(date +%s)

{
  echo "=== ARM $ARM finished $(date -u +%Y-%m-%dT%H:%M:%SZ) rc=$RC wall=$((END-START))s"
  echo "    convergence sentences: $(grep -c 'SIMPLE solution converged' "$LOG")"
  grep -m1 'SIMPLE solution converged' "$LOG" | sed 's/^/    /'
  grep 'ExecutionTime' "$LOG" | tail -1 | sed 's/^/    /'
  echo "    last written time dirs: $(ls -d "$CASE"/[0-9]* 2>/dev/null | xargs -n1 basename | tr '\n' ' ')"
  echo "    -- initial residuals every 500 iterations (Time, Ux, p) --"
  awk '/^Time = /{t=$3}
       /Solving for Ux/{if (match($0,/Initial residual = [^,]*/)) ux=substr($0,RSTART+19,RLENGTH-19)}
       /Solving for p,/{if (pdone[t]!=1 && match($0,/Initial residual = [^,]*/)) {p=substr($0,RSTART+19,RLENGTH-19); pdone[t]=1}}
       /^ExecutionTime/{if (t%500==0 && t>0 && !seen[t]++) printf "    %8s  %s  %s\n", t, ux, p}' "$LOG"
  echo ""
} >> "$LEDGER"
