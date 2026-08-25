#!/usr/bin/env bash
# CURRICULUM D12-F' launcher -- the FD PAIRS for the D12 probe's UNSTEADY adjoint.
# FROZEN INSTRUMENT; fixed at the pre-registration commit.
#
# Container pattern inherited VERBATIM from d12_stage_and_run.sh (L-251 --user 0:0;
# L-252 STAMP + .ok sentinel; 8.1 kernel-only stop; 8.2 no --rm so `docker inspect
# .State.OOMKilled` survives; --bind-to none).
#
# THE CASE IS THE PROBE'S CASE: the same upstream Cylinder tutorial, the same probe
# controlDict (endTime 0.05, 5 steps), the same fvSchemes_pimple/fvSolution_pimple.
# The controlDict is taken from the PROBE'S OWN committed copy, not re-authored.
#
# Stages, ALL np=1, numberOfSubdomains 1:
#   mesh                       pyHyp + plot3dToFoam + autoPatch + createPatch + renumberMesh
#   base   compute_totals      defaults                 -> INSTRUMENT IDENTITY (C1)
#   rep0   run_model           defaults                 -> delta_repeat, first  (C5)
#   rep1   run_model           defaults                 -> delta_repeat, second (C5)
#   plant  run_model           shape[0] = 1.234e-03     -> planted zero (C2)
#   c<i>_fdp_sN / c<i>_fdm_sN  shape[i] = +h / -h       for i in {3, 0}
#
# NO NEGATIVE NUMBER IS EVER WRITTEN ON A COMMAND LINE.  `-shapeSign minus` is a WORD
# and `-shapeMag` is non-negative; the run script combines them internally.  argparse
# reading a leading `-` on a value as an option flag burned 0.7167 core-min in D11-O'.
set -uo pipefail

IMG="${IMG:-dafoam/opt-packages:latest}"
IMG_ID_EXPECT="sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"
BASE="${BASE:-/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D12F}"
TUT="${TUT:-/home/ubuntu/dafoam-tutorials/Cylinder}"
CDICT="${CDICT:-/home/ubuntu/Certonomous/cases/dafoam/probes/curriculum_D12_unsteady_probe/d12_controlDict_probe}"
RUNPY="${RUNPY:-/home/ubuntu/Certonomous/cases/dafoam/probes/curriculum_D12_unsteady_probe_Fprime/d12f_run_script.py}"
TMO="${TMO:-600}"
# REGISTERED RUNAWAY GUARD (see d10f_stage_and_run.sh: a guard reported to the supervisor,
# not a budget rigor is trimmed to fit -- cost constraints are LIFTED, Sanaa 2026-08-25).
CAP_CORE_MIN="${CAP_CORE_MIN:-15.0}"
SPENT_CORE_MIN=0
PLANT_SHAPE="1.234e-03"
STEPS="s1:1.0e-6 s2:1.0e-5 s3:1.0e-4 s4:1.0e-3 s5:1.0e-2"
COMPONENTS="3 0"

