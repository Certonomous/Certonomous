#!/usr/bin/env bash
# D9 FD REPLICATION DRIVER.  NOT A FROZEN INSTRUMENT.  Written AFTER first compute and
# disclosed as such.  It edits NO frozen file and it FEEDS NO GATE: its output is crash
# triage -- evidence about REPRODUCIBILITY -- and the D9 verdict is graded from the
# ORIGINAL run tree by d9_grade_SUPPLEMENT.py, never from this one.
#
# WHY IT EXISTS.  Three of the four registered endpoint FD stages of run
# 20260825T181838Z_2370464 exited rc=1 with `AnalysisError: Mesh quality error!`.
# A crash is a FINDING until triage says otherwise.  Two things need proving:
#   1. the crash is DETERMINISTIC (same component index, same maxNonOrth), not a
#      contention or fleet-kill artifact;
#   2. the ONE surviving table (h=1e-5) is itself REPRODUCIBLE.
#
# THE DOCKER INVOCATION BELOW IS COPIED VERBATIM FROM THE FROZEN LAUNCHER'S run_stage
# (d9_stage_and_run.sh:115-120), flags included, so the replication is faithful.
# The endpoint design point is the SAME opt_dv.json the original FD chain was handed.
set -uo pipefail

H="${1:?usage: d9_fd_replicate.sh <fdStep> <tag> <cpuset> <base>}"
TAG="${2:?}"; CPUSET="${3:?}"; BASE="${4:?}"
IMG="dafoam-idwarp-rot:v1"
SRC="/home/ubuntu/certonomous-runs/W5-regrade/a5pl_stock"
RUNPY="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_D9/d9_run_script.py"
ORIG="/home/ubuntu/certonomous-runs/CURRICULUM-D9-a5-ubend-opt"
TMO_FD=1200
STAMP="$(basename "$BASE")"
arm="$BASE/$TAG"
LEDGER="$BASE/ledger_${TAG}.txt"

# ---- MEMORY GUARD.  dafoam is the memory-limited family; a batch that OOMs is worse
# ---- than a batch that queues.  Hold until >= 6 GiB is available.
for i in $(seq 1 120); do
  AVAIL=$(free -g | awk '/^Mem:/{print $7}')
  [ "$AVAIL" -ge 6 ] && break
  echo "MEMORY_HOLD $TAG available=${AVAIL}GiB < 6GiB, waiting" | tee -a "$LEDGER"
  sleep 15
done
AVAIL=$(free -g | awk '/^Mem:/{print $7}')
[ "$AVAIL" -ge 6 ] || { echo "ABORT $TAG: memory guard never cleared (available=${AVAIL}GiB)" | tee -a "$LEDGER"; exit 1; }
echo "MEMORY_GUARD_CLEARED $TAG available=${AVAIL}GiB >= 6GiB at launch" | tee -a "$LEDGER"

# ---- THE GUARD.  An existing arm is EVIDENCE, never something to delete.
[ -e "$arm" ] && { echo "ABORT: $arm already exists; guards refuse a case whose run directory exists"; exit 1; }
mkdir -p "$arm" || { echo "ABORT: cannot mkdir $arm"; exit 1; }
cp -a "$SRC"/0 "$SRC"/0.orig "$SRC"/constant "$SRC"/system "$SRC"/FFD "$arm"/ 2>/dev/null \
  || { echo "ABORT: cannot stage case tree"; exit 1; }
cp "$RUNPY" "$arm"/runScript.py || { echo "ABORT: cannot stage run script"; exit 1; }
cp "$ORIG/opt_dv.json" "$arm"/opt_dv.json || { echo "ABORT: cannot stage endpoint dv"; exit 1; }
chmod 666 "$arm"/opt_dv.json
# COLD-START PROOF, before any container starts (same substitute as the frozen launcher).
[ -e "$arm/d9_out.json" ] && { echo "ABORT: answer file present before launch"; exit 1; }
for t in $(ls -1 "$arm" 2>/dev/null | grep -E '^[0-9]+(\.[0-9]+)?$' | grep -v '^0$'); do
  echo "ABORT: time directory $t present before launch"; exit 1
done
[ -e "$arm/0/U.gz" ] && { echo "ABORT: 0/U.gz present before launch"; exit 1; }
[ -f "$arm/0/U" ]    || { echo "ABORT: 0/U absent after staging"; exit 1; }
chmod -R 777 "$arm"
echo "COLDSTART_PROVED stage=$TAG answer-file absent, no time dir, no 0/U.gz, before container start" | tee -a "$LEDGER"
echo "ENDPOINT_DV md5=$(md5sum "$arm"/opt_dv.json | cut -d' ' -f1) (same endpoint as the original FD chain)" | tee -a "$LEDGER"

cname="d9rep_${TAG}_${STAMP}"
log="$BASE/${TAG}_${STAMP}.log"
t0=$(date +%s)
timeout "$TMO_FD" sudo -n docker run --name "$cname" --user 0:0 \
    --cpuset-cpus="$CPUSET" --cpus=1 --memory=3g --memory-swap=3g --oom-score-adj=500 \
    -e PYTHONHASHSEED=0 \
    -v "$arm":/mnt -w /mnt "$IMG" \
    bash -lc "source /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun --allow-run-as-root -np 1 -x PYTHONPATH -x PYTHONHASHSEED python runScript.py -task=check_totals -dvFile=opt_dv.json -fdStep=$H -out=d9_out.json" \
    > "$log" 2>&1
rc=$?
t1=$(date +%s); wall=$((t1-t0))
insp=$(sudo -n docker inspect -f '{{.State.ExitCode}} {{.State.OOMKilled}}' "$cname" 2>/dev/null); [ -n "$insp" ] || insp="NA NA"
peak=$(sudo -n docker inspect -f '{{.HostConfig.Memory}}' "$cname" 2>/dev/null)
cm=$(python3 -c "print(round($wall*1/60.0,4))")
nskew=$(grep -c "Max skewness" "$log" 2>/dev/null || echo 0)
echo "REPLICATE STAGE=$TAG fdStep=$H rc=$rc wall_s=$wall ranks=1 core_min=$cm cpuset=$CPUSET inspect(exit,oomkilled)=[$insp] memcap_bytes=$peak skew_blocks=$nskew log=$(basename "$log")" | tee -a "$LEDGER"
exit $rc
