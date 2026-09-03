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

# RUNGS IMPLEMENTED SO FAR, each changing EXACTLY ONE control from the rung
# below it (registration section 3, frozen).  A rung is added only when the rung
# below it has been graded and failed; the frozen ORDER is not negotiable here.
#
#   E1  continuation seeding.  The change from E0.
#   E2a turbulence-equation relaxation k and omega 0.7 -> 0.5 (section 3.1 reads
#       the pair as ONE control).  The change from E1.  E1's configuration --
#       the continuation chain -- is INHERITED UNCHANGED, per section 3's rule
#       that a failed rung hands its configuration to the next rung as the new
#       baseline.  E2a is therefore NOT seeded from E1's output fields: that
#       would be two changes (a different seed AND a different relaxation) and
#       would destroy the attribution the ladder exists to produce.
#
#   E2b nNonOrthogonalCorrectors 1 -> 2.  The change from E2a.  E2a's
#       configuration -- the continuation chain AND the k/omega relaxation of
#       0.5 -- is INHERITED UNCHANGED, per section 3's rule that a failed rung
#       hands its configuration to the next rung as the new baseline.  E2b is
#       therefore NOT seeded from E2a's output fields, for the same reason E2a
#       was not seeded from E1's: that would be two changes.
#       ENABLED 2026-09-02, and only because E2a is graded GATE FAIL in
#       verification/campaign/JF1E_E2a_GRADING_RECORD.md.  A rung is implemented
#       here only after the rung below it has been graded and failed.
#
#   E2c div(phi,k) and div(phi,omega): limitedLinear 1 -> limitedLinear 0.5.
#       The change from E2b.  E2b's configuration -- the continuation chain, the
#       k/omega relaxation of 0.5 AND nNonOrthogonalCorrectors 2 -- is INHERITED
#       UNCHANGED, per section 3's rule that a failed rung hands its
#       configuration to the next rung as the new baseline.  E2c is therefore NOT
#       seeded from E2b's output fields, for the same reason E2b was not seeded
#       from E2a's: that would be two changes.
#       Section 3.1's reading of the k/omega relaxation pair as ONE control
#       applies identically to the div(phi,k)/div(phi,omega) scheme pair: it is
#       one knob -- the convective discretisation of the turbulence transport
#       pair -- and the frozen section 3 table names the two entries in one cell.
#       ENABLED 2026-09-02, and only because E2b is graded GATE FAIL in
#       verification/campaign/JF1E_E2b_GRADING_RECORD.md.  A rung is implemented
#       here only after the rung below it has been graded and failed.
#
# E3 and E4 are NOT implemented and are refused, so that a rung cannot be run out
# of the frozen order by a typo (registration section 7 clause 6).
case "${RUNG}" in
  E1)  RUNG_DESC="CONTINUATION, and it is the only change from the
                   2026-08-31 baseline: numerics dictionaries are the same
                   case templates, byte for byte." ;;
  E2a) RUNG_DESC="TURBULENCE-EQUATION RELAXATION k and omega 0.7 -> 0.5, and it
                   is the ONLY change from E1.  Continuation seeding, fvSchemes,
                   nNonOrthogonalCorrectors, U relaxation 0.7 and p field
                   relaxation 0.3 are all INHERITED FROM E1 UNCHANGED." ;;
  E2b) RUNG_DESC="nNonOrthogonalCorrectors 1 -> 2, and it is the ONLY change from
                   E2a.  Continuation seeding, fvSchemes, k and omega relaxation
                   0.5, U relaxation 0.7 and p field relaxation 0.3 are all
                   INHERITED FROM E2a UNCHANGED." ;;
  E2c) RUNG_DESC="div(phi,k) and div(phi,omega) limitedLinear 1 -> limitedLinear
                   0.5, and it is the ONLY change from E2b.  Continuation
                   seeding, k and omega relaxation 0.5, U relaxation 0.7, p field
                   relaxation 0.3 and nNonOrthogonalCorrectors 2 are all
                   INHERITED FROM E2b UNCHANGED." ;;
  *) echo "REFUSED: --rung must be E1, E2a, E2b or E2c (the frozen section 3 order, run in order); got '${RUNG}'"; exit 3 ;;
