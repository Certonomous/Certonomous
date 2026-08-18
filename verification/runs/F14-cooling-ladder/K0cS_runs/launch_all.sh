#!/bin/bash
# Launch every K0cS case concurrently and wait for all of them.
# Each case writes its own DONE.<case> marker; this script writes ALL_DONE last.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE" || exit 3
rm -f DONE.* ALL_DONE
for c in S_SST_f S_KE_f S_LS_f S_SST_c S_KE_c S_LS_c C1_laminar C2_seed_d100 C3_prt128 C4_adiabatic; do
    ./run_cases.sh "$c" > "out.$c.log" 2>&1 &
done
wait
{
  echo "all_cases_finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "markers=$(ls DONE.* 2>/dev/null | wc -l)"
} > ALL_DONE
