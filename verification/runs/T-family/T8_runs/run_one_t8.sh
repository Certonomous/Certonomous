#!/bin/bash
# T8 launcher -- ONE level, serial, with the arming guard and the registered cap.
#
# NOTHING IN THIS FILE MAY BE RUN UNTIL THE SUPERVISOR AUTHORISES THE FIRE.
#
# `set -e` is NOT relied upon: it does not gate at the top level of an agent's
# Bash call, and `( set -e; ... )` silently fails to gate too.  Every gating
# step therefore carries an explicit `|| { echo ABORT...; exit 1; }`.
#
# Arming guard (CLAUDE.md rule 4): REFUSE if `0/` or any time directory already
# exists.  `0/` is created here, from `0.orig/`, and `0/T` is touched LAST so
# that it dates the run allowed to produce the answer -- the age guard reads it.
#
# Cap (CLAUDE.md rule 12): timeout = cap_core_min * 60 / ranks.  ranks = 1, so
#   c  15 core-min ->    900 s
#   m  80 core-min ->   4800 s
#   f 500 core-min ->  30000 s
# A level killed by its cap is PENDING, a right-censored measurement, NEVER
# GATE FAIL.  An overrun stops the level; it does not get a new budget.

LEVEL="$1"
[ -n "$LEVEL" ] || { echo "ABORT: usage: run_one_t8.sh {c|m|f}"; exit 1; }

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || { echo "ABORT: cannot resolve HERE"; exit 1; }
CASE="$HERE/T8_MTT_$LEVEL"
RANKS=1

case "$LEVEL" in
  c) CAP_CORE_MIN=15  ;;
  m) CAP_CORE_MIN=80  ;;
  f) CAP_CORE_MIN=500 ;;
  *) echo "ABORT: unknown level '$LEVEL'"; exit 1 ;;
esac
TIMEOUT_S=$(( CAP_CORE_MIN * 60 / RANKS ))

[ -d "$CASE" ] || { echo "ABORT: no case directory $CASE"; exit 1; }

# ---- arming guard --------------------------------------------------------
[ -e "$CASE/0" ] && { echo "REFUSE: $CASE/0 already exists -- this case has been armed before"; exit 1; }
STALE=$(find "$CASE" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' -printf '%f ' 2>/dev/null)
[ -n "$STALE" ] && { echo "REFUSE: $CASE already holds time directories: $STALE"; exit 1; }
[ -d "$CASE/constant/polyMesh" ] || { echo "ABORT: $CASE has no mesh"; exit 1; }
[ -d "$CASE/0.orig" ] || { echo "ABORT: $CASE has no 0.orig"; exit 1; }

# ---- arm: 0/ from 0.orig, 0/T touched LAST -------------------------------
cp -r "$CASE/0.orig" "$CASE/0" || { echo "ABORT: could not create 0/ from 0.orig"; exit 1; }
for f in U p_rgh alphat nut k epsilon; do
  [ -f "$CASE/0/$f" ] || { echo "ABORT: 0/$f missing after arming"; exit 1; }
done
[ -f "$CASE/0/T" ] || { echo "ABORT: 0/T missing after arming"; exit 1; }
sleep 1
touch "$CASE/0/T" || { echo "ABORT: could not touch 0/T"; exit 1; }

# ---- solve ---------------------------------------------------------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>&1 || { echo "ABORT: no OpenFOAM environment"; exit 1; }
START=$(date +%s)
timeout --signal=TERM --kill-after=60 "$TIMEOUT_S" \
    buoyantBoussinesqSimpleFoam -case "$CASE" > "$CASE/log.solve" 2>&1
RC=$?
END=$(date +%s)
WALL=$(( END - START ))
CORE_MIN=$(awk -v w="$WALL" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60.0}')

{
  echo "case=T8_MTT_$LEVEL"
  echo "rc=$RC"
  echo "wall_s=$WALL"
  echo "ranks=$RANKS"
  echo "core_min=$CORE_MIN"
  echo "cap_core_min=$CAP_CORE_MIN"
  echo "timeout_s=$TIMEOUT_S"
  if [ "$RC" -eq 124 ] || [ "$RC" -eq 137 ]; then
    echo "verdict=PENDING (killed by the registered cap; right-censored, NOT GATE FAIL)"
  fi
} > "$HERE/STATUS.T8_MTT_$LEVEL"

echo "T8_MTT_$LEVEL rc=$RC wall=${WALL}s core_min=$CORE_MIN cap=$CAP_CORE_MIN"
exit 0
