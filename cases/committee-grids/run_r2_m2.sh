#!/bin/bash
# =====================================================================================
# R2-M2 DRIVER -- NASA CRM / DPW5 L1.T hex, TWO arms (B0 reproduction, B1 warm start).
# Registration: verification/campaign/RUNG2_CRM_M2_PREREGISTRATION.md
# Grading path: cases/committee-grids/grade_r2_m2.py  (FROZEN at the prereg commit)
#
# THIS FILE LAUNCHES NOTHING BY ITSELF. It is placed by the chief under its own captured
# grant, after the cfd supervisor's check 4. A BARE invocation exits NON-ZERO (code 8) so a
# call that ran nothing can never be logged as a clean run -- see the case switch below.
#
# WHAT M2 CARRIES FROM M1, PROVEN, VERBATIM IN BEHAVIOUR (registration section 4)
# ------------------------------------------------------------------------------
#  - the binary-safe warm-start guard, driven BOTH ways at run time (warm_guard /
#    guard_discriminates), the reconstruct -> guard -> decompose chain;
#  - rc captured INSIDE the wrapper, NEVER around a setsid;
#  - the cap that has been shown to bind (--selftest-cap, M1's 7/7 pattern);
#  - the run-root guard (rule 4), and the kill SCOPED to `-case $ROOT` (never the box-wide
#    idiom that is m0's frozen hazard -- m1 already scoped it; this matches it).
#
# THE ONE DEFECT M2 FIXES (registration sections 2.3, 2.4)
# -------------------------------------------------------
#  R2-M1's B1 iterated CLEAN to Time = 50 (rc = 0, End) but wrote NO snapshot at endTime,
#  because M1's set_endtime rewrote endTime ALONE, leaving writeInterval 120 > 50 steps
#  under purgeWrite 1 -- so R2M1-G4 was a GATE FAIL on the RECORDING, not the physics.
#  endTime and writeInterval are a COUPLED PAIR. M2 replaces set_endtime with
#  set_run_window(), which rewrites BOTH members together so the run window cannot be set
#  without setting the write that captures its end; and it adds a PRE-SOLVE guard
#  (check_write_window) that REFUSES any arm whose controlDict cannot write at endTime. The
#  arm must be able to PRODUCE the evidence its gate needs.
#
# EXIT CODES
#   0  ran; the grader's verdict is in the STATUS file (a GATE FAIL is still exit 0)
#   2  the grader REFUSED, or a live control did not fire
#   3  the run root already exists -- rule 4's guard
#   4  the OpenFOAM environment did not come up
#   5  a source artifact this probe reads is missing
#   6  THE CAP WAS EXHAUSTED -- the run was STOPPED and did not get a new budget
#   7  arm assembly failed, OR the pre-solve write-window guard refused an arm (section 2.4)
#   8  invoked with no mode (bare call) or an unknown mode -- NOTHING RAN; never a clean run
# =====================================================================================
set -uo pipefail

REPO=/home/ubuntu/Certonomous
SRC=/home/ubuntu/certonomous-runs/dpw5-committee-probe          # READ ONLY. Never written.
SEED="$SRC/run_hex_base_compressible_a2.11"                     # both arms' seed
WARM="$SRC/run_hex_base_incompressible_a2.11"                   # B1's warm-start source
ROOT="$REPO/verification/runs/RUNG2_CRM_runs/M2_snapshot_admission"
GRADER="$REPO/cases/committee-grids/grade_r2_m2.py"
GRADER_REL="cases/committee-grids/grade_r2_m2.py"

RANKS=14
CAP_CORE_S=720           # 12.0 core-min, registered section 6.5. NEVER RAISED, NEVER RESET.
ESTIMATE_CORE_MIN=6.32   # HEADLINE, incurred regardless of outcome. Conditional is separate.
SPENT_CORE_S=0
WARM_TIME=200

ARMS="B0 B1"
STATUS="$ROOT/STATUS.R2_M2"

