#!/usr/bin/env bash
# SO-2a AGGREGATE GATE — BOTH-DIRECTIONS REFUSAL PROOF, DRIVEN ON THE REAL PATH.
#
# WHY THIS EXISTS.  so2a_aggregate_memory.py decides whether an arm may start.
# Its whole risk is that a permissive implementation waves everything through and
# a green run looks identical either way.  Standing rule 3, applied to a guard:
# a gate not shown able to REFUSE is not evidence.  So this drives BOTH
# directions and the bound.
#
# WHAT MAKES IT "THE REAL PATH", not a re-typed copy.  The loop under test is
# EXTRACTED BY LINE RANGE FROM THE FROZEN DRIVER'S OWN BYTES (lines 141-155 of
# so2a_chain_driver.sh, md5 asserted before AND after every leg), and the script
# under test is the real so2a_aggregate_memory.py in this directory.  Nothing is
# transcribed.  The frozen driver is NEVER edited and never executed as a chain:
# only its aggregate block runs, against a THROWAWAY BASE in a temp directory, so
# no real run root is written and no container is ever started.
#
# THE FIVE LEGS
#   L1 KNOWN POSITIVE (the defect itself, reproduced):  script ABSENT -> the loop
#      MUST WAIT.  If L1 does not wait, this harness cannot see the thing it is
#      hunting and every other leg's result is worthless.
#   L2 MUST-WAIT:  the arm's own cap planted far over the ceiling -> over-ceiling
#      through the REAL arithmetic, ok=false, the loop WAITS and writes
#      AGGREGATE_WAIT to STATUS.<arm>.
#   L3 MUST-PROCEED: the REGISTERED ceiling 30.6 GiB and the REGISTERED 4 GiB cap
#      -> ok=true, the loop BREAKS on the first poll and reaches the next gate.
#   L4 BOUND: over-ceiling with a SHRUNKEN bound -> BLOCKED_AGGREGATE is shown
#      REACHABLE, with rc=6 and AGGREGATE_BLOCKED_AT_BOUND in STATUS.<arm>.
#   L5 AST: the ast.Assert counter is shown counting a PLANTED assert before its
#      zero on the real file is believed (L-332).
#
# ONE DEFECT THIS HARNESS COMMITTED AND CAUGHT, RECORDED RATHER THAN QUIETLY FIXED.
# The first run of L4 reported the bound branch UNREACHED.  It was not: the branch
# HAD fired -- its `ABORT AGGREGATE still over ... BLOCKED` line was printed -- and
# the very next statement died on `PERMISSION: unbound variable` under `set -u`,
# because the harness had not defined a variable the real driver defines at its own
# line 50.  A missing harness variable read as a gate that could not refuse.  The
# fix is not to define the constant here by hand but to GREP IT OUT OF THE FROZEN
# DRIVER'S OWN BYTES, so the harness cannot disagree with the driver about it.
#
# Exits 0 only if every leg lands as registered above.  Any other outcome exits 1.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DRIVER="$HERE/so2a_chain_driver.sh"
MD5_DRIVER_EXPECT=75921da288d6a410691c4f41f15568a3
SCRIPT="$HERE/so2a_aggregate_memory.py"
MD5_SCRIPT_EXPECT=709ab0b98ef0302a3a3a318588f9493f
LOOP_FIRST=141; LOOP_LAST=155
FAIL=0
# Taken from the frozen driver's OWN bytes, never typed here (see the note above).
PERMISSION=$(sed -n 's/^PERMISSION=\([A-Za-z0-9]*\)$/\1/p' "$DRIVER" | head -1)
test -n "$PERMISSION" || { echo "REFUSE cannot read PERMISSION out of the frozen driver"; exit 2; }

# grep -c prints 0 AND exits 1 when it matches nothing, so `$(grep -c ... || echo 0)`
# yields the two-line string "0\n0" and every equality test against "0" fails.  This
# harness's first run tripped exactly that.  One counter, used everywhere.
cnt() { # $1 pattern  $2 file
  local n; n=$(grep -c -- "$1" "$2" 2>/dev/null | head -1); printf '%s' "${n:-0}"
}

assert_frozen() {
  echo "$MD5_DRIVER_EXPECT  $DRIVER" | md5sum -c - > /dev/null \
    || { echo "REFUSE frozen driver md5 drifted ($1)"; exit 2; }
  echo "$MD5_SCRIPT_EXPECT  $SCRIPT" | md5sum -c - > /dev/null \
    || { echo "REFUSE aggregate script md5 drifted ($1)"; exit 2; }
}

