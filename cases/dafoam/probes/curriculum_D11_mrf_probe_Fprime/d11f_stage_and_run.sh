#!/usr/bin/env bash
# CURRICULUM D11-F' CAPABILITY PROBE launcher (the CLI re-buy).  Frozen instrument.
# Frozen instrument.
#
# D11-D' fixed the dictionary and proved it: omega=0 ran primal AND adjoint to rc=0.
# omega=300 rad/s did not -- the steady SIMPLE primal STALLED, continuity plateauing
# at ~2.5e-4 and never reaching primalMinResTol, so DAFoam raised
#   openmdao.core.analysis_error.AnalysisError: Primal solution failed!
# and no JSON was written.  That is the SUBSTRATE refusing a 300 rad/s zone, not the
# capability being absent.  ONE reduction, to 30.0 rad/s, registered before this run
# with its reason, and NO FOURTH ATTEMPT.
#
# The D11 probe as registered returned NOT A RESULT: every stage died pre-grading on
#   --> FOAM FATAL IO ERROR: Entry 'MRF' not found in dictionary "constant/MRFProperties"
# because the frozen MRFProperties.template used OpenFOAM's named-zone layout while
# DAFoam's IOMRFZoneListDF wants a single top-level `MRF` sub-dictionary.  That is a
# defect in THIS INSTRUMENT, and it is NOT the BLOCKED branch of D11's frozen mapping:
# the capability was never reached, so it was never shown absent.  Only the dictionary
# layout changed.  Gates, thresholds, plant magnitude, FD step and cap are D11's.
# Container pattern inherited from cases/dafoam/ladder-a/A1/curriculum_D2/d2_run_arm.sh
# (L-251 --user 0:0; L-252 STAMP + .ok sentinel; 8.1 kernel-only stop; 8.2 no --rm).
#
# THE PLANT IS ON THE MRF ZONE: constant/MRFProperties `omega` is the only key that
# differs between the omegaP and omega0 stages.
#
# Stages, all np=1:
#   omegaP  omega=300 rad/s  compute_totals  -> d11_omegaP.json
#   omega0  omega=0   rad/s  compute_totals  -> d11_omega0.json
#   clean   omega=0   rad/s  run_model       -> d11_clean.json   (discrimination control)
#   fdp     omega=300        run_model  U0+h -> d11_fdp.json
#   fdm     omega=300        run_model  U0-h -> d11_fdm.json
set -uo pipefail

IMG="${IMG:-dafoam/opt-packages:latest}"
BASE="${BASE:-/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D11F}"
SRC="${SRC:-/home/ubuntu/Certonomous/cases/dafoam/probes/curriculum_D11_mrf_probe_Fprime/d11f_case}"
RUNPY="${RUNPY:-/home/ubuntu/Certonomous/cases/dafoam/probes/curriculum_D11_mrf_probe_Fprime/d11f_run_script.py}"
TMO="${TMO:-240}"
# REGISTERED BUDGET CAP, core-min, cumulative over EVERY container this probe launches
# (mesh build included).  An overrun STOPS the probe; it does not get a new budget
# (CLAUDE.md rule 12).
CAP_CORE_MIN="${CAP_CORE_MIN:-5.0}"
SPENT_CORE_MIN=0
OMEGA_PLANT="30.0"      # rad/s -- THE PLANT, reduced once and only once; see PREREGISTRATION section 0
OMEGA_INERT="0.0"
FD_H="1.0e-3"           # m/s, central, on patchV[0]

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
mkdir -p "$BASE" || { echo "ABORT: cannot mkdir $BASE"; exit 1; }
chmod 777 "$BASE"
LEDGER="$BASE/ledger.txt"

sudo -n rm -rf "$BASE/mesh" 2>/dev/null
cp -a "$SRC" "$BASE/mesh" || { echo "ABORT: stage copy failed"; exit 1; }
cp -a "$RUNPY" "$BASE/mesh/" || { echo "ABORT: runscript copy failed"; exit 1; }
timeout 300 sudo -n docker run --name "d11f_mesh_${STAMP}" --user 0:0 --cpus=1 \
    -v "$BASE":/mnt -w /mnt/mesh "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && blockMesh && topoSet && checkMesh -constant | tail -30" \
    > "$BASE/mesh_${STAMP}.log" 2>&1
mrc=$?
MESH_WALL=$SECONDS
SPENT_CORE_MIN=$(python3 -c "print(round($SECONDS/60.0,4))")
sudo -n docker rm "d11f_mesh_${STAMP}" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$BASE" 2>/dev/null
if [ $mrc -ne 0 ]; then echo "ABORT: blockMesh/topoSet rc=$mrc, see mesh_${STAMP}.log"; exit 1; fi
grep -a "^nCells" "$BASE/mesh_${STAMP}.log" | tee -a "$LEDGER"
test -f "$BASE/mesh/constant/polyMesh/cellZones" || test -f "$BASE/mesh/constant/polyMesh/cellZones.gz" \
  || { echo "ABORT: topoSet produced no cellZones -- MRF zone absent"; exit 1; }