# Per-arm endTime. B0 keeps the SEED's own value (empty == leave the controlDict alone,
# endTime 120, writeInterval 120 -- already coupled). B1 is the only admission arm.
endtime_for() {
    case "$1" in
        B0) echo "" ;;      # empty == leave the seed's controlDict alone (endTime 120)
        B1) echo 50 ;;      # THE ONLY ADMISSION ARM
        *)  echo "" ;;
    esac
}

say() { echo "[$(date -u +%H:%M:%SZ)] $*"; }

# ⚠ SCOPED TO THIS RUN'S OWN ROOT, AND THE SCOPE IS THE POINT (carried from M1).
# The child's command line carries `-case <ROOT>/<arm>`, so keying on $ROOT kills this
# probe's arms and NOTHING ELSE on the box -- not another team's rhoSimpleFoam, and not the
# driver's own shell. CLAUDE.md's standing instruction is DO NOT TOUCH RUNNING SOLVERS.
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
# THE CAP. One total, recomputed before every step, charged after every step. Carried
# from M1 unchanged -- it is the M1 7/7 --selftest-cap pattern.
# =====================================================================================

budget_left_core_s() { echo $((CAP_CORE_S - SPENT_CORE_S)); }

# timeout_for <ranks> -- the wall-second timeout the REMAINING budget buys at <ranks>.
# THE FLOOR OF 1 s IS NOT TIDYING: `timeout 0s` means NO LIMIT AT ALL (coreutils treats a
# zero duration as "never time out"). Integer division makes 0 the natural result exactly
# when the budget is nearly exhausted, which would hand the solver an UNLIMITED run at the
# moment there is no budget to pay for it -- a runaway wearing the costume of a cap. The
# floor makes an exhausted budget produce a STOP; run_step's `left <= 0` refuses first.
timeout_for() {
    local ranks=$1 left; left=$(budget_left_core_s)
    local to=$(( left / ranks ))
    [ "$to" -lt 1 ] && to=1          # NEVER 0 -- see the runaway note above
    echo "$to"
}

