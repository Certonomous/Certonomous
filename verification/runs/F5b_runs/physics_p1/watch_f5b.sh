#!/bin/bash
# OS-LEVEL sampler for F5b physics_p1.  Detached (PPID 1); survives the death of any
# agent.  Reads the solver's OWN log and writes every result to DISK as a side effect,
# so a successor reconstructs state from artifacts and never from an agent's memory.
RUN=/home/ubuntu/Certonomous/verification/runs/F5b_runs/physics_p1
LOG=$RUN/case/log.pimpleFoam
PID=$(cat $RUN/PID.txt)
CAPW=4320          # 72.0 core-min x 60 / 1 rank -- SANAA'S CAP in wall seconds
L0=$(date -d "$(cat $RUN/LAUNCH_STAMP.txt)" +%s)
while true; do
  NOW=$(date -u +%s); WALL=$((NOW-L0))
  ET=$(grep 'ExecutionTime' $LOG 2>/dev/null | tail -1 | sed -E 's/.*ExecutionTime = ([0-9.]+) s.*/\1/'); [ -z "$ET" ] && ET=0
  T=$(grep '^Time = ' $LOG 2>/dev/null | tail -1 | sed 's/Time = //'); [ -z "$T" ] && T=0
  S=$(grep -c '^Time = ' $LOG 2>/dev/null)
  printf '%s wall=%ss ET=%ss t=%s steps=%s load=%s\n' "$(date -u +%H:%M:%SZ)" "$WALL" "$ET" "$T" "$S" "$(cut -d' ' -f1-3 /proc/loadavg)" >> $RUN/WATCH_LOG.txt
  if [ -f $RUN/record.json ]; then
    { echo "TERMINAL=COMPLETE"; echo "stamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "wall_s=$WALL"
      echo "ExecutionTime_s=$ET"; echo "core_min=$(awk -v e=$ET 'BEGIN{printf "%.3f", e/60}')"
      echo "cap_core_min=72.0"; echo "cap_breached=NO"; echo "last_time=$T"; echo "steps=$S"
      echo "loadavg_terminal=$(cat /proc/loadavg)"; } > $RUN/WATCH_TERMINAL.txt; sync; exit 0; fi
  if ! kill -0 $PID 2>/dev/null; then
    { echo "TERMINAL=DIED_NO_RECORD"; echo "stamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "wall_s=$WALL"
      echo "ExecutionTime_s=$ET"; echo "core_min=$(awk -v e=$ET 'BEGIN{printf "%.3f", e/60}')"
      echo "note=driver pid gone with NO record.json -> run_case raised (D-2 path)"
      echo "last_time=$T"; echo "steps=$S"; echo "loadavg_terminal=$(cat /proc/loadavg)"; } > $RUN/WATCH_TERMINAL.txt; sync; exit 0; fi
  if [ "$WALL" -gt "$CAPW" ]; then
    # AN OVERRUN STOPS THE RUN.  It does not get a new budget (CLAUDE.md rule 12).
    kill -TERM $PID 2>/dev/null; sleep 5; kill -KILL $PID 2>/dev/null
    { echo "TERMINAL=CAP_BREACH_STOPPED"; echo "stamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "wall_s=$WALL"
      echo "ExecutionTime_s=$ET"; echo "core_min=$(awk -v e=$ET 'BEGIN{printf "%.3f", e/60}')"
      echo "cap_core_min=72.0"; echo "cap_breached=YES -- RUN STOPPED, NO NEW BUDGET"
      echo "last_time=$T"; echo "steps=$S"; echo "loadavg_terminal=$(cat /proc/loadavg)"; } > $RUN/WATCH_TERMINAL.txt; sync; exit 0; fi
  sleep 15
done
