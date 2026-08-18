#!/usr/bin/env bash
# R4: mesh one Ahmed constant-ratio rung. Recipe identical to the production
# rung (surface level (3 4), feature level 2, region level 1); ONLY the
# background blockMesh division triple differs between rungs.
set -e
cd "$1"
rm -rf 0 constant/polyMesh constant/extendedFeatureEdgeMesh log.* postProcessing processor*
openfoam2606 surfaceFeatureExtract   > log.surfaceFeatureExtract 2>&1
openfoam2606 blockMesh               > log.blockMesh 2>&1
openfoam2606 snappyHexMesh -overwrite > log.snappyHexMesh 2>&1
openfoam2606 checkMesh               > log.checkMesh 2>&1
grep -m1 "    cells:" log.checkMesh
