#!/usr/bin/env bash
# drive.sh -- A3 rung 1 patched-IDWarp, np=4. Phase-2 lane, written AFTER the pre-registration
# commit 5d8e2f52 and committed BEFORE it runs. It changes no gate, threshold, band, cap or label.
#
# Runs the three arms STRICTLY SEQUENTIALLY in the registered order R1-A (patched) -> R1-B
# (shipped) -> R1-C (wrongstep), with the launch gate polled immediately before each and both
# guards ARMED before each container starts.
#
# PRECONDITIONS (PREREGISTRATION.md section 12 step 4):
#   GUARD_SELFTEST_PASS exists AND is newer than mem_guard.sh and coloring_guard.sh
#   free_cores >= 4 AND MemAvailable >= 12 GiB, polled 60 s x 240 (4 h)
# DECISION RULE (section 7): if R1-A expires on its timeout (rc 124), R1-B and R1-C are NOT
# launched, the item reports what it has, and NO SECOND BUDGET is requested.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT=/home/ubuntu/certonomous-runs/P4-a3-rung1-patched
IMG_PATCHED=dafoam-idwarp-rot:v1
IMG_SHIPPED=dafoam/opt-packages:latest
CACHE=dRdWColoring_4
COLOURS=1233
RSS_CEIL=11.0
HOST_FLOOR=8.0
say() { echo "$(date -u +%FT%TZ) $*" | tee -a "$ROOT/drive.status"; }

# --- precondition: the guard selftest licence -------------------------------
M="$ROOT/GUARD_SELFTEST_PASS"
[ -f "$M" ] || { say "NO GUARD_SELFTEST_PASS -- BLOCKED, no arm may launch."; exit 1; }
for g in mem_guard.sh coloring_guard.sh; do
  [ "$M" -nt "$HERE/$g" ] || { say "GUARD_SELFTEST_PASS is not newer than $g -- BLOCKED."; exit 1; }
done
say "precondition OK: GUARD_SELFTEST_PASS present and newer than both guard scripts"

freecores() {
  local s=() r k
  for k in 1 2 3 4 5; do r=$(ps -eo state= | grep -c '^R'); s+=($((r-1))); sleep 2; done
  local med=$(printf '%s\n' "${s[@]}" | sort -n | sed -n '3p')
  echo $(( $(nproc) - med ))
}

gate() {  # $1 = arm label; returns 0 if the gate opened, 9 if 240 polls expired
  local ARM="$1" i FC MG
  for i in $(seq 1 240); do
    FC=$(freecores); MG=$(awk '/MemAvailable/{printf "%.2f", $2/1048576}' /proc/meminfo)
    echo "$(date -u +%FT%TZ) $ARM poll=$i free_cores=$FC MemAvailable_GiB=$MG load1=$(cut -d' ' -f1 /proc/loadavg)" \
      >> "$ROOT/launch_condition.txt"
    if [ "$FC" -ge 4 ] && awk -v m="$MG" 'BEGIN{exit !(m>=12.0)}'; then
      GATE_FC=$FC; GATE_MG=$MG; return 0
    fi
    sleep 50
  done
  return 9
}

