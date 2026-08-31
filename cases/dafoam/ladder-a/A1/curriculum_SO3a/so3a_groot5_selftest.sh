#!/usr/bin/env bash
# SO-3a G-ROOT.5 SELFTEST -- ADOPTED from curriculum_SO1b/so1b_groot5_selftest.sh
# (md5 read at run time and printed below), driven against SO-3a's OWN FROZEN
# launcher so3a_run_arm.sh.  Discharges the requirement PREREGISTRATION.md:227
# (section 7.3) registered against this item:
#
#   "before this item is enqueued, the G-ROOT.5 container legs must be driven --
#    including a sacrificial container named so3a_<ARM>_... and a sacrificial
#    live pid with cwd inside the run root -- and the three new forbidden roots
#    must each be shown to abort at G-ROOT.1."
#
# WHAT SO-3a ACTUALLY REGISTERS, stated plainly because a sibling family
# registers something else.  SO-3a's G-ROOT.5 is "A LIVE ARM IS NEVER
# RE-STAGED" (so3a_run_arm.sh:234-267) and its refusal code is EXIT 3, on two
# live readings taken BEFORE any destructive act:
#   (a) a RUNNING container carrying so3a_<ARM>_ ;
#   (b) a driver pidfile in the run root naming a LIVE pid that is not an
#       ancestor of the launcher, or whose cwd IS the run root.
# A STALE pidfile does NOT block.  SO-3a's launcher does NOT refuse merely
# because the run root exists -- that clause belongs to the D12R2/W3 chain
# driver's phase 1 (exit 6) and SO-3a's driver instead re-stages on the FIRST
# fire only (so3a_chain_driver.sh:72-91).  Both directions are driven below and
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
# `sudo -n rm -rf "$WORK"` (so3a_run_arm.sh:338), and every leg here refuses
# above that line.  The run root is created empty, emptied by name, removed with
# rmdir (which refuses a non-empty directory), and its ABSENCE afterwards is
# asserted -- that absence is the freeze condition of PREREGISTRATION.md.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
L="$HERE/so3a_run_arm.sh"
GRADER="$HERE/so3a_grade.py"
PRE="$HERE/PREREGISTRATION.md"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO3a-a1-naca0012-alpha-multipoint-gradient
IMG_S=dafoam/opt-packages:latest
IMG_P=dafoam-idwarp-rot:v1
BOGUS=no-such-image:so3a-selftest
ARM=X-S
CPUSET=14
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
CREATED=()
mine() { CREATED+=("$1"); }

echo "SO3a G-ROOT.5 SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) launcher_md5=$(md5sum "$L" | cut -d' ' -f1) grader_md5=$(md5sum "$GRADER" | cut -d' ' -f1)"
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
# (a) a sacrificial RUNNING container carrying so3a_<ARM>_ .  ONE cpuset (the
# item's registered 9), 0.1 core, 64 MB, an explicit name, a bounded sleep, and
# `docker rm -f` by that name at the end of the leg.
CN="so3a_${ARM}_selftest_$(date -u +%Y%m%dT%H%M%SZ)"
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
echo "$SPID" > "$BASE/so3a_driver.pid"; mine "$BASE/so3a_driver.pid"
SCWD=$(readlink -f "/proc/$SPID/cwd" 2>/dev/null)
if [ "$SCWD" = "$BASE" ]; then ok "(b0) PLANTED CONTROL LIVE: pid $SPID is alive with cwd=$SCWD"; else bad "(b0) planted pid cwd=$SCWD"; fi
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 3 ] && echo "$out" | grep -q "ABORT G-ROOT.5 driver pidfile"; then
  ok "(b) MUST-REFUSE: a LIVE driver pid with cwd in the run root -> EXIT 3 -- $(echo "$out" | grep 'ABORT G-ROOT.5' | cut -c1-150)"
else bad "(b) rc=$rc (expected 3): $(echo "$out" | tail -2)"; fi
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null
rm -f "$BASE/so3a_driver.pid"

# (b2) a STALE pidfile must NOT block -- the guard must discriminate, not refuse.
echo "999999" > "$BASE/so3a_driver.pid"; mine "$BASE/so3a_driver.pid"
kill -0 999999 2>/dev/null && bad "(b2pre) pid 999999 is unexpectedly alive; this leg is void" || ok "(b2pre) the stale pid 999999 is confirmed DEAD before the leg"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "D4S_G_ROOT5_PASS" && echo "$out" | grep -q "ABORT L-251 run root mode"; then
  ok "(b2) a STALE pidfile is IGNORED: G-ROOT.5 passes and the launcher goes on to abort at the L-251 mode check (EXIT 4) -- nothing staged"
else bad "(b2) rc=$rc: $(echo "$out" | tail -2)"; fi
rm -f "$BASE/so3a_driver.pid"

