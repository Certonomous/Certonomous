#!/usr/bin/env bash
# Curriculum D2 arm launcher (optimizer A/B on the D1 problem).
#
# Derived from `d1_run_arm.sh` (md5 7571afabecd7760357f3a817a3de07d3) in D1's
# run root, with exactly TWO registered changes and no others:
#   (1) BASE points at D2's own run root;
#   (2) an -optimizer argument is passed through to the frozen run script.
# The marker greps still read D1_* because the run script IS D1's script,
# byte-identical (md5 4c9811d16f344bc23136981cd6092d8f).  Renaming a marker
# would break the md5 identity that arm A's whole evidentiary value rests on.
#
# Frozen discipline, inherited verbatim from D1:
#   L-251  --user 0:0 pinned; run root is mode 0777 (asserted below)
#   L-252  per-invocation STAMP on every name; test -s + .ok.STAMP provenance
#   8.1    kernel-only stop: --memory == --memory-swap, --oom-score-adj=500,
#          per-stage timeout.  NO watcher process is started, by design.
#   8.2    no --rm, so docker inspect .State.OOMKilled survives the arm
set -uo pipefail
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab
ARM="$1"; IMG="$2"; TASK="$3"; OPT="$4"; TMO="$5"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d2_${ARM}_${STAMP}"
LOG="$BASE/${ARM}_${STAMP}.log"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "L-251 FAIL: run root mode $(stat -c '%a' "$BASE")"; exit 4; }

# ---- staged-instrument identity, re-asserted before every launch -----------
echo "4c9811d16f344bc23136981cd6092d8f  $BASE/d1_opt_runScript.py" | md5sum -c - || exit 4
echo "7e454d2f1830a40086465d9b5c57a941  $BASE/d1_fd_endpoint.py"   | md5sum -c - || exit 4

# ---- stage a pristine copy of base/ for this arm ---------------------------
sudo -n rm -rf "$BASE/$ARM" 2>/dev/null
cp -a "$BASE/base" "$BASE/$ARM" || exit 4
cp -a "$BASE/d1_fd_endpoint.py" "$BASE/d1_opt_runScript.py" "$BASE/$ARM/" || exit 4

# ---- G8 cold start, verified BEFORE the launch, not after ------------------
for bad in "$BASE/$ARM/0.0001" "$BASE/$ARM/reports"; do
  test -e "$bad" && { echo "G8 FAIL: $bad exists"; exit 5; }
done
test -n "$(ls -d "$BASE/$ARM"/processor* 2>/dev/null)" && { echo "G8 FAIL: processor* present"; exit 5; }
test -f "$BASE/$ARM/0/U" || { echo "G8 FAIL: 0/U missing"; exit 5; }
echo "G8 OK ($ARM): no 0.0001, no processor*, no reports/, 0/ present"

ENVS=""
for v in D1_ETA D1_ENDPOINT_JSON D1_ENDPOINT_IN D1_ENDPOINT_OUT; do
  if [ -n "${!v:-}" ]; then ENVS="$ENVS -e $v=${!v}"; fi
done

T0=$(date -u +%s)
timeout "$TMO" sudo -n docker run --name "$NAME" \
    --user 0:0 --cpus=1 --memory=6g --memory-swap=6g --oom-score-adj=500 \
    $ENVS -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D1_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"IDWARP_IMPORTED_FROM:\",p); print(\"IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     ( command -v /usr/bin/time >/dev/null && echo D1_USRBIN_TIME: present || echo D1_USRBIN_TIME: absent ) && \
     mpirun --allow-run-as-root -np 1 -x PYTHONPATH python d1_opt_runScript.py -task $TASK -optimizer $OPT" \
    > "$LOG" 2>&1
rc=$?
T1=$(date -u +%s)
WALL=$((T1-T0))

# ---- kernel's own verdict, read before the container is removed (8.2) -----
INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$BASE/$ARM" 2>/dev/null

CORE_MIN=$(python3 -c "print(round($WALL/60.0,3))")
RSS=$(grep -aoE 'D1_[A-Z_]*MAXRSS_GiB [0-9.]+' "$LOG" | tail -1 | awk '{print $2}')
echo "ARM=$ARM IMG=$IMG TASK=$TASK OPT=$OPT rc=$rc wall_s=$WALL ranks=1 core_min=$CORE_MIN inspect(exit,oomkilled)=[$INSPECT] maxrss_GiB=${RSS:-NOT_MEASURED} log=$(basename "$LOG")" | tee -a "$BASE/ledger.txt"
grep -a "D1_CONTAINER_UID\|IDWARP_SO_MD5\|D1_USRBIN_TIME" "$LOG" | head -3 | tee -a "$BASE/ledger.txt"
grep -a "nProcs" "$LOG" | head -1 | tee -a "$BASE/ledger.txt"
grep -ao "pyOptSparse_[A-Za-z0-9_]*|" "$LOG" | sort -u | head -3 | tee -a "$BASE/ledger.txt"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP"
exit $rc
