#!/usr/bin/env bash
# SO-2a G-ROOT.5 SELFTEST -- ADOPTED from curriculum_SO1b/so1b_groot5_selftest.sh
# (md5 read at run time and printed below), driven against SO-2a's OWN FROZEN
# launcher so2a_run_arm.sh.  Discharges the requirement PREREGISTRATION.md:227
# (section 7.3) registered against this item:
#
#   "before this item is enqueued, the G-ROOT.5 container legs must be driven --
#    including a sacrificial container named so2a_<ARM>_... and a sacrificial
#    live pid with cwd inside the run root -- and the three new forbidden roots
#    must each be shown to abort at G-ROOT.1."
#
# WHAT SO-2a ACTUALLY REGISTERS, stated plainly because a sibling family
# registers something else.  SO-2a's G-ROOT.5 is "A LIVE ARM IS NEVER
# RE-STAGED" (so2a_run_arm.sh:234-267) and its refusal code is EXIT 3, on two
# live readings taken BEFORE any destructive act:
#   (a) a RUNNING container carrying so2a_<ARM>_ ;
#   (b) a driver pidfile in the run root naming a LIVE pid that is not an
#       ancestor of the launcher, or whose cwd IS the run root.
# A STALE pidfile does NOT block.  SO-2a's launcher does NOT refuse merely
# because the run root exists -- that clause belongs to the D12R2/W3 chain
# driver's phase 1 (exit 6) and SO-2a's driver instead re-stages on the FIRST
# fire only (so2a_chain_driver.sh:72-91).  Both directions are driven below and
# the observed codes are printed rather than assumed.
#
# CLEANUP DISCIPLINE -- W3-SELFTEST-DEF-1, PAID FOR ONCE IN THIS FAMILY ALREADY.
# d12y_w3_groot5_selftest.sh ran `rm -f STATUS.W3_chain` at its foot and deleted
# a REAL status file the queue runner had written, destroying evidence.  This
# selftest therefore:
#   * REFUSES to run at all if the run root already exists (exit 2), so nothing
#     inside it can pre-date the test;
#   * removes ONLY paths it recorded in CREATED[] at the moment it made them,
#     BY NAME, never by glob and never by sweep;
#   * DRIVES that discipline with a DECOY it did not create and requires the
#     decoy to SURVIVE the named cleanup;
#   * writes NOTHING into the case directory, and PROVES it by comparing a
#     sorted listing of the case directory before and after.
#
# SAFETY.  Legs (a)-(d) pass a BOGUS IMAGE and run on a temporary EMPTY run root
# at mode 775, so a launcher that got past G-ROOT.5 aborts at the L-251 mode
# check (exit 4) BEFORE any staging.  Leg (e) uses the REAL images but never
# drives arm MESH on the SHIPPED image: MESH is the ONE arm whose branch reaches
# `sudo -n rm -rf "$WORK"` (so2a_run_arm.sh:338), and every leg here refuses
# above that line.  The run root is created empty, emptied by name, removed with
# rmdir (which refuses a non-empty directory), and its ABSENCE afterwards is
# asserted -- that absence is the freeze condition of PREREGISTRATION.md.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
L="$HERE/so2a_run_arm.sh"
GRADER="$HERE/so2a_grade.py"
PRE="$HERE/PREREGISTRATION.md"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient
IMG_S=dafoam/opt-packages:latest
IMG_P=dafoam-idwarp-rot:v1
BOGUS=no-such-image:so2a-selftest
ARM=X-S
CPUSET=9
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
CREATED=()
mine() { CREATED+=("$1"); }

echo "SO2a G-ROOT.5 SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) launcher_md5=$(md5sum "$L" | cut -d' ' -f1) grader_md5=$(md5sum "$GRADER" | cut -d' ' -f1)"
echo "  adopted from: $HERE/../curriculum_SO1b/so1b_groot5_selftest.sh"

# ---- case-directory snapshot: this selftest writes NOTHING here -------------
CASE_BEFORE=$(ls -1a "$HERE" | sort | md5sum | cut -d' ' -f1)

# ---- ORDER, read out of the launcher's own bytes ---------------------------
G5=$(grep -n 'D4S_G_ROOT5_PASS' "$L" | head -1 | cut -d: -f1)
FIRSTOP=$(grep -nE '^[[:space:]]*[^#]*((sudo -n )?rm -rf|cp -a|docker run)' "$L" | grep -v '^[0-9]*:[[:space:]]*#' | head -1 | cut -d: -f1)
if [ -n "$G5" ] && [ -n "$FIRSTOP" ] && [ "$FIRSTOP" -gt "$G5" ]; then
  ok "(o1) G-ROOT.5 completes at :$G5, the FIRST destructive op is at :$FIRSTOP -- the guard is above the act"
