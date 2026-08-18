#!/bin/bash
# run_case.sh -- mesh and solve ONE K0cX case, then write a COMPLETION MARKER.
#
#   ./run_case.sh <case-name>
#
# THE MARKER IS THE CONTRACT.  Absence of a process proves neither death nor
# completion, other lanes share this box, and a solver's process NAME is
# truncated to 15 characters by the kernel so `buoyantBoussinesqSimpleFoam`
# never matches `pgrep -x`.  The caller waits for DONE.<case> and never for a
# process-table entry.
#
# NO `set -u` HERE, AND THAT IS DELIBERATE.  OpenFOAM v2606's etc/bashrc
# dereferences unset variables, so sourcing it under `set -u` exits this script
# silently BEFORE the completion marker is written.  At the K0cS rung all ten
# cases "finished" in 62 seconds with zero markers, and the marker discipline is
# the only thing that caught it: a process-table check would have shown no
# solvers running and read exactly like success.
#
# NOTHING HERE GLOBS FOR TIME DIRECTORIES.  `rm -rf <case>/[0-9]*` matches
# `0.orig` and destroyed every initial-condition directory in the K0b tree once
# already.  Only the explicitly named `0` is removed.
#
# THIS SCRIPT DELETES ONLY INSIDE ITS OWN NAMED CASE DIRECTORY: `0`,
# `postProcessing`, and OpenFOAM's own parseable time directories via
# `foamListTimes -rm`.  It never touches its parent, and it never removes
# `0.orig`, `CASE.txt`, `system/` or `constant/`.
case_name="$1"
[ -n "$case_name" ] || { echo "usage: run_case.sh <case-name>"; exit 3; }
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE="$HERE/$case_name"
[ -d "$CASE/0.orig" ] || { echo "REFUSE: $CASE has no 0.orig"; exit 3; }
cd "$CASE" || exit 3

rm -f "$HERE/DONE.$case_name"

source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1 || {
    echo "case=$case_name stage=foam_bashrc rc=1" > "$HERE/DONE.$case_name"; exit 1; }

foamListTimes -rm > /dev/null 2>&1
rm -rf ./0 ./postProcessing
cp -r ./0.orig ./0

start=$(date +%s)
blockMesh > log.blockMesh 2>&1; rc_mesh=$?
if [ $rc_mesh -ne 0 ]; then
    echo "case=$case_name stage=blockMesh rc=$rc_mesh" > "$HERE/DONE.$case_name"
    exit $rc_mesh
fi
checkMesh > log.checkMesh 2>&1; rc_check=$?

buoyantBoussinesqSimpleFoam > log.solve 2>&1; rc_solve=$?
end=$(date +%s)

# ExecutionTime is the SOLVER's own CPU accounting and is what gets charged.
# Wall clock is recorded beside it because other lanes share this box and the
# two diverge under contention.
exec_s=$(grep 'ExecutionTime' log.solve | tail -1 | awk '{print $3}')
clock_s=$(grep 'ExecutionTime' log.solve | tail -1 | awk '{print $7}')
iters=$(grep -c '^Time = ' log.solve)
bound_k=$(grep -c 'bounding k' log.solve)
bound_e=$(grep -c 'bounding epsilon' log.solve)
bound_o=$(grep -c 'bounding omega' log.solve)

{
  echo "case=$case_name"
  echo "rc_blockMesh=$rc_mesh"
  echo "rc_checkMesh=$rc_check"
  echo "rc_solve=$rc_solve"
  echo "iterations=$iters"
  echo "exec_seconds=${exec_s:-NA}"
  echo "clock_seconds=${clock_s:-NA}"
  echo "wall_seconds=$((end-start))"
  echo "bounding_k_events=$bound_k"
  echo "bounding_epsilon_events=$bound_e"
  echo "bounding_omega_events=$bound_o"
  echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$HERE/DONE.$case_name"
exit $rc_solve
