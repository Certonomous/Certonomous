#!/usr/bin/env bash
# queue_runner.sh -- start scripts/queue_runner.py detached IF it is not already running.
# Idempotent: safe to call from cron every minute and from @reboot. The runner's own
# pidfile lock (verification/queue/runner.pid + liveness check) refuses a second copy,
# so this wrapper cannot start two. Sanaa, 2026-08-26 (73eccb1b): "I do NOT want the
# instances to be idle at any point even if the lab dies."
REPO=/home/ubuntu/Certonomous
PIDFILE=$REPO/verification/queue/runner.pid
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
  exit 0   # alive; nothing to do
fi
cd "$REPO" || exit 1
setsid nohup python3 "$REPO/scripts/queue_runner.py" --daemon >> "$REPO/verification/queue/runner.out" 2>&1 < /dev/null &
echo "$(date -u +%FT%TZ) queue_runner.sh: (re)started runner pid $!" >> "$REPO/verification/queue/runner.restarts.log"