else bad "(o1) order G5=$G5 FIRSTOP=$FIRSTOP"; exit 2; fi
# The backtick is built with printf rather than written, so THIS FILE contains
# no literal backtick at all and leg (o3) below cannot count its own pattern.
# FIRST DRIVE, 2026-08-30T23:06:53Z: the check was written with a literal
# backtick in its own grep and reported 2 hits IN ITSELF -- the same "a check
# that measured its own selftest" defect this item records at
# PREREGISTRATION.md:232 for the C5 regex.  Recorded here rather than quietly
# replaced.  A PLANTED POSITIVE follows so (o3)'s zero stays evidence.
BT=$(printf '\140')
NBT=$(grep -vE '^[[:space:]]*#' "$L" | grep -c "$BT" || true)
if [ "$NBT" = "0" ]; then ok "(o2) zero backticks on executable lines of the launcher"; else bad "(o2) $NBT backticks on executable lines"; fi
NBT2=$(grep -vE '^[[:space:]]*#' "$0" | grep -c "$BT" || true)
if [ "$NBT2" = "0" ]; then ok "(o3) zero backticks on executable lines of THIS selftest, and the pattern is BUILT not written, so this zero is not the counter failing to see itself"; else bad "(o3) $NBT2 backticks in this selftest"; fi
NBT3=$(printf 'x=%sdate%s\n' "$BT" "$BT" | grep -c "$BT" || true)
if [ "$NBT3" = "1" ]; then ok "(o3b) PLANTED POSITIVE: the same counter, handed one synthesised backticked line, returns 1 -- (o2) and (o3) are readings, not a blind pattern"; else bad "(o3b) the backtick counter cannot see a planted backtick ($NBT3)"; fi

# ---- the freeze condition, and the refusal that protects a real root -------
if [ -e "$BASE" ]; then
  bad "run root $BASE already EXISTS -- refusing to test over a real root; nothing was touched"
  exit 2
else ok "(o4) run root ABSENT before the test (freeze condition): $BASE"; fi
DOCKER_PRE=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | sort | tr '\n' ',' | sed 's/,$//')
ok "(o5) docker ps BEFORE the test: [$DOCKER_PRE]"

mkdir -p "$BASE" || { bad "could not create the temporary empty run root"; exit 2; }
mine "$BASE"

# =============================================================================
# MUST-REFUSE, direction 1 of 2: A LIVE ARM.  Run root PRESENT, a live reading
# says the arm is running, and the launcher must REFUSE and start NO container.
# =============================================================================
# (a) a sacrificial RUNNING container carrying so2a_<ARM>_ .  ONE cpuset (the
# item's registered 9), 0.1 core, 64 MB, an explicit name, a bounded sleep, and
# `docker rm -f` by that name at the end of the leg.
CN="so2a_${ARM}_selftest_$(date -u +%Y%m%dT%H%M%SZ)"
sudo -n docker run -d --name "$CN" --cpus=0.1 --cpuset-cpus=$CPUSET --memory=64m --memory-swap=64m "$IMG_S" bash -c "sleep 180" >/dev/null 2>&1 \
  || { bad "could not start the sacrificial container $CN"; rmdir "$BASE"; exit 2; }
LIVE_CHECK=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -c "^$CN$")
if [ "$LIVE_CHECK" = "1" ]; then ok "(a0) PLANTED CONTROL LIVE: the sacrificial container $CN is RUNNING, so leg (a)'s refusal is a reading and not an absence"; else bad "(a0) the sacrificial container is not running"; fi
NBEFORE=$(sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | wc -l)
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
NAFTER=$(sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | wc -l)
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 a RUNNING container"; then
  ok "(a) MUST-REFUSE: a LIVE arm container -> EXIT 3 -- $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-130)"
else bad "(a) rc=$rc (expected 3): $(echo "$out" | tail -2)"; fi
if [ "$NAFTER" = "$NBEFORE" ]; then ok "(a2) the launcher started NO container of its own: docker ps -a count $NBEFORE before, $NAFTER after"; else bad "(a2) container count moved $NBEFORE -> $NAFTER"; fi
if ! echo "$out" | grep -q "D4S_G_ROOT5_PASS"; then ok "(a3) the launcher never printed D4S_G_ROOT5_PASS -- it stopped AT the gate, not after it"; else bad "(a3) the guard printed PASS and refused anyway"; fi
sudo -n docker rm -f "$CN" >/dev/null 2>&1
sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^$CN$" && bad "(a4) $CN survives" || ok "(a4) the sacrificial container $CN is REMOVED by name"

