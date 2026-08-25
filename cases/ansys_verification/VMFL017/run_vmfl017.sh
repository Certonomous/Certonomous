#!/usr/bin/env bash
# VMFL017 graded-run driver -- Transonic Flow over an RAE 2822 Airfoil (manual p.69).
# Solver rhoSimpleFoam / kOmegaSST (OpenFOAM v2606), steady, 2D C-mesh.
#
# NO `set -u`. CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606 (sourcing etc/bashrc
# dereferences WM_PROJECT_DIR at bashrc line 184 before assigning it; MEASURED rc 127).
# `set -e` also does NOT gate at a Bash tool top level and `( set -e; ... )` fails
# silently, so EVERY check gates EXPLICITLY with || { echo ABORT...; exit 1; }.
#
# COST (CLAUDE.md rule 12): core_minutes = wall_s*RANKS/60. CAPS ARE PER LEVEL, NOT a
# shared drawdown -- supervisor's anti-starvation directive 2026-08-25: a shared budget
# let one slow level starve a later one into a FALSE failure (VMFL003_M2 arm C). Each
# level here has an INDEPENDENT runaway cap, and each records its remaining-at-launch.
# timeout_s = cap_core_min*60/RANKS.  An overrun STOPS that level; it does not borrow.
RANKS=1
declare -A CAP=( [L1]=90 [L2]=300 [L3]=900 )   # per-level runaway guards (core-min), frozen prereg sec.12
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmfl017.sh <run_root> [L1 L2 L3]}"
shift || true
LEVELS_TO_RUN="${*:-L1 L2 L3}"
[ -n "${VMFL_SMOKE:-}" ] && LEVELS_TO_RUN="L1"   # smoke hook (Amendment 3 item 6): L1 only, short iters
# --- LAUNCH-TIME FREEZE CHECK (rule 2 / template Amendment 2) -----------------
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repo"; exit 1; }
PREREG_REL="cases/ansys_verification/VMFL017/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL017/grade_vmfl017.py"
git -C "$REPO" cat-file -e "HEAD:$PREREG_REL" 2>/dev/null || { echo "ABORT: $PREREG_REL not committed at HEAD -- the freeze is the evidence"; exit 1; }
git -C "$REPO" cat-file -e "HEAD:$GRADER_REL" 2>/dev/null || { echo "ABORT: $GRADER_REL not committed at HEAD"; exit 1; }
PREREG_HEAD="$(git -C "$REPO" rev-parse "HEAD:$PREREG_REL")" || { echo "ABORT: cannot resolve HEAD:$PREREG_REL"; exit 1; }
GRADER_HEAD="$(git -C "$REPO" rev-parse "HEAD:$GRADER_REL")" || { echo "ABORT: cannot resolve HEAD:$GRADER_REL"; exit 1; }
PREREG_DISK="$(git -C "$REPO" hash-object "$REPO/$PREREG_REL")" || { echo "ABORT: cannot hash $PREREG_REL on disk"; exit 1; }
GRADER_DISK="$(git -C "$REPO" hash-object "$REPO/$GRADER_REL")" || { echo "ABORT: cannot hash $GRADER_REL on disk"; exit 1; }
[ "$PREREG_DISK" = "$PREREG_HEAD" ] || { echo "ABORT: $PREREG_REL disk ($PREREG_DISK) != HEAD ($PREREG_HEAD)"; exit 1; }
[ "$GRADER_DISK" = "$GRADER_HEAD" ] || { echo "ABORT: $GRADER_REL disk ($GRADER_DISK) != HEAD ($GRADER_HEAD)"; exit 1; }
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
{ echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "prereg = $PREREG_REL"; echo "prereg_sha_head = $PREREG_HEAD"; echo "prereg_sha_disk = $PREREG_DISK"
  echo "comparator = $GRADER_REL"; echo "comparator_sha_head = $GRADER_HEAD"; echo "comparator_sha_disk = $GRADER_DISK"
  echo "levels = $LEVELS_TO_RUN"; echo "caps_core_min = L1=${CAP[L1]} L2=${CAP[L2]} L3=${CAP[L3]} (per-level, NOT shared)"
} > "$RUN_ROOT/LAUNCH_RECORD.txt" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 1; }
echo "  freeze OK: prereg $PREREG_HEAD ; comparator $GRADER_HEAD"
# -----------------------------------------------------------------------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: no OpenFOAM"; exit 1; }
command -v rhoSimpleFoam >/dev/null || { echo "ABORT: rhoSimpleFoam not on PATH"; exit 1; }
for L in $LEVELS_TO_RUN; do
  OUT="$RUN_ROOT/$L"
  [ -e "$OUT/0" -o -n "$(ls -d $OUT/[1-9]* 2>/dev/null)" ] && { echo "ABORT age guard: $OUT already has 0/ or a time dir"; exit 1; }
  CAPL="${CAP[$L]}"; [ -n "$CAPL" ] || { echo "ABORT: no cap for level $L"; exit 1; }
  TIMEOUT_S=$(python3 -c "print(int($CAPL*60/$RANKS))") || { echo "ABORT: timeout calc"; exit 1; }
  echo "--- $L  per-level cap ${CAPL} core-min  timeout=${TIMEOUT_S}s"
  mkdir -p "$OUT" || { echo "ABORT mkdir $OUT"; exit 1; }
  cp -r "$CASE_DIR"/{0,constant,system} "$OUT"/ || { echo "ABORT copy case"; exit 1; }
  cp "$OUT/system/blockMeshDict.$L" "$OUT/system/blockMeshDict" || { echo "ABORT: no blockMeshDict.$L"; exit 1; }
  [ -n "${VMFL_SMOKE:-}" ] && sed -i -e 's/endTime         6000;/endTime         200;/' -e 's/writeInterval   6000;/writeInterval   200;/' "$OUT/system/controlDict"
  # remaining-at-launch record (supervisor directive): per-level, so remaining == cap here
  printf 'level=%s\nremaining_core_min_at_launch=%s\ncap_core_min=%s\nranks=%d\ntimeout_s=%d\nnote=per-level independent cap (no shared drawdown)\n' \
    "$L" "$CAPL" "$CAPL" "$RANKS" "$TIMEOUT_S" > "$OUT/RUN_RC.txt" || { echo "ABORT: RUN_RC.txt preamble"; exit 1; }
  T0=$(date +%s)
  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 && checkMesh > log.checkMesh 2>&1 \
      && touch 0/U \
      && timeout "$TIMEOUT_S" rhoSimpleFoam > log.rhoSimpleFoam 2>&1 )
  RC=$?
  T1=$(date +%s); WALL=$((T1-T0))
  CORE_MIN=$(python3 -c "print($WALL*$RANKS/60.0)")
  printf 'level=%s\nrc=%d\nwall_s=%d\nranks=%d\ncore_min=%s\ntimeout_s=%d\ncap_core_min=%s\nremaining_core_min_at_launch=%s\nprereg_blob=%s\nutc=%s\n' \
    "$L" "$RC" "$WALL" "$RANKS" "$CORE_MIN" "$TIMEOUT_S" "$CAPL" "$CAPL" "$PREREG_HEAD" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUT/RUN_RC.txt" || { echo "ABORT: RUN_RC.txt"; exit 1; }
  [ "$RC" -eq 0 ] || { echo "ABORT solve $L rc=$RC after ${WALL}s (cap ${CAPL} core-min). A non-zero rc is a FINDING, not a retry. If rc=124 the level hit its per-level cap -- report to supervisor, do NOT shrink endTime."; exit 1; }
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (cap ${CAPL})"
done
echo "VMFL017 levels [$LEVELS_TO_RUN] complete -> grade: grade_vmfl017.py --run-root $RUN_ROOT"
