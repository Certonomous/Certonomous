#!/usr/bin/env bash
# SO-1bR G-ROOT.5 SELFTEST -- DERIVED from curriculum_SO1b/so1b_groot5_selftest.sh
# (md5 read at run time and printed below), driven against SO-1bR's OWN launcher
# so1br_run_arm.sh.  REGISTERED DELTAS in so1br_groot5_selftest_DELTAS_from_so1b.diff.
#
# WHAT SO-1bR ACTUALLY REGISTERS, stated plainly because sibling families register
# something else.  SO-1bR's G-ROOT.5 is inherited verbatim from SO-1b: "A LIVE ARM IS
# NEVER RE-STAGED", and its refusal code is EXIT 3, on two live readings taken BEFORE
# any destructive act:
#   (a) a RUNNING container carrying so1br_<ARM>_ ;
#   (b) a driver pidfile in the run root naming a LIVE pid that is not an ancestor of
#       the launcher, or whose cwd IS the run root.
# A STALE pidfile does NOT block.  SO-1bR's launcher does NOT refuse merely because the
# run root exists -- that clause belongs to the D12R2/W3 chain driver's phase 1 (exit 6);
# SO-1bR's driver re-stages on the FIRST fire only.  Both directions are driven below and
# THE OBSERVED CODES ARE PRINTED RATHER THAN ASSUMED.
#
# NEW IN SO-1bR: leg (h) drives G-CPUSET, the one guard this item adds, in BOTH
# directions with a sacrificial container pinned to the registered core.
#
# CLEANUP DISCIPLINE -- W3-SELFTEST-DEF-1, PAID FOR ONCE IN THIS FAMILY ALREADY.
# d12y_w3_groot5_selftest.sh ran `rm -f STATUS.W3_chain` at its foot and deleted a REAL
# status file the queue runner had written, destroying evidence.  This selftest therefore:
#   * REFUSES to run at all if the run root already exists (exit 2), so nothing inside it
#     can pre-date the test;
#   * removes ONLY paths it recorded in CREATED[] at the moment it made them, BY NAME,
#     never by glob and never by sweep;
#   * DRIVES that discipline with a DECOY IT DID NOT CREATE and requires the decoy to
#     SURVIVE the named cleanup, byte-intact;
#   * writes NOTHING into the case directory and PROVES it by comparing a listing and a
#     content digest of the case directory before and after.
#
# SAFETY.  Legs (a)-(d) and (h) pass a BOGUS IMAGE and run on a temporary EMPTY run root
# at mode 775, so a launcher that got past every guard aborts at the L-251 mode check
# (exit 4) BEFORE any staging.  Leg (e) uses the REAL images but never drives arm MESH on
# the SHIPPED image: MESH is the ONE arm whose branch reaches `sudo -n rm -rf "$WORK"`,
# and every leg here refuses above that line.  The run root is created empty, emptied by
# name, removed with rmdir (which refuses a non-empty directory), and its ABSENCE
# afterwards is asserted -- that absence is the freeze condition of PREREGISTRATION.md.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; L="$HERE/so1br_run_arm.sh"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt
IMG=dafoam/opt-packages:latest; IMG_P=dafoam-idwarp-rot:v1; BOGUS=no-such-image:so1br-selftest; ARM=O-P
CPUSET=9
SCRATCH="${SO1BR_SELFTEST_SCRATCH:-/tmp}/so1br_groot5_$$"; mkdir -p "$SCRATCH"
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
# ---- EVERY path this selftest creates is recorded HERE, AT THE MOMENT IT IS MADE,
# ---- and cleanup removes ONLY these, BY NAME.
CREATED=()
note_created() { CREATED+=("$1"); }

echo "SO1bR G-ROOT.5 SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "  launcher       = $L  md5=$(md5sum "$L" | cut -d' ' -f1)"
echo "  parent selftest= $HERE/../curriculum_SO1b/so1b_groot5_selftest.sh md5=$(md5sum "$HERE/../curriculum_SO1b/so1b_groot5_selftest.sh" 2>/dev/null | cut -d' ' -f1)"

# ---- case-directory snapshot: this selftest writes NOTHING here ------------------
CASE_BEFORE_LIST=$(ls -1a "$HERE" | sort | md5sum | cut -d' ' -f1)
CASE_BEFORE_SUM=$(find "$HERE" -maxdepth 1 -type f -exec md5sum {} + | sort -k2 | md5sum | cut -d' ' -f1)

