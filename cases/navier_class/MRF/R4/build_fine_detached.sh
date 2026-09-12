#!/usr/bin/env bash
# Detached wrapper for the R4 fine-level mesh build. rc is captured INSIDE this
# wrapper, never around the setsid line -- `setsid timeout cmd` exits 0 for every
# outcome (memory: setsid-parent-returns-zero).
RUN=/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R4/fine
export MRF_FEATURE_THICKNESS_M=0.00155
date -u +%FT%TZ > "$(dirname "$RUN")/BUILD_START_UTC.txt"
t0=$(date +%s)
bash /home/ubuntu/Certonomous/cases/navier_class/MRF/build_level_r4.sh "$RUN" 82 82 92 8
rc=$?
t1=$(date +%s)
echo "$rc" > "$(dirname "$RUN")/RC.build"
echo "$((t1-t0))" > "$(dirname "$RUN")/WALL_SECONDS.build"
date -u +%FT%TZ > "$(dirname "$RUN")/BUILD_END_UTC.txt"
