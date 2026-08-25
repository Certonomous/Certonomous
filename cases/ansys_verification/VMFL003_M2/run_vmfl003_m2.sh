#!/bin/bash
# ===========================================================================
# VMFL003-M2 -- "Try Other Models": THE LAUNCHER for the four-model slate
# {A kEpsilon, B realizableKE, C RNGkEpsilon, D kOmegaSST}.
#
# NOT FILED ANYWHERE.  Nothing this script produces leaves this box.
#
# NO GRADED COMPUTE HAS RUN FROM THIS FILE.  It is committed BEFORE the
# pre-registration is frozen and long before any graded solver starts.  The
# GRADED run of any arm is LOCKED: launch authorisation comes from the
# ansys-verification-supervisor PERSONALLY, after its four SUPERVISION_CHARTER
# section 3 checks (measurement-script diffs read as diffs; crash/refusal
# triage; big-claim verification; PREREGISTRATION.md COMMITTED before compute).
# No agent message is Sanaa's consent (CLAUDE.md rule 9).
#
# What HAS run before this commit, with its own 5-core-minute cap, in a scratch
# tree OUTSIDE verification/runs (so it can touch neither the age guard nor a
# launcher guard): blockMesh / checkMesh / topoSet on the six meshes, and a
# ONE-ITERATION pre-flight smoke test of each of the four arms.  The evidence
# copies live under cases/ansys_verification/VMFL003_M2/ (mesh_certificates/,
# smoke/), never in the runs tree.  See LANE_REPORT.md.
#
# ---------------------------------------------------------------------------
# `set -e` IS DELIBERATELY NOT RELIED ON.  It was MEASURED not to be in force
# in this lab's agent execution context, and `( set -e; ... )` silently fails
# too (this team's board).  Every single check below therefore gates with an
# explicit `|| { echo ABORT...; exit 1; }`.  A check that only prints is not a
# check.
# ---------------------------------------------------------------------------
#
# THE COST INSTRUMENT (CLAUDE.md rule 12).  RANKS is in both formulae so a
# future parallel copy inherits a correct cap:
#     timeout_s    = remaining_core_min * 60 / RANKS
#     core_minutes = wall_s * RANKS / 60
# Serial here (RANKS=1).  The cap is a RUNNING TOTAL across all four arms and
# all six meshes; a per-arm sub-cap also applies.  AN OVERRUN STOPS THE RUN; IT
# DOES NOT GET A NEW BUDGET.
# ===========================================================================

RANKS=1
CAP_CORE_MIN=160          # slate running total, frozen in PREREGISTRATION.md 12
PER_ARM_CAP=40            # per-model sub-cap, frozen in PREREGISTRATION.md 12
CASEDIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$CASEDIR/../../.." && pwd)"
RUNROOT="$REPO/verification/runs/ansys_verification/VMFL003_M2"
PREREG="cases/ansys_verification/VMFL003_M2/PREREGISTRATION.md"

# arm-id  case-overlay-dir       comparator
ARMS=(
  "A_kEpsilon      A_kEpsilon      grade_vmfl003_m2.py"
  "B_realizableKE  B_realizableKE  grade_vmfl003_m2.py"
  "C_RNGkEpsilon   C_RNGkEpsilon   grade_vmfl003_m2.py"
  "D_kOmegaSST     D_kOmegaSST     grade_vmfl003_m2_omega.py"
)

# level      nx     nr   endTime
LEVELS=(
  "L1_250x5    250   5   15000"
  "L2_500x5    500   5   18000"
  "L3_1000x5  1000   5   22000"
  "D_500x3     500   3   18000"
  "D_500x4     500   4   18000"
  "D_500x6     500   6   18000"
)

echo "VMFL003-M2 launcher -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- GUARD 1: the pre-registration must be COMMITTED at HEAD ----------------
git -C "$REPO" cat-file -e "HEAD:$PREREG" 2>/dev/null \
  || { echo "ABORT: $PREREG is not committed at HEAD -- the freeze is the "\
"evidence and no graded solver starts without it"; exit 1; }
DISK_SHA=$(git -C "$REPO" hash-object "$REPO/$PREREG") \
  || { echo "ABORT: cannot hash $PREREG"; exit 1; }
HEAD_SHA=$(git -C "$REPO" rev-parse "HEAD:$PREREG") \
  || { echo "ABORT: cannot resolve HEAD:$PREREG"; exit 1; }
