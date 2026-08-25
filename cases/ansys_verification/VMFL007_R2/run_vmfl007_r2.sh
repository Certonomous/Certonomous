#!/usr/bin/env bash
# ===========================================================================
# run_vmfl007_r2.sh -- VMFL007-R2, THE LINEAR-SOLVER / PRECONDITIONER SLATE.
#
#   ./run_vmfl007_r2.sh --prereg-sha <sha>     run the WHOLE slate, in order
#   ./run_vmfl007_r2.sh --smoke                pre-flight only, in /tmp scratch
#
# THE SLATE IS RUN IN FULL, IN A FIXED ORDER, WHATEVER ANY ARM RETURNS.
# There is deliberately NO `--arm` flag and NO way to stop early on a result:
# an arm that diverges, stalls or dies is RECORDED and the slate CONTINUES to
# the next arm.  A slate truncated after seeing a number is answer-directed
# selection, and this launcher makes that impossible rather than merely
# discouraging it.
#
# The ONLY thing that aborts the whole slate is a SETUP failure -- a freeze not
# named, a comparator that is not the frozen blob, a case input that is not the
# frozen blob, a failed smoke test, or the slate cost cap.  A RESULT never aborts.
#
# `set -e` DOES NOT GATE reliably: it is inert at a Bash tool's top level, it is
# suppressed for any command that is a NON-FINAL && MEMBER, and the
# `( set -e; ... )` subshell workaround FAILS SILENTLY.  EVERY assertion below is
# gated EXPLICITLY with  || { echo ABORT...; exit 1; }  and nothing relies on it.
# ===========================================================================

CASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$CASE_DIR" rev-parse --show-toplevel 2>/dev/null)" \
    || { echo "ABORT: not inside a git repository"; exit 1; }
[ -n "$REPO" ] || { echo "ABORT: empty repo root"; exit 1; }
SELF_REL="cases/ansys_verification/VMFL007_R2/run_vmfl007_r2.sh"
[ "$(cd "$REPO" && readlink -f "$SELF_REL")" = "$(readlink -f "${BASH_SOURCE[0]}")" ] \
    || { echo "ABORT: this file is not $SELF_REL inside $REPO"; exit 1; }

SRC="$CASE_DIR/case"
ARMS="$CASE_DIR/arms"
GRADER="$CASE_DIR/grade_vmfl007_r2.py"
RUN_ROOT="$REPO/verification/runs/ansys_verification/VMFL007_R2"
OF_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

# ---- FROZEN PARAMETERS.  These must match grade_vmfl007_r2.py exactly. -----
# EVERYTHING HERE IS IDENTICAL TO RUN 1 EXCEPT THE ARM'S fvSolution.
ENDTIME=10000
WRITEINTERVAL=5000
NX=25
NR=25
LEVEL="L1_25x25"          # SINGLE GRID by design; R2 seeks no credential.

# THE SLATE, IN ITS FROZEN ORDER.  Name and registered fvSolution blob.
SLATE_NAMES=(A1_GAMG_GaussSeidel A2_GAMG_DICGaussSeidel A3_PCG_DIC \
             A4_PCG_GAMGprecon A5_PBiCGStab_DIC A6_smoothSolver_symGaussSeidel)
SLATE_BLOBS=(70953b4ea8d71a0b4744b1df695ceac9e24fa820 \
             406f192f5dfcae6ded499f9c38e534270aaf2a70 \
             595dcc973b98d6740df7914a7b584fa127fba3c6 \
             753bc4221ab84841085bd0bf5974398ff2ceae0a \
             3bfff09c46bc2034c7b120a265f20a8708c60e8b \
             38a7c29aacb33dff23ab5c118718783b2ecc2a82)

# THE COST CAPS (CLAUDE.md rule 12).  Serial: core-min = wall_s / 60.
CAP_ARM_CORE_MIN=20        # per arm; an overrun STOPS THAT ARM
CAP_ARM_WALL_S=1200
CAP_SLATE_CORE_MIN=90      # hard stop for the whole slate
CAP_SLATE_WALL_S=5400

