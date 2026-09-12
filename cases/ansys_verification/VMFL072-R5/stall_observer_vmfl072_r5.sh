#!/usr/bin/env bash
# =============================================================================
# VMFL072-R5 STALL OBSERVER  --  IT OBSERVES. IT NEVER KILLS.
# =============================================================================
# DRAFTED by an `ansys-lane-opus48` lane for the `ansys-verification-supervisor`,
# 2026-09-12. NOT COMMITTED, NOT LAUNCHED by the drafting lane. Modelled on the
# proven cases/ansys_verification/VMFL078/stall_observer_vmfl078.sh.
#
# WHY: Sanaa's directive ~2026-09-12T01:10Z -- verbatim "dont forget i dont want
# any cap on any run, and that i bumped the volume to 1000 gib" -- and the
# supervisor's ruling of the same date: NO CAP MAY KILL A RUN. A run that may not
# be stopped for spending must still be WATCHED, because a silently hung solver
# is indistinguishable from a slow one until somebody looks.
#
#   *** THIS SCRIPT SENDS NO SIGNAL. IT CONTAINS NO `kill`, NO `pkill`, NO
#   *** `timeout`. ITS ONLY EFFECTS: (1) append a line to its own log, and
#   *** (2) write a marker file. A human or the supervisor decides what happens.
#
# The core-minute figures in PREREGISTRATION.md sec.6 are CALIBRATION PREDICTIONS,
# NOT cap-stops. Rule 12's costing/calibration duty survives the no-cap directive
# in full; the exemption withdraws the GATE, not the ARITHMETIC. Nothing here may
# be re-armed as a stop.
#
# USAGE:  ./stall_observer_vmfl072_r5.sh <run_root> [stall_s] [run_rc_path] [poll_s]
#   e.g.  setsid ./stall_observer_vmfl072_r5.sh "$RUN_ROOT" 600 "$RUN_ROOT/RC.txt" 30 \
#           >/dev/null 2>&1 &
# =============================================================================
# NO `set -u`: sourcing OpenFOAM's bashrc dereferences unbound vars; but this
# observer sources nothing, so the risk does not arise here. Kept off for
# symmetry with the launcher's rule and so a future edit that adds a source
# cannot be silently killed by `set -u` before a marker is written.

OUT="${1:?usage: stall_observer_vmfl072_r5.sh <run_root> [stall_s] [run_rc_path] [poll_s]}"

# --- THE INTERVAL, AS A NUMBER, WITH ITS ARITHMETIC (PREREGISTRATION.md sec.6) -
# STALL_S = 600 s (10 min) with no new `^Time = ` line in log.reactingParcelFoam.
# The smoke measured ~0.037 CPU-s/step on R5's own 65,536-cell mesh at loadavg
# ~77 (4.8x oversubscribed). Even at a 5x further contention inflation a step is
# O(0.2 s); 600 s is ~3000x a contended step -- far too long to false-fire on a
# merely slow solver, short enough that a genuine hang is named within 10 min.
STALL_S="${2:-600}"
RUN_RC="${3:-}"
POLL_S="${4:-30}"

LOG="$OUT/log.reactingParcelFoam"
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
  # Terminal conditions: the launcher recorded a completion state, or the solver
  # wrote End. Either ends the observer -- it does not outlive the solve.
  if [ -n "$RUN_RC" ] && [ -f "$RUN_RC" ] && grep -qE '^(state = FINISHED|rc = )' "$RUN_RC" 2>/dev/null; then
    say "observer END: launcher recorded a completion record in $RUN_RC"; exit 0
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
    if [ "$fired" -eq 1 ]; then
      say "RECOVERED: Time lines advanced to $n after a stall was reported; marker left as a record"
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
        printf 'run_root       = %s\n' "$OUT"
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
