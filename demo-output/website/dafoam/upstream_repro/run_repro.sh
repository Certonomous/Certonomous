#!/usr/bin/env bash
# run_repro.sh -- clone-to-result driver for the mesh.warpDeriv reproducers.
#
# Takes nothing but a working Docker and network. Clones the official DAFoam
# tutorials at a pinned commit into a scratch directory, meshes the two cases
# with their own preProcessing.sh, and runs both reproducers.
#
#   ./run_repro.sh [workdir]      (default workdir: ./repro-work)
#
# Requires: docker (with the dafoam/opt-packages:latest image pullable), git.
# Set DOCKER="sudo docker" if your Docker needs sudo.
set -euo pipefail

WORK="${1:-./repro-work}"
HERE="$(cd "$(dirname "$0")" && pwd)"
DOCKER="${DOCKER:-docker}"
IMAGE="dafoam/opt-packages:latest"
TUT_URL="https://github.com/DAFoam/tutorials.git"
TUT_COMMIT="d3b7e38b058aba2a98a74092e15c41ec455c570d"

mkdir -p "$WORK"
WORK="$(cd "$WORK" && pwd)"
echo "== workdir: $WORK"

# --- 1. official tutorials, pinned -----------------------------------------
if [ ! -d "$WORK/tutorials" ]; then
    git clone "$TUT_URL" "$WORK/tutorials"
fi
git -C "$WORK/tutorials" checkout -q "$TUT_COMMIT"
echo "== tutorials at $(git -C "$WORK/tutorials" rev-parse --short HEAD)"

# --- helpers ----------------------------------------------------------------
indocker() {  # indocker <case_dir> <command string>
    $DOCKER run --rm --cpus=4 --memory=6g \
        -v "$1":/home/dafoamuser/mount -w /home/dafoamuser/mount \
        "$IMAGE" bash -lc "source /home/dafoamuser/dafoam/loadDAFoam.sh && $2"
}

# DAFoam's renameSolution aborts with "already exists, moving failed!" if a
# previous invocation's numbered time directories are still present. Clear them
# and processor*, but NEVER 0/ or 0.orig/ -- deleting those silently destroys
# the case's initial conditions (this bit us once; it is why the case list is
# explicit rather than a [0-9]* glob).
clean_case() {
    ( cd "$1" && sudo rm -rf processor* 2>/dev/null || rm -rf processor* 2>/dev/null || true
      for d in $(ls -d */ 2>/dev/null | grep -E '^[0-9]' | tr -d '/'); do
          case "$d" in 0|0.orig) ;; *) (sudo rm -rf "./$d" 2>/dev/null || rm -rf "./$d") ;; esac
      done )
}

# --- 2. UBend_Channel: the primary reproducer -------------------------------
UB="$WORK/tutorials/UBend_Channel"
cp "$HERE/repro_warpderiv_ubend.py" "$UB"/
[ -f "$UB/log.meshGeneration" ] || indocker "$UB" './preProcessing.sh'

for OBJ in stock pressure-loss; do
    for SEED in random real; do
        echo
        echo "===== UBend_Channel  objective=$OBJ  seed=$SEED ====="
        clean_case "$UB"
        indocker "$UB" "mpirun --allow-run-as-root -np 4 python repro_warpderiv_ubend.py \
                        --seed $SEED --objective $OBJ --h 1e-4" \
            2>&1 | tee "$WORK/repro_ubend_${OBJ}_${SEED}_np4.log" | grep -a '^REPRO'
    done
done

# --- 3. NACA0012: the geometry-only reproducer ------------------------------
AF="$WORK/tutorials/NACA0012_Airfoil/incompressible"
cp "$HERE/repro_warpderiv_airfoil.py" "$AF"/
[ -f "$AF/logMeshGeneration.txt" ] || indocker "$AF" './preProcessing.sh'

for IDX in 4 6 7; do
    echo
    echo "===== NACA0012  idx=$IDX (4=single-station control, 6=LE combo, 7=TE combo) ====="
    clean_case "$AF"
    indocker "$AF" "mpirun --allow-run-as-root -np 4 python repro_warpderiv_airfoil.py \
                    --idx $IDX --h 1e-4 --seed 2026" \
        2>&1 | tee "$WORK/repro_airfoil_idx${IDX}_np4.log" | grep -a '^idx='
done

echo
echo "== done. Logs in $WORK/"
