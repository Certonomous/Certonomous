#!/bin/bash
# T25R3 LAUNCHER -- ONE RUN, TWO CHAINED LEGS (prereg §6.3, §15 steps 7-9).
#
# *** THE rc IS CAPTURED INSIDE THIS WRAPPER, IMMEDIATELY AFTER EACH mpirun. ***
# `setsid timeout cmd` exits 0 for EVERY outcome including a timeout kill, so an
# rc read AROUND the setsid line is a constant zero wearing the costume of a
# measurement. The caller setsid's THIS script; the rc below is the solver's.
#
# THE AGE GUARD DEPENDS ON THE ORDER OF THE NEXT FIFTEEN LINES. `0` is created
# from `0.orig` here, not by the stager, and `0/module/T` is touched LAST, so it
# dates the run allowed to produce the answer. Every field rule 4 checks must be
# newer than it.
#
# THE LAUNCH GUARD APPLIES TO LEG A ONLY, as registered in §6.3 BEFORE compute:
# at leg B's launch, time directories exist BY DESIGN.
#
# *** THIS SCRIPT MUST BE INVOKED AS:
#       setsid nohup bash run_one_t25R3.sh <RUN> </dev/null >log 2>&1 &
#       disown
# MEASURED, NOT ASSUMED: launched WITHOUT `</dev/null` the solvers inherit the
# caller's stdin, and when the caller exits they are SIGKILLed -- no rc file, no
# trap output, an empty launch log and a solver log that simply STOPS mid-step.
# All six died that way and the evidence looked like a solver crash rather than
# a launch defect. A controlled probe (setsid + disown + </dev/null, ticking to
# a file) SURVIVED the caller's exit, which is what identified the cause. ***
RUN="$1"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE="$HERE/$RUN"

# *** A LAUNCHER THAT DIES SILENTLY IS WORSE THAN ONE THAT DIES. ***  MEASURED,
# NOT GUESSED: the first version of this script carried `set -u` and sourced the
# OpenFOAM bashrc as `. bashrc >/dev/null 2>&1`.  The bashrc references unset
# variables, `set -u` killed the shell inside it, and MY OWN REDIRECT swallowed
# the message -- all six runs exited in under two seconds leaving an EMPTY
# launch log and NO rc file at all.  Two defects, and the second is the worse
# one: the failure produced no evidence of itself.
#
# So: `set -u` is NOT used (every variable below is checked explicitly instead),
# the bashrc's own output is KEPT, and an EXIT TRAP records an rc for any path
# out of this script -- including the ones nobody thought of.
trap 'S=$?; [ -d "$CASE" ] && echo "$S" > "$CASE/.rc.$RUN.launcher"; \
      echo "launcher exit rc=$S"' EXIT

if [ ! -d "$CASE" ]; then echo "REFUSE: no case dir $CASE"; exit 89; fi
. /usr/lib/openfoam/openfoam2606/etc/bashrc > "$CASE/log.foamenv" 2>&1
if ! command -v chtMultiRegionFoam >/dev/null 2>&1; then
  echo "REFUSE: chtMultiRegionFoam is not on PATH after sourcing the OpenFOAM \
environment -- see $CASE/log.foamenv. Launching without a checked environment \
is how a run dies with an empty log."; exit 88
fi
cd "$CASE" || exit 90

case "$RUN" in
  S1)  TA=2715;  TB=6435  ;;   # cap 305  core-min -> 9150  s, split 3500:8300
  S2)  TA=6105;  TB=14475 ;;   # cap 686  -> 20580
  S3)  TA=13731; TB=32559 ;;   # cap 1543 -> 46290
  T2)  TA=12208; TB=28952 ;;   # cap 1372 -> 41160, split 7000:16600
  T4)  TA=24421; TB=57899 ;;   # cap 2744 -> 82320, split 14000:33200
  W30) TA=11170; TB=26480 ;;   # cap 1255 -> 37650
  *) echo "REFUSE: $RUN is not one of the six registered runs"; exit 91 ;;
