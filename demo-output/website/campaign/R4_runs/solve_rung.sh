#!/usr/bin/env bash
# R4: solve one Ahmed constant-ratio rung at a FIXED 4 MPI ranks.
set -e
CASE="$1"; RANKS=4
cd "$CASE"
rm -rf 0 processor* postProcessing log.potentialFoam log.simpleFoam log.decomposePar log.reconstructPar
cp -r 0.orig 0
printf 'FoamFile{version 2.0;format ascii;class dictionary;object decomposeParDict;}\nnumberOfSubdomains %d;\nmethod scotch;\n' $RANKS > system/decomposeParDict
openfoam2606 decomposePar -force > log.decomposePar 2>&1
openfoam2606 mpirun -np $RANKS potentialFoam -writephi -parallel > log.potentialFoam 2>&1
openfoam2606 mpirun -np $RANKS simpleFoam -parallel > log.simpleFoam 2>&1
openfoam2606 reconstructPar -latestTime > log.reconstructPar 2>&1
grep -m1 "SIMPLE solution converged" log.simpleFoam || tail -3 log.simpleFoam
