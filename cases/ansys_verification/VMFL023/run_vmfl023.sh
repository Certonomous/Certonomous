#!/usr/bin/env bash
# ===========================================================================
# run_vmfl023.sh -- VMFL023, Oscillating Laminar Flow Around a Circular
# Cylinder (manual p.89).
#
#   ./run_vmfl023.sh --smoke                                pre-flight only
#   ./run_vmfl023.sh --prereg-sha <sha>                     all three levels
#   ./run_vmfl023.sh --prereg-sha <sha> --level L2_192x64   one level
#
# --- WHY THERE IS NO `set -u` (PREREG_TEMPLATE Amendment 3, item 3) ---------
# `set -u` is CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606: sourcing
# etc/bashrc dereferences WM_PROJECT_DIR before assigning it and the shell dies
# with rc 127 before any of this launcher's logic runs.  Omitted DELIBERATELY.
#
# --- WHY EVERY CHECK GATES EXPLICITLY --------------------------------------
# `set -e` does NOT gate at a Bash tool's top level, is suppressed for any
# non-final && member, and `( set -e; ... )` FAILS SILENTLY.  Every assertion
# carries its own || { echo ABORT...; exit 1; }.
# ===========================================================================

CASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$CASE_DIR" rev-parse --show-toplevel 2>/dev/null)" \
    || { echo "ABORT: not inside a git repository"; exit 1; }
[ -n "$REPO" ] || { echo "ABORT: empty repo root"; exit 1; }
SELF_REL="cases/ansys_verification/VMFL023/run_vmfl023.sh"
[ "$(cd "$REPO" && readlink -f "$SELF_REL")" = "$(readlink -f "${BASH_SOURCE[0]}")" ] \
    || { echo "ABORT: this file is not $SELF_REL inside $REPO"; exit 1; }

SRC="$CASE_DIR/case"
GRADER="$CASE_DIR/grade_vmfl023.py"
PREREG_REL="cases/ansys_verification/VMFL023/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL023/grade_vmfl023.py"
RUN_ROOT="$REPO/verification/runs/ansys_verification/VMFL023"
OF_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
SCRATCH="/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad"

# ---- FROZEN PARAMETERS.  These MUST match grade_vmfl023.py exactly. --------
ENDTIME=300
DELTAT=0.005
K_STRETCH=200.0
RANKS=1
# name  NT_per_block  NR  CAP_core_min
LEVELS=("L1_96x32 24 32 20" "L2_192x64 48 64 70" "L3_384x128 96 128 260")
NU_EXPECT="0.02"              # manual p.89; Re = 1*1*2/0.02 = 100 -- CONSISTENT

PREREG_SHA=""
ONLY_LEVEL=""
SMOKE_ONLY=0
while [ $# -gt 0 ]; do
    case "$1" in
        --prereg-sha) PREREG_SHA="$2"; shift 2 ;;
        --level)      ONLY_LEVEL="$2"; shift 2 ;;
        --smoke)      SMOKE_ONLY=1; shift ;;
        *) echo "ABORT: unknown argument $1"; exit 1 ;;
    esac
done

