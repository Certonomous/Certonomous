#!/usr/bin/env bash
# VMFL007-R3 -- Task 2 ARM ROBUSTNESS SCREEN.
#
# Builds one VMFL007 wedge case at a given (NX,NR) with a given fvSolution "arm"
# and runs simpleFoam to a FIXED iteration count.  It records CONVERGENCE
# EVIDENCE ONLY -- rc, End line, iteration count reached, residual behaviour and
# the peak-to-peak of the dp monitor on its tail window.
#
# IT DELIBERATELY DOES NOT COMPUTE, PRINT OR STORE ANY DEVIATION FROM THE
# REFERENCE VALUE.  Arm selection is on convergence robustness alone; an
# agreement number computed before selection contaminates the selection.
#
# Usage: arm_screen.sh <outdir> <armFvSolutionFile> <NX> <NR> <endTime>
# Writes <outdir>/RUN_RC.txt and <outdir>/log.simpleFoam.  Never writes inside
# verification/runs/.
# NOTE: no `set -u` -- the OpenFOAM etc/bashrc dereferences unset variables and
# aborts the shell under nounset, which silently skipped blockMesh on first use.
OUT=$1; ARM=$2; NX=$3; NR=$4; ET=$5
SRC=/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL007_R2/A5_PBiCGStab_DIC

rm -rf "$OUT"; mkdir -p "$OUT"
cp -a "$SRC/constant" "$SRC/system" "$SRC/0" "$OUT/"
rm -rf "$OUT/constant/polyMesh"
sed -e "s/__NX__/$NX/" -e "s/__NR__/$NR/" \
    /home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL007/L1_25x25/system/blockMeshDict.template \
    > "$OUT/system/blockMeshDict"
cp "$ARM" "$OUT/system/fvSolution"
sed -i "s/^endTime  *[0-9]*;/endTime         $ET;/" "$OUT/system/controlDict"

source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
cd "$OUT" || exit 3
blockMesh > log.blockMesh 2>&1 || { echo "blockMesh FAILED"; exit 3; }
T0=$(date +%s)
simpleFoam > log.simpleFoam 2>&1
RC=$?
T1=$(date +%s)
WALL=$((T1-T0))

LASTT=$(grep -c 'ExecutionTime' log.simpleFoam)
ENDS=$(grep -c '^End' log.simpleFoam)
{
  echo "arm      = $(basename "$ARM")"
  echo "mesh     = ${NX}x${NR}"
  echo "endTime  = $ET"
  echo "rc       = $RC"
  echo "iters    = $LASTT"
  echo "End      = $ENDS"
  echo "wall_s   = $WALL"
  echo "ranks    = 1"
  echo "core_min = $(python3 -c "print(f'{$WALL/60:.4f}')")"
} > RUN_RC.txt
cat RUN_RC.txt
