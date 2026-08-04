#!/usr/bin/env bash
# run_one.sh <tag> <stock|patched> [VIDX]
set -uo pipefail
SCR=/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/indep
CLONE=/home/ubuntu/certonomous-runs/W5-patch/idwarp
TAG="$1"; MODE="$2"; VIDX="${3:-8}"

# clean root-level numbered time dirs (never 0/ or 0.orig/), as the lab harness does
cd "$SCR/case"
sudo rm -rf processor*/0.0001 2>/dev/null || true
for d in $(ls -d */ 2>/dev/null | grep -E '^[0-9]' | tr -d '/'); do
    case "$d" in 0|0.orig) ;; *) sudo rm -rf "./$d" ;; esac
done

if [ "$MODE" = "patched" ]; then
    PYP="export PYTHONPATH=/patched-idwarp:\$PYTHONPATH &&"
else
    PYP=""
fi

echo "== [$TAG] mode=$MODE VIDX=$VIDX $(date -u +%FT%TZ)"
sudo docker run --rm --cpus=4 --memory=6g \
    -v "$SCR/case":/work -v "$CLONE":/patched-idwarp -w /work \
    -e VIDX="$VIDX" \
    dafoam/opt-packages:latest bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && $PYP mpirun --allow-run-as-root -np 4 -x VIDX -x PYTHONPATH python supervisor_verify_idx8.py" \
    > "$SCR/${TAG}.log" 2>&1
rc=$?
sudo chown -R ubuntu:ubuntu "$SCR" 2>/dev/null || true
echo "== [$TAG] rc=$rc $(date -u +%FT%TZ)"
grep -a '^SUPV' "$SCR/${TAG}.log" | head -30
exit $rc
