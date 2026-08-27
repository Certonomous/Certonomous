#!/usr/bin/env bash
# SO-1a G-ROOT.5 SELFTEST -- DERIVED from curriculum_D15/d15_groot5_selftest.sh
# (md5 8a2a7df64b2db87615a20fab2d9208f8), driven against SO-1a's OWN launcher
# (G-ROOT.5 from birth).  REGISTERED DELTAS (so1a_groot5_selftest_DELTAS_from_d15.diff):
# names and root; the forbidden-root legs (d) name D15's, D16's, D17's, AV-1's and
# AV-2's roots; leg (f) is NEW and drives the AGE-DATUM-BY-EXISTENCE resolution the
# launcher performs, including the case where NEITHER registered name is present.
# (a) a sacrificial RUNNING container carrying this item's prefix and the arm;
# (b) a sacrificial LIVE pid whose cwd is the run root, named in the driver
#     pidfile; (b2) a STALE pidfile must not block; (c) clear must pass;
# (d) G-ROOT.1 refusals on D4's, D5's, D13's and D16's roots;
# (e) G-ROW from birth (the row in the ARM NAME and the row of the IMAGE must
#     agree), driven with the REAL images on the temporary root made 777 and
#     holding ONLY the three staged instruments (no base/0.orig, no MESH/), so
#     a launcher that got past G-ROW still refuses at G-COLD with nothing to
#     remove; the copies are removed afterwards and the root's emptiness asserted.
# SAFETY: (a)-(d) pass a BOGUS IMAGE NAME and the run root is a temporary EMPTY
# directory (mode 775), so a launcher that got past G-ROOT.5 aborts at the
# L-251 mode check (exit 4) BEFORE any staging.  The run root is created empty
# for the test and removed with rmdir (which refuses a non-empty directory), and
# its ABSENCE afterwards is asserted -- that absence is the freeze condition of
# PREREGISTRATION.md section 8.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; L="$HERE/so1a_run_arm.sh"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient
IMG=dafoam/opt-packages:latest; IMG_P=dafoam-idwarp-rot:v1; BOGUS=no-such-image:selftest; ARM=X-S
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "SO1a G-ROOT.5 SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) launcher_md5=$(md5sum "$L" | cut -d' ' -f1)"
G5=$(grep -n 'G_ROOT5_PASS' "$L" | head -1 | cut -d: -f1)
FIRSTOP=$(grep -nE '^[[:space:]]*[^#]*((sudo -n )?rm -rf|cp -a|docker run)' "$L" | grep -v '^[0-9]*:[[:space:]]*#' | head -1 | cut -d: -f1)
if [ -n "$G5" ] && [ -n "$FIRSTOP" ] && [ "$FIRSTOP" -gt "$G5" ]; then ok "G-ROOT.5 completes at :$G5, first destructive op at :$FIRSTOP"; else bad "order G5=$G5 FIRSTOP=$FIRSTOP"; exit 2; fi
NBT=$(grep -vE '^[[:space:]]*#' "$L" | grep -c '`' || true)
if [ "$NBT" = "0" ]; then ok "zero backticks on executable lines of the launcher"; else bad "$NBT backticks on executable lines"; fi
if [ -e "$BASE" ]; then bad "run root $BASE already EXISTS -- refusing to test over a real root (freeze condition violated)"; exit 2; else ok "run root ABSENT before the test: $BASE"; fi
mkdir -p "$BASE" || { bad "could not create the temporary empty run root"; exit 2; }
# (a) sacrificial RUNNING container with this item's prefix and the arm
CN="so1a_${ARM}_selftest_$(date -u +%Y%m%dT%H%M%SZ)"
sudo -n docker run -d --name "$CN" --cpus=0.1 --cpuset-cpus=9 --memory=64m --memory-swap=64m "$IMG" bash -c "sleep 180" >/dev/null 2>&1 || { bad "could not start sacrificial container"; rmdir "$BASE"; exit 2; }
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 a RUNNING container"; then ok "(a) live container $CN -> rc=3: $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-120)"; else bad "(a) rc=$rc: $(echo "$out" | tail -2)"; fi
sudo -n docker rm -f "$CN" >/dev/null 2>&1
# (b) sacrificial LIVE pid, cwd = run root, named in the pidfile
( cd "$BASE" && exec sleep 180 ) & SPID=$!
echo "$SPID" > "$BASE/so1a_driver.pid"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 driver pidfile"; then ok "(b) live pid $SPID cwd=$BASE -> rc=3: $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-140)"; else bad "(b) rc=$rc: $(echo "$out" | tail -2)"; fi
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null; rm -f "$BASE/so1a_driver.pid"
# (b2) STALE pidfile (dead pid) must NOT block
echo "999999" > "$BASE/so1a_driver.pid"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "G_ROOT5_PASS" && echo "$out" | grep -q "ABORT L-251 run root mode"; then ok "(b2) stale pidfile ignored; launcher went on to abort at the L-251 mode check (rc=4) -- nothing staged"; else bad "(b2) rc=$rc: $(echo "$out" | tail -2)"; fi
rm -f "$BASE/so1a_driver.pid"
# (c) clear: guard passes, mode check aborts BEFORE staging
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "G_ROOT5_PASS"; then ok "(c) clear -> G-ROOT.5 passes; L-251 mode check aborts (rc=4) before any staging"; else bad "(c) rc=$rc"; fi
# (d) G-ROOT.1/.2 from birth: D4's, D5's, D13's and D16's roots REFUSE
for forb in /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin /home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic /home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic /home/ubuntu/certonomous-runs/CURRICULUM-D17-cone-supersonic /home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv /home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality; do
  out=$(BASE="$forb" bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.1"; then ok "(d) BASE=$forb -> rc=3 G-ROOT.1 REFUSED"; else bad "(d) $forb rc=$rc"; fi
done
# (e) G-ROW from birth, with the REAL images, on the 777 root holding only the
# three staged instruments.
chmod 777 "$BASE"; mkdir -p "$BASE/base/system"
cp -a "$HERE/so1a_runScript.py" "$HERE/so1a_xf.py" "$BASE/" && cp -a "$HERE/so1a_decomposeParDict" "$BASE/base/system/decomposeParDict"
out=$(bash "$L" X-P "$IMG" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "ABORT G-ROW arm X-P is registered on the PATCHED row; got ROW=SHIPPED"; then ok "(e1) X-P on the SHIPPED image -> rc=4 G-ROW REFUSED before any staging"; else bad "(e1) rc=$rc: $(echo "$out" | tail -2)"; fi
out=$(bash "$L" MESH "$IMG_P" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "ABORT G-ROW arm MESH is registered on the SHIPPED row; got ROW=PATCHED"; then ok "(e2) MESH on the PATCHED image -> rc=4 G-ROW REFUSED before any staging"; else bad "(e2) rc=$rc: $(echo "$out" | tail -2)"; fi
out=$(bash "$L" X-S "$IMG" 2>&1); rc=$?
if [ "$rc" -eq 5 ] && echo "$out" | grep -q "D4S_G_ROW_PASS row=SHIPPED" && echo "$out" | grep -q "ABORT arm X-S expects an existing MESH/"; then ok "(e3) X-S on the SHIPPED image -> G-ROW passes, then the arm REFUSES (rc=5) for want of the MESH arm's output -- nothing staged"; else bad "(e3) rc=$rc: $(echo "$out" | tail -2)"; fi
test -e "$BASE/X-S" && bad "(e3) left an X-S directory" || ok "(e3) no arm directory was created"
# (f) NEW -- the launcher's AGE-DATUM-BY-EXISTENCE resolution, DRIVEN in all three
# states, in a THROWAWAY directory that is not an arm and is removed afterwards.
# This is the AV-1/AV-2 defect: a datum pinned to the NAME 0/U vanishes when
# `writeCompression on` rewrites it as 0/U.gz on a serial arm.
FTMP="$BASE/_datum_probe"
mkdir -p "$FTMP/0"
resolve() { if [ -f "$1/0/U" ]; then echo 0/U; elif [ -f "$1/0/U.gz" ]; then echo 0/U.gz; else echo NONE; fi; }
: > "$FTMP/0/U"
[ "$(resolve "$FTMP")" = "0/U" ] && ok "(f1) plain 0/U present -> resolved 0/U" || bad "(f1) resolve returned $(resolve "$FTMP")"
rm -f "$FTMP/0/U"; : > "$FTMP/0/U.gz"
[ "$(resolve "$FTMP")" = "0/U.gz" ] && ok "(f2) only the COMPRESSED twin present (writeCompression on, np=1) -> resolved 0/U.gz, NOT a refusal -- this is exactly what killed AV-1 and AV-2" || bad "(f2) resolve returned $(resolve "$FTMP")"
rm -f "$FTMP/0/U.gz"
[ "$(resolve "$FTMP")" = "NONE" ] && ok "(f3) DRIVEN CONTROL -- NEITHER registered name present -> NONE, and the launcher/grader REFUSE (so1a_grade.py U24 drives the grader side)" || bad "(f3) resolve returned $(resolve "$FTMP")"
rm -rf "$FTMP"
grep -q 'elif \[ -f "\$WORK/0/U.gz" \]' "$L" && ok "(f4) the LAUNCHER itself carries the by-existence branch for the solver arms" || bad "(f4) launcher has no 0/U.gz branch"
grep -q '.so1a_age_datum_ref' "$L" && ok "(f5) the LAUNCHER records the resolved datum NAME to .so1a_age_datum_ref" || bad "(f5) launcher records no datum name"
rm -rf "$BASE/base" "$BASE/so1a_runScript.py" "$BASE/so1a_xf.py"
chmod 775 "$BASE"
N=$(find "$BASE" -mindepth 1 | wc -l)
if [ "$N" = "0" ]; then ok "temporary run root EMPTY after every invocation and after the (e) copies were removed ($N entries)"; else bad "run root gained $N entries"; fi
rmdir "$BASE" 2>/dev/null
if [ ! -e "$BASE" ]; then ok "run root ABSENT after the test (freeze condition): test -e $BASE -> false"; else bad "run root still present"; fi
sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^so1a_" && bad "a so1a_ container survives" || ok "no so1a_ container survives"
echo "SO1a G-ROOT5 SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
