#!/usr/bin/env bash
# CURRICULUM D9successor -- U-BEND PRESSURE-LOSS MINIMISATION WITH A meshQualityKS
# NON-ORTHOGONALITY CONSTRAINT, ladder A5.  DRAFT INSTRUMENT -- NOT FROZEN (awaiting
# the dafoam-supervisor's check-1 read and freeze).
#
# DERIVED FROM cases/dafoam/ladder-a/A5/curriculum_D9/d9_stage_and_run.sh
# (md5 7bb4234f75fa53556303c0c2408bb5a7).  CHANGES FROM D9, and nowhere else (each is
# a line in the _DELTAS_from_d9.diff):
#
#   D9SUCC-L1  RUNPY -> d9succ_run_script.py; PREREG -> D9successor/PREREGISTRATION.md.
#   D9SUCC-L2  REGISTERED_CAP_CORE_MIN 110.0 -> 120.0, asserted equal to the literal
#              'REGISTERED CAP: 120.0 core-min' in the frozen D9successor pre-registration
#              (PREREG section 5).  There is deliberately NO env override.
#   D9SUCC-L3  FD_STEPS re-registered to the 3 a-priori USABLE steps {5e-5,1e-4,2e-4}
#              (PREREG section 2.3); the probe 1e-3 is run SEPARATELY as the F-CEIL falsifier
#              (PREREG section 6), expected to invert the mesh, and is NEVER a usable step.
#   D9SUCC-L4  NEW `mesh` stage for the G-MESH headline: a run_model at the OPTIMISED
#              endpoint DV, whose primal-startup checkMesh block reports the RAW unperturbed
#              maxNonOrth -- the SAME mechanism by which D9 measured 80.93 (D9/RESULTS.md
#              section 2).  Its log is handed to the grader as --meshlog.
#
# STAGE ORDER IS REGISTERED AND IS NOT AN IMPLEMENTATION DETAIL:
#   1. cal          run_driver -maxit 1     THE CALIBRATION MAJOR, FIRST.
#   2. rep1, rep2   run_model x2            delta_repeat, MEASURED BEFORE ANY FD STEP.
#   3. opt          run_driver -maxit 20    the buy, NOW WITH THE meshQualityKS CONSTRAINT.
#   4. mesh         run_model @ endpoint    G-MESH: raw checkMesh maxNonOrth at the endpoint.
#   5. fd_<h>       check_totals            the endpoint FD table, 3 USABLE steps.
#   6. fd_probe     check_totals @ 1e-3     F-CEIL falsifier, EXPECTED to invert (not usable).
#
# OPERATIONAL FACTS CARRIED IN, NOT REDISCOVERED (verbatim from D9):
#   * `-flag=value`.  argparse reads a bare `-fdStep -1e-3` as an OPTION FLAG. Use `=`.
#   * mpirun inside `--cpus=N` binds rank 0 to the FIRST CORE OF THE HOST TOPOLOGY;
#     every container is pinned with `--cpuset-cpus` AND the placement is READ BACK.
#   * no `--rm`, so `docker inspect` survives the container.
#   * `set -e` does not gate at the top level of a harness Bash call; every step carries
#     its own explicit `|| { echo ABORT...; exit 1; }`.
#   * THE PATCHED IMAGE IS THE ONE BOUGHT (dafoam-idwarp-rot:v1); stock is GATE FAIL on
#     A5's OBJ.val wrt shapexUpper (2 sign flips), so an optimiser on the stock gradient
#     would be driving on a broken derivative.
set -uo pipefail

IMG="${IMG:-dafoam-idwarp-rot:v1}"
BASE="${BASE:-}"
SRC="${SRC:-/home/ubuntu/certonomous-runs/W5-regrade/a5pl_stock}"
RUNPY="${RUNPY:-/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_D9successor/d9succ_run_script.py}"
PREREG="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_D9successor/PREREGISTRATION.md"
GRADER="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_D9successor/d9succ_grade.py"

