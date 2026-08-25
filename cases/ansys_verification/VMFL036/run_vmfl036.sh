#!/usr/bin/env bash
# ===========================================================================
# run_vmfl036.sh -- VMFL036, Laminar Flow Past Sphere (manual p.125-126).
#
#   ./run_vmfl036.sh --smoke                              pre-flight only, in scratch
#   ./run_vmfl036.sh --prereg-sha <sha> --arm A           the GATE arm  (nu = 0.01)
#   ./run_vmfl036.sh --prereg-sha <sha> --arm B           the DIAGNOSTIC (nu = 0.02)
#   ./run_vmfl036.sh --prereg-sha <sha> --arm A --level L2_64x96
#
# --- WHY THERE IS NO `set -u` (PREREG_TEMPLATE Amendment 3, item 3) ---------
# `set -u` is CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606: sourcing
# etc/bashrc dereferences WM_PROJECT_DIR before assigning it, and the shell dies
# with rc 127 before a single line of this launcher's own logic runs.  Both
# previous template-speed cases (VMFL059, VMFL010) died exactly there.  It is
# omitted DELIBERATELY and this comment is the record of why.
#
# --- WHY EVERY CHECK GATES EXPLICITLY --------------------------------------
# `set -e` does NOT gate at a Bash tool's top level, is suppressed for any
# non-final && member, and the `( set -e; ... )` subshell workaround FAILS
# SILENTLY.  EVERY assertion below therefore carries its own
#     || { echo ABORT...; exit 1; }
# and nothing in this file relies on `set -e` to stop anything.
# ===========================================================================

CASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$CASE_DIR" rev-parse --show-toplevel 2>/dev/null)" \
    || { echo "ABORT: not inside a git repository"; exit 1; }
[ -n "$REPO" ] || { echo "ABORT: empty repo root"; exit 1; }
SELF_REL="cases/ansys_verification/VMFL036/run_vmfl036.sh"
[ "$(cd "$REPO" && readlink -f "$SELF_REL")" = "$(readlink -f "${BASH_SOURCE[0]}")" ] \
    || { echo "ABORT: this file is not $SELF_REL inside $REPO"; exit 1; }

SRC="$CASE_DIR/case"
GRADER="$CASE_DIR/grade_vmfl036.py"
PREREG_REL="cases/ansys_verification/VMFL036/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL036/grade_vmfl036.py"
PMESH_REL="cases/ansys_verification/VMFL036/polymesh_area.py"
RUN_ROOT="$REPO/verification/runs/ansys_verification/VMFL036"
OF_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
SCRATCH="/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad"

# ---- FROZEN PARAMETERS.  These MUST match grade_vmfl036.py exactly. --------
ENDTIME=10000
K_STRETCH=400.0
LEVELS=("L1_32x48 32 48" "L2_64x96 64 96" "L3_128x192 128 192")
RANKS=1                       # serial; the cap formula carries RANKS explicitly
# THE COST CAP, in core-minutes, PER INVOCATION i.e. PER ARM (CLAUDE.md rule 12).
# An overrun STOPS the run; it does not get a new budget.
CAP_CORE_MIN=120
# The viscosity each arm consumes.  ASSERTED at launch, never assumed.
NU_ARM_A="0.01"               # Re = 100 -- the manual's REFERENCE
NU_ARM_B="0.02"               # Re =  50 -- the manual's STATED viscosity

PREREG_SHA=""
ARM=""
ONLY_LEVEL=""
SMOKE_ONLY=0
while [ $# -gt 0 ]; do
    case "$1" in
        --prereg-sha) PREREG_SHA="$2"; shift 2 ;;
        --arm)        ARM="$2"; shift 2 ;;
        --level)      ONLY_LEVEL="$2"; shift 2 ;;
        --smoke)      SMOKE_ONLY=1; shift ;;
        *) echo "ABORT: unknown argument $1"; exit 1 ;;
    esac
done

