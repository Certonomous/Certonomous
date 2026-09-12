#!/usr/bin/env bash
# CURRICULUM MP_A5 -- A5 U-BEND, 3D INCOMPRESSIBLE MULTIPOINT PRESSURE-LOSS
# MINIMISATION OVER THREE INLET VELOCITIES.  Ladder A5.
#
# DERIVED FROM cases/dafoam/ladder-a/A5/curriculum_D9successor/d9succ_stage_and_run.sh.
# CHANGES FROM D9successor, and nowhere else:
#
#   MPA5-L1  **NO CAP OF ANY KIND.**  Sanaa's fourth NO-CAP ruling, 2026-09-12
#        (directive #17): no run is stopped by a time or budget cap, on any team.
#        REMOVED ENTIRELY: `REGISTERED_CAP_CORE_MIN` and its assertion, the
#        `CAP_CORE_MIN` pre-stage overrun check that returned 9, every `TMO_*`
#        variable, the `timeout` wrapper on `docker run`, and the frozen
#        projection rule that sized `TMO_OPT`.  Core-minutes are still MEASURED
#        and written to the ledger -- as a REPORTED figure that stops nothing.
#        **KEPT DELIBERATELY, and this is not a cap:** `--memory=3g
#        --memory-swap=3g --oom-score-adj=500`.  That is OOM containment on a
#        shared 16-core box with four sibling runs live; removing it would let
#        this item kill a peer's solver.
#
#   MPA5-L2  **THE RUN IS DETACHED AND SURVIVES THE FLEET DYING.**  The script
#        re-execs itself once under `setsid` with `MPA5_DETACHED=1`, reparents to
#        PPID 1, and the chain's rc is captured INSIDE the detached wrapper --
#        never around the `setsid` line, because `setsid <cmd>` returns 0 for
#        every outcome (lesson: "setsid parent returns zero").  The rc lands in
#        `$BASE/CHAIN_RC.txt` and in the ledger.
#
#   MPA5-L3  **THE P2 PRIMAL SETTING IS APPLIED HERE AND ASSERTED.**  A5P2
#        measured that `system/fvSolution` SIMPLE `nNonOrthogonalCorrectors 0->2`
#        takes the U-bend `p` initRes from 2.056815e-04 to 1.448577e-08 while
#        `TP1-TP2` moves 8.0e-08 RELATIVE.  The launcher rewrites that one token
#        in every staged arm and READS IT BACK; a staged arm whose fvSolution
#        does not carry `nNonOrthogonalCorrectors 2` in the SIMPLE block aborts
#        the chain rather than running the wrong primal.
#
#   MPA5-L4  **THE ARMS.**  Three, not nine:
#        1. `B`  run_model, shape=0, NO normFile  -> the three baseline dP_i, the
#                baseline raw checkMesh maxNonOrth, and the per-scenario primal
#                convergence that gate G-CONV grades.
#           -> the launcher then writes `norm.json` from B's own record.  The RULE
#              is frozen; the NUMBERS are measured.  No other source is admissible.
#        2. `O`  run_driver, all three scenarios, normalised composite objective.
#        3. `E`  run_model at the endpoint DV, all three scenarios, WITH normFile
#                -> the endpoint dP_i and the endpoint raw maxNonOrth (G-MESH).
#
# OPERATIONAL FACTS CARRIED IN FROM D9successor, not rediscovered:
#   * `-flag=value`.  argparse reads a bare `-maxit 30` as an OPTION FLAG. Use `=`.
#   * mpirun inside `--cpus=N` binds rank 0 to the FIRST CORE OF THE HOST
#     TOPOLOGY; every container is pinned with `--cpuset-cpus` AND the placement
#     is READ BACK from the process (`sched_affinity` in the record).
#   * no `--rm`, so `docker inspect` survives the container.
#   * `set -e` does not gate at the top level; every step carries its own explicit
#     `|| { echo ABORT...; exit 1; }`.
#   * THE PATCHED IMAGE IS THE ONE BOUGHT (dafoam-idwarp-rot:v1).
#
# SUBMISSIONS PARKED.
set -uo pipefail

