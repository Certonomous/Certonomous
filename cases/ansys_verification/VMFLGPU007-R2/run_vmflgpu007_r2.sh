#!/usr/bin/env bash
# ============================================================================
# run_vmflgpu007_r2.sh -- VMFLGPU007-R2 graded-run driver.
#
# Turbulent Flow with Heat Transfer in a Backward-Facing Step, manual p.243.
# CPU PARENT: VMFL013.  Object under verification: THE LAB'S GPU SOLVER PATH
# (OpenFOAM v2606 + petsc4Foam + PETSc-CUDA on the L4).
#
# RUNS ON THE GPU INSTANCE, never on the lab box.  SIX solves: three mesh
# levels x two arms (GPU aijcusparse/cuda; forced-CPU aij/standard, which is
# limb A's discriminator AND limb B's baseline, one run serving both).
#
# IT GRADES NOTHING.  Grading is grade_vmflgpu007_r2.py, frozen separately and
# cited by sha in PREREGISTRATION.md.
#
# ---------------------------------------------------------------------------
# THIS IS VMFLGPU007-R2, A FRESH REGISTRATION SUCCEEDING VMFLGPU007 (R1).
# R1 IS FROZEN AND PRESERVED; THIS LAUNCHER NEVER TOUCHES IT AND NOTHING HERE
# RE-GRADES IT.  R1's row stands as NOT A RESULT: at endTime 1200/1800/3000 its
# wallTmin plateau channel had not settled -- the 200-sample peak-to-peak read
# 0.0237893 / 0.0120540 / 0.00358665 K against a registered 1.0e-4 K.
#
# EXACTLY ONE REGISTERED QUANTITY MOVES IN THIS LAUNCHER: the three endTimes in
# the LEVELS line below, 1200 -> 3200, 1800 -> 4400, 3000 -> 6200, chosen from
# the MEASURED exponential decay rate of R1's own wallTmin channel (tau = 230.4 /
# 333.3 / 477.4 SIMPLE iterations, R^2 = 0.9999-1.0000) plus a 3-tau margin.
# THE PLATEAU TOLERANCE DOES NOT MOVE and neither do the caps, the mesh family,
# the cell counts, H1, the arms, the PETSc options or any band.  endTime is a
# COST parameter; a tolerance is a GATE, and a gate is never chosen from the
# answer it refused.
#
# CASE INPUTS AND INSTRUMENTS ARE BYTE-IDENTICAL COPIES of R1's: case/,
# reference/, field_completeness.py and resolve_blockmesh.py, verified with
# `cmp` and `diff -r`.  The pre-freeze mesh measurements this launcher's birth
# certificate checks against live in R1's record,
# cases/ansys_verification/VMFLGPU007/MESH_PREFREEZE_RECORD.md, cited here by
# full path because the cell counts did not change and re-measuring them would
# be inventing a second source for one number.
#
# ---------------------------------------------------------------------------
# HAZARDS, EACH MEASURED BY THIS LAB:
#  * NO `set -u`.  CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606: etc/bashrc
#    dereferences WM_PROJECT_DIR before assigning it.  MEASURED rc 127.
#  * NO `set -e`.  It does NOT gate at a Bash tool's top level.  EVERY step
#    below gates EXPLICITLY.
#  * THE FREEZE CHECK DERIVES ITS REPOSITORY FROM THIS SCRIPT'S OWN LOCATION
#    and never from the environment.  VMFLGPU001-R2 Amendment 1: SCRIPT_DIR and
#    a caller-supplied REPO are independent paths, so a check against REPO can
#    PASS WHILE PROVING NOTHING about the tree that actually runs.
#  * BOOKKEEPING NEVER VOIDS PHYSICS (L-342).  After a solver completes, a
#    failed bookkeeping write is a WARNING and the exit code STAYS the solver's.
#    Before any solver runs, the freeze check, the mesh birth certificate and
#    field completeness are PHYSICS-CRITICAL and DO abort.
#  * A NON-ZERO EXIT IS NOT EVIDENCE A GUARD FIRED (L-357).  Every refusal
#    below prints a NAMED message; the drive record asserts those strings.
#
# EXECUTE this script (`bash run_vmflgpu007_r2.sh <run_root>`); NEVER `source` it.
# ============================================================================
set -o pipefail   # wanted and safe. `set -e` / `set -u` deliberately NOT set.

