#!/usr/bin/env bash
# ============================================================================
# run_vmflgpu005.sh -- VMFLGPU005 graded-run driver.
#
# Tall differentially-heated cavity (Betts & Bokhari 2000), manual p.235.
# CPU PARENT: VMFL052.  Object under verification: THE LAB'S GPU SOLVER PATH
# (OpenFOAM v2606 buoyantBoussinesqSimpleFoam + petsc4Foam + PETSc-CUDA, L4).
#
# RUNS ON THE GPU INSTANCE, never on the lab box.  SIX solves: three mesh levels
# of a ROACHE r=2 TRIPLE x two arms (GPU aijcusparse/cuda; forced-CPU aij/standard,
# which is limb A's discriminator AND limb B's baseline).
#
# IT GRADES NOTHING.  Grading is grade_vmflgpu005.py, frozen separately and cited
# by sha in PREREGISTRATION.md.
#
# HAZARDS, EACH MEASURED BY THIS LAB (inherited from VMFLGPU007's two amendments):
#  * NO `set -u`.  v2606 etc/bashrc dereferences WM_PROJECT_DIR before assigning.
#  * NO `set -e`.  It does not gate at a Bash tool's top level.  Every step gates
#    EXPLICITLY with a NAMED message (L-357: a non-zero exit alone is not evidence).
#  * THE FREEZE CHECK DERIVES ITS REPOSITORY FROM THIS SCRIPT'S OWN LOCATION, never
#    the environment (007 Amendment 1: a check against a caller-supplied REPO can
#    PASS while proving nothing about the tree that runs).
#  * THE CASE DIRECTORY IS COMPLETED BEFORE ANY OpenFOAM UTILITY RUNS (007
#    Amendment 2: every utility builds a Time object that reads system/controlDict
#    in its constructor, so blockMesh dies if the templates are not materialised).
#  * BOOKKEEPING NEVER VOIDS PHYSICS (L-342): after a solver completes a failed
#    bookkeeping write is a WARNING and the exit stays the solver's.
#
# EXECUTE this script (`bash run_vmflgpu005.sh <run_root>`); NEVER `source` it.
# ============================================================================
set -o pipefail   # wanted and safe. `set -e` / `set -u` deliberately NOT set.

CASE_ID="VMFLGPU005"
RANKS=1                         # serial; core-minutes = wall_s * RANKS / 60
CAP_GPU_H=6.0                   # FROZEN in PREREGISTRATION.md section 9 (runaway guard)
CAP_CPU_ARM_CORE_MIN=240        # FROZEN in PREREGISTRATION.md section 9

# name:NX:NY:H1:ENDTIME:CELLS  -- a ROACHE r=2 TRIPLE. NX,NY,H1 all scale by 2
# between levels (geometric similarity: the condition an observed order requires;
# verified pre-freeze, MESH_PREFREEZE_RECORD.md). CELLS = NX*NY (single block).
LEVELS="L1:48:140:6.0e-4:15000:6720 L2:96:280:3.0e-4:20000:26880 L3:192:560:1.5e-4:25000:107520"

GPU_MAT="aijcusparse"; GPU_VEC="cuda"
CPU_MAT="aij";         CPU_VEC="standard"
# -use_gpu_aware_mpi 0 shared by BOTH arms (Part-1 finding: this MPI is not
# GPU-aware; at one rank the device-to-device path it governs is never exercised,
# so it declines a PERFORMANCE feature, not a correctness one). The two arms
# therefore differ ONLY in mat_type/vec_type -- the whole basis of limb B.
SHARED_PETSC_OPTIONS="-use_gpu_aware_mpi 0"
GPU_OWN_PETSC_OPTIONS="-ksp_view -log_view -log_view_gpu_time"
CPU_OWN_PETSC_OPTIONS="-ksp_view -log_view"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_SRC="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmflgpu005.sh <run_root>}"
BUILD_ROOT="${BUILD_ROOT:-$HOME/gpu_build}"
REPO_ENV="${REPO-}"     # what the caller ASKED for: CHECKED at STEP 1, never obeyed
REPO=""                 # DERIVED at STEP 1 from SCRIPT_DIR. Empty here ON PURPOSE.
CASE_REL_DIR="cases/ansys_verification/VMFLGPU005"
PREREG_REL="$CASE_REL_DIR/PREREGISTRATION.md"
GRADER_REL="$CASE_REL_DIR/grade_vmflgpu005.py"
LAUNCHER_REL="$CASE_REL_DIR/run_vmflgpu005.sh"
FIELDCHK_REL="$CASE_REL_DIR/field_completeness.py"
MESHGEN_REL="$CASE_REL_DIR/resolve_blockmesh.py"

