#!/usr/bin/env bash
# VMFL059 graded-run driver -- Conduction in a Composite Solid Block (manual p.185).
# GRADED COMPUTE IS LOCKED. This script performs NO compute until the
# ansys-verification SUPERVISOR unlocks it (four personal checks, prereg frozen
# and committed). It refuses if an output level already exists (age guard,
# CLAUDE.md rule 4). Runs live under verification/runs/, NEVER beside the prose.
set -u
CASE_DIR="$(cd "$(dirname "$0")" && pwd)/case"
RUN_ROOT="${1:?usage: run_vmfl059.sh <run_root> (e.g. verification/runs/ansys_verification/VMFL059)}"
# --- LAUNCH-TIME FREEZE CHECK (CLAUDE.md rule 2) -----------------------------
# The pre-registration AND the comparator on disk MUST be the blobs committed at
# HEAD -- the freeze is the evidence, and no solver starts without it. `set -e`
# does NOT gate at a Bash tool's top level and `( set -e; ... )` fails silently,
# so EVERY check below gates EXPLICITLY with || { echo ABORT...; exit 1; }.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 1; }
PREREG_REL="cases/ansys_verification/VMFL059/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL059/grade_vmfl059.py"
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
# per-level grid (r=2) and frozen time controls (steady; tau~6.5e-5 s)
declare -A NX1=( [L1]=20 [L2]=40 [L3]=80 )  NX2=( [L1]=8 [L2]=16 [L3]=32 )  NY=( [L1]=10 [L2]=20 [L3]=40 )
ENDTIME=0.05; DELTAT=1e-4
for L in L1 L2 L3; do
  OUT="$RUN_ROOT/$L"
  [ -e "$OUT/0" -o -n "$(ls -d $OUT/[1-9]* 2>/dev/null)" ] && { echo "ABORT age guard: $OUT already has 0/ or a time dir"; exit 1; }
  mkdir -p "$OUT" || { echo ABORT mkdir; exit 1; }
  cp -r "$CASE_DIR"/{0,constant,system} "$OUT"/ || { echo ABORT copy; exit 1; }
  sed -e "s/__NX1__/${NX1[$L]}/g" -e "s/__NX2__/${NX2[$L]}/g" -e "s/__NY__/${NY[$L]}/g" \
      "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo ABORT sed bmd; exit 1; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" -e "s/__DELTAT__/$DELTAT/g" \
      "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo ABORT sed cd; exit 1; }
  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 && setFields > log.setFields 2>&1 \
      && touch 0/T && laplacianFoam > log.laplacianFoam 2>&1 \
      && postProcess -func "patchAverage(name=rightWall,T)" -latestTime > log.pp_cool 2>&1 \
      && postProcess -func "patchAverage(name=leftWall,T)"  -latestTime > log.pp_adiab 2>&1 ) \
      || { echo "ABORT solve $L"; exit 1; }
  echo "done $L"
done
echo "VMFL059 all levels complete -> grade with grade_vmfl059.py --run-root $RUN_ROOT"
