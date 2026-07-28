#!/usr/bin/env bash
# Mega-batch keeper.
#
# The batch stops itself cleanly when free memory falls below its guard floor --
# that guard is correct and saved the host twice tonight. But "stopped cleanly"
# still means "not accumulating", and D1 requires the batch to run all night.
# Concurrent DAFoam adjoints (two 4-rank check_totals runs peaked around 21 GB
# resident on 2026-07-28) starve it for tens of minutes at a time.
#
# This keeper restarts the batch once memory has genuinely recovered, and does
# nothing otherwise. It is deliberately conservative:
#   - restarts only when MemAvailable is comfortably above the batch's own floor,
#     so it cannot flap the batch against its guard
#   - relies on acquire_runner_lock() to refuse a second instance, so a race
#     with a manual launch cannot produce the concurrent-writer duplication that
#     corrupted 55 ledger rows on 2026-07-27
#   - never edits the ledger, never passes --force
set -u

REPO=/home/ubuntu/Certonomous
BATCH="$REPO/sdk/workflows/mega_batch.py"
LOG="$REPO/demo-output/website/mega-batch/runner.log"
ERR="$REPO/demo-output/website/mega-batch/runner.err.log"
KEEPLOG="$REPO/demo-output/website/mega-batch/keeper.log"

WORKERS="${WORKERS:-2}"        # 2, not 3: leaves headroom for concurrent adjoints
RESTART_MEM_GB="${RESTART_MEM_GB:-8}"   # well above the batch's own 2 GB floor
INTERVAL="${INTERVAL:-120}"

avail_gb() { awk '/MemAvailable/ {printf "%.1f", $2/1048576}' /proc/meminfo; }

# Match on the script name, then confirm the process really is a python3 rather
# than a shell whose command line merely contains the name. A bare `pgrep -f`
# happily matches the very command asking the question, which produced two false
# "still running" readings tonight (see LESSONS.md L-6).
running() {
    local p
    for p in $(pgrep -f "mega_batch\.py" 2>/dev/null); do
        [ "$(cat "/proc/$p/comm" 2>/dev/null)" = "python3" ] && return 0
    done
    return 1
}

echo "[keeper] started $(date -u +%FT%TZ) workers=$WORKERS restart_floor=${RESTART_MEM_GB}GB" >> "$KEEPLOG"

while true; do
    if ! running; then
        mem=$(avail_gb)
        if awk -v m="$mem" -v f="$RESTART_MEM_GB" 'BEGIN{exit !(m+0 >= f+0)}'; then
            echo "[keeper] $(date -u +%FT%TZ) batch down, MemAvailable ${mem}GB >= ${RESTART_MEM_GB}GB, restarting" >> "$KEEPLOG"
            cd "$REPO/sdk" || exit 1
            setsid nohup python3 "$BATCH" --workers "$WORKERS" \
                --min-free-disk-gb 20 --min-avail-mem-gb 2 \
                >> "$LOG" 2>> "$ERR" < /dev/null &
            disown
        else
            echo "[keeper] $(date -u +%FT%TZ) batch down but MemAvailable ${mem}GB < ${RESTART_MEM_GB}GB, holding" >> "$KEEPLOG"
        fi
    fi
    sleep "$INTERVAL"
done
