#!/bin/bash
# F1 (ONERA M6) rung R0 -- build the three levels, checkMesh each, grade SS5 admission.
# SERIAL, 1 RANK.  Domain decomposition is NOT APPLICABLE to this rung: mesh
# generation and checkMesh both run single-rank, so SS6's partition pair does not
# enter here.  It enters at R1/R2/R3/R4.  Stated explicitly so an absent
# decomposition is not later read as an omission.
# HARD CAP: 90 core-min (SS8).  Serial => core-min == wall-min.  A BREACH STOPS THE RUN.
# NOTE, measured 2026-08-25: `set -u` is INCOMPATIBLE with the OpenFOAM v2606
# bashrc -- sourcing it under `set -u` exits 1 on an unbound variable, and with
# stderr redirected that failure arrives as an EMPTY LOG and rc=1.  This script
# therefore does not use `set -u`; every step's rc is MEASURED into its own
# RC_*.txt and read back instead.
R=/home/ubuntu/Certonomous/verification/runs/F13_ONERA_M6_runs
G=/home/ubuntu/Certonomous/cases/F13_onera_m6/make_blockmesh_m6.py
CAP_S=5400
T0=$(date +%s)
cap() { E=$(( $(date +%s) - T0 )); if [ "$E" -gt "$CAP_S" ]; then
  echo "CAP BREACH: ${E}s > ${CAP_S}s -- R0 STOPPED, no new budget" | tee -a "$R/R0_CAP_BREACH.txt"; exit 9; fi; }
source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>>"$R/log.r0.sourceerr"
command -v checkMesh >/dev/null || { echo 'ABORT: checkMesh not on PATH after sourcing'; exit 1; }
for m in 1 2 4; do
  cap
  D=$R/mesh/m$m
  mkdir -p "$D/system"
  cat > "$D/system/controlDict" <<'EOF'
FoamFile{version 2.0;format ascii;class dictionary;object controlDict;}
application checkMesh; startFrom startTime; startTime 0; stopAt endTime; endTime 1; deltaT 1;
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
  S=$(date +%s)
  python3 "$G" "$m" "$D" > "$D/log.makeMesh" 2>&1
  echo $? > "$D/RC_make.txt"; sync
  echo "mesh m$m built in $(( $(date +%s) - S ))s rc=$(cat "$D/RC_make.txt")"
  cap
  S=$(date +%s)
  ( cd "$D" && checkMesh > log.checkMesh 2>&1; echo $? > RC_check.txt )
  sync
  echo "checkMesh m$m in $(( $(date +%s) - S ))s rc=$(cat "$D/RC_check.txt")"
done
cap
python3 "$R/analyse_f13.py" 1 2 4 > "$R/log.analyse_f13" 2>&1
echo $? > "$R/RC_analyse.txt"; sync
echo "R0 wall $(( $(date +%s) - T0 ))s"