# ===========================================================================
# 1.  THE FREEZE MUST BE NAMED AND MUST BE REAL (rule 2; Amendment 2 + 3 item 1).
#     The pre-registration AND the comparator on disk must BE the blobs committed
#     at the named commit.  A launcher that does not re-prove the freeze at launch
#     can run against a document that has drifted -- an unverified freeze is no
#     freeze.
# ===========================================================================
if [ "$SMOKE_ONLY" -eq 0 ]; then
    [ -n "$PREREG_SHA" ] \
        || { echo "ABORT: --prereg-sha is mandatory.  No solver starts without"
             echo "       naming the committed freeze (CLAUDE.md rule 2)."; exit 1; }
    case "$ARM" in A|B) ;; *) echo "ABORT: --arm must be A or B"; exit 1 ;; esac

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

    FREEZE_PMESH="$(git -C "$REPO" rev-parse "${PREREG_SHA}:${PMESH_REL}" 2>/dev/null)" \
        || { echo "ABORT: commit $PREREG_SHA does not carry $PMESH_REL"; exit 1; }
    DISK_PMESH="$(git -C "$REPO" hash-object "$REPO/$PMESH_REL" 2>/dev/null)" \
        || { echo "ABORT: cannot hash $PMESH_REL on disk"; exit 1; }
    [ "$FREEZE_PMESH" = "$DISK_PMESH" ] \
        || { echo "ABORT: the MESH READER on disk is NOT the frozen blob."
             echo "       frozen=$FREEZE_PMESH  disk=$DISK_PMESH"; exit 1; }

    python3 "$GRADER" --verify-frozen "$PREREG_SHA" \
        || { echo "ABORT: the comparator's own freeze check failed"; exit 1; }
    python3 "$GRADER" --selftest > "$CASE_DIR/.selftest_${ARM}.log" 2>&1 \
        || { echo "ABORT: comparator --selftest failed; see .selftest_${ARM}.log"
             exit 1; }
    echo "freeze     : $PREREG_SHA"
    echo "  prereg   : $FREEZE_PREREG  (disk == frozen)"
    echo "  grader   : $FREEZE_GRADER  (disk == frozen)"
    echo "  meshread : $FREEZE_PMESH  (disk == frozen)"
    echo "  selftest : GREEN (planted-zero + Roache-classifier + reader controls)"
fi

# ===========================================================================
# 2.  OPENFOAM.
# ===========================================================================
[ -f "$OF_BASHRC" ] || { echo "ABORT: no OpenFOAM at $OF_BASHRC"; exit 1; }
# shellcheck disable=SC1090
. "$OF_BASHRC" > /dev/null 2>&1
command -v simpleFoam > /dev/null \
    || { echo "ABORT: simpleFoam not on PATH after sourcing $OF_BASHRC"; exit 1; }
command -v blockMesh > /dev/null \
    || { echo "ABORT: blockMesh not on PATH"; exit 1; }

# ===========================================================================
# 3.  THE CASE ASSERTS -- asserts, never comments (L-221/L-222).
# ===========================================================================
grep -q '^simulationType[[:space:]]\+laminar;' "$SRC/constant/turbulenceProperties" \
    || { echo "ABORT: constant/turbulenceProperties does not select laminar --"
         echo "       the manual states 'Flow is laminar and steady' (p.126)"; exit 1; }
[ -e "$SRC/constant/momentumTransport" ] \
    && { echo "ABORT: a stray constant/momentumTransport is present; OpenFOAM v2606"
         echo "       reads turbulenceProperties and the two would disagree"; exit 1; }
grep -q 'rhoInf[[:space:]]\+1;' "$SRC/system/controlDict.template" \
    || { echo "ABORT: the forces function object does not set rhoInf 1 (manual p.125"
         echo "       states density 1 kg/m3) -- Cd's numerator would be wrong"; exit 1; }
grep -q 'patches[[:space:]]*([[:space:]]*sphere[[:space:]]*)' "$SRC/system/controlDict.template" \
    || { echo "ABORT: the forces function object does not integrate over 'sphere'"; exit 1; }
# A SELECTION, not a mention: this dictionary's own comment names
# residualControl in order to record that it is deliberately absent, and a bare
# grep flags that warning as if it were the fault (the VMFL007 trap).  Comments
# are stripped FIRST, and only then is a setting line looked for.
sed 's://.*::' "$SRC/system/fvSolution" | grep -q 'residualControl' \
    && { echo "ABORT: fvSolution sets residualControl.  An early SIMPLE exit makes"
         echo "       rule 4's 'last time == endTime' and 'ExecutionTime count =="
         echo "       endTime' clauses FALSE, and this case declares NO departure"
         echo "       from rule 4."; exit 1; }
