#!/usr/bin/env bash
# VMFL010 graded-run driver -- Laminar Flow in a 90-degree Tee-Junction (manual p.39).
# GRADED COMPUTE IS LOCKED (see VMFL059 header). NO compute until supervisor unlock.
# GEOMETRY IS NOW SOURCED (prereg Amendment 2026-08-25): domain x in [0,4], y in [0,6]
# read from archive mesh nodes (plarb_r4-1.cas.h5, meshes/1/nodes/coords/1). Cells per
# level: L1/L2/L3 = 3600 / 14400 / 57600 (9 unit-squares). Scratch smoke on this
# geometry gave split 0.886 vs target 0.887 (grades nothing; the graded run is LOCKED).
set -u
CASE_DIR="$(cd "$(dirname "$0")" && pwd)/case"
RUN_ROOT="${1:?usage: run_vmfl010.sh <run_root>}"
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo ABORT: no OpenFOAM; exit 1; }
declare -A N=( [L1]=20 [L2]=40 [L3]=80 )  N2=( [L1]=40 [L2]=80 [L3]=160 )  N3=( [L1]=60 [L2]=120 [L3]=240 )
ENDTIME=2000   # SIMPLE iterations (residualControl 1e-7 stops earlier)
for L in L1 L2 L3; do
  OUT="$RUN_ROOT/$L"
  [ -e "$OUT/0" -o -n "$(ls -d $OUT/[1-9]* 2>/dev/null)" ] && { echo "ABORT age guard: $OUT exists"; exit 1; }
  mkdir -p "$OUT" || { echo ABORT mkdir; exit 1; }
  cp -r "$CASE_DIR"/{0,constant,system} "$OUT"/ || { echo ABORT copy; exit 1; }
  sed -e "s/__2N__/${N2[$L]}/g" -e "s/__3N__/${N3[$L]}/g" -e "s/__N__/${N[$L]}/g" \
      "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo ABORT sed bmd; exit 1; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo ABORT sed cd; exit 1; }
  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 && touch 0/U && simpleFoam > log.simpleFoam 2>&1 \
      && for p in inlet mainOutlet branchOutlet; do postProcess -func "flowRatePatch(name=$p)" -latestTime > log.pp_$p 2>&1; done ) \
      || { echo "ABORT solve $L"; exit 1; }
  echo "done $L"
done
echo "VMFL010 all levels complete -> grade with grade_vmfl010.py --run-root $RUN_ROOT"