# ---- THE REGISTERED CAP.  One literal, asserted equal to the figure in the frozen
# ---- pre-registration.  There is deliberately NO env override.
REGISTERED_CAP_CORE_MIN="120.0"
CAP_CORE_MIN="120.0"
python3 -c "
assert abs(float('$CAP_CORE_MIN') - float('$REGISTERED_CAP_CORE_MIN')) < 1e-12, 'ENFORCED CAP != REGISTERED CAP'
" || { echo "ABORT: enforced cap $CAP_CORE_MIN != registered cap $REGISTERED_CAP_CORE_MIN"; exit 1; }
grep -qF "REGISTERED CAP: ${REGISTERED_CAP_CORE_MIN} core-min" "$PREREG" \
  || { echo "ABORT: the pre-registration does not carry the literal 'REGISTERED CAP: ${REGISTERED_CAP_CORE_MIN} core-min'"; exit 1; }
echo "CAP ASSERTION PASSED: enforced=$CAP_CORE_MIN registered=$REGISTERED_CAP_CORE_MIN, literal present in $PREREG"

MAXIT_CAL=1
MAXIT_OPT=20
FD_STEPS="5.0e-5 1.0e-4 2.0e-4"      # D9SUCC-L3: the 3 USABLE steps
PROBE_STEP="1.0e-3"                   # D9SUCC-L3: F-CEIL falsifier, expected to invert
TMO_CAL=900
TMO_REP=600
TMO_FD=1200
CPUSET="${CPUSET:-}"
[ -n "$CPUSET" ] || { echo "ABORT: CPUSET must be given explicitly; placement is registered, never defaulted"; exit 1; }
[ -n "$BASE" ]   || { echo "ABORT: BASE must be given explicitly (fresh timestamped run dir)"; exit 1; }

SPENT_CORE_MIN=0
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$

# THE GUARD.  A run directory that already exists is EVIDENCE, never something to delete.
[ -e "$BASE" ] && { echo "ABORT: $BASE already exists; guards refuse a case whose run directory exists. Use a fresh timestamped dir; NEVER delete an interrupted tree."; exit 1; }
mkdir -p "$BASE" || { echo "ABORT: cannot mkdir $BASE"; exit 1; }
chmod 777 "$BASE"
LEDGER="$BASE/ledger.txt"
echo "=== D9successor RUN $STAMP cpuset=$CPUSET cap=$CAP_CORE_MIN image=$IMG ===" | tee -a "$LEDGER"

# image identity is an ID, never a tag (DAFOAM_CHARTER section 6)
IMGID=$(sudo -n docker images --no-trunc --format '{{.ID}}' "$IMG" 2>/dev/null | head -1)
[ -n "$IMGID" ] || { echo "ABORT: cannot resolve image ID for $IMG"; exit 1; }
echo "IMAGE $IMG ID=$IMGID" | tee -a "$LEDGER"

# ---------------------------------------------------------------------------
# stage_arm <name> -- destroy and re-copy the arm tree, then PROVE COLD START.
# ---------------------------------------------------------------------------
stage_arm() {
  local name="$1"
  local arm="$BASE/$name"
  rm -rf "$arm" || { echo "ABORT: cannot clear $arm"; exit 1; }
  mkdir -p "$arm" || { echo "ABORT: cannot mkdir $arm"; exit 1; }
  cp -a "$SRC"/0 "$SRC"/0.orig "$SRC"/constant "$SRC"/system "$SRC"/FFD "$arm"/ 2>/dev/null \
    || { echo "ABORT: cannot stage case tree from $SRC"; exit 1; }
  cp "$RUNPY" "$arm"/runScript.py || { echo "ABORT: cannot stage run script"; exit 1; }
  # COLD-START PROOF, before any container starts.
  [ -e "$arm/d9_out.json" ] && { echo "ABORT: answer file present before launch in $name"; exit 1; }
  for t in $(ls -1 "$arm" 2>/dev/null | grep -E '^[0-9]+(\.[0-9]+)?$' | grep -v '^0$'); do
    echo "ABORT: time directory $t present before launch in $name"; exit 1
  done
  [ -e "$arm/0/U.gz" ] && { echo "ABORT: 0/U.gz present before launch in $name"; exit 1; }
  [ -f "$arm/0/U" ] || { echo "ABORT: 0/U absent after staging $name"; exit 1; }
  chmod -R 777 "$arm"
  echo "COLDSTART_PROVED stage=$name answer-file absent, no time dir, no 0/U.gz, before container start" | tee -a "$LEDGER"
}

