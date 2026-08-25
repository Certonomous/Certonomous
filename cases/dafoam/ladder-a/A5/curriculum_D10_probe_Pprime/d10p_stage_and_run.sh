#!/usr/bin/env bash
# CURRICULUM D10-P' CAPABILITY PROBE launcher (the plant re-buy).  Frozen instrument.
#
# The D10 probe as registered returned NOT A RESULT because its plant was on the
# INITIAL internal field of 0/T, and a converged steady solve is independent of its
# initial guess by construction: HFX moved by EXACTLY 0.0.  Here the same +1.234 K is
# planted on the HEATED LOWER WALL FIXED-VALUE BOUNDARY, which IS an input to the
# converged answer.  Nothing else about the case, the driver or the gates changed.
#
# Derived from cases/dafoam/ladder-a/A1/curriculum_D2/d2_run_arm.sh, which is the
# proven container-invocation pattern on this box.  Inherited verbatim:
#   L-251  --user 0:0 pinned
#   L-252  per-invocation STAMP; .ok.STAMP provenance sentinel
#   8.1    kernel-only stop: --memory == --memory-swap, --oom-score-adj=500, timeout
#   8.2    no --rm, so `docker inspect .State.OOMKilled` survives the run
#
# Three stages, all np=1:
#   base   compute_totals  (primal + adjoint)          -> d10_base.json
#   plant  run_model       (PLANTED 0/T, +1.234 K)     -> d10_plant.json
#   clean  run_model       (UNPLANTED second copy)     -> d10_clean.json
set -uo pipefail

IMG="${IMG:-dafoam/opt-packages:latest}"
BASE="${BASE:-/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D10P}"
SRC="${SRC:-/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_D10_probe_Pprime/d10p_case}"
RUNPY="${RUNPY:-/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_D10_probe_Pprime/d10p_run_script.py}"
TMO="${TMO:-240}"
# REGISTERED BUDGET CAP, core-min, cumulative over EVERY container this probe launches
# (mesh build included).  An overrun STOPS the probe; it does not get a new budget
# (CLAUDE.md rule 12).
CAP_CORE_MIN="${CAP_CORE_MIN:-5.0}"
SPENT_CORE_MIN=0
PLANT_T="1.234"          # K, added to the HEATED WALL BOUNDARY TEMPERATURE in the plant stage
BASE_T="353.15"          # lowerWall fixedValue in 0/T
PLANTED_T="354.384"      # 353.15 + 1.234, written literally so the grader can read it back

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
mkdir -p "$BASE" || { echo "ABORT: cannot mkdir $BASE"; exit 1; }
chmod 777 "$BASE"
LEDGER="$BASE/ledger.txt"

# ---- 1. build the mesh once, in a container -------------------------------
sudo -n rm -rf "$BASE/mesh" 2>/dev/null
cp -a "$SRC" "$BASE/mesh" || { echo "ABORT: stage copy failed"; exit 1; }
cp -a "$RUNPY" "$BASE/mesh/" || { echo "ABORT: runscript copy failed"; exit 1; }
timeout 300 sudo -n docker run --name "d10p_mesh_${STAMP}" --user 0:0 --cpus=1 \
    -v "$BASE":/mnt -w /mnt/mesh "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && blockMesh && checkMesh -constant | tail -30" \
    > "$BASE/mesh_${STAMP}.log" 2>&1
mrc=$?
MESH_WALL=$SECONDS
SPENT_CORE_MIN=$(python3 -c "print(round($SECONDS/60.0,4))")
sudo -n docker rm "d10p_mesh_${STAMP}" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$BASE" 2>/dev/null
if [ $mrc -ne 0 ]; then echo "ABORT: blockMesh/checkMesh rc=$mrc, see mesh_${STAMP}.log"; exit 1; fi
grep -a "^nCells" "$BASE/mesh_${STAMP}.log" | tee -a "$LEDGER"

run_stage () {
  # ---- REGISTERED BUDGET GUARD: an overrun STOPS the probe (CLAUDE.md rule 12)
  if python3 -c "import sys; sys.exit(0 if $SPENT_CORE_MIN >= $CAP_CORE_MIN else 1)"; then
    echo "BUDGET STOP: $SPENT_CORE_MIN core-min spent >= cap $CAP_CORE_MIN; stage $1 NOT LAUNCHED" | tee -a "$LEDGER"
    return 9
  fi
  local STAGE="$1" TASK="$2" PLANT="$3"
  local NAME="d10p_${STAGE}_${STAMP}"
  local LOG="$BASE/${STAGE}_${STAMP}.log"
  sudo -n rm -rf "$BASE/$STAGE" 2>/dev/null
  cp -a "$BASE/mesh" "$BASE/$STAGE" || { echo "ABORT: stage $STAGE copy failed"; return 4; }
  cp -a "$BASE/mesh/0.orig" "$BASE/$STAGE/0" || { echo "ABORT: 0 copy failed"; return 4; }
  if [ "$PLANT" = "yes" ]; then
    sed -i "s/uniform ${BASE_T};/uniform ${PLANTED_T};/" "$BASE/$STAGE/0/T" \
      || { echo "ABORT: plant sed failed"; return 4; }
    grep -q "uniform ${PLANTED_T};" "$BASE/$STAGE/0/T" || { echo "ABORT: PLANT DID NOT LAND in $STAGE/0/T"; return 4; }
    echo "PLANT_LANDED stage=$STAGE file=$STAGE/0/T value=${PLANTED_T}" | tee -a "$LEDGER"
  else
    grep -q "uniform ${BASE_T};" "$BASE/$STAGE/0/T" || { echo "ABORT: baseline 0/T not at ${BASE_T}"; return 4; }
  fi
  # cold-start guard (strict-completion rule 4): no pre-existing time dirs
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
       mpirun --allow-run-as-root --bind-to none -np 1 python d10p_run_script.py -task $TASK -out d10p_${STAGE}.json" \
      > "$LOG" 2>&1
  rc=$?
  T1=$(date -u +%s); WALL=$((T1-T0))
  INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
  sudo -n docker rm "$NAME" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "$LOG" "$BASE/$STAGE" 2>/dev/null
  local CM; CM=$(python3 -c "print(round($WALL/60.0,4))")
  echo "STAGE=$STAGE TASK=$TASK rc=$rc wall_s=$WALL ranks=1 core_min=$CM inspect(exit,oomkilled)=[$INSPECT] json=$STAGE/d10p_${STAGE}.json log=$(basename "$LOG")" | tee -a "$LEDGER"
  SPENT_CORE_MIN=$(python3 -c "print(round($SPENT_CORE_MIN + $CM, 4))")
  echo "SPENT_CORE_MIN=$SPENT_CORE_MIN of cap $CAP_CORE_MIN" | tee -a "$LEDGER"
  test -s "$LOG" && touch "$LOG.ok.${STAMP}"
  return $rc
}

run_stage base  compute_totals no  || echo "STAGE base NONZERO rc"
run_stage plant run_model      yes || echo "STAGE plant NONZERO rc"
run_stage clean run_model      no  || echo "STAGE clean NONZERO rc"
echo "TOTAL_SPENT_CORE_MIN=$SPENT_CORE_MIN CAP=$CAP_CORE_MIN" | tee -a "$LEDGER"
echo "STAMP=$STAMP" | tee -a "$LEDGER"
