#!/usr/bin/env bash
# ============================================================================
# run_vmflgpu001_r2.sh -- VMFLGPU001 graded-run driver.
#
# Flow Between Rotating and Stationary Concentric Cylinders, manual p.225.
# CPU PARENT: VMFL001 / VMFL001-R2.  Object under verification: THE LAB'S GPU
# SOLVER PATH (OpenFOAM v2606 + petsc4Foam + PETSc-CUDA on the L4).
#
# THIS SCRIPT RUNS **ON THE GPU INSTANCE**, never on the lab box.  It builds and
# runs SIX solves: three mesh levels x two arms.
#
#     GPU arm             mat_type aijcusparse  vec_type cuda      (the object)
#     forced-CPU control  mat_type aij          vec_type standard  (limb A's
#                         discriminator AND limb B's baseline, one run serving
#                         both -- it IS the forced-CPU control by construction)
#
# IT GRADES NOTHING.  Grading is grade_vmflgpu001.py, frozen separately and
# cited by sha in PREREGISTRATION.md.
#
# ---------------------------------------------------------------------------
# HAZARDS, EACH MEASURED BY THIS LAB, EACH NAMED HERE BECAUSE A COMMENT IS THE
# ONLY PLACE THE NEXT AUTHOR WILL LOOK (L-339):
#
#  * NO `set -u`.  CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606: etc/bashrc
#    dereferences WM_PROJECT_DIR at its line 184 BEFORE assigning it, and
#    config.sh/functions unsets WM_SHELL_FUNCTIONS then dereferences it.
#    MEASURED: `bash -c 'set -u; . <bashrc>'` -> rc 127; without `set -u` -> rc 0.
#    Two frozen launchers of this team shipped `set -u` and aborted before any
#    compute (PREREG_TEMPLATE Amendment 3).
#  * NO `set -e`.  It does NOT gate at a Bash tool's top level, and
#    `( set -e; ... )` fails silently.  EVERY step below gates EXPLICITLY with
#    `|| { echo "ABORT: ..."; exit 1; }`.  A check that only prints is not one.
#  * THE SOLVER'S rc IS CAPTURED INSIDE THIS SCRIPT, from `$?`, and written to
#    BOTH $RUN_ROOT/RUN_RC.<level>.<arm> and <level>/RUN_RC.txt by one
#    statement.  An earlier draft of this launcher refused to use `timeout` at
#    all, citing a note that "`setsid` and `timeout` were MEASURED returning 0
#    for every outcome (4225ef0c, 83769288)".  THAT NOTE IS ABOUT A
#    BACKGROUNDED/`setsid` INVOCATION, NOT ABOUT `timeout` ITSELF, and this
#    launcher does not judge a tool by a note about its shape: STEP 0c DRIVES
#    `timeout` on the host, before any solver, and REFUSES (exit 2) unless a
#    child exiting 7 comes back as 7 and an overrun comes back as 124.
#    MEASURED on the lab box 2026-08-26, GNU coreutils 9.4: 7 and 124.  The cap
#    is therefore enforced IN THE EXECUTABLE PATH as PREREG_TEMPLATE Amendment 3
#    item 2 requires, and CLAUDE.md rule 12's "an overrun STOPS the run" is a
#    fact about this script rather than a sentence in a comment.
#  * TIME DIRECTORIES ARE MATCHED BY A DRIVEN REGEX, NOT A GLOB.  `[0-9]*`
#    matches `0.orig` and misses nothing it should (L-339); the test below is
#    `[[ $name =~ ^[0-9]+([.][0-9]*)?([eE][+-]?[0-9]+)?$ ]]`, and the guard is
#    driven against `0.orig` in the pre-freeze dry run recorded in
#    PREREGISTRATION.md section 13.
#  * FIELD COMPLETENESS IS CHECKED AGAINST THE CONSUMER'S ACTUAL CONFIGURATION,
#    never against a regex surface (PREREG_TEMPLATE Amendment 5 item 1 as
#    refined by Amendment 5a): fvSolution's solver-block keys INTERSECT the
#    fields the closure named in constant/turbulenceProperties creates, MINUS
#    phi, and every lookup accepts `X` or `X.gz`.
#  * BOOKKEEPING NEVER VOIDS PHYSICS (L-342, Sanaa's universal rule).  After a
#    solver has completed, a failed bookkeeping write is a WARNING and the exit
#    code STAYS THE SOLVER'S rc.  Before any solver runs, the freeze check and
#    the mesh birth certificate are PHYSICS-CRITICAL and do abort.
#
# EXECUTE this script (`bash run_vmflgpu001_r2.sh <run_root>`); NEVER `source` it.
# ============================================================================
set -o pipefail   # wanted and safe. `set -e` / `set -u` deliberately NOT set.

CASE_ID="VMFLGPU001-R2"
RANKS=1                       # serial; core-minutes = wall_s * RANKS / 60
CAP_GPU_H=2.0                 # FROZEN in PREREGISTRATION.md section 12.
CAP_CPU_ARM_CORE_MIN=40       # FROZEN in PREREGISTRATION.md section 12.
# name:NR:NAZB:ENDTIME  -- NR radial cells, NAZB azimuthal per 90-deg block,
# total cells = 4*NR*NAZB.  Per-level endTime inherited from VMFL001-R2.
LEVELS="L1_16x64:16:16:3000 L2_32x128:32:32:3000 L3_64x256:64:64:6000"

GPU_MAT="aijcusparse"; GPU_VEC="cuda"
CPU_MAT="aij";         CPU_VEC="standard"
# AMENDMENT 1 (PRE-COMPUTE, 2026-08-26T17:38Z).  These are the options THIS CASE
# owns.  The FULL PETSC_OPTIONS handed to each solve is composed AFTER
# $BUILD_ROOT/env.sh is sourced, as "$PETSC_OPTIONS_BASE <shared> <arm-specific>",
# so the build's own base value is APPENDED TO, NEVER OVERWRITTEN.
#
# `-use_gpu_aware_mpi 0` is SHARED BY BOTH ARMS so that the two arms differ ONLY
# in mat_type/vec_type -- which is the whole basis on which limb B is a statement
# about WHERE the linear algebra ran and about nothing else.
#
# MEASURED on ip-172-31-44-162 at 17:33:50Z, in the smoke test's OWN GPU run:
# simpleFoam printed "Initializing PETSc... success", ran 0.22 s, then
#   [0]PETSC ERROR: PETSc is configured with GPU support, but your MPI is not
#   GPU-aware. ... If you do not care, add option -use_gpu_aware_mpi 0
# followed by MPI_ABORT errorcode 76.  PETSc REFUSES TO PROCEED rather than
# quietly staging device buffers through the host.  Ubuntu's Open MPI 5.0.10 --
# the ONE MPI the whole stack is now correctly pinned to -- is not built
# --with-cuda.  THIS CASE RUNS AT ONE RANK, so the device-to-device MPI transfer
# path the option governs is NEVER EXERCISED here: the option declines a
# PERFORMANCE feature, not a correctness one, and it cannot move a number.
# Without it every GPU solve would abort at rc 76 before writing a field.
SHARED_PETSC_OPTIONS="-use_gpu_aware_mpi 0"
GPU_OWN_PETSC_OPTIONS="-ksp_view -log_view -log_view_gpu_time"
CPU_OWN_PETSC_OPTIONS="-ksp_view -log_view"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_SRC="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmflgpu001_r2.sh <run_root>}"
BUILD_ROOT="${BUILD_ROOT:-$HOME/gpu_build}"
REPO="${REPO:-$HOME/Certonomous}"
PREREG_REL="cases/ansys_verification/VMFLGPU001-R2/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFLGPU001-R2/grade_vmflgpu001_r2.py"