CASE_ID="VMFLGPU007-R2"
RANKS=1                        # serial; core-minutes = wall_s * RANKS / 60
CAP_GPU_H=1.5                  # FROZEN in PREREGISTRATION.md section 9
CAP_CPU_ARM_CORE_MIN=90        # FROZEN in PREREGISTRATION.md section 9

# name:NXI:NXD:NYU:NYL:ENDTIME:CELLS
# CELLS are the MEASURED counts from the pre-freeze blockMesh+checkMesh on the
# lab box (MESH_PREFREEZE_RECORD.md), NOT predictions.  H1 is IDENTICAL at
# every level -- that is what makes this a mesh-sensitivity family.
LEVELS="L1:16:96:24:10:3200:3648 L2:24:144:36:12:4400:7776 L3:36:216:52:14:6200:16128"
H1_WALL=0.07

GPU_MAT="aijcusparse"; GPU_VEC="cuda"
CPU_MAT="aij";         CPU_VEC="standard"
# -use_gpu_aware_mpi 0 is SHARED BY BOTH ARMS so the two arms differ ONLY in
# mat_type/vec_type -- which is the whole basis on which limb B is a statement
# about WHERE the linear algebra ran and about nothing else.  This case runs at
# ONE RANK, so the device-to-device MPI path the option governs is never
# exercised: it declines a PERFORMANCE feature, not a correctness one.
SHARED_PETSC_OPTIONS="-use_gpu_aware_mpi 0"
GPU_OWN_PETSC_OPTIONS="-ksp_view -log_view -log_view_gpu_time"
CPU_OWN_PETSC_OPTIONS="-ksp_view -log_view"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_SRC="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmflgpu007_r2.sh <run_root>}"
BUILD_ROOT="${BUILD_ROOT:-$HOME/gpu_build}"
REPO_ENV="${REPO-}"     # what the caller ASKED for: CHECKED at STEP 1, never obeyed
REPO=""                 # DERIVED at STEP 1 from SCRIPT_DIR.  Empty here ON PURPOSE.
CASE_REL_DIR="cases/ansys_verification/VMFLGPU007-R2"
PREREG_REL="$CASE_REL_DIR/PREREGISTRATION.md"
GRADER_REL="$CASE_REL_DIR/grade_vmflgpu007_r2.py"
LAUNCHER_REL="$CASE_REL_DIR/run_vmflgpu007_r2.sh"
FIELDCHK_REL="$CASE_REL_DIR/field_completeness.py"
MESHGEN_REL="$CASE_REL_DIR/resolve_blockmesh.py"

