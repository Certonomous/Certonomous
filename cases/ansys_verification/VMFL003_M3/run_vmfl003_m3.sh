#!/bin/bash
# ===========================================================================
# VMFL003-M3 -- WALL-RESOLVED kOmegaSST (y+ ~ 1).  THE LAUNCHER.
#
# SINGLE-LEVER successor to VMFL003-M2 (supervisor ruling 2026-09-07): the ONE
# registered physics change is the near-wall TREATMENT (log-law wall FUNCTION ->
# model integrated TO THE WALL).  Model pinned a priori to kOmegaSST for
# METHODOLOGICAL reasons.  One coupled INSTRUMENT change (p solver GAMG -> PCG/DIC,
# system/fvSolution) makes the high-aspect radial mesh solvable; it is NOT a
# physics lever and touches neither the gate nor the residual floor.
#
# NOT FILED ANYWHERE.  Nothing this script produces leaves this box.
#
# NO GRADED COMPUTE HAS RUN FROM THIS FILE.  It is committed BEFORE the freeze.
# The GRADED run is LOCKED: launch authorisation comes from the
# ansys-verification-supervisor PERSONALLY after its SUPERVISION_CHARTER section 3
# checks, AND graded launches are additionally BLOCKED on the auto-mode
# permission classifier (Sanaa's desk, not cleared).  No agent message is Sanaa's
# consent (CLAUDE.md rule 9).
#
# What HAS run before this commit, with its own cap, in a SCRATCH tree OUTSIDE
# verification/runs (touching neither the age guard nor a launcher guard):
# blockMesh / checkMesh on the wall-resolved meshes, an answer-blind y+ smoke
# (y+ and residuals read; Delta p NEVER read), and a p-solver calibration smoke.
# See PREREGISTRATION.md sections 4 and 5.
#
# `set -e` IS DELIBERATELY NOT RELIED ON (measured not in force in this lab's
# agent context).  Every check gates with an explicit `|| { echo ABORT; exit 1; }`.
#
# THE COST INSTRUMENT (CLAUDE.md rule 12):
#     timeout_s    = remaining_core_min * 60 / RANKS
#     core_minutes = wall_s * RANKS / 60
# Serial (RANKS=1).  Per-level caps AND a running-total cap.  AN OVERRUN STOPS
# THE RUN; IT DOES NOT GET A NEW BUDGET.
#
# rc IS CAPTURED FROM THE FOREGROUND `( cd && timeout ) ; RC=$?` SUBSHELL, and
# setsid is DELIBERATELY NOT USED: `setsid timeout cmd` exits 0 for every outcome
# (the setsid-parent-returns-zero trap), so a foreground timeout whose own rc is
# read immediately is the correct idiom -- rc = 124 is timeout's budget-fired
# signature and is preserved.
# ===========================================================================

RANKS=1
CAP_CORE_MIN=180          # running-total cap, frozen in PREREGISTRATION.md 12
CASEDIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$CASEDIR/../../.." && pwd)"
RUNROOT="$REPO/verification/runs/ansys_verification/VMFL003_M3"
PREREG="cases/ansys_verification/VMFL003_M3/PREREGISTRATION.md"
CMP="grade_vmfl003_m3.py"

# level          nx     nr   gr           endTime  per-level-cap(core-min)
# The PRIMARY RADIAL triple (L1/L2/L3) + the orthogonal AXIAL ladder
# (A_500x25, L1[reused], A_2000x25).  gr = blockMesh simpleGrading (last/first)
# along the radial edge, FROZEN (computed once from NR + wall-cell target; see
# PREREGISTRATION.md section 4); gr < 1 clusters the small cell at the wall.
LEVELS=(
  "L1_1000x25    1000    25   0.0369274    5000   20"
  "L2_1000x50    1000    50   0.0361289    5000   35"
  "L3_1000x100   1000   100   0.0357391    5000   80"
  "A_500x25       500    25   0.0369274    5000   12"
  "A_2000x25     2000    25   0.0369274    5000   35"
)

echo "VMFL003-M3 launcher -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- GUARD 1: the pre-registration must be COMMITTED at HEAD ----------------
git -C "$REPO" cat-file -e "HEAD:$PREREG" 2>/dev/null \
  || { echo "ABORT: $PREREG is not committed at HEAD -- the freeze is the evidence"; exit 1; }
DISK_SHA=$(git -C "$REPO" hash-object "$REPO/$PREREG") \
  || { echo "ABORT: cannot hash $PREREG"; exit 1; }
HEAD_SHA=$(git -C "$REPO" rev-parse "HEAD:$PREREG") \
  || { echo "ABORT: cannot resolve HEAD:$PREREG"; exit 1; }
[ "$DISK_SHA" = "$HEAD_SHA" ] \
  || { echo "ABORT: $PREREG on disk ($DISK_SHA) differs from HEAD ($HEAD_SHA)"; exit 1; }
