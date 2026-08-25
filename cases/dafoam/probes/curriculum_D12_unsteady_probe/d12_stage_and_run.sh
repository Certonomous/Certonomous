#!/usr/bin/env bash
# CURRICULUM D12 CAPABILITY PROBE launcher.  Frozen instrument.
# Container pattern inherited from cases/dafoam/ladder-a/A1/curriculum_D2/d2_run_arm.sh
# (L-251 --user 0:0; L-252 STAMP + .ok sentinel; 8.1 kernel-only stop; 8.2 no --rm,
#  so `docker inspect .State.OOMKilled` survives -- which is D12's named failure mode).
#
# Substrate: the upstream DAFoam Cylinder tutorial (2D cylinder, DAPimpleFoam,
# unsteadyAdjoint mode timeAccurate), at the registered probe reduction of 5 steps.
#
# Stages, all np=1:
#   base   compute_totals, shapePlant 0.0        -> d12_base.json   (primal + unsteady adjoint)
#   plant  run_model,      shapePlant 1.234e-03  -> d12_plant.json  (THE PLANT)
#   clean  run_model,      shapePlant 0.0        -> d12_clean.json  (discrimination control AND
#                                                      the primal-only disk/RAM reference)
set -uo pipefail

IMG="${IMG:-dafoam/opt-packages:latest}"
BASE="${BASE:-/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D12}"
TUT="${TUT:-/home/ubuntu/dafoam-tutorials/Cylinder}"
CDICT="${CDICT:-/home/ubuntu/Certonomous/cases/dafoam/probes/curriculum_D12_unsteady_probe/d12_controlDict_probe}"
RUNPY="${RUNPY:-/home/ubuntu/Certonomous/cases/dafoam/probes/curriculum_D12_unsteady_probe/d12_run_script.py}"
TMO="${TMO:-600}"
# REGISTERED BUDGET CAP, core-min, cumulative over EVERY container this probe launches
# (mesh build included).  An overrun STOPS the probe; it does not get a new budget
# (CLAUDE.md rule 12).
CAP_CORE_MIN="${CAP_CORE_MIN:-6.0}"
SPENT_CORE_MIN=0
PLANT_SHAPE="1.234e-03"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
mkdir -p "$BASE" || { echo "ABORT: cannot mkdir $BASE"; exit 1; }
chmod 777 "$BASE"
LEDGER="$BASE/ledger.txt"

# ---- 1. mesh, once, in a container (pyHyp + plot3dToFoam + autoPatch + createPatch)
sudo -n rm -rf "$BASE/mesh" 2>/dev/null
mkdir -p "$BASE/mesh" || { echo ABORT; exit 1; }
cp -a "$TUT"/0_orig "$TUT"/FFD "$TUT"/constant "$TUT"/system "$TUT"/genMesh.py "$BASE/mesh/" \
  || { echo "ABORT: tutorial stage copy failed"; exit 1; }
cp -a "$CDICT" "$BASE/mesh/system/controlDict" || { echo "ABORT: controlDict copy failed"; exit 1; }
cp -a "$TUT"/system/fvSchemes_pimple "$BASE/mesh/system/fvSchemes" || { echo ABORT; exit 1; }
cp -a "$TUT"/system/fvSolution_pimple "$BASE/mesh/system/fvSolution" || { echo ABORT; exit 1; }
cp -a "$RUNPY" "$BASE/mesh/" || { echo "ABORT: runscript copy failed"; exit 1; }
grep -q "^endTime         0.05;" "$BASE/mesh/system/controlDict" \
  || { echo "ABORT: probe controlDict endTime is not 0.05"; exit 1; }

timeout 600 sudo -n docker run --name "d12_mesh_${STAMP}" --user 0:0 --cpus=1 \
    -v "$BASE":/mnt -w /mnt/mesh "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     python genMesh.py && plot3dToFoam -noBlank volumeMesh.xyz && autoPatch 30 -overwrite && \
     createPatch -overwrite && renumberMesh -overwrite && checkMesh -constant | tail -30" \
    > "$BASE/mesh_${STAMP}.log" 2>&1
