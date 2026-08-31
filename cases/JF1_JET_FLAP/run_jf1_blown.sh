#!/usr/bin/env bash
# =============================================================================
# JF1 JET-FLAP AIRFOIL -- L1 FEASIBILITY LAUNCHER, BLOWN ROWS
#   alpha = 0, tau = 30 deg, C_mu_jet in {0.05, 0.1, 0.2, 0.4}.
#   jetSlot is a FLOW PATCH carrying the frozen section 5.2 jet BCs.
#
# LABEL: feasibility.  NO GATE, NO THRESHOLD, NO VERDICT OF THE FIXED
# VOCABULARY (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
# PENDING) ATTACHES TO ANY RUN THIS SCRIPT PRODUCES.  It scores nothing, counts
# toward no result column and no challenge column, and no GCI, observed order or
# PASS may be computed, quoted or implied from it.  Sanaa's SANAA-DIRECT of
# 2026-08-31 (commit 927924f1): feasibility/physics rungs need no freeze,
# "never was".  The freeze checked below is therefore BELT-AND-BRACES -- it
# guarantees the physics constants this script substitutes are the frozen ones,
# and it gates nothing.
#
# rc DISCIPLINE: the return code is captured INSIDE this wrapper by its own EXIT
# trap.  `setsid timeout cmd` returns 0 for every outcome, so an rc taken AROUND
# a setsid line is not the solver's rc (lab memory: "setsid parent returns zero").
# There is no setsid line here; the queue runner detaches this script itself.
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

CASE_DIR="/home/ubuntu/Certonomous/cases/JF1_JET_FLAP"
REPO="/home/ubuntu/Certonomous"
PREREG_PATH="verification/campaign/JF1_PREREGISTRATION.md"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

# --- THE FREEZE, PINNED -------------------------------------------------------
# DERIVED ON DISK, NOT TAKEN ON ANYONE'S SAY-SO:
#   git log --format=%H -1 -- verification/campaign/JF1_PREREGISTRATION.md
#     -> 12b1bd84766117d99c88dedf391470bb8bf47e5c   (2026-08-31T15:29Z freeze)
#   git rev-parse 12b1bd84...:verification/campaign/JF1_PREREGISTRATION.md
#     -> 66543c97fa1527ef7c36f0980460fcc0ca348508   (the frozen BLOB)
# Both re-derived 2026-08-31.  The blob pin is the load-bearing one: a commit sha
# alone proves only that SOME document existed there.
FREEZE_COMMIT="12b1bd84766117d99c88dedf391470bb8bf47e5c"
FREEZE_BLOB="66543c97fa1527ef7c36f0980460fcc0ca348508"

# Registered cap.  CAP_CORE_MIN is NEVER raised (CLAUDE.md rule 12): an overrun
# STOPS the run.  RANKS = 1, so the wall allowance in seconds is CAP x 60.
RANKS=1
CAP_CORE_MIN=45.0
WALL_ALLOWANCE_S=2700

PREREG_COMMIT=""
CMU=""
PREFLIGHT=0
for a in "$@"; do
  case "$a" in
    --prereg-commit=*) PREREG_COMMIT="${a#*=}" ;;
    --cmu=*)           CMU="${a#*=}" ;;
    --preflight)       PREFLIGHT=1 ;;
    *) echo "REFUSED: unrecognised argument '$a'"; exit 3 ;;
  esac
done

