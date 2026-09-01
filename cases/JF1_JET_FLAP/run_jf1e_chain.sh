#!/usr/bin/env bash
# =============================================================================
# JF1E CONTINUATION CHAIN, RUN IN SANAA'S ORDER.  ONE RUNG PER INVOCATION.
#
# USAGE:  run_jf1e_chain.sh --rung=E1|E2a
#
# The chain STRUCTURE is E1's configuration and every later rung inherits it
# unchanged (registration section 3: a failed rung hands its configuration to the
# next rung as the new baseline).  Each rung differs from the rung below it by
# exactly one control, and that control is applied inside run_jf1e.sh, where it
# is asserted against the case template line by line.
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

RUNG=""
for a in "$@"; do
  case "$a" in
    --rung=*) RUNG="${a#*=}" ;;
    *) echo "REFUSED: unrecognised argument '$a'"; exit 3 ;;
  esac
done

# THE REGISTERED RUNG CAP, section 6 of the frozen registration, VERBATIM.
# CLAUDE.md rule 12: an overrun STOPS the run; it does not get a new budget.
# The cap is enforced HERE as well as per-link, because the per-link wrapper cap
# (40 core-min) times four links is 160, which is ABOVE the rung's registered
# 150 -- so a per-link cap alone would let the rung overspend its registration.
case "${RUNG}" in
  E1)  RUNG_CAP_CORE_MIN="150" ;;
  E2a) RUNG_CAP_CORE_MIN="150" ;;
  *) echo "REFUSED: --rung must be E1 or E2a (frozen section 3 order); got '${RUNG}'"; exit 3 ;;
esac

LOG="${RUNS}/JF1E_${RUNG}_CHAIN.log"

SEED_ROOT="${RUNS}/JF1_L1_UNBLOWN_A0"
SEED_TIME="8000"
SPENT_CORE_MIN="0"

{
  echo "== JF1E RUNG ${RUNG} CONTINUATION CHAIN =="
  echo "   started $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "   prereg  ${PREREG}"
  echo "   rung cap ${RUNG_CAP_CORE_MIN} core-min (registration section 6, frozen)"
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
  CASE_ID="JF1E_${RUNG}_${TAG}_A0"
  {
    echo "--- LINK C_mu ${CMU} -> ${CASE_ID} ---"
    echo "    seed ${SEED_ROOT}/${SEED_TIME}"
    echo "    launched $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } >> "${LOG}"

  bash "${CASE_DIR}/run_jf1e.sh" \
      --prereg-commit="${PREREG}" \
      --rung="${RUNG}" --cmu="${CMU}" \
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

  # --- BUDGET, ACCUMULATED FROM THE LINK'S OWN MEASURED FIGURE ---------------
  # Read from the status file the wrapper wrote, never from a wall clock kept
  # here: the wrapper's EXIT trap is what dates the run.
  LINK_CM=$(grep -E "^core_min_MEASURED" "${RUNS}/${CASE_ID}/RUN_STATUS.${CASE_ID}.txt" 2>/dev/null | awk '{print $2}')
  if [ -z "${LINK_CM:-}" ]; then
    echo "    LINK OK but NO MEASURED COST ON DISK -- CHAIN STOPPED (a rung whose" >> "${LOG}"
    echo "    spend cannot be read cannot be held to its registered cap)." >> "${LOG}"
    exit 20
  fi
  SPENT_CORE_MIN=$(awk -v a="${SPENT_CORE_MIN}" -v b="${LINK_CM}" 'BEGIN{printf "%.4f", a+b}')
  echo "    LINK OK  $(date -u +%Y-%m-%dT%H:%M:%SZ)  ${LINK_CM} core-min; rung total ${SPENT_CORE_MIN} / ${RUNG_CAP_CORE_MIN}" >> "${LOG}"

  if awk -v s="${SPENT_CORE_MIN}" -v c="${RUNG_CAP_CORE_MIN}" 'BEGIN{exit !(s > c)}'; then
    {
      echo "    RUNG CAP STRUCK: ${SPENT_CORE_MIN} core-min > ${RUNG_CAP_CORE_MIN} registered."
      echo "    CHAIN STOPPED.  CLAUDE.md rule 12: an overrun stops the run; it does"
      echo "    NOT get a new budget.  The links after this one are not run."
      echo "    finished $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } >> "${LOG}"
    exit 21
  fi

  SEED_ROOT="${RUNS}/${CASE_ID}"
  SEED_TIME="8000"
done

{
  echo
  echo "== CHAIN COMPLETE, all four links, $(date -u +%Y-%m-%dT%H:%M:%SZ) =="
  echo "   rung ${RUNG} measured spend ${SPENT_CORE_MIN} core-min against a registered cap of ${RUNG_CAP_CORE_MIN}"
  echo "   Gate E is evaluated by the comparator, not here.  This driver reports"
  echo "   completion only; it emits no verdict."
} >> "${LOG}"
exit 0
