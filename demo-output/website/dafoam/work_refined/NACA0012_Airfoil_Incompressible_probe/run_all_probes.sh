#!/bin/bash
cd "$(dirname "$0")"
LOGDIR=/home/ubuntu/Certonomous/demo-output/website/dafoam
# only the pairs not already successfully completed (idx0 +h done in a prior partial run)
for pair in "0:-1e-4" "1:1e-4" "1:-1e-4" "6:1e-4" "6:-1e-4" "4:1e-4" "4:-1e-4"; do
  idx="${pair%%:*}"
  step="${pair##*:}"
  tag="idx${idx}_$(echo $step | sed 's/^-/neg/;s/\./p/')"
  echo "=== RUNNING $tag (idx=$idx step=$step) ==="
  # clean any stray non-zero time dirs from a previous run to avoid renameSolution collisions
  sudo rm -rf processor*/[1-9]* processor*/0.[0-9]* 2>/dev/null
  sudo docker run --rm --cpus=3 \
    -v "$(pwd)":/home/dafoamuser/mount \
    -w /home/dafoamuser/mount \
    dafoam/opt-packages:latest \
    bash -lc "source /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun --allow-run-as-root -np 4 python probeFreshY.py --idx $idx --step=$step" \
    > "$LOGDIR/probe_${tag}_run1.log" 2>&1
  rc=$?
  echo "=== DONE $tag (exit $rc) ==="
done
echo "ALL PROBES DONE"
