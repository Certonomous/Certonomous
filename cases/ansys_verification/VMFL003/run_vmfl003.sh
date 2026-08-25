#!/bin/bash
# ===========================================================================
# VMFL003 -- Pressure Drop in Turbulent Flow Through a Pipe.  THE LAUNCHER.
#
# NOT FILED ANYWHERE.  Nothing this script produces leaves this box.
#
# NOTHING HERE HAS RUN.  This file is committed BEFORE the pre-registration is
# frozen and long before any solver starts.  Launch authorisation comes from
# the ansys-verification-supervisor after its own personal verification that
# PREREGISTRATION.md is committed (SUPERVISION_CHARTER.md section 3, check 4).
# No agent message is Sanaa's consent (CLAUDE.md rule 9).
#
# ---------------------------------------------------------------------------
# `set -e` IS DELIBERATELY NOT RELIED ON.  It was MEASURED not to be in force
# in this lab's agent execution context: `set -e; python3 -c "raise
# SystemExit(1)"; echo REACHED` prints REACHED.  Every single check below
# therefore gates with an explicit `|| { echo ABORT...; exit 1; }`.  A check
# that only prints is not a check.
# ---------------------------------------------------------------------------
#
# THE COST INSTRUMENT, IN ITS GENERAL FORM (CLAUDE.md rule 12).  Both formulae
# are written with RANKS in them so a future PARALLEL copy of this launcher
# inherits a correct cap instead of a silently broken one:
#
#     timeout_s      = CAP_CORE_MIN * 60 / RANKS
#     core_minutes   = wall_s * RANKS / 60
#
# A wall-clock timeout equals a core-minute cap ONLY for a serial run.  This
# run is serial (RANKS=1).  The cap is enforced against the RUNNING TOTAL, so
# the aggregate across all six meshes cannot exceed it.  AN OVERRUN STOPS THE
# RUN; IT DOES NOT GET A NEW BUDGET.
# ===========================================================================

RANKS=1
CAP_CORE_MIN=24            # frozen in PREREGISTRATION.md section 9
CASEDIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$CASEDIR/../../.." && pwd)"
RUNROOT="$REPO/verification/runs/ansys_verification/VMFL003"
PREREG="cases/ansys_verification/VMFL003/PREREGISTRATION.md"

# level  nx   nr   endTime
LEVELS=(
  "L1_250x5    250   5    6000"
  "L2_500x5    500   5    8000"
  "L3_1000x5  1000   5   12000"
  "D_500x3     500   3    8000"
  "D_500x4     500   4    8000"
  "D_500x6     500   6    8000"
)

echo "VMFL003 launcher -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- GUARD 1: the pre-registration must be COMMITTED at HEAD ---------------
git -C "$REPO" cat-file -e "HEAD:$PREREG" 2>/dev/null \
  || { echo "ABORT: $PREREG is not committed at HEAD -- the freeze is the "\
"evidence and no solver starts without it"; exit 1; }
DISK_SHA=$(git -C "$REPO" hash-object "$REPO/$PREREG") \
  || { echo "ABORT: cannot hash $PREREG"; exit 1; }
HEAD_SHA=$(git -C "$REPO" rev-parse "HEAD:$PREREG") \
  || { echo "ABORT: cannot resolve HEAD:$PREREG"; exit 1; }
[ "$DISK_SHA" = "$HEAD_SHA" ] \
  || { echo "ABORT: $PREREG on disk ($DISK_SHA) differs from HEAD ($HEAD_SHA)"; exit 1; }
echo "  freeze check OK: $PREREG == HEAD ($HEAD_SHA)"

# --- GUARD 2: the comparator must be the frozen file -----------------------
python3 "$CASEDIR/grade_vmfl003.py" --verify-frozen HEAD \
  || { echo "ABORT: the comparator on disk is not the committed grading path"; exit 1; }

# --- GUARD 3: refuse to start into ANY pre-existing level directory --------
for spec in "${LEVELS[@]}"; do
  set -- $spec
  [ -e "$RUNROOT/$1" ] \
    && { echo "ABORT: $RUNROOT/$1 already exists -- rule 4's guard refuses a "\
"case where 0/ or a time directory already exists.  A repeat is a NEW RUNG, "\
"never a re-grade in place."; exit 1; }
done
echo "  no pre-existing level directories"

# --- OpenFOAM environment --------------------------------------------------
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1 \
  || { echo "ABORT: cannot source the OpenFOAM v2606 environment"; exit 1; }
command -v simpleFoam >/dev/null \
  || { echo "ABORT: simpleFoam not on PATH after sourcing"; exit 1; }

