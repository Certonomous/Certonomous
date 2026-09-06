#!/bin/bash
# =====================================================================================
# R2-M1 DRIVER -- NASA CRM / DPW5 L1.T hex, seven arms.
# Registration: verification/campaign/RUNG2_CRM_M1_PREREGISTRATION.md
# Grading path: cases/committee-grids/grade_r2_m1.py  (FROZEN at the prereg commit)
#
# THIS FILE LAUNCHES NOTHING BY ITSELF. It is placed by the chief under its own captured
# grant, after the cfd supervisor's check 4. Running it with no argument prints usage.
#
# WHAT IT CARRIES THAT M0's DRIVER DID NOT
# ----------------------------------------
#  1. THE BINARY-SAFE WARM-START GUARD, AND THE GUARD IS DRIVEN BOTH WAYS AT RUN TIME.
#     M0's guard did `open(path).read()` in TEXT mode against a `writeFormat binary`
#     field, died of UnicodeDecodeError at byte 0xfd position 900, and the driver recorded
#     "FAILED TO MAP" for a reconstructPar that had ALREADY SUCCEEDED (rc=0, End line,
#     all three fields at Time=200, 15,656,211 bytes landed in A3/0/U). A crashed guard's
#     exit code is indistinguishable from the failure it was watching for, so this driver
#     REFUSES TO TRUST ITS OWN GUARD until it has watched it accept a good field and
#     REFUSE a scrubbed one, on the real reconstructed file, in this run.
#
#  2. A CAP THAT HAS BEEN SHOWN TO WORK. M0's CAP_CORE_S path has NEVER EXECUTED -- its
#     calibration row says so: "both remain UNEXERCISED and this run is not evidence that
#     either works." `--selftest-cap` drives the arithmetic AND the refusal AND the
#     charging, and proves the refusal happens WITHOUT running the command it refused.
#
#  3. PER-ARM endTime. Only B1 is an admission arm. The diagnostic arms carry endTime 3
#     so the estimate's mass cannot sit in a survival branch (registration section 6).
#
#  4. B2 RUNS WITH THE FPE TRAP OFF, so the step that kills the other arms COMPLETES and
#     its state is RECORDED rather than inferred from a stack trace.
#
# EXIT CODES
#   0  ran; the grader's verdict is in the STATUS file (a GATE FAIL is still exit 0)
#   2  the grader REFUSED, or a live control did not fire
#   3  the run root already exists -- rule 4's guard
#   4  the OpenFOAM environment did not come up
#   5  a source artifact this probe reads is missing
#   6  THE CAP WAS EXHAUSTED -- the run was STOPPED and did not get a new budget
#   7  arm assembly failed
# =====================================================================================
set -uo pipefail

REPO=/home/ubuntu/Certonomous
SRC=/home/ubuntu/certonomous-runs/dpw5-committee-probe          # READ ONLY. Never written.
SEED="$SRC/run_hex_base_compressible_a2.11"                     # every arm's seed
WARM="$SRC/run_hex_base_incompressible_a2.11"                   # B1's warm-start source
ROOT="$REPO/verification/runs/RUNG2_CRM_runs/M1_mechanism_and_warmstart"
GRADER="$REPO/cases/committee-grids/grade_r2_m1.py"
GRADER_REL="cases/committee-grids/grade_r2_m1.py"

RANKS=14
CAP_CORE_S=3300           # 55.0 core-min, registered section 6.5. NEVER RAISED, NEVER RESET.
ESTIMATE_CORE_MIN=5.27    # HEADLINE, incurred regardless of outcome. Conditional is separate.
SPENT_CORE_S=0
WARM_TIME=200

ARMS="B0 B1 B2 B3 B4 B5 B6"
STATUS="$ROOT/STATUS.R2_M1"

# Per-arm endTime. B0 keeps the SEED's own value so it reproduces the August numerics
# rather than a rewritten version of them.
endtime_for() {
    case "$1" in
        B0) echo "" ;;      # empty == leave the seed's controlDict alone (endTime 120)
        B1) echo 50 ;;      # THE ONLY ADMISSION ARM
        *)  echo 3 ;;       # B2..B6 are diagnostic: one step BEYOND B0's abort point
    esac
}

say() { echo "[$(date -u +%H:%M:%SZ)] $*"; }

# ⚠ SCOPED TO THIS RUN'S OWN ROOT, AND THE SCOPE IS THE POINT.
# M0's driver sweeps `pkill -f "rhoSimpleFoam -parallel"`, which matches EVERY
# rhoSimpleFoam on this box -- including another team's, mid-campaign, on the way out of an
# unrelated failure. CLAUDE.md's standing instruction is DO NOT TOUCH RUNNING SOLVERS, and a
# trap that fires on EXIT is exactly where that gets violated silently.
# The child's command line carries `-case <ROOT>/<arm>`, so keying on $ROOT kills this
# probe's arms and nothing else. $ROOT is absolute and unique to this run.
# It also cannot match the driver's own shell (whose cmdline is `bash run_r2_m1.sh ...`),
# which is the OTHER way this idiom misfires -- a pattern that matches the invoking process
# kills the shell and every chained command after it silently never runs.
sweep() {
    [ -n "${ROOT:-}" ] || return 0
    pkill -TERM -f "rhoSimpleFoam -case $ROOT" 2>/dev/null
    sleep 2
    pkill -KILL -f "rhoSimpleFoam -case $ROOT" 2>/dev/null
    return 0
}

