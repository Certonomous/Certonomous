#!/bin/bash
# F6d Option A queue runner.
# Survives the death of any agent: it is launched with setsid and holds its own
# concurrency limit. Launches only cases that have no log.simpleFoam yet, so it
# is safe to re-run and will never disturb a case already running or finished.
ROOT=/home/ubuntu/Certonomous/demo-output/website/dafoam/f6d_random_matrix_uq/f6d_option_a
MAXJOBS=8
REMAINING="d0.2_s000 d0.2_s027 d0.6_s011 d0.6_s021 d0.6_s022 d0.6_s035 d0.6_s039 null"

source /usr/lib/openfoam/openfoam2606/etc/bashrc || exit 91

for c in $REMAINING; do
  if [ -f "$ROOT/$c/log.simpleFoam" ]; then
    continue                      # already started by someone else
  fi
  while [ "$(pgrep -c simpleFoam || true)" -ge "$MAXJOBS" ]; do
    sleep 20
  done
  cd "$ROOT/$c" || continue
  setsid nohup simpleFoam > "$ROOT/$c/log.simpleFoam" 2>&1 < /dev/null &
  sleep 3
done

wait
echo "queue_runner: all remaining cases launched" > "$ROOT/.queue_runner_done"