T_START=$(date +%s)
log()  { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ${CASE_ID}: $*"; }
warn_infra() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ${CASE_ID}: WARNING(INFRASTRUCTURE): $*"; }

log "=== START (run_root=$RUN_ROOT build_root=$BUILD_ROOT repo=DERIVED-AT-STEP-1 repo_env=${REPO_ENV:-<unset>}) ==="

# ---------------------------------------------------------------------------
# STEP 0  THE SMOKE GATE -- REFUSES AT ZERO COMPUTE (exit 2)
# This case's WHOLE OBJECT is the GPU solver path.  If that path has not been
# PROVEN on this instance, every solve below is at best a CPU number wearing a
# GPU case's name.
# ---------------------------------------------------------------------------
STATUS_SMOKE="$BUILD_ROOT/STATUS.smoke"
MANIFEST="$BUILD_ROOT/TOOLCHAIN_MANIFEST.txt"
BUILD_ENV="$BUILD_ROOT/env.sh"
test -f "$STATUS_SMOKE" \
    || { echo "REFUSE (exit 2): $STATUS_SMOKE is absent. The GPU solver path has not been PROVEN on this instance, so nothing this script could run would be evidence about it."; exit 2; }
grep -Eq '^[[:space:]]*smoke_rc[[:space:]]*=[[:space:]]*0([[:space:]]|$)' "$STATUS_SMOKE" \
    || { echo "REFUSE (exit 2): $STATUS_SMOKE does not read smoke_rc=0. Contents follow, and this script does not interpret them charitably:"; sed -e 's/^/    | /' "$STATUS_SMOKE"; exit 2; }
test -f "$MANIFEST" \
    || { echo "REFUSE (exit 2): $MANIFEST is absent. A GPU-path proof whose toolchain cannot be NAMED is not evidence about any particular toolchain."; exit 2; }
test -f "$BUILD_ENV" \
    || { echo "REFUSE (exit 2): $BUILD_ENV is absent. It carries THE MPI PIN this stack must run under; the DLAMI prepends AWS Open MPI 4.1.7, SHADOWING Ubuntu's 5.0.10 that OpenFOAM and PETSc were compiled against (SAME SONAME, so the linker resolves it silently)."; exit 2; }
log "SMOKE GATE PASSED: $STATUS_SMOKE reads smoke_rc=0, $MANIFEST exists, $BUILD_ENV exists"

# ---------------------------------------------------------------------------
# STEP 0c  THE CAP MECHANISM IS DRIVEN BEFORE IT IS TRUSTED (L-339)
# ---------------------------------------------------------------------------
command -v timeout >/dev/null \
    || { echo "REFUSE (exit 2): \`timeout\` is not on PATH, so the per-solve cap registered in PREREGISTRATION.md section 9 cannot be enforced in the executable path."; exit 2; }
timeout 10 bash -c 'exit 7'; TO_RC_PASS=$?
timeout 1  bash -c 'sleep 3'; TO_RC_KILL=$?
if [ "$TO_RC_PASS" != "7" ] || [ "$TO_RC_KILL" != "124" ]; then
  echo "REFUSE (exit 2): \`timeout\` does not behave as the cap requires on this host -- a child exiting 7 came back as $TO_RC_PASS (expected 7) and a child that overran came back as $TO_RC_KILL (expected 124)."
  exit 2
fi
log "CAP MECHANISM DRIVEN: timeout passes a child rc through (7) and reports an overrun as 124 on this host"

# ---------------------------------------------------------------------------
# STEP 1  LAUNCH-TIME FREEZE CHECK -- PHYSICS-CRITICAL, NON-DROPPABLE
#         FIVE paths: prereg, comparator, THIS LAUNCHER, the field-completeness
#         guard and the mesh generator.  A launcher that verifies everything
#         except itself and its own instruments is the same hole one level up.
# ---------------------------------------------------------------------------
SCRIPT_DIR_P="$(cd "$SCRIPT_DIR" 2>/dev/null && pwd -P)" \
    || { echo "ABORT (freeze a): cannot resolve SCRIPT_DIR=$SCRIPT_DIR with 'cd && pwd -P'."; exit 1; }
REPO_TOP="$(git -C "$SCRIPT_DIR_P" rev-parse --show-toplevel 2>/dev/null)" \
    || { echo "ABORT (freeze a): SCRIPT_DIR=$SCRIPT_DIR_P is NOT inside a git worktree, so there is no HEAD that could certify the pre-registration, the comparator or this launcher. The repository is NEVER taken from the environment."; exit 1; }
test -n "$REPO_TOP" \
    || { echo "ABORT (freeze a): 'git rev-parse --show-toplevel' at $SCRIPT_DIR_P returned an EMPTY toplevel."; exit 1; }
REPO="$(cd "$REPO_TOP" 2>/dev/null && pwd -P)" \
    || { echo "ABORT (freeze a): cannot resolve the derived toplevel $REPO_TOP with 'cd && pwd -P'."; exit 1; }
EXPECT_DIR="$(cd "$REPO/$CASE_REL_DIR" 2>/dev/null && pwd -P)" \
    || { echo "ABORT (freeze b): the derived repository $REPO has no directory $CASE_REL_DIR."; exit 1; }
[ "$SCRIPT_DIR_P" = "$EXPECT_DIR" ] \
    || { echo "ABORT (freeze b): SCRIPT_DIR=$SCRIPT_DIR_P is NOT $REPO/$CASE_REL_DIR (which resolves to $EXPECT_DIR). The case inputs and the blobs the freeze check would certify are IN DIFFERENT TREES."; exit 1; }
if [ -n "$REPO_ENV" ]; then
  REPO_ENV_P="$(cd "$REPO_ENV" 2>/dev/null && pwd -P)" \
      || { echo "ABORT (freeze c): REPO=$REPO_ENV was set in the environment but does not resolve to a directory."; exit 1; }
  [ "$REPO_ENV_P" = "$REPO" ] \
      || { echo "ABORT (freeze c): REPO=$REPO_ENV resolves to $REPO_ENV_P, which is NOT the repository derived from this script's own location ($REPO). The environment does not select the tree a freeze is proved against."; exit 1; }
fi
log "REPO DERIVED FROM SCRIPT_DIR: $REPO (script_dir $SCRIPT_DIR_P == \$REPO/$CASE_REL_DIR; env REPO ${REPO_ENV:-<unset>})"

FROZEN_PATHS="$PREREG_REL $GRADER_REL $LAUNCHER_REL $FIELDCHK_REL $MESHGEN_REL"
FROZEN_REPORT=""
for rel in $FROZEN_PATHS; do
  git -C "$REPO" cat-file -e "HEAD:$rel" 2>/dev/null \
      || { echo "ABORT (freeze d): $rel is not committed at HEAD -- the freeze is the evidence"; exit 1; }
  hh="$(git -C "$REPO" rev-parse "HEAD:$rel")" || { echo "ABORT (freeze d): cannot resolve HEAD:$rel"; exit 1; }
  hd="$(git -C "$REPO" hash-object "$REPO/$rel")" || { echo "ABORT (freeze d): cannot hash $rel on disk"; exit 1; }
  [ "$hd" = "$hh" ] || { echo "ABORT (freeze d): $rel on disk ($hd) differs from HEAD ($hh). The bytes now executing are NOT the committed blob, so every guard they contain is unverified."; exit 1; }
  FROZEN_REPORT="$FROZEN_REPORT $rel=$hh"
done
HEAD_SHA="$(git -C "$REPO" rev-parse HEAD)" || { echo "ABORT: cannot resolve HEAD"; exit 1; }
log "FREEZE VERIFIED:$FROZEN_REPORT ; HEAD $HEAD_SHA"

mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
{ echo "case_id = $CASE_ID"
  echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "head = $HEAD_SHA"
  echo "script_dir = $SCRIPT_DIR_P"
  echo "repo_toplevel_derived = $REPO"
  echo "repo_env_as_passed = ${REPO_ENV:-<unset>}"
  for kv in $FROZEN_REPORT; do echo "frozen_blob ${kv%%=*} = ${kv##*=}"; done
  echo "host = $(hostname)"
} > "$RUN_ROOT/LAUNCH_RECORD.txt" || { echo "ABORT: cannot write $RUN_ROOT/LAUNCH_RECORD.txt"; exit 1; }

# ---------------------------------------------------------------------------
# STEP 2  ENVIRONMENT -- sourced EXACTLY as build_gpu_solver.sh recorded it.
# THE MPI PIN GOES FIRST, before OpenFOAM's bashrc, because the bashrc's own
# MPI selection reads PATH.
# ---------------------------------------------------------------------------
test -f "$BUILD_ROOT/OF_BASHRC" \
    || { echo "ABORT: $BUILD_ROOT/OF_BASHRC absent -- build_gpu_solver.sh records the OpenFOAM bashrc it actually used; this script never guesses the path"; exit 1; }
OF_BASHRC="$(cat "$BUILD_ROOT/OF_BASHRC")" || { echo "ABORT: cannot read $BUILD_ROOT/OF_BASHRC"; exit 1; }
test -f "$OF_BASHRC" || { echo "ABORT: recorded OF_BASHRC ($OF_BASHRC) does not exist"; exit 1; }
# THE POSITIONAL PARAMETERS ARE CLEARED BEFORE ANY ENVIRONMENT FILE IS SOURCED.
# MEASURED on the lab box with OpenFOAM v2606: etc/bashrc ends with
#   . "$WM_PROJECT_DIR/etc/config.sh/setup" "$@"
# and that chain reaches `_foamEtc -config paraview -- "$@"  # Pass through for
# evaluation`, which SOURCES any argument that resolves to a *.sh file. RUN_ROOT
# is a DIRECTORY, so this launcher was never exposed -- driven both ways: a
# directory argument leaves blockMesh on PATH, a *.sh argument is EXECUTED inside
# the bashrc with none of this script's variables set. It is one line to close a
# path from an argument to code execution, and $1 is not read after line 86.
set --
. "$BUILD_ENV"  || { echo "ABORT: cannot source $BUILD_ENV (the MPI pin)"; exit 1; }
. "$OF_BASHRC"  || { echo "ABORT: cannot source $OF_BASHRC"; exit 1; }
command -v blockMesh >/dev/null || { echo "ABORT: blockMesh is not on PATH after sourcing $OF_BASHRC"; exit 1; }
command -v buoyantSimpleFoam >/dev/null || { echo "ABORT: buoyantSimpleFoam is not on PATH after sourcing $OF_BASHRC"; exit 1; }
log "ENVIRONMENT OK: $(command -v buoyantSimpleFoam)"

# ---------------------------------------------------------------------------
# STEP 3  refuse to start if ANY level directory of EITHER arm already exists.
# Rule 4's age guard depends on the tree not already holding an answer.
# ---------------------------------------------------------------------------
for spec in $LEVELS; do
  name="${spec%%:*}"
  for arm in gpu cpu; do
    d="$RUN_ROOT/$arm/$name"
    [ -e "$d" ] && { echo "ABORT: $d already exists -- this script never runs into an existing case (CLAUDE.md rule 4)"; exit 1; }
  done
done
log "no level directory of either arm pre-exists"

# ---------------------------------------------------------------------------
# STEP 4  THE SIX SOLVES
# ---------------------------------------------------------------------------
CPU_ARM_CORE_MIN=0
FAILED=0
for spec in $LEVELS; do
  IFS=: read -r NAME NXI NXD NYU NYL ETIME EXPECT_CELLS <<< "$spec"
  for arm in gpu cpu; do
    D="$RUN_ROOT/$arm/$NAME"
    mkdir -p "$D" || { echo "ABORT: cannot create $D"; exit 1; }
    cp -a "$CASE_SRC/." "$D/" || { echo "ABORT: cannot stage case inputs into $D"; exit 1; }

    # ---- COMPLETE THE CASE DIRECTORY BEFORE ANY OpenFOAM UTILITY RUNS ------
    # AMENDMENT 2 (PRE-COMPUTE, 2026-08-27).  EVERY OpenFOAM utility constructs a
    # Time object before it does anything else, and Time READS system/controlDict.
    # blockMesh is no exception.  In the frozen ordering this templating sat 27
    # lines BELOW the blockMesh call, so blockMesh ran against a case directory
    # holding only controlDict.template and died in its constructor:
    #   --> FOAM FATAL ERROR: cannot find file ".../gpu/L1/system/controlDict"
    # The case directory is now COMPLETE before the first utility is invoked.
    sed -e "s/__MATTYPE__/$([ "$arm" = gpu ] && echo "$GPU_MAT" || echo "$CPU_MAT")/g" \
        -e "s/__VECTYPE__/$([ "$arm" = gpu ] && echo "$GPU_VEC" || echo "$CPU_VEC")/g" \
        "$D/system/fvSolution.template" > "$D/system/fvSolution" \
        || { echo "ABORT ($NAME/$arm): cannot materialise fvSolution"; exit 1; }
    rm -f "$D/system/fvSolution.template"
    sed -e "s/__ENDTIME__/$ETIME/g" "$D/system/controlDict.template" > "$D/system/controlDict" \
        || { echo "ABORT ($NAME/$arm): cannot materialise controlDict"; exit 1; }
    rm -f "$D/system/controlDict.template"

    # ---- MESH: generated by the FROZEN generator from the FROZEN template ----
    python3 "$REPO/$MESHGEN_REL" "$D/system/blockMeshDict.template" \
            "$NXI" "$NXD" "$NYU" "$NYL" "$H1_WALL" "$D/system/blockMeshDict" \
        || { echo "ABORT ($NAME/$arm): the frozen mesh generator REFUSED. Its refusal text is above and is the finding; a non-zero exit alone is not (L-357)."; exit 1; }
    rm -f "$D/system/blockMeshDict.template"
    ( cd "$D" && blockMesh > log.blockMesh 2>&1 ) \
        || { echo "ABORT ($NAME/$arm): blockMesh failed; see $D/log.blockMesh"; exit 1; }
    ( cd "$D" && checkMesh > log.checkMesh 2>&1 ) \
        || { echo "ABORT ($NAME/$arm): checkMesh failed; see $D/log.checkMesh"; exit 1; }
    grep -q '^Mesh OK' "$D/log.checkMesh" \
        || { echo "ABORT ($NAME/$arm): checkMesh did not report 'Mesh OK'. A mesh defect found now costs minutes; found at grade time it costs a GPU-hour and yields no verdict."; exit 1; }

    # ---- THE BIRTH CERTIFICATE, against the PRE-FREEZE MEASURED count -------
    GOT_CELLS="$(grep -oP '^\s+cells:\s+\K[0-9]+' "$D/log.checkMesh" | head -1)"
    [ -n "$GOT_CELLS" ] \
        || { echo "ABORT ($NAME/$arm): could not read a cell count from $D/log.checkMesh, so the birth certificate cannot be checked"; exit 1; }
    [ "$GOT_CELLS" = "$EXPECT_CELLS" ] \
        || { echo "ABORT ($NAME/$arm): BIRTH CERTIFICATE MISMATCH -- checkMesh reports $GOT_CELLS cells, the pre-freeze MEASURED count registered in PREREGISTRATION.md is $EXPECT_CELLS. The mesh that would run is not the mesh that was registered."; exit 1; }
    log "$NAME/$arm BIRTH CERTIFICATE OK: $GOT_CELLS cells == registered $EXPECT_CELLS"

    # ---- FIELD COMPLETENESS, the REPAIRED guard (not the ancestor) ---------
    # Three defects repaired and each driven: the parser cleared the key at the
    # newline before the brace (required={} on every conventionally formatted
    # fvSolution); the base set was hard-coded {p,U} and could not see p_rgh;
    # and the closure lookup was line-anchored and missed the INLINE
    # `RAS { RASModel kEpsilon; ... }` form this case actually carries.  It now
    # REFUSES an empty required set instead of certifying it.
    python3 "$REPO/$FIELDCHK_REL" "$D" \
        || { echo "ABORT ($NAME/$arm): FIELD COMPLETENESS refused. Its named refusal above is the finding."; exit 1; }

    # 0/T is touched LAST, so it dates the run allowed to produce this answer
    # (rule 4's age guard reference).
    touch "$D/0/T" || { echo "ABORT ($NAME/$arm): cannot touch the age-guard reference $D/0/T"; exit 1; }

    # ---- THE SOLVE, under the registered cap -------------------------------
    if [ "$arm" = gpu ]; then
      CAP_S=$(python3 -c "print(int($CAP_GPU_H*3600))")
      export PETSC_OPTIONS="$PETSC_OPTIONS_BASE $SHARED_PETSC_OPTIONS $GPU_OWN_PETSC_OPTIONS"
    else
      CAP_S=$(python3 -c "print(int($CAP_CPU_ARM_CORE_MIN*60/$RANKS))")
      export PETSC_OPTIONS="$PETSC_OPTIONS_BASE $SHARED_PETSC_OPTIONS $CPU_OWN_PETSC_OPTIONS"
    fi
    S0=$(date +%s)
    ( cd "$D" && timeout -k 30 "$CAP_S" buoyantSimpleFoam > log.buoyantSimpleFoam 2>&1 )
    RC=$?
    S1=$(date +%s); WALL=$((S1-S0))
    CAP_FIRED=0; [ "$RC" = "124" ] && CAP_FIRED=1
    if [ "$CAP_FIRED" = "1" ]; then
      { echo "case_id = $CASE_ID"; echo "level = $NAME"; echo "arm = $arm"
        echo "cap_s = $CAP_S"; echo "wall_s = $WALL"
        echo "note = THE CAP FIRED. CLAUDE.md rule 12: an overrun STOPS the run and does not get a new budget."
      } > "$RUN_ROOT/CAP_EXCEEDED.txt" 2>/dev/null || warn_infra "could not write CAP_EXCEEDED.txt"
    fi
    CORE_MIN=$(python3 -c "print('%.4f' % ($WALL*$RANKS/60.0))")
    GPU_H=$(python3 -c "print('%.6f' % ($WALL/3600.0))")
    [ "$arm" = cpu ] && CPU_ARM_CORE_MIN=$(python3 -c "print($CPU_ARM_CORE_MIN+$CORE_MIN)")
    { echo "case_id = $CASE_ID"; echo "arm = $arm"; echo "level = $NAME"
      echo "rc = $RC"; echo "cap_fired = $CAP_FIRED"; echo "cap_s = $CAP_S"
      echo "wall_s = $WALL"; echo "ranks = $RANKS"; echo "core_min = $CORE_MIN"
      echo "gpu_h = $GPU_H"; echo "endtime = $ETIME"; echo "cells = $GOT_CELLS"
      echo "mat_type = $([ "$arm" = gpu ] && echo "$GPU_MAT" || echo "$CPU_MAT")"
      echo "vec_type = $([ "$arm" = gpu ] && echo "$GPU_VEC" || echo "$CPU_VEC")"
      echo "petsc_options = $PETSC_OPTIONS"
      echo "utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } > "$RUN_ROOT/RUN_RC.$NAME.$arm" || warn_infra "could not write RUN_RC.$NAME.$arm"
    echo "solve rc = $RC  arm = $arm  level = $NAME  wall_s = $WALL  cap_fired = $CAP_FIRED  utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        >> "$RUN_ROOT/LAUNCH_RECORD.txt" || warn_infra "could not append to LAUNCH_RECORD.txt"
    log "$NAME/$arm rc=$RC wall_s=$WALL cap_fired=$CAP_FIRED"
    [ "$RC" != "0" ] && FAILED=1
  done
done

# ---------------------------------------------------------------------------
# STEP 5  COST (CLAUDE.md rule 12).  INFRASTRUCTURE: a failed write here is a
# warning; it never changes the solver's exit code (L-342).
# ---------------------------------------------------------------------------
TOTAL_WALL=$(( $(date +%s) - T_START ))
{ echo "case_id = $CASE_ID"
  echo "total_wall_s = $TOTAL_WALL"
  echo "gpu_h_total = $(python3 -c "print('%.6f' % ($TOTAL_WALL/3600.0))")"
  echo "cpu_arm_core_min = $CPU_ARM_CORE_MIN"
  echo "cap_gpu_h_registered = $CAP_GPU_H"
  echo "cap_cpu_arm_core_min_registered = $CAP_CPU_ARM_CORE_MIN"
  echo "cost_basis = DERIVED, NOT MEASURED -- this box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md section 5)."
  echo "utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$RUN_ROOT/COST.txt" 2>/dev/null \
  || warn_infra "could not write COST.txt -- cost is an INFRASTRUCTURE field; the grade proceeds on the physics artifacts and reports cost as NOT MEASURED (L-342)"

log "grade with: python3 $GRADER_REL --run-root $RUN_ROOT"
exit $FAILED
