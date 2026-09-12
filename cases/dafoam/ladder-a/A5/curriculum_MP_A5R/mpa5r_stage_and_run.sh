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
#        re-execs itself once under `setsid` with `MPA5R_DETACHED=1`, reparents to
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
CASEDIR="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_MP_A5R"
RUNPY="${RUNPY:-$CASEDIR/mpa5r_run_script.py}"
PREREG="$CASEDIR/PREREGISTRATION.md"
GRADER="$CASEDIR/mpa5r_grade.py"

# MP_A5R-L1  the registered primal length.  ONE literal, asserted equal to the
# figure in the frozen pre-registration, and written into every staged tree.
REGISTERED_END_TIME=5000

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
if [ "${MPA5R_DETACHED:-0}" != "1" ]; then
  [ -e "$BASE" ] && { echo "ABORT: $BASE already exists; guards refuse a case whose run directory exists. Use a fresh timestamped dir; NEVER delete an interrupted tree."; exit 1; }
  mkdir -p "$BASE" || { echo "ABORT: cannot mkdir $BASE"; exit 1; }
  chmod 777 "$BASE"
  setsid bash -c "
    MPA5R_DETACHED=1 IMG='$IMG' BASE='$BASE' SRC='$SRC' RUNPY='$RUNPY' CPUSET='$CPUSET' \
      bash '$SELF' > '$BASE/chain.out' 2>&1
    rc=\$?
    echo \"MPA5R_CHAIN_RC: \$rc\" >> '$BASE/chain.out'
    printf '%s\n' \"\$rc\" > '$BASE/CHAIN_RC.txt'
    echo \"CHAIN_RC=\$rc\" >> '$BASE/ledger.txt'
  " < /dev/null > /dev/null 2>&1 &
  sleep 2
  echo "MPA5R DETACHED: base=$BASE cpuset=$CPUSET image=$IMG"
  echo "MPA5R CHAIN PGID: $(ps -o pgid= -C bash 2>/dev/null | tr -d ' ' | tail -1)"
  echo "MPA5R WATCH: tail -f $BASE/chain.out   |   LEDGER: $BASE/ledger.txt   |   RC: $BASE/CHAIN_RC.txt"
  exit 0
fi

# ===========================================================================
# From here down we are the DETACHED chain.
# ===========================================================================
SPENT_CORE_MIN=0
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
LEDGER="$BASE/ledger.txt"
echo "=== MP_A5R RUN $STAMP cpuset=$CPUSET image=$IMG NO-CAP (Sanaa 2026-09-12 directive 17) ===" | tee -a "$LEDGER"
echo "PPID=$PPID (1 == reparented, survives the fleet dying)" | tee -a "$LEDGER"

# the pre-registration must be on disk and must carry the NO-CAP literal, so an
# instrument that grew a cap back cannot run against this registration.
[ -f "$PREREG" ] || { echo "ABORT: pre-registration absent at $PREREG"; exit 1; }
grep -qF "NO CAP OF ANY KIND" "$PREREG" \
  || { echo "ABORT: the pre-registration does not carry the literal 'NO CAP OF ANY KIND'"; exit 1; }
# MP_A5R-L1  the launcher's primal length must be the registered one, and the
# grader must be grading the same number.  Three places, asserted equal, because
# the predecessor's whole failure was two of them disagreeing unseen.
grep -qF "REGISTERED endTime: ${REGISTERED_END_TIME}" "$PREREG" \
  || { echo "ABORT: the pre-registration does not carry the literal 'REGISTERED endTime: ${REGISTERED_END_TIME}'"; exit 1; }
grep -qE "^REGISTERED_END_TIME = ${REGISTERED_END_TIME}$" "$GRADER" \
  || { echo "ABORT: the grader's REGISTERED_END_TIME does not read ${REGISTERED_END_TIME}"; exit 1; }
