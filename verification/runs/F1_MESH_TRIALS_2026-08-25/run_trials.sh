#!/bin/bash
# F1 mesh-topology TRIAL -- v2 butterfly tip fill via blockMesh.  NOT a registered
# rung: MESH_STANDARD 8.1 says build and checkMesh BEFORE any ladder is frozen,
# and this is that build.  SERIAL, 1 RANK; decomposition is not applicable here.
R=/home/ubuntu/Certonomous/verification/runs/F1_MESH_TRIALS_2026-08-25
G=/home/ubuntu/Certonomous/cases/F1_onera_m6/make_blockmesh_f1.py
T0=$(date +%s)
source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>&1
command -v blockMesh >/dev/null || { echo 'ABORT: blockMesh not on PATH'; exit 1; }
for m in 1 2 4; do
  D=$R/v2_m$m; mkdir -p "$D/system"
  cat > "$D/system/controlDict" <<'EOF'
FoamFile{version 2.0;format ascii;class dictionary;object controlDict;}
application blockMesh; startFrom startTime; startTime 0; stopAt endTime; endTime 1; deltaT 1;
writeControl timeStep; writeInterval 1;
EOF
  cat > "$D/system/fvSchemes" <<'EOF'
FoamFile{version 2.0;format ascii;class dictionary;object fvSchemes;}
ddtSchemes{default steadyState;} gradSchemes{default Gauss linear;} divSchemes{default none;}
laplacianSchemes{default Gauss linear corrected;} interpolationSchemes{default linear;}
snGradSchemes{default corrected;}
EOF
  echo "FoamFile{version 2.0;format ascii;class dictionary;object fvSolution;}
solvers{}" > "$D/system/fvSolution"
  S=$(date +%s); python3 "$G" "$m" "$D" > "$D/log.makeDict" 2>&1
  echo $? > "$D/RC_dict.txt"; sync
  ( cd "$D" && rm -rf constant && blockMesh > log.blockMesh 2>&1; echo $? > RC_blockMesh.txt )
  sync
  ( cd "$D" && checkMesh > log.checkMesh 2>&1; echo $? > RC_checkMesh.txt )
  sync
  echo "m$m: dict rc=$(cat $D/RC_dict.txt) blockMesh rc=$(cat $D/RC_blockMesh.txt) checkMesh rc=$(cat $D/RC_checkMesh.txt)  $(( $(date +%s) - S ))s"
done
echo "TRIAL wall $(( $(date +%s) - T0 ))s"
