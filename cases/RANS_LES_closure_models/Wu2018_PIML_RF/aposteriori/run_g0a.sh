#!/bin/bash
# G0a: stock kOmegaSST vs kOmegaSSTCorrected with zero corrections, SAME start,
# SAME 200 iterations. Registered threshold: rel-L2 in U < 1e-10.
set -o pipefail
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
OUT=/home/ubuntu/closure-data/aposteriori/wu2018
for CASE in AR_1_Ret_360 AR_3_Ret_360 CBFS13700; do
  for CFG in stock null; do
    SRC=$OUT/$CASE/$CFG; D=$OUT/_g0a/$CASE/$CFG
    rm -rf "$D"; mkdir -p "$(dirname "$D")"; cp -r "$SRC" "$D"
    /home/ubuntu/closure-venv/bin/python - "$D/system/controlDict" "$D/system/fvSolution" <<'PY'
import sys,re
cd,fs=sys.argv[1],sys.argv[2]
s=open(cd).read()
s=re.sub(r'^endTime\s+.*$','endTime         200;',s,flags=re.M)
s=re.sub(r'^writeInterval\s+.*$','writeInterval   200;',s,flags=re.M)
open(cd,"w").write(s)
t=open(fs).read()
t=re.sub(r'\n\s*residualControl\s*\{[^{}]*\}', '\n    residualControl { }', t, count=1)
open(fs,"w").write(t)
PY
    ( cd "$D" && timeout 1800 simpleFoam > log.g0a 2>&1 )
    echo "[g0a] $CASE/$CFG exit=$? last=$(grep -c '^Time = ' "$D/log.g0a")"
  done
done