IMG="${IMG:-dafoam-idwarp-rot:v1}"
BASE="${BASE:-}"
SRC="${SRC:-/home/ubuntu/certonomous-runs/W5-regrade/a5pl_stock}"
SELF="$(readlink -f "${BASH_SOURCE[0]}")"
CASEDIR="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_MP_A5"
RUNPY="${RUNPY:-$CASEDIR/mpa5_run_script.py}"
PREREG="$CASEDIR/PREREGISTRATION.md"
GRADER="$CASEDIR/mpa5_grade.py"

MAXIT_OPT=30          # SLSQP major-iteration limit.  An OPTIMISER CONVERGENCE
                      # SETTING, not a resource cap: it bounds how many majors
                      # SLSQP is willing to take, exactly as `ACC` bounds its
                      # tolerance.  Nothing here stops a running solver.

CPUSET="${CPUSET:-}"
[ -n "$CPUSET" ] || { echo "ABORT: CPUSET must be given explicitly; placement is registered, never defaulted"; exit 1; }
[ -n "$BASE" ]   || { echo "ABORT: BASE must be given explicitly (fresh timestamped run dir)"; exit 1; }

# ---------------------------------------------------------------------------
# MPA5-L2  DETACH ONCE.  rc is captured INSIDE the wrapper, never around setsid.
# ---------------------------------------------------------------------------
if [ "${MPA5_DETACHED:-0}" != "1" ]; then
  [ -e "$BASE" ] && { echo "ABORT: $BASE already exists; guards refuse a case whose run directory exists. Use a fresh timestamped dir; NEVER delete an interrupted tree."; exit 1; }
  mkdir -p "$BASE" || { echo "ABORT: cannot mkdir $BASE"; exit 1; }
  chmod 777 "$BASE"
  setsid bash -c "
    MPA5_DETACHED=1 IMG='$IMG' BASE='$BASE' SRC='$SRC' RUNPY='$RUNPY' CPUSET='$CPUSET' \
      bash '$SELF' > '$BASE/chain.out' 2>&1
    rc=\$?
    echo \"MPA5_CHAIN_RC: \$rc\" >> '$BASE/chain.out'
    printf '%s\n' \"\$rc\" > '$BASE/CHAIN_RC.txt'
    echo \"CHAIN_RC=\$rc\" >> '$BASE/ledger.txt'
  " < /dev/null > /dev/null 2>&1 &
  sleep 2
  echo "MPA5 DETACHED: base=$BASE cpuset=$CPUSET image=$IMG"
  echo "MPA5 CHAIN PGID: $(ps -o pgid= -C bash 2>/dev/null | tr -d ' ' | tail -1)"
  echo "MPA5 WATCH: tail -f $BASE/chain.out   |   LEDGER: $BASE/ledger.txt   |   RC: $BASE/CHAIN_RC.txt"
  exit 0
fi

# ===========================================================================
# From here down we are the DETACHED chain.
# ===========================================================================
SPENT_CORE_MIN=0
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
LEDGER="$BASE/ledger.txt"
echo "=== MP_A5 RUN $STAMP cpuset=$CPUSET image=$IMG NO-CAP (Sanaa 2026-09-12 directive 17) ===" | tee -a "$LEDGER"
echo "PPID=$PPID (1 == reparented, survives the fleet dying)" | tee -a "$LEDGER"

# the pre-registration must be on disk and must carry the NO-CAP literal, so an
# instrument that grew a cap back cannot run against this registration.
[ -f "$PREREG" ] || { echo "ABORT: pre-registration absent at $PREREG"; exit 1; }
grep -qF "NO CAP OF ANY KIND" "$PREREG" \
  || { echo "ABORT: the pre-registration does not carry the literal 'NO CAP OF ANY KIND'"; exit 1; }
grep -qF "timeout" "$SELF" && { echo "NOTE: the word 'timeout' appears in this file (comments only -- no timeout wrapper exists on any docker run)"; }
grep -qE '^\s*timeout ' "$SELF" && { echo "ABORT: an executable 'timeout' wrapper is present in this launcher; NO-CAP is violated"; exit 1; }
echo "NO-CAP ASSERTION PASSED: no executable timeout wrapper; memory containment RETAINED (--memory=3g --memory-swap=3g --oom-score-adj=500)" | tee -a "$LEDGER"

IMGID=$(sudo -n docker images --no-trunc --format '{{.ID}}' "$IMG" 2>/dev/null | head -1)
[ -n "$IMGID" ] || { echo "ABORT: cannot resolve image ID for $IMG"; exit 1; }
echo "IMAGE $IMG ID=$IMGID" | tee -a "$LEDGER"

