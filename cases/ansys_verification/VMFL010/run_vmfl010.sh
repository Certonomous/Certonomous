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
# --- LAUNCH-TIME FREEZE CHECK (CLAUDE.md rule 2) -----------------------------
# The pre-registration AND the comparator on disk MUST be the blobs committed at
# HEAD -- the freeze is the evidence, and no solver starts without it. `set -e`
# does NOT gate at a Bash tool's top level and `( set -e; ... )` fails silently,
# so EVERY check below gates EXPLICITLY with || { echo ABORT...; exit 1; }.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 1; }
PREREG_REL="cases/ansys_verification/VMFL010/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL010/grade_vmfl010.py"
git -C "$REPO" cat-file -e "HEAD:$PREREG_REL" 2>/dev/null || { echo "ABORT: $PREREG_REL is not committed at HEAD -- the freeze is the evidence"; exit 1; }
git -C "$REPO" cat-file -e "HEAD:$GRADER_REL" 2>/dev/null || { echo "ABORT: $GRADER_REL is not committed at HEAD"; exit 1; }
PREREG_HEAD="$(git -C "$REPO" rev-parse "HEAD:$PREREG_REL")" || { echo "ABORT: cannot resolve HEAD:$PREREG_REL"; exit 1; }
GRADER_HEAD="$(git -C "$REPO" rev-parse "HEAD:$GRADER_REL")" || { echo "ABORT: cannot resolve HEAD:$GRADER_REL"; exit 1; }
PREREG_DISK="$(git -C "$REPO" hash-object "$REPO/$PREREG_REL")" || { echo "ABORT: cannot hash $PREREG_REL on disk"; exit 1; }
GRADER_DISK="$(git -C "$REPO" hash-object "$REPO/$GRADER_REL")" || { echo "ABORT: cannot hash $GRADER_REL on disk"; exit 1; }
[ "$PREREG_DISK" = "$PREREG_HEAD" ] || { echo "ABORT: $PREREG_REL on disk ($PREREG_DISK) differs from HEAD ($PREREG_HEAD)"; exit 1; }
[ "$GRADER_DISK" = "$GRADER_HEAD" ] || { echo "ABORT: $GRADER_REL on disk ($GRADER_DISK) differs from HEAD ($GRADER_HEAD)"; exit 1; }
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT for the launch record"; exit 1; }
{ echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "prereg = $PREREG_REL"
  echo "prereg_sha_head = $PREREG_HEAD"
  echo "prereg_sha_disk = $PREREG_DISK"
  echo "comparator = $GRADER_REL"
  echo "comparator_sha_head = $GRADER_HEAD"
  echo "comparator_sha_disk = $GRADER_DISK"
} > "$RUN_ROOT/LAUNCH_RECORD.txt" || { echo "ABORT: cannot write $RUN_ROOT/LAUNCH_RECORD.txt"; exit 1; }
echo "  freeze check OK: prereg $PREREG_HEAD ; comparator $GRADER_HEAD (recorded in $RUN_ROOT/LAUNCH_RECORD.txt)"
# ----------------------------------------------------------------------------
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
