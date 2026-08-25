#!/usr/bin/env bash
# VMFL021 launcher -- Cavitation over a sharp-edged orifice, Case A (high P1).
# Builds the three-level spatial Roache family (orifice-radial N2R = 12/24/48,
# ratio 2) and runs interPhaseChangeFoam to a statistically-steady discharge on
# each, SEQUENTIALLY, inside ONE detached orchestrator (setsid+nohup) so the
# family survives this lane being stopped.  It does NOT grade; grading is
# grade_vmfl021.py, frozen separately and cited by sha in PREREGISTRATION.md.
#
# NO `set -u` ANYWHERE: OpenFOAM v2606 etc/bashrc dereferences WM_PROJECT_DIR
# (bashrc line 184) before assigning it -- with set -u that is rc 127 at source
# time (PREREG_TEMPLATE Amendment 3, measured).  Every check therefore gates
# with an EXPLICIT `|| { echo ABORT..; exit 1; }` -- `set -e` does not gate at a
# Bash tool top level, nor inside ( set -e; .. ).
#
# REQUIRED LAUNCHER ARTIFACTS (PREREG_TEMPLATE Amendment 3), all present here:
#  1. launch-time freeze verification of the pre-registration AND the comparator
#     against HEAD, each `|| { echo ABORT; exit 1; }`;
#  2. cap enforcement in the executable path: per-level timeout_s =
#     remaining_core_min*60/RANKS with running core-minute accounting drawing a
#     total budget down and REFUSING at zero;
#  3. no set -u, reason named above;
#  4. planted-zero control -- fires in grade_vmfl021.py (rule 3);
#  5. mesh birth certificate -- blockMesh+checkMesh per level, recorded;
#  6. a smoke test that EXERCISES THIS LAUNCHER ITSELF: `run_vmfl021.sh --smoke`
#     runs the whole path (freeze-check, mesh build, orchestrator, RUN_RC) on a
#     tiny endTime in a scratch run-root -- not the solver in a bypass env.
#
# Usage:
#   run_vmfl021.sh            # freeze-checked; build + launch the graded family
#   run_vmfl021.sh --smoke    # exercise the launcher machinery, scratch root

set -o pipefail

SMOKE=0
[ "${1:-}" = "--smoke" ] && SMOKE=1

REPO="/home/ubuntu/Certonomous"
PREREG="cases/ansys_verification/VMFL021/R2/PREREGISTRATION.md"
COMPARATOR="cases/ansys_verification/VMFL021/R2/grade_vmfl021_r2.py"
CASE_SRC="${REPO}/cases/ansys_verification/VMFL021/R2/case"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
RANKS=1                       # serial: keeps the core-minute cost measurement clean

if [ "$SMOKE" -eq 1 ]; then
  RUN_ROOT="/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/vmfl021_r2_smoke_run"
  LEVELS="L1:12:10:40"        # L1 only
  CAP_CORE_MIN=6
  ENDTIME_OVERRIDE="0.0003"
  WRITEINT_OVERRIDE="0.0001"  # keeps endTime an EXACT multiple: 0.0003/0.0001 = 3
  rm -rf "$RUN_ROOT"
else
  RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL021/R2"
  # name:N2R:N1R:NX pattern -- NX1 scales with N2R too (ratio 2 all directions)
  LEVELS="L1:12:10:16:40 L2:24:20:32:80 L3:48:40:64:160"
  CAP_CORE_MIN=180           # runaway guard; estimate ~40 core-min (see PREREG line 12)
  ENDTIME_OVERRIDE=""
  WRITEINT_OVERRIDE=""       # frozen controlDict already writes AT endTime (adjustableRunTime, wi=0.0005, 6x)
fi

abort() { echo "ABORT: $*" >&2; exit 1; }
refuse() { echo "REFUSE: $*" >&2; exit 2; }

cd "$REPO" || abort "repository not found at $REPO"

