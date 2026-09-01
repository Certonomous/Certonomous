#!/usr/bin/env bash
# Detached launcher.  rc is captured INSIDE, never inferred from the setsid line.
R="/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap"
OUT="${R}/JF1E_E2a_LAUNCH_RC.txt"
echo "launched_utc $(date -u +%Y-%m-%dT%H:%M:%SZ) driver_pid $$" > "${OUT}"
nice -n 5 bash /home/ubuntu/Certonomous/cases/JF1_JET_FLAP/run_jf1e_chain.sh --rung=E2a
RC=$?
echo "chain_rc ${RC}" >> "${OUT}"
echo "finished_utc $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${OUT}"
exit ${RC}