T_START=$(date +%s)
log()  { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ${CASE_ID}: $*"; }
warn_infra() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ${CASE_ID}: WARNING(INFRASTRUCTURE): $*"; }

log "=== START (run_root=$RUN_ROOT build_root=$BUILD_ROOT repo=DERIVED-AT-STEP-1 repo_env=${REPO_ENV:-<unset>}) ==="

# --- STEP 0  THE SMOKE GATE -- REFUSES AT ZERO COMPUTE (exit 2) --------------
STATUS_SMOKE="$BUILD_ROOT/STATUS.smoke"; MANIFEST="$BUILD_ROOT/TOOLCHAIN_MANIFEST.txt"; BUILD_ENV="$BUILD_ROOT/env.sh"
test -f "$STATUS_SMOKE" || { echo "REFUSE (exit 2): $STATUS_SMOKE absent. The GPU solver path has not been PROVEN on this instance, so nothing this script runs is evidence about it."; exit 2; }
grep -Eq '^[[:space:]]*smoke_rc[[:space:]]*=[[:space:]]*0([[:space:]]|$)' "$STATUS_SMOKE" || { echo "REFUSE (exit 2): $STATUS_SMOKE does not read smoke_rc=0. Contents:"; sed -e 's/^/    | /' "$STATUS_SMOKE"; exit 2; }
test -f "$MANIFEST" || { echo "REFUSE (exit 2): $MANIFEST absent. A GPU-path proof whose toolchain cannot be NAMED is not evidence about any particular toolchain."; exit 2; }
test -f "$BUILD_ENV" || { echo "REFUSE (exit 2): $BUILD_ENV absent. It carries THE MPI PIN this stack runs under (the DLAMI prepends AWS Open MPI, SHADOWING Ubuntu's that OpenFOAM+PETSc were compiled against, SAME SONAME)."; exit 2; }
log "SMOKE GATE PASSED: $STATUS_SMOKE reads smoke_rc=0, manifest and env present"

# --- STEP 0c  THE CAP MECHANISM IS DRIVEN BEFORE IT IS TRUSTED (L-339) -------
command -v timeout >/dev/null || { echo "REFUSE (exit 2): \`timeout\` not on PATH; the per-solve cap cannot be enforced in the executable path."; exit 2; }
timeout 10 bash -c 'exit 7'; TO_RC_PASS=$?
timeout 1  bash -c 'sleep 3'; TO_RC_KILL=$?
if [ "$TO_RC_PASS" != "7" ] || [ "$TO_RC_KILL" != "124" ]; then
  echo "REFUSE (exit 2): \`timeout\` does not behave as the cap requires -- child exit 7 came back $TO_RC_PASS (want 7), overrun came back $TO_RC_KILL (want 124)."; exit 2
fi
log "CAP MECHANISM DRIVEN: timeout passes rc 7 through and reports an overrun as 124"

# --- STEP 1  LAUNCH-TIME FREEZE CHECK -- PHYSICS-CRITICAL, REPO FROM SCRIPT ---
SCRIPT_DIR_P="$(cd "$SCRIPT_DIR" 2>/dev/null && pwd -P)" || { echo "ABORT (freeze a): cannot resolve SCRIPT_DIR=$SCRIPT_DIR"; exit 1; }
REPO_TOP="$(git -C "$SCRIPT_DIR_P" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT (freeze a): SCRIPT_DIR=$SCRIPT_DIR_P is NOT inside a git worktree; there is no HEAD to certify the frozen files. The repository is NEVER taken from the environment."; exit 1; }
test -n "$REPO_TOP" || { echo "ABORT (freeze a): empty toplevel at $SCRIPT_DIR_P"; exit 1; }
REPO="$(cd "$REPO_TOP" 2>/dev/null && pwd -P)" || { echo "ABORT (freeze a): cannot resolve derived toplevel $REPO_TOP"; exit 1; }
EXPECT_DIR="$(cd "$REPO/$CASE_REL_DIR" 2>/dev/null && pwd -P)" || { echo "ABORT (freeze b): derived repo $REPO has no $CASE_REL_DIR"; exit 1; }
[ "$SCRIPT_DIR_P" = "$EXPECT_DIR" ] || { echo "ABORT (freeze b): SCRIPT_DIR=$SCRIPT_DIR_P is NOT $REPO/$CASE_REL_DIR ($EXPECT_DIR). Case inputs and the certified blobs are IN DIFFERENT TREES."; exit 1; }
if [ -n "$REPO_ENV" ]; then
  REPO_ENV_P="$(cd "$REPO_ENV" 2>/dev/null && pwd -P)" || { echo "ABORT (freeze c): REPO=$REPO_ENV set in env but does not resolve"; exit 1; }
  [ "$REPO_ENV_P" = "$REPO" ] || { echo "ABORT (freeze c): REPO=$REPO_ENV ($REPO_ENV_P) is NOT the repo derived from this script's location ($REPO). The environment does not select the tree a freeze is proved against."; exit 1; }
