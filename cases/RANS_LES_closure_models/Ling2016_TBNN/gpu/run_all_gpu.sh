#!/usr/bin/env bash
# Launcher / sync for the Ling (2016) TBNN GPU arm — PREREGISTRATION_DRAFT.md.
#
# DO NOT RUN before the pre-registration is signed and frozen: the driver is
# launched with --frozen, which asserts exactly that. Restartable: re-running
# this script re-copies the driver, relaunches it ONLY if it is not already
# running (the driver itself skips stages whose status JSON says DONE), and
# always rsyncs the out directory back to the lab box.
#
# Usage:  bash run_all_gpu.sh          # launch (if needed) + sync back
#         bash run_all_gpu.sh sync     # sync back only, never launch
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GPU=gpu1                                    # ~/.ssh/config alias, 172.31.44.162
RDIR='~/r_ling_gpu'
RPY='~/r_ling_gpu/venv/bin/python'
LOCAL_OUT=/home/ubuntu/closure-data/tbnn_gpu/out
PIDFILE='~/r_ling_gpu/driver.pid'

mkdir -p "$LOCAL_OUT"

# 1. copy the driver (idempotent; the driver never edits itself on gpu1)
scp -q "$HERE/train_gpu_ling.py" "$GPU:$RDIR/train_gpu_ling.py"

# 2. launch under nohup unless already running or launch-suppressed
if [[ "${1:-}" != "sync" ]]; then
  ssh "$GPU" "
    set -e
    cd ~/r_ling_gpu
    if [ -f driver.pid ] && kill -0 \$(cat driver.pid) 2>/dev/null; then
      echo '[run_all] driver already running, pid' \$(cat driver.pid)
    else
      mkdir -p out
      nohup $RPY train_gpu_ling.py --frozen \
          --data ~/r_ling_gpu/data/dataset.npz \
          --out  ~/r_ling_gpu/out \
          >> ~/r_ling_gpu/driver.log 2>&1 &
      echo \$! > driver.pid
      echo '[run_all] launched driver, pid' \$(cat driver.pid)
    fi
  "
fi

# 3. sync results back to the lab box (safe to repeat any time)
rsync -a "$GPU:$RDIR/out/" "$LOCAL_OUT/"
rsync -a "$GPU:$RDIR/driver.log" "$LOCAL_OUT/driver.log" 2>/dev/null || true
echo "[run_all] synced gpu1:$RDIR/out/ -> $LOCAL_OUT/"
ls "$LOCAL_OUT" | sed 's/^/  /'