echo "ENDTIME_TRIPLE_ASSERTION PASSED: launcher=$REGISTERED_END_TIME, pre-registration literal present, grader constant matches" | tee -a "$LEDGER"
grep -qF "timeout" "$SELF" && { echo "NOTE: the word 'timeout' appears in this file (comments only -- no timeout wrapper exists on any docker run)"; }
grep -qE '^\s*timeout ' "$SELF" && { echo "ABORT: an executable 'timeout' wrapper is present in this launcher; NO-CAP is violated"; exit 1; }
echo "NO-CAP ASSERTION PASSED: no executable timeout wrapper; memory containment RETAINED (--memory=3g --memory-swap=3g --oom-score-adj=500)" | tee -a "$LEDGER"

IMGID=$(sudo -n docker images --no-trunc --format '{{.ID}}' "$IMG" 2>/dev/null | head -1)
[ -n "$IMGID" ] || { echo "ABORT: cannot resolve image ID for $IMG"; exit 1; }
echo "IMAGE $IMG ID=$IMGID" | tee -a "$LEDGER"

# MPA5-L5  ADDENDUM 1 -- the per-scenario directory names are READ OUT OF THE RUN
# SCRIPT'S OWN `RUN_DIRS`, never spelled here.  A name written twice is a name
# that can drift; SO3 asserts the same invariant with so3_collision_leg.py.
RUN_DIR_NAMES=$(python3 -c "
import re, sys
src = open('$RUNPY').read()
m = re.search(r'^SCENARIOS\s*=\s*(\[[^\]]*\])', src, re.M)
assert m, 'cannot find SCENARIOS in the run script'
scen = eval(m.group(1))
m2 = re.search(r'^RUN_DIRS\s*=\s*(\{[^}]*\})', src, re.M)
assert m2, 'cannot find RUN_DIRS in the run script'
rd = eval(m2.group(1), {'SCENARIOS': scen, 'enumerate': enumerate})
assert set(rd) == set(scen), 'RUN_DIRS is not total over SCENARIOS'
assert len(set(rd.values())) == len(scen), 'RUN_DIRS is not injective'
print(' '.join(rd[s] for s in scen))
") || { echo "ABORT: cannot derive RUN_DIRS from $RUNPY"; exit 1; }
[ -n "$RUN_DIR_NAMES" ] || { echo "ABORT: RUN_DIRS derived empty"; exit 1; }
echo "RUN_DIRS_DERIVED_FROM_RUNSCRIPT=[$RUN_DIR_NAMES] (per-scenario isolation, addendum 1)" | tee -a "$LEDGER"

# ---------------------------------------------------------------------------
# MPA5-L6  ADDENDUM 1 -- THE TIME-DIRECTORY PREDICATE, AND A CONTROL THAT PROVES
# IT CAN REFUSE.  A guard never shown able to fail is not evidence, exactly as a
# zero from a reader never shown able to see a non-zero is not evidence
# (CLAUDE.md rule 3).  `stale_time_dirs` names every DECIMAL-named time directory
# (`0.0001`, `1000`) other than the `0` template; `0.orig` is an input and is not
# a time directory.  The control below plants a `0.0001` and requires the
# predicate to NAME it, and plants a clean tree and requires silence.
# ---------------------------------------------------------------------------
stale_time_dirs() {
  local d="$1"
  ls -1 "$d" 2>/dev/null | while read -r e; do
    [ -d "$d/$e" ] || continue
    case "$e" in 0) continue ;; esac
    printf '%s\n' "$e" | grep -qE '^[0-9]+(\.[0-9]+)?$' && printf '%s ' "$e"
  done
}