[ "$DISK_SHA" = "$HEAD_SHA" ] \
  || { echo "ABORT: $PREREG on disk ($DISK_SHA) differs from HEAD ($HEAD_SHA)"; exit 1; }
echo "  freeze check OK: $PREREG == HEAD ($HEAD_SHA)"

# --- GUARD 2: BOTH comparators must be the frozen files --------------------
python3 "$CASEDIR/grade_vmfl003_m2.py" --verify-frozen HEAD \
  || { echo "ABORT: grade_vmfl003_m2.py on disk is not the committed grading path"; exit 1; }
python3 "$CASEDIR/grade_vmfl003_m2_omega.py" --verify-frozen HEAD \
  || { echo "ABORT: grade_vmfl003_m2_omega.py on disk is not the committed grading path"; exit 1; }

# --- GUARD 3: refuse to start into ANY pre-existing arm/level directory -----
for aspec in "${ARMS[@]}"; do
  set -- $aspec; ARM="$1"
  for lspec in "${LEVELS[@]}"; do
    set -- $lspec
    [ -e "$RUNROOT/$ARM/$1" ] \
      && { echo "ABORT: $RUNROOT/$ARM/$1 already exists -- rule 4's guard "\
"refuses a case where 0/ or a time directory already exists.  A repeat is a "\
"NEW RUNG, never a re-grade in place."; exit 1; }
  done
done
echo "  no pre-existing arm/level directories"

# --- OpenFOAM environment --------------------------------------------------
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1 \
  || { echo "ABORT: cannot source the OpenFOAM v2606 environment"; exit 1; }
command -v simpleFoam >/dev/null \
  || { echo "ABORT: simpleFoam not on PATH after sourcing"; exit 1; }

# ===========================================================================
# build_case <dest> <arm-overlay> <nx> <nr> <endtime>
#   Materialises one arm/level: the model-agnostic base, then the arm overlay
#   ON TOP (turbulenceProperties, the 2nd turbulence field, and for D the
#   omega fvSchemes/fvSolution).  NEVER edits a template.
# ===========================================================================
build_case() {
  local dest="$1" arm="$2" nx="$3" nr="$4" endt="$5"
  mkdir -p "$dest" || return 1
  cp -a "$CASEDIR/case/0"                 "$dest/0"        || return 1
  cp -a "$CASEDIR/case/constant"          "$dest/constant" || return 1
  mkdir -p "$dest/system" || return 1
  cp "$CASEDIR/case/system/fvSchemes"     "$dest/system/"  || return 1
  cp "$CASEDIR/case/system/fvSolution"    "$dest/system/"  || return 1
  cp "$CASEDIR/case/system/topoSetDict"   "$dest/system/"  || return 1
  # overlay the arm's model-specific files OVER the base (may replace fvSchemes/
  # fvSolution for the omega arm; adds turbulenceProperties and the 2nd field).
  cp -a "$CASEDIR/arms/$arm/." "$dest/" || return 1
  sed -e "s/__NX__/$nx/g" -e "s/__NR__/$nr/g" \
      "$CASEDIR/case/system/blockMeshDict.template" > "$dest/system/blockMeshDict" || return 1
  sed -e "s/__ENDTIME__/$endt/g" \
      "$CASEDIR/case/system/controlDict.template" > "$dest/system/controlDict" || return 1
  grep -q "__NX__\|__NR__\|__ENDTIME__" "$dest/system/blockMeshDict" "$dest/system/controlDict" \
    && return 1
  return 0
}

