#!/usr/bin/env bash
# Launcher / sync for ARM 2 of the Ling (2016) TBNN GPU arm (matched-update-count).
#
# DO NOT RUN `launch` before the arm-2 pre-registration is signed and frozen:
# the driver is launched with --frozen, which asserts exactly that. The node
# gpu1 is STOPPED by the owner; only Sanaa starts it (GPU_CAPABILITY_STATE sec. 8).
# The driver is launched with --shutdown: on every completion path it writes
# out/COMPLETE.json and then powers the node off itself (owner-approved standing
# mechanism), so `pull` is normally run AFTER Sanaa restarts the node, or from a
# second terminal before it halts.
#
# Restartable: `launch` re-copies the driver, relaunches ONLY if it is not
# already running (the driver skips DONE stages and resumes from its per-epoch
# checkpoint), and records the run-window start with a `date -u` read on the
# node in the SAME shell line as the launch.
#
# Usage:  bash run_all_gpu_v2.sh launch     # copy driver, launch (if needed), record start
#         bash run_all_gpu_v2.sh --pull     # rsync out dir + logs back, never launch
#         bash run_all_gpu_v2.sh status     # driver.pid / COMPLETE.json state, never launch
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GPU=gpu1                                    # ~/.ssh/config alias, 172.31.44.162
RDIR='~/r_ling_gpu/arm2'
RPY='~/r_ling_gpu/venv/bin/python'
RDATA='~/r_ling_gpu/data/dataset.npz'       # sha verified by the driver's g0 stage
LOCAL_ROOT=/home/ubuntu/closure-data/tbnn_gpu/arm2
LOCAL_OUT="$LOCAL_ROOT/out"
DRIVER=train_gpu_ling_v2.py

mode="${1:-}"
case "$mode" in
  launch)
    mkdir -p "$LOCAL_ROOT"
    # 1. copy the driver (idempotent; the driver never edits itself on gpu1)
    ssh "$GPU" "mkdir -p $RDIR/out"
    scp -q "$HERE/$DRIVER" "$GPU:$RDIR/$DRIVER"
    # 2. driver sha on the node must equal the repo copy (the frozen file IS the file that runs)
    local_sha=$(sha256sum "$HERE/$DRIVER" | cut -d' ' -f1)
    remote_sha=$(ssh "$GPU" "sha256sum $RDIR/$DRIVER | cut -d' ' -f1")
    if [[ "$local_sha" != "$remote_sha" ]]; then
      echo "[run_all_v2] REFUSING: driver sha differs (local $local_sha, node $remote_sha)"; exit 2
    fi
    # 3. launch under nohup unless already running; the launch and the
    #    run-window `date -u` read happen in the same remote shell line
    start=$(ssh "$GPU" "
      set -e
      cd $RDIR
      if [ -f driver.pid ] && kill -0 \$(cat driver.pid) 2>/dev/null; then
        echo '[run_all_v2] driver already running, pid' \$(cat driver.pid) >&2
        echo ALREADY_RUNNING
      else
        nohup $RPY $DRIVER --frozen --shutdown --data $RDATA --out $RDIR/out >> $RDIR/driver.log 2>&1 & echo \$! > driver.pid; date -u +%Y-%m-%dT%H:%M:%SZ
      fi
    ")
    if [[ "$start" == "ALREADY_RUNNING" ]]; then
      echo "[run_all_v2] not relaunched; existing run continues"
    else
      printf '{\n "start_utc": "%s",\n "driver": "%s",\n "driver_sha256": "%s",\n "node": "%s",\n "remote_out": "%s"\n}\n' \
        "$start" "$DRIVER" "$local_sha" "$GPU" "$RDIR/out" > "$LOCAL_ROOT/run_window.json"
      echo "[run_all_v2] launched at $start (node clock, same shell line as the launch); pid $(ssh "$GPU" "cat $RDIR/driver.pid")"
      echo "[run_all_v2] wrote $LOCAL_ROOT/run_window.json"
    fi
    ;;
  --pull|pull)
    mkdir -p "$LOCAL_OUT"
    rsync -a "$GPU:$RDIR/out/" "$LOCAL_OUT/"
    rsync -a "$GPU:$RDIR/driver.log" "$LOCAL_OUT/driver.log" 2>/dev/null || true
    rsync -a "$GPU:$RDIR/driver.pid" "$LOCAL_OUT/driver.pid" 2>/dev/null || true
    echo "[run_all_v2] pulled $GPU:$RDIR/out/ -> $LOCAL_OUT/ at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    ls "$LOCAL_OUT" | sed 's/^/  /'
    [[ -f "$LOCAL_OUT/COMPLETE.json" ]] && { echo "[run_all_v2] COMPLETE.json:"; cat "$LOCAL_OUT/COMPLETE.json"; }
    ;;
  status)
    ssh "$GPU" "
      cd $RDIR 2>/dev/null || { echo '[run_all_v2] no $RDIR on the node'; exit 0; }
      if [ -f driver.pid ] && kill -0 \$(cat driver.pid) 2>/dev/null; then echo 'driver RUNNING pid' \$(cat driver.pid); else echo 'driver not running'; fi
      ls out 2>/dev/null | sed 's/^/  /'
      [ -f out/COMPLETE.json ] && cat out/COMPLETE.json
      tail -n 5 driver.log 2>/dev/null || true
    "
    ;;
  *)
    echo "usage: bash run_all_gpu_v2.sh launch | --pull | status" >&2
    exit 1
    ;;
esac