# ---- (o) ORDER, read out of the launcher's own bytes -----------------------------
G5=$(grep -n 'G_ROOT5_PASS' "$L" | head -1 | cut -d: -f1)
GCP=$(grep -n 'SO1BR_G_CPUSET_PASS' "$L" | head -1 | cut -d: -f1)
FIRSTOP=$(grep -nE '^[[:space:]]*[^#]*((sudo -n )?rm -rf|cp -a|docker run)' "$L" | grep -v '^[0-9]*:[[:space:]]*#' | head -1 | cut -d: -f1)
if [ -n "$G5" ] && [ -n "$GCP" ] && [ -n "$FIRSTOP" ] && [ "$FIRSTOP" -gt "$GCP" ] && [ "$GCP" -gt "$G5" ]; then
  ok "(o1) order is EVIDENCE not a claim: G-ROOT.5 completes at :$G5, G-CPUSET at :$GCP, first destructive op at :$FIRSTOP"
else bad "(o1) order G5=$G5 GCPUSET=$GCP FIRSTOP=$FIRSTOP"; exit 2; fi
NBT=$(grep -vE '^[[:space:]]*#' "$L" | grep -c '`' || true)
if [ "$NBT" = "0" ]; then ok "(o2) zero backticks on executable lines of the launcher"; else bad "(o2) $NBT backticks on executable lines"; fi
NBTD=$(grep -vE '^[[:space:]]*#' "$HERE/so1br_chain_driver.sh" | grep -c '`' || true)
if [ "$NBTD" = "0" ]; then ok "(o3) zero backticks on executable lines of the driver"; else bad "(o3) $NBTD backticks on executable lines of the driver"; fi
if grep -vE '^[[:space:]]*#' "$HERE/so1br_chain_driver.sh" | grep -q "SO1a_grade"; then
  bad "(o4) the driver still EXECUTES the frozen SO1a_grade glob"
else ok "(o4) the driver executes NO SO1a_grade glob -- the ruling, checked in the bytes that will run"; fi

# ---- the freeze condition, and the DECOY that proves cleanup is by name -----------
if [ -e "$BASE" ]; then bad "run root $BASE already EXISTS -- refusing to test over a real root"; exit 2; else ok "(p1) run root ABSENT before the test: $BASE"; fi
mkdir -p "$BASE" || { bad "could not create the temporary empty run root"; exit 2; }
note_created "$BASE"
# A DECOY THIS SELFTEST DID NOT CREATE, written by a DIFFERENT hand (a stand-in for the
# queue runner's STATUS file that a sibling selftest destroyed).  It is deliberately NOT
# recorded in CREATED[] and MUST SURVIVE the named cleanup, byte-intact.
DECOY="$BASE/STATUS.SO1bR_chain_DECOY_not_created_by_this_selftest"
printf '%s\n' "written by a hand that is not this selftest -- W3-SELFTEST-DEF-1 control" > "$DECOY"
DECOY_MD5=$(md5sum "$DECOY" | cut -d' ' -f1)
ok "(p2) DECOY planted and NOT recorded in CREATED[]: $(basename "$DECOY") md5=$DECOY_MD5"

# ---- (a) sacrificial RUNNING container with this item's prefix and the arm --------
CN="so1br_${ARM}_selftest_$(date -u +%Y%m%dT%H%M%SZ)"
if sudo -n docker run -d --name "$CN" --cpus=0.1 --cpuset-cpus=$CPUSET --memory=64m --memory-swap=64m "$IMG" bash -c "sleep 180" >/dev/null 2>&1; then
  note_created "container:$CN"
  out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 a RUNNING container"; then
    ok "(a) live container $CN -> rc=3 (REGISTERED CODE): $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-110)"
  else bad "(a) rc=$rc: $(echo "$out" | tail -2)"; fi
  sudo -n docker rm -f "$CN" >/dev/null 2>&1
else bad "(a) could not start the sacrificial container"; fi

# ---- (b) sacrificial LIVE pid, cwd = run root, named in the pidfile ---------------
( cd "$BASE" && exec sleep 180 ) & SPID=$!
echo "$SPID" > "$BASE/so1br_driver.pid"; note_created "$BASE/so1br_driver.pid"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 driver pidfile"; then
  ok "(b) live pid $SPID cwd=$BASE -> rc=3: $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-130)"
else bad "(b) rc=$rc: $(echo "$out" | tail -2)"; fi
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null; rm -f "$BASE/so1br_driver.pid"

# ---- (b2) STALE pidfile (dead pid) must NOT block ---------------------------------
echo "999999" > "$BASE/so1br_driver.pid"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "G_ROOT5_PASS" && echo "$out" | grep -q "ABORT L-251 run root mode"; then
  ok "(b2) stale pidfile ignored; launcher went on to the L-251 mode check (rc=4) -- nothing staged"