# ===========================================================================
# 1.  THE FREEZE MUST BE NAMED AND MUST BE REAL (rule 2; Amendments 2 + 3).
# ===========================================================================
if [ "$SMOKE_ONLY" -eq 0 ]; then
    [ -n "$PREREG_SHA" ] \
        || { echo "ABORT: --prereg-sha is mandatory.  No solver starts without"
             echo "       naming the committed freeze (CLAUDE.md rule 2)."; exit 1; }
    git -C "$REPO" cat-file -e "${PREREG_SHA}^{commit}" 2>/dev/null \
        || { echo "ABORT: $PREREG_SHA is not a commit in this repository"; exit 1; }
    FREEZE_PREREG="$(git -C "$REPO" rev-parse "${PREREG_SHA}:${PREREG_REL}" 2>/dev/null)" \
        || { echo "ABORT: commit $PREREG_SHA does not carry $PREREG_REL"; exit 1; }
    DISK_PREREG="$(git -C "$REPO" hash-object "$REPO/$PREREG_REL" 2>/dev/null)" \
        || { echo "ABORT: cannot hash $PREREG_REL on disk"; exit 1; }
    [ "$FREEZE_PREREG" = "$DISK_PREREG" ] \
        || { echo "ABORT: the PRE-REGISTRATION on disk is NOT the frozen blob."
             echo "       frozen=$FREEZE_PREREG  disk=$DISK_PREREG"; exit 1; }
    FREEZE_GRADER="$(git -C "$REPO" rev-parse "${PREREG_SHA}:${GRADER_REL}" 2>/dev/null)" \
        || { echo "ABORT: commit $PREREG_SHA does not carry $GRADER_REL"; exit 1; }
    DISK_GRADER="$(git -C "$REPO" hash-object "$REPO/$GRADER_REL" 2>/dev/null)" \
        || { echo "ABORT: cannot hash $GRADER_REL on disk"; exit 1; }
    [ "$FREEZE_GRADER" = "$DISK_GRADER" ] \
        || { echo "ABORT: the COMPARATOR on disk is NOT the frozen blob."
             echo "       frozen=$FREEZE_GRADER  disk=$DISK_GRADER"; exit 1; }
    python3 "$GRADER" --verify-frozen "$PREREG_SHA" \
        || { echo "ABORT: the comparator's own freeze check failed"; exit 1; }
    python3 "$GRADER" --selftest > "$CASE_DIR/.selftest.log" 2>&1 \
        || { echo "ABORT: comparator --selftest failed; see .selftest.log"; exit 1; }
    echo "freeze     : $PREREG_SHA"
    echo "  prereg   : $FREEZE_PREREG  (disk == frozen)"
    echo "  grader   : $FREEZE_GRADER  (disk == frozen)"
    echo "  selftest : GREEN (planted-frequency + flat-signal + Roache + reference)"
fi

# ===========================================================================
# 2.  OPENFOAM.
# ===========================================================================
[ -f "$OF_BASHRC" ] || { echo "ABORT: no OpenFOAM at $OF_BASHRC"; exit 1; }
# shellcheck disable=SC1090
. "$OF_BASHRC" > /dev/null 2>&1
command -v pimpleFoam > /dev/null \
    || { echo "ABORT: pimpleFoam not on PATH after sourcing $OF_BASHRC"; exit 1; }
command -v blockMesh > /dev/null || { echo "ABORT: blockMesh not on PATH"; exit 1; }

# ===========================================================================
# 3.  THE CASE ASSERTS -- asserts, never comments (L-221/L-222).
#     THE REYNOLDS ASSERT IS THE VMFL036 LESSON MADE EXECUTABLE: the viscosity
#     the solver will actually consume must be the one that reproduces the Re the
#     manual's page states.  A mis-specified gate quantity dies HERE, at launch.
# ===========================================================================
grep -q '^simulationType[[:space:]]\+laminar;' "$SRC/constant/turbulenceProperties" \
    || { echo "ABORT: turbulenceProperties does not select laminar"; exit 1; }
NU_ON_DISK="$(grep -oP '^nu\s+\K[-+0-9.eE]+' "$SRC/constant/transportProperties" | head -1)"
[ -n "$NU_ON_DISK" ] || { echo "ABORT: no nu in constant/transportProperties"; exit 1; }
python3 -c "
import sys
nu = float('$NU_ON_DISK')
if abs(nu - float('$NU_EXPECT')) > 1e-15: sys.exit(1)
re = 1.0 * 1.0 * 2.0 / nu
sys.exit(0 if abs(re - 100.0) < 1e-9 else 2)" \
    || { echo "ABORT: nu on disk is $NU_ON_DISK, which does not give the Re = 100"
         echo "       the manual's page states from rho=1, U=1, D=2.  THIS IS THE"
         echo "       VMFL036 FAILURE CLASS AND IT STOPS THE RUN."; exit 1; }
echo "  assert   nu = $NU_ON_DISK -> Re = rho*U*D/nu = 100, the Re the page states"
sed 's://.*::' "$SRC/system/controlDict.template" | grep -q 'adjustTimeStep[[:space:]]\+yes' \
    && { echo "ABORT: adjustTimeStep is on.  A Courant-adjusted step puts a"
         echo "       DIFFERENT time discretisation on each grid level and the"
         echo "       Roache triple would measure two refinements at once."; exit 1; }
