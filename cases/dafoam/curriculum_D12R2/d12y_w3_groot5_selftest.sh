#!/usr/bin/env bash
# W3 G-ROOT.5 SELFTEST -- drives the chain driver's own refusals at ZERO compute:
# (a) a sacrificial RUNNING container carrying this item's prefix -> rc=3, nothing run;
# (b) an EXISTING run root with a pidfile naming a LIVE pid -> rc=3 (the sibling-driver
#     refusal), nothing run; (c) an existing run root with a STALE pidfile -> rc=6
#     (phase 1 requires an absent root), nothing run.  The temporary root is created
#     empty and removed with rmdir; its ABSENCE afterwards is the freeze condition.
# SAFETY: no leg reaches the launcher: (a) refuses before it; (b)/(c) refuse before it.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; D="$HERE/d12y_w3_chain_driver.sh"
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady
IMG=dafoam/opt-packages:latest
PASS=0; FAIL=0; ok() { echo "  [OK ] $1"; PASS=$((PASS+1)); }; bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "W3 G-ROOT.5 SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) driver_md5=$(md5sum "$D" | cut -d' ' -f1)"
[ -e "$ROOT" ] && { bad "run root $ROOT already EXISTS -- refusing to test over a real root"; exit 2; } || ok "run root ABSENT before the test: $ROOT"
CN="d12y_w3_selftest_$(date -u +%Y%m%dT%H%M%SZ)"
sudo -n docker run -d --name "$CN" --cpus=0.1 --cpuset-cpus=1 --memory=64m --memory-swap=64m "$IMG" bash -c "sleep 120" >/dev/null 2>&1 || { bad "could not start the sacrificial container"; exit 2; }
out=$(bash "$D" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "G_ROOT5_REFUSED live_prefix_containers"; then ok "(a) live prefix container $CN -> rc=3, NOTHING RUN"; else bad "(a) rc=$rc: $(echo "$out" | tail -1)"; fi
sudo -n docker rm -f "$CN" >/dev/null 2>&1
mkdir -p "$ROOT" || { bad "could not create the temporary root"; exit 2; }
( cd "$ROOT" && exec sleep 120 ) & SPID=$!
echo "$SPID" > "$ROOT/d12y_w3_driver.pid"
out=$(bash "$D" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "G_ROOT5_REFUSED live_driver_pid=$SPID"; then ok "(b) live sibling driver pid $SPID -> rc=3, NOTHING RUN"; else bad "(b) rc=$rc: $(echo "$out" | tail -1)"; fi
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null; echo "999999" > "$ROOT/d12y_w3_driver.pid"
out=$(bash "$D" 2>&1); rc=$?
if [ "$rc" -eq 6 ] && echo "$out" | grep -q "ROOT_EXISTS"; then ok "(c) stale pidfile ignored; existing root -> rc=6 (phase 1 requires an absent root), NOTHING RUN"; else bad "(c) rc=$rc: $(echo "$out" | tail -1)"; fi
rm -f "$ROOT/d12y_w3_driver.pid"; rmdir "$ROOT" 2>/dev/null
[ ! -e "$ROOT" ] && ok "run root ABSENT after the test (freeze condition): test -e $ROOT -> false" || bad "run root still present"
sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q '^d12y_w3_' && bad "a d12y_w3_ container survives" || ok "no d12y_w3_ container survives"
N=$(ls "$HERE"/W3_*.out 2>/dev/null | wc -l); [ "$N" = "0" ] && ok "no step output was written (no leg reached the launcher)" || bad "$N W3_*.out files written"
rm -f "$HERE/STATUS.W3_chain"
echo "W3 G-ROOT5 SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
