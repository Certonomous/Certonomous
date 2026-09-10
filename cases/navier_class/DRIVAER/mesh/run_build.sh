#!/bin/bash
# DRIVAER R1 -- build ONE mesh level.  NEVER deletes anything.
# rc is captured INSIDE this wrapper: `setsid timeout cmd` exits 0 for every
# outcome, so an rc read around the setsid line is meaningless.
LVL="$1"; ROOT="$2"; NP="${3:-1}"
[ -d "$ROOT" ] || { echo "REFUSE: no such level root $ROOT"; exit 2; }
set +u
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
cd "$ROOT" || exit 2
: > BUILD_RC
step () {  # step <name> <cmd...>
  local n="$1"; shift
  /usr/bin/time -v nice -n 10 "$@" > "log.$n" 2> "time.$n"
  local rc=$?
  echo "$n rc=$rc" >> BUILD_RC
  grep -E "Maximum resident set size|Elapsed \(wall" "time.$n" | sed "s/^/$n /" >> BUILD_RC
  if [ $rc -ne 0 ]; then echo "$n FAILED rc=$rc" >> BUILD_RC; exit $rc; fi
}
step blockMesh blockMesh
step surfaceFeatureExtract surfaceFeatureExtract
if [ "$NP" -gt 1 ]; then
  cat > system/decomposeParDict <<DPD
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $NP;
method scotch;
DPD
  step decomposePar decomposePar
  /usr/bin/time -v nice -n 10 mpirun -np "$NP" snappyHexMesh -overwrite -parallel \
      > log.snappyHexMesh 2> time.snappyHexMesh
  rc=$?; echo "snappyHexMesh rc=$rc" >> BUILD_RC
  grep -E "Maximum resident set size|Elapsed \(wall" time.snappyHexMesh | sed 's/^/snappyHexMesh /' >> BUILD_RC
  [ $rc -ne 0 ] && exit $rc
  step reconstructParMesh reconstructParMesh -constant
else
  step snappyHexMesh snappyHexMesh -overwrite
fi
# checkMesh: OUR OWN run, full flag set.  checkMesh returns 0 even when checks
# FAIL, so the verdict is parsed from the "Failed N mesh checks" line, never
# from rc and never from the substring "Mesh OK.".
step checkMeshFull checkMesh -allGeometry -allTopology -constant
step checkMeshPlain checkMesh -constant
echo "ALL_STEPS_OK" >> BUILD_RC
