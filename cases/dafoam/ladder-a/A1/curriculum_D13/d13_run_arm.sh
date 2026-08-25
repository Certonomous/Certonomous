#!/usr/bin/env bash
# Curriculum D13 arm launcher: ONE perturbed start of the D1 problem.
#
# Derived from `curriculum_D2/d2_run_arm.sh` (md5 4629c57e64863db21625c6c61fd46e7d)
# with exactly FIVE registered changes and no others:
#   (1) BASE points at D13's own run root;
#   (2) three instruments are staged and md5-asserted, not two;
#   (3) the D13 env channel (D13_ETA, D13_START_ID, D13_ENDPOINT_JSON);
#   (4) the run script is `d13_opt_runScript.py`;
#   (5) the maxrss grep also matches the D13_ marker.
#
# Frozen discipline, inherited verbatim from D1 and D2:
#   L-251  --user 0:0 pinned; run root is mode 0777 (asserted below)
#   L-252  per-invocation STAMP on every name; test -s + .ok.STAMP provenance
#   8.1    kernel-only stop: --memory == --memory-swap, --oom-score-adj=500,
#          per-stage timeout.  NO watcher process is started, by design.
#   8.2    no --rm, so docker inspect .State.OOMKilled survives the arm
#
# `set -e` IS NOT USED and would not gate here.  Every step that must stop the
# arm carries its own explicit `|| exit N`.
set -uo pipefail
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D13-a1-basin-restart
ARM="$1"; IMG="$2"; TASK="$3"; OPT="$4"; TMO="$5"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d13_${ARM}_${STAMP}"
LOG="$BASE/${ARM}_${STAMP}.log"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "L-251 FAIL: run root mode $(stat -c '%a' "$BASE")"; exit 4; }

# ---- staged-instrument identity, re-asserted before every launch -----------
echo "bf6500c7ef89f7f5c8be02292e274181  $BASE/d13_opt_runScript.py" | md5sum -c - || exit 4
echo "7e454d2f1830a40086465d9b5c57a941  $BASE/d1_fd_endpoint.py"    | md5sum -c - || exit 4
echo "e96d77ff53e356d67f54a4cc46338c0e  $BASE/d13_basin.py"         | md5sum -c - || exit 4

# ---- stage a pristine copy of base/ for this arm ---------------------------
sudo -n rm -rf "$BASE/$ARM" 2>/dev/null
cp -a "$BASE/base" "$BASE/$ARM" || exit 4
cp -a "$BASE/d1_fd_endpoint.py" "$BASE/d13_opt_runScript.py" "$BASE/d13_basin.py" "$BASE/$ARM/" || exit 4

# ---- G8 cold start, verified BEFORE the launch, not after ------------------
for bad in "$BASE/$ARM/0.0001" "$BASE/$ARM/reports" "$BASE/$ARM/opt_IPOPT.txt" "$BASE/$ARM/endpoint_d13.json"; do
  test -e "$bad" && { echo "G8 FAIL: $bad exists"; exit 5; }
done
test -n "$(ls -d "$BASE/$ARM"/processor* 2>/dev/null)" && { echo "G8 FAIL: processor* present"; exit 5; }
test -f "$BASE/$ARM/0/U" || { echo "G8 FAIL: 0/U missing"; exit 5; }
# AGE GUARD reference: touch the arm's own 0/U LAST at staging, so it dates the
# run allowed to produce the answer (CLAUDE.md rule 4).
touch "$BASE/$ARM/0/U" || exit 5
echo "G8 OK ($ARM): no 0.0001, no processor*, no reports/, no stale endpoint, 0/ present, age reference touched"

ENVS=""
for v in D13_ETA D13_START_ID D13_ENDPOINT_JSON; do
  if [ -n "${!v:-}" ]; then ENVS="$ENVS -e $v=${!v}"; fi
done

T0=$(date -u +%s)
timeout "$TMO" sudo -n docker run --name "$NAME" \
    --user 0:0 --cpus=1 --memory=6g --memory-swap=6g --oom-score-adj=500 \
    $ENVS -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D1_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"IDWARP_IMPORTED_FROM:\",p); print(\"IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     mpirun --allow-run-as-root -np 1 -x PYTHONPATH python d13_opt_runScript.py -task $TASK -optimizer $OPT" \
    > "$LOG" 2>&1
rc=$?
T1=$(date -u +%s)
WALL=$((T1-T0))

# ---- kernel's own verdict, read before the container is removed (8.2) -----
INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$BASE/$ARM" 2>/dev/null

CORE_MIN=$(python3 -c "print(round($WALL/60.0,3))")
RSS=$(grep -aoE 'D13?_[A-Z_0-9]*MAXRSS_GiB [0-9.]+' "$LOG" | tail -1 | awk '{print $2}')
echo "ARM=$ARM IMG=$IMG TASK=$TASK OPT=$OPT rc=$rc wall_s=$WALL ranks=1 core_min=$CORE_MIN inspect(exit,oomkilled)=[$INSPECT] maxrss_GiB=${RSS:-NOT_MEASURED} log=$(basename "$LOG")" | tee -a "$BASE/ledger.txt"
grep -a "D1_CONTAINER_UID\|IDWARP_SO_MD5" "$LOG" | head -2 | tee -a "$BASE/ledger.txt"
grep -a "nProcs" "$LOG" | head -1 | tee -a "$BASE/ledger.txt"
grep -a "D13_IPOPT_EXIT\|D13_IPOPT_MAJORS\|D13_DRIVER_WALL_S" "$LOG" | head -3 | tee -a "$BASE/ledger.txt"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP"
exit $rc