# ===========================================================================
# mesh_case <dest> <generator-label>
#   blockMesh + checkMesh + topoSet; REFUSES if either frozen sampling zone is
#   EMPTY; then writes the MESH BIRTH CERTIFICATE beside constant/polyMesh from
#   the checkMesh log (Mesh Standard section 6 / Verification Charter v1.5
#   section 9) -- born clean or it does not enter, and the check that ran is
#   provable from the artifact.
# ===========================================================================
mesh_case() {
  local dest="$1" label="$2"
  ( cd "$dest" && blockMesh > log.blockMesh 2>&1 ) || return 1
  ( cd "$dest" && checkMesh -allGeometry > log.checkMesh 2>&1 ) || return 1
  ( cd "$dest" && topoSet   > log.topoSet   2>&1 ) || return 1
  local na nb
  na=$(grep -oE "cellZoneSet slabA now size [0-9]+" "$dest/log.topoSet" | tail -1 | grep -oE "[0-9]+$")
  nb=$(grep -oE "cellZoneSet slabB now size [0-9]+" "$dest/log.topoSet" | tail -1 | grep -oE "[0-9]+$")
  [ -n "$na" ] && [ "$na" -gt 0 ] || return 1
  [ -n "$nb" ] && [ "$nb" -gt 0 ] || return 1
  PYTHONPATH="$REPO" python3 - "$dest" "$label" <<'PYCERT' || return 1
import sys
from pathlib import Path
from sdk.chief_engineer.mesh_certificate import write_certificate, certificate_admits, PROVENANCE_AT_CREATION
dest, label = sys.argv[1], sys.argv[2]
log = (Path(dest) / "log.checkMesh").read_text(errors="replace")
cert = write_certificate(Path(dest) / "constant", check_log_text=log,
                         generator="blockMesh, VMFL003-M2 %s, PREREGISTRATION.md" % label,
                         provenance=PROVENANCE_AT_CREATION)
if cert is None:
    sys.stderr.write("mesh certificate NOT written for %s\n" % dest); sys.exit(1)
ok, why = certificate_admits(Path(dest) / "constant")
if not ok:
    sys.stderr.write("mesh does not enter (%s): %s\n" % (dest, why)); sys.exit(1)
print("  mesh cert %s: %s (%s cells, aspect %s, nonOrtho %s, skew %s)" % (
    label, cert["verdict"], cert["cells"], cert["max_aspect_ratio"],
    cert["max_non_orthogonality"], cert["max_skewness"]))
PYCERT
  return 0
}

# ===========================================================================
# PRE-FLIGHT SMOKE TEST -- ONE TIMESTEP, COARSEST MESH, PER ARM, IN A SCRATCH
# DIRECTORY OUTSIDE verification/runs.
#
# WHY, and it is MEASURED, not a precaution: a comparator --selftest proves the
# GRADER, not the CASE or the LAUNCHER.  This team's VMFL045 passed 45/45
# selftest and still died on its first timestep; VMFL003's OWN run-1 launcher
# passed 60/60 while being UNRUNNABLE (a topoSet-guard pattern that matched zero
# lines of real v2606 output).  Each of the four arms is a DISTINCT case setup
# (different turbulenceProperties, and for D different fields and system files),
# so each is smoke-tested independently.  The smoke trees are deleted and
# NOTHING they produce is ever graded.
# ===========================================================================
SMOKE=$(mktemp -d "${TMPDIR:-/tmp}/vmfl003m2-smoke-XXXXXX") \
  || { echo "ABORT: cannot create a scratch directory for the smoke test"; exit 1; }
echo "  pre-flight smoke test in $SMOKE (outside verification/runs)"
for aspec in "${ARMS[@]}"; do
  set -- $aspec; ARM="$1"; OVL="$2"
  build_case "$SMOKE/$ARM" "$OVL" 250 5 1 \
    || { echo "ABORT: smoke ($ARM) could not materialise the case from templates"; rm -rf "$SMOKE"; exit 1; }
  mesh_case "$SMOKE/$ARM" "smoke-$ARM" \
    || { echo "ABORT: smoke ($ARM) FAILED at blockMesh/checkMesh/topoSet/cert -- see $SMOKE/$ARM/log.*"; exit 1; }
  ( cd "$SMOKE/$ARM" && timeout 300 simpleFoam > log.simpleFoam 2>&1 ) \
    || { echo "ABORT: smoke ($ARM) FAILED on its first timestep.  The case setup "\
"is broken and NO level is launched.  Log: $SMOKE/$ARM/log.simpleFoam"; exit 1; }
  grep -qE "^End$" "$SMOKE/$ARM/log.simpleFoam" \
    || { echo "ABORT: smoke ($ARM) produced no End line"; exit 1; }
  echo "  smoke ($ARM) PASSED (1 iteration on the coarsest mesh)"
done
rm -rf "$SMOKE"

# ===========================================================================
# THE REAL LEVELS -- FOUR ARMS x SIX MESHES.  GRADED COMPUTE.  LOCKED until the
# supervisor unlocks it (this script is run BY the supervisor after its four
# checks, not by the drafting/mesh lane).
# ===========================================================================
mkdir -p "$RUNROOT" || { echo "ABORT: cannot create $RUNROOT"; exit 1; }
SPENT_CORE_MIN=0
TOTAL_WALL=0

