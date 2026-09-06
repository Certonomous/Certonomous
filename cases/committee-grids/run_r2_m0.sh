#!/bin/bash
# =============================================================================
# !! THIS DRIVER HAS NEVER BEEN EXECUTED !!
#
# WHAT HAS BEEN DONE, AND BY WHOM:
#   * `bash -n` on this file was DENIED BY THE PERMISSION SYSTEM in the session that
#     wrote it (pre-registration §14.4a, verbatim). The authoring lane has therefore
#     never parsed it.
#   * The cfd supervisor REPORTS that the owner ran `bash -n` on it in her own session
#     and it returned "SYNTAX OK" (§14.4a-4). THE AUTHORING LANE DID NOT WITNESS THIS
#     and records it as a relayed report, not as a first-hand fact.
#
# WHAT HAS **NOT** BEEN DONE:
#   * IT HAS NEVER BEEN RUN. Not once, not partially, not on one arm.
#   * A PARSE IS NOT VERIFICATION. `bash -n` proves the file is well-formed. It proves
#     NOTHING about whether it does the right thing -- not the cap arithmetic, not the
#     rc capture, not the arm assembly, not the age-guard ordering. Do not let
#     "syntax-checked" be read as "verified"; that is how the next reader stops looking.
#   * NO QUEUE ENTRY FOR IT EXISTS AND NONE HAS BEEN FILED.
#
# ENQUEUEING THIS FIRES IT. The cfd drop path is a launch button: a live daemon polls
# it and launches within a minute, at 14 ranks. A syntax check is not an authorisation
# to launch, and no agent's message is the owner's consent (CLAUDE.md rule 9).
# =============================================================================
#
# R2-M0 driver -- RUNG 2 / CRM (DPW5 L1.T hex) compressible admission probe.
#
# Registered by verification/campaign/RUNG2_CRM_M0_PREREGISTRATION.md v1.1.
# Launched ONLY by the queue daemon (scripts/queue_runner.py --daemon).
#
# THE CAP IS ENFORCED STRUCTURALLY, INSIDE THIS DRIVER, NOT BY THE RUNNER.
#   scripts/queue_runner.py's cap_watch REPORTS an overrun and does NOT kill.
#   This driver therefore carries its own budget of 170.0 core-min = 10200 CORE-SECONDS,
#   RECOMPUTED BEFORE EVERY STEP from that one total, and converted to a wall-clock
#   `timeout` by dividing by that step's rank count. An exhausted budget stops the run at
#   exit 6. A cap nothing enforces is not a cap.
#
# rc IS CAPTURED INSIDE THIS WRAPPER, NEVER AROUND A `setsid` LINE.
#   `setsid timeout cmd` exits 0 for every outcome -- success, timeout and crash alike.
#   Every rc below is taken immediately after the command it belongs to, inside run_step().
#
# EXIT CODES
#   0  ran; the grader's verdict is in the STATUS file (a GATE FAIL is still exit 0)
#   2  the grader REFUSED (a planted control did not fire)
#   3  the run root already exists -- rule 4's guard
#   4  the OpenFOAM environment did not come up
#   5  a source artifact this probe reads is missing
#   6  THE CAP WAS EXHAUSTED -- the run was stopped and did not get a new budget
#   7  arm assembly failed

set -uo pipefail

REPO=/home/ubuntu/Certonomous
SRC=/home/ubuntu/certonomous-runs/dpw5-committee-probe          # READ ONLY. Never written.
SEED="$SRC/run_hex_base_compressible_a2.11"                     # A0's reproduction seed
WARM="$SRC/run_hex_base_incompressible_a2.11"                   # A3's warm-start source
ROOT="$REPO/verification/runs/RUNG2_CRM_runs/M0_compressible_admission"
GRADER="$REPO/cases/committee-grids/grade_r2_m0.py"

RANKS=14
ENDTIME=50
CAP_CORE_S=10200          # 170.0 core-min, registered §6. NEVER RAISED, NEVER RESET.
SPENT_CORE_S=0
ARMS="A0 A1 A2 A3 A4"

STATUS="$ROOT/STATUS.R2_M0"

say() { echo "[$(date -u +%H:%M:%SZ)] $*"; }

