#!/usr/bin/env bash
# D4-SHIPPED chain driver (PREREGISTRATION.md ADDENDUM 2).  Runs the named
# arms IN ORDER through the frozen launcher and STOPS AT THE FIRST NON-ZERO
# rc.  Started ONLY as
#   setsid nohup bash d4s_chain_driver.sh ACC F3 > <root>/chain_launch.out 2>&1 &
# so it is its own session leader and outlives the agent that started it --
# the failure this file exists not to repeat is D4-SHIPPED arm O, whose host
# poller died with the agent fleet and whose ledger row was never written.
#
# rc per arm = the launcher's exit = `docker inspect .State.ExitCode`, written
# HERE into STATUS.<arm> as `rc=<n> stamp=<utc> ...`.  Nothing trusts `$?` of a
# detached line.  Before each arm: the WINDOWED H5 gate (45 samples over 60 s,
# refuse on ANY sample below the floor -- never fire on one sample) and an
# aggregate-memory check (live container caps + this cap + host non-container
# RSS under the ceiling).  cwd is the CASE directory, never the run root
# (G-ROOT.5 b).  The driver's own pidfile is written so a second driver or a
# queue-runner re-fire is refused by the launcher's G-ROOT.5.
# Permission for detached launches: bc0e687e (Sanaa, boarded verbatim).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d4s_run_arm.sh"
IMG=dafoam/opt-packages:latest
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin
PERMISSION=bc0e687e
H5_FLOOR_GIB=16.0; H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6
# The launcher is FROZEN (Addendum 2 md5); asserted before EVERY arm so a
# mid-chain edit cannot change what the later arms run.
MD5_LAUNCHER=51987c2f5c583bc910ffe0f4415b09f5
test $# -ge 1 || { echo "ABORT usage: d4s_chain_driver.sh <ARM...>"; exit 64; }
ARMS="$*"; STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/d4s_driver.pid"
cd "$HERE" || exit 4
if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."; exit 3
  fi
fi
echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"' EXIT
echo "D4S_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] permission=$PERMISSION"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) permission=$PERMISSION" > "$STATUS"
mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
cap_mem_gib() { case "$1" in P1) echo 4;; ACC) echo 8;; *) echo 12;; esac; }
for ARM in $ARMS; do
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before arm $ARM"; echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 4; }
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
    echo "ABORT H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB.  A batch that OOMs is worse than a batch that queues.  REFUSED."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_REFUSED below=$BELOW min_GiB=$MIN permission=$PERMISSION" > "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_H5 arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 6
  fi
  # ---- AGGREGATE: live container caps + this cap + host non-container RSS
  AGG=$(python3 "$HERE/d4s_aggregate_memory.py" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
  echo "D4S_AGGREGATE arm=$ARM $AGG"
  if [ "$(printf '%s' "$AGG" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" != "1" ]; then
    echo "ABORT AGGREGATE over $AGG_CEILING_GIB GiB or unreadable.  REFUSED."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=AGGREGATE_REFUSED permission=$PERMISSION" > "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_AGGREGATE arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 6
  fi
  echo "D4S_DRIVER arm=$ARM begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID permission=$PERMISSION"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "D4S_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN permission=$PERMISSION" > "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit "$rc"; fi
done
echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
exit 0
