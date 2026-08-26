#!/usr/bin/env bash
# D4S-F3S G-ROOT.5 SELFTEST -- D4-SHIPPED's d4s_groot5_selftest.sh (Addendum 2)
# carried to this item.  Drives the launcher's guards with (a) a sacrificial
# RUNNING container carrying this item's prefix and arm, (b) a sacrificial LIVE
# pid whose cwd is the run root named in the driver pidfile, (b2) a STALE
# pidfile that must not block, (c) the clear path with the CORRECT image, which
# must pass G-ROOT.5, the instrument md5s, the digest and G-ROW and then stop at
# the WORK-absent check (rc=5, nothing staged, nothing removed), (d) the WRONG
# image for the arm, refused by G-ROW (rc=4).
# THE REGISTERED ROOT IS ABSENT AT FREEZE: this selftest creates it, stages the
# frozen instruments into it (never an arm directory), and REMOVES it at the
# end, asserting absence as its final leg.  It refuses to run over an existing
# root.  Sacrificial objects are removed; no graded artefact is touched.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; L="$HERE/d4s_f3s_run_arm.sh"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin
SRC_S=/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin
CASE_D4=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D4
IMG_S=dafoam/opt-packages:latest; IMG_P=dafoam-idwarp-rot:v1; BOGUS=no-such-image:selftest
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "D4S-F3S G-ROOT.5 SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) launcher_md5=$(md5sum "$L" | cut -d' ' -f1)"
test ! -e "$BASE" || { bad "the registered root already exists -- refusing to selftest over it"; exit 2; }
G5=$(grep -n 'D4S_G_ROOT5_PASS' "$L" | head -1 | cut -d: -f1)
FIRSTOP=$(grep -nE '^[[:space:]]*[^#]*((sudo -n )?rm -rf|cp -a|docker run)' "$L" | grep -v '^[0-9]*:[[:space:]]*#' | head -1 | cut -d: -f1)
if [ -n "$G5" ] && [ -n "$FIRSTOP" ] && [ "$FIRSTOP" -gt "$G5" ]; then ok "G-ROOT.5 completes at :$G5, first destructive op at :$FIRSTOP"; else bad "order G5=$G5 FIRSTOP=$FIRSTOP"; exit 2; fi
NB=$(grep -cvE '^[[:space:]]*#' "$L"); BT=$(grep -vE '^[[:space:]]*#' "$L" | grep -c '`')
if [ "$BT" -eq 0 ]; then ok "zero backticks on any executable line ($NB executable lines)"; else bad "$BT executable lines carry backticks"; fi
# ---- build the sacrificial root with the frozen instruments (no arm directory)
mkdir "$BASE" && chmod 777 "$BASE" || { bad "cannot create sacrificial root"; exit 2; }
echo "ITEM=D4S-F3S" > "$BASE/ledger.txt"
cp -a "$SRC_S/d4_opt_runScript.py" "$SRC_S/d4_extract_endpoint.py" "$BASE/" || { bad "stage producer"; }
cp -a "$CASE_D4/d4_repair_instruments.md5" "$CASE_D4/d4_endpoint_locus.py" "$CASE_D4/d4_endpoint_physical.py" "$CASE_D4/d4_accept_primal.py" "$CASE_D4/d4_accept_compare.py" "$BASE/" || { bad "stage repair instruments"; }
cp -a "$HERE/d4s_f3s_instruments.md5" "$HERE/d4s_f3s_fd_endpoint.py" "$HERE/d4s_f3s_accept.py" "$BASE/" || { bad "stage item instruments"; }
NB0=$(find "$BASE" | wc -l); SO=$(stat -c '%Y %s' "$SRC_S/O/OptView.hst"); NS0=$(find "$SRC_S/O" | wc -l)
# (a) sacrificial RUNNING container with this item's prefix and the arm
CN="d4sf3s_F-S_selftest_$(date -u +%Y%m%dT%H%M%SZ)"
sudo -n docker run -d --name "$CN" --cpus=0.1 --cpuset-cpus=9 --memory=64m "$IMG_S" bash -c "sleep 180" >/dev/null 2>&1 || { bad "could not start sacrificial container"; }
out=$(bash "$L" F-S "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 a RUNNING container"; then ok "(a) live container $CN -> rc=3: $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-120)"; else bad "(a) rc=$rc: $(echo "$out" | tail -2)"; fi
sudo -n docker rm -f "$CN" >/dev/null 2>&1
# (b) sacrificial LIVE pid, cwd = run root, named in the pidfile
( cd "$BASE" && exec sleep 180 ) & SPID=$!
echo "$SPID" > "$BASE/d4s_f3s_driver.pid"
out=$(bash "$L" F-S "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 driver pidfile"; then ok "(b) live pid $SPID cwd=$BASE -> rc=3: $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-140)"; else bad "(b) rc=$rc: $(echo "$out" | tail -2)"; fi
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null; rm -f "$BASE/d4s_f3s_driver.pid"
# (b2) STALE pidfile (dead pid) must NOT block; the bogus image aborts at the digest check
echo "999999" > "$BASE/d4s_f3s_driver.pid"
out=$(bash "$L" F-S "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "D4S_G_ROOT5_PASS" && echo "$out" | grep -q "ABORT cannot read digest"; then ok "(b2) stale pidfile ignored; instrument md5s passed; bogus image aborted at the digest check (rc=4) -- nothing staged"; else bad "(b2) rc=$rc: $(echo "$out" | tail -2)"; fi
rm -f "$BASE/d4s_f3s_driver.pid"
# (c) CLEAR, CORRECT image: G-ROOT.1-.5, md5s, digest, G-ROW pass; stops at WORK absent (rc=5)
out=$(bash "$L" F-S "$IMG_S" 2>&1); rc=$?
if [ "$rc" -eq 5 ] && echo "$out" | grep -q "D4S_G_ROW_PASS arm=F-S row=SHIPPED" && echo "$out" | grep -q "absent -- run d4s_f3s_stage_arm.sh"; then ok "(c) F-S with the SHIPPED image -> G-ROOT.5, md5s, digest, G-ROW all PASS; stopped at WORK absent (rc=5), nothing staged"; else bad "(c) rc=$rc: $(echo "$out" | tail -3)"; fi
out=$(bash "$L" F-P "$IMG_P" 2>&1); rc=$?
if [ "$rc" -eq 5 ] && echo "$out" | grep -q "D4S_G_ROW_PASS arm=F-P row=PATCHED"; then ok "(c2) F-P with the PATCHED image -> G-ROW PASS; stopped at WORK absent (rc=5)"; else bad "(c2) rc=$rc: $(echo "$out" | tail -3)"; fi
# (d) WRONG image for the arm -> G-ROW refuses (rc=4)
out=$(bash "$L" F-S "$IMG_P" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "ABORT G-ROW arm F-S is registered on row SHIPPED; got ROW=PATCHED"; then ok "(d) F-S with the PATCHED image -> G-ROW rc=4: $(echo "$out" | grep 'ABORT G-ROW' | cut -c1-110)"; else bad "(d) rc=$rc: $(echo "$out" | tail -2)"; fi
out=$(bash "$L" F-P "$IMG_S" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "ABORT G-ROW arm F-P is registered on row PATCHED; got ROW=SHIPPED"; then ok "(d2) F-P with the SHIPPED image -> G-ROW rc=4"; else bad "(d2) rc=$rc: $(echo "$out" | tail -2)"; fi
# (e) G-ROOT.1/.2: pointed at D4-SHIPPED's root and D4's root -> refused before anything
out=$(BASE="$SRC_S" bash "$L" F-S "$IMG_S" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.1"; then ok "(e) BASE=D4-SHIPPED root -> G-ROOT.1 rc=3 (its evidence protected)"; else bad "(e) rc=$rc"; fi
out=$(BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin bash "$L" F-P "$IMG_P" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.1"; then ok "(e2) BASE=D4 root -> G-ROOT.1 rc=3"; else bad "(e2) rc=$rc"; fi
# (f) unknown arm -> usage
out=$(bash "$L" F3 "$IMG_S" 2>&1); rc=$?
if [ "$rc" -eq 64 ]; then ok "(f) arm F3 is not this item's -> rc=64 usage"; else bad "(f) rc=$rc"; fi
# census: the sacrificial root unchanged by every leg; the SOURCE evidence untouched; no arm dir
NB1=$(find "$BASE" | wc -l); SO1=$(stat -c '%Y %s' "$SRC_S/O/OptView.hst"); NS1=$(find "$SRC_S/O" | wc -l)
if [ "$NB0" = "$NB1" ] && [ ! -d "$BASE/F-S" ] && [ ! -d "$BASE/F-P" ]; then ok "sacrificial root unchanged ($NB1 entries), no arm directory staged by any leg"; else bad "root CHANGED $NB0->$NB1 or an arm dir appeared"; fi
if [ "$SO" = "$SO1" ] && [ "$NS0" = "$NS1" ]; then ok "D4-SHIPPED O/ untouched ($NS1 entries, OptView.hst [$SO1])"; else bad "SOURCE CHANGED"; fi
if ! sudo -n docker ps -a --format '{{.Names}}' | grep -q '^d4sf3s_'; then ok "no d4sf3s_ container survives"; else bad "a d4sf3s_ container survives"; fi
# ---- remove the sacrificial root; the registered root must be ABSENT at freeze
rm -rf "$BASE"
if [ ! -e "$BASE" ]; then ok "registered root REMOVED and ABSENT at $(date -u +%Y-%m-%dT%H:%M:%SZ): $BASE"; else bad "root still present"; fi
echo "D4S-F3S G-ROOT5 SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
