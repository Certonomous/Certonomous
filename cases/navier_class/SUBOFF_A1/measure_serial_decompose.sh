#!/bin/bash
# SUBOFF A1b -- MEASURE THE PEAK RSS OF THE **SERIAL** decomposePar STEP.
#
# WHY.  The SOLVE_L2 memory gate is derived from a PER-RANK footprint measured off L1's
# running simpleFoam ranks.  decomposePar logs `nProcs : 1` -- it is SERIAL, it holds the
# WHOLE mesh in ONE process, and NOTHING in a rank-derived bound covers it.  A memory
# prediction is a BOUND, not a best estimate, and the only error that hurts is the low one.
#
# IT RUNS IN A SCRATCH COPY AND NEVER IN A LIVE CASE.  L0c is the smallest mesh in the
# family and is NOT solve-ready and NOT scheduled, so measuring on it costs no queued work.
# The scratch case takes L0c's polyMesh with SOLVE_L2's OWN system/ and 0/, so the step
# measured is the step SOLVE_L2 will actually run -- mesh AND fields -- not a mesh-only
# proxy that would under-read the bound.
#
# Peak RSS comes from /usr/bin/time -v ("Maximum resident set size"), which is the kernel's
# own high-water mark -- not a poller, which can miss a peak between samples.
set -u
SRC="$1"; SCRATCH="$2"; OUT="$3"; LEVEL="${4:-L0c}"
rm -rf "$SCRATCH"; mkdir -p "$SCRATCH"
cp -r "$SRC/$LEVEL/constant" "$SCRATCH/constant"
rm -rf "$SCRATCH/constant/polyMesh/sets" 2>/dev/null
cp -r "$SRC/SOLVE_L2/system" "$SCRATCH/system"
cp -r "$SRC/SOLVE_L2/0" "$SCRATCH/0"
cp "$SRC/$LEVEL/system/decomposeParDict" "$SCRATCH/system/decomposeParDict" 2>/dev/null || true
set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc '' >/dev/null 2>&1; set -u
cd "$SCRATCH" || exit 90
T0=$(date +%s)
/usr/bin/time -v decomposePar -force > log.decomposePar 2> time.decomposePar
RC=$?
T1=$(date +%s)
PEAK=$(grep "Maximum resident set size" time.decomposePar | grep -oE '[0-9]+$')
CELLS=$(grep -m1 "nCells:" log.decomposePar | grep -oE "[0-9]+" | head -1)
{ echo "level=$LEVEL"; echo "rc=$RC"; echo "wall_s=$((T1-T0))"; echo "peak_rss_kB=$PEAK"; echo "cells=$CELLS"; } > "$OUT"
echo "$RC" > "$SCRATCH/measure_rc"
