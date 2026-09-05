#!/usr/bin/env bash
# S1 FD-PLATEAU single-run launcher. Bills cpus x wall to this item's OWN ledger.csv.
#
# PROVENANCE: this file is /home/ubuntu/certonomous-runs/S1-cbfs-reinversion/run_one.sh
# with exactly three changes, and nothing else:
#   (1) BASE      -> this item's run root, so billing lands in THIS item's ledger;
#   (2) container name prefix s1re_ -> s1fdp_, so it cannot collide with the archive;
#   (3) a HARD WALL TIMEOUT, passed in as TIMEOUT_S, which is how CLAUDE.md rule 12's
#       "an overrun STOPS the run" is made mechanical rather than promised.
# The docker invocation, image, --cpus, --memory, -np and the runScript argv are
# UNCHANGED, because reproducing the archived fd8 protocol is the whole point.
set -uo pipefail
BASE=/home/ubuntu/certonomous-runs/S1-fd-plateau
TAG="$1"; CPUS="$2"; TIMEOUT_S="$3"; shift 3
NAME="s1fdp_${TAG}"
start=$(date -u +%s)
echo "$TAG,START,$start,$CPUS" >> "$BASE/ledger.csv"
# rc is captured IMMEDIATELY after the timeout+docker line and never around a setsid
# wrapper (memory: `setsid timeout cmd` exits 0 for every outcome).
timeout --signal=TERM --kill-after=30 "$TIMEOUT_S" \
  sudo docker run --rm --name "$NAME" --cpus="$CPUS" --memory=22g \
    -e DAFOAM_SUBPC_TYPE=lu -v "$BASE":/mnt -w /mnt/cbfs_inv \
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
