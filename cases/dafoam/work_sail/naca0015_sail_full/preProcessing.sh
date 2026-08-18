#!/bin/bash

# Check if the OpenFOAM enviroments are loaded
if [ -z "$WM_PROJECT" ]; then
  echo "OpenFOAM environment not found, forgot to source the OpenFOAM bashrc?"
  exit
fi

# mesh already generated (snappyHexMesh, from the lab's own mesh cache) and
# staged into constant/polyMesh before this script runs.
echo "Checking mesh.."
checkMesh -allTopology -allGeometry > logMeshCheck.txt 2>&1
echo "Checking mesh.. Done! See logMeshCheck.txt"

# copy initial and boundary condition files
rm -rf 0
cp -r 0.orig 0