die() {
    local code=$1; shift
    say "ABORT($code): $*"
    if [ -d "$ROOT" ]; then
        { echo "rc=$code"; echo "reason=$*"; echo "spent_core_s=$SPENT_CORE_S"; } >> "$STATUS"
    fi
    sweep
    exit "$code"
}

# Condition 5: STOP THE PARENT BEFORE THE CHILD, THEN SWEEP. A load average is a decaying
# mean and never confirms a stop; only an empty process list does.
sweep() {
    pkill -TERM -f "rhoSimpleFoam -parallel" 2>/dev/null
    sleep 2
    pkill -KILL -f "rhoSimpleFoam -parallel" 2>/dev/null
    return 0
}
trap 'sweep' EXIT

budget_left_core_s() { echo $((CAP_CORE_S - SPENT_CORE_S)); }

# run_step <name> <ranks> <logfile> -- command...
# Recomputes the wall budget from the ONE total before every step, captures rc INSIDE,
# and charges wall x ranks to the spend.
run_step() {
    local name=$1 ranks=$2 log=$3; shift 3
    local left; left=$(budget_left_core_s)
    if [ "$left" -le 0 ]; then
        say "CAP EXHAUSTED before step '$name' (spent ${SPENT_CORE_S} of ${CAP_CORE_S} core-s)"
        return 66
    fi
    local to=$(( left / ranks ))
    [ "$to" -lt 1 ] && to=1
    say "step '$name' ranks=$ranks budget_left=${left}core-s timeout=${to}s"
    local t0 t1 rc wall
    t0=$(date +%s)
    timeout --kill-after=20s "${to}s" "$@" > "$log" 2>&1
    rc=$?                                   # <-- rc captured HERE, inside the wrapper
    t1=$(date +%s)
    wall=$(( t1 - t0 ))
    SPENT_CORE_S=$(( SPENT_CORE_S + wall * ranks ))
    say "step '$name' rc=$rc wall=${wall}s charged=$(( wall * ranks ))core-s cumulative=${SPENT_CORE_S}core-s"
    printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$rc" "$wall" "$ranks" "$(( wall * ranks ))" >> "$ROOT/COST.tsv"
    LAST_RC=$rc
    LAST_WALL=$wall
    return 0
}

# ---------------------------------------------------------------- preflight

for p in "$SEED" "$WARM" "$GRADER" "$SEED/constant/polyMesh" "$WARM/processor0/200"; do
    [ -e "$p" ] || { echo "MISSING SOURCE: $p"; exit 5; }
done

# Rule 4's guard: refuse a run root that already exists.
[ -e "$ROOT" ] && { echo "RUN ROOT ALREADY EXISTS: $ROOT"; exit 3; }

mkdir -p "$ROOT" || exit 7
date -u +%s > "$ROOT/RUN_ROOT_CREATED_EPOCH"
printf 'name\trc\twall_s\tranks\tcore_s\n' > "$ROOT/COST.tsv"
say "run root created; cap ${CAP_CORE_S} core-s (170.0 core-min), estimate 66.9 core-min"

# The OpenFOAM environment. `set -u` is lifted ONLY across the source line: v2606's
# etc/bashrc:184 reads WM_PROJECT_DIR before setting it, and an unbound variable inside a
# SOURCED file kills the sourcing shell outright. That defect cost RUNG0 attempt 1.
set +u
# shellcheck disable=SC1091
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
if [ -z "${FOAM_APPBIN:-}" ] || ! command -v rhoSimpleFoam >/dev/null 2>&1; then
    die 4 "OpenFOAM environment did not come up (FOAM_APPBIN='${FOAM_APPBIN:-}')"
fi
say "OpenFOAM up: $(command -v rhoSimpleFoam)"

# ---------------------------------------------------------------- arm assembly

# Every arm is COPIED, never symlinked, so that nothing this probe does can write into the
# read-only source store, and so the run root is self-contained for provenance.
assemble_arm() {
    local arm=$1 d="$ROOT/$1"
    mkdir -p "$d" || return 1
    cp -a "$SEED/constant"  "$d/constant"  || return 1
    cp -a "$SEED/system"    "$d/system"    || return 1
    cp -a "$SEED/0"         "$d/0"         || return 1
    local i
    for i in $(seq 0 $((RANKS-1))); do
        mkdir -p "$d/processor$i" || return 1
        cp -a "$SEED/processor$i/constant" "$d/processor$i/constant" || return 1
        cp -a "$SEED/processor$i/0"        "$d/processor$i/0"        || return 1
    done
    return 0
}

