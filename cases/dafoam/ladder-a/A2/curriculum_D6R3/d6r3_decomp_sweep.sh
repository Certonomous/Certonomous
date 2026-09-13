#!/bin/bash
# D6R3 DECOMP SWEEP DRIVER -- runs the five registered cells of the decomposition sweep in the
# registered order and batching, then rolls them up through the registered grading path.
# Registered by D6R3_DECOMP_PREREGISTRATION.md before any compute (rule 2).  DRAFT (rule 7).
#
# ORDER AND BATCHING ARE REGISTERED, and they are chosen to FINISH rather than to be pre-empted:
# the 48-core propeller lane takes its cores the moment its mesh gate passes, so the sweep never
# holds more than 28 cores and lands its most load-bearing cell (the 28-rank replication that
# carries G-DET) first and cheapest.
#   batch 1: N28              (28 cores)  -- G-DET.  If G-DET is GATE FAIL the sweep is
#                                            NOT A RESULT and batches 2 and 3 still run, because
#                                            a non-deterministic case is itself the finding.
#   batch 2: N20 + N08        (28 cores)  -- production ceiling, and the longest lever arm
#   batch 3: N16 + N12        (28 cores)  -- the interior of the sweep
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085
LEDGER="$ROOT/ledger.txt"
ARMSH="$HERE/d6r3_decomp_arm.sh"
say(){ echo "D6R3_DEC_SWEEP_$1 $2" | tee -a "$LEDGER"; }

cellname(){ printf "DECOMP_N%02d" "$1"; }

# wait until a backgrounded cell has passed G-CORES and published the cores it took
wait_cpuset(){
  local arm="$1" i=0
  while [ $i -lt 60 ]; do
    [ -s "$ROOT/$arm.cpuset" ] && { cat "$ROOT/$arm.cpuset"; return 0; }
    sleep 5; i=$((i+1))
  done
  echo ""; return 1
}

start(){   # start <ranks> <exclude>   -> backgrounds one cell, echoes its pid
  local n="$1" ex="${2:-}"
  bash "$ARMSH" "$n" "$ex" >>"$ROOT/sweep_driver.log" 2>&1 &
  echo $!
}

say START "$(date -u +%Y-%m-%dT%H:%M:%SZ) freeze=$(cd "$HERE" && git rev-parse HEAD)"

# ---- batch 1: the replication cell, alone -------------------------------------------------
P1=$(start 28 "")
say BATCH1 "N28 pid=$P1"
wait $P1; R1=$?
say BATCH1_DONE "N28 rc=$R1"

# ---- batch 2: N20 then N08, N08 excluding N20's cores --------------------------------------
rm -f "$ROOT/$(cellname 20).cpuset" "$ROOT/$(cellname 8).cpuset"
PA=$(start 20 "")
EX=$(wait_cpuset "$(cellname 20)")
say BATCH2 "N20 pid=$PA cpuset=[$EX]"
PB=$(start 8 "$EX")
say BATCH2 "N08 pid=$PB excluding=[$EX]"
wait $PA; RA=$?
wait $PB; RB=$?
say BATCH2_DONE "N20 rc=$RA  N08 rc=$RB"

# ---- batch 3: N16 then N12, N12 excluding N16's cores --------------------------------------
rm -f "$ROOT/$(cellname 16).cpuset" "$ROOT/$(cellname 12).cpuset"
PC=$(start 16 "")
EX2=$(wait_cpuset "$(cellname 16)")
say BATCH3 "N16 pid=$PC cpuset=[$EX2]"
PD=$(start 12 "$EX2")
say BATCH3 "N12 pid=$PD excluding=[$EX2]"
wait $PC; RC3=$?
wait $PD; RD=$?
say BATCH3_DONE "N16 rc=$RC3  N12 rc=$RD"

# ---- rollup through the registered grading path --------------------------------------------
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
