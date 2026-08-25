#!/usr/bin/env bash
# build_gpu_solver.sh — build the lab's GPU solver path (OpenFOAM v2606 + petsc4Foam
# + PETSc --with-cuda, cuSPARSE sm_89) on a FRESH g6.xlarge / NVIDIA L4 DLAMI.
#
# DRAFT, ansys-lane-opus48 for ansys-verification-supervisor, 2026-08-25. FIRST ARROW
# of Sanaa's sequence: this script is REVIEWED OFFLINE before any boot. It is NOT run
# by this task and touches NO instance.
#
# HAZARD, measured this team (PREREG_TEMPLATE Amendment 2/3):
#   - `set -e` does NOT gate at a Bash tool top level; `( set -e; ... )` does not either.
#     => every step gates EXPLICITLY with `|| { echo ABORT; exit 1; }`.
#   - `set -u` is INCOMPATIBLE with OpenFOAM v2606: etc/bashrc dereferences WM_PROJECT_DIR
#     before assigning it (rc 127). => NO `set -u` anywhere in this script.
#   - EXECUTE this script (`bash build_gpu_solver.sh`); NEVER `source` it (a sourced
#     script does not gate the caller).
#
# IDEMPOTENT: each step writes a marker in $MARK and skips if the marker exists, so a
# re-run after a partial failure RESUMES rather than rebuilds.
#
# Pins are placeholders in <ANGLE_BRACKETS> to be resolved at review against the
# versions the box actually offers; the script ABORTS on an unresolved pin rather
# than guessing.

set -o pipefail   # pipefail is safe and wanted; `set -e`/`set -u` deliberately NOT set.

# ----------------------------------------------------------------------------- paths
BUILD_ROOT="${BUILD_ROOT:-$HOME/gpu_build}"
LOG="$BUILD_ROOT/build.log"
MARK="$BUILD_ROOT/markers"
OF_VERSION="openfoam2606"
CUDA_ARCH="89"                       # NVIDIA L4 = Ada Lovelace, compute capability 8.9
PETSC_TAG="<PIN: PETSc release tag verified --with-cuda for CUDA on this DLAMI>"
PETSC4FOAM_TAG="<PIN: petsc4Foam / modules tag matching ${OF_VERSION}>"

mkdir -p "$BUILD_ROOT" "$MARK" || { echo "ABORT: cannot create $BUILD_ROOT"; exit 1; }

# ------------------------------------------------------------------------- utilities
log()  { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG"; }
done_marker() { test -f "$MARK/$1"; }
mark() { touch "$MARK/$1" || { echo "ABORT: cannot write marker $1"; exit 1; }; }

log "=== build_gpu_solver.sh START ==="
log "BUILD_ROOT=$BUILD_ROOT  OF_VERSION=$OF_VERSION  CUDA_ARCH=sm_$CUDA_ARCH"

# Refuse to run on unresolved pins (guessing a tag is worse than aborting).
case "$PETSC_TAG$PETSC4FOAM_TAG" in
  *"<PIN"*) log "ABORT: unresolved <PIN> tags; resolve at review before running."; exit 1;;
esac

# ============================================================ STEP 1: preflight
if done_marker 01_preflight; then log "STEP 1 preflight: SKIP (done)"; else
  log "STEP 1 preflight: capturing environment"
  { nvidia-smi; echo; nvidia-smi -L; echo; uname -a; echo; df -h; echo; free -h; } \
      >> "$LOG" 2>&1 || { log "ABORT: nvidia-smi/env capture failed (no GPU?)"; exit 1; }
  nvidia-smi -L | grep -q 'NVIDIA L4' \
      || { log "ABORT: no NVIDIA L4 visible; sm_$CUDA_ARCH flags would be wrong."; exit 1; }
  mark 01_preflight
fi

# ============================================================ STEP 2: OS prereqs
if done_marker 02_osprereq; then log "STEP 2 OS prereqs: SKIP (done)"; else
  log "STEP 2 OS prereqs: apt-get build tooling"
  sudo apt-get update >> "$LOG" 2>&1 \
      || { log "ABORT: apt-get update failed"; exit 1; }
  sudo apt-get install -y build-essential gfortran cmake git flex bison zlib1g-dev \
      libopenmpi-dev openmpi-bin libfftw3-dev libscotch-dev libptscotch-dev pkg-config \
      >> "$LOG" 2>&1 \
      || { log "ABORT: apt-get install of build prereqs failed"; exit 1; }
  mark 02_osprereq
