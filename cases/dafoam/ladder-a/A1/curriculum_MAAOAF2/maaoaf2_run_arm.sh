#!/usr/bin/env bash
# =============================================================================
# PERMISSION: NOT_FROZEN -- DRAFT.  NOT COMMITTED BY ITS AUTHOR.  NOT LAUNCHED
# BY ITS AUTHOR.  NOT RUNNABLE UNTIL THE FREEZE PLACEHOLDERS ARE REPLACED
# (G-FREEZE.0 refuses, first executable statement).
#
# MAAOAF2 -- MA288 potentialFoam-BASELINED SETTINGS LADDER -- ARM LAUNCHER
#
# Runs ONE arm (M1|M2|M3|M4) of the ladder registered in
#   cases/dafoam/ladder-a/A1/curriculum_MAAOAF2/PREREGISTRATION.md
#
# DERIVED FROM the REPAIRED (commit 266f34bfc) frozen launcher
#   cases/dafoam/ladder-a/A1/curriculum_MAAOAF/maaoaf_run_arm.sh
# and carrying its launch discipline verbatim in behaviour: the
# `^ExecutionTime = ` first-artifact witness with `^Time = ` the NAMED decoy,
# refusal codes 88/89/90, the `launched: false reason=[...]` ledger token, the
# killed-and-READ-BACK refusal path, NO `2>/dev/null` on ANY docker reader, the
# DISK-WRITTEN pre-launch mtime capture compared by STRICT increase with no
# slack term, the suffixed-token G-FREEZE.0 whose slot names are DESCRIBED and
# never written literally, `mpirun --allow-run-as-root`, printInterval 1, and
# daOptions patches appended AFTER the md5-hashed physics block, never inside.
#
# WHAT IS DIFFERENT HERE, AND EACH IS A MEASURED CONSEQUENCE OF MAAOAF:
#
#  (1) potentialFoam IS THE BASELINE ON EVERY ARM, NOT ONE ARM'S CHANGE.
#      MAAOAF measured it: clip onset moved from iteration 1 (R0/N1/N3) to
#      iteration 167 with ZERO clips through 100, and the arm cost LESS than
#      the control (9.100 vs 9.950 core-min).  Every hazard MAAOAF handled for
#      one arm therefore applies to all four here: the initialiser prints
#      `ExecutionTime = ` and `End` BEFORE the primal exists, so its output is
#      redirected to a file on EVERY arm and LA.0c asserts that on EVERY arm;
#      the age datum is 0/T on EVERY arm because potentialFoam rewrites 0/U;
#      and `no 0/Phi at staging` is a baseline assert, not an N2 assert.
#
#  (2) LA.0c CARRIES THE REPAIRED TEST, NOT THE ONE THAT SHIPPED.
#      MAAOAF's first form was `grep -qE '^potentialFoam .*[^>]$'` -- "the line
#      does not END in >" as a proxy for "no redirect".  The staged line ends
#      in `$?`, so the guard MATCHED A CORRECTLY REDIRECTED COMMAND and aborted
#      the one arm predicted most likely to work (measured: exit 9, no
#      container; ADDENDUM 1, 266f34bfc).  The test here is what it always
#      meant: a potentialFoam invocation carrying NO redirect operator ANYWHERE
#      on its line.
#
#  (3) THE CAP IS PER-ARM, BECAUSE ONE ARM COSTS MORE THAN THE OTHERS.
#      M2 solves the pressure equation three times per outer iteration instead
#      of once.  A single item-wide CAP_COREMIN would either kill M2 or buy the
#      other three a budget the pre-registration does not give them.
# =============================================================================
set -uo pipefail

# ===========================================================================
# G-FREEZE.0 -- A DRAFT MUST NOT BE RUNNABLE BY ACCIDENT.
# Every constant PREREGISTRATION.md must fix is written as the unfrozen token
# plus an uppercase slot name.  This guard greps THIS FILE for that shape and
# refuses.  The counting pattern REQUIRES A SUFFIX and the threshold is >0:
# a bare-token pattern with a >1 threshold counts this guard and its own prose
# and REFUSES A CORRECTLY FROZEN FILE -- an off-by-one whose only victim is the
# frozen case, which trains a reader to bypass the guard (A5P2, measured).
# THE SLOT NAMES ARE DESCRIBED HERE AND NEVER WRITTEN LITERALLY: MAAOAF's first
# version spelled them out, so the guard matched its own documentation and
# refused a frozen file (measured: 3).  The slots are: the run root, the image
# tag, the image id, the staged instrument's md5, and the cpuset map.
# Exercise this guard in BOTH directions before freeze -- it is invisible to
# reading and appears only on execution.
# ===========================================================================
UNFROZEN_TOKENS=$(grep -cE '__MAAOAF2_UNFROZEN__[A-Z0-9_]+' "${BASH_SOURCE[0]}" || true)
if [ "${UNFROZEN_TOKENS:-0}" -gt 0 ]; then
  echo "ABORT G-FREEZE.0 this file still carries $UNFROZEN_TOKENS unfrozen placeholders."
  echo "  MAAOAF2's registered root, image, image id, staged-instrument md5 and"
  echo "  cpuset map are fixed in"
  echo "  cases/dafoam/ladder-a/A1/curriculum_MAAOAF2/PREREGISTRATION.md at its"
  echo "  freeze commit.  A launcher that ran on placeholders would produce a"
  echo "  row no pre-registration covers.  REFUSED."
  exit 3
fi

ITEM=MAAOAF2
PREFIX=maaoaf2

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (filled at the freeze commit).  Not duplicated from
# PREREGISTRATION.md as prose -- a second copy is a second thing that can drift.
# ---------------------------------------------------------------------------
REGISTERED_BASE=/home/ubuntu/certonomous-runs/MAAOAF2-ma288-init
IMG=dafoam-idwarp-rot:v1TAG
IMG_ID_EXPECT=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
MD5_RUNSCRIPT_SRC_EXPECT=__MAAOAF2_UNFROZEN__SRCMD5
CPUSET_M1=__MAAOAF2_UNFROZEN__CPUSETM1
CPUSET_M2=__MAAOAF2_UNFROZEN__CPUSETM2
CPUSET_M3=__MAAOAF2_UNFROZEN__CPUSETM3
CPUSET_M4=__MAAOAF2_UNFROZEN__CPUSETM4
# A file CANNOT check its own md5 -- writing the hash into the file changes the
# hash.  There is NO md5-of-this-runner slot.  This runner's md5 and the
# grader's are recorded in PREREGISTRATION.md at the freeze commit and verified
# by the SUPERVISOR against the committed blob (CLAUDE.md rule 2).  What this
# script CAN and does check is the md5 of the instrument it STAGES.

RANKS=1                  # PREREG 2: np = 1, as MAAOAF and the sweep ran
MEM=3g
LAUNCH_BUDGET_S=600      # witness budget; strict minority of TMO, asserted below
END_TIME=500             # PREREG 2: 500 iterations, every arm

BASE="${BASE:-$REGISTERED_BASE}"
ARM="${1:-}"
case "$ARM" in
  M1|M2|M3|M4) : ;;
  *) echo "usage: $0 <M1|M2|M3|M4>"; exit 3 ;;
esac
eval "CPUSET=\$CPUSET_$ARM"

# PREREG 5 reconciliation, per-arm because the arms are not equal in cost.
# Measured anchor: MAAOAF N2 (this item's baseline, potentialFoam INCLUDED)
# 546 s = 9.100 core-min at np = 1.  M2 triples the pressure solves per outer
# iteration; its cap carries a x2.0 whole-arm allowance.  4 caps sum EXACTLY
# to the 68.0 core-min item cap: 26.0 + 14.0 + 14.0 + 14.0.
case "$ARM" in
  M2) CAP_COREMIN=26.0; TMO=2400 ;;
  *)  CAP_COREMIN=14.0; TMO=1800 ;;
esac

# ===========================================================================
# G-ROOT.1 -- the registered root, NORMALISED, and never another item's tree.
# ===========================================================================
BASE_REAL=$(readlink -f "$BASE" 2>/dev/null || echo "$BASE")
REG_REAL=$(readlink -f "$REGISTERED_BASE" 2>/dev/null || echo "$REGISTERED_BASE")
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE '$BASE_REAL' is not the registered root '$REG_REAL'."
  exit 6
fi
# G-ROOT.2 -- forbidden roots.  MAAOAF2 READS the graded MAAOA sweep, the A1WR
# mesh AND THE GRADED MAAOAF LADDER, and must never write into any of them.
for FORBIDDEN in \
    /home/ubuntu/certonomous-runs/MAAOA \
    /home/ubuntu/certonomous-runs/A1WR \
    /home/ubuntu/certonomous-runs/MAAOAF-ma288-init ; do
  F_REAL=$(readlink -f "$FORBIDDEN" 2>/dev/null || echo "$FORBIDDEN")
  case "$BASE_REAL/" in
    "$F_REAL"/*) echo "ABORT G-ROOT.2 BASE is inside forbidden root $F_REAL"; exit 6 ;;
  esac
  [ "$BASE_REAL" = "$F_REAL" ] && { echo "ABORT G-ROOT.2 BASE IS forbidden root $F_REAL"; exit 6; }
done

# The MA288 case tree that produced the graded failure is the staging source
# and is READ-ONLY to this item.
SRC_CASE=/home/ubuntu/certonomous-runs/MAAOA/MA288/case
SRC_RUNSCRIPT=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/fixed_lift_mach_sweep/maaoa_runScript_comp.py
[ -d "$SRC_CASE/0.orig" ]                      || { echo "ABORT staging source missing: $SRC_CASE/0.orig"; exit 6; }
[ -f "$SRC_CASE/constant/polyMesh/points.gz" ] || { echo "ABORT staging source missing the mesh"; exit 6; }
[ -f "$SRC_RUNSCRIPT" ]                        || { echo "ABORT registered instrument missing: $SRC_RUNSCRIPT"; exit 6; }

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
NAME="${PREFIX}_${ARM}_${STAMP}_$$"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"
CMDFILE="$WORK/${PREFIX}_cmd.sh"
mkdir -p "$BASE" || { echo "ABORT cannot create $BASE"; exit 6; }

# G-ROOT.5 -- refuse if this arm is already live.
PIDFILE="$BASE/.${PREFIX}_${ARM}.pid"
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
  echo "ABORT G-ROOT.5 arm $ARM already has a live driver (pid $(cat "$PIDFILE"))."
  exit 6
fi
echo $$ > "$PIDFILE"

# ===========================================================================
# G-IMG -- the image is pinned BY HASH.  The tag is not the identity.
# MAAOA ran the PATCHED build, not the stock one A5 uses; the pin is the only
# thing that keeps that true.  stderr is NOT discarded.
# ===========================================================================
IMGERR="$BASE/${ARM}_${STAMP}.imgerr"
GOT_DIGEST=$(sudo -n docker inspect --format '{{.Id}}' "$IMG" 2>"$IMGERR")
if [ -z "$GOT_DIGEST" ]; then
  echo "ABORT G-IMG could not resolve image '$IMG': $(head -c 400 "$IMGERR")"
  exit 7
fi
if [ "$GOT_DIGEST" != "$IMG_ID_EXPECT" ]; then
  echo "ABORT G-IMG '$IMG' resolves to $GOT_DIGEST, not the registered"
  echo "  $IMG_ID_EXPECT.  The tag moved; the pin did not."
  exit 7
fi
echo "MAAOAF2_IMAGE arm=$ARM img=$IMG id=$GOT_DIGEST pinned_by=hash"

# ===========================================================================
# STAGING.  Copies OUT of the graded MA288 tree; that tree is never written.
# 0/ is built on the HOST from 0.orig: the shipped maaoa_cmd.sh resets 0/ at
# container start, which would destroy the host-side age datum before the
# solver runs.  The container program here never resets 0/.
# ===========================================================================
rm -rf "$WORK"; mkdir -p "$WORK"
cp -a "$SRC_CASE/0.orig"   "$WORK/0.orig"
cp -a "$SRC_CASE/constant" "$WORK/constant"
cp -a "$SRC_CASE/system"   "$WORK/system"
cp -a "$SRC_CASE/FFD"      "$WORK/FFD"
cp    "$SRC_RUNSCRIPT"     "$WORK/runScript.py"
rm -rf "$WORK/0"; cp -a "$WORK/0.orig" "$WORK/0"

# G-SRC-MD5 -- the PROVENANCE of the instrument, pinned BEFORE the arm's change
# is applied.  Pinning after the patch would pin the patch.
GOT_MD5_SRC=$(md5sum "$WORK/runScript.py" | awk '{print $1}')
if [ "$GOT_MD5_SRC" != "$MD5_RUNSCRIPT_SRC_EXPECT" ]; then
  echo "ABORT G-SRC-MD5 the staged runScript.py md5 is $GOT_MD5_SRC, not the"
  echo "  registered $MD5_RUNSCRIPT_SRC_EXPECT.  This arm would run an"
  echo "  instrument the pre-registration does not describe.  REFUSED."
  exit 8
fi
echo "MAAOAF2_SRC_MD5 arm=$ARM runScript.py(pre-patch)=$GOT_MD5_SRC pinned=yes"

# ---------------------------------------------------------------------------
# BASELINE, identical on every arm and registered as such (PREREG 2):
#   endTime 4000 -> 500
#   writeInterval 4000 -> 500.  NOT COSMETIC: with writeControl timeStep and
#     writeInterval 4000, an endTime of 500 writes NO fields at all and rule
#     4's age guard would have nothing to read.
#   printInterval -> 1, appended AFTER the hashed physics block.
#   potentialFoam -writePhi before the primal -- applied in the container
#     program below, on EVERY arm.
# ---------------------------------------------------------------------------
sed -i "s/^endTime .*/endTime         $END_TIME;/"       "$WORK/system/controlDict"
sed -i "s/^writeInterval .*/writeInterval   $END_TIME;/" "$WORK/system/controlDict"

# THE ANCHOR IS A LITERAL STRING AND IS MATCHED LITERALLY -- grep -F and awk's
# index(), never a regexp.  MEASURED twice in MAAOAF dry test: the anchor text
# contains '(' , so as a regexp it is an unmatched group; `awk -v anc='...'`
# strips the backslash in the -v assignment and then FATALS on the dynamic
# regexp, and `awk ... && mv` short-circuits, so the append SILENTLY NO-OPS and
# the arm stages as an unpatched duplicate of the baseline.
PATCH_ANCHOR_LIT='print("AOAC_PHYSICS_MD5_PASS'
grep -qF "$PATCH_ANCHOR_LIT" "$WORK/runScript.py" || {
  echo "ABORT the daOptions patch anchor is not in the staged instrument; the"
  echo "  append-after-the-hashed-block strategy cannot be applied safely."
  exit 8; }
append_daoption() {     # $1 = a single python line, inserted after the anchor
  awk -v ins="$1" -v anc="$PATCH_ANCHOR_LIT" '
    { print }
    !done && index($0, anc) == 1 { print ""; print ins; done=1 }
  ' "$WORK/runScript.py" > "$WORK/runScript.py.new" \
    && mv "$WORK/runScript.py.new" "$WORK/runScript.py" \
    || { echo "ABORT append_daoption failed to rewrite the staged instrument."; exit 8; }
}
append_daoption 'daOptions["printInterval"] = 1  # MAAOAF2 baseline: the grader REFUSES a sampled Bounding census'

FVS="$WORK/system/fvSchemes"
FVSOL="$WORK/system/fvSolution"
RS="$WORK/runScript.py"
CD="$WORK/system/controlDict"

# G-COUNT -- PRE-EDIT MULTIPLICITY.  A sed whose pattern matches a DIFFERENT
# line than intended is not caught by a read-back of the intended line.  Both
# targets below are asserted to have exactly the multiplicity measured in the
# staged source before anything is edited.
N_NONORTH=$(grep -cE '^ *nNonOrthogonalCorrectors ' "$FVSOL")
[ "$N_NONORTH" = "2" ] || { echo "ABORT G-COUNT fvSolution has $N_NONORTH nNonOrthogonalCorrectors lines, not the measured 2 (SIMPLE 0, potentialFlow 20)."; exit 8; }
N_GRADDEF=$(grep -cE '^ *default +Gauss linear;' "$FVS")
[ "$N_GRADDEF" = "1" ] || { echo "ABORT G-COUNT fvSchemes has $N_GRADDEF 'default Gauss linear;' lines, not the measured 1 (gradSchemes only)."; exit 8; }

# NOTE: the M1 field-group pattern contains '|' , which is an alternation
# metacharacter in sed's BRE-with-| and a literal in the dict key.  It is
# therefore matched by a python rewrite on FIXED STRINGS, never by sed.
apply_one_change() {
  case "$ARM" in
    M1) python3 - "$FVSOL" <<'PYEOF' || { echo "ABORT M1 relaxation rewrite failed"; exit 8; }
import sys
p = sys.argv[1]; s = open(p).read()
a = '"(p|p_rgh|rho)"                     0.30;'
b = '"(U|T|e|h|nuTilda|k|epsilon|omega)" 0.70;'
if s.count(a) != 1 or s.count(b) != 1:
    sys.exit(1)
s = s.replace(a, '"(p|p_rgh|rho)"                     0.15;')
s = s.replace(b, '"(U|T|e|h|nuTilda|k|epsilon|omega)" 0.35;')
open(p, 'w').write(s)
PYEOF
        echo "relaxationFactors halved as ONE scalar damping factor lambda=0.5: fields 0.30->0.15, equations 0.70->0.35 (ratio alpha_U/alpha_p = 7/3 held FIXED)" ;;
    M2) sed -i 's|^\( *nNonOrthogonalCorrectors  *\)0;|\12;|' "$FVSOL"
        echo "fvSolution SIMPLE nNonOrthogonalCorrectors 0 -> 2 (potentialFlow's 20 untouched)" ;;
    M3) sed -i 's|^\( *default  *\)Gauss linear;|\1cellLimited Gauss linear 1;|' "$FVS"
        echo "fvSchemes gradSchemes default Gauss linear -> cellLimited Gauss linear 1" ;;
    M4) append_daoption 'daOptions["primalVarBounds"] = {"pMax": 121590.0, "pMin": 81060.0, "UMax": 300.0, "UMin": -300.0, "eMax": -1.2439e4, "eMin": -1.2014e5, "rhoMax": 1.70, "rhoMin": 0.70}'
        echo "daOptions primalVarBounds TIGHTENED to the physical range: T in [250,400] K, p within +/-20% of 101325, rho and U to match" ;;
  esac
}
CHANGE=$(apply_one_change)

# ---------------------------------------------------------------------------
# G-DEADLEVER -- Case Protocol: every setting the registration CLAIMS is
# present in the file the solver reads.  A sed or an awk that matched nothing
# is a SILENT no-op that would produce a duplicate of the baseline under
# another arm's name.  THE ARM'S OWN CHANGE IS READ BACK OUT OF THE STAGED
# FILES, and every OTHER arm's change is read back as ABSENT.
# ---------------------------------------------------------------------------
assert_in()  { grep -qE "$2" "$1" || { echo "ABORT G-DEADLEVER arm=$ARM: expected /$2/ in $(basename "$1") and it is NOT there.  The change did not apply."; exit 8; }; }
assert_out() { grep -qE "$2" "$1" && { echo "ABORT G-DEADLEVER arm=$ARM: /$2/ is STILL in $(basename "$1"); the change did not take or another arm's change leaked in."; exit 8; }; return 0; }

# baseline, every arm
assert_in "$CD" "^endTime +$END_TIME;"
assert_in "$CD" "^writeInterval +$END_TIME;"
assert_in "$RS" '^daOptions\["printInterval"\] = 1'
# the potentialFlow solver block N2 proved is wired and was never invoked
assert_in "$FVSOL" '^ *nNonOrthogonalCorrectors +20;'
assert_in "$FVSOL" '^ *Phi$'
# the patch MUST sit after the hashed block, or the instrument self-aborts
python3 - "$RS" <<'PYEOF' || { echo "ABORT G-DEADLEVER a daOptions patch landed INSIDE the hashed physics block; the instrument would raise AOAC_ABORT and the arm would never start."; exit 8; }
import sys, re
src = open(sys.argv[1]).read()
end = src.index("# ---- A1WR_PHYSICS" "_END ----")
for m in re.finditer(r'^daOptions\[', src, re.M):
    if m.start() < end:
        sys.exit(1)
PYEOF
# BASELINE: potentialFoam must be initialising, not re-reading a staged field.
if [ -f "$WORK/0/Phi" ] || [ -f "$WORK/0/Phi.gz" ]; then
  echo "ABORT G-DEADLEVER a 0/Phi already exists at staging; the registered"
  echo "  potentialFoam initialisation would not be the thing under test."
  exit 8
fi

case "$ARM" in
  M1) assert_in  "$FVSOL" '0\.15;'
      assert_in  "$FVSOL" '0\.35;'
      assert_out "$FVSOL" '0\.30;'
      assert_out "$FVSOL" '0\.70;'
      assert_out "$FVSOL" '^ *nNonOrthogonalCorrectors +2;'
      assert_in  "$FVS"   '^ *default +Gauss linear;'
      assert_out "$RS"    '^daOptions\["primalVarBounds"\]' ;;
  M2) assert_in  "$FVSOL" '^ *nNonOrthogonalCorrectors +2;'
      assert_out "$FVSOL" '^ *nNonOrthogonalCorrectors +0;'
      assert_in  "$FVSOL" '0\.30;'
      assert_in  "$FVS"   '^ *default +Gauss linear;'
      assert_out "$RS"    '^daOptions\["primalVarBounds"\]' ;;
  M3) assert_in  "$FVS"   '^ *default +cellLimited Gauss linear 1;'
      assert_out "$FVS"   '^ *default +Gauss linear;'
      assert_in  "$FVS"   '^ *default +Gauss linear corrected;'
      assert_in  "$FVSOL" '0\.30;'
      assert_out "$FVSOL" '^ *nNonOrthogonalCorrectors +2;'
      assert_out "$RS"    '^daOptions\["primalVarBounds"\]' ;;
  M4) assert_in  "$RS"    '^daOptions\["primalVarBounds"\] = \{"pMax": 121590\.0'
      assert_in  "$RS"    '"eMin": -1\.2014e5'
      assert_in  "$FVSOL" '0\.30;'
      assert_out "$FVSOL" '^ *nNonOrthogonalCorrectors +2;'
      assert_in  "$FVS"   '^ *default +Gauss linear;' ;;
esac
echo "MAAOAF2_ONE_CHANGE arm=$ARM change=[$CHANGE] verified_in_staged_files=yes baseline=potentialFoam"

# THE AGE DATUM.  0/T is touched LAST at staging: potentialFoam rewrites 0/U
# (measured, MAAOAF) and a 0/U datum would not date the solver's run.  0/T is
# written by nothing but the solver and dates the run allowed to produce the
# answer (CLAUDE.md rule 4).
touch "$WORK/0/T"
AGE_DATUM=$(stat -c %Y "$WORK/0/T")

# ===========================================================================
# THE IN-CONTAINER PROGRAM.  No 0/ reset.  The initialiser writes to a FILE,
# never to stdout -- it prints `ExecutionTime = ` and `End` BEFORE the primal
# exists and would otherwise BE the registered launch witness.
# ===========================================================================
{
  echo 'set -o pipefail'
  echo "cd /mnt/$ARM"
  echo "potentialFoam -writePhi > /mnt/$ARM/potentialFoam.log 2>&1; PF_RC=\$?"
  echo "echo \"MAAOAF2_POTENTIALFOAM_RC: \$PF_RC\""
  echo "if [ \"\$PF_RC\" -ne 0 ]; then echo 'MAAOAF2_INIT_FAILED potentialFoam did not succeed; the primal is NOT run and this arm is BLOCKED, not GATE FAIL.'; echo 'MAAOAF2_SOLVER_RC: 91'; exit 91; fi"
  echo "mpirun --allow-run-as-root -np $RANKS python runScript.py -task trim 2>&1"
  echo "echo \"MAAOAF2_SOLVER_RC: \$?\""
} > "$CMDFILE"

# LA.0c -- ASSERT THE INITIALISER CANNOT BECOME THE LAUNCH WITNESS.  EVERY ARM.
grep -qE "^potentialFoam -writePhi > /mnt/$ARM/potentialFoam\.log 2>&1;" "$CMDFILE" || {
  echo "ABORT LA.0c the potentialFoam output is not redirected to a file.  It"
  echo "  prints 'ExecutionTime = ' before the solver runs and would satisfy"
  echo "  the registered launch witness with no solver started."
  exit 9; }
# THE REPAIRED TEST (MAAOAF ADDENDUM 1, 266f34bfc).  The shipped form was
#     grep -qE '^potentialFoam .*[^>]$'
# -- "the LINE does not END in >" as a proxy for "no redirect".  The staged
# line ends in `$?`, so it MATCHED A CORRECTLY REDIRECTED COMMAND and aborted
# the arm at exit 9.  A guard whose only victim is the correct case.  The test
# below is what it always meant: a potentialFoam invocation with NO redirect
# operator ANYWHERE on its line.
if grep -E '^potentialFoam ' "$CMDFILE" | grep -qv '>'; then
  echo "ABORT LA.0c a potentialFoam invocation without a redirect is present."; exit 9; fi
echo "MAAOAF2_LA0C arm=$ARM initialiser_output=redirected_to_file witness_unambiguous=yes"

# ===========================================================================
# LA.1 -- READERS THAT PRESERVE STDERR.  THERE IS NO `2>/dev/null` ON ANY
# DOCKER READER IN THIS FILE.  "I could not look" is a THIRD return value and
# never collapses into "I looked and saw nothing".
# ===========================================================================
: "${DOCKER:=sudo -n docker}"
: "${LAUNCH_WITNESS_RE:=^ExecutionTime = }"      # LA.0, registered
: "${LAUNCH_WITNESS_FORBIDDEN_RE:=^Time = }"     # the registered decoy
: "${LAUNCH_CORROBORATOR_RE:=^Running Primal Solver}"
: "${LAUNCH_WITNESS_POLL_S:=5}"
: "${LAUNCH_READER_RETRIES:=6}"
: "${LAUNCH_KILL:=yes}"                          # L-540: a refusal KILLS

# LA.0b -- ASSERT THE DECOY IS NOT THE WITNESS.  np = 1 here and nothing
# decomposes, so A5P2's decoy source (decomposePar's `Time = 0`) is absent; the
# guard is kept because the decoy is cheap and because this item has its OWN
# false witness -- potentialFoam -- handled at LA.0c on every arm.
if [ "$LAUNCH_WITNESS_RE" = "$LAUNCH_WITNESS_FORBIDDEN_RE" ]; then
  echo "ABORT LA.0b the launch witness has been set to the FORBIDDEN decoy"
  echo "  '$LAUNCH_WITNESS_FORBIDDEN_RE'.  REFUSED."
  exit 9
fi
case "$LAUNCH_WITNESS_RE" in
  '^ExecutionTime = ') : ;;
  *) echo "ABORT LA.0b the launch witness is '$LAUNCH_WITNESS_RE', not the"
     echo "  registered '^ExecutionTime = '.  REFUSED."; exit 9 ;;
esac

la_state() {            # $1 = cid  $2 = stderr sink -> true | false | UNREADABLE
  local out rc
  out=$($DOCKER inspect --format '{{.State.Running}}' "$1" 2>>"$2"); rc=$?
  if [ "$rc" -ne 0 ]; then echo "UNREADABLE"; return 0; fi
  case "$out" in
    true|false) echo "$out" ;;
    *) printf 'la_state: inspect rc=0 but value was %q\n' "$out" >> "$2"
       echo "UNREADABLE" ;;
  esac
}

la_logs() {             # rc 0 = read.  rc != 0 = COULD NOT LOOK; dest holds the error.
  $DOCKER logs "$1" > "$2" 2>&1
}

# ===========================================================================
# LA.2 -- THE ASSERTION.
#   0  witness seen                           -> launched: true
#  88  container exited before any witness    -> never started
#  89  bounded wait elapsed, alive, no witness-> wedged
#  90  the witness reader itself failed       -> could not look
# Disjoint from this family's solver codes (0, 1, 91 init-failed, 97, 124/137
# timeout, 125 docker).  LIMIT, STATED: nothing prevents a future solver
# exiting 88/89/90 itself, which is why the LEDGER carries an explicit
# `launched: false reason=<r>` TOKEN and the grader reads the token.
# ===========================================================================
la_assert_launch() {    # $1 = cid  $2 = budget s  $3 = scratch dir
  local cid="$1" budget="$2" tmp="$3"
  local logf="$tmp/la.log" errf="$tmp/la.stderr" t0 el st
  # TWO COUNTERS, NOT ONE.  With one, a successful inspect resets the tally of
  # failed log reads every tick, so a permanently broken log reader never
  # reaches the retry threshold and is reported as wedged (89) instead of
  # unreadable (90).
  local unread_logs=0 unread_state=0
  : > "$errf"
  t0=$(date -u +%s)
  LA_REASON=""; LA_WITNESS_LINE=""; LA_WAITED_S=0
  LA_CORROBORATED=no; LA_DECOY_SEEN=no
  while :; do
    el=$(( $(date -u +%s) - t0 )); LA_WAITED_S=$el

    if la_logs "$cid" "$logf"; then
      unread_logs=0
      if grep -aqE "$LAUNCH_CORROBORATOR_RE" "$logf"; then LA_CORROBORATED=yes; fi
      if grep -aqE "$LAUNCH_WITNESS_FORBIDDEN_RE" "$logf"; then LA_DECOY_SEEN=yes; fi
      LA_WITNESS_LINE=$(grep -anE "$LAUNCH_WITNESS_RE" "$logf" | head -1)
      if [ -n "$LA_WITNESS_LINE" ]; then
        LA_REASON="witness=$LAUNCH_WITNESS_RE seen after ${el}s at log line ${LA_WITNESS_LINE%%:*}"
        return 0
      fi
    else
      unread_logs=$((unread_logs+1))
      printf 'la_logs failed (attempt %d): %s\n' "$unread_logs" \
             "$(head -c 400 "$logf" | tr '\n' ' ')" >> "$errf"
      if [ "$unread_logs" -ge "$LAUNCH_READER_RETRIES" ]; then
        LA_REASON="witness_reader_unreadable (docker logs) after $unread_logs consecutive failures: $(tail -1 "$errf" | head -c 300)"
        return 90
      fi
    fi

    st=$(la_state "$cid" "$errf")
    case "$st" in
      false)
        # ONE FINAL READ: the last poll may have raced the final flush.
        if la_logs "$cid" "$logf"; then
          LA_WITNESS_LINE=$(grep -anE "$LAUNCH_WITNESS_RE" "$logf" | head -1)
          if [ -n "$LA_WITNESS_LINE" ]; then
            LA_REASON="witness seen on the final read after ${el}s at log line ${LA_WITNESS_LINE%%:*}"
            return 0
          fi
        fi
        LA_REASON="never_started_container_exited after ${el}s with no ${LAUNCH_WITNESS_RE} line; decoy_seen=$LA_DECOY_SEEN solver_call_seen=$LA_CORROBORATED"
        return 88 ;;
      UNREADABLE)
        unread_state=$((unread_state+1))
        if [ "$unread_state" -ge "$LAUNCH_READER_RETRIES" ]; then
          LA_REASON="witness_reader_unreadable (docker inspect) after $unread_state consecutive failures: $(tail -1 "$errf" | head -c 300)"
          return 90
        fi ;;
      true) unread_state=0 ;;
    esac

    if [ "$el" -ge "$budget" ]; then
      LA_REASON="never_started_wedged: ${budget}s elapsed, container still Running, no ${LAUNCH_WITNESS_RE} line; decoy_seen=$LA_DECOY_SEEN solver_call_seen=$LA_CORROBORATED"
      return 89
    fi
    sleep "$LAUNCH_WITNESS_POLL_S"
  done
}

# ===========================================================================
# LA.1b -- THE mtime WITNESS: A STRICT INCREASE AGAINST A RECORDED CAPTURE.
# A witness of the form `mtime >= t_launch - slack` confirms a launch where no
# solver started: pre-existing STAGED files satisfy it.  Required form,
# implemented here: capture before the container starts; WRITE THE CAPTURE TO
# DISK so a later reader can see what was compared against; assert a STRICT
# increase.  NO SLACK TERM EXISTS IN THIS FILE and none may be added.
# ===========================================================================
la_capture_pre() {      # $1 = work dir, $2 = capture file.  echoes row count.
  : > "$2"
  find "$1" -type f -printf '%T@ %p\n' | sort > "$2"
  wc -l < "$2" | tr -d ' '
}

la_mtime_witness() {    # $1 = work dir, $2 = the capture
  LA_MTIME_EVIDENCE=$(find "$1" -type f -printf '%T@ %p\n' | sort | awk -v prefile="$2" '
    BEGIN { while ((getline l < prefile) > 0) { i=index(l," "); p=substr(l,i+1); pre[p]=substr(l,1,i-1)+0; seen[p]=1 } }
    { i=index($0," "); p=substr($0,i+1); m=substr($0,1,i-1)+0
      if (!(p in seen))    { print "NEW " p;                         n++ }
      else if (m > pre[p]) { print "ADVANCED " p " " pre[p] " -> " m; n++ } }
    END { exit (n > 0 ? 0 : 1) }')
  return $?
}

# ===========================================================================
# LA.2b -- THE REFUSAL PATH KILLS, AND READS THE KILL BACK (L-540).
# `timeout` around a docker CLIENT does not stop the CONTAINER.  A lane on this
# team leaked a container that ran 2,834 s against a 300 s timeout.  A kill
# that returns 0 and leaves the container Running is the same false zero as a
# reader that cannot see a non-zero.
# ===========================================================================
la_kill() {             # $1 = cid, $2 = stderr sink
  [ "$LAUNCH_KILL" = "yes" ] || { echo "not_attempted"; return 0; }
  if $DOCKER kill "$1" >/dev/null 2>>"$2"; then
    local st; st=$(la_state "$1" "$2")
    case "$st" in false) echo "killed" ;; *) echo "kill_failed(state_after=$st)" ;; esac
  else
    echo "kill_failed(client_error)"
  fi
}

# ===========================================================================
# LA.3 -- THE BEFORE-LAUNCH CAPTURE, then the launch, then the assertion.
# A zero-row capture would make the witness vacuous, so the row count is
# ASSERTED non-zero.
# ===========================================================================
LAUNCH_PRE="$BASE/${ARM}_${STAMP}.launch_pre.tsv"
PRE_ROWS=$(la_capture_pre "$WORK" "$LAUNCH_PRE")
test "${PRE_ROWS:-0}" -gt 0 || {
  echo "ABORT LA.1b the before-launch capture of $WORK is EMPTY; the mtime"
  echo "  witness would call every file NEW and confirm a launch that never happened"
  exit 5; }
echo "MAAOAF2_LAUNCH_PRECAPTURE arm=$ARM capture=$(basename "$LAUNCH_PRE") rows=$PRE_ROWS staging_anchor_epoch=$AGE_DATUM comparison=strict_increase slack=none"

python3 -c "
import sys
b, t = $LAUNCH_BUDGET_S, $TMO
if not (0 < b < 0.5*t):
    sys.stderr.write('ABORT LA budget %r is not a strict minority of deadline %r\n' % (b, t)); sys.exit(1)
" || { echo "ABORT LA.3 launch-witness budget vs deadline"; exit 65; }

# THE CONTAINER ID IS CAPTURED.  Names are reusable; ids are not.  Every reader
# below addresses the ID, never the name.
CIDFILE="$BASE/${ARM}_${STAMP}.cid"
RUNERR="$BASE/${ARM}_${STAMP}.runerr"
T0=$(date -u +%s)
CID=$(sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET \
    --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -e OMP_NUM_THREADS=1 -e MAAOA_U0=100.0 -e AOA_ALPHA0=4.0 \
    -e MAAOA_TRIM_JSON=/mnt/$ARM/trim.json \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo MAAOAF2_CONTAINER_UID: \$(id -u) && \
     echo MAAOAF2_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k 60 $TMO bash /mnt/$ARM/${PREFIX}_cmd.sh" 2> "$RUNERR") \
  || { echo "ABORT could not start container: $(head -c 400 "$RUNERR")"; exit 4; }
# THE RUN COMMAND RETURNING IS NOT A WITNESS.  It has bought exactly one thing:
# an id to address.  Everything else is asserted below.
case "$CID" in
  [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]*) : ;;
  *) echo "ABORT docker run returned something that is not a container id: '$CID'"
     exit 4 ;;
esac
echo "$CID" > "$CIDFILE"
echo "MAAOAF2_CONTAINER_ID arm=$ARM name=$NAME cid=$CID launched_claim=NOT_YET_ASSERTED"

LA_TMP="$BASE/.la_${ARM}_${STAMP}"; mkdir -p "$LA_TMP"
la_assert_launch "$CID" "$LAUNCH_BUDGET_S" "$LA_TMP"; LA_RC=$?

# THE mtime WITNESS, against the RECORDED capture.  CORROBORATING, NOT GATING:
# DAFoam writes fields at writeInterval, hundreds of steps after launch, so as
# a gate it would fire far too late.  The LOG witness gates.  It is recorded on
# every arm because `launched: true` with NOTHING written since the capture is
# a contradiction a grader must be able to see.
if la_mtime_witness "$WORK" "$LAUNCH_PRE"; then
  LA_MTIME=advanced
else
  LA_MTIME=unchanged_since_capture
fi
echo "MAAOAF2_LAUNCH_MTIME_WITNESS arm=$ARM result=$LA_MTIME capture=$(basename "$LAUNCH_PRE") rows=$PRE_ROWS gating=no evidence=[$(printf '%s' "${LA_MTIME_EVIDENCE:-none}" | tr '\n' ';' | head -c 300)]"
if [ "$LA_RC" -eq 0 ] && [ "$LA_MTIME" = "unchanged_since_capture" ]; then
  echo "MAAOAF2_LAUNCH_CONTRADICTION arm=$ARM the log witness fired but NOT ONE FILE in $WORK is strictly newer than the recorded capture.  A grader must treat this row as suspect." \
    | tee -a "$BASE/ledger.txt"
fi

# ===========================================================================
# LA.4 -- `launched: false` WITH A REASON.  Not a bare false, not an rc alone.
# ===========================================================================
if [ "$LA_RC" -ne 0 ]; then
  KILLED=$(la_kill "$CID" "$LA_TMP/la.stderr")
  sudo -n docker logs "$CID" > "$LOG" 2>&1
  EXITCODE=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$CID" 2>>"$LA_TMP/la.stderr")
  {
    echo "ARM=$ARM ITEM=$ITEM IMG=$IMG DIGEST=$GOT_DIGEST change=[$CHANGE] launched: false reason=[$LA_REASON] launch_rc=$LA_RC waited_s=$LA_WAITED_S budget_s=$LAUNCH_BUDGET_S mtime_witness=$LA_MTIME precapture=$(basename "$LAUNCH_PRE") precapture_rows=$PRE_ROWS cid=$CID container_kill=$KILLED inspect(exit,oomkilled)=[$EXITCODE] decoy_seen=$LA_DECOY_SEEN solver_call_seen=$LA_CORROBORATED log=$(basename "$LOG") stamp=$STAMP"
    echo "MAAOAF2_LAUNCH_REFUSED arm=$ARM rc=$LA_RC -- THE SOLVER'S FIRST ARTIFACT NEVER APPEARED.  This row is NOT A RESULT and no grading may read it."
    echo "MAAOAF2_LAUNCH_READER_STDERR arm=$ARM: $(tr '\n' ' ' < "$LA_TMP/la.stderr" | head -c 600)"
  } | tee -a "$BASE/ledger.txt"
  sudo -n docker rm "$CID" >/dev/null 2>&1
  rm -f "$PIDFILE"
  exit "$LA_RC"
fi
echo "MAAOAF2_LAUNCH_ASSERTED arm=$ARM launched: true reason=[$LA_REASON] waited_s=$LA_WAITED_S budget_s=$LAUNCH_BUDGET_S mtime_witness=$LA_MTIME precapture=$(basename "$LAUNCH_PRE") precapture_rows=$PRE_ROWS cid=$CID solver_call_seen=$LA_CORROBORATED" \
  | tee -a "$BASE/ledger.txt"

# ===========================================================================
# THE RUNAWAY GUARD.  T0 was set BEFORE the launch wait, so the launch wait --
# and the ~46 s initialiser, on every arm -- are inside the graded wall and
# cannot be spent for free.
# ===========================================================================
while :; do
  ST=$(la_state "$CID" "$LA_TMP/la.stderr")
  [ "$ST" = "true" ] || break
  EL=$(( $(date -u +%s) - T0 ))
  COREMIN=$(python3 -c "print('%.3f' % ($EL*$RANKS/60.0))")
  OVER=$(python3 -c "print(1 if $COREMIN > $CAP_COREMIN else 0)")
  if [ "$OVER" = "1" ]; then
    KILLED=$(la_kill "$CID" "$LA_TMP/la.stderr")
    echo "MAAOAF2_CAP_EXCEEDED arm=$ARM elapsed_s=$EL core_min=$COREMIN cap=$CAP_COREMIN container_kill=$KILLED -- an overrun STOPS the run; it does not get a new budget (CLAUDE.md rule 12).  This row is NOT A RESULT." \
      | tee -a "$BASE/ledger.txt"
    break
  fi
  sleep 10
done

WALL=$(( $(date -u +%s) - T0 ))
COREMIN=$(python3 -c "print('%.3f' % ($WALL*$RANKS/60.0))")
sudo -n docker logs "$CID" > "$LOG" 2>&1
KRC=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$CID" 2>>"$LA_TMP/la.stderr")
OOM=$(sudo -n docker inspect --format '{{.State.OOMKilled}}' "$CID" 2>>"$LA_TMP/la.stderr")
# rc is READ FROM THE PROCESS, never inferred from a marker.
SOLVER_RC=$(grep -a '^MAAOAF2_SOLVER_RC: ' "$LOG" | tail -1 | awk '{print $2}')
sudo -n docker rm "$CID" >/dev/null 2>&1
sudo -n chown -R "$(id -u):$(id -g)" "$WORK" 2>>"$LA_TMP/la.stderr" || true

# G-PHYS READ-BACK.  The instrument's own md5 self-assert must have PASSED in
# the log.  Its absence means the physics block moved.
PHYS=$(grep -ac '^AOAC_PHYSICS_MD5_PASS ' "$LOG")
[ "${PHYS:-0}" -ge 1 ] || echo "MAAOAF2_G_PHYS_ABSENT arm=$ARM the instrument's AOAC_PHYSICS_MD5_PASS line is NOT in the log -- treat this row as suspect."

# G-SAMPLE READ-BACK, pre-empting the grader's refusal so a wasted arm is named
# at once rather than at grading time.
PI=$(grep -aoE '^ *printInterval +[0-9]+;' "$LOG" | head -1 | grep -oE '[0-9]+')
[ "${PI:-0}" = "1" ] || echo "MAAOAF2_G_SAMPLE_FAIL arm=$ARM the solver's own dict dump reads printInterval=${PI:-UNREAD}, not 1.  The Bounding census would be a SAMPLE and the grader will REFUSE this log."

# BASELINE READ-BACK, EVERY ARM: the initialiser actually ran and initialised.
PFRC=$(grep -a '^MAAOAF2_POTENTIALFOAM_RC: ' "$LOG" | tail -1 | awk '{print $2}')
PFOK=0
[ -f "$WORK/potentialFoam.log" ] && PFOK=$(grep -ac 'Calculating potential flow' "$WORK/potentialFoam.log" || true)
if [ -f "$WORK/0/Phi" ] || [ -f "$WORK/0/Phi.gz" ]; then PHI=present; else PHI=ABSENT; fi
echo "MAAOAF2_BASELINE_INIT arm=$ARM potentialFoam_rc=${PFRC:-UNREAD} calculating_potential_flow_lines=$PFOK zero_Phi=$PHI"
[ "$PHI" = present ] || echo "MAAOAF2_BASELINE_DEADLEVER arm=$ARM no 0/Phi after the run -- the registered potentialFoam BASELINE did NOT take and this row is NOT the registered arm."

# THE AGE GUARD (CLAUDE.md rule 4): every field at endTime must be NEWER than
# the case's own staged 0/T, touched last at staging.
NEWER=$(find "$WORK" -path "*/$END_TIME/*" -type f -newermt "@$AGE_DATUM" | wc -l)
TOTAL=$(find "$WORK" -path "*/$END_TIME/*" -type f | wc -l)
echo "MAAOAF2_AGE_GUARD arm=$ARM fields_at_${END_TIME}=$TOTAL newer_than_staging=$NEWER age_datum_epoch=$AGE_DATUM datum_file=0/T"

{
  echo "ARM=$ARM ITEM=$ITEM IMG=$IMG DIGEST=$GOT_DIGEST change=[$CHANGE] launched: true reason=[$LA_REASON] wall_s=$WALL core_min=$COREMIN cap_core_min=$CAP_COREMIN kernel_rc=$KRC oomkilled=$OOM solver_rc=${SOLVER_RC:-UNREAD} phys_md5_pass=${PHYS:-0} print_interval=${PI:-UNREAD} potentialfoam_rc=${PFRC:-UNREAD} zero_Phi=$PHI age_datum=$AGE_DATUM fields_at_${END_TIME}=$TOTAL newer_than_staging=$NEWER log=$(basename "$LOG") stamp=$STAMP"
} | tee -a "$BASE/ledger.txt"

echo ""
echo "MAAOAF2 arm $ARM finished.  GRADE IT WITH THE REGISTERED GRADER, WHICH IS"
echo "THE ONLY THING ENTITLED TO A VERDICT:"
echo "  python3 <repo>/cases/dafoam/ladder-a/A1/curriculum_MAAOAF2/maaoaf2_grade.py $LOG"
echo "  (it REFUSES any log whose dict dump is not printInterval 1, it runs its"
echo "   planted control in BOTH directions on the verdict AND on"
echo "   first_clip_iteration, and it prints G-MATCH -- the onset and matched-"
echo "   iteration census the arms are ranked on.  NEVER rank on a total.)"

rm -f "$PIDFILE"
exit 0