die() {
    local code=$1; shift
    say "ABORT($code): $*"
    if [ -d "$ROOT" ]; then
        { echo "rc=$code"; echo "reason=$*"; echo "spent_core_s=$SPENT_CORE_S"; } >> "$STATUS"
    fi
    sweep
    exit "$code"
}

# =====================================================================================
# THE CAP. One total, recomputed before every step, charged after every step.
# =====================================================================================

budget_left_core_s() { echo $((CAP_CORE_S - SPENT_CORE_S)); }

# timeout_for <ranks> -- the wall-second timeout that the REMAINING budget buys at <ranks>.
# Shrinks as spend grows.
#
# ⚠⚠ THE CLAMP BELOW IS NOT DEFENSIVE TIDYING. READ THIS BEFORE TOUCHING THE ARITHMETIC.
#
#     `timeout 0s cmd` DOES NOT MEAN "no time". IT MEANS NO LIMIT AT ALL -- coreutils
#     treats a zero duration as "never time out", so the command runs FOREVER.
#
# Integer division makes 0 the NATURAL result exactly when the budget is nearly exhausted:
# at 14 ranks any remaining budget below 14 core-s gives `left / ranks == 0`. So without
# the floor, the cap would apply a shrinking, correct-looking limit at every step right up
# to the LAST one -- and then hand the solver an UNLIMITED run, at the precise moment there
# was no budget left to pay for it.
#
# THAT IS A RUNAWAY WEARING THE COSTUME OF A CAP. The log would show a timeout being set
# at every step, including the one that never ends, and neither the registration nor the
# cost row would catch it. The floor of 1 s is what makes an exhausted budget produce a
# STOP rather than an unbounded run; `budget_left <= 0` in run_step is what refuses before
# it gets here. Control K1 exists to keep both properties honest.
timeout_for() {
    local ranks=$1 left; left=$(budget_left_core_s)
    local to=$(( left / ranks ))
    [ "$to" -lt 1 ] && to=1          # NEVER 0 -- see the runaway note above
    echo "$to"
}

# run_step <name> <ranks> <logfile> -- command...
# Returns 66 -- WITHOUT RUNNING THE COMMAND -- when the cap is already exhausted.
# rc is captured on the line IMMEDIATELY after the command, inside this wrapper. It is
# never taken around a `setsid`: `setsid timeout cmd` exits 0 for every outcome, so an rc
# read outside it is a zero that means nothing.
run_step() {
    local name=$1 ranks=$2 log=$3; shift 3
    local left; left=$(budget_left_core_s)
    if [ "$left" -le 0 ]; then
        say "CAP EXHAUSTED before step '$name' (spent ${SPENT_CORE_S} of ${CAP_CORE_S} core-s)"
        printf '%s\t%s\t%s\t%s\t%s\n' "$name" "CAP" 0 "$ranks" 0 >> "$ROOT/COST.tsv" 2>/dev/null
        LAST_RC=66
        return 66
    fi
    local to; to=$(timeout_for "$ranks")
    say "step '$name' ranks=$ranks budget_left=${left}core-s timeout=${to}s"
    local t0 t1 rc wall
    t0=$(date +%s)
    timeout --kill-after=20s "${to}s" "$@" > "$log" 2>&1
    rc=$?                                   # <-- rc captured HERE, inside the wrapper
    t1=$(date +%s)
    wall=$(( t1 - t0 ))
    SPENT_CORE_S=$(( SPENT_CORE_S + wall * ranks ))
    say "step '$name' rc=$rc wall=${wall}s charged=$(( wall * ranks ))core-s cumulative=${SPENT_CORE_S}core-s"
    printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$rc" "$wall" "$ranks" "$(( wall * ranks ))" \
        >> "$ROOT/COST.tsv" 2>/dev/null
    LAST_RC=$rc
    LAST_WALL=$wall
    return 0
}