# --- the frozen section 5.2 table, VERBATIM -----------------------------------
# k_jet     = max( 1.5 (I V_j)^2 , k_inf ),        I = 0.01, k_inf = 1.5000e-04
# omega_jet = max( sqrt(k_jet)/(C_mu_turb^0.25 l_j) , omega_inf )
#             C_mu_turb = 0.09 (MODEL CONSTANT, never the jet coefficient),
#             l_j = 0.07 h = 3.5e-04 m, omega_inf = 5.0
# V_j       = U_inf sqrt( C_mu_jet / (2 h/c) ),    U_inf = 10, h/c = 0.005
# U_jetSlot = V_j (cos tau, -sin tau, 0),          tau = 30 deg, FIXED IN THE
#                                                  AIRFOIL FRAME (A3, sec 1.6a)
case "${CMU}" in
  0.05) TAG="CMU005"; VJ="22.360680"; KJET="7.5000000000e-02"; OMJET="1428.571429" ;;
  0.1)  TAG="CMU010"; VJ="31.622777"; KJET="1.5000000000e-01"; OMJET="2020.305089" ;;
  0.2)  TAG="CMU020"; VJ="44.721360"; KJET="3.0000000000e-01"; OMJET="2857.142857" ;;
  0.4)  TAG="CMU040"; VJ="63.245553"; KJET="6.0000000000e-01"; OMJET="4040.610178" ;;
  *) echo "REFUSED: --cmu must be one of 0.05 0.1 0.2 0.4 (the frozen sweep); got '${CMU}'"; exit 3 ;;
esac

CASE_ID="JF1_L1_BLOWN_${TAG}_A0"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/${CASE_ID}"
STATUS="${CASE_DIR}/RUN_STATUS.${CASE_ID}.guard.txt"

RC=99
STAGE="init"
YPLUS_ROWS="not-reached"
# The status file must report the OUTCOME of the freeze check, never a constant.
# A line reading "prereg_status FROZEN" beside "rc 3" is exactly the stale-status
# shape that cost this case an afternoon: it describes the registration when the
# reader needs to know what THIS invocation verified.  Default is the refusal.
FREEZE_CHECK="NOT REACHED -- refused at or before the freeze guard"
T_START=$(date +%s)

finish() {
  RC=$?
  local t_end elapsed core_min
  t_end=$(date +%s); elapsed=$(( t_end - T_START ))
  core_min=$(awk -v s="$elapsed" -v r="$RANKS" 'BEGIN{printf "%.4f", s*r/60.0}')
  # A GUARD FAILURE MUST NOT CREATE THE RUN ROOT.  If it did, the age guard
  # ("run root already exists") would refuse every later attempt at this case and
  # a refusal at zero compute would permanently block the rung.  Before the
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
    echo "row                BLOWN  C_mu_jet ${CMU}  alpha 0 deg  tau 30 deg  V_j ${VJ} m/s"
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

# (a) it must BE the freeze commit.  A pointer to some later commit that merely
#     happens to carry the same bytes is not the freeze and is not accepted here.
[ "${PREREG_COMMIT}" = "${FREEZE_COMMIT}" ] \
  || { echo "REFUSED: prereg commit ${PREREG_COMMIT} is not the freeze commit ${FREEZE_COMMIT}"; exit 3; }

# (b) the commit must exist.
git -C "${REPO}" cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "REFUSED: prereg commit does not exist"; exit 3; }

# (c) the document must exist AT that commit.  A sha with no document at it is
#     the laundering shape.
git -C "${REPO}" cat-file -e "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null \
  || { echo "REFUSED: ${PREREG_PATH} absent at ${PREREG_COMMIT}"; exit 3; }

# (d) THE BLOB CHECK -- CLAUDE.md rule 2, "verify the frozen file IS the file
#     that ran by hashing it against the committed blob."  Fail-closed: an empty
#     or unreadable rev-parse result is a REFUSAL, never a pass.
GOT_BLOB="$(git -C "${REPO}" rev-parse "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null || true)"
[ -n "${GOT_BLOB}" ] || { echo "REFUSED: could not read the prereg blob sha at that commit"; exit 3; }
[ "${GOT_BLOB}" = "${FREEZE_BLOB}" ] \
  || { echo "REFUSED: prereg blob ${GOT_BLOB} != frozen blob ${FREEZE_BLOB}"; exit 3; }