# (b) a sacrificial LIVE pid whose cwd IS the run root, named in the pidfile.
( cd "$BASE" && exec sleep 180 ) & SPID=$!
echo "$SPID" > "$BASE/so2a_driver.pid"; mine "$BASE/so2a_driver.pid"
SCWD=$(readlink -f "/proc/$SPID/cwd" 2>/dev/null)
if [ "$SCWD" = "$BASE" ]; then ok "(b0) PLANTED CONTROL LIVE: pid $SPID is alive with cwd=$SCWD"; else bad "(b0) planted pid cwd=$SCWD"; fi
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 driver pidfile"; then
  ok "(b) MUST-REFUSE: a LIVE driver pid with cwd in the run root -> EXIT 3 -- $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-150)"
else bad "(b) rc=$rc (expected 3): $(echo "$out" | tail -2)"; fi
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null
rm -f "$BASE/so2a_driver.pid"

# (b2) a STALE pidfile must NOT block -- the guard must discriminate, not refuse.
echo "999999" > "$BASE/so2a_driver.pid"; mine "$BASE/so2a_driver.pid"
kill -0 999999 2>/dev/null && bad "(b2pre) pid 999999 is unexpectedly alive; this leg is void" || ok "(b2pre) the stale pid 999999 is confirmed DEAD before the leg"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "D4S_G_ROOT5_PASS" && echo "$out" | grep -q "ABORT L-251 run root mode"; then
  ok "(b2) a STALE pidfile is IGNORED: G-ROOT.5 passes and the launcher goes on to abort at the L-251 mode check (EXIT 4) -- nothing staged"
else bad "(b2) rc=$rc: $(echo "$out" | tail -2)"; fi
rm -f "$BASE/so2a_driver.pid"

# =============================================================================
# MUST-PROCEED: run root PRESENT and clear.  The launcher must get PAST
# G-ROOT.5 -- and here it is stopped by the NEXT gate, so nothing is staged.
# =============================================================================
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "D4S_G_ROOT5_PASS"; then
  ok "(c) MUST-PROCEED: run root PRESENT and clear -> $(echo "$out" | grep D4S_G_ROOT5_PASS | cut -c1-120) ; the launcher then aborts at the L-251 mode check (EXIT 4) before any staging"
else bad "(c) rc=$rc: $(echo "$out" | tail -2)"; fi
echo "$out" | grep -q "D4S_G_ROOT_PASS item=SO2a" && ok "(c2) G-ROOT.1-.3 also PASS on this item's own root, ledger_clean=yes" || bad "(c2) G-ROOT.1-.3 did not pass on the item's own root"
CAPLINE=$(echo "$out" | grep 'D4_CAP_ASSERT' | head -1)
ok "(c3) the OPERATIVE cap the launcher would enforce for $ARM, read from its own print: $CAPLINE"

