#!/bin/bash
# Detached wrapper for ratio_watch_t4e.py. rc is captured INSIDE this wrapper:
# `setsid timeout cmd` exits 0 for every outcome, so an rc read around the setsid
# line is meaningless. Nothing here touches the live case or the solver.
cd /home/ubuntu/Certonomous/verification/runs/T-family/T4e_runs || exit 1
echo "WRAPPER: start $(date -u +%FT%TZ) pid=$$ ppid=$PPID" >> A2_RATIO_WATCH.nohup
python3 ratio_watch_t4e.py --mirror /home/ubuntu/certonomous-runs/T4e_A2_mirror/T4e_IJ_f >> A2_RATIO_WATCH.nohup 2>&1
RC=$?
echo "WRAPPER: python3 exited rc=$RC at $(date -u +%FT%TZ)" >> A2_RATIO_WATCH.nohup