echo "MRF_CELLZONE_CREATED rotor" | tee -a "$LEDGER"

run_stage () {
  # ---- REGISTERED BUDGET GUARD: an overrun STOPS the probe (CLAUDE.md rule 12)
  if python3 -c "import sys; sys.exit(0 if $SPENT_CORE_MIN >= $CAP_CORE_MIN else 1)"; then
    echo "BUDGET STOP: $SPENT_CORE_MIN core-min spent >= cap $CAP_CORE_MIN; stage $1 NOT LAUNCHED" | tee -a "$LEDGER"
    return 9
  fi
  local STAGE="$1" TASK="$2" OMEGA="$3" UOFF="$4"
  local NAME="d11f_${STAGE}_${STAMP}"
  local LOG="$BASE/${STAGE}_${STAMP}.log"
  sudo -n rm -rf "$BASE/$STAGE" 2>/dev/null
  cp -a "$BASE/mesh" "$BASE/$STAGE" || { echo "ABORT: stage $STAGE copy failed"; return 4; }
  cp -a "$BASE/mesh/0.orig" "$BASE/$STAGE/0" || { echo "ABORT: 0 copy failed"; return 4; }
  sed "s/OMEGA_PLACEHOLDER/${OMEGA}/" "$BASE/$STAGE/constant/MRFProperties.template" \
      > "$BASE/$STAGE/constant/MRFProperties" || { echo "ABORT: omega substitution failed"; return 4; }
  rm -f "$BASE/$STAGE/constant/MRFProperties.template"
  grep -qE "^[[:space:]]+omega[[:space:]]+${OMEGA};" "$BASE/$STAGE/constant/MRFProperties" \
      || { echo "ABORT: PLANT DID NOT LAND -- omega ${OMEGA} not in $STAGE/constant/MRFProperties"; return 4; }
  echo "PLANT_LANDED stage=$STAGE file=$STAGE/constant/MRFProperties omega=${OMEGA}" | tee -a "$LEDGER"
  for bad in "$BASE/$STAGE/2000" "$BASE/$STAGE/1"; do
    test -e "$bad" && { echo "COLDSTART FAIL: $bad exists"; return 5; }
  done
  local T0 T1 WALL rc INSPECT
  T0=$(date -u +%s)
  timeout "$TMO" sudo -n docker run --name "$NAME" \
      --user 0:0 --cpus=1 --memory=6g --memory-swap=6g --oom-score-adj=500 \
      -v "$BASE":/mnt -w "/mnt/$STAGE" "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
       mpirun --allow-run-as-root --bind-to none -np 1 python d11f_run_script.py -task $TASK -uOffset=$UOFF -out d11f_${STAGE}.json" \
      > "$LOG" 2>&1
  rc=$?
  T1=$(date -u +%s); WALL=$((T1-T0))
  INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
  sudo -n docker rm "$NAME" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "$LOG" "$BASE/$STAGE" 2>/dev/null
  local CM; CM=$(python3 -c "print(round($WALL/60.0,4))")
  echo "STAGE=$STAGE TASK=$TASK omega=$OMEGA uOffset=$UOFF rc=$rc wall_s=$WALL ranks=1 core_min=$CM inspect(exit,oomkilled)=[$INSPECT] log=$(basename "$LOG")" | tee -a "$LEDGER"
  SPENT_CORE_MIN=$(python3 -c "print(round($SPENT_CORE_MIN + $CM, 4))")
  echo "SPENT_CORE_MIN=$SPENT_CORE_MIN of cap $CAP_CORE_MIN" | tee -a "$LEDGER"
  test -s "$LOG" && touch "$LOG.ok.${STAMP}"
  return $rc
}

run_stage omegaP compute_totals "$OMEGA_PLANT" 0.0        || echo "STAGE omegaP NONZERO rc"
run_stage omega0 compute_totals "$OMEGA_INERT" 0.0        || echo "STAGE omega0 NONZERO rc"
run_stage clean  run_model      "$OMEGA_INERT" 0.0        || echo "STAGE clean NONZERO rc"
run_stage fdp    run_model      "$OMEGA_PLANT" "$FD_H"    || echo "STAGE fdp NONZERO rc"
run_stage fdm    run_model      "$OMEGA_PLANT" "-$FD_H"   || echo "STAGE fdm NONZERO rc"
echo "TOTAL_SPENT_CORE_MIN=$SPENT_CORE_MIN CAP=$CAP_CORE_MIN" | tee -a "$LEDGER"
echo "STAMP=$STAMP" | tee -a "$LEDGER"
