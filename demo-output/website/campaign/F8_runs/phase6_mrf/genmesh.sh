#!/usr/bin/env bash
# F8 Phase VI feasibility mesh: blockMesh -> decompose -> parallel snappyHexMesh
# -> parallel topoSet (region0 MRF zone) -> parallel renumberMesh -> checkMesh.
# Fields are all "uniform" in 0.orig, so they are copied straight into each
# processorN/0 rather than run through decomposePar -fields.
FOAM_BASHRC=/usr/lib/openfoam/openfoam2606/etc/bashrc
source "$FOAM_BASHRC" >/dev/null 2>&1 || true
set -e
cd "$(dirname "$0")"

echo "=== blockMesh ==="
blockMesh > log.blockMesh 2>&1

echo "=== decomposePar (mesh only) ==="
decomposePar -force > log.decomposePar 2>&1

echo "=== snappyHexMesh -parallel ==="
mpirun -np 4 snappyHexMesh -parallel -overwrite > log.snappyHexMesh 2>&1

echo "=== topoSet -parallel (region0 MRF cellZone) ==="
mpirun -np 4 topoSet -parallel > log.topoSet 2>&1

echo "=== renumberMesh -parallel ==="
mpirun -np 4 renumberMesh -parallel -overwrite > log.renumberMesh 2>&1

echo "=== reconstructParMesh -constant (merge refined mesh back to serial) ==="
reconstructParMesh -constant > log.reconstructParMesh 2>&1

echo "=== seed case-level 0/ then decomposePar (mesh+fields, proper processor BCs) ==="
rm -rf 0
cp -r 0.orig 0
rm -rf processor*
decomposePar > log.decomposePar2 2>&1

echo "=== checkMesh -parallel ==="
mpirun -np 4 checkMesh -parallel > log.checkMesh 2>&1 || true

echo "=== cell count ==="
grep -a "cells:" log.checkMesh | head -5
echo "MESH_GENERATION_DONE"
