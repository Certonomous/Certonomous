#!/bin/bash
# run_k2b.sh -- mesh and solve the K2b-pilot cases, single core, timed.
#
#   bash run_k2b.sh                       # the two primaries, in order
#   bash run_k2b.sh K2bP_coarse           # or exactly the cases named
#   bash run_k2b.sh K2bP_C1_g0 ...        # controls: see the SEEDING note below
#
# Cost is written per case into COST.txt in core-minutes.  There is no verified
# currency rate for this machine, so no dollar figure is produced.
#
# MEASURED AT KV1, DO NOT REORDER: the OpenFOAM bashrc must be sourced BEFORE
# `set -e`.  Under `set -e` it aborts the script silently at the source line and
# every case is skipped with an empty log and an exit 1 that names nothing.
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -e
HERE=$(cd "$(dirname "$0")" && pwd)

# MEASURED AT KV1, DO NOT "SIMPLIFY" BACK: `for c in "${@:-a b c}"` collapses
# the default into ONE word and `cd` then fails on a directory named "a b c".
CASES=("$@")
if [ ${#CASES[@]} -eq 0 ]; then
  CASES=(K2bP_coarse K2bP_fine)
fi

# SEEDING.  The three controls are RESTART twins: they are their PARENT case
# (K2bP_under) perturbed in exactly one dictionary, and they start from its
# converged field.
# `seed_k2b.py` copies that field in -- the internal field only, keeping the
# control's OWN boundary conditions.  Running a control before its seed exists
# is refused here rather than silently started from `0.orig`, because a control
# that started from a different initial state is not the twin it claims to be.
for c in "${CASES[@]}"; do
  cd "$HERE/$c"
  case "$c" in
    K2bP_C*)
      if [ ! -d "$HERE/$c/0" ]; then
        echo "REFUSE: $c has no seeded 0/ directory; run: python3 seed_k2b.py $c" >&2
        exit 2
      fi
      ;;
    *)
      rm -rf 0
      cp -r 0.orig 0
      ;;
  esac
  rm -rf postProcessing constant/polyMesh
  rm -f log.blockMesh log.checkMesh log.buoyantBoussinesqSimpleFoam
  for d in [1-9]*; do [ -d "$d" ] && rm -rf "$d"; done
  blockMesh > log.blockMesh 2>&1
  checkMesh > log.checkMesh 2>&1
  grep -q "^Mesh OK" log.checkMesh || { echo "checkMesh not OK in $c" >&2; exit 3; }
  T0=$(date +%s.%N)
  buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam 2>&1
  T1=$(date +%s.%N)
  WALL=$(echo "$T1-$T0" | bc)
  CM=$(echo "scale=4; $WALL/60" | bc)
  NC=$(awk '/^  nCells:/{print $2}' log.blockMesh | head -1)
  NI=$(grep -c "^Time = " log.buoyantBoussinesqSimpleFoam || true)
  { echo "case $c"
    echo "cells $NC"
    echo "iterations $NI"
    echo "wall_clock_s $WALL"
    echo "cores 1"
    echo "core_minutes $CM"
    echo "cell_iter_per_core_s $(echo "scale=1; $NC*$NI/$WALL" | bc)"; } > COST.txt
  echo "$c: ${NC} cells, ${NI} iters, ${WALL}s = ${CM} core-minutes"
done
