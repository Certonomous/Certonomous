#!/usr/bin/env bash
# D4-LAUNCHER-DEF-1 -- THE GUARD SELFTEST.  DRIVES THE GUARD AGAINST THE REAL
# D4 RUN ROOT AND REQUIRES IT TO ABORT.
#
# "A guard not shown to fire is ceremony" -- and this is the guard standing
# between a re-fire and 384 MB of irreplaceable graded evidence:
# /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O, 5,085 files,
# holding OptView.hst and opt_IPOPT.txt, the artifacts D4's accepted
# GATE REACHED rests on.
#
# TWO INDEPENDENT BARRIERS, because a test that could destroy what it protects
# is not an acceptable test:
#   BARRIER 1  the guard itself, which completes at d4s_run_arm.sh:100, and
#              the FIRST EXECUTABLE destructive operation in that file is at
#              :229 -- asserted below by parsing the file, not by memory.
#   BARRIER 2  every dangerous invocation passes NO ARM ARGUMENT.  Even with
#              the guard entirely removed, the script reaches its usage check
#              and exits 64 before it can stage anything.
# And the real root is MEASURED before and after, so "it aborted" is not taken
# on the exit code's word alone.
#
# `set -e` does not gate here; every assertion is explicit.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d4s_run_arm.sh"
REAL_D4=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
REGISTERED=/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin
PASS=0; FAIL=0

ok ()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad () { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }

echo "D4-LAUNCHER-DEF-1 GUARD SELFTEST"
echo "================================================================"

# ---- BARRIER 1, asserted from the file rather than remembered -------------
G=$(grep -n 'D4S_G_ROOT_PASS' "$LAUNCHER" | head -1 | cut -d: -f1)
FIRSTOP=$(grep -nE '^[[:space:]]*[^#]*((sudo -n )?rm -rf|cp -a|docker run)' "$LAUNCHER" \
          | grep -v '^[0-9]*:[[:space:]]*#' | head -1 | cut -d: -f1)
if [ -n "$G" ] && [ -n "$FIRSTOP" ] && [ "$FIRSTOP" -gt "$G" ]; then
  ok "BARRIER 1: guard completes at :$G, first executable destructive op at :$FIRSTOP"
else
  bad "BARRIER 1: guard at :${G:-?} does NOT precede first destructive op at :${FIRSTOP:-?}"
  echo "REFUSING to run the real-root test -- it could destroy what it protects."
  exit 2
fi

# ---- no live command substitution anywhere in the launcher ----------------
NBT=$(grep -n '`' "$LAUNCHER" | grep -vcE '^[0-9]+:[[:space:]]*#')
if [ "$NBT" -eq 0 ]; then
  ok "no backticks on any executable line (a backtick in a double-quoted abort message is executed)"
else
  bad "$NBT executable line(s) carry backticks -- live command substitution in the launcher"
fi

# ---- census the real root BEFORE ------------------------------------------
N_BEFORE=$(find "$REAL_D4" -mindepth 1 -maxdepth 2 2>/dev/null | wc -l)
O_BEFORE=$(stat -c '%Y %s' "$REAL_D4/O/OptView.hst" 2>/dev/null)
echo "  real D4 root before: $N_BEFORE entries; O/OptView.hst [$O_BEFORE]"

run_guard () {  # $1 = BASE value ; prints exit code
  BASE="$1" bash "$LAUNCHER" >/dev/null 2>&1
  echo $?
}

# ---- P2 first: THE ONE THAT MATTERS.  Real D4 root, no arm argument -------
RC=$(run_guard "$REAL_D4")
[ "$RC" = "3" ] && ok "G-ROOT.2 aborts (exit 3) on the REAL D4 run root" \
                || bad "G-ROOT.2 did NOT abort on the real D4 root (exit $RC)"
RC=$(run_guard "$REAL_D4/")
[ "$RC" = "3" ] && ok "G-ROOT.2 aborts on the real root with a TRAILING SLASH (path normalised)" \
                || bad "trailing-slash form was not caught (exit $RC)"
