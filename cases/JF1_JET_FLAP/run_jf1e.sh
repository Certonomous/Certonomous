#!/usr/bin/env bash
# =============================================================================
# JF1E -- TURBULENCE-STALL ESCALATION LADDER.  One change per rung.
#
# Registration: verification/campaign/JF1E_TURBULENCE_STALL_ESCALATION_PREREGISTRATION.md
#   frozen 6e83157c112cdf606094f88ff0592bf1b02bc4b3, blob 800944bcfeb591973c...
#
# LABEL: numerics-diagnostic.  NO RUNG OF THIS LADDER PRODUCES A PHYSICS
# VERDICT, A LIFT CLAIM, AN OBSERVED ORDER, A GCI OR A BAND (registration sec 0).
#
# RUNG E1 -- CONTINUATION, AND IT IS THE ONLY CHANGE.  The numerics dictionaries
# are copied from the same case templates the 2026-08-31 rows used, byte for
# byte.  The single difference is that 0/ carries the previous C_mu's solved
# interior instead of freestream.
#
# THE SEED IS NOT A CONVERGED FIELD, AND NO REPORT MAY SAY IT IS (departure D-1).
# This lab has no converged JF1 solution at any C_mu.  The chain is seeded from a
# stationary-but-clipping-held final field.
#
# rc DISCIPLINE: rc is captured INSIDE this wrapper by its own EXIT trap.
# ARTIFACT DISCIPLINE: everything under RUN_ROOT.  Nothing in /tmp.
# STATUS NAME: RUN_STATUS.*.txt, never STATUS.* (queue_runner.py:496 truncates).
# =============================================================================
set -u
set -o pipefail

CASE_DIR="/home/ubuntu/Certonomous/cases/JF1_JET_FLAP"
REPO="/home/ubuntu/Certonomous"
RUNS="/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap"
PREREG_PATH="verification/campaign/JF1E_TURBULENCE_STALL_ESCALATION_PREREGISTRATION.md"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

FREEZE_COMMIT="6e83157c112cdf606094f88ff0592bf1b02bc4b3"
FREEZE_BLOB="800944bcfeb591973ca8830ae6c8ec6787ce730c"

RANKS=1
RUNG=""; CMU=""; SEED_ROOT=""; SEED_TIME=""; PREFLIGHT=0; PREREG_COMMIT=""
for a in "$@"; do
  case "$a" in
    --prereg-commit=*) PREREG_COMMIT="${a#*=}" ;;
    --rung=*)          RUNG="${a#*=}" ;;
    --cmu=*)           CMU="${a#*=}" ;;
    --seed-from=*)     SEED_ROOT="${a#*=}" ;;
    --seed-time=*)     SEED_TIME="${a#*=}" ;;
    --preflight)       PREFLIGHT=1 ;;
    *) echo "REFUSED: unrecognised argument '$a'"; exit 3 ;;
  esac
done

case "${RUNG}" in
  E1) : ;;   # continuation only.  Later rungs are added as they are reached,
             # each changing exactly one control from the rung below it.
  *) echo "REFUSED: --rung must be E1 (the frozen section 3 order); got '${RUNG}'"; exit 3 ;;
esac

# --- the frozen section 5.2 table, VERBATIM -----------------------------------
case "${CMU}" in
  0.05) TAG="CMU005"; VJ="22.360680"; KJET="7.5000000000e-02"; OMJET="1428.571429" ;;
  0.1)  TAG="CMU010"; VJ="31.622777"; KJET="1.5000000000e-01"; OMJET="2020.305089" ;;
  0.2)  TAG="CMU020"; VJ="44.721360"; KJET="3.0000000000e-01"; OMJET="2857.142857" ;;
  0.4)  TAG="CMU040"; VJ="63.245553"; KJET="6.0000000000e-01"; OMJET="4040.610178" ;;
  *) echo "REFUSED: --cmu must be one of 0.05 0.1 0.2 0.4; got '${CMU}'"; exit 3 ;;