fi
log "REPO DERIVED FROM SCRIPT_DIR: $REPO (env REPO ${REPO_ENV:-<unset>})"

FROZEN_PATHS="$PREREG_REL $GRADER_REL $LAUNCHER_REL $FIELDCHK_REL $MESHGEN_REL"
FROZEN_REPORT=""
for rel in $FROZEN_PATHS; do
  git -C "$REPO" cat-file -e "HEAD:$rel" 2>/dev/null || { echo "ABORT (freeze d): $rel is not committed at HEAD -- the freeze is the evidence"; exit 1; }
  hh="$(git -C "$REPO" rev-parse "HEAD:$rel")" || { echo "ABORT (freeze d): cannot resolve HEAD:$rel"; exit 1; }
  hd="$(git -C "$REPO" hash-object "$REPO/$rel")" || { echo "ABORT (freeze d): cannot hash $rel on disk"; exit 1; }
  [ "$hd" = "$hh" ] || { echo "ABORT (freeze d): $rel on disk ($hd) differs from HEAD ($hh). The bytes now executing are NOT the committed blob."; exit 1; }
  FROZEN_REPORT="$FROZEN_REPORT $rel=$hh"
done
HEAD_SHA="$(git -C "$REPO" rev-parse HEAD)" || { echo "ABORT: cannot resolve HEAD"; exit 1; }
log "FREEZE VERIFIED:$FROZEN_REPORT ; HEAD $HEAD_SHA"

mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
{ echo "case_id = $CASE_ID"; echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "head = $HEAD_SHA"
  echo "script_dir = $SCRIPT_DIR_P"; echo "repo_toplevel_derived = $REPO"; echo "repo_env_as_passed = ${REPO_ENV:-<unset>}"
  for kv in $FROZEN_REPORT; do echo "frozen_blob ${kv%%=*} = ${kv##*=}"; done
  echo "host = $(hostname)"
} > "$RUN_ROOT/LAUNCH_RECORD.txt" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 1; }

# --- STEP 2  ENVIRONMENT -- MPI pin BEFORE OpenFOAM bashrc ------------------
test -f "$BUILD_ROOT/OF_BASHRC" || { echo "ABORT: $BUILD_ROOT/OF_BASHRC absent -- build records the OpenFOAM bashrc it used; this script never guesses"; exit 1; }
OF_BASHRC="$(cat "$BUILD_ROOT/OF_BASHRC")" || { echo "ABORT: cannot read OF_BASHRC pointer"; exit 1; }
test -f "$OF_BASHRC" || { echo "ABORT: recorded OF_BASHRC ($OF_BASHRC) does not exist"; exit 1; }
. "$BUILD_ENV" || { echo "ABORT: cannot source $BUILD_ENV (the MPI pin)"; exit 1; }
. "$OF_BASHRC" || { echo "ABORT: cannot source $OF_BASHRC"; exit 1; }
command -v blockMesh >/dev/null || { echo "ABORT: blockMesh not on PATH after sourcing $OF_BASHRC"; exit 1; }
command -v buoyantBoussinesqSimpleFoam >/dev/null || { echo "ABORT: buoyantBoussinesqSimpleFoam not on PATH after sourcing $OF_BASHRC"; exit 1; }
log "ENVIRONMENT OK: $(command -v buoyantBoussinesqSimpleFoam)"