# (e) the WORKING-TREE copy must be the frozen bytes too, so that a reader who
#     opens the file on disk is reading what this run was configured against.
WT_BLOB="$(git -C "${REPO}" hash-object "${REPO}/${PREREG_PATH}" 2>/dev/null || true)"
[ "${WT_BLOB}" = "${FREEZE_BLOB}" ] \
  || { echo "REFUSED: working-tree ${PREREG_PATH} (${WT_BLOB}) is not the frozen blob"; exit 3; }

# Only NOW may the status file claim the freeze was verified.  Set after the
# check, never before it.
FREEZE_CHECK="VERIFIED -- commit is the freeze commit; document present at it; its blob and the working-tree copy both hash to the pinned blob"

# (f) the frozen physics constants this script substitutes must be REPRODUCED
#     from the registered formulae, not merely transcribed.  A transcription
#     error in KJET/OMJET is exactly the failure this catches, and it is a
#     refusal rather than a silently wrong jet.
awk -v cmu="${CMU}" -v vj="${VJ}" -v kj="${KJET}" -v om="${OMJET}" 'BEGIN{
    Uinf=10.0; hoc=0.005; I=0.01; lj=0.07*0.005; Cmt=0.09; kinf=1.5e-04; ominf=5.0;
    v = Uinf*sqrt(cmu/(2*hoc));
    k = 1.5*(I*v)^2; if (k < kinf) k = kinf;
    o = sqrt(k)/((Cmt^0.25)*lj); if (o < ominf) o = ominf;
    bad = 0;
    if ((v-vj)/v >  1e-6 || (v-vj)/v < -1e-6) { printf "V_j mismatch: derived %.9f vs table %s\n", v, vj; bad=1 }
    if ((k-kj)/k >  1e-9 || (k-kj)/k < -1e-9) { printf "k_jet mismatch: derived %.12e vs table %s\n", k, kj; bad=1 }
    if ((o-om)/o >  1e-8 || (o-om)/o < -1e-8) { printf "omega_jet mismatch: derived %.9f vs table %s\n", o, om; bad=1 }
    exit bad
}' || { echo "REFUSED: substituted jet constants do not reproduce the frozen section 5.2 formulae"; exit 3; }

# AGE GUARD (CLAUDE.md rule 4): never launch into a tree that already holds an
# answer.  The run root must not exist.
[ -e "${RUN_ROOT}" ] && { echo "REFUSED: run root already exists: ${RUN_ROOT}"; exit 3; }

for f in "${CASE_DIR}/case_blown/0/U.template" \
         "${CASE_DIR}/case_blown/0/k.template" \
         "${CASE_DIR}/case_blown/0/omega.template" \
         "${CASE_DIR}/case_blown/0/nut" \
         "${CASE_DIR}/case_blown/0/p" \
         "${CASE_DIR}/case_blown/system/controlDict" \
         "${CASE_DIR}/case/system/fvSchemes" \
         "${CASE_DIR}/case/system/fvSolution" \
         "${CASE_DIR}/case/constant/transportProperties" \
         "${CASE_DIR}/case/constant/turbulenceProperties" \
         "${CASE_DIR}/build_jf1.py" ; do
  [ -f "$f" ] || { echo "REFUSED: required input absent: $f"; exit 3; }
done

[ -f "${FOAM_BASHRC}" ] || { echo "REFUSED: OpenFOAM bashrc absent"; exit 3; }

# THE ENVIRONMENT STEP IS PART OF THE PREFLIGHT, AND THAT IS NOT A REFINEMENT.
# The unblown row's attempt 1 (2026-08-31T15:38:32Z, rc 1) died on this `source`:
# the OpenFOAM bashrc expands unset variables and `set -u` EXITS a non-interactive
# shell on that.  Its preflight had returned rc 0 because it exited BEFORE this
# line -- it tested only the part that was never going to fail.  A preflight that
# stops short of the environment is not a preflight.
STAGE="foamenv"
set +u
# shellcheck disable=SC1090
source "${FOAM_BASHRC}" "" > /dev/null 2>&1 || true
set -u
command -v simpleFoam > /dev/null 2>&1 || { echo "REFUSED: simpleFoam not on PATH after sourcing the OpenFOAM environment"; exit 3; }
command -v checkMesh  > /dev/null 2>&1 || { echo "REFUSED: checkMesh not on PATH after sourcing the OpenFOAM environment"; exit 3; }

