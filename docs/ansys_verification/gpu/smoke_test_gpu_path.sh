#!/usr/bin/env bash
# smoke_test_gpu_path.sh — prove the lab's GPU SOLVER PATH ran ON THE GPU.
#
# DRAFT, ansys-lane-opus48 for ansys-verification-supervisor, 2026-08-25. FIRST ARROW:
# reviewed offline.
# REPAIRED 2026-08-26 by ansys-verification-supervisor personally (two defects found at the
# review that precedes the first run, both recorded here rather than silently fixed):
#   (1) the draft passed PETSc options on simpleFoam's argv; simpleFoam rejects unknown
#       arguments and petsc4Foam reads mat_type/vec_type from fvSolution's petsc.options
#       dict. The types are now TEMPLATED into fvSolution per run (__MATTYPE__/__VECTYPE__ in
#       smoke_case/system/fvSolution.template) and the GLOBAL options (-log_view, -ksp_view)
#       go through the PETSC_OPTIONS environment variable.
#   (2) the smoke case was never materialised ("fill at review"); it now ships committed at
#       docs/ansys_verification/gpu/smoke_case/ (VMFL001's L1 mesh, 16x16 per block, endTime
#       300, petsc solvers for p and U) and is copied in by build_case.
#
# This is NOT "a binary exists" and NOT "a case completed". It proves the linear solve
# executed on the L4, and it is BUILT TO FAIL on a silent CPU fallback. It runs the
# smallest VMFLGPU case (VMFLGPU001, concentric-cylinder Couette) through petsc4Foam.
#
# THREE INDEPENDENT GPU TELLS, ALL must fire (any one has a failure mode; requiring all
# three means a silent CPU fallback cannot pass):
#   TELL 1  PETSc -log_view reports NON-ZERO GPU flops for KSPSolve.
#   TELL 2  the solver PID holds NON-ZERO GPU memory during the solve (nvidia-smi).
#   TELL 3  the ACTIVE PETSc matrix type is aijcusparse/mpiaijcusparse (not seqaij/mpiaij).
#
# PROOF THE TEST CAN FAIL (planted-negative, rule 3 discipline): the SAME case is run a
# second time with CPU types FORCED (aij / standard). That control MUST report GPU-ABSENT
# on tells 1 and 3. If the forced-CPU control "passes" the GPU tells, the test is broken
# and CERTIFIES NOTHING (exit 2). SUPERVISOR_REVIEW.md lines 27-44: the control IS the
# discriminator and is never removed, skipped, short-circuited or made conditional.
#
# HAZARDS: no `set -e` (does not gate at top level), no `set -u` (v2606 bashrc dies).
set -o pipefail

OF_VERSION="openfoam2606"
OF_BASHRC="${OF_BASHRC:-/usr/lib/openfoam/${OF_VERSION}/etc/bashrc}"
WORK="${WORK:-$HOME/gpu_build/smoke}"
CASE="$WORK/VMFLGPU001_smoke"
SMOKE_CASE_SRC="${SMOKE_CASE_SRC:-$HOME/gpu_build/smoke_case}"
# PIN 4 2026-08-26T17:3xZ (supervisor, MEASURED on build attempt 3, smoke rc=76 in 1 s): PETSc
# refuses at PetscInitialize -- "PETSc is configured with GPU support, but your MPI is not
# GPU-aware" -- and names the switch itself. Ubuntu's Open MPI 5.0.10 is not CUDA-aware; for a
# single-rank solve no device buffer ever crosses MPI, so the option changes nothing physical.
# It is part of BOTH arms so the forced-CPU control differs from the GPU arm ONLY in mat/vec type.
GPU_MAT="aijcusparse"; GPU_VEC="cuda";     GPU_ENV="-use_gpu_aware_mpi 0 -ksp_view -log_view -log_view_gpu_time"
CPU_MAT="aij";         CPU_VEC="standard"; CPU_ENV="-use_gpu_aware_mpi 0 -ksp_view -log_view"

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] SMOKE: $*"; }

mkdir -p "$WORK" || { log "ABORT: cannot make $WORK"; exit 1; }
# shellcheck disable=SC1090
source "$OF_BASHRC" \
    || { log "ABORT: cannot source $OF_BASHRC"; exit 1; }
test -n "$PETSC_DIR" || { log "ABORT: PETSC_DIR not exported (run via build_gpu_solver.sh or export it)"; exit 1; }

# ---- materialise the committed smoke case with the linear-algebra types templated in ----
build_case() {  # $1 = mat type, $2 = vec type
  rm -rf "$CASE"; mkdir -p "$CASE" || { log "ABORT: mkdir case"; return 1; }
  test -d "$SMOKE_CASE_SRC/system" || { log "ABORT: smoke case source $SMOKE_CASE_SRC absent"; return 1; }
  cp -r "$SMOKE_CASE_SRC"/. "$CASE"/ || { log "ABORT: copy smoke case"; return 1; }
  sed -e "s/__MATTYPE__/$1/g" -e "s/__VECTYPE__/$2/g" "$CASE/system/fvSolution.template" \
      > "$CASE/system/fvSolution" || { log "ABORT: fvSolution templating"; return 1; }
  grep -q "__" "$CASE/system/fvSolution" && { log "ABORT: untemplated placeholder left in fvSolution"; return 1; }
  return 0
}

