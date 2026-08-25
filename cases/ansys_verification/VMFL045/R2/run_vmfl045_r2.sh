#!/usr/bin/env bash
# VMFL045 -- Oblique Shock Over an Inclined Ramp.
# Builds and runs the three-level Roache family.  It does NOT grade anything;
# grading is grade_vmfl045.py, frozen separately and cited by blob sha in
# PREREGISTRATION.md.
#
# Per-level mesh counts (__NX__, __NY__) are substituted into system/blockMeshDict
# from blockMeshDict.template, and the (level-INDEPENDENT) endTime and
# writeInterval into system/controlDict from controlDict.template.  Every level
# doubles both mesh counts, so h halves EXACTLY and the Roache refinement ratio is
# r = 2 by construction, never inferred from a cell count.
#
# GUARDS, in order:
#   1. refuses if the run directory for a level already exists in any form
#      (CLAUDE.md rule 4: a guard refuses a case where 0 or a time dir already
#      exists -- here the whole level directory must be absent);
#   2. refuses if PREREGISTRATION.md is not committed at HEAD (rule 2);
#   3. refuses if topoSet did not put cells into BOTH frozen sampling zones --
#      an empty sampling zone reads as a number and must never be graded;
#   4. enforces the pre-registered CAP in core-minutes -- an overrun STOPS the
#      run, it does not get a new budget (rule 12).
#
# CAP AS A WALL-CLOCK TIMEOUT (the instrument trap the team measured): this is a
# SERIAL run (RANKS=1), so core-minutes = wall_s / 60 and the timeout in seconds
# equals CAP_CORE_MIN*60.  For a PARALLEL run the timeout would instead have to be
# CAP_CORE_MIN*60/RANKS; that formula is written here so a future parallel variant
# cannot get it wrong.
#
# The age-guard datum is the whole of 0/: every file in it is touched immediately
# before the solver launches, so every field at endTime must be strictly newer
# than the newest file in 0/.
set -u -o pipefail

CASE_SRC="/home/ubuntu/Certonomous/cases/ansys_verification/VMFL045/R2/case"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL045/R2"
PREREG="cases/ansys_verification/VMFL045/R2/PREREGISTRATION.md"

CAP_CORE_MIN=48          # pre-registered CEILING (point estimate 20.4 core-min);
                         # the supervisor's authorisation for this case is 50.
                         # An overrun STOPS the run; it does not get a new budget.
RANKS=1                  # serial: core-minutes = wall_s * RANKS / 60
                         # timeout_s = CAP_CORE_MIN*60/RANKS  (= CAP_CORE_MIN*60 serial)

ENDTIME="0.007"          # s -- IDENTICAL at every level (physical time)
WRITEINTERVAL="0.0035"   # s -- two field writes: 0.0035 and 0.007

# name:NX:NY
LEVELS="L1_90x76:90:76 L2_180x152:180:152 L3_360x304:360:304"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

refuse() { echo "REFUSE: $*" >&2; exit 2; }

# --- guard 2: the freeze must be committed before any compute -----------------
cd /home/ubuntu/Certonomous || refuse "repository not found"
git cat-file -e "HEAD:${PREREG}" 2>/dev/null || \
  refuse "the pre-registration is NOT committed at HEAD -- no solver may start (CLAUDE.md rule 2)"
PREREG_SHA=$(git rev-parse "HEAD:${PREREG}")
GRADER_SHA=$(git rev-parse "HEAD:cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py") \
  || refuse "the comparator is not committed at HEAD"
echo "pre-registration frozen at blob ${PREREG_SHA}"
echo "comparator        frozen at blob ${GRADER_SHA}"

# --- guard 1: no level directory may pre-exist -------------------------------
for spec in $LEVELS; do
  name="${spec%%:*}"
  [ -e "${RUN_ROOT}/${name}" ] && refuse "${RUN_ROOT}/${name} already exists -- this script never runs into an existing case"
done
mkdir -p "$RUN_ROOT" || refuse "cannot create ${RUN_ROOT}"

# shellcheck disable=SC1090
# The vendor bashrc READS $WM_PROJECT_DIR before it EXPORTS it, so under set -u
# the source dies before || refuse fires (VMFL001-R2 Amendment 1).  Source it
# with u unset, then restore.
set +u
source "$FOAM_BASHRC" || refuse "cannot source ${FOAM_BASHRC}"
set -u
for c in rhoCentralFoam blockMesh checkMesh topoSet; do
  command -v "$c" >/dev/null || refuse "$c not on PATH after sourcing ${FOAM_BASHRC}"
