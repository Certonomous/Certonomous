#!/bin/bash
# Launch all K0cR cases and BLOCK until every one finishes.
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
echo "launch started $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> LAUNCH.log
for c in R_sq_c R_sq_f R_tl_c R_tl_f; do
    (
        cd "$HERE/$c"
        buoyantBoussinesqSimpleFoam > log.solve 2>&1
        rc=$?
        et=$(grep -a 'ExecutionTime' log.solve | tail -1 | awk '{print $3}')
        { echo "case=$c"; echo "rc=$rc"; echo "exec_seconds=$et";
          echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$HERE/DONE.$c"
    ) &
done
wait
n=$(ls "$HERE"/DONE.* 2>/dev/null | wc -l)
{ echo "all_cases_finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)";
  echo "markers=$n"; echo "expected=4"; } > "$HERE/ALL_DONE"
echo "done: $n markers" >> LAUNCH.log
