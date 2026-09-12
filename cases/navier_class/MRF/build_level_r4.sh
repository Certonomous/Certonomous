#!/usr/bin/env bash
# MRF_R4 PER-LEVEL MESH BUILDER -- usage: build_level_r4.sh <RUNDIR> <NX> <NY> <NZ> <NCBL>
# Derived from build_level_r2.sh with TWO changes, both asserted: the system
# template is R4/system (impeller refinement (2 4), checkpoint policy), and the
# blade/disc/baffle thickness override is REQUIRED rather than optional.
#
# R2's ONE CHANGE vs R1: the refinement-transition shell is held CONSTANT IN
# METRES instead of constant in CELLS.  R1 used nCellsBetweenLevels 3 at every
# level, so the shell was 30.0 / 20.0 / 13.3 mm coarse->fine and the family was
# NOT geometrically similar -- the mechanism R1's A1.1 identified and the
# hypothesis H1 that R2 tests.  Here NCBL is passed per level so the shell is
# ~31 mm at all three:
#     coarse  NCBL 3 x 10.000 mm = 30.0 mm
#     medium  NCBL 5 x  6.275 mm = 31.4 mm
#     fine    NCBL 8 x  3.902 mm = 31.2 mm      max/min = 1.047 (<= 5%)
#
# NEVER `rm -rf $RUNDIR` (R1 A1.5: build_mesh.sh opens that way and pointed at a
# graded level it deletes it).  This script REFUSES an existing RUNDIR.
# Every substitution asserts on BOTH sides (L-221/L-222) and every stage's rc is
# captured INSIDE the shell that ran it, never inferred from an End line.
set -o pipefail

# The bashrc source's stderr is CAPTURED, never discarded, and its rc checked
# (verification ruling 2026-09-10).  No `set -u`: the OpenFOAM bashrc
# dereferences WM_PROJECT_DIR unset and under `set -u` exits rc=127 at line 184
# before any abort handler can run.  Measured 2026-09-10.
_ENVLOG="$(mktemp -t mrf_r2_env.XXXXXX.log)"
source /usr/lib/openfoam/openfoam2606/etc/bashrc > "$_ENVLOG" 2>&1
_ENVRC=$?
if [ "$_ENVRC" -ne 0 ] || ! command -v snappyHexMesh >/dev/null 2>&1; then
    echo "ABORT: OpenFOAM env did not load (rc=$_ENVRC, snappyHexMesh not on PATH)."
    cat "$_ENVLOG"; exit 2
fi

HERE="$(cd "$(dirname "$0")" && pwd)"

# ---- R4's ONE CHANGE, and this script REFUSES to run without it ------------
# generate_geometry.py's override is INERT unless MRF_FEATURE_THICKNESS_M is set,
# so a forgotten export would silently rebuild R2's 4.00 mm blades under an R4
# directory name -- the exact shape of failure that is invisible afterwards.
: "${MRF_FEATURE_THICKNESS_M:?ABORT: MRF_FEATURE_THICKNESS_M is unset; R4 must not build R2 geometry}"
[ "$MRF_FEATURE_THICKNESS_M" = "0.00155" ] || {
    echo "ABORT: MRF_FEATURE_THICKNESS_M=$MRF_FEATURE_THICKNESS_M, but MRF_R4_PREREGISTRATION section 1 registers 0.00155"; exit 2; }
export MRF_FEATURE_THICKNESS_M
RUNDIR="${1:?usage: build_level_r2.sh <RUNDIR> <NX> <NY> <NZ> <NCBL>}"
NX="${2:?NX}"; NY="${3:?NY}"; NZ="${4:?NZ}"; NCBL="${5:?NCBL}"

[ -e "$RUNDIR" ] && { echo "ABORT: $RUNDIR already exists; this script never deletes a case directory"; exit 2; }
mkdir -p "$RUNDIR" || { echo "ABORT: mkdir $RUNDIR"; exit 2; }
cp "$_ENVLOG" "$RUNDIR/log.env"; rm -f "$_ENVLOG"