T_START=$(date +%s)
log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ${CASE_ID}: $*"; }
warn_infra() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ${CASE_ID}: WARNING(INFRASTRUCTURE): $*"; }

log "=== START (run_root=$RUN_ROOT build_root=$BUILD_ROOT repo=$REPO) ==="

# ---------------------------------------------------------------------------
# STEP 0  THE SMOKE GATE -- REFUSES AT ZERO COMPUTE (exit 2)
#
#   This case's WHOLE OBJECT is the GPU solver path.  If that path has not been
#   PROVEN on this instance, every solve below is at best a CPU number wearing a
#   GPU case's name -- and limb A would then have to discover after the fact what
#   this check settles before a single cell is meshed.  So the launcher refuses,
#   here, at the top, having spent nothing:
#
#     * $BUILD_ROOT/STATUS.smoke must READ `smoke_rc=0` as its FIRST FIELD
#       (the writer appends `end=` and `note=`).  It is written by the
#       supervisor's build wrapper from the rc of build_gpu_solver.sh STEP 8,
#       which is smoke_test_gpu_path.sh -- the script whose forced-CPU control
#       IS the discriminator (SUPERVISOR_REVIEW.md lines 27-44).  A smoke test
#       run WITHOUT it certifies nothing: absent, unreadable or rc != 0 REFUSE.
#     * $BUILD_ROOT/TOOLCHAIN_MANIFEST.txt must EXIST.  It is build_gpu_solver.sh
#       STEP 7's record of WHICH OpenFOAM, WHICH PETSc sha, WHICH petsc4Foam sha
#       and WHICH libpetscFoam.so the proof was obtained against.  A proof whose
#       toolchain cannot be named is not evidence about any particular toolchain.
#
#   MEASURED HAZARD RECORDED IN THE FREEZE (supervisor, 2026-08-26T17:15:07Z):
#   on the GPU instance the PETSc CUDA build COMPILED but `make check` FAILED --
#   Open MPI's runtime could not initialise (`opal_init failed`), because the
#   DLAMI carries AWS Open MPI 4.1.7 under /opt/amazon BESIDE Ubuntu's openmpi
#   5.0.10 from apt.  A mixed-MPI toolchain is exactly the "internally perfect,
#   externally false" shape (PREREG_TEMPLATE Amendment 5): every package
#   installed, nothing able to run.  STATUS.smoke reading smoke_rc=0 is what
#   settles it, because the smoke test EXECUTES the path; and STEP 0b below
#   refuses unless the manifest names ONE MPI, resolvable, for the whole stack.
#
#   exit 2, not 1, and deliberately: this is a REFUSAL to certify, of the same
#   kind the comparator's refuse() uses, not a failure of a step.
# ---------------------------------------------------------------------------
STATUS_SMOKE="$BUILD_ROOT/STATUS.smoke"
MANIFEST="$BUILD_ROOT/TOOLCHAIN_MANIFEST.txt"
test -f "$STATUS_SMOKE" \
    || { echo "REFUSE (exit 2): $STATUS_SMOKE is absent. The GPU solver path has not been PROVEN on this instance, so nothing this script could run would be evidence about it. Run build_gpu_solver.sh (its STEP 8 is smoke_test_gpu_path.sh) and try again."; exit 2; }
grep -Eq '^[[:space:]]*smoke_rc[[:space:]]*=[[:space:]]*0([[:space:]]|$)' "$STATUS_SMOKE" \
    || { echo "REFUSE (exit 2): $STATUS_SMOKE does not read smoke_rc=0. Contents follow, and this script does not interpret them charitably:"; sed -e 's/^/    | /' "$STATUS_SMOKE"; exit 2; }
test -f "$MANIFEST" \
    || { echo "REFUSE (exit 2): $MANIFEST is absent. A GPU-path proof whose toolchain cannot be NAMED (OpenFOAM, PETSc sha, petsc4Foam sha, libpetscFoam.so sha256) is not evidence about any particular toolchain."; exit 2; }
BUILD_ENV="$BUILD_ROOT/env.sh"
test -f "$BUILD_ENV" \
    || { echo "REFUSE (exit 2): $BUILD_ENV is absent. build_gpu_solver.sh STEP 7 writes it, and it carries THE MPI PIN this stack must run under. TRIAGED AND MEASURED 2026-08-26T17:15:07Z: the DLAMI PREPENDS /opt/amazon/openmpi (AWS Open MPI 4.1.7) to PATH and LD_LIBRARY_PATH, SHADOWING Ubuntu's Open MPI 5.0.10 that OpenFOAM and PETSc were compiled against -- SAME SONAME libmpi.so.40, so the linker resolves it silently and PETSc died in MPI_Init (opal_init failed). Without the pin this launcher would run the solver against an MPI the toolchain was not built for, which is NOT the toolchain under verification."; exit 2; }
# Printed INSIDE the branch that verified it (PREREG_TEMPLATE Amendment 6a item 1).
log "SMOKE GATE PASSED: $STATUS_SMOKE reads smoke_rc=0, $MANIFEST exists, $BUILD_ENV exists"

# ---------------------------------------------------------------------------
# STEP 0c  THE CAP MECHANISM IS DRIVEN BEFORE IT IS TRUSTED (L-339)
#
# The per-solve cap below is enforced with `timeout`, and the rc is captured
# INSIDE this script.  An earlier draft of this launcher refused to use
# `timeout` at all, on a recorded note that "`setsid` and `timeout` were
# MEASURED returning 0 for every outcome (4225ef0c, 83769288)".  That note is
# about a BACKGROUNDED/`setsid` invocation, not about `timeout` itself, and
# judging the tool by that note is judging a pattern by its shape.  So this
# script DRIVES it, here, on THIS host, before relying on it -- two seconds of
# CPU and no solver:
#
#   timeout <t> <cmd that exits 7>   MUST return 7    (the child's rc passes through)
#   timeout 1 <cmd that sleeps 3>    MUST return 124  (the cap fired)
#
# MEASURED ON THE LAB BOX 2026-08-26 with GNU coreutils 9.4: 7 and 124
# respectively, and 0 for a clean child.  If this host disagrees, the cap
# cannot be enforced as registered and the script REFUSES rather than running
# six solves under a guard it has not shown works.
# ---------------------------------------------------------------------------
command -v timeout >/dev/null \
    || { echo "REFUSE (exit 2): \`timeout\` is not on PATH, so the per-solve cap registered in PREREGISTRATION.md section 12 cannot be enforced in the executable path (PREREG_TEMPLATE Amendment 3 item 2)."; exit 2; }
