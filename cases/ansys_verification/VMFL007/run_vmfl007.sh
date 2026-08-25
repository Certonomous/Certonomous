#!/usr/bin/env bash
# ===========================================================================
# run_vmfl007.sh -- VMFL007, Non-Newtonian Flow in a Pipe (manual p. 29).
#
# THE LAUNCHER DOES NOT LAUNCH UNTIL THE FREEZE IS NAMED.  Usage:
#     ./run_vmfl007.sh --prereg-sha <sha>            all three levels
#     ./run_vmfl007.sh --prereg-sha <sha> --level L1_25x25
#     ./run_vmfl007.sh --smoke                       pre-flight only, in /tmp
#
# `set -e` DOES NOT GATE reliably here: it is inert at a Bash tool's top level,
# it is suppressed for any command that is a NON-FINAL && MEMBER, and the
# `( set -e; ... )` subshell workaround FAILS SILENTLY.  So EVERY assertion in
# this file is gated EXPLICITLY with  || { echo ABORT...; exit 1; }  and nothing
# relies on `set -e` to stop anything.
# ===========================================================================

CASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$CASE_DIR" rev-parse --show-toplevel 2>/dev/null)" \
    || { echo "ABORT: not inside a git repository"; exit 1; }
[ -n "$REPO" ] || { echo "ABORT: empty repo root"; exit 1; }
SELF_REL="cases/ansys_verification/VMFL007/run_vmfl007.sh"
[ "$(cd "$REPO" && readlink -f "$SELF_REL")" = "$(readlink -f "${BASH_SOURCE[0]}")" ] \
    || { echo "ABORT: this file is not $SELF_REL inside $REPO"; exit 1; }

SRC="$CASE_DIR/case"
GRADER="$CASE_DIR/grade_vmfl007.py"
RUN_ROOT="$REPO/verification/runs/ansys_verification/VMFL007"
OF_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

# ---- FROZEN PARAMETERS.  These must match grade_vmfl007.py exactly. --------
ENDTIME=10000
WRITEINTERVAL=5000
LEVELS=("L1_25x25 25 25" "L2_50x50 50 50" "L3_100x100 100 100")
# THE COST CAP, in core-minutes (CLAUDE.md rule 12).  AN OVERRUN STOPS THE RUN;
# it does not get a new budget.  Serial, so core-min = wall_s * 1 / 60.
CAP_CORE_MIN=60
CAP_WALL_S=3600           # 60 core-min at 1 rank
# The coefficients this run intends to consume.  ASSERTED, never assumed.
K_OF_EXPECT="0.01"        # KINEMATIC = manual k (10, DYNAMIC) / rho (1000)
N_EXPECT="0.4"
RHO_EXPECT="1000"

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
# 1.  THE FREEZE MUST BE NAMED AND MUST BE REAL (CLAUDE.md rule 2).
# ===========================================================================
if [ "$SMOKE_ONLY" -eq 0 ]; then
    [ -n "$PREREG_SHA" ] \
        || { echo "ABORT: --prereg-sha is mandatory. No solver starts without naming"
             echo "       the committed freeze (CLAUDE.md rule 2)."; exit 1; }
    git -C "$REPO" cat-file -e "${PREREG_SHA}^{commit}" 2>/dev/null \
        || { echo "ABORT: $PREREG_SHA is not a commit in this repository"; exit 1; }
    git -C "$REPO" cat-file -e "${PREREG_SHA}:cases/ansys_verification/VMFL007/PREREGISTRATION.md" 2>/dev/null \
        || { echo "ABORT: commit $PREREG_SHA does not carry PREREGISTRATION.md"; exit 1; }
    # THE GRADING PATH IS FIXED AT THE PRE-REGISTRATION COMMIT.  The comparator
    # on disk must BE the blob committed there.
    python3 "$GRADER" --verify-frozen "$PREREG_SHA" \
        || { echo "ABORT: the comparator on disk is NOT the frozen blob at $PREREG_SHA"; exit 1; }
    python3 "$GRADER" --selftest > "$CASE_DIR/.selftest.log" 2>&1 \
        || { echo "ABORT: comparator --selftest failed; see .selftest.log"; exit 1; }
    echo "freeze     : $PREREG_SHA"
    echo "comparator : verified against the frozen blob; selftest clean"
fi

