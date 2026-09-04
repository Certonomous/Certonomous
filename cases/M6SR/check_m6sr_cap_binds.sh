#!/usr/bin/env bash
# =========================================================================================
# check_m6sr_cap_binds.sh -- ITEM 39's REPAIR, KEPT EXECUTABLE.
#
# WHAT THIS SUITE IS FOR.  Amendment 14 §20.3 measured that an outer `timeout` IS NOT A CAP ON
# A CONTAINER: it SIGTERMs the docker CLIENT, the client proxies to the container's `bash -c`,
# that `bash` is waiting on a foreground child and does not act, and `timeout` THEN WAITS.
# A 3 s cap on a 60 s container returned rc 124 AFTER 61 WALL SECONDS; under an UNBOUNDED
# payload the wrapper NEVER RETURNED AT ALL.  Rule 12's "an overrun stops the run" was
# therefore FALSE for every containerised step in this campaign -- including `B2`'s 70 core-min
# cap and `B5c`'s 1,630 core-min cap.
#
# THE REPAIR UNDER TEST, IN THREE LIMBS THAT ARE ONLY A CAP TOGETHER:
#   (1) `timeout -k <grace> <cap>s` on the client  -- bounds THE CLIENT.
#   (2) an UNCONDITIONAL `docker kill` + `rm -f` on the RECORDED container name
#                                                 -- bounds THE CONTAINER.
#   (3) an overrun branch accepting **124 AND 137** -- 137 is the rc a `-k` SIGKILL produces
#       and is the NORMAL rc for a real containerised overrun on this box.  A branch testing
#       only 124 MISSES EVERY REAL OVERRUN (the item-35 trap).
#
# HOW IT AVOIDS TESTING ITSELF.  This suite does NOT reimplement the mechanism.  It EXTRACTS
# THE DRIVERS' OWN LINES -- `docker_timeout_q()`, `docker_q()`, the grace constant, both kill
# lines and the overrun branch condition -- from a COMMENT-STRIPPED view, and runs THOSE
# against REAL containers on the PINNED digest.  A mutation to either driver drives this RED.
# Reading a comment-stripped view is load-bearing and is MEASURED to be (see K1'), because both
# drivers now contain long comments DESCRIBING the fix that a whole-file grep would accept.
#
# ⚠ EVERY CONTAINER THIS SUITE STARTS IS ITSELF BOUND BY THE MECHANISM UNDER TEST, plus a
# belt-and-braces sweep at the end.  Two consecutive earlier passes were bitten by the very
# unboundedness they were measuring (284 container-seconds in one).  Container-seconds are
# accumulated and reported as WASTE, separately, never absorbed.
#
# ⚠ THE UNBOUNDED PAYLOAD IS `while :; do sleep 1; done`, NOT A BUSY LOOP.  It is unbounded in
# exactly the way that matters -- pid 1 is a `bash` blocked on a foreground child, which is the
# signal-handling path the whole finding turns on -- but it does NOT burn a core.  The box is
# NOT idle (heat-transfer's T3e holds 8 ranks of 16).  This is a deliberate substitution and it
# is named rather than buried.
#
# EXIT: 0 all checks passed / 1 a check FAILED / 2 REFUSAL (a precondition; never a silent skip)
# =========================================================================================
set +e
set +u

HERE=$(cd "$(dirname "$0")" && pwd)
DRIVER_L1="$HERE/build_m6sr_l1.sh"
DRIVER_B5="$HERE/run_m6sr_b5.sh"
IMG_PINNED=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35

WORK=$(mktemp -d -t m6sr_cap_check.XXXXXX) || { echo "REFUSE: no scratch dir" >&2; exit 2; }
trap 'rm -rf "$WORK"' EXIT

PASS=0; FAIL=0
ok(){   PASS=$((PASS+1)); printf '  PASS  %s\n' "$1"; }
bad(){  FAIL=$((FAIL+1)); printf '  FAIL  %s\n' "$1"; }
note(){ printf '  ....  %s\n' "$1"; }
# ⚠ A REFUSAL GOES TO STDERR AND IS ADDITIONALLY `|| exit 2` AT EVERY CALL SITE INSIDE `$( )`.
# `refuse` inside a command substitution exits only the SUBSHELL, and a message on stdout would
# be CAPTURED AS THE VALUE -- a refusal captured as a value is not a refusal.
refuse(){ printf 'REFUSE: %s\n' "$1" >&2; exit 2; }