# =============================================================================
# (d) G-ROOT.1 -- THE THREE SO-1 ROOTS, the registered requirement of section 7.3.
# SO-1a's root holds this box's only graded SO-1 evidence.  G-ROOT.1 is the FIRST
# act after BASE resolution, so this leg cannot touch what it names.
# =============================================================================
for forb in /home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient \
            /home/ubuntu/certonomous-runs/CURRICULUM-SO1b-a1-naca0012-dragmin-opt \
            /home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-postopt \
            /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin \
            /home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint \
            /home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality \
            /home/ubuntu/certonomous-runs \
            /home/ubuntu/Certonomous; do
  EX=$([ -e "$forb" ] && echo ON_DISK || echo not_on_disk)
  out=$(BASE="$forb" bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
  if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.1"; then
    ok "(d) BASE=$forb ($EX) -> EXIT 3, G-ROOT.1 REFUSED before any staging"
  else bad "(d) $forb rc=$rc: $(echo "$out" | tail -2)"; fi
done
# and the same guard must NOT refuse a root that only LOOKS different
out=$(BASE="$BASE/./" bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "D4S_G_ROOT_PASS"; then
  ok "(d2) DRIVEN CONTROL: the SAME root written with a trailing '/./' NORMALISES and is ACCEPTED (rc=4 at L-251) -- the guard compares realpaths, it does not compare strings"
else bad "(d2) rc=$rc on the normalised form of the item's own root"; fi

# (d3) G-ROOT.3 -- a FOREIGN ledger in this item's own root refuses.
echo "ITEM=D4" > "$BASE/ledger.txt"; mine "$BASE/ledger.txt"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.3"; then
  ok "(d3) a ledger carrying ITEM=D4 in this item's own root -> EXIT 3, G-ROOT.3 REFUSED"
else bad "(d3) rc=$rc: $(echo "$out" | tail -2)"; fi
echo "ITEM=SO2a" > "$BASE/ledger.txt"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "ledger_clean=yes"; then
  ok "(d4) DRIVEN CONTROL: the SAME ledger carrying ITEM=SO2a is ACCEPTED -- (d3)'s refusal is a reading of the line, not of the file's existence"
else bad "(d4) rc=$rc on this item's own ledger"; fi
rm -f "$BASE/ledger.txt"

# =============================================================================
# (e) THE REAL IMAGES, on the 777 root holding ONLY the three staged instruments.
# arm MESH is NEVER driven on the SHIPPED image here: MESH is the one branch that
# reaches `sudo -n rm -rf "$WORK"`, and every leg below refuses above that line.
# =============================================================================
chmod 777 "$BASE"
mkdir -p "$BASE/base/system"; mine "$BASE/base/system"; mine "$BASE/base"
cp -a "$HERE/so2a_runScript.py" "$BASE/so2a_runScript.py"; mine "$BASE/so2a_runScript.py"
cp -a "$HERE/so2a_xg.py" "$BASE/so2a_xg.py"; mine "$BASE/so2a_xg.py"
cp -a "$HERE/so2a_decomposeParDict" "$BASE/base/system/decomposeParDict"; mine "$BASE/base/system/decomposeParDict"
out=$(bash "$L" X-P "$IMG_S" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "ABORT G-ROW arm X-P is registered on the PATCHED row; got ROW=SHIPPED"; then
  ok "(e1) X-P on the SHIPPED image -> EXIT 4, G-ROW REFUSED before any staging"
else bad "(e1) rc=$rc: $(echo "$out" | tail -2)"; fi
out=$(bash "$L" MESH "$IMG_P" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "ABORT G-ROW arm MESH is registered on the SHIPPED row; got ROW=PATCHED"; then
  ok "(e2) MESH on the PATCHED image -> EXIT 4, G-ROW REFUSED before any staging (and this is the only form in which MESH is driven at all)"
else bad "(e2) rc=$rc: $(echo "$out" | tail -2)"; fi
out=$(bash "$L" X-S "$IMG_S" 2>&1); rc=$?
if [ "$rc" -eq 5 ] && echo "$out" | grep -q "D4S_G_ROW_PASS row=SHIPPED" && echo "$out" | grep -q "ABORT arm X-S expects an existing MESH/"; then
  ok "(e3) X-S on the SHIPPED image -> the md5s and the DIGEST verify, G-ROW PASSES, and the arm then REFUSES (EXIT 5) for want of the MESH arm's output -- nothing staged"
else bad "(e3) rc=$rc: $(echo "$out" | tail -2)"; fi
test -e "$BASE/X-S" && bad "(e4) an X-S directory was created" || ok "(e4) no arm directory was created by any leg"
echo "$out" | grep -q "D4_IMAGE_OK row=SHIPPED image=$IMG_S digest=sha256:9d45679d" && ok "(e5) the SHIPPED digest the launcher resolved is the registered one" || bad "(e5) SHIPPED digest not confirmed"

# =============================================================================
# (f) THE CAP AGREEMENT, driven -- the W3-LAUNCHER-DEF-1 class.  The OPERATIVE
# cap the launcher prints for every arm must equal the FROZEN grader's CAPS, and
# the ceiling must equal their sum.  Two frozen files, read independently.
# =============================================================================
CAPSUM=0
for a in MESH X-S G-S X-P G-P; do
  LC=$(bash "$L" "$a" "$BOGUS" 2>&1 | grep 'D4_CAP_ASSERT' | head -1 | sed 's/.*registered_core_min=\([0-9.]*\).*/\1/')
  GC=$(python3 -c "import re,sys; s=open('$GRADER').read(); m=re.search(r'^CAPS = (\{[^}]*\})', s, re.M); print(eval(m.group(1))['$a'])")
  if [ -n "$LC" ] && [ "$(python3 -c "print(abs($LC-$GC)<1e-9)")" = "True" ]; then
    ok "(f) arm $a: the LAUNCHER enforces $LC core-min and the FROZEN GRADER scores against $GC -- they AGREE"
  else bad "(f) arm $a: launcher=$LC grader=$GC DISAGREE"; fi
  CAPSUM=$(python3 -c "print('%.1f' % ($CAPSUM + ${LC:-0}))")
done
GCEIL=$(grep -oE '^ITEM_CEILING_CORE_MIN = [0-9.]+' "$GRADER" | head -1 | grep -oE '[0-9.]+$')
if [ "$(python3 -c "print(abs($CAPSUM-$GCEIL)<1e-9)")" = "True" ]; then
  ok "(f2) the five operative caps sum to $CAPSUM and the grader's ITEM_CEILING_CORE_MIN is $GCEIL -- a ceiling that is not the sum of the caps could not pass this leg"
else bad "(f2) sum of operative caps $CAPSUM != grader ceiling $GCEIL"; fi
grep -q 'ceiling 79.0' "$PRE" && ok "(f3) the FROZEN pre-registration names the same ceiling 79.0 (section 4)" || bad "(f3) the pre-registration does not name ceiling 79.0"
# REPORTED, NEVER GATED: a stale COMMENT inside the frozen launcher.
echo "  [NOTE] so2a_run_arm.sh's inline 'REGISTERED CAP TABLE' COMMENT (:186-192) still reads X 10.0 core-min / 600 s, inherited from SO-1a.  The OPERATIVE constant, the frozen grader and PREREGISTRATION.md section 4 all read 12.0 / 720 s, and section 7 registers the delta 'the X cap 10.0 -> 12.0'.  The comment is stale; the file is FROZEN and is not edited.  REPORTED, never gated."

# =============================================================================
# (g) THE CLEANUP DISCIPLINE ITSELF, DRIVEN -- W3-SELFTEST-DEF-1.
# A DECOY this selftest did not create must SURVIVE the named cleanup.
# =============================================================================
DECOY="$BASE/STATUS.not_written_by_this_selftest"
echo "a real status line a queue runner might have written" > "$DECOY"
NREM=0
for p in "${CREATED[@]}"; do
  [ "$p" = "$BASE" ] && continue
  if [ -f "$p" ]; then rm -f "$p"; NREM=$((NREM+1)); fi
done
for p in "$BASE/base/system" "$BASE/base"; do
  [ -d "$p" ] && rmdir "$p" 2>/dev/null && NREM=$((NREM+1))
done
if [ -f "$DECOY" ] && [ "$(head -c 4 "$DECOY")" = "a re" ]; then
  ok "(g) DRIVEN: the named cleanup removed $NREM path(s) IT recorded creating and the DECOY it did not create SURVIVED BYTE-INTACT -- W3-SELFTEST-DEF-1 cannot recur here"
else bad "(g) the decoy did not survive the cleanup -- this selftest deletes files it did not write"; fi
rm -f "$DECOY"
test -e "$DECOY" && bad "(g2) the decoy was not removed by its own named rm" || ok "(g2) the decoy is now removed BY ITS OWN NAME, by the line that created it"

CASE_AFTER=$(ls -1a "$HERE" | sort | md5sum | cut -d' ' -f1)
if [ "$CASE_BEFORE" = "$CASE_AFTER" ]; then
  ok "(g3) the CASE DIRECTORY listing is byte-identical before and after ($CASE_BEFORE) -- this selftest wrote and deleted nothing there at all"
else bad "(g3) the case directory listing CHANGED: $CASE_BEFORE -> $CASE_AFTER"; fi

# ---- LEAVE NOTHING ----------------------------------------------------------
chmod 775 "$BASE" 2>/dev/null
N=$(find "$BASE" -mindepth 1 | wc -l)
if [ "$N" = "0" ]; then ok "(z1) the temporary run root is EMPTY after every invocation and after the named cleanup ($N entries)"; else bad "(z1) run root holds $N entries: $(find "$BASE" -mindepth 1 | head -5 | tr '\n' ' ')"; fi
rmdir "$BASE" 2>/dev/null
if [ ! -e "$BASE" ]; then ok "(z2) run root ABSENT after the test (the freeze condition restored): test -e $BASE -> false"; else bad "(z2) the run root is still present"; fi
DOCKER_POST=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | sort | tr '\n' ',' | sed 's/,$//')
if [ "$DOCKER_POST" = "$DOCKER_PRE" ]; then ok "(z3) docker ps AFTER the test: [$DOCKER_POST] -- identical to before, nothing was left behind"; else bad "(z3) docker ps moved: [$DOCKER_PRE] -> [$DOCKER_POST]"; fi
sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^so2a_" && bad "(z4) a so2a_ container survives" || ok "(z4) no so2a_ container survives, running or stopped"

echo "SO2a G-ROOT5 SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
