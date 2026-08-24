#!/usr/bin/env bash
# VMFL005 -- Poiseuille flow in a pipe.  Builds and runs the three-level Roache
# family (axisymmetric wedge).  It does NOT grade anything; grading is
# grade_vmfl005.py, frozen separately and cited by sha in PREREGISTRATION.md.
#
# Per-level endTime (L1 2000, L2 3000, L3 6000 SIMPLE iterations) is substituted
# into system/controlDict from controlDict.template (__ENDTIME__ placeholder on
# both endTime and writeInterval); the mesh size (__NX__, __NR__) into
# system/blockMeshDict from blockMeshDict.template.
#
# GUARDS, in order:
#   1. refuses to start if the run directory for a level already exists in any
#      form (CLAUDE.md rule 4: a guard refuses a case where 0 or a time dir
#      already exists -- here the whole level directory must be absent);
#   2. refuses if the pre-registration is not committed at HEAD (rule 2);
#   3. enforces the pre-registered CAP in core-minutes -- an overrun STOPS the
#      run, it does not get a new budget (rule 12).
#
# The age-guard marker is 0/U: touched immediately before the solver launches,
# so every field at endTime must be strictly newer than it.
set -u -o pipefail

CASE_SRC="/home/ubuntu/Certonomous/cases/ansys_verification/VMFL005/case"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL005"
PREREG="cases/ansys_verification/VMFL005/PREREGISTRATION.md"
CAP_CORE_MIN=13          # pre-registered cap (estimate ~4.9 core-min x 2.5, rounded up); overrun stops the run
RANKS=1                  # serial: core-minutes = wall_s * RANKS / 60
# name:NX:NR:endTime -- per-level endTime
LEVELS="L1_100x10:100:10:2000 L2_200x20:200:20:3000 L3_400x40:400:40:6000"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

refuse() { echo "REFUSE: $*" >&2; exit 2; }

# --- guard 2: the freeze must be committed before any compute -----------------
cd /home/ubuntu/Certonomous || refuse "repository not found"
git cat-file -e "HEAD:${PREREG}" 2>/dev/null || \
  refuse "the pre-registration is NOT committed at HEAD -- no solver may start (CLAUDE.md rule 2)"
PREREG_SHA=$(git rev-parse "HEAD:${PREREG}")
echo "pre-registration frozen at blob ${PREREG_SHA}"

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
command -v simpleFoam >/dev/null || refuse "simpleFoam not on PATH after sourcing ${FOAM_BASHRC}"
command -v blockMesh  >/dev/null || refuse "blockMesh not on PATH after sourcing ${FOAM_BASHRC}"

BUDGET_S=$(python3 -c "print(int(${CAP_CORE_MIN}*60/${RANKS}))")
SPENT_S=0

for spec in $LEVELS; do
  IFS=: read -r name NX NR ETIME <<< "$spec"
  d="${RUN_ROOT}/${name}"
  echo "=== ${name}: NX=${NX}, NR=${NR} (cells $((NX*NR))), endTime=${ETIME} ==="
  mkdir -p "$d" || refuse "cannot create $d"
  cp -r "${CASE_SRC}/0" "${CASE_SRC}/constant" "${CASE_SRC}/system" "$d/" || refuse "case copy failed"
  rm -f "$d/system/blockMeshDict.template" "$d/system/controlDict.template"
  sed -e "s/__NX__/${NX}/g" -e "s/__NR__/${NR}/g" \
      "${CASE_SRC}/system/blockMeshDict.template" > "$d/system/blockMeshDict" || refuse "blockMeshDict substitution failed"
  grep -q "__N" "$d/system/blockMeshDict" && refuse "an unsubstituted mesh placeholder survived in ${name}"
  sed -e "s/__ENDTIME__/${ETIME}/g" \
      "${CASE_SRC}/system/controlDict.template" > "$d/system/controlDict" || refuse "controlDict substitution failed"
  grep -q "__ENDTIME__" "$d/system/controlDict" && refuse "an unsubstituted endTime placeholder survived in ${name}"

  ( cd "$d" && blockMesh > log.blockMesh 2>&1 ); rc=$?
  [ $rc -eq 0 ] || refuse "${name}: blockMesh returned ${rc}"
  # mesh birth certificate (VERIFICATION_CHARTER section 9): checkMesh at creation
  ( cd "$d" && checkMesh > log.checkMesh 2>&1 )

  remaining=$(( BUDGET_S - SPENT_S ))
  [ "$remaining" -gt 0 ] || { echo "CAP_EXCEEDED before ${name}" > "${RUN_ROOT}/CAP_EXCEEDED.txt"; refuse "cap of ${CAP_CORE_MIN} core-min exhausted before ${name} -- the run stops, it does not get a new budget"; }

  touch "$d/0/U"                      # AGE-GUARD MARKER, last thing before launch
  t0=$(date +%s)
  ( cd "$d" && timeout "${remaining}" simpleFoam > log.simpleFoam 2>&1 ); rc=$?
  t1=$(date +%s)
  wall=$(( t1 - t0 )); SPENT_S=$(( SPENT_S + wall ))
  cm=$(python3 -c "print('%.4f' % (${wall}*${RANKS}/60.0))")
  printf 'level=%s\nrc=%d\nwall_s=%d\nranks=%d\ncore_min=%s\nprereg_blob=%s\nutc=%s\n' \
      "$name" "$rc" "$wall" "$RANKS" "$cm" "$PREREG_SHA" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$d/RUN_RC.txt"
  echo "${name}: rc=${rc}, wall=${wall}s, ${cm} core-min"
  if [ $rc -eq 124 ]; then
    echo "CAP_EXCEEDED during ${name}" > "${RUN_ROOT}/CAP_EXCEEDED.txt"
    refuse "${name} hit the ${CAP_CORE_MIN} core-min cap -- the run STOPS (rule 12)"
  fi
  [ $rc -eq 0 ] || refuse "${name}: simpleFoam returned ${rc} -- a crash is a finding, triage before anything else"
done

total_cm=$(python3 -c "print('%.4f' % (${SPENT_S}*${RANKS}/60.0))")
printf 'total_wall_s=%d\nranks=%d\ntotal_core_min=%s\ncap_core_min=%d\nutc=%s\n' \
    "$SPENT_S" "$RANKS" "$total_cm" "$CAP_CORE_MIN" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "${RUN_ROOT}/COST.txt"
echo "all three levels complete: ${total_cm} core-min of a ${CAP_CORE_MIN} core-min cap"
echo "grade with: python3 cases/ansys_verification/VMFL005/grade_vmfl005.py"
