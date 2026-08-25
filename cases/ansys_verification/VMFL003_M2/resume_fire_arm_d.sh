#!/bin/bash
# ===========================================================================
# VMFL003-M2 -- RESUME LAUNCHER, ARM D (kOmegaSST) ONLY.
#
# NOT FILED ANYWHERE.  Nothing this script produces leaves this box.
#
# WHY THIS FILE EXISTS, AND WHAT IT IS NOT.
# The frozen slate launcher run_vmfl003_m2.sh (HEAD blob
# 29a53e035a1bb595d7dde69b0e2e6b77bcd561b4) carries GUARD 3: it refuses to
# start if ANY arm/level directory already exists.  Arms A and B are complete
# on disk and arm C is partly on disk, so the frozen launcher can never be
# re-run.  It is FROZEN and is therefore NOT EDITED (CLAUDE.md rule 6).  This
# is a SEPARATE, NEW file that fires the ONE registered arm that has never had
# a directory at all: D_kOmegaSST.
#
# IT CHANGES NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.
#   * the level set, nx, nr and endTimes are the frozen launcher's, verbatim;
#   * build_case() and mesh_case() are not re-typed -- they are EXTRACTED FROM
#     THE HEAD BLOB of the frozen launcher (lines 111-169), sha256-asserted,
#     and eval'd, so the case materialisation is provably the frozen code;
#   * the caps are the frozen CAP_CORE_MIN=160 / PER_ARM_CAP=40, and the
#     running total is SEEDED FROM DISK by summing the core_min recorded in
#     every RUN_RC.txt already written -- spent is spent;
#   * timeout_s = remaining_core_min * 60 / RANKS, the frozen formula.
#
# TWO DELIBERATE DEPARTURES, BOTH STATED, NEITHER TOUCHING THE DATA:
#   1. IT DOES NOT GRADE.  The frozen launcher calls the comparator at the end
#      of an arm; this one does not.  Grading is a separate lane's job and the
#      supervisor's to rule on.  The frozen comparator can be run against this
#      arm root at any later time with no loss -- omitting it changes nothing
#      about what is written to disk.
#   2. IT FIRES ONE ARM.  A, B and C are not touched, not re-run, not read for
#      anything but their recorded cost.
#
# `set -e` IS NOT RELIED ON: measured not to gate in this lab's agent
# execution context, and `( set -e; ... )` silently fails too.  EVERY check
# below gates with an explicit `|| { echo ABORT...; exit 1; }`.
# ===========================================================================

RANKS=1
CAP_CORE_MIN=160
PER_ARM_CAP=40
ARM="D_kOmegaSST"
OVL="D_kOmegaSST"
OLD_LAUNCHER_PID=2218904
FUNCS_SHA="3fee43cb254c47d2c6bf6a11817556a1958134686b42629ef2a0228e0658d43e"

CASEDIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$CASEDIR/../../.." && pwd)"
RUNROOT="$REPO/verification/runs/ansys_verification/VMFL003_M2"
ARM_ROOT="$RUNROOT/$ARM"
PREREG="cases/ansys_verification/VMFL003_M2/PREREGISTRATION.md"
REC="$RUNROOT/_resume_fire"

# level      nx     nr   endTime      (verbatim from the frozen launcher)
LEVELS=(
  "L1_250x5    250   5   15000"
  "L2_500x5    500   5   18000"
  "L3_1000x5  1000   5   22000"
  "D_500x3     500   3   18000"
  "D_500x4     500   4   18000"
  "D_500x6     500   6   18000"
)

mkdir -p "$REC" || { echo "ABORT: cannot create $REC"; exit 1; }
LOG="$REC/resume_fire_arm_d.log"
exec >>"$LOG" 2>&1
echo "=== VMFL003-M2 resume launcher, ARM $ARM -- $(date -u +%Y-%m-%dT%H:%M:%SZ) pid=$$"

# --- GUARD 0: the frozen slate launcher must be GONE ------------------------
# It is orphaned to init and INVISIBLE to a naive process check (L-41).  It
# owns this run tree while it lives; building a directory it is about to build
# would put two solvers in one case.  ps -eo, never pgrep -f (self-match, 3x today).
while ps -o pid= -p "$OLD_LAUNCHER_PID" >/dev/null 2>&1; do
  echo "  waiting: frozen slate launcher pid $OLD_LAUNCHER_PID still alive at $(date -u +%H:%M:%SZ)"
  sleep 30