done

# --- PRE-FLIGHT SMOKE TEST (R2 addition; the generalisable fix for run 1) -----
# Run 1 died on its first timestep with "Entry 'e' not found in fvSolution/solvers":
# a viscous (mu>0) rhoCentralFoam needs an energy solver entry that the inviscid
# precedent's dictionary lacked, and NO comparator --selftest could catch it,
# because a selftest proves the GRADER, not the CASE.  So before any graded level
# runs, execute a few timesteps of rhoCentralFoam on the COARSEST mesh in a SCRATCH
# directory OUTSIDE verification/runs/, exercising the real solver dictionary set.
# If it fails, abort the whole run.  The smoke run NEVER touches the graded run
# tree -- the age guard and guard-1 depend on that tree, so the smoke lives in /tmp
# and is deleted on success.  Cost: a few core-seconds, inside the cap.
SMOKE_DIR=$(mktemp -d /tmp/vmfl045_r2_smoke.XXXXXX) || refuse "cannot create smoke scratch dir"
cp -r "${CASE_SRC}/0" "${CASE_SRC}/constant" "${CASE_SRC}/system" "$SMOKE_DIR/" || refuse "smoke: case copy failed"
rm -f "$SMOKE_DIR/system/blockMeshDict.template" "$SMOKE_DIR/system/controlDict.template"
sed -e "s/__NX__/90/g" -e "s/__NY__/76/g" \
    "${CASE_SRC}/system/blockMeshDict.template" > "$SMOKE_DIR/system/blockMeshDict" \
    || refuse "smoke: blockMeshDict substitution failed"
# a handful of steps only -- a dictionary error, if present, fires on step 1
sed -e "s/__ENDTIME__/1e-7/g" -e "s/__WRITEINTERVAL__/1e-7/g" \
    "${CASE_SRC}/system/controlDict.template" > "$SMOKE_DIR/system/controlDict" \
    || refuse "smoke: controlDict substitution failed"
sm_t0=$(date +%s)
( cd "$SMOKE_DIR" && blockMesh > log.blockMesh 2>&1 && topoSet > log.topoSet 2>&1 \
    && timeout 120 rhoCentralFoam > log.rhoCentralFoam 2>&1 ); sm_rc=$?
sm_t1=$(date +%s); sm_wall=$(( sm_t1 - sm_t0 ))
printf 'smoke_rc=%d\nsmoke_wall_s=%d\nsmoke_dir=%s\nendTime=1e-7\nlevel=L1_90x76(coarsest)\nutc=%s\n' \
    "$sm_rc" "$sm_wall" "$SMOKE_DIR" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "${RUN_ROOT}/SMOKE.txt"
if [ "$sm_rc" -ne 0 ]; then
  cp "$SMOKE_DIR/log.rhoCentralFoam" "${RUN_ROOT}/smoke.log.rhoCentralFoam" 2>/dev/null || true
  rm -rf "$SMOKE_DIR"
  refuse "PRE-FLIGHT SMOKE FAILED (rc=${sm_rc}) -- the solver dictionary set is incomplete; NO graded level will run (this is run 1's exact failure mode). See ${RUN_ROOT}/smoke.log.rhoCentralFoam"
fi
echo "pre-flight smoke PASSED (rc=0, ${sm_wall}s) on the coarsest mesh -- solver dictionaries are complete"
rm -rf "$SMOKE_DIR"

BUDGET_S=$(python3 -c "print(int(${CAP_CORE_MIN}*60/${RANKS}))")
SPENT_S=0