grep -q 'rhoInf[[:space:]]\+1;' "$SRC/system/controlDict.template" \
    || { echo "ABORT: the forces function object does not set rhoInf 1"; exit 1; }
grep -q 'patches[[:space:]]*([[:space:]]*cylinder[[:space:]]*)' "$SRC/system/controlDict.template" \
    || { echo "ABORT: the forces function object does not integrate over 'cylinder'"; exit 1; }
grep -q 'internalField[[:space:]]\+uniform[[:space:]]*([[:space:]]*1[[:space:]]\+0.2[[:space:]]\+0[[:space:]]*)' "$SRC/0/U" \
    || { echo "ABORT: 0/U does not carry the frozen symmetry-breaking kick"
         echo "       (1 0.2 0).  Without it a symmetric mesh may never shed and"
         echo "       the levels would not share one start-up."; exit 1; }
echo "  assert   adjustTimeStep off; rhoInf 1; forces on 'cylinder'; kick (1 0.2 0)"

# ===========================================================================
# 4.  THE COST CAP, ENFORCED IN THE EXECUTABLE PATH (Amendment 3, item 2).
#     PER LEVEL **AND** IN TOTAL.  One budget -- the sum of the caps of the
#     levels this invocation will run -- is drawn down across them, and the
#     grant for each level is the SMALLER of what remains in total and that
#     level's own cap.  RANKS is in BOTH formulae so a parallel copy inherits a
#     correct cap:
#         core_minutes = wall_s * RANKS / 60
#         timeout_s    = min(remaining_total, level_cap) * 60 / RANKS
# ===========================================================================
TOTAL_CAP=0
for SPEC in "${LEVELS[@]}"; do
    set -- $SPEC
    if [ -z "$ONLY_LEVEL" ] || [ "$ONLY_LEVEL" = "$1" ]; then
        TOTAL_CAP=$(python3 -c "print('%g' % ($TOTAL_CAP + $4))")
    fi
done
python3 -c "import sys; sys.exit(0 if $TOTAL_CAP > 0 else 1)" \
    || { echo "ABORT: no level selected, so the budget is zero"; exit 1; }
BUDGET_FILE="$(mktemp "${SCRATCH}/vmfl023_budget_XXXXXX")" \
    || { echo "ABORT: cannot create the budget accounting file"; exit 1; }
echo "0" > "$BUDGET_FILE"

timeout_for_next () {   # $1 = this level's own cap
    python3 -c "
rem = $TOTAL_CAP - $(cat "$BUDGET_FILE")
grant = min(rem, $1)
t = grant * 60.0 / $RANKS
print(int(t) if t > 0 else 0)"
}
spend () {
    python3 -c "print('%.6f' % ($(cat "$BUDGET_FILE") + $1 * $RANKS / 60.0))" \
        > "${BUDGET_FILE}.new" || { echo "ABORT: cost accounting failed"; return 1; }
    mv "${BUDGET_FILE}.new" "$BUDGET_FILE" \
        || { echo "ABORT: cannot update the budget file"; return 1; }
}

