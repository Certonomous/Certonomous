#!/bin/bash
# DETACHED autograder for the M6 own-family fine-triple (disconnect-prep, 2026-09-08).
# WHY: run_m6_own_family_triple.sh DEFERS grading (its line 309 -- "THIS DRIVER GRADES
# NOTHING"); the queue daemon runs no post-completion grade hook. So without this watcher,
# a fleet death while Sanaa is offline would leave the triple SOLVED but UNGRADED -- raw
# fields, no Gate P verdict. This watcher is launched via setsid so it survives the death of
# the launching agent AND the whole fleet: it waits for the triple driver to terminate, then
# runs the PINNED, check-1'd grader and writes Gate P + the observed-order triple to disk.
# It grades NOTHING itself -- it invokes analyse_m6_own_family.py --grade, the frozen
# instrument (rule 2; the grader re-hashes its own committed blob + rehearses the planted
# controls before grading). rc is captured INSIDE this wrapper (L-'setsid parent returns 0').
set +e
cd /home/ubuntu/Certonomous || exit 1
RR=verification/runs/M6_OWN_FAMILY_runs
GRADER="$RR/analyse_m6_own_family.py"
OUT="$RR/M6_OWN_FAMILY_FINE_TRIPLE_AUTOGRADE.out"
RCF="$RR/M6_OWN_FAMILY_FINE_TRIPLE_AUTOGRADE.rc"
STAMP="$RR/M6_OWN_FAMILY_FINE_TRIPLE_AUTOGRADE.stamp"
{
  echo "armed=$(date -u +%FT%TZ) pid=$$ ppid=$PPID"
  echo "purpose=detached autograde of the M6 own-family fine-triple; survives fleet death"
} > "$STAMP"

# 1) WAIT for the triple driver to terminate (all levels solved, OR a level crashed and the
#    && chain aborted). Cap 4h (triple ~1.5h + generous margin).
i=0
while [ $i -lt 960 ]; do            # 960 * 15s = 4h
  if ! pgrep -f 'run_m6_own_family_triple.sh' >/dev/null 2>&1; then
    echo "driver_terminal=$(date -u +%FT%TZ) after_${i}x15s" >> "$STAMP"
    break
  fi
  i=$((i+1)); sleep 15
done
[ $i -ge 960 ] && echo "driver_wait_TIMEOUT_4h=$(date -u +%FT%TZ) -- grading anyway (grader will refuse on incomplete, honest)" >> "$STAMP"

# 2) RUN the pinned grader. It emits Gate G + Gate P + the {L2,L1,L0} triple to stdout and
#    REFUSES (exit 2) fail-closed if any level is incomplete/crashed (rule-4). Either way a
#    durable verdict lands on disk. rc captured INSIDE this wrapper.
python3 "$GRADER" --grade > "$OUT" 2>&1
GRC=$?
echo "$GRC" > "$RCF"
echo "grade_complete=$(date -u +%FT%TZ) grader_rc=$GRC out=$OUT" >> "$STAMP"
echo "NOTE: this is the FROZEN INSTRUMENT's verdict on disk. A returning agent still owes the" >> "$STAMP"
echo "assembled RESULTS record + the supervisor's check-3 big-claim read before it is repeated upward." >> "$STAMP"
exit 0