# ===========================================================================
# build_case <dest> <nx> <nr> <endtime>
#   Materialises one level from the frozen templates.  NEVER edits a template.
# ===========================================================================
build_case() {
  local dest="$1" nx="$2" nr="$3" endt="$4"
  mkdir -p "$dest" || return 1
  cp -r "$CASEDIR/case/0" "$dest/0" || return 1
  cp -r "$CASEDIR/case/constant" "$dest/constant" || return 1
  mkdir -p "$dest/system" || return 1
  cp "$CASEDIR/case/system/fvSchemes"   "$dest/system/" || return 1
  cp "$CASEDIR/case/system/fvSolution"  "$dest/system/" || return 1
  cp "$CASEDIR/case/system/topoSetDict" "$dest/system/" || return 1
  sed -e "s/__NX__/$nx/g" -e "s/__NR__/$nr/g" \
      "$CASEDIR/case/system/blockMeshDict.template" > "$dest/system/blockMeshDict" || return 1
  sed -e "s/__ENDTIME__/$endt/g" \
      "$CASEDIR/case/system/controlDict.template" > "$dest/system/controlDict" || return 1
  grep -q "__NX__\|__NR__\|__ENDTIME__" "$dest/system/blockMeshDict" "$dest/system/controlDict" \
    && return 1
  return 0
}

# ===========================================================================
# mesh_case <dest>
#   blockMesh + checkMesh + topoSet, and REFUSES if either frozen sampling
#   zone came out EMPTY.  A gate read from an empty zone is not a measurement.
# ===========================================================================
mesh_case() {
  local dest="$1"
  ( cd "$dest" && blockMesh > log.blockMesh 2>&1 ) || return 1
  ( cd "$dest" && checkMesh > log.checkMesh 2>&1 ) || return 1
  ( cd "$dest" && topoSet   > log.topoSet   2>&1 ) || return 1
  local na nb
  na=$(grep -oE "cellZoneSet slabA now size [0-9]+" "$dest/log.topoSet" | tail -1 | grep -oE "[0-9]+$")
  nb=$(grep -oE "cellZoneSet slabB now size [0-9]+" "$dest/log.topoSet" | tail -1 | grep -oE "[0-9]+$")
  [ -n "$na" ] && [ "$na" -gt 0 ] || return 1
  [ -n "$nb" ] && [ "$nb" -gt 0 ] || return 1
  return 0
}

# ===========================================================================
# PRE-FLIGHT SMOKE TEST -- ONE TIMESTEP, COARSEST MESH, IN A SCRATCH DIRECTORY
# OUTSIDE verification/runs.
#
# WHY, and it is a measured reason, not a precaution: a comparator --selftest
# proves the GRADER, not the CASE.  This team's VMFL045 passed 45/45 selftest
# checks and still died on its first timestep on a missing fvSolution entry
# that no selftest could see.  Seconds of cost; it would have caught it in
# seconds.  The smoke tree is deleted and NOTHING it produces is ever graded.
# ===========================================================================
SMOKE=$(mktemp -d "${TMPDIR:-/tmp}/vmfl003-smoke-XXXXXX") \
  || { echo "ABORT: cannot create a scratch directory for the smoke test"; exit 1; }
echo "  pre-flight smoke test in $SMOKE (outside verification/runs)"
build_case "$SMOKE/smoke" 250 5 1 \
  || { echo "ABORT: smoke test could not materialise the case from templates"; rm -rf "$SMOKE"; exit 1; }
mesh_case "$SMOKE/smoke" \
  || { echo "ABORT: smoke test FAILED at blockMesh/checkMesh/topoSet -- see $SMOKE/smoke/log.*"; exit 1; }
( cd "$SMOKE/smoke" && timeout 300 simpleFoam > log.simpleFoam 2>&1 ) \
  || { echo "ABORT: smoke test FAILED on its first timestep.  The case setup is "\
"broken and NO level is launched.  Log: $SMOKE/smoke/log.simpleFoam"; exit 1; }
grep -qE "^End$" "$SMOKE/smoke/log.simpleFoam" \
  || { echo "ABORT: smoke test produced no End line"; exit 1; }
echo "  smoke test PASSED (1 iteration on the coarsest mesh)"
rm -rf "$SMOKE"

# ===========================================================================
# THE REAL LEVELS
# ===========================================================================
mkdir -p "$RUNROOT" || { echo "ABORT: cannot create $RUNROOT"; exit 1; }
SPENT_CORE_MIN=0
TOTAL_WALL=0

