#!/bin/bash
# =============================================================================
# W3-A3 PIN-GUARD CONTROL -- ZERO COMPUTE, BOTH DIRECTIONS.
#
# Drives d12y_w3_chain_driver.sh's OWN md5 assertion (the `MD5_GRADER` line and
# the `md5sum -c` line beside it) in both directions.  Sanaa's standing
# directives section 1 / L-314: a guard shown only to pass is not shown to be a
# guard.  CLAUDE.md rule 3: a reader not shown able to see a NON-match is not
# evidence.
#
# THE ASSERTION IS NOT RETYPED.  The harness is the driver's OWN first N bytes,
# cut at the grader-assertion line and byte-asserted identical to the driver, so
# it cannot keep passing after the driver drifts.  The launcher and the grader
# are reached by SYMLINK, so md5sum reads the REAL files' bytes; only the STATUS
# file lands in the sandbox.  NOTHING IS LAUNCHED: the harness stops at the line
# after the guard.
#
# Legs:
#   P1  extraction control -- the driver contains EXACTLY ONE grader assertion
#       line and EXACTLY ONE MD5_GRADER assignment, else REFUSE (never a zero)
#   P2  harness prefix is BYTE-IDENTICAL to the driver's prefix
#   P3  correct pin + real grader          -> rc=0, GUARD_PASSED, no drift line
#   P4  pin deliberately WRONG             -> rc=4, reason=grader_md5_drifted
#   P5  pin correct, GRADER BYTES PLANTED  -> rc=4  (the guard reads the FILE,
#       not merely its own constant -- the planted control)
#   P6  P4/P5's rc=4 is the GRADER limb, not the launcher limb
# =============================================================================
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
DRIVER="$HERE/d12y_w3_chain_driver.sh"
TMPD="${1:-/tmp/d12y_w3_pin_guard_control}"
PASS=0; FAIL=0
chk () { if [ "$2" = "1" ]; then PASS=$((PASS+1)); echo "  PASS  $1"; else FAIL=$((FAIL+1)); echo "  FAIL  $1"; fi; }

test -f "$DRIVER" || { echo "ABORT no driver at $DRIVER"; exit 4; }

# ---- P1 extraction control: refuse rather than report a clean zero
NASSERT=$(grep -c '^echo "\$MD5_GRADER  \$GRADEPY" | md5sum -c -' "$DRIVER")
NPIN=$(grep -c '^MD5_GRADER=' "$DRIVER")
[ "$NASSERT" = "1" ] && [ "$NPIN" = "1" ] || {
  echo "ABORT extraction found assert=$NASSERT pin=$NPIN (expected 1/1) -- REFUSING rather than reporting a zero"; exit 4; }
chk "P1 driver holds exactly one MD5_GRADER pin and one grader assertion (extraction is live)" 1

LN=$(grep -n '^echo "\$MD5_GRADER  \$GRADEPY" | md5sum -c -' "$DRIVER" | cut -d: -f1)
rm -rf "$TMPD"; mkdir -p "$TMPD"
head -n "$LN" "$DRIVER" > "$TMPD/harness.sh"
printf 'echo GUARD_PASSED\nexit 0\n' >> "$TMPD/harness.sh"
chmod +x "$TMPD/harness.sh"
ln -sf "$HERE/d12y_w3_stage_and_run.sh" "$TMPD/d12y_w3_stage_and_run.sh"
ln -sf "$HERE/d12y_grade_w3.py"         "$TMPD/d12y_grade_w3.py"

# ---- P2 the harness prefix IS the driver's bytes
A=$(head -n "$LN" "$DRIVER" | md5sum | cut -d' ' -f1)
B=$(head -n "$LN" "$TMPD/harness.sh" | md5sum | cut -d' ' -f1)
chk "P2 harness prefix byte-identical to driver lines 1-$LN ($A)" "$([ "$A" = "$B" ] && echo 1 || echo 0)"

cnt () { # grep -c prints 0 AND exits 1 on no-match; `|| echo 0` would emit TWO values.
  # Measured: that bug failed this control's own leg P6 on 2026-08-28 before repair.
  local n; n=$(grep -c "$1" "$2" 2>/dev/null); [ -n "$n" ] || n=0; echo "${n%%%%$'\n'*}"; }
