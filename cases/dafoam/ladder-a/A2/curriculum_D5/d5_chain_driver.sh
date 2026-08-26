#!/usr/bin/env bash
# D5 chain driver -- DERIVED from curriculum_D4_SHIPPED/d4s_chain_driver.sh at
# commit 8b91be2b (Addendum 2) with the REGISTERED DELTAS listed in
# PREREGISTRATION.md section 7 and recorded in d5_chain_driver_DELTAS_from_d4s.diff:
#   (1) item names, run root, launcher, pidfile, PATCHED image (the row D4 was
#       graded on, C-97), per-arm memory caps, MD5_LAUNCHER;
#   (2) AGGREGATE in the WAIT-AND-RETRY form ruled for D4-SHIPPED in UPDATE F
#       (dafoam-supervisor, 2026-08-26 [lab-attributed]): poll 30 s, bounded 4 h,
#       EVERY wait written to STATUS.<arm>, refuse-and-BLOCK at the bound with
#       the series recorded;
#   (3) ALREADY_BOUGHT: an rc=0 ledger row for the arm refuses a re-fire (a
#       queue-runner duplicate would otherwise re-stage a graded arm);
#   (4) ROOT STAGING: the run root does not exist at freeze (the freeze
#       condition); the FIRST fire creates it (mode 777, L-251), copies D4's
#       PATCHED base/ READ-ONLY from D4's run root, the instruments from this
#       case directory, and the two FFD boxes; every copy is md5-asserted by the
#       launcher before any container starts.  A second fire finds the root and
#       stages nothing;
#   (5) STATUS.<arm> is OPENED at preflight and APPENDED; the LAST line carries
#       the rc, source=launcher_exit=docker_inspect_ExitCode -- never the $? of
#       a setsid/timeout line.
#   ADDENDUM 1 (pre-compute): every arm's memory cap is 12g, never 8g -- the
#       D4-SHIPPED ACC arm (the same compute_totals shape as ACC48/ACC192) was
#       OOM-killed by its 8g cgroup (rc=137, 16:56:28Z 2026-08-26).
# Runs the named arms IN ORDER through the frozen launcher and STOPS AT THE
# FIRST NON-ZERO rc.  Started ONLY detached (the queue runner's own form, or
#   setsid nohup bash d5_chain_driver.sh O48 ACC48 F48 O192 ACC192 F192 > <root>/chain_launch.out 2>&1 &
# ) so it is its own session leader and outlives the agent that started it.
# Before each arm: launcher md5; the WINDOWED H5 gate (45 samples over 60 s,
# refuse on ANY sample below the floor); ALREADY_BOUGHT; AGGREGATE wait-and-retry.
# cwd is the CASE directory, never the run root (G-ROOT.5 b).
# Permission for detached launches: bc0e687e (Sanaa, boarded verbatim).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d5_run_arm.sh"
IMG=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density
D4_BASE_SRC=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/base
D4_CASE_DIR="$HERE/../curriculum_D4"
PERMISSION=bc0e687e
H5_FLOOR_GIB=16.0; H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6
AGG_POLL_S=30; AGG_BOUND_S=14400
# The launcher is FROZEN (PREREGISTRATION.md section 8 + Addendum 1 md5);
# asserted before EVERY arm so a mid-chain edit cannot change what runs.
MD5_LAUNCHER=50a976780e357998238ede3bbb8e5521
MD5_RUNSCRIPT=fa1d91c82d11aacd0ae072652b346952
MD5_FD=91b9f3526a39cb02eafbd5be504d7107
MD5_EXTRACT=ee7d3c99fd716da23779cb651961918e
MD5_FFD48=85a8bcd5d39f1b11a612ac0a39aee776
MD5_FFD192=8eb161df4c546d10d7fcb30132f58907
test $# -ge 1 || { echo "ABORT usage: d5_chain_driver.sh <ARM...>"; exit 64; }
ARMS="$*"; STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/d5_driver.pid"
cd "$HERE" || exit 4
echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before staging"; exit 4; }
# ---- (4) ROOT STAGING on the first fire only ------------------------------
if [ ! -d "$BASE" ]; then
  test -d "$D4_BASE_SRC" || { echo "ABORT D4 base source absent: $D4_BASE_SRC"; exit 4; }
  mkdir -p "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
  chmod 777 "$BASE" || { echo "ABORT chmod 777 $BASE (L-251)"; exit 4; }
  cp -a "$D4_BASE_SRC" "$BASE/base" || { echo "ABORT copy base/"; exit 4; }
  mkdir -p "$BASE/ffd" || exit 4
  cp -a "$HERE/ffd/wingFFD_48.xyz" "$HERE/ffd/wingFFD_192.xyz" "$BASE/ffd/" || { echo "ABORT copy ffd"; exit 4; }
  cp -a "$HERE/d5_opt_runScript.py" "$HERE/d5_fd_endpoint.py" "$D4_CASE_DIR/d4_extract_endpoint.py" "$BASE/" || { echo "ABORT copy instruments"; exit 4; }
  echo "ITEM=D5 staged=$(date -u +%Y%m%dT%H%M%SZ) base_src=$D4_BASE_SRC permission=$PERMISSION" > "$BASE/ledger.txt"
  echo "D5_ROOT_STAGED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ) mode=$(stat -c '%a' "$BASE") permission=$PERMISSION"