CONTAINER_S=0
NAME_PREFIX="m6cap"

# -----------------------------------------------------------------------------------------
# 0.  PRECONDITIONS.  Each is a REFUSAL, never a skip that prints green.
# -----------------------------------------------------------------------------------------
[ -f "$DRIVER_L1" ] || refuse "driver under test is ABSENT: $DRIVER_L1"
[ -f "$DRIVER_B5" ] || refuse "driver under test is ABSENT: $DRIVER_B5"
DOCKER_BIN=$(command -v docker 2>/dev/null)
[ -n "$DOCKER_BIN" ] || refuse "docker does not resolve on PATH"
"$DOCKER_BIN" inspect --format '{{.Id}}' "$IMG_PINNED" >/dev/null 2>&1 \
  || refuse "the PINNED IMAGE $IMG_PINNED is not on this daemon. This suite does NOT fall back to a mock: a mock has no docker client to SIGTERM and therefore cannot exhibit the defect at all."

# The comment-stripped views ALSO have leading indentation removed, so a `^` anchor below
# addresses the statement and not its position inside a function body.  Line NUMBERS are
# preserved (this is a substitution, not a deletion), which K1'' relies on.
CODE_L1="$WORK/code_l1.sh"; grep -vE '^[[:space:]]*#' "$DRIVER_L1" | sed 's/^[[:space:]]*//' > "$CODE_L1"
CODE_B5="$WORK/code_b5.sh"; grep -vE '^[[:space:]]*#' "$DRIVER_B5" | sed 's/^[[:space:]]*//' > "$CODE_B5"
[ -s "$CODE_L1" ] && [ -s "$CODE_B5" ] || refuse "stripping comments left no code -- the extraction is broken"

# extract_line: EXACTLY ONE matching CODE line, or refuse.  Leading whitespace is stripped.
extract_line(){   # $1 = code view, $2 = ERE
  local n; n=$(grep -cE "$2" "$1")
  [ "$n" = "1" ] || refuse "expected exactly ONE code line matching /$2/ in $1, found $n. This suite EXECUTES the driver's own line; it will not substitute its own."
  grep -E "$2" "$1" | sed 's/^[[:space:]]*//'
}
extract_fn(){     # $1 = driver, $2 = fn name -- from the COMMENT-STRIPPED view
  awk -v f="$2" '$0 ~ "^"f"\\(\\)\\{" {p=1} p {print} p && /^\}/ {exit}' "$1"
}

# T0.  THE SUITE'S OWN REFUSAL MECHANISM IS PLANTED AND READ BACK BEFORE ANYTHING RESTS ON IT.
_X=$(extract_line "$CODE_L1" '^__M6SR_NO_SUCH_CODE_LINE__' 2>/dev/null); _XRC=$?
{ [ "$_XRC" = "2" ] && [ -z "$_X" ]; } \
  || refuse "THE SUITE'S OWN REFUSAL MECHANISM IS BROKEN: an unmatchable extraction returned rc '$_XRC' and value '${_X:-<empty>}'. It must return rc 2 and NOTHING."
echo "refusal mechanism: an unmatchable extraction returns rc 2 and no value (planted, read back)"
echo

