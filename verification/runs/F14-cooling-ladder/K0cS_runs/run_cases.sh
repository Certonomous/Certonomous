#!/bin/bash
# Run one K0cS case to its endTime and write a COMPLETION MARKER.
#
# THE MARKER IS THE CONTRACT.  Absence of a process proves neither death nor
# completion, and this box has other agents on it, so the caller waits for
# DONE.<case> and never for a process table entry.
# NO `set -u` HERE, AND THAT IS DELIBERATE.  The first version of this script
# carried it; OpenFOAM v2606's etc/bashrc dereferences unset variables, so
# sourcing it under `set -u` exits the script silently, BEFORE the completion
# marker is written.  All ten cases "finished" in 62 seconds with zero markers.
# The marker discipline is what caught it: a process-table check would have
# shown no solvers running and read exactly like success.
case_name="$1"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE/$case_name" || exit 3
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1 || { echo "case=$case_name stage=foam_bashrc rc=1" > "$HERE/DONE.$case_name"; exit 1; }

rm -f "$HERE/DONE.$case_name"
rm -rf 0 processor* postProcessing
cp -r 0.orig 0

start=$(date +%s)
blockMesh > log.blockMesh 2>&1; rc_mesh=$?
if [ $rc_mesh -ne 0 ]; then
    echo "case=$case_name stage=blockMesh rc=$rc_mesh" > "$HERE/DONE.$case_name"
    exit $rc_mesh
fi
checkMesh > log.checkMesh 2>&1; rc_check=$?

buoyantBoussinesqSimpleFoam > log.solve 2>&1; rc_solve=$?
end=$(date +%s)

# ExecutionTime is the solver's own accounting and is what gets charged.
exec_s=$(grep 'ExecutionTime' log.solve | tail -1 | awk '{print $3}')
iters=$(grep -c '^Time = ' log.solve)

{
  echo "case=$case_name"
  echo "rc_blockMesh=$rc_mesh"
  echo "rc_checkMesh=$rc_check"
  echo "rc_solve=$rc_solve"
  echo "iterations=$iters"
  echo "exec_seconds=${exec_s:-NA}"
  echo "wall_seconds=$((end-start))"
  echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$HERE/DONE.$case_name"
exit $rc_solve
