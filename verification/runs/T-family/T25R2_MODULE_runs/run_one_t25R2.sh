#!/usr/bin/env bash
# LAUNCHER for ONE registered T25R2 case.
#
# Registered at docs/campaigns/T-family/T25R2_PREREGISTRATION.md sections 1,
# 6.4 and 8.2.  Written and committed BEFORE ANY T25R2 COMPUTE.
#
# PATTERN: run_one_t25R.sh, which is FROZEN and IS NOT EDITED (rule 6).  Its
# three guards were right and are inherited verbatim; what changes is the case
# list (FOUR now, including the section 3.5 outer-loop arm) and the name of the
# script that stages a case.
#
# *** THIS FILE HAS NEVER BEEN EXECUTED. ***  Section 10 registers the order
# commit -> the supervisor's personal diff read -> mesh -> launch.
#
# THREE THINGS THIS SCRIPT EXISTS TO GET RIGHT, EACH PAID FOR BY A PAST FAILURE:
#
#  1. THE rc IS CAPTURED INSIDE THE DETACHED WRAPPER, NEVER AROUND `setsid`.
#     `setsid timeout cmd` EXITS 0 FOR EVERY OUTCOME.  An rc read from the
#     setsid line is the shape of a false clean.  Here the solver's own `$?` is
#     captured on the line after it runs, inside the same shell that ran it.
#
#  2. `0/module/T` IS TOUCHED LAST, IMMEDIATELY BEFORE THE START BLOCK.  Rule 4
#     conjunct 6's age guard dates the run against that file, so it must be the
#     newest thing on disk when the solver starts and nothing may be written
#     after it.  A multi-region case has NO `0/T`; the referent is per section
#     6.4 conjunct 6.
#
#  3. THE GUARD REFUSES A DIRTY CASE.  If `0` or any non-zero time directory
#     already exists, this script REFUSES.  A re-launch over an existing time
#     tree makes the age guard unevaluable and can leave fields from a previous
#     run that would satisfy conjunct 4 without having been written by this one.
#
# `set -e` is NOT relied on: it does not gate when the failing command is a
# non-final member of an && / || list.  Every step is checked explicitly with
# `|| { echo ABORT ...; exit 1; }`.
#
# Usage: run_one_t25R2.sh <CASE> <TIMEOUT_S> <CAP_CORE_MIN>
# The timeout and the cap are PASSED IN, never defaulted: they are registered
# per case at section 8.2 and a default here would silently re-price a run.

CASE="$1"
TIMEOUT_S="$2"
CAP_CORE_MIN="$3"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
D="$HERE/$CASE"
RANKS=1

case "$CASE" in
  T25R2_L1|T25R2_L1_OC20|T25R2_L2|T25R2_L2_DT025) ;;
  *) echo "ABORT: $CASE is not a registered T25R2 case (section 1)"; exit 1 ;;
esac
[ -n "$TIMEOUT_S" ] && [ -n "$CAP_CORE_MIN" ] || {
  echo "ABORT: timeout_s and cap_core_min are REGISTERED per case (section 8.2)"
  echo "       and are never defaulted here"; exit 1; }
[ -d "$D" ] || { echo "ABORT: no case directory $D"; exit 1; }

# --- GUARD 3: refuse a dirty case. -----------------------------------------
if [ -d "$D/0" ]; then
  echo "ABORT: $D/0 already exists. Rule 4's age guard dates the run against"
  echo "       0/module/T and a pre-existing 0 makes that unevaluable."
  exit 1
fi
STALE=$(find "$D" -maxdepth 1 -regextype posix-extended \
        -regex '.*/[0-9]+(\.[0-9]+)?' -not -name 0 2>/dev/null | head -3)
if [ -n "$STALE" ]; then
  echo "ABORT: $D already holds time directories:"; echo "$STALE"
  echo "       A relaunch over an existing time tree is refused, not cleaned."
  exit 1
fi
[ -d "$D/0.orig" ] || { echo "ABORT: no $D/0.orig -- run stage_t25R2.py <CASE> first"
                        exit 1; }
[ -d "$D/constant/coolant/polyMesh" ] && [ -d "$D/constant/module/polyMesh" ] || {
  echo "ABORT: both region meshes must exist -- run stage_t25R2.py <CASE> first"
  exit 1; }

cp -a "$D/0.orig" "$D/0" || { echo "ABORT: could not stage 0 from 0.orig"; exit 1; }
[ -f "$D/0/module/T" ] || { echo "ABORT: no 0/module/T after staging"; exit 1; }

# --- GUARD 2: the age referent is touched LAST. -----------------------------
# NOTHING may be written into the case between this line and the solver start.
touch "$D/0/module/T" || { echo "ABORT: could not touch the age referent"; exit 1; }

START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
T0=$(date +%s)

# --- GUARD 1: rc captured INSIDE the wrapper. ------------------------------
setsid bash -c '
  cd "'"$D"'" || exit 97
  . /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
  timeout '"$TIMEOUT_S"' chtMultiRegionFoam > log.solve 2>&1
  echo $? > .rc.'"$CASE"'
' </dev/null >/dev/null 2>&1

while [ ! -f "$D/.rc.$CASE" ]; do sleep 5; done
RC=$(cat "$D/.rc.$CASE")
T1=$(date +%s)
WALL=$((T1 - T0))
CORE_MIN=$(awk -v w="$WALL" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')
CAPPED=no
[ "$RC" = "124" ] && CAPPED=yes

# --- STATUS lives INSIDE the case directory (section 6.4). -----------------
# `rc` here is the SOLVER's, captured inside the wrapper. It is written for the
# record; mark_done_t25R2.py DERIVES conjunct 1 from log.solve regardless,
# because the queue runner is measured to clobber this file.
cat > "$D/STATUS.$CASE" <<EOF
case=$CASE
rc=$RC
wall_s=$WALL
ranks=$RANKS
core_min=$CORE_MIN
cap_core_min=$CAP_CORE_MIN
timeout_s=$TIMEOUT_S
capped=$CAPPED
solver=chtMultiRegionFoam
started_utc=$START
ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
note=rc-captured-INSIDE-the-detached-wrapper-NOT-around-setsid
EOF

echo "$CASE rc=$RC wall_s=$WALL core_min=$CORE_MIN cap=$CAP_CORE_MIN capped=$CAPPED"
if [ "$CAPPED" = "yes" ]; then
  echo "CAP STOP: $CASE reached its REGISTERED cap and was STOPPED."
  echo "  CLAUDE.md rule 12: it DOES NOT GET A NEW BUDGET. This row is"
  echo "  NOT A RESULT, the other rows are untouched, and the cap stop is its"
  echo "  own finding -- never folded into the cost ratio."
fi
exit "$RC"
