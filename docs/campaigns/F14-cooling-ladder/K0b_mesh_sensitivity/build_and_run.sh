#!/usr/bin/env bash
# build_and_run.sh -- the K0b mesh-sensitivity pair.  F14, proposal P2.
#
# WHAT THIS IS
# ------------
# `demo-output/website/campaign/THERMAL_K0_RESULTS.md`, proposal P2: "Every K0b
# number above is from a single 64x64 mesh. A single-mesh number is not a
# converged number."  P2 costed a 32/64/128 triple at 4.85 core-minutes measured
# plus this lab's 3x planning multiplier, i.e. an ask of 15 core-minutes.  The
# 64x64 leg is already run and committed at 183c91c0, so this script runs the
# two NEW legs -- 32x32 and 128x128 -- and the analysis reads the third leg from
# the committed K0b case.  That is the "pair" in the authorisation.
#
# WHAT IS AND IS NOT ALLOWED TO CHANGE
# ------------------------------------
# Exactly one line changes: the cell counts in system/blockMeshDict.  Everything
# else -- Pr = 0.706814, the limitedLinear/linearUpwind schemes, relaxation,
# residualControl, endTime 4000, the 0.orig fields -- is copied byte-for-byte
# from the committed K0b case.  A mesh study that also changes the scheme is not
# a mesh study.  In particular these cases deliberately do NOT adopt the
# central-difference schemes or the Pr = 0.71 of the K0c gate cases next door:
# the question here is whether K0b's OWN published numbers move with mesh.
#
# The `[0-9]*` glob is not used anywhere here; see the note in
# ../K0c_runs/run_cases.sh for what it cost the last time it was.
set -eo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$(cd "$HERE/../../../.." && pwd)/demo-output/website/campaign/THERMAL_K0_runs/K0b_cavity_Ra1e5
FOAM_BASHRC=${FOAM_BASHRC:-/usr/lib/openfoam/openfoam2606/etc/bashrc}

[ -d "$SRC/0.orig" ] || { echo "REFUSE: K0b source case not found at $SRC"; exit 2; }

for n in 32 128; do
    dst="$HERE/K0b_m$n"
    rm -rf "$dst"
    mkdir -p "$dst"
    cp -r "$SRC/0.orig" "$SRC/constant" "$SRC/system" "$dst/"
    rm -rf "$dst/constant/polyMesh"
    sed -i "s/hex (0 1 3 2 4 5 7 6) (64 64 1)/hex (0 1 3 2 4 5 7 6) ($n $n 1)/" \
        "$dst/system/blockMeshDict"
    grep -q "($n $n 1)" "$dst/system/blockMeshDict" \
        || { echo "REFUSE: blockMeshDict edit did not take for n=$n"; exit 2; }
    # Prove nothing else moved.
    for f in system/fvSchemes system/fvSolution system/controlDict \
             constant/transportProperties constant/g constant/turbulenceProperties \
             constant/thermalAuditProperties 0.orig/T 0.orig/U 0.orig/p_rgh 0.orig/alphat; do
        cmp -s "$SRC/$f" "$dst/$f" \
            || { echo "REFUSE: $f differs from the committed K0b case"; exit 2; }
    done
done

for n in 32 128; do
(
    dst="$HERE/K0b_m$n"
    start=$(date +%s.%N)
    bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$dst'; foamListTimes -rm >/dev/null 2>&1 || true"
    rm -rf "$dst/0" "$dst/postProcessing"
    cp -r "$dst/0.orig" "$dst/0"
    bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$dst'; blockMesh > log.blockMesh 2>&1"
    bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$dst'; checkMesh > log.checkMesh 2>&1"
    bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$dst'; buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam 2>&1"
    end=$(date +%s.%N)
    el=$(echo "$end - $start" | bc)
    printf 'case K0b_m%s\nwall_clock_s %.3f\ncores 1\ncore_minutes %.4f\n' \
        "$n" "$el" "$(echo "$el / 60" | bc -l)" > "$dst/COST.txt"
    printf 'K0b_m%s  wall %.2f s\n' "$n" "$el"
) &
done
wait
