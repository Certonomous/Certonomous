#!/bin/bash
# T9aH extra-case chain: the three cases the frozen comparator cannot see.
# The seven frozen case names are run by the BYTE-IDENTICAL run_chain_t9a.sh
# (sha cbf3b957...); this file exists only because that chain's case list is
# fixed, and it invokes the SAME byte-identical per-case wrapper run_one_t9a.sh
# (sha 163c4345...) so the two chains differ in nothing but their case list.
#
# Serial: one laplacianFoam process at a time, nProcs 1, peak 1 core of 16.
# Other lanes' solvers on this box are NOT touched.
# Registered cap: 300 core-seconds for the whole rung.  An overrun STOPS THE
# RUN; it does not get a new budget.
root="$(cd "$(dirname "$0")" && pwd)"
for c in RL_f H40_f H4000_f; do
  cd "$root/$c" || { echo "rc=99 wall=0s checkMesh_rc=99 case=$c missing" > "$root/STATUS.$c"; continue; }
  setsid nohup ../run_one_t9a.sh "$c" > /dev/null 2>&1 &
  wait $!
done
echo "chain finished $(date -u +%FT%TZ)" > "$root/CHAIN_DONE_H"
