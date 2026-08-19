#!/bin/bash
# K0cG launcher.  Blocks until every case finishes.
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
echo "launch started $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> LAUNCH.log
for c in S_SST_x S_KE_x; do
    ( cd "$HERE/$c"
      blockMesh > log.blockMesh 2>&1 || { echo "case=$c"; echo "rc=blockMesh"; } > "$HERE/DONE.$c"
      checkMesh > log.checkMesh 2>&1
      cp -r 0.orig 0
      buoyantBoussinesqSimpleFoam > log.solve 2>&1; rc=$?
      et=$(grep -a 'ExecutionTime' log.solve | tail -1 | awk '{print $3}')
      cells=$(grep -a -m1 'cells:' log.checkMesh | awk '{print $2}')
      { echo "case=$c"; echo "rc=$rc"; echo "cells=$cells"; echo "exec_seconds=$et";
        echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$HERE/DONE.$c" ) &
done
wait
n=$(ls "$HERE"/DONE.* 2>/dev/null | wc -l)
{ echo "all_cases_finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "markers=$n"; echo "expected=2"; } > "$HERE/ALL_DONE"
echo "done: $n markers" >> LAUNCH.log