else bad "(b2) rc=$rc: $(echo "$out" | tail -2)"; fi
rm -f "$BASE/so1br_driver.pid"

# ---- (c) clear: guards pass, mode check aborts BEFORE staging ---------------------
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "G_ROOT5_PASS"; then
  ok "(c) clear -> G-ROOT.5 passes; L-251 mode check aborts (rc=4) before any staging"
else bad "(c) rc=$rc"; fi

# ---- (d) G-ROOT.1 refusals, including THE TWO ROOTS SO-1bR ADDS -------------------
for forb in /home/ubuntu/certonomous-runs/CURRICULUM-SO1b-a1-naca0012-dragmin-opt \
            /home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient \
            /home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient \
            /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin \
            /home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic \
            /home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv; do
  out=$(BASE="$forb" bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.1"; then ok "(d) BASE=$(basename "$forb") -> rc=3 G-ROOT.1 REFUSED"; else bad "(d) $forb rc=$rc"; fi
done

# ---- (h) NEW -- G-CPUSET, BOTH DIRECTIONS, THE ONE GUARD SO-1bR ADDS --------------
# MUST-FLAG: a container ACTUALLY RUNNING on the registered core.  Its name deliberately
# does NOT match so1br_<ARM>_, so G-ROOT.5 passes and G-CPUSET is the guard under test.
PROBE="so1brcpuprobe_$(date -u +%Y%m%dT%H%M%SZ)"
if sudo -n docker run -d --name "$PROBE" --cpus=0.1 --cpuset-cpus=$CPUSET --memory=64m --memory-swap=64m "$IMG" bash -c "sleep 120" >/dev/null 2>&1; then
  note_created "container:$PROBE"
  out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-CPUSET a RUNNING container already holds cpuset $CPUSET"; then
    ok "(h1) MUST-FLAG a live container on cpuset $CPUSET -> rc=3 G-CPUSET REFUSED: $(echo "$out" | grep 'ABORT G-CPUSET' | cut -c1-120)"
  else bad "(h1) rc=$rc: $(echo "$out" | tail -3)"; fi
  if echo "$out" | grep -q "G_ROOT5_PASS"; then ok "(h2) G-ROOT.5 PASSED first, so the refusal above is G-CPUSET's own and not a G-ROOT.5 hit"; else bad "(h2) G-ROOT.5 did not pass; (h1) may be attributing the wrong guard"; fi
  sudo -n docker rm -f "$PROBE" >/dev/null 2>&1
  sleep 2
  out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 4 ] && echo "$out" | grep -q "SO1BR_G_CPUSET_PASS"; then
    ok "(h3) MUST-NOT-FLAG core $CPUSET clear -> G-CPUSET PASSES and the launcher proceeds to the L-251 check (rc=4): $(echo "$out" | grep SO1BR_G_CPUSET_PASS | cut -c1-90)"
  else bad "(h3) rc=$rc: $(echo "$out" | tail -3)"; fi
else bad "(h) could not start the cpuset probe container"; fi