done
echo "  GUARD 0 OK: frozen slate launcher pid $OLD_LAUNCHER_PID has exited"
ps -eo pid,args | grep -E '[s]impleFoam' | grep -v grep
echo "  (no simpleFoam line above = none live)"

# --- GUARD 1: the pre-registration must be COMMITTED and byte-identical -----
git -C "$REPO" cat-file -e "HEAD:$PREREG" 2>/dev/null \
  || { echo "ABORT: $PREREG not committed at HEAD"; exit 1; }
DISK_SHA=$(git -C "$REPO" hash-object "$REPO/$PREREG") || { echo "ABORT: cannot hash prereg"; exit 1; }
HEAD_SHA=$(git -C "$REPO" rev-parse "HEAD:$PREREG")     || { echo "ABORT: cannot resolve HEAD prereg"; exit 1; }
[ "$DISK_SHA" = "$HEAD_SHA" ] || { echo "ABORT: prereg disk $DISK_SHA != HEAD $HEAD_SHA"; exit 1; }
[ "$HEAD_SHA" = "cdbf2659b6eec2599fc3eda7a149aaca391461b0" ] \
  || { echo "ABORT: prereg HEAD blob $HEAD_SHA is not the supervisor-verified freeze"; exit 1; }
echo "  GUARD 1 OK: prereg == HEAD == $HEAD_SHA"

# --- GUARD 2: BOTH comparators must be the frozen files --------------------
for pair in "grade_vmfl003_m2.py 6dcc99940154ea204a598ba2118042bf972a786d" \
            "grade_vmfl003_m2_omega.py b595c86a4b8580d5928b4d4dd1458698f6de8ac2"; do
  set -- $pair
  H=$(git -C "$REPO" rev-parse "HEAD:cases/ansys_verification/VMFL003_M2/$1") \
    || { echo "ABORT: cannot resolve HEAD blob for $1"; exit 1; }
  D=$(git -C "$REPO" hash-object "$CASEDIR/$1") || { echo "ABORT: cannot hash $1"; exit 1; }
  [ "$H" = "$2" ] || { echo "ABORT: $1 HEAD blob $H != verified $2"; exit 1; }
  [ "$D" = "$H" ] || { echo "ABORT: $1 on disk $D != HEAD $H"; exit 1; }
  python3 "$CASEDIR/$1" --verify-frozen HEAD || { echo "ABORT: $1 self-check refused"; exit 1; }
  echo "  GUARD 2 OK: $1 == HEAD == $H"
done

# --- GUARD 2b: the frozen launcher's case-building code, verbatim ----------
FUNCS=$(git -C "$REPO" show "HEAD:cases/ansys_verification/VMFL003_M2/run_vmfl003_m2.sh" | sed -n '111,169p') \
  || { echo "ABORT: cannot extract build_case/mesh_case from the frozen launcher"; exit 1; }
GOT=$(printf '%s\n' "$FUNCS" | sha256sum | cut -d' ' -f1)
[ "$GOT" = "$FUNCS_SHA" ] || { echo "ABORT: frozen build/mesh extract sha $GOT != $FUNCS_SHA"; exit 1; }
eval "$FUNCS" || { echo "ABORT: cannot eval the frozen build/mesh functions"; exit 1; }
declare -F build_case >/dev/null || { echo "ABORT: build_case not defined"; exit 1; }
declare -F mesh_case  >/dev/null || { echo "ABORT: mesh_case not defined"; exit 1; }
echo "  GUARD 2b OK: build_case/mesh_case are the frozen code (sha256 $GOT)"

# --- GUARD 3: refuse to start into ANY pre-existing arm-D level directory ---
for lspec in "${LEVELS[@]}"; do
  set -- $lspec
  [ -e "$ARM_ROOT/$1" ] \
    && { echo "ABORT: $ARM_ROOT/$1 already exists -- rule 4's guard refuses a case "\
"where 0/ or a time directory already exists.  A repeat is a NEW RUNG, never a "\
"re-grade in place."; exit 1; }
done
echo "  GUARD 3 OK: no pre-existing $ARM level directory"

