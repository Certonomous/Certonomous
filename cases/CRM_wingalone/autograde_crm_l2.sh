#!/bin/bash
# CRM WING-ALONE L2, M=0.85 -- GRADE ON THE RUN'S OWN rc, ON THE REGISTERED GATES.
#
# IT HAS NO KILL PRIMITIVE AND NO CAP.  Sanaa has ruled FOUR times that no run is stopped
# by clock or by budget.  This watcher READS.  It never signals, never stops, never
# touches another team's process.  If it is wrong about anything, the run keeps going.
#
# rc IS CAPTURED INSIDE THIS WRAPPER.  `setsid timeout cmd` exits 0 for every outcome, so
# the rc of the thing that matters is captured here, at the point of the call, never around
# the setsid line.
#
# THE TRIGGER IS THE RUN'S OWN rc.  launch_crm_l2.sh writes $CASE/solve_rc on EVERY exit
# path (success, solver failure, BLOCKED-on-memory, BLOCKED-on-S5).  This waits on that file.
#
# LAUNCHER IDENTITY, NOT ITS PID NUMBER.  Linux recycles pids.  The launcher counts as gone
# only when /proc/<pid> is absent OR its cwd is no longer this case OR its cmdline is no
# longer the launcher -- all three read in the SAME iteration, never a bare `-d /proc/<pid>`
# and never a pattern match against a process list (L-559: the pattern matches the shell
# that typed it).
#
# BOOKKEEPING NEVER VOIDS PHYSICS.  If the launcher dies without writing an rc but the
# solver log carries End, the run is graded anyway and the missing rc is reported as a
# G-S4 clause failure -- a fact about the bookkeeping, printed, not hidden and not fatal.
set -u
CASE="$1"; LPID="$2"; GRADER="$3"
LOG="$CASE/AUTOGRADE.log"
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOG"; }

say "ARMED case=$CASE launcher_pid=$LPID grader=$GRADER"
say "grader sha256=$(sha256sum "$GRADER" | cut -d' ' -f1)"
say "TRIGGER = \$CASE/solve_rc (the run's OWN rc). NO CAP, NO CLOCK TRIGGER, NO KILL PRIMITIVE."

N=0
while [ ! -f "$CASE/solve_rc" ]; do
  ALIVE=0
  if [ -d "/proc/$LPID" ]; then
    CWD=$(readlink "/proc/$LPID/cwd" 2>/dev/null || echo "")
    CMD=$(tr '\0' ' ' < "/proc/$LPID/cmdline" 2>/dev/null || echo "")
    if [ "$CWD" = "$CASE" ]; then
      case "$CMD" in *launch_crm_l2.sh*) ALIVE=1 ;; esac
    fi
  fi
  if [ "$ALIVE" -eq 0 ]; then
    say "LAUNCHER $LPID IS GONE BY IDENTITY and no solve_rc was written."
    if grep -q '^End' "$CASE/log.rhoSimpleFoam" 2>/dev/null; then
      say "BUT the solver log carries End. Bookkeeping never voids physics: GRADING ANYWAY."
    else
      say "The solver log carries no End either. Grading what exists; G-S4 will say so."
    fi
    break
  fi
  N=$((N+1))
  if [ $((N % 20)) -eq 1 ]; then
    IT=$(grep -c '^ExecutionTime' "$CASE/log.rhoSimpleFoam" 2>/dev/null || echo 0)
    say "WAITING reading=$N launcher alive by identity; iteration $IT of 4000. Not signalling."
  fi
  sleep 60
done

[ -f "$CASE/solve_rc" ] && say "SOLVE rc FILE PRESENT: $(cat "$CASE/solve_rc")"
say "GRADING NOW on the registered §7 gates."

# rc CAPTURED INSIDE THIS WRAPPER, at the point of the call.
python3 "$GRADER" "$CASE" > "$CASE/AUTOGRADE.stdout" 2>&1
GRC=$?
echo "$GRC" > "$CASE/grade_rc"
say "GRADER EXITED rc=$GRC (0 PASS | 1 GATE FAIL | 2 REFUSED | 3 NOT A RESULT)"
if [ -f "$CASE/VERDICT.crm_l2" ]; then
  say "VERDICT: $(grep '^OVERALL=' "$CASE/VERDICT.crm_l2" | cut -d= -f2)"
  while read -r l; do say "  $l"; done < "$CASE/VERDICT.crm_l2"
else
  say "NO VERDICT FILE WRITTEN -- the grader did not reach its own footer. See AUTOGRADE.stdout."
fi
say "DONE. Nothing was signalled and nothing was stopped."
exit "$GRC"
