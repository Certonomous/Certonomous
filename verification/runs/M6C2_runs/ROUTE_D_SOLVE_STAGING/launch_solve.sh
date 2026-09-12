#!/bin/bash
# M6 route (d) L1 SOLVE. rc captured INSIDE this wrapper for every stage --
# `setsid timeout cmd` exits 0 for every outcome, so an rc captured AROUND the
# detached line is meaningless.
set -u
CASE=/home/ubuntu/Certonomous/verification/runs/M6C2_runs/ROUTE_D_SOLVE/L1
STAGE=/home/ubuntu/Certonomous/verification/runs/M6C2_runs/ROUTE_D_SOLVE_STAGING
FOAM=/usr/lib/openfoam/openfoam2606/etc/bashrc
RANKS=4
MIN_FREE=21474836480   # 20 GiB, registered section 8

# GUARD 1 (pre-registration section 8, satisfied literally, not explained away)
if [ -d "$CASE" ]; then
  echo "REFUSED: $CASE already exists -- grading it could grade a previous attempt."; exit 2
fi
FREE=$(df --output=avail -B1 /home/ubuntu | tail -1 | tr -d ' ')
if [ "$FREE" -lt "$MIN_FREE" ]; then
  echo "REFUSED: free $(awk "BEGIN{printf \"%.3f\",$FREE/1073741824}") GiB < 20 GiB floor."; exit 3
fi
echo "free at launch: $(awk "BEGIN{printf \"%.3f\",$FREE/1073741824}") GiB"

mkdir -p "$CASE"
cp -r "$STAGE/0" "$STAGE/constant" "$STAGE/system" "$CASE/"
# 0/T is touched LAST at launch: it dates the run allowed to produce the answer (age guard)
touch "$CASE/0/T"
date -u +%FT%TZ > "$CASE/SOLVE_START_UTC.txt"
echo $RANKS > "$CASE/RANKS.txt"

cat > "$CASE/system/decomposeParDict" <<EOD
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $RANKS;
method scotch;
EOD

T0=$(date +%s)
run () { local n="$1"; shift
  bash -c "source $FOAM && cd $CASE && $* > log.$n 2>&1"; local rc=$?
  echo "$rc" > "$CASE/rc.$n"; echo "  $n rc=$rc End=$(grep -c '^End' "$CASE/log.$n" 2>/dev/null)"; return $rc; }
rc=0
run decomposePar "decomposePar -force"                         || rc=$?
[ $rc -eq 0 ] && { run rhoSimpleFoam "mpirun -np $RANKS rhoSimpleFoam -parallel" || rc=$?; }
[ $rc -eq 0 ] && { run reconstructPar "reconstructPar -latestTime" || rc=$?; }
T1=$(date +%s)
echo "$rc" > "$CASE/rc"
echo $((T1-T0)) > "$CASE/WALL_SECONDS_SOLVE.txt"
awk "BEGIN{printf \"%.2f\n\", ($T1-$T0)*$RANKS/60}" > "$CASE/CORE_MINUTES.txt"
echo "total rc=$rc wall=$((T1-T0))s core-min=$(cat $CASE/CORE_MINUTES.txt) (est ~53, CAP 150)"
exit $rc
