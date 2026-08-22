#!/bin/bash
# Idempotent, collision-safe foreground launcher for ONE T3 ext1 extension.
# Same G1/G2/G3 shape as launch_t3.sh, with G3 adapted for a continuation:
#   G1  mkdir <case>/LAUNCH_LOCK_EXT1 atomically -- if it already exists, skip.
#       (The ORIGINAL <case>/LAUNCH_LOCK is left strictly alone: it is the
#       record of the first segment and run_one_t3.sh's noclobber solver.pid
#       claim still sits inside it.)
#   G2  refuse if any running process has /proc/<pid>/cwd == the case dir.
#   G3  ADAPTED: the original segment's final time dir 20000/ MUST exist
#       (there must be something to resume from) and log.solve.ext1 must NOT
#       exist (no extension may already have run).  This is the mirror image
#       of launch_t3.sh's G3, which refused when a solution time dir existed.
# Then detach run_one_t3_ext1.sh via setsid nohup.  Nothing here ever kills a
# process, and nothing here ever touches 0/ or log.solve.
# usage: launch_t3_ext1.sh <case> <new_endTime>
# Exit: 0 launched, 1 skipped (lock held), 2 refused (G2/G3), 4 usage.
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"
NEWEND="$2"
CDIR="$HERE/$CASE"
LOCK="$CDIR/LAUNCH_LOCK_EXT1"
LOG="$HERE/LAUNCH_EXT1.log"

[ -n "$CASE" ] && [ -n "$NEWEND" ] && [ -d "$CDIR" ] || { echo "usage: $0 <case> <new_endTime>  (case dir must exist)" >&2; exit 4; }
case "$NEWEND" in ''|*[!0-9]*) echo "REFUSED $CASE: new_endTime '$NEWEND' is not an integer" >&2; exit 4;; esac
[ -f "$CDIR/log.solve" ] || { echo "REFUSED $CASE: no log.solve (no original segment)" >&2; exit 4; }
[ -f "$HERE/STATUS.$CASE" ] || { echo "REFUSED $CASE: no STATUS.$CASE (original segment never finished)" >&2; exit 4; }

if ! mkdir "$LOCK" 2>/dev/null; then
    echo "SKIP    $CASE: G1 LAUNCH_LOCK_EXT1 already exists ($(tr '\n' ';' < "$LOCK/launch.log" 2>/dev/null))"
    exit 1
fi
echo "launcher pid=$$ lock=$(date -u +%FT%TZ) endTime=$NEWEND" >> "$LOCK/launch.log"

for p in /proc/[0-9]*; do
    if [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ]; then
        msg="G2: pid ${p#/proc/} ($(readlink "$p/exe" 2>/dev/null)) already running in case dir"
        echo "REFUSED launcher pid=$$ $(date -u +%FT%TZ): $msg" >> "$LOCK/launch.log"
        echo "REFUSED $CASE: $msg"; exit 2
    fi
done

if [ ! -d "$CDIR/20000" ]; then
    msg="G3: no 20000/ time dir -- nothing to resume from"
    echo "REFUSED launcher pid=$$ $(date -u +%FT%TZ): $msg" >> "$LOCK/launch.log"
    echo "REFUSED $CASE: $msg"; exit 2
fi
if [ -e "$CDIR/log.solve.ext1" ]; then
    msg="G3: log.solve.ext1 already exists -- an extension has already run"
    echo "REFUSED launcher pid=$$ $(date -u +%FT%TZ): $msg" >> "$LOCK/launch.log"
    echo "REFUSED $CASE: $msg"; exit 2
fi

cd "$HERE" || exit 4
setsid nohup "$HERE/run_one_t3_ext1.sh" "$CASE" "$NEWEND" >> "$HERE/wrapper_ext1.$CASE.out" 2>&1 &
WP=$!
TS=$(date -u +%FT%TZ)
echo "launcher pid=$$ detached wrapper pid=$WP $TS endTime=$NEWEND" >> "$LOCK/launch.log"
echo "LAUNCH $CASE endTime=$NEWEND wrapper_pid=$WP at=$TS" >> "$LOG"
echo "LAUNCH  $CASE: guards G1 G2 G3 passed; endTime=$NEWEND wrapper pid=$WP"
exit 0
