#!/bin/bash
# SUBOFF A1b -- RUN WATCHER.  IT ESCALATES AND IT NEVER KILLS.
#
# Sanaa, ~2026-09-12T01:10Z, verbatim: "dont forget i dont want any cap on any run".
# WITH NO CAPS A HEALTHY RUN MAY BE ARBITRARILY LONG, so a watcher sized against a capped
# run is under-sized by construction, and a watcher that gives up on a healthy run
# produces no record -- the same loss by another route.  This one therefore has NO kill
# path at all: every branch below writes a line and keeps watching.
#
# It reports, into <case>/WATCH.log:
#   STALL      - no new ExecutionTime line for STALL_S seconds (the run may be starved,
#                not dead: the box has run 3.7x oversubscribed tonight)
#   CEILING    - the DERIVED wall ceiling was reached.  A REPORT TO THE SUPERVISOR, NOT A
#                TERMINATION.  Derived per level in SUBOFF_A1b 6, never a literal.
#   EXIT       - the run wrote solve_rc.  The watcher then stops, having nothing to watch.
#   PROGRESS   - a heartbeat every PROGRESS_S, with the measured s/iteration so the rate
#                is on record with its timestamp (rates moved 2.4x in 40 min tonight).
set -u
CASE="$1"; CEIL_S="$2"; STALL_S="${3:-1800}"; PROGRESS_S="${4:-1800}"
LOG="$CASE/WATCH.log"; SL="$CASE/log.simpleFoam"
T0=$(date +%s); LAST_N=-1; LAST_CHANGE=$T0; LAST_PROG=$T0; CEIL_FIRED=0
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOG"; }
say "WATCH START case=$CASE derived_ceiling_s=$CEIL_S stall_s=$STALL_S  (NEVER KILLS)"
while true; do
  NOW=$(date +%s)
  if [ -f "$CASE/solve_rc" ]; then
    say "EXIT solve_rc=$(cat "$CASE/solve_rc") after $((NOW-T0)) s; watcher stopping."
    exit 0
  fi
  N=$(grep -c '^ExecutionTime' "$SL" 2>/dev/null || echo 0)
  if [ "$N" != "$LAST_N" ]; then LAST_N=$N; LAST_CHANGE=$NOW; fi
  if [ $((NOW-LAST_CHANGE)) -ge "$STALL_S" ]; then
    say "STALL no new iteration for $((NOW-LAST_CHANGE)) s at iteration $N. NOT KILLED -- the box has run heavily oversubscribed and a starved rank is not a dead one. ESCALATED."
    LAST_CHANGE=$NOW
  fi
  if [ "$CEIL_FIRED" = "0" ] && [ $((NOW-T0)) -ge "$CEIL_S" ]; then
    say "CEILING derived wall ceiling $CEIL_S s reached at iteration $N. THIS IS A REPORT TO THE cfd-SUPERVISOR, NOT A TERMINATION. The run continues."
    CEIL_FIRED=1
  fi
  if [ $((NOW-LAST_PROG)) -ge "$PROGRESS_S" ]; then
    E=$((NOW-T0))
    if [ "$N" -gt 0 ]; then
      say "PROGRESS iteration $N at $E s => $(echo "scale=3; $E/$N" | bc -l) s/iteration measured over the run so far (rate quoted WITH its timestamp; tonight's rates moved 2.4x in 40 min)."
    else
      say "PROGRESS no iterations yet at $E s."
    fi
    LAST_PROG=$NOW
  fi
  sleep 60
done
