#!/usr/bin/env bash
# D4 ACCEPTANCE-PRIMAL LAUNCHER -- LIMIT 1 of the D4-DEF-4 ruling.
#
# THIS IS A NEW FILE.  The frozen launcher `d4_run_arm.sh` (md5
# 399957c616215c8f1ae078abe2e97958, PREREGISTRATION.md 9a) IS NOT EDITED and is
# not invoked here; its arm table has no acceptance arm and adding one would be
# an edit to a frozen file.  Every discipline that file enforces is carried over
# VERBATIM below -- an INTERNAL cap table, a cap assertion that inverts its own
# arithmetic, image identity BY DIGEST, md5 assertions on every staged
# instrument, `--no-rm` so the KERNEL's exit verdict survives, a passive cgroup
# sampler that can never change a verdict, and a ledger row.
#
# THE LEDGER IS A SEPARATE FILE.  Rows go to `acc_ledger.txt`, NOT `ledger.txt`.
# `d4_grade_SUPPLEMENT.py` grades caps and completion from `ledger.txt` against
# the registered arm set {P1,P2,O,F}; an unregistered row in that file could
# move a gate, and no gate moves for this work (LIMIT 3).
#
# ADDED GUARD, not in the frozen launcher: a MEMORY HEADROOM assertion.  Two
# peer lanes are live.  The box floor is MemAvailable >= 12 GiB, so this arm
# refuses to start unless MemAvailable - memory_cap >= 12 GiB.  A run that would
# push the box under the floor does not get to decide that for itself.
#
# `set -e` does NOT gate at the top level and `( set -e; ... )` does not either.
set -uo pipefail

BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
RANKS=4
ARM=ACC
WORK="$BASE/ACC"

# ---- REGISTERED CAP TABLE (D4_DEF4_REPAIR_PREREGISTRATION.md, verbatim) --
#   arm    core-min cap   memory cap   predicted core-min
#   ACC        80.0           8g            20.0
CAP=80.0
MEM=8g
MEM_GIB=8.0
MEM_FLOOR_GIB=12.0

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER 11) ----
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc

# ---- FROZEN INSTRUMENT HASHES (PREREGISTRATION.md 9a, verbatim) ----------
MD5_RUNSCRIPT=2906d52a5dbed2bacbaeaf85a37d3fe8
MD5_EXTRACT=ee7d3c99fd716da23779cb651961918e

IMG="${1:-}"; CPUSET="${2:-}"
test -n "$IMG"    || { echo "ABORT usage: d4_run_acc.sh <image> <cpuset>"; exit 64; }
test -n "$CPUSET" || { echo "ABORT usage: d4_run_acc.sh <image> <cpuset>"; exit 64; }

# THE CAP ASSERTION.  The enforced wall timeout is DERIVED from the registered
# core-minute cap and the rank count and then re-checked by inverting the
# arithmetic.  No second number in this file can drift from the first.
TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)))") || { echo "ABORT tmo calc"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % ($TMO*$RANKS/60.0))") || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
cap, back = $CAP, $BACKCHECK
if abs(cap-back) > 0.02:
    sys.stderr.write('ABORT CAP MISMATCH registered=%r enforced=%r\n' % (cap, back)); sys.exit(1)
" || { echo "ABORT enforced cap != registered cap"; exit 65; }
echo "D4_CAP_ASSERT arm=$ARM registered_core_min=$CAP ranks=$RANKS enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM"

container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d4_" | tr '\n' ',' | sed 's/,$//'
}

MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D4_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

# ---- THE MEMORY HEADROOM GUARD ------------------------------------------
python3 -c "
import sys
avail, cap, floor = $MEMAVAIL_GIB, $MEM_GIB, $MEM_FLOOR_GIB
if avail - cap < floor:
    sys.stderr.write('ABORT MEM HEADROOM MemAvailable=%.2f GiB - cap=%.2f GiB = %.2f GiB < floor %.2f GiB\n'
                     % (avail, cap, avail-cap, floor)); sys.exit(1)
print('D4_MEM_HEADROOM_OK avail=%.2f cap=%.2f headroom=%.2f floor=%.2f' % (avail, cap, avail-cap, floor))
" || { echo "ABORT memory headroom -- this arm will not push the box under the floor"; exit 5; }

test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 run root mode $(stat -c '%a' "$BASE")"; exit 4; }
test -d "$WORK" || { echo "ABORT $WORK absent -- run d4_stage_ACC.sh first"; exit 5; }
test -f "$WORK/.d4_stage_ACC_copy_epoch" || { echo "ABORT $WORK carries no ACC copy epoch -- the age guard would have no datum"; exit 5; }
AGE_DATUM=$(cat "$WORK/.d4_stage_ACC_copy_epoch")
echo "D4_AGE_DATUM arm=$ARM copy_epoch=$AGE_DATUM"

# ---- staged-instrument identity, re-asserted before the launch ----------
echo "$MD5_RUNSCRIPT  $BASE/d4_opt_runScript.py"  | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_EXTRACT  $BASE/d4_extract_endpoint.py" | md5sum -c - || { echo "ABORT extract md5"; exit 4; }
( cd "$BASE" && md5sum -c d4_repair_instruments.md5 ) || { echo "ABORT repair-instrument md5"; exit 4; }