echo "  assert   laminar; rhoInf 1; forces on 'sphere'; NO residualControl"

# ===========================================================================
# 4.  THE COST CAP, ENFORCED IN THE EXECUTABLE PATH (Amendment 3, item 2).
#     Running core-minute accounting draws ONE budget down across the levels of
#     this invocation and REFUSES at zero.  RANKS appears in BOTH formulae so a
#     parallel copy of this launcher inherits a correct cap:
#         core_minutes = wall_s * RANKS / 60
#         timeout_s    = remaining_core_min * 60 / RANKS
# ===========================================================================
SPENT_CORE_MIN=0
BUDGET_FILE="$(mktemp "${SCRATCH}/vmfl036_budget_XXXXXX")" \
    || { echo "ABORT: cannot create the budget accounting file"; exit 1; }
echo "0" > "$BUDGET_FILE"

remaining_core_min () {
    python3 -c "print('%.6f' % ($CAP_CORE_MIN - $(cat "$BUDGET_FILE")))"
}
timeout_for_next () {
    python3 -c "
rem = $CAP_CORE_MIN - $(cat "$BUDGET_FILE")
t = rem * 60.0 / $RANKS
print(int(t) if t > 0 else 0)"
}
spend () {   # $1 = wall seconds
    python3 -c "
cur = $(cat "$BUDGET_FILE")
print('%.6f' % (cur + $1 * $RANKS / 60.0))" > "${BUDGET_FILE}.new" \
        || { echo "ABORT: cost accounting failed"; exit 1; }
    mv "${BUDGET_FILE}.new" "$BUDGET_FILE" \
        || { echo "ABORT: cannot update the budget file"; exit 1; }
}