prove_time_dir_guard() {
  local t
  t=$(mktemp -d) || { echo "ABORT: cannot make a scratch dir for the guard control"; exit 1; }
  mkdir -p "$t/clean/0" "$t/clean/0.orig" "$t/clean/constant"
  local neg
  neg=$(stale_time_dirs "$t/clean")
  [ -z "$neg" ] || { echo "ABORT: GUARD CONTROL NEGATIVE LEG FAILED -- a clean tree was reported stale: [$neg]"; rm -rf "$t"; exit 1; }
  mkdir -p "$t/dirty/0" "$t/dirty/0.orig" "$t/dirty/0.0001" "$t/dirty/1000"
  local pos
  pos=$(stale_time_dirs "$t/dirty")
  case "$pos" in
    *0.0001*) : ;;
    *) echo "ABORT: GUARD CONTROL POSITIVE LEG FAILED -- a planted 0.0001 was NOT seen; the predicate read [$pos]"; rm -rf "$t"; exit 1 ;;
  esac
  case "$pos" in
    *1000*) : ;;
    *) echo "ABORT: GUARD CONTROL POSITIVE LEG FAILED -- a planted 1000 was NOT seen; the predicate read [$pos]"; rm -rf "$t"; exit 1 ;;
  esac
  rm -rf "$t"
  echo "GUARD_CONTROL_PASSED: planted 0.0001 and 1000 were both NAMED [$pos]; a clean tree read silent. The cold-start guard is shown able to refuse." | tee -a "$LEDGER"
}

