#!/bin/bash
# T10a-VF sweep runner.  Mesh-side preprocessing only: blockMesh, optionally
# faceAgglomerate, then viewFactorsGen.  NO SOLVER IS EVER STARTED and no case
# in this tree holds a time directory.
#
# Serial by construction: one utility at a time, at most MAXJOBS concurrent
# cases (default 2), because the box is shared with other lanes' solvers.
# no `set -u`: the openfoam2606 bashrc reads unset variables and aborts under it
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$HERE/cases}"
MAXJOBS="${MAXJOBS:-2}"

. /usr/lib/openfoam/openfoam2606/etc/bashrc
export WM_NCOMPPROCS=1
export OMP_NUM_THREADS=1

run_one() {
    local d="$1" nm
    nm="$(basename "$d")"
    [ -f "$d/CASE.json" ] || { echo "SKIP $nm (no CASE.json)"; return; }
    local agg
    agg=$(python3 -c "import json;print(json.load(open('$d/CASE.json'))['agglomeration'])")
    ( cd "$d"
      rm -rf constant/polyMesh constant/F constant/globalFaceFaces constant/mapDist \
             constant/finalAgglom processor* 0 1
      local t0 t1
      t0=$(date +%s.%N)
      blockMesh > log.blockMesh 2>&1        || { echo "FAIL blockMesh $nm"; exit 1; }
      checkMesh > log.checkMesh 2>&1        || true
      if [ "$agg" != "0" ]; then
          faceAgglomerate -dict constant/viewFactorsDict > log.faceAgglomerate 2>&1 \
              || { echo "FAIL faceAgglomerate $nm"; exit 1; }
      fi
      viewFactorsGen > log.viewFactorsGen 2>&1 || { echo "FAIL viewFactorsGen $nm"; exit 1; }
      t1=$(date +%s.%N)
      printf 'case=%s wall_s=%.2f nFaces=%s\n' "$nm" "$(echo "$t1-$t0" | bc)" \
             "$(grep -c '' constant/globalFaceFaces 2>/dev/null || echo 0)" > STATUS
      echo "OK   $nm  $(awk '{print $2}' STATUS)"
    )
}

n=0
for d in "$ROOT"/*/; do
    [ -d "$d" ] || continue
    run_one "$d" &
    n=$((n+1))
    if [ $((n % MAXJOBS)) -eq 0 ]; then wait; fi
done
wait
echo "ALL DONE"