# run_step <name> <ranks> <logfile> -- command...
# Returns 66 -- WITHOUT RUNNING THE COMMAND -- when the cap is already exhausted.
# rc is captured on the line IMMEDIATELY after the command, inside this wrapper. It is
# never taken around a `setsid`: `setsid timeout cmd` exits 0 for every outcome.
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
# --selftest-cap : DRIVE THE CAP (M1's 7/7 pattern). The arithmetic, the refusal and the
# charging are made observable, and it costs nothing.
# -------------------------------------------------------------------------------------
selftest_cap() {
    local tmp fails=0
    tmp=$(mktemp -d)
    ROOT="$tmp"                     # so COST.tsv writes land somewhere harmless
    printf 'name\trc\twall_s\tranks\tcore_s\n' > "$ROOT/COST.tsv"

    _chk() { if [ "$2" -eq 0 ]; then echo "PASS $1  $3"; else echo "FAIL $1  $3"; fails=$((fails+1)); fi; }

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

    # K2 -- THE REFUSAL, WITHOUT RUNNING THE COMMAND. Planted witness must not appear.
    CAP_CORE_S=100; SPENT_CORE_S=100
    local witness="$tmp/witness_must_not_exist"
    run_step "capped" 14 "$tmp/log.capped" touch "$witness"
    local rc=$?
    [ "$rc" -eq 66 ] && [ ! -e "$witness" ]
    _chk K2 $? "exhausted cap returns 66 and the command DID NOT RUN (witness absent=$([ ! -e "$witness" ] && echo yes || echo NO))"

    # K3 -- the same command RUNS when budget remains.
    CAP_CORE_S=1000; SPENT_CORE_S=0
    run_step "uncapped" 14 "$tmp/log.uncapped" touch "$witness"
    [ "${LAST_RC}" -eq 0 ] && [ -e "$witness" ]
    _chk K3 $? "with budget left the command RUNS (witness present=$([ -e "$witness" ] && echo yes || echo NO)), rc=${LAST_RC}"

    # K4 -- CHARGING. Spend must rise by wall x ranks.
    CAP_CORE_S=100000; SPENT_CORE_S=0
    run_step "charge" 14 "$tmp/log.charge" sleep 2
    [ "$SPENT_CORE_S" -ge 28 ]
    _chk K4 $? "a 2 wall-s step at 14 ranks charged ${SPENT_CORE_S} core-s (>= 28)"

    # K5 -- the timeout ACTUALLY FIRES and the rc says so (124 on expiry).
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
# THE COUPLED-SETTING FIX (registration section 2.3) AND THE PRE-SOLVE GUARD (section 2.4).
# =====================================================================================

# set_run_window <controlDict> <endTime> -- rewrites endTime AND its COUPLED PARTNER
# writeInterval TOGETHER (registration section 2.3), so the run window cannot be set without
# setting the write that captures its end. Under purgeWrite 1 a snapshot lands at endTime
# only if writeInterval coincides with the final step; rewriting endTime alone (M1's defect,
# GATE FAIL on R2M1-G4) silently defeats the write. writeInterval := nsteps gives EXACTLY
# ONE snapshot, at the final step -- no per-step I/O tax.
#
# Two on-disk refusals, both stronger than a bare `assert` (which vanishes under python -O
# -- a guard that can vanish is not a guard, L-221/L-222 in spirit):
#   (1) writeInterval must be in [1, nsteps] so it captures endTime;
#   (2) the function-object writers' own INDENTED writeInterval lines must be UNTOUCHED --
#       section 2.3 relies on count=1 catching the top-level line first (top-level keys
#       precede the functions sub-dict in a controlDict); this makes that reliance
#       self-checking rather than trusting the comment.
set_run_window() {
    python3 - "$1" "$2" <<'PY'
import re, sys
p, et = sys.argv[1], float(sys.argv[2])
s0 = open(p).read()
indented_before = len(re.findall(r"^[ \t]+writeInterval\s+[0-9.eE+-]+\s*;", s0, re.M))
m = re.search(r"^\s*deltaT\s+([0-9.eE+-]+)\s*;", s0, re.M)
dt = float(m.group(1)) if m else 1.0
nsteps = int(round(et / dt))                       # steps from startTime 0 to endTime
if nsteps < 1:
    raise SystemExit("run window < one step in %s" % p)
s, n1 = re.subn(r"^(\s*endTime\s+)[0-9.eE+-]+\s*;",      r"\g<1>%s;" % et,     s0, count=1, flags=re.M)
s, n2 = re.subn(r"^(\s*writeInterval\s+)[0-9.eE+-]+\s*;", r"\g<1>%d;" % nsteps, s,  count=1, flags=re.M)
if n1 != 1 or n2 != 1:
    raise SystemExit("run window not fully rewritten (endTime=%d writeInterval=%d) in %s" % (n1, n2, p))
open(p, "w").write(s)
t = open(p).read()
wi = int(re.search(r"^\s*writeInterval\s+([0-9]+)\s*;", t, re.M).group(1))   # first == top-level
if not (1 <= wi <= nsteps):
    raise SystemExit("writeInterval %d does not capture endTime (nsteps %d) in %s" % (wi, nsteps, p))
indented_after = len(re.findall(r"^[ \t]+writeInterval\s+[0-9.eE+-]+\s*;", t, re.M))
if indented_after != indented_before:
    raise SystemExit("set_run_window disturbed a function-object writeInterval in %s (%d -> %d)"
                     % (p, indented_before, indented_after))
PY
}

# check_write_window <controlDict> -- the PRE-SOLVE guard (registration section 2.4). Exit 0
# iff a snapshot at endTime is POSSIBLE for this arm: 1 <= (top-level) writeInterval <=
# round((endTime - startTime) / deltaT). M1's arm was assembled with a controlDict that
# could not write, and nothing noticed. This driver notices.
check_write_window() {
    python3 - "$1" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
def firstnum(key):
    m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % key, s, re.M)
    return float(m.group(1)) if m else None
et = firstnum("endTime"); st = firstnum("startTime"); dt = firstnum("deltaT")
st = 0.0 if st is None else st
m = re.search(r"^\s*writeInterval\s+([0-9]+)\s*;", s, re.M)   # first == top-level
wi = int(m.group(1)) if m else None
if et is None or dt is None or dt == 0 or wi is None:
    sys.stderr.write("write-window guard: missing endTime/deltaT/writeInterval in %s\n" % p)
    raise SystemExit(1)
nsteps = int(round((et - st) / dt))
if not (1 <= wi <= nsteps):
    sys.stderr.write("write-window guard REFUSES %s: writeInterval %d not in [1,%d] -- "
                     "cannot write at endTime\n" % (p, wi, nsteps))
    raise SystemExit(1)
raise SystemExit(0)
PY
}