# --- ARTIFACT 1: launch-time freeze verification against HEAD ----------------
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
  # smoke L1 spec has 4 fields (name:N2R:N1R:NX) -> map: NX1==NX2==that NX
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
  if [ -n "$WRITEINT_OVERRIDE" ]; then
    sed -i "s/^writeInterval .*/writeInterval   ${WRITEINT_OVERRIDE};/" "$d/system/controlDict" || abort "writeInterval override failed"
  fi
  # --- ARTIFACT 7 (VMFL021-R2 NEW, required): endTime an EXACT integer multiple
  #     of writeInterval under a runTime write control, ASSERTED before starting.
  #     Attempt-1 died here silently: writeInterval 0.01 > endTime 0.003 under
  #     `adjustable` wrote NO field dir at endTime, so nothing was gradeable and
  #     rule 4 could not certify a rc=0 run.  Amendment-3's six checks all passed
  #     yet the run produced nothing -- this is the new guard that closes it.
  et=$(grep -E "^endTime " "$d/system/controlDict" | awk '{print $2}' | tr -d ';')
  wi=$(grep -E "^writeInterval " "$d/system/controlDict" | awk '{print $2}' | tr -d ';')
  wc=$(grep -E "^writeControl " "$d/system/controlDict" | awk '{print $2}' | tr -d ';')
  { [ -n "$et" ] && [ -n "$wi" ] && [ -n "$wc" ]; } || abort "${name}: cannot read endTime/writeInterval/writeControl from controlDict"
  { [ "$wc" = "adjustableRunTime" ] || [ "$wc" = "runTime" ]; } || abort "${name}: writeControl=${wc} is not a runTime form -- a write AT endTime is NOT guaranteed"
  mult_ok=$(awk -v e="$et" -v w="$wi" 'BEGIN{ if(w<=0){print 0; exit} r=e/w; k=int(r+0.5); d=r-k; if(d<0)d=-d; print (d<1e-6)?1:0 }')
  [ "$mult_ok" = "1" ] || abort "${name}: endTime (${et}) is NOT an exact integer multiple of writeInterval (${wi}) -- no field dir written AT endTime (attempt-1 defect)"
  echo "level=${name} endTime=${et} writeInterval=${wi} writeControl=${wc} multiple=OK" >> "$MESH_BIRTH"
  ( cd "$d" && blockMesh > log.blockMesh 2>&1 ); rc=$?
  [ $rc -eq 0 ] || { cat "$d/log.blockMesh" | tail -5 >&2; abort "${name}: blockMesh rc=${rc}"; }
  ( cd "$d" && checkMesh > log.checkMesh 2>&1 )
  cells=$(grep -m1 -E "^\s*cells:" "$d/log.checkMesh" | grep -oE "[0-9]+" | head -1)
  echo "level=${name} cells=${cells} blockMesh=ok checkMesh=$(grep -c 'Mesh OK' "$d/log.checkMesh") utc=$(date -u +%FT%TZ)" | tee -a "$MESH_BIRTH"
done
echo "mesh birth certificate: $MESH_BIRTH"

# --- ARTIFACT 2: detached orchestrator, sequential, budget draw-down ---------
: > "${RUN_ROOT}/LAUNCH_RECORD.txt"
printf "case=VMFL021-R2\nprereg_blob=%s\ncomparator_blob=%s\ncap_core_min=%s\nranks=%s\nutc=%s\nlevels=%s\nsmoke=%s\n" \
  "$PREREG_HEAD" "$COMP_HEAD" "$CAP_CORE_MIN" "$RANKS" "$(date -u +%FT%TZ)" "$LEVELS" "$SMOKE" >> "${RUN_ROOT}/LAUNCH_RECORD.txt"

# effective endTime (override if set, else the frozen controlDict's value): the
# orchestrator asserts a field dir exists AT this time before calling a level done.
ENDTIME_EFF="${ENDTIME_OVERRIDE}"
if [ -z "$ENDTIME_EFF" ]; then
  ENDTIME_EFF=$(grep -E "^endTime " "$CASE_SRC/system/controlDict" | awk '{print $2}' | tr -d ';')