for spec in "${LEVELS[@]}"; do
  set -- $spec
  LEVEL="$1"; NX="$2"; NR="$3"; ENDT="$4"
  DEST="$RUNROOT/$LEVEL"

  REMAIN=$(python3 -c "print(max(0.0, $CAP_CORE_MIN - $SPENT_CORE_MIN))") \
    || { echo "ABORT: cannot compute the remaining budget"; exit 1; }
  # ---- THE GENERAL FORMULA: timeout_s = cap_core_min * 60 / RANKS ---------
  TIMEOUT_S=$(python3 -c "print(int($REMAIN * 60 / $RANKS))") \
    || { echo "ABORT: cannot compute the timeout"; exit 1; }
  [ "$TIMEOUT_S" -gt 0 ] \
    || { echo "ABORT: BUDGET EXHAUSTED before $LEVEL ($SPENT_CORE_MIN of "\
"$CAP_CORE_MIN core-min spent).  An overrun STOPS the run; it does not get a "\
"new budget (CLAUDE.md rule 12)."; exit 1; }

  echo "--- $LEVEL  nx=$NX nr=$NR endTime=$ENDT  timeout=${TIMEOUT_S}s "\
"(remaining budget ${REMAIN} core-min)"

  build_case "$DEST" "$NX" "$NR" "$ENDT" \
    || { echo "ABORT: could not build $LEVEL"; exit 1; }
  mesh_case "$DEST" \
    || { echo "ABORT: $LEVEL FAILED at meshing, or topoSet left a frozen "\
"sampling zone EMPTY.  See $DEST/log.topoSet"; exit 1; }

  # ---- AGE-GUARD DATUM: touch EVERY file in this level's own 0/ as the LAST
  #      action before the solver starts.  Every field at endTime must then be
  #      STRICTLY NEWER than it (comparator clause C6, stricter than rule 4).
  find "$DEST/0" -type f -exec touch {} + \
    || { echo "ABORT: could not set the age-guard datum for $LEVEL"; exit 1; }
  sleep 1

  T0=$(date +%s)
  ( cd "$DEST" && timeout "$TIMEOUT_S" simpleFoam > log.simpleFoam 2>&1 )
  RC=$?
  T1=$(date +%s)
  WALL=$((T1 - T0))
  # ---- THE GENERAL FORMULA: core_minutes = wall_s * RANKS / 60 ------------
  CORE_MIN=$(python3 -c "print($WALL * $RANKS / 60.0)")
  SPENT_CORE_MIN=$(python3 -c "print($SPENT_CORE_MIN + $CORE_MIN)")
  TOTAL_WALL=$((TOTAL_WALL + WALL))

  printf 'rc=%d\nlevel=%s\nnx=%s\nnr=%s\nendTime=%s\nwall_s=%d\nranks=%d\ncore_min=%s\ntimeout_s=%d\n' \
    "$RC" "$LEVEL" "$NX" "$NR" "$ENDT" "$WALL" "$RANKS" "$CORE_MIN" "$TIMEOUT_S" \
    > "$DEST/RUN_RC.txt" \
    || { echo "ABORT: could not write RUN_RC.txt for $LEVEL"; exit 1; }

  [ "$RC" -eq 0 ] \
    || { echo "ABORT: $LEVEL exited rc=$RC after ${WALL}s (timeout was "\
"${TIMEOUT_S}s).  A non-zero rc is a FINDING, not a retry: it is triaged "\
"before anything else runs."; exit 1; }
  echo "    $LEVEL done: ${WALL}s = ${CORE_MIN} core-min "\
"(running total ${SPENT_CORE_MIN} of ${CAP_CORE_MIN})"
done

printf 'total_wall_s=%d\nranks=%d\ntotal_core_min=%s\ncap_core_min=%s\ncost_basis=owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md section 5)\n' \
  "$TOTAL_WALL" "$RANKS" "$SPENT_CORE_MIN" "$CAP_CORE_MIN" > "$RUNROOT/COST.txt" \
  || { echo "ABORT: could not write COST.txt"; exit 1; }

echo "ALL LEVELS COMPLETE: ${TOTAL_WALL}s wall = ${SPENT_CORE_MIN} core-min "\
"of a ${CAP_CORE_MIN} core-min cap."
echo "Grade with:  python3 $CASEDIR/grade_vmfl003.py --runroot $RUNROOT "\
"--json $RUNROOT/GRADING_VMFL003.json"