# The coefficients this run intends to consume.  ASSERTED, never assumed.
K_OF_EXPECT="0.01"
N_EXPECT="0.4"

# The frozen NON-fvSolution inputs.  Asserted so that "the linear solver and
# NOTHING ELSE changed between arms" is a MACHINE-CHECKED fact and not a claim.
FROZEN_PATHS=(0/U 0/p constant/transportProperties constant/turbulenceProperties \
              system/blockMeshDict.template system/controlDict.template system/fvSchemes)
FROZEN_BLOBS=(b626d65ada23d57c62337f1a26e411c1bdc3cd16 \
              54562f8cbc730c083492ac97d21c9d7c214414a3 \
              db848a12eb939d1ac0ad81bedea135f536926f38 \
              f68f346789696b45b8d245b57ef06e1fc0aaad55 \
              9ea967ebeedf20eb9428c7785abf966eadbf01a3 \
              fe8524ab1fb2abe1c440b3685c65cb16202e8f65 \
              ad718abf3cdc834b17478c2c391affeba1dbf2b2)

PREREG_SHA=""
SMOKE_ONLY=0
while [ $# -gt 0 ]; do
    case "$1" in
        --prereg-sha) PREREG_SHA="$2"; shift 2 ;;
        --smoke)      SMOKE_ONLY=1; shift ;;
        *) echo "ABORT: unknown argument $1 (there is deliberately no --arm flag:"
           echo "       the slate is run in FULL or not at all)"; exit 1 ;;
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
    git -C "$REPO" cat-file -e "${PREREG_SHA}:cases/ansys_verification/VMFL007_R2/PREREGISTRATION.md" 2>/dev/null \
        || { echo "ABORT: commit $PREREG_SHA does not carry the R2 PREREGISTRATION.md"; exit 1; }
    python3 "$GRADER" --verify-frozen "$PREREG_SHA" \
        || { echo "ABORT: the comparator on disk is NOT the frozen blob at $PREREG_SHA"; exit 1; }
    python3 "$GRADER" --selftest > "$CASE_DIR/.selftest.log" 2>&1 \
        || { echo "ABORT: comparator --selftest failed; see .selftest.log"; exit 1; }
    echo "freeze     : $PREREG_SHA"
    echo "comparator : verified against the frozen blob; selftest clean"
fi

# ===========================================================================
# 2.  THE "NOTHING ELSE CHANGED" ASSERT.
#     Every non-fvSolution input must be the blob frozen for VMFL007 run 1.
#     This is the guard that makes the registered variable the ONLY variable.
# ===========================================================================
for i in "${!FROZEN_PATHS[@]}"; do
    P="$SRC/${FROZEN_PATHS[$i]}"
    [ -f "$P" ] || { echo "ABORT: missing frozen input ${FROZEN_PATHS[$i]}"; exit 1; }
    G="$(git -C "$REPO" hash-object "$P")"
    [ "$G" = "${FROZEN_BLOBS[$i]}" ] \
        || { echo "ABORT: ${FROZEN_PATHS[$i]} is blob $G, not run 1's frozen"
             echo "       ${FROZEN_BLOBS[$i]}. Anything but the linear solver"
             echo "       changing between run 1 and R2 is a CONFOUND."; exit 1; }
done
echo "  assert  all 7 non-fvSolution inputs ARE run 1's frozen blobs"
[ -f "$SRC/system/fvSolution" ] \
    && { echo "ABORT: case/system/fvSolution exists. It must NOT: the arm supplies"
         echo "       it, so no arm can silently inherit a stale one."; exit 1; }
