#!/usr/bin/env bash
# monitor_m1c.sh -- M1-C LIVE MONITOR (sec 2ba live-monitor half).
# FROZEN 2026-09-09 (§3 check-1 done, SOUND).  Read-only progress watcher for the six M1-C arms.  It does
# NOT grade, does NOT complete, does NOT write into any run tree -- it only READS
# each arm's log.run and STATUS and prints a compact table.  It is the human/live
# half of the dual-mechanism standard; the detached autograde_m1c.sh is the other,
# and NEITHER substitutes for the other (a monitor that grades, or a grader that
# needs a live agent, is NON-COMPLIANT under sec 2ba).
set -uo pipefail
M1C_ROOT="/home/ubuntu/closure-data/m1c_completion"
ENDTIME=20000
INTERVAL="${1:-30}"     # seconds between refreshes; one-shot if 0
ARMS6=( "kOmega/PH_Breuer" "kOmegaSST_null/PH_Breuer" "kOmega/AR_14_Ret_180" \
        "kOmega/AR_7_Ret_180" "kOmega/AR_1_Ret_180" "kOmegaSST_null/AR_1_Ret_180" )

one_pass(){
  printf '=== M1-C live monitor  %s ===\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '%-32s %8s %8s %10s %8s %6s\n' "arm/case" "lastT" "of20k%" "wall_s" "cap_s" "rc"
  for ac in "${ARMS6[@]}"; do
    d="$M1C_ROOT/$ac"; lg="$d/log.run"; S="$d/STATUS"
    lastT="-"; pct="-"; wall="-"; cap="-"; rc="-"
    [ -f "$lg" ] && lastT=$(grep -a '^Time = ' "$lg" 2>/dev/null | tail -1 | awk '{print $3}')
    [ -n "${lastT:-}" ] && [ "$lastT" != "-" ] && pct=$(awk -v t="$lastT" -v e="$ENDTIME" 'BEGIN{printf "%.1f", 100*t/e}')
    if [ -f "$S" ]; then
      wall=$(sed -n 's/^wall_s=//p' "$S"); cap=$(sed -n 's/^timeout_s=//p' "$S"); rc=$(sed -n 's/^rc=//p' "$S")
    fi
    printf '%-32s %8s %8s %10s %8s %6s\n' "$ac" "${lastT:--}" "${pct:--}" "${wall:--}" "${cap:--}" "${rc:--}"
  done
}

if [ "$INTERVAL" = "0" ]; then one_pass; exit 0; fi
while :; do one_pass; echo; sleep "$INTERVAL"; done
