#!/usr/bin/env bash
# drive.sh -- A3 rung 3 patched-IDWarp, np=4, ATTEMPT 2. Copied byte-identical from
# ../rung3_patched_idwarp_np4/drive.sh (frozen at 3525f1d2) except for the lines listed in this
# item's PREREGISTRATION.md section 11. It changes no gate, threshold, band, cap or label.
#
# One arm: R3-A, `dafoam-idwarp-rot:v1`, -task ct_cd, --cpus=4 --memory=16g, timeout 2600.
#
# PRECONDITIONS (PREREGISTRATION.md section 12 step 4):
#   GUARD_SELFTEST_PASS exists AND is newer than mem_guard.sh, coloring_guard.sh,
#     identity_stop.sh and shipped_cd_checkpoints.txt
#   free_cores >= 4 AND MemAvailable >= 19.65 GiB, polled 60 s x 360 (6 h)
# DECISION RULE (section 7): rc=124 => report what matched, NO second budget, and neither the
# ct_cd discriminator of section 3 departure 6 nor stage R3-2 is launched under any branch.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT=/home/ubuntu/certonomous-runs/P5-a3-rung3-patched-attempt2
IMG=dafoam-idwarp-rot:v1
ARM=patched
NAME=p3_a3r3_patched
CACHE=dRdWColoring_4
COLOURS=1355
RSS_CEIL=15.0
HOST_FLOOR=8.0
CONV=1.0e-03
TMO=2600
say() { echo "$(date -u +%FT%TZ) $*" | tee -a "$ROOT/drive.status"; }

M="$ROOT/GUARD_SELFTEST_PASS"
[ -f "$M" ] || { say "NO GUARD_SELFTEST_PASS -- BLOCKED, the arm may not launch."; exit 1; }
for g in mem_guard.sh coloring_guard.sh identity_stop.sh shipped_cd_checkpoints.txt; do
  [ "$M" -nt "$HERE/$g" ] || { say "GUARD_SELFTEST_PASS is not newer than $g -- BLOCKED."; exit 1; }
done
say "precondition OK: GUARD_SELFTEST_PASS present and newer than all four grading-path files"

freecores() {
  local s=() r k
  for k in 1 2 3 4 5; do r=$(ps -eo state= | grep -c '^R'); s+=($((r-1))); sleep 2; done
  local med=$(printf '%s\n' "${s[@]}" | sort -n | sed -n '3p')
  echo $(( $(nproc) - med ))
}

GATE_FC=""; GATE_MG=""
gate() {
  local i FC MG
  for i in $(seq 1 360); do
    FC=$(freecores); MG=$(awk '/MemAvailable/{printf "%.2f", $2/1048576}' /proc/meminfo)
    echo "$(date -u +%FT%TZ) $ARM poll=$i free_cores=$FC MemAvailable_GiB=$MG load1=$(cut -d' ' -f1 /proc/loadavg)" \
      >> "$ROOT/launch_condition.txt"
    if [ "$FC" -ge 4 ] && awk -v m="$MG" 'BEGIN{exit !(m>=19.65)}'; then
      GATE_FC=$FC; GATE_MG=$MG; return 0
    fi
    sleep 50
  done
  return 9
}

BASE="$ROOT/$ARM"; LOG="$ROOT/${ARM}.log"
if ! gate; then
  say "LAUNCH CONDITION NEVER MET in 360 polls -- BLOCKED on host contention, \$0.00 of solver compute spent"
  exit 9
fi
{ echo "LEVER_ECHO arm=$ARM task=ct_cd image=$IMG at=$(date -u +%FT%TZ)"
  echo "LEVER_ECHO image_id=$(sudo -n docker images --no-trunc --format '{{.ID}}' "$IMG" | head -1)"
  echo "LEVER_ECHO ranks=4 cpus=4 memcap=16g timeout=${TMO}s decomposePar=-force"
  echo "LEVER_ECHO guards: mem_guard $RSS_CEIL/$HOST_FLOOR GiB; coloring_guard $CACHE/$COLOURS; identity_stop conv=$CONV"
  echo "LEVER_ECHO gate_at_launch free_cores=$GATE_FC MemAvailable_GiB=$GATE_MG load1=$(cut -d' ' -f1 /proc/loadavg)"
} > "$ROOT/lever_echo_${ARM}.txt"
say "gate open (free_cores=$GATE_FC MemAvailable=${GATE_MG} GiB). Arming all three guards."

: > "$LOG"
"$HERE/mem_guard.sh"      "$NAME" "$RSS_CEIL" "$HOST_FLOOR" "$ROOT" "$ARM" >/dev/null 2>&1 & MGPID=$!
"$HERE/coloring_guard.sh" "$NAME" "$LOG" "$CACHE" "$COLOURS" "$ROOT" "$ARM" >/dev/null 2>&1 & CGPID=$!
"$HERE/identity_stop.sh"  "$NAME" "$LOG" "$HERE/shipped_cd_checkpoints.txt" "$CONV" "$ROOT" "$ARM" >/dev/null 2>&1 & IDPID=$!

T0=$(date -u +%s)
timeout "$TMO" sudo -n docker run --rm --name "$NAME" --cpus=4 --memory=16g \
    -v "$BASE":/home/dafoamuser/mount/case -w /home/dafoamuser/mount/case \
    "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && decomposePar -force > decomposePar.log 2>&1 && mpirun --allow-run-as-root -np 4 -x PYTHONPATH python runScript_rung3p.py -task ct_cd" \
    >> "$LOG" 2>&1
RC=$?
T1=$(date -u +%s)
sudo -n docker kill "$NAME" >/dev/null 2>&1 || true
wait $MGPID; MGRC=$?
wait $CGPID; CGRC=$?
wait $IDPID; IDRC=$?
WALL=$((T1-T0))
CM=$(awk -v w=$WALL 'BEGIN{printf "%.3f", w*4/60.0}')
PEAK=$(awk 'NF>=3 && $2+0>0 {if ($2+0>m) m=$2+0} END{printf "%.3f", m}' "$ROOT/rss_${ARM}.txt" 2>/dev/null)
echo "$ARM image=$IMG image_id=$(sudo -n docker images --no-trunc --format '{{.ID}}' "$IMG" | head -1) task=ct_cd ranks=4 t0=$T0 t1=$T1 wall_s=$WALL core_min=$CM rc=$RC timeout=$TMO peak_rss_GiB=$PEAK mem_guard_rc=$MGRC coloring_guard_rc=$CGRC identity_stop_rc=$IDRC" \
  >> "$ROOT/ledger.txt"
sudo -n chown -R ubuntu:ubuntu "$BASE" 2>/dev/null || true
say "R3-A done: rc=$RC wall=${WALL}s core_min=$CM peak_rss=${PEAK}GiB mem_guard=$MGRC coloring_guard=$CGRC identity_stop=$IDRC"
if [ $RC -eq 124 ]; then
  say "R3-A TIMED OUT. Per section 7 the item reports what matched and NO SECOND BUDGET is requested."
fi
say "=== ARM DONE ==="