# -------------------------------------------------------------------------------------
# --selftest-cap : DRIVE THE CAP. M0's cap path has never executed, so M0 is not evidence
# that a cap in this lab stops anything. This mode makes the arithmetic, the refusal and
# the charging observable, and it costs nothing.
# -------------------------------------------------------------------------------------
selftest_cap() {
    local tmp fails=0
    tmp=$(mktemp -d)
    ROOT="$tmp"                     # so COST.tsv writes land somewhere harmless
    printf 'name\trc\twall_s\tranks\tcore_s\n' > "$ROOT/COST.tsv"

    _chk() { # _chk <label> <condition-rc> <detail>
        if [ "$2" -eq 0 ]; then echo "PASS $1  $3"; else echo "FAIL $1  $3"; fails=$((fails+1)); fi
    }

    # K0 -- the arithmetic.
    CAP_CORE_S=1000; SPENT_CORE_S=0
    [ "$(budget_left_core_s)" -eq 1000 ]; local a=$?
    SPENT_CORE_S=400
    [ "$(budget_left_core_s)" -eq 600 ]; local b=$?
    _chk K0 $(( a + b )) "budget_left is CAP-SPENT: 1000-0=$(SPENT_CORE_S=0; budget_left_core_s), 1000-400=600"

    # K1 -- the timeout SHRINKS as spend grows, and never reaches 0 (0s == no limit).
    CAP_CORE_S=1400; SPENT_CORE_S=0;    local t0; t0=$(timeout_for 14)
    SPENT_CORE_S=700;                   local t1; t1=$(timeout_for 14)
    SPENT_CORE_S=1399;                  local t2; t2=$(timeout_for 14)
    [ "$t0" -eq 100 ] && [ "$t1" -eq 50 ] && [ "$t2" -ge 1 ]
    _chk K1 $? "timeout at 14 ranks: ${t0}s -> ${t1}s -> ${t2}s, and NEVER 0s"

    # K2 -- THE REFUSAL, and it must happen WITHOUT RUNNING THE COMMAND. Planted: the
    # command would create a witness file. If the file appears, the cap did not stop it.
    CAP_CORE_S=100; SPENT_CORE_S=100
    local witness="$tmp/witness_must_not_exist"
    run_step "capped" 14 "$tmp/log.capped" touch "$witness"
    local rc=$?
    [ "$rc" -eq 66 ] && [ ! -e "$witness" ]
    _chk K2 $? "exhausted cap returns 66 and the command DID NOT RUN (witness absent=$([ ! -e "$witness" ] && echo yes || echo NO))"

    # K3 -- the same command RUNS when budget remains. The planted control in the other
    # direction: a refusal that refuses everything is not a cap, it is a broken driver.
    CAP_CORE_S=1000; SPENT_CORE_S=0
    run_step "uncapped" 14 "$tmp/log.uncapped" touch "$witness"
    [ "${LAST_RC}" -eq 0 ] && [ -e "$witness" ]
    _chk K3 $? "with budget left the command RUNS (witness present=$([ -e "$witness" ] && echo yes || echo NO)), rc=${LAST_RC}"

    # K4 -- CHARGING. Spend must rise by wall x ranks. A cap that never charges never bites.
    CAP_CORE_S=100000; SPENT_CORE_S=0
    run_step "charge" 14 "$tmp/log.charge" sleep 2
    [ "$SPENT_CORE_S" -ge 28 ]
    _chk K4 $? "a 2 wall-s step at 14 ranks charged ${SPENT_CORE_S} core-s (>= 28)"

    # K5 -- the timeout ACTUALLY FIRES and the rc says so. `timeout` returns 124 on expiry.
    CAP_CORE_S=28; SPENT_CORE_S=0      # 28 core-s / 14 ranks = 2 s of wall
    run_step "expire" 14 "$tmp/log.expire" sleep 60
    [ "${LAST_RC}" -eq 124 ]
    _chk K5 $? "a step exceeding its budgeted wall time was KILLED, rc=${LAST_RC} (124 == timeout fired)"

    # K6 -- and the run is then over budget, which the caller turns into exit 6.
    [ "$(budget_left_core_s)" -le 0 ]
    _chk K6 $? "after the expiry the budget is exhausted (left=$(budget_left_core_s) core-s) -- the run STOPS, it does not get a new budget"

    rm -rf "$tmp"
    echo "CAP SELFTEST: $([ $fails -eq 0 ] && echo PASS || echo FAIL) -- $((7-fails))/7 controls fired."
    return $fails
}

# =====================================================================================
# THE BINARY-SAFE WARM-START GUARD, and the control that must pass before it is trusted.
# =====================================================================================

# warm_guard <field file> -- 0 == all registered patches present, 1 == one is missing,
# and it reads BYTES so a `writeFormat binary` field cannot crash it into a false verdict.
warm_guard() {
    python3 - "$1" <<'PY'
import sys
# THE REPAIR, AND IT HAS NO DEGREES OF FREEDOM. M0 read this file in TEXT mode and died
# of UnicodeDecodeError before it could test anything; the test itself is unchanged.
data = open(sys.argv[1], 'rb').read()
missing = [p for p in (b"wall", b"symmetry", b"farfield") if p not in data]
if missing:
    sys.stderr.write("warm-start field lost patch %s\n" % missing[0].decode())
    raise SystemExit(1)
raise SystemExit(0)
PY
}

