#!/bin/bash
# 18 solves: {AR_1_Ret_360, AR_3_Ret_360, CBFS13700} x {null,truth,mean,ml_s0,ml_s1,ml_s2}
# Each bounded by its own controlDict iteration cap AND a 3600 s timeout.
set -o pipefail
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
OUT=/home/ubuntu/closure-data/aposteriori/wu2018
run_one() {
  D=$1
  [ -f "$D/log.solve.done" ] && { echo "[skip] $D"; return 0; }
  S=$(date +%s)
  ( cd "$D" && timeout 3600 simpleFoam > log.solve 2>&1 )
  RC=$?
  E=$(( $(date +%s) - S ))
  echo "rc=$RC seconds=$E" > "$D/log.solve.done"
  echo "[done] ${D#$OUT/} rc=$RC ${E}s iters=$(grep -c '^Time = ' "$D/log.solve")"
}
export -f run_one; export OUT
for C in AR_1_Ret_360 AR_3_Ret_360 CBFS13700; do
  for G in null truth mean ml_s0 ml_s1 ml_s2; do echo "$OUT/$C/$G"; done
done | xargs -P 6 -I{} bash -c 'run_one {}'
echo "ALL SOLVES FINISHED"