esac

# ---- GUARD 1 (LEG A ONLY): no `0`, no time directory ----
if [ -d "$CASE/0" ]; then
  echo "REFUSE: $CASE/0 already exists; the age guard would be unevaluable"; exit 92
fi
# *** THE GLOB `[0-9]*` MATCHES `0.orig`. ***  MEASURED: the first version of
# this guard used it and REFUSED every freshly staged case, reporting a time
# directory that did not exist.  A guard that fires on a clean case is not a
# strict guard, it is a broken one, and it would have been trivially "fixed" by
# deleting the guard.  A time directory name is ALL digits with at most one
# decimal point, and that is what is matched.
TD=$(find "$CASE" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended \
     -regex '.*/[0-9]+(\.[0-9]+)?$' 2>/dev/null | head -3)
if [ -n "$TD" ]; then
  echo "REFUSE: $CASE already holds a time directory: $TD"; exit 93
fi

# ---- `0` FROM `0.orig`, REFERENCE TOUCHED LAST ----
cp -r "$CASE/0.orig" "$CASE/0" || exit 94
sleep 1
touch "$CASE/0/module/T" || exit 95

decomposePar -allRegions -force > log.decomposePar 2>&1
DRC=$?
echo "$DRC" > ".rc.$RUN.decomposePar"
[ "$DRC" -eq 0 ] || { echo "decomposePar rc=$DRC"; exit 96; }

# *** `--bind-to none` IS LOAD-BEARING AND WAS ADDED AFTER MEASUREMENT. ***
# OpenMPI binds ranks to cores by default, and each INDEPENDENT `mpirun` numbers
# from core 0. Six concurrent runs therefore pinned ALL TWELVE RANKS to CPUs 0
# and 1 -- six processes per core -- while cores 2-7 and 9-15 sat 100 percent
# IDLE. MEASURED, not inferred: `taskset -pc` reported allowed_cpus=0 for six
# ranks and =1 for the other six, and `mpstat -P ALL` showed 100 percent on
# cores 0 and 1 and 0.00 percent on ten others. The fleet was running at about a
# sixth of its speed and the logs looked like a slow solver rather than a
# scheduling defect. `--bind-to none` hands placement to the OS scheduler.
# IT CHANGES NO NUMBER: rank count, decomposition and arithmetic are identical,
# so only wall time moves.
# ---- LEG A ----
timeout "$TA" mpirun --bind-to none -np 2 chtMultiRegionFoam -parallel \
  > log.solve.legA 2>&1
RC_A=$?                                    # <-- INSIDE. This is the solver's.
echo "$RC_A" > ".rc.$RUN.legA"
if [ "$RC_A" -ne 0 ]; then
  echo "LEG A rc=$RC_A (124 = CAP STOP; rule 12: an overrun STOPS the run and \
does not get a new budget)"
  exit "$RC_A"
fi

# ---- SWAP TO LEG B ----
cp "$CASE/system/controlDict" "$CASE/system/controlDict.legA.used" || exit 97
cp "$CASE/system/controlDict.legB" "$CASE/system/controlDict" || exit 98

# ---- LEG B ----
timeout "$TB" mpirun --bind-to none -np 2 chtMultiRegionFoam -parallel \
  > log.solve.legB 2>&1
RC_B=$?                                    # <-- INSIDE.
echo "$RC_B" > ".rc.$RUN.legB"
if [ "$RC_B" -ne 0 ]; then
  echo "LEG B rc=$RC_B (124 = CAP STOP)"
  exit "$RC_B"
fi

reconstructPar -allRegions -newTimes > log.reconstructPar 2>&1
RRC=$?
echo "$RRC" > ".rc.$RUN.reconstructPar"
[ "$RRC" -eq 0 ] || { echo "reconstructPar rc=$RRC"; exit 99; }

python3 "$HERE/mark_done_t25R3.py" --mark "$CASE" "$RUN" > "STATUS.$RUN" 2>&1
echo "DONE $RUN"