for i in "${!SLATE_NAMES[@]}"; do
    A="$ARMS/${SLATE_NAMES[$i]}.fvSolution"
    [ -f "$A" ] || { echo "ABORT: missing arm file ${SLATE_NAMES[$i]}"; exit 1; }
    G="$(git -C "$REPO" hash-object "$A")"
    [ "$G" = "${SLATE_BLOBS[$i]}" ] \
        || { echo "ABORT: arm ${SLATE_NAMES[$i]} is blob $G, registered ${SLATE_BLOBS[$i]}"; exit 1; }
    # AND EVERY ARM MUST DIFFER FROM THE A1 CONTROL ONLY IN THE `p` ENTRY.
    # Brace-matched, because A4's entry spans three lines; a line-wise grep
    # filter would have to know that in advance and would quietly pass an arm
    # whose U solver or relaxation factors had also moved.
    python3 - "$ARMS/${SLATE_NAMES[0]}.fvSolution" "$A" "${SLATE_NAMES[$i]}" <<'PYEOF' \
        || exit 1
import sys
def strip_p_entry(path):
    out, depth, inp = [], 0, False
    for ln in open(path):
        s = ln.strip()
        if not inp and s.startswith('p ') and '{' in s:
            inp = True
            depth = s.count('{') - s.count('}')
            if depth <= 0:
                inp = False
            continue
        if inp:
            depth += s.count('{') - s.count('}')
            if depth <= 0:
                inp = False
            continue
        out.append(ln)
    return out
a, b, name = sys.argv[1], sys.argv[2], sys.argv[3]
ra, rb = strip_p_entry(a), strip_p_entry(b)
if ra != rb:
    print("ABORT: arm %s differs from the A1 control OUTSIDE the p entry." % name)
    for i, (x, y) in enumerate(zip(ra, rb)):
        if x != y:
            print("       line %d: control %r vs arm %r" % (i + 1, x.rstrip(), y.rstrip()))
    print("       Only the linear solver may vary across the slate.")
    sys.exit(1)
if len(ra) < 5:
    print("ABORT: arm %s -- the p-entry stripper removed too much (%d lines left);"
          " it is not doing what it claims." % (name, len(ra)))
    sys.exit(1)
PYEOF
done
echo "  assert  all 6 arms are the registered blobs and differ ONLY in the p entry"

# ===========================================================================
# 3.  OPENFOAM.
# ===========================================================================
[ -f "$OF_BASHRC" ] || { echo "ABORT: no OpenFOAM at $OF_BASHRC"; exit 1; }
# shellcheck disable=SC1090
. "$OF_BASHRC" > /dev/null 2>&1
command -v simpleFoam > /dev/null \
    || { echo "ABORT: simpleFoam not on PATH after sourcing $OF_BASHRC"; exit 1; }
export FOAM_ALLOW_SYSTEM_OPERATIONS=1