run_arm() {  # $1 arm  $2 image  $3 task  $4 timeout_s
  local ARM="$1" IMG="$2" TASK="$3" TMO="$4"
  local BASE="$ROOT/$ARM" LOG="$ROOT/${ARM}.log" NAME="p4_a3r1_${ARM}"
  if ! gate "$ARM"; then
    say "$ARM: LAUNCH CONDITION NEVER MET in 240 polls -- BLOCKED on host contention, \$0.00 spent"
    return 9
  fi
  { echo "LEVER_ECHO arm=$ARM task=$TASK image=$IMG at=$(date -u +%FT%TZ)"
    echo "LEVER_ECHO image_id=$(sudo -n docker images --no-trunc --format '{{.ID}}' "$IMG" | head -1)"
    echo "LEVER_ECHO ranks=4 cpus=4 memcap=12g timeout=${TMO}s decomposePar=-force"
    echo "LEVER_ECHO guards: mem_guard $RSS_CEIL/$HOST_FLOOR GiB; coloring_guard $CACHE/$COLOURS"
    echo "LEVER_ECHO gate_at_launch free_cores=$GATE_FC MemAvailable_GiB=$GATE_MG load1=$(cut -d' ' -f1 /proc/loadavg)"
  } > "$ROOT/lever_echo_${ARM}.txt"
  say "$ARM: gate open (free_cores=$GATE_FC MemAvailable=${GATE_MG} GiB). Arming guards."

  : > "$LOG"
  "$HERE/mem_guard.sh"      "$NAME" "$RSS_CEIL" "$HOST_FLOOR" "$ROOT" "$ARM" >/dev/null 2>&1 &
  local MGPID=$!
  "$HERE/coloring_guard.sh" "$NAME" "$LOG" "$CACHE" "$COLOURS" "$ROOT" "$ARM" >/dev/null 2>&1 &
  local CGPID=$!

  local T0=$(date -u +%s)
  timeout "$TMO" sudo -n docker run --rm --name "$NAME" --cpus=4 --memory=12g \
      -v "$BASE":/home/dafoamuser/mount/case -w /home/dafoamuser/mount/case \
      "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && decomposePar -force > decomposePar.log 2>&1 && mpirun --allow-run-as-root -np 4 -x PYTHONPATH python runScript_fd3p.py -task $TASK" \
      >> "$LOG" 2>&1
  local RC=$?
  local T1=$(date -u +%s)
  sudo -n docker kill "$NAME" >/dev/null 2>&1 || true
  wait $MGPID; local MGRC=$?
  wait $CGPID; local CGRC=$?
  local WALL=$((T1-T0))
  local CM=$(awk -v w=$WALL 'BEGIN{printf "%.3f", w*4/60.0}')
  local PEAK=$(awk 'NF>=3 && $2+0>0 {if ($2+0>m) m=$2+0} END{printf "%.3f", m}' "$ROOT/rss_${ARM}.txt" 2>/dev/null)
  echo "$ARM image=$IMG image_id=$(sudo -n docker images --no-trunc --format '{{.ID}}' "$IMG" | head -1) task=$TASK ranks=4 t0=$T0 t1=$T1 wall_s=$WALL core_min=$CM rc=$RC timeout=$TMO peak_rss_GiB=$PEAK mem_guard_rc=$MGRC coloring_guard_rc=$CGRC" \
    >> "$ROOT/ledger.txt"
  sudo -n chown -R ubuntu:ubuntu "$BASE" 2>/dev/null || true
  say "$ARM done: rc=$RC wall=${WALL}s core_min=$CM peak_rss=${PEAK}GiB mem_guard=$MGRC coloring_guard=$CGRC"
  return $RC
}

say "=== A3 rung 1 drive begins: R1-A patched -> R1-B shipped -> R1-C wrongstep ==="
run_arm patched "$IMG_PATCHED" fd3 780
RCA=$?
if [ $RCA -eq 124 ]; then
  say "R1-A TIMED OUT (rc 124). Per section 7 the registered decision rule, R1-B and R1-C are NOT"
  say "launched and NO SECOND BUDGET is requested."
  exit 124
fi
if [ $RCA -eq 9 ]; then
  say "R1-A never launched (gate). Nothing further is launched."
  exit 9
fi

run_arm shipped "$IMG_SHIPPED" fd3 780
RCB=$?
if [ $RCB -eq 124 ]; then
  say "R1-B TIMED OUT. R1-C still runs; R1-P6 and R1-P10 are recorded PENDING, never absent."
fi

run_arm wrongstep "$IMG_PATCHED" fd1wrong 300
say "=== ALL ARMS DONE ==="