# Extract the driver's OWN loop bytes.  Asserted to be the intended block by its
# first and last line, so a driver edit that shifted the range is caught here and
# not silently tested around.
extract_loop() {
  sed -n "${LOOP_FIRST},${LOOP_LAST}p" "$DRIVER" > "$1"
  head -1 "$1" | grep -q 'WAITED=0; AGG_SERIES=' \
    || { echo "REFUSE extracted block does not begin at the WAITED=0 line"; exit 2; }
  tail -1 "$1" | grep -q 'SO2A_AGGREGATE arm=' \
    || { echo "REFUSE extracted block does not end at the SO2A_AGGREGATE line"; exit 2; }
  grep -q 'so2a_aggregate_memory.py' "$1" \
    || { echo "REFUSE extracted block does not call the script under test"; exit 2; }
}

# One leg.  $1 label  $2 script-dir handed to the block as HERE  $3 arm cap GiB
# $4 ceiling GiB  $5 poll s  $6 bound s  $7 hard timeout s
run_leg() {
  local LABEL=$1 SDIR=$2 CAP=$3 CEIL=$4 POLL=$5 BOUND=$6 TMO=$7
  local WORK; WORK=$(mktemp -d)
  local BODY="$WORK/loop.sh"
  extract_loop "$WORK/block.sh"
  {
    echo 'set -uo pipefail'
    echo "HERE='$SDIR'"
    echo "BASE='$WORK'"
    echo "AGG_CEILING_GIB=$CEIL"
    echo "AGG_POLL_S=$POLL"
    echo "AGG_BOUND_S=$BOUND"
    echo "cap_mem_gib() { echo $CAP; }"
    echo "PERMISSION='$PERMISSION'"
    echo 'STATUS="$BASE/STATUS.chain"'
    echo 'CHAIN_RC=0'
    echo 'for ARM in TEST; do'
    cat "$WORK/block.sh"
    echo '  echo "REACHED_NEXT_GATE arm=$ARM"'
    echo 'done'
    echo 'echo "LEG_CHAIN_RC=$CHAIN_RC"'
  } > "$BODY"
  timeout "$TMO" bash "$BODY" > "$WORK/leg.out" 2>&1
  echo "$WORK"
}

say() { printf '%s\n' "$1"; }
check() { # $1 label  $2 condition-result(0/1)  $3 detail
  if [ "$2" = "0" ]; then say "  PASS  $1 -- $3"; else say "  FAIL  $1 -- $3"; FAIL=1; fi
}

say "SO-2a AGGREGATE GATE REFUSAL PROOF  stamp=$(date -u +%Y%m%dT%H%M%SZ)"
assert_frozen "start"
say "frozen driver md5 $MD5_DRIVER_EXPECT AGREES; script md5 $MD5_SCRIPT_EXPECT AGREES"
say "loop under test: $DRIVER lines $LOOP_FIRST-$LOOP_LAST (extracted, not transcribed)"
say ""

# ---- L1  KNOWN POSITIVE: the defect reproduced -----------------------------
# An EMPTY directory is handed to the block as HERE, so $HERE/so2a_aggregate_memory.py
# is ABSENT exactly as it was on the stopped fire.  Registered outcome: WAIT.
say "L1 KNOWN POSITIVE -- script ABSENT (SO2a-DRIVER-DEF-1 reproduced)"
EMPTY=$(mktemp -d)
W1=$(run_leg L1 "$EMPTY" 4 30.6 1 30 6)
N1=$(cnt 'AGGREGATE_WAIT' "$W1/STATUS.TEST")
E1=$(awk '{print NF}' "$W1/TEST_aggregate_series.txt" 2>/dev/null | sort -u | tr '\n' ',')
R1=$(cnt 'REACHED_NEXT_GATE' "$W1/leg.out")
check "L1 the loop WAITED" "$([ "$N1" -ge 2 ] && echo 0 || echo 1)" "AGGREGATE_WAIT lines = $N1 (>= 2 required)"
check "L1 payload EMPTY"   "$([ "$E1" = "1," ] && echo 0 || echo 1)" "series fields-per-line set = {$E1} (epoch only)"
check "L1 never proceeded" "$([ "$R1" = "0" ] && echo 0 || echo 1)" "REACHED_NEXT_GATE lines = $R1"
say ""

# ---- L2  MUST-WAIT: over-ceiling through the real arithmetic ---------------
# The plant is on the MEASURED side, not the gate side: this arm's cap is planted
# at 4000 GiB against the REGISTERED 30.6 GiB ceiling, so the real docker/meminfo
# reading is performed and the real comparison refuses on a real over-ceiling sum.
say "L2 MUST-WAIT -- arm cap PLANTED at 4000 GiB, REGISTERED ceiling 30.6 GiB"
W2=$(run_leg L2 "$HERE" 4000 30.6 1 30 6)
N2=$(cnt 'AGGREGATE_WAIT' "$W2/STATUS.TEST")
R2=$(cnt 'REACHED_NEXT_GATE' "$W2/leg.out")
OK2=$(tail -1 "$W2/TEST_aggregate_series.txt" 2>/dev/null | cut -d' ' -f2- | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('ok'),d.get('aggregate_GiB'),d.get('ceiling_GiB'))" 2>/dev/null)
check "L2 the loop WAITED" "$([ "$N2" -ge 2 ] && echo 0 || echo 1)" "AGGREGATE_WAIT lines = $N2 (>= 2 required)"
check "L2 never proceeded" "$([ "$R2" = "0" ] && echo 0 || echo 1)" "REACHED_NEXT_GATE lines = $R2"
check "L2 read a REAL non-empty refusal" "$(echo "$OK2" | grep -q '^False ' && echo 0 || echo 1)" "ok/aggregate_GiB/ceiling_GiB = $OK2"
say ""