for aspec in "${ARMS[@]}"; do
  set -- $aspec; ARM="$1"; OVL="$2"; CMP="$3"
  ARM_ROOT="$RUNROOT/$ARM"
  ARM_SPENT=0
  echo "=== ARM $ARM  (overlay $OVL, comparator $CMP) ==="

  for lspec in "${LEVELS[@]}"; do
    set -- $lspec
    LEVEL="$1"; NX="$2"; NR="$3"; ENDT="$4"
    DEST="$ARM_ROOT/$LEVEL"

    REMAIN=$(python3 -c "print(max(0.0, min($CAP_CORE_MIN - $SPENT_CORE_MIN, $PER_ARM_CAP - $ARM_SPENT)))") \
      || { echo "ABORT: cannot compute the remaining budget"; exit 1; }
    TIMEOUT_S=$(python3 -c "print(int($REMAIN * 60 / $RANKS))") \
      || { echo "ABORT: cannot compute the timeout"; exit 1; }
    [ "$TIMEOUT_S" -gt 0 ] \
      || { echo "ABORT: BUDGET EXHAUSTED before $ARM/$LEVEL (slate $SPENT_CORE_MIN "\
"of $CAP_CORE_MIN, arm $ARM_SPENT of $PER_ARM_CAP core-min).  An overrun STOPS "\
"the run; it does not get a new budget (CLAUDE.md rule 12)."; exit 1; }

    echo "--- $ARM/$LEVEL  nx=$NX nr=$NR endTime=$ENDT  timeout=${TIMEOUT_S}s "\
"(remaining ${REMAIN} core-min)"

    build_case "$DEST" "$OVL" "$NX" "$NR" "$ENDT" \
      || { echo "ABORT: could not build $ARM/$LEVEL"; exit 1; }
    mesh_case "$DEST" "$ARM/$LEVEL" \
      || { echo "ABORT: $ARM/$LEVEL FAILED at meshing/cert, or topoSet left a "\
"frozen sampling zone EMPTY.  See $DEST/log.*"; exit 1; }

    # AGE-GUARD DATUM: touch EVERY file in this level's own 0/ as the LAST
    # action before the solver starts (comparator clause C6, stricter than rule 4).
    find "$DEST/0" -type f -exec touch {} + \
      || { echo "ABORT: could not set the age-guard datum for $ARM/$LEVEL"; exit 1; }
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

    printf 'rc=%d\narm=%s\nlevel=%s\nnx=%s\nnr=%s\nendTime=%s\nwall_s=%d\nranks=%d\ncore_min=%s\ntimeout_s=%d\n' \
      "$RC" "$ARM" "$LEVEL" "$NX" "$NR" "$ENDT" "$WALL" "$RANKS" "$CORE_MIN" "$TIMEOUT_S" \
      > "$DEST/RUN_RC.txt" \
      || { echo "ABORT: could not write RUN_RC.txt for $ARM/$LEVEL"; exit 1; }

    [ "$RC" -eq 0 ] \
      || { echo "ABORT: $ARM/$LEVEL exited rc=$RC after ${WALL}s (timeout ${TIMEOUT_S}s). "\
"A non-zero rc is a FINDING, not a retry: it is triaged before anything else runs."; exit 1; }
    echo "    $ARM/$LEVEL done: ${WALL}s = ${CORE_MIN} core-min "\
"(arm ${ARM_SPENT}/${PER_ARM_CAP}, slate ${SPENT_CORE_MIN}/${CAP_CORE_MIN})"
  done

  echo "  grading $ARM with $CMP ..."
  python3 "$CASEDIR/$CMP" --runroot "$ARM_ROOT" --json "$ARM_ROOT/GRADING_${ARM}.json" \
    || echo "  NOTE: comparator for $ARM returned non-zero (a REFUSAL is a finding; triage before belief)"
done

printf 'total_wall_s=%d\nranks=%d\ntotal_core_min=%s\ncap_core_min=%s\nper_arm_cap=%s\ncost_basis=owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md section 5)\n' \
  "$TOTAL_WALL" "$RANKS" "$SPENT_CORE_MIN" "$CAP_CORE_MIN" "$PER_ARM_CAP" > "$RUNROOT/COST.txt" \
  || { echo "ABORT: could not write COST.txt"; exit 1; }

echo "ALL ARMS COMPLETE: ${TOTAL_WALL}s wall = ${SPENT_CORE_MIN} core-min of a ${CAP_CORE_MIN} core-min cap."
