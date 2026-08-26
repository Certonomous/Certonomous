#!/usr/bin/env bash
# G-ROOT.5 SELFTEST (ADDENDUM 2).  Drives the new guard with (a) a sacrificial
# RUNNING container carrying this item's prefix and the arm, and (b) a
# sacrificial LIVE pid whose cwd is the run root, named in the driver pidfile;
# (b2) a STALE pidfile must not block; (c) clear must pass.
# SAFETY: every invocation passes a BOGUS IMAGE NAME, so if the guard did NOT
# fire the launcher would still abort at the digest check (exit 4) BEFORE any
# staging -- the two outcomes are distinguishable by exit code and message.
# The real run root is censused before and after.  Sacrificial objects are
# removed at the end; graded arms and their containers are never touched.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; L="$HERE/d4s_run_arm.sh"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin
IMG=dafoam/opt-packages:latest; BOGUS=no-such-image:selftest
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "G-ROOT.5 SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) launcher_md5=$(md5sum "$L" | cut -d' ' -f1)"
G5=$(grep -n 'D4S_G_ROOT5_PASS' "$L" | head -1 | cut -d: -f1)
FIRSTOP=$(grep -nE '^[[:space:]]*[^#]*((sudo -n )?rm -rf|cp -a|docker run)' "$L" | grep -v '^[0-9]*:[[:space:]]*#' | head -1 | cut -d: -f1)
if [ -n "$G5" ] && [ -n "$FIRSTOP" ] && [ "$FIRSTOP" -gt "$G5" ]; then ok "G-ROOT.5 completes at :$G5, first destructive op at :$FIRSTOP"; else bad "order G5=$G5 FIRSTOP=$FIRSTOP"; exit 2; fi
NB=$(find "$BASE" -mindepth 1 -maxdepth 1 | wc -l); OB=$(stat -c '%Y %s' "$BASE/O/OptView.hst")
test ! -f "$BASE/d4s_driver.pid" || { bad "a driver pidfile already exists -- refusing to test over a live driver"; exit 2; }
# (a) sacrificial RUNNING container with this item's prefix and the arm
CN="d4_ACC_selftest_$(date -u +%Y%m%dT%H%M%SZ)"
sudo -n docker run -d --name "$CN" --cpus=0.1 --cpuset-cpus=9 --memory=64m "$IMG" bash -c "sleep 180" >/dev/null 2>&1 || { bad "could not start sacrificial container"; exit 2; }
out=$(bash "$L" ACC "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 a RUNNING container"; then ok "(a) live container $CN -> rc=3: $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-120)"; else bad "(a) rc=$rc: $(echo "$out" | tail -2)"; fi
sudo -n docker rm -f "$CN" >/dev/null 2>&1
# (b) sacrificial LIVE pid, cwd = run root, named in the pidfile
( cd "$BASE" && exec sleep 180 ) & SPID=$!
echo "$SPID" > "$BASE/d4s_driver.pid"
out=$(bash "$L" ACC "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 driver pidfile"; then ok "(b) live pid $SPID cwd=$BASE -> rc=3: $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-140)"; else bad "(b) rc=$rc: $(echo "$out" | tail -2)"; fi
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null; rm -f "$BASE/d4s_driver.pid"
# (b2) STALE pidfile (dead pid) must NOT block
echo "999999" > "$BASE/d4s_driver.pid"
out=$(bash "$L" ACC "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "D4S_G_ROOT5_PASS" && echo "$out" | grep -q "ABORT cannot read digest"; then ok "(b2) stale pidfile ignored; launcher went on to abort at the digest check (rc=4) -- nothing staged"; else bad "(b2) rc=$rc"; fi
rm -f "$BASE/d4s_driver.pid"
# (c) clear: guard passes, digest check aborts BEFORE staging
out=$(bash "$L" ACC "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "D4S_G_ROOT5_PASS"; then ok "(c) clear -> G-ROOT.5 passes; bogus image aborts at digest (rc=4) before any staging"; else bad "(c) rc=$rc"; fi
NA=$(find "$BASE" -mindepth 1 -maxdepth 1 | wc -l); OA=$(stat -c '%Y %s' "$BASE/O/OptView.hst")
if [ "$NB" = "$NA" ] && [ "$OB" = "$OA" ]; then ok "run root unchanged: $NB top-level entries, O/OptView.hst [$OB]"; else bad "run root CHANGED $NB->$NA"; fi
if [ -d "$BASE/ACC" ]; then bad "ACC/ was staged"; else ok "no ACC/ staged by any selftest invocation"; fi
echo "G-ROOT5 SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
