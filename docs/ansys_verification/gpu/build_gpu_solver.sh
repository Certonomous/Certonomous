#!/usr/bin/env bash
# build_gpu_solver.sh — build the lab's GPU solver path (OpenFOAM v2606 + petsc4Foam
# + PETSc --with-cuda, cuSPARSE sm_89) on a FRESH g6.xlarge / NVIDIA L4 DLAMI.
#
# DRAFT, ansys-lane-opus48 for ansys-verification-supervisor, 2026-08-25. FIRST ARROW
# of Sanaa's sequence: this script is REVIEWED OFFLINE before any boot.
#
# PINNED AND REPAIRED 2026-08-26 by ansys-verification-supervisor personally, against what
# the instance (ubuntu@3.15.199.152, Ubuntu 26.04 "resolute", driver 595.91.07, gcc 15.2)
# actually offers — every pin carries its evidence line beside it. Launch authority:
# Sanaa's verbatim permission boarded at commit bc0e687e.
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
# Pins were placeholders in <ANGLE_BRACKETS>; the script still ABORTS on an unresolved
# pin rather than guessing (the check below is kept as a planted guard).

set -o pipefail   # pipefail is safe and wanted; `set -e`/`set -u` deliberately NOT set.

# PIN 2026-08-26T17:2xZ (supervisor, MEASURED on the first run, build_rc=1 at 17:15:07Z):
# ONE Open MPI for the whole toolchain -- Ubuntu's 5.0.10 (/usr/bin/mpicc; the openfoam2606
# package links WM_MPLIB=SYSTEMOPENMPI against it). The DLAMI's /etc/profile.d/dlami.sh exports
# LD_LIBRARY_PATH=/opt/amazon/openmpi/lib:... and PATH=/opt/amazon/openmpi/bin:..., so a binary
# compiled against Ubuntu's headers resolved libmpi.so.40 (SAME soname) to AWS Open MPI 4.1.7 at
# run time: `ldd libpetsc.so` and `ldd simpleFoam` both showed /opt/amazon/openmpi/lib, and
# PETSc `make check` died in MPI_Init ("opal_init failed"). With /usr/lib/x86_64-linux-gnu
# first, ldd resolves libmpi.so.40 -> /usr/lib/x86_64-linux-gnu (libopen-pal.so.80, libpmix.so.2).
# Every consumer (smoke test, case launchers) must source $BUILD_ROOT/env.sh (written at STEP 7).
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="/usr/bin:$PATH"

# ----------------------------------------------------------------------------- paths
BUILD_ROOT="${BUILD_ROOT:-$HOME/gpu_build}"
LOG="$BUILD_ROOT/build.log"
MARK="$BUILD_ROOT/markers"
OF_VERSION="openfoam2606"
# OF_BASHRC: the binary package's path by default; the source fallback in STEP 4 overwrites
# it and records it in $BUILD_ROOT/OF_BASHRC so a resumed run (markers) finds the same one.
OF_BASHRC="/usr/lib/openfoam/${OF_VERSION}/etc/bashrc"
test -f "$BUILD_ROOT/OF_BASHRC" && OF_BASHRC="$(cat "$BUILD_ROOT/OF_BASHRC")"
CUDA_ARCH="89"                       # NVIDIA L4 = Ada Lovelace, compute capability 8.9
# PIN 2026-08-26: newest v3.24.x release tag on gitlab.com/petsc (git ls-remote --tags from the
# lab box: v3.24.3, v3.24.4, v3.24.5, v3.24.6). Ubuntu 26.04's own petsc-dev is 3.24.4 (no CUDA).
PETSC_TAG="v3.24.6"
# PIN 2026-08-26: develop.openfoam.com/modules/external-solver.git publishes NO v2606 tag
# (git ls-remote --tags: newest is v2412); `main` is the v2606-era branch. The sha actually
# cloned is written to the toolchain manifest, so the pin is "main @ <measured sha>".
PETSC4FOAM_TAG="main"

mkdir -p "$BUILD_ROOT" "$MARK" || { echo "ABORT: cannot create $BUILD_ROOT"; exit 1; }