fi
[ -n "$ENDTIME_EFF" ] || abort "cannot resolve effective endTime for the completeness check"
echo "endtime_eff=${ENDTIME_EFF}" >> "${RUN_ROOT}/LAUNCH_RECORD.txt"

setsid nohup bash -c '
  RUN_ROOT="'"$RUN_ROOT"'"; LEVELS="'"$LEVELS"'"; RANKS='"$RANKS"'
  CAP="'"$CAP_CORE_MIN"'"; PREREG_HEAD="'"$PREREG_HEAD"'"; ENDTIME_EFF="'"$ENDTIME_EFF"'"
  remaining=$CAP
  echo "orchestrator start utc=$(date -u +%FT%TZ) budget_core_min=$remaining" >> "$RUN_ROOT/ORCH.log"
  for spec in $LEVELS; do
    name="${spec%%:*}"
    d="$RUN_ROOT/$name"
    # ARTIFACT 2: per-level timeout from REMAINING budget
    timeout_s=$(awk "BEGIN{printf \"%d\", ($remaining*60)/$RANKS}")
    if [ "$timeout_s" -le 0 ]; then
      echo "level=$name BUDGET EXHAUSTED remaining=$remaining -- refusing to launch" >> "$RUN_ROOT/ORCH.log"
      printf "level=%s\nrc=137\nnote=budget_exhausted\nremaining_core_min=%s\n" "$name" "$remaining" > "$d/RUN_RC.txt"
      touch "$d/DONE.flag"
      continue
    fi
    touch "$d/0/U"   # AGE-GUARD MARKER, last thing before the solver
    t0=$(date +%s)
    ( cd "$d" && timeout ${timeout_s} interPhaseChangeFoam > log.interPhaseChangeFoam 2>&1 )
    rc=$?
    t1=$(date +%s); wall=$(( t1 - t0 ))
    cm=$(awk "BEGIN{printf \"%.4f\", $wall*$RANKS/60.0}")
    remaining=$(awk "BEGIN{printf \"%.4f\", $remaining - $cm}")
    # ARTIFACT 8 (VMFL021-R2 NEW, required): a field dir MUST exist AT endTime
    # before this level is called complete.  Belt-and-suspenders on ARTIFACT 7:
    # 7 asserts the controlDict CAN write at endTime; 8 confirms it DID.  Records
    # endtime_ok into RUN_RC so the state is visible at run time, not only at grade.
    end_dir=""
    for cand in "$d"/*/; do
      b=$(basename "$cand")
      case "$b" in ""|*[!0-9.]* ) continue;; esac
      same=$(awk -v a="$b" -v e="$ENDTIME_EFF" "BEGIN{dd=a-e; if(dd<0)dd=-dd; print (dd<1e-9)?1:0}")
      [ "$same" = "1" ] && { end_dir="$b"; break; }
    done
    if [ -n "$end_dir" ] && [ -f "$d/$end_dir/U" ]; then endtime_ok=1; else endtime_ok=0; fi
    if [ "$endtime_ok" = "0" ]; then
      echo "level=$name ENDTIME-FIELD-DIR MISSING (endTime=$ENDTIME_EFF) -- run wrote nothing gradeable AT endTime (attempt-1 defect class)" >> "$RUN_ROOT/ORCH.log"
    fi
    printf "level=%s\nrc=%d\nwall_s=%d\nranks=%d\ncore_min=%s\ntimeout_s=%d\nremaining_core_min=%s\nendtime_eff=%s\nendtime_field_dir=%s\nendtime_ok=%s\nprereg_blob=%s\nutc=%s\n" \
      "$name" "$rc" "$wall" "$RANKS" "$cm" "$timeout_s" "$remaining" "$ENDTIME_EFF" "${end_dir:-none}" "$endtime_ok" "$PREREG_HEAD" "$(date -u +%FT%TZ)" > "$d/RUN_RC.txt"
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
echo "VMFL021 launcher done. Grade when FAMILY_DONE.flag exists:"
echo "  python3 cases/ansys_verification/VMFL021/R2/grade_vmfl021_r2.py"
