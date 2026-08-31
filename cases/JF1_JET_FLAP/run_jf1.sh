#!/usr/bin/env bash
# =============================================================================
# JF1 JET-FLAP AIRFOIL -- L1 FEASIBILITY LAUNCHER
#   Row: UNBLOWN NACA 0012, alpha = 0, C_mu = 0.  jetSlot treated as a WALL.
#
# LABEL: feasibility.  NO GATE, NO THRESHOLD, NO VERDICT OF THE FIXED
# VOCABULARY ATTACHES TO THIS RUN.  It scores nothing and counts toward no
# result column.  Sanaa's SANAA-DIRECT of 2026-08-31 (commit 927924f1):
# feasibility/physics rungs need no freeze, "never was".
#
# 2026-08-31, AMENDED -- WHY, AND WHAT WAS WRONG.  As first written this script
# hardcoded, in its own status file, the two lines:
#       prereg_status      UNFROZEN DRAFT -- lawful for a feasibility rung per
#                          SANAA-DIRECT 927924f1, 2026-08-31.  Not a freeze.
# That was true when written and became FALSE at 15:29Z, when the registration
# was frozen by commit 12b1bd84.  A status file that states a constant instead of
# a measurement goes stale silently and is then read as evidence.  The lines are
# replaced by prereg_check, which reports what THIS INVOCATION actually verified
# and whose default value is the refusal.  The guard is also hardened: it now
# pins the freeze commit AND the frozen BLOB (CLAUDE.md rule 2 -- "verify the
# frozen file IS the file that ran by hashing it against the committed blob"),
# which the original did not do.  NOTHING IS WEAKENED: every refusal path the
# original had is still a refusal, and four more were added.
#
# rc DISCIPLINE: the return code is captured INSIDE this wrapper by its own
# EXIT trap.  `setsid timeout cmd` returns 0 for every outcome, so an rc taken
# AROUND the setsid line is not the solver's rc (lab memory: "setsid parent
# returns zero").
#
# ARTIFACT DISCIPLINE: every artifact is written under RUN_ROOT and retained.
# NOTHING goes to ${TMPDIR:-/tmp}.  cases/F23b_HP_WEDGE/run_f23b.sh:87 wrote its
# deciding measurement there on 2026-08-30 and the 14:35Z reboot destroyed it.
#
# STATUS FILE NAME: RUN_STATUS.*.txt, NOT STATUS.*.  scripts/queue_runner.py:496
# truncates any file named STATUS.* in the launch cwd unconditionally.
# =============================================================================
set -u
set -o pipefail

CASE_ID="JF1_L1_UNBLOWN_A0"
CASE_DIR="/home/ubuntu/Certonomous/cases/JF1_JET_FLAP"
REPO="/home/ubuntu/Certonomous"
PREREG_PATH="verification/campaign/JF1_PREREGISTRATION.md"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/${CASE_ID}"
STATUS="${RUN_ROOT}/RUN_STATUS.${CASE_ID}.txt"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

# --- THE FREEZE, PINNED -------------------------------------------------------
# DERIVED ON DISK, NOT TAKEN ON ANYONE'S SAY-SO:
#   git log --format=%H -1 -- verification/campaign/JF1_PREREGISTRATION.md
#     -> 12b1bd84766117d99c88dedf391470bb8bf47e5c   (2026-08-31T15:29Z freeze)
#   git rev-parse 12b1bd84...:verification/campaign/JF1_PREREGISTRATION.md
#     -> 66543c97fa1527ef7c36f0980460fcc0ca348508   (the frozen BLOB)
# The blob pin is the load-bearing one: a commit sha alone proves only that SOME
# document existed there.  Note that commit b52ed93b -- a heat-transfer commit
# made at 15:36:51Z, seven minutes AFTER the freeze -- carries the IDENTICAL
# frozen blob, and is still refused below, because it is not the freeze.
FREEZE_COMMIT="12b1bd84766117d99c88dedf391470bb8bf47e5c"
FREEZE_BLOB="66543c97fa1527ef7c36f0980460fcc0ca348508"