# ===========================================================================
# 2.  OPENFOAM, AND THE RUNTIME-COMPILATION SWITCH.
#     0/U's inlet is a codedFixedValue, so on-the-fly compilation must be on.
#     CLAUDE.md rule 14's discipline: this is ASSERTED after the run, from the
#     log, not assumed from having exported it.
# ===========================================================================
[ -f "$OF_BASHRC" ] || { echo "ABORT: no OpenFOAM at $OF_BASHRC"; exit 1; }
# shellcheck disable=SC1090
. "$OF_BASHRC" > /dev/null 2>&1
command -v simpleFoam > /dev/null \
    || { echo "ABORT: simpleFoam not on PATH after sourcing $OF_BASHRC"; exit 1; }
export FOAM_ALLOW_SYSTEM_OPERATIONS=1

# ===========================================================================
# 3.  THE COEFFICIENT ASSERT -- an ASSERT, never a comment (L-221/L-222).
#     There are TWO selectable OpenFOAM classes named `powerLaw` with DIFFERENT
#     dictionary keys, and which one is instantiated is decided SILENTLY by the
#     turbulence/laminar model:
#       A  viscosityModels::powerLaw          keys k, n, nuMin, nuMax   <- WANTED
#       B  laminarModels::generalizedNewtonian
#          ViscosityModels::powerLaw          keys n, nuMin, nuMax -- NO `k`;
#          it multiplies nu0 from the transport model instead.
#     A case written for A and run under B does NOT fail: `k` is simply ignored
#     and the viscosity is wrong by k/nu0.  Seeded from a Newtonian 1e-05 that
#     factor is EXACTLY 1000, and dp reads ~3819 Pa instead of ~60522 Pa.
# ===========================================================================
assert_dict () {
    local f="$1" key="$2" want="$3"
    local got
    got="$(grep -oP "^\s*${key}\s+\K[-+0-9.eE]+" "$f" | head -1)"
    [ -n "$got" ] || { echo "ABORT: key '$key' absent from $f"; exit 1; }
    python3 -c "import sys; sys.exit(0 if abs(float('$got')-float('$want'))<1e-15 else 1)" \
        || { echo "ABORT: $f has $key = $got, expected $want"; exit 1; }
    echo "  assert  $key = $got  in $(basename "$f")"
}
TP="$SRC/constant/transportProperties"
grep -q '^transportModel[[:space:]]\+powerLaw;' "$TP" \
    || { echo "ABORT: $TP does not select transportModel powerLaw"; exit 1; }
assert_dict "$TP" "k"     "$K_OF_EXPECT"
assert_dict "$TP" "n"     "$N_EXPECT"
assert_dict "$TP" "nuMin" "1e-08"
assert_dict "$TP" "nuMax" "1.0"
# and the OTHER class must not be selectable: the laminar model must be Stokes.
grep -q 'model[[:space:]]\+Stokes;' "$SRC/constant/turbulenceProperties" \
    || { echo "ABORT: turbulenceProperties does not set laminar { model Stokes; }"; exit 1; }
# The test is for a SELECTION, not a mention: this dictionary's own comment
# names generalizedNewtonian in order to warn about it, and a bare `grep -q` on
# the word flags the warning as if it were the fault.  Comments are stripped
# first, and only then is a selecting line looked for.
sed 's://.*::' "$SRC/constant/turbulenceProperties" \
    | grep -qE '(model|generalizedNewtonianModel)[[:space:]]+generalizedNewtonian' \
    && { echo "ABORT: turbulenceProperties SELECTS generalizedNewtonian -- that is"
         echo "       the OTHER powerLaw class, which has no k key and takes nu0"
         echo "       from the transport model instead"; exit 1; }
echo "  assert  laminar model is Stokes; generalizedNewtonian not selected"