# ===========================================================================
# 5.  ONE LEVEL.  THE SAME CODE PATH IS USED BY THE SMOKE TEST AND BY THE
#     GRADED RUNS (Amendment 3 item 6).
#     $1 dir  $2 NT  $3 NR  $4 levelcap  $5 endTime  $6 mode
# ===========================================================================
run_level () {
    local D="$1" NT="$2" NR="$3" LCAP="$4" ET="$5" MODE="$6"
    local RGRAD WALL T0 T1 RC CORE_MIN TMO NSTEPS

    [ -e "$D" ] && { echo "ABORT: $D already exists -- the rule-4 guard refuses a"
                     echo "       case whose 0/ or time directories are already there."
                     return 1; }
    mkdir -p "$D" || { echo "ABORT: cannot create $D"; return 1; }
    cp -r "$SRC"/. "$D"/ || { echo "ABORT: case copy failed for $D"; return 1; }

    RGRAD="$(python3 -c "print('%.12g' % ($K_STRETCH ** (($NR - 1.0) / $NR)))")" \
        || { echo "ABORT: cannot compute the radial grading for NR=$NR"; return 1; }
    sed -e "s/__NT__/$NT/" -e "s/__NR__/$NR/" -e "s/__RGRAD__/$RGRAD/" \
        "$D/system/blockMeshDict.template" > "$D/system/blockMeshDict" \
        || { echo "ABORT: blockMeshDict substitution failed"; return 1; }
    sed -e "s/__ENDTIME__/$ET/" -e "s/__DELTAT__/$DELTAT/" \
        "$D/system/controlDict.template" > "$D/system/controlDict" \
        || { echo "ABORT: controlDict substitution failed"; return 1; }
    grep -q '__NT__\|__NR__\|__RGRAD__\|__ENDTIME__\|__DELTAT__' \
        "$D/system/blockMeshDict" "$D/system/controlDict" \
        && { echo "ABORT: an unsubstituted placeholder survived in $D"; return 1; }

    ( cd "$D" && blockMesh > log.blockMesh 2>&1 ) \
        || { echo "ABORT: blockMesh failed for $D -- a finding, not a retry"; return 1; }
    ( cd "$D" && checkMesh > log.checkMesh 2>&1 )
    grep -q "^Mesh OK" "$D/log.checkMesh" \
        || { echo "ABORT: checkMesh did not report Mesh OK for $D"; return 1; }

    # THE MESH BIRTH CERTIFICATE (MESH_STANDARD sec.6; Amendment 3 item 5).
    # The cylinder patch's WETTED area is compared against the analytic
    # pi*D*thickness, read from checkMesh/blockMesh output, not from the solver.
    {
        echo "# VMFL023 mesh birth certificate for $(basename "$D")"
        echo "NT_per_block = $NT"
        echo "NR = $NR"
        echo "cells_expected = $((4 * NT * NR))"
        grep -E "nCells|nPoints|nFaces" "$D/log.blockMesh"
        grep -E "^  patch [0-9]" "$D/log.blockMesh"
        grep -E "Overall domain bounding box|Max cell openness|Max aspect ratio|"\
"Mesh non-orthogonality Max|Max skewness" "$D/log.checkMesh"
    } > "$D/MESH_BIRTH_CERTIFICATE.txt" 2>&1
    grep -q "nCells: $((4 * NT * NR))" "$D/MESH_BIRTH_CERTIFICATE.txt" \
        || { echo "ABORT: $D has a cell count that is not 4*NT*NR = $((4*NT*NR))"
             return 1; }

    touch "$D/0/U" "$D/0/p" || { echo "ABORT: cannot touch the age marker"; return 1; }
    sleep 1

    TMO="$(timeout_for_next "$LCAP")"
    [ "$TMO" -gt 0 ] 2>/dev/null \
        || { echo "ABORT: the ${TOTAL_CAP} core-min budget is EXHAUSTED before $D"
             echo "       started.  Rule 12: an overrun STOPS the run."; return 1; }

    T0=$(date +%s)
    ( cd "$D" && timeout "$TMO" pimpleFoam > log.pimpleFoam 2>&1 )
    RC=$?
    T1=$(date +%s)
    WALL=$((T1 - T0))
    spend "$WALL" || return 1
    CORE_MIN="$(python3 -c "print('%.4f' % ($WALL * $RANKS / 60.0))")"
    NSTEPS="$(python3 -c "print(int(round($ET / $DELTAT)))")"
    {
        echo "rc = $RC"
        echo "dir = $D"
        echo "mode = $MODE"
        echo "NT = $NT"
        echo "NR = $NR"
        echo "cells = $((4 * NT * NR))"
        echo "rgrad = $RGRAD"
        echo "endTime = $ET"
        echo "deltaT = $DELTAT"
        echo "steps_expected = $NSTEPS"
        echo "wall_s = $WALL"
        echo "ranks = $RANKS"
        echo "core_min = $CORE_MIN"
        echo "timeout_s_granted = $TMO"
        echo "level_cap_core_min = $LCAP"
        echo "total_cap_core_min = $TOTAL_CAP"
        echo "spent_core_min_after = $(cat "$BUDGET_FILE")"
        echo "prereg_sha = $PREREG_SHA"
        echo "finished_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } > "$D/RUN_RC.txt"

    if [ "$RC" -eq 124 ]; then
        echo "ABORT: $D hit the ${TMO}s timeout granted from the remaining budget."
        echo "       CLAUDE.md rule 12: an overrun STOPS the run.  Recorded in"
        echo "       $D/RUN_RC.txt."
        return 1
    fi
    [ "$RC" -eq 0 ] \
        || { echo "ABORT: pimpleFoam rc = $RC for $D (a crash is a FINDING until"
             echo "       triage says otherwise)"; return 1; }
    grep -q "^End$" "$D/log.pimpleFoam" \
        || { echo "ABORT: no 'End' line in $D/log.pimpleFoam"; return 1; }
    echo "  ran      $(basename "$D")  ${WALL}s  ${CORE_MIN} core-min"
    return 0
}

# ===========================================================================
# 6.  THE PRE-FLIGHT SMOKE TEST -- IT EXERCISES THIS LAUNCHER'S OWN run_level,
#     in scratch, OUTSIDE verification/runs/.  IT PRINTS NO St.
# ===========================================================================
smoke () {
    local S; S="$(mktemp -d "${SCRATCH}/vmfl023_smoke_XXXXXX")" \
        || { echo "ABORT: cannot make a scratch smoke directory"; return 1; }
    rmdir "$S" || { echo "ABORT: cannot clear the smoke directory"; return 1; }
    run_level "$S" 8 8 5 0.05 smoke \
        || { echo "ABORT: SMOKE -- run_level failed ($S)"; return 1; }
    python3 "$GRADER" --dryrun-reader "$S/postProcessing/forces/0/force.dat" \
        || { echo "ABORT: SMOKE -- the gate-channel reader refused ($S)"; return 1; }
    grep -q "^rc = 0" "$S/RUN_RC.txt" \
        || { echo "ABORT: SMOKE -- RUN_RC.txt does not record rc 0 ($S)"; return 1; }
    grep -q "^timeout_s_granted = " "$S/RUN_RC.txt" \
        || { echo "ABORT: SMOKE -- the cap was not enforced in the executable path"
             return 1; }
    echo "  smoke    PASS -- the LAUNCHER's own run_level ran end to end (256 cells,"
    echo "           10 steps, cap arithmetic exercised, birth certificate written,"
    echo "           gate-channel reader opened WITHOUT printing a value)"
    echo "           $S"
    return 0
}

if [ "$SMOKE_ONLY" -eq 1 ]; then
    smoke || { echo "ABORT: the pre-flight smoke test failed"; exit 1; }
    exit 0
fi
smoke || { echo "ABORT: the pre-flight smoke test failed"; exit 1; }
# The smoke's spend is REFUNDED: it is machinery, not the graded run.
echo "0" > "$BUDGET_FILE"

# ===========================================================================
# 7.  THE GRADED RUNS.
# ===========================================================================
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
{
    echo "VMFL023 LAUNCH RECORD"
    echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "prereg_sha = $PREREG_SHA"
    echo "prereg_blob = $FREEZE_PREREG"
    echo "grader_blob = $FREEZE_GRADER"
    echo "head_at_launch = $(git -C "$REPO" rev-parse HEAD)"
    echo "nu = $NU_ON_DISK"
    echo "Re = 100 (derived from the manual's own rho=1 U=1 D=2)"
    echo "endTime = $ENDTIME"
    echo "deltaT = $DELTAT"
    echo "total_cap_core_min = $TOTAL_CAP"
    echo "ranks = $RANKS"
    echo "levels_selected = ${ONLY_LEVEL:-ALL}"
    echo "openfoam = $OF_BASHRC"
} >> "$RUN_ROOT/LAUNCH_RECORD.txt" \
    || { echo "ABORT: cannot write the launch record"; exit 1; }

for SPEC in "${LEVELS[@]}"; do
    set -- $SPEC; NAME="$1"; NT="$2"; NR="$3"; LCAP="$4"
    if [ -n "$ONLY_LEVEL" ] && [ "$ONLY_LEVEL" != "$NAME" ]; then continue; fi
    run_level "$RUN_ROOT/$NAME" "$NT" "$NR" "$LCAP" "$ENDTIME" graded \
        || { echo "ABORT: level $NAME did not complete"; exit 1; }
done

echo "complete.  spent $(cat "$BUDGET_FILE") core-min of $TOTAL_CAP."
echo "grade with:  python3 $GRADER"
