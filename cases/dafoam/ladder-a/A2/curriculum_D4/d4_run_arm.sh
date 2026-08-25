#!/usr/bin/env bash
# Curriculum D4 arm launcher -- MACH wing constrained CD minimisation at fixed CL.
#
# Derived from `cases/dafoam/ladder-a/A1/curriculum_D2/d2_run_arm.sh` (this
# family's proven container pattern) with the registered changes: D4's own run
# root, np=4 instead of np=1, a per-arm CAP TABLE that is INTERNAL to this file,
# and a decomposition-determinism arm.
#
# CAP DISCIPLINE (the failure this file exists not to repeat).  A peer lane
# today registered a 3.0 core-min cap and its launcher enforced 6.0 by
# copy-forward with no assertion.  Here the caps are NOT arguments.  They are
# constants in the table below, the table is reproduced verbatim in
# PREREGISTRATION.md §8, this file's md5 is frozen there, and the launcher
# ASSERTS that the wall timeout it is about to enforce equals CAP_CORE_MIN*60/4
# to the second.  A cap that disagrees aborts the arm before the container runs.
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call and
# `( set -e; ... )` does not gate either.  Every step below gates explicitly
# with `|| { echo ABORT...; exit N; }`.
#
# 8.2: NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives
# the arm and the KERNEL's verdict is read, not the harness's.
set -uo pipefail

BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
RANKS=4

# ---- REGISTERED CPU PLACEMENT (PREREGISTRATION.md §5b, verbatim) ---------
# `mpirun` inside a `--cpus=N` container binds rank 0 to the FIRST CORE OF THE
# HOST TOPOLOGY.  Concurrent containers then land on the same host core and
# throughput collapses as 1/N while the box reports itself idle -- MEASURED by
# the D13 lane 2026-08-25: affinity=0 on all three concurrent arms, 0.250 cores
# delivered against a 1.0-core quota, host 61 % idle, throughput moved 4x on a
# control that changed only the sibling count.  `--cpus=4` does NOT hand out
# four distinct cores.  So: PIN, and MEASURE the placement rather than infer it
# from the flag that was passed.
#
# Cores 5,6,7,9 were measured idle at freeze time (2026-08-25 ~17:45Z) and
# 5,6,7 sit OUTSIDE the host-affinity mask 8-15 of the only live sibling
# container (d8_opt, A6 CRM, 1.0-core quota).  Cores 1,2,3,4,8,12,14 carried
# native peer load and 0 is the default landing core the defect names.
CPUSET=5,6,7,9

# For containerised MPI the conditioning variable is CONCURRENT CONTAINERS, not
# loadavg -- `uptime` will lie.  Censused before and after every arm.
container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d4_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md §8, verbatim) ---------------
#   arm   core-min cap    memory cap
#   P1        5.0             4g
#   P2       55.0            12g
#   O       620.0            12g
#   F       120.0            12g
cap_core_min() {
  case "$1" in
    P1) echo 5.0 ;;
    P2) echo 55.0 ;;
    O)  echo 620.0 ;;
    F)  echo 120.0 ;;
    *)  echo "" ;;
  esac
}
cap_memory() {
  case "$1" in
    P1) echo 4g ;;
    P2|O|F) echo 12g ;;
    *) echo "" ;;
  esac
}

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER §11) ---
# PATCHED IDWarp : dafoam-idwarp-rot:v1
#   sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
# SHIPPED (stock): dafoam/opt-packages:latest
#   sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc

# ---- FROZEN INSTRUMENT HASHES (PREREGISTRATION.md §9, verbatim) ----------
MD5_RUNSCRIPT=2906d52a5dbed2bacbaeaf85a37d3fe8
MD5_FD=c6112b0ec3bfdb5287345e350500f64a
MD5_EXTRACT=ee7d3c99fd716da23779cb651961918e

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: d4_run_arm.sh <P1|P2|O|F> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: d4_run_arm.sh <P1|P2|O|F> <image>"; exit 64; }

CAP=$(cap_core_min "$ARM")
MEM=$(cap_memory "$ARM")
test -n "$CAP" || { echo "ABORT unknown arm $ARM -- no registered cap"; exit 64; }
test -n "$MEM" || { echo "ABORT unknown arm $ARM -- no registered memory cap"; exit 64; }

