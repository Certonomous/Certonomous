#!/bin/bash
# Frozen-k case copies. Benchmark clone is READ-ONLY. Two arms:
#   S : k frozen at the shipped SST k
#   L : k frozen at k_LES
set -o pipefail
B=/home/ubuntu/closure-challenge-benchmark/data
OUT=/home/ubuntu/closure-data/aposteriori_frozenk/wu2018
FLD=/home/ubuntu/closure-data/aposteriori/wu2018/_fields   # G0-verified bijDelta/kDeficit
declare -A SRC=( [AR_1_Ret_360]="$B/DUCT/AR_1_Ret_360" [AR_3_Ret_360]="$B/DUCT/AR_3_Ret_360" [CBFS13700]="$B/CBFS" )
declare -A CAP=( [AR_1_Ret_360]=200000 [AR_3_Ret_360]=200000 [CBFS13700]=40000 )
mkdir -p "$OUT"
for CASE in "${!SRC[@]}"; do
  S=${SRC[$CASE]}
  T=$(ls "$S" | grep -E '^[0-9]+$' | sort -n | tail -1)
  for ARM in S L; do
   for CFG in null truth mean ml_s0 ml_s1 ml_s2; do
    D=$OUT/$CASE/${ARM}_$CFG
    rm -rf "$D"; mkdir -p "$D/0" "$D/constant"
    cp -r "$S/system" "$D/system"; cp -r "$S/constant/polyMesh" "$D/constant/polyMesh"
    cp "$S/constant/transportProperties" "$D/constant/" 2>/dev/null || true
    [ -f "$S/caseDef" ] && cp "$S/caseDef" "$D/caseDef"
    for f in U p k omega nut phi; do cp "$S/$T/$f" "$D/0/$f" 2>/dev/null || true; done
    # arm L: replace k with k_LES (rename the object entry)
    if [ "$ARM" = "L" ]; then
      sed -e 's/object *k_LES *;/object      k;/' "$S/0/k_LES" > "$D/0/k"
    fi
    # corrections
    if [ "$CFG" = "null" ]; then
      /home/ubuntu/closure-venv/bin/python - "$FLD/$CASE/truth/bijDelta" "$D/0/bijDelta" <<'PY'
import sys
src,dst=sys.argv[1],sys.argv[2]; t=open(src).read()
head,rest=t.split("internalField",1); bf=rest[rest.index("boundaryField"):]
open(dst,"w").write(head+"internalField   uniform (0 0 0 0 0 0);\n\n"+bf)
PY
      cp "$FLD/$CASE/truth/kDeficit" "$D/0/kDeficit"
    else
      cp "$FLD/$CASE/$CFG/bijDelta" "$D/0/bijDelta"
      cp "$FLD/$CASE/$CFG/kDeficit" "$D/0/kDeficit"
    fi
    cat > "$D/constant/turbulenceProperties" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; location "constant"; object turbulenceProperties; }
simulationType RAS;
RAS { RASModel kOmegaSSTCorrectedFrozenK; turbulence on; printCoeffs on; }
EOF
    /home/ubuntu/closure-venv/bin/python - "$D/system/controlDict" "${CAP[$CASE]}" <<'PY'
import sys,re
p,cap=sys.argv[1],sys.argv[2]; s=open(p).read()
s=re.sub(r'^libs.*$','',s,flags=re.M)
s=re.sub(r'^startFrom.*$','startFrom       startTime;',s,flags=re.M)
if re.search(r'^startTime\s+',s,flags=re.M): s=re.sub(r'^startTime\s+.*$','startTime       0;',s,flags=re.M)
else: s=re.sub(r'^startFrom.*$','startFrom       startTime;\nstartTime       0;',s,flags=re.M)
s=re.sub(r'^endTime\s+.*$',f'endTime         {cap};',s,flags=re.M)
s=re.sub(r'writeInterval\s+\$endTime','writeInterval   1000',s)
s=re.sub(r'^writeInterval\s+.*$','writeInterval   1000;',s,flags=re.M)
s=re.sub(r'^purgeWrite.*$','purgeWrite      2;',s,flags=re.M)
i=s.find('functions')
if i>=0: s=s[:i]+'functions { }\n'
s=s.rstrip()+'\nlibs ( "libspartaTurbulenceModels.so" "libwu2018FrozenK.so" );\n'
if 'purgeWrite' not in s: s=s.replace('writeInterval   1000;','writeInterval   1000;\npurgeWrite      2;')
open(p,"w").write(s)
PY
    # k and omega are FROZEN -> excluded from the convergence criterion (prereg sec.7)
    /home/ubuntu/closure-venv/bin/python - "$D/system/fvSolution" <<'PY'
import sys,re
p=sys.argv[1]; s=open(p).read()
new="""    residualControl
    {
        "(U|Ux|Uy|Uz)"  1e-6;
        p               1e-6;
    }"""
if 'residualControl' in s: s=re.sub(r'\n\s*residualControl\s*\{[^{}]*\}', "\n"+new, s, count=1)
else: s=re.sub(r'(SIMPLE\s*\{)', r'\1\n'+new, s, count=1)
open(p,"w").write(s)
PY
   done
  done
  echo "built $CASE (2 arms x 6 configs), latest time $T"
done