esac

CAP_CORE_MIN=40.0
WALL_ALLOWANCE_S=2400

CASE_ID="JF1E_${RUNG}_${TAG}_A0"
RUN_ROOT="${RUNS}/${CASE_ID}"
STATUS="${CASE_DIR}/RUN_STATUS.${CASE_ID}.guard.txt"

RC=99
STAGE="init"
YPLUS_ROWS="not-reached"
SEED_CHECK="NOT REACHED"
FREEZE_CHECK="NOT REACHED -- refused at or before the freeze guard"
T_START=$(date +%s)

finish() {
  RC=$?
  local t_end elapsed core_min
  t_end=$(date +%s); elapsed=$(( t_end - T_START ))
  core_min=$(awk -v s="$elapsed" -v r="$RANKS" 'BEGIN{printf "%.4f", s*r/60.0}')
  if [ "${STAGE}" = "init" ] || [ "${STAGE}" = "guard" ] || [ "${STAGE}" = "foamenv" ]; then
    STATUS="${CASE_DIR}/RUN_STATUS.${CASE_ID}.guard.txt"
  else
    mkdir -p "$RUN_ROOT" 2>/dev/null || true
    STATUS="${RUN_ROOT}/RUN_STATUS.${CASE_ID}.txt"
  fi
  {
    echo "case_id            ${CASE_ID}"
    echo "ladder             JF1E turbulence-stall escalation"
    echo "rung               ${RUNG} -- CONTINUATION, and it is the only change from the"
    echo "                   2026-08-31 baseline: numerics dictionaries are the same"
    echo "                   case templates, byte for byte."
    echo "row                BLOWN  C_mu_jet ${CMU}  alpha 0 deg  tau 30 deg  V_j ${VJ} m/s"
    echo "label              numerics-diagnostic -- NO physics verdict, NO lift claim,"
    echo "                   NO observed order, NO GCI, NO band (registration sec 0)"
    echo "seed_from          ${SEED_ROOT:-none}  time ${SEED_TIME:-none}"
    echo "seed_check         ${SEED_CHECK}"
    echo "seed_caveat        THE SEED IS NOT A CONVERGED FIELD.  It is the final field of"
    echo "                   a stationary-but-clipping-held run.  Departure D-1, disclosed."
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
    echo "freeze_commit      ${FREEZE_COMMIT}"
    echo "prereg_check       ${FREEZE_CHECK}"
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
[ "${PREREG_COMMIT}" = "${FREEZE_COMMIT}" ] \
  || { echo "REFUSED: prereg commit ${PREREG_COMMIT} is not the freeze commit ${FREEZE_COMMIT}"; exit 3; }
git -C "${REPO}" cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "REFUSED: prereg commit does not exist"; exit 3; }
git -C "${REPO}" cat-file -e "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null \
  || { echo "REFUSED: ${PREREG_PATH} absent at ${PREREG_COMMIT}"; exit 3; }
GOT_BLOB="$(git -C "${REPO}" rev-parse "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null || true)"
[ -n "${GOT_BLOB}" ] || { echo "REFUSED: could not read the prereg blob sha"; exit 3; }
[ "${GOT_BLOB}" = "${FREEZE_BLOB}" ] \
  || { echo "REFUSED: prereg blob ${GOT_BLOB} != frozen blob ${FREEZE_BLOB}"; exit 3; }
WT_BLOB="$(git -C "${REPO}" hash-object "${REPO}/${PREREG_PATH}" 2>/dev/null || true)"
[ "${WT_BLOB}" = "${FREEZE_BLOB}" ] \
  || { echo "REFUSED: working-tree ${PREREG_PATH} (${WT_BLOB}) is not the frozen blob"; exit 3; }
FREEZE_CHECK="VERIFIED -- commit is the freeze commit; document present at it; its blob and the working-tree copy both hash to the pinned blob"

