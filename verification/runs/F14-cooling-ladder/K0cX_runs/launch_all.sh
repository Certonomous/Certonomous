#!/bin/bash
# launch_all.sh -- run every K0cX case, in two waves, and wait on MARKERS.
#
# THE MARKER IS THE CONTRACT.  This script waits on `wait` for its own children
# and then asserts one DONE.<case> per case; the caller polls ALL_DONE.  It never
# consults the process table: other lanes share this box, and a solver's process
# NAME is truncated to 15 characters by the kernel so `buoyantBoussinesqSimpleFoam`
# never matches `pgrep -x`.
#
# TWO WAVES, and the reason is cost accounting rather than tidiness.  The box has
# 16 cores.  Running all 22 at once oversubscribes it, and `ExecutionTime` -- the
# solver's own CPU accounting, which is what gets charged -- inflates under
# contention.  Wave A is the 14 expensive cases, wave B the 8 coarse ones, so at
# most 14 solvers are ever resident.
#
# NO `set -u`.  See run_case.sh.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE" || exit 3

WAVE_A="X_hi_x_SST X_hi_x_KE X_hi_x_LS \
        X_hi_f_SST X_hi_f_KE X_hi_f_LS X_hi_f_LAM \
        X_lo_f_SST X_lo_f_KE X_lo_f_LS X_lo_f_LAM \
        P_hi_f_SST P_hi_f_KE P_lo_f_SST"
WAVE_B="X_hi_c_SST X_hi_c_KE X_hi_c_LS X_hi_c_LAM \
        X_lo_c_SST X_lo_c_KE X_lo_c_LS X_lo_c_LAM"

rm -f DONE.* ALL_DONE WAVE_A_DONE
echo "wave A started $(date -u +%Y-%m-%dT%H:%M:%SZ)"
for c in $WAVE_A; do ./run_case.sh "$c" > "out.$c.log" 2>&1 & done
wait
echo "wave_a_finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > WAVE_A_DONE

echo "wave B started $(date -u +%Y-%m-%dT%H:%M:%SZ)"
for c in $WAVE_B; do ./run_case.sh "$c" > "out.$c.log" 2>&1 & done
wait

n=$(ls DONE.* 2>/dev/null | wc -l)
{
  echo "all_cases_finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "markers=$n"
  echo "expected=22"
} > ALL_DONE
echo "done: $n markers"
