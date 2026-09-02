#!/usr/bin/env bash
# =============================================================================
# JF1R-QB4 -- QUIET-BOX 4-RANK PARALLEL RERUN OF THE FROZEN JF1 L1 SWEEP
#   Sanaa's 2026-09-02 order: "The quiet-box parallel rerun proceeds in the
#   background; when its log lands, screens silently update to its numbers."
#   Registration: verification/campaign/JF1R_QB4_QUIET_BOX_RERUN_NOTE.md
#   (pinned below).  TIMING RERUN.  Same physics as the landed sweep; what is
#   measured is per-case wall time, per-case core-minutes, and the sweep span.
#
# LABEL: feasibility / timing.  NO GATE, NO THRESHOLD, NO VERDICT OF THE FIXED
# VOCABULARY ATTACHES TO ANY RUN THIS SCRIPT PRODUCES.
#
# CONCURRENCY: each case is decomposed to 4 ranks (her "4 workers" per run)
# and launched with `mpirun --bind-to none` (L-431: every independent mpirun
# binds from core 0, so concurrent MPI jobs stack on the same cores unless
# binding is off).  Cases run in TWO WAVES of at most 3 concurrent cases,
# 12 ranks peak, which is what the queue entry declares.
#
# CAP, ENFORCED STRUCTURALLY (rule 12): each case runs under `timeout 1200`,
# so the launcher cannot spend more than 5 x 4 x 1200 / 60 = 400 core-min,
# the registered cap.  A timeout stops the case; the cap is never raised.
#
# rc DISCIPLINE: captured inside this wrapper by its own EXIT trap; no setsid
# here (the queue runner detaches this script itself).
# ARTIFACT DISCIPLINE: everything lands under the run roots; nothing in /tmp.
# STATUS FILE NAMES: RUN_STATUS.*, never STATUS.* (queue_runner.py truncates
# any STATUS.* in the launch cwd).
# =============================================================================
set -u
set -o pipefail

CASE_DIR="/home/ubuntu/Certonomous/cases/JF1_JET_FLAP"
REPO="/home/ubuntu/Certonomous"
RUNS="/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap"
PREREG_PATH="verification/campaign/JF1R_QB4_QUIET_BOX_RERUN_NOTE.md"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

# --- THE REGISTRATION, PINNED (belt-and-braces; no gate scores on this) -----
# Derived on disk 2026-09-02:
#   git log --format=%H -1 -- verification/campaign/JF1R_QB4_QUIET_BOX_RERUN_NOTE.md
#   git rev-parse <commit>:verification/campaign/JF1R_QB4_QUIET_BOX_RERUN_NOTE.md
FREEZE_COMMIT="4778bf75572dffc3dcd8779433ea5b585c5c390b"
FREEZE_BLOB="c05afbf6a37deea2575d8cd1f7b3785942848acf"

RANKS_PER_CASE=4
WALL_ALLOWANCE_S=1200          # per case; 5 x 4 x 1200 / 60 = 400 core-min cap
CAP_CORE_MIN_TOTAL=400.0

PREREG_COMMIT=""
PREFLIGHT=0
for a in "$@"; do
  case "$a" in
    --prereg-commit=*) PREREG_COMMIT="${a#*=}" ;;
    --preflight)       PREFLIGHT=1 ;;
    *) echo "REFUSED: unrecognised argument '$a'"; exit 3 ;;
  esac
done

# --- the frozen section 5.2 table, VERBATIM (same as run_jf1_blown.sh) ------
# TAG VJ KJET OMJET, one row per blown setting; UNBLOWN carries none.
SWEEP="UNBLOWN CMU005 CMU010 CMU020 CMU040"
cmu_of()   { case "$1" in CMU005) echo 0.05;; CMU010) echo 0.1;; CMU020) echo 0.2;; CMU040) echo 0.4;; *) echo "";; esac; }
vj_of()    { case "$1" in CMU005) echo 22.360680;; CMU010) echo 31.622777;; CMU020) echo 44.721360;; CMU040) echo 63.245553;; esac; }
kjet_of()  { case "$1" in CMU005) echo 7.5000000000e-02;; CMU010) echo 1.5000000000e-01;; CMU020) echo 3.0000000000e-01;; CMU040) echo 6.0000000000e-01;; esac; }
omjet_of() { case "$1" in CMU005) echo 1428.571429;; CMU010) echo 2020.305089;; CMU020) echo 2857.142857;; CMU040) echo 4040.610178;; esac; }