awk -v cmu="${CMU}" -v vj="${VJ}" -v kj="${KJET}" -v om="${OMJET}" 'BEGIN{
    Uinf=10.0; hoc=0.005; I=0.01; lj=0.07*0.005; Cmt=0.09; kinf=1.5e-04; ominf=5.0;
    v = Uinf*sqrt(cmu/(2*hoc));
    k = 1.5*(I*v)^2; if (k < kinf) k = kinf;
    o = sqrt(k)/((Cmt^0.25)*lj); if (o < ominf) o = ominf;
    bad = 0;
    if ((v-vj)/v >  1e-6 || (v-vj)/v < -1e-6) { printf "V_j mismatch\n"; bad=1 }
    if ((k-kj)/k >  1e-9 || (k-kj)/k < -1e-9) { printf "k_jet mismatch\n"; bad=1 }
    if ((o-om)/o >  1e-8 || (o-om)/o < -1e-8) { printf "omega_jet mismatch\n"; bad=1 }
    exit bad
}' || { echo "REFUSED: substituted jet constants do not reproduce the frozen formulae"; exit 3; }

# --- the seed must exist and carry the fields the splice needs ----------------
[ -n "${SEED_ROOT}" ] || { echo "REFUSED: --seed-from=<run root> is required for a continuation rung"; exit 3; }
[ -n "${SEED_TIME}" ] || { echo "REFUSED: --seed-time=<time dir> is required"; exit 3; }
[ -d "${SEED_ROOT}/${SEED_TIME}" ] || { echo "REFUSED: seed time dir absent: ${SEED_ROOT}/${SEED_TIME}"; exit 3; }
for f in U p k omega nut; do
  [ -f "${SEED_ROOT}/${SEED_TIME}/${f}" ] \
    || { echo "REFUSED: seed field absent: ${SEED_ROOT}/${SEED_TIME}/${f}"; exit 3; }
done
# The seed run must itself have COMPLETED.  Seeding from a killed run's partial
# write is a continuation from an artifact, not from a solution.
grep -q "^End" "${SEED_ROOT}/log.simpleFoam" \
  || { echo "REFUSED: seed run printed no End line: ${SEED_ROOT}"; exit 3; }

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
         "${CASE_DIR}/build_jf1.py" \
         "${CASE_DIR}/seed_from_field.py" ; do
  [ -f "$f" ] || { echo "REFUSED: required input absent: $f"; exit 3; }
done
[ -f "${FOAM_BASHRC}" ] || { echo "REFUSED: OpenFOAM bashrc absent"; exit 3; }

STAGE="foamenv"
set +u
# shellcheck disable=SC1090
source "${FOAM_BASHRC}" "" > /dev/null 2>&1 || true
set -u
command -v simpleFoam > /dev/null 2>&1 || { echo "REFUSED: simpleFoam not on PATH"; exit 3; }
command -v checkMesh  > /dev/null 2>&1 || { echo "REFUSED: checkMesh not on PATH"; exit 3; }

if [ "${PREFLIGHT}" = "1" ]; then
  echo "PREFLIGHT OK -- guards pass, OpenFOAM environment live, zero compute"
  echo "  case_id : ${CASE_ID}"
  echo "  rung    : ${RUNG}  C_mu ${CMU}  V_j ${VJ}"
  echo "  seed    : ${SEED_ROOT}/${SEED_TIME}  (End line present)"
  echo "  freeze  : ${FREEZE_COMMIT} blob ${FREEZE_BLOB} (commit, blob and worktree verified)"
  echo "  cap     : ${CAP_CORE_MIN} core-min"
  exit 0
fi