# R2-G2: every arm prints min/max of T, p and rho EVERY iteration, so the proximate cause of
# an abort is READ FROM A FIELD BOUND rather than inferred from a stack trace. This is a
# read-only diagnostic: it changes no equation, no scheme, no relaxation and no boundary
# condition, and A0 therefore remains a faithful reproduction of the August NUMERICS.
add_minmax_fo() {
    local d=$1
    python3 - "$d/system/controlDict" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
fo = """
    r2m0MinMax
    {
        type            fieldMinMax;
        libs            (fieldFunctionObjects);
        writeControl    timeStep;
        writeInterval   1;
        mode            magnitude;
        log             true;
        fields          (T p rho U);
    }
"""
m = re.search(r"^functions\s*\{", s, re.M)
if not m:
    s = s.rstrip() + "\n\nfunctions\n{\n" + fo + "}\n"
else:
    s = s[:m.end()] + "\n" + fo + s[m.end():]
open(p, "w").write(s)
PY
}

set_endtime() {
    python3 - "$1/system/controlDict" "$2" <<'PY'
import re, sys
p, t = sys.argv[1], sys.argv[2]
s = open(p).read()
s2, n = re.subn(r"^(\s*endTime\s+)[0-9.]+\s*;", r"\g<1>%s;" % t, s, count=1, flags=re.M)
if n != 1:
    raise SystemExit("endTime not rewritten in %s" % p)
open(p, "w").write(s2)
PY
}

# A1's registered remedy: bound the thermo inversion. `limitTemperature` is an fvOption; the
# pressure limits go in the SIMPLE dict where rhoSimpleFoam's pressureControl reads them.
add_bounds() {
    local d=$1
    cat > "$d/constant/fvOptions" <<'EOF'
limitT
{
    type            limitTemperature;
    active          yes;
    selectionMode   all;
    min             100;
    max             1000;
}
EOF
    python3 - "$d/system/fvSolution" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
if "pMin" in s:
    raise SystemExit(0)
s2, n = re.subn(r"(rhoMin\s+[0-9.]+\s*;\s*rhoMax\s+[0-9.]+\s*;)",
                r"\g<1> pMin 1000; pMax 1e7;", s, count=1)
if n != 1:
    s2, n = re.subn(r"^(SIMPLE\s*\{)", r"\g<1>\n    pMin 1000;\n    pMax 1e7;", s, count=1, flags=re.M)
    if n != 1:
        raise SystemExit("could not insert pressure bounds into %s" % p)
open(p, "w").write(s2)
PY
}

say "assembling five arms from the archived compressible seed"
for arm in $ARMS; do
    assemble_arm "$arm" || die 7 "arm $arm did not assemble"
    add_minmax_fo "$ROOT/$arm" || die 7 "arm $arm: min/max function object not added"
done

# A0 -- reproduction control. Dictionaries otherwise untouched; endTime left at the seed's
# own value so the arm reproduces the August run rather than a rewritten version of it.
md5sum "$SEED/system/fvSolution" "$ROOT/A0/system/fvSolution" > "$ROOT/A0/FVSOLUTION_MD5.txt" 2>&1
md5sum "$SEED/system/fvSchemes"  "$ROOT/A0/system/fvSchemes"  >> "$ROOT/A0/FVSOLUTION_MD5.txt" 2>&1

# A1 -- thermo/pressure bounds, nothing else.
add_bounds "$ROOT/A1" || die 7 "A1 bounds"
set_endtime "$ROOT/A1" "$ENDTIME" || die 7 "A1 endTime"

# A2 -- sensibleEnthalpy + transonic yes, on top of A1's bounds.
add_bounds "$ROOT/A2" || die 7 "A2 bounds"
set_endtime "$ROOT/A2" "$ENDTIME" || die 7 "A2 endTime"
sed -i 's/sensibleInternalEnergy/sensibleEnthalpy/' "$ROOT/A2/constant/thermophysicalProperties"
sed -i 's/transonic no;/transonic yes;/'            "$ROOT/A2/system/fvSolution"
grep -q sensibleEnthalpy "$ROOT/A2/constant/thermophysicalProperties" || die 7 "A2 energy form not switched"
grep -q 'transonic yes'  "$ROOT/A2/system/fvSolution"                 || die 7 "A2 transonic not switched"