echo "  freeze check OK: $PREREG == HEAD ($HEAD_SHA)"

# --- GUARD 2: the comparator must be the frozen grading path ---------------
FREEZE_COMMIT=$(git -C "$REPO" rev-parse HEAD) \
  || { echo "ABORT: cannot resolve HEAD (FREEZE_COMMIT)"; exit 1; }
python3 "$CASEDIR/$CMP" --verify-frozen "$FREEZE_COMMIT" \
  || { echo "ABORT: $CMP on disk is not the committed grading path at $FREEZE_COMMIT"; exit 1; }
echo "  comparator freeze-pin OK against $FREEZE_COMMIT"

# --- GUARD 3: refuse to start into ANY pre-existing level directory ---------
for lspec in "${LEVELS[@]}"; do
  set -- $lspec
  [ -e "$RUNROOT/$1" ] \
    && { echo "ABORT: $RUNROOT/$1 already exists -- rule 4's guard refuses a case "\
"where 0/ or a time directory already exists.  A repeat is a NEW RUNG, never a "\
"re-grade in place."; exit 1; }
done
echo "  no pre-existing level directories"

# --- OpenFOAM environment --------------------------------------------------
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1 \
  || { echo "ABORT: cannot source the OpenFOAM v2606 environment"; exit 1; }
command -v simpleFoam >/dev/null \
  || { echo "ABORT: simpleFoam not on PATH after sourcing"; exit 1; }

# ===========================================================================
# build_case <dest> <nx> <nr> <gr> <endtime>
#   Materialises one level from the single wall-resolved kOmegaSST case; NEVER
#   edits a template.
# ===========================================================================
build_case() {
  local dest="$1" nx="$2" nr="$3" gr="$4" endt="$5"
  mkdir -p "$dest/system" || return 1
  cp -a "$CASEDIR/case/0"        "$dest/0"        || return 1
  cp -a "$CASEDIR/case/constant" "$dest/constant" || return 1
  cp "$CASEDIR/case/system/fvSchemes"   "$dest/system/" || return 1
  cp "$CASEDIR/case/system/fvSolution"  "$dest/system/" || return 1
  cp "$CASEDIR/case/system/topoSetDict" "$dest/system/" || return 1
  sed -e "s/__NX__/$nx/g" -e "s/__NR__/$nr/g" -e "s/__GR__/$gr/g" \
      "$CASEDIR/case/system/blockMeshDict.template" > "$dest/system/blockMeshDict" || return 1
  sed -e "s/__ENDTIME__/$endt/g" \
      "$CASEDIR/case/system/controlDict.template" > "$dest/system/controlDict" || return 1
  grep -q "__NX__\|__NR__\|__GR__\|__ENDTIME__" "$dest/system/blockMeshDict" "$dest/system/controlDict" \
    && return 1
  return 0
}

# ===========================================================================
# mesh_case <dest> <label>
#   blockMesh + checkMesh + topoSet; REFUSES if either frozen sampling zone is
#   EMPTY; writes the MESH BIRTH CERTIFICATE and REFUSES if it does not admit.
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
                         generator="blockMesh, VMFL003-M3 %s, PREREGISTRATION.md" % label,
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
# PRE-FLIGHT SMOKE -- ONE TIMESTEP, COARSEST MESH, IN A SCRATCH DIRECTORY
# OUTSIDE verification/runs.  A comparator --selftest proves the GRADER, not the
# CASE.  The smoke trees are deleted and NOTHING they produce is ever graded.
# ===========================================================================
SMOKE=$(mktemp -d "${TMPDIR:-/tmp}/vmfl003m3-smoke-XXXXXX") \
  || { echo "ABORT: cannot create a scratch directory for the smoke test"; exit 1; }
echo "  pre-flight smoke in $SMOKE (outside verification/runs)"
build_case "$SMOKE/pf" 500 25 0.0369274 1 \
  || { echo "ABORT: smoke could not materialise the case"; rm -rf "$SMOKE"; exit 1; }
mesh_case "$SMOKE/pf" "smoke" \
  || { echo "ABORT: smoke FAILED at blockMesh/checkMesh/topoSet/cert -- see $SMOKE/pf/log.*"; exit 1; }
( cd "$SMOKE/pf" && timeout 300 simpleFoam > log.simpleFoam 2>&1 ) \
  || { echo "ABORT: smoke FAILED on its first timestep -- see $SMOKE/pf/log.simpleFoam"; exit 1; }
grep -qE "^End$" "$SMOKE/pf/log.simpleFoam" \
  || { echo "ABORT: smoke produced no End line"; exit 1; }
echo "  smoke PASSED (1 iteration on the coarsest wall-resolved mesh)"
rm -rf "$SMOKE"

