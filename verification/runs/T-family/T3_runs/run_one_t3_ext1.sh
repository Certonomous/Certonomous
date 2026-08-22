#!/bin/bash
# Detached EXTENSION runner for one T3 case -- a disclosed continuation of a
# NOT-A-RESULT ladder (T3_PREREGISTRATION sec.5 "extension from latestTime",
# T1b_RESULTS sec.6 disclosure rule; pattern of T1_runs/run_one_ext1.sh).
#
# It resumes the solve from latestTime to a RAISED endTime, appending to a NEW
# log (log.solve.ext1 -- log.solve is NEVER touched) and writing
# STATUS_EXT1.<case> beside the case directory in the T1b pool format.
#
# 0/ IS NEVER TOUCHED.  run_one_t3.sh touched 0/T last so its mtime dates the
# start of the ORIGINAL segment; mark_done_t3_ext1.py test 6 dates the
# extension's fields against 0/T *and* against STATUS.<case>.  Rewriting or
# re-touching 0/ would destroy both guards.  There is no cp, touch, rm or any
# other write to 0/ anywhere below.
#
# controlDict discipline: system/controlDict is edited by a COPY-EDIT
# (sed > tmp, mv), and EVERY sed is followed by a grep POST-CHECK.  If the
# post-check does not see the intended line the script REFUSES with exit 2
# and the solver is never started.  This is the T1b lesson made explicit: a
# silently-unapplied sed would have restarted the case from 0 or stopped it
# at 20000, and either would have been discovered only after hours of wall.
#
# usage: run_one_t3_ext1.sh <case> <new_endTime>
# exit:  0 ok (solver ran; see STATUS_EXT1.<case> for its rc)
#        2 REFUSED -- a controlDict edit did not take, or a precondition failed
#        3 REFUSED -- collision guard
#      127 case dir unusable
# no `set -u`: the openfoam2606 bashrc reads unset variables and aborts under nounset

HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"
NEWEND="$2"
CDIR="$HERE/$CASE"
CD="$CDIR/system/controlDict"

refuse2() { echo "REFUSED $CASE pid=$$ $(date -u +%FT%TZ): $*" >&2; exit 2; }
refuse3() { echo "REFUSED $CASE pid=$$ $(date -u +%FT%TZ): $*" >&2; exit 3; }

[ -n "$CASE" ] && [ -n "$NEWEND" ] || { echo "usage: $0 <case> <new_endTime>" >&2; exit 4; }
case "$NEWEND" in ''|*[!0-9]*) refuse2 "new_endTime '$NEWEND' is not an integer";; esac
[ -d "$CDIR" ] || refuse2 "no such case dir $CDIR"
[ -f "$CD" ]   || refuse2 "no system/controlDict"
[ -f "$CDIR/log.solve" ] || refuse2 "no log.solve -- there is no original segment to extend"
[ -f "$HERE/STATUS.$CASE" ] || refuse2 "no STATUS.$CASE -- the original segment never finished"

# --- collision guards (same shape as run_one_t3.sh G2; checked before cd) ---
# G2: no live process may already be running in this case dir.
for p in /proc/[0-9]*; do
    [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ] && \
        refuse3 "G2: pid ${p#/proc/} ($(readlink "$p/exe" 2>/dev/null)) already running in case dir"
done
# G3(ext1): the original segment's final time dir must exist, and no ext1 log may.
[ -d "$CDIR/20000" ] || refuse3 "G3: no 20000/ time dir -- nothing to resume from"
[ -e "$CDIR/log.solve.ext1" ] && refuse3 "G3: log.solve.ext1 already exists -- an extension has already run"

# --- controlDict: copy-edit + grep post-check after EACH sed, REFUSE if not applied ---
cp -p "$CD" "$CD.pre_ext1" || refuse2 "could not snapshot controlDict"

sed -E 's|^([[:space:]]*startFrom[[:space:]]+).*;|\1latestTime;|' "$CD" > "$CD.tmp" \
    || refuse2 "sed startFrom failed"
mv "$CD.tmp" "$CD" || refuse2 "mv after startFrom sed failed"
grep -Eq '^[[:space:]]*startFrom[[:space:]]+latestTime[[:space:]]*;' "$CD" \
    || refuse2 "POST-CHECK FAILED: startFrom is not latestTime after the sed -- refusing to start a solver that might restart from 0"

sed -E "s|^([[:space:]]*endTime[[:space:]]+)[0-9.eE+-]+;|\1$NEWEND;|" "$CD" > "$CD.tmp" \
    || refuse2 "sed endTime failed"
mv "$CD.tmp" "$CD" || refuse2 "mv after endTime sed failed"
grep -Eq "^[[:space:]]*endTime[[:space:]]+$NEWEND[[:space:]]*;" "$CD" \
    || refuse2 "POST-CHECK FAILED: endTime is not $NEWEND after the sed -- refusing to start a solver that would stop at the old endTime"

# stopAt must still be endTime, or the raised endTime means nothing.
grep -Eq '^[[:space:]]*stopAt[[:space:]]+endTime[[:space:]]*;' "$CD" \
    || refuse2 "POST-CHECK FAILED: stopAt is not endTime"

echo "controlDict OK  $CASE: $(grep -E '^[[:space:]]*(startFrom|endTime|stopAt)' "$CD" | tr -s ' \n' ' ')"

# --- solve.  0/ is not touched.  log.solve is not touched. ---
source /usr/lib/openfoam/openfoam2606/etc/bashrc
cd "$CDIR" || { echo "rc=127 wall=0 endTime=$NEWEND" > "$HERE/STATUS_EXT1.$CASE"; exit 127; }
T0=$(date +%s)
buoyantBoussinesqSimpleFoam > log.solve.ext1 2>&1
RC=$?
T1=$(date +%s)
echo "rc=$RC wall=$((T1-T0)) endTime=$NEWEND" > "$HERE/STATUS_EXT1.$CASE"
exit 0