# ===========================================================================
# 4.  THE PRE-FLIGHT SMOKE TEST (charter v1.4 Clause B).
#     ONE iteration on the COARSEST mesh, in a scratch directory OUTSIDE
#     verification/runs/ -- so it cannot create a 0/ or a time directory that
#     would trip the age guard or consume the run the guard protects.
#     A FAILURE ABORTS.  IT IS NOT A RETRY.
# ===========================================================================
smoke () {
    local S; S="$(mktemp -d /tmp/claude-1000/vmfl007_smoke_XXXXXX)" \
        || { echo "ABORT: cannot make a scratch smoke directory"; exit 1; }
    cp -r "$SRC"/. "$S"/ || { echo "ABORT: smoke copy failed"; exit 1; }
    sed -e "s/__NX__/25/" -e "s/__NR__/25/" \
        "$S/system/blockMeshDict.template" > "$S/system/blockMeshDict" \
        || { echo "ABORT: smoke blockMeshDict substitution failed"; exit 1; }
    sed -e "s/__ENDTIME__/1/" -e "s/__WRITEINTERVAL__/1/" \
        "$S/system/controlDict.template" > "$S/system/controlDict" \
        || { echo "ABORT: smoke controlDict substitution failed"; exit 1; }
    ( cd "$S" && blockMesh > log.blockMesh 2>&1 ) \
        || { echo "ABORT: SMOKE blockMesh failed -- a finding, not a retry ($S)"; exit 1; }
    ( cd "$S" && checkMesh > log.checkMesh 2>&1 )
    grep -q "^Mesh OK" "$S/log.checkMesh" \
        || { echo "ABORT: SMOKE checkMesh did not report Mesh OK ($S)"; exit 1; }
    ( cd "$S" && simpleFoam > log.simpleFoam 2>&1 ) \
        || { echo "ABORT: SMOKE simpleFoam failed on iteration 1 -- a finding ($S)"; exit 1; }
    grep -q "Selecting incompressible transport model powerLaw" "$S/log.simpleFoam" \
        || { echo "ABORT: SMOKE did not instantiate viscosityModels::powerLaw ($S)"; exit 1; }
    grep -q "Selecting laminar stress model Stokes" "$S/log.simpleFoam" \
        || { echo "ABORT: SMOKE did not instantiate the Stokes laminar model ($S)"; exit 1; }
    grep -q "generalizedNewtonian" "$S/log.simpleFoam" \
        && { echo "ABORT: SMOKE log mentions generalizedNewtonian -- WRONG powerLaw class ($S)"; exit 1; }
    for f in pInlet pOutlet QInlet UmaxInlet nuMinAll nuMaxAll; do
        ls "$S/postProcessing/$f"/*/*.dat > /dev/null 2>&1 \
            || { echo "ABORT: SMOKE wrote no monitor for $f ($S)"; exit 1; }
    done
    # STRUCTURE ONLY.  The gate channel is read with --dryrun-reader, which
    # prints NO value, so the smoke test cannot leak the answer before the freeze.
    python3 "$GRADER" --dryrun-reader "$S/postProcessing/pInlet/0/surfaceFieldValue.dat" \
        || { echo "ABORT: SMOKE gate-channel reader refused ($S)"; exit 1; }
    echo "  smoke   PASS (1 iteration, 625 cells, $S)"
    # The directory is handed back through a FILE, never through stdout.
    # `SMOKE_DIR="$(smoke)"` would run this function in a SUBSHELL, where every
    # `exit 1` above kills only the subshell and the script sails on with an
    # empty SMOKE_DIR -- the same silent-non-gating class as `( set -e; ... )`.
    printf '%s' "$S" > "$SMOKE_DIR_FILE" \
        || { echo "ABORT: cannot record the smoke directory"; exit 1; }
    return 0
}

SMOKE_DIR_FILE="$(mktemp /tmp/claude-1000/vmfl007_smokedir_XXXXXX)" \
    || { echo "ABORT: cannot make the smoke-directory handoff file"; exit 1; }

if [ "$SMOKE_ONLY" -eq 1 ]; then smoke; exit 0; fi
smoke || { echo "ABORT: the pre-flight smoke test failed"; exit 1; }
SMOKE_DIR="$(cat "$SMOKE_DIR_FILE")"
[ -n "$SMOKE_DIR" ] && [ -d "$SMOKE_DIR" ] \
    || { echo "ABORT: the smoke test did not report a directory -- it did not run"; exit 1; }

# ===========================================================================
# 5.  THE GRADED RUNS.
# ===========================================================================
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
TOTAL_WALL=0

for SPEC in "${LEVELS[@]}"; do
    set -- $SPEC; NAME="$1"; NX="$2"; NR="$3"
    if [ -n "$ONLY_LEVEL" ] && [ "$ONLY_LEVEL" != "$NAME" ]; then continue; fi
    D="$RUN_ROOT/$NAME"

    # THE GUARD (CLAUDE.md rule 4): refuse a case where 0/ or a time directory
    # already exists.  A re-run goes to a NEW directory; nothing is overwritten.
    [ -e "$D" ] && { echo "ABORT: $D already exists -- the age guard refuses a"
                     echo "       case whose 0/ or time directories are already there."
                     echo "       A re-run is a NEW directory citing the old one."; exit 1; }

    mkdir -p "$D" || { echo "ABORT: cannot create $D"; exit 1; }
    cp -r "$SRC"/. "$D"/ || { echo "ABORT: case copy failed for $NAME"; exit 1; }
    sed -e "s/__NX__/$NX/" -e "s/__NR__/$NR/" \
        "$D/system/blockMeshDict.template" > "$D/system/blockMeshDict" \
        || { echo "ABORT: blockMeshDict substitution failed for $NAME"; exit 1; }
    sed -e "s/__ENDTIME__/$ENDTIME/" -e "s/__WRITEINTERVAL__/$WRITEINTERVAL/" \
        "$D/system/controlDict.template" > "$D/system/controlDict" \
        || { echo "ABORT: controlDict substitution failed for $NAME"; exit 1; }
    grep -q '__NX__\|__NR__\|__ENDTIME__\|__WRITEINTERVAL__' \
        "$D/system/blockMeshDict" "$D/system/controlDict" \
        && { echo "ABORT: an unsubstituted placeholder survived in $NAME"; exit 1; }

    ( cd "$D" && blockMesh > log.blockMesh 2>&1 ) \
        || { echo "ABORT: blockMesh failed for $NAME"; exit 1; }
    ( cd "$D" && checkMesh > log.checkMesh 2>&1 )
    grep -q "^Mesh OK" "$D/log.checkMesh" \
        || { echo "ABORT: checkMesh did not report Mesh OK for $NAME"; exit 1; }

    # THE AGE MARKER.  0/U is touched LAST, immediately before the solver, so it
    # dates the run that was allowed to produce the answer.  Every field written
    # at endTime must be NEWER than it; grade_vmfl007.py clause C6 checks that.
    touch "$D/0/U" || { echo "ABORT: cannot touch the age marker for $NAME"; exit 1; }
    sleep 1

    T0=$(date +%s)
    ( cd "$D" && timeout "$CAP_WALL_S" simpleFoam > log.simpleFoam 2>&1 )
    RC=$?
    T1=$(date +%s)
    WALL=$((T1 - T0))
    TOTAL_WALL=$((TOTAL_WALL + WALL))
    CORE_MIN=$(python3 -c "print('%.4f' % ($WALL*1/60.0))")
    {
        echo "rc = $RC"
        echo "level = $NAME"
        echo "cells = $((NX*NR))"
        echo "endTime = $ENDTIME"
        echo "wall_s = $WALL"
        echo "ranks = 1"
        echo "core_min = $CORE_MIN"
        echo "prereg_sha = $PREREG_SHA"
        echo "finished_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } > "$D/RUN_RC.txt"

    if [ "$RC" -eq 124 ]; then
        echo "ABORT: $NAME EXCEEDED the ${CAP_WALL_S}s (${CAP_CORE_MIN} core-min) cap."
        echo "       CLAUDE.md rule 12: an overrun STOPS the run. It does not get"
        echo "       a new budget. Recorded in $D/RUN_RC.txt."
        exit 1
    fi
    [ "$RC" -eq 0 ] || { echo "ABORT: simpleFoam rc = $RC for $NAME (a crash is a"
                         echo "       finding until triage says otherwise)"; exit 1; }
    echo "  ran     $NAME  ${WALL}s  ${CORE_MIN} core-min"
done

TOTAL_CORE_MIN=$(python3 -c "print('%.4f' % ($TOTAL_WALL*1/60.0))")
{
    echo "total_wall_s = $TOTAL_WALL"
    echo "total_core_min = $TOTAL_CORE_MIN"
    echo "cap_core_min = $CAP_CORE_MIN"
    echo "ranks = 1 (serial, sequential)"
    echo "rate_basis = c7a.4xlarge \$0.0513/core-h, OWNER-STATED not measured"
    echo "prereg_sha = $PREREG_SHA"
    echo "smoke_dir = $SMOKE_DIR (scratch, OUTSIDE the runs tree)"
} > "$RUN_ROOT/COST.txt"
python3 -c "
cm=float('$TOTAL_CORE_MIN'); cap=float('$CAP_CORE_MIN')
print('total   %.4f core-min against a cap of %.0f (%.1f %%)' % (cm,cap,100*cm/cap))
print('derived \$%.5f at \$0.0513/core-h -- DERIVED, not measured' % (cm/60*0.0513))
"
echo "cost record: $RUN_ROOT/COST.txt"
echo "now grade:   python3 $GRADER"