# ===========================================================================
# 4.  THE COEFFICIENT ASSERT -- an ASSERT, never a comment (L-221/L-222).
#     Two selectable OpenFOAM classes are named `powerLaw` and the wrong one
#     does NOT fail: it ignores `k` and reads nu0 instead, giving dp ~3819 Pa
#     against ~60522 Pa.  Carried verbatim from run 1's launcher.
# ===========================================================================
assert_dict () {
    local f="$1" key="$2" want="$3" got
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
grep -q 'model[[:space:]]\+Stokes;' "$SRC/constant/turbulenceProperties" \
    || { echo "ABORT: turbulenceProperties does not set laminar { model Stokes; }"; exit 1; }
sed 's://.*::' "$SRC/constant/turbulenceProperties" \
    | grep -qE '(model|generalizedNewtonianModel)[[:space:]]+generalizedNewtonian' \
    && { echo "ABORT: turbulenceProperties SELECTS generalizedNewtonian -- the OTHER"
         echo "       powerLaw class, which has no k key"; exit 1; }
echo "  assert  laminar model is Stokes; generalizedNewtonian not selected"

# ===========================================================================
# 5.  THE PRE-FLIGHT SMOKE TEST (charter v1.4 Clause B).
#     ONE iteration PER ARM on the coarsest (and only) mesh, in scratch OUTSIDE
#     verification/runs/, so it cannot create a 0/ or a time directory that
#     would trip the age guard or consume the run the guard protects.
#     A FAILURE ABORTS.  IT IS NOT A RETRY.
# ===========================================================================
smoke () {
    local S; S="$(mktemp -d /tmp/claude-1000/vmfl007r2_smoke_XXXXXX)" \
        || { echo "ABORT: cannot make a scratch smoke directory"; exit 1; }
    local i A D RC
    for i in "${!SLATE_NAMES[@]}"; do
        A="${SLATE_NAMES[$i]}"; D="$S/$A"
        mkdir -p "$D" || { echo "ABORT: smoke mkdir $A"; exit 1; }
        cp -r "$SRC"/. "$D"/ || { echo "ABORT: smoke copy $A"; exit 1; }
        cp "$ARMS/$A.fvSolution" "$D/system/fvSolution" \
            || { echo "ABORT: smoke arm install $A"; exit 1; }
        sed -e "s/__NX__/$NX/" -e "s/__NR__/$NR/" \
            "$D/system/blockMeshDict.template" > "$D/system/blockMeshDict" \
            || { echo "ABORT: smoke blockMeshDict $A"; exit 1; }
        sed -e "s/__ENDTIME__/1/" -e "s/__WRITEINTERVAL__/1/" \
            "$D/system/controlDict.template" > "$D/system/controlDict" \
            || { echo "ABORT: smoke controlDict $A"; exit 1; }
        ( cd "$D" && blockMesh > log.blockMesh 2>&1 ) \
            || { echo "ABORT: SMOKE blockMesh failed for $A -- a finding, not a retry ($D)"; exit 1; }
        ( cd "$D" && checkMesh > log.checkMesh 2>&1 )
        grep -q "^Mesh OK" "$D/log.checkMesh" \
            || { echo "ABORT: SMOKE checkMesh not Mesh OK for $A ($D)"; exit 1; }
        ( cd "$D" && timeout 300 simpleFoam > log.simpleFoam 2>&1 ); RC=$?
        [ "$RC" -eq 0 ] \
            || { echo "ABORT: SMOKE simpleFoam rc=$RC on iteration 1 for $A -- a"
                 echo "       FINDING, not a retry ($D)"; exit 1; }
        grep -q "Selecting incompressible transport model powerLaw" "$D/log.simpleFoam" \
            || { echo "ABORT: SMOKE did not instantiate viscosityModels::powerLaw ($A)"; exit 1; }
        grep -q "Selecting laminar stress model Stokes" "$D/log.simpleFoam" \
            || { echo "ABORT: SMOKE did not instantiate the Stokes laminar model ($A)"; exit 1; }
        grep -q "generalizedNewtonian" "$D/log.simpleFoam" \
            && { echo "ABORT: SMOKE log mentions generalizedNewtonian -- WRONG class ($A)"; exit 1; }
        for f in pInlet pOutlet QInlet UmaxInlet nuMinAll nuMaxAll; do
            ls "$D/postProcessing/$f"/*/*.dat > /dev/null 2>&1 \
                || { echo "ABORT: SMOKE wrote no monitor for $f ($A)"; exit 1; }
        done
        # STRUCTURE ONLY: --dryrun-reader prints NO value, so the smoke test
        # cannot leak an answer before the freeze.
        python3 "$GRADER" --dryrun-reader "$D/postProcessing/pInlet/0/surfaceFieldValue.dat" \
            > /dev/null || { echo "ABORT: SMOKE gate-channel reader refused ($A)"; exit 1; }
        echo "  smoke   $A PASS (1 iteration, $((NX*NR)) cells)"
    done
    printf '%s' "$S" > "$SMOKE_DIR_FILE" \
        || { echo "ABORT: cannot record the smoke directory"; exit 1; }
    return 0
}
# The directory is handed back through a FILE, never through stdout:
# `S="$(smoke)"` would run smoke in a SUBSHELL, where every `exit 1` above kills
# only the subshell and the script sails on -- the same silent-non-gating class
# as `( set -e; ... )`.
SMOKE_DIR_FILE="$(mktemp /tmp/claude-1000/vmfl007r2_smokedir_XXXXXX)" \
    || { echo "ABORT: cannot make the smoke-directory handoff file"; exit 1; }

if [ "$SMOKE_ONLY" -eq 1 ]; then smoke; echo "smoke dir: $(cat "$SMOKE_DIR_FILE")"; exit 0; fi
smoke || { echo "ABORT: the pre-flight smoke test failed"; exit 1; }
SMOKE_DIR="$(cat "$SMOKE_DIR_FILE")"
[ -n "$SMOKE_DIR" ] && [ -d "$SMOKE_DIR" ] \
    || { echo "ABORT: the smoke test did not report a directory -- it did not run"; exit 1; }

# ===========================================================================
# 6.  CONTENTION, recorded honestly at launch (never used to excuse a number).
# ===========================================================================
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 1; }
{
    echo "--- BASELINE at launch --- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "loadavg(1/5/15) = $(cut -d' ' -f1-3 /proc/loadavg) on $(nproc) cores"
    echo "co-resident solvers (ps args, NOT comm):"
    ps -eo pid,etimes,pcpu,args --no-headers \
        | grep -E 'Foam|fluent|docker run' | grep -v grep | head -30
} > "$RUN_ROOT/CONTENTION.txt"

# ===========================================================================
# 7.  THE SLATE.  RUN IN FULL, IN ORDER.  A RESULT NEVER STOPS IT.
# ===========================================================================
TOTAL_WALL=0
for i in "${!SLATE_NAMES[@]}"; do
    A="${SLATE_NAMES[$i]}"; D="$RUN_ROOT/$A"

    # THE SLATE COST CAP (rule 12).  Checked BEFORE launching each arm, so the
    # slate stops at its cap rather than overrunning it and asking for more.
    if [ "$TOTAL_WALL" -ge "$CAP_SLATE_WALL_S" ]; then
        echo "SLATE CAP REACHED at ${TOTAL_WALL}s (${CAP_SLATE_CORE_MIN} core-min)."
        echo "Remaining arms NOT launched. CLAUDE.md rule 12: an overrun stops the"
        echo "run; it does not get a new budget. The unrun arms are reported by the"
        echo "comparator as MISSING, never silently dropped."
        break
    fi

    # THE AGE GUARD (rule 4): refuse a directory that already exists.
    [ -e "$D" ] && { echo "ABORT: $D already exists -- the age guard refuses a case"
                     echo "       whose 0/ or time directories are already there. A"
                     echo "       re-run is a NEW directory citing the old one."; exit 1; }
    mkdir -p "$D" || { echo "ABORT: cannot create $D"; exit 1; }
    cp -r "$SRC"/. "$D"/ || { echo "ABORT: case copy failed for $A"; exit 1; }
    cp "$ARMS/$A.fvSolution" "$D/system/fvSolution" \
        || { echo "ABORT: arm install failed for $A"; exit 1; }
    # the fvSolution that will ACTUALLY RUN must be the registered blob
    G="$(git -C "$REPO" hash-object "$D/system/fvSolution")"
    [ "$G" = "${SLATE_BLOBS[$i]}" ] \
        || { echo "ABORT: the fvSolution placed in $D is $G, not ${SLATE_BLOBS[$i]}"; exit 1; }
    sed -e "s/__NX__/$NX/" -e "s/__NR__/$NR/" \
        "$D/system/blockMeshDict.template" > "$D/system/blockMeshDict" \
        || { echo "ABORT: blockMeshDict substitution failed for $A"; exit 1; }
    sed -e "s/__ENDTIME__/$ENDTIME/" -e "s/__WRITEINTERVAL__/$WRITEINTERVAL/" \
        "$D/system/controlDict.template" > "$D/system/controlDict" \
        || { echo "ABORT: controlDict substitution failed for $A"; exit 1; }
    grep -q '__NX__\|__NR__\|__ENDTIME__\|__WRITEINTERVAL__' \
        "$D/system/blockMeshDict" "$D/system/controlDict" \
        && { echo "ABORT: an unsubstituted placeholder survived in $A"; exit 1; }

    ( cd "$D" && blockMesh > log.blockMesh 2>&1 ) \
        || { echo "ABORT: blockMesh failed for $A"; exit 1; }
    ( cd "$D" && checkMesh > log.checkMesh 2>&1 )
    grep -q "^Mesh OK" "$D/log.checkMesh" \
        || { echo "ABORT: checkMesh did not report Mesh OK for $A"; exit 1; }

    # THE AGE MARKER.  0/U is touched LAST, immediately before the solver.
    touch "$D/0/U" || { echo "ABORT: cannot touch the age marker for $A"; exit 1; }
    sleep 1

    T0=$(date +%s)
    ( cd "$D" && timeout "$CAP_ARM_WALL_S" simpleFoam > log.simpleFoam 2>&1 )
    RC=$?
    T1=$(date +%s)
    WALL=$((T1 - T0))
    TOTAL_WALL=$((TOTAL_WALL + WALL))
    CORE_MIN=$(python3 -c "print('%.4f' % ($WALL*1/60.0))")
    {
        echo "rc = $RC"
        echo "arm = $A"
        echo "fvSolution_blob = ${SLATE_BLOBS[$i]}"
        echo "level = $LEVEL"
        echo "cells = $((NX*NR))"
        echo "endTime = $ENDTIME"
        echo "wall_s = $WALL"
        echo "ranks = 1"
        echo "core_min = $CORE_MIN"
        echo "cap_arm_core_min = $CAP_ARM_CORE_MIN"
        echo "prereg_sha = $PREREG_SHA"
        echo "finished_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } > "$D/RUN_RC.txt"

    # ---- AND THIS IS THE POINT OF THE SLATE: A RESULT DOES NOT STOP IT. ----
    if [ "$RC" -eq 124 ]; then
        echo "  arm     $A CAP-STOPPED at ${WALL}s (${CAP_ARM_CORE_MIN} core-min)."
        echo "          Rule 12: it does not get a new budget and is NOT re-run."
    elif [ "$RC" -ne 0 ]; then
        echo "  arm     $A rc=$RC (${CORE_MIN} core-min) -- RECORDED. A crash is a"
        echo "          FINDING about this arm, and the slate CONTINUES: the slate"
        echo "          was committed to in full before any arm ran."
    else
        echo "  arm     $A rc=0 ${WALL}s ${CORE_MIN} core-min"
    fi
done

TOTAL_CORE_MIN=$(python3 -c "print('%.4f' % ($TOTAL_WALL*1/60.0))")
{
    echo "total_wall_s = $TOTAL_WALL"
    echo "total_core_min = $TOTAL_CORE_MIN"
    echo "cap_slate_core_min = $CAP_SLATE_CORE_MIN"
    echo "cap_arm_core_min = $CAP_ARM_CORE_MIN"
    echo "ranks = 1 (serial, arms run sequentially)"
    echo "rate_basis = c7a.4xlarge \$0.0513/core-h, OWNER-STATED not measured"
    echo "prereg_sha = $PREREG_SHA"
    echo "smoke_dir = $SMOKE_DIR (scratch, OUTSIDE the runs tree)"
} > "$RUN_ROOT/COST.txt"
python3 -c "
cm=float('$TOTAL_CORE_MIN'); cap=float('$CAP_SLATE_CORE_MIN')
print('slate   %.4f core-min against a cap of %.0f (%.1f %%)' % (cm,cap,100*cm/cap))
print('derived \$%.5f at \$0.0513/core-h -- DERIVED, not measured' % (cm/60*0.0513))
"
echo "cost record: $RUN_ROOT/COST.txt"
echo "now grade:   python3 $GRADER"