# ===========================================================================
# DATED AMENDMENT 1 -- 2026-08-25, ansys-lane-opus (Opus 5), run-and-grade lane.
#
# THE ZONE-NON-EMPTY GUARD IN mesh_case() WAS REPAIRED BEFORE ANY GRADED
# COMPUTE.  Lines whose NUMBER changed above this section: 0.  Lines whose
# CONTENT changed: exactly TWO, 118 and 119, quoted in full both ways below.
#
# STRUCK (the frozen text, blob 5ed5ff81d41322d3b482ac911a6219952c57957a):
#   na=$(grep -oE "Selected [0-9]+ cell" "$dest/log.topoSet" | head -1 | grep -oE "[0-9]+")
#   nb=$(grep -oE "Selected [0-9]+ cell" "$dest/log.topoSet" | sed -n 2p | grep -oE "[0-9]+")
#
# NOW:
#   na=$(grep -oE "cellZoneSet slabA now size [0-9]+" "$dest/log.topoSet" | tail -1 | grep -oE "[0-9]+$")
#   nb=$(grep -oE "cellZoneSet slabB now size [0-9]+" "$dest/log.topoSet" | tail -1 | grep -oE "[0-9]+$")
#
# WHY -- A DEMONSTRABLE ERROR, NOT A PREFERENCE.  OpenFOAM v2606's topoSet does
# not print the string "Selected N cell" at all.  It prints "cellSet <name>
# now size N" and "cellZoneSet <name> now size N".  MEASURED on the real log of
# the pre-flight smoke test of 2026-08-25T02:15Z: `grep -c "Selected [0-9]\+
# cell"` returns 0 while the four "now size" lines are present and correct
# (slabA 26 cells, slabB 24 cells).  The frozen guard therefore could NEVER
# report success on this OpenFOAM version, on any mesh, however well populated
# the zones were.  The launcher as frozen was UNRUNNABLE, and it aborted on its
# first use at exactly this line.
#
# THE REPAIR IS ALSO A STRENGTHENING, and this is the part worth reading.  The
# frozen guard located its two counts POSITIONALLY -- `head -1` and `sed -n 2p`
# -- so even had the pattern matched, it would have been asserting "the first
# and second numbers topoSet happened to print", not "slabA and slabB".  This
# case's own PREREGISTRATION.md section 5 states the opposite rule in terms:
# "Every column is located BY HEADER NAME, NEVER BY POSITION (N-AV4/L-286)".
# That rule was applied to the comparator's readers and NOT to the launcher's
# guard -- the L-221/L-222 defect exactly: a lesson is not applied until EVERY
# call site asserts it.  The repaired guard names slabA and slabB explicitly
# and is order-independent.  " slabA now size" cannot match "slabACells".
#
# WHAT DID NOT MOVE.  No gate, threshold, band, cap, label, reference value,
# endTime, mesh, y+ target, verdict rule or cost figure is touched.  The
# comparator grade_vmfl003.py is BYTE-IDENTICAL and untouched (blob
# 15b14d40f166cc31770ead452c27905332670c97).  The guard's SEMANTICS are
# unchanged and fail-closed in both directions: refuse unless both frozen zones
# are present and non-empty.  Both refusal arms were exercised on the real log
# before this commit -- a zone forced to size 0 is refused, a zone whose line is
# deleted is refused.
#
# THE CONDITION, CHECKED AND NOT ASSERTED (CLAUDE.md rule 2; VERIFICATION
# _CHARTER.md section 2b.1).  At 2026-08-25T02:15Z,
# verification/runs/ansys_verification/VMFL003/ DID NOT EXIST -- `ls -d`
# returned "No such file or directory" -- because the launcher aborted at the
# smoke test, which precedes `mkdir -p "$RUNROOT"`.  NO simpleFoam HAS
# EXECUTED ANYWHERE FOR THIS CASE: the smoke tree held only `0/` and three mesh
# logs, and `find /tmp/vmfl003-smoke-* -name log.simpleFoam` returned 0 files.
# NO VALUE OF THE GATE QUANTITY, OR OF ANY QUANTITY, EXISTED WHEN THIS REPAIR
# WAS MADE.  This is BEFORE first compute in the only sense rule 2 protects.
#
# AGAINST VERIFICATION_CHARTER.md section 2d.1's four conditions, which govern
# the strictly harder case of a repair AFTER a graded solve, all four hold a
# fortiori: (1) a demonstrable error -- the pattern matches zero lines of real
# output; (2) established by an instrument INDEPENDENT OF THE HYPOTHESIS -- the
# pre-flight smoke test, which grades nothing, produces no gate quantity and
# cannot know which direction a verdict would want; (3) disclosed here, naming
# that instrument and quantifying what moved; (4) pre-repair values recorded --
# there are none, because nothing had been graded.
#
# THE SMOKE TEST EARNED ITS KEEP ON ITS FIRST USE, which is the second finding.
# It was written into this launcher because VMFL045 passed 45/45 comparator
# selftest checks and still died on its first timestep.  Here the comparator's
# own --selftest passed 60 checks with 0 failures and could not have seen this:
# the defect was in the LAUNCHER, on a code path no selftest of the GRADER
# reaches.  It cost seconds, in /tmp, with no level directory created and no
# budget consumed.
# ===========================================================================
