#!/bin/bash
# Detached runner for ONE T10a-R case.  Identical guard set to
# T10a_runs/run_one_t10a.sh (G1 lock claim, G2 cwd scan, G3 no stray time dir,
# plus constant/F must already exist from the preprocessing step).  nice 15:
# this lane shares a 16-core box with T1b L4, T3 ext1 and a T9a-D lane and
# must never displace them.
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"; CDIR="$HERE/$CASE"; LOCK="$CDIR/LAUNCH_LOCK"
refuse() { echo "REFUSED $CASE pid=$$ $(date -u +%FT%TZ): $*" >&2; [ -d "$LOCK" ] && echo "REFUSED pid=$$ $(date -u +%FT%TZ): $*" >> "$LOCK/launch.log"; exit 3; }
[ -d "$CDIR" ] || refuse "no such case dir"
[ -d "$LOCK" ] || refuse "G1: no LAUNCH_LOCK (not launched via launch_t10aR.sh)"
( set -o noclobber; echo "$$" > "$LOCK/solver.pid" ) 2>/dev/null || refuse "G1: LAUNCH_LOCK/solver.pid already claimed by pid $(cat "$LOCK/solver.pid" 2>/dev/null)"
for p in /proc/[0-9]*; do
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ] && refuse "G2: pid ${p#/proc/} ($(readlink "$p/exe" 2>/dev/null)) already running in case dir"
done
for t in "$CDIR"/*; do
    b="${t##*/}"
    case "$b" in 0) ;; *[!0-9.]*) ;; *) refuse "G3: solution time dir $b already exists";; esac
done
[ -f "$CDIR/constant/F" ] || refuse "no constant/F (preprocess_t10aR.sh did not run)"
echo "wrapper pid=$$ start=$(date -u +%FT%TZ)" >> "$LOCK/launch.log"
source /usr/lib/openfoam/openfoam2606/etc/bashrc
cd "$CDIR" || { echo "rc=127 wall=0 checkMesh_rc=127" > "$HERE/STATUS.$CASE"; exit 127; }
rm -rf 0 && cp -r 0.orig 0
nice -n 15 checkMesh > log.checkMesh 2>&1
CMRC=$?
T0=$(date +%s)
/usr/bin/time -v nice -n 15 buoyantSimpleFoam > log.solve 2>log.solve.time
RC=$?
T1=$(date +%s)
RSS=$(awk '/Maximum resident/{print $NF}' log.solve.time)
echo "rc=$RC wall=$((T1-T0)) checkMesh_rc=$CMRC maxRSS_kB=$RSS case=$CASE end=$(date -u +%FT%TZ) pid=$$" > "$HERE/STATUS.$CASE"
echo "wrapper pid=$$ end=$(date -u +%FT%TZ) rc=$RC wall=$((T1-T0)) checkMesh_rc=$CMRC maxRSS_kB=$RSS" >> "$LOCK/launch.log"
