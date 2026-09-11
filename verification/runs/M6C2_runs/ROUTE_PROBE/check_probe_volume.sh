#!/bin/bash
# Reads the FIVE METHOD NUMBERS the probe was built to produce. rc is never the verdict;
# the checkMesh REPORT TEXT is read (M6C1 Addendum 2 bound 3).
set -u
R=/home/ubuntu/Certonomous/verification/runs/M6C2_runs
P=$R/ROUTE_PROBE
C=$P/foam
chmod 0777 $P
mkdir -p $C/system $C/constant
# 1. volume CGNS -> formatted multiblock PLOT3D, in the image that can read the CGNS
/usr/bin/time -f "VOL2P3D_WALL_S %e PEAK_RSS_KB %M" -o $P/time.vol2p3d \
  docker run --rm -v $R:/work dafoam-team:v1 bash -c \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; python3 /work/MP/vol2plot3d.py /work/ROUTE_PROBE/ROUTE_PROBE_vol.cgns /work/ROUTE_PROBE/ROUTE_PROBE_vol.xyz" \
  > $P/log.vol2p3d 2>&1
echo "vol2p3d_rc=$?" > $P/RC_CHECK.txt
[ -s $P/ROUTE_PROBE_vol.xyz ] || { echo "NO_PLOT3D_ARTIFACT" >> $P/RC_CHECK.txt; exit 5; }
set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc '' > $P/log.foam_src 2>&1; set -u
cat > $C/system/controlDict <<'CD'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application checkMesh; startFrom startTime; startTime 0; stopAt endTime;
endTime 1; deltaT 1; writeControl timeStep; writeInterval 1;
CD
plot3dToFoam -case $C -noBlank $P/ROUTE_PROBE_vol.xyz > $P/log.plot3dToFoam 2>&1
echo "plot3dToFoam_rc=$?" >> $P/RC_CHECK.txt
checkMesh -case $C -allGeometry -allTopology > $P/log.checkMesh 2>&1
echo "checkMesh_rc=$?" >> $P/RC_CHECK.txt
echo "done=$(date -u +%H:%M:%SZ)" >> $P/RC_CHECK.txt
