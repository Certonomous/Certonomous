#!/usr/bin/env bash
# VMFL022-R2 launcher -- Cavitation over a sharp-edged orifice, Case B (low P1).
# Builds the regime-consistent spatial Roache family (orifice-radial N2R =
# 24/48/96, ratio 2 -- the base 12 level is EXCLUDED a-priori because it runs
# single-phase; see PREREGISTRATION.md) and runs interPhaseChangeFoam to a
# statistically-steady discharge on each, SEQUENTIALLY, inside ONE detached
# orchestrator (setsid+nohup) so the family survives this lane being stopped.
# It does NOT grade; grading is grade_vmfl022_r2.py, frozen separately and cited
# by sha in PREREGISTRATION.md.
#
# NO `set -u` ANYWHERE: OpenFOAM v2606 etc/bashrc dereferences WM_PROJECT_DIR
# before assigning it -- with set -u that is rc 127 at source time (measured).
# Every check therefore gates with an EXPLICIT `|| { echo ABORT..; exit 1; }`.
#
# LAUNCHER ARTIFACTS (all present):
#  1. launch-time freeze verification of the pre-registration AND the comparator
#     against HEAD (rule 2), each `|| abort`;
#  2. cap enforcement in the executable path: per-level timeout_s =
#     remaining_core_min*60/RANKS with running core-minute accounting drawing a
#     total budget down and REFUSING (rc 124/137) at zero (rule 12);
#  3. no set -u, reason named above;
#  4. planted-zero control -- fires in grade_vmfl022_r2.py (rule 3, L-487 subset);
#  5. mesh birth certificate -- blockMesh+checkMesh per level, recorded;
#  6. RUN_RC captured INSIDE the detached wrapper (setsid parent returns 0 for
#     every outcome -- MEMORY setsid-parent trap), age-guard marker 0/U touched
#     as the LAST thing before the solver (rule 4);
#  7. a --smoke path that exercises this launcher on a tiny endTime, scratch root.
#
# NB: This launcher only BUILDS + LAUNCHES. It performs NO graded launch on its
# own -- a graded run is gated by the supervisor/Sanaa (LAUNCH HELD, rule 9).
#
# Usage:
#   run_vmfl022_r2.sh            # freeze-checked; build + launch the graded family
#   run_vmfl022_r2.sh --smoke    # exercise the launcher machinery, scratch root

set -o pipefail

SMOKE=0
[ "${1:-}" = "--smoke" ] && SMOKE=1

REPO="/home/ubuntu/Certonomous"
PREREG="cases/ansys_verification/VMFL022-R2/PREREGISTRATION.md"
COMPARATOR="cases/ansys_verification/VMFL022-R2/grade_vmfl022_r2.py"
CASE_SRC="${REPO}/cases/ansys_verification/VMFL022-R2/case"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
RANKS=1                       # serial: keeps the core-minute cost measurement clean

if [ "$SMOKE" -eq 1 ]; then
  RUN_ROOT="/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/vmfl022r2_smoke_run"
  LEVELS="L1:24:20:32:80"      # L1 only, tiny endTime
  CAP_CORE_MIN=6
  ENDTIME_OVERRIDE="0.002"
  rm -rf "$RUN_ROOT"
else
  RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL022-R2"
  # name:N2R:N1R:NX1:NX2 -- ratio 2 in ALL directions per level (base's own
  # uniform meshing, shifted up one rung + one new finest level).
  LEVELS="L1:24:20:32:80 L2:48:40:64:160 L3:96:80:128:320"
  CAP_CORE_MIN=300           # RUNAWAY GUARD; estimate ~120 core-min total
                             # (L1~1, L2~13, L3~100; reported-by-owner, see PREREG).
  ENDTIME_OVERRIDE=""
fi

abort() { echo "ABORT: $*" >&2; exit 1; }
refuse() { echo "REFUSE: $*" >&2; exit 2; }

cd "$REPO" || abort "repository not found at $REPO"

