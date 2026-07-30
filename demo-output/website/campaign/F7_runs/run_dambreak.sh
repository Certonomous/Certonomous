#!/usr/bin/env bash
# run_dambreak.sh <case_dir> [ranks]
# blockMesh -> setFields -> (decomposePar) -> interFoam -> reconstructPar
# -> writeCellCentres.  Foreground; all output to log.* inside the case.
CASE="$1"
RANKS="${2:-4}"
set +u
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -eu
cd "$CASE"
rm -rf processor* 0
blockMesh              > log.blockMesh 2>&1
checkMesh              > log.checkMesh 2>&1
cp -r 0.orig 0
setFields              > log.setFields 2>&1
if [ "$RANKS" -gt 1 ]; then
    decomposePar -force > log.decomposePar 2>&1
    mpirun -np "$RANKS" interFoam -parallel > log.interFoam 2>&1
    reconstructPar -newTimes > log.reconstructPar 2>&1
else
    interFoam           > log.interFoam 2>&1
fi
postProcess -func writeCellCentres -time 0 > log.writeCellCentres 2>&1
echo "done: $CASE"
tail -3 log.interFoam