# --- stage: the SAME dictionaries the baseline used, byte for byte ------------
STAGE="stage"
mkdir -p "${RUN_ROOT}/0" "${RUN_ROOT}/system" "${RUN_ROOT}/constant"
cp "${CASE_DIR}/case/system/fvSchemes"                "${RUN_ROOT}/system/fvSchemes"
cp "${CASE_DIR}/case/system/fvSolution"               "${RUN_ROOT}/system/fvSolution"
cp "${CASE_DIR}/case_blown/system/controlDict"        "${RUN_ROOT}/system/controlDict"
cp "${CASE_DIR}/case/constant/transportProperties"    "${RUN_ROOT}/constant/transportProperties"
cp "${CASE_DIR}/case/constant/turbulenceProperties"   "${RUN_ROOT}/constant/turbulenceProperties"
cp "${CASE_DIR}/case_blown/0/nut"                     "${RUN_ROOT}/0/nut"
cp "${CASE_DIR}/case_blown/0/p"                       "${RUN_ROOT}/0/p"

VJX=$(awk -v v="${VJ}" 'BEGIN{printf "%.8f", v*cos(3.14159265358979323846/6.0)}')
VJY=$(awk -v v="${VJ}" 'BEGIN{printf "%.8f", -v*sin(3.14159265358979323846/6.0)}')
sed -e "s|@VJX@|${VJX}|" -e "s|@VJY@|${VJY}|" \
    "${CASE_DIR}/case_blown/0/U.template"     > "${RUN_ROOT}/0/U"
sed -e "s|@KJET@|${KJET}|"      "${CASE_DIR}/case_blown/0/k.template"     > "${RUN_ROOT}/0/k"
sed -e "s|@OMEGAJET@|${OMJET}|" "${CASE_DIR}/case_blown/0/omega.template" > "${RUN_ROOT}/0/omega"
if grep -l '@[A-Z]*@' "${RUN_ROOT}"/0/U "${RUN_ROOT}"/0/k "${RUN_ROOT}"/0/omega > /dev/null 2>&1; then
  echo "SUBSTITUTION INCOMPLETE: an @TOKEN@ survived into a 0/ field"; exit 8
fi

# --- mesh ---------------------------------------------------------------------
STAGE="mesh"
python3 "${CASE_DIR}/build_jf1.py" \
    --out "${RUN_ROOT}" --level L1 --slot-type patch \
    > "${RUN_ROOT}/log.build_jf1" 2>&1 \
  || { echo "MESH BUILD FAILED"; exit 4; }

STAGE="checkMesh"
checkMesh -case "${RUN_ROOT}" > "${RUN_ROOT}/log.checkMesh" 2>&1 || true
grep -q "^Mesh OK" "${RUN_ROOT}/log.checkMesh" \
  || { echo "checkMesh did not print Mesh OK"; exit 5; }

# --- THE MESH-IDENTITY ASSERT (registration sec 3.2 clause 2) -----------------
# The splice is only legitimate if seed and target are the same mesh.  Measured
# once and asserted every time: points/faces/owner/neighbour must be byte
# identical.  `boundary` is EXPECTED to differ when the seed is the slot-closed
# row (type wall vs type patch) and is deliberately not compared.
STAGE="meshassert"
for f in points faces owner neighbour; do
  a=$(md5sum "${SEED_ROOT}/constant/polyMesh/${f}" 2>/dev/null | cut -d' ' -f1)
  b=$(md5sum "${RUN_ROOT}/constant/polyMesh/${f}"  2>/dev/null | cut -d' ' -f1)
  [ -n "$a" ] && [ -n "$b" ] \
    || { echo "REFUSED: could not hash polyMesh/${f} on both sides"; exit 11; }
  [ "$a" = "$b" ] \
    || { echo "REFUSED: polyMesh/${f} differs between seed and target -- the two are"
         echo "         not the same mesh, and a cell-for-cell splice would produce a"
         echo "         plausible, cell-misaligned, entirely wrong field."
         echo "         seed ${a}   target ${b}"; exit 11; }
done
SEED_CHECK="VERIFIED -- polyMesh points/faces/owner/neighbour byte-identical to the seed"

