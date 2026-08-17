#!/bin/bash
# run_kv1.sh -- build the mesh and solve both KV1 cases, single core, timed.
# Cost is written per case into COST.txt in core-minutes, no dollar figure:
# there is no verified rate for this machine.
#
# NOTE, MEASURED: the OpenFOAM bashrc must be sourced BEFORE `set -e`. Under
# `set -e` it aborts the script silently at the source line and every case is
# skipped with an empty log and an exit 1 that names nothing.
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
for c in "${@:-KV1a_duct_source KV1b_duct_nosource KV1c_duct_heated}"; do
  cd "$HERE/$c"
  rm -rf 0 postProcessing constant/polyMesh
  rm -f log.*
  for d in [1-9]*; do [ -d "$d" ] && rm -rf "$d"; done
  cp -r 0.orig 0
  blockMesh > log.blockMesh 2>&1
  checkMesh > log.checkMesh 2>&1
  T0=$(date +%s.%N)
  buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam 2>&1
  T1=$(date +%s.%N)
  WALL=$(echo "$T1-$T0" | bc)
  CM=$(echo "scale=4; $WALL/60" | bc)
  { echo "case $c"
    echo "wall_clock_s $WALL"
    echo "cores 1"
    echo "core_minutes $CM"; } > COST.txt
  echo "$c: ${WALL}s = ${CM} core-minutes"
done