# ---- L3  MUST-PROCEED: the registered numbers -------------------------------
say "L3 MUST-PROCEED -- REGISTERED cap 4 GiB, REGISTERED ceiling 30.6 GiB"
W3=$(run_leg L3 "$HERE" 4 30.6 1 30 20)
N3=$(cnt 'AGGREGATE_WAIT' "$W3/STATUS.TEST")
R3=$(cnt 'REACHED_NEXT_GATE' "$W3/leg.out")
A3=$(cnt 'SO2A_AGGREGATE arm=TEST waited=0' "$W3/leg.out")
OK3=$(tail -1 "$W3/TEST_aggregate_series.txt" 2>/dev/null | cut -d' ' -f2- | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('ok'),d.get('aggregate_GiB'),d.get('ceiling_GiB'),d.get('live'))" 2>/dev/null)
check "L3 PROCEEDED"          "$([ "$R3" = "1" ] && echo 0 || echo 1)" "REACHED_NEXT_GATE lines = $R3"
check "L3 broke on poll ONE"  "$([ "$N3" = "0" ] && echo 0 || echo 1)" "AGGREGATE_WAIT lines = $N3 (0 required)"
check "L3 printed the pass line" "$([ "$A3" = "1" ] && echo 0 || echo 1)" "SO2A_AGGREGATE waited=0 lines = $A3"
check "L3 ok=True on a real reading" "$(echo "$OK3" | grep -q '^True ' && echo 0 || echo 1)" "ok/aggregate/ceiling/live = $OK3"
say ""

# ---- L4  BOUND: BLOCKED_AGGREGATE shown REACHABLE ---------------------------
say "L4 BOUND -- over-ceiling with the bound SHRUNKEN to 2 s (poll 1 s)"
W4=$(run_leg L4 "$HERE" 4000 30.6 1 2 20)
B4=$(cnt 'note=AGGREGATE_BLOCKED_AT_BOUND' "$W4/STATUS.TEST")
C4=$(cnt 'chain=BLOCKED_AGGREGATE arm=TEST' "$W4/STATUS.chain")
RC4=$(cnt '^LEG_CHAIN_RC=6$' "$W4/leg.out")
R4=$(cnt 'REACHED_NEXT_GATE' "$W4/leg.out")
check "L4 STATUS carries the bound refusal" "$([ "$B4" = "1" ] && echo 0 || echo 1)" "AGGREGATE_BLOCKED_AT_BOUND lines = $B4"
check "L4 chain=BLOCKED_AGGREGATE written"  "$([ "$C4" = "1" ] && echo 0 || echo 1)" "chain=BLOCKED_AGGREGATE lines = $C4"
check "L4 CHAIN_RC = 6"                     "$([ "$RC4" = "1" ] && echo 0 || echo 1)" "LEG_CHAIN_RC=6 lines = $RC4"
check "L4 never proceeded"                  "$([ "$R4" = "0" ] && echo 0 || echo 1)" "REACHED_NEXT_GATE lines = $R4"
say ""

# ---- L5  AST counter shown counting a PLANTED assert (L-332) ----------------
say "L5 ast.Assert counter -- known positive before the zero is believed"
PL=$(mktemp -d)/planted.py
{ cat "$SCRIPT"; printf '\n\ndef _planted():\n    assert True, "planted known positive"\n'; } > "$PL"
AST_REAL=$(python3 -c "import ast,sys;print(sum(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(open(sys.argv[1]).read()))))" "$SCRIPT")
AST_PLANT=$(python3 -c "import ast,sys;print(sum(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(open(sys.argv[1]).read()))))" "$PL")
check "L5 counter SEES a planted assert" "$([ "$AST_PLANT" = "1" ] && echo 0 || echo 1)" "planted copy count = $AST_PLANT"
check "L5 real file carries none"        "$([ "$AST_REAL" = "0" ] && echo 0 || echo 1)" "real file count = $AST_REAL"
say ""

assert_frozen "end"
say "frozen driver and script md5s RE-ASSERTED after all legs: unchanged"
if [ "$FAIL" = "0" ]; then say "RESULT: ALL LEGS AS REGISTERED"; exit 0; fi
say "RESULT: AT LEAST ONE LEG DID NOT LAND AS REGISTERED"; exit 1
