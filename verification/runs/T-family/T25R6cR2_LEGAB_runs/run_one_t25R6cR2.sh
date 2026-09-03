#!/bin/bash
# T25R6c-R2 RUNNER -- ONE CASE, TWO LEGS, ONE mpirun EACH.
#
#   run_one_t25R6cR2.sh [--case-dir <abs case dir>]
#
# rc IS CAPTURED INSIDE, immediately after each mpirun.  A `setsid timeout ...`
# line exits 0 for EVERY outcome including a kill, so an rc read around it is a
# constant zero that means nothing (T25R3 6.3; the lab's own measurement 4225ef0c).
set -o pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DEFAULT="$HERE/W1150_C4_L1"

# --- FROZEN AT THE REGISTRATION.  The hard per-run cap is 45.0 core-min at 2
# --- ranks = 1350 s of CPU budget.  It is split between the legs so neither can
# --- eat the other's:
# ---     leg A    60 s  ~ 3x the 14.36 s T25R6c's leg A actually took
# ---     leg B  1290 s  ~ 3x the 426.85 s predicted for 1110 leg-B steps
# --- and (60 + 1290) x 2 / 60 = 45.0000 core-min <= 45.0.  ASSERTED BELOW.
# --- The cap is ~3x the 14.707 core-min POINT estimate, which is this team's
# --- own figure.  IT IS NOT A REQUEST TO WIDEN ANYTHING: the whole run is
# --- 0.23 % of the 20,000 core-min T25 ceiling, which is not this team's to move.
TA_REG=60
TB_REG=1290
CAP_CORE_MIN=45.0
RANKS_REG=2

CASE="$CASE_DEFAULT"
while [ $# -gt 0 ]; do
  case "$1" in
    --case-dir) CASE="$2"; shift 2 ;;
    *) echo "REFUSE: unknown argument $1"; exit 80 ;;
  esac
done
RUN="$(basename "$CASE")"
trap 'S=$?; [ -d "$CASE" ] && echo "$S" > "$CASE/.rc.$RUN.launcher"; \
      echo "launcher exit rc=$S"' EXIT

# --- THE CAP IS ENFORCED, NOT INTENDED.  A cap nothing enforces is not a cap.
SUM=$(python3 -c "print('%.6f' % (($TA_REG + $TB_REG) * $RANKS_REG / 60.0))")
OK=$(python3 -c "print(1 if ($TA_REG + $TB_REG) * $RANKS_REG / 60.0 <= $CAP_CORE_MIN else 0)")
[ "$OK" = "1" ] || { echo "REFUSE: registered leg timeouts sum to $SUM core-min, above the registered cap $CAP_CORE_MIN"; exit 84; }
echo "  cap check: ($TA_REG + $TB_REG) s x $RANKS_REG ranks / 60 = $SUM core-min <= $CAP_CORE_MIN registered cap"

[ -d "$CASE" ] || { echo "REFUSE: no case dir $CASE (run stage_t25R6cR2.py first)"; exit 89; }

. /usr/lib/openfoam/openfoam2606/etc/bashrc > "$CASE/log.foamenv" 2>&1
command -v chtMultiRegionFoam >/dev/null 2>&1 || { echo "REFUSE: solver not on PATH"; exit 88; }
cd "$CASE" || exit 90

# --- RULE 4's AGE GUARD is only evaluable if `0/` is created HERE, at launch.
[ -d "$CASE/0" ] && { echo "REFUSE: 0/ exists; the age guard would be unevaluable"; exit 92; }
TD=$(find "$CASE" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended \
     -regex '.*/[0-9]+(\.[0-9]+)?$' 2>/dev/null | head -3)
[ -n "$TD" ] && { echo "REFUSE: time directory present: $TD"; exit 93; }
cp -r "$CASE/0.orig" "$CASE/0" || exit 94
# THE REGION IS `module`.  `0/module/T` -- NOT `0/T` -- is touched LAST, because
# it DATES the run allowed to produce the answer.  A comparator asserting `0/T`
# on this family would assert a file that does not exist.
sleep 1; touch "$CASE/0/module/T" || exit 95
[ -f "$CASE/0/module/T" ] || { echo "REFUSE: 0/module/T was not created"; exit 95; }