# --- ARTIFACT 1: launch-time freeze verification against HEAD (rule 2) --------
git cat-file -e "HEAD:${PREREG}" 2>/dev/null || abort "pre-registration not committed at HEAD (rule 2)"
git cat-file -e "HEAD:${COMPARATOR}" 2>/dev/null || abort "comparator not committed at HEAD (rule 2)"
PREREG_HEAD=$(git rev-parse "HEAD:${PREREG}") || abort "cannot resolve HEAD blob for prereg"
COMP_HEAD=$(git rev-parse "HEAD:${COMPARATOR}") || abort "cannot resolve HEAD blob for comparator"
PREREG_DISK=$(git hash-object "${PREREG}") || abort "cannot hash prereg on disk"
COMP_DISK=$(git hash-object "${COMPARATOR}") || abort "cannot hash comparator on disk"
[ "$PREREG_HEAD" = "$PREREG_DISK" ] || abort "prereg on disk ($PREREG_DISK) != HEAD ($PREREG_HEAD) -- freeze drifted"
[ "$COMP_HEAD" = "$COMP_DISK" ] || abort "comparator on disk ($COMP_DISK) != HEAD ($COMP_HEAD) -- freeze drifted"
echo "freeze verified: prereg=${PREREG_HEAD} comparator=${COMP_HEAD}"

# --- source OpenFOAM (no set -u in scope) ------------------------------------
source "$FOAM_BASHRC" || abort "cannot source $FOAM_BASHRC"
command -v interPhaseChangeFoam >/dev/null || abort "interPhaseChangeFoam not on PATH"
command -v blockMesh >/dev/null || abort "blockMesh not on PATH"

# --- refuse if any level dir pre-exists (rule 4 age guard) -------------------
for spec in $LEVELS; do
  name="${spec%%:*}"
  [ -e "${RUN_ROOT}/${name}" ] && refuse "${RUN_ROOT}/${name} already exists -- never run into an existing case"
done
mkdir -p "$RUN_ROOT" || abort "cannot create $RUN_ROOT"

MESH_BIRTH="${RUN_ROOT}/MESH_BIRTH.txt"
: > "$MESH_BIRTH"

# --- ARTIFACT 5: build all meshes first, birth-certify each ------------------
for spec in $LEVELS; do
  IFS=: read -r name N2R N1R NX1 NX2 <<< "$spec"
  if [ -z "$NX2" ]; then NX2="$NX1"; fi
  d="${RUN_ROOT}/${name}"
  echo "=== building ${name}: N2R=${N2R} N1R=${N1R} NX1=${NX1} NX2=${NX2} ==="
  mkdir -p "$d" || abort "cannot create $d"
  cp -r "${CASE_SRC}/0.orig" "$d/0" || abort "0.orig copy failed"
  cp -r "${CASE_SRC}/constant" "${CASE_SRC}/system" "$d/" || abort "case copy failed"
  sed -e "s/__NX1__/${NX1}/g" -e "s/__NX2__/${NX2}/g" -e "s/__N2R__/${N2R}/g" \
      -e "s/__N1R__/${N1R}/g" -e "s/__G1R__/3/g" -e "s/__GX2__/4/g" \
      "${CASE_SRC}/system/blockMeshDict.template" > "$d/system/blockMeshDict" || abort "blockMeshDict subst failed"
  rm -f "$d/system/blockMeshDict.template"
  grep -q "__N" "$d/system/blockMeshDict" && abort "unsubstituted mesh placeholder in ${name}"
  if [ -n "$ENDTIME_OVERRIDE" ]; then
    sed -i "s/^endTime .*/endTime         ${ENDTIME_OVERRIDE};/" "$d/system/controlDict" || abort "endTime override failed"
  fi
  ( cd "$d" && blockMesh > log.blockMesh 2>&1 ); rc=$?
  [ $rc -eq 0 ] || { tail -5 "$d/log.blockMesh" >&2; abort "${name}: blockMesh rc=${rc}"; }
  ( cd "$d" && checkMesh > log.checkMesh 2>&1 )
  cells=$(grep -m1 -E "^\s*cells:" "$d/log.checkMesh" | grep -oE "[0-9]+" | head -1)
  echo "level=${name} cells=${cells} blockMesh=ok checkMesh_OK=$(grep -c 'Mesh OK' "$d/log.checkMesh") utc=$(date -u +%FT%TZ)" | tee -a "$MESH_BIRTH"
done
echo "mesh birth certificate: $MESH_BIRTH"

