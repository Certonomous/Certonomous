#!/usr/bin/env bash
# VMFL010-R2 graded-run driver -- Laminar Flow in a 90-degree Tee-Junction (manual p.39).
# GRADED COMPUTE IS LOCKED. NO compute until the ansys-verification supervisor unlocks it;
# the launch permission is HELD on Sanaa's desk (rule 9). This driver exists as a frozen
# input; running it is the supervisor's act after the four personal checks.
#
# R2 lever (SINGLE-LEVER, supervisor §3 ruling 2026-09-07; gate UNCHANGED): the base
# VMFL010 was ALREADY a self-similar structured-hex r=2 triple (birth certs: 3600/14400/57600
# hex, non-orth 0, skew ~1e-13). Its split was textbook 2nd-order in magnitude but sign-flipped
# at the finest level (N=80) by a ~1e-4 iterative perturbation at residualControl 1e-7. R2
# KEEPS the base triple N=20/40/80 UNCHANGED (drop nothing, reposition nothing) and changes
# ONLY the convergence to residualControl 1e-9 (in fvSolution). This directly tests the noise
# diagnosis on the SAME triple that 'failed'. No scheme, no gate changes.
#
# NO `set -u`: it is CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606 (sourcing etc/bashrc
# dereferences WM_PROJECT_DIR before assigning it -> rc 127). EVERY check gates EXPLICITLY
# with || { echo ABORT...; exit 1; }; `set -e` does not gate at a Bash tool top level.
#
# COST INSTRUMENT (rule 12): RANKS in BOTH formulae so a parallel copy inherits a correct cap:
#     timeout_s    = remaining_core_min * 60 / RANKS
#     core_minutes = wall_s * RANKS / 60
# CAP_CORE_MIN is the RUNNING TOTAL across all three levels. AN OVERRUN STOPS THE RUN.
RANKS=1
CAP_CORE_MIN=18.0         # running total, frozen in PREREGISTRATION.md amendment (~4x the ~4.5 est)
CASE_DIR="$(cd "$(dirname "$0")" && pwd)/case"
RUN_ROOT="${1:?usage: run_vmfl010_r2.sh <run_root>}"
# --- LAUNCH-TIME FREEZE CHECK (rule 2): prereg AND comparator on disk == HEAD blobs --------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 1; }
PREREG_REL="cases/ansys_verification/VMFL010-R2/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL010-R2/grade_vmfl010_r2.py"
git -C "$REPO" cat-file -e "HEAD:$PREREG_REL" 2>/dev/null || { echo "ABORT: $PREREG_REL not committed at HEAD -- the freeze is the evidence"; exit 1; }
git -C "$REPO" cat-file -e "HEAD:$GRADER_REL" 2>/dev/null || { echo "ABORT: $GRADER_REL not committed at HEAD"; exit 1; }
PREREG_HEAD="$(git -C "$REPO" rev-parse "HEAD:$PREREG_REL")" || { echo "ABORT: cannot resolve HEAD:$PREREG_REL"; exit 1; }
GRADER_HEAD="$(git -C "$REPO" rev-parse "HEAD:$GRADER_REL")" || { echo "ABORT: cannot resolve HEAD:$GRADER_REL"; exit 1; }
PREREG_DISK="$(git -C "$REPO" hash-object "$REPO/$PREREG_REL")" || { echo "ABORT: cannot hash $PREREG_REL on disk"; exit 1; }
GRADER_DISK="$(git -C "$REPO" hash-object "$REPO/$GRADER_REL")" || { echo "ABORT: cannot hash $GRADER_REL on disk"; exit 1; }
[ "$PREREG_DISK" = "$PREREG_HEAD" ] || { echo "ABORT: $PREREG_REL on disk ($PREREG_DISK) differs from HEAD ($PREREG_HEAD)"; exit 1; }
[ "$GRADER_DISK" = "$GRADER_HEAD" ] || { echo "ABORT: $GRADER_REL on disk ($GRADER_DISK) differs from HEAD ($GRADER_HEAD)"; exit 1; }
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
{ echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "prereg = $PREREG_REL"; echo "prereg_sha_head = $PREREG_HEAD"; echo "prereg_sha_disk = $PREREG_DISK"
  echo "comparator = $GRADER_REL"; echo "comparator_sha_head = $GRADER_HEAD"; echo "comparator_sha_disk = $GRADER_DISK"
} > "$RUN_ROOT/LAUNCH_RECORD.txt" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 1; }
echo "  freeze check OK: prereg $PREREG_HEAD ; comparator $GRADER_HEAD"
# ------------------------------------------------------------------------------------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo ABORT: no OpenFOAM; exit 1; }
command -v simpleFoam >/dev/null || { echo "ABORT: simpleFoam not on PATH after sourcing"; exit 1; }
declare -A N=( [L1]=20 [L2]=40 [L3]=80 )  N2=( [L1]=40 [L2]=80 [L3]=160 )  N3=( [L1]=60 [L2]=120 [L3]=240 )
ENDTIME=8000   # SIMPLE iterations (residualControl 1e-9 stops earlier)
SPENT_CORE_MIN=0
TOTAL_WALL=0
for L in L1 L2 L3; do
  OUT="$RUN_ROOT/$L"
  [ -e "$OUT/0" -o -n "$(ls -d $OUT/[1-9]* 2>/dev/null)" ] && { echo "ABORT age guard: $OUT exists"; exit 1; }
  REMAIN=$(python3 -c "print(max(0.0, $CAP_CORE_MIN - $SPENT_CORE_MIN))") || { echo "ABORT: cannot compute remaining budget"; exit 1; }
  TIMEOUT_S=$(python3 -c "print(int($REMAIN * 60 / $RANKS))") || { echo "ABORT: cannot compute timeout"; exit 1; }
  [ "$TIMEOUT_S" -gt 0 ] || { echo "ABORT: BUDGET EXHAUSTED before $L (spent $SPENT_CORE_MIN of $CAP_CORE_MIN core-min). An overrun STOPS the run (rule 12)."; exit 1; }
  echo "--- $L  timeout=${TIMEOUT_S}s (remaining ${REMAIN} core-min of ${CAP_CORE_MIN})"
  mkdir -p "$OUT" || { echo ABORT mkdir; exit 1; }
  cp -r "$CASE_DIR"/{0,constant,system} "$OUT"/ || { echo ABORT copy; exit 1; }
  sed -e "s/__2N__/${N2[$L]}/g" -e "s/__3N__/${N3[$L]}/g" -e "s/__N__/${N[$L]}/g" \
      "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo ABORT sed bmd; exit 1; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo ABORT sed cd; exit 1; }
  T0=$(date +%s)
  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 && touch 0/U && timeout "$TIMEOUT_S" simpleFoam > log.simpleFoam 2>&1 \
      && for p in inlet mainOutlet branchOutlet; do postProcess -func "flowRatePatch(name=$p)" -latestTime > log.pp_$p 2>&1; done )
  RC=$?
  T1=$(date +%s); WALL=$((T1 - T0))
  CORE_MIN=$(python3 -c "print($WALL * $RANKS / 60.0)")
  SPENT_CORE_MIN=$(python3 -c "print($SPENT_CORE_MIN + $CORE_MIN)")
  TOTAL_WALL=$((TOTAL_WALL + WALL))
  printf 'rc=%d\nlevel=%s\nwall_s=%d\nranks=%d\ncore_min=%s\ntimeout_s=%d\n' \
    "$RC" "$L" "$WALL" "$RANKS" "$CORE_MIN" "$TIMEOUT_S" > "$OUT/RUN_RC.txt" || { echo "ABORT: could not write RUN_RC.txt for $L"; exit 1; }
  [ "$RC" -eq 0 ] || { echo "ABORT solve $L exited rc=$RC after ${WALL}s (timeout ${TIMEOUT_S}s). A non-zero rc is a FINDING, not a retry."; exit 1; }
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (spent ${SPENT_CORE_MIN}/${CAP_CORE_MIN})"
done
printf 'total_wall_s=%d\nranks=%d\ntotal_core_min=%s\ncap_core_min=%s\ncost_basis=owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED (COMPUTE_BUDGET_CHARTER sec.5)\n' \
  "$TOTAL_WALL" "$RANKS" "$SPENT_CORE_MIN" "$CAP_CORE_MIN" > "$RUN_ROOT/COST.txt" || { echo "ABORT: could not write COST.txt"; exit 1; }
echo "VMFL010-R2 all levels complete (${SPENT_CORE_MIN}/${CAP_CORE_MIN} core-min) -> grade: grade_vmfl010_r2.py --run-root $RUN_ROOT"
