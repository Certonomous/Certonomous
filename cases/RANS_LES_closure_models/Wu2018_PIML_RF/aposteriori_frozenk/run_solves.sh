#!/bin/bash
# 36 solves: 3 cases x 2 arms x 6 configs. Each bounded by its controlDict cap
# AND a 3600 s timeout. Nothing is ever killed by hand.
set -o pipefail
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
OUT=/home/ubuntu/closure-data/aposteriori_frozenk/wu2018
run_one() {
  D=$1
  [ -f "$D/log.solve.done" ] && { echo "[skip] ${D#*wu2018/}"; return 0; }
  S=$(date +%s)
  ( cd "$D" && timeout 3600 simpleFoam > log.solve 2>&1 )
  RC=$?; E=$(( $(date +%s) - S ))
  echo "rc=$RC seconds=$E" > "$D/log.solve.done"
  echo "[done] ${D#*wu2018/} rc=$RC ${E}s iters=$(grep -c '^Time = ' "$D/log.solve")"
}
export -f run_one
for C in AR_1_Ret_360 AR_3_Ret_360 CBFS13700; do
  for A in S L; do for G in null truth mean ml_s0 ml_s1 ml_s2; do echo "$OUT/$C/${A}_$G"; done; done
done | xargs -P 6 -I{} bash -c 'run_one {}'
echo "ALL SOLVES FINISHED"