# ---------------------------------------------------------------------------
# run_stage <name> <timeout_s> <extra args...>
# ---------------------------------------------------------------------------
run_stage() {
  local name="$1"; shift
  local tmo="$1"; shift
  local arm="$BASE/$name"
  local cname="d9succ_${name}_${STAMP}"
  local log="$BASE/${name}_${STAMP}.log"

  # CAP CHECK BEFORE the stage, not after.  An overrun STOPS the run (rule 12).
  local over
  over=$(python3 -c "print('1' if float('$SPENT_CORE_MIN') >= float('$CAP_CORE_MIN') else '0')")
  [ "$over" = "1" ] && { echo "STOP: cap $CAP_CORE_MIN core-min reached at $SPENT_CORE_MIN before stage $name; the run STOPS and does not get a new budget" | tee -a "$LEDGER"; return 9; }

  local t0 t1 wall rc
  t0=$(date +%s)
  timeout "$tmo" sudo -n docker run --name "$cname" --user 0:0 \
      --cpuset-cpus="$CPUSET" --cpus=1 --memory=3g --memory-swap=3g --oom-score-adj=500 \
      -e PYTHONHASHSEED=0 \
      -v "$arm":/mnt -w /mnt "$IMG" \
      bash -lc "source /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun --allow-run-as-root -np 1 -x PYTHONPATH -x PYTHONHASHSEED python runScript.py $*" \
      > "$log" 2>&1
  rc=$?
  t1=$(date +%s)
  wall=$((t1 - t0))

  local insp
  insp=$(sudo -n docker inspect -f '{{.State.ExitCode}} {{.State.OOMKilled}}' "$cname" 2>/dev/null)
  [ -n "$insp" ] || insp="NA NA"

  local cm
  cm=$(python3 -c "print(round($wall*1/60.0,4))")
  SPENT_CORE_MIN=$(python3 -c "print(round(float('$SPENT_CORE_MIN')+float('$cm'),4))")

  local aff="NA"
  if [ -f "$arm/d9_out.json" ]; then
    aff=$(python3 -c "
import json
try:
    d=json.load(open('$arm/d9_out.json'))
    print(d.get('sched_affinity','NA'))
except Exception:
    print('NA')
")
  fi

  echo "STAGE=$name ARGS=$* rc=$rc wall_s=$wall ranks=1 core_min=$cm measured_affinity=$aff inspect(exit,oomkilled)=[$insp] log=$(basename "$log")" | tee -a "$LEDGER"
  echo "SPENT_CORE_MIN=$SPENT_CORE_MIN of cap $CAP_CORE_MIN" | tee -a "$LEDGER"
  echo "$wall" > "$BASE/.wall_${name}"
  return $rc
}

# ===========================================================================
# 1.  THE CALIBRATION MAJOR -- FIRST, before any budget is committed to a buy.
# ===========================================================================
stage_arm cal
run_stage cal "$TMO_CAL" "-task=run_driver" "-optimizer=SLSQP" "-maxit=$MAXIT_CAL" "-out=d9_out.json"
CAL_RC=$?
CAL_WALL=$(cat "$BASE/.wall_cal" 2>/dev/null || echo 0)
echo "CALIBRATION_MAJOR rc=$CAL_RC wall_s=$CAL_WALL" | tee -a "$LEDGER"

# THE FROZEN PROJECTION RULE.  Formula frozen before compute; input MEASURED.
TMO_OPT=$(python3 -c "import math; t=float('$CAL_WALL') if float('$CAL_WALL')>0 else 300.0; print(int(min(3600, math.ceil(t*(1+$MAXIT_OPT)))))")
echo "TMO_OPT_PROJECTED=$TMO_OPT s (frozen rule: min(3600, ceil(t_cal * (1 + MAXIT_OPT))))" | tee -a "$LEDGER"

# ===========================================================================
# 2.  delta_repeat -- MEASURED BEFORE ANY FD STEP IS SIZED.
# ===========================================================================
stage_arm rep1
run_stage rep1 "$TMO_REP" "-task=run_model" "-out=d9_out.json"
stage_arm rep2
run_stage rep2 "$TMO_REP" "-task=run_model" "-out=d9_out.json"

# ===========================================================================
# 3.  THE BUY -- now with the meshQualityKS constraint.
# ===========================================================================
stage_arm opt
run_stage opt "$TMO_OPT" "-task=run_driver" "-optimizer=SLSQP" "-maxit=$MAXIT_OPT" "-out=d9_out.json"
OPT_RC=$?

# The endpoint design point.
DVFILE="$BASE/opt_dv.json"
if [ -f "$BASE/opt/d9_out.json" ]; then
  python3 -c "
import json
d=json.load(open('$BASE/opt/d9_out.json'))
dv=d.get('shapexUpper')
assert dv is not None and len(dv)>0, 'no shapexUpper in the driver record'
json.dump({'shapexUpper':dv}, open('$DVFILE','w'))
print('ENDPOINT_DV_WRITTEN n=%d l2=%.10e'%(len(dv), sum(v*v for v in dv)**0.5))
" 2>&1 | tee -a "$LEDGER"
else
  echo "ENDPOINT_DV_ABSENT: the driver left no record; the endpoint chain does not run" | tee -a "$LEDGER"
fi

# ===========================================================================
# 4.  THE G-MESH STAGE -- run_model at the endpoint, whose primal-startup checkMesh
#     block reports the RAW unperturbed maxNonOrth (D9's proven mechanism).
# ===========================================================================
MESHLOG=""
if [ -f "$DVFILE" ]; then
  stage_arm mesh
  cp "$DVFILE" "$BASE/mesh/opt_dv.json" || { echo "ABORT: cannot stage dv file for mesh"; exit 1; }
  chmod 666 "$BASE/mesh/opt_dv.json"
  run_stage mesh "$TMO_REP" "-task=run_model" "-dvFile=opt_dv.json" "-out=d9_out.json"
  MESHLOG="$BASE/mesh_${STAMP}.log"
  # report the raw maxNonOrth that G-MESH will grade (READ, not graded, here)
  python3 -c "
import re
v=None
for ln in open('$MESHLOG', errors='replace'):
    m=re.search(r'Mesh non-orthogonality Max:\s*([-+0-9.eE]+)', ln)
    if m: v=float(m.group(1))
print('G-MESH_RAW_MAXNONORTH_READ_FROM_LOG=%s (threshold 70.0)'%v)
" 2>&1 | tee -a "$LEDGER"
fi

# ===========================================================================
# 5.  THE ENDPOINT FD TABLE -- 3 registered USABLE steps, at the OPTIMISED point.
# ===========================================================================
if [ -f "$DVFILE" ]; then
  for h in $FD_STEPS; do
    tag="fd_$(echo "$h" | sed 's/\./p/; s/-/m/; s/+/p/')"
    stage_arm "$tag"
    cp "$DVFILE" "$BASE/$tag/opt_dv.json" || { echo "ABORT: cannot stage dv file for $tag"; exit 1; }
    chmod 666 "$BASE/$tag/opt_dv.json"
    run_stage "$tag" "$TMO_FD" "-task=check_totals" "-dvFile=opt_dv.json" "-fdStep=$h" "-out=d9_out.json"
  done

  # ===========================================================================
  # 6.  THE F-CEIL PROBE -- 1e-3, EXPECTED to invert the mesh. NOT a usable step.
  # ===========================================================================
  tag="fd_$(echo "$PROBE_STEP" | sed 's/\./p/; s/-/m/; s/+/p/')"
  stage_arm "$tag"
  cp "$DVFILE" "$BASE/$tag/opt_dv.json" || { echo "ABORT: cannot stage dv file for $tag"; exit 1; }
  chmod 666 "$BASE/$tag/opt_dv.json"
  run_stage "$tag" "$TMO_FD" "-task=check_totals" "-dvFile=opt_dv.json" "-fdStep=$PROBE_STEP" "-out=d9_out.json"
  echo "F-CEIL_PROBE stage=$tag step=$PROBE_STEP -- expected to AnalysisError (invert); its outcome is REPORTED, not a usable plateau step" | tee -a "$LEDGER"
fi

echo "TOTAL_SPENT_CORE_MIN=$SPENT_CORE_MIN CAP=$CAP_CORE_MIN" | tee -a "$LEDGER"
echo "STAMP=$STAMP" | tee -a "$LEDGER"
echo "TO GRADE: python3 $GRADER --root $BASE --cpuset $CPUSET --meshlog ${MESHLOG:-$BASE/mesh_${STAMP}.log}" | tee -a "$LEDGER"
