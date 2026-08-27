#!/usr/bin/env bash
# D4S-F3SR chain driver -- D4S-F3S's d4s_f3s_chain_driver.sh (md5 da74cd11...,
# frozen at 8dfb4598) with the run root, the instrument names and the frozen
# md5s moved to this item, and ONE addition: THE STAGER IS NOW MD5-ASSERTED
# BEFORE EVERY ARM.  The predecessor asserted only the launcher and the grader;
# the D4S-F3S-AGE-DEF-1 repair lives in the STAGER (the age datum, the sibling
# `rm -f`, the touch-last reference and the staged-input manifest), so an
# unasserted stager would leave the repair unfrozen.  Two endpoint arms, F-S
# (SHIPPED image) and F-P (PATCHED image), under ONE stationarity rule.  Runs the
# named arms IN ORDER through the frozen launcher and STOPS AT THE FIRST
# NON-ZERO rc.  Started ONLY detached (the queue runner's setsid nohup form;
# permission bc0e687e) so it outlives the agent that filed it.
#   rc per arm = the launcher's exit = docker inspect .State.ExitCode, written
#   HERE into STATUS.<arm>; nothing trusts $? of a detached line.
#   Before each arm: WINDOWED H5 (45 samples / 60 s, refuse on ANY sample below
#   the floor), ALREADY_BOUGHT, AGGREGATE wait-and-retry (bounded 4 h).
#   FIRST FIRE creates the run root (mode 777, ITEM= ledger header); a later
#   fire finds it and stages nothing over a present arm (the stager refuses an
#   existing destination; the launcher refuses a live arm, G-ROOT.5).
#   At chain end the FROZEN grader runs on the artefacts; its rc is
#   INFRASTRUCTURE (L-342) and is labelled so.  CHAIN_DONE is written at exit.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d4s_f3sr_run_arm.sh"
STAGER="$HERE/d4s_f3sr_stage_arm.sh"
GRADER="$HERE/d4s_f3sr_grade.py"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3SR-a2-wing-cdmin
ITEM=D4S-F3SR
PERMISSION=bc0e687e
H5_FLOOR_GIB=16.0; H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6
# FROZEN instrument md5s (PREREGISTRATION.md section 7); asserted before EVERY arm.
MD5_LAUNCHER=ae13edeae807be82269de2fa5c5dc488
MD5_STAGER=39a01c8d76d3cd27285ff1fb754bf12b
MD5_GRADER=9596c7bf711a934313a9b4d5801481c6
img_of() { case "$1" in F-S) echo dafoam/opt-packages:latest ;; F-P) echo dafoam-idwarp-rot:v1 ;; *) echo "" ;; esac; }
cap_mem_gib() { case "$1" in F-S|F-P) echo 12 ;; *) echo 12 ;; esac; }
test $# -ge 1 || { echo "ABORT usage: d4s_f3sr_chain_driver.sh <F-S|F-P ...>"; exit 64; }
for A in "$@"; do test -n "$(img_of "$A")" || { echo "ABORT unknown arm $A (F-S|F-P)"; exit 64; }; done
ARMS="$*"; STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/d4s_f3sr_driver.pid"
cd "$HERE" || exit 4
# ---- FIRST FIRE: create the registered root (asserted ABSENT at freeze) ----
if [ ! -d "$BASE" ]; then
  mkdir "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
  chmod 777 "$BASE" || { echo "ABORT cannot chmod run root"; exit 4; }
  echo "ITEM=$ITEM" > "$BASE/ledger.txt"
  echo "D4SF3SR_ROOT_CREATED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ)"
fi
if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."; exit 3
  fi