run () { # $1 = harness path -> prints rc
  rm -f "$(dirname "$1")/STATUS.W3_chain"
  ( bash "$1" >"$(dirname "$1")/out.txt" 2>&1 ); echo $?
}

# ---- P3 correct pin, real grader bytes
RC3=$(run "$TMPD/harness.sh")
OK3=$(grep -c '^GUARD_PASSED$' "$TMPD/out.txt")
DR3=$(cnt 'grader_md5_drifted' "$TMPD/STATUS.W3_chain")
chk "P3 correct pin + REAL grader -> rc=0, GUARD_PASSED, zero drift lines (rc=$RC3 marker=$OK3 drift=$DR3)" \
    "$([ "$RC3" = 0 ] && [ "$OK3" = 1 ] && [ "$DR3" = 0 ] && echo 1 || echo 0)"

# ---- P4 deliberately wrong pin
mkdir -p "$TMPD/wrongpin"
sed 's/^MD5_GRADER=.*/MD5_GRADER=00000000000000000000000000000000/' "$TMPD/harness.sh" > "$TMPD/wrongpin/harness.sh"
ln -sf "$HERE/d12y_w3_stage_and_run.sh" "$TMPD/wrongpin/d12y_w3_stage_and_run.sh"
ln -sf "$HERE/d12y_grade_w3.py"         "$TMPD/wrongpin/d12y_grade_w3.py"
RC4=$(run "$TMPD/wrongpin/harness.sh")
DR4=$(cnt 'reason=grader_md5_drifted' "$TMPD/wrongpin/STATUS.W3_chain")
OK4=$(grep -c '^GUARD_PASSED$' "$TMPD/wrongpin/out.txt")
chk "P4 WRONG pin -> rc=4 reason=grader_md5_drifted, and GUARD_PASSED never printed (rc=$RC4 drift=$DR4 marker=$OK4)" \
    "$([ "$RC4" = 4 ] && [ "$DR4" -ge 1 ] && [ "$OK4" = 0 ] && echo 1 || echo 0)"

# ---- P5 correct pin, PLANTED grader bytes: the guard reads the FILE
mkdir -p "$TMPD/plantedgrader"
cp "$TMPD/harness.sh" "$TMPD/plantedgrader/harness.sh"
ln -sf "$HERE/d12y_w3_stage_and_run.sh" "$TMPD/plantedgrader/d12y_w3_stage_and_run.sh"
cp -a "$HERE/d12y_grade_w3.py" "$TMPD/plantedgrader/d12y_grade_w3.py"
printf '\n# planted byte -- W3-A3 pin-guard control leg P5\n' >> "$TMPD/plantedgrader/d12y_grade_w3.py"
RC5=$(run "$TMPD/plantedgrader/harness.sh")
DR5=$(cnt 'reason=grader_md5_drifted' "$TMPD/plantedgrader/STATUS.W3_chain")
chk "P5 correct pin + PLANTED grader bytes -> rc=4 grader_md5_drifted (the guard reads the FILE) (rc=$RC5 drift=$DR5)" \
    "$([ "$RC5" = 4 ] && [ "$DR5" -ge 1 ] && echo 1 || echo 0)"

# ---- P6 the rc=4 is the GRADER limb, not the launcher limb
L4=$(cnt 'launcher_md5_drifted' "$TMPD/wrongpin/STATUS.W3_chain")
L5=$(cnt 'launcher_md5_drifted' "$TMPD/plantedgrader/STATUS.W3_chain")
chk "P6 P4/P5 fired the GRADER limb, not the launcher limb (launcher drift lines $L4/$L5 = 0/0)" \
    "$([ "$L4" = 0 ] && [ "$L5" = 0 ] && echo 1 || echo 0)"

echo "== W3-A3 PIN-GUARD CONTROL pass=$PASS fail=$FAIL driver_md5=$(md5sum "$DRIVER" | cut -d' ' -f1) =="
[ "$FAIL" = 0 ] || exit 2