# Registered cap.  CAP_CORE_MIN is never raised (CLAUDE.md rule 12): an overrun
# STOPS the run.  RANKS = 1, so the wall allowance in seconds is CAP x 60.
RANKS=1
CAP_CORE_MIN=45.0
WALL_ALLOWANCE_S=2700

PREREG_COMMIT=""
PREFLIGHT=0
for a in "$@"; do
  case "$a" in
    --prereg-commit=*) PREREG_COMMIT="${a#*=}" ;;
    --preflight)       PREFLIGHT=1 ;;
    *) echo "REFUSED: unrecognised argument '$a'"; exit 3 ;;
  esac
done

RC=99
STAGE="init"
YPLUS_ROWS="not-reached"
# The status file must report the OUTCOME of the freeze check, never a constant.
# Default is the refusal; it is raised only after the check has actually passed.
FREEZE_CHECK="NOT REACHED -- refused at or before the freeze guard"
T_START=$(date +%s)

finish() {
  RC=$?
  local t_end elapsed core_min
  t_end=$(date +%s); elapsed=$(( t_end - T_START ))
  core_min=$(awk -v s="$elapsed" -v r="$RANKS" 'BEGIN{printf "%.4f", s*r/60.0}')
  # A GUARD FAILURE MUST NOT CREATE THE RUN ROOT.  If it did, the age guard
  # ("run root already exists") would refuse every later attempt at this case
  # and a refusal at zero compute would permanently block the rung.  Before the
  # staging step the status therefore goes beside the case, not under the run
  # root.  Neither path is named STATUS.* (queue_runner.py:496 truncates those).
  if [ "${STAGE}" = "init" ] || [ "${STAGE}" = "guard" ] || [ "${STAGE}" = "foamenv" ]; then
    STATUS="${CASE_DIR}/RUN_STATUS.${CASE_ID}.guard.txt"
  else
    mkdir -p "$RUN_ROOT" 2>/dev/null || true
    STATUS="${RUN_ROOT}/RUN_STATUS.${CASE_ID}.txt"
  fi
  {
    echo "case_id            ${CASE_ID}"
    echo "row                UNBLOWN  C_mu_jet 0  alpha 0 deg  jetSlot as WALL"
    echo "label              feasibility"
    echo "gate               NONE -- this run scores nothing"
    echo "rc                 ${RC}"
    echo "stage_at_exit      ${STAGE}"
    echo "utc_start          $(date -u -d "@${T_START}" +%Y-%m-%dT%H:%M:%SZ)"
    echo "utc_end            $(date -u -d "@${t_end}" +%Y-%m-%dT%H:%M:%SZ)"
    echo "wall_s             ${elapsed}"
    echo "ranks              ${RANKS}"
    echo "core_min_MEASURED  ${core_min}"
    echo "cap_core_min       ${CAP_CORE_MIN}"
    echo "prereg_commit      ${PREREG_COMMIT}"
    echo "prereg_blob_pinned ${FREEZE_BLOB}"
    echo "freeze_commit      ${FREEZE_COMMIT}   (registration frozen 2026-08-31T15:29Z)"
    echo "prereg_check       ${FREEZE_CHECK}"
    echo "                   NOTE: a freeze is NOT required for a feasibility rung"
    echo "                   (SANAA-DIRECT 927924f1) and NO gate of this"
    echo "                   registration scores on this run."
    echo "yplus_data_rows    ${YPLUS_ROWS}"
    echo "run_root           ${RUN_ROOT}"
  } > "${STATUS}"
  exit "${RC}"
}
trap finish EXIT

# --- guards, FAIL-CLOSED ------------------------------------------------------
STAGE="guard"
[ -n "${PREREG_COMMIT}" ] || { echo "REFUSED: --prereg-commit=<40hex> is required"; exit 3; }
[ ${#PREREG_COMMIT} -eq 40 ] || { echo "REFUSED: prereg commit is not 40 hex"; exit 3; }
case "${PREREG_COMMIT}" in
  *[!0-9a-f]*) echo "REFUSED: prereg commit is not lowercase hex"; exit 3 ;;
esac

# (a) it must BE the freeze commit.
[ "${PREREG_COMMIT}" = "${FREEZE_COMMIT}" ] \
  || { echo "REFUSED: prereg commit ${PREREG_COMMIT} is not the freeze commit ${FREEZE_COMMIT}"; exit 3; }

# (b) the commit must exist.
git -C "${REPO}" cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "REFUSED: prereg commit does not exist"; exit 3; }