fi

# ============================================================ STEP 3: CUDA toolkit
# Detect nvcc; install the toolkit ONLY if absent. Never touch the DLAMI's driver.
if done_marker 03_cuda; then log "STEP 3 CUDA toolkit: SKIP (done)"; else
  if nvcc --version >> "$LOG" 2>&1; then
    log "STEP 3 CUDA toolkit: nvcc present -> using it"
  else
    log "STEP 3 CUDA toolkit: nvcc ABSENT -> installing CUDA TOOLKIT ONLY (driver untouched)"
    sudo apt-get install -y cuda-toolkit >> "$LOG" 2>&1 \
        || { log "ABORT: CUDA toolkit install failed; resolve toolkit source at review."; exit 1; }
    export PATH="/usr/local/cuda/bin:$PATH"
    nvcc --version >> "$LOG" 2>&1 \
        || { log "ABORT: nvcc still not found after toolkit install"; exit 1; }
  fi
  mark 03_cuda
fi

# ============================================================ STEP 4: OpenFOAM v2606
if done_marker 04_openfoam; then log "STEP 4 OpenFOAM: SKIP (done)"; else
  log "STEP 4 OpenFOAM v2606: install SAME version as the lab box"
  # NO `set -u` here: sourcing v2606 bashrc dies under set -u (measured).
  if test -f "/usr/lib/openfoam/${OF_VERSION}/etc/bashrc"; then
    log "STEP 4: ${OF_VERSION} already present"
  else
    curl -s https://dl.openfoam.com/add-debian-repo.sh | sudo bash >> "$LOG" 2>&1 \
        || { log "ABORT: openfoam.com repo add failed"; exit 1; }
    sudo apt-get update >> "$LOG" 2>&1 \
        || { log "ABORT: apt-get update (openfoam repo) failed"; exit 1; }
    sudo apt-get install -y "${OF_VERSION}-default" >> "$LOG" 2>&1 \
        || { log "ABORT: ${OF_VERSION} install failed"; exit 1; }
  fi
  # shellcheck disable=SC1090
  source "/usr/lib/openfoam/${OF_VERSION}/etc/bashrc" \
      || { log "ABORT: sourcing ${OF_VERSION} bashrc failed"; exit 1; }
  test -n "$WM_PROJECT_VERSION" \
      || { log "ABORT: WM_PROJECT_VERSION empty after sourcing bashrc"; exit 1; }
  log "STEP 4: OpenFOAM $WM_PROJECT_VERSION active"
  mark 04_openfoam
fi

# Re-source OpenFOAM for the steps below (markers may have skipped step 4).
# shellcheck disable=SC1090
source "/usr/lib/openfoam/${OF_VERSION}/etc/bashrc" \
    || { log "ABORT: re-sourcing ${OF_VERSION} bashrc failed"; exit 1; }

# ============================================================ STEP 5: PETSc --with-cuda
if done_marker 05_petsc; then log "STEP 5 PETSc: SKIP (done)"; else
  log "STEP 5 PETSc --with-cuda (sm_$CUDA_ARCH)"
  cd "$BUILD_ROOT" || { log "ABORT: cd $BUILD_ROOT"; exit 1; }
  test -d petsc || git clone --depth 1 --branch "$PETSC_TAG" \
      https://gitlab.com/petsc/petsc.git petsc >> "$LOG" 2>&1 \
      || { log "ABORT: PETSc clone (tag $PETSC_TAG) failed"; exit 1; }
  cd petsc || { log "ABORT: cd petsc"; exit 1; }
  export PETSC_DIR="$BUILD_ROOT/petsc" PETSC_ARCH="arch-cuda-opt"
  ./configure PETSC_ARCH="$PETSC_ARCH" --with-cuda --with-cuda-arch="$CUDA_ARCH" \
      --with-precision=double --download-fblaslapack --download-hypre --download-amgx \
      --with-mpi-dir="$(dirname "$(dirname "$(which mpicc)")")" >> "$LOG" 2>&1 \
      || { log "ABORT: PETSc configure --with-cuda failed"; exit 1; }
  make PETSC_DIR="$PETSC_DIR" PETSC_ARCH="$PETSC_ARCH" all >> "$LOG" 2>&1 \
      || { log "ABORT: PETSc make failed"; exit 1; }
  make PETSC_DIR="$PETSC_DIR" PETSC_ARCH="$PETSC_ARCH" check >> "$LOG" 2>&1 \
      || { log "ABORT: PETSc make check failed (CUDA example did not run)"; exit 1; }
  mark 05_petsc