if [ "${PREFLIGHT}" = "1" ]; then
  echo "PREFLIGHT OK -- guards pass, OpenFOAM environment live, zero compute"
  echo "  case_id    : ${CASE_ID}"
  echo "  C_mu_jet   : ${CMU}    V_j ${VJ} m/s    k_jet ${KJET}    omega_jet ${OMJET}"
  echo "  freeze     : ${FREEZE_COMMIT} blob ${FREEZE_BLOB} (commit, blob and worktree all verified)"
  echo "  simpleFoam : $(command -v simpleFoam)"
  echo "  cap        : ${CAP_CORE_MIN} core-min"
  exit 0
fi

# --- stage --------------------------------------------------------------------
STAGE="stage"
mkdir -p "${RUN_ROOT}/0" "${RUN_ROOT}/system" "${RUN_ROOT}/constant"
cp "${CASE_DIR}/case/system/fvSchemes"                "${RUN_ROOT}/system/fvSchemes"
cp "${CASE_DIR}/case/system/fvSolution"               "${RUN_ROOT}/system/fvSolution"
cp "${CASE_DIR}/case_blown/system/controlDict"        "${RUN_ROOT}/system/controlDict"
cp "${CASE_DIR}/case/constant/transportProperties"    "${RUN_ROOT}/constant/transportProperties"
cp "${CASE_DIR}/case/constant/turbulenceProperties"   "${RUN_ROOT}/constant/turbulenceProperties"
cp "${CASE_DIR}/case_blown/0/nut"                     "${RUN_ROOT}/0/nut"
cp "${CASE_DIR}/case_blown/0/p"                       "${RUN_ROOT}/0/p"

# tau = 30 deg, jet fixed in the AIRFOIL frame (frozen sec 1.6a / A3).
VJX=$(awk -v v="${VJ}" 'BEGIN{printf "%.8f", v*cos(3.14159265358979323846/6.0)}')
VJY=$(awk -v v="${VJ}" 'BEGIN{printf "%.8f", -v*sin(3.14159265358979323846/6.0)}')

sed -e "s|@VJX@|${VJX}|" -e "s|@VJY@|${VJY}|" \
    "${CASE_DIR}/case_blown/0/U.template"     > "${RUN_ROOT}/0/U"
sed -e "s|@KJET@|${KJET}|"     "${CASE_DIR}/case_blown/0/k.template"     > "${RUN_ROOT}/0/k"
sed -e "s|@OMEGAJET@|${OMJET}|" "${CASE_DIR}/case_blown/0/omega.template" > "${RUN_ROOT}/0/omega"

# NO UNSUBSTITUTED TOKEN MAY SURVIVE INTO A FIELD FILE.  An `@VJX@` left in 0/U
# is not a crash -- OpenFOAM would reject it, but a partially substituted file
# could read as a plausible wrong number.  Refuse instead.
if grep -l '@[A-Z]*@' "${RUN_ROOT}"/0/U "${RUN_ROOT}"/0/k "${RUN_ROOT}"/0/omega > /dev/null 2>&1; then
  echo "SUBSTITUTION INCOMPLETE: an @TOKEN@ survived into a 0/ field"; exit 8
fi

# --- mesh, WITH THE SLOT AS A FLOW PATCH --------------------------------------
STAGE="mesh"
python3 "${CASE_DIR}/build_jf1.py" \
    --out "${RUN_ROOT}" --level L1 --slot-type patch \
    > "${RUN_ROOT}/log.build_jf1" 2>&1 \
  || { echo "MESH BUILD FAILED"; exit 4; }

