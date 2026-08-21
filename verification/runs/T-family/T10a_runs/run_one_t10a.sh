#!/bin/bash
# Detached runner for one T10a case: re-copy 0/ from 0.orig (so 0/T is dated
# by THIS run -- mark_done test 6, L-143), checkMesh, buoyantSimpleFoam, then
# STATUS.<case> in the T1b pool format (rc= wall= checkMesh_rc=).
# no `set -u`: the openfoam2606 bashrc reads unset variables and aborts under nounset
#
# COLLISION GUARDS (defence in depth; launch_t10a.sh applies the same guards
# in the foreground before detaching this script).  Every guard is checked
# BEFORE cd into the case, so this process never matches its own cwd scan:
#   G1  <case>/LAUNCH_LOCK must exist (created atomically by launch_t10a.sh)
#       and this process must be the FIRST to claim LAUNCH_LOCK/solver.pid
#       (noclobber create = atomic).  A direct, un-launched invocation refuses.
#   G2  no running process may have /proc/<pid>/cwd == the case dir.
#   G3  the case may hold no numeric time directory other than 0.
# Plus: refuse if constant/F is missing (viewFactorsGen is a BUILD step; a
# run may not silently regenerate the registered view factors).
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"
CDIR="$HERE/$CASE"
LOCK="$CDIR/LAUNCH_LOCK"
refuse() { echo "REFUSED $CASE pid=$$ $(date -u +%FT%TZ): $*" >&2; [ -d "$LOCK" ] && echo "REFUSED pid=$$ $(date -u +%FT%TZ): $*" >> "$LOCK/launch.log"; exit 3; }
[ -d "$CDIR" ] || refuse "no such case dir"
[ -d "$LOCK" ] || refuse "G1: no LAUNCH_LOCK (not launched via launch_t10a.sh)"
( set -o noclobber; echo "$$" > "$LOCK/solver.pid" ) 2>/dev/null || refuse "G1: LAUNCH_LOCK/solver.pid already claimed by pid $(cat "$LOCK/solver.pid" 2>/dev/null)"
for p in /proc/[0-9]*; do
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ] && refuse "G2: pid ${p#/proc/} ($(readlink "$p/exe" 2>/dev/null)) already running in case dir"
done
for t in "$CDIR"/*; do
    b="${t##*/}"
    case "$b" in 0) ;; *[!0-9.]*) ;; *) refuse "G3: solution time dir $b already exists";; esac
done
[ -f "$CDIR/constant/F" ] || refuse "no constant/F (viewFactorsGen did not run at build)"
echo "wrapper pid=$$ start=$(date -u +%FT%TZ)" >> "$LOCK/launch.log"
source /usr/lib/openfoam/openfoam2606/etc/bashrc
cd "$CDIR" || { echo "rc=127 wall=0 checkMesh_rc=127" > "$HERE/STATUS.$CASE"; exit 127; }
rm -rf 0 && cp -r 0.orig 0
checkMesh > log.checkMesh 2>&1
CMRC=$?
T0=$(date +%s)
buoyantSimpleFoam > log.solve 2>&1
RC=$?
T1=$(date +%s)
echo "rc=$RC wall=$((T1-T0)) checkMesh_rc=$CMRC case=$CASE end=$(date -u +%FT%TZ) pid=$$" > "$HERE/STATUS.$CASE"
echo "wrapper pid=$$ end=$(date -u +%FT%TZ) rc=$RC wall=$((T1-T0)) checkMesh_rc=$CMRC" >> "$LOCK/launch.log"
