#!/usr/bin/env bash
# =============================================================================
# VMFL063-R3 -- TERMINATE THE LADDER AFTER D0, BY SUPERVISOR RULING 2026-09-10.
#
# WHAT THIS IS NOT: it is not a gate change, a band change, a cap change or a
# label change, and it cannot make a failing row pass.  The frozen comparator
# refuses D0 either way -- grade_vmfl063_r3.py:671-673 raises SystemExit2 on
# `not (last_time < endTime)` ("reached endTime -- it ran out of clock and did
# NOT converge"), and :654 independently refuses a level that did not meet its
# own residualControl.  rc2 = NOT A RESULT, whether the ladder stops here or
# burns its whole cap first.  THE VERDICT IS IDENTICAL; ONLY THE COST DIFFERS.
#
# WHY: D0's residuals are in a SUSTAINED LIMIT CYCLE, measured by the
# supervisor from D0/log.simpleFoam and re-verified twice:
#     Ux parked at 2.64329659714e-06  (frozen residualControl U = 1e-09)
#     p  parked at 5.83603430443e-04  (frozen residualControl p = 1e-08)
#   bit-identical to 12 significant figures across iterations 28,001->44,001,
#   i.e. a FIXED POINT of the iteration map, 3-4 orders above tolerance.  It
#   will not reach residualControl by 100,000.  D0 is therefore certain to hit
#   its frozen endTime ceiling, which is exactly the outcome the pre-freeze
#   amendment anticipated: "a level hitting the ceiling without residualControl,
#   or a sustained limit cycle, is NOT A RESULT -- genuine non-convergence /
#   de-confined unsteadiness -- NEVER a widened band."
#
# WHY STOP AFTER D0 AND NOT NOW: the refusal must land on the comparator's
# DESIGNED limb (:671, "reached endTime"), not on the incidental no-End-line
# limb a mid-flight kill would trip.  The supervisor will not short-circuit his
# own frozen instrument to save $0.45.
#
# WHY STOP BEFORE D1: run_vmfl063_r3.sh:186-189 runs D0->D1->D2->D0_CONFINED
# UNCONDITIONALLY (a level that reaches endTime returns rc 0, so nothing stops
# the ladder but the CAP_CORE_MIN=4000 rc124 overrun).  D0 projects to ~910
# core-min; D1 ~1200; D2 (737k cells) ~1800.  D0+D1+D2 ~= 3,900 ~= the cap, so
# the ladder would rc124-stop BEFORE D0_CONFINED -- the whole cap spent, no
# control, and a verdict already determined at iteration 28,001.  D0 is required
# to build the LR/(2t) ladder, so its refusal sinks the row whatever D1/D2 do.
# AVOIDED WASTE ~3,000 core-min (~$2.57 DERIVED, not measured, at $0.0513/core-h;
# COMPUTE_BUDGET_CHARTER 5 and 6 -- waste is named, never absorbed).
#
# VMFL063-R4 IS OWED: test the de-confined-unsteadiness hypothesis properly, with
# a transient solver or with the confined control run FIRST rather than last.
#
# MECHANISM: every process in the ladder shares PGID 827496 (launcher 827496 ->
# driver 827501 -> subshell 827893 -> timeout 827894 -> simpleFoam 827895), so
# the group is signalled directly.  NO `pkill` PATTERN IS USED -- a pattern
# matches the killing shell's own command line, which has silently eaten a
# chained command in this lab before.
# =============================================================================
set -uo pipefail

RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL063-R3"
TRIGGER="$RUN_ROOT/RUN_RC.D0"
REC="$RUN_ROOT/TERMINATION_RECORD.txt"
PGID=827496
GUARD_PID=827496
POLL=60
MAX_WAIT_S=$((22*3600))          # D0 needs ~8.3 h; give it generous headroom

log(){ echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$REC"; }

# --- PID-REUSE GUARD: refuse to signal a group that is not OUR ladder --------
guard_ok(){
  local cl
  cl="$(tr '\0' ' ' < "/proc/$GUARD_PID/cmdline" 2>/dev/null)" || return 1
  case "$cl" in *VMFL063-R3*) return 0 ;; *) return 1 ;; esac
}

log "watcher START pid=$$ ppid=$PPID pgid_target=$PGID trigger=$TRIGGER"
if ! guard_ok; then
  log "REFUSE at start: pid $GUARD_PID is not the VMFL063-R3 launcher (gone, or reused). Killing NOTHING."
  exit 3
fi
log "guard OK: pid $GUARD_PID cmdline contains VMFL063-R3"

waited=0
while [ ! -f "$TRIGGER" ]; do
  if ! kill -0 "$GUARD_PID" 2>/dev/null; then
    log "ladder ended on its own before RUN_RC.D0 appeared (launcher $GUARD_PID gone). Killing NOTHING; autograder will grade what is on disk."
    exit 0
  fi
  sleep "$POLL"; waited=$((waited+POLL))
  if [ "$waited" -ge "$MAX_WAIT_S" ]; then
    log "REFUSE: RUN_RC.D0 did not appear within ${MAX_WAIT_S}s. Killing NOTHING -- a watcher that fires on a stale assumption is worse than one that does not fire."
    exit 3
  fi
done

log "TRIGGER: RUN_RC.D0 exists -- D0 has finished. Contents follow."
sed 's/^/    /' "$TRIGGER" >> "$REC" 2>/dev/null
LAST_T="$(grep -E '^Time =' "$RUN_ROOT/D0/log.simpleFoam" 2>/dev/null | tail -1)"
log "D0 final log line: ${LAST_T:-unavailable}"

if ! guard_ok; then
  log "REFUSE before signalling: pid $GUARD_PID no longer the VMFL063-R3 launcher. Killing NOTHING."
  exit 3
fi

log "SIGTERM to process group -$PGID (supervisor ruling: ladder terminated after D0)"
kill -TERM -"$PGID" 2>/dev/null
for i in $(seq 1 30); do kill -0 "$GUARD_PID" 2>/dev/null || break; sleep 2; done
if kill -0 "$GUARD_PID" 2>/dev/null; then
  log "still alive after 60s -- SIGKILL to process group -$PGID"
  kill -KILL -"$PGID" 2>/dev/null
  sleep 5
fi
if kill -0 "$GUARD_PID" 2>/dev/null; then
  log "ERROR: launcher $GUARD_PID STILL ALIVE after SIGKILL -- escalate, do not assume"
  exit 1
fi

log "ladder TERMINATED after D0. D1/D2/D0_CONFINED did NOT run, by ruling, not by failure."
log "EXPECTED VERDICT: NOT A RESULT (frozen comparator refuses D0 at :671 / :654). No gate, band, cap or label was touched."
log "Detached autograder 827346 now sees the driver gone and grades once."
log "watcher DONE"
exit 0