# --- STEP 3  refuse if ANY level dir of EITHER arm already exists (rule 4) ---
for spec in $LEVELS; do
  name="${spec%%:*}"
  for arm in gpu cpu; do d="$RUN_ROOT/$arm/$name"; [ -e "$d" ] && { echo "ABORT: $d already exists -- this script never runs into an existing case (rule 4 age guard)"; exit 1; }; done
done
log "no level directory of either arm pre-exists"

# --- STEP 4  THE SIX SOLVES -------------------------------------------------
CPU_ARM_CORE_MIN=0; FAILED=0
for spec in $LEVELS; do
  IFS=: read -r NAME NX NY H1 ETIME EXPECT_CELLS <<< "$spec"
  for arm in gpu cpu; do
    D="$RUN_ROOT/$arm/$NAME"
    mkdir -p "$D" || { echo "ABORT: cannot create $D"; exit 1; }
    cp -a "$CASE_SRC/." "$D/" || { echo "ABORT: cannot stage case inputs into $D"; exit 1; }

    # ---- COMPLETE THE CASE DIRECTORY BEFORE ANY OpenFOAM UTILITY (007 Amdt 2) --
    sed -e "s/__MATTYPE__/$([ "$arm" = gpu ] && echo "$GPU_MAT" || echo "$CPU_MAT")/g" \
        -e "s/__VECTYPE__/$([ "$arm" = gpu ] && echo "$GPU_VEC" || echo "$CPU_VEC")/g" \
        "$D/system/fvSolution.template" > "$D/system/fvSolution" || { echo "ABORT ($NAME/$arm): cannot materialise fvSolution"; exit 1; }
    rm -f "$D/system/fvSolution.template"
    sed -e "s/__ENDTIME__/$ETIME/g" "$D/system/controlDict.template" > "$D/system/controlDict" || { echo "ABORT ($NAME/$arm): cannot materialise controlDict"; exit 1; }
    rm -f "$D/system/controlDict.template"
    python3 "$REPO/$MESHGEN_REL" "$D/system/blockMeshDict.template" "$NX" "$NY" "$H1" "$D/system/blockMeshDict" || { echo "ABORT ($NAME/$arm): the frozen mesh generator REFUSED (its text above is the finding; a non-zero exit alone is not, L-357)."; exit 1; }
    rm -f "$D/system/blockMeshDict.template"

    ( cd "$D" && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT ($NAME/$arm): blockMesh failed; see $D/log.blockMesh"; exit 1; }
    ( cd "$D" && checkMesh > log.checkMesh 2>&1 ) || { echo "ABORT ($NAME/$arm): checkMesh failed; see $D/log.checkMesh"; exit 1; }
    grep -q '^Mesh OK' "$D/log.checkMesh" || { echo "ABORT ($NAME/$arm): checkMesh did not report 'Mesh OK'. A defect found now costs minutes; found at grade time it costs a GPU-hour and yields no verdict."; exit 1; }

    GOT_CELLS="$(grep -oP '^\s+cells:\s+\K[0-9]+' "$D/log.checkMesh" | head -1)"
    [ -n "$GOT_CELLS" ] || { echo "ABORT ($NAME/$arm): could not read a cell count from log.checkMesh"; exit 1; }
    [ "$GOT_CELLS" = "$EXPECT_CELLS" ] || { echo "ABORT ($NAME/$arm): BIRTH CERTIFICATE MISMATCH -- checkMesh reports $GOT_CELLS cells, the pre-freeze registered count is $EXPECT_CELLS. The mesh that would run is not the mesh registered."; exit 1; }
    log "$NAME/$arm BIRTH CERTIFICATE OK: $GOT_CELLS cells == registered $EXPECT_CELLS"

    python3 "$REPO/$FIELDCHK_REL" "$D" || { echo "ABORT ($NAME/$arm): FIELD COMPLETENESS refused (its named refusal above is the finding)."; exit 1; }

    touch "$D/0/T" || { echo "ABORT ($NAME/$arm): cannot touch the age-guard reference $D/0/T"; exit 1; }

    if [ "$arm" = gpu ]; then
      CAP_S=$(python3 -c "print(int($CAP_GPU_H*3600))")
      export PETSC_OPTIONS="$PETSC_OPTIONS_BASE $SHARED_PETSC_OPTIONS $GPU_OWN_PETSC_OPTIONS"
    else
      CAP_S=$(python3 -c "print(int($CAP_CPU_ARM_CORE_MIN*60/$RANKS))")
      export PETSC_OPTIONS="$PETSC_OPTIONS_BASE $SHARED_PETSC_OPTIONS $CPU_OWN_PETSC_OPTIONS"
    fi
    S0=$(date +%s)
    ( cd "$D" && timeout -k 30 "$CAP_S" buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam 2>&1 )
    RC=$?; S1=$(date +%s); WALL=$((S1-S0))
    CAP_FIRED=0; [ "$RC" = "124" ] && CAP_FIRED=1
    if [ "$CAP_FIRED" = "1" ]; then
      { echo "case_id = $CASE_ID"; echo "level = $NAME"; echo "arm = $arm"; echo "cap_s = $CAP_S"; echo "wall_s = $WALL"
        echo "note = THE CAP FIRED. rule 12: an overrun STOPS the run and does not get a new budget."; } > "$RUN_ROOT/CAP_EXCEEDED.txt" 2>/dev/null || warn_infra "could not write CAP_EXCEEDED.txt"
    fi
    CORE_MIN=$(python3 -c "print('%.4f' % ($WALL*$RANKS/60.0))")
    GPU_H=$(python3 -c "print('%.6f' % ($WALL/3600.0))")
    [ "$arm" = cpu ] && CPU_ARM_CORE_MIN=$(python3 -c "print($CPU_ARM_CORE_MIN+$CORE_MIN)")
    { echo "case_id = $CASE_ID"; echo "arm = $arm"; echo "level = $NAME"; echo "rc = $RC"; echo "cap_fired = $CAP_FIRED"; echo "cap_s = $CAP_S"
      echo "wall_s = $WALL"; echo "ranks = $RANKS"; echo "core_min = $CORE_MIN"; echo "gpu_h = $GPU_H"; echo "endtime = $ETIME"; echo "cells = $GOT_CELLS"
      echo "nx = $NX"; echo "ny = $NY"; echo "h1 = $H1"
      echo "mat_type = $([ "$arm" = gpu ] && echo "$GPU_MAT" || echo "$CPU_MAT")"; echo "vec_type = $([ "$arm" = gpu ] && echo "$GPU_VEC" || echo "$CPU_VEC")"
      echo "petsc_options = $PETSC_OPTIONS"; echo "utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$RUN_ROOT/RUN_RC.$NAME.$arm" || warn_infra "could not write RUN_RC.$NAME.$arm"
    echo "solve rc = $RC  arm = $arm  level = $NAME  wall_s = $WALL  cap_fired = $CAP_FIRED  utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RUN_ROOT/LAUNCH_RECORD.txt" || warn_infra "could not append to LAUNCH_RECORD.txt"
    log "$NAME/$arm rc=$RC wall_s=$WALL cap_fired=$CAP_FIRED"
    [ "$RC" != "0" ] && FAILED=1
  done
done

# --- STEP 5  COST (rule 12). INFRASTRUCTURE: a failed write is a warning -----
TOTAL_WALL=$(( $(date +%s) - T_START ))
{ echo "case_id = $CASE_ID"; echo "total_wall_s = $TOTAL_WALL"; echo "gpu_h_total = $(python3 -c "print('%.6f' % ($TOTAL_WALL/3600.0))")"
  echo "cpu_arm_core_min = $CPU_ARM_CORE_MIN"; echo "cap_gpu_h_registered = $CAP_GPU_H"; echo "cap_cpu_arm_core_min_registered = $CAP_CPU_ARM_CORE_MIN"
  echo "cost_basis = DERIVED, NOT MEASURED -- this box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md section 5)."; echo "utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$RUN_ROOT/COST.txt" 2>/dev/null || warn_infra "could not write COST.txt (INFRASTRUCTURE; the grade proceeds on physics artifacts, L-342)"

log "grade with: python3 $GRADER_REL --run-root $RUN_ROOT"
exit $FAILED