# -------------------------------------------------------------------------------------
# --selftest-window : DRIVE set_run_window AND check_write_window in BOTH directions, on
# controlDicts of the seed's shape (top-level writeInterval + an INDENTED function-object
# writeInterval). No solver. This is the M2 analogue of "a cap shown to bind".
# -------------------------------------------------------------------------------------
selftest_window() {
    local tmp fails=0 rc
    tmp=$(mktemp -d)
    _wchk() { if [ "$2" -eq 0 ]; then echo "PASS $1  $3"; else echo "FAIL $1  $3"; fails=$((fails+1)); fi; }

    make_cd() {  # seed-shaped: top-level writeInterval 120, functions block w/ indented 1
        cat > "$1" <<'EOF'
application     rhoSimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         120;
deltaT          1;
writeControl    timeStep;
writeInterval   120;
purgeWrite      1;
functions
{
    forceCoeffs
    {
        writeControl    timeStep;
        writeInterval   1;
    }
}
EOF
    }

    # WW0 -- set_run_window couples: endTime 50 => top-level writeInterval 50, indented 1 kept.
    make_cd "$tmp/cd0"
    set_run_window "$tmp/cd0" 50 2>"$tmp/err0"; rc=$?
    local top indent et0
    top=$(grep -m1 -E '^writeInterval' "$tmp/cd0" | grep -oE '[0-9]+' | head -1)
    et0=$(grep -m1 -E '^endTime' "$tmp/cd0" | grep -oE '[0-9.]+' | head -1)
    indent=$(grep -cE '^[[:space:]]+writeInterval[[:space:]]+1;' "$tmp/cd0")
    { [ "$rc" -eq 0 ] && [ "$top" = "50" ] && [ "$indent" -eq 1 ]; }
    _wchk WW0 $? "set_run_window(50): top-level writeInterval=$top (want 50), endTime=$et0, function-object writeInterval 1 preserved=$indent (want 1)"

    # WW1 -- the coupled dict PASSES the pre-solve guard (50 <= 50).
    check_write_window "$tmp/cd0" 2>"$tmp/errg0"; _wchk WW1 $? "coupled controlDict (writeInterval 50, nsteps 50) PASSES the pre-solve guard"

    # WW2 -- M1's EXACT DEFECT (endTime rewritten alone, writeInterval left 120 > 50) REFUSED.
    make_cd "$tmp/cd1"
    sed -i 's/^endTime         120;/endTime         50;/' "$tmp/cd1"    # emulate M1's set_endtime
    if check_write_window "$tmp/cd1" 2>"$tmp/errg1"; then rc=1; else rc=0; fi
    _wchk WW2 $rc "M1's defect (endTime 50, writeInterval 120 > 50 steps) is REFUSED by the pre-solve guard"

    # WW3 -- B0's untouched seed (writeInterval 120 == 120 steps) PASSES.
    make_cd "$tmp/cd2"
    check_write_window "$tmp/cd2" 2>"$tmp/errg2"; _wchk WW3 $? "B0's untouched seed (writeInterval 120 == 120 steps) PASSES"

    # WW4 -- set_run_window refuses a window shorter than one step (endTime 0 => nsteps 0).
    make_cd "$tmp/cd3"
    if set_run_window "$tmp/cd3" 0 2>"$tmp/err3"; then rc=1; else rc=0; fi
    _wchk WW4 $rc "set_run_window refuses a run window shorter than one step (endTime 0)"

    rm -rf "$tmp"
    echo "WINDOW SELFTEST: $([ $fails -eq 0 ] && echo PASS || echo FAIL) -- $((5-fails))/5 controls fired."
    return $fails
}