for spec in $LEVELS; do
  IFS=: read -r name NX NY <<< "$spec"
  d="${RUN_ROOT}/${name}"
  cells=$(( NX * NY ))
  echo "=== ${name}: NX=${NX}, NY=${NY} (cells ${cells}), endTime=${ENDTIME} ==="
  mkdir -p "$d" || refuse "cannot create $d"
  cp -r "${CASE_SRC}/0" "${CASE_SRC}/constant" "${CASE_SRC}/system" "$d/" || refuse "case copy failed"
  rm -f "$d/system/blockMeshDict.template" "$d/system/controlDict.template"

  sed -e "s/__NX__/${NX}/g" -e "s/__NY__/${NY}/g" \
      "${CASE_SRC}/system/blockMeshDict.template" > "$d/system/blockMeshDict" \
      || refuse "blockMeshDict substitution failed"
  grep -q "__NX__\|__NY__" "$d/system/blockMeshDict" && refuse "an unsubstituted mesh placeholder survived in ${name}"

  sed -e "s/__ENDTIME__/${ENDTIME}/g" -e "s/__WRITEINTERVAL__/${WRITEINTERVAL}/g" \
      "${CASE_SRC}/system/controlDict.template" > "$d/system/controlDict" \
      || refuse "controlDict substitution failed"
  grep -q "__ENDTIME__\|__WRITEINTERVAL__" "$d/system/controlDict" && refuse "an unsubstituted time placeholder survived in ${name}"

  ( cd "$d" && blockMesh > log.blockMesh 2>&1 ); rc=$?
  [ $rc -eq 0 ] || refuse "${name}: blockMesh returned ${rc}"
  # mesh birth certificate (VERIFICATION_CHARTER section 9): checkMesh at creation
  ( cd "$d" && checkMesh > log.checkMesh 2>&1 )

  # the frozen sampling zones
  ( cd "$d" && topoSet > log.topoSet 2>&1 ); rc=$?
  [ $rc -eq 0 ] || refuse "${name}: topoSet returned ${rc}"
  # --- guard 3: BOTH zones must be non-empty --------------------------------
  for z in gateZone gateZoneInner; do
    n=$(grep -oE "${z} now size [0-9]+" "$d/log.topoSet" | tail -1 | grep -oE '[0-9]+$')
    [ -n "${n:-}" ] || refuse "${name}: cannot read the size of ${z} from log.topoSet"
    [ "$n" -gt 0 ] || refuse "${name}: the frozen sampling zone ${z} is EMPTY -- an empty zone reads as a number and must never be graded"
    echo "${name}: ${z} holds ${n} cells"
  done

  remaining=$(( BUDGET_S - SPENT_S ))
  [ "$remaining" -gt 0 ] || { echo "CAP_EXCEEDED before ${name}" > "${RUN_ROOT}/CAP_EXCEEDED.txt"; refuse "cap of ${CAP_CORE_MIN} core-min exhausted before ${name} -- the run stops, it does not get a new budget"; }

  # AGE-GUARD MARKER: the whole of 0/, touched last before launch
  touch "$d"/0/* || refuse "cannot touch the age-guard datum in ${name}"
  t0=$(date +%s)
  ( cd "$d" && timeout "${remaining}" rhoCentralFoam > log.rhoCentralFoam 2>&1 ); rc=$?
  t1=$(date +%s)
  wall=$(( t1 - t0 )); SPENT_S=$(( SPENT_S + wall ))
  cm=$(python3 -c "print('%.4f' % (${wall}*${RANKS}/60.0))")
  printf 'level=%s\nrc=%d\nwall_s=%d\nranks=%d\ncore_min=%s\ncells=%d\nprereg_blob=%s\ngrader_blob=%s\nutc=%s\n' \
      "$name" "$rc" "$wall" "$RANKS" "$cm" "$cells" "$PREREG_SHA" "$GRADER_SHA" \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$d/RUN_RC.txt"
  echo "${name}: rc=${rc}, wall=${wall}s, ${cm} core-min"
  if [ $rc -eq 124 ]; then
    echo "CAP_EXCEEDED during ${name}" > "${RUN_ROOT}/CAP_EXCEEDED.txt"
    refuse "${name} hit the ${CAP_CORE_MIN} core-min cap -- the run STOPS (rule 12)"
  fi
  [ $rc -eq 0 ] || refuse "${name}: rhoCentralFoam returned ${rc} -- a crash is a finding, triage before anything else"
done

total_cm=$(python3 -c "print('%.4f' % (${SPENT_S}*${RANKS}/60.0))")
printf 'total_wall_s=%d\nranks=%d\ntotal_core_min=%s\ncap_core_min=%d\npoint_estimate_core_min=20.4\nutc=%s\n' \
    "$SPENT_S" "$RANKS" "$total_cm" "$CAP_CORE_MIN" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "${RUN_ROOT}/COST.txt"
echo "all three levels complete: ${total_cm} core-min of a ${CAP_CORE_MIN} core-min cap"
echo "grade with: python3 cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py"
