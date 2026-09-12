#!/bin/bash
# DRIVAER R2b probe C2 -- DURABLE DETACHED WAIT-AND-GRADE for the layer probe.
#
# WHY THIS EXISTS.  C2's mesh build (RUN_C2.sh, wrapper under ppid 1) was launched by an
# agent session that has since died, and NOTHING was armed on its rc.  A probe that lands
# and is never graded is compute spent for nothing.  This script lives under the CASE
# directory, writes every artifact BESIDE THE RUN, and runs under setsid so it outlives
# the agent that armed it.  The scratchpad is temp only and is NEVER a handoff channel
# (CLAUDE.md rule 13 / L-186); nothing here touches it.
#
# IT KILLS NOTHING.  No clock cap, no spend cap, no kill primitive, no signal of any
# kind -- Sanaa has ruled four times that nothing may stop on spend or clock.
# MemAvailable is OBSERVED AND LOGGED ONLY.
#
# IT NEVER TOUCHES ANOTHER TEAM'S PROCESS.  The probe wrapper is identified by
# /proc/<pid>/cmdline AND the run path it carries, RE-CONFIRMED ON EVERY POLL
# (L-559: a pattern match tells you WHAT, never WHOSE, and matches the shell that typed
# it).  If the identity stops matching, this script STOPS WATCHING AND EXITS.  It does
# not signal and it does not grade a run it can no longer prove it was watching.
#
# rc IS CAPTURED INSIDE THIS WRAPPER, never around a setsid line -- `setsid timeout cmd`
# exits 0 for every outcome.  The PROBE's rc is NOT invented here: it is read from
# $ROOT/RUN_RC, which RUN_C2.sh writes LAST, AFTER the measurement (its §6.2 fix of the
# C1 race).  If RUN_RC never appears, this script says so and lets grade_c2_exits.py
# REFUSE.  It writes no file matching RUN_C2.sh's rc name, so it cannot fabricate a
# completion, and it never chooses a branch on an absent measurement.
#
# usage: watch_grade_c2.sh <RUN_DIR> <WRAPPER_PID>
set -u
ROOT="$1"; WPID="$2"
REPO=/home/ubuntu/Certonomous
GRADER="$REPO/cases/navier_class/DRIVAER/grade_c2_exits.py"
LOG="$ROOT/C2_WATCH.log"
POLL=30
RC_WAIT_S=3600

say () { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" >> "$LOG"; }
finish () { printf 'watcher_rc=%s\n' "$1" > "$ROOT/C2_WATCH_RC.txt"; exit "$1"; }

[ -d "$ROOT" ]      || { echo "no such run root $ROOT"; exit 2; }
[ -f "$GRADER" ]    || { echo "no grader at $GRADER"; exit 2; }
say "WATCH START root=$ROOT wrapper_pid=$WPID grader=$GRADER"

# ---- identity, asserted before anything and re-asserted on every poll -------------
# The wrapper's cwd is the REPO, not the run dir, so cwd alone cannot identify it.
# It is identified by BOTH markers its cmdline must carry: the script name AND the
# run path.  Both are read in the SAME invocation as the decision that uses them.
identity_ok () {
  local cmd
  cmd=$(tr '\0' ' ' < "/proc/$1/cmdline" 2>/dev/null) || return 1
  case "$cmd" in *RUN_C2.sh*) ;; *) return 2 ;; esac
  case "$cmd" in *"$ROOT"*) ;; *) return 3 ;; esac
  return 0
}
identity_ok "$WPID"; rc=$?
if [ $rc -ne 0 ]; then
  if [ -f "$ROOT/RUN_RC" ]; then
    say "wrapper $WPID is gone but RUN_RC is already on disk -- the probe finished before this watcher was armed. Proceeding straight to grading."
  else
    say "REFUSE: pid $WPID does not carry RUN_C2.sh and $ROOT in its cmdline (code $rc), and no RUN_RC exists. NOTHING WATCHED, NOTHING SIGNALLED, NOTHING GRADED."
    finish 4
  fi
else
  say "IDENTITY CONFIRMED: /proc/$WPID/cmdline carries RUN_C2.sh and $ROOT"
  # ---- wait for the probe.  Observe only. ----------------------------------------
  n=0
  while :; do
    if [ -f "$ROOT/RUN_RC" ]; then say "RUN_RC appeared"; break; fi
    if [ ! -d "/proc/$WPID" ]; then say "WRAPPER PID $WPID GONE"; break; fi
    identity_ok "$WPID"; rc=$?
    if [ $rc -ne 0 ]; then
      say "IDENTITY LOST on pid $WPID (code $rc) -- the pid was recycled or is no longer this probe. STOPPING. No signal sent, no grade attempted."
      finish 5
    fi
    n=$((n+1))
    if [ $((n % 20)) -eq 1 ]; then
      st=$(grep -E '^(Layer mesh|Snapped mesh|Morph iteration|Added layer)' "$ROOT/log.snappyHexMesh" 2>/dev/null | tail -1)
      ma=$(awk '/^MemAvailable:/{printf "%.2f", $2/1048576}' /proc/meminfo)
      say "alive: snappy=[${st}] MemAvailable=${ma}GiB (OBSERVED ONLY -- this script stops nothing)"
    fi
    sleep $POLL
  done
fi

# ---- RUN_RC, written LAST by RUN_C2.sh.  Not invented here. -----------------------
waited=0
while [ ! -f "$ROOT/RUN_RC" ] && [ $waited -lt $RC_WAIT_S ]; do
  if [ ! -d "/proc/$WPID" ] && [ $waited -gt 300 ]; then
    say "WRAPPER $WPID gone and no RUN_RC after ${waited}s"
    break
  fi
  sleep 15; waited=$((waited+15))
done
if [ -f "$ROOT/RUN_RC" ]; then
  say "RUN_RC present: $(tr -d '\n' < "$ROOT/RUN_RC") (written by RUN_C2.sh AFTER its measurement)"
else
  say "NO RUN_RC. RUN_C2.sh writes it last, after the measurement; it never appeared and the wrapper is gone. The probe's exit status is UNKNOWN to this lab and is NOT invented. grade_c2_exits.py will REFUSE, and that refusal is the correct outcome."
  cat > "$ROOT/C2_RUN_RC_MISSING.txt" <<TXT
NO RUN_RC at $(date -u +%FT%TZ).
RUN_C2.sh writes \$R/RUN_RC as its LAST action, after run_build.sh, writeCellCentres and
stage_r2_measure.py.  It did not appear within ${RC_WAIT_S}s of the wrapper disappearing.
The probe's exit status is therefore UNKNOWN.  It is NOT guessed here.  C2 is BLOCKED on
completion -- not PASS, not GATE FAIL, and NO registered exit is declared fired.
TXT
fi

# ---- grade.  rc captured here. ---------------------------------------------------
say "grading: $GRADER $ROOT"
python3 "$GRADER" "$ROOT" > "$ROOT/C2_EXIT_VERDICT.out" 2>&1
grc=$?
say "grade_c2_exits.py exit rc=$grc (0=verdict produced, 2=REFUSED, 70=internal defect)"
say "$(grep -m1 -E '^(verdict=|REFUSED)' "$ROOT/C2_EXIT_VERDICT.out" 2>/dev/null)"
say "WATCH DONE grade_rc=$grc"
finish $grc