# =============================================================================
# MUST-PROCEED: run root PRESENT and clear.  The launcher must get PAST
# G-ROOT.5 -- and here it is stopped by the NEXT gate, so nothing is staged.
# =============================================================================
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "D4S_G_ROOT5_PASS"; then
  ok "(c) MUST-PROCEED: run root PRESENT and clear -> $(echo "$out" | grep D4S_G_ROOT5_PASS | cut -c1-120) ; the launcher then aborts at the L-251 mode check (EXIT 4) before any staging"
else bad "(c) rc=$rc: $(echo "$out" | tail -2)"; fi
echo "$out" | grep -q "D4S_G_ROOT_PASS item=SO3a" && ok "(c2) G-ROOT.1-.3 also PASS on this item's own root, ledger_clean=yes" || bad "(c2) G-ROOT.1-.3 did not pass on the item's own root"
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
echo "ITEM=SO3a" > "$BASE/ledger.txt"
out=$(bash "$L" $ARM "$BOGUS" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q "ledger_clean=yes"; then
  ok "(d4) DRIVEN CONTROL: the SAME ledger carrying ITEM=SO3a is ACCEPTED -- (d3)'s refusal is a reading of the line, not of the file's existence"
else bad "(d4) rc=$rc on this item's own ledger"; fi
rm -f "$BASE/ledger.txt"

# =============================================================================
# (e) THE REAL IMAGES, on the 777 root holding ONLY the three staged instruments.
# arm MESH is NEVER driven on the SHIPPED image here: MESH is the one branch that
# reaches `sudo -n rm -rf "$WORK"`, and every leg below refuses above that line.
# =============================================================================
chmod 777 "$BASE"
mkdir -p "$BASE/base/system"; mine "$BASE/base/system"; mine "$BASE/base"
cp -a "$HERE/so3a_runScript.py" "$BASE/so3a_runScript.py"; mine "$BASE/so3a_runScript.py"
cp -a "$HERE/so3a_xf.py" "$BASE/so3a_xf.py"; mine "$BASE/so3a_xf.py"
cp -a "$HERE/so3a_decomposeParDict" "$BASE/base/system/decomposeParDict"; mine "$BASE/base/system/decomposeParDict"

# ---- SO-3a REGISTERED STATE OF THESE LEGS, AND WHY THEY ASSERT A REFUSAL THE
# ---- PARENT'S ASSERTED A PASS FOR.
# The parent's (e1)-(e3) expected the staged-instrument md5s to VERIFY and the
# run to proceed to G-ROW.  SO-3a's instrument pins are deliberately the
# FAIL-CLOSED SENTINEL until the Stage-2 amendment (so3a_run_arm.sh MD5_UNSET),
# because a pin table filled in for whichever files happen to exist is the
# SO2a-DRIVER-DEF-1 shape.  So the launcher REFUSES at the md5 re-assertion
# BEFORE it reaches G-ROW, at rc=4, and that is the CORRECT PRE-AMENDMENT
# BEHAVIOUR -- the guard doing its job, not a leg failing.
# THE LEGS THEREFORE ASSERT THE REFUSAL, AND NAME WHAT THEY BECOME.  At the
# Stage-2 amendment the pins are set, these three legs stop reading the md5
# refusal and start reading G-ROW's, and THAT FLIP IS ITSELF THE AMENDMENT'S
# EVIDENCE: a leg that passed identically before and after would not have been
# testing the pin.  Re-running this selftest after the amendment is a REGISTERED
# obligation of it, not an optional re-check.
md5_refusal() { echo "$1" | grep -q "md5 drifted\|computed checksum did NOT match\|ABORT staged"; }

out=$(bash "$L" X-P "$IMG_S" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && md5_refusal "$out"; then
  ok "(e1) X-P on the SHIPPED image -> EXIT 4 at the FAIL-CLOSED instrument pin, before staging.  PRE-AMENDMENT STATE; at the amendment this leg reads G-ROW's refusal instead"
elif [ "$rc" -eq 4 ] && echo "$out" | grep -q "ABORT G-ROW arm X-P is registered on the PATCHED row"; then
  ok "(e1) POST-AMENDMENT STATE: the pins verify and G-ROW refuses X-P on the SHIPPED image -> EXIT 4"
else bad "(e1) rc=$rc: $(echo "$out" | tail -2)"; fi

out=$(bash "$L" MESH "$IMG_P" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && md5_refusal "$out"; then
  ok "(e2) MESH on the PATCHED image -> EXIT 4 at the FAIL-CLOSED pin (and this is the only form in which MESH is driven at all).  PRE-AMENDMENT STATE"
elif [ "$rc" -eq 4 ] && echo "$out" | grep -q "ABORT G-ROW arm MESH is registered on the SHIPPED row"; then
  ok "(e2) POST-AMENDMENT STATE: G-ROW refuses MESH on the PATCHED image -> EXIT 4"
else bad "(e2) rc=$rc: $(echo "$out" | tail -2)"; fi

out=$(bash "$L" X-S "$IMG_S" 2>&1); rc=$?
if [ "$rc" -eq 4 ] && md5_refusal "$out"; then
  ok "(e3) X-S on the SHIPPED image -> EXIT 4 at the FAIL-CLOSED pin, above every destructive act.  PRE-AMENDMENT STATE; at the amendment this becomes EXIT 5 for want of the MESH arm's output"
elif [ "$rc" -eq 5 ] && echo "$out" | grep -q "ABORT arm X-S expects an existing MESH/"; then
  ok "(e3) POST-AMENDMENT STATE: the pins verify, G-ROW passes, and the arm REFUSES (EXIT 5) for want of the MESH arm's output"
else bad "(e3) rc=$rc: $(echo "$out" | tail -2)"; fi

test -e "$BASE/X-S" && bad "(e4) an X-S directory was created" || ok "(e4) no arm directory was created by any leg"

# (e5) THE DIGEST.  The launcher refuses at the pin BEFORE it resolves an image,
# so this reading is genuinely UNAVAILABLE pre-amendment.  It is reported as NOT
# EXERCISED rather than inferred from the absence of a failure -- a control that
# was never run is never counted as a pass.  The registered digest is confirmed
# to be PRESENT IN THE LOCAL STORE by an independent reader, which is a weaker
# statement and is labelled as one.
if echo "$out" | grep -q "D4_IMAGE_OK row=SHIPPED image=$IMG_S digest=sha256:9d45679d"; then
  ok "(e5) the SHIPPED digest the launcher resolved is the registered one"
else
  LOCAL_D=$(sudo -n docker image inspect "$IMG_S" --format '{{index .RepoDigests 0}}' 2>/dev/null | sed 's/.*@//')
  if [ -n "$LOCAL_D" ]; then
    echo "  [NOT EXERCISED] (e5) the launcher refuses at the FAIL-CLOSED pin before resolving an image, so its OWN digest reading is unavailable pre-amendment.  Independent reader says the local store holds $IMG_S at ${LOCAL_D:0:20}...  NOT EXERCISED IS NEVER COUNTED AS A PASS"
  else
    echo "  [NOT EXERCISED] (e5) the launcher refuses at the FAIL-CLOSED pin before resolving an image, and no local digest could be read independently either"
  fi
fi

# =============================================================================
# (f) THE CAP AGREEMENT, driven -- the W3-LAUNCHER-DEF-1 class.  The OPERATIVE
# cap the launcher prints for every arm must equal the FROZEN grader's CAPS, and
# the ceiling must equal their sum.  Two frozen files, read independently.
# =============================================================================
CAPSUM=0
for a in MESH X-S F-S X-P F-P; do
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
grep -q 'ceiling 115.0' "$PRE" && ok "(f3) the FROZEN pre-registration names the same ceiling 115.0 (line 8 / section 4)" || bad "(f3) the pre-registration does not name ceiling 115.0"
# REPORTED, NEVER GATED: a stale COMMENT inside the frozen launcher.
echo "  [NOTE] so3a_run_arm.sh's inline 'REGISTERED CAP TABLE' COMMENT (:186-192) still reads X 10.0 core-min / 600 s, inherited from SO-1a.  The OPERATIVE constant, the frozen grader and PREREGISTRATION.md section 4 all read 12.0 / 720 s, and section 7 registers the delta 'the X cap 10.0 -> 12.0'.  The comment is stale; the file is FROZEN and is not edited.  REPORTED, never gated."

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
sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^so3a_" && bad "(z4) a so3a_ container survives" || ok "(z4) no so3a_ container survives, running or stopped"


# =============================================================================
# (x) THE CROSS-FILE AGREEMENT LEGS.  ADDED BECAUSE A MUTATION DRIVE MEASURED
#     THAT NOTHING CHECKED THEM -- not because they seemed like a good idea.
#
# On 2026-08-31 so3a_run_arm.sh was mutated four ways and the grader's 91-unit
# suite was run against each, rc captured directly and never through a pipe.
# Renaming a ledger field failed the suite loudly.  But CPUSET 14 -> 7, the X-arm
# cap 15.0 -> 9.0, and replacing the registered row table with a suffix glob ALL
# LEFT THE SUITE GREEN.  The reason is structural: the grader's fixture passes
# cpuset and caps INTO the launcher's ledger-row function as ARGUMENTS from the
# GRADER'S OWN constants, so the launcher's values are never read on that path.
# At RUN time a drift is caught, because the row carries the launcher's value and
# G10/G12 compare it against the grader's.  NOTHING CHECKED THE TWO FILES AGREE
# AT BUILD TIME, which is the window in which a drift is cheap to fix.
#
# Every leg below reads BOTH files and compares.  Each is then PROVED ABLE TO
# FAIL by planting the disagreement in a COPY -- never in the real file -- and
# requiring the same comparison to go red.  A leg that has only ever agreed is a
# claim about the pattern, not about the files (L-400).
# =============================================================================
echo ""
echo "(x) CROSS-FILE AGREEMENT -- launcher vs comparator vs producer"

# The comparator is the authority on its own constants; ask IT rather than
# re-implement its table here, which would be a third place to drift.
gconst() { python3 -c "
import sys; sys.path.insert(0,'$HERE')
import so3a_grade as G
print($1)
" 2>/dev/null; }

# ---- x1  cpuset -------------------------------------------------------------
L_CPUSET=$(grep -oP '^CPUSET=\K[0-9,]+' "$L" | head -1)
G_CPUSET=$(gconst 'G.CPUSET_REGISTERED')
if [ -n "$L_CPUSET" ] && [ "$L_CPUSET" = "$G_CPUSET" ]; then
  ok "(x1) cpuset agrees: launcher=$L_CPUSET comparator=$G_CPUSET"
else bad "(x1) cpuset DISAGREES: launcher=$L_CPUSET comparator=$G_CPUSET"; fi

# ---- x2  the cap table, per declared arm ------------------------------------
ARMS_D=$(gconst '" ".join(G.ARMS_DECLARED)')
capfail=0
for a in $ARMS_D; do
  lc=$(bash -c ". '$L' --source-only >/dev/null 2>&1; cap_core_min $a")
  gc=$(gconst "G.CAPS['$a']")
  [ "$(python3 -c "print(abs(float('$lc')-float('$gc'))<1e-9)")" = "True" ] || { capfail=1; echo "      $a launcher=$lc comparator=$gc"; }
done
[ "$capfail" -eq 0 ] && ok "(x2) the cap table agrees on all 5 declared arms" \
                     || bad "(x2) the cap table DISAGREES -- see the rows above"

# ---- x3  memory and ranks, per declared arm ---------------------------------
memfail=0; rankfail=0
for a in $ARMS_D; do
  lm=$(bash -c ". '$L' --source-only >/dev/null 2>&1; cap_memory $a")
  lr=$(bash -c ". '$L' --source-only >/dev/null 2>&1; ranks_of $a")
  [ "$lm" = "12g" ] || { memfail=1; echo "      $a memory=$lm want 12g"; }
  [ "$lr" = "1" ]   || { rankfail=1; echo "      $a ranks=$lr want 1"; }
done
[ "$memfail" -eq 0 ] && ok "(x3a) every declared arm carries the registered 12g memory cap" \
                     || bad "(x3a) a memory cap is not the registered 12g"
[ "$rankfail" -eq 0 ] && ok "(x3b) every declared arm is np = 1 (DAFOAM_CHARTER section 5)" \
                      || bad "(x3b) an arm is not np = 1"

# ---- x4  the arm -> row mapping, and the undeclared-arm refusal -------------
rowfail=0
for a in $ARMS_D; do
  lr=$(bash -c ". '$L' --source-only >/dev/null 2>&1; row_of $a")
  gr=$(gconst "G.ARM_ROW['$a']")
  [ "$lr" = "$gr" ] || { rowfail=1; echo "      $a launcher=$lr comparator=$gr"; }
done
[ "$rowfail" -eq 0 ] && ok "(x4) the arm -> row mapping agrees on all 5 declared arms" \
                     || bad "(x4) the arm -> row mapping DISAGREES"
UND=$(bash -c ". '$L' --source-only >/dev/null 2>&1; row_of Q-S")
if [ -z "$UND" ]; then
  ok "(x4b) an UNDECLARED arm (Q-S) gets NO row -- the parent's *-S glob would have handed it SHIPPED"
else bad "(x4b) undeclared arm Q-S was handed row '$UND'"; fi

# ---- x5  the comment cap table vs the code it documents ---------------------
# The derivation inherited the PARENT's numbers in this comment while the code
# already carried SO-3a's, and only the code was right.  A comment table that
# contradicts its own code is what a reviewer in a hurry reads.
docfail=0
while read -r a want; do
  got=$(bash -c ". '$L' --source-only >/dev/null 2>&1; cap_core_min $a")
  [ "$(python3 -c "print(abs(float('$got')-float('$want'))<1e-9)")" = "True" ] \
    || { docfail=1; echo "      comment says $a=$want, code says $got"; }
done < <(sed -n 's/^#   \([A-Z][A-Z0-9-]*\)  *1  *\([0-9.]*\).*/\1 \2/p' "$L")
[ "$docfail" -eq 0 ] && ok "(x5) the cap COMMENT TABLE agrees with cap_core_min() -- doc and code" \
                     || bad "(x5) the cap comment table CONTRADICTS the code it documents"

# ---- x6  the md5 pins are the fail-closed sentinel while any instrument is absent
NINE="so3a_chain_driver.sh so3a_run_arm.sh so3a_xf.py so3a_grade.py so3a_runScript.py
so3a_aggregate_memory.py so3a_groot5_selftest.sh so3a_decomposeParDict so3a_stop_marker.sh"
MISSING=""
for f in $NINE; do [ -f "$HERE/$f" ] || MISSING="$MISSING $f"; done
NPRESENT=$(for f in $NINE; do [ -f "$HERE/$f" ] && echo x; done | wc -l)
echo "      section 18.3 EXISTENCE FIRST: present=$NPRESENT of 9;${MISSING:- none absent}"
UNSET_PINS=$(grep -c '=\$MD5_UNSET' "$L")
if [ -n "$MISSING" ]; then
  [ "$UNSET_PINS" -ge 2 ] && ok "(x6) instruments are INCOMPLETE and the launcher's instrument pins are the FAIL-CLOSED sentinel ($UNSET_PINS of them) -- no partial pin table" \
                          || bad "(x6) instruments are incomplete but the launcher carries $UNSET_PINS sentinel pins"
else
  ok "(x6) all nine instruments EXIST; the pins are set at the Stage-2 amendment, not here"
fi

# ---- x7  the producer's anchor appears EXACTLY ONCE -------------------------
# so3a_xf.py REFUSES (exit 2) otherwise, and this lane shipped a docstring that
# carried the anchor THREE times -- every arm would have refused before writing
# an artefact.  The anchor is read OUT OF THE INSTRUMENT, never spelled here.
ANCH=$(python3 -c "
import sys; sys.path.insert(0,'$HERE')
import so3a_xf as XF; print(XF.ANCHOR)")
NANCH=$(grep -Fc -- "$ANCH" "$HERE/so3a_runScript.py")
if [ "$NANCH" -eq 1 ]; then
  ok "(x7) the producer carries the instrument's anchor EXACTLY ONCE (count=$NANCH)"
else bad "(x7) the producer carries the anchor $NANCH times -- so3a_xf.py:478 would REFUSE every arm"; fi

# ---- x8  the producer declares the registered alphas, weights and scenarios --
PCHK=$(python3 - "$HERE" <<'PYX'
import sys, types
HERE = sys.argv[1]
sys.path.insert(0, HERE)
def stub(n, **a):
    m = types.ModuleType(n); [setattr(m, k, v) for k, v in a.items()]; sys.modules[n] = m
class B:
    def __init__(self, *a, **k): pass
class MP(B): pass
stub("mpi4py"); sys.modules["mpi4py"].MPI = types.SimpleNamespace(
    COMM_WORLD=types.SimpleNamespace(rank=0, size=1))
stub("openmdao"); stub("openmdao.api", ExecComp=B, IndepVarComp=B, Problem=B)
stub("mphys"); stub("mphys.multipoint", Multipoint=MP)
stub("mphys.scenario_aerodynamic", ScenarioAerodynamic=B)
stub("dafoam"); stub("dafoam.mphys", DAFoamBuilder=B, OptFuncs=B)
stub("pygeo"); stub("pygeo.mphys", OM_DVGEOCOMP=B)
import ast
import so3a_xf as XF
src = open(HERE + "/so3a_runScript.py").read()
ns = {"__name__": "hdr", "__file__": "so3a_runScript.py"}
saved = list(sys.argv); sys.argv = ["so3a_runScript.py", "-task", "run_model"]
exec(compile(src.split(XF.ANCHOR)[0], "so3a_runScript.py", "exec"), ns)
sys.argv = saved
bad = []
if ns["ALPHAS"] != list(XF.ALPHAS_REGISTERED): bad.append("ALPHAS")
if ns["WEIGHTS"] != list(XF.WEIGHTS_REGISTERED): bad.append("WEIGHTS")
if ns["SCENARIOS"] != list(XF.SCENARIOS): bad.append("SCENARIOS")
if ns["daOptions"]["solverName"] != "DASimpleFoam": bad.append("solverName")
# the AST absence checks: no optimiser CONSTRUCTED, CALLED or CONFIGURED, and
# shape the only design variable.  BY TREE, because a text scan cannot tell a
# COMMENT from CODE and this file's docstring names what it removed.
mod = ast.parse(src)
calls = [f.func.attr if isinstance(f.func, ast.Attribute) else getattr(f.func, "id", "")
         for f in ast.walk(mod) if isinstance(f, ast.Call)]
attrs = [t.attr for nd in ast.walk(mod) if isinstance(nd, ast.Assign)
         for t in nd.targets if isinstance(t, ast.Attribute)]
if set(calls) & {"pyOptSparseDriver", "run_driver", "ScipyOptimizeDriver", "findFeasibleDesign"}:
    bad.append("optimiser_call")
if set(attrs) & {"driver", "opt_settings", "hist_file"}: bad.append("optimiser_attr")
dv = [nd.args[0].value for nd in ast.walk(mod)
      if isinstance(nd, ast.Call) and isinstance(nd.func, ast.Attribute)
      and nd.func.attr == "add_design_var" and nd.args
      and isinstance(nd.args[0], ast.Constant)]
if dv != ["shape"]: bad.append("design_vars=%s" % dv)
if any(str(d).startswith("patchV") for d in dv): bad.append("patchV_is_a_DV")
if sum(1 for x in ast.walk(mod) if isinstance(x, ast.Assert)) != 0: bad.append("ast_assert")
print("OK" if not bad else "BAD:" + ",".join(bad))
PYX
)
if [ "$PCHK" = "OK" ]; then
  ok "(x8) the producer declares the registered alphas, weights, scenarios and solver, carries NO optimiser in its TREE, and makes shape its only design variable"
else bad "(x8) producer contract: $PCHK"; fi

# ---- x9  THE KNOWN POSITIVES.  Every comparison above is now shown able to FAIL,
# ---- on COPIES in a temp dir.  The real files are never touched.
KP="$(mktemp -d)"; CREATED+=("$KP")
cp -a "$L" "$KP/launcher_planted.sh"
sed -i 's/^CPUSET=14/CPUSET=7/' "$KP/launcher_planted.sh"
KP_CPUSET=$(grep -oP '^CPUSET=\K[0-9,]+' "$KP/launcher_planted.sh" | head -1)
[ "$KP_CPUSET" != "$G_CPUSET" ] \
  && ok "(x9a) KNOWN POSITIVE: the cpuset comparison goes RED on a planted copy (7 != $G_CPUSET)" \
  || bad "(x9a) the cpuset comparison could not be made to fail"
cp -a "$L" "$KP/launcher_cap.sh"
sed -i 's/X-S|X-P)  echo 15.0 ;;/X-S|X-P)  echo 9.0 ;;/' "$KP/launcher_cap.sh"
KPC=$(bash -c ". '$KP/launcher_cap.sh' --source-only >/dev/null 2>&1; cap_core_min X-S")
[ "$KPC" = "9.0" ] \
  && ok "(x9b) KNOWN POSITIVE: the cap comparison sees a planted 9.0 against the registered 15.0" \
  || bad "(x9b) the cap comparison could not be made to fail (read $KPC)"
cp -a "$L" "$KP/launcher_row.sh"
python3 - "$KP/launcher_row.sh" <<'PYR'
import sys
p = sys.argv[1]; s = open(p).read()
open(p, "w").write(s.replace("    X-P)   echo PATCHED ;;", "    X-P)   echo SHIPPED ;;", 1))
PYR
KPR=$(bash -c ". '$KP/launcher_row.sh' --source-only >/dev/null 2>&1; row_of X-P")
[ "$KPR" = "SHIPPED" ] \
  && ok "(x9c) KNOWN POSITIVE: the row-mapping comparison sees a planted X-P -> SHIPPED" \
  || bad "(x9c) the row-mapping comparison could not be made to fail (read $KPR)"
cp -a "$HERE/so3a_runScript.py" "$KP/producer_planted.py"
printf '\n# %s\n' "$ANCH" >> "$KP/producer_planted.py"
KPA=$(grep -Fc -- "$ANCH" "$KP/producer_planted.py")
[ "$KPA" -eq 2 ] \
  && ok "(x9d) KNOWN POSITIVE: the anchor count reads 2 on a planted copy -- the count is real" \
  || bad "(x9d) the anchor count could not be made to move (read $KPA)"
rm -rf "$KP"

# ---- x10 the row-label call-site sweep, over ALL NINE, via the comparator ----
SWEEP=$(python3 -c "
import sys, os; sys.path.insert(0,'$HERE')
import so3a_grade as G
present, absent = G.so3a_instrument_files()
hits = {os.path.basename(f): G.row_label_call_sites(f) for f in present}
n = sum(len(v) for v in hits.values())
print('%d %d %d' % (n, len(present), len(absent)))")
SW_N=$(echo "$SWEEP" | cut -d' ' -f1); SW_P=$(echo "$SWEEP" | cut -d' ' -f2); SW_A=$(echo "$SWEEP" | cut -d' ' -f3)
if [ "$SW_N" -eq 0 ]; then
  ok "(x10) row-label sweep: 0 short-form literals and 0 positional derivations across $SW_P instruments ($SW_A not built)"
else bad "(x10) row-label sweep found $SW_N call sites across $SW_P instruments"; fi

# ---- x11 THE THIRD CALL SITE OF THE ARM -> ROW MAPPING: THE CHAIN DRIVER.
# (x4) compares the LAUNCHER against the COMPARATOR and was green while a THIRD
# consumer -- so3a_chain_driver.sh's `img_of` -- derived the row from an ARM-NAME
# SUFFIX GLOB.  Two agreeing call sites say nothing about a third.  This leg reads
# the driver's OWN registry out of its OWN bytes (no re-spelling here) and
# requires all three to agree on every declared arm AND to refuse an undeclared
# one.  It is proved able to fail on a planted copy below.
DRV="$HERE/so3a_chain_driver.sh"
drv_row() { sed -n '/^row_of_arm() {/,/^}/p' "$1" > "$2"; }
X11T="$(mktemp -d)"; CREATED+=("$X11T")
drv_row "$DRV" "$X11T/reg.sh"
if [ ! -s "$X11T/reg.sh" ]; then
  bad "(x11) the chain driver carries no readable row_of_arm registry"
else
  drvfail=0
  for a in $ARMS_D; do
    dr=$(bash -c ". '$X11T/reg.sh'; row_of_arm $a")
    lr=$(bash -c ". '$L' --source-only >/dev/null 2>&1; row_of $a")
    gr=$(gconst "G.ARM_ROW['$a']")
    { [ "$dr" = "$lr" ] && [ "$dr" = "$gr" ]; } || { drvfail=1; echo "      $a driver=$dr launcher=$lr comparator=$gr"; }
  done
  [ "$drvfail" -eq 0 ] && ok "(x11) the arm -> row mapping agrees across ALL THREE call sites (driver, launcher, comparator) on all 5 declared arms" \
                       || bad "(x11) the THREE call sites of the arm -> row mapping DISAGREE"
  UNDD=$(bash -c ". '$X11T/reg.sh'; row_of_arm Q-S")
  [ -z "$UNDD" ] && ok "(x11b) the DRIVER too refuses an undeclared arm (Q-S -> no row); the suffix glob it replaced returned the SHIPPED image for exactly that arm, MEASURED" \
                 || bad "(x11b) the driver handed undeclared arm Q-S the row '$UNDD'"
  # KNOWN POSITIVE: the three-way comparison must go RED on a planted copy.
  cp -a "$DRV" "$X11T/drv_planted.sh"
  python3 - "$X11T/drv_planted.sh" <<'PYD'
import sys
p = sys.argv[1]; s = open(p).read()
open(p, "w").write(s.replace("    X-P)   echo PATCHED ;;", "    X-P)   echo SHIPPED ;;", 1))
PYD
  drv_row "$X11T/drv_planted.sh" "$X11T/reg_planted.sh"
  KPD=$(bash -c ". '$X11T/reg_planted.sh'; row_of_arm X-P")
  [ "$KPD" = "SHIPPED" ] \
    && ok "(x11c) KNOWN POSITIVE: the driver-side comparison sees a planted X-P -> SHIPPED, so (x11)'s agreement is a reading of the driver's bytes" \
    || bad "(x11c) the driver-side comparison could not be made to fail (read $KPD)"
fi
rm -rf "$X11T"

# =============================================================================
# (x12)-(x14) THE md5 PIN TABLE: PINS DRIVEN vs PINS DECLARED.
#
# SO-1c's equivalent leg DROVE FOUR PINS OF TWELVE under a printed label reading
# "EVERY md5 PIN IN THE DRIVER", and NO leg could see the gap -- the label was the
# only thing asserting completeness, and a label is not a count.  A stale pin
# aborts this chain at rc=4 BEFORE any container starts, so an undriven pin is a
# whole run lost to a string.
#
# So the count is DERIVED FROM THE FILE, not written here: (x12) drives every
# IN-REPO pin, (x13) every OUT-OF-TREE tutorial pin, and (x14) asserts that
# driven == declared by re-counting the declared pins out of the driver's own
# bytes.  An EMPTY read on either side is a REFUSAL, never a match -- two empty
# strings compare equal, which is how a renamed pin variable passes a naive check.
# =============================================================================
echo ""
echo "(x12-x14) md5 PIN TABLE -- pins DRIVEN versus pins DECLARED"
DRVF="$HERE/so3a_chain_driver.sh"
TUT_SRC=$(grep -oP '^TUT_SRC=\K\S+' "$DRVF" | tr -d '"' | head -1)

pin_of() { grep -oP "^$1=\K[0-9a-f]{32}" "$DRVF" | head -1; }
PINFAIL=0; PINSEEN=0
while read -r v f; do
  p=$(pin_of "$v")
  a=$([ -f "$HERE/$f" ] && md5sum "$HERE/$f" | cut -d' ' -f1)
  if [ -z "$p" ]; then echo "      PIN UNREADABLE $v: no 32-hex pin under that name (renamed or deleted variable) -- an EMPTY read REFUSES"; PINFAIL=1; continue; fi
  if [ -z "$a" ]; then echo "      FILE UNREADABLE $f: no md5 (absent or unreadable) -- an EMPTY read REFUSES"; PINFAIL=1; continue; fi
  PINSEEN=$((PINSEEN+1))
  [ "$p" = "$a" ] || { echo "      PIN MISMATCH $v pinned=$p actual=$a ($f)"; PINFAIL=1; }
done <<'PINS'
MD5_LAUNCHER so3a_run_arm.sh
MD5_GRADER so3a_grade.py
MD5_RUNSCRIPT so3a_runScript.py
MD5_XF so3a_xf.py
MD5_AGG so3a_aggregate_memory.py
MD5_DECOMP so3a_decomposeParDict
MD5_STOP_MARKER so3a_stop_marker.sh
PINS
[ "$PINSEEN" = "7" ] || { echo "      PIN COUNT $PINSEEN in-repo pins compared, expected 7"; PINFAIL=1; }
[ "$PINFAIL" -eq 0 ] && ok "(x12) ALL SEVEN IN-REPO md5 PINS IN THE DRIVER EQUAL THE FILES THEY PIN ($PINSEEN compared), empty reads REFUSING.  The six MD5_TUT_* pins name OUT-OF-TREE tutorial inputs and are driven by (x13); the exclusion is STATED, not silent" \
                     || bad "(x12) an in-repo md5 pin does not equal the file it pins"

TUTFAIL=0; TUTSEEN=0
while read -r v f; do
  p=$(pin_of "$v")
  a=$([ -f "$TUT_SRC/$f" ] && md5sum "$TUT_SRC/$f" | cut -d' ' -f1)
  if [ -z "$p" ]; then echo "      PIN UNREADABLE $v -- an EMPTY read REFUSES"; TUTFAIL=1; continue; fi
  if [ -z "$a" ]; then echo "      FILE UNREADABLE $TUT_SRC/$f -- an EMPTY read REFUSES"; TUTFAIL=1; continue; fi
  TUTSEEN=$((TUTSEEN+1))
  [ "$p" = "$a" ] || { echo "      PIN MISMATCH $v pinned=$p actual=$a ($TUT_SRC/$f)"; TUTFAIL=1; }
done <<'TPINS'
MD5_TUT_RUNSCRIPT runScript.py
MD5_TUT_GEN genAirFoilMesh.py
MD5_TUT_PREPROC preProcessing.sh
MD5_TUT_PS profiles/NACA0012PS.profile
MD5_TUT_SS profiles/NACA0012SS.profile
MD5_TUT_FFD FFD/wingFFD.xyz
TPINS
[ "$TUTSEEN" = "6" ] || { echo "      PIN COUNT $TUTSEEN out-of-tree pins compared, expected 6"; TUTFAIL=1; }
[ "$TUTFAIL" -eq 0 ] && ok "(x13) ALL SIX OUT-OF-TREE MD5_TUT_* PINS EQUAL THE TUTORIAL INPUTS THEY PIN under $TUT_SRC ($TUTSEEN compared) -- the driver asserts these with exit 4, so a moved checkout is the same death mode as a stale in-repo pin" \
                     || bad "(x13) an out-of-tree tutorial md5 pin does not equal the file it pins"

PINS_DECLARED=$(grep -cE '^MD5_[A-Z_0-9]+=[0-9a-f]{32}' "$DRVF")
PINS_DRIVEN=$((PINSEEN+TUTSEEN))
if [ "$PINS_DECLARED" = "$PINS_DRIVEN" ]; then
  ok "(x14) THE PIN LIST IS COMPLETE: the driver DECLARES $PINS_DECLARED MD5_* pins and (x12)+(x13) DROVE $PINS_DRIVEN of them.  SO-1c drove 4 of 12 under a label claiming all of them; this leg counts the declared side out of the driver's own bytes, so a pin ADDED and not driven turns it RED"
else
  bad "(x14) PINS DECLARED=$PINS_DECLARED but PINS DRIVEN=$PINS_DRIVEN -- a pin was added to the driver and no leg drives it"
fi
# KNOWN POSITIVE: (x12) and (x14) must both be able to go red.
KPP="$(mktemp -d)"; CREATED+=("$KPP")
cp -a "$DRVF" "$KPP/drv.sh"
sed -i 's/^MD5_GRADER=[0-9a-f]\{32\}/MD5_GRADER=deadbeefdeadbeefdeadbeefdeadbeef/' "$KPP/drv.sh"
KPIN=$(grep -oP '^MD5_GRADER=\K[0-9a-f]{32}' "$KPP/drv.sh" | head -1)
KACT=$(md5sum "$HERE/so3a_grade.py" | cut -d' ' -f1)
[ -n "$KPIN" ] && [ "$KPIN" != "$KACT" ] \
  && ok "(x12b) KNOWN POSITIVE: the pin comparison sees a planted stale MD5_GRADER (${KPIN:0:12}... != ${KACT:0:12}...) -- (x12)'s seven matches are readings of the files, not of the pattern" \
  || bad "(x12b) the pin comparison could not be made to fail"
printf 'MD5_NEWTHING=%s\n' "$KACT" >> "$KPP/drv.sh"
KPD2=$(grep -cE '^MD5_[A-Z_0-9]+=[0-9a-f]{32}' "$KPP/drv.sh")
[ "$KPD2" -eq "$((PINS_DECLARED+1))" ] \
  && ok "(x14b) KNOWN POSITIVE: an UNDRIVEN pin added to a planted copy moves the declared count $PINS_DECLARED -> $KPD2, so (x14) would go RED on exactly the SO-1c gap" \
  || bad "(x14b) the declared-pin count could not be made to move (read $KPD2)"
rm -rf "$KPP"

echo "SO3a G-ROOT5 SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