SWEEP_STATUS="${CASE_DIR}/RUN_STATUS.JF1R_QB4_SWEEP.guard.txt"
RC=99
STAGE="init"
FREEZE_CHECK="NOT REACHED -- refused at or before the freeze guard"
T_START=$(date +%s)

finish() {
  RC=$?
  local t_end elapsed
  t_end=$(date +%s); elapsed=$(( t_end - T_START ))
  {
    echo "sweep              JF1R_QB4 (quiet-box 4-rank parallel rerun of the L1 sweep)"
    echo "label              feasibility / timing"
    echo "gate               NONE -- this sweep scores nothing"
    echo "rc                 ${RC}"
    echo "stage_at_exit      ${STAGE}"
    echo "utc_start          $(date -u -d "@${T_START}" +%Y-%m-%dT%H:%M:%SZ)"
    echo "utc_end            $(date -u -d "@${t_end}" +%Y-%m-%dT%H:%M:%SZ)"
    echo "wall_span_s        ${elapsed}"
    echo "ranks_per_case     ${RANKS_PER_CASE}   waves of at most 3 cases, 12 ranks peak"
    echo "cap_core_min       ${CAP_CORE_MIN_TOTAL}  (structural: per-case timeout ${WALL_ALLOWANCE_S} s)"
    echo "prereg_commit      ${PREREG_COMMIT}"
    echo "prereg_blob_pinned ${FREEZE_BLOB}"
    echo "prereg_check       ${FREEZE_CHECK}"
    echo "per_case_status    ${RUNS}/JF1R_QB4_<TAG>/RUN_STATUS.JF1R_QB4_<TAG>.txt"
  } > "${SWEEP_STATUS}"
  exit "${RC}"
}
trap finish EXIT

# --- guards, FAIL-CLOSED -----------------------------------------------------
STAGE="guard"
[ -n "${PREREG_COMMIT}" ] || { echo "REFUSED: --prereg-commit=<40hex> is required"; exit 3; }
[ ${#PREREG_COMMIT} -eq 40 ] || { echo "REFUSED: prereg commit is not 40 hex"; exit 3; }
case "${PREREG_COMMIT}" in *[!0-9a-f]*) echo "REFUSED: not lowercase hex"; exit 3 ;; esac
[ "${PREREG_COMMIT}" = "${FREEZE_COMMIT}" ] \
  || { echo "REFUSED: ${PREREG_COMMIT} is not the pinned note commit ${FREEZE_COMMIT}"; exit 3; }
git -C "${REPO}" cat-file -e "${PREREG_COMMIT}^{commit}" 2>/dev/null \
  || { echo "REFUSED: note commit does not exist"; exit 3; }
git -C "${REPO}" cat-file -e "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null \
  || { echo "REFUSED: ${PREREG_PATH} absent at ${PREREG_COMMIT}"; exit 3; }
GOT_BLOB="$(git -C "${REPO}" rev-parse "${PREREG_COMMIT}:${PREREG_PATH}" 2>/dev/null || true)"
[ "${GOT_BLOB}" = "${FREEZE_BLOB}" ] \
  || { echo "REFUSED: note blob ${GOT_BLOB} != pinned ${FREEZE_BLOB}"; exit 3; }
WT_BLOB="$(git -C "${REPO}" hash-object "${REPO}/${PREREG_PATH}" 2>/dev/null || true)"
[ "${WT_BLOB}" = "${FREEZE_BLOB}" ] \
  || { echo "REFUSED: working-tree note (${WT_BLOB}) is not the pinned blob"; exit 3; }
FREEZE_CHECK="VERIFIED -- commit, in-commit blob and working-tree copy all pinned"

# The frozen jet constants must REPRODUCE from the registered formulae
# (transcription guard, exactly as run_jf1_blown.sh carries it).
for TAG in CMU005 CMU010 CMU020 CMU040; do
  awk -v cmu="$(cmu_of "$TAG")" -v vj="$(vj_of "$TAG")" \
      -v kj="$(kjet_of "$TAG")" -v om="$(omjet_of "$TAG")" 'BEGIN{
      Uinf=10.0; hoc=0.005; I=0.01; lj=0.07*0.005; Cmt=0.09; kinf=1.5e-04; ominf=5.0;
      v = Uinf*sqrt(cmu/(2*hoc));
      k = 1.5*(I*v)^2; if (k < kinf) k = kinf;
      o = sqrt(k)/((Cmt^0.25)*lj); if (o < ominf) o = ominf;
      bad = 0;
      if ((v-vj)/v >  1e-6 || (v-vj)/v < -1e-6) bad=1;
      if ((k-kj)/k >  1e-9 || (k-kj)/k < -1e-9) bad=1;
      if ((o-om)/o >  1e-8 || (o-om)/o < -1e-8) bad=1;
      exit bad
  }' || { echo "REFUSED: ${TAG} constants do not reproduce the frozen formulae"; exit 3; }