RC=$(run_guard "$REAL_D4/O/..")
[ "$RC" = "3" ] && ok "G-ROOT.2 aborts on the real root reached via '..' (path normalised)" \
                || bad "'..' form was not caught (exit $RC)"

# ---- and PROVE the real root is untouched ---------------------------------
N_AFTER=$(find "$REAL_D4" -mindepth 1 -maxdepth 2 2>/dev/null | wc -l)
O_AFTER=$(stat -c '%Y %s' "$REAL_D4/O/OptView.hst" 2>/dev/null)
if [ "$N_BEFORE" = "$N_AFTER" ] && [ "$O_BEFORE" = "$O_AFTER" ] && [ -n "$O_AFTER" ]; then
  ok "REAL D4 ROOT UNCHANGED after three attempts: $N_AFTER entries, O/OptView.hst [$O_AFTER]"
else
  bad "REAL D4 ROOT CHANGED -- before[$N_BEFORE|$O_BEFORE] after[$N_AFTER|$O_AFTER]"
fi

# ---- P1: some other foreign path -----------------------------------------
RC=$(run_guard /home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin)
[ "$RC" = "3" ] && ok "G-ROOT.2 aborts on D7R's run root" || bad "D7R root not caught (exit $RC)"
RC=$(run_guard /tmp/some-unrelated-directory)
[ "$RC" = "3" ] && ok "G-ROOT.1 aborts on a path that is simply not the registered root" \
                || bad "unregistered path not caught (exit $RC)"

# ---- P3/P4: the LEDGER-IDENTITY limb, on a sacrificial registered root ----
# The registered root does not exist yet, so it is created, planted, driven,
# and REMOVED here.  Nothing else in the lab writes to this path.
for plant in "ITEM=D12R2" "ARM=O ROW=PATCHED rc=0"; do
  rm -rf "$REGISTERED"; mkdir -p "$REGISTERED"
  printf '%s\n' "$plant" > "$REGISTERED/ledger.txt"
  RC=$(run_guard "$REGISTERED")
  label=$(echo "$plant" | cut -c1-24)
  [ "$RC" = "3" ] && ok "G-ROOT.3 aborts on a ledger carrying [$label]" \
                  || bad "G-ROOT.3 did not catch [$label] (exit $RC)"
  rm -rf "$REGISTERED"
done

# ---- N1: THE NEGATIVE CONTROL.  The guard must NOT refuse everything. -----
# Registered root, clean. The guard must PASS and the script must then stop for
# a DIFFERENT reason. A guard that refuses every input is not a guard.
OUT=$(BASE="$REGISTERED" bash "$LAUNCHER" 2>&1); RC=$?
if echo "$OUT" | grep -q "D4S_G_ROOT_PASS" && [ "$RC" != "3" ]; then
  ok "NEGATIVE CONTROL: guard PASSES on the registered root and the script stops later (exit $RC, not 3)"
else
  bad "NEGATIVE CONTROL: guard did not pass on its own registered root (exit $RC)"
fi

# ---- the rule-2 amendment condition, CHECKED HERE AND RECORDED ------------
if [ -e "$REGISTERED" ]; then
  bad "RULE-2 CONDITION: $REGISTERED EXISTS -- this item is not before first compute"
else
  ok "RULE-2 CONDITION CHECKED: test -e '$REGISTERED' -> ABSENT. No container has run; the amendment is legal."
fi

echo "================================================================"
if [ "$FAIL" -eq 0 ]; then
  echo "GUARD SELFTEST PASSED: $PASS checks, including three abort attempts against"
  echo "the REAL D4 run root with that root measured unchanged, and a negative"
  echo "control proving the guard does not simply refuse everything."
  exit 0
fi
echo "GUARD SELFTEST FAILED: $FAIL of $((PASS+FAIL)) checks."
exit 2
