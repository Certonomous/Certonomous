#!/usr/bin/env bash
# MRF_R1 RUNAWAY GUARD -- REPORT ONLY.  IT NEVER KILLS ANYTHING.
#
# budget_gate: NONE -- Sanaa 2026-09-10.  No core-minute or wall cap STOPS this
# run.  This watcher exists so that a genuinely runaway solve is VISIBLE rather
# than silent: when a level passes 3x its OWN pre-registered projection
# (MRF_R1_PREREGISTRATION.md A1.3: coarse ~66 / medium ~192 / fine ~546
# core-min) it appends a line to RUNAWAY_REPORT.txt.  It sends no signal, it
# calls no kill, it changes no file inside a level.
#
# Sampling every 300 s.  Exits once all three levels have written RC.txt.
set -u
ROOT=/home/ubuntu/Certonomous/verification/runs/navier_class/MRF
REPORT=$ROOT/RUNAWAY_REPORT.txt
INTERVAL=300

# level:projected_core_min
LEVELS="coarse:66 medium:192 fine:546"

{ echo "=== MRF_R1 runaway guard (REPORT ONLY -- never kills) started $(date -u +%FT%TZ)"
  echo "=== thresholds are 3x the A1.3 projection: coarse 198 / medium 576 / fine 1638 core-min"
} >> "$REPORT"

declare -A FLAGGED
while :; do
  DONE=0
  for spec in $LEVELS; do
    L=${spec%%:*}; PROJ=${spec##*:}
    D=$ROOT/$L
    if [ -e "$D/RC.txt" ]; then
      DONE=$((DONE+1))
      if [ -z "${FLAGGED[$L]:-}" ] && [ -e "$D/CORE_MINUTES.txt" ]; then
        CM=$(cat "$D/CORE_MINUTES.txt")
        echo "$(date -u +%FT%TZ) $L FINISHED core_min=$CM projected=$PROJ ratio=$(awk -v a="$CM" -v b="$PROJ" 'BEGIN{printf "%.2f",a/b}')" >> "$REPORT"
        FLAGGED[$L]=done
      fi
      continue
    fi
    [ -e "$D/SOLVE_START_UTC.txt" ] || continue
    [ -e "$D/RANKS.txt" ] || continue
    T0=$(date -d "$(cat "$D/SOLVE_START_UTC.txt")" +%s 2>/dev/null) || continue
    R=$(cat "$D/RANKS.txt")
    NOW=$(date +%s)
    CM=$(awk -v w="$((NOW-T0))" -v r="$R" 'BEGIN{printf "%.1f",w*r/60.0}')
    OVER=$(awk -v c="$CM" -v p="$PROJ" 'BEGIN{print (c > 3.0*p) ? 1 : 0}')
    if [ "$OVER" = "1" ] && [ -z "${FLAGGED[$L]:-}" ]; then
      LASTT=$(grep -o '^Time = [0-9]*' "$D/log.simpleFoam" 2>/dev/null | tail -1 | awk '{print $3}')
      echo "$(date -u +%FT%TZ) RUNAWAY-REPORT $L core_min=$CM EXCEEDS 3x projection ($((3*PROJ))) ranks=$R iter=${LASTT:-?} -- REPORT ONLY, NOT STOPPED (budget_gate NONE, Sanaa 2026-09-10)" >> "$REPORT"
      FLAGGED[$L]=flagged
    fi
  done
  [ "$DONE" -ge 3 ] && { echo "$(date -u +%FT%TZ) all three levels have RC.txt -- guard exiting" >> "$REPORT"; break; }
  sleep $INTERVAL
done