done

# AGE GUARD (rule 4): never launch into a tree that already holds an answer.
for TAG in ${SWEEP}; do
  [ -e "${RUNS}/JF1R_QB4_${TAG}" ] \
    && { echo "REFUSED: run root already exists: ${RUNS}/JF1R_QB4_${TAG}"; exit 3; }
done

for f in "${CASE_DIR}/case_blown/0/U.template" "${CASE_DIR}/case_blown/0/k.template" \
         "${CASE_DIR}/case_blown/0/omega.template" "${CASE_DIR}/case_blown/0/nut" \
         "${CASE_DIR}/case_blown/0/p" "${CASE_DIR}/case_blown/system/controlDict" \
         "${CASE_DIR}/case/system/fvSchemes" "${CASE_DIR}/case/system/fvSolution" \
         "${CASE_DIR}/case/constant/transportProperties" \
         "${CASE_DIR}/case/constant/turbulenceProperties" \
         "${CASE_DIR}/case/system/controlDict" "${CASE_DIR}/build_jf1.py"; do
  [ -f "$f" ] || { echo "REFUSED: required input absent: $f"; exit 3; }
done
[ -d "${CASE_DIR}/case/0" ] || { echo "REFUSED: unblown 0/ set absent"; exit 3; }
[ -f "${FOAM_BASHRC}" ] || { echo "REFUSED: OpenFOAM bashrc absent"; exit 3; }

STAGE="foamenv"
set +u
# shellcheck disable=SC1090
source "${FOAM_BASHRC}" "" > /dev/null 2>&1 || true
set -u
for cmd in simpleFoam checkMesh decomposePar reconstructPar mpirun; do
  command -v "$cmd" > /dev/null 2>&1 \
    || { echo "REFUSED: $cmd not on PATH after sourcing the OpenFOAM environment"; exit 3; }
done

if [ "${PREFLIGHT}" = "1" ]; then
  echo "PREFLIGHT OK -- guards pass, OpenFOAM environment live, zero compute"
  echo "  freeze    : ${FREEZE_COMMIT} blob ${FREEZE_BLOB} (all three checks verified)"
  echo "  cap       : ${CAP_CORE_MIN_TOTAL} core-min total (timeout ${WALL_ALLOWANCE_S} s x 4 ranks x 5 cases)"
  echo "  waves     : [CMU040 UNBLOWN CMU010] then [CMU005 CMU020], 12 ranks peak"
  exit 0
fi