# (c) the document must exist AT that commit.  A sha with no document at it is
#     the laundering shape.
git -C "${REPO}" cat-file -e "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null \
  || { echo "REFUSED: ${PREREG_PATH} absent at ${PREREG_COMMIT}"; exit 3; }

# (d) THE BLOB CHECK -- CLAUDE.md rule 2.  Fail-closed: an empty or unreadable
#     rev-parse result is a REFUSAL, never a pass.
GOT_BLOB="$(git -C "${REPO}" rev-parse "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null || true)"
[ -n "${GOT_BLOB}" ] || { echo "REFUSED: could not read the prereg blob sha at that commit"; exit 3; }
[ "${GOT_BLOB}" = "${FREEZE_BLOB}" ] \
  || { echo "REFUSED: prereg blob ${GOT_BLOB} != frozen blob ${FREEZE_BLOB}"; exit 3; }

# (e) the WORKING-TREE copy must be the frozen bytes too, so a reader who opens
#     the file on disk is reading what this run was configured against.
WT_BLOB="$(git -C "${REPO}" hash-object "${REPO}/${PREREG_PATH}" 2>/dev/null || true)"
[ "${WT_BLOB}" = "${FREEZE_BLOB}" ] \
  || { echo "REFUSED: working-tree ${PREREG_PATH} (${WT_BLOB}) is not the frozen blob"; exit 3; }

# Only NOW may the status file claim the freeze was verified.
FREEZE_CHECK="VERIFIED -- commit is the freeze commit; document present at it; its blob and the working-tree copy both hash to the pinned blob"

# AGE GUARD (CLAUDE.md rule 4): never launch into a tree that already holds an
# answer.  The run root must not exist.
if [ -e "${RUN_ROOT}" ]; then
  echo "REFUSED: run root already exists: ${RUN_ROOT}"
  exit 3
fi

[ -f "${FOAM_BASHRC}" ] || { echo "REFUSED: OpenFOAM bashrc absent"; exit 3; }

# THE ENVIRONMENT STEP IS PART OF THE PREFLIGHT, AND THAT IS NOT A REFINEMENT.
# Attempt 1 (2026-08-31T15:38:32Z, rc 1, stage_at_exit "mesh", retained at
# .../JF1_L1_UNBLOWN_A0.attempt1_FAILED_2026-08-31T1538Z) died on the `source`
# below: the OpenFOAM bashrc expands variables that are unset, and under `set -u`
# a non-interactive shell EXITS on that.  The preflight had returned rc 0 because
# it exited BEFORE this line -- it tested only the part that was never going to
# fail.  A preflight that stops short of the environment is not a preflight.
STAGE="foamenv"
set +u
# shellcheck disable=SC1090
source "${FOAM_BASHRC}" "" > /dev/null 2>&1 || true
set -u
command -v simpleFoam > /dev/null 2>&1 || { echo "REFUSED: simpleFoam not on PATH after sourcing the OpenFOAM environment"; exit 3; }
command -v checkMesh  > /dev/null 2>&1 || { echo "REFUSED: checkMesh not on PATH after sourcing the OpenFOAM environment"; exit 3; }

if [ "${PREFLIGHT}" = "1" ]; then
  echo "PREFLIGHT OK -- guards pass, OpenFOAM environment live"
  echo "  freeze     : ${FREEZE_COMMIT} blob ${FREEZE_BLOB} (commit, blob and worktree all verified)"
  echo "  simpleFoam : $(command -v simpleFoam)"
  echo "  checkMesh  : $(command -v checkMesh)"
  echo "  cap ${CAP_CORE_MIN} core-min, zero compute"
  exit 0
fi

# --- stage ------------------------------------------------------------------
STAGE="stage"
mkdir -p "${RUN_ROOT}"
cp -r "${CASE_DIR}/case/0"        "${RUN_ROOT}/0"
cp -r "${CASE_DIR}/case/constant" "${RUN_ROOT}/constant"
cp -r "${CASE_DIR}/case/system"   "${RUN_ROOT}/system"