# R2 system template (physical-thickness shell); constant/ and 0.orig from the
# shared case root -- geometry, MRF setup and fields are UNCHANGED from R1.
cp -r "$HERE/R4/system" "$RUNDIR/system"      || { echo "ABORT: R4 system copy"; exit 2; }
cp -r "$HERE/constant" "$HERE/0.orig" "$RUNDIR/" || { echo "ABORT: template copy"; exit 2; }
mkdir -p "$RUNDIR/constant/triSurface"

exec > "$RUNDIR/log.build" 2>&1
echo "=== MRF_R4 build $(date -u +%FT%TZ) rundir=$RUNDIR block=($NX $NY $NZ) NCBL=$NCBL"

# ---- background block, asserted on both sides ----------------------------
BMD="$RUNDIR/system/blockMeshDict"
before=$(grep -c 'hex (0 1 2 3 4 5 6 7) (32 32 36)' "$BMD")
[ "$before" = "1" ] || { echo "ABORT: expected exactly 1 template hex line, found $before"; exit 2; }
sed -i "s/hex (0 1 2 3 4 5 6 7) (32 32 36)/hex (0 1 2 3 4 5 6 7) ($NX $NY $NZ)/" "$BMD"
after=$(grep -c "hex (0 1 2 3 4 5 6 7) ($NX $NY $NZ)" "$BMD")
[ "$after" = "1" ] || { echo "ABORT: block substitution did not read back"; exit 2; }
echo "blockMeshDict background block -> ($NX $NY $NZ), matched once and read back once"

# ---- THE ONE CHANGE: nCellsBetweenLevels, asserted on both sides ---------
SHD="$RUNDIR/system/snappyHexMeshDict"
before=$(grep -c 'nCellsBetweenLevels @NCBL@;' "$SHD")
[ "$before" = "1" ] || { echo "ABORT: expected exactly 1 @NCBL@ token, found $before"; exit 2; }
sed -i "s/nCellsBetweenLevels @NCBL@;/nCellsBetweenLevels $NCBL;/" "$SHD"
after=$(grep -c "nCellsBetweenLevels $NCBL;" "$SHD")
[ "$after" = "1" ] || { echo "ABORT: NCBL substitution did not read back"; exit 2; }
# NO PIPELINE HERE.  `grep -c` EXITS 1 WHEN THE COUNT IS ZERO, and under
# `set -o pipefail` the old form
#     grep -c '@NCBL@' "$SHD" | grep -qx 0 || abort
# aborted the build precisely when the token was correctly ABSENT -- an inverted
# assert that failed a good build (measured 2026-09-11T00:55Z, first R2 fine
# attempt).  Capture the count, then test it numerically.
LEFT=$(grep -c '@NCBL@' "$SHD" || true)
[ "$LEFT" = "0" ] || { echo "ABORT: $LEFT @NCBL@ token(s) survived"; exit 2; }
DX=$(awk -v n="$NX" 'BEGIN{printf "%.5f", 0.32/n*1000}')
echo "snappyHexMeshDict nCellsBetweenLevels -> $NCBL ; base cell dx = ${DX} mm ; shell = $(awk -v n="$NCBL" -v d="$DX" 'BEGIN{printf "%.2f", n*d}') mm"

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

# ---- the cap must NOT have bound: a silently truncated refinement would
#      destroy the very similarity this rung exists to create.
NC=$(grep -m1 'nCells' constant/polyMesh/owner | sed 's/.*nCells: *//;s/ .*//')
echo "delivered nCells = $NC"
awk -v n="$NC" 'BEGIN{ if (n+0 >= 40000000) { print "ABORT: delivered count reached maxLocalCells -- refinement may have been SILENTLY TRUNCATED"; exit 1 } else print "cap check OK: delivered " n " << maxLocalCells 40000000" }' || exit 2

echo "rc: blockMesh=$(cat rc.blockMesh) sfe=$(cat rc.surfaceFeatureExtract) snappy=$(cat rc.snappyHexMesh) topoSet=$(cat rc.topoSet) checkMesh=$(cat rc.checkMesh)"
cat WALL_SECONDS.txt
echo "DONE build_level_r2 $RUNDIR  $(date -u +%FT%TZ)"