# ---- image identity by DIGEST -------------------------------------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1)       WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  dafoam/opt-packages:latest) WANT=$IMG_SHIPPED_DIGEST; ROW=SHIPPED ;;
  *) echo "ABORT image $IMG is not a registered row"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }
echo "D4_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

# ---- the answer files must not pre-exist --------------------------------
for bad in "$WORK/d4_accept_primal.json" "$WORK/d4_endpoint_dvs.json" \
           "$WORK/d4_endpoint_dvs_PHYSICAL.json" "$WORK/d4_endpoint_dvs_DRIVERSCALED.json"; do
  test -e "$bad" && { echo "ABORT G-COLD $bad exists BEFORE the arm that must produce it"; exit 5; }
done
echo "D4_G_COLD OK arm=$ARM -- no answer file present"

cp -a "$BASE/d4_opt_runScript.py" "$BASE/d4_extract_endpoint.py" \
      "$BASE/d4_endpoint_locus.py" "$BASE/d4_endpoint_physical.py" \
      "$BASE/d4_accept_primal.py" "$WORK/" || { echo "ABORT stage instruments"; exit 4; }

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d4_${ARM}_${STAMP}"
LOG="$BASE/${ARM}_${STAMP}.log"
CPUSAMPLE="$BASE/${ARM}_${STAMP}.cpu.jsonl"

CMD="rm -f d4_placement_rank*.json && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings python -c \"
import json,os
from mpi4py import MPI
r=MPI.COMM_WORLD.rank
json.dump({'rank':r,'affinity':sorted(os.sched_getaffinity(0)),'n_cores':len(os.sched_getaffinity(0)),'pid':os.getpid()}, open('d4_placement_rank%d.json'%r,'w'))
\" && python d4_endpoint_physical.py --age-datum $AGE_DATUM && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d4_accept_primal.py"

# DELIVERED CORES ARE MEASURED, NOT INFERRED FROM THE QUOTA FLAG.  Passive
# reader: it starts nothing, kills nothing, and an absent sample file is
# reported as NOT_MEASURED, never as a passing placement gate.
(
  for _ in $(seq 1 100000); do
    cid=$(sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | head -1)
    if [ -n "$cid" ]; then break; fi
    sleep 1
  done
  cg=""
  for cand in /sys/fs/cgroup/system.slice/docker-${cid}*.scope/cpu.stat \
              /sys/fs/cgroup/cpu/docker/${cid}*/cpuacct.usage; do
    if [ -e "$cand" ]; then cg="$cand"; break; fi
  done
  if [ -z "$cg" ]; then echo '{"delivered_cores":null,"note":"cgroup path not found"}' >> "$CPUSAMPLE"; exit 0; fi
  prev=""; prevt=""
  while sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | grep -q .; do
    now=$(date +%s.%N)
    if [ "$(basename "$cg")" = "cpu.stat" ]; then
      u=$(awk '/^usage_usec/{print $2}' "$cg" 2>/dev/null)
      t=$(awk '/^throttled_usec/{print $2}' "$cg" 2>/dev/null)
      n=$(awk '/^nr_throttled/{print $2}' "$cg" 2>/dev/null)
    else
      u=$(( $(cat "$cg" 2>/dev/null || echo 0) / 1000 )); t=0; n=0
    fi
    if [ -n "$prev" ] && [ -n "$u" ]; then
      python3 -c "
import json
du=($u-$prev)/1e6; dt=$now-$prevt
print(json.dumps({'t':round($now,2),'delivered_cores':round(du/dt,4) if dt>0 else None,'throttled_usec':$t,'nr_throttled':$n}))
" >> "$CPUSAMPLE" 2>/dev/null
    fi
    prev=$u; prevt=$now
    sleep 10
  done
) &
SAMPLER=$!

T0=$(date -u +%s)
timeout "$TMO" sudo -n docker run --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4_IDWARP_IMPORTED_FROM:\",p); print(\"D4_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     $CMD" \
    > "$LOG" 2>&1
rc=$?
T1=$(date -u +%s)
WALL=$((T1-T0))
kill $SAMPLER 2>/dev/null; wait $SAMPLER 2>/dev/null
SIBLINGS_POST=$(container_census)
DELIVERED=$(python3 -c "
import json,sys,os
p='$CPUSAMPLE'
if not os.path.exists(p): print('NOT_MEASURED'); sys.exit()
v=[]; thr=0
for line in open(p):
    try: d=json.loads(line)
    except Exception: continue
    if d.get('delivered_cores') is not None: v.append(d['delivered_cores'])
    thr=max(thr, d.get('nr_throttled') or 0)
print('%s n=%d max_nr_throttled=%d' % (('%.4f'%(sum(v)/len(v)) if v else 'NOT_MEASURED'), len(v), thr))
" 2>/dev/null)

INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$WORK" 2>/dev/null

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/acc_ledger.txt"
{
  echo "ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM inspect(exit,oomkilled)=[$INSPECT] memavail_pre_GiB=$MEMAVAIL_GIB memavail_post_GiB=$MEMAVAIL_POST cpuset=$CPUSET delivered_cores_mean=[$DELIVERED] siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] age_datum=$AGE_DATUM log=$(basename "$LOG") stamp=$STAMP"
  grep -a "D4_CONTAINER_UID\|D4_IDWARP_SO_MD5" "$LOG" | head -2
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc
