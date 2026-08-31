#!/usr/bin/env bash
# SO-2M PIN AND NO-LAUNCH SELFTEST.
#
# TWO JOBS, and the first exists because of a MEASURED failure in this family:
# SO-1c's chain driver carries TWELVE md5 pins and its selftest leg drove FOUR
# while its message claimed "every pin".  So this file does NOT carry a list of
# pins to check.  It ENUMERATES every `MD5_*=` assignment out of the frozen
# driver's and launcher's OWN BYTES, maps each to its registered target through
# ONE table, and REFUSES if any enumerated pin has no registered target.  The
# count DRIVEN and the count that EXISTS are printed side by side and must be
# equal; a new pin added to either file with no target FAILS this selftest.
#
# The second job drives the FOUR NO-LAUNCH BRANCHES of PREREGISTRATION.md
# section 10 and shows each writing its NAMED file and exiting with its NAMED rc.
#
# SAFETY, AND THE ONE THING THIS FILE MUST NOT DO.  PREREGISTRATION.md section 2
# records this item's freeze condition as the ABSENCE of
#   /home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient
# and section 2 also records that this item has started NO CONTAINER.  Both
# statements must still be true when this selftest ends, so:
#   * NO leg starts a container.  The container-based G-ROOT.5 legs that SO-2a
#     drives (a sacrificial container, a sacrificial live pid inside a real run
#     root) are DELIBERATELY NOT DRIVEN HERE and their absence is REPORTED, not
#     hidden: driving them would create the run root and start a container, which
#     would falsify two sentences of a frozen document and is in any case the
#     SUPERVISOR's arming decision (SUPERVISION_CHARTER.md section 3 check 4),
#     not this lane's.
#   * The branches that need a run root are driven on a SANDBOX COPY of the
#     driver whose ONLY difference is the BASE line (and, for NL-1, the H5/AGG
#     constants so the bounded wait terminates in seconds instead of 14,400 s).
#     Every sandbox delta is PRINTED as a diff so nobody has to take it on trust.
#   * Everything this file creates is removed BY NAME, never by glob and never by
#     sweep, and a DECOY it did not create must SURVIVE that cleanup.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DRIVER="$HERE/so2m_chain_driver.sh"
LAUNCHER="$HERE/so2m_run_arm.sh"
REAL_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient
TMP="${1:-/tmp}/so2m_pin_selftest_$$"
PASS=0; FAIL=0
ok()  { echo "  [OK ] $1"; PASS=$((PASS+1)); }
bad() { echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
CREATED=()
mine() { CREATED+=("$1"); }

echo "SO2M PIN + NO-LAUNCH SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "  driver_md5=$(md5sum "$DRIVER" | cut -d' ' -f1) launcher_md5=$(md5sum "$LAUNCHER" | cut -d' ' -f1)"
CASE_BEFORE=$(ls -1a "$HERE" | sort | md5sum | cut -d' ' -f1)
DOCKER_PRE=$(sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -c '^so2m_')
mkdir -p "$TMP" || { bad "cannot create sandbox $TMP"; exit 2; }
mine "$TMP"

# =============================================================================
# (o0) THE FREEZE CONDITION, verified BESIDE A KNOWN POSITIVE (rule 3, L-400).
# A lister that cannot see an existing root proves nothing about an absent one.
# =============================================================================
if [ -e "$REAL_BASE" ]; then
  bad "(o0) the SO-2M run root EXISTS: $REAL_BASE -- refusing to run over a real root"
  exit 2
fi
KP=/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient
if [ -e "$KP" ]; then
  ok "(o0) SO-2M run root ABSENT and the SAME lister SEES SO-2a's existing root -- the absence is a reading of the disk, not of a broken test"
else
  bad "(o0) the known positive is missing; the absence reading is void"
fi

# =============================================================================
# (p1) THE PIN ENUMERATION.  Read out of the frozen files' own bytes.
# =============================================================================
target_of() {   # THE ONE registered table.  A pin with no entry here FAILS.
  case "$1" in
    MD5_LAUNCHER)       echo "$HERE/so2m_run_arm.sh" ;;
    MD5_GRADER)         echo "$HERE/so2m_grade.py" ;;
    MD5_RUNSCRIPT)      echo "$HERE/so2m_runScript.py" ;;
    MD5_XM)             echo "$HERE/so2m_xm.py" ;;
    MD5_DECOMP)         echo "$HERE/so2m_decomposeParDict" ;;
    MD5_TUT_RUNSCRIPT)  echo "/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/runScript.py" ;;
    MD5_TUT_GEN)        echo "/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/genAirFoilMesh.py" ;;
    MD5_TUT_PREPROC)    echo "/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/preProcessing.sh" ;;
    MD5_TUT_PS)         echo "/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/profiles/NACA0012PS.profile" ;;
    MD5_TUT_SS)         echo "/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/profiles/NACA0012SS.profile" ;;
    MD5_TUT_FFD)        echo "/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/FFD/wingFFD.xyz" ;;
    *)                  echo "" ;;
  esac
}
N_EXIST=0; N_DRIVEN=0; N_UNMAPPED=0; N_MISMATCH=0
for SRC in "$DRIVER" "$LAUNCHER"; do
  while IFS= read -r line; do
    VAR="${line%%=*}"; VAL="${line#*=}"; VAL="${VAL%% *}"
    N_EXIST=$((N_EXIST+1))
    TGT=$(target_of "$VAR")
    if [ -z "$TGT" ]; then
      bad "(p1) PIN $VAR in $(basename "$SRC") has NO REGISTERED TARGET -- a new pin nobody drives"
      N_UNMAPPED=$((N_UNMAPPED+1)); continue
    fi
    GOT=$(md5sum "$TGT" 2>/dev/null | cut -d' ' -f1)
    N_DRIVEN=$((N_DRIVEN+1))
    if [ "$GOT" != "$VAL" ]; then
      bad "(p1) PIN $VAR in $(basename "$SRC"): pinned $VAL but $TGT is $GOT"
      N_MISMATCH=$((N_MISMATCH+1))
    fi
  done < <(grep -E '^MD5_[A-Z_]+=' "$SRC")
done
echo "  [--] PIN CENSUS: pins that EXIST across the two frozen shell files = $N_EXIST ; pins DRIVEN = $N_DRIVEN ; unmapped = $N_UNMAPPED ; mismatched = $N_MISMATCH"
if [ "$N_EXIST" -eq "$N_DRIVEN" ] && [ "$N_UNMAPPED" -eq 0 ] && [ "$N_MISMATCH" -eq 0 ]; then
  ok "(p1) EVERY pin that exists was DRIVEN and every one matches -- the count driven ($N_DRIVEN) EQUALS the count that exists ($N_EXIST), so 'every pin' is a census and not a claim"
else
  bad "(p1) pin census failed: exist=$N_EXIST driven=$N_DRIVEN unmapped=$N_UNMAPPED mismatch=$N_MISMATCH"
fi

# (p2) PLANTED NEGATIVE: corrupt ONE pin in a COPY and require the same census to catch it.
CORRUPT="$TMP/corrupt_driver.sh"; mine "$CORRUPT"
sed 's/^MD5_XM=.*/MD5_XM=00000000000000000000000000000000/' "$DRIVER" > "$CORRUPT"
CVAL=$(grep -E '^MD5_XM=' "$CORRUPT" | cut -d= -f2)
CGOT=$(md5sum "$HERE/so2m_xm.py" | cut -d' ' -f1)
if [ "$CVAL" != "$CGOT" ]; then
  ok "(p2) PLANTED NEGATIVE: one corrupted pin in a COPY is caught by the same comparison ($CVAL != $CGOT) -- (p1)'s zero mismatches is a reading"
else bad "(p2) the corrupted pin was not detected"; fi

# (p3) PLANTED NEGATIVE: an UNMAPPED pin must be caught by the table, not waved through.
if [ -z "$(target_of MD5_SOMETHING_NEW)" ]; then
  ok "(p3) PLANTED NEGATIVE: a pin name with no entry in the registered table resolves to NO TARGET, which (p1) counts as unmapped and FAILS on -- a new unpinned pin cannot appear silently"
else bad "(p3) an unregistered pin name resolved to a target"; fi

# =============================================================================
# NL-4 FREEZE (rc=5) -- driven on a sandbox copy of the whole case directory.
# =============================================================================
SB="$TMP/nl4"; mine "$SB"
mkdir -p "$SB"
cp -a "$HERE"/so2m_*.sh "$HERE"/so2m_*.py "$HERE"/so2m_decomposeParDict "$SB/" 2>/dev/null
printf '\n# planted drift\n' >> "$SB/so2m_grade.py"
out=$(bash "$SB/so2m_chain_driver.sh" MESH 2>&1); rc=$?
if [ "$rc" -eq 5 ] && [ -f "$SB/NOLAUNCH_FREEZE.txt" ] && echo "$out" | grep -q 'SO2M_NOLAUNCH FREEZE rc=5'; then
  ok "(nl4) NL-4 FREEZE: a drifted grader md5 -> rc=5, NOLAUNCH_FREEZE.txt written, verdict BLOCKED, nothing staged, no container"
else bad "(nl4) rc=$rc file=$([ -f "$SB/NOLAUNCH_FREEZE.txt" ] && echo present || echo absent): $(echo "$out" | tail -2)"; fi
grep -q 'verdict=BLOCKED rc=5 core_min=0.00' "$SB/NOLAUNCH_FREEZE.txt" 2>/dev/null \
  && ok "(nl4b) the NL-4 file states verdict=BLOCKED, its rc, and core_min=0.00 -- a no-launch branch costs nothing and says so" \
  || bad "(nl4b) NL-4 file does not carry the registered verdict/rc/cost line"

# =============================================================================
# NL-2 PRODUCER (rc=4) -- an unregistered edit to the producer.
# =============================================================================
SB2="$TMP/nl2"; mine "$SB2"
mkdir -p "$SB2"
cp -a "$HERE"/so2m_*.sh "$HERE"/so2m_*.py "$HERE"/so2m_decomposeParDict "$SB2/" 2>/dev/null
printf '\n# an edit the registration does not name\n' >> "$SB2/so2m_runScript.py"
sed -i "s/^MD5_RUNSCRIPT=.*/MD5_RUNSCRIPT=$(md5sum "$SB2/so2m_runScript.py" | cut -d' ' -f1)/" "$SB2/so2m_chain_driver.sh"
out=$(bash "$SB2/so2m_chain_driver.sh" MESH 2>&1); rc=$?
if [ "$rc" -eq 4 ] && [ -f "$SB2/NOLAUNCH_PRODUCER.txt" ]; then
  ok "(nl2) NL-2 PRODUCER: an ELEVENTH added line the registration does not name -> rc=4 even though its md5 pin was updated to match, because the DIFF against the tutorial is COMPUTED and not asserted"
else bad "(nl2) rc=$rc file=$([ -f "$SB2/NOLAUNCH_PRODUCER.txt" ] && echo present || echo absent): $(echo "$out" | tail -2)"; fi
grep -q 'offending_hunks' "$SB2/NOLAUNCH_PRODUCER.txt" 2>/dev/null \
  && ok "(nl2b) NOLAUNCH_PRODUCER.txt carries the OFFENDING HUNKS, as section 10 registers -- the refusal says what it saw" \
  || bad "(nl2b) NL-2 file carries no offending hunks"
# and the DRIVEN CONTROL in the other direction: the REAL producer PASSES NL-2.
SB2b="$TMP/nl2b"; mine "$SB2b"
mkdir -p "$SB2b"
cp -a "$HERE"/so2m_*.sh "$HERE"/so2m_*.py "$HERE"/so2m_decomposeParDict "$SB2b/" 2>/dev/null
sed -i "s|^BASE=.*|BASE=$TMP/nl2b_root|" "$SB2b/so2m_chain_driver.sh"
# THIS LEG MUST REACH NL-2 AND THEN STOP BEFORE ANYTHING IS STAGED OR LAUNCHED.
# It previously invoked the driver with NO ARM, which aborts at the usage test
# (rc=64) BEFORE NL-2 runs -- so the one leg whose whole job was to show the REAL
# producer PASSING never reached the check, and the ordering defect that refused
# that producer with rc=4 sat behind a leg that could not see it.  A leg that
# cannot reach its subject does not merely miss a break, it CONCEALS one.
# The arm is now passed, and the root is PRE-CREATED so NL-3 refuses with rc=3
# immediately AFTER NL-2 has printed its verdict: the producer check is exercised
# and the chain still stages nothing and starts NO container.
mkdir -p "$TMP/nl2b_root"; mine "$TMP/nl2b_root"
out=$(bash "$SB2b/so2m_chain_driver.sh" MESH 2>&1); rc=$?
if echo "$out" | grep -q 'SO2M_PRODUCER_OK'; then
  ok "(nl2c) DRIVEN CONTROL: the REAL producer PASSES NL-2 -- its ten added lines ARE exactly the registered insertions and it removes nothing, so (nl2)'s refusal is a reading of the diff"
else bad "(nl2c) the real producer did not pass NL-2: $(echo "$out" | tail -3)"; fi

# =============================================================================
# NL-3 ROOT (rc=3) -- driven on a sandbox copy whose ONLY delta is the BASE line.
# =============================================================================
SB3="$TMP/nl3"; mine "$SB3"
mkdir -p "$SB3"
cp -a "$HERE"/so2m_*.sh "$HERE"/so2m_*.py "$HERE"/so2m_decomposeParDict "$SB3/" 2>/dev/null
FAKE_ROOT="$TMP/nl3_root"; mkdir -p "$FAKE_ROOT"; mine "$FAKE_ROOT"
sed -i "s|^BASE=.*|BASE=$FAKE_ROOT|" "$SB3/so2m_chain_driver.sh"
echo "  [--] NL-3 SANDBOX DELTA (the only difference from the frozen driver):"
diff "$HERE/so2m_chain_driver.sh" "$SB3/so2m_chain_driver.sh" | sed 's/^/       /'
NDELTA=$(diff "$HERE/so2m_chain_driver.sh" "$SB3/so2m_chain_driver.sh" | grep -c '^[<>]')
if [ "$NDELTA" -eq 2 ]; then
  ok "(nl3a) the sandbox driver differs from the frozen one by EXACTLY the BASE line (2 diff lines) -- printed above, not taken on trust"
else bad "(nl3a) the sandbox driver differs by $NDELTA lines, not 2"; fi
out=$(bash "$SB3/so2m_chain_driver.sh" MESH 2>&1); rc=$?
if [ "$rc" -eq 3 ] && [ -f "$SB3/NOLAUNCH_ROOT.txt" ] && echo "$out" | grep -q 'SO2M_NOLAUNCH ROOT rc=3'; then
  ok "(nl3) NL-3 ROOT: a run root that ALREADY EXISTS at driver start -> rc=3, NOLAUNCH_ROOT.txt written, verdict BLOCKED, and the existing root is INSPECTED, never deleted"
else bad "(nl3) rc=$rc file=$([ -f "$SB3/NOLAUNCH_ROOT.txt" ] && echo present || echo absent): $(echo "$out" | tail -2)"; fi
if [ -d "$FAKE_ROOT" ]; then
  ok "(nl3b) the pre-existing root SURVIVED the refusal byte-intact -- NL-3 protects a root, it does not clear one"
else bad "(nl3b) NL-3 destroyed the root it was refusing over"; fi

# =============================================================================
# NL-1 AGGREGATE (rc=6) -- the BOUNDED WAIT that TERMINATES WITH A NON-ZERO rc.
# Sandbox deltas: BASE, and the bound/ceiling so the wait expires in seconds.
# =============================================================================
SB1="$TMP/nl1"; mine "$SB1"
mkdir -p "$SB1"
cp -a "$HERE"/so2m_*.sh "$HERE"/so2m_*.py "$HERE"/so2m_decomposeParDict "$SB1/" 2>/dev/null
NL1_ROOT="$TMP/nl1_root"; mine "$NL1_ROOT"
sed -i "s|^BASE=.*|BASE=$NL1_ROOT|; s/^H5_FLOOR_GIB=.*/H5_FLOOR_GIB=8.0; H5_SAMPLES=2; H5_WINDOW_S=2; AGG_CEILING_GIB=0.0001/; s/^AGG_POLL_S=.*/AGG_POLL_S=1; AGG_BOUND_S=0/" "$SB1/so2m_chain_driver.sh"
T0=$(date -u +%s)
out=$(bash "$SB1/so2m_chain_driver.sh" MESH 2>&1); rc=$?
T1=$(date -u +%s); EL=$((T1-T0))
if [ "$rc" -eq 6 ] && [ -f "$SB1/NOLAUNCH_AGGREGATE.txt" ]; then
  ok "(nl1) NL-1 AGGREGATE: the bounded wait EXPIRED and TERMINATED WITH rc=6 in ${EL}s -- it did NOT block-and-continue and it did NOT return 0 on expiry (section 18.7)"
else bad "(nl1) rc=$rc (expected 6) file=$([ -f "$SB1/NOLAUNCH_AGGREGATE.txt" ] && echo present || echo absent) in ${EL}s: $(echo "$out" | tail -3)"; fi
if grep -q 'DISCARD ACCOUNTING' "$SB1/NOLAUNCH_AGGREGATE.txt" 2>/dev/null; then
  ok "(nl1b) NOLAUNCH_AGGREGATE.txt STATES THE FRACTION OF THE DECLARED PROGRAM the block discards, computed from the arms actually bought: $(grep -A1 'DISCARD ACCOUNTING' "$SB1/NOLAUNCH_AGGREGATE.txt" | tail -1 | cut -c1-120)"
else bad "(nl1b) the NL-1 file carries no discard accounting"; fi
if ! echo "$out" | grep -q 'SO2M_DRIVER arm=MESH image='; then
  ok "(nl1c) the driver NEVER reached the launcher after losing the wait -- a bounded wait that is lost stops the chain, it does not proceed"
else bad "(nl1c) the driver proceeded to the launcher after the wait expired"; fi

# =============================================================================
# G-ROW (rc=4) -- RULING 3, 2026-08-31.  THE ROW-DERIVATION SAFETY IS DRIVEN.
#
# WHY THIS EXISTS.  so2m_run_arm.sh derives the row TWICE from two independent
# sources: once from the IMAGE (its name is resolved to a DIGEST, the digest is
# checked against the registered one, and ROW falls out of that case), and once
# from the ARM NAME (-S/MESH -> SHIPPED, -P -> PATCHED).  G-ROW then requires the
# two to AGREE and refuses with rc=4 when they do not.  That cross-check is what
# makes the three shell-side row derivations in this item defensible -- but until
# this section it was ASSERTED AND NEVER DRIVEN.  This family lost a run on
# 2026-08-31 (SO-1c) to a row-derivation safety that was believed rather than
# exercised, so G-ROW is now shown REFUSING when the two sources disagree and
# PASSING when they agree.
#
# NO CONTAINER IS STARTED.  The refusing direction reaches rc=4 at G-ROW, which is
# upstream of every staging and launch line.  The agreeing direction runs on a
# second sandbox copy carrying a SENTINEL `exit 0` immediately after G-ROW's own
# pass line, so the launcher stops at the gate under test; both sandbox deltas are
# PRINTED and COUNTED below rather than taken on trust.
# =============================================================================
GROW_ROOT="$TMP/grow_root"; mine "$GROW_ROOT"
mkdir -p "$GROW_ROOT/base/system"; chmod 777 "$GROW_ROOT"
cp -a "$HERE/so2m_runScript.py" "$HERE/so2m_xm.py" "$GROW_ROOT/"
cp -a "$HERE/so2m_decomposeParDict" "$GROW_ROOT/base/system/decomposeParDict"
SBL="$TMP/grow_launcher.sh"; mine "$SBL"
sed "s|^REGISTERED_BASE=.*|REGISTERED_BASE=$GROW_ROOT|" "$LAUNCHER" > "$SBL"
echo "  [--] G-ROW SANDBOX DELTA (refusing direction; the only difference from the frozen launcher):"
diff "$LAUNCHER" "$SBL" | sed 's/^/       /'
GD=$(diff "$LAUNCHER" "$SBL" | grep -c '^[<>]')
if [ "$GD" -eq 2 ]; then
  ok "(gr0) the G-ROW sandbox launcher differs from the frozen one by EXACTLY the REGISTERED_BASE line (2 diff lines) -- printed above.  G-ROOT.1 refuses a BASE that is not the registered root, so a copy is the only way to reach G-ROW without creating the real run root"
else bad "(gr0) the G-ROW sandbox launcher differs by $GD lines, not 2"; fi

# (gr1) DISAGREEMENT, direction one: an arm registered SHIPPED handed the PATCHED image.
out=$(bash "$SBL" G-S dafoam-idwarp-rot:v1 2>&1); rc=$?
if [ "$rc" -eq 4 ] \
   && echo "$out" | grep -q 'ABORT G-ROW arm G-S is registered on the SHIPPED row; got ROW=PATCHED' \
   && ! echo "$out" | grep -q 'D4S_G_ROW_PASS'; then
  ok "(gr1) G-ROW REFUSES rc=4 when the two derivations DISAGREE: the IMAGE-DIGEST-derived row reads PATCHED (sha256:2927768a...) while the ARM-NAME-derived row reads SHIPPED for G-S.  Two sources, one comparison, and the refusal names both -- so the cross-check is reading two values, not one value against itself"
else bad "(gr1) rc=$rc (expected 4): $(echo "$out" | tail -2)"; fi

# (gr2) DISAGREEMENT, the MIRROR direction -- a gate that only refuses one way is half a gate.
out=$(bash "$SBL" G-P dafoam/opt-packages:latest 2>&1); rc=$?
if [ "$rc" -eq 4 ] \
   && echo "$out" | grep -q 'ABORT G-ROW arm G-P is registered on the PATCHED row; got ROW=SHIPPED'; then
  ok "(gr2) G-ROW REFUSES rc=4 in the MIRROR direction too: G-P handed the SHIPPED image.  The refusal is symmetric, so it is not a one-sided test that happens to catch one swap"
else bad "(gr2) rc=$rc (expected 4): $(echo "$out" | tail -2)"; fi

# (gr3) MESH is registered on SHIPPED by a REGISTERED DELTA (mesh generation does
# not touch IDWarp).  The arm-name derivation must carry that, not just the suffix.
out=$(bash "$SBL" MESH dafoam-idwarp-rot:v1 2>&1); rc=$?
if [ "$rc" -eq 4 ] && echo "$out" | grep -q 'ABORT G-ROW arm MESH is registered on the SHIPPED row; got ROW=PATCHED'; then
  ok "(gr3) G-ROW REFUSES rc=4 for MESH on the PATCHED image -- MESH carries no -S suffix, so this shows the arm-name derivation encodes the REGISTERED delta (MESH runs SHIPPED) and not merely a suffix test"
else bad "(gr3) rc=$rc (expected 4): $(echo "$out" | tail -2)"; fi

# (gr4)+(gr5) AGREEMENT.  Second sandbox: the BASE line plus a SENTINEL that stops
# the launcher at the gate under test, so the PASSING direction starts NO container.
SBL2="$TMP/grow_launcher_pass.sh"; mine "$SBL2"
sed -e "s|^REGISTERED_BASE=.*|REGISTERED_BASE=$GROW_ROOT|" \
    -e '/^echo "D4S_G_ROW_PASS row=\$ROW digest=\$GOT_DIGEST"$/a exit 0   # SELFTEST SENTINEL: stop AT the gate under test; nothing is staged and no container starts' \
    "$LAUNCHER" > "$SBL2"
echo "  [--] G-ROW SANDBOX DELTA (agreeing direction; BASE line + the sentinel):"
diff "$LAUNCHER" "$SBL2" | sed 's/^/       /'
GD2=$(diff "$LAUNCHER" "$SBL2" | grep -c '^[<>]')
if [ "$GD2" -eq 3 ]; then
  ok "(gr4) the agreeing-direction sandbox differs from the frozen launcher by EXACTLY 3 diff lines -- the REGISTERED_BASE line and ONE added sentinel -- both printed above.  The sentinel is what keeps a PASSING G-ROW from proceeding to stage and launch, which would be ARMING and is the SUPERVISOR's decision"
else bad "(gr4) the agreeing sandbox differs by $GD2 lines, not 3"; fi
out=$(bash "$SBL2" G-S dafoam/opt-packages:latest 2>&1); rc=$?
if [ "$rc" -eq 0 ] \
   && echo "$out" | grep -q 'D4S_G_ROW_PASS row=SHIPPED digest=sha256:9d45679d' \
   && ! echo "$out" | grep -q 'ABORT G-ROW'; then
  ok "(gr5) G-ROW PASSES when the two derivations AGREE: G-S on dafoam/opt-packages:latest prints D4S_G_ROW_PASS row=SHIPPED with the digest.  Taken with (gr1)-(gr3) this makes the refusal a READING of a disagreement rather than a gate that refuses everything"
else bad "(gr5) rc=$rc (expected 0 at the sentinel): $(echo "$out" | tail -3)"; fi
if [ ! -d "$GROW_ROOT/G-S" ] && [ ! -d "$GROW_ROOT/MESH" ] && [ -z "$(ls "$GROW_ROOT"/*.log 2>/dev/null)" ]; then
  ok "(gr6) NOTHING WAS STAGED AND NO ARM LOG EXISTS in the G-ROW sandbox root after all five drives -- every one of them stopped at or before G-ROW, upstream of staging and launch"
else bad "(gr6) the G-ROW sandbox root carries staged work: $(ls -1 "$GROW_ROOT" | tr '\n' ' ')"; fi

# =============================================================================
# WHAT IS NOT DRIVEN, STATED PLAINLY RATHER THAN OMITTED
# =============================================================================
echo "  [--] NOT DRIVEN, AND WHY: the container-based G-ROOT.5 legs SO-2a drives"
echo "       (so2a_groot5_selftest.sh legs (a), (b), (e)) need a SACRIFICIAL CONTAINER and"
echo "       a REAL run root.  PREREGISTRATION.md section 2 records that this item has"
echo "       started NO container and created NO run directory; driving those legs would"
echo "       falsify both sentences, and arming this item is the SUPERVISOR'S decision"
echo "       (SUPERVISION_CHARTER.md section 3 check 4), not this lane's.  They are OWED"
echo "       before launch and are reported here as NOT DRIVEN -- an unchecked condition,"
echo "       never a passing one."

# =============================================================================
# CLEANUP BY NAME, DRIVEN WITH A DECOY (W3-SELFTEST-DEF-1)
# =============================================================================
DECOY="$TMP/DECOY_not_written_by_this_selftest"
echo "a real file a peer might have written" > "$DECOY"
rm -rf "$TMP/nl1" "$TMP/nl2" "$TMP/nl2b" "$TMP/nl3" "$TMP/nl4" "$TMP/nl1_root" "$TMP/nl3_root" \
       "$TMP/nl2b_root" "$TMP/corrupt_driver.sh" "$TMP/grow_root" "$TMP/grow_launcher.sh" \
       "$TMP/grow_launcher_pass.sh"
if [ -f "$DECOY" ] && [ "$(head -c 6 "$DECOY")" = "a real" ]; then
  ok "(z1) DRIVEN: the named cleanup removed only paths this selftest recorded creating, and the DECOY it did not create SURVIVED byte-intact"
else bad "(z1) the decoy did not survive the cleanup"; fi
rm -f "$DECOY"; rmdir "$TMP" 2>/dev/null

CASE_AFTER=$(ls -1a "$HERE" | sort | md5sum | cut -d' ' -f1)
if [ "$CASE_BEFORE" = "$CASE_AFTER" ]; then
  ok "(z2) the CASE DIRECTORY listing is byte-identical before and after ($CASE_BEFORE) -- no NOLAUNCH file was written here and nothing was deleted here"
else bad "(z2) the case directory listing CHANGED: $CASE_BEFORE -> $CASE_AFTER"; fi
if [ ! -e "$REAL_BASE" ]; then
  ok "(z3) the SO-2M run root is STILL ABSENT: the freeze condition of PREREGISTRATION.md section 2 survives this selftest"
else bad "(z3) the SO-2M run root now EXISTS"; fi
DOCKER_POST=$(sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -c '^so2m_')
if [ "$DOCKER_POST" = "$DOCKER_PRE" ]; then
  ok "(z4) so2m_ container count is $DOCKER_POST before and after -- this item has still started NO container"
else bad "(z4) so2m_ container count moved $DOCKER_PRE -> $DOCKER_POST"; fi

echo "SO2M PIN + NO-LAUNCH SELFTEST pass=$PASS fail=$FAIL pins_exist=$N_EXIST pins_driven=$N_DRIVEN $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
