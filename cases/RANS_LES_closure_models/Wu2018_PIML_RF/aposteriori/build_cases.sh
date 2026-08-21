#!/bin/bash
# Build a-posteriori case copies. Benchmark clone is READ-ONLY: we copy out.
# Usage: build_cases.sh
set -euo pipefail
B=/home/ubuntu/closure-challenge-benchmark/data
OUT=/home/ubuntu/closure-data/aposteriori/wu2018
declare -A SRC=( [AR_1_Ret_360]="$B/DUCT/AR_1_Ret_360" [AR_3_Ret_360]="$B/DUCT/AR_3_Ret_360" [CBFS13700]="$B/CBFS" )
declare -A CAP=( [AR_1_Ret_360]=200000 [AR_3_Ret_360]=200000 [CBFS13700]=40000 )

for CASE in "${!SRC[@]}"; do
  S=${SRC[$CASE]}
  T=$(ls "$S" | grep -E '^[0-9]+$' | sort -n | tail -1)
  [ -n "$T" ] && [ -d "$S/$T" ] || { echo "MISSING latest time dir in $S"; exit 1; }
  echo "  $CASE: latest time = $T"
  for CFG in null stock truth mean ml_s0 ml_s1 ml_s2; do
    D=$OUT/$CASE/$CFG
    rm -rf "$D"; mkdir -p "$D/0" "$D/constant"
    cp -r "$S/system" "$D/system"
    cp -r "$S/constant/polyMesh" "$D/constant/polyMesh"
    cp "$S/constant/transportProperties" "$D/constant/" 2>/dev/null || true
    [ -f "$S/caseDef" ] && cp "$S/caseDef" "$D/caseDef"
    for f in U p k omega nut phi; do cp "$S/$T/$f" "$D/0/$f" 2>/dev/null || true; done
    # corrections
    if [ "$CFG" = "stock" ]; then
      RAS=kOmegaSST; LIBS=""
    else
      RAS=kOmegaSSTCorrected; LIBS='libs ( "libspartaTurbulenceModels.so" );'
      if [ "$CFG" = "null" ]; then
        # zero corrections: reuse truth's patch layout, zeroed
        /home/ubuntu/closure-venv/bin/python - "$OUT/_fields/$CASE/truth/bijDelta" "$D/0/bijDelta" <<'PY'
import sys,re
src,dst=sys.argv[1],sys.argv[2]
t=open(src).read()
head,rest=t.split("internalField",1)
bf=rest[rest.index("boundaryField"):]
open(dst,"w").write(head+"internalField   uniform (0 0 0 0 0 0);\n\n"+bf)
PY
        cp "$OUT/_fields/$CASE/truth/kDeficit" "$D/0/kDeficit"
      else
        cp "$OUT/_fields/$CASE/$CFG/bijDelta" "$D/0/bijDelta"
        cp "$OUT/_fields/$CASE/$CFG/kDeficit" "$D/0/kDeficit"
      fi
    fi
    cat > "$D/constant/turbulenceProperties" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; location "constant"; object turbulenceProperties; }
simulationType RAS;
RAS { RASModel $RAS; turbulence on; printCoeffs on; }
EOF
    # controlDict
    /home/ubuntu/closure-venv/bin/python - "$D/system/controlDict" "${CAP[$CASE]}" "$LIBS" <<'PY'
import sys,re
p,cap,libs=sys.argv[1],sys.argv[2],sys.argv[3]
s=open(p).read()
s=re.sub(r'^libs.*$','',s,flags=re.M)
s=re.sub(r'^startFrom.*$','startFrom       startTime;',s,flags=re.M)
if re.search(r'^startTime\s+',s,flags=re.M):
    s=re.sub(r'^startTime\s+.*$','startTime       0;',s,flags=re.M)
else:   # duct controlDicts use 'startFrom latestTime' and omit startTime
    s=re.sub(r'^startFrom.*$','startFrom       startTime;\\nstartTime       0;',s,flags=re.M)
s=re.sub(r'writeInterval\s+\$endTime','writeInterval   '+cap,s)
s=re.sub(r'^endTime\s+.*$',f'endTime         {cap};',s,flags=re.M)
s=re.sub(r'^writeInterval\s+.*$',f'writeInterval   {cap};',s,flags=re.M)
s=re.sub(r'^purgeWrite.*$','purgeWrite      0;',s,flags=re.M)
# v2112-era functionObjects reference etc files absent in v2606; we read
# residuals from the log, so disable them outright.
i=s.find('functions')
if i>=0: s=s[:i]+'functions { }\n'

if libs.strip(): s=s.rstrip()+"\n"+libs+"\n"
open(p,"w").write(s)
PY
    # residualControl -> registered 1e-6 on all
    /home/ubuntu/closure-venv/bin/python - "$D/system/fvSolution" <<'PY'
import sys,re
p=sys.argv[1]; s=open(p).read()
new="""    residualControl
    {
        "(U|Ux|Uy|Uz)"  1e-6;
        p               1e-6;
        k               1e-6;
        omega           1e-6;
    }"""
if 'residualControl' in s:
    s=re.sub(r'\n\s*residualControl\s*\{[^{}]*\}', "\n"+new, s, count=1)
else:
    s=re.sub(r'(SIMPLE\s*\{)', r'\1\n'+new, s, count=1)
open(p,"w").write(s)
PY
  done
  echo "built $CASE (7 configs)"
done
