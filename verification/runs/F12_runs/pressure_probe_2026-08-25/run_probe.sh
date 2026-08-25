#!/bin/bash
# F12 PRESSURE PROBE -- where does FIRST-SOLVE p bottom, and does `transonic`
# change it?  Runs on the REAL coarse mesh, OUTSIDE the repository and outside
# every registered run root.  Touches no registered case, no gate, no threshold.
# residualControl is NOT loosened: that is a threshold change and is unavailable
# post-freeze.  This probe reads FIRST-SOLVE residuals only -- never a tail read.
set -u
PB=/home/ubuntu/certonomous-runs/F12_pressure_probe_2026-08-25
REPO=/home/ubuntu/Certonomous
RUNG1=$REPO/verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79
ITERS=2000
CAP_CORE_MIN=6.0          # per arm; measured rate says ~3.9, so ~1.5x headroom
CAP_WALL_S=$(python3 -c "print(int($CAP_CORE_MIN*60))")

for d in attempt2_medium_workshop_M0.734_a2.79 attempt2_fine_workshop_M0.734_a2.79 \
         attempt2_medium_tape_M0.730_a2.79 attempt2_medium_farfield2x_M0.734_a2.79; do
  [ -e "$REPO/verification/runs/F12_runs/$d" ] && { echo "ABORT: $d exists"; exit 1; }
done
ls -d $REPO/verification/runs/F12_runs/attempt3* >/dev/null 2>&1 && { echo "ABORT: attempt3 exists"; exit 1; }
find $RUNG1 -type f | sort | xargs sha256sum 2>/dev/null | sha256sum > $PB/rung1_fingerprint_before.txt
echo "PRE-ASSERT OK $(date -u +%FT%TZ)  cap ${CAP_CORE_MIN} core-min/arm = ${CAP_WALL_S}s at ranks 1"

build_arm () {           # $1 = arm dir, $2 = "yes" to add transonic
  local C=$1 TR=$2
  mkdir -p $C
  cp -r $RUNG1/system $RUNG1/constant $RUNG1/0 $C/
  rm -rf $C/constant/polyMesh
  # attempt-3 relaxation: F2's values, which survived 2000 iterations here.
  python3 - "$C/system/fvSolution" "$TR" <<'PY'
import re, sys
p, tr = sys.argv[1], sys.argv[2]
t = open(p).read()
t = t.replace("rho             0.05;", "rho             0.01;")
t = t.replace("U               0.3;",  "U               0.15;")
t = t.replace("e               0.5;",  "e               0.3;")
t = t.replace('"(k|omega)"     0.5;',  '"(k|omega)"     0.3;')
t = t.replace("nNonOrthogonalCorrectors 1;", "nNonOrthogonalCorrectors 2;")
if tr == "yes":
    t = t.replace("nNonOrthogonalCorrectors 2;",
                  "nNonOrthogonalCorrectors 2;\n    transonic       yes;")
open(p, "w").write(t)
# refuse silently-unapplied edits
s = open(p).read()
assert "rho             0.01;" in s and "U               0.15;" in s \
   and "e               0.3;" in s and '"(k|omega)"     0.3;' in s \
   and "nNonOrthogonalCorrectors 2;" in s, "an intended fvSolution edit did NOT apply"
assert ("transonic       yes;" in s) == (tr == "yes"), "transonic switch not as intended"
assert "1e-06" in s, "residualControl was altered -- it must NOT be"
PY
  sed -i "s/^endTime .*/endTime         $ITERS;/;s/^writeInterval .*/writeInterval   $ITERS;/" $C/system/controlDict
  ( cd $C && openfoam2606 blockMesh > log.blockMesh 2>&1; echo $? > RC.blockMesh )
}

run_arm () {             # $1 = arm dir
  local C=$1
  ( cd $C && timeout ${CAP_WALL_S}s openfoam2606 rhoSimpleFoam > log.rhoSimpleFoam 2>&1
    RC=$?; echo "$RC" > RC.txt; sync ) &
  local SOLVE=$!
  local T0=$(date +%s)
  while kill -0 $SOLVE 2>/dev/null; do
    local EL=$(( $(date +%s) - T0 ))
    printf '{"utc":"%s","elapsed_s":%d,"core_min":%.4f,"cap_core_min":%s,"loadavg":[%s]}\n' \
      "$(date -u +%FT%TZ)" "$EL" "$(python3 -c "print($EL/60)")" "$CAP_CORE_MIN" \
      "$(awk '{printf "\"%s\",\"%s\",\"%s\"",$1,$2,$3}' /proc/loadavg)" >> $C/SAMPLES.jsonl
    sleep 20
  done
  wait $SOLVE 2>/dev/null
  echo "  $(basename $C): rc=$(cat $C/RC.txt) wall=$(( $(date +%s) - T0 ))s"
}

build_arm $PB/armA_relaxation_only  no
build_arm $PB/armB_relaxation_plus_transonic yes
echo "MESHES BUILT: A rc=$(cat $PB/armA_relaxation_only/RC.blockMesh) B rc=$(cat $PB/armB_relaxation_plus_transonic/RC.blockMesh)"
run_arm $PB/armA_relaxation_only
run_arm $PB/armB_relaxation_plus_transonic

find $RUNG1 -type f | sort | xargs sha256sum 2>/dev/null | sha256sum > $PB/rung1_fingerprint_after.txt
cmp -s $PB/rung1_fingerprint_before.txt $PB/rung1_fingerprint_after.txt \
  && echo "POST-ASSERT OK: rung 1 byte-unchanged" || echo "POST-ASSERT FAILED"
for d in attempt2_medium_workshop_M0.734_a2.79 attempt2_fine_workshop_M0.734_a2.79 \
         attempt2_medium_tape_M0.730_a2.79 attempt2_medium_farfield2x_M0.734_a2.79; do
  [ -e "$REPO/verification/runs/F12_runs/$d" ] && echo "POST-ASSERT FAILED: $d appeared"
done
echo "POST-ASSERT: rungs 2-5 still absent.  DONE $(date -u +%FT%TZ)"