# THE ASSERTION.  The enforced wall timeout is DERIVED from the registered
# core-minute cap and the registered rank count, and is then re-checked
# against that cap by inverting the arithmetic.  There is no second number
# anywhere in this file that could drift from the first.
TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)))") || { echo "ABORT tmo calc"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % ($TMO*$RANKS/60.0))") || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
cap, back = $CAP, $BACKCHECK
if abs(cap-back) > 0.02:
    sys.stderr.write('ABORT CAP MISMATCH registered=%r enforced=%r\n' % (cap, back)); sys.exit(1)
" || { echo "ABORT enforced cap != registered cap"; exit 65; }
echo "D4_CAP_ASSERT arm=$ARM registered_core_min=$CAP ranks=$RANKS enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM"

# ---- host state, read before ranks are claimed ---------------------------
MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D4_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 run root mode $(stat -c '%a' "$BASE")"; exit 4; }

# ---- staged-instrument identity, re-asserted before EVERY launch ---------
echo "$MD5_RUNSCRIPT  $BASE/d4_opt_runScript.py"    | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_FD  $BASE/d4_fd_endpoint.py"             | md5sum -c - || { echo "ABORT fd md5"; exit 4; }
echo "$MD5_EXTRACT  $BASE/d4_extract_endpoint.py"   | md5sum -c - || { echo "ABORT extract md5"; exit 4; }

# ---- image identity by DIGEST, resolved from the local store -------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1)    WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  dafoam/opt-packages:latest) WANT=$IMG_SHIPPED_DIGEST; ROW=SHIPPED ;;
  *) echo "ABORT image $IMG is not a registered row"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }
echo "D4_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d4_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- stage a pristine copy of base/ for arms that need a cold case -------
if [ "$ARM" != "F" ]; then
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/base" "$WORK" || { echo "ABORT stage copy"; exit 4; }
  cp -a "$BASE/d4_opt_runScript.py" "$BASE/d4_fd_endpoint.py" "$BASE/d4_extract_endpoint.py" "$WORK/" || { echo "ABORT stage instruments"; exit 4; }
  # COLD START, verified BEFORE the launch (D2 G8), and the AGE GUARD's datum:
  # 0/ is touched LAST at stage time, so every artifact the run produces must
  # be strictly newer than 0/U or it did not come from this run.
  for bad in "$WORK/reports" "$WORK/OptView.hst" "$WORK/opt_IPOPT.txt" "$WORK/dRdWColoring_4.bin" "$WORK/d4_fd_endpoint.json"; do
    test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
  done
  test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
  test -n "$(ls -d "$WORK"/[0-9]*.[0-9]* 2>/dev/null)" && { echo "ABORT G-COLD time dir present"; exit 5; }
  test -f "$WORK/0/U" || { echo "ABORT G-COLD 0/U missing"; exit 5; }
  touch "$WORK/0"/* || { echo "ABORT age-guard datum"; exit 5; }
  AGE_DATUM=$(stat -c '%Y' "$WORK/0/U")
  echo "$AGE_DATUM" > "$WORK/.d4_age_datum"
  echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM"
else
  test -d "$WORK" || { echo "ABORT arm F expects an existing $WORK from arm O"; exit 5; }
  test -f "$WORK/OptView.hst" || { echo "ABORT arm F: no OptView.hst to read an endpoint from"; exit 5; }
  cp -a "$BASE/d4_fd_endpoint.py" "$BASE/d4_extract_endpoint.py" "$WORK/" || { echo "ABORT stage F instruments"; exit 4; }
  rm -f "$WORK/d4_fd_endpoint.json" "$WORK/d4_fd_endpoint.jsonl" "$WORK/d4_endpoint_dvs.json"
fi

case "$ARM" in
  P1) CMD="rm -rf processor* ; decomposePar -force > d4_decomp_A.log 2>&1 && for p in processor*; do echo \"A \$p \$(head -20 \$p/constant/polyMesh/owner | grep -a note || true)\"; done > /dev/null ; python -c \"
import glob,gzip,io,os,json
def ncells(p):
    b=os.path.join(p,'constant','polyMesh','owner')
    op=gzip.open(b+'.gz','rt') if os.path.exists(b+'.gz') else open(b)
    with op as fh:
        for line in fh:
            if 'nCells' in line:
                return int(line.split('nCells:')[1].split()[0])
    return -1
d={p:ncells(p) for p in sorted(glob.glob('processor*'))}
json.dump(d, open('d4_decomp_A.json','w'), indent=1, sort_keys=True)
print('DECOMP_A', json.dumps(d, sort_keys=True))
\" && rm -rf processor* && decomposePar -force > d4_decomp_B.log 2>&1 && python -c \"
import glob,gzip,json,os
def ncells(p):
    b=os.path.join(p,'constant','polyMesh','owner')
    op=gzip.open(b+'.gz','rt') if os.path.exists(b+'.gz') else open(b)
    with op as fh:
        for line in fh:
            if 'nCells' in line:
                return int(line.split('nCells:')[1].split()[0])
    return -1
d={p:ncells(p) for p in sorted(glob.glob('processor*'))}
json.dump(d, open('d4_decomp_B.json','w'), indent=1, sort_keys=True)
print('DECOMP_B', json.dumps(d, sort_keys=True))
\" && grep -a 'method\|numberOfSubdomains' system/decomposeParDict && rm -f d4_placement_rank*.json && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings python -c \"
import json,os
from mpi4py import MPI
r=MPI.COMM_WORLD.rank
aff=sorted(os.sched_getaffinity(0))
json.dump({'rank':r,'affinity':aff,'n_cores':len(aff),'pid':os.getpid()}, open('d4_placement_rank%d.json'%r,'w'))
\" && cat d4_placement_rank*.json" ;;
  P2) CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d4_opt_runScript.py -task compute_totals" ;;
  O)  CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d4_opt_runScript.py -task run_driver -optimizer IPOPT" ;;
  F)  CMD="python d4_extract_endpoint.py && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d4_fd_endpoint.py" ;;
esac

CPUSAMPLE="$BASE/${ARM}_${STAMP}.cpu.jsonl"
# DELIVERED CORES ARE MEASURED, NOT INFERRED FROM THE QUOTA FLAG.  This sampler
# polls the container's own cgroup cpu.stat and writes cores-delivered to a
# FILE.  It is a passive reader: it starts nothing, kills nothing, and its
# failure cannot change a verdict -- an absent sample file is reported as
# NOT_MEASURED, never as a passing placement gate.
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
import json,sys
du=($u-$prev)/1e6; dt=$now-$prevt
print(json.dumps({'t':round($now,2),'delivered_cores':round(du/dt,4) if dt>0 else None,'throttled_usec':$t,'nr_throttled':$n}))
" >> "$CPUSAMPLE" 2>/dev/null
    fi
    prev=$u; prevt=$now
    sleep 15
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
     ( /usr/bin/time -v true >/dev/null 2>&1 && echo D4_USRBIN_TIME: present || echo D4_USRBIN_TIME: absent ) && \
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
v=[]
thr=0
for line in open(p):
    try: d=json.loads(line)
    except Exception: continue
    if d.get('delivered_cores') is not None: v.append(d['delivered_cores'])
    thr=max(thr, d.get('nr_throttled') or 0)
print('%s n=%d max_nr_throttled=%d' % (('%.4f'%(sum(v)/len(v)) if v else 'NOT_MEASURED'), len(v), thr))
" 2>/dev/null)

# ---- the KERNEL's verdict, read BEFORE the container is removed (8.2) ----
INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$WORK" 2>/dev/null

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/ledger.txt"
{
  echo "ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM inspect(exit,oomkilled)=[$INSPECT] memavail_pre_GiB=$MEMAVAIL_GIB memavail_post_GiB=$MEMAVAIL_POST cpuset=$CPUSET delivered_cores_mean=[$DELIVERED] siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] log=$(basename "$LOG") stamp=$STAMP"
  grep -a "D4_CONTAINER_UID\|D4_IDWARP_SO_MD5\|D4_USRBIN_TIME" "$LOG" | head -3
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc
