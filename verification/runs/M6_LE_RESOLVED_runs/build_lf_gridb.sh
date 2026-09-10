#!/bin/bash
# M6 GRID-(b) FAMILY (II) `Lf` BUILD DRIVER -- surface-only family, fixed ~150 wall-normal layers,
# 228,544 surface faces x 150 = 34,281,600 cells.
#
# THIS SCRIPT CANNOT START THE BUILD WITHOUT PASSING THE MEMORY PRE-FLIGHT GUARD.
# The guard is the FIRST executable statement after the paths, it is invoked with `python3 -O`
# (the mode in which an `assert`-based guard would silently vanish -- L-332), and a non-zero
# exit STOPS the script.  There is no --force, no environment override and no bypass; adding one
# would make the guard an offer instead of a guard.
set -euo pipefail

RR=/home/ubuntu/Certonomous/verification/runs/M6_LE_RESOLVED_runs
GUARD="$RR/mem_preflight_guard.py"
IMG=dafoam-idwarp-rot:v1
LF_CELLS=34281600          # 228,544 faces (RECLUSTER_Lf.json surface_faces_all9) x 150 layers
LEVEL=Lf
W="$RR/$LEVEL/work"
S="$RR/$LEVEL/solve"

# ---------------------------------------------------------------------------------------
# GATE 0 -- MEMORY PRE-FLIGHT.  Runs under -O deliberately.
# ---------------------------------------------------------------------------------------
echo "=== GATE 0: memory pre-flight, $LF_CELLS cells, $(date -u +%FT%TZ) ==="
python3 -O "$GUARD" --explain --cells "$LF_CELLS"
if ! python3 -O "$GUARD" --cells "$LF_CELLS"; then
  echo "BUILD NOT STARTED: memory pre-flight REFUSED (see above).  Nothing was created." >&2
  echo "Do not lower the requirement to make this pass; wait for the box to drain." >&2
  exit 2
fi

# ---------------------------------------------------------------------------------------
# GATE 1 -- rule-4 age guard: refuse a directory that already holds a build or a solve.
# ---------------------------------------------------------------------------------------
if [ -e "$S/constant/polyMesh" ]; then
  echo "BUILD NOT STARTED: $S/constant/polyMesh already exists.  A guard refuses a case whose" >&2
  echo "outputs already exist; move or name the previous attempt, never overwrite it." >&2
  exit 2
fi
for t in "$S"/[0-9]*; do
  if [ -e "$t" ]; then
    echo "BUILD NOT STARTED: $S holds a time directory ($t).  No flow solve has ever run on" >&2
    echo "this rung and this driver must not be the thing that changes that silently." >&2
    exit 2
  fi
done

mkdir -p "$W" "$S"

# ---------------------------------------------------------------------------------------
# STAGE 1 -- re-clustered 9-zone surface at the REGISTERED resolution (chord 557, span 177).
# ---------------------------------------------------------------------------------------
python3 "$RR/build_reclustered_surface.py" --n-chord 557 --n-span 177 \
        --out "$W/surfaceMesh_Lf.xyz" --fmt big_r8 --report "$W/RECLUSTER_Lf_build.json"

# ---------------------------------------------------------------------------------------
# STAGE 2..6 -- pyHyp march (150 layers, s0=1.546335e-06) then the OpenFOAM tail, serial,
# 1 rank, no mpirun.  Peak RSS is polled per stage, as for Lc/Lm, so the Lf point CONVERTS the
# guard's extrapolation into a measurement for whoever sizes the next level.
# ---------------------------------------------------------------------------------------
docker run --rm -u 1002:1002 -v "$RR/$LEVEL":/home/dafoamuser/mount -w /home/dafoamuser/mount \
  --name "m6gridb_build_$LEVEL" "$IMG" bash -lc '
set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1
cd /home/dafoamuser/mount/work
python march_Lf.py                       > march_Lf.out       2>&1; echo "rc_march=$?"
cd /home/dafoamuser/mount/solve
poll_peak () {   # $1 = stage name, $2.. = command
  local NAME=$1; shift
  "$@" > log.$NAME 2>&1 &
  local P=$! HWM=0 V
  while kill -0 $P 2>/dev/null; do
    V=$(awk "/^VmHWM:/{print \$2}" /proc/$P/status 2>/dev/null)
    [ -n "$V" ] && [ "$V" -gt "$HWM" ] && HWM=$V
    sleep 0.2
  done
  wait $P; local RC=$?
  echo "$NAME VmHWM_peak_kB=$HWM rc=$RC" >> MEM_STAGES_Lf.txt
  return $RC
}
: > MEM_STAGES_Lf.txt
poll_peak plot3dToFoam plot3dToFoam -noBlank volumeMesh_Lf_yp1.xyz
poll_peak autoPatch    autoPatch 60 -overwrite
poll_peak createPatch  createPatch -overwrite
poll_peak renumberMesh renumberMesh -overwrite
poll_peak checkMesh    checkMesh
' 2>&1 | grep -viE 'vspaero|vspviewer'

echo "=== Lf build finished $(date -u +%FT%TZ) ==="
echo "Per-stage MEASURED peaks: $S/MEM_STAGES_Lf.txt -- these RETIRE the guard's extrapolation."
