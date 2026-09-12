#!/usr/bin/env bash
# =============================================================================
# VMFL078 STALL OBSERVER  --  IT OBSERVES. IT NEVER KILLS.
# =============================================================================
# DRAFTED by an `ansys-lane-opus` lane for the `ansys-verification-supervisor`,
# 2026-09-12. NOT COMMITTED, NOT LAUNCHED by the drafting lane.
#
# WHY THIS EXISTS, IN ONE SENTENCE: Sanaa's directive of ~2026-09-12T01:10Z --
# verbatim, "dont forget i dont want any cap on any run, and that i bumped the
# volume to 1000 gib" -- forbids a budget gate from stopping a run, and the
# supervisor's ruling of the same date is that NO CAP MAY KILL A RUN. A run that
# may not be stopped for spending still has to be WATCHED, because a silently
# hung solver is indistinguishable from a slow one until somebody looks.
#
#   *** THIS SCRIPT SENDS NO SIGNAL AND CONTAINS NO `kill`, NO `pkill`, AND NO
#   *** `timeout`. ITS ONLY EFFECTS ARE: (1) APPEND A LINE TO ITS OWN LOG, AND
#   *** (2) WRITE A MARKER FILE. A HUMAN OR THE SUPERVISOR DECIDES WHAT HAPPENS.
#
# RELATIONSHIP TO COST (CLAUDE.md rule 12): every core-minute figure in
# `PREREGISTRATION.md` sec.7 -- the 383 core-min central estimate, the 88-1,010
# band, and the 1,148 "3x reference" figure -- is a CALIBRATION PREDICTION AND
# NOT A CAP-STOP. Rule 12's costing duty survives the no-cap directive in full:
# the run is costed, and the estimate is compared against the actual at
# completion in `docs/COST_CALIBRATION.md`. The exemption withdraws the GATE, not
# the ARITHMETIC. NOTHING IN THIS FILE OR IN THAT SECTION MAY BE RE-ARMED AS A
# STOP, and this paragraph is here so that nobody re-arms them by mistake.
#
# USAGE:  ./stall_observer_vmfl078.sh <level_out_dir> [stall_s] [run_rc_path] [poll_s]
#   e.g.  setsid ./stall_observer_vmfl078.sh "$OUT" 900 "$RUN_ROOT/RUN_RC.$L" 60 \
#           >/dev/null 2>&1 &
#
# NOTE ON <run_rc_path>: the launcher writes its per-level completion record to
# `$RUN_ROOT/RUN_RC.$L`, NOT to a file inside the level directory. Pass it
# explicitly. If it is omitted the observer still terminates correctly on the
# solver's own `End` line -- it simply loses the earlier of its two exits.
# =============================================================================
set -u

OUT="${1:?usage: stall_observer_vmfl078.sh <level_out_dir> [stall_seconds] [run_rc_path]}"

# --- THE INTERVAL, AS A NUMBER, WITH ITS ARITHMETIC -------------------------
# STALL_S = 900 s (15 min) with no new `^Time = ` line in log.simpleFoam.
#
# Why 900 and not something tighter: the registered PESSIMISTIC rate is
# 2.9e-06 s/cell/iter (PREREGISTRATION.md sec.7, measured on this case's own L1
# mesh at box loadavg ~18). At L3 = 1,048,576 cells over RANKS = 4 that is
#   2.9e-06 * 1048576 / 4 = 0.76 s per iteration at the load it was measured at.
# This box has been observed at loadavg 77 on 16 cores (4.8x oversubscribed), so
# allow a 5x contention inflation: ~3.8 s per iteration. 900 s is therefore
# ~237x the pessimistic contended iteration time -- far too long to false-fire on
# a merely slow solver, and short enough that a genuine hang is named within a
# quarter of an hour instead of at the next human glance.
STALL_S="${2:-900}"
RUN_RC="${3:-}"
# POLL_S is the sampling cadence only -- it changes how promptly a stall is
# NOTICED, never whether anything is stopped. Settable so the control below can
# drive it in seconds instead of quarter-hours.
POLL_S="${4:-60}"

LOG="$OUT/log.simpleFoam"
OBS="$OUT/STALL_OBSERVER.log"
MARK="$OUT/STALL_MARKER.txt"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
say() { echo "$(ts) $*" >> "$OBS"; }

say "observer START pid=$$ ppid=$PPID stall_s=$STALL_S poll_s=$POLL_S log=$LOG run_rc=${RUN_RC:-<not supplied>}"
say "THIS OBSERVER NEVER KILLS. It appends to this log and may write $MARK. Nothing else."

last_count=-1
last_change=$(date -u +%s)
fired=0

while :; do
  # Terminal conditions: the launcher's own per-level record says FINISHED, or
  # the solver wrote End. Either way the observer's job is over -- it does not
  # outlive the solve and it does not poll forever.
  if [ -n "$RUN_RC" ] && [ -f "$RUN_RC" ] && grep -q '^state = FINISHED' "$RUN_RC" 2>/dev/null; then
    say "observer END: launcher recorded state = FINISHED in $RUN_RC"; exit 0
  fi
  if [ -f "$LOG" ] && grep -qE '^End$' "$LOG" 2>/dev/null; then
    say "observer END: solver log carries an End line"; exit 0
  fi

  if [ -f "$LOG" ]; then
    n="$(grep -cE '^Time = ' "$LOG" 2>/dev/null || echo 0)"
  else
    n=0
  fi
  now=$(date -u +%s)

  if [ "$n" -ne "$last_count" ]; then
    # progress: reset the clock, and re-arm so a second stall is reported too
    if [ "$fired" -eq 1 ]; then
      say "RECOVERED: Time lines advanced to $n after a stall was reported; marker left in place as a record"
      fired=0
    fi
    last_count="$n"
    last_change="$now"
  else
    idle=$(( now - last_change ))
    if [ "$idle" -ge "$STALL_S" ] && [ "$fired" -eq 0 ]; then
      fired=1
      last_time="$(grep -E '^Time = ' "$LOG" 2>/dev/null | tail -1 | sed -E 's/^Time = //')"
      {
        printf 'STALL OBSERVED -- THIS IS AN ESCALATION, NOT A STOP\n'
        printf 'utc            = %s\n' "$(ts)"
        printf 'level_out      = %s\n' "$OUT"
        printf 'log            = %s\n' "$LOG"
        printf 'idle_s         = %d\n' "$idle"
        printf 'stall_s        = %d\n' "$STALL_S"
        printf 'Time_lines     = %s\n' "$n"
        printf 'last_Time      = %s\n' "${last_time:-none}"
        printf 'action_taken   = NONE. No signal was sent. The solver is untouched and still running.\n'
        printf 'what_this_is   = the solver has written no new `Time =` line for at least %d s.\n' "$STALL_S"
        printf 'what_this_isNOT= a cap, a budget gate, or a verdict. It gates nothing and grades nothing.\n'
        printf 'who_decides    = the ansys-verification-supervisor. A stall is a FINDING until triage says otherwise.\n'
      } > "$MARK"
      say "STALL: no new Time line for ${idle}s (>= ${STALL_S}s). Marker written to $MARK. NO SIGNAL SENT."
    fi
  fi

  sleep "$POLL_S"
done