timeout 10 bash -c 'exit 7'; TO_RC_PASS=$?
timeout 1  bash -c 'sleep 3'; TO_RC_KILL=$?
if [ "$TO_RC_PASS" != "7" ] || [ "$TO_RC_KILL" != "124" ]; then
  echo "REFUSE (exit 2): \`timeout\` does not behave as the cap requires on this host -- a child exiting 7 came back as $TO_RC_PASS (expected 7) and a child that overran came back as $TO_RC_KILL (expected 124). The cap would be unenforceable or the solver rc unreadable, and this script does not run six solves behind a guard it cannot demonstrate."
  exit 2
fi
# Printed INSIDE the branch that verified it (Amendment 6a item 1).
log "CAP MECHANISM DRIVEN: timeout passes a child rc through (7) and reports an overrun as 124 on this host"

# ---------------------------------------------------------------------------
# STEP 1  LAUNCH-TIME FREEZE CHECK -- PHYSICS-CRITICAL, NON-DROPPABLE
#         (CLAUDE.md rule 2; PREREG_TEMPLATE Amendment 2)
#         The pre-registration AND the comparator on disk MUST be the blobs
#         committed at HEAD.  An unverified freeze is no freeze, so this
#         script REFUSES to run where it cannot prove the freeze -- it does
#         not "carry on without the check".
# ---------------------------------------------------------------------------
git -C "$REPO" rev-parse --show-toplevel >/dev/null 2>&1 \
    || { echo "ABORT: no git repository at REPO=$REPO. The launch-time freeze check (PREREG_TEMPLATE Amendment 2) is NON-DROPPABLE: this script cannot prove the pre-registration and the comparator are the committed blobs, so it refuses to start a solver. Put a clone of Certonomous at \$REPO on this instance, or pass REPO=<path>."; exit 1; }
git -C "$REPO" cat-file -e "HEAD:$PREREG_REL" 2>/dev/null \
    || { echo "ABORT: $PREREG_REL is not committed at HEAD -- the freeze is the evidence"; exit 1; }
git -C "$REPO" cat-file -e "HEAD:$GRADER_REL" 2>/dev/null \
    || { echo "ABORT: $GRADER_REL is not committed at HEAD"; exit 1; }
PREREG_HEAD="$(git -C "$REPO" rev-parse "HEAD:$PREREG_REL")" || { echo "ABORT: cannot resolve HEAD:$PREREG_REL"; exit 1; }
GRADER_HEAD="$(git -C "$REPO" rev-parse "HEAD:$GRADER_REL")" || { echo "ABORT: cannot resolve HEAD:$GRADER_REL"; exit 1; }
PREREG_DISK="$(git -C "$REPO" hash-object "$REPO/$PREREG_REL")" || { echo "ABORT: cannot hash $PREREG_REL on disk"; exit 1; }
GRADER_DISK="$(git -C "$REPO" hash-object "$REPO/$GRADER_REL")" || { echo "ABORT: cannot hash $GRADER_REL on disk"; exit 1; }
[ "$PREREG_DISK" = "$PREREG_HEAD" ] || { echo "ABORT: $PREREG_REL on disk ($PREREG_DISK) differs from HEAD ($PREREG_HEAD)"; exit 1; }
[ "$GRADER_DISK" = "$GRADER_HEAD" ] || { echo "ABORT: $GRADER_REL on disk ($GRADER_DISK) differs from HEAD ($GRADER_HEAD)"; exit 1; }
HEAD_SHA="$(git -C "$REPO" rev-parse HEAD)" || { echo "ABORT: cannot resolve HEAD"; exit 1; }
# Printed INSIDE the branch that verified it: deleting the checks deletes the claim
# (PREREG_TEMPLATE Amendment 6a item 1).
log "FREEZE VERIFIED: prereg $PREREG_HEAD ; comparator $GRADER_HEAD ; HEAD $HEAD_SHA"

mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
{ echo "case_id = $CASE_ID"
  echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "head = $HEAD_SHA"
  echo "prereg = $PREREG_REL"
  echo "prereg_sha_head = $PREREG_HEAD"
  echo "prereg_sha_disk = $PREREG_DISK"
  echo "comparator = $GRADER_REL"
  echo "comparator_sha_head = $GRADER_HEAD"
  echo "comparator_sha_disk = $GRADER_DISK"
  echo "host = $(hostname)"
} > "$RUN_ROOT/LAUNCH_RECORD.txt" || { echo "ABORT: cannot write $RUN_ROOT/LAUNCH_RECORD.txt"; exit 1; }

# ---------------------------------------------------------------------------
# STEP 2  ENVIRONMENT -- sourced EXACTLY as build_gpu_solver.sh recorded it
# ---------------------------------------------------------------------------
test -f "$BUILD_ROOT/OF_BASHRC" \
    || { echo "ABORT: $BUILD_ROOT/OF_BASHRC absent -- build_gpu_solver.sh records the OpenFOAM bashrc it actually used there (binary or source build); this script never guesses the path"; exit 1; }
OF_BASHRC="$(cat "$BUILD_ROOT/OF_BASHRC")" || { echo "ABORT: cannot read $BUILD_ROOT/OF_BASHRC"; exit 1; }
test -f "$OF_BASHRC" || { echo "ABORT: recorded OF_BASHRC ($OF_BASHRC) does not exist"; exit 1; }
# THE MPI PIN GOES FIRST, BEFORE OpenFOAM'S BASHRC.  env.sh puts
# /usr/lib/x86_64-linux-gnu ahead of /opt/amazon/openmpi on LD_LIBRARY_PATH and
# /usr/bin ahead of it on PATH, so the libmpi.so.40 the linker hands to
# OpenFOAM, PETSc and petsc4Foam is the ONE they were compiled against.  Sourced
# BEFORE the bashrc because the bashrc's own MPI selection reads PATH.
# shellcheck disable=SC1090
source "$BUILD_ENV" || { echo "ABORT: sourcing $BUILD_ENV failed -- the MPI pin is not in force and this launcher will not run the solver on an unpinned MPI"; exit 1; }
# ---- USER: the bashrc DEFAULTS it, and cron does not set it -----------------
# MEASURED 2026-08-26T22:10:08Z: under the cron-restarted queue runner (its environ
# carries LOGNAME=ubuntu and HOME, and NO USER) $OF_BASHRC:190 sets
# WM_PROJECT_USER_DIR="$HOME/$WM_PROJECT/${USER:-user}-$WM_PROJECT_VERSION", so
# FOAM_USER_LIBBIN became the PHANTOM .../user-v2606/... and STEP 2a aborted -- while
# petsc4Foam is built into .../ubuntu-v2606/... .  Set BEFORE the bashrc reads it.
export USER="${USER:-${LOGNAME:-$(id -un)}}"
export LOGNAME="${LOGNAME:-$USER}"
# shellcheck disable=SC1090
source "$OF_BASHRC" || { echo "ABORT: sourcing $OF_BASHRC failed"; exit 1; }
test -n "$WM_PROJECT_VERSION" || { echo "ABORT: WM_PROJECT_VERSION empty after sourcing $OF_BASHRC"; exit 1; }

