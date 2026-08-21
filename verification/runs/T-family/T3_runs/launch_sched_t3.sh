#!/bin/bash
# Box-aware scheduler for the T3 pool.  Launches the given cases one at a
# time through launch_t3.sh, never exceeding MYCAP of this rung's own solver
# processes (readlink /proc/pid/exe ends in buoyantBoussinesqSimpleFoam and
# cwd under this tree) and never launching while the box has fewer than
# MINIDLE idle cores (nproc minus the 1-minute load average, rounded down).
# The box is shared with two other teams.  Polls every 120 s.  Exits when
# every case has been handed to launch_t3.sh (rc 0 launched, 1 already
# locked, 2 refused -- all three are terminal for that case).  Kills nothing.
# Usage: launch_sched_t3.sh MYCAP MINIDLE case [case ...]
HERE="$(cd "$(dirname "$0")" && pwd)"
MYCAP="$1"; MINIDLE="$2"; shift 2
LOG="$HERE/log.sched"
mine() { n=0; for p in /proc/[0-9]*; do e=$(readlink "$p/exe" 2>/dev/null); case "$e" in */buoyantBoussinesqSimpleFoam|*/checkMesh) c=$(readlink "$p/cwd" 2>/dev/null); case "$c" in "$HERE"/*) n=$((n+1));; esac;; esac; done; echo $n; }
idle() { awk -v n="$(nproc)" '{i=n-$1; if(i<0)i=0; printf "%d\n", i}' /proc/loadavg; }
for CASE in "$@"; do
    while :; do
        m=$(mine); i=$(idle)
        if [ "$m" -lt "$MYCAP" ] && [ "$i" -ge "$MINIDLE" ]; then break; fi
        echo "$(date -u +%FT%TZ) WAIT $CASE mine=$m cap=$MYCAP idle=$i minidle=$MINIDLE" >> "$LOG"
        sleep 120
    done
    "$HERE/launch_t3.sh" "$CASE" >> "$LOG" 2>&1; rc=$?
    echo "$(date -u +%FT%TZ) HANDED $CASE rc=$rc mine_before=$m idle_before=$i" >> "$LOG"
    sleep 90
done
echo "$(date -u +%FT%TZ) SCHED_DONE all cases handed to launch_t3.sh" >> "$LOG"