# -----------------------------------------------------------------------------------------
# K1.  COUPLING -- ALL THREE LIMBS ARE IN BOTH DRIVERS' **CODE**, NOT ONLY IN THEIR COMMENTS.
# -----------------------------------------------------------------------------------------
echo "K1  the three limbs are present in CODE, in BOTH drivers"
for pair in "L1:$CODE_L1" "B5:$CODE_B5"; do
  TAG=${pair%%:*}; CV=${pair#*:}
  extract_line "$CV" '^CAP_KILL_GRACE_S=[0-9]+$' >/dev/null || exit 2
  N_K=$(grep -cE 'timeout -k "\$\{CAP_KILL_GRACE_S\}"s' "$CV")
  [ "$N_K" = "2" ] \
    && ok "K1a/$TAG limb 1: \`timeout -k\` is on BOTH invocation branches (bare and sg), $N_K code sites" \
    || bad "K1a/$TAG limb 1: expected \`timeout -k\` on both branches (2 code sites), found $N_K"
  extract_line "$CV" '^docker_q kill "\$cname"' >/dev/null || exit 2
  extract_line "$CV" '^docker_q rm -f "\$cname"' >/dev/null || exit 2
  ok "K1b/$TAG limb 2: an UNCONDITIONAL \`docker_q kill\` + \`rm -f\` on the recorded name \$cname"
  extract_line "$CV" '^if \[ "\$rc" -eq 124 \] \|\| \[ "\$rc" -eq 137 \]; then$' >/dev/null || exit 2
  ok "K1c/$TAG limb 3: the overrun branch accepts 124 OR 137"
  extract_line "$CV" '^cname="m6sr_\$\{tag\}_\$\$"$' >/dev/null || exit 2
  ok "K1d/$TAG the container name is BOUND TO A VARIABLE before the run, so the kill has something to aim at"
done

# K1'.  AND READING A COMMENT-STRIPPED VIEW IS LOAD-BEARING -- MEASURED, NOT ASSERTED.
W_L1=$(grep -cE 'timeout -k' "$DRIVER_L1"); C_L1=$(grep -cE 'timeout -k' "$CODE_L1")
[ "$W_L1" -gt "$C_L1" ] \
  && ok "K1' the comment-stripped view MATTERS: \`timeout -k\` appears $W_L1 times in build_m6sr_l1.sh but only $C_L1 times in its CODE. A whole-file grep would be satisfied by the PROSE DESCRIBING the fix" \
  || bad "K1' expected the driver to mention \`timeout -k\` in prose more often than in code (whole-file $W_L1, code $C_L1); the comment-stripping control is a NO-OP here and must not be reported as a control"

# K1''.  THE UNCONDITIONAL KILL IS NOT INSIDE THE OVERRUN BRANCH.  Guarding it would restore
# the defect in a form that every text-presence check above would still accept.
for pair in "L1:$CODE_L1" "B5:$CODE_B5"; do
  TAG=${pair%%:*}; CV=${pair#*:}
  KL=$(grep -nE '^[[:space:]]*docker_q kill "\$cname"' "$CV" | cut -d: -f1)
  BL=$(grep -nE '^[[:space:]]*if \[ "\$rc" -eq 124 \]' "$CV" | cut -d: -f1)
  { [ -n "$KL" ] && [ -n "$BL" ] && [ "$KL" -lt "$BL" ]; } \
    && ok "K1''/$TAG the kill (code line $KL) precedes the overrun branch (code line $BL), so it runs on EVERY path -- it is not guarded by the rc" \
    || bad "K1''/$TAG the kill must precede and sit outside the overrun branch (kill '$KL', branch '$BL')"
done
echo

# -----------------------------------------------------------------------------------------
# 2.  THE HARNESS.  Assembled FROM THE DRIVER'S OWN EXTRACTED LINES, in the driver's order.
#     Variants mutate exactly ONE limb each.
# -----------------------------------------------------------------------------------------
GRACE_LINE=$(extract_line "$CODE_L1" '^CAP_KILL_GRACE_S=[0-9]+$')       || exit 2
KILL1=$(extract_line "$CODE_L1" '^docker_q kill "\$cname"')             || exit 2
KILL2=$(extract_line "$CODE_L1" '^docker_q rm -f "\$cname"')            || exit 2
BRANCH=$(extract_line "$CODE_L1" '^if \[ "\$rc" -eq 124 \] \|\| \[ "\$rc" -eq 137 \]; then$') || exit 2
FN_Q=$(extract_fn "$CODE_L1" docker_q)
FN_TQ=$(extract_fn "$CODE_L1" docker_timeout_q)
[ -n "$FN_Q" ] && [ -n "$FN_TQ" ] || refuse "could not extract docker_q()/docker_timeout_q() from the driver's code view"
GRACE=${GRACE_LINE#*=}

build_harness(){   # $1 = real | nok | nokill | no137
  local v="$1" out="$WORK/h_$1.sh"
  {
    echo 'DOCKER_BRANCH=bare'
    echo "DOCKER_BIN='$DOCKER_BIN'"
    echo "IMG_PINNED='$IMG_PINNED'"
    echo "$GRACE_LINE"
    echo "$FN_Q"
    if [ "$v" = "nok" ]; then
      # MUTANT: limb 1 removed -- a bare `timeout`, exactly the pre-repair shape.
      printf '%s\n' "$FN_TQ" | sed 's/timeout -k "${CAP_KILL_GRACE_S}"s /timeout /'
    else
      printf '%s\n' "$FN_TQ"
    fi
    cat <<'EOS'
cap_run(){
  local tag="$1" tmo="$2" payload="$3"
  local cname rc t0 t1 wall OVERRUN
  cname="m6cap_${tag}_$$"
  t0=$(date +%s)
  docker_timeout_q "$tmo" run --rm --name "$cname" "$IMG_PINNED" bash -c "$payload" >/dev/null 2>&1
  rc=$?
  t1=$(date +%s); wall=$((t1-t0))
EOS
    if [ "$v" != "nokill" ]; then
      printf '  %s >/dev/null 2>&1\n' "$KILL1"
      printf '  %s >/dev/null 2>&1\n' "$KILL2"
    fi   # MUTANT nokill: limb 2 removed -- nothing ends the container.
    if [ "$v" = "no137" ]; then
      # MUTANT: limb 3 narrowed to the pre-repair condition.
      echo '  if [ "$rc" -eq 124 ]; then OVERRUN=FIRED; else OVERRUN=NOTFIRED; fi'
    else
      printf '  %s OVERRUN=FIRED; else OVERRUN=NOTFIRED; fi\n' "$BRANCH"
    fi
    echo '  echo "rc=$rc wall=$wall overrun=$OVERRUN cname=$cname"'
    echo '}'
  } > "$out"
  bash -n "$out" || refuse "assembled harness '$v' is not valid bash"
  echo "$out"
}

H_REAL=$(build_harness real)     || exit 2
H_NOK=$(build_harness nok)       || exit 2
H_NOKILL=$(build_harness nokill) || exit 2
H_NO137=$(build_harness no137)   || exit 2

# EVERY MUTANT MUST DIFFER FROM THE REAL HARNESS.  A mutant identical to the control is a
# NO-OP dressed as a test, and would print green while proving nothing.
for M in "$H_NOK:nok" "$H_NOKILL:nokill" "$H_NO137:no137"; do
  cmp -s "$H_REAL" "${M%%:*}" \
    && bad "MUTANT ${M##*:} is BYTE-IDENTICAL to the real harness -- it is a NO-OP CONTROL and proves nothing" \
    || ok "mutant ${M##*:} differs from the control harness (the mutation actually applied)"
done
echo

BOUNDED_PAYLOAD='sleep 2; echo INSIDE_OK'
UNBOUNDED_PAYLOAD='while :; do sleep 1; done'
CAP=3
LEFT_UP(){ "$DOCKER_BIN" ps --filter "name=${NAME_PREFIX}_" --filter status=running --format '{{.Names}}' | grep -c . ; }
SWEEP(){ for c in $("$DOCKER_BIN" ps -aq --filter "name=${NAME_PREFIX}_"); do "$DOCKER_BIN" rm -f "$c" >/dev/null 2>&1; done; }

# -----------------------------------------------------------------------------------------
# K2.  THE KNOWN-POSITIVE.  ⚠ WITHOUT THIS EVERY NEGATIVE BELOW IS WORTHLESS: a mechanism that
#      kills everything would pass every "it was stopped" check.  A container that finishes
#      INSIDE its cap must return CLEANLY, with rc 0, and must NOT be reported as an overrun.
# -----------------------------------------------------------------------------------------
echo "K2  KNOWN-POSITIVE -- a container that finishes inside its cap"
T0=$(date +%s)
R=$(. "$H_REAL"; cap_run pos 20 "$BOUNDED_PAYLOAD")
T1=$(date +%s); CONTAINER_S=$((CONTAINER_S + T1 - T0))
P_RC=$(echo "$R" | sed 's/.*rc=\([0-9]*\) .*/\1/'); P_W=$(echo "$R" | sed 's/.*wall=\([0-9]*\) .*/\1/')
P_OV=$(echo "$R" | sed 's/.*overrun=\([A-Z]*\) .*/\1/')
{ [ "$P_RC" = "0" ] && [ "$P_OV" = "NOTFIRED" ]; } \
  && ok "K2 a 2 s container under a 20 s cap returned rc $P_RC in ${P_W}s and the overrun branch did NOT fire. THE READER CAN SEE A SUCCESS -- the mechanism does not simply kill everything, so the negatives below mean something" \
  || bad "K2 KNOWN-POSITIVE FAILED (rc '$P_RC', wall ${P_W}s, overrun '$P_OV'). Every negative in this suite is void until a success is visible"
LU=$(LEFT_UP)
[ "$LU" = "0" ] && ok "K2' docker ps shows $LU containers left Up after the known-positive" \
                || bad "K2' $LU container(s) left Up after a container that completed on its own"
echo

# -----------------------------------------------------------------------------------------
# K3.  **BEFORE** -- THE DEFECT, RE-MEASURED.  A bare `timeout` (the `nok` harness, which IS
#      the pre-repair shape) on an UNBOUNDED payload.  ⚠ THIS IS THE ONE THING IN THIS SUITE
#      THAT CANNOT BE ALLOWED TO RUN FREE: it is the defect itself.  It is launched in the
#      BACKGROUND under this suite's OWN hard deadline and the container is killed by name.
# -----------------------------------------------------------------------------------------
echo "K3  BEFORE -- the pre-repair shape (bare \`timeout\`, no -k) on an UNBOUNDED payload"
DEADLINE=25
T0=$(date +%s)
( . "$H_NOK"; cap_run before "$CAP" "$UNBOUNDED_PAYLOAD" ) > "$WORK/before.out" 2>&1 &
BPID=$!
BEFORE_RET=""
for _i in $(seq 1 $DEADLINE); do
  kill -0 "$BPID" 2>/dev/null || { BEFORE_RET=$(( $(date +%s) - T0 )); break; }
  sleep 1
done
if [ -z "$BEFORE_RET" ]; then
  B_ELAPSED=$(( $(date +%s) - T0 ))
  B_UP=$(LEFT_UP)
  kill -9 "$BPID" 2>/dev/null; wait "$BPID" 2>/dev/null
  SWEEP
  T1=$(date +%s); CONTAINER_S=$((CONTAINER_S + T1 - T0))
  ok "K3 BEFORE, THE DEFECT REPRODUCES: under a ${CAP}s cap the pre-repair wrapper HAD STILL NOT RETURNED after ${B_ELAPSED}s (a LOWER BOUND -- this suite stopped waiting; it did not stop being blocked), with $B_UP container(s) still Up. This is the shape that carried B2's 70 core-min and B5c's 1,630 core-min caps"
  BEFORE_TXT=">${B_ELAPSED}s (never returned; suite deadline)"
else
  T1=$(date +%s); CONTAINER_S=$((CONTAINER_S + T1 - T0))
  SWEEP
  bad "K3 the pre-repair shape RETURNED in ${BEFORE_RET}s under a ${CAP}s cap. If a bare \`timeout\` now bounds a container on this daemon, the whole item-39 finding must be RE-MEASURED before the repair is believed"
  BEFORE_TXT="${BEFORE_RET}s"
fi
echo

# -----------------------------------------------------------------------------------------
# K4.  **AFTER** -- THE REAL TEST.  The SAME unbounded payload, the SAME cap, through the
#      driver's own repaired lines.  It must be STOPPED, bounded by cap+grace, and leave
#      ZERO containers Up.
# -----------------------------------------------------------------------------------------
echo "K4  AFTER -- the repaired mechanism on the SAME unbounded payload"
T0=$(date +%s)
R=$(. "$H_REAL"; cap_run after "$CAP" "$UNBOUNDED_PAYLOAD")
T1=$(date +%s); CONTAINER_S=$((CONTAINER_S + T1 - T0))
A_RC=$(echo "$R" | sed 's/.*rc=\([0-9]*\) .*/\1/'); A_W=$(echo "$R" | sed 's/.*wall=\([0-9]*\) .*/\1/')
A_OV=$(echo "$R" | sed 's/.*overrun=\([A-Z]*\) .*/\1/')
BOUND=$((CAP + GRACE + 5))
{ [ "$A_W" -le "$BOUND" ]; } \
  && ok "K4a BOUNDED: the wrapper returned in ${A_W}s under a ${CAP}s cap with a ${GRACE}s grace (bound cap+grace+5 = ${BOUND}s). BEFORE: $BEFORE_TXT" \
  || bad "K4a NOT BOUNDED: wall ${A_W}s exceeds cap+grace+5 = ${BOUND}s"
{ [ "$A_RC" = "124" ] || [ "$A_RC" = "137" ]; } \
  && ok "K4b the outer rc is $A_RC ($([ "$A_RC" = 124 ] && echo 'client exited on SIGTERM at the cap' || echo 'client SIGKILLed by `timeout -k` at cap+grace'))" \
  || bad "K4b expected outer rc 124 or 137 on an overrun; got '$A_RC'"
[ "$A_OV" = "FIRED" ] \
  && ok "K4c THE OVERRUN BRANCH FIRED on rc $A_RC -- rule 12's 'an overrun stops the run' is delivered" \
  || bad "K4c the overrun branch did NOT fire on rc $A_RC. The run would have continued past its cap"
A_UP=$(LEFT_UP)
[ "$A_UP" = "0" ] \
  && ok "K4d docker ps shows $A_UP containers left Up -- the CONTAINER was ended, not merely the client" \
  || bad "K4d $A_UP container(s) still Up after the cap fired. The client returned but the container survived -- this is the defect, not the repair"
echo

# -----------------------------------------------------------------------------------------
# K5.  THE MUTANTS.  ONE PER LIMB.  Each must drive this suite RED, and **HOW** it dies is
#      reported, not merely THAT it did.
# -----------------------------------------------------------------------------------------
echo "K5  MUTATION -- one per limb; each must break the cap in its OWN way"

# M-1  limb 1 removed (`-k` dropped).  Expect: the client is never bounded -> no return.
T0=$(date +%s)
( . "$H_NOK"; cap_run m1 "$CAP" "$UNBOUNDED_PAYLOAD" ) > "$WORK/m1.out" 2>&1 &
MPID=$!; M1_RET=""
for _i in $(seq 1 $((CAP + GRACE + 6))); do
  kill -0 "$MPID" 2>/dev/null || { M1_RET=$(( $(date +%s) - T0 )); break; }
  sleep 1
done
M1_EL=$(( $(date +%s) - T0 )); M1_UP=$(LEFT_UP)
kill -9 "$MPID" 2>/dev/null; wait "$MPID" 2>/dev/null; SWEEP
T1=$(date +%s); CONTAINER_S=$((CONTAINER_S + T1 - T0))
[ -z "$M1_RET" ] \
  && ok "M-1 (limb 1, \`-k\` DROPPED) DIED CORRECTLY -- and HOW: the wrapper NEVER RETURNED. At the cap+grace+6 = $((CAP+GRACE+6))s deadline it was still blocked (${M1_EL}s, $M1_UP container(s) Up), where the real harness returned in ${A_W}s. \`timeout\` without -k does not bound the CLIENT at all, so K4a's wall bound is violated by an unbounded margin" \
  || bad "M-1 was a NO-OP CONTROL: dropping \`-k\` still returned in ${M1_RET}s. Limb 1 is not load-bearing on this daemon and must be re-measured"

# M-2  limb 2 removed (unconditional kill dropped).  Expect: client returns, CONTAINER SURVIVES.
T0=$(date +%s)
R2=$(. "$H_NOKILL"; cap_run m2 "$CAP" "$UNBOUNDED_PAYLOAD")
M2_RC=$(echo "$R2" | sed 's/.*rc=\([0-9]*\) .*/\1/'); M2_W=$(echo "$R2" | sed 's/.*wall=\([0-9]*\) .*/\1/')
M2_UP=$(LEFT_UP)
SWEEP; T1=$(date +%s); CONTAINER_S=$((CONTAINER_S + T1 - T0))
[ "$M2_UP" -ge 1 ] \
  && ok "M-2 (limb 2, UNCONDITIONAL KILL DROPPED) DIED CORRECTLY -- and HOW: the client returned rc $M2_RC in ${M2_W}s, looking exactly like a clean bounded overrun, but $M2_UP container(s) were STILL Up afterwards. K4d goes RED. This is the precise reason the kill must not be guarded by the rc: THE CLIENT'S RETURN TELLS YOU NOTHING ABOUT THE CONTAINER" \
  || bad "M-2 was a NO-OP CONTROL: with the kill removed, $M2_UP containers were left Up. Something else is reaping them and limb 2 is not load-bearing here"

# M-3  limb 3 narrowed (137 dropped).  Expect: the real overrun rc misses the branch.
T0=$(date +%s)
R3=$(. "$H_NO137"; cap_run m3 "$CAP" "$UNBOUNDED_PAYLOAD")
M3_RC=$(echo "$R3" | sed 's/.*rc=\([0-9]*\) .*/\1/'); M3_OV=$(echo "$R3" | sed 's/.*overrun=\([A-Z]*\) .*/\1/')
SWEEP; T1=$(date +%s); CONTAINER_S=$((CONTAINER_S + T1 - T0))
if [ "$M3_RC" = "137" ] && [ "$M3_OV" = "NOTFIRED" ]; then
  ok "M-3 (limb 3, 137 DROPPED) DIED CORRECTLY -- and HOW: the overrun produced rc $M3_RC and the narrowed branch did NOT fire (overrun=$M3_OV). K4c goes RED. The run would have sailed past its cap and then aborted at exit 6 on the INNER rc with a misleading cause -- the item-35 trap exactly"
elif [ "$M3_RC" = "124" ]; then
  bad "M-3 was a NO-OP CONTROL on this run: the overrun returned rc 124, which the narrowed branch still catches. The 137 limb is untested here and must not be reported as proven"
else
  bad "M-3 unexpected: rc '$M3_RC', overrun '$M3_OV'"
fi
echo

# -----------------------------------------------------------------------------------------
# K6.  THE LADDER RUN TREE MUST NOT EXIST.  ⚠ PLANTED AT THE EXACT SEARCHED PATH FIRST: a
#      reader not shown able to see a PRESENT tree cannot be trusted to report an ABSENT one.
# -----------------------------------------------------------------------------------------
REPO=$(cd "$HERE/../.." && pwd)
RUNS="$REPO/verification/runs/M6SR_runs"
SEEN_PRESENT=no
mkdir -p "$RUNS/_plant" 2>/dev/null && [ -d "$RUNS" ] && SEEN_PRESENT=yes
rm -rf "$RUNS" 2>/dev/null
if [ "$SEEN_PRESENT" = "yes" ] && [ ! -e "$RUNS" ]; then
  ok "K6 the run tree $RUNS is ABSENT -- and the check is LIVE: it saw the planted directory at that exact path immediately before, then saw it gone. NO LADDER COMPUTE WAS RUN"
else
  bad "K6 the absence check is not trustworthy (planted-visible=$SEEN_PRESENT, still-exists=$([ -e "$RUNS" ] && echo yes || echo no))"
fi

# -----------------------------------------------------------------------------------------
FINAL_UP=$("$DOCKER_BIN" ps -a --filter "name=${NAME_PREFIX}_" --format '{{.Names}}' | tr '\n' ' ')
[ -z "$FINAL_UP" ] \
  && ok "SWEEP no container this suite started is left on the daemon (running or exited)" \
  || bad "SWEEP containers left behind: $FINAL_UP"

echo
echo "container-seconds spent by this suite: ${CONTAINER_S}s  <- WASTE, reported separately, never absorbed into a step's cost"
echo "checks: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
