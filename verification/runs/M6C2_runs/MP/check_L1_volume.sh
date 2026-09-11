#!/bin/bash
# Converts the L1 volume and reads its gates. rc is never the verdict; the report text is.
set -u
R=/home/ubuntu/Certonomous/verification/runs/M6C2_runs
L=$R/MP/L1; C=$L/foam
chmod 0777 $L
mkdir -p $C/system $C/constant
/usr/bin/time -f "VOL2P3D_WALL_S %e PEAK_RSS_KB %M" -o $L/time.vol2p3d \
  docker run --rm -v $R:/work dafoam-team:v1 bash -c \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; python3 /work/MP/vol2plot3d.py /work/MP/L1/m6c2_mp_L1_vol.cgns /work/MP/L1/m6c2_mp_L1_vol.xyz" \
  > $L/log.vol2p3d 2>&1
echo "vol2p3d_rc=$?" > $L/RC_CHECK.txt
[ -s $L/m6c2_mp_L1_vol.xyz ] || { echo "NO_PLOT3D_ARTIFACT" >> $L/RC_CHECK.txt; exit 5; }
set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc '' > $L/log.foam_src 2>&1; set -u
cat > $C/system/controlDict <<'CD'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application checkMesh; startFrom startTime; startTime 0; stopAt endTime;
endTime 1; deltaT 1; writeControl timeStep; writeInterval 1;
CD
cat > $C/system/fvSchemes <<'FS'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes { default steadyState; } gradSchemes { default Gauss linear; }
divSchemes { default none; } laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; } snGradSchemes { default corrected; }
FS
echo 'FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; } solvers {}' > $C/system/fvSolution
plot3dToFoam -case $C -noBlank $L/m6c2_mp_L1_vol.xyz > $L/log.plot3dToFoam 2>&1
echo "plot3dToFoam_rc=$?" >> $L/RC_CHECK.txt
checkMesh -case $C -allGeometry -allTopology > $L/log.checkMesh 2>&1
echo "checkMesh_rc=$?" >> $L/RC_CHECK.txt
[ -f $C/constant/polyMesh/sets/nonOrthoFaces ] && \
  python3 $R/MP/locate_over_gate_faces.py $C/constant/polyMesh $C/constant/polyMesh/sets/nonOrthoFaces > $L/log.locate 2>&1
echo "locate_rc=$?" >> $L/RC_CHECK.txt
echo "done=$(date -u +%H:%M:%SZ)" >> $L/RC_CHECK.txt
