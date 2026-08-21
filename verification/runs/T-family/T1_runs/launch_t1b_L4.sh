#!/bin/bash
# Idempotent, collision-safe foreground launcher for ONE T1b fourth-level case
# (R_10k_x, R_30k_x, R_100k_x, R_300k_x).  Same guard structure as
# launch_dts.sh / launch_t3.sh.  Guards (all before anything is touched):
#   G1  mkdir <case>/LAUNCH_LOCK atomically -- if it already exists, skip.
#   G2  refuse if any running process has /proc/<pid>/cwd == the case dir
#       (identified by readlink /proc/<pid>/exe in the message).
#   G3  refuse if the case has any numeric time directory other than 0.
#       The pattern test does NOT match 0.orig (L-143: a [0-9]* glob did).
# Then detach run_one_t1b_L4.sh (0.orig -> 0 with 0/T touched last, checkMesh
# -> log.checkMesh, solver -> log.solve, STATUS.<case> "rc= wall=
# checkMesh_rc=") via setsid nohup.  Nothing here ever kills a process.
# Exit: 0 launched, 1 skipped (lock held), 2 refused (G2/G3), 4 usage.
#
# Only the four x cases are accepted: this launcher can never touch one of the
# nineteen frozen attempt-2 cases.
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"
CDIR="$HERE/$CASE"
LOCK="$CDIR/LAUNCH_LOCK"
case "$CASE" in
    R_10k_x|R_30k_x|R_100k_x|R_300k_x) ;;
    *) echo "usage: $0 <R_10k_x|R_30k_x|R_100k_x|R_300k_x>" >&2; exit 4;;
esac
[ -d "$CDIR" ] || { echo "usage: $0 <case>  (case dir must exist)" >&2; exit 4; }
[ -d "$CDIR/0.orig" ] || { echo "REFUSED $CASE: no 0.orig (not built)" >&2; exit 4; }
[ -f "$CDIR/constant/polyMesh/points" ] || { echo "REFUSED $CASE: no polyMesh (run check_t1b_L4_mesh.py first)" >&2; exit 4; }
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
setsid nohup "$HERE/run_one_t1b_L4.sh" "$CASE" > /dev/null 2>&1 &
WP=$!
echo "launcher pid=$$ detached wrapper pid=$WP $(date -u +%FT%TZ)" >> "$LOCK/launch.log"
echo "LAUNCH  $CASE: guards G1 G2 G3 passed; wrapper pid=$WP"
exit 0
