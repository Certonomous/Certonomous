#!/bin/bash
# Detached runner for one T1b fourth-level case (R_*_x): 0.orig -> 0,
# checkMesh, solve, then write STATUS.<case> beside the case directory in the
# T1b pool format (rc= wall= checkMesh_rc=).  checkMesh already ran at build
# time (check_t1b_L4_mesh.py); it is re-run here so checkMesh_rc in STATUS is
# measured by the run that produced the solution, not inherited from the build.
# no set -u: the openfoam2606 bashrc reads unset variables and aborts under nounset
#
# COLLISION GUARDS (defence in depth; launch_t1b_L4.sh applies the same guards
# in the foreground before detaching this script).  Every guard is checked
# BEFORE cd into the case, so this process never matches its own cwd scan:
#   G1  <case>/LAUNCH_LOCK must exist (created atomically by launch_t1b_L4.sh)
#       and this process must be the FIRST to claim LAUNCH_LOCK/solver.pid
#       (noclobber create = atomic).  A direct, un-launched invocation refuses.
#   G2  no running process may have /proc/<pid>/cwd == the case dir.
#   G3  the case may hold no numeric time directory other than 0, and 0 itself
#       must NOT yet exist: this runner creates 0 from 0.orig and touches 0/T
#       LAST so its mtime dates the run that is allowed to produce the answer
#       (mark_done_t1b_L4.py test 6, D438, L-143).  A pre-existing 0 means
#       some earlier run started; it is never overwritten or merged into.
# Nothing here ever kills a process.  nProcs = 1, as on every T1b case.
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"
CDIR="$HERE/$CASE"
LOCK="$CDIR/LAUNCH_LOCK"
refuse() { echo "REFUSED $CASE pid=$$ $(date -u +%FT%TZ): $*" >&2; [ -d "$LOCK" ] && echo "REFUSED pid=$$ $(date -u +%FT%TZ): $*" >> "$LOCK/launch.log"; exit 3; }
case "$CASE" in
    R_10k_x|R_30k_x|R_100k_x|R_300k_x) ;;
    *) refuse "not an x-level case";;
esac
[ -d "$CDIR" ] || refuse "no such case dir"
[ -d "$CDIR/0.orig" ] || refuse "no 0.orig (not built)"
[ -d "$LOCK" ] || refuse "G1: no LAUNCH_LOCK (not launched via launch_t1b_L4.sh)"
( set -o noclobber; echo "$$" > "$LOCK/solver.pid" ) 2>/dev/null || refuse "G1: LAUNCH_LOCK/solver.pid already claimed by pid $(cat "$LOCK/solver.pid" 2>/dev/null)"
for p in /proc/[0-9]*; do
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ] && refuse "G2: pid ${p#/proc/} ($(readlink "$p/exe" 2>/dev/null)) already running in case dir"
done
for t in "$CDIR"/*; do
    b="${t##*/}"
    case "$b" in 0) refuse "G3: 0/ already exists (an earlier run started); not overwriting";; *[!0-9.]*) ;; *) refuse "G3: solution time dir $b already exists";; esac
done
echo "wrapper pid=$$ start=$(date -u +%FT%TZ)" >> "$LOCK/launch.log"
source /usr/lib/openfoam/openfoam2606/etc/bashrc
cd "$CDIR" || { echo "rc=127 wall=0 checkMesh_rc=127" > "$HERE/STATUS.$CASE"; exit 127; }
cp -r 0.orig 0 || { echo "rc=126 wall=0 checkMesh_rc=126" > "$HERE/STATUS.$CASE"; refuse "cp 0.orig 0 failed"; }
touch 0/T            # LAST: its mtime dates the start of this run
checkMesh > log.checkMesh 2>&1
CMRC=$?
T0=$(date +%s)
buoyantBoussinesqSimpleFoam > log.solve 2>&1
RC=$?
T1=$(date +%s)
echo "rc=$RC wall=$((T1-T0)) checkMesh_rc=$CMRC" > "$HERE/STATUS.$CASE"
echo "wrapper pid=$$ end=$(date -u +%FT%TZ) rc=$RC wall=$((T1-T0)) checkMesh_rc=$CMRC" >> "$LOCK/launch.log"
