#!/bin/bash
# F1 TOPOLOGY-STUDY batch runner.  MESH_STANDARD 8.1 build trial -- NOT a registered rung.
#
# DIFFERENCE FROM te_study/run_batch.sh, AND THE REASON FOR IT.  That runner wrote the single
# character "-" into RC_blockMesh.txt / RC_checkMesh.txt to record "no mesh attempted".  All 14
# of its b1 variants died at a ModuleNotFoundError, so every one of those files held "-", and a
# reader that treats a non-empty RC file as a result reads a FALSE ZERO.  This runner NEVER
# writes an RC file for a step it did not run: it writes NOT_ATTEMPTED_<step>.txt instead.  A
# MISSING RC FILE CANNOT BE MISREAD AS A ZERO.  Every rc is read back FROM THE FILE, never
# inferred, because `set -e` gates neither at tool top level nor inside ( set -e; ... ).
S=/home/ubuntu/Certonomous/verification/runs/F1_MESH_TRIALS_2026-08-25/topology_study
G=$S/gen_topo.py
MAN=$1; JOBS=${2:-4}
[ -f "$MAN" ] || { echo "ABORT: no manifest $MAN"; exit 1; }
[ -f "$G" ]   || { echo "ABORT: no generator $G"; exit 1; }
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
  sync
  local RCD=$(cat "$D/RC_dict.txt")
  if [ "$RCD" != "0" ]; then
    echo "$NAME: GENERATOR FAILED rc=$RCD -- NO MESH ATTEMPTED, no RC_blockMesh/RC_checkMesh written"
    echo "generator rc=$RCD" > "$D/NOT_ATTEMPTED_blockMesh.txt"
    echo "generator rc=$RCD" > "$D/NOT_ATTEMPTED_checkMesh.txt"
    echo $(( $(date +%s) - T0 )) > "$D/WALL_S.txt"; return 1
  fi
  ( cd "$D" && rm -rf constant && blockMesh > log.blockMesh 2>&1; echo $? > RC_blockMesh.txt )
  sync
  local RCB=$(cat "$D/RC_blockMesh.txt")
  if [ "$RCB" != "0" ]; then
    # MESH_STANDARD 8.2: a blockMesh refusal is a DIAGNOSTIC.  It is captured with its log and
    # reported.  No generator is edited to make the refusal go away.
    echo "$NAME: blockMesh REFUSED rc=$RCB -- CAPTURED, NOT ROUTED AROUND (MESH_STANDARD 8.2)"
    echo "blockMesh rc=$RCB" > "$D/NOT_ATTEMPTED_checkMesh.txt"
    echo $(( $(date +%s) - T0 )) > "$D/WALL_S.txt"; return 1
  fi
  ( cd "$D" && checkMesh > log.checkMesh 2>&1; echo $? > RC_checkMesh.txt )
  sync
  echo $(( $(date +%s) - T0 )) > "$D/WALL_S.txt"
  echo "$NAME m=$M  rc $(cat $D/RC_dict.txt)/$(cat $D/RC_blockMesh.txt)/$(cat $D/RC_checkMesh.txt)  $(cat $D/WALL_S.txt)s"
}

T0=$(date +%s); n=0
while IFS='|' read -r NAME ENVS M; do
  case "$NAME" in ''|\#*) continue;; esac
  one "$NAME" "$ENVS" "$M" &
  n=$((n+1)); [ $((n % JOBS)) -eq 0 ] && wait
done < "$MAN"
wait
echo "BATCH wall $(( $(date +%s) - T0 ))s over $n variants"