else
  echo "D5_ROOT_PRESENT base=$BASE (not re-staged)"
fi
{ echo "$MD5_RUNSCRIPT  $BASE/d5_opt_runScript.py"; echo "$MD5_FD  $BASE/d5_fd_endpoint.py"; echo "$MD5_EXTRACT  $BASE/d4_extract_endpoint.py"; echo "$MD5_FFD48  $BASE/ffd/wingFFD_48.xyz"; echo "$MD5_FFD192  $BASE/ffd/wingFFD_192.xyz"; } | md5sum -c - || { echo "ABORT staged instrument md5"; exit 4; }
test -f "$BASE/base/FFD/wingFFD.xyz" || { echo "ABORT staged base/ has no FFD/wingFFD.xyz"; exit 4; }
if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."; exit 3
  fi
fi
echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"' EXIT
echo "D5_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] permission=$PERMISSION"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) permission=$PERMISSION" >> "$STATUS"
mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
cap_mem_gib() { echo 12; }   # ADDENDUM 1: every arm 12g
for ARM in $ARMS; do
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before arm $ARM"; echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 4; }
  # ---- (5) STATUS.<arm> is OPENED here (preflight line) and APPENDED from now
  # ---- on; the LAST line carries the rc.  Every AGGREGATE_WAIT is a line in it.
  echo "preflight arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ permission=$PERMISSION" > "$BASE/STATUS.$ARM"
  # ---- (3) ALREADY BOUGHT: a launcher-written rc=0 row for this arm means a
  # ---- re-fire would re-stage a graded arm.  REFUSED.
  if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT ALREADY_BOUGHT arm $ARM has an rc=0 ledger row; a second record for one run is the defect."
    echo "rc=3 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=ALREADY_BOUGHT permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=REFUSED_ALREADY_BOUGHT arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 3
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
  echo "D5_H5_WINDOW arm=$ARM n=$N window_s=$H5_WINDOW_S floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAX samples_below_floor=$BELOW file=$(basename "$H5_FILE")"
  if [ "$BELOW" -gt 0 ] || [ "$N" -ne "$H5_SAMPLES" ]; then
    echo "ABORT H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB.  A batch that OOMs is worse than a batch that queues.  REFUSED."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_REFUSED below=$BELOW min_GiB=$MIN permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_H5 arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 6
  fi
  # ---- (2) AGGREGATE: live container caps + this cap + host non-container RSS,
  # ---- WAIT-AND-RETRY (UPDATE F ruling): poll AGG_POLL_S, bounded AGG_BOUND_S;
  # ---- every wait written to STATUS.<arm>; refuse-and-BLOCK at the bound.
  WAITED=0; AGG_SERIES="$BASE/${ARM}_aggregate_series.txt"
  while true; do
    AGG=$(python3 "$HERE/d5_aggregate_memory.py" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
    echo "$(date -u +%s) $AGG" >> "$AGG_SERIES"
    if [ "$(printf '%s' "$AGG" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ]; then break; fi
    if [ "$WAITED" -ge "$AGG_BOUND_S" ]; then
      echo "ABORT AGGREGATE still over $AGG_CEILING_GIB GiB after ${WAITED}s.  BLOCKED.  Series: $(basename "$AGG_SERIES")"
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=AGGREGATE_BLOCKED_AT_BOUND waited=$WAITED series=$(basename "$AGG_SERIES") permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_AGGREGATE arm=$ARM waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 6
    fi
    echo "AGGREGATE_WAIT waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM $AGG" >> "$BASE/STATUS.$ARM"
    sleep "$AGG_POLL_S"; WAITED=$((WAITED+AGG_POLL_S))
  done
  echo "D5_AGGREGATE arm=$ARM waited=$WAITED $AGG"
  echo "D5_DRIVER arm=$ARM begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID permission=$PERMISSION"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "D5_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN aggregate_waited_s=$WAITED permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit "$rc"; fi
done
echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
exit 0
