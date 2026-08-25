#!/bin/bash
# Memory guard for the F1 v2 butterfly mesh trial.  The box is SHARED --
# heat-transfer has 3 solvers and dafoam 2 containers live -- and m=4 is
# 7,159,808 cells.  This guard exists so a mesh trial cannot OOM the box and
# take down three other teams' runs.
#
# It NEVER touches a process it does not own: the only kill targets are
# blockMesh / checkMesh whose /proc/PID/cwd resolves INSIDE this run directory.
#
#   pre-check   -- when the m=4 leg starts, if MemAvailable < 6 GiB, skip m=4
#   hard floor  -- at any time, if MemAvailable < 3 GiB, stop this trial's mesher
R=/home/ubuntu/Certonomous/verification/runs/F1_MESH_TRIALS_2026-08-25
avail_gib() { awk '/MemAvailable/{printf "%.2f", $2/1048576}' /proc/meminfo; }
mine() {  # PIDs of blockMesh/checkMesh running inside $R
  for p in $(pgrep -x blockMesh; pgrep -x checkMesh); do
    c=$(readlink /proc/$p/cwd 2>/dev/null) || continue
    case "$c" in "$R"/*) echo $p;; esac
  done
}
m4_checked=0
while :; do
  [ -f "$R/TRIAL_DONE.txt" ] && { echo "guard: trial finished, exiting"; break; }
  A=$(avail_gib)
  if [ "$m4_checked" = 0 ] && [ -d "$R/v2_m4" ]; then
    m4_checked=1
    echo "$(date -u +%FT%TZ) m=4 leg starting, MemAvailable ${A} GiB" >> "$R/MEMORY_GUARD.log"
    if [ "$(echo "$A < 6.0" | bc -l)" = 1 ]; then
      echo "SKIP m=4: MemAvailable ${A} GiB < 6 GiB floor at leg start" > "$R/M4_SKIPPED.txt"
      for p in $(mine); do kill -TERM $p; done
      touch "$R/GUARD_TRIPPED.txt"
    fi
  fi
  if [ "$(echo "$A < 3.0" | bc -l)" = 1 ]; then
    P=$(mine)
    if [ -n "$P" ]; then
      echo "$(date -u +%FT%TZ) HARD FLOOR: MemAvailable ${A} GiB < 3 GiB, TERM $P" >> "$R/MEMORY_GUARD.log"
      for p in $P; do kill -TERM $p; done
      touch "$R/GUARD_TRIPPED.txt"
    fi
  fi
  echo "$(date -u +%FT%TZ) avail=${A}GiB load=$(cut -d' ' -f1-3 /proc/loadavg)" >> "$R/MEMORY_GUARD.log"
  sleep 10
done