# =====================================================================================
# THE BINARY-SAFE WARM-START GUARD, and the control that must pass before it is trusted.
# Carried from M1 verbatim in behaviour (registration section 4.1/4.2).
# =====================================================================================

warm_guard() {
    python3 - "$1" <<'PY'
import sys
# Reads BYTES so a `writeFormat binary` field cannot crash it into a false verdict. M0 read
# this file in TEXT mode and died of UnicodeDecodeError before it could test anything.
data = open(sys.argv[1], 'rb').read()
missing = [p for p in (b"wall", b"symmetry", b"farfield") if p not in data]
if missing:
    sys.stderr.write("warm-start field lost patch %s\n" % missing[0].decode())
    raise SystemExit(1)
raise SystemExit(0)
PY
}

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

# The registered writer block (registration section 4.4). The registered object is INSERTED,
# never substituted for what is there (L-221/L-222). The seed's own forceCoeffs object is
# left as M1 left it -- this probe reads NO force claim from it (grade_r2_m2.py has no force
# reader), so its presence in the solve is immaterial to the verdict.
add_writers() {
    python3 - "$1/system/controlDict" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
fo = """
    r2m2MinMax
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
if "r2m2MinMax" not in open(p).read():
    raise SystemExit("writer block did not land in %s" % p)
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

# =====================================================================================
# MAIN
# =====================================================================================

REGISTERED_ROOT="$ROOT"

case "${1:-}" in
    --selftest-cap)    selftest_cap;    exit $? ;;
    --selftest-window) selftest_window; exit $? ;;
    --go)              : ;;
    *) {
         echo "usage: run_r2_m2.sh --go | --selftest-cap | --selftest-window"
         echo "  --go               assemble and run B0 (reproduction) and B1 (warm start)"
         echo "                     on the DPW5 grid, then grade. LAUNCHES A SOLVER."
         echo "  --selftest-cap     drive the cap arithmetic, refusal and charging; no solve"
         echo "  --selftest-window  drive set_run_window and the pre-solve write-window"
         echo "                     guard in both directions; no solve"
         echo ""
         echo "REFUSED: no mode given. Nothing ran. A bare call exits 8, NEVER 0, so it can"
         echo "         never be logged as a clean run that never happened (M1 launcher trap)."
       } >&2
       exit 8 ;;
esac

# --go from here.
[ "$ROOT" = "$REGISTERED_ROOT" ] \
    || { echo "REFUSED: --go did not resolve to the registered run root." >&2; exit 2; }

trap 'sweep' EXIT

# ---------------------------------------------------------------- preflight

for p in "$SEED" "$WARM" "$GRADER" "$SEED/constant/polyMesh" "$WARM/processor0/$WARM_TIME"; do
    [ -e "$p" ] || { echo "MISSING SOURCE: $p"; exit 5; }
done

# Rule 4's guard: refuse a run root that already exists.
[ -e "$ROOT" ] && { echo "RUN ROOT ALREADY EXISTS: $ROOT"; exit 3; }

# THE CAP IS DRIVEN BEFORE ANY COMPUTE IS BOUGHT, in a SUBSHELL (selftest_cap reassigns
# ROOT/CAP/SPENT to drive an exhausted budget; a subshell keeps that from leaking).
EXPECT_CAP=$CAP_CORE_S; EXPECT_ROOT=$ROOT
CAPLOG=$(mktemp)
if ! ( selftest_cap ) > "$CAPLOG" 2>&1; then
    cat "$CAPLOG"; rm -f "$CAPLOG"
    echo "REFUSED: the cap did not demonstrate that it stops a command."
    exit 2
fi
CAPTEST=$(cat "$CAPLOG"); rm -f "$CAPLOG"
[ "$CAP_CORE_S" -eq "$EXPECT_CAP" ] && [ "$SPENT_CORE_S" -eq 0 ] && [ "$ROOT" = "$EXPECT_ROOT" ] \
    || { echo "REFUSED: the cap selftest leaked into the run's budget (CAP=$CAP_CORE_S expected $EXPECT_CAP; SPENT=$SPENT_CORE_S; ROOT=$ROOT expected $EXPECT_ROOT)"; exit 2; }

# THE WRITE-WINDOW GUARD IS ALSO DRIVEN BEFORE ANY COMPUTE. It is the whole point of M2:
# an arm assembled with a controlDict that cannot write at endTime must be caught, and the
# guard itself must be shown to accept a coupled dict AND refuse a broken one.
WINLOG=$(mktemp)
if ! ( selftest_window ) > "$WINLOG" 2>&1; then
    cat "$WINLOG"; rm -f "$WINLOG"
    echo "REFUSED: the write-window guard did not demonstrate that it refuses a controlDict "
    echo "         that cannot write at endTime (M1's exact defect)."
    exit 2
fi
WINTEST=$(cat "$WINLOG"); rm -f "$WINLOG"

mkdir -p "$ROOT" || exit 7
date -u +%s > "$ROOT/RUN_ROOT_CREATED_EPOCH"
printf 'name\trc\twall_s\tranks\tcore_s\n' > "$ROOT/COST.tsv"
echo "$CAPTEST" > "$ROOT/log.capselftest"
echo "$WINTEST" > "$ROOT/log.windowselftest"
say "run root created; cap ${CAP_CORE_S} core-s, HEADLINE estimate ${ESTIMATE_CORE_MIN} core-min"
say "cap selftest: $CAPTEST"
say "window selftest: $WINTEST"

# OpenFOAM. `set -u` is lifted ONLY across the source line: v2606's etc/bashrc reads
# WM_PROJECT_DIR before setting it, and an unbound variable inside a SOURCED file kills the
# sourcing shell outright -- silently, exit 1, no output.
set +u
# shellcheck disable=SC1091
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
if [ -z "${FOAM_APPBIN:-}" ] || ! command -v rhoSimpleFoam >/dev/null 2>&1; then
    die 4 "OpenFOAM environment did not come up (FOAM_APPBIN='${FOAM_APPBIN:-}')"
fi
say "OpenFOAM up: $(command -v rhoSimpleFoam)"

# ---------------------------------------------------------------- assemble

say "assembling two arms (B0 reproduction, B1 warm start) from the archived compressible seed"
for arm in $ARMS; do
    assemble_arm "$arm" || die 7 "arm $arm did not assemble"
    add_writers "$ROOT/$arm" || die 7 "arm $arm: registered writer block did not land"
    et=$(endtime_for "$arm")
    # THE COUPLED FIX: set_run_window rewrites endTime AND writeInterval together (section
    # 2.3). B0's empty et leaves the seed's already-coupled controlDict alone.
    [ -n "$et" ] && { set_run_window "$ROOT/$arm/system/controlDict" "$et" || die 7 "$arm run window"; }
done

# B0 -- reproduction control. endTime left at the seed's own value (120), writeInterval
# already coupled (120 == 120). It reproduces the August numerics rather than a rewrite.
md5sum "$SEED/system/fvSolution" "$ROOT/B0/system/fvSolution" > "$ROOT/B0/FVSOLUTION_MD5.txt" 2>&1
md5sum "$SEED/system/fvSchemes"  "$ROOT/B0/system/fvSchemes"  >> "$ROOT/B0/FVSOLUTION_MD5.txt" 2>&1

add_bounds "$ROOT/B1" || die 7 "B1 bounds"                       # warm start, bounded

# THE PRE-SOLVE WRITE-WINDOW GUARD (section 2.4). AFTER assembly, BEFORE any solve: every
# arm's controlDict must be able to write a snapshot at endTime. M1's arm could not, and
# nothing noticed; this driver refuses (exit 7) rather than pay for an ungradeable arm.
for arm in $ARMS; do
    if ! check_write_window "$ROOT/$arm/system/controlDict" 2>"$ROOT/$arm/log.writewindow"; then
        cat "$ROOT/$arm/log.writewindow"
        die 7 "$arm controlDict cannot write at endTime -- refusing to pay for an arm that "\
"cannot produce the evidence its gate needs (registration section 2.4)"
    fi
    say "$arm write-window guard: PASS -- a snapshot at endTime is possible"
done
say "arms assembled and write-window-checked"

# ---------------------------------------------------------------- B1's warm start
# The decompositions differ; the field is reconstructed onto the serial mesh and
# re-decomposed onto THIS arm's own addressing. Carried from M1 verbatim in behaviour.

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

    # RULE 3 ON THE GUARD, BEFORE THE GUARD IS BELIEVED. A crashed guard's exit code is
    # indistinguishable from the failure it watches for (M0's disease). This driver will not
    # accept either verdict from a guard it has not just watched discriminate.
    if ! guard_discriminates "$ROOT/B1/0/U"; then
        B1_FAIL_REASON="the warm-start guard did not discriminate; its verdict is not evidence"
    elif ! warm_guard "$ROOT/B1/0/U" 2>"$ROOT/B1/log.warmguard"; then
        B1_FAIL_REASON="the reconstructed U is missing a registered patch: $(cat "$ROOT/B1/log.warmguard")"
    else
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
    # CLEAR THE FAILURE NOTE ON SUCCESS -- a note that outlives the state it described is how
    # a false sentence gets quoted later (M0's "FAILED TO MAP" about a map that succeeded).
    B1_FAIL_REASON="none -- mapped"
    echo "MAPPED via reconstructPar($WARM_TIME) -> guard(binary-safe, discriminated) -> decomposePar -fields" \
        > "$ROOT/B1/WARMSTART_MAPPED"
    say "B1 warm start MAPPED and re-decomposed onto this arm's own addressing"
else
    echo "$B1_FAIL_REASON" > "$ROOT/B1/WARMSTART_NOT_MAPPED"
    say "B1 warm start did NOT complete: $B1_FAIL_REASON"
    say "  -> B1 will be recorded BLOCKED. R2M2-G3 is then BLOCKED, NOT a GATE FAIL."
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

    # THE AGE GUARD'S ANCHOR. `0/T` is touched LAST at launch, so it dates the run allowed to
    # produce this answer. Every field at endTime must end up newer than it.
    touch "$d/0/T"
    for i in $(seq 0 $((RANKS-1))); do touch "$d/processor$i/0/T"; done

    run_step "$arm" "$RANKS" "$d/log.solve" \
        mpirun -np "$RANKS" rhoSimpleFoam -case "$d" -parallel
    if [ $? -eq 66 ]; then CAP_HIT=1; echo "NOT RUN -- CAP EXHAUSTED" > "$d/ARM_STATE.txt"; continue; fi
    echo "${LAST_RC}" > "$d/rc.txt"          # rc from INSIDE the wrapper
    echo "LAUNCHED"   > "$d/ARM_STATE.txt"
    say "$arm rc=${LAST_RC}"

    # Reconstruct only if the arm actually reached its own endTime, so the grader can read
    # <case>/<endTime>/<field> and apply rule 4's field and age clauses. With the coupled
    # fix, B1 that reaches Time=50 now HAS processor0/50 to reconstruct (M1 did not).
    et=$(endtime_for "$arm"); [ -z "$et" ] && et=120
    if [ "${LAST_RC}" -eq 0 ] && [ -d "$d/processor0/$et" ]; then
        run_step "${arm}_reconstruct" 1 "$d/log.reconstructPar" \
            reconstructPar -case "$d" -time "$et"
    fi
done

# ---------------------------------------------------------------- grade

say "spend at grading: ${SPENT_CORE_S} core-s of ${CAP_CORE_S} ($(python3 -c "print('%.4f'%($SPENT_CORE_S/60.0))") core-min)"

# Rule 2: verify the file ABOUT TO RUN is the committed blob. A comparator edited after the
# freeze is not the grading path that was registered. HEAD captured once for both sides.
FROZEN_OK=0
H=$(cd "$REPO" && git rev-parse HEAD 2>/dev/null)
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
    echo "case_id=RUNG2-CRM-M2"
    echo "prereg=verification/campaign/RUNG2_CRM_M2_PREREGISTRATION.md"
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
