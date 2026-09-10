#!/usr/bin/env bash
# MRF_R1 coarse-mesh build (background/silent). Instantiates a run case from the
# committed template, generates the parametric STL geometry, and runs the OF
# meshing chain: blockMesh -> surfaceFeatureExtract -> snappyHexMesh -> topoSet
# -> checkMesh. Run outputs land under verification/runs/ (NOT beside the case).
#
#   build_mesh.sh <RUNDIR>
# (no `set -u`: the OpenFOAM bashrc dereferences unset vars and would abort.)
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
HERE="$(cd "$(dirname "$0")" && pwd)"          # cases/navier_class/MRF
RUNDIR="${1:?usage: build_mesh.sh <RUNDIR>}"

rm -rf "$RUNDIR"; mkdir -p "$RUNDIR"
cp -r "$HERE/system" "$HERE/constant" "$HERE/0.orig" "$RUNDIR/"
mkdir -p "$RUNDIR/constant/triSurface"
python3 "$HERE/mesh/generate_geometry.py" "$RUNDIR/constant/triSurface" > "$RUNDIR/log.geometry" 2>&1

cd "$RUNDIR" || exit 3
blockMesh                 > log.blockMesh            2>&1; echo "blockMesh rc=$?"
surfaceFeatureExtract     > log.surfaceFeatureExtract 2>&1; echo "surfaceFeatureExtract rc=$?"
snappyHexMesh -overwrite  > log.snappyHexMesh        2>&1; echo "snappyHexMesh rc=$?"
topoSet                   > log.topoSet              2>&1; echo "topoSet rc=$?"
checkMesh -allTopology -allGeometry > log.checkMesh  2>&1; echo "checkMesh rc=$?"
echo "DONE build_mesh $RUNDIR"
