#!/usr/bin/env bash
# mem_guard.sh -- the WIRED memory stop for the A3 rung-1 patched-IDWarp arms (np=4).
#
# WHY THIS FILE EXISTS. A3 rung 2 registered "host MemAvailable < 8 GiB -> the arm is stopped by
# memory" and armed a RECORD-ONLY watcher. Nothing connected the two. The graded arm drove host
# MemAvailable to 5.85 GiB and held it below the registered floor for 82 of 156 samples and no stop
# fired (rung2_patched_idwarp_np4/RESULTS.md section 9.1; L-239). This script is the enforcement
# path that was missing. It polls, it decides, and it kills.
#
# It only ever REDUCES spend. It alters no gate, threshold, band, cap or label.
#
# Usage: mem_guard.sh <container-name> <rss_ceiling_GiB> <host_floor_GiB> <root> <arm>
# Exit:  0 = container exited on its own, no breach       (arm is graded normally)
#        4 = STOP FIRED, container killed                  (arm is NOT A RESULT -- stopped by memory)
#        2 = usage / preconditions wrong                   (arm must not launch)
set -u

if [ "$#" -ne 5 ]; then
  echo "usage: mem_guard.sh <container> <rss_ceiling_GiB> <host_floor_GiB> <root> <arm>" >&2
  exit 2
fi
NAME="$1"; CEIL="$2"; FLOOR="$3"; ROOT="$4"; ARM="$5"

SAMPLE_S=5          # seconds between samples
STRIKES_TO_FIRE=3   # consecutive breaching samples before the kill; 3 x 5 s = 15 s of debounce.
                    # Rationale, registered: a single dip can be a FOREIGN process (rung 2 saw a
                    # foreign viewFactorsGen at 14.96 GiB RSS). A breach sustained 15 s on this box
                    # is the arm's own doing -- rung 2's real breach lasted 52.6% of the run and
                    # would have fired this guard on its third sample.
MAX_SAMPLES=100000

TRACE="$ROOT/rss_${ARM}.txt"
MARK="$ROOT/MEMORY_STOP_FIRED.${ARM}"
NOKILL="${MEM_GUARD_NO_KILL:-0}"   # selftest hook only; the driver never sets it

# Convert a docker-stats size token (9.263GiB / 912.3MiB / 512B) to GiB. Prints NaN on a bad parse.
to_gib() {
  awk -v s="$1" 'BEGIN{
    if (!match(s, /[0-9.]+/)) { print "NaN"; exit }
    v = substr(s, RSTART, RLENGTH) + 0
    u = substr(s, RSTART + RLENGTH)
    if      (u ~ /^GiB/) f = 1
    else if (u ~ /^MiB/) f = 1/1024
    else if (u ~ /^KiB/) f = 1/1048576
    else if (u ~ /^TiB/) f = 1024
    else if (u ~ /^B/)   f = 1/1073741824
    else { print "NaN"; exit }
    printf "%.6f", v * f
  }'
}
gt() { awk -v a="$1" -v b="$2" 'BEGIN{ exit !(a > b) }'; }

strikes=0
seen=0
echo "# mem_guard armed $(date -u +%FT%TZ) container=$NAME rss_ceiling=${CEIL}GiB host_floor=${FLOOR}GiB strikes=${STRIKES_TO_FIRE} interval=${SAMPLE_S}s" >> "$TRACE"

for _ in $(seq 1 "$MAX_SAMPLES"); do
  RAW=$(sudo -n docker stats --no-stream --format '{{.MemUsage}}' "$NAME" 2>/dev/null | awk '{print $1}')
  MAVAIL=$(awk '/MemAvailable/{printf "%.4f", $2/1048576}' /proc/meminfo)

  if [ -z "$RAW" ]; then
    if [ "$seen" = "1" ]; then
      echo "$(date -u +%s) container_gone MemAvailable_GiB=$MAVAIL" >> "$TRACE"
      exit 0
    fi
    sleep "$SAMPLE_S"; continue
  fi
  seen=1

  RSS=$(to_gib "$RAW")
  if [ "$RSS" = "NaN" ]; then
    # A parse failure must not silently disable the guard (that is the L-239 failure again).
    echo "$(date -u +%s) PARSE_FAILURE raw='$RAW' -- guard cannot read the instrument" >> "$TRACE"
    echo "$(date -u +%FT%TZ) mem_guard: cannot parse docker stats output '$RAW'; refusing to run blind." >> "$TRACE"
    exit 2
  fi

  WHY=""
  if gt "$RSS" "$CEIL";      then WHY="own RSS ${RSS} GiB > ceiling ${CEIL} GiB"; fi
  if gt "$FLOOR" "$MAVAIL";  then WHY="${WHY:+$WHY; }host MemAvailable ${MAVAIL} GiB < floor ${FLOOR} GiB"; fi

  if [ -n "$WHY" ]; then strikes=$((strikes + 1)); else strikes=0; fi
  echo "$(date -u +%s) $RSS $MAVAIL strikes=$strikes ${WHY:-ok}" >> "$TRACE"

  if [ "$strikes" -ge "$STRIKES_TO_FIRE" ]; then
    {
      echo "$(date -u +%FT%TZ) MEMORY STOP FIRED on arm $ARM (container $NAME)"
      echo "reason: $WHY"
      echo "sustained for $strikes consecutive samples at ${SAMPLE_S}s = $((strikes * SAMPLE_S))s"
      echo "last sample: own_RSS_GiB=$RSS host_MemAvailable_GiB=$MAVAIL"
      echo "DISPOSITION: the arm is STOPPED BY MEMORY. Per DAFOAM_CHARTER.md section 7 and this"
      echo "item's PREREGISTRATION.md, it is NOT A RESULT: no gradient, conditioning or patch claim"
      echo "is drawn from it in any direction, the cap is NOT raised, and no second budget is taken."
    } | tee -a "$MARK" >> "$TRACE"
    if [ "$NOKILL" = "1" ]; then
      echo "$(date -u +%FT%TZ) NO_KILL set (selftest) -- would have killed $NAME" >> "$TRACE"
    else
      sudo -n docker kill "$NAME" >/dev/null 2>&1
    fi
    exit 4
  fi
  sleep "$SAMPLE_S"
done
echo "$(date -u +%s) sample budget exhausted without a breach" >> "$TRACE"
exit 0