# ---- (e) G-ROW and G-EDEP, with the REAL images, on the 777 root ------------------
chmod 777 "$BASE"; mkdir -p "$BASE/base/system"; note_created "$BASE/base"
cp -a "$HERE/so1b_runScript.py" "$HERE/so1b_of.py" "$BASE/" && note_created "$BASE/so1b_runScript.py" && note_created "$BASE/so1b_of.py"
cp -a "$HERE/so1br_decomposeParDict" "$BASE/base/system/decomposeParDict"
out=$(bash "$L" O-P "$IMG" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "ABORT G-ROW arm O-P is registered on the PATCHED row; got ROW=SHIPPED"; then ok "(e1) O-P on the SHIPPED image -> rc=4 G-ROW REFUSED before any staging"; else bad "(e1) rc=$rc: $(echo "$out" | tail -2)"; fi
out=$(bash "$L" MESH "$IMG_P" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "ABORT G-ROW arm MESH is registered on the SHIPPED row; got ROW=PATCHED"; then ok "(e2) MESH on the PATCHED image -> rc=4 G-ROW REFUSED before any staging"; else bad "(e2) rc=$rc: $(echo "$out" | tail -2)"; fi
out=$(bash "$L" O-S "$IMG" 2>&1); rc=$?
if [ "$rc" -eq 5 ] && echo "$out" | grep -q "D4S_G_ROW_PASS row=SHIPPED" && echo "$out" | grep -q "ABORT arm O-S expects an existing MESH/"; then ok "(e3) O-S on the SHIPPED image -> G-ROW passes, arm REFUSES (rc=5) for want of MESH/ -- nothing staged"; else bad "(e3) rc=$rc: $(echo "$out" | tail -2)"; fi
test -e "$BASE/O-S" && bad "(e3) left an O-S directory" || ok "(e3) no arm directory was created"
out=$(bash "$L" E-S "$IMG" 2>&1); rc=$?
if [ "$rc" -eq 5 ] && echo "$out" | grep -q "ABORT G-EDEP arm E-S requires its own row"; then ok "(e4) E-S with no O-S/so1b_O.json -> rc=5 G-EDEP REFUSED"; else bad "(e4) rc=$rc: $(echo "$out" | tail -2)"; fi
test -e "$BASE/E-S" && bad "(e4) left an E-S directory" || ok "(e4) no arm directory was created"

# ---- (f) the AGE-DATUM-BY-EXISTENCE resolution, all three states ------------------
FTMP="$BASE/_datum_probe"; mkdir -p "$FTMP/0"; note_created "$FTMP"
resolve() { if [ -f "$1/0/U" ]; then echo 0/U; elif [ -f "$1/0/U.gz" ]; then echo 0/U.gz; else echo NONE; fi; }
: > "$FTMP/0/U"
[ "$(resolve "$FTMP")" = "0/U" ] && ok "(f1) plain 0/U present -> resolved 0/U" || bad "(f1) resolve returned $(resolve "$FTMP")"
rm -f "$FTMP/0/U"; : > "$FTMP/0/U.gz"
[ "$(resolve "$FTMP")" = "0/U.gz" ] && ok "(f2) only the COMPRESSED twin present -> resolved 0/U.gz, NOT a refusal -- this is what killed AV-1 and AV-2" || bad "(f2) resolve returned $(resolve "$FTMP")"
rm -f "$FTMP/0/U.gz"
[ "$(resolve "$FTMP")" = "NONE" ] && ok "(f3) DRIVEN CONTROL -- NEITHER registered name present -> NONE, and launcher and grader both REFUSE" || bad "(f3) resolve returned $(resolve "$FTMP")"
rm -rf "$FTMP"
grep -q 'elif \[ -f "\$WORK/0/U.gz" \]' "$L" && ok "(f4) the LAUNCHER carries the by-existence branch for the solver arms" || bad "(f4) launcher has no 0/U.gz branch"
grep -q '.so1b_age_datum_ref' "$L" && ok "(f5) the LAUNCHER records the resolved datum NAME, under the grader's FROZEN filename" || bad "(f5) launcher records no datum name"

# ---- (g) THE CAP-AGREEMENT PREFLIGHT, DRIVEN WITH PLANTED DISAGREEMENTS -----------
PRE="$HERE/PREREGISTRATION.md"
if [ -f "$PRE" ]; then
  ok "(g0) the frozen pre-registration is present for the preflight to read: $PRE"
  out=$(bash "$L" $ARM "$BOGUS" 2>&1)
  if echo "$out" | grep -q "SO1BR_G_CAP_PREREG_PASS"; then ok "(g1) real launcher vs real pre-registration -> preflight PASSES: $(echo "$out" | grep SO1BR_G_CAP_PREREG_PASS | cut -c1-160)"; else bad "(g1) preflight did not pass: $(echo "$out" | tail -3)"; fi
  sed 's/^    O-P|O-S)  echo 25.0 ;;$/    O-P|O-S)  echo 40.0 ;;/' "$L" > "$SCRATCH/planted_cap.sh"
  NDIFF=$(diff "$L" "$SCRATCH/planted_cap.sh" | grep -c "^[<>]")
  if [ "$NDIFF" = "2" ]; then ok "(g2a) the planted-cap mutant differs from the frozen launcher by exactly one constant (2 diff lines)"; else bad "(g2a) mutant diff lines = $NDIFF, expected 2"; fi
  out=$(bash "$SCRATCH/planted_cap.sh" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 65 ] && echo "$out" | grep -q "ABORT G-CAP-PREREG arm O-P"; then ok "(g2b) a launcher enforcing 40.0 against a registered 25.0 -> rc=65 REFUSED before any container"; else bad "(g2b) rc=$rc: $(echo "$out" | tail -3)"; fi
  sed 's/CEILING=115.0/CEILING=999.0/' "$PRE" > "$SCRATCH/planted_prereg.md"
  sed "s#^PREREG=.*#PREREG=$SCRATCH/planted_prereg.md#" "$L" > "$SCRATCH/planted_ceiling.sh"
  out=$(bash "$SCRATCH/planted_ceiling.sh" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 65 ] && echo "$out" | grep -q "ABORT G-CAP-PREREG the registered CEILING"; then ok "(g3) a CEILING that is not the sum of the registered caps -> rc=65 REFUSED"; else bad "(g3) rc=$rc: $(echo "$out" | tail -3)"; fi
  grep -v "SO1BR-CAP-MANIFEST v1" "$PRE" > "$SCRATCH/noman_prereg.md"
  sed "s#^PREREG=.*#PREREG=$SCRATCH/noman_prereg.md#" "$L" > "$SCRATCH/planted_noman.sh"
  out=$(bash "$SCRATCH/planted_noman.sh" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 65 ] && echo "$out" | grep -q "names no SO1BR-CAP-MANIFEST v1 line"; then ok "(g4) a pre-registration carrying NO manifest line -> rc=65 REFUSED (a missing gate is never a passing gate)"; else bad "(g4) rc=$rc: $(echo "$out" | tail -3)"; fi
  sed "s#^PREREG=.*#PREREG=$SCRATCH/does_not_exist.md#" "$L" > "$SCRATCH/planted_nopre.sh"
  out=$(bash "$SCRATCH/planted_nopre.sh" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 65 ] && echo "$out" | grep -q "the frozen pre-registration is absent"; then ok "(g5) the pre-registration absent -> rc=65 REFUSED"; else bad "(g5) rc=$rc: $(echo "$out" | tail -3)"; fi
  HS=$(bash "$L" $ARM "$BOGUS" 2>&1 | grep -o "head_channel=[A-Z_]*" | head -1)
  ok "(g6) channel (b), the HEAD comparison, REPORTS its own state rather than assuming one: $HS -- NOT_MEASURED is the correct reading BEFORE the freeze commit, when this amendment is not yet at HEAD; channel (a) binds regardless, and this is stated rather than papered over"
else
  bad "(g) PREREGISTRATION.md is absent -- the cap-agreement preflight cannot be driven"
fi

# ---- CLEANUP: ONLY WHAT THIS SELFTEST CREATED, BY NAME ---------------------------
rm -rf "$SCRATCH"
rm -rf "$BASE/base" "$BASE/so1b_runScript.py" "$BASE/so1b_of.py"
chmod 775 "$BASE"
# the decoy MUST still be here, byte-intact
if [ -f "$DECOY" ] && [ "$(md5sum "$DECOY" | cut -d' ' -f1)" = "$DECOY_MD5" ]; then
  ok "(z1) W3-SELFTEST-DEF-1 CONTROL: the decoy this selftest did NOT create SURVIVED the named cleanup, byte-intact"
else bad "(z1) the decoy was destroyed or altered -- cleanup is not by name"; fi
rm -f "$DECOY"
N=$(find "$BASE" -mindepth 1 | wc -l)
if [ "$N" = "0" ]; then ok "(z2) temporary run root EMPTY after every invocation ($N entries)"; else bad "(z2) run root gained $N entries: $(find "$BASE" -mindepth 1 | head -5 | tr '\n' ' ')"; fi
rmdir "$BASE" 2>/dev/null
if [ ! -e "$BASE" ]; then ok "(z3) run root ABSENT after the test (the freeze condition): test -e $BASE -> false"; else bad "(z3) run root still present"; fi
SURV=$(sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -c "^so1br" || true)
if [ "$SURV" = "0" ]; then ok "(z4) no so1br* container survives in ANY state (ps -a, not ps)"; else bad "(z4) $SURV so1br* containers survive"; fi
CASE_AFTER_LIST=$(ls -1a "$HERE" | sort | md5sum | cut -d' ' -f1)
CASE_AFTER_SUM=$(find "$HERE" -maxdepth 1 -type f -exec md5sum {} + | sort -k2 | md5sum | cut -d' ' -f1)
if [ "$CASE_BEFORE_LIST" = "$CASE_AFTER_LIST" ] && [ "$CASE_BEFORE_SUM" = "$CASE_AFTER_SUM" ]; then
  ok "(z5) the CASE DIRECTORY is byte-unchanged: listing and content digests both match"
else bad "(z5) the case directory changed: list $CASE_BEFORE_LIST->$CASE_AFTER_LIST sum $CASE_BEFORE_SUM->$CASE_AFTER_SUM"; fi
echo "SO1bR G-ROOT5 SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