# ---- compose PETSC_OPTIONS: APPEND to the build's base, never overwrite ------
# env.sh may export a PETSC_OPTIONS the build proved the toolchain on.  Dropping
# it would run the solver under options the smoke test never exercised, which is
# precisely the "prove one thing, run another" shape this family exists to avoid.
PETSC_OPTIONS_BASE="${PETSC_OPTIONS}"
GPU_PETSC_OPTIONS="$PETSC_OPTIONS_BASE $SHARED_PETSC_OPTIONS $GPU_OWN_PETSC_OPTIONS"
CPU_PETSC_OPTIONS="$PETSC_OPTIONS_BASE $SHARED_PETSC_OPTIONS $CPU_OWN_PETSC_OPTIONS"
case "$GPU_PETSC_OPTIONS" in
  *-use_gpu_aware_mpi*) ;;
  *) echo "ABORT: -use_gpu_aware_mpi is missing from the composed GPU options; the measured 17:33:50Z MPI_ABORT (errorcode 76) would recur"; exit 1;;
esac
log "PETSC_OPTIONS composed: base='$PETSC_OPTIONS_BASE' ; gpu='$GPU_PETSC_OPTIONS' ; cpu='$CPU_PETSC_OPTIONS'"
command -v simpleFoam >/dev/null || { echo "ABORT: simpleFoam not on PATH after sourcing $OF_BASHRC"; exit 1; }
command -v blockMesh  >/dev/null || { echo "ABORT: blockMesh not on PATH"; exit 1; }
command -v checkMesh  >/dev/null || { echo "ABORT: checkMesh not on PATH"; exit 1; }
command -v python3    >/dev/null || { echo "ABORT: python3 not on PATH (needed for the cost arithmetic and the consumer-side field enumeration)"; exit 1; }

# EXACTLY as build_gpu_solver.sh exports them (its STEP 5/6 block).
export PETSC_DIR="$BUILD_ROOT/petsc"
export PETSC_ARCH="arch-cuda-opt"
export PETSC_ARCH_PATH="$PETSC_DIR/$PETSC_ARCH"
test -d "$PETSC_ARCH_PATH" || { echo "ABORT: PETSC_ARCH_PATH=$PETSC_ARCH_PATH is not a directory -- the PETSc build is not where build_gpu_solver.sh puts it"; exit 1; }
test -f "$FOAM_USER_LIBBIN/libpetscFoam.so" \
    || { echo "ABORT: libpetscFoam.so not found in FOAM_USER_LIBBIN=$FOAM_USER_LIBBIN -- petsc4Foam is not built for this OpenFOAM"; exit 1; }
# ---- STEP 2b  ONE MPI, RESOLVED, SHARED BY THE WHOLE STACK ----------------
# PHYSICS-CRITICAL for limb A, and paid for by a MEASURED failure on this very
# instance (supervisor, 2026-08-26T17:15:07Z): the PETSc CUDA build COMPILED and
# then `make check` FAILED with `opal_init failed` -- Open MPI could not
# initialise, because the DLAMI carries AWS Open MPI 4.1.7 under /opt/amazon
# BESIDE Ubuntu's openmpi 5.0.10 from apt.  Two Open MPIs on one box is the
# "internally perfect, externally false" shape of PREREG_TEMPLATE Amendment 5:
# every package installed, and nothing able to run.
#
# THE CHECK IS DRIVEN, NOT DECLARED (L-339): it does not read a manifest line
# claiming an MPI, it RESOLVES the libmpi.so that the dynamic linker actually
# hands to each of the three consumers -- OpenFOAM's Pstream binding, PETSc, and
# petsc4Foam -- and refuses unless all three realpath to THE SAME FILE.  A stack
# whose three halves load two MPIs cannot be shown to have run anything.
mpi_of_lib() { ldd "$1" 2>/dev/null | awk '/libmpi\.so/ {print $3}' | head -1; }
OF_PSTREAM="$FOAM_LIBBIN/$FOAM_MPI/libPstream.so"
PETSC_SO="$PETSC_ARCH_PATH/lib/libpetsc.so"
P4F_SO="$FOAM_USER_LIBBIN/libpetscFoam.so"
for f in "$OF_PSTREAM" "$PETSC_SO" "$P4F_SO"; do
  test -f "$f" || { echo "REFUSE (exit 2): $f is absent, so the MPI the stack actually loads cannot be RESOLVED for it. Limb A rests on the three halves of this toolchain being one toolchain; that cannot be shown here."; exit 2; }
done
MPI_OF="$(mpi_of_lib "$OF_PSTREAM")"
MPI_PETSC="$(mpi_of_lib "$PETSC_SO")"
MPI_P4F="$(mpi_of_lib "$P4F_SO")"
for pair in "OpenFOAM/libPstream:$MPI_OF" "PETSc/libpetsc:$MPI_PETSC" "petsc4Foam/libpetscFoam:$MPI_P4F"; do
  case "$pair" in
    *:) echo "REFUSE (exit 2): ${pair%%:*} resolves NO libmpi.so. This launcher will not name an MPI it cannot resolve (L-339: drive the pattern, do not judge its shape)."; exit 2;;
  esac
done
MPI_OF_R="$(readlink -f "$MPI_OF")"; MPI_PETSC_R="$(readlink -f "$MPI_PETSC")"; MPI_P4F_R="$(readlink -f "$MPI_P4F")"
if [ "$MPI_OF_R" != "$MPI_PETSC_R" ] || [ "$MPI_OF_R" != "$MPI_P4F_R" ]; then
  echo "REFUSE (exit 2): THE STACK LOADS MORE THAN ONE MPI."
  echo "    OpenFOAM/libPstream    -> $MPI_OF_R"
  echo "    PETSc/libpetsc         -> $MPI_PETSC_R"
  echo "    petsc4Foam/libpetscFoam-> $MPI_P4F_R"
  echo "    This is the measured 2026-08-26T17:15:07Z hazard (AWS Open MPI 4.1.7 under /opt/amazon beside Ubuntu openmpi 5.0.10). Rebuild the stack against ONE MPI; do not run this case on a mixed one."
  exit 2
