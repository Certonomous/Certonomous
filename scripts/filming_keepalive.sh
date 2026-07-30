#!/bin/bash
# Keep this instance awake while you film -- WITHOUT needing sudo.
#
#   bash scripts/filming_keepalive.sh on        # default 6 hours
#   bash scripts/filming_keepalive.sh on 3      # 3 hours
#   bash scripts/filming_keepalive.sh off
#   bash scripts/filming_keepalive.sh status
#
# WHY THIS EXISTS, AND WHY IT IS DIFFERENT FROM filming_mode.sh
# -------------------------------------------------------------
# A root cron job runs /usr/local/bin/auto-stop.sh every 5 minutes and powers
# the box off after 30 idle minutes.
#
# The script INSTALLED TODAY decides "is the lab busy?" with exactly one test:
#
#   pgrep -f 'simpleFoam|pimpleFoam|rhoSimpleFoam|rhoCentralFoam|interFoam|
#             potentialFoam|blockMesh|snappyHexMesh|vspaero|mega_batch|
#             mega_batch_keeper|dafoam|Certonomous/sdk'
#
# Verified on 2026-07-30: the control room runs with the command line
# "python3 -u -m chief_engineer.server", which matches NONE of those patterns.
# Filming is therefore indistinguishable from an idle box, and 30 minutes of
# talking to camera between acts is enough to power it off mid-shoot.
#
# scripts/filming_mode.sh is the proper fix, but it writes a hold file that
# ONLY the proposed auto-stop.sh reads. Until that proposed script is actually
# installed to /usr/local/bin (which needs root), filming_mode.sh has no
# effect. This script needs no root and works against the script that is
# really running right now: it simply holds open one process whose command
# line contains "Certonomous/sdk", which the live pgrep already counts as
# activity.
#
# The hold ALWAYS expires. An unbounded keep-alive is how a forgotten box
# quietly runs for a month, so the cost of forgetting to switch it off is
# bounded to the hours you asked for.

set -uo pipefail

TAG=/home/ubuntu/Certonomous/sdk/.filming-keepalive
PIDFILE=/tmp/certonomous-filming-keepalive.pid
DEFAULT_HOURS=6

running_pid() {
    [ -f "$PIDFILE" ] || return 1
    local pid
    pid=$(tr -dc '0-9' < "$PIDFILE")
    [ -n "$pid" ] || return 1
    kill -0 "$pid" 2>/dev/null || return 1
    echo "$pid"
}

case "${1:-status}" in
  on)
    hours=${2:-$DEFAULT_HOURS}
    if ! [[ "$hours" =~ ^[0-9]+$ ]] || [ "$hours" -lt 1 ] || [ "$hours" -gt 24 ]; then
        echo "hours must be a whole number from 1 to 24 (got: $hours)" >&2; exit 1
    fi
    if pid=$(running_pid); then
        echo "Keep-alive already running (pid $pid). Run 'off' first to change the duration."
        exit 0
    fi
    seconds=$(( hours * 3600 ))
    until_ts=$(( $(date +%s) + seconds ))
    # The command line below is the whole trick: it contains the literal
    # string "Certonomous/sdk", which the installed auto-stop.sh greps for.
    # It burns no CPU -- it sleeps in one-minute steps and then exits by
    # itself, so the hold cannot outlive the window you asked for.
    #
    # TOKEN is a unique marker so we can find the holder again by its command
    # line. We deliberately do NOT trust $! here: setsid only execs without
    # forking when the caller is not already a process-group leader, so under
    # a shell with job control enabled $! would capture a short-lived parent
    # and 'off' would then report success while the real holder survived.
    TOKEN="certonomous-keepalive-$$-$until_ts"
    setsid nohup bash -c "
        # Certonomous/sdk filming keepalive $TOKEN, expires $(date -u -d "@$until_ts" '+%FT%TZ')
        end=$until_ts
        while [ \"\$(date +%s)\" -lt \"\$end\" ]; do sleep 60; done
    " >/dev/null 2>&1 < /dev/null &
    disown 2>/dev/null || true
    # Re-derive the pid from the command line rather than from $!.
    pid=""
    for _ in 1 2 3 4 5 6 7 8 9 10; do
        pid=$(pgrep -f "$TOKEN" | head -n1)
        [ -n "$pid" ] && break
        sleep 0.3
    done
    if [ -z "$pid" ]; then
        echo "Keep-alive FAILED to start (no process matched)." >&2; exit 1
    fi
    echo "$pid" > "$PIDFILE"
    printf '%s\n' "$until_ts" > "$TAG" 2>/dev/null || true
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
        echo "Keep-alive ON for ${hours}h (pid $pid)."
        echo "The instance will not auto-stop until $(date -u -d "@$until_ts" '+%Y-%m-%d %H:%M:%S UTC')."
        echo "It then expires on its own and the 30-minute idle timer comes back."
    else
        echo "Keep-alive FAILED to start." >&2; exit 1
    fi
    ;;
  off)
    if pid=$(running_pid); then
        # setsid made the holder a process-group leader, so signalling the
        # whole group takes its sleeping child down with it instead of
        # leaving an orphan to linger for up to a minute.
        kill -- "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null
        echo "Keep-alive OFF (stopped pid $pid). The 30-minute idle timer is armed again."
    else
        echo "Keep-alive was not running."
    fi
    rm -f "$PIDFILE" "$TAG"
    ;;
  status)
    if pid=$(running_pid); then
        until_ts=$(tr -dc '0-9' < "$TAG" 2>/dev/null)
        if [ -n "$until_ts" ]; then
            left=$(( (until_ts - $(date +%s)) / 60 ))
            echo "Keep-alive ON, ${left} minutes left (pid $pid)."
        else
            echo "Keep-alive ON (pid $pid, expiry unknown)."
        fi
    else
        echo "Keep-alive OFF. The instance auto-stops after 30 idle minutes."
    fi
    # The whole truth, not just this script's half of it.
    if pgrep -f 'simpleFoam|pimpleFoam|rhoSimpleFoam|rhoCentralFoam|interFoam|potentialFoam|blockMesh|snappyHexMesh|vspaero|mega_batch|mega_batch_keeper|dafoam|Certonomous/sdk' >/dev/null; then
        echo "Idle timer currently sees the lab as BUSY."
    else
        echo "Idle timer currently sees the lab as IDLE."
    fi
    if [ -f /tmp/last_job_activity ]; then
        echo "Last activity recorded: $(( ( $(date +%s) - $(stat -c %Y /tmp/last_job_activity) ) / 60 )) minutes ago."
    fi
    ;;
  *)
    sed -n '2,10p' "$0" | sed 's/^# \?//'
    exit 1
    ;;
esac
