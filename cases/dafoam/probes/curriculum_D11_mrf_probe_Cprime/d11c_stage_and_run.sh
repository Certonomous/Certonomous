#!/usr/bin/env bash
# CURRICULUM D11-C' launcher -- the COMPONENT-1 FD STEP SWEEP.  Frozen instrument.
#
# WHAT THIS BUYS.  D11-F' graded `adj = dP[0]`: component 0 only.  Component 1 -- the one
# the MRF term dominates, moving from 3.1484221063860114e-09 (omega=0) to
# -1.366011909783860e-04 (omega=30) -- was never FD-checked.  This launcher produces the
# artifacts for that check, AS A SWEEP, because DAFOAM_CHARTER.md section 3 reads the
# plateau PER COMPONENT and a step proved in m/s on component 0 has no standing in
# degrees on component 1.  A secondary, separately registered sweep re-asks component 0
# in m/s so the standing of D11-F's h = 1.0e-3 can be settled either way.
#
# NOTHING OF D11-F' IS EDITED.  This is a new tree, a new pre-registration, new gates.
#
# OPERATIONAL FACTS CARRIED IN, NOT REDISCOVERED:
#   * `-flag=value`.  argparse reads a bare `-aoaOffset -1.0e-3` as an OPTION FLAG, not a
#     value: its negative-number matcher accepts `-1` and `-0.001` but NOT exponent
#     notation.  That defect cost the D11 chain three attempts.
#   * mpirun inside `--cpus=N` binds rank 0 to the FIRST CORE OF THE HOST TOPOLOGY, so
#     concurrent containers collide on one core while the box reports itself idle.  Every
#     container here is pinned with `--cpuset-cpus` AND the placement is READ BACK from
#     the process into each JSON record; the grader compares the reading, not the flag.
#   * no `--rm`, so `docker inspect` survives the container (L-252 pattern from
#     cases/dafoam/ladder-a/A1/curriculum_D2/d2_run_arm.sh).
#   * `set -e` does not gate at the top level of a harness Bash call; every step below
#     carries its own explicit `|| { echo ABORT...; exit 1; }`.
set -uo pipefail

IMG="${IMG:-dafoam/opt-packages:latest}"
BASE="${BASE:-/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D11C}"
SRC="${SRC:-/home/ubuntu/Certonomous/cases/dafoam/probes/curriculum_D11_mrf_probe_Cprime/d11c_case}"
RUNPY="${RUNPY:-/home/ubuntu/Certonomous/cases/dafoam/probes/curriculum_D11_mrf_probe_Cprime/d11c_run_script.py}"
TMO="${TMO:-240}"

# ---- THE REGISTERED CAP.  A peer lane today registered 3.0 core-min and enforced 6.0 by
# ---- copy-forward with no assertion.  Harmless in outcome, a freeze-integrity defect in
# ---- kind.  The literal below is the ONE number, and it is ASSERTED equal to the figure
# ---- written into PREREGISTRATION.md section 6.  There is deliberately NO env override.
REGISTERED_CAP_CORE_MIN="8.0"
CAP_CORE_MIN="8.0"
PREREG="/home/ubuntu/Certonomous/cases/dafoam/probes/curriculum_D11_mrf_probe_Cprime/PREREGISTRATION.md"
python3 -c "
import sys
assert abs(float('$CAP_CORE_MIN') - float('$REGISTERED_CAP_CORE_MIN')) < 1e-12, 'ENFORCED CAP != REGISTERED CAP'
" || { echo "ABORT: enforced cap $CAP_CORE_MIN != registered cap $REGISTERED_CAP_CORE_MIN"; exit 1; }
grep -qF "REGISTERED CAP: ${REGISTERED_CAP_CORE_MIN} core-min" "$PREREG" \
  || { echo "ABORT: the pre-registration does not carry the literal 'REGISTERED CAP: ${REGISTERED_CAP_CORE_MIN} core-min'; the enforced cap is not the registered one"; exit 1; }
echo "CAP ASSERTION PASSED: enforced=$CAP_CORE_MIN registered=$REGISTERED_CAP_CORE_MIN, and the literal is present in $PREREG"

CPUSET="${CPUSET:-13}"          # registered in PREREGISTRATION.md section 7; grader asserts the READ-BACK
SPENT_CORE_MIN=0
OMEGA_PLANT="30.0"
OMEGA_INERT="0.0"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
mkdir -p "$BASE" || { echo "ABORT: cannot mkdir $BASE"; exit 1; }
chmod 777 "$BASE"
LEDGER="$BASE/ledger.txt"
echo "=== D11-C' RUN $STAMP cpuset=$CPUSET cap=$CAP_CORE_MIN ===" | tee -a "$LEDGER"

