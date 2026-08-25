#!/bin/bash
# OS-level contention sampler -- fires and WRITES THE SAMPLE ITSELF.
#
# WHY THIS EXISTS.  A lane cannot be a watcher: a watcher dies with the agent that
# armed it (L-5 addendum, landed by this team 2026-08-25).  A VMFL045-R2 lane
# reported "awaiting the L3 MIDPOINT event" twice and had already terminated both
# times.  The general form, which is worth carrying beyond monitors: A TASK MUST
# NEVER DEPEND ON AN AGENT BEING ALIVE AT A FUTURE INSTANT.  Either the work is
# done now, or an OS-level process does it, or it is recorded as NOT DONE.
#
# The midpoint is defined by SIMULATION TIME read from the solver's own log, not
# by a wall-clock guess -- so the sample is self-verifying: it records the sim
# time at which it actually fired.
#
# usage: contention_sampler.sh <CONTENTION.txt> <solver.log> <threshold_simtime> <label>
set -u
OUT="$1"; LOG="$2"; THRESH="$3"; LABEL="$4"
DEADLINE=$(( $(date +%s) + 7200 ))

emit() {  # $1 = heading, $2 = extra line
  { printf '\n--- %s --- %s\n' "$1" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'loadavg(1/5/15) = %s on %s cores\n' "$(cut -d' ' -f1-3 /proc/loadavg)" "$(nproc)"
    # ps ARGS, never comm: comm truncates at 15 chars, so buoyantBoussinesqSimpleFoam
    # reads "buoyantBoussine" and a grep for "Foam" MISSES IT (measured 2026-08-25).
    printf 'co-resident solvers (ps args, NOT comm -- comm truncates at 15 chars):\n'
    ps -eo pid,etimes,pcpu,args --sort=-pcpu \
      | grep -iE 'Foam|simpleFoam|rhoCentral' | grep -v grep \
      | sed 's/^/  /' | cut -c1-140
    [ -n "${2:-}" ] && printf '%s\n' "$2"
  } >> "$OUT"
}

# guarantee a trailing newline before appending: a file without one turns an
# append into a LINE CONTINUATION (measured on this lab's C-51 row).
[ -s "$OUT" ] && [ -n "$(tail -c1 "$OUT")" ] && printf '\n' >> "$OUT"

while :; do
  if [ ! -f "$LOG" ]; then sleep 5; [ "$(date +%s)" -gt "$DEADLINE" ] && break || continue; fi
  T=$(grep '^Time = ' "$LOG" 2>/dev/null | tail -1 | awk '{print $3}')
  if [ -n "$T" ] && awk -v a="$T" -v b="$THRESH" 'BEGIN{exit !(a+0>=b+0)}'; then
    emit "$LABEL" "fired at SIMULATION TIME = $T (threshold $THRESH), read from $LOG -- this
  sample is the MIDPOINT BY SIMULATION TIME, not a wall-clock estimate."
    exit 0
  fi
  if grep -q '^End$' "$LOG" 2>/dev/null; then
    emit "$LABEL -- MISSED" "THE RUN ENDED BEFORE THE THRESHOLD WAS OBSERVED. This sample DOES
  NOT EXIST and is recorded as MISSED. It must NOT be reconstructed from a later
  load average: later is not mid-run, and a reconstructed sample presented as a
  measurement is the defect this lab spent 2026-08-25 removing."
    exit 1
  fi
  [ "$(date +%s)" -gt "$DEADLINE" ] && { emit "$LABEL -- MISSED (sampler deadline)" \
    "Sampler hit its 2 h deadline without observing the threshold. Recorded as MISSED."; exit 1; }
  sleep 10
done
emit "$LABEL -- MISSED (no log)" "Solver log never appeared. Recorded as MISSED."
exit 1