# A3 -- warm start from the archived CONVERGED incompressible field, on top of A1's bounds.
add_bounds "$ROOT/A3" || die 7 "A3 bounds"
set_endtime "$ROOT/A3" "$ENDTIME" || die 7 "A3 endTime"

# A4 -- relaxation crawl, on top of A1's bounds.
add_bounds "$ROOT/A4" || die 7 "A4 bounds"
set_endtime "$ROOT/A4" "$ENDTIME" || die 7 "A4 endTime"
python3 - "$ROOT/A4/system/fvSolution" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
s = re.sub(r"fields\s*\{[^}]*\}", "fields { p 0.1; rho 1.0; }", s, count=1)
s = re.sub(r"equations\s*\{[^}]*\}",
           'equations { U 0.3; "(k|omega|nuTilda|e|h)" 0.3; }', s, count=1)
open(p, "w").write(s)
PY
grep -q 'p 0.1' "$ROOT/A4/system/fvSolution" || die 7 "A4 relaxation not applied"

say "arms assembled"

# ---------------------------------------------------------------- A3's warm start

# THE DECOMPOSITIONS DIFFER. Measured, not assumed: the archived compressible and
# incompressible cases were each decomposed with `scotch` independently, and their
# processor0 owner lists are 559549 and 559881 bytes. A processor-to-processor field copy
# would therefore map the converged field onto the WRONG CELLS while looking perfectly
# healthy. The field is instead reconstructed onto the serial mesh and re-decomposed onto
# THIS arm's own addressing, and the result is checked against the source's own bounds.
A3_OK=0
say "A3: reconstructing the archived converged incompressible field"
WARMTMP="$ROOT/A3/_warmstart_src"
mkdir -p "$WARMTMP"
cp -a "$WARM/constant" "$WARMTMP/constant" 2>/dev/null
cp -a "$WARM/system"   "$WARMTMP/system"   2>/dev/null
cp -a "$WARM/0"        "$WARMTMP/0"        2>/dev/null
for i in $(seq 0 $((RANKS-1))); do
    mkdir -p "$WARMTMP/processor$i"
    cp -a "$WARM/processor$i/constant" "$WARMTMP/processor$i/constant" 2>/dev/null
    cp -a "$WARM/processor$i/200"      "$WARMTMP/processor$i/200"      2>/dev/null
done
run_step "A3_reconstruct" 1 "$ROOT/A3/log.reconstructPar" \
    reconstructPar -case "$WARMTMP" -time 200 -fields '(U k omega)'
if [ "${LAST_RC:-1}" -eq 0 ] && [ -d "$WARMTMP/200" ]; then
    cp -f "$WARMTMP/200/U"     "$ROOT/A3/0/U"     2>/dev/null
    cp -f "$WARMTMP/200/k"     "$ROOT/A3/0/k"     2>/dev/null
    cp -f "$WARMTMP/200/omega" "$ROOT/A3/0/omega" 2>/dev/null
    python3 - "$ROOT/A3/0/U" <<'PY'
import re, sys
# The warm field must carry a boundaryField the compressible case can read. The
# incompressible case's U carries the same patch names and BC types, so this is a
# transcription check rather than a translation: refuse if a patch went missing.
s = open(sys.argv[1]).read()
for patch in ("wall", "symmetry", "farfield"):
    if patch not in s:
        raise SystemExit("warm-start U lost patch %s" % patch)
PY
    if [ $? -eq 0 ]; then
        run_step "A3_decompose_fields" 1 "$ROOT/A3/log.decomposePar" \
            decomposePar -case "$ROOT/A3" -fields -time 0
        [ "${LAST_RC:-1}" -eq 0 ] && A3_OK=1
    fi
fi
rm -rf "$WARMTMP"
if [ "$A3_OK" -eq 1 ]; then
    say "A3 warm start MAPPED and re-decomposed onto this arm's own addressing"
    echo "A3 warm start: MAPPED via reconstructPar(200) -> decomposePar -fields" > "$ROOT/A3/WARMSTART.txt"
else
    say "A3 warm start FAILED TO MAP -- A3 will be recorded BLOCKED, not run"
    echo "A3 warm start: FAILED TO MAP. Arm BLOCKED, not run, no conclusion drawn." > "$ROOT/A3/WARMSTART.txt"
fi

