#!/bin/bash
# AGGREGATE cost-cap watchdog for VMFL007 (CLAUDE.md rule 12).
# The frozen run_vmfl007.sh applies `timeout 3600` PER LEVEL; across three levels
# that is 180 core-min, not the 60 core-min cap the freeze names.  This process
# enforces the AGGREGATE cap at OS level.  It can only STOP; it never extends a
# budget, never edits the frozen script and never touches a result.  A lane cannot
# be a watcher (a watcher dies with the agent), so this is an OS process.
#
# CORRECTION 2026-08-25T16:58Z: the first arming watched the pid of `setsid`,
# which forks and exits immediately, so it saw a dead pid and exited within
# seconds.  It also signalled only ONE process group, which would have killed the
# launcher shell and LEFT simpleFoam RUNNING.  This version watches the real
# session leader and signals EVERY pid in the session.
set -u
SID="$1"; OUT="$2"; CAP_S="$3"; T0="$4"
while kill -0 "$SID" 2>/dev/null; do
  NOW=$(date +%s)
  if [ $((NOW - T0)) -ge "$CAP_S" ]; then
    PIDS=$(ps -eo pid,sid --no-headers | awk -v s="$SID" '$2==s {print $1}')
    { echo "CAP STOP at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      echo "elapsed_s = $((NOW - T0)); aggregate cap = ${CAP_S}s = 60 core-min at 1 rank"
      echo "CLAUDE.md rule 12: an overrun STOPS the run. It does not get a new budget."
      echo "Killed every pid in session $SID: $PIDS"
    } > "$OUT"
    for p in $PIDS; do kill -TERM "$p" 2>/dev/null; done
    sleep 15
    for p in $PIDS; do kill -KILL "$p" 2>/dev/null; done
    exit 0
  fi
  sleep 10
done
exit 0
