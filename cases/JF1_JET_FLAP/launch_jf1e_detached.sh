#!/usr/bin/env bash
# Detached launcher.  rc is captured INSIDE, never inferred from the setsid line.
#
# `setsid timeout cmd` returns 0 for EVERY outcome of cmd, so a wrapper that
# reads rc around the setsid line reads the launcher's success, not the run's.
# rc is therefore taken here, inside the detached process, and written to disk.
#
# USAGE: launch_jf1e_detached.sh --rung=E1|E2a|E2b|E2c
R="/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap"

RUNG=""
for a in "$@"; do
  case "$a" in
    --rung=*) RUNG="${a#*=}" ;;
    *) echo "REFUSED: unrecognised argument '$a'"; exit 3 ;;
  esac
done
case "${RUNG}" in
  E1|E2a|E2b|E2c) ;;
  *) echo "REFUSED: --rung must be E1, E2a, E2b or E2c (frozen section 3 order); got '${RUNG}'"; exit 3 ;;
esac

OUT="${R}/JF1E_${RUNG}_LAUNCH_RC.txt"
echo "launched_utc $(date -u +%Y-%m-%dT%H:%M:%SZ) driver_pid $$" > "${OUT}"
nice -n 5 bash /home/ubuntu/Certonomous/cases/JF1_JET_FLAP/run_jf1e_chain.sh --rung="${RUNG}"
RC=$?
echo "chain_rc ${RC}" >> "${OUT}"
echo "finished_utc $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${OUT}"
exit ${RC}