# ---------------------------------------------------------------------------
# stage_arm <name> -- destroy and re-copy the arm tree, apply the P2 primal
# setting, PROVE COLD START.
# ---------------------------------------------------------------------------
stage_arm() {
  local name="$1"
  local arm="$BASE/$name"
  rm -rf "$arm" || { echo "ABORT: cannot clear $arm"; exit 1; }
  mkdir -p "$arm" || { echo "ABORT: cannot mkdir $arm"; exit 1; }
  cp -a "$SRC"/0 "$SRC"/0.orig "$SRC"/constant "$SRC"/system "$SRC"/FFD "$arm"/ 2>/dev/null \
    || { echo "ABORT: cannot stage case tree from $SRC"; exit 1; }
  cp "$RUNPY" "$arm"/runScript.py || { echo "ABORT: cannot stage run script"; exit 1; }

  # MPA5-L3  the P2 primal setting, APPLIED AND READ BACK.
  sed -i 's/^\(\s*nNonOrthogonalCorrectors\s*\)0;/\12;/' "$arm/system/fvSolution" \
    || { echo "ABORT: cannot apply the P2 setting in $name"; exit 1; }
  local nnoc
  nnoc=$(awk '/^SIMPLE/{f=1} f&&/nNonOrthogonalCorrectors/{print $2; exit}' "$arm/system/fvSolution" | tr -d ';')
  [ "$nnoc" = "2" ] || { echo "ABORT: P2 setting did not land in $name (SIMPLE nNonOrthogonalCorrectors reads '$nnoc', expected 2)"; exit 1; }
  echo "P2_APPLIED stage=$name SIMPLE/nNonOrthogonalCorrectors=$nnoc (A5P2 RESULTS.md: p initRes 2.056815e-04 -> 1.448577e-08)" | tee -a "$LEDGER"

  # COLD-START PROOF, before any container starts.
  [ -e "$arm/mpa5_out.json" ] && { echo "ABORT: answer file present before launch in $name"; exit 1; }
  for t in $(ls -1 "$arm" 2>/dev/null | grep -E '^[0-9]+(\.[0-9]+)?$' | grep -v '^0$'); do
    echo "ABORT: time directory $t present before launch in $name"; exit 1
  done
  [ -e "$arm/0/U.gz" ] && { echo "ABORT: 0/U.gz present before launch in $name"; exit 1; }
  [ -f "$arm/0/U" ] || { echo "ABORT: 0/U absent after staging $name"; exit 1; }
  chmod -R 777 "$arm"
  # the AGE DATUM: 0/U is touched last at staging and so dates the run allowed to
  # produce this arm's answer.  Every answer file must be NEWER than it.
  echo "COLDSTART_PROVED stage=$name answer-file absent, no time dir, no 0/U.gz, age_datum=$(stat -c %Y "$arm/0/U")" | tee -a "$LEDGER"
}

