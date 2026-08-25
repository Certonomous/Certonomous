#!/usr/bin/env bash
# VMFL059 graded-run driver -- Conduction in a Composite Solid Block (manual p.185).
# GRADED COMPUTE IS LOCKED. This script performs NO compute until the
# ansys-verification SUPERVISOR unlocks it (four personal checks, prereg frozen
# and committed). It refuses if an output level already exists (age guard,
# CLAUDE.md rule 4). Runs live under verification/runs/, NEVER beside the prose.
#
# NO `set -u`. It is CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606: sourcing
# etc/bashrc dereferences WM_PROJECT_DIR (bashrc line 184) BEFORE assigning it,
# and config.sh/functions unsets WM_SHELL_FUNCTIONS then dereferences it unguarded
# -- a non-removable cycle. MEASURED: `bash -c 'set -u; . <bashrc>'` -> rc 127,
# "WM_PROJECT_DIR: unbound variable"; the identical source without set -u -> rc 0,
# solver on PATH. `set -e` also does NOT gate at a Bash tool's top level and
# `( set -e; ... )` / `( set -u; ... )` fail silently, so EVERY check below gates
# EXPLICITLY with || { echo ABORT...; exit 1; }. A check that only prints is not one.
#
# THE COST INSTRUMENT (CLAUDE.md rule 12). RANKS is in BOTH formulae so a future
# parallel copy inherits a correct cap automatically -- a comment is a hope, a
# correct general formula is a guard:
#     timeout_s    = remaining_core_min * 60 / RANKS
#     core_minutes = wall_s * RANKS / 60
# CAP_CORE_MIN is the RUNNING TOTAL across all three levels, frozen at 15 in
# PREREGISTRATION.md sec.12. AN OVERRUN STOPS THE RUN; IT DOES NOT GET A NEW BUDGET.
RANKS=1
CAP_CORE_MIN=15            # slate running total, frozen in PREREGISTRATION.md sec.12
CASE_DIR="$(cd "$(dirname "$0")" && pwd)/case"
RUN_ROOT="${1:?usage: run_vmfl059.sh <run_root> (e.g. verification/runs/ansys_verification/VMFL059)}"
# --- LAUNCH-TIME FREEZE CHECK (CLAUDE.md rule 2) -----------------------------
# The pre-registration AND the comparator on disk MUST be the blobs committed at
# HEAD -- the freeze is the evidence, and no solver starts without it.
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
command -v laplacianFoam >/dev/null || { echo "ABORT: laplacianFoam not on PATH after sourcing"; exit 1; }
# per-level grid (r=2) and frozen time controls (steady; tau~6.5e-5 s)
declare -A NX1=( [L1]=20 [L2]=40 [L3]=80 )  NX2=( [L1]=8 [L2]=16 [L3]=32 )  NY=( [L1]=10 [L2]=20 [L3]=40 )
ENDTIME=0.05; DELTAT=1e-4
SPENT_CORE_MIN=0
TOTAL_WALL=0
for L in L1 L2 L3; do
  OUT="$RUN_ROOT/$L"
  [ -e "$OUT/0" -o -n "$(ls -d $OUT/[1-9]* 2>/dev/null)" ] && { echo "ABORT age guard: $OUT already has 0/ or a time dir"; exit 1; }
  # --- CAP ENFORCEMENT (CLAUDE.md rule 12): running-total drawdown, refuse at zero
  REMAIN=$(python3 -c "print(max(0.0, $CAP_CORE_MIN - $SPENT_CORE_MIN))") || { echo "ABORT: cannot compute remaining budget"; exit 1; }
  TIMEOUT_S=$(python3 -c "print(int($REMAIN * 60 / $RANKS))") || { echo "ABORT: cannot compute the timeout"; exit 1; }
  [ "$TIMEOUT_S" -gt 0 ] || { echo "ABORT: BUDGET EXHAUSTED before $L (spent $SPENT_CORE_MIN of $CAP_CORE_MIN core-min). An overrun STOPS the run; it does not get a new budget (CLAUDE.md rule 12)."; exit 1; }
  echo "--- $L  timeout=${TIMEOUT_S}s (remaining ${REMAIN} core-min of ${CAP_CORE_MIN})"
  mkdir -p "$OUT" || { echo ABORT mkdir; exit 1; }
  cp -r "$CASE_DIR"/{0,constant,system} "$OUT"/ || { echo ABORT copy; exit 1; }
  sed -e "s/__NX1__/${NX1[$L]}/g" -e "s/__NX2__/${NX2[$L]}/g" -e "s/__NY__/${NY[$L]}/g" \
      "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo ABORT sed bmd; exit 1; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" -e "s/__DELTAT__/$DELTAT/g" \
      "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo ABORT sed cd; exit 1; }
  T0=$(date +%s)
  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 && setFields > log.setFields 2>&1 \
      && touch 0/T && timeout "$TIMEOUT_S" laplacianFoam > log.laplacianFoam 2>&1 \
      && postProcess -func "patchAverage(name=rightWall,T)" -latestTime > log.pp_cool 2>&1 \
      && postProcess -func "patchAverage(name=leftWall,T)"  -latestTime > log.pp_adiab 2>&1 )
  RC=$?
  T1=$(date +%s); WALL=$((T1 - T0))
  CORE_MIN=$(python3 -c "print($WALL * $RANKS / 60.0)")
  SPENT_CORE_MIN=$(python3 -c "print($SPENT_CORE_MIN + $CORE_MIN)")
  TOTAL_WALL=$((TOTAL_WALL + WALL))
  printf 'rc=%d\nlevel=%s\nwall_s=%d\nranks=%d\ncore_min=%s\ntimeout_s=%d\n' \
    "$RC" "$L" "$WALL" "$RANKS" "$CORE_MIN" "$TIMEOUT_S" > "$OUT/RUN_RC.txt" \
    || { echo "ABORT: could not write RUN_RC.txt for $L"; exit 1; }
  [ "$RC" -eq 0 ] || { echo "ABORT solve $L exited rc=$RC after ${WALL}s (timeout ${TIMEOUT_S}s). A non-zero rc is a FINDING, not a retry."; exit 1; }
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (spent ${SPENT_CORE_MIN}/${CAP_CORE_MIN})"
done
printf 'total_wall_s=%d\nranks=%d\ntotal_core_min=%s\ncap_core_min=%s\ncost_basis=owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md sec.5)\n' \
  "$TOTAL_WALL" "$RANKS" "$SPENT_CORE_MIN" "$CAP_CORE_MIN" > "$RUN_ROOT/COST.txt" \
  || { echo "ABORT: could not write COST.txt"; exit 1; }
echo "VMFL059 all levels complete (${SPENT_CORE_MIN}/${CAP_CORE_MIN} core-min) -> grade with grade_vmfl059.py --run-root $RUN_ROOT"