# --- mesh -------------------------------------------------------------------
STAGE="mesh"
python3 "${CASE_DIR}/build_jf1.py" \
    --out "${RUN_ROOT}" --level L1 --slot-type wall \
    > "${RUN_ROOT}/log.build_jf1" 2>&1 \
  || { echo "MESH BUILD FAILED"; exit 4; }

STAGE="checkMesh"
checkMesh -case "${RUN_ROOT}" > "${RUN_ROOT}/log.checkMesh" 2>&1 || true
grep -q "^Mesh OK" "${RUN_ROOT}/log.checkMesh" \
  || { echo "checkMesh did not print Mesh OK"; exit 5; }

# --- age guard on the fields, re-asserted after staging ---------------------
# 0/ is written last before the solver so every endTime field must be newer.
STAGE="touch0"
touch "${RUN_ROOT}"/0/*

# --- solve ------------------------------------------------------------------
STAGE="simpleFoam"
timeout --signal=TERM --kill-after=60 "${WALL_ALLOWANCE_S}" \
    simpleFoam -case "${RUN_ROOT}" > "${RUN_ROOT}/log.simpleFoam" 2>&1
SOLVER_RC=$?
echo "solver_rc ${SOLVER_RC}" > "${RUN_ROOT}/SOLVER_RC.txt"

# The y+ row count is read WHATEVER the solver did, including a cap kill.
# max(y+) <= 1 is FROZEN GATE LINE 7, and the 15:35Z pilot wrote a yPlus.dat of
# HEADER ONLY, ZERO DATA ROWS, because it stopped at Time = 468 and this case's
# yPlus function object writes on `writeTime` at an interval of 1000.  A gate
# whose quantity is never written is unverifiable by construction, so the count
# is recorded in the status file where it cannot be missed.
YPLUS_DAT="${RUN_ROOT}/postProcessing/yPlus/0/yPlus.dat"
if [ -f "${YPLUS_DAT}" ]; then
  YPLUS_ROWS=$(grep -v '^#' "${YPLUS_DAT}" | wc -l | tr -d ' ')
else
  YPLUS_ROWS=0
fi

if [ ${SOLVER_RC} -eq 124 ] || [ ${SOLVER_RC} -eq 137 ]; then
  echo "CAP REACHED: solver killed at the ${WALL_ALLOWANCE_S} s wall allowance."
  echo "The cap is NEVER raised (CLAUDE.md rule 12); an overrun stops the run."
  exit 6
fi
[ ${SOLVER_RC} -eq 0 ] || { echo "SOLVER FAILED rc=${SOLVER_RC}"; exit 7; }

# --- post -------------------------------------------------------------------
STAGE="post"
{
  echo "== JF1 L1 UNBLOWN alpha=0 -- FEASIBILITY READOUT =="
  echo "== LABEL feasibility: NO GATE SCORES ON THIS RUN. =="
  echo "-- last 3 forceCoeffs rows (column order read from the file's own header) --"
  find "${RUN_ROOT}/postProcessing/forceCoeffs" -name 'coefficient*.dat' \
    -exec sh -c 'grep "^#" "$1" | tail -1; grep -v "^#" "$1" | tail -3' _ {} \;
  echo "-- End line --"
  grep -c "^End" "${RUN_ROOT}/log.simpleFoam" || true
  echo "-- last Time --"
  grep "^Time = " "${RUN_ROOT}/log.simpleFoam" | tail -1
  echo "-- SIMPLE convergence line, if any --"
  grep -c "SIMPLE solution converged" "${RUN_ROOT}/log.simpleFoam" || true
  echo "-- final residuals --"
  grep -E "Solving for (Ux|Uy|p|k|omega)" "${RUN_ROOT}/log.simpleFoam" | tail -5
  echo "-- continuity --"
  grep "continuity errors" "${RUN_ROOT}/log.simpleFoam" | tail -2
  echo "-- y+ : last row per patch, and the DATA-ROW COUNT --"
  echo "   yplus_data_rows ${YPLUS_ROWS}"
  grep -v '^#' "${YPLUS_DAT}" 2>/dev/null | tail -4
} > "${RUN_ROOT}/READOUT.txt" 2>&1

STAGE="done"
exit 0
