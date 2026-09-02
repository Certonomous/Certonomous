#!/bin/bash
# T25R5 ARM RUNNER -- ONE ARM, 40 STEPS, endTime 0.8 (prereg section 3.1).
#
# Invoke as:
#   setsid nohup bash run_one_t25R5.sh <ARM>_L2 </dev/null > launch.<ARM>_L2.out 2>&1 &
#   disown
#
# `</dev/null` IS LOAD-BEARING: without it the solver inherits the caller's stdin
# and is SIGKILLed when the caller exits, leaving NO rc file and NO trap output
# (T25R3 section 6.3).  rc IS CAPTURED INSIDE, immediately after mpirun -- a
# `setsid timeout ...` line exits 0 for EVERY outcome including a kill, so an rc
# read around it is a constant zero that means nothing.
set -o pipefail
RUN="$1"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE="$HERE/$RUN"
trap 'S=$?; [ -d "$CASE" ] && echo "$S" > "$CASE/.rc.$RUN.launcher"; \
      echo "launcher exit rc=$S"' EXIT

# --- REGISTERED TIMEOUTS, prereg section 5.2 as amended by A1.2.  An arm slower
# --- than 1.5x the measured T25R4 baseline is DISQUALIFIED by E3 BY DEFINITION,
# --- so the timeout kill IS the measurement, not waste.
case "$RUN" in
  *_L1) TO=290  ;;   # CAP  9.667 core-min at 2 ranks
  *_L2) TO=770  ;;   # CAP 25.667
  *_L3) TO=1600 ;;   # CAP 53.333
  *) echo "REFUSE: $RUN carries no registered level suffix (_L1/_L2/_L3)"; exit 91 ;;
esac

[ -d "$CASE" ] || { echo "REFUSE: no case dir $CASE"; exit 89; }

# --- E6 IS ENFORCED HERE, NOT ASSUMED.  Exit 0 is the FULL E6 verdict; exit 3
# --- (ADMISSIBLE-DICTONLY) is NOT E6 and must not launch a solver.
ARM="${RUN%_L*}"
python3 "$HERE/verify_arm_t25R5.py" --arm "$ARM" --case "$CASE"
V=$?
[ "$V" -eq 0 ] || { echo "REFUSE: verify_arm_t25R5.py returned $V (0 = full E6). Not launching."; exit 87; }

. /usr/lib/openfoam/openfoam2606/etc/bashrc > "$CASE/log.foamenv" 2>&1
command -v chtMultiRegionFoam >/dev/null 2>&1 || { echo "REFUSE: solver not on PATH"; exit 88; }
cd "$CASE" || exit 90

# --- RULE 4's AGE GUARD is only evaluable if `0/` is created HERE, at launch.
[ -d "$CASE/0" ] && { echo "REFUSE: 0/ exists; the age guard would be unevaluable"; exit 92; }
TD=$(find "$CASE" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended \
     -regex '.*/[0-9]+(\.[0-9]+)?$' 2>/dev/null | head -3)
[ -n "$TD" ] && { echo "REFUSE: time directory present: $TD"; exit 93; }
cp -r "$CASE/0.orig" "$CASE/0" || exit 94
sleep 1; touch "$CASE/0/module/T" || exit 95   # touched LAST: it dates the run

decomposePar -allRegions -force > log.decomposePar 2>&1
D=$?; echo "$D" > ".rc.$RUN.decomposePar"; [ "$D" -eq 0 ] || exit 96

# --- CONTENTION WITNESS.  Stage 0's whole output is a TIMING RATIO, and this box
# --- is shared.  Record the load either side of the run so the ratio can be read
# --- with its environment rather than as if the box were quiet.
cat /proc/loadavg > ".load.$RUN.before"
date -u +%Y-%m-%dT%H:%M:%SZ > ".t.$RUN.start"

timeout "$TO" mpirun --bind-to none -np 2 chtMultiRegionFoam -parallel > log.solve.legA 2>&1
RC=$?                                   # <-- INSIDE, immediately after mpirun
echo "$RC" > ".rc.$RUN.legA"
date -u +%Y-%m-%dT%H:%M:%SZ > ".t.$RUN.end"
cat /proc/loadavg > ".load.$RUN.after"
echo "T25R5 $RUN rc=$RC (124 = CAP STOP; rule 12: an overrun stops the run)"
exit "$RC"
