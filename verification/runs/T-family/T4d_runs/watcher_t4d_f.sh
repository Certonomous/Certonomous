#!/usr/bin/env bash
# OS-level watcher for the T4d FINE launch (T4d_IJ_f only). Same pattern as
# watcher_t4d.sh (which is hardcoded to c+m). Detached via setsid so it survives
# the launching agent. Logs pid/iteration/rate/ETA/box load every 5 min to
# WATCH_t4d_f.log. Self-exits when STATUS.T4d_IJ_f appears or after MAX_S.
set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SELF/WATCH_t4d_f.log"
INTERVAL=300
MAX_S=655200          # fine cap is 649440 s; watcher self-terminates just after
ENDT=64000
CD="$SELF/T4d_IJ_f"
PREV_IT=0; PREV_T=0

iter_of() { grep -aE "^Time = " "$1" 2>/dev/null | tail -1 | sed 's/^Time = //' | tr -d '[:space:]'; }
pid_of()  { pgrep -f "buoyantBoussinesqSimpleFoam -case $CD\$" 2>/dev/null | head -1; }

T_START=$(date +%s)
echo "=== T4d FINE watcher started $(date -u +%Y-%m-%dT%H:%M:%SZ) pid=$$ interval=${INTERVAL}s ===" >> "$LOG"
while :; do
  NOW=$(date +%s)
  STAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  LOAD=$(cut -d' ' -f1-3 /proc/loadavg)
  if [ -f "$SELF/STATUS.T4d_IJ_f" ]; then
    rc=$(grep -aE "^rc=" "$SELF/STATUS.T4d_IJ_f" | cut -d= -f2)
    echo "[$STAMP] load=$LOAD | f=DONE(rc=$rc) -- watcher exiting" >> "$LOG"; break
  fi
  it=$(iter_of "$CD/log.solve"); it=${it:-0}
  pid=$(pid_of)
  dt=$((NOW - PREV_T)); di=$(( it - PREV_IT ))
  if [ "$PREV_T" -gt 0 ] && [ "$dt" -gt 0 ]; then
    rate=$(awk -v d="$di" -v t="$dt" 'BEGIN{printf "%.3f", d/t}')
    rem=$(( ENDT - it ))
    eta=$(awk -v r="$rate" -v rem="$rem" 'BEGIN{ if(r>0) printf "%.2f h", rem/r/3600.0; else print "n/a"}')
  else
    rate="--"; eta="--"
  fi
  echo "[$STAMP] load=$LOAD | f: pid=${pid:-?} it=$it/$ENDT rate=${rate}it/s ETA=$eta" >> "$LOG"
  PREV_IT=$it; PREV_T=$NOW
  [ $((NOW - T_START)) -ge "$MAX_S" ] && { echo "[$STAMP] MAX_S reached -- watcher exiting" >> "$LOG"; break; }
  sleep "$INTERVAL"
done