fi
export PETSC_DIR="$BUILD_ROOT/petsc" PETSC_ARCH="arch-cuda-opt"

# ============================================================ STEP 6: petsc4Foam module
if done_marker 06_petsc4foam; then log "STEP 6 petsc4Foam: SKIP (done)"; else
  log "STEP 6 petsc4Foam module (tag $PETSC4FOAM_TAG matching $OF_VERSION)"
  cd "$BUILD_ROOT" || { log "ABORT: cd $BUILD_ROOT"; exit 1; }
  test -d petsc4Foam || git clone --depth 1 --branch "$PETSC4FOAM_TAG" \
      https://develop.openfoam.com/modules/external-solver.git petsc4Foam >> "$LOG" 2>&1 \
      || { log "ABORT: petsc4Foam clone (tag $PETSC4FOAM_TAG) failed"; exit 1; }
  cd petsc4Foam || { log "ABORT: cd petsc4Foam"; exit 1; }
  ./Allwmake >> "$LOG" 2>&1 \
      || { log "ABORT: petsc4Foam Allwmake failed against $OF_VERSION -- DO NOT fall back to a mismatched tag; report the compiler error above."; exit 1; }
  test -f "$FOAM_USER_LIBBIN/libpetscFoam.so" \
      || { log "ABORT: libpetscFoam.so not produced"; exit 1; }
  mark 06_petsc4foam
fi

# ============================================================ STEP 7: toolchain manifest
log "STEP 7 toolchain manifest"
MANIFEST="$BUILD_ROOT/TOOLCHAIN_MANIFEST.txt"
{
  echo "generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "driver:    $(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)"
  echo "gpu:       $(nvidia-smi -L | head -1)"
  echo "cuda_arch: sm_$CUDA_ARCH"
  echo "nvcc:      $(nvcc --version | tr '\n' ' ')"
  echo "openfoam:  $WM_PROJECT_VERSION"
  echo "petsc_tag: $PETSC_TAG  PETSC_ARCH=$PETSC_ARCH"
  echo "petsc_sha: $(git -C "$BUILD_ROOT/petsc" rev-parse HEAD 2>/dev/null)"
  echo "p4f_tag:   $PETSC4FOAM_TAG"
  echo "p4f_sha:   $(git -C "$BUILD_ROOT/petsc4Foam" rev-parse HEAD 2>/dev/null)"
  echo "libpetscFoam.so sha256: $(sha256sum "$FOAM_USER_LIBBIN/libpetscFoam.so" 2>/dev/null | awk '{print $1}')"
} > "$MANIFEST" 2>>"$LOG" || { log "ABORT: manifest write failed"; exit 1; }
log "STEP 7: manifest at $MANIFEST"
cat "$MANIFEST" | tee -a "$LOG"

# ============================================================ STEP 8: smoke test
log "STEP 8 smoke test: handing off to smoke_test_gpu_path.sh"
SMOKE="$(dirname "$0")/smoke_test_gpu_path.sh"
test -x "$SMOKE" || SMOKE="bash $(dirname "$0")/smoke_test_gpu_path.sh"
$SMOKE >> "$LOG" 2>&1 \
    || { log "ABORT: smoke test FAILED -- do NOT snapshot the AMI; GPU path unproven."; exit 1; }

log "=== build_gpu_solver.sh COMPLETE: GPU path built AND smoke-proven. AMI snapshot may proceed. ==="
exit 0