esac

# --- the frozen section 5.2 table, VERBATIM -----------------------------------
case "${CMU}" in
  0.05) TAG="CMU005"; VJ="22.360680"; KJET="7.5000000000e-02"; OMJET="1428.571429" ;;
  0.1)  TAG="CMU010"; VJ="31.622777"; KJET="1.5000000000e-01"; OMJET="2020.305089" ;;
  0.2)  TAG="CMU020"; VJ="44.721360"; KJET="3.0000000000e-01"; OMJET="2857.142857" ;;
  0.4)  TAG="CMU040"; VJ="63.245553"; KJET="6.0000000000e-01"; OMJET="4040.610178" ;;
  *) echo "REFUSED: --cmu must be one of 0.05 0.1 0.2 0.4; got '${CMU}'"; exit 3 ;;
esac

# PER-LINK WALL CAP.  This is a wrapper guard, NOT a registered threshold: the
# registered figure is the RUNG cap of registration section 6, enforced
# cumulatively by run_jf1e_chain.sh.  The per-link figure is set at
# (registered rung cap)/4 for E2b so that a link cannot be killed for spending
# less than its registered share -- E1 and E2a keep the 40.0/2400 they ran at,
# unchanged, because changing them would change what those graded rungs mean.
case "${RUNG}" in
  E2b) CAP_CORE_MIN=55.0; WALL_ALLOWANCE_S=3300 ;;   # 4 x 55   = the registered 220
  E2c) CAP_CORE_MIN=37.5; WALL_ALLOWANCE_S=2250 ;;   # 4 x 37.5 = the registered 150
  *)   CAP_CORE_MIN=40.0; WALL_ALLOWANCE_S=2400 ;;
esac

CASE_ID="JF1E_${RUNG}_${TAG}_A0"
RUN_ROOT="${RUNS}/${CASE_ID}"
STATUS="${CASE_DIR}/RUN_STATUS.${CASE_ID}.guard.txt"

RC=99
STAGE="init"
YPLUS_ROWS="not-reached"
SEED_CHECK="NOT REACHED"
FREEZE_CHECK="NOT REACHED -- refused at or before the freeze guard"
ONE_CHANGE="NOT REACHED -- the staged dictionaries were never asserted"
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
    echo "rung               ${RUNG} -- ${RUNG_DESC}"
    echo "one_change         ${ONE_CHANGE}"
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

# --- THE ONE CHANGE OF THIS RUNG, APPLIED HERE AND ONLY HERE ------------------
#
# The case TEMPLATES ARE NEVER EDITED.  Editing `case/system/fvSolution` in place
# would silently change what E1 means: E1's four rows were staged from that file
# and any later reader reproducing E1 would get E2a's numerics.  The rung's one
# change is therefore applied to the STAGED COPY, after the byte-identical copy,
# and is asserted line by line against the template it came from.
#
# THE ANTI-BUNDLING ASSERTS ARE THE POINT.  E2b (`nNonOrthogonalCorrectors`) and
# E2c (`limitedLinear`) are separate rungs in the frozen order; if either drifted
# into this run the ladder would measure a bundle and attribute it to relaxation.
# So both are asserted UNCHANGED on every rung, including E1.
STAGE="onechange"
if ! cmp -s "${CASE_DIR}/case/system/fvSchemes" "${RUN_ROOT}/system/fvSchemes"; then
  echo "REFUSED: staged fvSchemes is not byte-identical to the case template"; exit 13