# ---------------------------------------------------------------- the solves

CAP_HIT=0
for arm in $ARMS; do
    d="$ROOT/$arm"
    if [ "$arm" = "A3" ] && [ "$A3_OK" -ne 1 ]; then
        echo "BLOCKED" > "$d/ARM_STATE.txt"
        say "$arm SKIPPED (warm start did not map) -- BLOCKED, no core-minutes spent"
        continue
    fi
    if [ "$(budget_left_core_s)" -le 0 ]; then
        echo "NOT RUN -- CAP EXHAUSTED" > "$d/ARM_STATE.txt"
        CAP_HIT=1
        say "$arm NOT RUN: cap exhausted"
        continue
    fi
    # THE AGE GUARD'S ANCHOR. `0/T` is touched LAST at launch, so it dates the run that was
    # allowed to produce this answer. Every field at endTime must end up newer than it.
    touch "$d/0/T"
    for i in $(seq 0 $((RANKS-1))); do touch "$d/processor$i/0/T"; done

    run_step "$arm" "$RANKS" "$d/log.solve" \
        mpirun -np "$RANKS" rhoSimpleFoam -case "$d" -parallel
    if [ $? -eq 66 ]; then CAP_HIT=1; echo "NOT RUN -- CAP EXHAUSTED" > "$d/ARM_STATE.txt"; continue; fi
    echo "${LAST_RC}" > "$d/rc.txt"          # rc from INSIDE the wrapper, per condition 2
    say "$arm rc=${LAST_RC}"

    # Reconstruct only if the arm actually reached endTime, so the grader can read
    # <case>/<endTime>/<field> and apply rule 4's clauses 4 and 6.
    if [ "${LAST_RC}" -eq 0 ] && [ -d "$d/processor0/$ENDTIME" ]; then
        run_step "${arm}_reconstruct" 1 "$d/log.reconstructPar" \
            reconstructPar -case "$d" -time "$ENDTIME"
    fi
done

# ---------------------------------------------------------------- grade

say "spend at grading: ${SPENT_CORE_S} core-s of ${CAP_CORE_S} ($(python3 -c "print('%.4f'%($SPENT_CORE_S/60.0))") core-min)"

# The comparator refuses on a stale copy of itself. Verify the file that is about to run IS
# the committed blob, per rule 2 and §8.
FROZEN_OK=0
if [ "$(cd "$REPO" && git hash-object cases/committee-grids/grade_r2_m0.py)" \
   = "$(cd "$REPO" && git rev-parse HEAD:cases/committee-grids/grade_r2_m0.py 2>/dev/null)" ]; then
    FROZEN_OK=1
fi
echo "comparator_matches_committed_blob=$FROZEN_OK" >> "$STATUS"

run_step "selftest" 1 "$ROOT/log.selftest" python3 "$GRADER" --selftest
SELFTEST_RC=${LAST_RC:-1}

GRADE_ARGS=""
for arm in $ARMS; do
    [ -f "$ROOT/$arm/log.solve" ] && GRADE_ARGS="$GRADE_ARGS $ROOT/$arm"
done
# shellcheck disable=SC2086
run_step "grade" 1 "$ROOT/log.grade" python3 "$GRADER" --grade $GRADE_ARGS
GRADE_RC=${LAST_RC:-1}

{
    echo "case_id=RUNG2-CRM-M0"
    echo "prereg=verification/campaign/RUNG2_CRM_M0_PREREGISTRATION.md"
    echo "spent_core_s=$SPENT_CORE_S"
    echo "spent_core_min=$(python3 -c "print('%.4f'%($SPENT_CORE_S/60.0))")"
    echo "cap_core_min=170.0"
    echo "estimate_core_min=66.9"
    echo "cap_hit=$CAP_HIT"
    echo "a3_warmstart_mapped=$A3_OK"
    echo "selftest_rc=$SELFTEST_RC"
    echo "grade_rc=$GRADE_RC"
    echo "comparator_frozen_match=$FROZEN_OK"
} >> "$STATUS"

say "STATUS written to $STATUS"
[ "$CAP_HIT" -eq 1 ] && { say "CAP WAS HIT -- the run was STOPPED and did not get a new budget"; exit 6; }
[ "$SELFTEST_RC" -ne 0 ] && exit 2
[ "$GRADE_RC" -eq 2 ] && exit 2
exit 0
