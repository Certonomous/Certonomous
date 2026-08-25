#!/bin/bash
# Detached EXTENSION runner for one T1b fourth-level case (R_*_x), of the
# run_one_ext1.sh form registered in T1b_L4_AMENDMENT.md section 4:
#   checkMesh          -> log.checkMesh.ext1   (log.checkMesh untouched)
#   solver appends     -> log.solve.ext1       (log.solve untouched)
#   STATUS_ext1.<case> beside STATUS.<case>    (STATUS.<case> untouched)
# STATUS_ext1 is the name the FROZEN mark_done_t1b_L4.py reads
# (STATUS_EXT = "STATUS_ext1"); run_one_ext1.sh writes STATUS3, which that
# marker does not read, so this runner carries the registered form under the
# name the marker requires.  No frozen file is edited by this script.
#
# Usage: run_one_t1b_L4_ext1.sh <case> <cap_core_min> <ranks>
# The cap is enforced as the pre-registered identity
#     timeout_seconds = cap_core_min * 60 / ranks
# so a later parallel case cannot inherit a silent factor-of-ranks overrun.
# On cap the solver is killed, rc=124 lands in STATUS_ext1, and the marker
# refuses the case.  An overrun STOPS the run; it does not get a new budget.
#
# no set -e / set -u anywhere: set -e does not gate reliably here and the
# openfoam bashrc reads unset variables.  Every step is gated explicitly.
#
# GUARDS, all applied BEFORE cd into the case so this process never matches
# its own cwd scan:
#   E0  only the three cases the pre-registration names
#   E1  EXT1_LOCK claimed atomically (mkdir), solver.pid claimed noclobber
#   E2  no running process may have /proc/<pid>/cwd == the case dir
#   E3  STATUS.<case> must exist and report rc=0, and log.solve must carry an
#       End line: the original segment must be COMPLETE before it is extended
#   E4  log.solve.ext1 must NOT already exist (never a second append)
# Nothing here ever kills another process.
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"; CAP="$2"; RANKS="$3"
CDIR="$HERE/$CASE"
LOCK="$CDIR/EXT1_LOCK"
refuse() { echo "REFUSED $CASE pid=$$ $(date -u +%FT%TZ): $*" >&2; [ -d "$LOCK" ] && echo "REFUSED pid=$$ $(date -u +%FT%TZ): $*" >> "$LOCK/launch.log"; exit 3; }
case "$CASE" in
    R_10k_x|R_100k_x|R_300k_x) ;;
    *) refuse "E0: not a case this pre-registration extends";;
esac
[ -n "$CAP" ] && [ -n "$RANKS" ] || refuse "E0: cap_core_min and ranks are required"
TIMEOUT=$(( CAP * 60 / RANKS ))
[ -d "$CDIR" ] || refuse "E0: no such case dir"
[ -d "$LOCK" ] || refuse "E1: no EXT1_LOCK (not launched via launch_t1b_L4_ext1.sh)"
( set -o noclobber; echo "$$" > "$LOCK/solver.pid" ) 2>/dev/null || refuse "E1: solver.pid already claimed by pid $(cat "$LOCK/solver.pid" 2>/dev/null)"
for p in /proc/[0-9]*; do
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ] && refuse "E2: pid ${p#/proc/} ($(readlink "$p/exe" 2>/dev/null)) already running in case dir"
done
grep -q '^rc=0 ' "$HERE/STATUS.$CASE" 2>/dev/null || refuse "E3: STATUS.$CASE is not rc=0 (original segment not complete)"
grep -q '^End$' "$CDIR/log.solve" || refuse "E3: log.solve has no End line"
[ -e "$CDIR/log.solve.ext1" ] && refuse "E4: log.solve.ext1 already exists; never appending twice"
echo "wrapper pid=$$ start=$(date -u +%FT%TZ) cap_core_min=$CAP ranks=$RANKS timeout_s=$TIMEOUT" >> "$LOCK/launch.log"
source /usr/lib/openfoam/openfoam2606/etc/bashrc
cd "$CDIR" || { echo "rc=127 wall=0 checkMesh_rc=127" > "$HERE/STATUS_ext1.$CASE"; exit 127; }
checkMesh > log.checkMesh.ext1 2>&1
CMRC=$?
T0=$(date +%s)
timeout "$TIMEOUT" buoyantBoussinesqSimpleFoam >> log.solve.ext1 2>&1
RC=$?
T1=$(date +%s)
echo "rc=$RC wall=$((T1-T0)) checkMesh_rc=$CMRC" > "$HERE/STATUS_ext1.$CASE"
echo "wrapper pid=$$ end=$(date -u +%FT%TZ) rc=$RC wall=$((T1-T0)) checkMesh_rc=$CMRC timeout_s=$TIMEOUT" >> "$LOCK/launch.log"
