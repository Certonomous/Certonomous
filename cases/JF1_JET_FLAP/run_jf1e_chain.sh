#!/usr/bin/env bash
# =============================================================================
# JF1E RUNG E1 -- THE CONTINUATION CHAIN, RUN IN SANAA'S ORDER.
#
#   C_mu = 0 -> 0.05 -> 0.1 -> 0.2 -> 0.4
#
# Registration: verification/campaign/JF1E_TURBULENCE_STALL_ESCALATION_PREREGISTRATION.md
#   frozen 6e83157c112cdf606094f88ff0592bf1b02bc4b3, section 3.
#
# The chain is SEQUENTIAL by construction: each link's seed is the previous
# link's own output, so it cannot be parallelised and no attempt is made to.
#
# A BROKEN LINK STOPS THE CHAIN.  If a link exits non-zero, the links after it
# would be seeded from a field that does not exist or from the wrong row, so the
# driver stops and says which link broke.  It does NOT fall back to a freestream
# start: that would silently turn a continuation rung into a baseline rung and
# the rung would then measure nothing.
#
# The chain start is the SLOT-CLOSED reference row, whose jetSlot is polyMesh
# type `wall` where every blown row's is type `patch`.  It is NOT "the same wing
# with the jet turned down to zero".  The splice is legitimate because the two
# meshes' points/faces/owner/neighbour are byte-identical -- asserted per link
# inside run_jf1e.sh, not assumed here.
# =============================================================================
set -u
set -o pipefail

CASE_DIR="/home/ubuntu/Certonomous/cases/JF1_JET_FLAP"
RUNS="/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap"
PREREG="6e83157c112cdf606094f88ff0592bf1b02bc4b3"
LOG="${RUNS}/JF1E_E1_CHAIN.log"

SEED_ROOT="${RUNS}/JF1_L1_UNBLOWN_A0"
SEED_TIME="8000"

{
  echo "== JF1E RUNG E1 CONTINUATION CHAIN =="
  echo "   started $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "   prereg  ${PREREG}"
  echo "   chain   C_mu 0 (slot-closed reference) -> 0.05 -> 0.1 -> 0.2 -> 0.4"
  echo "   CAVEAT D-1: no link is seeded from a CONVERGED field.  This lab has"
  echo "   none at any C_mu.  Each seed is a stationary-but-clipping-held final"
  echo "   field, and no report of this chain may call it converged."
  echo
} > "${LOG}"

for CMU in 0.05 0.1 0.2 0.4; do
  case "${CMU}" in
    0.05) TAG="CMU005" ;; 0.1) TAG="CMU010" ;;
    0.2)  TAG="CMU020" ;; 0.4) TAG="CMU040" ;;
  esac
  CASE_ID="JF1E_E1_${TAG}_A0"
  {
    echo "--- LINK C_mu ${CMU} -> ${CASE_ID} ---"
    echo "    seed ${SEED_ROOT}/${SEED_TIME}"
    echo "    launched $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } >> "${LOG}"

  bash "${CASE_DIR}/run_jf1e.sh" \
      --prereg-commit="${PREREG}" \
      --rung=E1 --cmu="${CMU}" \
      --seed-from="${SEED_ROOT}" --seed-time="${SEED_TIME}" \
      >> "${LOG}" 2>&1
  RC=$?

  if [ ${RC} -ne 0 ]; then
    {
      echo "    LINK FAILED rc=${RC} -- CHAIN STOPPED at C_mu ${CMU}."
      echo "    The links after this one are NOT run: they would be seeded from a"
      echo "    field that does not exist.  No freestream fallback is taken --"
      echo "    that would turn a continuation rung into a baseline rung."
      echo "    finished $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } >> "${LOG}"
    exit ${RC}
  fi

  echo "    LINK OK  $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${LOG}"
  SEED_ROOT="${RUNS}/${CASE_ID}"
  SEED_TIME="8000"
done

{
  echo
  echo "== CHAIN COMPLETE, all four links, $(date -u +%Y-%m-%dT%H:%M:%SZ) =="
  echo "   Gate E is evaluated by the comparator, not here.  This driver reports"
  echo "   completion only; it emits no verdict."
} >> "${LOG}"
exit 0
