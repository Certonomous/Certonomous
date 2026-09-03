#!/bin/bash
# T25R6c RUNNER -- ONE CASE, TWO LEGS, ONE mpirun EACH.
#
#   run_one_t25R6c.sh [--case-dir <abs case dir>]
#
# rc IS CAPTURED INSIDE, immediately after each mpirun.  A `setsid timeout ...`
# line exits 0 for EVERY outcome including a kill, so an rc read around it is a
# constant zero that means nothing (T25R3 6.3; the lab's own measurement 4225ef0c).
set -o pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DEFAULT="$HERE/W440_C4_L1"

# --- FROZEN AT THE REGISTRATION (amendment v1.1).  The hard per-run cap is
# --- 210.485 core-min at 2 ranks = 6314.55 s of wall.  It is SPLIT between the
# --- legs in proportion to their registered step counts, 40 : 400, so neither
# --- leg can eat the other's budget:
# ---     leg A  40/440 x 6314.55 =  574.05 s  -> 574
# ---     leg B 400/440 x 6314.55 = 5740.50 s  -> 5740
# --- and (574 + 5740) x 2 / 60 = 210.4667 core-min <= 210.485.  ASSERTED BELOW.
TA_REG=574
TB_REG=5740
CAP_CORE_MIN=210.485
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

[ -d "$CASE" ] || { echo "REFUSE: no case dir $CASE (run stage_t25R6c.py first)"; exit 89; }

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

decomposePar -allRegions -force > log.decomposePar 2>&1
D=$?; echo "$D" > ".rc.$RUN.decomposePar"; [ "$D" -eq 0 ] || exit 96

# --- CONTENTION WITNESS.  This rung's whole output is a TIMING RATIO between two
# --- windows on a SHARED box.  If per-core throughput differs between the legs,
# --- rho absorbs contention as if it were the deltaT regime change -- the one
# --- shared assumption that would break the legs' independence.  Witnessed here
# --- BEFORE A, BETWEEN, and AFTER B so the ratio is read with its environment.
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

# ---- LEG B: 400 steps, deltaT 0.1, latestTime -> 40.8 -----------------------
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

python3 "$HERE/mark_done_t25R6c.py" --case "$CASE" || true
echo "T25R6c $RUN legA rc=$RC_A legB rc=$RC_B"
exit 0
