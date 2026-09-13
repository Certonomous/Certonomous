#!/bin/bash
# D6R3 ADDENDUM 1 -- CONTROLS FOR THE THREE REPAIRED LAUNCH PRECONDITIONS.
# Each is driven to its FAILING side against a KNOWN-BAD case tree.  A guard that has never said
# no is not a guard.  These are LAUNCH PRECONDITIONS, not grading gates: they can only prevent a
# run from starting, never change how a completed run is graded.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085
SRC="$ROOT/mesh/L2"
TMP=$(mktemp -d /tmp/d6r3_ctl_XXXX)
PASS=0; FAIL=0
run(){ # name, want_rc, mutation
  local name="$1" want="$2" mut="$3"
  rm -rf "$TMP/case"; cp -r "$SRC" "$TMP/case" >/dev/null 2>&1
  eval "$mut"
  D6R3_DRYRUN=1 CASE_OVERRIDE="$TMP/case" ARM_OVERRIDE="$TMP/arm" \
    bash "$HERE/d6r3_run_arm_ctl.sh" CTL 1 0 4 >"$TMP/out" 2>&1
  local got=$?
  if [ "$got" -eq "$want" ]; then printf "  PASS  rc=%-3s %s\n" "$got" "$name"; PASS=$((PASS+1))
  else printf "  FAIL  rc=%-3s (want %s) %s\n" "$got" "$want" "$name"; FAIL=$((FAIL+1))
       sed -n '1,6p' "$TMP/out" | sed 's/^/          /'; fi
}
# a launcher variant whose CASE/ARM come from the environment, so the controls touch no real root
sed -e 's|^CASE=.*|CASE="${CASE_OVERRIDE:?}"|' \
    -e 's|^ARMDIR=.*|ARMDIR="${ARM_OVERRIDE:?}"; LOG=/dev/null; LEDGER=/dev/null|' \
    -e 's|^ROOT=.*|ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085|' \
    "$HERE/d6r3_run_arm.sh" > "$HERE/d6r3_run_arm_ctl.sh"
sed -i 's|^\[ ! -d "\$ARMDIR" \]|rm -rf "$ARMDIR"; [ ! -d "$ARMDIR" ]|' "$HERE/d6r3_run_arm_ctl.sh"
echo "D6R3 LAUNCH-PRECONDITION CONTROLS"
run "clean: a complete case tree passes every precondition and stops at DRYRUN" 0 "true"
run "KNOWN-BAD/G-INPUTS: 0.orig removed -- the exact P0 18:58:42Z defect, which must now REFUSE" 7 \
    "rm -rf \"\$TMP/case/0.orig\""
run "KNOWN-BAD/G-INPUTS: constant/polyMesh/points removed" 7 \
    "rm -f \"\$TMP/case/constant/polyMesh/points\" \"\$TMP/case/constant/polyMesh/points.gz\""
run "KNOWN-BAD/G-INPUTS: system/fvSchemes removed" 7 "rm -f \"\$TMP/case/system/fvSchemes\""
run "KNOWN-BAD/G-INPUTS: one initial field (p) removed from 0.orig" 7 \
    "rm -f \"\$TMP/case/0.orig/p\""

# --- G-DATUM, driven directly on the EXACT case statement extracted from the launcher, because
# --- G-INPUTS now guarantees 0/U exists and the tree controls can no longer reach it.
echo
echo "G-DATUM -- the empty-age-datum refusal, driven on the launcher's own case statement"
GD=$(sed -n '/^case "\$DATUM" in$/,/^esac$/p' "$HERE/d6r3_run_arm.sh")
[ -n "$GD" ] || { echo "  FAIL  could not extract the G-DATUM case statement from the launcher"; FAIL=$((FAIL+1)); }
gd(){ # value, want_rc
  local DATUM="$1" want="$2" desc="$3"
  local got
  ( say(){ :; }; eval "$GD"; exit 0 ) >/dev/null 2>&1; got=$?
  if [ "$got" -eq "$want" ]; then printf "  PASS  rc=%-3s %s\n" "$got" "$desc"; PASS=$((PASS+1))
  else printf "  FAIL  rc=%-3s (want %s) %s\n" "$got" "$want" "$desc"; FAIL=$((FAIL+1)); fi
}
gd ""            8 "KNOWN-BAD/MEASURED: DATUM EMPTY -- exactly what the failed P0 printed, and it did NOT stop"
gd "   "         8 "KNOWN-BAD: DATUM whitespace"
gd "notanumber"  8 "KNOWN-BAD: DATUM non-numeric"
gd "1789315938"  0 "clean: a real epoch datum passes"
gd "0"           0 "boundary: DATUM=0 is numeric and passes -- the guard tests readability, not value"

rm -rf "$TMP"
echo
echo "D6R3_LAUNCH_CONTROLS n_total=$((PASS+FAIL)) n_pass=$PASS n_fail=$FAIL"
[ "$FAIL" -eq 0 ] && echo "D6R3_LAUNCH_CONTROLS PASS" || echo "D6R3_LAUNCH_CONTROLS FAIL"
exit $FAIL
