#!/usr/bin/env bash
# D5 ADDENDUM 4 CONTROLS -- D5-LAUNCHER-DEF-1, the WORK-vs-ARM container path divergence.
# ALL FIVE ARE ZERO COMPUTE.  (1)/(2) drive lines lifted VERBATIM from d5_run_arm.sh in a
# scratch subshell with planted values -- the technique Addendum 3 control (i) used on the
# EXIT trap.  (3) is a static read of the file.  (4) is the planted control ON (3)'s reader.
# (5) is the Addendum 2/3 bogus-image control on the REAL run root: the launcher aborts at
# the image digest read, exit 4, before any rm -rf, cp -a or docker run.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; L="$HERE/d5_run_arm.sh"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density
PASS=0; FAIL=0; ok(){ echo "  [OK ] $1"; PASS=$((PASS+1)); }; bad(){ echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "D5 ADDENDUM 4 CONTROLS $(date -u +%Y-%m-%dT%H:%M:%SZ) launcher_md5=$(md5sum "$L" | cut -d' ' -f1)"

# ---- (1) THE F-ARM WORK DERIVATION, lifted verbatim, must yield the REGISTERED directory.
# PREREGISTRATION.md sec.2 registers the F arm's run directory as O<density>/.
DERIV=$(grep -n '^  WORK="\$BASE/O\${DENS}"$' "$L" | head -1)
[ -n "$DERIV" ] || { bad "(1) could not lift the F-arm WORK line from the launcher"; }
out=$(ARM=F48; DENS="${ARM//[A-Z]/}"; BASE="$BASE"
      eval "$(grep -m1 '^  WORK="\$BASE/O\${DENS}"$' "$L" | sed 's/^  //')"
      echo "$WORK $(basename "$WORK")")
if [ "$out" = "$BASE/O48 O48" ]; then
  ok "(1) ARM=F48 -> WORK=$BASE/O48, WORKNAME=O48 -- the directory sec.2 REGISTERS"
else bad "(1) F-arm WORK derivation gave '$out'"; fi

# ---- (2) THE NEW GUARD, lifted verbatim, PLANTED TO FAIL twice and to pass once.
G1=$(grep -m1 '^\[ "\$WORK" = "\$BASE/\$WORKNAME" \]' "$L")
G2=$(grep -m1 '^\[ -d "\$WORK" \]' "$L")
[ -n "$G1" ] && [ -n "$G2" ] || bad "(2) could not lift the guard lines"
run_guard () { ( BASE="$1"; WORK="$2"; WORKNAME="$(basename "$WORK")"; eval "$G1"; eval "$G2"; echo GUARD_PASSED ) 2>&1; }
# (2a) PLANTED: WORK not directly under BASE -> must refuse
o=$(run_guard "$BASE" "$BASE/sub/dir"); r=$?
echo "$o" | grep -q 'ABORT D5-LAUNCHER-DEF-1 WORK=.* is not directly under BASE' && ! echo "$o" | grep -q GUARD_PASSED \
  && ok "(2a) PLANTED WORK=\$BASE/sub/dir -> guard REFUSES (not directly under BASE)" || bad "(2a) guard did not fire: $o"
# (2b) PLANTED: WORK directly under BASE but ABSENT -> must refuse.  THIS IS THE EXACT
# SHAPE THAT PRODUCED rc=127: a container working directory nothing on the host created.
o=$(run_guard "$BASE" "$BASE/F48_no_such_dir"); 
echo "$o" | grep -q 'does not exist on the host' && ! echo "$o" | grep -q GUARD_PASSED \
  && ok "(2b) PLANTED WORK absent on the host -> guard REFUSES (the rc=127 shape)" || bad "(2b) guard did not fire: $o"
# (2c) the REGISTERED F48 value must PASS -- a guard that refuses everything is not a guard.
o=$(run_guard "$BASE" "$BASE/O48")
echo "$o" | grep -q GUARD_PASSED && ! echo "$o" | grep -q ABORT \
  && ok "(2c) REGISTERED WORK=\$BASE/O48 -> guard PASSES (it does not refuse everything)" || bad "(2c) guard refused the registered value: $o"

# ---- (3) STATIC: no EXECUTABLE line still routes the container through $ARM.
N=$(grep -n '/mnt/\$ARM' "$L" | grep -v '^[0-9]*:#' | wc -l)
[ "$N" = "0" ] && ok "(3) zero EXECUTABLE lines carry /mnt/\$ARM (the defect's path)" || bad "(3) $N executable lines still carry /mnt/\$ARM"
grep -q -- '-w "/mnt/\$WORKNAME"' "$L" && grep -q 'bash /mnt/\$WORKNAME/d5_cmd.sh' "$L" \
  && ok "(3b) both container paths now read /mnt/\$WORKNAME" || bad "(3b) container paths not repaired"

# ---- (4) PLANTED CONTROL ON (3)'s READER.  A reader not shown able to see the defect is
# ---- not evidence (CLAUDE.md rule 3).  A sacrificial copy with the defect RESTORED must
# ---- make (3) come out non-zero.
MUT=$(mktemp /tmp/d5_mutated_launcher.XXXXXX.sh)
sed 's|-w "/mnt/\$WORKNAME"|-w "/mnt/$ARM"|' "$L" > "$MUT"
M=$(grep -n '/mnt/\$ARM' "$MUT" | grep -v '^[0-9]*:#' | wc -l)
[ "$M" -gt 0 ] && ok "(4) PLANTED CONTROL: the defect restored in a copy makes (3)'s reader count $M -- the reader CAN see it" \
                || bad "(4) PLANTED CONTROL FAILED: reader saw 0 on a copy carrying the defect; (3) is not evidence"
rm -f "$MUT"

# ---- (5) THE REAL LAUNCHER ON THE REAL ROOT, arm F48, bogus image (Addendum 2/3 form).
# Aborts at the image digest read, exit 4, BEFORE any rm -rf / cp -a / docker run.
LED_BEFORE=$(md5sum "$BASE/ledger.txt" | cut -d' ' -f1)
O48_BEFORE=$(stat -c '%Y' "$BASE/O48")
out=$(bash "$L" F48 no-such-image:selftest 2>&1); rc=$?
LED_AFTER=$(md5sum "$BASE/ledger.txt" | cut -d' ' -f1)
O48_AFTER=$(stat -c '%Y' "$BASE/O48")
if [ "$rc" -eq 4 ] && echo "$out" | grep -q 'ABORT cannot read digest of no-such-image:selftest'; then
  ok "(5) launcher on the real root, arm F48 -> exit 4 at the image digest read, NOTHING STAGED"
else bad "(5) rc=$rc: $(echo "$out" | tail -1)"; fi
echo "$out" | grep -q 'D4S_G_ROOT_PASS item=D5' && ok "(5b) G-ROOT.1-.3 PASS on the real r3 ledger" || bad "(5b) G-ROOT did not pass"
echo "$out" | grep -q 'D4_CAP_ASSERT arm=F48 registered_core_min=120.0 ranks=4 enforced_wall_s=1800' \
  && ok "(5c) F48 cap assert UNMOVED: 120.0 core-min / 1800 s -- this addendum moves no cap" || bad "(5c) F48 cap assert changed"
[ "$LED_BEFORE" = "$LED_AFTER" ] && ok "(5d) ledger.txt md5 UNCHANGED across the control" || bad "(5d) ledger.txt was written"
[ "$O48_BEFORE" = "$O48_AFTER" ] && ok "(5e) O48/ mtime UNCHANGED -- no staging, no rm -rf" || bad "(5e) O48/ was touched"
echo "D5 ADDENDUM 4 CONTROLS pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