# --- GUARD 4: seed the RUNNING TOTAL from disk -- spent is spent ------------
SPENT_CORE_MIN=$(python3 - "$RUNROOT" <<'PYSEED'
import sys,os,re
root=sys.argv[1]; tot=0.0; n=0
for a in sorted(os.listdir(root)):
    ap=os.path.join(root,a)
    if not os.path.isdir(ap): continue
    for l in sorted(os.listdir(ap)):
        f=os.path.join(ap,l,"RUN_RC.txt")
        if os.path.exists(f):
            m=re.search(r'^core_min=([\d.]+)',open(f).read(),re.M)
            if m: tot+=float(m.group(1)); n+=1
sys.stderr.write("  seeded from %d RUN_RC.txt files\n"%n)
print("%.6f"%tot)
PYSEED
) || { echo "ABORT: cannot seed the running total from disk"; exit 1; }
python3 -c "import sys; sys.exit(0 if 0.0 < $SPENT_CORE_MIN < $CAP_CORE_MIN else 1)" \
  || { echo "ABORT: seeded spend $SPENT_CORE_MIN core-min is not in (0,$CAP_CORE_MIN) -- "\
"the slate cap is already exhausted or the seed is wrong.  An overrun STOPS the run; "\
"it does not get a new budget (CLAUDE.md rule 12)."; exit 1; }
ARM_SPENT=0
echo "  GUARD 4 OK: slate spent = $SPENT_CORE_MIN of $CAP_CORE_MIN core-min; arm $ARM spent = 0 of $PER_ARM_CAP"

# --- OpenFOAM environment --------------------------------------------------
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1 \
  || { echo "ABORT: cannot source the OpenFOAM v2606 environment"; exit 1; }
command -v simpleFoam >/dev/null || { echo "ABORT: simpleFoam not on PATH"; exit 1; }

# --- LOAD SAMPLER: what else was on the machine, THROUGHOUT the run --------
# A calibration row that does not say what else was running is not a calibration.
( while true; do
    printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(cut -d' ' -f1-3 /proc/loadavg)" \
      "$(ps -eo pcpu,comm --sort=-pcpu | awk 'NR>1 && $1>20 {printf "%s(%s%%) ",$2,$1}')"
    sleep 30
  done ) > "$REC/loadavg_arm_d.tsv" 2>/dev/null &
SAMPLER=$!
echo "  load sampler pid $SAMPLER -> $REC/loadavg_arm_d.tsv"

# --- PRE-FLIGHT SMOKE, ARM D, ONE ITERATION, OUTSIDE verification/runs -----
SMOKE=$(mktemp -d "${TMPDIR:-/tmp}/vmfl003m2-resumeD-XXXXXX") \
  || { echo "ABORT: cannot create the smoke scratch dir"; kill $SAMPLER 2>/dev/null; exit 1; }
build_case "$SMOKE/$ARM" "$OVL" 250 5 1 \
  || { echo "ABORT: smoke ($ARM) could not materialise the case"; rm -rf "$SMOKE"; kill $SAMPLER 2>/dev/null; exit 1; }
mesh_case "$SMOKE/$ARM" "resume-smoke-$ARM" \
  || { echo "ABORT: smoke ($ARM) FAILED at blockMesh/checkMesh/topoSet/cert"; kill $SAMPLER 2>/dev/null; exit 1; }
( cd "$SMOKE/$ARM" && timeout 300 simpleFoam > log.simpleFoam 2>&1 ) \
  || { echo "ABORT: smoke ($ARM) FAILED on its first timestep -- NO level is launched"; kill $SAMPLER 2>/dev/null; exit 1; }
grep -qE "^End$" "$SMOKE/$ARM/log.simpleFoam" \
  || { echo "ABORT: smoke ($ARM) produced no End line"; kill $SAMPLER 2>/dev/null; exit 1; }
echo "  smoke ($ARM) PASSED (1 iteration, coarsest mesh)"
rm -rf "$SMOKE"

# ===========================================================================
# THE REAL LEVELS -- ARM D, SIX MESHES, IN THE FROZEN ORDER.  GRADED COMPUTE.
# The order is the frozen launcher's and is NOT reordered: reordering to
# protect the gate level would be an outcome-affecting choice this lane has no
# standing to make.
# ===========================================================================
mkdir -p "$ARM_ROOT" || { echo "ABORT: cannot create $ARM_ROOT"; kill $SAMPLER 2>/dev/null; exit 1; }
TOTAL_WALL=0
echo "=== ARM $ARM  (overlay $OVL, graded later by grade_vmfl003_m2_omega.py) ==="

