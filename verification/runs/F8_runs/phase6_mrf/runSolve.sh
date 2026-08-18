#!/usr/bin/env bash
# F8 Phase VI MRF solve at U=7 m/s (UAE Sequence S, low-speed attached-flow point).
FOAM_BASHRC=/usr/lib/openfoam/openfoam2606/etc/bashrc
source "$FOAM_BASHRC" >/dev/null 2>&1 || true
set -e
cd "$(dirname "$0")"

echo "=== simpleFoam -parallel ==="
mpirun -np 4 simpleFoam -parallel > log.simpleFoam 2>&1
echo "SOLVE_DONE"