# --- THE ONE CHANGE: seed the interior from the previous C_mu ------------------
STAGE="seed"
for f in U p k omega nut; do
  python3 "${CASE_DIR}/seed_from_field.py" \
      --seed  "${SEED_ROOT}/${SEED_TIME}/${f}" \
      --target "${RUN_ROOT}/0/${f}" \
      --owner "${RUN_ROOT}/constant/polyMesh/owner" \
    >> "${RUN_ROOT}/log.seed" 2>&1 \
    || { echo "SEEDING REFUSED on field ${f} -- see ${RUN_ROOT}/log.seed"; exit 12; }
done
# The seeded fields must still carry this row's OWN jet BCs, not the seed's.
grep -q "${VJX}" "${RUN_ROOT}/0/U" \
  || { echo "REFUSED: this row's jet velocity is not in 0/U after seeding -- the"
       echo "         splice took the seed's boundaryField"; exit 12; }
grep -q "${KJET}" "${RUN_ROOT}/0/k" \
  || { echo "REFUSED: this row's k_jet is not in 0/k after seeding"; exit 12; }

# --- age guard on the fields, re-asserted after seeding -----------------------
STAGE="touch0"
touch "${RUN_ROOT}"/0/*

# --- solve --------------------------------------------------------------------
STAGE="simpleFoam"
timeout --signal=TERM --kill-after=60 "${WALL_ALLOWANCE_S}" \
    simpleFoam -case "${RUN_ROOT}" > "${RUN_ROOT}/log.simpleFoam" 2>&1
SOLVER_RC=$?
echo "solver_rc ${SOLVER_RC}" > "${RUN_ROOT}/SOLVER_RC.txt"

YPLUS_DAT="${RUN_ROOT}/postProcessing/yPlus/0/yPlus.dat"
if [ -f "${YPLUS_DAT}" ]; then
  YPLUS_ROWS=$(grep -v '^#' "${YPLUS_DAT}" | wc -l | tr -d ' ')
else
  YPLUS_ROWS=0
fi

if [ ${SOLVER_RC} -eq 124 ] || [ ${SOLVER_RC} -eq 137 ]; then
  echo "CAP REACHED at ${WALL_ALLOWANCE_S} wall s (${CAP_CORE_MIN} core-min)."
  echo "The cap is NEVER raised (CLAUDE.md rule 12); an overrun stops the run."
  exit 6
fi
[ ${SOLVER_RC} -eq 0 ] || { echo "SOLVER FAILED rc=${SOLVER_RC}"; exit 7; }

# --- post ---------------------------------------------------------------------
STAGE="post"
{
  echo "== ${CASE_ID} -- JF1E RUNG ${RUNG} READOUT, C_mu ${CMU}, alpha 0, tau 30 deg =="
  echo "== LABEL numerics-diagnostic: NO physics verdict, NO lift claim, NO      =="
  echo "== observed order, NO GCI, NO band comes off this run.                   =="
  echo
  echo "-- the ONE change from baseline --"
  echo "   0/ seeded from ${SEED_ROOT}/${SEED_TIME}; numerics dictionaries unchanged"
  echo "   seed check: ${SEED_CHECK}"
  echo "   CAVEAT D-1: the seed is NOT a converged field."
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
  grep -E "Solving for (Ux|Uy|p|k|omega)" "${RUN_ROOT}/log.simpleFoam" | tail -6
  echo "-- GATE E CLAUSES E-1/E-2: bounding events, WHOLE RUN --"
  echo "   bounding k     $(grep -c 'bounding k' "${RUN_ROOT}/log.simpleFoam" || true)"
  echo "   bounding omega $(grep -c 'bounding omega' "${RUN_ROOT}/log.simpleFoam" || true)"
  echo "   (the final-500 counts that the gate actually reads are computed by the"
  echo "    comparator, which carries the planted control)"
  echo "-- continuity --"
  grep "continuity errors" "${RUN_ROOT}/log.simpleFoam" | tail -2
  echo "-- y+ --"
  echo "   yplus_data_rows ${YPLUS_ROWS}"
  grep -v '^#' "${YPLUS_DAT}" 2>/dev/null | tail -3
} > "${RUN_ROOT}/READOUT.txt" 2>&1

STAGE="done"
exit 0