fi
# These two asserts run on the FRESHLY COPIED template, before any rung applies
# its change, so they are a BASELINE assert on every rung including E2c.  For E1,
# E2a and E2b the staged file must still read `limitedLinear 1` at solve time --
# a drift to 0.5 there would be E2c's change leaking into a rung that does not own
# it.  For E2c this is the starting point that the one change below moves to 0.5,
# on the STAGED COPY only, asserted line by line against E2b's own dictionary.
grep -qE '^[[:space:]]*div\(phi,k\)[[:space:]]+bounded Gauss limitedLinear 1;' "${RUN_ROOT}/system/fvSchemes" \
  || { echo "REFUSED: the staged case template's div(phi,k) is not the frozen 'limitedLinear 1'"
       echo "         -- the baseline this ladder departs from has drifted"; exit 13; }
grep -qE '^[[:space:]]*div\(phi,omega\)[[:space:]]+bounded Gauss limitedLinear 1;' "${RUN_ROOT}/system/fvSchemes" \
  || { echo "REFUSED: the staged case template's div(phi,omega) is not the frozen 'limitedLinear 1'"
       echo "         -- the baseline this ladder departs from has drifted"; exit 13; }
# Asserted on the FRESHLY COPIED TEMPLATE, before any rung applies its change:
# the baseline every rung departs from must still read 1.  For E1 and E2a it must
# also still read 1 in the run (E2b is a different rung); for E2b this is the
# starting point that the one change below moves to 2, asserted line by line.
grep -qE '^[[:space:]]*nNonOrthogonalCorrectors[[:space:]]+1;' "${RUN_ROOT}/system/fvSolution" \
  || { echo "REFUSED: the staged case template's nNonOrthogonalCorrectors is not 1 -- the"
       echo "         baseline this ladder departs from has drifted"; exit 13; }

