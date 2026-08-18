#!/bin/bash
# Import the three DPW5 L1.T committee grids and run checkMesh on each.
# The three share one node distribution and differ only in element topology,
# so any difference in the mesh-quality metrics is attributable to topology
# alone.
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
export PATH="$FOAM_APPBIN:$PATH"
R=/home/ubuntu/certonomous-runs/dpw5-committee-probe
cd "$R" || exit 1

for G in "$@"; do
  C="$R/case_$G"
  echo "=== $G  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  rm -rf "$C"; mkdir -p "$C/constant" "$C/system"
  cat > "$C/system/controlDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     simpleFoam;
startFrom       startTime;  startTime 0;
stopAt          endTime;    endTime   1;
deltaT          1;          writeControl timeStep;  writeInterval 1000;
runTimeModifiable false;
EOF
  python3 "$R/memwatch.py" --tag "dpw5_${G}_convert" --out "$R/measurements.jsonl" \
      --log "$R/logs/DPW5_${G}_convert.log" -- \
      python3 "$R/ugrid_to_foam.py" "$R/grid/L1.T.rev01.p3d.$G.r8.ugrid" \
              "$R/grid/dpw5_L1T.mapbc" "$C"
  python3 "$R/memwatch.py" --tag "dpw5_${G}_checkMesh" --out "$R/measurements.jsonl" \
      --cwd "$C" --log "$R/logs/DPW5_${G}_checkMesh.log" -- checkMesh
  echo "--- $G checkMesh tail"
  grep -iE "non-orthogonality|skewness|aspect ratio|cells:|faces:|Mesh OK|\*\*\*|Failed" \
      "$R/logs/DPW5_${G}_checkMesh.log" | head -20
done
echo "=== all done $(date -u +%Y-%m-%dT%H:%M:%SZ)"
