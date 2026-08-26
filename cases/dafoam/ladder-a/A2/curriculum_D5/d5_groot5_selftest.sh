#!/usr/bin/env bash
# D5 G-ROOT.5 SELFTEST -- the d4s_groot5_selftest.sh pattern, driven against
# D5's OWN launcher (G-ROOT.5 from birth, standing rule of 2026-08-26).
# (a) a sacrificial RUNNING container carrying this item's prefix and the arm;
# (b) a sacrificial LIVE pid whose cwd is the run root, named in the driver
#     pidfile; (b2) a STALE pidfile must not block; (c) clear must pass.
# SAFETY: every invocation passes a BOGUS IMAGE NAME and the run root is a
# temporary EMPTY directory (mode 775), so a launcher that got past G-ROOT.5
# aborts at the L-251 mode check (exit 4) BEFORE any staging.  The run root is
# created empty for the test and removed with rmdir (which refuses a non-empty
# directory), and its ABSENCE afterwards is asserted -- that absence is the
# freeze condition of PREREGISTRATION.md section 8.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; L="$HERE/d5_run_arm.sh"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density
IMG=dafoam-idwarp-rot:v1; BOGUS=no-such-image:selftest; ARM=ACC48
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "D5 G-ROOT.5 SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) launcher_md5=$(md5sum "$L" | cut -d' ' -f1)"
G5=$(grep -n 'G_ROOT5_PASS' "$L" | head -1 | cut -d: -f1)
FIRSTOP=$(grep -nE '^[[:space:]]*[^#]*((sudo -n )?rm -rf|cp -a|docker run)' "$L" | grep -v '^[0-9]*:[[:space:]]*#' | head -1 | cut -d: -f1)
if [ -n "$G5" ] && [ -n "$FIRSTOP" ] && [ "$FIRSTOP" -gt "$G5" ]; then ok "G-ROOT.5 completes at :$G5, first destructive op at :$FIRSTOP"; else bad "order G5=$G5 FIRSTOP=$FIRSTOP"; exit 2; fi
NBT=$(grep -vE '^[[:space:]]*#' "$L" | grep -c '`' || true)
if [ "$NBT" = "0" ]; then ok "zero backticks on executable lines of the launcher"; else bad "$NBT backticks on executable lines"; fi
if [ -e "$BASE" ]; then bad "run root $BASE already EXISTS -- refusing to test over a real root (freeze condition violated)"; exit 2; else ok "run root ABSENT before the test: $BASE"; fi
mkdir -p "$BASE" || { bad "could not create the temporary empty run root"; exit 2; }
# (a) sacrificial RUNNING container with this item's prefix and the arm
CN="d5_${ARM}_selftest_$(date -u +%Y%m%dT%H%M%SZ)"
sudo -n docker run -d --name "$CN" --cpus=0.1 --cpuset-cpus=13 --memory=64m "$IMG" bash -c "sleep 180" >/dev/null 2>&1 || { bad "could not start sacrificial container"; rmdir "$BASE"; exit 2; }
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 a RUNNING container"; then ok "(a) live container $CN -> rc=3: $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-120)"; else bad "(a) rc=$rc: $(echo "$out" | tail -2)"; fi
sudo -n docker rm -f "$CN" >/dev/null 2>&1
# (b) sacrificial LIVE pid, cwd = run root, named in the pidfile
( cd "$BASE" && exec sleep 180 ) & SPID=$!
echo "$SPID" > "$BASE/d5_driver.pid"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 driver pidfile"; then ok "(b) live pid $SPID cwd=$BASE -> rc=3: $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-140)"; else bad "(b) rc=$rc: $(echo "$out" | tail -2)"; fi
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null; rm -f "$BASE/d5_driver.pid"
# (b2) STALE pidfile (dead pid) must NOT block
echo "999999" > "$BASE/d5_driver.pid"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "G_ROOT5_PASS" && echo "$out" | grep -q "ABORT L-251 run root mode"; then ok "(b2) stale pidfile ignored; launcher went on to abort at the L-251 mode check (rc=4) -- nothing staged"; else bad "(b2) rc=$rc: $(echo "$out" | tail -2)"; fi
rm -f "$BASE/d5_driver.pid"
# (c) clear: guard passes, mode check aborts BEFORE staging
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "G_ROOT5_PASS"; then ok "(c) clear -> G-ROOT.5 passes; L-251 mode check aborts (rc=4) before any staging"; else bad "(c) rc=$rc"; fi
# (d) G-ROOT.1/.2 from birth: D4's, D4-SHIPPED's and D6's roots REFUSE
for forb in /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin /home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin /home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint; do
  out=$(BASE="$forb" bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.1"; then ok "(d) BASE=$forb -> rc=3 G-ROOT.1 REFUSED"; else bad "(d) $forb rc=$rc"; fi
done
N=$(find "$BASE" -mindepth 1 | wc -l)
if [ "$N" = "0" ]; then ok "temporary run root still EMPTY after every invocation ($N entries)"; else bad "run root gained $N entries"; fi
rmdir "$BASE" 2>/dev/null
if [ ! -e "$BASE" ]; then ok "run root ABSENT after the test (freeze condition): test -e $BASE -> false"; else bad "run root still present"; fi
echo "D5 G-ROOT5 SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
