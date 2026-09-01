#!/bin/bash
# Build the M6I ladder registered in verification/campaign/M6I_PREREGISTRATION.md section 3.
#
#   ONE generator call, then TWO coarsenings.  That is the whole point of the design:
#   no generator parameter can fail to scale with the ladder (L-430), because the
#   generator is invoked once.  The coarsener removes every other node, so r = 2.000000
#   in every direction and the levels are exact node subsets by construction.
#
#   L1 fine   983,040 cells   (80 x 128 x 96)   wing_strct.1
#   L2 medium 122,880 cells   (40 x  64 x 48)   wing_strct.2
#   L3 coarse  15,360 cells   (20 x  32 x 24)   wing_strct.3
#
# NO SOLVER IS LAUNCHED BY THIS SCRIPT.  It meshes and inspects only.
set -u
RUNS="$(cd "$(dirname "$0")" && pwd)"
GEN="${1:?usage: build_m6i_ladder.sh <path to wing_release_072319>}"
MESH="$RUNS/mesh"
COST="$RUNS/COST.tsv"

printf 'stage\twall_s\tranks\tcore_min\n' > "$COST"
t0=$(date +%s)
timed () {  # timed <name> <ranks> -- cmd...
  local name="$1" ranks="$2"; shift 3
  local s=$(date +%s); "$@"; local rc=$?; local w=$(( $(date +%s) - s ))
  printf '%s\t%d\t%d\t%.4f\n' "$name" "$w" "$ranks" \
    "$(python3 -c "print($w*$ranks/60)")" >> "$COST"
  return $rc
}

rm -rf "$MESH"; mkdir -p "$MESH"; cd "$MESH" || exit 1
cp "$GEN"/{hcf_wing,hcf_coarsening,om6_wing_section_sharp.dat} . || exit 1

# ---- the ONE generator call -------------------------------------------------
# Deviations from the published demo namelist, and there are exactly two, BOTH
# registered in M6I_PREREGISTRATION section 3:
#   target_y_plus 1.0 -> 0.25   so the family lands at y+ ~ 0.25/0.5/1.0 and EVERY
#                               level is under 1 (section 0 requires it on every level;
#                               a nested family cannot hold y+ fixed, so the FINE
#                               level is targeted and coarsening doubles it twice).
#   counts x2                   nnodes_cylinder_input 32->64, nr_gs 8->16, nre 64->128,
#                               which yields 80 x 128 x 96 = 983,040 = the registered
#                               fine level.  (Measured: i = 5 * nr_gs.)
# Everything else is the published namelist verbatim, INCLUDING target_reynolds_number
# = 14.6e6 on the root chord with the sharp TE, which is TMR's own published figure.
# Shape parameters are HELD FIXED across the family by construction: there is only one
# generator call, so stretching_tanh_towards_lete, R_outer, tr and beta cannot drift.
sed -e 's/target_y_plus = 1.0/target_y_plus = 0.25/' \
    -e 's/nnodes_cylinder_input = 32/nnodes_cylinder_input = 64/' \
    -e 's/nr_gs = 8 /nr_gs = 16/' \
    -e 's/nre = 64 /nre = 128/' \
    -e 's/generate_su2grid_file = T/generate_su2grid_file = F/' \
    "$GEN/input.nml_strct" > input.nml || exit 1

timed generate 1 -- nice -n 15 ./hcf_wing > log.hcf_wing 2>&1 || { echo "GENERATOR FAILED"; exit 1; }
cp "$GEN/input_coarsen.nml_strct" input_coarsen.nml
timed coarsen 1 -- nice -n 15 ./hcf_coarsening > log.hcf_coarsening 2>&1 || { echo "COARSENER FAILED"; exit 1; }

# ---- convert and inspect each level ----------------------------------------
# OpenFOAM's bashrc references unset variables, so `set -u` must be lifted across the
# source and restored immediately after.  Without this the script exits here with the
# generator's output already on disk and no conversion done -- which is exactly what it
# did on its first run, and is recorded rather than quietly fixed.
set +u
# shellcheck disable=SC1090
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
command -v checkMesh >/dev/null || { echo "NO OPENFOAM: checkMesh not on PATH"; exit 1; }
command -v plot3dToFoam >/dev/null || { echo "NO OPENFOAM: plot3dToFoam not on PATH"; exit 1; }
map_level () { case "$1" in L1) echo 1;; L2) echo 2;; L3) echo 3;; esac; }

for L in L3 L2 L1; do
  n=$(map_level "$L")
  C="$RUNS/$L"
  rm -rf "$C"; mkdir -p "$C/system"
  printf 'FoamFile{version 2.0;format ascii;class dictionary;object controlDict;}\napplication none;\nstartFrom startTime;\nstartTime 0;\nstopAt endTime;\nendTime 1;\ndeltaT 1;\nwriteControl timeStep;\nwriteInterval 1;\n' > "$C/system/controlDict"
  printf 'FoamFile{version 2.0;format ascii;class dictionary;object fvSchemes;}\nddtSchemes{default steadyState;}\ngradSchemes{default Gauss linear;}\ndivSchemes{default none;}\nlaplacianSchemes{default Gauss linear corrected;}\n' > "$C/system/fvSchemes"
  printf 'FoamFile{version 2.0;format ascii;class dictionary;object fvSolution;}\nsolvers{}\n' > "$C/system/fvSolution"
  timed "p3d2asc_$L" 1 -- python3 "$RUNS/p3d_bin2asc.py" "$MESH/wing_strct.$n.ufmt" "$MESH/wing_strct.$n.asc" > "$C/log.p3d2asc" 2>&1 || exit 1
  ( cd "$C" && timed "plot3dToFoam_$L" 1 -- nice -n 15 plot3dToFoam -noBlank "$MESH/wing_strct.$n.asc" > log.plot3dToFoam 2>&1 ) || exit 1
  ( cd "$C" && timed "checkMesh_$L" 1 -- nice -n 15 checkMesh > log.checkMesh 2>&1 )
done

printf 'TOTAL\t%d\t1\t%.4f\n' "$(( $(date +%s) - t0 ))" \
  "$(python3 -c "print(($(date +%s)-$t0)/60)")" >> "$COST"
echo "BUILD COMPLETE"
column -t -s$'\t' "$COST"