# guard_discriminates <real field file> -- rule 3 on the guard itself. The guard is watched
# accepting a good field AND REFUSING a scrubbed one, on the REAL file, in THIS run. A
# guard only ever seen to pass is not a guard, and a guard that crashes reports the wrong
# failure -- which is exactly what M0 recorded.
guard_discriminates() {
    local real=$1 scrubbed="$1.scrubprobe" ok=1
    warm_guard "$real" 2>/dev/null || ok=0
    if [ "$ok" -ne 1 ]; then
        say "GUARD CONTROL: the guard REJECTED the real reconstructed field -- not trusted"
        rm -f "$scrubbed"; return 1
    fi
    python3 - "$real" "$scrubbed" <<'PY'
import sys
open(sys.argv[2], 'wb').write(open(sys.argv[1], 'rb').read().replace(b"farfield", b"XXXXXXXX"))
PY
    if warm_guard "$scrubbed" 2>/dev/null; then
        say "GUARD CONTROL: the guard ACCEPTED a field with 'farfield' scrubbed -- NOT TRUSTED"
        rm -f "$scrubbed"; return 1
    fi
    rm -f "$scrubbed"
    say "GUARD CONTROL: accepts the real field, REFUSES the scrubbed one -- DISCRIMINATES"
    return 0
}

# =====================================================================================
# ARM ASSEMBLY
# =====================================================================================

assemble_arm() {
    local arm=$1 d="$ROOT/$1" i
    mkdir -p "$d" || return 1
    cp -a "$SEED/constant" "$d/constant" || return 1
    cp -a "$SEED/system"   "$d/system"   || return 1
    cp -a "$SEED/0"        "$d/0"        || return 1
    for i in $(seq 0 $((RANKS-1))); do
        mkdir -p "$d/processor$i" || return 1
        cp -a "$SEED/processor$i/constant" "$d/processor$i/constant" || return 1
        cp -a "$SEED/processor$i/0"        "$d/processor$i/0"        || return 1
    done
    return 0
}

