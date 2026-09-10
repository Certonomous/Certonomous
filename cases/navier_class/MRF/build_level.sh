#!/usr/bin/env bash
# MRF_R1 -- build ONE ladder level of the Rushton stirred tank at a given
# background-block resolution. Same chain as build_mesh.sh (blockMesh ->
# surfaceFeatureExtract -> snappyHexMesh -> topoSet -> checkMesh) with two
# deliberate differences:
#
#   (1) IT REFUSES an existing RUNDIR instead of `rm -rf`-ing it.  build_mesh.sh
#       opens with `rm -rf "$RUNDIR"`; pointed at a graded level that deletes it.
#       No `rm -rf` on a case directory appears anywhere in this file.
#   (2) The background block count is a PARAMETER, substituted into
#       blockMeshDict with an ASSERT that the substitution happened and reads
#       back the intended value (never a blind replace).
#
# Geometric similarity: ONLY the background block count changes between levels.
# Every snappyHexMesh feature level, surface level, refinement region and
# nCellsBetweenLevels is left untouched, so cell size at every refinement level
# scales with the base cell and the family is similar.  The STL geometry is
# resolution-independent (mesh/generate_geometry.py fixes NSEG = 64), so all
# levels converge to the SAME faceted body -- which is what a Roache triple
# requires.
#
#   build_level.sh <RUNDIR> <NX> <NY> <NZ>
#
# rc of every stage is captured INSIDE this shell and written to rc.<stage>,
# never inferred from an End line (setsid-parent-returns-zero lesson, L-342).
# (no `set -u`: the OpenFOAM bashrc dereferences unset vars and would abort --
#  under `set -u` it exits rc=127 at bashrc line 184 `WM_PROJECT_DIR: unbound
#  variable`, BEFORE any abort handler can run.  Measured 2026-09-10.)
set -o pipefail

# The bashrc source's stderr is CAPTURED, NEVER DISCARDED, and its rc is
# checked.  Verification ruling 2026-09-10: an error that is ERASED and an
# error that NEVER HAPPENED must not leave the same trace.  `>/dev/null 2>&1`
# on this exact line is what turned a loud abort into a silent one in the Case
# Protocol stage-4 launcher and in launch_graded.sh's first version.
_ENVLOG="$(mktemp -t mrf_build_env.XXXXXX.log)"
source /usr/lib/openfoam/openfoam2606/etc/bashrc > "$_ENVLOG" 2>&1
_ENVRC=$?
if [ "$_ENVRC" -ne 0 ] || ! command -v simpleFoam >/dev/null 2>&1; then
    echo "ABORT: OpenFOAM env did not load (source rc=$_ENVRC, simpleFoam not on PATH)."
    echo "----- captured output of etc/bashrc (this is what >/dev/null used to erase) -----"
    cat "$_ENVLOG"
    exit 2
fi
HERE="$(cd "$(dirname "$0")" && pwd)"
RUNDIR="${1:?usage: build_level.sh <RUNDIR> <NX> <NY> <NZ>}"
NX="${2:?NX}"; NY="${3:?NY}"; NZ="${4:?NZ}"

[ -e "$RUNDIR" ] && { echo "ABORT: $RUNDIR already exists; this script never deletes a case directory"; exit 2; }
mkdir -p "$RUNDIR" || { echo "ABORT: mkdir $RUNDIR"; exit 2; }
# the captured env output now lives BESIDE the case, not in a temp file
cp "$_ENVLOG" "$RUNDIR/log.env" 2>/dev/null; rm -f "$_ENVLOG"
cp -r "$HERE/system" "$HERE/constant" "$HERE/0.orig" "$RUNDIR/" || { echo "ABORT: template copy"; exit 2; }
mkdir -p "$RUNDIR/constant/triSurface"

BMD="$RUNDIR/system/blockMeshDict"
before=$(grep -c 'hex (0 1 2 3 4 5 6 7) (32 32 36)' "$BMD")
[ "$before" = "1" ] || { echo "ABORT: expected exactly 1 template hex line, found $before"; exit 2; }
sed -i "s/hex (0 1 2 3 4 5 6 7) (32 32 36)/hex (0 1 2 3 4 5 6 7) ($NX $NY $NZ)/" "$BMD"
after=$(grep -c "hex (0 1 2 3 4 5 6 7) ($NX $NY $NZ)" "$BMD")
[ "$after" = "1" ] || { echo "ABORT: substitution did not read back as ($NX $NY $NZ)"; exit 2; }
echo "blockMeshDict background block set to ($NX $NY $NZ); template line matched once and read back once"

python3 "$HERE/mesh/generate_geometry.py" "$RUNDIR/constant/triSurface" > "$RUNDIR/log.geometry" 2>&1
echo "$?" > "$RUNDIR/rc.geometry"

cd "$RUNDIR" || exit 3
t0=$(date +%s)
blockMesh                           > log.blockMesh             2>&1; echo "$?" > rc.blockMesh
t1=$(date +%s)
surfaceFeatureExtract               > log.surfaceFeatureExtract 2>&1; echo "$?" > rc.surfaceFeatureExtract
t2=$(date +%s)
/usr/bin/time -v snappyHexMesh -overwrite > log.snappyHexMesh   2>&1; echo "$?" > rc.snappyHexMesh
t3=$(date +%s)
topoSet                             > log.topoSet               2>&1; echo "$?" > rc.topoSet
t4=$(date +%s)
checkMesh -allTopology -allGeometry > log.checkMesh             2>&1; echo "$?" > rc.checkMesh
t5=$(date +%s)
printf 'blockMesh %d\nsurfaceFeatureExtract %d\nsnappyHexMesh %d\ntopoSet %d\ncheckMesh %d\nTOTAL %d\n' \
  $((t1-t0)) $((t2-t1)) $((t3-t2)) $((t4-t3)) $((t5-t4)) $((t5-t0)) > WALL_SECONDS.txt
echo "rc: blockMesh=$(cat rc.blockMesh) sfe=$(cat rc.surfaceFeatureExtract) snappy=$(cat rc.snappyHexMesh) topoSet=$(cat rc.topoSet) checkMesh=$(cat rc.checkMesh)"
cat WALL_SECONDS.txt
echo "DONE build_level $RUNDIR"
