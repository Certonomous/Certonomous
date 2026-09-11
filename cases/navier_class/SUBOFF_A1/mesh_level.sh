#!/bin/bash
# SUBOFF_A1 -- build ONE mesh level.  Detached-safe: rc is captured INSIDE this
# wrapper from each utility, never around a setsid line (L: setsid parent returns 0).
# checkMesh is run with -allGeometry -allTopology and its rc is NEVER the verdict;
# the PRINTED "Failed N mesh checks" line is what the gate reads.
set -u
CASE="$1"; RANKS="$2"
S="$CASE/STATUS.mesh"
set +u
source /usr/lib/openfoam/openfoam2606/etc/bashrc '' > "$CASE/log.foam_bashrc_source" 2>&1
SRC=$?
set -u
if [ "$SRC" -ne 0 ]; then echo "91" > "$CASE/mesh_rc"; echo "REFUSED=foam_source rc=$SRC" > "$S"; exit 91; fi
cd "$CASE" || exit 90
echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$S"
T0=$(date +%s)

surfaceCheck constant/triSurface/hull.stl > log.surfaceCheck.hull 2>&1; echo "surfaceCheck_hull_rc=$?" >> "$S"
surfaceCheck constant/triSurface/sail.stl > log.surfaceCheck.sail 2>&1; echo "surfaceCheck_sail_rc=$?" >> "$S"

blockMesh > log.blockMesh 2>&1; RC=$?; echo "blockMesh_rc=$RC" >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > "$CASE/mesh_rc"; exit "$RC"; fi

decomposePar -force > log.decomposePar 2>&1; RC=$?; echo "decomposePar_rc=$RC" >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > "$CASE/mesh_rc"; exit "$RC"; fi

mpirun -np "$RANKS" snappyHexMesh -overwrite -parallel > log.snappyHexMesh 2>&1
RC=$?; echo "snappyHexMesh_rc=$RC" >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > "$CASE/mesh_rc"; exit "$RC"; fi

reconstructParMesh -constant > log.reconstructParMesh 2>&1; RC=$?
echo "reconstructParMesh_rc=$RC" >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > "$CASE/mesh_rc"; exit "$RC"; fi
rm -rf processor*

checkMesh -allGeometry -allTopology > log.checkMesh.FULLFLAG 2>&1
echo "checkMesh_rc_NOT_THE_VERDICT=$?" >> "$S"

T1=$(date +%s)
{ echo "wall_s=$((T1-T0))"; echo "ranks=$RANKS"
  echo "core_min=$(echo "($T1-$T0)*$RANKS/60" | bc -l)"
  echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } >> "$S"
echo "0" > "$CASE/mesh_rc"
exit 0