STAGE="checkMesh"
checkMesh -case "${RUN_ROOT}" > "${RUN_ROOT}/log.checkMesh" 2>&1 || true
grep -q "^Mesh OK" "${RUN_ROOT}/log.checkMesh" \
  || { echo "checkMesh did not print Mesh OK"; exit 5; }

# --- age guard on the fields, re-asserted after staging -----------------------
# 0/ is touched LAST before the solver so every endTime field must be newer.
STAGE="touch0"
touch "${RUN_ROOT}"/0/*

# --- solve --------------------------------------------------------------------
STAGE="simpleFoam"
timeout --signal=TERM --kill-after=60 "${WALL_ALLOWANCE_S}" \
    simpleFoam -case "${RUN_ROOT}" > "${RUN_ROOT}/log.simpleFoam" 2>&1
SOLVER_RC=$?
echo "solver_rc ${SOLVER_RC}" > "${RUN_ROOT}/SOLVER_RC.txt"

# The yPlus row count is read WHATEVER the solver did, including a cap kill: the
# whole point of moving yPlus off writeTime is that the quantity exists even on a
# run that never reached a write interval.
YPLUS_DAT="${RUN_ROOT}/postProcessing/yPlus/0/yPlus.dat"
# `grep -c -v` is NOT used here: grep exits 1 on a zero count, so
# `$(grep -c ... || echo 0)` yields the two-line string "0\n0" on exactly the
# case this line exists to detect.  wc -l on the filtered stream cannot do that.
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

# --- post ---------------------------------------------------------------------
STAGE="post"
{
  echo "== ${CASE_ID} -- FEASIBILITY READOUT, C_mu_jet ${CMU}, alpha 0, tau 30 deg =="
  echo "== LABEL feasibility: NO GATE SCORES ON THIS RUN.  No PASS, no GCI, no =="
  echo "== observed order, no verdict of the fixed vocabulary.                 =="
  echo
  echo "-- jet BCs actually written into 0/ --"
  echo "   V_j ${VJ}   U_jetSlot (${VJX} ${VJY} 0)   k_jet ${KJET}   omega_jet ${OMJET}"
  echo "-- last 3 forceCoeffs rows (column order read from the file's own header) --"
  find "${RUN_ROOT}/postProcessing/forceCoeffs" -name 'coefficient*.dat' \
    -exec sh -c 'grep "^#" "$1" | tail -1; grep -v "^#" "$1" | tail -3' _ {} \;
  echo "-- End line count --"
  grep -c "^End" "${RUN_ROOT}/log.simpleFoam" || true
  echo "-- last Time --"
  grep "^Time = " "${RUN_ROOT}/log.simpleFoam" | tail -1
  echo "-- SIMPLE convergence line, if any --"
  grep -c "SIMPLE solution converged" "${RUN_ROOT}/log.simpleFoam" || true
  echo "-- final residuals --"
  grep -E "Solving for (Ux|Uy|p|k|omega)" "${RUN_ROOT}/log.simpleFoam" | tail -5
  echo "-- continuity --"
  grep "continuity errors" "${RUN_ROOT}/log.simpleFoam" | tail -2
  echo "-- y+ : LAST ROW PER PATCH, and the DATA-ROW COUNT --"
  echo "   yplus_data_rows ${YPLUS_ROWS}   (0 would mean frozen gate line 7's"
  echo "   quantity was never written and is unverifiable by construction)"
  grep -v '^#' "${YPLUS_DAT}" 2>/dev/null | tail -4
  echo "-- jet mass flow through jetSlot, sum(phi), last row (DIAGNOSTIC, NOT GATED) --"
  find "${RUN_ROOT}/postProcessing/jetMassFlow" -name '*.dat' \
    -exec sh -c 'grep -v "^#" "$1" | tail -1' _ {} \; 2>/dev/null
  echo "   comparand rho h V_j per unit span, rho = 1: 0.005 * ${VJ} * 0.01 (span)"
} > "${RUN_ROOT}/READOUT.txt" 2>&1

STAGE="done"
exit 0