# --- THE WRITE CONTROL THAT KILLED T25R6c.  Leg B MUST be runTime, not timeStep:
# --- timeStep counts the GLOBAL time index, which does not reset across a
# --- `startFrom latestTime` restart, so leg A's 40 steps offset it and nothing
# --- writes at endTime.  Checked on the bytes about to be used, not on intent.
WC=$(grep -cE '^writeControl[[:space:]]+runTime;' "$CASE/system/controlDict.legB")
[ "$WC" = "1" ] || { echo "REFUSE: leg B controlDict is not writeControl runTime -- THE T25R6c DEFECT WOULD REPEAT"; exit 86; }
WI=$(grep -cE '^writeInterval[[:space:]]+111;' "$CASE/system/controlDict.legB")
[ "$WI" = "1" ] || { echo "REFUSE: leg B writeInterval is not the registered 111"; exit 87; }
ET=$(grep -cE '^endTime[[:space:]]+111\.8;' "$CASE/system/controlDict.legB")
[ "$ET" = "1" ] || { echo "REFUSE: leg B endTime is not the registered 111.8"; exit 85; }
echo "  ok   leg B write control verified on disk: runTime / 111 / endTime 111.8"

decomposePar -allRegions -force > log.decomposePar 2>&1
D=$?; echo "$D" > ".rc.$RUN.decomposePar"; [ "$D" -eq 0 ] || exit 96

# --- CONTENTION WITNESS.  This rung's whole output is a TIMING RATIO between two
# --- windows on a SHARED box.  ExecutionTime is CPU TIME (verified from this
# --- build's source, see grade_t25R6cR2.py), so pure descheduling DEFLATES it
# --- rather than inflating it -- but memory-bandwidth contention and MPI
# --- busy-wait still charge to it.  /proc/loadavg is witnessed before A, between
# --- and after B, AND ITS RUNNABLE FIELD IS THE ONE THAT MATTERS: T25R6c's
# --- loadavg of 51.80-58.34 was read as oversubscription when the same
# --- witnesses' runnable counts were 9-11 against 16 cores.  nproc is recorded
# --- beside them so the ratio is never read without its denominator again.
nproc > ".ncores.$RUN"
cat /proc/loadavg > ".load.$RUN.before_legA"
date -u +%Y-%m-%dT%H:%M:%SZ > ".t.$RUN.start"

# ---- LEG A: 40 steps, deltaT 0.02, startTime -> 0.8 --------------------------
timeout "$TA_REG" mpirun --bind-to none -np "$RANKS_REG" chtMultiRegionFoam -parallel \
  > log.solve.legA 2>&1
RC_A=$?                                    # <-- INSIDE, immediately after mpirun
echo "$RC_A" > ".rc.$RUN.legA"
cat /proc/loadavg > ".load.$RUN.between_legs"
if [ "$RC_A" -ne 0 ]; then
  echo "LEG A rc=$RC_A (124 = CAP STOP; rule 12: an overrun STOPS the run and does not get a new budget)"
  exit "$RC_A"
fi

# ---- SWAP TO LEG B ----------------------------------------------------------
cp "$CASE/system/controlDict" "$CASE/system/controlDict.legA.used" || exit 97
cp "$CASE/system/controlDict.legB" "$CASE/system/controlDict" || exit 98

# ---- LEG B: 1110 steps, deltaT 0.1, latestTime -> 111.8 ---------------------
timeout "$TB_REG" mpirun --bind-to none -np "$RANKS_REG" chtMultiRegionFoam -parallel \
  > log.solve.legB 2>&1
RC_B=$?                                    # <-- INSIDE
echo "$RC_B" > ".rc.$RUN.legB"
cat /proc/loadavg > ".load.$RUN.after_legB"
date -u +%Y-%m-%dT%H:%M:%SZ > ".t.$RUN.end"
if [ "$RC_B" -ne 0 ]; then
  echo "LEG B rc=$RC_B (124 = CAP STOP)"
  exit "$RC_B"
fi

reconstructPar -allRegions -newTimes > log.reconstructPar 2>&1
RRC=$?; echo "$RRC" > ".rc.$RUN.reconstructPar"
[ "$RRC" -eq 0 ] || { echo "reconstructPar rc=$RRC"; exit 99; }

python3 "$HERE/mark_done_t25R6cR2.py" --case "$CASE" || true
echo "T25R6c-R2 $RUN legA rc=$RC_A legB rc=$RC_B"
exit 0
