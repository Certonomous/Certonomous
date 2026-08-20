#!/bin/bash
# Idempotent, collision-safe foreground launcher for ONE D_Ts_* case.
# Guards (all before anything is touched):
#   G1  mkdir <case>/LAUNCH_LOCK atomically -- if it already exists, skip.
#   G2  refuse if any running process has /proc/<pid>/cwd == the case dir.
#   G3  refuse if the case has any numeric time directory other than 0.
# Then detach run_one_dts.sh (checkMesh -> log.checkMesh, solver -> log.solve,
# STATUS.<case> "rc= wall= checkMesh_rc=") via setsid nohup.
# Exit: 0 launched, 1 skipped (lock held), 2 refused (G2/G3), 4 usage.
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"
CDIR="$HERE/$CASE"
LOCK="$CDIR/LAUNCH_LOCK"
[ -n "$CASE" ] && [ -d "$CDIR" ] || { echo "usage: $0 <case>  (case dir must exist)" >&2; exit 4; }
if ! mkdir "$LOCK" 2>/dev/null; then
    echo "SKIP    $CASE: G1 LAUNCH_LOCK already exists ($(tr '\n' ';' < "$LOCK/launch.log" 2>/dev/null))"
    exit 1
fi
echo "launcher pid=$$ lock=$(date -u +%FT%TZ)" >> "$LOCK/launch.log"
for p in /proc/[0-9]*; do
    if [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ]; then
        msg="G2: pid ${p#/proc/} ($(readlink "$p/exe" 2>/dev/null)) already running in case dir"
        echo "REFUSED launcher pid=$$ $(date -u +%FT%TZ): $msg" >> "$LOCK/launch.log"
        echo "REFUSED $CASE: $msg"; exit 2
    fi
done
for t in "$CDIR"/*; do
    b="${t##*/}"
    case "$b" in 0) ;; *[!0-9.]*) ;; *)
        msg="G3: solution time dir $b already exists"
        echo "REFUSED launcher pid=$$ $(date -u +%FT%TZ): $msg" >> "$LOCK/launch.log"
        echo "REFUSED $CASE: $msg"; exit 2;;
    esac
done
cd "$HERE" || exit 4
setsid nohup "$HERE/run_one_dts.sh" "$CASE" > /dev/null 2>&1 &
WP=$!
echo "launcher pid=$$ detached wrapper pid=$WP $(date -u +%FT%TZ)" >> "$LOCK/launch.log"
echo "LAUNCH  $CASE: guards G1 G2 G3 passed; wrapper pid=$WP"
exit 0
