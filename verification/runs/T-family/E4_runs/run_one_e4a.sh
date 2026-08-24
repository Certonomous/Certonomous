#!/bin/bash
# Detached runner for ONE E4a case.  Identical guard set to
# T10aR_runs/run_one_t10aR.sh (G1 lock claim, G2 cwd scan, G3 no stray time
# dir), adapted: this rung has no preprocessing step, so blockMesh runs here,
# after the guards and before 0/ is laid down.  nice 15: this lane shares the
# 16-core box and must never displace spine compute.
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"; CDIR="$HERE/$CASE"; LOCK="$CDIR/LAUNCH_LOCK"
refuse() { echo "REFUSED $CASE pid=$$ $(date -u +%FT%TZ): $*" >&2; [ -d "$LOCK" ] && echo "REFUSED pid=$$ $(date -u +%FT%TZ): $*" >> "$LOCK/launch.log"; exit 3; }
[ -d "$CDIR" ] || refuse "no such case dir"
[ -d "$LOCK" ] || refuse "G1: no LAUNCH_LOCK (not launched via launch_e4a.sh)"
( set -o noclobber; echo "$$" > "$LOCK/solver.pid" ) 2>/dev/null || refuse "G1: LAUNCH_LOCK/solver.pid already claimed by pid $(cat "$LOCK/solver.pid" 2>/dev/null)"
for p in /proc/[0-9]*; do
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ] && refuse "G2: pid ${p#/proc/} ($(readlink "$p/exe" 2>/dev/null)) already running in case dir"
done
for t in "$CDIR"/*; do
    b="${t##*/}"
    case "$b" in 0) ;; *[!0-9.]*) ;; *) refuse "G3: solution time dir $b already exists";; esac
done
[ -f "$CDIR/system/blockMeshDict" ] || refuse "no system/blockMeshDict (build_e4a.py did not run)"
[ -d "$CDIR/0.orig" ] || refuse "no 0.orig (build_e4a.py did not run)"
echo "wrapper pid=$$ start=$(date -u +%FT%TZ)" >> "$LOCK/launch.log"
source /usr/lib/openfoam/openfoam2606/etc/bashrc
cd "$CDIR" || { echo "rc=127 wall=0 blockMesh_rc=127 checkMesh_rc=127" > "$HERE/STATUS.$CASE"; exit 127; }
nice -n 15 blockMesh > log.blockMesh 2>&1
BMRC=$?
if [ $BMRC -ne 0 ]; then
    echo "rc=$BMRC wall=0 blockMesh_rc=$BMRC checkMesh_rc=-1 case=$CASE end=$(date -u +%FT%TZ) pid=$$" > "$HERE/STATUS.$CASE"
    echo "wrapper pid=$$ end=$(date -u +%FT%TZ) blockMesh FAILED rc=$BMRC" >> "$LOCK/launch.log"
    exit $BMRC
fi
rm -rf 0 && cp -r 0.orig 0
nice -n 15 checkMesh > log.checkMesh 2>&1
CMRC=$?
T0=$(date +%s)
/usr/bin/time -v nice -n 15 simpleFoam > log.solve 2>log.solve.time
RC=$?
T1=$(date +%s)
RSS=$(awk '/Maximum resident/{print $NF}' log.solve.time)
echo "rc=$RC wall=$((T1-T0)) blockMesh_rc=$BMRC checkMesh_rc=$CMRC maxRSS_kB=$RSS case=$CASE end=$(date -u +%FT%TZ) pid=$$" > "$HERE/STATUS.$CASE"
echo "wrapper pid=$$ end=$(date -u +%FT%TZ) rc=$RC wall=$((T1-T0)) blockMesh_rc=$BMRC checkMesh_rc=$CMRC maxRSS_kB=$RSS" >> "$LOCK/launch.log"