# ===========================================================================
# 5.  ONE LEVEL.  THE SAME CODE PATH IS USED BY THE SMOKE TEST AND BY THE
#     GRADED RUNS (Amendment 3, item 6: the smoke must exercise THE LAUNCHER,
#     not the solver in a bypass environment).
#     $1 dir  $2 NT  $3 NR  $4 nu  $5 endTime  $6 mode(smoke|graded)
# ===========================================================================
run_level () {
    local D="$1" NT="$2" NR="$3" NU="$4" ET="$5" MODE="$6"
    local RGRAD WALL T0 T1 RC CORE_MIN TMO

    # THE RULE-4 GUARD: refuse a case whose 0/ or time directories already exist.
    # A re-run goes to a NEW directory; nothing is ever overwritten.
    [ -e "$D" ] && { echo "ABORT: $D already exists -- the rule-4 guard refuses a"
                     echo "       case whose 0/ or time directories are already there."
                     echo "       A re-run is a NEW directory citing the old one."
                     return 1; }
    mkdir -p "$D" || { echo "ABORT: cannot create $D"; return 1; }
    cp -r "$SRC"/. "$D"/ || { echo "ABORT: case copy failed for $D"; return 1; }

    # The radial expansion ratio for THIS level, from the FROZEN stretching map
    # r(xi) = r_in + L*(K^xi - 1)/(K - 1).  R(N) = K^((N-1)/N).  Holding K fixed
    # (not R) is what makes every L2 node at even index coincide EXACTLY with an
    # L1 node, so h halves EXACTLY and the triple's r is 2 BY CONSTRUCTION.
    RGRAD="$(python3 -c "print('%.12g' % ($K_STRETCH ** (($NR - 1.0) / $NR)))")" \
        || { echo "ABORT: cannot compute the radial grading for NR=$NR"; return 1; }

    sed -e "s/__NT__/$NT/" -e "s/__NR__/$NR/" -e "s/__RGRAD__/$RGRAD/" \
        "$D/system/blockMeshDict.template" > "$D/system/blockMeshDict" \
        || { echo "ABORT: blockMeshDict substitution failed"; return 1; }
    sed -e "s/__ENDTIME__/$ET/" \
        "$D/system/controlDict.template" > "$D/system/controlDict" \
        || { echo "ABORT: controlDict substitution failed"; return 1; }
    sed -e "s/__NU__/$NU/" \
        "$D/constant/transportProperties.template" > "$D/constant/transportProperties" \
        || { echo "ABORT: transportProperties substitution failed"; return 1; }
    grep -q '__NT__\|__NR__\|__RGRAD__\|__ENDTIME__\|__NU__' \
        "$D/system/blockMeshDict" "$D/system/controlDict" \
        "$D/constant/transportProperties" \
        && { echo "ABORT: an unsubstituted placeholder survived in $D"; return 1; }
    # The viscosity actually on disk is ASSERTED, not assumed from having sed'd it.
    grep -q "^nu[[:space:]]\+${NU};" "$D/constant/transportProperties" \
        || { echo "ABORT: $D/constant/transportProperties does not carry nu $NU"
             return 1; }

    ( cd "$D" && blockMesh > log.blockMesh 2>&1 ) \
        || { echo "ABORT: blockMesh failed for $D -- a finding, not a retry"; return 1; }
    ( cd "$D" && checkMesh > log.checkMesh 2>&1 )
    grep -q "^Mesh OK" "$D/log.checkMesh" \
        || { echo "ABORT: checkMesh did not report Mesh OK for $D"; return 1; }

    # THE MESH BIRTH CERTIFICATE (MESH_STANDARD sec.6; Amendment 3 item 5), read
    # off constant/polyMesh by the FROZEN pure-python reader -- never from the
    # solver, never from a function object.
    python3 "$CASE_DIR/polymesh_area.py" "$D/constant/polyMesh" \
        > "$D/MESH_BIRTH_CERTIFICATE.txt" 2>&1 \
        || { echo "ABORT: the mesh birth certificate could not be read for $D"
             return 1; }
    grep -q "^sphere " "$D/MESH_BIRTH_CERTIFICATE.txt" \
        || { echo "ABORT: the birth certificate has no sphere patch for $D"; return 1; }
    grep -qE "^axis .*area=0 " "$D/MESH_BIRTH_CERTIFICATE.txt" \
        || { echo "ABORT: the axis patch of $D does not have EXACTLY zero area --"
             echo "       the wedge axis did not collapse"; return 1; }

    # THE AGE MARKER (rule 4).  0/p is touched LAST, immediately before the
    # solver, so it dates the run that was allowed to produce the answer.
    touch "$D/0/U" "$D/0/p" || { echo "ABORT: cannot touch the age marker"; return 1; }
    sleep 1

    TMO="$(timeout_for_next)"
    [ "$TMO" -gt 0 ] 2>/dev/null \
        || { echo "ABORT: the ${CAP_CORE_MIN} core-min budget for this invocation is"
             echo "       EXHAUSTED before $D started.  Rule 12: an overrun STOPS the"
             echo "       run; it does not get a new budget."; return 1; }

    T0=$(date +%s)
    ( cd "$D" && timeout "$TMO" simpleFoam > log.simpleFoam 2>&1 )
    RC=$?
    T1=$(date +%s)
    WALL=$((T1 - T0))
    spend "$WALL" || return 1
    CORE_MIN="$(python3 -c "print('%.4f' % ($WALL * $RANKS / 60.0))")"
    {
        echo "rc = $RC"
        echo "dir = $D"
        echo "mode = $MODE"
        echo "arm = $ARM"
        echo "nu = $NU"
        echo "NT = $NT"
        echo "NR = $NR"
        echo "cells = $((2 * NT * NR))"
        echo "rgrad = $RGRAD"
        echo "endTime = $ET"
        echo "wall_s = $WALL"
        echo "ranks = $RANKS"
        echo "core_min = $CORE_MIN"
        echo "timeout_s_granted = $TMO"
        echo "cap_core_min = $CAP_CORE_MIN"
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
        || { echo "ABORT: simpleFoam rc = $RC for $D (a crash is a FINDING until"
             echo "       triage says otherwise)"; return 1; }
    grep -q "^End$" "$D/log.simpleFoam" \
        || { echo "ABORT: no 'End' line in $D/log.simpleFoam"; return 1; }
    echo "  ran      $(basename "$D")  ${WALL}s  ${CORE_MIN} core-min  "\
"(remaining $(remaining_core_min) of $CAP_CORE_MIN)"
    return 0
}

# ===========================================================================
# 6.  THE PRE-FLIGHT SMOKE TEST -- IT EXERCISES THIS LAUNCHER'S OWN run_level,
#     in a scratch directory OUTSIDE verification/runs/, so it cannot create a 0/
#     or a time directory that would trip the age guard or consume the run the
#     guard protects.  IT PRINTS NO Cd: the gate channel is opened with
#     --dryrun-reader, which prints structure and NO VALUE, so the smoke cannot
#     leak an answer before the freeze.  A FAILURE ABORTS.  IT IS NOT A RETRY.
# ===========================================================================
smoke () {
    local S; S="$(mktemp -d "${SCRATCH}/vmfl036_smoke_XXXXXX")" \
        || { echo "ABORT: cannot make a scratch smoke directory"; return 1; }
    rmdir "$S" || { echo "ABORT: cannot clear the smoke directory"; return 1; }
    run_level "$S" 8 12 "$NU_ARM_A" 5 smoke \
        || { echo "ABORT: SMOKE -- run_level failed ($S)"; return 1; }
    python3 "$GRADER" --dryrun-reader "$S/postProcessing/forces/0/force.dat" \
        || { echo "ABORT: SMOKE -- the gate-channel reader refused ($S)"; return 1; }
    grep -q "^Mesh OK" "$S/log.checkMesh" \
        || { echo "ABORT: SMOKE -- checkMesh not OK ($S)"; return 1; }
    grep -q "^rc = 0" "$S/RUN_RC.txt" \
        || { echo "ABORT: SMOKE -- RUN_RC.txt does not record rc 0 ($S)"; return 1; }
    grep -q "^timeout_s_granted = " "$S/RUN_RC.txt" \
        || { echo "ABORT: SMOKE -- the cap was not enforced in the executable path"
             return 1; }
    echo "  smoke    PASS -- the LAUNCHER's own run_level ran end to end (192 cells,"
    echo "           5 iterations, cap arithmetic exercised, birth certificate"
    echo "           written, gate-channel reader opened WITHOUT printing a value)"
    echo "           $S"
    return 0
}

if [ "$SMOKE_ONLY" -eq 1 ]; then
    smoke || { echo "ABORT: the pre-flight smoke test failed"; exit 1; }
    exit 0
fi
smoke || { echo "ABORT: the pre-flight smoke test failed"; exit 1; }
# The smoke's spend is REFUNDED: it is machinery, not the graded run, and it must
# not eat the graded run's budget.  Stated here so the accounting is honest.
echo "0" > "$BUDGET_FILE"

# ===========================================================================
# 7.  THE GRADED RUNS.
# ===========================================================================
case "$ARM" in
    A) NU="$NU_ARM_A" ;;
    B) NU="$NU_ARM_B" ;;