# ===========================================================================
# THE REAL LEVELS.  GRADED COMPUTE.  LOCKED until the supervisor unlocks it AND
# the auto-mode graded-launch block is cleared at Sanaa's desk.
# ===========================================================================
mkdir -p "$RUNROOT" || { echo "ABORT: cannot create $RUNROOT"; exit 1; }
SPENT_CORE_MIN=0
TOTAL_WALL=0

for lspec in "${LEVELS[@]}"; do
  set -- $lspec
  LEVEL="$1"; NX="$2"; NR="$3"; GR="$4"; ENDT="$5"; LCAP="$6"
  DEST="$RUNROOT/$LEVEL"

  REMAIN=$(python3 -c "print(max(0.0, min($CAP_CORE_MIN - $SPENT_CORE_MIN, $LCAP)))") \
    || { echo "ABORT: cannot compute the remaining budget"; exit 1; }
  TIMEOUT_S=$(python3 -c "print(int($REMAIN * 60 / $RANKS))") \
    || { echo "ABORT: cannot compute the timeout"; exit 1; }
  [ "$TIMEOUT_S" -gt 0 ] \
    || { echo "ABORT: BUDGET EXHAUSTED before $LEVEL (spent $SPENT_CORE_MIN of $CAP_CORE_MIN "\
"core-min).  An overrun STOPS the run; it does not get a new budget (rule 12)."; exit 1; }

  echo "--- $LEVEL  nx=$NX nr=$NR gr=$GR endTime=$ENDT  cap=${LCAP} timeout=${TIMEOUT_S}s "\
"(remaining ${REMAIN} core-min)"

  build_case "$DEST" "$NX" "$NR" "$GR" "$ENDT" \
    || { echo "ABORT: could not build $LEVEL"; exit 1; }
  mesh_case "$DEST" "$LEVEL" \
    || { echo "ABORT: $LEVEL FAILED at meshing/cert, or topoSet left a frozen "\
"sampling zone EMPTY.  See $DEST/log.*"; exit 1; }

  # AGE-GUARD DATUM (comparator clause C6): touch EVERY file in this level's own
  # 0/ as the LAST action before the solver starts.
  find "$DEST/0" -type f -exec touch {} + \
    || { echo "ABORT: could not set the age-guard datum for $LEVEL"; exit 1; }
  sleep 1

  T0=$(date +%s)
  ( cd "$DEST" && timeout "$TIMEOUT_S" simpleFoam > log.simpleFoam 2>&1 )
  RC=$?
  T1=$(date +%s)
  WALL=$((T1 - T0))
  CORE_MIN=$(python3 -c "print($WALL * $RANKS / 60.0)")
  SPENT_CORE_MIN=$(python3 -c "print($SPENT_CORE_MIN + $CORE_MIN)")
  TOTAL_WALL=$((TOTAL_WALL + WALL))

  printf 'rc=%d\nlevel=%s\nnx=%s\nnr=%s\ngr=%s\nendTime=%s\nwall_s=%d\nranks=%d\ncore_min=%s\ntimeout_s=%d\nremaining_core_min_at_launch=%s\n' \
    "$RC" "$LEVEL" "$NX" "$NR" "$GR" "$ENDT" "$WALL" "$RANKS" "$CORE_MIN" "$TIMEOUT_S" "$REMAIN" \
    > "$DEST/RUN_RC.txt" \
    || { echo "ABORT: could not write RUN_RC.txt for $LEVEL"; exit 1; }

  [ "$RC" -eq 0 ] \
    || { echo "ABORT: $LEVEL exited rc=$RC after ${WALL}s (timeout ${TIMEOUT_S}s). "\
"A non-zero rc is a FINDING, not a retry: it is triaged before anything else runs "\
"(rc=124 is timeout's budget-fired signature)."; exit 1; }
  echo "    $LEVEL done: ${WALL}s = ${CORE_MIN} core-min (spent ${SPENT_CORE_MIN}/${CAP_CORE_MIN})"
done

echo "  grading with $CMP ..."
python3 "$CASEDIR/$CMP" --runroot "$RUNROOT" --json "$RUNROOT/GRADING_VMFL003_M3.json" \
  || echo "  NOTE: comparator returned non-zero (a REFUSAL is a finding; triage before belief)"

printf 'total_wall_s=%d\nranks=%d\ntotal_core_min=%s\ncap_core_min=%s\ncost_basis=owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md section 5)\n' \
  "$TOTAL_WALL" "$RANKS" "$SPENT_CORE_MIN" "$CAP_CORE_MIN" > "$RUNROOT/COST.txt" \
  || { echo "ABORT: could not write COST.txt"; exit 1; }

echo "ALL LEVELS COMPLETE: ${TOTAL_WALL}s wall = ${SPENT_CORE_MIN} core-min of a ${CAP_CORE_MIN} core-min cap."
echo "REMINDER (rule 12): compare this actual against the PREREGISTRATION.md section 12 estimate"
echo "and land a row in docs/COST_CALIBRATION.md at process completion."
