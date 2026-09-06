#!/usr/bin/env bash
# W4 CBFS RE-ANCHOR single-run launcher. Bills cpus x wall to THIS arm's OWN ledger.csv.
#
# DERIVATION: this file is the S1-FD-PLATEAU run_one.sh (I2, md5
# 1b269bb9b95cafe5ce3945b9e665c5c3, prereg 4.1) with exactly the retargeting edits
# CLAUDE.md rule 12 forces and prereg 4.1 / 5.2 register, and NOTHING ELSE:
#   (1) BASE      -> W4-reanchor, so billing lands in THIS arm's ledger (rule 12);
#   (2) container name prefix s1fdp_ -> w4ra_, the name prereg 5.2 registers, so it
#       cannot collide with the S1 archive (prereg 3 REGISTERED REFUSAL);
#   (3) working dir /mnt/cbfs_inv -> /mnt/cbfs_beta, W4's case state, NOT S1's
#       (prereg 3: "this arm runs on W4's case state, cbfs_beta, and on nothing else").
# The docker invocation, image (dafoam-subpclu:v1), --cpus, --memory=22g,
# -e DAFOAM_SUBPC_TYPE=lu (prereg 5.2 requires it on EVERY leg incl. the adjoint),
# -np 4, the HARD WALL TIMEOUT and the runScript argv are UNCHANGED, because
# reproducing the archived 1e-8 protocol is the whole point (prereg 4.2 ruling).
set -uo pipefail
BASE=/home/ubuntu/certonomous-runs/W4-reanchor
TAG="$1"; CPUS="$2"; TIMEOUT_S="$3"; shift 3
NAME="w4ra_${TAG}"
start=$(date -u +%s)
echo "$TAG,START,$start,$CPUS" >> "$BASE/ledger.csv"
# rc is captured IMMEDIATELY after the timeout+docker line and never around a setsid
# wrapper (memory: `setsid timeout cmd` exits 0 for every outcome).
timeout --signal=TERM --kill-after=30 "$TIMEOUT_S" \
  sudo docker run --rm --name "$NAME" --cpus="$CPUS" --memory=22g \
    -e DAFOAM_SUBPC_TYPE=lu -v "$BASE":/mnt -w /mnt/cbfs_beta \
    dafoam-subpclu:v1 bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun --allow-run-as-root -np 4 python runScript.py $*" \
    > "$BASE/log.${TAG}" 2>&1
rc=$?
# A TERMed `docker run` can leave the container alive and still billing. Reap it.
sudo docker rm -f "$NAME" >/dev/null 2>&1 || true
end=$(date -u +%s)
sudo chown -R ubuntu:ubuntu "$BASE" 2>/dev/null || true
cm=$(awk "BEGIN{printf \"%.2f\", ($end-$start)*$CPUS/60}")
echo "$TAG,END,$end,$CPUS,rc=$rc,wall=$((end-start)),core_min=$cm" >> "$BASE/ledger.csv"
echo "== $TAG rc=$rc wall=$((end-start))s cpus=$CPUS core_min=$cm $(date -u +%FT%TZ)"
exit $rc
