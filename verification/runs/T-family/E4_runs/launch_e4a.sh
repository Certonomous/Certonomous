#!/bin/bash
# Idempotent, collision-safe foreground launcher for ONE E4a case.
# Guards G1 (atomic mkdir lock), G2 (cwd scan), G3 (no stray numeric time
# dir), exactly as T10aR_runs/launch_t10aR.sh.  Touches no process it did not
# start.  RUNS NOTHING until the supervisor has committed the freeze and
# authorised launch.
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"; CDIR="$HERE/$CASE"; LOCK="$CDIR/LAUNCH_LOCK"
[ -n "$CASE" ] && [ -d "$CDIR" ] || { echo "usage: $0 <case>" >&2; exit 4; }
if ! mkdir "$LOCK" 2>/dev/null; then
    echo "SKIP    $CASE: G1 LAUNCH_LOCK already exists ($(tr '\n' ';' < "$LOCK/launch.log" 2>/dev/null))"; exit 1
fi
echo "launcher pid=$$ lock=$(date -u +%FT%TZ)" >> "$LOCK/launch.log"
for p in /proc/[0-9]*; do
    if [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ]; then
        msg="G2: pid ${p#/proc/} already running in case dir"
        echo "REFUSED launcher pid=$$ $(date -u +%FT%TZ): $msg" >> "$LOCK/launch.log"; echo "REFUSED $CASE: $msg"; exit 2
    fi
done
for t in "$CDIR"/*; do
    b="${t##*/}"
    case "$b" in 0) ;; *[!0-9.]*) ;; *)
        msg="G3: solution time dir $b already exists"
        echo "REFUSED launcher pid=$$ $(date -u +%FT%TZ): $msg" >> "$LOCK/launch.log"; echo "REFUSED $CASE: $msg"; exit 2;;
    esac
done
cd "$HERE" || exit 4
setsid nohup "$HERE/run_one_e4a.sh" "$CASE" > /dev/null 2>&1 &
WP=$!
echo "launcher pid=$$ detached wrapper pid=$WP $(date -u +%FT%TZ)" >> "$LOCK/launch.log"
echo "LAUNCH  $CASE: guards G1 G2 G3 passed; wrapper pid=$WP"
