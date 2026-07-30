#!/bin/bash
# Hold the instance up while you are presenting from it.
#
# WHY THIS EXISTS
# ---------------
# A root cron job, /usr/local/bin/auto-stop.sh, powers this instance off after
# 30 minutes with no lab activity. On 2026-07-30 it did exactly that at 10:40
# UTC and killed a running 3D solve.
#
# The part that matters for filming: the control room does NOT count as
# activity on its own. It runs as `python3 -m chief_engineer.server`, and the
# demo acts are in-process replays -- so a person actively filming, typing
# prompts and talking to camera, spawns no process the idle check can see.
# Filming looks identical to an idle box. Thirty minutes in, the box powers
# off mid-shoot.
#
# So: run this before you roll.
#
#   bash scripts/filming_mode.sh on      # default 6 hours
#   bash scripts/filming_mode.sh on 3    # 3 hours
#   bash scripts/filming_mode.sh off     # release early
#   bash scripts/filming_mode.sh status  # what is the current state
#
# The hold ALWAYS carries an expiry. An unbounded "never stop" switch is how a
# forgotten box quietly runs for a month, so the cost of forgetting to turn
# this off is bounded to the hours you asked for and no more.

set -euo pipefail

HOLD=/var/lib/certonomous-filming-hold
DEFAULT_HOURS=6

usage() { sed -n '2,30p' "$0" | sed 's/^# \?//'; exit 1; }

cmd=${1:-status}

case "$cmd" in
  on)
    hours=${2:-$DEFAULT_HOURS}
    if ! [[ "$hours" =~ ^[0-9]+$ ]] || [ "$hours" -lt 1 ] || [ "$hours" -gt 24 ]; then
        echo "hours must be a whole number from 1 to 24 (got: $hours)" >&2; exit 1
    fi
    until_ts=$(( $(date +%s) + hours * 3600 ))
    printf '%s\n# certonomous filming hold, written %s\n' \
        "$until_ts" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" | sudo tee "$HOLD" >/dev/null
    sudo chmod 644 "$HOLD"
    echo "Filming hold ON for ${hours}h."
    echo "The instance will not auto-stop until $(date -u -d "@$until_ts" '+%Y-%m-%d %H:%M:%S UTC')."
    echo "After that the normal 30-minute idle timer comes back on its own."
    ;;
  off)
    sudo rm -f "$HOLD"
    echo "Filming hold OFF. The 30-minute idle timer is armed again."
    ;;
  status)
    if [ -f "$HOLD" ]; then
        until_ts=$(head -n1 "$HOLD" | tr -dc '0-9')
        now=$(date +%s)
        if [ -n "$until_ts" ] && [ "$now" -lt "$until_ts" ]; then
            left=$(( (until_ts - now) / 60 ))
            echo "Filming hold ON, ${left} minutes left "\
"(until $(date -u -d "@$until_ts" '+%H:%M:%S UTC'))."
        else
            echo "A hold file exists but has EXPIRED; the idle timer is active."
        fi
    else
        echo "Filming hold OFF. The instance auto-stops after 30 idle minutes."
    fi
    # Show what the idle timer currently thinks, so status is the whole truth
    # rather than just this script's half of it.
    if [ -f /tmp/last_job_activity ]; then
        idle=$(( ( $(date +%s) - $(stat -c %Y /tmp/last_job_activity) ) / 60 ))
        echo "Last activity seen by the idle timer: ${idle} minutes ago."
    fi
    ;;
  *) usage ;;
esac
