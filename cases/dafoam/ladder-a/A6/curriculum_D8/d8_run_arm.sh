#!/usr/bin/env bash
# Curriculum D8 arm launcher.  FROZEN INSTRUMENT (PREREGISTRATION.md s9, md5).
#
# Inherited discipline, by lesson:
#   L-251   --user 0:0 pinned; run root asserted world-writable before launch
#   8.1     kernel-only stop: --memory == --memory-swap, --oom-score-adj=500.
#           NO watcher process kills anything.  The RSS sampler RECORDS ONLY.
#   8.2     NO --rm, so `docker inspect .State.{ExitCode,OOMKilled}` survives the
#           arm.  At a 9.787 GiB measured adjoint basis that read is load-bearing:
#           it is the only thing that separates a cap-kill (right-censored ->
#           PENDING) from a genuine failure.
#   A3 bug  peak_rss_GiB was printed as 0.000 from an UNINITIALISED awk variable
#           with `2>/dev/null` hiding a missing sample file, and the class already
#           fired once (curriculum_D3_attempt2/RESULTS.md:76, peak_rss_GiB=11
#           against a true 0.5973).  Here PEAK is initialised to NOT_MEASURED and
#           a MISSING OR EMPTY sample file REFUSES rather than printing a zero.
#   set -e  does NOT gate at the top level of an agent Bash call and `( set -e )`
#           does not either.  Every step below gates with an explicit `|| exit`.
set -uo pipefail

BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt
ARM="${1:?arm}"; TASK="${2:?task}"; TMO="${3:-10800}"
IMG=dafoam-idwarp-rot:v1
IMG_ID=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
EXPECT_MD5=85f59e87253e0a71a813f64ca6e4c425
MEM=12g
FLOOR_KB=12582912          # the standing MemAvailable floor, 12 GiB

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d8_${ARM}_${STAMP}"
LOG="$BASE/${ARM}.log"
RSSF="$BASE/rss_${ARM}.txt"

# ---- G-MEM-PRE: the standing 12 GiB MemAvailable floor, BEFORE the launch ----
AVAIL=$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)
[ -n "$AVAIL" ] || { echo "ABORT: MemAvailable unreadable"; exit 6; }
echo "D8_MEMAVAIL_PRE_KB=$AVAIL"
[ "$AVAIL" -ge "$FLOOR_KB" ] || { echo "ABORT BLOCKED: MemAvailable ${AVAIL}kB < floor ${FLOOR_KB}kB"; exit 6; }

# ---- L-251: run root must be world-writable (container runs --user 0:0) ------
[ "$(stat -c '%a' "$BASE")" = "777" ] || { echo "ABORT L-251: run root mode $(stat -c '%a' "$BASE")"; exit 4; }

# ---- image identity by ID, not by tag (DAFOAM_CHARTER s11) -------------------
GOT_ID=$(sudo -n docker images --no-trunc --format '{{.ID}}' "$IMG" | head -1)
[ "$GOT_ID" = "$IMG_ID" ] || { echo "ABORT: image id $GOT_ID != registered $IMG_ID"; exit 4; }

# ---- G8 cold start, verified BEFORE the launch, not after -------------------
sudo -n rm -rf "$BASE/$ARM/processor"* "$BASE/$ARM"/dRdWColoring_*.bin "$BASE/$ARM/reports" 2>/dev/null
for bad in "$BASE/$ARM/1000" "$BASE/$ARM/250" "$BASE/$ARM/500" "$BASE/$ARM/750" "$BASE/$ARM/reports"; do
  [ -e "$bad" ] && { echo "ABORT G8: $bad exists"; exit 5; }
done
[ -f "$BASE/$ARM/0/U" ] || { echo "ABORT G8: $ARM/0/U missing"; exit 5; }
echo "G8 OK ($ARM): no written time dirs, no processor*, no reports/, 0/ present"

: > "$RSSF"
T0=$(date -u +%s)
timeout "$TMO" sudo -n docker run --name "$NAME" \
    --user 0:0 --cpus=1 --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"IDWARP_IMPORTED_FROM:\",p); print(\"IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     mpirun --allow-run-as-root -np 1 -x PYTHONPATH python runScript.py -task $TASK -optimizer IPOPT" \
    > "$LOG" 2>&1 &
DPID=$!

# ---- RECORD-ONLY RSS sampler.  It never kills anything. ---------------------
( while kill -0 $DPID 2>/dev/null; do
    s=$(sudo -n docker stats --no-stream --format '{{.MemUsage}}' "$NAME" 2>/dev/null | head -1)
    [ -n "$s" ] && echo "$(date -u +%FT%TZ) $ARM $s" >> "$RSSF"
    sleep 15
  done ) &
MPID=$!
wait $DPID; rc=$?
kill $MPID 2>/dev/null; wait $MPID 2>/dev/null
T1=$(date -u +%s); W=$((T1-T0))

# ---- the kernel's own verdict, read BEFORE the container is removed (8.2) ---
CID=$(sudo -n docker inspect --format '{{.Id}}' "$NAME" 2>/dev/null)
INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
CGPEAK=NOT_MEASURED
for c in "/sys/fs/cgroup/system.slice/docker-${CID}.scope/memory.peak" \
         "/sys/fs/cgroup/docker/${CID}/memory.peak"; do
  if [ -r "$c" ]; then CGPEAK=$(cat "$c"); break; fi
done
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$RSSF" "$BASE/$ARM" 2>/dev/null

# ---- peak RSS: INITIALISED, and a missing/empty sample file REFUSES ---------
PEAK=NOT_MEASURED
if [ -s "$RSSF" ]; then
  P=$(awk '{v=$3;
            if (v ~ /GiB/) { sub("GiB","",v); print v+0 }
            else if (v ~ /MiB/) { sub("MiB","",v); print (v+0)/1024 }
            else if (v ~ /KiB/) { sub("KiB","",v); print (v+0)/1048576 }}' "$RSSF" | sort -g | tail -1)
  if [ -n "$P" ]; then PEAK="$P"; else PEAK=REFUSED_UNPARSEABLE; fi
else
  PEAK=REFUSED_NO_SAMPLES
fi
AVAIL_POST=$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)

{
echo "ARM=$ARM TASK=$TASK IMG=$IMG IMG_ID=$IMG_ID rc=$rc wall_s=$W ranks=1 core_min=$(python3 -c "print(round($W/60.0,3))") inspect(exit,oomkilled)=[$INSPECT] cgroup_memory_peak_B=$CGPEAK peak_rss_GiB=$PEAK memavail_pre_kB=$AVAIL memavail_post_kB=$AVAIL_POST cap=$MEM stamp=$STAMP"
grep -a "IDWARP_SO_MD5" "$LOG" | head -1
grep -a "transonicPCOption " "$LOG" | head -1
grep -a "primalMinResTolDiff " "$LOG" | head -1
grep -a "^nProcs" "$LOG" | head -1
grep -a "Mesh region0 size" "$LOG" | head -1
grep -a "D8_DVS " "$LOG" | head -1
grep -a "D8_COLD_CD\|D8_START_CD\|D8_FINAL_CD\|FD_BASELINE_CD" "$LOG" | head -4
if grep -aq "IDWARP_SO_MD5: $EXPECT_MD5" "$LOG"; then echo "ASSERT_MD5 OK"; else echo "ASSERT_MD5 FAIL -- ARM VOID"; fi
} | tee -a "$BASE/ledger.txt"
exit $rc
