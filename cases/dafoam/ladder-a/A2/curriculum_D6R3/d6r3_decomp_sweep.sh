#!/bin/bash
# D6R3 DECOMP SWEEP DRIVER -- runs the registered cells in the registered order and batching,
# then rolls them up through the registered grading path.
# Registered by D6R3_DECOMP_PREREGISTRATION.md before any compute (rule 2).  DRAFT (rule 7).
#
# REPAIR 2 (ADDENDUM 1, 2026-09-13).  The first version of this driver did `P=$(start 28 "")`.
# COMMAND SUBSTITUTION RUNS start() IN A SUBSHELL, so the backgrounded arm is a GRANDCHILD of
# this script and `wait $P` was not waiting on a child at all -- it returned instantly and all
# three batches launched at once, five cells claiming 56 DISTINCT cores against the registered
# 28-core ceiling.  Measured, disclosed in the ledger, the four over-footprint cells stopped and
# removed as NOT A RESULT.  This version backgrounds each cell INLINE and captures $! in the
# driver's own shell, and it additionally REFUSES to open a batch while any DECOMP container is
# still up -- so the ceiling is enforced by the driver and not merely intended by it.
#
# usage: d6r3_decomp_sweep.sh [FIRST_BATCH]     FIRST_BATCH defaults to 1
#
# ORDER AND BATCHING ARE REGISTERED, and chosen to FINISH rather than be pre-empted: the 48-core
# propeller lane takes its cores the moment its mesh gate passes, so the sweep never holds more
# than 28 and lands the most load-bearing cell (28 ranks, carrying G-DET) first and cheapest.
#   batch 1: N28              (28 cores)
#   batch 2: N20 + N08        (28 cores)
#   batch 3: N16 + N12        (28 cores)
set -uo pipefail
FIRST_BATCH="${1:-1}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085
LEDGER="$ROOT/ledger.txt"
ARMSH="$HERE/d6r3_decomp_arm.sh"
say(){ echo "D6R3_DEC_SWEEP_$1 $2" | tee -a "$LEDGER"; }
cellname(){ printf "DECOMP_N%02d" "$1"; }

# THE CEILING GUARD.  Never opens a batch while a DECOMP container is still holding cores.
# It waits; it never stops anything (directive #17).
wait_all_clear(){
  local i=0 n
  while [ $i -lt 720 ]; do
    n=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -c '^d6r3_DECOMP_')
    [ "$n" -eq 0 ] && { say CEILING "no DECOMP container holding cores; batch may open"; return 0; }
    [ $((i % 12)) -eq 0 ] && say CEILING "waiting: $n DECOMP container(s) still up"
    sleep 10; i=$((i+1))
  done
  say CEILING "REFUSE: a DECOMP container was still up after 2 h; not opening the batch"
  return 1
}

# wait until a backgrounded cell has passed G-CORES and published the cores it took
wait_cpuset(){
  local arm="$1" i=0
  while [ $i -lt 60 ]; do
    [ -s "$ROOT/$arm.cpuset" ] && { cat "$ROOT/$arm.cpuset"; return 0; }
    sleep 5; i=$((i+1))
  done
  echo ""; return 1
}

say START "$(date -u +%Y-%m-%dT%H:%M:%SZ) first_batch=$FIRST_BATCH freeze=$(cd "$HERE" && git rev-parse HEAD)"

if [ "$FIRST_BATCH" -le 1 ]; then
  wait_all_clear || exit 12
  bash "$ARMSH" 28 "" >>"$ROOT/sweep_driver.log" 2>&1 &
  P1=$!
  say BATCH1 "N28 pid=$P1"
  wait "$P1"; R1=$?
  say BATCH1_DONE "N28 rc=$R1"
fi

if [ "$FIRST_BATCH" -le 2 ]; then
  wait_all_clear || exit 12
  rm -f "$ROOT/$(cellname 20).cpuset" "$ROOT/$(cellname 8).cpuset"
  bash "$ARMSH" 20 "" >>"$ROOT/sweep_driver.log" 2>&1 &
  PA=$!
  EX=$(wait_cpuset "$(cellname 20)")
  say BATCH2 "N20 pid=$PA cpuset=[$EX]"
  bash "$ARMSH" 8 "$EX" >>"$ROOT/sweep_driver.log" 2>&1 &
  PB=$!
  say BATCH2 "N08 pid=$PB excluding=[$EX]"
  wait "$PA"; RA=$?
  wait "$PB"; RB=$?
  say BATCH2_DONE "N20 rc=$RA  N08 rc=$RB"
fi

if [ "$FIRST_BATCH" -le 3 ]; then
  wait_all_clear || exit 12
  rm -f "$ROOT/$(cellname 16).cpuset" "$ROOT/$(cellname 12).cpuset"
  bash "$ARMSH" 16 "" >>"$ROOT/sweep_driver.log" 2>&1 &
  PC=$!
  EX2=$(wait_cpuset "$(cellname 16)")
  say BATCH3 "N16 pid=$PC cpuset=[$EX2]"
  bash "$ARMSH" 12 "$EX2" >>"$ROOT/sweep_driver.log" 2>&1 &
  PD=$!
  say BATCH3 "N12 pid=$PD excluding=[$EX2]"
  wait "$PC"; RC3=$?
  wait "$PD"; RD=$?
  say BATCH3_DONE "N16 rc=$RC3  N12 rc=$RD"
fi

CELLS=""
for n in 28 20 16 12 8; do
  f="$ROOT/$(cellname $n)_GRADE.json"
  [ -s "$f" ] && CELLS="$CELLS $f"
done
if [ -n "$CELLS" ]; then
  python3 "$HERE/d6r3_decomp_grade.py" --rollup $CELLS > "$ROOT/DECOMP_SWEEP_ROLLUP.json" 2>"$ROOT/DECOMP_SWEEP_ROLLUP.err"
  say ROLLUP "$ROOT/DECOMP_SWEEP_ROLLUP.json from$CELLS"
else
  say ROLLUP "NO CELL GRADE JSON PRODUCED -- sweep is NOT A RESULT"
fi
say END "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
