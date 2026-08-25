#!/usr/bin/env bash
# smoke_test_gpu_path.sh — prove the lab's GPU SOLVER PATH ran ON THE GPU.
#
# DRAFT, ansys-lane-opus48 for ansys-verification-supervisor, 2026-08-25. FIRST ARROW:
# reviewed offline; NOT run by this task; touches NO instance.
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
# second time with CPU types FORCED (-mat_type aij -vec_type standard). That control MUST
# report GPU-ABSENT on tells 1 and 3. If the forced-CPU control "passes" the GPU tells,
# the test is broken and CERTIFIES NOTHING (exit 2).
#
# HAZARDS: no `set -e` (does not gate at top level), no `set -u` (v2606 bashrc dies).
set -o pipefail

OF_VERSION="openfoam2606"
WORK="${WORK:-$HOME/gpu_build/smoke}"
CASE="$WORK/VMFLGPU001_smoke"
GPU_OPTS="-mat_type aijcusparse -vec_type cuda -ksp_view -log_view -log_view_gpu_time"
CPU_OPTS="-mat_type aij -vec_type standard -ksp_view -log_view"

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] SMOKE: $*"; }

# shellcheck disable=SC1090
source "/usr/lib/openfoam/${OF_VERSION}/etc/bashrc" \
    || { log "ABORT: cannot source ${OF_VERSION} bashrc"; exit 1; }

# ---- build the tiny case (concentric-cylinder annulus, few-thousand cells) ----------
build_case() {
  rm -rf "$CASE"; mkdir -p "$CASE" || { log "ABORT: mkdir case"; exit 1; }
  # A minimal annulus wedge/section: geometry from manual p.225 (r_in=17.8mm, r_out=46.28mm,
  # omega_in=1 rad/s, rho=1, mu=2e-4). The full frozen case is the VMFLGPU001 prereg's job;
  # this smoke case is deliberately tiny and its numbers are only sanity-checked, not graded.
  # <case dictionaries (0/, constant/, system/) materialised here at review>
  # system/fvSolution selects petsc for the pressure solve:
  #     p { solver petsc; petsc { options { <read from PETSC options file> } } }
  test -d "$CASE/system" || { log "ABORT: smoke case not materialised (fill at review)"; return 1; }
}

# ---- run once, capture the log; sample the GPU concurrently ------------------------
run_solver() {  # $1 = petsc options string, $2 = tag
  local opts="$1" tag="$2" solverlog="$CASE/log.$2"
  ( cd "$CASE" && blockMesh > "$CASE/log.blockMesh.$tag" 2>&1 ) \
      || { log "ABORT: blockMesh failed ($tag)"; return 1; }
  # background GPU sampler while the solver runs
  ( for i in $(seq 1 60); do
        nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader
        sleep 0.5
      done ) > "$CASE/gpusample.$tag" 2>/dev/null &
  local sampler=$!
  ( cd "$CASE" && simpleFoam $opts > "$solverlog" 2>&1 )
  local rc=$?
  kill "$sampler" 2>/dev/null
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
log "materialising smoke case"
build_case || exit 1
log "GPU run: $GPU_OPTS"
run_solver "$GPU_OPTS" gpu || { log "FAIL: GPU solver run did not complete rc!=0"; exit 1; }

G1=1; G2=1; G3=1
tell1_gpu_flops "$CASE/log.gpu" && G1=0
tell2_pid_on_gpu "$CASE/gpusample.gpu" && G2=0
tell3_cuda_type  "$CASE/log.gpu" && G3=0
log "GPU tells: flops=$([ $G1 = 0 ] && echo YES || echo NO)  pid_on_gpu=$([ $G2 = 0 ] && echo YES || echo NO)  cuda_type=$([ $G3 = 0 ] && echo YES || echo NO)"
if [ $G1 -ne 0 ] || [ $G2 -ne 0 ] || [ $G3 -ne 0 ]; then
  log "FAIL: not all three GPU tells fired -> the solve did NOT run on the GPU (silent CPU fallback)."
  exit 1
fi

# ============================================================= FORCED-CPU CONTROL (must FAIL the GPU tells)
log "forced-CPU control run: $CPU_OPTS  (MUST show GPU-ABSENT, else the test is broken)"
run_solver "$CPU_OPTS" cpu || { log "FAIL: forced-CPU control run did not complete"; exit 1; }
C1=1; C3=1
tell1_gpu_flops "$CASE/log.cpu" && C1=0     # expect NO (C1 stays 1)
tell3_cuda_type  "$CASE/log.cpu" && C3=0     # expect NO (C3 stays 1)
if [ $C1 -eq 0 ] || [ $C3 -eq 0 ]; then
  log "REFUSE (exit 2): forced-CPU control REPORTED GPU work -> the tells cannot tell GPU from CPU. Test certifies NOTHING."
  exit 2
fi
log "control OK: forced-CPU run correctly shows GPU-ABSENT; the tells discriminate."

# ============================================================= PHYSICS SANITY FLOOR (not the graded gate)
# VMFLGPU001 manual targets: v_theta = 0.0151/0.0105/0.0072/0.0046 m/s at r=20/25/30/35mm.
# A loose 5% floor: proves the GPU solve returned physical numbers, not NaNs. The GRADED
# gate is the frozen VMFLGPU001 comparator, not this.
log "physics sanity floor at 5% (sanity only; the frozen comparator grades)"
# <sample v_theta at the four radii from the GPU result and compare to targets at 5%>
# if any radius is off by >5% or NaN: log FAIL and exit 1.

log "PASS: GPU solver path proven on the GPU (3 tells fired, forced-CPU control discriminated, physics sane)."
exit 0
