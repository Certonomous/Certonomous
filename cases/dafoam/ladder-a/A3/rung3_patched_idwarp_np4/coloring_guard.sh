#!/usr/bin/env bash
# coloring_guard.sh -- the WIRED colouring-cache stop for the A3 rung-3 patched-IDWarp arm.
#
# The cost basis registered in PREREGISTRATION.md section 8 is a WARM-CACHE basis: the rung-1
# shipped fd3 arm read dRdWColoring_4.bin and did not build it. If an arm rebuilds the colouring,
# that basis is void, the arm is no longer cost-comparable with the shipped row, and it is no longer
# reading the identical colouring the shipped row read. This script kills such an arm immediately
# rather than letting it grade against a void basis.
#
# DISCRIMINATOR, and it is the non-obvious part: a REBUILD also prints a "Reading Coloring" line
# afterwards (rung 2 verified this in an archived log). So the discriminator is the PRESENCE of
# "Calculating dRdW Coloring", never the absence of "Reading Coloring".
#
# Adapted from the proven rung-2 instrument
# /home/ubuntu/certonomous-runs/P3-a3-rung2-patched/coloring_watchdog.sh, generalised to take its
# cache name and expected colour count as arguments and given a --no-kill single-pass selftest mode.
#
# Usage: coloring_guard.sh <container> <logpath> <cachename> <colours> <root> <arm> [--no-kill]
# Exit:  0 = cache READ confirmed, expected colour count seen  (arm proceeds)
#        3 = REBUILD detected, container killed                (arm is NOT A RESULT -- void basis)
#        5 = cache read but the COLOUR COUNT differs           (arm killed; not the same colouring)
#        7 = neither signature reachable (container gone / single pass found nothing)
#        2 = usage wrong
set -u

if [ "$#" -lt 6 ]; then
  echo "usage: coloring_guard.sh <container> <log> <cachename> <colours> <root> <arm> [--no-kill]" >&2
  exit 2
fi
NAME="$1"; LOG="$2"; CACHE="$3"; COLOURS="$4"; ROOT="$5"; ARM="$6"; NOKILL="${7:-}"
OUT="$ROOT/coloring_guard_${ARM}.log"
SINGLE=0; [ "$NOKILL" = "--no-kill" ] && SINGLE=1

kill_arm() {
  if [ "$SINGLE" = "1" ]; then
    echo "$(date -u +%FT%TZ) NO_KILL (selftest) -- would have killed $NAME" >> "$OUT"
  else
    sudo -n docker kill "$NAME" >/dev/null 2>&1
  fi
}

echo "# coloring_guard armed $(date -u +%FT%TZ) container=$NAME cache=$CACHE expect_colours=$COLOURS single_pass=$SINGLE" >> "$OUT"
seen_container=0

for _ in $(seq 1 20000); do
  if [ -f "$LOG" ]; then
    if grep -q "Calculating dRdW Coloring" "$LOG" 2>/dev/null; then
      {
        echo "$(date -u +%FT%TZ) GUARD FIRED: arm $ARM is REBUILDING the colouring, not reading $CACHE."
        grep -nE "Checking if Coloring file exists|Reading Coloring|Calculating dRdW Coloring" "$LOG"
        echo "The warm-cache cost basis in PREREGISTRATION.md section 8 is VOID. Killing the arm."
      } >> "$OUT"
      touch "$ROOT/COLORING_REBUILD_DETECTED.${ARM}"
      kill_arm
      exit 3
    fi
    if grep -q "Reading Coloring ${CACHE}" "$LOG" 2>/dev/null; then
      SEEN=$(grep -m1 -oE 'dRdWTPC: 0 of [0-9]+' "$LOG" | grep -oE '[0-9]+$' || true)
      if [ -n "${SEEN:-}" ] && [ "$SEEN" != "$COLOURS" ]; then
        echo "$(date -u +%FT%TZ) GUARD FIRED: colour count $SEEN != registered $COLOURS. Not the same colouring. Killing." >> "$OUT"
        touch "$ROOT/COLORING_COUNT_MISMATCH.${ARM}"
        kill_arm
        exit 5
      fi
      if [ -n "${SEEN:-}" ]; then
        echo "$(date -u +%FT%TZ) cache READ confirmed, no rebuild, colours=$SEEN as registered." >> "$OUT"
        exit 0
      fi
    fi
  fi

  if [ "$SINGLE" = "1" ]; then
    echo "$(date -u +%FT%TZ) single pass: neither signature decided on $LOG" >> "$OUT"
    exit 7
  fi

  if sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$NAME"; then
    seen_container=1
  elif [ "$seen_container" = "1" ]; then
    if [ -f "$LOG" ] && grep -q "Reading Coloring ${CACHE}" "$LOG" 2>/dev/null; then exit 0; fi
    echo "$(date -u +%FT%TZ) container gone before a colouring signature appeared." >> "$OUT"
    exit 7
  fi
  sleep 5
done
exit 7
