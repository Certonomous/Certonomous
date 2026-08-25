#!/usr/bin/env bash
# CURRICULUM D10-F' launcher -- the FD PAIR for the D10-P' adjoint gradient.
# FROZEN INSTRUMENT; fixed at the pre-registration commit.
#
# Container pattern inherited VERBATIM from d10p_stage_and_run.sh, which is the proven
# invocation on this box:
#   L-251  --user 0:0 pinned
#   L-252  per-invocation STAMP; .ok.STAMP provenance sentinel
#   8.1    kernel-only stop: --memory == --memory-swap, --oom-score-adj=500, timeout
#   8.2    no --rm, so `docker inspect .State.OOMKilled` survives the arm
#   --bind-to none, which avoided the measured 3.99x CPU-0 collision
#
# THE CASE IS NOT COPIED INTO THIS DIRECTORY.  SRC points AT D10-P''s own d10p_case.
# That is deliberate and is stronger than a copy: an FD table is a table about D10-P''s
# gradient only if it ran on D10-P''s case, and pointing at the one directory makes that
# true by construction rather than by a hash somebody has to remember to check.
#
# Stages, ALL np=1, numberOfSubdomains 1 (DAFOAM_CHARTER.md §5: serial before parallel;
# a gradient verified at one np is a statement about that np).
#   mesh                blockMesh + checkMesh, once
#   base   compute_totals  patchV0 = 10.0        -> INSTRUMENT IDENTITY control (C1)
#   rep0   run_model       patchV0 = 10.0        -> delta_repeat, first  (C5)
#   rep1   run_model       patchV0 = 10.0        -> delta_repeat, second (C5)
#   plant  run_model       patchV0 = 10.0, 0/T lowerWall +1.234 K -> planted zero (C2)
#   fdp_sN run_model       patchV0 = 10.0 + h
#   fdm_sN run_model       patchV0 = 10.0 - h    (10 - h is ALWAYS POSITIVE for every
#                                                 registered h, so no negative number is
#                                                 ever written on a command line)
set -uo pipefail

IMG="${IMG:-dafoam/opt-packages:latest}"
# Toolchain identity is the IMAGE ID, never the tag (DAFOAM_CHARTER.md §11).
IMG_ID_EXPECT="sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"
BASE="${BASE:-/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D10F}"
SRC="${SRC:-/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_D10_probe_Pprime/d10p_case}"
RUNPY="${RUNPY:-/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_D10_probe_Fprime/d10f_run_script.py}"
TMO="${TMO:-240}"
# REGISTERED RUNAWAY GUARD, core-min, cumulative over EVERY container this arm launches.
# Cost constraints are LIFTED (Sanaa, 2026-08-25), so this is a RUNAWAY GUARD reported to
# the supervisor, not a budget rigor is trimmed to fit.  A trip STOPS the arm and is
# reported; it does not get a new number.
CAP_CORE_MIN="${CAP_CORE_MIN:-8.0}"
SPENT_CORE_MIN=0
DV_BASE="10.0"
BASE_T="353.15"
PLANTED_T="354.384"      # 353.15 + 1.234, written literally so the grader reads it back
# The registered step sweep.  tag:h  -- must match STEPS in d10f_grade.py exactly.
STEPS="s1:1.0e-5 s2:1.0e-4 s3:1.0e-3 s4:1.0e-2 s5:1.0e-1 s6:5.0e-1"