# ---------------------------------------------------------------------------
# stage_arm <name> -- destroy and re-copy the arm tree AND the three
# per-scenario case copies, apply the P2 primal setting, PROVE COLD START.
# ---------------------------------------------------------------------------
stage_arm() {
  local name="$1"
  local arm="$BASE/$name"
  rm -rf "$arm" || { echo "ABORT: cannot clear $arm"; exit 1; }
  mkdir -p "$arm" || { echo "ABORT: cannot mkdir $arm"; exit 1; }
  cp -a "$SRC"/0 "$SRC"/0.orig "$SRC"/constant "$SRC"/system "$SRC"/FFD "$arm"/ 2>/dev/null \
    || { echo "ABORT: cannot stage case tree from $SRC"; exit 1; }
  cp "$RUNPY" "$arm"/runScript.py || { echo "ABORT: cannot stage run script"; exit 1; }

  # MPA5-L5  ADDENDUM 1 -- THE PER-SCENARIO CASE COPIES.  One full case tree per
  # operating point at mp0/ mp1/ mp2/, so no two DASolvers and no two IDWarp
  # instances address the same directory.  The names MUST equal the values of
  # `RUN_DIRS` in mpa5r_run_script.py, and that equality is ASSERTED below against
  # the run script's own text rather than trusted.
  for mp in $RUN_DIR_NAMES; do
    cp -a "$SRC"/0 "$SRC"/0.orig "$SRC"/constant "$SRC"/system "$SRC"/FFD "$arm/$mp"/ 2>/dev/null \
      || { mkdir -p "$arm/$mp" && cp -a "$SRC"/0 "$SRC"/0.orig "$SRC"/constant "$SRC"/system "$SRC"/FFD "$arm/$mp"/ ; } \
      || { echo "ABORT: cannot stage per-scenario case copy $mp in $name"; exit 1; }
  done

  # MPA5-L3  the P2 primal setting, APPLIED AND READ BACK -- in the arm root AND
  # in every per-scenario copy, because each DASolver reads its OWN system/.
  for d in "$arm" $(for mp in $RUN_DIR_NAMES; do echo "$arm/$mp"; done); do
    sed -i 's/^\(\s*nNonOrthogonalCorrectors\s*\)0;/\12;/' "$d/system/fvSolution" \
      || { echo "ABORT: cannot apply the P2 setting in $d"; exit 1; }
    local nnoc
    nnoc=$(awk '/^SIMPLE/{f=1} f&&/nNonOrthogonalCorrectors/{print $2; exit}' "$d/system/fvSolution" | tr -d ';')
    [ "$nnoc" = "2" ] || { echo "ABORT: P2 setting did not land in $d (SIMPLE nNonOrthogonalCorrectors reads '$nnoc', expected 2)"; exit 1; }
  done
  echo "P2_APPLIED stage=$name in the arm root and in $RUN_DIR_NAMES, SIMPLE/nNonOrthogonalCorrectors=2 (A5P2 RESULTS.md: p initRes 2.056815e-04 -> 1.448577e-08)" | tee -a "$LEDGER"

  # MP_A5R-L1  THE PRIMAL LENGTH, APPLIED AND READ BACK -- the whole reason this
  # successor exists.  MP_A5's floor was calibrated on A5P2's `endTime 5000` tree
  # and applied to a tree that stages `endTime 1000`; nothing could see the
  # mismatch and its arm B graded GATE FAIL for it.  Here the length is written
  # into every staged controlDict and READ BACK, and the grader's G-ENDTIME reads
  # what the primal ACTUALLY reached, so the floor and its tree cannot drift.
  for d in "$arm" $(for mp in $RUN_DIR_NAMES; do echo "$arm/$mp"; done); do
    sed -i "s/^\(endTime[[:space:]]\+\)[0-9.]\+;/\1${REGISTERED_END_TIME};/" "$d/system/controlDict" \
      || { echo "ABORT: cannot set endTime in $d"; exit 1; }
    local et
    et=$(awk '/^endTime/{print $2; exit}' "$d/system/controlDict" | tr -d ';')
    [ "$et" = "$REGISTERED_END_TIME" ] \
      || { echo "ABORT: endTime did not land in $d (reads '$et', expected $REGISTERED_END_TIME)"; exit 1; }
    # the write interval must still land ON the endpoint, or no fields are written there
    sed -i "s/^\(writeInterval[[:space:]]\+\)[0-9.]\+;/\1${REGISTERED_END_TIME};/" "$d/system/controlDict" \
      || { echo "ABORT: cannot set writeInterval in $d"; exit 1; }
    local wi
    wi=$(awk '/^writeInterval/{print $2; exit}' "$d/system/controlDict" | tr -d ';')
    [ "$wi" = "$REGISTERED_END_TIME" ] \
      || { echo "ABORT: writeInterval did not land in $d (reads '$wi'); a non-endpoint interval writes no fields at endTime"; exit 1; }
  done
  echo "ENDTIME_APPLIED stage=$name endTime=$REGISTERED_END_TIME writeInterval=$REGISTERED_END_TIME in the arm root and in $RUN_DIR_NAMES (MP_A5 staged 1000 against a floor measured at 5000)" | tee -a "$LEDGER"

  # COLD-START PROOF, before any container starts.  Checked in the arm root AND
  # in every per-scenario copy.
  [ -e "$arm/mpa5r_out.json" ] && { echo "ABORT: answer file present before launch in $name"; exit 1; }
  for d in "$arm" $(for mp in $RUN_DIR_NAMES; do echo "$arm/$mp"; done); do
    local stale
    stale=$(stale_time_dirs "$d")
    [ -z "$stale" ] || { echo "ABORT: time directory/ies [$stale] present before launch in $d"; exit 1; }
    [ -e "$d/0/U.gz" ] && { echo "ABORT: 0/U.gz present before launch in $d"; exit 1; }
    [ -f "$d/0/U" ]   || { echo "ABORT: 0/U absent after staging $d"; exit 1; }
  done
  chmod -R 777 "$arm"
  # the AGE DATUM: 0/U is touched last at staging and so dates the run allowed to
  # produce this arm's answer.  Every answer file must be NEWER than it.
  echo "COLDSTART_PROVED stage=$name answer-file absent, no time dir in the arm root or in any of [$RUN_DIR_NAMES], no 0/U.gz, age_datum=$(stat -c %Y "$arm/0/U")" | tee -a "$LEDGER"
}

