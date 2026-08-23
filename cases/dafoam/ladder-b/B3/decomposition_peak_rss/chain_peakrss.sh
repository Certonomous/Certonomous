#!/usr/bin/env bash
# B3 decomposition peak-RSS chain. Registered at
# cases/dafoam/ladder-b/B3/decomposition_peak_rss/PREREGISTRATION.md, committed
# d062aace BEFORE any container of this item started. Sections 2.5 and 9.
#
# This file exists in the RUN ROOT and not in a scratch directory, because the
# graded chain's own driver was lost to a scratch wipe (L-186) and that is the
# single biggest gap in this item's reconstruction. It is preserved here.
#
# Every container is foreground, --rm, timeout-bounded and NAMED. Nothing runs in
# the background except the watcher, which exits on its own when its container is
# gone. Nothing needs killing.
#
# LEDGER FORMAT is fixed by the FROZEN grader analyse_peak_rss.py, which reads
# rc at field 4, wall_s at 5, core_min at 6:
#   arm,image,np,env,rc,wall_s,core_min,finished_utc
# The decomposition is not a ledger column here; it is read back out of each
# arm's own directory afterwards, which is the stronger check anyway (the graded
# item's section 6a trap was an arm that silently ran scotch).
set -uo pipefail
R=/home/ubuntu/certonomous-runs/B3-decomposition-peakrss
W=/home/ubuntu/Certonomous/cases/dafoam/ladder-b/B3/decomposition_peak_rss/b3_rss_watch.sh
IMG=dafoam-subpclu:v2
HARD_FLOOR_KIB=4194304          # 4 GiB host floor -> docker kill (prereg 3.1)
GATE_KIB=12582912               # registered launch gate, -gt, unchanged

echo "arm,image,np,env,rc,wall_s,core_min,finished_utc" > "$R/ledger.csv"

gate () {   # bounded 60 x 20 s = 20 min; BLOCKED if it never opens
  local ok=0 i
  for i in $(seq 1 60); do
    L=$(awk '{print int($1)}' /proc/loadavg)
    M=$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)
    if [ "$L" -le 10 ] && [ "$M" -gt "$GATE_KIB" ]; then
      echo "GATE OPEN load=$L mem_kB=$M utc=$(date -u +%FT%TZ)"; ok=1; break
    fi
    sleep 20
  done
  [ "$ok" = "1" ] || { echo "GATE NEVER OPENED after 20 min -- BLOCKED"; return 1; }
}

run () {
  ARM="$1"; NP="$2"; TMO="$3"; TICKS="$4"
  gate || { echo "== $ARM BLOCKED (launch gate)"; return 1; }

  "$W" "b3rss_$ARM" "$R/logs/${ARM}_rss.log" "$TICKS" "$HARD_FLOOR_KIB" &
  WPID=$!

  start=$(date -u +%s)
  timeout "$TMO" sudo -n docker run --rm --name "b3rss_$ARM" \
    --cpuset-cpus 0-3 --memory=12g -e DAFOAM_SUBPC_TYPE=lu \
    -v "$R":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun --allow-run-as-root -np $NP python runScript.py -task compute_totals ; rc=\$? ; echo CGROUP_PEAK_BYTES=\$(cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo 0) ; exit \$rc" \
    > "$R/logs/${ARM}.log" 2>&1
  rc=$?; end=$(date -u +%s)
  wait $WPID 2>/dev/null

  sudo -n chown -R ubuntu:ubuntu "$R" 2>/dev/null || true
  cm=$(awk "BEGIN{printf \"%.2f\", ($end-$start)*$NP/60}")
  echo "$ARM,$IMG,$NP,SUBPC=lu,$rc,$((end-start)),$cm,$(date -u +%FT%TZ)" >> "$R/ledger.csv"

  # decomposition read back out of the arm's OWN directory, never from the launch
  # command (decomposition_np4/RESULTS.md section 6a: editing the file does nothing,
  # and an arm that silently ran scotch looks completely healthy)
  { echo "--- $ARM system/decomposeParDict as DAFoam wrote it ---"
    grep -aE 'numberOfSubdomains|^method|n +\(' "$R/$ARM/system/decomposeParDict" 2>/dev/null
    echo "--- processor dirs present ---"; ls -d "$R/$ARM"/processor* 2>/dev/null | wc -l
  } > "$R/logs/${ARM}_decomp.txt" 2>&1

  echo "== DONE $ARM rc=$rc wall=$((end-start))s core_min=$cm"
  grep -aE 'T3 DECOMP OVERRIDE|DAFOAM_SUBPC_TYPE=lu:|Total iterations.*PetscConvergedReason|OBJ varianceU|GRAD n=|CGROUP_PEAK_BYTES' "$R/logs/${ARM}.log" | tail -6
  cat "$R/logs/${ARM}_decomp.txt"
}

run D_serial  1 2400 1300
run D_simple2 4 2100 1100

touch "$R/.done"
echo "=== CHAIN PEAKRSS COMPLETE $(date -u +%FT%TZ) ==="
cat "$R/ledger.csv"