# ---- run once, capture the log; sample the GPU concurrently ------------------------
run_solver() {  # $1 = mat type, $2 = vec type, $3 = PETSC_OPTIONS string, $4 = tag
  local mat="$1" vec="$2" opts="$3" tag="$4" solverlog="$CASE/log.$4"
  build_case "$mat" "$vec" || return 1
  ( cd "$CASE" && blockMesh > "$CASE/log.blockMesh.$tag" 2>&1 ) \
      || { log "ABORT: blockMesh failed ($tag)"; return 1; }
  # background GPU sampler while the solver runs
  ( for i in $(seq 1 120); do
        nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader
        sleep 0.5
      done ) > "$CASE/gpusample.$tag" 2>/dev/null &
  local sampler=$!
  ( cd "$CASE" && PETSC_OPTIONS="$opts" simpleFoam > "$solverlog" 2>&1 )
  local rc=$?
  kill "$sampler" 2>/dev/null
  cp "$solverlog" "$WORK/log.$tag.keep" 2>/dev/null
  cp "$CASE/gpusample.$tag" "$WORK/gpusample.$tag.keep" 2>/dev/null
  echo "rc=$rc tag=$tag mat=$mat vec=$vec finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$WORK/RUN_RC.txt"
  return $rc
}

# ---- the three tells, evaluated from a run's artifacts ------------------------------
tell1_gpu_flops() {  # $1 solverlog -> 0 if NON-ZERO GPU flops present
  # -log_view prints a "GPU Mflop/s" / "GPU flops" column; a CPU run shows 0.
  grep -Eiq 'GPU .*[1-9][0-9]*' "$1" && grep -Eiq 'CpuToGpu|GpuToCpu' "$1"
}
tell2_pid_on_gpu() { # $1 gpusample -> 0 if a PID held non-zero device memory
  grep -Eq '[0-9]+, *[1-9][0-9]* MiB' "$1"
}
tell3_cuda_type() {  # $1 solverlog -> 0 if active matrix type is a cusparse type
  grep -Eiq 'type: *(seqaijcusparse|mpiaijcusparse|aijcusparse)' "$1"
}

# ============================================================= GPU RUN (must PASS)
log "GPU run: mat=$GPU_MAT vec=$GPU_VEC PETSC_OPTIONS='$GPU_ENV'"
run_solver "$GPU_MAT" "$GPU_VEC" "$GPU_ENV" gpu || { log "FAIL: GPU solver run did not complete rc!=0"; exit 1; }

G1=1; G2=1; G3=1
tell1_gpu_flops "$WORK/log.gpu.keep" && G1=0
tell2_pid_on_gpu "$WORK/gpusample.gpu.keep" && G2=0
tell3_cuda_type  "$WORK/log.gpu.keep" && G3=0
log "GPU tells: flops=$([ $G1 = 0 ] && echo YES || echo NO)  pid_on_gpu=$([ $G2 = 0 ] && echo YES || echo NO)  cuda_type=$([ $G3 = 0 ] && echo YES || echo NO)"
if [ $G1 -ne 0 ] || [ $G2 -ne 0 ] || [ $G3 -ne 0 ]; then
  log "FAIL: not all three GPU tells fired -> the solve did NOT run on the GPU (silent CPU fallback)."
  exit 1
fi

# ============================================================= FORCED-CPU CONTROL (must FAIL the GPU tells)
log "forced-CPU control run: mat=$CPU_MAT vec=$CPU_VEC  (MUST show GPU-ABSENT, else the test is broken)"
run_solver "$CPU_MAT" "$CPU_VEC" "$CPU_ENV" cpu || { log "FAIL: forced-CPU control run did not complete"; exit 1; }
C1=1; C3=1
tell1_gpu_flops "$WORK/log.cpu.keep" && C1=0     # expect NO (C1 stays 1)
tell3_cuda_type  "$WORK/log.cpu.keep" && C3=0     # expect NO (C3 stays 1)
if [ $C1 -eq 0 ] || [ $C3 -eq 0 ]; then
  log "REFUSE (exit 2): forced-CPU control REPORTED GPU work -> the tells cannot tell GPU from CPU. Test certifies NOTHING."
  exit 2
fi
log "control OK: forced-CPU run correctly shows GPU-ABSENT; the tells discriminate."

# ============================================================= SANITY FLOOR (not the graded gate)
# REPAIR 2026-08-26: the floor implemented here is COMPLETION + NO NaN on the kept GPU log,
# stated as exactly that. The four-radius comparison against the manual's targets is the
# frozen VMFLGPU001 comparator's job, not this script's.
log "sanity floor: End line present and no NaN in the GPU run (the frozen comparator grades physics)"
grep -q "^End" "$WORK/log.gpu.keep" || { log "FAIL: GPU run log has no End line"; exit 1; }
grep -qi "nan" "$WORK/log.gpu.keep" && { log "FAIL: NaN in the GPU run log"; exit 1; }

log "PASS: GPU solver path proven on the GPU (3 tells fired, forced-CPU control discriminated, GPU run completed without NaN)."
exit 0