fi
echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"; echo "chain_done stamp=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ arms=[$ARMS]" >> "$BASE/CHAIN_DONE"' EXIT
echo "D4SF3SR_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] permission=$PERMISSION"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) permission=$PERMISSION" >> "$STATUS"
mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
for ARM in $ARMS; do
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before arm $ARM"; echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 4; }
  echo "$MD5_STAGER  $STAGER" | md5sum -c - || { echo "ABORT stager md5 drifted before arm $ARM -- the age repair lives here"; echo "chain=ABORT arm=$ARM reason=stager_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 4; }
  IMG=$(img_of "$ARM")
  echo "preflight arm=$ARM image=$IMG stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ permission=$PERMISSION" > "$BASE/STATUS.$ARM"
  # ---- ALREADY BOUGHT: a launcher-written rc=0 row for this arm refuses a re-fire
  if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT ALREADY_BOUGHT arm $ARM has an rc=0 ledger row; a second record for one run is the defect."
    echo "chain=REFUSED_ALREADY_BOUGHT arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 3
  fi
  # ---- STAGE the arm's copy of its source O/ if absent; a present copy without
  # ---- its epoch is REFUSED, never re-staged over.
  if [ ! -d "$BASE/$ARM" ]; then
    bash "$STAGER" "$ARM" > "$BASE/${ARM}_stage.out" 2>&1
    src=$?
    if [ "$src" -ne 0 ]; then
      echo "ABORT staging of $ARM failed rc=$src (see ${ARM}_stage.out)"
      echo "rc=$src stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=STAGING_REFUSED stage_out=${ARM}_stage.out permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
      echo "chain=STOPPED_STAGING arm=$ARM rc=$src stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit "$src"
    fi
    echo "D4SF3SR_STAGED arm=$ARM copy_epoch=$(cat "$BASE/$ARM/.d4s_f3sr_stage_${ARM}_copy_epoch") age_ref=$(cat "$BASE/$ARM/.d4s_f3sr_stage_${ARM}_age_ref") staged_inputs=$(python3 -c "import json;print(len(json.load(open('$BASE/$ARM/.d4s_f3sr_staged_inputs.json'))['staged_inputs']))") evidence=${ARM}_STAGING_EVIDENCE.txt"
  elif [ ! -f "$BASE/$ARM/.d4s_f3sr_stage_${ARM}_copy_epoch" ]; then
    echo "ABORT $BASE/$ARM exists without a copy epoch -- not a staged copy; REFUSED, nothing removed"
    echo "rc=5 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=UNSTAGED_DIR_PRESENT permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_STAGING arm=$ARM rc=5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 5
  fi
  # ---- H5: a WINDOW of MemAvailable, every sample above the floor
  H5_FILE="$BASE/${ARM}_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"; BELOW=0; N=0; MIN=999; MAX=0
  STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))")
  for _ in $(seq 1 $H5_SAMPLES); do
    s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"
    MIN=$(python3 -c "print(min($MIN,$s))"); MAX=$(python3 -c "print(max($MAX,$s))")
    [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1))
    sleep "$STEP"
  done
  echo "D4S_H5_WINDOW arm=$ARM n=$N window_s=$H5_WINDOW_S floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAX samples_below_floor=$BELOW file=$(basename "$H5_FILE")"
  if [ "$BELOW" -gt 0 ] || [ "$N" -ne "$H5_SAMPLES" ]; then
    echo "ABORT H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB.  REFUSED."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_REFUSED below=$BELOW min_GiB=$MIN permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_H5 arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 6
  fi
  # ---- AGGREGATE: WAIT-AND-RETRY, poll 30 s, bounded 4 h; refuse-and-BLOCK at the bound
  WAITED=0; AGG_BOUND_S=14400; AGG_SERIES="$BASE/${ARM}_aggregate_series.txt"
  while true; do
    AGG=$(python3 "$HERE/d4s_aggregate_memory.py" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
    echo "$(date -u +%s) $AGG" >> "$AGG_SERIES"
    if [ "$(printf '%s' "$AGG" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ]; then break; fi
    if [ "$WAITED" -ge "$AGG_BOUND_S" ]; then
      echo "ABORT AGGREGATE still over $AGG_CEILING_GIB GiB after ${WAITED}s.  BLOCKED."
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=AGGREGATE_BLOCKED_AT_BOUND waited=$WAITED series=$(basename "$AGG_SERIES") permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_AGGREGATE arm=$ARM waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 6
    fi
    echo "AGGREGATE_WAIT waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM $AGG" >> "$BASE/STATUS.$ARM"
    sleep 30; WAITED=$((WAITED+30))
  done
  echo "D4S_AGGREGATE arm=$ARM waited=$WAITED $AGG"
  echo "D4SF3SR_DRIVER arm=$ARM image=$IMG begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID permission=$PERMISSION"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "D4SF3SR_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit "$rc"; fi
done
# ---- chain end: the FROZEN grader on the artefacts (rc is INFRASTRUCTURE, L-342)
GST=$(date -u +%Y%m%dT%H%M%SZ)
if echo "$MD5_GRADER  $GRADER" | md5sum -c - ; then
  python3 "$GRADER" --base "$BASE" --out "$BASE/d4s_f3sr_grade_$GST.json" > "$BASE/grade_$GST.out" 2>&1
  grc=$?
  echo "grade_rc=$grc stamp=$GST out=d4s_f3sr_grade_$GST.json note=grader-exit-status-INFRASTRUCTURE-L-342-not-the-verdict" >> "$STATUS"
else
  echo "grade_rc=NOT_RUN stamp=$GST reason=grader_md5_drift note=INFRASTRUCTURE-L-342" >> "$STATUS"
fi
echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
exit 0