# --- stage all five cases (serial; the SOLVES are the concurrent part) ------
STAGE="stage"
for TAG in ${SWEEP}; do
  CID="JF1R_QB4_${TAG}"
  ROOT="${RUNS}/${CID}"
  if [ "${TAG}" = "UNBLOWN" ]; then
    # The exact staging shape run_jf1.sh used for the landed unblown row:
    # whole-directory copies, nothing pre-created underneath them.
    mkdir -p "${ROOT}"
    cp -r "${CASE_DIR}/case/0"        "${ROOT}/0"
    cp -r "${CASE_DIR}/case/constant" "${ROOT}/constant"
    cp -r "${CASE_DIR}/case/system"   "${ROOT}/system"
    SLOT_TYPE="wall"
  else
    mkdir -p "${ROOT}/0" "${ROOT}/system" "${ROOT}/constant"
    cp "${CASE_DIR}/case/system/fvSchemes"                "${ROOT}/system/fvSchemes"
    cp "${CASE_DIR}/case/system/fvSolution"               "${ROOT}/system/fvSolution"
    cp "${CASE_DIR}/case_blown/system/controlDict"        "${ROOT}/system/controlDict"
    cp "${CASE_DIR}/case/constant/transportProperties"    "${ROOT}/constant/transportProperties"
    cp "${CASE_DIR}/case/constant/turbulenceProperties"   "${ROOT}/constant/turbulenceProperties"
    cp "${CASE_DIR}/case_blown/0/nut"                     "${ROOT}/0/nut"
    cp "${CASE_DIR}/case_blown/0/p"                       "${ROOT}/0/p"
    VJ="$(vj_of "$TAG")"
    VJX=$(awk -v v="${VJ}" 'BEGIN{printf "%.8f", v*cos(3.14159265358979323846/6.0)}')
    VJY=$(awk -v v="${VJ}" 'BEGIN{printf "%.8f", -v*sin(3.14159265358979323846/6.0)}')
    sed -e "s|@VJX@|${VJX}|" -e "s|@VJY@|${VJY}|" \
        "${CASE_DIR}/case_blown/0/U.template"                 > "${ROOT}/0/U"
    sed -e "s|@KJET@|$(kjet_of "$TAG")|"      "${CASE_DIR}/case_blown/0/k.template"     > "${ROOT}/0/k"
    sed -e "s|@OMEGAJET@|$(omjet_of "$TAG")|" "${CASE_DIR}/case_blown/0/omega.template" > "${ROOT}/0/omega"
    if grep -l '@[A-Z]*@' "${ROOT}"/0/U "${ROOT}"/0/k "${ROOT}"/0/omega > /dev/null 2>&1; then
      echo "SUBSTITUTION INCOMPLETE in ${CID}"; exit 8
    fi
    SLOT_TYPE="patch"
  fi
  # decomposition: 4 subdomains, scotch (no geometric coeffs to mistype)
  cat > "${ROOT}/system/decomposeParDict" <<'EOD'
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains 4;
method scotch;
EOD
  STAGE="mesh_${TAG}"
  python3 "${CASE_DIR}/build_jf1.py" --out "${ROOT}" --level L1 --slot-type "${SLOT_TYPE}" \
      > "${ROOT}/log.build_jf1" 2>&1 || { echo "MESH BUILD FAILED: ${CID}"; exit 4; }
  checkMesh -case "${ROOT}" > "${ROOT}/log.checkMesh" 2>&1 || true
  grep -q "^Mesh OK" "${ROOT}/log.checkMesh" \
    || { echo "checkMesh did not print Mesh OK: ${CID}"; exit 5; }
  STAGE="decompose_${TAG}"
  decomposePar -case "${ROOT}" > "${ROOT}/log.decomposePar" 2>&1 \
    || { echo "decomposePar FAILED: ${CID}"; exit 4; }
done