# ------------------------------------------------------------------------- utilities
log()  { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG"; }
done_marker() { test -f "$MARK/$1"; }
mark() { touch "$MARK/$1" || { echo "ABORT: cannot write marker $1"; exit 1; }; }

log "=== build_gpu_solver.sh START ==="
log "BUILD_ROOT=$BUILD_ROOT  OF_VERSION=$OF_VERSION  CUDA_ARCH=sm_$CUDA_ARCH  PETSC_TAG=$PETSC_TAG  PETSC4FOAM_TAG=$PETSC4FOAM_TAG"

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
      python3 >> "$LOG" 2>&1 \
      || { log "ABORT: apt-get install of build prereqs failed"; exit 1; }
  mark 02_osprereq
fi

# ============================================================ STEP 3: CUDA toolkit
# Detect nvcc; install the toolkit ONLY if absent. Never touch the DLAMI's driver.
# PIN 2026-08-26: the DLAMI carries a CUDA 13.0 nvcc only inside a PyTorch wheel directory
# (/opt/pytorch/lib/python3.13/site-packages/nvidia/cu13/bin/nvcc), off PATH and without a
# full toolkit layout, and gcc 15.2 is not a supported host compiler for it. Ubuntu 26.04's
# apt offers nvidia-cuda-toolkit 12.4.131 (apt-cache policy), whose package pulls g++-13 as
# the nvcc host compiler and installs /usr/bin/nvcc. Driver 595.91.07 supports CUDA 12.4.
if done_marker 03_cuda; then log "STEP 3 CUDA toolkit: SKIP (done)"; else
  if nvcc --version >> "$LOG" 2>&1; then
    log "STEP 3 CUDA toolkit: nvcc present -> using it"
  else
    log "STEP 3 CUDA toolkit: nvcc ABSENT -> installing nvidia-cuda-toolkit (apt, driver untouched)"
    sudo apt-get install -y nvidia-cuda-toolkit >> "$LOG" 2>&1 \
        || { log "ABORT: nvidia-cuda-toolkit install failed"; exit 1; }
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
    log "STEP 4: ${OF_VERSION} already present (binary)"
  elif test -f "$HOME/OpenFOAM/OpenFOAM-v2606/etc/bashrc" && test -x "$HOME/OpenFOAM/OpenFOAM-v2606/platforms/linux64GccDPInt32Opt/bin/simpleFoam"; then
    OF_BASHRC="$HOME/OpenFOAM/OpenFOAM-v2606/etc/bashrc"
    log "STEP 4: OpenFOAM-v2606 already built from source"
  else
    # Binary route first. MEASURED 2026-08-26: dl.openfoam.com lists a resolute/ dist but its
    # binary-amd64 Packages index returned no openfoam2606 entry when read from the instance,
    # so the apt route may fail here; it is tried, and the source build is the recorded fallback.
    if ( curl -s https://dl.openfoam.com/add-debian-repo.sh | sudo bash >> "$LOG" 2>&1 ) \
       && sudo apt-get update >> "$LOG" 2>&1 \
       && sudo apt-get install -y "${OF_VERSION}-default" >> "$LOG" 2>&1 \
       && test -f "/usr/lib/openfoam/${OF_VERSION}/etc/bashrc"; then
      OF_BASHRC="/usr/lib/openfoam/${OF_VERSION}/etc/bashrc"
      log "STEP 4: ${OF_VERSION} installed from dl.openfoam.com binaries"
    else
      log "STEP 4: binary install unavailable on this OS -> building OpenFOAM-v2606 from source (4 vCPU; hours)"
      mkdir -p "$HOME/OpenFOAM" || { log "ABORT: cannot make $HOME/OpenFOAM"; exit 1; }
      cd "$HOME/OpenFOAM" || { log "ABORT: cd $HOME/OpenFOAM"; exit 1; }
      if ! test -d OpenFOAM-v2606; then
        curl -sL https://dl.openfoam.com/source/v2606/OpenFOAM-v2606.tgz -o OpenFOAM-v2606.tgz \
            || { log "ABORT: OpenFOAM-v2606 source download failed"; exit 1; }
        tar xzf OpenFOAM-v2606.tgz >> "$LOG" 2>&1 \
            || { log "ABORT: OpenFOAM-v2606 source unpack failed"; exit 1; }
      fi
      test -d OpenFOAM-v2606 || { log "ABORT: source tree absent after download"; exit 1; }
      OF_BASHRC="$HOME/OpenFOAM/OpenFOAM-v2606/etc/bashrc"
      ( source "$OF_BASHRC" && cd "$WM_PROJECT_DIR" && ./Allwmake -j 4 -s -q -l ) >> "$LOG" 2>&1 \
          || { log "ABORT: OpenFOAM-v2606 source build failed (see $LOG)"; exit 1; }
    fi
  fi
  echo "$OF_BASHRC" > "$BUILD_ROOT/OF_BASHRC" || { log "ABORT: cannot record OF_BASHRC"; exit 1; }
  # shellcheck disable=SC1090
  source "$OF_BASHRC" \
      || { log "ABORT: sourcing $OF_BASHRC failed"; exit 1; }
  test -n "$WM_PROJECT_VERSION" \
      || { log "ABORT: WM_PROJECT_VERSION empty after sourcing bashrc"; exit 1; }
  command -v simpleFoam >/dev/null \
      || { log "ABORT: simpleFoam not on PATH after sourcing $OF_BASHRC"; exit 1; }
  log "STEP 4: OpenFOAM $WM_PROJECT_VERSION active from $OF_BASHRC"
  mark 04_openfoam
fi

# Re-source OpenFOAM for the steps below (markers may have skipped step 4).
test -f "$BUILD_ROOT/OF_BASHRC" && OF_BASHRC="$(cat "$BUILD_ROOT/OF_BASHRC")"
# shellcheck disable=SC1090
source "$OF_BASHRC" \
    || { log "ABORT: re-sourcing $OF_BASHRC failed"; exit 1; }

# ============================================================ STEP 5: PETSc --with-cuda
if done_marker 05_petsc; then log "STEP 5 PETSc: SKIP (done)"; else
  log "STEP 5 PETSc --with-cuda (sm_$CUDA_ARCH)"
  # PIN 2026-08-26: --download-hypre and --download-amgx REMOVED from the first build. AmgX is the
  # recipe's ESCALATION route (§2), not the selected one, and each is an additional multi-hour CUDA
  # compile on 4 vCPU that can sink the whole build. Add in a later build if a case needs it.
  cd "$BUILD_ROOT" || { log "ABORT: cd $BUILD_ROOT"; exit 1; }
  test -d petsc || git clone --depth 1 --branch "$PETSC_TAG" \
      https://gitlab.com/petsc/petsc.git petsc >> "$LOG" 2>&1 \
      || { log "ABORT: PETSc clone (tag $PETSC_TAG) failed"; exit 1; }
  cd petsc || { log "ABORT: cd petsc"; exit 1; }
  export PETSC_DIR="$BUILD_ROOT/petsc" PETSC_ARCH="arch-cuda-opt"
  ./configure PETSC_ARCH="$PETSC_ARCH" --with-cuda --with-cuda-arch="$CUDA_ARCH" \
      --with-cudac="$(command -v nvcc)" --with-precision=double --download-fblaslapack \
      --with-debugging=0 \
      --with-mpi-dir="$(dirname "$(dirname "$(which mpicc)")")" >> "$LOG" 2>&1 \
      || { log "ABORT: PETSc configure --with-cuda failed"; exit 1; }
  make PETSC_DIR="$PETSC_DIR" PETSC_ARCH="$PETSC_ARCH" all >> "$LOG" 2>&1 \
      || { log "ABORT: PETSc make failed"; exit 1; }
  make PETSC_DIR="$PETSC_DIR" PETSC_ARCH="$PETSC_ARCH" check >> "$LOG" 2>&1 \
      || { log "ABORT: PETSc make check failed (CUDA example did not run)"; exit 1; }
  mark 05_petsc
fi
export PETSC_DIR="$BUILD_ROOT/petsc" PETSC_ARCH="arch-cuda-opt"
# What OpenFOAM's etc/config.sh/petsc and the petsc4Foam Allwmake read to find the library.
export PETSC_ARCH_PATH="$PETSC_DIR/$PETSC_ARCH"

# ============================================================ STEP 6: petsc4Foam module
if done_marker 06_petsc4foam; then log "STEP 6 petsc4Foam: SKIP (done)"; else
  log "STEP 6 petsc4Foam module (branch $PETSC4FOAM_TAG against $OF_VERSION)"
  cd "$BUILD_ROOT" || { log "ABORT: cd $BUILD_ROOT"; exit 1; }
  test -d petsc4Foam || git clone --depth 1 --branch "$PETSC4FOAM_TAG" \
      https://develop.openfoam.com/modules/external-solver.git petsc4Foam >> "$LOG" 2>&1 \
      || { log "ABORT: petsc4Foam clone (branch $PETSC4FOAM_TAG) failed"; exit 1; }
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
  echo "openfoam:  $WM_PROJECT_VERSION ($OF_BASHRC)"
  echo "petsc_tag: $PETSC_TAG  PETSC_ARCH=$PETSC_ARCH"
  echo "petsc_sha: $(git -C "$BUILD_ROOT/petsc" rev-parse HEAD 2>/dev/null)"
  echo "p4f_tag:   $PETSC4FOAM_TAG"
  echo "p4f_sha:   $(git -C "$BUILD_ROOT/petsc4Foam" rev-parse HEAD 2>/dev/null)"
  echo "libpetscFoam.so sha256: $(sha256sum "$FOAM_USER_LIBBIN/libpetscFoam.so" 2>/dev/null | awk '{print $1}')"
  echo "mpicc:     $(command -v mpicc) -- $(mpicc --showme:version 2>/dev/null | head -1)"
  echo "libmpi (petsc):      $(ldd "$PETSC_ARCH_PATH/lib/libpetsc.so" 2>/dev/null | awk '/libmpi\.so/{print $3}')"
  echo "libmpi (petscFoam):  $(ldd "$FOAM_USER_LIBBIN/libpetscFoam.so" 2>/dev/null | awk '/libmpi\.so/{print $3}')"
  echo "libmpi (simpleFoam): $(ldd "$(command -v simpleFoam)" 2>/dev/null | awk '/libmpi\.so/{print $3}')"
  echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
} > "$MANIFEST" 2>>"$LOG" || { log "ABORT: manifest write failed"; exit 1; }
# The three libmpi lines above MUST agree (one MPI for the whole toolchain) -- refuse otherwise.
NMPI="$(grep -E '^libmpi ' "$MANIFEST" | awk '{print $NF}' | sort -u | wc -l)"
test "$NMPI" = "1" || { log "ABORT: mixed MPI runtimes in manifest ($NMPI distinct libmpi paths); see the 2026-08-26 pin"; exit 1; }
# Environment every consumer sources (smoke test, case launchers): the pin, OpenFOAM, PETSc.
{
  echo "# written by build_gpu_solver.sh STEP 7 on $(date -u +%Y-%m-%dT%H:%M:%SZ); source, never execute"
  echo "export LD_LIBRARY_PATH=\"/usr/lib/x86_64-linux-gnu\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}\""
  echo "export PATH=\"/usr/bin:\$PATH\""
  echo "export OF_BASHRC=\"$OF_BASHRC\""
  echo "export PETSC_DIR=\"$PETSC_DIR\" PETSC_ARCH=\"$PETSC_ARCH\" PETSC_ARCH_PATH=\"$PETSC_ARCH_PATH\""
} > "$BUILD_ROOT/env.sh" || { log "ABORT: cannot write $BUILD_ROOT/env.sh"; exit 1; }
log "STEP 7: manifest at $MANIFEST; env at $BUILD_ROOT/env.sh"
cat "$MANIFEST" | tee -a "$LOG"

# ============================================================ STEP 8: smoke test
log "STEP 8 smoke test: handing off to smoke_test_gpu_path.sh"
SMOKE="$(dirname "$0")/smoke_test_gpu_path.sh"
test -x "$SMOKE" || SMOKE="bash $(dirname "$0")/smoke_test_gpu_path.sh"
SMOKE_CASE_SRC="$BUILD_ROOT/smoke_case" OF_BASHRC="$OF_BASHRC" $SMOKE >> "$LOG" 2>&1 \
    || { log "ABORT: smoke test FAILED -- do NOT snapshot the AMI; GPU path unproven."; exit 1; }

log "=== build_gpu_solver.sh COMPLETE: GPU path built AND smoke-proven. AMI snapshot may proceed. ==="
exit 0
