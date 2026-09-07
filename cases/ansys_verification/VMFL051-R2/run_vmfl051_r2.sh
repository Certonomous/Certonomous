#!/usr/bin/env bash
# VMFL051-R2 -- Isentropic Expansion of Supersonic Flow Over a Convex Corner.
# SUCCESSOR to VMFL051 run 1 (register #4, NOT A RESULT).
#
# The SOLVE is byte-identical to run 1: same three-level r=2 family, same
# endTime (7.0e-3 s), same scheme, same sampling zones.  The ONLY change from
# run 1 is in the COMPARATOR (grade_vmfl051_r2.py): the per-level gate value is
# the TIME-MEAN of volAverage(Ma) over the settled window, not the endTime
# snapshot.  This script builds and runs the family; it does NOT grade anything.
#
# GUARDS, in order:
#   1. FREEZE-PIN (rule 2): the pre-registration AND the comparator on disk must
#      be BYTE-IDENTICAL to their committed HEAD blobs -- not merely present.  No
#      solver may start otherwise.
#   2. AGE GUARD (rule 4): refuses if the run directory for a level already
#      exists in any form; the run root is created only here, at launch.
#   3. refuses if topoSet did not put cells into BOTH frozen sampling zones --
#      an empty sampling zone reads as a number and must never be graded.
#   4. enforces the pre-registered CAP in core-minutes as a RUNNING TOTAL -- an
#      overrun STOPS the run (rc 124), it does not get a new budget (rule 12).
#
# The age-guard datum is the whole of 0/: every file in it is touched
# immediately before the solver launches, so every field at endTime must be
# strictly newer than the newest file in 0/.
#
# RUN_RC.txt records the solver's OWN return code, captured INSIDE this script
# immediately after the timeout subshell (rc=$?), never a setsid/detach wrapper's
# zero (the setsid-parent-returns-zero trap): if a launcher wraps this whole
# script in `setsid`/`timeout`, the per-level rc written below is still the real
# solver rc because it is captured here, one statement after the solver call.
set -u -o pipefail

REPO="/home/ubuntu/Certonomous"
CASE_SRC="${REPO}/cases/ansys_verification/VMFL051-R2/case"
RUN_ROOT="${REPO}/verification/runs/ansys_verification/VMFL051-R2"
PREREG_REL="cases/ansys_verification/VMFL051-R2/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL051-R2/grade_vmfl051_r2.py"

CAP_CORE_MIN=28          # pre-registered CEILING; UNCHANGED from run 1 (which
                         # ran the identical solve in 23.32 core-min, 83% of cap).
                         # The supervisor's authorisation for this case is 30.
                         # An overrun STOPS the run; it does not get a new budget.
RANKS=1                  # serial: core-minutes = wall_s * RANKS / 60
                         # timeout seconds = CAP_CORE_MIN * 60 / RANKS (correct
                         # for any rank count; run 1's C-50 instrument note).

ENDTIME="0.007"          # s -- IDENTICAL at every level and UNCHANGED from run 1
WRITEINTERVAL="0.0035"   # s -- two field writes: 0.0035 and 0.007

# name:NXA:NXB:NY  (every level doubles all three counts -> r = 2 by construction)
LEVELS="L1_120x52:24:96:52 L2_240x104:48:192:104 L3_480x208:96:384:208"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

refuse() { echo "REFUSE: $*" >&2; exit 2; }

cd "$REPO" || refuse "repository not found"

# --- guard 1: FREEZE-PIN -- disk must be byte-identical to the HEAD blob -------
for pair in "${PREREG_REL}" "${GRADER_REL}"; do
  [ -f "$pair" ] || refuse "missing on disk: $pair"
  head_sha=$(git rev-parse "HEAD:${pair}" 2>/dev/null) || \
    refuse "$pair is NOT committed at HEAD -- no solver may start (CLAUDE.md rule 2)"
  disk_sha=$(git hash-object "$pair") || refuse "cannot hash $pair"
  [ "$disk_sha" = "$head_sha" ] || \
    refuse "$pair on disk (blob ${disk_sha}) is NOT the HEAD blob (${head_sha}) -- the freeze has moved (rule 2)"
  echo "freeze-pin OK: ${pair} == HEAD blob ${head_sha}"
done
PREREG_SHA=$(git rev-parse "HEAD:${PREREG_REL}")
GRADER_SHA=$(git rev-parse "HEAD:${GRADER_REL}")

# --- guard 2: no level directory may pre-exist (age guard) --------------------
for spec in $LEVELS; do
  name="${spec%%:*}"
  [ -e "${RUN_ROOT}/${name}" ] && refuse "${RUN_ROOT}/${name} already exists -- this script never runs into an existing case"
done
mkdir -p "$RUN_ROOT" || refuse "cannot create ${RUN_ROOT}"

# shellcheck disable=SC1090
# The vendor bashrc READS $WM_PROJECT_DIR before it EXPORTS it, so under set -u
# the source dies before || refuse fires (VMFL001-R2 Amendment 1).  Source with
# u unset, then restore.
set +u
source "$FOAM_BASHRC" || refuse "cannot source ${FOAM_BASHRC}"
set -u
for c in rhoCentralFoam blockMesh checkMesh topoSet; do
  command -v "$c" >/dev/null || refuse "$c not on PATH after sourcing ${FOAM_BASHRC}"
done

BUDGET_S=$(python3 -c "print(int(${CAP_CORE_MIN}*60/${RANKS}))")
SPENT_S=0

for spec in $LEVELS; do
  IFS=: read -r name NXA NXB NY <<< "$spec"
  d="${RUN_ROOT}/${name}"
  cells=$(( (NXA + NXB) * NY ))
  echo "=== ${name}: NXA=${NXA}, NXB=${NXB}, NY=${NY} (cells ${cells}), endTime=${ENDTIME} ==="
  mkdir -p "$d" || refuse "cannot create $d"
  cp -r "${CASE_SRC}/0" "${CASE_SRC}/constant" "${CASE_SRC}/system" "$d/" || refuse "case copy failed"
  rm -f "$d/system/blockMeshDict.template" "$d/system/controlDict.template"

  sed -e "s/__NXA__/${NXA}/g" -e "s/__NXB__/${NXB}/g" -e "s/__NY__/${NY}/g" \
      "${CASE_SRC}/system/blockMeshDict.template" > "$d/system/blockMeshDict" \
      || refuse "blockMeshDict substitution failed"
  grep -q "__NX\|__NY__" "$d/system/blockMeshDict" && refuse "an unsubstituted mesh placeholder survived in ${name}"

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
  ( cd "$d" && timeout "${remaining}" rhoCentralFoam > log.rhoCentralFoam 2>&1 ); rc=$?   # rc = the SOLVER's own return code, captured here
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
printf 'total_wall_s=%d\nranks=%d\ntotal_core_min=%s\ncap_core_min=%d\npoint_estimate_core_min=23.32\nutc=%s\n' \
    "$SPENT_S" "$RANKS" "$total_cm" "$CAP_CORE_MIN" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "${RUN_ROOT}/COST.txt"
echo "all three levels complete: ${total_cm} core-min of a ${CAP_CORE_MIN} core-min cap"
echo "grade with: python3 cases/ansys_verification/VMFL051-R2/grade_vmfl051_r2.py"