# ---- toolchain identity, asserted before a single core-minute is spent ----
GOT_ID=$(sudo -n docker inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
[ "$GOT_ID" = "$IMG_ID_EXPECT" ] || { echo "ABORT: image id is '$GOT_ID', registered '$IMG_ID_EXPECT'"; exit 1; }
echo "IMAGE_ID_VERIFIED=$GOT_ID"

# ---- the guard that refuses a run root that already exists.  A guard that refuses is
# ---- the guard WORKING; it is never disabled to get past a completed stage.
if [ -e "$BASE" ]; then
  echo "REFUSE: run root already exists: $BASE"
  echo "A completed arm is not deleted to re-run it.  Inspect it, do not clear it."
  exit 6
fi
mkdir -p "$BASE" || { echo "ABORT: cannot mkdir $BASE"; exit 1; }
chmod 777 "$BASE"
LEDGER="$BASE/ledger.txt"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
{ echo "ARM=D10Fprime"; echo "IMAGE_ID=$GOT_ID"; echo "NP=1 numberOfSubdomains=1";
  echo "STEPS=$STEPS"; echo "CAP_CORE_MIN=$CAP_CORE_MIN"; echo "STAMP=$STAMP";
  echo "STARTED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } | tee -a "$LEDGER"

# ---- mesh, once -----------------------------------------------------------
cp -a "$SRC" "$BASE/mesh" || { echo "ABORT: stage copy failed"; exit 1; }
cp -a "$RUNPY" "$BASE/mesh/" || { echo "ABORT: runscript copy failed"; exit 1; }
timeout 300 sudo -n docker run --name "d10f_mesh_${STAMP}" --user 0:0 --cpus=1 \
    -v "$BASE":/mnt -w /mnt/mesh "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && blockMesh && checkMesh -constant | tail -30" \
    > "$BASE/mesh_${STAMP}.log" 2>&1
mrc=$?
SPENT_CORE_MIN=$(python3 -c "print(round($SECONDS/60.0,4))")
sudo -n docker rm "d10f_mesh_${STAMP}" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$BASE" 2>/dev/null
if [ $mrc -ne 0 ]; then echo "ABORT: blockMesh/checkMesh rc=$mrc"; exit 1; fi
grep -a "^nCells" "$BASE/mesh_${STAMP}.log" | tee -a "$LEDGER"
echo "MESH_SPENT_CORE_MIN=$SPENT_CORE_MIN" | tee -a "$LEDGER"

run_stage () {
  # $1 stage dir, $2 task, $3 patchV0, $4 plant yes/no, $5 json basename
  if python3 -c "import sys; sys.exit(0 if $SPENT_CORE_MIN >= $CAP_CORE_MIN else 1)"; then
    echo "RUNAWAY GUARD TRIPPED: $SPENT_CORE_MIN core-min >= cap $CAP_CORE_MIN; stage $1 NOT LAUNCHED" | tee -a "$LEDGER"
    return 9
  fi
  local STAGE="$1" TASK="$2" PV="$3" PLANT="$4" JB="$5"
  local NAME="d10f_${STAGE}_${STAMP}"
  local LOG="$BASE/${STAGE}_${STAMP}.log"
  cp -a "$BASE/mesh" "$BASE/$STAGE" || { echo "ABORT: stage $STAGE copy failed"; return 4; }
  cp -a "$BASE/mesh/0.orig" "$BASE/$STAGE/0" || { echo "ABORT: 0 copy failed"; return 4; }
  if [ "$PLANT" = "yes" ]; then
    sed -i "s/uniform ${BASE_T};/uniform ${PLANTED_T};/" "$BASE/$STAGE/0/T" || { echo "ABORT: plant sed"; return 4; }
    grep -q "uniform ${PLANTED_T};" "$BASE/$STAGE/0/T" || { echo "ABORT: PLANT DID NOT LAND in $STAGE/0/T"; return 4; }
    echo "PLANT_LANDED stage=$STAGE file=$STAGE/0/T value=${PLANTED_T}" | tee -a "$LEDGER"
  else
    grep -q "uniform ${BASE_T};" "$BASE/$STAGE/0/T" || { echo "ABORT: baseline 0/T not at ${BASE_T}"; return 4; }
  fi
  # cold-start guard (CLAUDE.md rule 4): no pre-existing time dirs, no processor dirs
  for bad in "$BASE/$STAGE/2000" "$BASE/$STAGE/1"; do
    test -e "$bad" && { echo "COLDSTART FAIL: $bad exists"; return 5; }
  done
  test -n "$(ls -d "$BASE/$STAGE"/processor* 2>/dev/null)" && { echo "COLDSTART FAIL: processor* present"; return 5; }
  local T0 T1 WALL rc INSPECT
  T0=$(date -u +%s)
  timeout "$TMO" sudo -n docker run --name "$NAME" \
      --user 0:0 --cpus=1 --memory=6g --memory-swap=6g --oom-score-adj=500 \
      -v "$BASE":/mnt -w "/mnt/$STAGE" "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
       mpirun --allow-run-as-root --bind-to none -np 1 python d10f_run_script.py \
       -task $TASK -patchV0 $PV -out ${JB}.json" \
      > "$LOG" 2>&1
  rc=$?
  T1=$(date -u +%s); WALL=$((T1-T0))
  INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
  sudo -n docker rm "$NAME" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "$LOG" "$BASE/$STAGE" 2>/dev/null
  local CM; CM=$(python3 -c "print(round($WALL/60.0,4))")
  echo "STAGE=$STAGE TASK=$TASK patchV0=$PV plant=$PLANT rc=$rc wall_s=$WALL ranks=1 core_min=$CM inspect(exit,oomkilled)=[$INSPECT] json=$STAGE/${JB}.json log=$(basename "$LOG")" | tee -a "$LEDGER"
  SPENT_CORE_MIN=$(python3 -c "print(round($SPENT_CORE_MIN + $CM, 4))")
  echo "SPENT_CORE_MIN=$SPENT_CORE_MIN of cap $CAP_CORE_MIN" | tee -a "$LEDGER"
  test -s "$LOG" && touch "$LOG.ok.${STAMP}"
  return $rc
}

run_stage base  compute_totals "$DV_BASE" no  d10f_base  || echo "STAGE base NONZERO rc"
run_stage rep0  run_model      "$DV_BASE" no  d10f_rep0  || echo "STAGE rep0 NONZERO rc"
run_stage rep1  run_model      "$DV_BASE" no  d10f_rep1  || echo "STAGE rep1 NONZERO rc"
run_stage plant run_model      "$DV_BASE" yes d10f_plant || echo "STAGE plant NONZERO rc"

for SP in $STEPS; do
  TAG="${SP%%:*}"; H="${SP##*:}"
  VP=$(python3 -c "print(repr($DV_BASE + $H))")
  VM=$(python3 -c "print(repr($DV_BASE - $H))")
  # NO NEGATIVE NUMBER EVER REACHES A COMMAND LINE: assert both are positive first.
  python3 -c "import sys; sys.exit(0 if ($VP>0 and $VM>0) else 1)" \
    || { echo "ABORT: step $TAG would put a non-positive value on the CLI"; exit 1; }
  run_stage "fdp_${TAG}" run_model "$VP" no "d10f_fdp_${TAG}" || echo "STAGE fdp_${TAG} NONZERO rc"
  run_stage "fdm_${TAG}" run_model "$VM" no "d10f_fdm_${TAG}" || echo "STAGE fdm_${TAG} NONZERO rc"
done

echo "TOTAL_SPENT_CORE_MIN=$SPENT_CORE_MIN CAP=$CAP_CORE_MIN" | tee -a "$LEDGER"
echo "FINISHED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LEDGER"
