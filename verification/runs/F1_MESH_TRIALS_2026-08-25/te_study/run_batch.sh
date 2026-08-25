#!/bin/bash
# F1 TE-STUDY batch runner.  MESH_STANDARD 8.1 build trial -- NOT a registered rung.
# Reads a variant manifest, builds each variant with gen_var.py, runs blockMesh then
# checkMesh, and writes RC_*.txt for each step.  Serial per variant; variants in
# parallel, capped at $JOBS.  No generator is edited to silence a refusal: a blockMesh
# refusal is CAPTURED (rc + log kept) and the variant is left recorded as refused.
S=/home/ubuntu/Certonomous/verification/runs/F1_MESH_TRIALS_2026-08-25/te_study
G=$S/gen_var.py
MAN=$1; JOBS=${2:-8}
[ -f "$MAN" ] || { echo "ABORT: no manifest $MAN"; exit 1; }
source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>&1
command -v blockMesh >/dev/null || { echo 'ABORT: blockMesh not on PATH'; exit 1; }
command -v checkMesh >/dev/null || { echo 'ABORT: checkMesh not on PATH'; exit 1; }

one () {
  local NAME="$1" ENVS="$2" M="$3"
  local D=$S/$NAME
  rm -rf "$D"; mkdir -p "$D/system" || { echo "ABORT mkdir $NAME"; return 1; }
  cat > "$D/system/controlDict" <<'CD'
FoamFile{version 2.0;format ascii;class dictionary;object controlDict;}
application blockMesh; startFrom startTime; startTime 0; stopAt endTime; endTime 1; deltaT 1;
writeControl timeStep; writeInterval 1;
CD
  cat > "$D/system/fvSchemes" <<'FS'
FoamFile{version 2.0;format ascii;class dictionary;object fvSchemes;}
ddtSchemes{default steadyState;} gradSchemes{default Gauss linear;} divSchemes{default none;}
laplacianSchemes{default Gauss linear corrected;} interpolationSchemes{default linear;}
snGradSchemes{default corrected;}
FS
  echo "FoamFile{version 2.0;format ascii;class dictionary;object fvSolution;}
solvers{}" > "$D/system/fvSolution"
  echo "$ENVS" > "$D/DIALS.txt"; echo "$M" > "$D/LEVEL.txt"
  local T0=$(date +%s)
  ( export $ENVS; python3 "$G" "$M" "$D" > "$D/log.makeDict" 2>&1; echo $? > "$D/RC_dict.txt" )
  if [ "$(cat $D/RC_dict.txt)" != "0" ]; then
    echo "$NAME: GENERATOR rc=$(cat $D/RC_dict.txt) -- no mesh attempted"
    echo "-" > "$D/RC_blockMesh.txt"; echo "-" > "$D/RC_checkMesh.txt"
    echo $(( $(date +%s) - T0 )) > "$D/WALL_S.txt"; return 0
  fi
  ( cd "$D" && rm -rf constant && blockMesh > log.blockMesh 2>&1; echo $? > RC_blockMesh.txt )
  if [ "$(cat $D/RC_blockMesh.txt)" != "0" ]; then
    echo "$NAME: blockMesh REFUSED rc=$(cat $D/RC_blockMesh.txt) -- captured, NOT routed around"
    echo "-" > "$D/RC_checkMesh.txt"
    echo $(( $(date +%s) - T0 )) > "$D/WALL_S.txt"; return 0
  fi
  ( cd "$D" && checkMesh > log.checkMesh 2>&1; echo $? > RC_checkMesh.txt )
  echo $(( $(date +%s) - T0 )) > "$D/WALL_S.txt"
  echo "$NAME m=$M  rc $(cat $D/RC_dict.txt)/$(cat $D/RC_blockMesh.txt)/$(cat $D/RC_checkMesh.txt)  $(cat $D/WALL_S.txt)s"
}

T0=$(date +%s)
n=0
while IFS='|' read -r NAME ENVS M; do
  case "$NAME" in ''|\#*) continue;; esac
  one "$NAME" "$ENVS" "$M" &
  n=$((n+1)); [ $((n % JOBS)) -eq 0 ] && wait
done < "$MAN"
wait
echo "BATCH wall $(( $(date +%s) - T0 ))s over $n variants"
