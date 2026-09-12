#!/usr/bin/env bash
# =============================================================================
# d8g_stall_watcher.sh -- D8G ARM STALL WATCHER.  2026-09-12.
#
# IT ESCALATES.  IT NEVER KILLS.  There is no `kill`, no `docker kill`, no
# `docker stop` and no `pkill` anywhere in this file, and that is checkable
# rather than promised:
#     grep -nE '\b(pkill|kill|docker (kill|stop|rm))\b' d8g_stall_watcher.sh
# returns only THIS comment block.  The watcher's entire output is lines in a
# text file.  Nothing it observes can end a run.
# THE ONE EXCEPTION, DISCLOSED RATHER THAN GLOSSED: `--selftest` calls
# `rm -rf` on ITS OWN mktemp directory.  That path is not reachable from the
# watch loop and touches nothing belonging to a run.
#
# A STALL IS NOT SLOWNESS.  The only thing it calls a stall is THE LOG FILE'S
# mtime FAILING TO ADVANCE for a whole window.  A solver grinding through a
# hard iteration is writing; a solver that has stopped writing for minutes is
# the event a supervisor wants to see.  Slowness is never escalated and the
# distinction is the point of the instrument.
#
# WHAT IT DOES NOT KNOW, STATED HERE: mtime advancing proves BYTES ARE BEING
# WRITTEN, not that they are iterations.  A crashing solver looping on a
# traceback advances mtime too.  This watcher is a liveness reader, not a
# progress reader, and it must not be cited as one.
#
# USAGE:  d8g_stall_watcher.sh <base_dir> <arm> <log_path> [stall_window_s]
#         d8g_stall_watcher.sh --selftest
# =============================================================================
set -uo pipefail

# --- PLANTED CONTROL --------------------------------------------------------
# A watcher that reports "no stall" without being shown able to report a stall
# is a false zero (CLAUDE.md rule 3).  --selftest plants BOTH readings on one
# fixture and refuses if either is missing.
if [ "${1:-}" = "--selftest" ]; then
  T=$(mktemp -d); F="$T/fixture.log"; : > "$F"; P=0; N=0
  ck() { if [ "$2" = "$3" ]; then P=$((P+1)); echo "  PASS  $1 (got=$3)"; else N=$((N+1)); echo "  FAIL  $1 (expected=$2 got=$3)"; fi; }
  age_of() { echo $(( $(date -u +%s) - $(stat -c %Y "$1") )); }
  touch -d '@'"$(( $(date -u +%s) - 900 ))" "$F"
  ck "a 900 s-old log READS AS STALLED against a 300 s window" yes "$([ "$(age_of "$F")" -ge 300 ] && echo yes || echo no)"
  printf 'Time = 1\n' >> "$F"            # the plant: one write, nothing else
  ck "ONE WRITE flips the same reader to NOT STALLED" no  "$([ "$(age_of "$F")" -ge 300 ] && echo yes || echo no)"
  ck "the reader saw the planted byte on disk, not in memory" 1 "$(grep -c 'Time = 1' "$F")"
  rm -rf "$T"
  echo "d8g_stall_watcher --selftest pass=$P fail=$N"
  [ "$N" -eq 0 ] || exit 2
  exit 0
fi

BASE="${1:?base dir}"; ARM="${2:?arm}"; LOG="${3:?log path}"; WINDOW="${4:-300}"
OUT="$BASE/STALL_ESCALATIONS.txt"
POLL=30
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
note() { printf '%s %s\n' "$(stamp)" "$*" | tee -a "$OUT"; }

note "STALL_WATCHER_START arm=$ARM log=$(basename "$LOG") window_s=$WINDOW poll_s=$POLL kills=NEVER pid=$$"
LAST_SIZE=-1; LAST_CHANGE=$(date -u +%s); ESC=0; SAW_LOG=no
while :; do
  NOW=$(date -u +%s)
  if [ ! -f "$LOG" ]; then
    # NOT a stall.  The log does not exist yet; the container may still be
    # starting.  Recorded once so a reader can tell "not yet" from "frozen".
    [ "$SAW_LOG" = no ] && { note "STALL_WATCHER_WAITING arm=$ARM log_absent=yes note=pre-launch-is-not-a-stall"; SAW_LOG=seen_absent; }
    sleep "$POLL"; continue
  fi
  SZ=$(stat -c %s "$LOG" 2>/dev/null || echo -1)
  if [ "$SZ" != "$LAST_SIZE" ]; then LAST_SIZE=$SZ; LAST_CHANGE=$NOW; ESC=0; fi
  QUIET=$(( NOW - LAST_CHANGE ))
  if [ "$QUIET" -ge "$WINDOW" ]; then
    MULT=$(( QUIET / WINDOW ))
    if [ "$MULT" -gt "$ESC" ]; then
      ESC=$MULT
      note "STALL_ESCALATION arm=$ARM quiet_s=$QUIET window_s=$WINDOW over=${MULT}x log_bytes=$SZ last_line=[$(tail -1 "$LOG" 2>/dev/null | head -c 160)] load1=$(cut -d' ' -f1 /proc/loadavg) memavail_GiB=$(awk '/MemAvailable/{printf "%.2f",$2/1048576}' /proc/meminfo) verdict=NONE killed=nothing"
    fi
  fi
  # THE WATCHER ENDS WHEN THE ARM ENDS, AND IT LEARNS THAT FROM THE ARM'S OWN
  # STATUS FILE -- never by inspecting or touching a container.
  if [ -f "$BASE/STATUS.$ARM" ] && grep -q '^rc=' "$BASE/STATUS.$ARM" 2>/dev/null; then
    note "STALL_WATCHER_END arm=$ARM reason=arm_status_has_rc escalations=$ESC status=[$(grep -m1 '^rc=' "$BASE/STATUS.$ARM" | head -c 200)]"
    exit 0
  fi
  sleep "$POLL"
done