# --- solve, in two waves of concurrent 4-rank cases -------------------------
run_case() {
  # Runs ONE case to completion and writes its own RUN_STATUS.  Executed in
  # the background; its exit code is the solver's disposition.
  local TAG="$1" CID ROOT t0 t1 rc CMU
  CID="JF1R_QB4_${TAG}"; ROOT="${RUNS}/${CID}"; CMU="$(cmu_of "$TAG")"
  # 0/ is touched LAST before the solver so every endTime field must be newer
  # (rule 4 age guard).  The decomposed copies are touched with it.
  touch "${ROOT}"/0/* "${ROOT}"/processor*/0/* 2>/dev/null
  t0=$(date +%s)
  timeout --signal=TERM --kill-after=60 "${WALL_ALLOWANCE_S}" \
      mpirun --bind-to none -np "${RANKS_PER_CASE}" \
      simpleFoam -case "${ROOT}" -parallel > "${ROOT}/log.simpleFoam" 2>&1
  rc=$?
  t1=$(date +%s)
  echo "solver_rc ${rc}" > "${ROOT}/SOLVER_RC.txt"
  if [ ${rc} -eq 0 ]; then
    reconstructPar -case "${ROOT}" -latestTime > "${ROOT}/log.reconstructPar" 2>&1 || true
  fi
  {
    echo "case_id            ${CID}"
    if [ "${TAG}" = "UNBLOWN" ]; then
      echo "row                UNBLOWN reference (slot sealed)  alpha 0 deg"
    else
      echo "row                BLOWN  C_mu_jet ${CMU}  alpha 0 deg  tau 30 deg"
    fi
    echo "label              feasibility / timing (JF1R_QB4 quiet-box rerun)"
    echo "gate               NONE -- this run scores nothing"
    echo "rc                 ${rc}"
    echo "utc_start          $(date -u -d "@${t0}" +%Y-%m-%dT%H:%M:%SZ)"
    echo "utc_end            $(date -u -d "@${t1}" +%Y-%m-%dT%H:%M:%SZ)"
    echo "wall_s             $(( t1 - t0 ))"
    echo "ranks              ${RANKS_PER_CASE}"
    echo "core_min_MEASURED  $(awk -v s=$(( t1 - t0 )) -v r=${RANKS_PER_CASE} 'BEGIN{printf "%.4f", s*r/60.0}')"
    echo "cap_core_min       ${CAP_CORE_MIN_TOTAL} (sweep total; per-case wall allowance ${WALL_ALLOWANCE_S} s)"
    echo "prereg_commit      ${PREREG_COMMIT}"
    echo "prereg_blob_pinned ${FREEZE_BLOB}"
    echo "prereg_check       ${FREEZE_CHECK}"
    echo "run_root           ${ROOT}"
    echo "-- completion clauses, read off the artifacts (rule 4) --"
    echo "end_lines          $(grep -c '^End' "${ROOT}/log.simpleFoam" 2>/dev/null || true)"
    echo "last_time          $(grep '^Time = ' "${ROOT}/log.simpleFoam" 2>/dev/null | tail -1)"
    echo "-- last 3 forceCoeffs rows --"
    find "${ROOT}/postProcessing" -name 'coefficient*.dat' \
      -exec sh -c 'grep "^#" "$1" | tail -1; grep -v "^#" "$1" | tail -3' _ {} \; 2>/dev/null
  } > "${ROOT}/RUN_STATUS.${CID}.txt"
  return "${rc}"
}

STAGE="solve_wave1"
declare -A CASE_RC
for TAG in CMU040 UNBLOWN CMU010; do run_case "${TAG}" & CASE_RC[$TAG]=$!; done
WAVE_FAIL=0
for TAG in CMU040 UNBLOWN CMU010; do
  wait "${CASE_RC[$TAG]}"; rc=$?; CASE_RC[$TAG]=$rc
  [ $rc -eq 0 ] || WAVE_FAIL=1
done

STAGE="solve_wave2"
for TAG in CMU005 CMU020; do run_case "${TAG}" & CASE_RC[$TAG]=$!; done
for TAG in CMU005 CMU020; do
  wait "${CASE_RC[$TAG]}"; rc=$?; CASE_RC[$TAG]=$rc
  [ $rc -eq 0 ] || WAVE_FAIL=1
done

STAGE="post"
{
  echo "== JF1R_QB4 sweep readout -- per-case rc and measured walls =="
  for TAG in ${SWEEP}; do
    echo "-- ${TAG}: rc ${CASE_RC[$TAG]}"
    grep -E "^(wall_s|core_min_MEASURED|utc_start|utc_end)" \
      "${RUNS}/JF1R_QB4_${TAG}/RUN_STATUS.JF1R_QB4_${TAG}.txt" 2>/dev/null
  done
} > "${RUNS}/JF1R_QB4_READOUT.txt" 2>&1

[ ${WAVE_FAIL} -eq 0 ] || { echo "AT LEAST ONE CASE FAILED OR HIT ITS ALLOWANCE"; exit 7; }
STAGE="done"
exit 0