GOT_ID=$(sudo -n docker inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
[ "$GOT_ID" = "$IMG_ID_EXPECT" ] || { echo "ABORT: image id is '$GOT_ID', registered '$IMG_ID_EXPECT'"; exit 1; }
echo "IMAGE_ID_VERIFIED=$GOT_ID"

if [ -e "$BASE" ]; then
  echo "REFUSE: run root already exists: $BASE"
  echo "A completed arm is not deleted to re-run it.  Inspect it, do not clear it."
  exit 6
fi
mkdir -p "$BASE/mesh" || { echo "ABORT: cannot mkdir $BASE"; exit 1; }
chmod 777 "$BASE"
LEDGER="$BASE/ledger.txt"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
{ echo "ARM=D12Fprime"; echo "IMAGE_ID=$GOT_ID"; echo "NP=1 numberOfSubdomains=1";
  echo "STEPS=$STEPS"; echo "COMPONENTS=$COMPONENTS"; echo "CAP_CORE_MIN=$CAP_CORE_MIN";
  echo "STAMP=$STAMP"; echo "STARTED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } | tee -a "$LEDGER"

cp -a "$TUT"/0_orig "$TUT"/FFD "$TUT"/constant "$TUT"/system "$TUT"/genMesh.py "$BASE/mesh/" \
  || { echo "ABORT: tutorial stage copy failed"; exit 1; }
cp -a "$CDICT" "$BASE/mesh/system/controlDict" || { echo "ABORT: controlDict copy failed"; exit 1; }
cp -a "$TUT"/system/fvSchemes_pimple "$BASE/mesh/system/fvSchemes" || { echo ABORT; exit 1; }
cp -a "$TUT"/system/fvSolution_pimple "$BASE/mesh/system/fvSolution" || { echo ABORT; exit 1; }
cp -a "$RUNPY" "$BASE/mesh/" || { echo "ABORT: runscript copy failed"; exit 1; }
grep -q "^endTime         0.05;" "$BASE/mesh/system/controlDict" \
  || { echo "ABORT: probe controlDict endTime is not 0.05"; exit 1; }

timeout 600 sudo -n docker run --name "d12f_mesh_${STAMP}" --user 0:0 --cpus=1 \
    -v "$BASE":/mnt -w /mnt/mesh "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     python genMesh.py && plot3dToFoam -noBlank volumeMesh.xyz && autoPatch 30 -overwrite && \
     createPatch -overwrite && renumberMesh -overwrite && checkMesh -constant | tail -30" \
    > "$BASE/mesh_${STAMP}.log" 2>&1
mrc=$?
SPENT_CORE_MIN=$(python3 -c "print(round($SECONDS/60.0,4))")
sudo -n docker rm "d12f_mesh_${STAMP}" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$BASE" 2>/dev/null
if [ $mrc -ne 0 ]; then echo "ABORT: mesh generation rc=$mrc"; exit 1; fi
grep -a "^nCells" "$BASE/mesh_${STAMP}.log" | tee -a "$LEDGER"
echo "MESH_SPENT_CORE_MIN=$SPENT_CORE_MIN" | tee -a "$LEDGER"
sudo -n rm -rf "$BASE/mesh/0" "$BASE/mesh/processor"* 2>/dev/null

run_stage () {
  # $1 stage dir, $2 task, $3 shapeIdx, $4 shapeSign, $5 shapeMag, $6 json basename
  if python3 -c "import sys; sys.exit(0 if $SPENT_CORE_MIN >= $CAP_CORE_MIN else 1)"; then
    echo "RUNAWAY GUARD TRIPPED: $SPENT_CORE_MIN core-min >= cap $CAP_CORE_MIN; stage $1 NOT LAUNCHED" | tee -a "$LEDGER"
    return 9
  fi
  local STAGE="$1" TASK="$2" IDX="$3" SGN="$4" MAG="$5" JB="$6"
  local NAME="d12f_${STAGE}_${STAMP}"
  local LOG="$BASE/${STAGE}_${STAMP}.log"
  # magnitude must be non-negative -- asserted here as well as in the run script
  python3 -c "import sys; sys.exit(0 if $MAG >= 0 else 1)" \
    || { echo "ABORT: stage $STAGE magnitude $MAG is negative"; return 4; }
  cp -a "$BASE/mesh" "$BASE/$STAGE" || { echo "ABORT: stage $STAGE copy failed"; return 4; }
  cp -a "$BASE/mesh/0_orig" "$BASE/$STAGE/0" || { echo "ABORT: 0 copy failed"; return 4; }
  for bad in "$BASE/$STAGE/0.01" "$BASE/$STAGE/0.05"; do
    test -e "$bad" && { echo "COLDSTART FAIL: $bad exists"; return 5; }
  done
  test -n "$(ls -d "$BASE/$STAGE"/processor* 2>/dev/null)" && { echo "COLDSTART FAIL: processor* present"; return 5; }
  local DU0; DU0=$(du -sb "$BASE/$STAGE" | awk '{print $1}')
  local T0 T1 WALL rc INSPECT DU1
  T0=$(date -u +%s)
  timeout "$TMO" sudo -n docker run --name "$NAME" \
      --user 0:0 --cpus=1 --memory=12g --memory-swap=12g --oom-score-adj=500 \
      -v "$BASE":/mnt -w "/mnt/$STAGE" "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
       mpirun --allow-run-as-root --bind-to none -np 1 python d12f_run_script.py \
       -task $TASK -shapeIdx $IDX -shapeSign $SGN -shapeMag $MAG -out ${JB}.json" \
      > "$LOG" 2>&1
  rc=$?
  T1=$(date -u +%s); WALL=$((T1-T0))
  INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
  sudo -n docker rm "$NAME" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "$LOG" "$BASE/$STAGE" 2>/dev/null
  DU1=$(du -sb "$BASE/$STAGE" | awk '{print $1}')
  local CM; CM=$(python3 -c "print(round($WALL/60.0,4))")
  echo "STAGE=$STAGE TASK=$TASK shapeIdx=$IDX shapeSign=$SGN shapeMag=$MAG rc=$rc wall_s=$WALL ranks=1 core_min=$CM inspect(exit,oomkilled)=[$INSPECT] du_before_B=$DU0 du_after_B=$DU1 du_delta_B=$((DU1-DU0)) json=$STAGE/${JB}.json log=$(basename "$LOG")" | tee -a "$LEDGER"
  SPENT_CORE_MIN=$(python3 -c "print(round($SPENT_CORE_MIN + $CM, 4))")
  echo "SPENT_CORE_MIN=$SPENT_CORE_MIN of cap $CAP_CORE_MIN" | tee -a "$LEDGER"
  test -s "$LOG" && touch "$LOG.ok.${STAMP}"
  return $rc
}

run_stage base  compute_totals 0 plus 0.0             d12f_base  || echo "STAGE base NONZERO rc"
run_stage rep0  run_model      0 plus 0.0             d12f_rep0  || echo "STAGE rep0 NONZERO rc"
run_stage rep1  run_model      0 plus 0.0             d12f_rep1  || echo "STAGE rep1 NONZERO rc"
run_stage plant run_model      0 plus "$PLANT_SHAPE"  d12f_plant || echo "STAGE plant NONZERO rc"

for IDX in $COMPONENTS; do
  for SP in $STEPS; do
    TAG="${SP%%:*}"; H="${SP##*:}"
    run_stage "c${IDX}_fdp_${TAG}" run_model "$IDX" plus  "$H" "d12f_c${IDX}_fdp_${TAG}" \
      || echo "STAGE c${IDX}_fdp_${TAG} NONZERO rc"
    run_stage "c${IDX}_fdm_${TAG}" run_model "$IDX" minus "$H" "d12f_c${IDX}_fdm_${TAG}" \
      || echo "STAGE c${IDX}_fdm_${TAG} NONZERO rc"
  done
done

echo "TOTAL_SPENT_CORE_MIN=$SPENT_CORE_MIN CAP=$CAP_CORE_MIN" | tee -a "$LEDGER"
echo "FINISHED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LEDGER"
