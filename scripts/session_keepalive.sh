#!/bin/bash
# Keep the instance awake while a Claude supervision SESSION is active --
# even when no solver is running (diagnosis, agent report reading, commits).
#
#   bash scripts/session_keepalive.sh on       # arm for this session
#   bash scripts/session_keepalive.sh off
#   bash scripts/session_keepalive.sh status
#
# WHY THIS EXISTS, AND WHY filming_keepalive.sh IS NOT ENOUGH
# -----------------------------------------------------------
# The root cron auto-stop.sh decides "busy" with one pgrep:
#   simpleFoam|...|dafoam|Certonomous/sdk
# A supervision session doing pure diagnosis matches NONE of those, so 30
# minutes of reading agent reports powers the box off. This happened three
# times before 2026-08-05 (Katie's report; also the 2026-07-30 mid-campaign
# stop in the lab record).
#
# filming_keepalive.sh holds for a FIXED window you must remember to set.
# This script instead ties the hold to observable session activity: the
# holder process (whose command line carries the literal "Certonomous/sdk",
# which auto-stop.sh greps for) stays alive only while the Claude session
# directories show fresh writes, and exits on its own when either
#   - no session write for STALE_MINUTES, or
#   - HARD_CAP_HOURS elapsed (a forgotten box stays bounded).
# When a solver IS running, auto-stop counts it busy anyway; this only covers
# the gaps between runs.

set -uo pipefail

SESSION_DIRS=(
    /home/ubuntu/.claude/projects/-home-ubuntu-Certonomous
    /tmp/claude-1000/-home-ubuntu-Certonomous
)
STALE_MINUTES=45
HARD_CAP_HOURS=24
PIDFILE=/tmp/certonomous-session-keepalive.pid

running_pid() {
    [ -f "$PIDFILE" ] || return 1
    local pid
    pid=$(tr -dc '0-9' < "$PIDFILE")
    [ -n "$pid" ] || return 1
    kill -0 "$pid" 2>/dev/null || return 1
    echo "$pid"
}

newest_write_age_min() {
    # Minutes since the newest file write under any session dir; 99999 if none.
    local newest=0 t d
    for d in "${SESSION_DIRS[@]}"; do
        [ -d "$d" ] || continue
        t=$(find "$d" -type f -printf '%T@\n' 2>/dev/null | sort -rn | head -n1 | cut -d. -f1)
        [ -n "${t:-}" ] && [ "$t" -gt "$newest" ] && newest=$t
    done
    if [ "$newest" -eq 0 ]; then echo 99999; else echo $(( ( $(date +%s) - newest ) / 60 )); fi
}

case "${1:-status}" in
  on)
    if pid=$(running_pid); then
        echo "Session keep-alive already running (pid $pid)."
        exit 0
    fi
    cap_end=$(( $(date +%s) + HARD_CAP_HOURS * 3600 ))
    TOKEN="certonomous-session-keepalive-$$"
    # The literal "Certonomous/sdk" below is what auto-stop.sh greps for.
    setsid nohup bash -c "
        # Certonomous/sdk session keepalive $TOKEN (holds while the Claude session writes)
        while [ \"\$(date +%s)\" -lt $cap_end ]; do
            newest=0
            for d in ${SESSION_DIRS[*]}; do
                [ -d \"\$d\" ] || continue
                t=\$(find \"\$d\" -type f -printf '%T@\n' 2>/dev/null | sort -rn | head -n1 | cut -d. -f1)
                [ -n \"\$t\" ] && [ \"\$t\" -gt \"\$newest\" ] && newest=\$t
            done
            [ \"\$newest\" -eq 0 ] && exit 0
            age=\$(( ( \$(date +%s) - newest ) / 60 ))
            [ \"\$age\" -ge $STALE_MINUTES ] && exit 0
            sleep 120
        done
    " >/dev/null 2>&1 < /dev/null &
    disown 2>/dev/null || true
    pid=""
    for _ in 1 2 3 4 5 6 7 8 9 10; do
        pid=$(pgrep -f "$TOKEN" | head -n1)
        [ -n "$pid" ] && break
        sleep 0.3
    done
    if [ -z "$pid" ]; then
        echo "Session keep-alive FAILED to start." >&2; exit 1
    fi
    echo "$pid" > "$PIDFILE"
    echo "Session keep-alive ON (pid $pid): holds while the session writes,"
    echo "self-expires after ${STALE_MINUTES}min of session silence or ${HARD_CAP_HOURS}h hard cap."
    ;;
  off)
    if pid=$(running_pid); then
        kill -- "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null
        echo "Session keep-alive OFF (stopped pid $pid)."
    else
        echo "Session keep-alive was not running."
    fi
    rm -f "$PIDFILE"
    ;;
  status)
    if pid=$(running_pid); then
        echo "Session keep-alive ON (pid $pid). Newest session write: $(newest_write_age_min) min ago."
    else
        echo "Session keep-alive OFF."
    fi
    if pgrep -f 'simpleFoam|pimpleFoam|rhoSimpleFoam|rhoCentralFoam|interFoam|potentialFoam|blockMesh|snappyHexMesh|vspaero|mega_batch|mega_batch_keeper|dafoam|Certonomous/sdk' >/dev/null; then
        echo "Idle timer currently sees the lab as BUSY."
    else
        echo "Idle timer currently sees the lab as IDLE."
    fi
    ;;
  *)
    sed -n '2,8p' "$0" | sed 's/^# \?//'
    exit 1
    ;;
esac