# ---------------------------------------------------------------------------
# run_stage <name> <extra args...>   -- NO TIMEOUT, NO CAP CHECK.
# ---------------------------------------------------------------------------
run_stage() {
  local name="$1"; shift
  local arm="$BASE/$name"
  local cname="mpa5_${name}_${STAMP}"
  local log="$BASE/${name}_${STAMP}.log"
  local t0 t1 wall rc

  t0=$(date +%s)
  sudo -n docker run --name "$cname" --user 0:0 \
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
  if [ -f "$arm/mpa5_out.json" ]; then
    aff=$(python3 -c "
import json
try:
    print(json.load(open('$arm/mpa5_out.json')).get('sched_affinity','NA'))
except Exception:
    print('NA')
")
  fi

  echo "STAGE=$name ARGS=$* rc=$rc wall_s=$wall ranks=1 core_min=$cm measured_affinity=$aff inspect(exit,oomkilled)=[$insp] log=$(basename "$log")" | tee -a "$LEDGER"
  echo "SPENT_CORE_MIN=$SPENT_CORE_MIN (REPORTED -- stops nothing, Sanaa 2026-09-12 directive 17)" | tee -a "$LEDGER"
  echo "$wall" > "$BASE/.wall_${name}"
  return $rc
}

# ===========================================================================
# ARM B -- the three baselines, at shape = 0, UNNORMALISED.
# ===========================================================================
stage_arm B
run_stage B "-task=run_model" "-out=mpa5_out.json"
B_RC=$?
echo "ARM_B rc=$B_RC" | tee -a "$LEDGER"

# ---- the normalisers.  RULE frozen; NUMBERS measured, from THIS chain's arm B.
NORMFILE="$BASE/norm.json"
if [ -f "$BASE/B/mpa5_out.json" ]; then
  python3 -c "
import json
d=json.load(open('$BASE/B/mpa5_out.json'))
dp=d.get('dP')
assert dp is not None and len(dp)==3, 'arm B left no three-scenario dP'
for v in dp:
    assert float(v) > 0.0, 'a baseline pressure loss must be strictly positive; got %r' % (dp,)
json.dump({'norms': [float(v) for v in dp], 'source': 'arm B of this chain, shape=0'}, open('$NORMFILE','w'), indent=2)
print('NORMALISERS_WRITTEN %r' % (dp,))
" 2>&1 | tee -a "$LEDGER"
else
  echo "NORMALISERS_ABSENT: arm B left no record; the chain does not proceed to O" | tee -a "$LEDGER"
fi

# ===========================================================================
# ARM O -- THE BUY.  Three scenarios, weighted normalised composite objective.
# ===========================================================================
if [ -f "$NORMFILE" ]; then
  stage_arm O
  cp "$NORMFILE" "$BASE/O/norm.json" || { echo "ABORT: cannot stage norm.json for O"; exit 1; }
  chmod 666 "$BASE/O/norm.json"
  run_stage O "-task=run_driver" "-optimizer=SLSQP" "-maxit=$MAXIT_OPT" "-normFile=norm.json" "-out=mpa5_out.json"
  O_RC=$?
  echo "ARM_O rc=$O_RC" | tee -a "$LEDGER"

  DVFILE="$BASE/opt_dv.json"
  if [ -f "$BASE/O/mpa5_out.json" ]; then
    python3 -c "
import json
d=json.load(open('$BASE/O/mpa5_out.json'))
dv=d.get('shapexUpper')
assert dv is not None and len(dv)>0, 'no shapexUpper in the driver record'
json.dump({'shapexUpper':dv}, open('$DVFILE','w'))
print('ENDPOINT_DV_WRITTEN n=%d l2=%.10e'%(len(dv), sum(v*v for v in dv)**0.5))
" 2>&1 | tee -a "$LEDGER"
  else
    echo "ENDPOINT_DV_ABSENT: the driver left no record; the endpoint arm does not run" | tee -a "$LEDGER"
  fi
fi

# ===========================================================================
# ARM E -- THE ENDPOINT.  Per-scenario dP at the optimum, and the raw checkMesh
# maxNonOrth that G-MESH grades (D9successor's proven mechanism).
# ===========================================================================
if [ -f "${DVFILE:-/nonexistent}" ]; then
  stage_arm E
  cp "$DVFILE"   "$BASE/E/opt_dv.json" || { echo "ABORT: cannot stage dv file for E"; exit 1; }
  cp "$NORMFILE" "$BASE/E/norm.json"   || { echo "ABORT: cannot stage norm.json for E"; exit 1; }
  chmod 666 "$BASE/E/opt_dv.json" "$BASE/E/norm.json"
  run_stage E "-task=run_model" "-dvFile=opt_dv.json" "-normFile=norm.json" "-out=mpa5_out.json"
  E_RC=$?
  echo "ARM_E rc=$E_RC" | tee -a "$LEDGER"
  python3 -c "
import re
v=None
for ln in open('$BASE/E_${STAMP}.log', errors='replace'):
    m=re.search(r'Mesh non-orthogonality Max:\s*([-+0-9.eE]+)', ln)
    if m: v=float(m.group(1))
print('G-MESH_RAW_MAXNONORTH_READ_FROM_LOG=%s (threshold 70.0)'%v)
" 2>&1 | tee -a "$LEDGER"
fi

echo "TOTAL_SPENT_CORE_MIN=$SPENT_CORE_MIN (REPORTED; no cap)" | tee -a "$LEDGER"
echo "STAMP=$STAMP" | tee -a "$LEDGER"
echo "TO GRADE: python3 $GRADER --root $BASE --stamp $STAMP --cpuset $CPUSET" | tee -a "$LEDGER"