esac
mkdir -p "$RUN_ROOT/$ARM" || { echo "ABORT: cannot create $RUN_ROOT/$ARM"; exit 1; }

{
    echo "VMFL036 ARM $ARM LAUNCH RECORD"
    echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "prereg_sha = $PREREG_SHA"
    echo "prereg_blob = $FREEZE_PREREG"
    echo "grader_blob = $FREEZE_GRADER"
    echo "meshreader_blob = $FREEZE_PMESH"
    echo "head_at_launch = $(git -C "$REPO" rev-parse HEAD)"
    echo "nu = $NU"
    echo "endTime = $ENDTIME"
    echo "cap_core_min = $CAP_CORE_MIN"
    echo "ranks = $RANKS"
    echo "openfoam = $OF_BASHRC"
} > "$RUN_ROOT/$ARM/LAUNCH_RECORD.txt" \
    || { echo "ABORT: cannot write the launch record"; exit 1; }

for SPEC in "${LEVELS[@]}"; do
    set -- $SPEC; NAME="$1"; NT="$2"; NR="$3"
    if [ -n "$ONLY_LEVEL" ] && [ "$ONLY_LEVEL" != "$NAME" ]; then continue; fi
    run_level "$RUN_ROOT/$ARM/$NAME" "$NT" "$NR" "$NU" "$ENDTIME" graded \
        || { echo "ABORT: arm $ARM level $NAME did not complete"; exit 1; }
done

echo "arm $ARM complete.  spent $(cat "$BUDGET_FILE") core-min of $CAP_CORE_MIN."
echo "grade with:  python3 $GRADER --arm $ARM"