for lspec in "${LEVELS[@]}"; do
  set -- $lspec
  LEVEL="$1"; NX="$2"; NR="$3"; ENDT="$4"
  DEST="$ARM_ROOT/$LEVEL"

  REMAIN=$(python3 -c "print(max(0.0, min($CAP_CORE_MIN - $SPENT_CORE_MIN, $PER_ARM_CAP - $ARM_SPENT)))") \
    || { echo "ABORT: cannot compute the remaining budget"; break; }
  TIMEOUT_S=$(python3 -c "print(int($REMAIN * 60 / $RANKS))") \
    || { echo "ABORT: cannot compute the timeout"; break; }
  [ "$TIMEOUT_S" -gt 0 ] \
    || { echo "ABORT: BUDGET EXHAUSTED before $ARM/$LEVEL (slate $SPENT_CORE_MIN of "\
"$CAP_CORE_MIN, arm $ARM_SPENT of $PER_ARM_CAP core-min).  An overrun STOPS the run; "\
"it does not get a new budget (CLAUDE.md rule 12)."; break; }

  echo "--- $ARM/$LEVEL  nx=$NX nr=$NR endTime=$ENDT  timeout=${TIMEOUT_S}s (remaining ${REMAIN} core-min)  $(date -u +%H:%M:%SZ)"

  build_case "$DEST" "$OVL" "$NX" "$NR" "$ENDT" || { echo "ABORT: could not build $ARM/$LEVEL"; break; }
  mesh_case  "$DEST" "$ARM/$LEVEL" || { echo "ABORT: $ARM/$LEVEL FAILED at meshing/cert or an EMPTY sampling zone"; break; }

  # AGE-GUARD DATUM (comparator clause C6): touch every file in this level's
  # own 0/ as the LAST action before the solver starts.
  find "$DEST/0" -type f -exec touch {} + \
    || { echo "ABORT: could not set the age-guard datum for $ARM/$LEVEL"; break; }
  sleep 1

  T0=$(date +%s)
  ( cd "$DEST" && timeout "$TIMEOUT_S" simpleFoam > log.simpleFoam 2>&1 )
  RC=$?
  T1=$(date +%s)
  WALL=$((T1 - T0))
  CORE_MIN=$(python3 -c "print($WALL * $RANKS / 60.0)")
  SPENT_CORE_MIN=$(python3 -c "print($SPENT_CORE_MIN + $CORE_MIN)")
  ARM_SPENT=$(python3 -c "print($ARM_SPENT + $CORE_MIN)")
  TOTAL_WALL=$((TOTAL_WALL + WALL))

  printf 'rc=%d\narm=%s\nlevel=%s\nnx=%s\nnr=%s\nendTime=%s\nwall_s=%d\nranks=%d\ncore_min=%s\ntimeout_s=%d\nlaunched_by=resume_fire_arm_d.sh\n' \
    "$RC" "$ARM" "$LEVEL" "$NX" "$NR" "$ENDT" "$WALL" "$RANKS" "$CORE_MIN" "$TIMEOUT_S" \
    > "$DEST/RUN_RC.txt" || { echo "ABORT: could not write RUN_RC.txt for $ARM/$LEVEL"; break; }

  [ "$RC" -eq 0 ] \
    || { echo "ABORT: $ARM/$LEVEL exited rc=$RC after ${WALL}s (timeout ${TIMEOUT_S}s).  "\
"A non-zero rc is a FINDING, not a retry: it is triaged before anything else runs.  "\
"rc=124 means the BUDGET TIMEOUT fired -- that is a budget stop, and rule 12 gives it "\
"no new budget."; break; }
  echo "    $ARM/$LEVEL done: ${WALL}s = ${CORE_MIN} core-min (arm ${ARM_SPENT}/${PER_ARM_CAP}, slate ${SPENT_CORE_MIN}/${CAP_CORE_MIN})"
done

kill $SAMPLER 2>/dev/null
printf 'arm=%s\ntotal_wall_s=%d\nranks=%d\narm_core_min=%s\nslate_core_min_after=%s\ncap_core_min=%s\nper_arm_cap=%s\nfinished_utc=%s\ncost_basis=owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md section 5)\n' \
  "$ARM" "$TOTAL_WALL" "$RANKS" "$ARM_SPENT" "$SPENT_CORE_MIN" "$CAP_CORE_MIN" "$PER_ARM_CAP" \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$REC/COST_ARM_D.txt"
echo "ARM $ARM FINISHED: ${TOTAL_WALL}s wall = ${ARM_SPENT} core-min of a ${PER_ARM_CAP} core-min arm cap; slate now ${SPENT_CORE_MIN}/${CAP_CORE_MIN}."
echo "NOT GRADED BY THIS SCRIPT -- grading is a separate lane's job and the supervisor's ruling."