# The registered writer block, section 7 of the registration, character for character as
# `rehearse_r2_m1_writers.sh` rehearsed it on all seven arms. M0's forceCoeffs object is
# deliberately NOT carried forward: this probe produces no force claim, and an instrument
# whose output cannot be used is an invitation to quote it.
add_writers() {
    python3 - "$1/system/controlDict" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
fo = """
    r2m1MinMax
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
    # M0's seed may already carry a functions block with its own objects; the registered
    # object is INSERTED, never substituted for what is there (L-221/L-222).
    s = s[:m.end()] + "\n" + fo + s[m.end():]
open(p, "w").write(s)
if "r2m1MinMax" not in open(p).read():
    raise SystemExit("writer block did not land in %s" % p)
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
p = sys.argv[1]; s = open(p).read()
if "pMin" in s:
    raise SystemExit(0)
s2, n = re.subn(r"(rhoMin\s+[0-9.]+\s*;\s*rhoMax\s+[0-9.]+\s*;)",
                r"\g<1> pMin 1000; pMax 1e7;", s, count=1)
if n != 1:
    s2, n = re.subn(r"^(SIMPLE\s*\{)", r"\g<1>\n    pMin 1000;\n    pMax 1e7;", s,
                    count=1, flags=re.M)
    if n != 1:
        raise SystemExit("could not insert pressure bounds into %s" % p)
open(p, "w").write(s2)
PY
}

set_energy_enthalpy() {
    sed -i 's/sensibleInternalEnergy/sensibleEnthalpy/' "$1/constant/thermophysicalProperties"
    grep -q sensibleEnthalpy "$1/constant/thermophysicalProperties"
}
set_transonic_yes() {
    sed -i 's/transonic no;/transonic yes;/' "$1/system/fvSolution"
    grep -q 'transonic yes' "$1/system/fvSolution"
}

# =====================================================================================
# MAIN
# =====================================================================================

DRY=0
REGISTERED_ROOT="$ROOT"

case "${1:-}" in
    --selftest-cap) selftest_cap; exit $? ;;
    --go)           : ;;
    --dry-go)
        # DRY RUN. Exercises the PRODUCTION SEQUENCE -- assembly, the warm-start
        # reconstruct/guard/decompose chain, the solve loop, the cost accounting, the
        # status write -- IN ORDER, on a stand-in seed where a defect costs nothing.
        # L-495: running the parts is not running the sequence.
        DRY=1
        DRYDIR=${2:?usage: run_r2_m1.sh --dry-go <stand-in dir built by build_r2_m1_standin.sh>}
        SEED="$DRYDIR/seed"
        WARM="$DRYDIR/warm"
        ROOT="$DRYDIR/run"
        STATUS="$ROOT/STATUS.R2_M1"
        RANKS=4
        CAP_CORE_S=600          # the dry run's OWN cap. It is NOT the registered 3300.
        ;;
    *) echo "usage: run_r2_m1.sh --go | --dry-go <stand-in dir> | --selftest-cap"
       echo "  --go            assemble and run the seven arms on the DPW5 grid, then grade"
       echo "  --dry-go <dir>  the same sequence on a stand-in seed. NOT A RESULT."
       echo "  --selftest-cap  drive the cap arithmetic, refusal and charging; no solve"
       exit 0 ;;
esac

# ⚠ THE DRY RUN MUST NEVER BE ABLE TO CREATE OR TOUCH THE REGISTERED RUN ROOT.
# Creating it would trip rule 4's guard for the real run afterwards, and -- far worse --
# would leave a directory that LOOKS like a graded run at the registered path. Asserted,
# not assumed, and in both directions so a future edit cannot quietly collapse the modes.
if [ "$DRY" -eq 1 ]; then
    [ "$ROOT" != "$REGISTERED_ROOT" ] \
        || { echo "REFUSED: --dry-go resolved to the REGISTERED run root. Refusing."; exit 2; }
    case "$ROOT" in
        "$REGISTERED_ROOT"*) echo "REFUSED: --dry-go root is inside the registered run root."; exit 2 ;;
    esac
else
    [ "$ROOT" = "$REGISTERED_ROOT" ] \
        || { echo "REFUSED: --go did not resolve to the registered run root."; exit 2; }
fi

trap 'sweep' EXIT

# ---------------------------------------------------------------- preflight

for p in "$SEED" "$WARM" "$GRADER" "$SEED/constant/polyMesh" "$WARM/processor0/$WARM_TIME"; do
    [ -e "$p" ] || { echo "MISSING SOURCE: $p"; exit 5; }
done

# Rule 4's guard: refuse a run root that already exists. A pre-existing field is not this
# run's answer, and the age guard downstream cannot tell them apart on its own.
[ -e "$ROOT" ] && { echo "RUN ROOT ALREADY EXISTS: $ROOT"; exit 3; }

# THE CAP IS DRIVEN BEFORE ANY COMPUTE IS BOUGHT. If the cap cannot be shown to stop a
# command, nothing below it is safe to start.
# IN A SUBSHELL. selftest_cap deliberately reassigns ROOT, CAP_CORE_S and SPENT_CORE_S so
# it can drive an exhausted budget; running it in this shell would leave the registered cap
# overwritten by whatever the last control set. A restore afterwards would work only for
# the variables somebody remembered to list -- the subshell is exhaustive by construction.
EXPECT_CAP=$CAP_CORE_S; EXPECT_ROOT=$ROOT      # captured BEFORE, compared AFTER
CAPLOG=$(mktemp)
if ! ( selftest_cap ) > "$CAPLOG" 2>&1; then
    cat "$CAPLOG"; rm -f "$CAPLOG"
    echo "REFUSED: the cap did not demonstrate that it stops a command."
    exit 2
fi
CAPTEST=$(cat "$CAPLOG"); rm -f "$CAPLOG"

# And assert the budget SURVIVED it, rather than trusting that it did. Compared against
# values captured before the call, so this check cannot rot when a cap or root changes.
[ "$CAP_CORE_S" -eq "$EXPECT_CAP" ] && [ "$SPENT_CORE_S" -eq 0 ] && [ "$ROOT" = "$EXPECT_ROOT" ] \
    || { echo "REFUSED: the cap selftest leaked into the run's budget (CAP=$CAP_CORE_S expected $EXPECT_CAP; SPENT=$SPENT_CORE_S; ROOT=$ROOT expected $EXPECT_ROOT)"; exit 2; }

mkdir -p "$ROOT" || exit 7
date -u +%s > "$ROOT/RUN_ROOT_CREATED_EPOCH"
printf 'name\trc\twall_s\tranks\tcore_s\n' > "$ROOT/COST.tsv"
echo "$CAPTEST" > "$ROOT/log.capselftest"
say "run root created; cap ${CAP_CORE_S} core-s, HEADLINE estimate ${ESTIMATE_CORE_MIN} core-min"
say "cap selftest: $CAPTEST"

# ⚠ THE DRY RUN LABELS ITSELF, IN ITS OWN RUN ROOT, BEFORE IT PRODUCES ANYTHING.
# The report a lane writes is read once; this file is read by whoever opens the directory.
if [ "$DRY" -eq 1 ]; then
cat > "$ROOT/DRY_RUN_NOT_A_RESULT" <<EOF
NOT A RESULT.

This directory is a DRY RUN of run_r2_m1.sh's PRODUCTION SEQUENCE against a STAND-IN SEED.
It is not R2-M1, it grades nothing, and no number in it may be quoted as a measurement of
anything on the DPW5 CRM grid.

WHAT IT DOES ESTABLISH: that the driver's steps execute IN ORDER on a case of the right
SHAPE -- assembly of seven arms from a seed, the registered per-arm mutations landing in
real dictionary text, the warm-start reconstructPar -> binary-safe guard -> decomposePar
chain, the solve loop, the cost accounting and the status write. That ORDER is what the
part-by-part controls could not cover (L-495).

WHAT IT DOES NOT COVER, AND A GREEN HERE MUST NOT BE READ AS ANY OF IT:
  - THE REAL SEED. This stand-in is a 216-cell box. The DPW5 L1.T hex grid is 638,976
    cells -- roughly 3,000x -- with max non-orthogonality 89.7134, 11,506 severe
    non-orthogonal faces, max skewness 14.0594 and max aspect ratio 14,426.8. Nothing
    about mesh quality, memory, or I/O at that size is tested here.
  - THE REAL DECOMPOSITION. This runs $RANKS subdomains; the registered run is 14.
  - THE REAL PHYSICS. These arms are expected to RUN, not to abort. R2-M1's arms abort at
    iteration <= 2 on the real grid. This dry run therefore says NOTHING about whether the
    compressible path is admissible, and its comparator verdict is meaningless: R2M1-G0 is
    a reproduction control that expects rc=136 and a thermophysical frame, and a stand-in
    that completes cannot satisfy it. G0 returning NOT A RESULT here is CORRECT BEHAVIOUR
    of the gate, not a finding about the arms.
  - THE REAL WARM-START FIELD. The warm source here is a few-hundred-kilobyte binary
    field; the real one is 15.6 MB reconstructed from 14 subdomains, and decomposePar
    -fields HAS NEVER RUN ON THE REAL GRID -- its cost is ESTIMATED, not measured, and its
    success is NOT assumed (registration sections 2.4 and 6.2).
  - THE REGISTERED CAP. This run carries its own cap of ${CAP_CORE_S} core-s, NOT the
    registered 3300 core-s (55.0 core-min).

Built by cases/committee-grids/build_r2_m1_standin.sh. Registration:
verification/campaign/RUNG2_CRM_M1_PREREGISTRATION.md. Generated $(date -u +%Y-%m-%dT%H:%M:%SZ).
EOF
say "DRY RUN: $ROOT/DRY_RUN_NOT_A_RESULT written BEFORE anything else"
fi

# OpenFOAM. `set -u` is lifted ONLY across the source line: v2606's etc/bashrc reads
# WM_PROJECT_DIR before setting it, and an unbound variable inside a SOURCED file kills the
# sourcing shell outright -- silently, with exit 1 and no output. It cost this lane a cycle
# while rehearsing the writers, and it cost RUNG0 attempt 1 before that.
set +u
# shellcheck disable=SC1091
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
if [ -z "${FOAM_APPBIN:-}" ] || ! command -v rhoSimpleFoam >/dev/null 2>&1; then
    die 4 "OpenFOAM environment did not come up (FOAM_APPBIN='${FOAM_APPBIN:-}')"
fi
say "OpenFOAM up: $(command -v rhoSimpleFoam)"

# ---------------------------------------------------------------- assemble

say "assembling seven arms from the archived compressible seed"
for arm in $ARMS; do
    assemble_arm "$arm" || die 7 "arm $arm did not assemble"
    add_writers "$ROOT/$arm" || die 7 "arm $arm: registered writer block did not land"
    et=$(endtime_for "$arm")
    [ -n "$et" ] && { set_endtime "$ROOT/$arm" "$et" || die 7 "$arm endTime"; }
done

# B0 -- reproduction control. Dictionaries otherwise untouched, endTime left at the seed's
# own value, so it reproduces the August numerics rather than a rewritten version.
md5sum "$SEED/system/fvSolution" "$ROOT/B0/system/fvSolution" > "$ROOT/B0/FVSOLUTION_MD5.txt" 2>&1
md5sum "$SEED/system/fvSchemes"  "$ROOT/B0/system/fvSchemes"  >> "$ROOT/B0/FVSOLUTION_MD5.txt" 2>&1

# B2 -- the mechanism arm. NO bounds and NO dictionary change: it must be B0's case so that
# the ONLY difference is that the FPE trap is off. Anything else and it stops being a
# measurement of B0's failure.
md5sum "$SEED/system/fvSolution" "$ROOT/B2/system/fvSolution" > "$ROOT/B2/FVSOLUTION_MD5.txt" 2>&1

add_bounds "$ROOT/B1" || die 7 "B1 bounds"                       # warm start
add_bounds "$ROOT/B5" || die 7 "B5 bounds"                       # 2x2: neither
add_bounds "$ROOT/B3" || die 7 "B3 bounds"                       # 2x2: energy alone
set_energy_enthalpy "$ROOT/B3" || die 7 "B3 energy form not switched"
add_bounds "$ROOT/B4" || die 7 "B4 bounds"                       # 2x2: transonic alone
set_transonic_yes "$ROOT/B4" || die 7 "B4 transonic not switched"
add_bounds "$ROOT/B6" || die 7 "B6 bounds"                       # 2x2: both
set_energy_enthalpy "$ROOT/B6" || die 7 "B6 energy form not switched"
set_transonic_yes  "$ROOT/B6" || die 7 "B6 transonic not switched"
say "arms assembled"

# ---------------------------------------------------------------- B1's warm start

# THE DECOMPOSITIONS DIFFER -- measured, not assumed: the archived compressible and
# incompressible cases were each decomposed with `scotch` independently. A processor-to-
# processor field copy would map the converged field onto the WRONG CELLS while looking
# perfectly healthy. The field is reconstructed onto the serial mesh and re-decomposed onto
# THIS arm's own addressing.
B1_OK=0
B1_FAIL_REASON="not attempted"
say "B1: reconstructing the archived converged incompressible field"
WARMTMP="$ROOT/B1/_warmstart_src"
mkdir -p "$WARMTMP"
cp -a "$WARM/constant" "$WARMTMP/constant" 2>/dev/null
cp -a "$WARM/system"   "$WARMTMP/system"   2>/dev/null
cp -a "$WARM/0"        "$WARMTMP/0"        2>/dev/null
for i in $(seq 0 $((RANKS-1))); do
    mkdir -p "$WARMTMP/processor$i"
    cp -a "$WARM/processor$i/constant"   "$WARMTMP/processor$i/constant"   2>/dev/null
    cp -a "$WARM/processor$i/$WARM_TIME" "$WARMTMP/processor$i/$WARM_TIME" 2>/dev/null
done

run_step "B1_reconstruct" 1 "$ROOT/B1/log.reconstructPar" \
    reconstructPar -case "$WARMTMP" -time "$WARM_TIME" -fields '(U k omega)'

if [ "${LAST_RC:-1}" -ne 0 ] || [ ! -d "$WARMTMP/$WARM_TIME" ]; then
    B1_FAIL_REASON="reconstructPar rc=${LAST_RC:-unset}, ${WARM_TIME}/ dir present=$([ -d "$WARMTMP/$WARM_TIME" ] && echo yes || echo no)"
else
    cp -f "$WARMTMP/$WARM_TIME/U"     "$ROOT/B1/0/U"
    cp -f "$WARMTMP/$WARM_TIME/k"     "$ROOT/B1/0/k"
    cp -f "$WARMTMP/$WARM_TIME/omega" "$ROOT/B1/0/omega"

    # RULE 3 ON THE GUARD, BEFORE THE GUARD IS BELIEVED. M0 recorded "FAILED TO MAP" on a
    # guard that had CRASHED, not refused -- a crashed guard's exit code is
    # indistinguishable from the failure it was watching for. This driver will not accept
    # either verdict from a guard it has not just watched discriminate.
    if ! guard_discriminates "$ROOT/B1/0/U"; then
        B1_FAIL_REASON="the warm-start guard did not discriminate; its verdict is not evidence"
    elif ! warm_guard "$ROOT/B1/0/U" 2>"$ROOT/B1/log.warmguard"; then
        B1_FAIL_REASON="the reconstructed U is missing a registered patch: $(cat "$ROOT/B1/log.warmguard")"
    else
        # decomposePar -fields HAS NEVER RUN ON THIS GRID. Its cost is ESTIMATED, not
        # measured (registration section 2.4 and 6.2), and its success is NOT assumed.
        run_step "B1_decompose_fields" 1 "$ROOT/B1/log.decomposePar" \
            decomposePar -case "$ROOT/B1" -fields -time 0
        if [ "${LAST_RC:-1}" -eq 0 ]; then
            B1_OK=1
        else
            B1_FAIL_REASON="decomposePar -fields rc=${LAST_RC:-unset} -- the re-decomposition failed"
        fi
    fi
fi
rm -rf "$WARMTMP"

if [ "$B1_OK" -eq 1 ]; then
    # ⚠ CLEAR THE FAILURE NOTE ON SUCCESS. Its initial value is "not attempted", and the
    # dry run caught it being written into STATUS as `b1_warmstart_note=not attempted`
    # BESIDE `b1_warmstart_mapped=1` -- a stale sentence contradicting the fact next to it.
    # That is this campaign's own disease: M0's WARMSTART.txt said "FAILED TO MAP" about a
    # map that had succeeded. A note that outlives the state it described is exactly how a
    # false sentence gets quoted later.
    B1_FAIL_REASON="none -- mapped"
    echo "MAPPED via reconstructPar($WARM_TIME) -> guard(binary-safe, discriminated) -> decomposePar -fields" \
        > "$ROOT/B1/WARMSTART_MAPPED"
    say "B1 warm start MAPPED and re-decomposed onto this arm's own addressing"
else
    # NOT "FAILED TO MAP". The reason is recorded verbatim, because M0's artifact said
    # "FAILED TO MAP" about a map that had already succeeded and that sentence travelled
    # up four levels unchallenged.
    echo "$B1_FAIL_REASON" > "$ROOT/B1/WARMSTART_NOT_MAPPED"
    say "B1 warm start did NOT complete: $B1_FAIL_REASON"
    say "  -> B1 will be recorded BLOCKED. R2M1-G4 is then BLOCKED, NOT a GATE FAIL:"
    say "     a remedy that could not be exercised has still not been tested."
fi

# ---------------------------------------------------------------- the solves

CAP_HIT=0
for arm in $ARMS; do
    d="$ROOT/$arm"
    if [ "$arm" = "B1" ] && [ "$B1_OK" -ne 1 ]; then
        echo "BLOCKED" > "$d/ARM_STATE.txt"
        say "$arm SKIPPED (warm start did not complete) -- BLOCKED, no core-minutes spent"
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

    if [ "$arm" = "B2" ]; then
        # THE MECHANISM ARM. With the trap off the killing step COMPLETES, so the
        # end-of-step writer records the diverged state instead of it being inferred from
        # a stack trace. rc will NOT be 136 here and that is the point, not a defect.
        say "B2: FPE TRAP OFF -- the killing step is allowed to complete and be RECORDED"
        run_step "$arm" "$RANKS" "$d/log.solve" \
            env FOAM_SIGFPE=false mpirun -np "$RANKS" rhoSimpleFoam -case "$d" -parallel
    else
        run_step "$arm" "$RANKS" "$d/log.solve" \
            mpirun -np "$RANKS" rhoSimpleFoam -case "$d" -parallel
    fi
    if [ $? -eq 66 ]; then CAP_HIT=1; echo "NOT RUN -- CAP EXHAUSTED" > "$d/ARM_STATE.txt"; continue; fi
    echo "${LAST_RC}" > "$d/rc.txt"          # rc from INSIDE the wrapper
    echo "LAUNCHED"   > "$d/ARM_STATE.txt"
    say "$arm rc=${LAST_RC}"

    # Reconstruct only if the arm actually reached its own endTime, so the grader can read
    # <case>/<endTime>/<field> and apply rule 4's field and age clauses.
    et=$(endtime_for "$arm"); [ -z "$et" ] && et=120
    if [ "${LAST_RC}" -eq 0 ] && [ -d "$d/processor0/$et" ]; then
        run_step "${arm}_reconstruct" 1 "$d/log.reconstructPar" \
            reconstructPar -case "$d" -time "$et"
    fi
done

# ---------------------------------------------------------------- grade

say "spend at grading: ${SPENT_CORE_S} core-s of ${CAP_CORE_S} ($(python3 -c "print('%.4f'%($SPENT_CORE_S/60.0))") core-min)"

# Rule 2: verify the file that is ABOUT TO RUN is the committed blob. A comparator edited
# after the freeze is not the grading path that was registered.
FROZEN_OK=0
if [ "$(cd "$REPO" && git hash-object "$GRADER_REL")" \
   = "$(cd "$REPO" && git rev-parse "HEAD:$GRADER_REL" 2>/dev/null)" ]; then
    FROZEN_OK=1
fi
echo "comparator_matches_committed_blob=$FROZEN_OK" >> "$STATUS"

run_step "selftest" 1 "$ROOT/log.selftest" python3 "$GRADER" --selftest
SELFTEST_RC=${LAST_RC:-1}

run_step "grade" 1 "$ROOT/log.grade" python3 "$GRADER" "$ROOT"
GRADE_RC=${LAST_RC:-1}

{
    [ "$DRY" -eq 1 ] && echo "DRY_RUN=1 -- NOT A RESULT, stand-in seed, see DRY_RUN_NOT_A_RESULT"
    echo "case_id=RUNG2-CRM-M1$([ "$DRY" -eq 1 ] && echo '-DRYRUN')"
    echo "prereg=verification/campaign/RUNG2_CRM_M1_PREREGISTRATION.md"
    echo "ranks=$RANKS"
    echo "spent_core_s=$SPENT_CORE_S"
    echo "spent_core_min=$(python3 -c "print('%.4f'%($SPENT_CORE_S/60.0))")"
    echo "cap_core_min=$(python3 -c "print('%.4f'%($CAP_CORE_S/60.0))")"
    echo "headline_estimate_core_min=$ESTIMATE_CORE_MIN"
    echo "cap_hit=$CAP_HIT"
    echo "b1_warmstart_mapped=$B1_OK"
    echo "b1_warmstart_note=$B1_FAIL_REASON"
    echo "selftest_rc=$SELFTEST_RC"
    echo "grade_rc=$GRADE_RC"
    echo "comparator_frozen_match=$FROZEN_OK"
} >> "$STATUS"

say "STATUS written to $STATUS"
[ "$CAP_HIT" -eq 1 ] && { say "CAP WAS HIT -- the run was STOPPED and did not get a new budget"; exit 6; }
[ "$SELFTEST_RC" -ne 0 ] && exit 2
[ "$GRADE_RC" -eq 2 ] && exit 2
exit 0
