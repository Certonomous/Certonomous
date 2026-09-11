#!/bin/bash
# M6 ROUTE (d) L1 mesh-admission build.
# rc IS CAPTURED INSIDE THIS WRAPPER for every stage. `setsid timeout cmd` exits 0
# for every outcome, so an rc captured AROUND the detached line is meaningless.
set -u
CASE=/home/ubuntu/Certonomous/verification/runs/M6C2_runs/ROUTE_D/L2
STAGE=/home/ubuntu/Certonomous/verification/runs/M6C2_runs/ROUTE_D_STAGING_L2
SURF=/home/ubuntu/Certonomous/verification/runs/M6C2_runs/surface
FOAM=/usr/lib/openfoam/openfoam2606/etc/bashrc
MIN_FREE=21474836480   # 20 GiB -- registered in the pre-registration, section 10

# ---- GUARD 1: the registered run directory must NOT already exist ------------
if [ -d "$CASE" ]; then
  echo "REFUSED: $CASE already exists. A guard refuses a case where a previous"
  echo "attempt may already have written -- grading that tree would grade the wrong run."
  exit 2
fi
# ---- GUARD 2: free space, re-read IMMEDIATELY before launch -----------------
FREE=$(df --output=avail -B1 /home/ubuntu | tail -1 | tr -d ' ')
if [ "$FREE" -lt "$MIN_FREE" ]; then
  echo "REFUSED: free $(awk "BEGIN{printf \"%.3f\",$FREE/1073741824}") GiB < 20 GiB registered floor."
  exit 3
fi
echo "free at launch: $(awk "BEGIN{printf \"%.3f\",$FREE/1073741824}") GiB"

mkdir -p "$CASE"
cp -r "$STAGE/system" "$CASE/system"
mkdir -p "$CASE/constant/triSurface"
cp "$SURF/m6_mp_L1.stl" "$CASE/constant/triSurface/"
date -u +%FT%TZ > "$CASE/SOLVE_START_UTC.txt"
echo 1 > "$CASE/RANKS.txt"

T0=$(date +%s)
run () {  # run <name> <command...>; captures rc INSIDE, next stage only on rc 0
  local n="$1"; shift
  bash -c "source $FOAM && cd $CASE && $* > log.$n 2>&1"; local rc=$?
  echo "$rc" > "$CASE/rc.$n"
  echo "  $n rc=$rc  End=$(grep -c '^End' "$CASE/log.$n" 2>/dev/null)"
  return $rc
}
rc=0
run blockMesh blockMesh              || rc=$?
[ $rc -eq 0 ] && { run surfaceFeatureExtract surfaceFeatureExtract || rc=$?; }
[ $rc -eq 0 ] && { run snappyHexMesh "snappyHexMesh -overwrite" || rc=$?; }
[ $rc -eq 0 ] && { run checkMesh "checkMesh -allTopology -allGeometry" || rc=$?; }
T1=$(date +%s)

echo "$rc" > "$CASE/rc"
echo $((T1-T0)) > "$CASE/WALL_SECONDS_BUILD.txt"
awk "BEGIN{printf \"%.2f\n\", ($T1-$T0)*1/60}" > "$CASE/CORE_MINUTES.txt"
echo "total rc=$rc wall=$((T1-T0))s core-min=$(cat $CASE/CORE_MINUTES.txt)"
exit $rc
