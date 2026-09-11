#!/bin/bash
# Convert one level's Plot3D volume mesh to OpenFOAM and checkMesh it.
# rc is recorded but NEVER graded on: the PRINTED VERDICT LINES are the grading path.
LVL=$1; R=/home/ubuntu/Certonomous/verification/runs/CRM_WINGALONE_runs; D=$R/$LVL
source /usr/lib/openfoam/openfoam2606/etc/bashrc > $D/log.foam_bashrc_source 2>&1
cd $D || exit 90
rm -rf foam/constant/polyMesh foam/0 log.plot3dToFoam log.checkMesh CONVERT_RC.txt DONE_CHECK
t0=$(date +%s)
plot3dToFoam -case foam -noBlank volumeMesh.xyz > log.plot3dToFoam 2>&1
rc1=$?
t1=$(date +%s)
echo "PLOT3DTOFOAM_RC=$rc1"  > CONVERT_RC.txt
echo "PLOT3DTOFOAM_WALL_S=$((t1-t0))" >> CONVERT_RC.txt
if [ $rc1 -ne 0 ]; then echo "CONVERT FAILED rc=$rc1"; tail -20 log.plot3dToFoam; exit $rc1; fi
checkMesh -case foam -allTopology -allGeometry > log.checkMesh 2>&1
rc2=$?
t2=$(date +%s)
echo "CHECKMESH_RC=$rc2 (NOT the grading path)" >> CONVERT_RC.txt
echo "CHECKMESH_WALL_S=$((t2-t1))" >> CONVERT_RC.txt
echo "CONVERT_CHECK_MARKER_OK $(date -u +%Y-%m-%dT%H:%M:%SZ)" > DONE_CHECK
cat CONVERT_RC.txt