fi
# simpleFoam itself usually resolves MPI only through libPstream, so an EMPTY
# result here is normal and is NOT treated as a failure; a NON-empty one that
# disagrees IS, because then the solver binary is loading a second MPI.
MPI_SF="$(mpi_of_lib "$(command -v simpleFoam)")"
if [ -n "$MPI_SF" ] && [ "$(readlink -f "$MPI_SF")" != "$MPI_OF_R" ]; then
  echo "REFUSE (exit 2): the simpleFoam BINARY resolves $(readlink -f "$MPI_SF") while the rest of the stack resolves $MPI_OF_R. That is the measured /opt/amazon/openmpi 4.1.7 vs Ubuntu 5.0.10 shadowing (same soname libmpi.so.40); the MPI pin in $BUILD_ENV is not in force for the solver."
  exit 2
fi
MPIRUN_PATH="$(command -v mpirun 2>/dev/null)"
MPIRUN_VER="$( { mpirun --version 2>&1 || true; } | head -1)"
# Printed INSIDE the branch that verified it (Amendment 6a item 1).
log "ONE MPI VERIFIED: all three of OpenFOAM, PETSc and petsc4Foam resolve $MPI_OF_R ; mpirun=$MPIRUN_PATH ($MPIRUN_VER)"

command -v nvidia-smi >/dev/null || { echo "ABORT: nvidia-smi not on PATH -- tell 2 (the solver PID holding device memory) could not be sampled, and limb A is PHYSICS-CRITICAL"; exit 1; }
nvidia-smi -L | grep -q 'NVIDIA L4' \
    || { echo "ABORT: no NVIDIA L4 visible -- this case is registered against the L4 (sm_89)"; exit 1; }
log "ENVIRONMENT VERIFIED: OpenFOAM $WM_PROJECT_VERSION from $OF_BASHRC ; PETSC_ARCH_PATH=$PETSC_ARCH_PATH ; libpetscFoam.so present ; L4 visible"

{ echo "openfoam = $WM_PROJECT_VERSION"
  echo "of_bashrc = $OF_BASHRC"
  echo "petsc_dir = $PETSC_DIR"
  echo "petsc_arch = $PETSC_ARCH"
  echo "petsc_arch_path = $PETSC_ARCH_PATH"
  echo "libpetscFoam_sha256 = $(sha256sum "$FOAM_USER_LIBBIN/libpetscFoam.so" 2>/dev/null | awk '{print $1}')"
  echo "gpu = $(nvidia-smi -L | head -1)"
  echo "driver = $(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)"
  echo "mpi_resolved = $MPI_OF_R"
  echo "mpi_openfoam = $MPI_OF"
  echo "mpi_petsc = $MPI_PETSC"
  echo "mpi_petsc4foam = $MPI_P4F"
  echo "mpirun = $MPIRUN_PATH"
  echo "mpirun_version = $MPIRUN_VER"
  echo "ldd_simpleFoam_libmpi = $(ldd "$(command -v simpleFoam)" 2>/dev/null | grep -i 'libmpi' | tr -s ' ' | tr '\n' ';')"
  echo "ldd_libpetsc_libmpi = $(ldd "$PETSC_SO" 2>/dev/null | grep -i 'libmpi' | tr -s ' ' | tr '\n' ';')"
  echo "ldd_libpetscFoam_libmpi = $(ldd "$P4F_SO" 2>/dev/null | grep -i 'libmpi' | tr -s ' ' | tr '\n' ';')"
  echo "status_smoke = $(tr '\n' ' ' < "$STATUS_SMOKE")"
  echo "toolchain_manifest_sha256 = $(sha256sum "$MANIFEST" 2>/dev/null | awk '{print $1}')"
  echo "launch_user = $USER"
  echo "launch_id_un = $(id -un)"
  echo "foam_user_libbin = $FOAM_USER_LIBBIN"
} >> "$RUN_ROOT/LAUNCH_RECORD.txt" || warn_infra "could not append the toolchain block to LAUNCH_RECORD.txt"
# The manifest itself is COPIED into the run record: a proof whose toolchain is
# named only by a file living outside the run is a proof a reader cannot check.
cp "$MANIFEST" "$RUN_ROOT/TOOLCHAIN_MANIFEST.txt" 2>/dev/null \
    || warn_infra "could not copy $MANIFEST into the run root"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

# A DRIVEN time-directory test (L-339): the regex is matched against the NAME,
# and `0.orig` is deliberately NOT a time directory while `0`, `0.1`, `250` and
# `1e-05` are.  A glob such as [0-9]* would match `0.orig` and be wrong.
is_time_dir() {
  local n="$1"
  [[ "$n" =~ ^[0-9]+([.][0-9]*)?([eE][+-]?[0-9]+)?$ ]]
}