mrc=$?
MESH_WALL=$SECONDS
SPENT_CORE_MIN=$(python3 -c "print(round($SECONDS/60.0,4))")
sudo -n docker rm "d12_mesh_${STAMP}" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$BASE" 2>/dev/null
if [ $mrc -ne 0 ]; then echo "ABORT: mesh generation rc=$mrc, see mesh_${STAMP}.log"; exit 1; fi
grep -a "^nCells" "$BASE/mesh_${STAMP}.log" | tee -a "$LEDGER"
# strip the time dirs the mesh pipeline may have left; the probe starts cold from 0_orig
sudo -n rm -rf "$BASE/mesh/0" "$BASE/mesh/processor"* 2>/dev/null

run_stage () {
  # ---- REGISTERED BUDGET GUARD: an overrun STOPS the probe (CLAUDE.md rule 12)
  if python3 -c "import sys; sys.exit(0 if $SPENT_CORE_MIN >= $CAP_CORE_MIN else 1)"; then
    echo "BUDGET STOP: $SPENT_CORE_MIN core-min spent >= cap $CAP_CORE_MIN; stage $1 NOT LAUNCHED" | tee -a "$LEDGER"
    return 9
  fi
  local STAGE="$1" TASK="$2" PLANT="$3"
  local NAME="d12_${STAGE}_${STAMP}"
  local LOG="$BASE/${STAGE}_${STAMP}.log"
  sudo -n rm -rf "$BASE/$STAGE" 2>/dev/null
  cp -a "$BASE/mesh" "$BASE/$STAGE" || { echo "ABORT: stage $STAGE copy failed"; return 4; }
  cp -a "$BASE/mesh/0_orig" "$BASE/$STAGE/0" || { echo "ABORT: 0 copy failed"; return 4; }
  for bad in "$BASE/$STAGE/0.01" "$BASE/$STAGE/0.05"; do
    test -e "$bad" && { echo "COLDSTART FAIL: $bad exists"; return 5; }
  done
  local DU0; DU0=$(du -sb "$BASE/$STAGE" | awk '{print $1}')
  local T0 T1 WALL rc INSPECT DU1
  T0=$(date -u +%s)
  timeout "$TMO" sudo -n docker run --name "$NAME" \
      --user 0:0 --cpus=1 --memory=12g --memory-swap=12g --oom-score-adj=500 \
      -v "$BASE":/mnt -w "/mnt/$STAGE" "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
       mpirun --allow-run-as-root -np 1 python d12_run_script.py -task $TASK -shapePlant $PLANT -out d12_${STAGE}.json" \
      > "$LOG" 2>&1
  rc=$?
  T1=$(date -u +%s); WALL=$((T1-T0))
  INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
  sudo -n docker rm "$NAME" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "$LOG" "$BASE/$STAGE" 2>/dev/null
  DU1=$(du -sb "$BASE/$STAGE" | awk '{print $1}')
  local CM; CM=$(python3 -c "print(round($WALL/60.0,4))")
  echo "STAGE=$STAGE TASK=$TASK shapePlant=$PLANT rc=$rc wall_s=$WALL ranks=1 core_min=$CM inspect(exit,oomkilled)=[$INSPECT] du_before_B=$DU0 du_after_B=$DU1 du_delta_B=$((DU1-DU0)) log=$(basename "$LOG")" | tee -a "$LEDGER"
  SPENT_CORE_MIN=$(python3 -c "print(round($SPENT_CORE_MIN + $CM, 4))")
  echo "SPENT_CORE_MIN=$SPENT_CORE_MIN of cap $CAP_CORE_MIN" | tee -a "$LEDGER"
  test -s "$LOG" && touch "$LOG.ok.${STAMP}"
  return $rc
}

run_stage base  compute_totals 0.0              || echo "STAGE base NONZERO rc"
run_stage plant run_model      "$PLANT_SHAPE"   || echo "STAGE plant NONZERO rc"
run_stage clean run_model      0.0              || echo "STAGE clean NONZERO rc"
echo "TOTAL_SPENT_CORE_MIN=$SPENT_CORE_MIN CAP=$CAP_CORE_MIN" | tee -a "$LEDGER"
echo "STAMP=$STAMP" | tee -a "$LEDGER"