# --- ARTIFACT 2/6: detached orchestrator, sequential, budget draw-down -------
: > "${RUN_ROOT}/LAUNCH_RECORD.txt"
printf "case=VMFL022-R2\nprereg_blob=%s\ncomparator_blob=%s\ncap_core_min=%s\nranks=%s\nutc=%s\nlevels=%s\nsmoke=%s\n" \
  "$PREREG_HEAD" "$COMP_HEAD" "$CAP_CORE_MIN" "$RANKS" "$(date -u +%FT%TZ)" "$LEVELS" "$SMOKE" >> "${RUN_ROOT}/LAUNCH_RECORD.txt"

setsid nohup bash -c '
  RUN_ROOT="'"$RUN_ROOT"'"; LEVELS="'"$LEVELS"'"; RANKS='"$RANKS"'
  CAP="'"$CAP_CORE_MIN"'"; PREREG_HEAD="'"$PREREG_HEAD"'"
  remaining=$CAP
  echo "orchestrator start utc=$(date -u +%FT%TZ) budget_core_min=$remaining" >> "$RUN_ROOT/ORCH.log"
  for spec in $LEVELS; do
    name="${spec%%:*}"
    d="$RUN_ROOT/$name"
    # ARTIFACT 2: per-level timeout from REMAINING budget (rule 12)
    timeout_s=$(awk "BEGIN{printf \"%d\", ($remaining*60)/$RANKS}")
    if [ "$timeout_s" -le 0 ]; then
      echo "level=$name BUDGET EXHAUSTED remaining=$remaining -- refusing to launch" >> "$RUN_ROOT/ORCH.log"
      printf "level=%s\nrc=137\nnote=budget_exhausted\nremaining_core_min=%s\n" "$name" "$remaining" > "$d/RUN_RC.txt"
      touch "$d/DONE.flag"
      continue
    fi
    touch "$d/0/U"   # AGE-GUARD MARKER (rule 4), last thing before the solver
    t0=$(date +%s)
    ( cd "$d" && timeout ${timeout_s} interPhaseChangeFoam > log.interPhaseChangeFoam 2>&1 )
    rc=$?             # ARTIFACT 6: rc captured INSIDE the detached wrapper
    t1=$(date +%s); wall=$(( t1 - t0 ))
    cm=$(awk "BEGIN{printf \"%.4f\", $wall*$RANKS/60.0}")
    remaining=$(awk "BEGIN{printf \"%.4f\", $remaining - $cm}")
    printf "level=%s\nrc=%d\nwall_s=%d\nranks=%d\ncore_min=%s\ntimeout_s=%d\nremaining_core_min=%s\nprereg_blob=%s\nutc=%s\n" \
      "$name" "$rc" "$wall" "$RANKS" "$cm" "$timeout_s" "$remaining" "$PREREG_HEAD" "$(date -u +%FT%TZ)" > "$d/RUN_RC.txt"
    touch "$d/DONE.flag"
    echo "level=$name rc=$rc wall_s=$wall core_min=$cm remaining=$remaining utc=$(date -u +%FT%TZ)" >> "$RUN_ROOT/ORCH.log"
  done
  echo "orchestrator done utc=$(date -u +%FT%TZ) remaining_core_min=$remaining" >> "$RUN_ROOT/ORCH.log"
  touch "$RUN_ROOT/FAMILY_DONE.flag"
' > /dev/null 2>&1 &

ORCH_PID=$!
echo "orchestrator launched detached pid=${ORCH_PID} run_root=${RUN_ROOT}"
echo "level dirs will each gain RUN_RC.txt + DONE.flag; family gains FAMILY_DONE.flag"
if [ "$SMOKE" -eq 1 ]; then
  echo "SMOKE: waiting for L1 to finish (<= $CAP_CORE_MIN core-min)..."
  for i in $(seq 1 120); do
    [ -f "${RUN_ROOT}/FAMILY_DONE.flag" ] && break
    sleep 5
  done
  echo "=== SMOKE RUN_RC ==="; cat "${RUN_ROOT}/L1/RUN_RC.txt" 2>/dev/null || echo "(no RUN_RC yet)"
  echo "=== SMOKE mesh birth ==="; cat "$MESH_BIRTH"
  rc=$(grep -oE '^rc=[0-9-]+' "${RUN_ROOT}/L1/RUN_RC.txt" 2>/dev/null | head -1)
  echo "SMOKE result: $rc (expect rc=0)"
fi
echo "VMFL022-R2 launcher done. Grade when FAMILY_DONE.flag exists:"
echo "  python3 cases/ansys_verification/VMFL022-R2/grade_vmfl022_r2.py"