# image identity is an ID, never a tag (DAFOAM_CHARTER section 6)
IMGID=$(sudo -n docker image inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
test -n "$IMGID" || { echo "ABORT: cannot resolve image id for $IMG"; exit 1; }
echo "IMAGE $IMG ID=$IMGID" | tee -a "$LEDGER"

sudo -n rm -rf "$BASE/mesh" 2>/dev/null
cp -a "$SRC" "$BASE/mesh" || { echo "ABORT: stage copy failed"; exit 1; }
cp -a "$RUNPY" "$BASE/mesh/" || { echo "ABORT: runscript copy failed"; exit 1; }
MT0=$(date -u +%s)
timeout 300 sudo -n docker run --name "d11c_mesh_${STAMP}" --user 0:0 --cpus=1 --cpuset-cpus="$CPUSET" \
    -v "$BASE":/mnt -w /mnt/mesh "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && blockMesh && topoSet && checkMesh -constant | tail -30" \
    > "$BASE/mesh_${STAMP}.log" 2>&1
mrc=$?
MT1=$(date -u +%s)
SPENT_CORE_MIN=$(python3 -c "print(round(($MT1-$MT0)/60.0,4))")
sudo -n docker rm "d11c_mesh_${STAMP}" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$BASE" 2>/dev/null
if [ $mrc -ne 0 ]; then echo "ABORT: blockMesh/topoSet rc=$mrc, see mesh_${STAMP}.log"; exit 1; fi
grep -a "^nCells" "$BASE/mesh_${STAMP}.log" | tee -a "$LEDGER"
test -f "$BASE/mesh/constant/polyMesh/cellZones" || test -f "$BASE/mesh/constant/polyMesh/cellZones.gz" \
  || { echo "ABORT: topoSet produced no cellZones -- MRF zone absent"; exit 1; }
echo "MRF_CELLZONE_CREATED rotor  mesh_core_min=$SPENT_CORE_MIN" | tee -a "$LEDGER"

run_stage () {
  # ---- REGISTERED BUDGET GUARD: an overrun STOPS the probe (CLAUDE.md rule 12)
  if python3 -c "import sys; sys.exit(0 if $SPENT_CORE_MIN >= $CAP_CORE_MIN else 1)"; then
    echo "BUDGET STOP: $SPENT_CORE_MIN core-min spent >= cap $CAP_CORE_MIN; stage $1 NOT LAUNCHED" | tee -a "$LEDGER"
    return 9
  fi
  local STAGE="$1" TASK="$2" OMEGA="$3" UOFF="$4" AOFF="$5"
  local NAME="d11c_${STAGE}_${STAMP}"
  local LOG="$BASE/${STAGE}_${STAMP}.log"

  # ---- COLD START, PROVED BEFORE THE CONTAINER STARTS.
  # Rule 4's age guard is UNSATISFIABLE on this family: a DAFoam run gzips 0/U to 0/U.gz
  # mid-solve, so no post-hoc mtime comparison against 0/U can be formed.  Its evidentiary
  # purpose -- that no stale answer could have produced the number -- is discharged HERE
  # instead, and more strongly: the arm directory is destroyed, re-copied from the mesh
  # tree, and the ANSWER FILE IS ASSERTED ABSENT while the container is not yet running.
  sudo -n rm -rf "$BASE/$STAGE" 2>/dev/null
  cp -a "$BASE/mesh" "$BASE/$STAGE" || { echo "ABORT: stage $STAGE copy failed"; return 4; }
  cp -a "$BASE/mesh/0.orig" "$BASE/$STAGE/0" || { echo "ABORT: 0 copy failed"; return 4; }
  test -e "$BASE/$STAGE/d11c_${STAGE}.json" && { echo "COLDSTART FAIL: answer file already exists for $STAGE"; return 5; }
  for bad in "$BASE/$STAGE/2000" "$BASE/$STAGE/1" "$BASE/$STAGE/0/U.gz"; do
    test -e "$bad" && { echo "COLDSTART FAIL: $bad exists before launch"; return 5; }
  done
  echo "COLDSTART_PROVED stage=$STAGE answer-file absent, no time dir, no 0/U.gz, before container start" | tee -a "$LEDGER"

  sed "s/OMEGA_PLACEHOLDER/${OMEGA}/" "$BASE/$STAGE/constant/MRFProperties.template" \
      > "$BASE/$STAGE/constant/MRFProperties" || { echo "ABORT: omega substitution failed"; return 4; }
  rm -f "$BASE/$STAGE/constant/MRFProperties.template"
  grep -qE "^[[:space:]]+omega[[:space:]]+${OMEGA};" "$BASE/$STAGE/constant/MRFProperties" \
      || { echo "ABORT: PLANT DID NOT LAND -- omega ${OMEGA} not in $STAGE/constant/MRFProperties"; return 4; }
  echo "PLANT_LANDED stage=$STAGE omega=${OMEGA}" | tee -a "$LEDGER"

  local T0 T1 WALL rc INSPECT AFF
  T0=$(date -u +%s)
  timeout "$TMO" sudo -n docker run --name "$NAME" \
      --user 0:0 --cpus=1 --cpuset-cpus="$CPUSET" --memory=6g --memory-swap=6g --oom-score-adj=500 \
      -v "$BASE":/mnt -w "/mnt/$STAGE" "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
       mpirun --allow-run-as-root --bind-to none -np 1 python d11c_run_script.py -task=$TASK -uOffset=$UOFF -aoaOffset=$AOFF -out=d11c_${STAGE}.json" \
      > "$LOG" 2>&1
  rc=$?
  T1=$(date -u +%s); WALL=$((T1-T0))
  INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
  sudo -n docker rm "$NAME" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "$LOG" "$BASE/$STAGE" 2>/dev/null
  AFF=$(python3 -c "
import json,sys
try:
    print(json.load(open('$BASE/$STAGE/d11c_${STAGE}.json')).get('sched_affinity'))
except Exception as e:
    print('UNREADABLE')" 2>/dev/null)
  local CM; CM=$(python3 -c "print(round($WALL/60.0,4))")
  echo "STAGE=$STAGE TASK=$TASK omega=$OMEGA uOffset=$UOFF aoaOffset=$AOFF rc=$rc wall_s=$WALL ranks=1 core_min=$CM measured_affinity=$AFF inspect(exit,oomkilled)=[$INSPECT] log=$(basename "$LOG")" | tee -a "$LEDGER"
  SPENT_CORE_MIN=$(python3 -c "print(round($SPENT_CORE_MIN + $CM, 4))")
  echo "SPENT_CORE_MIN=$SPENT_CORE_MIN of cap $CAP_CORE_MIN" | tee -a "$LEDGER"
  test -s "$LOG" && touch "$LOG.ok.${STAMP}"
  return $rc
}

# ---- scalar stages
run_stage omegaP compute_totals "$OMEGA_PLANT" 0.0 0.0 || echo "STAGE omegaP NONZERO rc"
run_stage omega0 compute_totals "$OMEGA_INERT" 0.0 0.0 || echo "STAGE omega0 NONZERO rc"
run_stage base1  run_model      "$OMEGA_PLANT" 0.0 0.0 || echo "STAGE base1 NONZERO rc"
run_stage base2  run_model      "$OMEGA_PLANT" 0.0 0.0 || echo "STAGE base2 NONZERO rc"

# ---- PRIMARY sweep: component 1, aoa in DEGREES, MRF ON.  Steps frozen; the grader
#      carries the identical list and refuses on a short table.
for pair in "1em5 1.0e-5" "1em4 1.0e-4" "1em3 1.0e-3" "1em2 1.0e-2" "1em1 1.0e-1" "1e00 1.0e0"; do
  set -- $pair
  run_stage "aoa_p_$1" run_model "$OMEGA_PLANT" 0.0 "$2"  || echo "STAGE aoa_p_$1 NONZERO rc"
  run_stage "aoa_m_$1" run_model "$OMEGA_PLANT" 0.0 "-$2" || echo "STAGE aoa_m_$1 NONZERO rc"
done

# ---- SECONDARY sweep: component 0, U in m/s, MRF ON.  Registered in advance as NOT
#      altering the probe verdict; it exists to settle the standing of D11-F's h = 1.0e-3.
for pair in "1em4 1.0e-4" "1em3 1.0e-3" "1em2 1.0e-2" "1em1 1.0e-1"; do
  set -- $pair
  run_stage "u_p_$1" run_model "$OMEGA_PLANT" "$2" 0.0  || echo "STAGE u_p_$1 NONZERO rc"
  run_stage "u_m_$1" run_model "$OMEGA_PLANT" "-$2" 0.0 || echo "STAGE u_m_$1 NONZERO rc"
done

echo "TOTAL_SPENT_CORE_MIN=$SPENT_CORE_MIN CAP=$CAP_CORE_MIN" | tee -a "$LEDGER"
echo "STAMP=$STAMP" | tee -a "$LEDGER"
