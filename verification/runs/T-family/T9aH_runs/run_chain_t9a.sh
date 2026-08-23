#!/bin/bash
# Serial chain: one solver process at a time (host carries 15 other solver processes on 16 cores).
root="$(cd "$(dirname "$0")" && pwd)"
for c in W_c W_m W_f W_C3 F_c F_m F_f; do
  cd "$root/$c" || { echo "rc=99 wall=0s checkMesh_rc=99 case=$c missing" > "$root/STATUS.$c"; continue; }
  setsid nohup ../run_one_t9a.sh "$c" > /dev/null 2>&1 &
  wait $!
done
echo "chain finished $(date -u +%FT%TZ)" > "$root/CHAIN_DONE"