case "${RUNG}" in
  E1)
    cmp -s "${CASE_DIR}/case/system/fvSolution" "${RUN_ROOT}/system/fvSolution" \
      || { echo "REFUSED: E1 staged fvSolution is not byte-identical to the case template"; exit 13; }
    ONE_CHANGE="continuation seeding of 0/ only; fvSolution and fvSchemes byte-identical to the case templates"
    ;;
  E2a)
    # Rewrite ONLY the `k` and `omega` entries inside relaxationFactors/equations.
    # A bare `sed s/0.7/0.5/g` would also hit U -- a second change, unregistered.
    awk '
      /^relaxationFactors/           { inRF = 1 }
      inRF && /equations/            { inEQ = 1 }
      inEQ && /^[[:space:]]*k[[:space:]]+0\.7;[[:space:]]*$/     { sub(/0\.7;/, "0.5;"); n++ }
      inEQ && /^[[:space:]]*omega[[:space:]]+0\.7;[[:space:]]*$/ { sub(/0\.7;/, "0.5;"); n++ }
      inEQ && /^[[:space:]]*}/       { inEQ = 0 }
                                     { print }
      END                            { if (n != 2) exit 1 }
    ' "${RUN_ROOT}/system/fvSolution" > "${RUN_ROOT}/system/fvSolution.E2a" \
      || { echo "REFUSED: the E2a rewrite did not change exactly two lines (k and omega)"; exit 13; }
    mv "${RUN_ROOT}/system/fvSolution.E2a" "${RUN_ROOT}/system/fvSolution"

    # The diff against the template must be EXACTLY two changed lines.
    NDIFF=$(diff "${CASE_DIR}/case/system/fvSolution" "${RUN_ROOT}/system/fvSolution" \
              | grep -cE '^[<>]' || true)
    [ "${NDIFF}" = "4" ] \
      || { echo "REFUSED: E2a changed ${NDIFF} diff lines against the template, expected 4 (two < and two >)"
           diff "${CASE_DIR}/case/system/fvSolution" "${RUN_ROOT}/system/fvSolution" || true
           exit 13; }
    grep -qE '^[[:space:]]*k[[:space:]]+0\.5;'     "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: k relaxation is not 0.5"; exit 13; }
    grep -qE '^[[:space:]]*omega[[:space:]]+0\.5;' "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: omega relaxation is not 0.5"; exit 13; }
    grep -qE '^[[:space:]]*U[[:space:]]+0\.7;'     "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: U relaxation left 0.7 -- that is a SECOND, UNREGISTERED change"; exit 13; }
    grep -qE '^[[:space:]]*p[[:space:]]+0\.3;'     "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: p field relaxation left 0.3 -- that is a SECOND, UNREGISTERED change"; exit 13; }
    ONE_CHANGE="relaxationFactors/equations k 0.7 -> 0.5 and omega 0.7 -> 0.5, asserted as EXACTLY four diff lines against case/system/fvSolution; U 0.7, p 0.3, nNonOrthogonalCorrectors 1 and both limitedLinear 1 entries all asserted UNCHANGED"
    ;;
  E2b)
    # E2b's baseline is E2a's CONFIGURATION, not E2a's output.  So the staged
    # dictionary is built in two explicit steps and BOTH are asserted:
    #
    #   step 1  reproduce E2a exactly  (k, omega 0.7 -> 0.5)
    #   step 2  the ONE change of THIS rung  (nNonOrthogonalCorrectors 1 -> 2)
    #
    # The single-change claim is then proved where it actually lives: as a diff
    # of the finished dictionary against the E2a baseline reconstructed here,
    # which must be EXACTLY ONE changed line.  Proving it only against the case
    # template would show three changed lines and prove nothing about the rung.
    awk '
      /^relaxationFactors/           { inRF = 1 }
      inRF && /equations/            { inEQ = 1 }
      inEQ && /^[[:space:]]*k[[:space:]]+0\.7;[[:space:]]*$/     { sub(/0\.7;/, "0.5;"); n++ }
      inEQ && /^[[:space:]]*omega[[:space:]]+0\.7;[[:space:]]*$/ { sub(/0\.7;/, "0.5;"); n++ }
      inEQ && /^[[:space:]]*}/       { inEQ = 0 }
                                     { print }
      END                            { if (n != 2) exit 1 }
    ' "${RUN_ROOT}/system/fvSolution" > "${RUN_ROOT}/system/fvSolution.E2a_baseline" \
      || { echo "REFUSED: the inherited E2a rewrite did not change exactly two lines"; exit 13; }

    # The reconstructed E2a baseline must be byte-identical to the dictionary E2a
    # ACTUALLY RAN, wherever that run root is still on disk.  This is the assert
    # that makes "inherited from E2a unchanged" a measurement and not a claim.
    E2A_REF="${RUNS}/JF1E_E2a_${TAG}_A0/system/fvSolution"
    if [ -f "${E2A_REF}" ]; then
      cmp -s "${E2A_REF}" "${RUN_ROOT}/system/fvSolution.E2a_baseline" \
        || { echo "REFUSED: the reconstructed E2a baseline is not byte-identical to the"
             echo "         fvSolution E2a actually ran (${E2A_REF}).  E2b would then be"
             echo "         measuring more than one change."
             diff "${E2A_REF}" "${RUN_ROOT}/system/fvSolution.E2a_baseline" || true
             exit 13; }
      E2A_PROOF="byte-identical to the fvSolution E2a actually ran (${E2A_REF})"
    else
      echo "REFUSED: E2a's run root for ${TAG} is absent, so 'inherited from E2a"
      echo "         unchanged' cannot be measured.  It is not asserted on trust."
      exit 13
    fi

    # step 2 -- THE ONE CHANGE OF THIS RUNG.
    awk '
      /^SIMPLE/                                                            { inS = 1 }
      inS && /^[[:space:]]*nNonOrthogonalCorrectors[[:space:]]+1;[[:space:]]*$/ \
                                                 { sub(/1;/, "2;"); n++ }
                                                                           { print }
      END                                        { if (n != 1) exit 1 }
    ' "${RUN_ROOT}/system/fvSolution.E2a_baseline" > "${RUN_ROOT}/system/fvSolution.E2b" \
      || { echo "REFUSED: the E2b rewrite did not change exactly one line (nNonOrthogonalCorrectors)"; exit 13; }
    mv "${RUN_ROOT}/system/fvSolution.E2b" "${RUN_ROOT}/system/fvSolution"

    # THE SINGLE-CHANGE PROOF: exactly one changed line against the E2a baseline.
    NDIFF_E2A=$(diff "${RUN_ROOT}/system/fvSolution.E2a_baseline" "${RUN_ROOT}/system/fvSolution" \
                  | grep -cE '^[<>]' || true)
    [ "${NDIFF_E2A}" = "2" ] \
      || { echo "REFUSED: E2b changed ${NDIFF_E2A} diff lines against the E2a baseline,"
           echo "         expected 2 (one < and one >).  One change per rung is the"
           echo "         ladder's entire evidentiary content."
           diff "${RUN_ROOT}/system/fvSolution.E2a_baseline" "${RUN_ROOT}/system/fvSolution" || true
           exit 13; }
    # NOTE: `... | grep -q ...` is NOT usable here.  Under `set -o pipefail`,
    # `grep -q` exits on its first match and SIGPIPEs the upstream `grep`, so the
    # pipeline returns non-zero on SUCCESS.  Measured on this very script
    # 2026-09-02: the assert refused a dictionary that was provably correct.
    # The diff is captured first and matched afterwards.
    DIFF_LINES=$(diff "${RUN_ROOT}/system/fvSolution.E2a_baseline" "${RUN_ROOT}/system/fvSolution" || true)
    case "${DIFF_LINES}" in
      *nNonOrthogonalCorrectors*) ;;
      *) echo "REFUSED: the single changed line is not nNonOrthogonalCorrectors"
         echo "${DIFF_LINES}"; exit 13 ;;
    esac

    # and, for the record, exactly three changed lines against the case template.
    NDIFF_T=$(diff "${CASE_DIR}/case/system/fvSolution" "${RUN_ROOT}/system/fvSolution" \
                | grep -cE '^[<>]' || true)
    [ "${NDIFF_T}" = "6" ] \
      || { echo "REFUSED: E2b differs from the case template in ${NDIFF_T} diff lines,"
           echo "         expected 6 (k, omega, nNonOrthogonalCorrectors)"
           diff "${CASE_DIR}/case/system/fvSolution" "${RUN_ROOT}/system/fvSolution" || true
           exit 13; }

    grep -qE '^[[:space:]]*nNonOrthogonalCorrectors[[:space:]]+2;' "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: nNonOrthogonalCorrectors is not 2"; exit 13; }
    grep -qE '^[[:space:]]*k[[:space:]]+0\.5;'     "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: k relaxation is not the inherited 0.5"; exit 13; }
    grep -qE '^[[:space:]]*omega[[:space:]]+0\.5;' "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: omega relaxation is not the inherited 0.5"; exit 13; }
    grep -qE '^[[:space:]]*U[[:space:]]+0\.7;'     "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: U relaxation left 0.7 -- that is a SECOND, UNREGISTERED change"; exit 13; }
    grep -qE '^[[:space:]]*p[[:space:]]+0\.3;'     "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: p field relaxation left 0.3 -- that is a SECOND, UNREGISTERED change"; exit 13; }
    ONE_CHANGE="SIMPLE/nNonOrthogonalCorrectors 1 -> 2, asserted as EXACTLY TWO diff lines (one <, one >) against the E2a baseline, which is itself ${E2A_PROOF}; k 0.5, omega 0.5, U 0.7, p 0.3 and both limitedLinear 1 entries all asserted INHERITED UNCHANGED"
    ;;
  E2c)
    # E2c's baseline is E2b's CONFIGURATION, not E2b's output.  The staged
    # dictionaries are built in three explicit steps and ALL of them are asserted:
    #
    #   step 1  reproduce E2a exactly   (k, omega 0.7 -> 0.5)         [fvSolution]
    #   step 2  reproduce E2b exactly   (nNonOrthogonalCorrectors 1 -> 2)
    #   step 3  the ONE change of THIS rung, which lives in a DIFFERENT FILE:
    #           fvSchemes div(phi,k) and div(phi,omega) limitedLinear 1 -> 0.5
    #
    # Because this rung's change is in fvSchemes, fvSolution is touched by NO
    # part of it, and the proof there is the strongest available: the finished
    # fvSolution must be BYTE-IDENTICAL to the one E2b actually ran, zero diff
    # lines.  The single-change proof for fvSchemes is a diff against the
    # fvSchemes E2b actually ran, which must be EXACTLY FOUR lines (two <, two >).
    #
    # Registration section 3.1 reads the k/omega relaxation pair as ONE control.
    # The same reading applies to div(phi,k)/div(phi,omega): the frozen section 3
    # table names both entries in a single cell as one rung's one change.
    awk '
      /^relaxationFactors/           { inRF = 1 }
      inRF && /equations/            { inEQ = 1 }
      inEQ && /^[[:space:]]*k[[:space:]]+0\.7;[[:space:]]*$/     { sub(/0\.7;/, "0.5;"); n++ }
      inEQ && /^[[:space:]]*omega[[:space:]]+0\.7;[[:space:]]*$/ { sub(/0\.7;/, "0.5;"); n++ }
      inEQ && /^[[:space:]]*}/       { inEQ = 0 }
                                     { print }
      END                            { if (n != 2) exit 1 }
    ' "${RUN_ROOT}/system/fvSolution" > "${RUN_ROOT}/system/fvSolution.E2a_baseline" \
      || { echo "REFUSED: the inherited E2a rewrite did not change exactly two lines"; exit 13; }

    awk '
      /^SIMPLE/                                                            { inS = 1 }
      inS && /^[[:space:]]*nNonOrthogonalCorrectors[[:space:]]+1;[[:space:]]*$/ \
                                                 { sub(/1;/, "2;"); n++ }
                                                                           { print }
      END                                        { if (n != 1) exit 1 }
    ' "${RUN_ROOT}/system/fvSolution.E2a_baseline" > "${RUN_ROOT}/system/fvSolution.E2b_baseline" \
      || { echo "REFUSED: the inherited E2b rewrite did not change exactly one line"; exit 13; }
    cp "${RUN_ROOT}/system/fvSolution.E2b_baseline" "${RUN_ROOT}/system/fvSolution"

    # The reconstruction must be byte-identical to the dictionaries E2b ACTUALLY
    # RAN.  This is the assert that makes "inherited from E2b unchanged" a
    # measurement and not a claim.  It is made on BOTH files, because this rung
    # changes fvSchemes and must prove it departs from E2b's fvSchemes, not
    # merely from a template that happens to match it.
    E2B_SOL="${RUNS}/JF1E_E2b_${TAG}_A0/system/fvSolution"
    E2B_SCH="${RUNS}/JF1E_E2b_${TAG}_A0/system/fvSchemes"
    if [ ! -f "${E2B_SOL}" ] || [ ! -f "${E2B_SCH}" ]; then
      echo "REFUSED: E2b's run root for ${TAG} is absent or incomplete, so 'inherited"
      echo "         from E2b unchanged' cannot be measured.  It is not asserted on trust."
      echo "         looked for ${E2B_SOL} and ${E2B_SCH}"
      exit 13
    fi
    cmp -s "${E2B_SOL}" "${RUN_ROOT}/system/fvSolution" \
      || { echo "REFUSED: the reconstructed E2b baseline fvSolution is not byte-identical"
           echo "         to the fvSolution E2b actually ran (${E2B_SOL}).  E2c would then"
           echo "         be measuring more than one change."
           diff "${E2B_SOL}" "${RUN_ROOT}/system/fvSolution" || true
           exit 13; }
    cmp -s "${E2B_SCH}" "${RUN_ROOT}/system/fvSchemes" \
      || { echo "REFUSED: the staged fvSchemes, BEFORE this rung's change, is not"
           echo "         byte-identical to the fvSchemes E2b actually ran (${E2B_SCH})."
           diff "${E2B_SCH}" "${RUN_ROOT}/system/fvSchemes" || true
           exit 13; }
    cp "${RUN_ROOT}/system/fvSchemes" "${RUN_ROOT}/system/fvSchemes.E2b_baseline"

    # step 3 -- THE ONE CHANGE OF THIS RUNG.  Scoped to the divSchemes block and
    # to the two named entries.  A bare `sed s/limitedLinear 1/limitedLinear 0.5/g`
    # would be the same edit today and a silent second change the moment another
    # limitedLinear entry is added to this dictionary.
    awk '
      /^divSchemes/ { inD = 1 }
      inD && /^[[:space:]]*div\(phi,k\)[[:space:]]+bounded Gauss limitedLinear 1;[[:space:]]*$/ \
                    { sub(/limitedLinear 1;/, "limitedLinear 0.5;"); n++ }
      inD && /^[[:space:]]*div\(phi,omega\)[[:space:]]+bounded Gauss limitedLinear 1;[[:space:]]*$/ \
                    { sub(/limitedLinear 1;/, "limitedLinear 0.5;"); n++ }
      inD && /^}/   { inD = 0 }
                    { print }
      END           { if (n != 2) exit 1 }
    ' "${RUN_ROOT}/system/fvSchemes.E2b_baseline" > "${RUN_ROOT}/system/fvSchemes.E2c" \
      || { echo "REFUSED: the E2c rewrite did not change exactly two lines (div(phi,k) and div(phi,omega))"; exit 13; }
    mv "${RUN_ROOT}/system/fvSchemes.E2c" "${RUN_ROOT}/system/fvSchemes"

    # THE SINGLE-CHANGE PROOF: exactly four changed lines against E2b's fvSchemes.
    NDIFF_SCH=$(diff "${RUN_ROOT}/system/fvSchemes.E2b_baseline" "${RUN_ROOT}/system/fvSchemes" \
                  | grep -cE '^[<>]' || true)
    [ "${NDIFF_SCH}" = "4" ] \
      || { echo "REFUSED: E2c changed ${NDIFF_SCH} diff lines in fvSchemes against the E2b"
           echo "         baseline, expected 4 (two <, two >).  One change per rung is the"
           echo "         ladder's entire evidentiary content."
           diff "${RUN_ROOT}/system/fvSchemes.E2b_baseline" "${RUN_ROOT}/system/fvSchemes" || true
           exit 13; }
    # NOTE: `... | grep -q ...` is NOT usable here.  Under `set -o pipefail`,
    # `grep -q` exits on its first match and SIGPIPEs the upstream command, so the
    # pipeline returns non-zero on SUCCESS.  Measured on this very script
    # 2026-09-02 at E2b: the assert refused a dictionary that was provably
    # correct.  The diff is captured FIRST into a variable and matched afterwards.
    DIFF_LINES=$(diff "${RUN_ROOT}/system/fvSchemes.E2b_baseline" "${RUN_ROOT}/system/fvSchemes" || true)
    case "${DIFF_LINES}" in
      *'div(phi,k)'*) ;;
      *) echo "REFUSED: the changed lines do not name div(phi,k)"; echo "${DIFF_LINES}"; exit 13 ;;
    esac
    case "${DIFF_LINES}" in
      *'div(phi,omega)'*) ;;
      *) echo "REFUSED: the changed lines do not name div(phi,omega)"; echo "${DIFF_LINES}"; exit 13 ;;
    esac

    # fvSolution is NOT this rung's file and must differ from E2b's by NOTHING.
    NDIFF_SOL=$(diff "${E2B_SOL}" "${RUN_ROOT}/system/fvSolution" | grep -cE '^[<>]' || true)
    [ "${NDIFF_SOL}" = "0" ] \
      || { echo "REFUSED: fvSolution differs from E2b's in ${NDIFF_SOL} diff lines; this rung"
           echo "         changes fvSchemes only, so any fvSolution change is a SECOND,"
           echo "         UNREGISTERED change."
           diff "${E2B_SOL}" "${RUN_ROOT}/system/fvSolution" || true
           exit 13; }

    grep -qE '^[[:space:]]*div\(phi,k\)[[:space:]]+bounded Gauss limitedLinear 0\.5;' "${RUN_ROOT}/system/fvSchemes" \
      || { echo "REFUSED: div(phi,k) is not limitedLinear 0.5"; exit 13; }
    grep -qE '^[[:space:]]*div\(phi,omega\)[[:space:]]+bounded Gauss limitedLinear 0\.5;' "${RUN_ROOT}/system/fvSchemes" \
      || { echo "REFUSED: div(phi,omega) is not limitedLinear 0.5"; exit 13; }
    grep -qE '^[[:space:]]*div\(phi,U\)[[:space:]]+bounded Gauss linearUpwind grad\(U\);' "${RUN_ROOT}/system/fvSchemes" \
      || { echo "REFUSED: div(phi,U) left its frozen linearUpwind scheme -- that is a SECOND, UNREGISTERED change"; exit 13; }
    grep -qE '^[[:space:]]*nNonOrthogonalCorrectors[[:space:]]+2;' "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: nNonOrthogonalCorrectors is not the inherited 2"; exit 13; }
    grep -qE '^[[:space:]]*k[[:space:]]+0\.5;'     "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: k relaxation is not the inherited 0.5"; exit 13; }
    grep -qE '^[[:space:]]*omega[[:space:]]+0\.5;' "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: omega relaxation is not the inherited 0.5"; exit 13; }
    grep -qE '^[[:space:]]*U[[:space:]]+0\.7;'     "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: U relaxation left 0.7 -- that is a SECOND, UNREGISTERED change"; exit 13; }
    grep -qE '^[[:space:]]*p[[:space:]]+0\.3;'     "${RUN_ROOT}/system/fvSolution" || { echo "REFUSED: p field relaxation left 0.3 -- that is a SECOND, UNREGISTERED change"; exit 13; }
    ONE_CHANGE="fvSchemes divSchemes div(phi,k) and div(phi,omega) limitedLinear 1 -> limitedLinear 0.5, asserted as EXACTLY FOUR diff lines (two <, two >) against the fvSchemes E2b actually ran (${E2B_SCH}); fvSolution asserted byte-identical to the one E2b actually ran (${E2B_SOL}), ZERO diff lines, so nNonOrthogonalCorrectors 2, k 0.5, omega 0.5, U 0.7 and p 0.3 are INHERITED UNCHANGED; div(phi,U) linearUpwind asserted UNCHANGED"
    ;;
esac

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
  echo "-- the ONE change of rung ${RUNG}, and the asserts that bound it --"
  echo "   ${ONE_CHANGE}"
  echo "   0/ seeded from ${SEED_ROOT}/${SEED_TIME} (E1's configuration, inherited)"
  echo "   seed check: ${SEED_CHECK}"
  echo "-- relaxationFactors ACTUALLY IN THE STAGED DICTIONARY --"
  sed -n '/^relaxationFactors/,/^}/p' "${RUN_ROOT}/system/fvSolution"
  echo "-- the controls the OTHER rungs own, as actually staged here --"
  grep -E 'nNonOrthogonalCorrectors' "${RUN_ROOT}/system/fvSolution"
  grep -E 'div\(phi,(k|omega)\)'     "${RUN_ROOT}/system/fvSchemes"
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
