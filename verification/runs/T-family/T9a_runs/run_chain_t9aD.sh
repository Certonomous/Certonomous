#!/bin/bash
# T9a-D SERIAL chain: ONE laplacianFoam process at a time, nProcs 1, so the arm
# peaks at 1 core of 16. Twelve cores carry other lanes' solvers (T1b L4 x4,
# T3 ext1 x8) and NOTHING here touches them.
root="$(cd "$(dirname "$0")" && pwd)"
for c in D_A_c D_A_m D_A_f D_B_x D_C_c D_C_m D_C_f D_R_f; do
  cd "$root/$c" || { echo "rc=99 wall=0s checkMesh_rc=99 case=$c missing" > "$root/STATUS.$c"; continue; }
  setsid nohup ../run_one_t9aD.sh "$c" > /dev/null 2>&1 &
  wait $!
done
echo "chain finished $(date -u +%FT%TZ)" > "$root/CHAIN_DONE_D"