# ---------------------------------------------------------------------------
# run_stage <name> <extra args...>   -- NO TIMEOUT, NO CAP CHECK.
# ---------------------------------------------------------------------------
run_stage() {
  local name="$1"; shift
  local arm="$BASE/$name"
  local cname="mpa5r_${name}_${STAMP}"
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
  if [ -f "$arm/mpa5r_out.json" ]; then
    aff=$(python3 -c "
import json
try:
    print(json.load(open('$arm/mpa5r_out.json')).get('sched_affinity','NA'))
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
# MPA5-L6  ADDENDUM 1a -- PROVE THE COLD-START GUARD CAN REFUSE, BEFORE ANY ARM
# IS STAGED.  The call sits HERE, below the function definitions, because on the
# first relaunch it sat ABOVE them and bash reported
# `prove_time_dir_guard: command not found` -- the control SILENTLY DID NOT RUN
# and the chain proceeded anyway.  A control that can quietly not run is not a
# control, so the two lines below make a missing function FATAL: the guard of the
# guard.
# ===========================================================================
declare -F prove_time_dir_guard >/dev/null \
  || { echo "ABORT: prove_time_dir_guard is not defined at its call site; the cold-start control cannot run and the chain must not proceed without it"; exit 1; }
declare -F stale_time_dirs >/dev/null \
  || { echo "ABORT: stale_time_dirs is not defined at its call site"; exit 1; }
prove_time_dir_guard

# ===========================================================================
# ARM B -- the three baselines, at shape = 0, UNNORMALISED.
# ===========================================================================
stage_arm B
run_stage B "-task=run_model" "-out=mpa5r_out.json"
B_RC=$?
echo "ARM_B rc=$B_RC" | tee -a "$LEDGER"

# ---- the normalisers.  RULE frozen; NUMBERS measured, from THIS chain's arm B.
NORMFILE="$BASE/norm.json"
if [ -f "$BASE/B/mpa5r_out.json" ]; then
  python3 -c "
import json
d=json.load(open('$BASE/B/mpa5r_out.json'))
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
  run_stage O "-task=run_driver" "-optimizer=SLSQP" "-maxit=$MAXIT_OPT" "-normFile=norm.json" "-out=mpa5r_out.json"
  O_RC=$?
  echo "ARM_O rc=$O_RC" | tee -a "$LEDGER"

  DVFILE="$BASE/opt_dv.json"
  if [ -f "$BASE/O/mpa5r_out.json" ]; then
    python3 -c "
import json
d=json.load(open('$BASE/O/mpa5r_out.json'))
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
  run_stage E "-task=run_model" "-dvFile=opt_dv.json" "-normFile=norm.json" "-out=mpa5r_out.json"
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

# ---------------------------------------------------------------------------
# MPA5-L7  ADDENDUM 1 -- THE CHAIN'S rc REFLECTS ITS ARMS.
#
# THE DEFECT THIS REPAIRS, MEASURED ON THIS ITEM'S OWN FIRST LAUNCH: arm B exited
# rc=1, the chain correctly refused to proceed to O (`NORMALISERS_ABSENT`), and
# then the chain exited 0 and wrote `MPA5R_CHAIN_RC: 0`.  Anything keying on
# CHAIN_RC.txt would have read SUCCESS on a failed chain.  A wrapper that reports
# success for a failed run is worse than one that reports nothing.
#
# rc is the FIRST non-zero arm rc, or 0 only if EVERY declared arm ran and every
# one returned 0.  An arm that never ran (because a predecessor failed) makes the
# chain non-zero -- an unrun arm is not a passed arm.  Exit status is still NOT
# the verdict; the verdict is the comparator's.
# ---------------------------------------------------------------------------
CHAIN_RC=0
for a in B O E; do
  v=$(eval "echo \${${a}_RC:-MISSING}")
  echo "ARM_RC_ROLLUP arm=$a rc=$v" | tee -a "$LEDGER"
  if [ "$v" = "MISSING" ]; then
    [ "$CHAIN_RC" = "0" ] && CHAIN_RC=70   # 70 == a declared arm never ran
  elif [ "$v" != "0" ]; then
    [ "$CHAIN_RC" = "0" ] && CHAIN_RC=$v
  fi
done
echo "CHAIN_RC_ROLLUP=$CHAIN_RC (0 only if all of B,O,E ran and all returned 0; 70 == a declared arm never ran)" | tee -a "$LEDGER"
exit "$CHAIN_RC"