# Rule 4's guard: refuse a case directory that already holds an answer.
age_guard_clean() {
  local d="$1" n
  test -e "$d" || return 0          # absent is clean
  test -d "$d" || { echo "ABORT age guard: $d exists and is not a directory"; return 1; }
  for n in "$d"/*; do
    test -e "$n" || continue
    n="$(basename "$n")"
    if [ "$n" = "0" ] || is_time_dir "$n"; then
      echo "ABORT age guard: $d already contains the time directory '$n'. A run is never launched into a tree that already holds an answer (CLAUDE.md rule 4)."
      return 1
    fi
  done
  return 0
}

# CONSUMER-SIDE field completeness (Amendment 5 item 1, refined by 5a).
# required = (fvSolution solver-block keys, regex alternations expanded)
#            INTERSECT (base {p,U} + the fields the closure in
#                       constant/turbulenceProperties actually creates)
#            MINUS {phi}
# Every lookup accepts `X` or `X.gz` (Amendment 5 item 4).
field_completeness() {
  local d="$1"
  python3 - "$d" <<'PYEOF'
import os, re, sys
d = sys.argv[1]
fvs = os.path.join(d, "system", "fvSolution")
tp  = os.path.join(d, "constant", "turbulenceProperties")
if not os.path.isfile(fvs):
    print("ABORT: no system/fvSolution in %s" % d); sys.exit(1)
txt = open(fvs).read()
m = re.search(r"\bsolvers\b\s*\{", txt)
if not m:
    print("ABORT: no solvers block in %s" % fvs); sys.exit(1)
i = m.end(); depth = 1; start = i
while i < len(txt) and depth:
    if txt[i] == "{": depth += 1
    elif txt[i] == "}": depth -= 1
    i += 1
if depth:
    print("ABORT: unbalanced solvers block in %s" % fvs); sys.exit(1)
body = txt[start:i-1]
# top-level keys of the solvers block
keys, depth, j = [], 0, 0
tok = ""
for ch in body:
    if ch == "{":
        if depth == 0:
            k = tok.strip().strip('"').split()
            if k: keys.append(k[-1])
        depth += 1; tok = ""
    elif ch == "}":
        depth -= 1; tok = ""
    elif depth == 0:
        tok += ch
    if ch in ";\n" and depth == 0:
        tok = ""
cand = set()
for k in keys:
    mm = re.fullmatch(r"\(([^)]*)\)", k)
    if mm:
        for alt in mm.group(1).split("|"):
            alt = alt.strip()
            if alt: cand.add(alt)
    else:
        cand.add(k)
# strip the OpenFOAM final-iteration suffix
cand = {c[:-5] if c.endswith("Final") else c for c in cand}
model = "laminar"
if os.path.isfile(tp):
    mm = re.search(r"^\s*simulationType\s+(\w+)\s*;", open(tp).read(), re.M)
    if mm: model = mm.group(1)
    mm = re.search(r"^\s*(?:RASModel|LESModel|model)\s+(\w+)\s*;", open(tp).read(), re.M)
    if mm and model != "laminar": model = mm.group(1)
CLOSURE = {
    "laminar": set(),
    "kEpsilon": {"k", "epsilon", "nut"},
    "realizableKE": {"k", "epsilon", "nut"},
    "RNGkEpsilon": {"k", "epsilon", "nut"},
    "kOmegaSST": {"k", "omega", "nut"},
    "kOmega": {"k", "omega", "nut"},
    "SpalartAllmaras": {"nuTilda", "nut"},
}
if model not in CLOSURE:
    print("ABORT: closure %r is not in this launcher's registered closure map; "
          "the consumer-side field set cannot be derived and this launcher does "
          "not guess (Amendment 5a)" % model)
    sys.exit(1)
required = (cand & ({"p", "U"} | CLOSURE[model])) - {"phi"}
missing = []
for f in sorted(required):
    if not (os.path.isfile(os.path.join(d, "0", f)) or
            os.path.isfile(os.path.join(d, "0", f + ".gz"))):
        missing.append(f)
if missing:
    print("ABORT: field(s) %s required by the consumer (fvSolution solver blocks "
          "INTERSECT closure %r) are ABSENT from %s/0/ -- neither X nor X.gz"
          % (", ".join(missing), model, d))
    sys.exit(1)
print("FIELD COMPLETENESS OK: closure=%s required={%s} all present in 0/"
      % (model, ", ".join(sorted(required))))
sys.exit(0)
PYEOF
}

elapsed_gpu_h() {
  python3 -c "print('%.6f' % (($(date +%s) - $T_START)/3600.0))"
}

# ---------------------------------------------------------------------------
# STEP 3  refuse to start if ANY level directory of EITHER arm already exists
# ---------------------------------------------------------------------------
for spec in $LEVELS; do
  name="${spec%%:*}"
  for arm in gpu cpu; do
    d="$RUN_ROOT/$arm/$name"
    [ -e "$d" ] && { echo "ABORT: $d already exists -- this script never runs into an existing case"; exit 1; }
  done
done
log "no level directory of either arm pre-exists"

# ---------------------------------------------------------------------------
# STEP 4  the six solves
# ---------------------------------------------------------------------------
CPU_ARM_CORE_MIN=0
FAILED=0
for spec in $LEVELS; do
  IFS=: read -r NAME NR NAZB ETIME <<< "$spec"
  EXPECT_CELLS=$(( 4 * NR * NAZB ))
  for arm in gpu cpu; do
    if [ "$arm" = "gpu" ]; then MAT="$GPU_MAT"; VEC="$GPU_VEC"; POPTS="$GPU_PETSC_OPTIONS";
    else                        MAT="$CPU_MAT"; VEC="$CPU_VEC"; POPTS="$CPU_PETSC_OPTIONS"; fi
    D="$RUN_ROOT/$arm/$NAME"
    log "--- $arm / $NAME : ${NR}x${NAZB} per block (${EXPECT_CELLS} cells), endTime=$ETIME, mat=$MAT vec=$VEC"

    # ---- runaway guard: REPORT, and refuse to START a further solve ---------
    SPENT_H="$(elapsed_gpu_h)" || { echo "ABORT: cannot compute elapsed GPU-hours"; exit 1; }
    OVER="$(python3 -c "print(1 if $SPENT_H >= $CAP_GPU_H else 0)")" || { echo "ABORT: cannot compare against the cap"; exit 1; }
    if [ "$OVER" = "1" ]; then
      { echo "cap_gpu_h = $CAP_GPU_H"
        echo "elapsed_gpu_h = $SPENT_H"
        echo "stopped_before = $arm/$NAME"
        echo "utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "note = the cap was ALREADY EXHAUSTED before this solve started, so no solve was launched (CLAUDE.md rule 12: an overrun stops the run). Completed levels stand."
      } > "$RUN_ROOT/CAP_EXCEEDED.txt" 2>/dev/null || warn_infra "could not write CAP_EXCEEDED.txt"
      echo "ABORT: the ${CAP_GPU_H} GPU-h cap is exhausted (${SPENT_H} GPU-h elapsed) BEFORE $arm/$NAME. No further solve is started (CLAUDE.md rule 12: an overrun stops the run and does not get a new budget)."
      exit 1
    fi

    # ---- materialise the case ---------------------------------------------
    age_guard_clean "$D" || exit 1
    mkdir -p "$D" || { echo "ABORT: cannot create $D"; exit 1; }
    cp -r "$CASE_SRC/0" "$CASE_SRC/constant" "$CASE_SRC/system" "$D/" \
        || { echo "ABORT: case copy failed for $arm/$NAME"; exit 1; }
    sed -e "s/__NR__/${NR}/g" -e "s/__NAZB__/${NAZB}/g" \
        "$CASE_SRC/system/blockMeshDict.template" > "$D/system/blockMeshDict" \
        || { echo "ABORT: blockMeshDict templating failed for $arm/$NAME"; exit 1; }
    sed -e "s/__ENDTIME__/${ETIME}/g" \
        "$CASE_SRC/system/controlDict.template" > "$D/system/controlDict" \
        || { echo "ABORT: controlDict templating failed for $arm/$NAME"; exit 1; }
    sed -e "s/__MATTYPE__/${MAT}/g" -e "s/__VECTYPE__/${VEC}/g" \
        "$CASE_SRC/system/fvSolution.template" > "$D/system/fvSolution" \
        || { echo "ABORT: fvSolution templating failed for $arm/$NAME"; exit 1; }
    rm -f "$D/system/blockMeshDict.template" "$D/system/controlDict.template" "$D/system/fvSolution.template"
    for f in blockMeshDict controlDict fvSolution; do
      grep -q "__" "$D/system/$f" \
        && { echo "ABORT: an unsubstituted __PLACEHOLDER__ survived in $arm/$NAME system/$f"; exit 1; }
    done
    grep -q "mat_type *${MAT};" "$D/system/fvSolution" \
        || { echo "ABORT: fvSolution for $arm/$NAME does not carry mat_type $MAT -- the arm is not the arm it claims to be"; exit 1; }
    grep -q "vec_type *${VEC};" "$D/system/fvSolution" \
        || { echo "ABORT: fvSolution for $arm/$NAME does not carry vec_type $VEC"; exit 1; }
    log "  templating OK: mat_type=$MAT vec_type=$VEC endTime=$ETIME, no placeholder survived"

    # ---- consumer-side field completeness ---------------------------------
    FC="$(field_completeness "$D")" || { echo "$FC"; exit 1; }
    case "$FC" in *ABORT*) echo "$FC"; exit 1;; esac
    log "  $FC"

    # ---- mesh + birth certificate (MESH_STANDARD section 6) ----------------
    ( cd "$D" && blockMesh > log.blockMesh 2>&1 ); rc=$?
    [ $rc -eq 0 ] || { echo "ABORT: blockMesh returned $rc for $arm/$NAME"; exit 1; }
    ( cd "$D" && checkMesh > log.checkMesh 2>&1 ); rc=$?
    grep -q "^Mesh OK" "$D/log.checkMesh" \
        || { echo "ABORT: checkMesh did not report 'Mesh OK' for $arm/$NAME (rc=$rc) -- a mesh is born clean or it does not enter"; exit 1; }
    GOTCELLS="$(grep -Eo 'cells:[[:space:]]*[0-9]+' "$D/log.checkMesh" | head -1 | grep -Eo '[0-9]+')"
    [ "$GOTCELLS" = "$EXPECT_CELLS" ] \
        || { echo "ABORT: $arm/$NAME has $GOTCELLS cells, the pre-registration says $EXPECT_CELLS"; exit 1; }
    log "  MESH BIRTH CERTIFICATE OK: Mesh OK, $GOTCELLS cells == registered $EXPECT_CELLS"

    # ---- the GPU sampler for TELL 2 ---------------------------------------
    # Runs for the whole solve; one line per sample, 0.5 s apart. Started BEFORE
    # the solver so it cannot miss the start of a short solve.
    ( while true; do
        echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader 2>/dev/null)"
        sleep 0.5
      done ) > "$D/gpusample.txt" 2>/dev/null &
    SAMPLER=$!

    # ---- THE PER-SOLVE CAP, ENFORCED BY `timeout` --------------------------
    # CLAUDE.md rule 12: "an overrun STOPS the run; it does not get a new
    # budget."  A guard that only writes a file is not that.  PREREG_TEMPLATE
    # Amendment 3 item 2 requires cap enforcement IN THE EXECUTABLE PATH by the
    # GENERAL formula, with RANKS in it so a parallel copy inherits a correct
    # cap:
    #        timeout_s = remaining_core_min * 60 / RANKS
    # Here the budget that draws down across levels is the GPU-hour cap (the
    # instance is billed by the hour, whatever a rank is doing), and RANKS = 1,
    # so remaining_core_min = (CAP_GPU_H - SPENT_H) * 60 * RANKS and the two
    # forms coincide; both are written out so a parallel successor changing
    # RANKS gets the right number without re-deriving it.
    #
    # `timeout` was DRIVEN on this host at STEP 0c: a child's rc passes through,
    # and an overrun comes back as 124.  So NOTHING is lost by interposing it --
    # the rc recorded below is the solver's own except when the cap fired, and
    # when the cap fired 124 is exactly the fact that must be recorded.
    REMAIN_CORE_MIN="$(python3 -c "print('%.6f' % (($CAP_GPU_H - $SPENT_H) * 60.0 * $RANKS))")" \
        || { echo "ABORT: cannot compute the remaining core-minute budget"; exit 1; }
    CAP_S="$(python3 -c "print(int(max(1.0, $REMAIN_CORE_MIN * 60.0 / $RANKS)))")" \
        || { echo "ABORT: cannot compute the per-solve timeout"; exit 1; }
    log "  per-solve cap: ${CAP_S}s (remaining budget ${REMAIN_CORE_MIN} core-min at RANKS=$RANKS, of a ${CAP_GPU_H} GPU-h total)"

    # ---- AGE-GUARD MARKER, touched LAST before launch ----------------------
    # Rule 4 clause 6: every field at endTime must be strictly NEWER than the
    # case's own 0/U.  Touched here, after the mesh, after the sampler, after
    # the cap arithmetic -- nothing between this line and the solver writes a
    # file, so 0/U is the newest thing in the tree at the instant of launch.
    touch "$D/0/U" || { echo "ABORT: cannot touch the age-guard marker $D/0/U"; exit 1; }

    T0=$(date +%s)
    # The rc is captured INSIDE this script, from `$?` of the pipeline that ran
    # the solver.  -k 30 sends KILL 30 s after TERM if the solver ignores TERM.
    ( cd "$D" && PETSC_OPTIONS="$POPTS" timeout -k 30 "$CAP_S" simpleFoam > log.simpleFoam 2>&1 )
    RC=$?
    T1=$(date +%s)
    kill "$SAMPLER"  2>/dev/null
    WALL=$(( T1 - T0 ))

    CAP_FIRED=0
    if [ "$RC" -eq 124 ] || [ "$RC" -eq 137 ]; then
      CAP_FIRED=1
      { echo "cap_gpu_h = $CAP_GPU_H"
        echo "cap_s_for_this_solve = $CAP_S"
        echo "overrun_at = $arm/$NAME"
        echo "solver_rc = $RC"
        echo "wall_s = $WALL"
        echo "utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "note = THE CAP FIRED AND STOPPED THE SOLVE (CLAUDE.md rule 12: an overrun stops the run and does not get a new budget). The artifacts on disk are kept and are a FINDING, not a retry."
      } > "$RUN_ROOT/CAP_EXCEEDED.txt" 2>/dev/null || warn_infra "could not write CAP_EXCEEDED.txt"
    fi

    # ---- bookkeeping. FROM HERE ON A FAILED WRITE IS A WARNING, NEVER A
    #      NON-ZERO EXIT: the solver has already produced its artifacts and a
    #      bookkeeping failure invalidates the bookkeeping, never the physics
    #      (L-342, Sanaa's universal rule).
    CORE_MIN="$(python3 -c "print('%.4f' % ($WALL * $RANKS / 60.0))" 2>/dev/null)" || { CORE_MIN="NOT MEASURED"; warn_infra "core-minute arithmetic failed for $arm/$NAME"; }
    GPU_H="$(python3 -c "print('%.6f' % ($WALL / 3600.0))" 2>/dev/null)" || { GPU_H="NOT MEASURED"; warn_infra "GPU-hour arithmetic failed for $arm/$NAME"; }
    # THE rc IS RECORDED TWICE, BOTH FROM INSIDE THIS SCRIPT, from the same
    # `$RC` captured at the solve:
    #   $RUN_ROOT/RUN_RC.<level>.<arm>   canonical -- the NAME carries the level
    #                                    and the arm, so a record cannot be read
    #                                    against the wrong arm by being moved
    #   $D/RUN_RC.txt                    the per-level fallback the comparator
    #                                    reads when the run-root copy is absent
    # Written by ONE statement so they cannot disagree.  L-342: from here on a
    # failed bookkeeping write is a WARNING and the exit code stays the solver's.
    RC_TEXT="$(printf 'case_id = %s\narm = %s\nlevel = %s\nrc = %d\ncap_fired = %d\ncap_s = %s\nwall_s = %d\nranks = %d\ncore_min = %s\ngpu_h = %s\nendtime = %s\ncells = %s\nmat_type = %s\nvec_type = %s\npetsc_options = %s\nprereg_blob = %s\ncomparator_blob = %s\nutc = %s\n' \
        "$CASE_ID" "$arm" "$NAME" "$RC" "$CAP_FIRED" "$CAP_S" "$WALL" "$RANKS" "$CORE_MIN" "$GPU_H" "$ETIME" "$EXPECT_CELLS" \
        "$MAT" "$VEC" "$POPTS" "$PREREG_HEAD" "$GRADER_HEAD" "$(date -u +%Y-%m-%dT%H:%M:%SZ)")" \
        || warn_infra "could not format the rc record for $arm/$NAME"
    printf '%s' "$RC_TEXT" > "$RUN_ROOT/RUN_RC.$NAME.$arm" \
        || warn_infra "could not write $RUN_ROOT/RUN_RC.$NAME.$arm"
    printf '%s' "$RC_TEXT" > "$D/RUN_RC.txt" \
        || warn_infra "could not write $D/RUN_RC.txt -- the comparator falls back to the run-root copy, and if neither is there it reports rc as NOT MEASURED and grades the physics it can see"
    printf 'solve rc = %d  arm = %s  level = %s  wall_s = %d  cap_fired = %d  utc = %s\n' \
        "$RC" "$arm" "$NAME" "$WALL" "$CAP_FIRED" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        >> "$RUN_ROOT/LAUNCH_RECORD.txt" \
        || warn_infra "could not append the rc line for $arm/$NAME to LAUNCH_RECORD.txt"
    if [ "$arm" = "cpu" ]; then
      CPU_ARM_CORE_MIN="$(python3 -c "print('%.4f' % ($CPU_ARM_CORE_MIN + $WALL * $RANKS / 60.0))" 2>/dev/null)" || warn_infra "CPU-arm core-minute accumulation failed"
      # The CPU arm has its OWN registered cap and it is ENFORCED, not merely
      # reported: an unenforced number in a record is a hope (Amendment 3 item 2).
      CPU_OVER="$(python3 -c "print(1 if $CPU_ARM_CORE_MIN >= $CAP_CPU_ARM_CORE_MIN else 0)" 2>/dev/null)" || CPU_OVER=0
      if [ "$CPU_OVER" = "1" ]; then
        { echo "cap_cpu_arm_core_min = $CAP_CPU_ARM_CORE_MIN"
          echo "cpu_arm_core_min = $CPU_ARM_CORE_MIN"
          echo "exhausted_after = $arm/$NAME"
          echo "utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
          echo "note = THE CPU-ARM CORE-MINUTE CAP IS EXHAUSTED. No further solve is started (CLAUDE.md rule 12). Completed levels stand and their artifacts are kept."
        } > "$RUN_ROOT/CAP_EXCEEDED.txt" 2>/dev/null || warn_infra "could not write CAP_EXCEEDED.txt"
        echo "STOP: the CPU arm has spent $CPU_ARM_CORE_MIN core-min of its registered ${CAP_CPU_ARM_CORE_MIN} core-min cap. An overrun stops the run and does not get a new budget (CLAUDE.md rule 12)."
        FAILED=1
        break 2
      fi
    fi
    log "  $arm/$NAME: rc=$RC wall=${WALL}s core_min=$CORE_MIN gpu_h=$GPU_H"

    if [ "$CAP_FIRED" -ne 0 ]; then
      echo "STOP: the ${CAP_GPU_H} GPU-h cap fired DURING $arm/$NAME (per-solve timeout ${CAP_S}s, solver rc=$RC). CLAUDE.md rule 12: an overrun STOPS the run and does not get a new budget. No further solve is started. The artifacts on disk are kept and CAP_EXCEEDED.txt names what happened."
      FAILED=1
      break 2
    fi
    if [ "$RC" -ne 0 ]; then
      echo "FINDING: $arm/$NAME exited rc=$RC. A non-zero solver rc is a FINDING, not a retry -- triage before anything else (SUPERVISION_CHARTER section 3 check 2). The artifacts on disk are kept."
      FAILED=1
      break 2
    fi
  done
done

# ---------------------------------------------------------------------------
# STEP 5  the cost record.  INFRASTRUCTURE: a failure here never changes the
#         exit code, which stays the solver's.
# ---------------------------------------------------------------------------
TOTAL_WALL=$(( $(date +%s) - T_START ))
TOTAL_GPU_H="$(python3 -c "print('%.6f' % ($TOTAL_WALL/3600.0))" 2>/dev/null)" || TOTAL_GPU_H="NOT MEASURED"
{ printf 'case_id = %s\ntotal_wall_s = %d\ntotal_gpu_h = %s\ncap_gpu_h = %s\ncpu_arm_core_min = %s\ncap_cpu_arm_core_min = %s\nranks = %d\nvcpu_on_instance = 4\ncost_basis = GPU-hours at the AWS PUBLISHED PRICE LIST $0.8048/GPU-h for g6.xlarge us-east-2 (retrieved 2026-08-23, GPU_CAPABILITY_STATE.md section 9); dollars DERIVED, NOT MEASURED -- this box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md section 5). The CONSOLE figure is STILL OWED and supersedes. The CPU arm runs on the same billed instance, so its core-minutes are work, not a separate charge.\nutc = %s\n' \
    "$CASE_ID" "$TOTAL_WALL" "$TOTAL_GPU_H" "$CAP_GPU_H" "$CPU_ARM_CORE_MIN" "$CAP_CPU_ARM_CORE_MIN" "$RANKS" \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$RUN_ROOT/COST.txt"; } \
  || warn_infra "could not write $RUN_ROOT/COST.txt -- cost is an INFRASTRUCTURE field; the grade proceeds on the physics artifacts and reports cost as NOT MEASURED (L-342)"

if [ "$FAILED" -ne 0 ]; then
  log "=== STOPPED on a non-zero solver rc. ${TOTAL_GPU_H} GPU-h of a ${CAP_GPU_H} GPU-h cap. ==="
  exit 1
fi
log "=== COMPLETE: six solves (3 levels x {GPU, forced-CPU}), ${TOTAL_GPU_H} GPU-h of a ${CAP_GPU_H} GPU-h cap, CPU arm ${CPU_ARM_CORE_MIN} core-min ==="
log "grade with: python3 $GRADER_REL --run-root $RUN_ROOT"
exit 0
