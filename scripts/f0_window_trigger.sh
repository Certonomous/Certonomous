#!/bin/bash
# F0 WINDOW TRIGGER -- fire the auto-stop liveness suite the instant this box has NO
# OpenFOAM solver running, and file the result. Then exit.
#
# WHY A DETACHED TRIGGER AND NOT A WATCHER
# ----------------------------------------
# Control F0 of scripts/test_auto_stop_liveness.py is "the identical binary under a
# NON-solver basename must NOT hold the box". Clause (1) of scripts/auto_stop_patched.sh
# reads the REAL /proc and cannot be sandboxed, so with any real solver live the script
# says ALIVE for a different reason and F0 discriminates nothing. Running it anyway would
# produce a green result that tests nothing -- the exact defect found in this suite on
# 2026-09-03, when it exited 0 having skipped all twelve IDLE halves.
#
# The window cannot be waited for by an agent: a watcher dies with the agent that spawned
# it (see the lab's own note on that failure mode), and the lane that wrote this will not
# outlive the window. So this is a plain detached OS process with a deadline.
#
# WHAT IT WILL NOT DO
# -------------------
#   * It NEVER runs the SOLVERS-emptied isolation variant. F0 passes there trivially,
#     because an empty SOLVERS list matches nothing by construction, and a control that
#     cannot fail is not a control. It runs the REAL, UNMODIFIED scripts/auto_stop_patched.sh.
#   * It REFUSES rather than reports if the no-solver condition is never established. A
#     deadline reached is not a result.
#   * It sends no signal to anything, touches no other team's files, and runs no sudo. The
#     suite it invokes exports AUTO_STOP_DRY_RUN=1 and shims every power command to a
#     tripwire, so it cannot stop the box.
#
# rc IS CAPTURED INSIDE THIS SCRIPT, never around the setsid line that launches it:
# `setsid timeout cmd` exits 0 for every outcome, so a caller reading the setsid parent's
# status learns nothing. The rc written to the artifact below is the suite's own.

set -u

REPO=/home/ubuntu/Certonomous
PATCH="$REPO/scripts/auto_stop_patched.sh"
SUITE="$REPO/scripts/test_auto_stop_liveness.py"
OUTDIR="$REPO/verification/runs/AUTOSTOP_LIVENESS"
LOCK="$OUTDIR/.f0_trigger.lock"

POLL_S=${POLL_S:-60}
DEADLINE_S=${DEADLINE_S:-28800}          # 8 h, then refuse rather than linger
QUIET_CONFIRMATIONS=${QUIET_CONFIRMATIONS:-3}   # consecutive quiet polls before firing

stamp() { date -u +%Y-%m-%dT%H%M%SZ; }
START=$(stamp)
OUT="$OUTDIR/F0_window_trigger_${START}.txt"

# One instance only. A second trigger would race the first for the same window and file
# two artifacts describing one reading.
exec 9>"$LOCK"
if ! flock -n 9; then
    echo "another F0 trigger already holds $LOCK -- exiting without firing" >&2
    exit 0
fi

# THE SOLVER LIST IS READ FROM THE REAL SCRIPT, NEVER RETYPED HERE. A list copied into
# this file would drift from the one clause (1) actually matches, and the drift would be
# silent -- which is the defect that put buoyantBoussinesqSimpleFoam (27 chars) outside a
# `pgrep -x` comm match for weeks.
SOLVERS=$(grep -m1 '^SOLVERS=' "$PATCH" | cut -d"'" -f2)
if [ -z "$SOLVERS" ]; then
    { echo "REFUSED $(stamp): could not read SOLVERS from $PATCH"
      echo "The condition cannot be established, so nothing is reported."; } > "$OUT"
    exit 1
fi

# Returns the first live solver found, or empty. Reads basename(/proc/PID/exe) -- the
# kernel-resolved binary, the same fact clause (1) matches on, not a command-line string.
live_solver() {
    local pid exe base s
    for pid in $(ls /proc 2>/dev/null | grep -E '^[0-9]+$'); do
        exe=$(readlink "/proc/$pid/exe" 2>/dev/null) || continue
        [ -n "$exe" ] || continue
        base=${exe##*/}
        for s in $SOLVERS; do
            if [ "$base" = "$s" ]; then echo "pid $pid is $base"; return 0; fi
        done
    done
    return 1
}

{
  echo "F0 WINDOW TRIGGER armed $START"
  echo "  waiting for: NO process whose basename(/proc/PID/exe) is in the REAL SOLVERS list"
  echo "  solver list read from $PATCH ($(echo "$SOLVERS" | wc -w) names)"
  echo "  poll ${POLL_S}s, deadline ${DEADLINE_S}s, ${QUIET_CONFIRMATIONS} consecutive quiet polls required"
  echo "  target: the REAL UNMODIFIED $PATCH (never the SOLVERS-emptied isolation variant)"
} > "$OUT"

t0=$(date +%s)
quiet=0
last_seen="(none yet)"
while :; do
    now=$(date +%s)
    if [ $(( now - t0 )) -ge "$DEADLINE_S" ]; then
        { echo
          echo "REFUSED $(stamp): deadline ${DEADLINE_S}s reached and the box was never quiet."
          echo "  last solver seen: $last_seen"
          echo "  F0 REMAINS PENDING. A deadline reached is not a result, and no suite run is"
          echo "  reported here, because a run taken against a contaminated box would test nothing."
        } >> "$OUT"
        exit 2
    fi
    if found=$(live_solver); then
        quiet=0
        last_seen="$found at $(stamp)"
    else
        quiet=$(( quiet + 1 ))
        echo "  quiet poll $quiet/$QUIET_CONFIRMATIONS at $(stamp)" >> "$OUT"
        if [ "$quiet" -ge "$QUIET_CONFIRMATIONS" ]; then
            break
        fi
    fi
    sleep "$POLL_S"
done

{
  echo
  echo "WINDOW OPEN at $(stamp) -- no live solver across $QUIET_CONFIRMATIONS consecutive polls."
  echo "Running the FULL suite against the real unmodified patch. With a quiet box every"
  echo "control runs, so F0 and all ten flip pairs are evaluated in BOTH directions."
  echo "================================================================================"
} >> "$OUT"

# rc captured HERE, inside the detached process, not from any setsid parent.
timeout 900 python3 "$SUITE" --script "$PATCH" >> "$OUT" 2>&1
RC=$?

{
  echo "================================================================================"
  echo "SUITE RC = $RC   (captured inside this script, at $(stamp))"
  case "$RC" in
    0) echo "VERDICT: every control behaved as pre-registered AND every pair was evaluated in"
       echo "  BOTH directions. F0 is WITNESSED. This converts the auto-stop patch's standing"
       echo "  verdict from GATE REACHED to a clean both-directions PASS on the real install"
       echo "  candidate. The grading of that upgrade is the supervisor's, not this script's." ;;
    3) echo "VERDICT: NOT WITNESSED -- a solver started during the run, so a half was skipped."
       echo "  F0 REMAINS PENDING. Re-arm the trigger for the next window." ;;
    1) echo "VERDICT: REFUSED -- a control landed off its pre-registered verdict, or an"
       echo "  evaluated pair did not flip. This is a finding about the PATCH and must be"
       echo "  triaged, not re-run away." ;;
    124) echo "VERDICT: the suite timed out at 900 s. NOT A RESULT." ;;
    *) echo "VERDICT: unexpected rc. NOT A RESULT until triaged." ;;
  esac
  echo "Artifact complete."
} >> "$OUT"
exit "$RC"
