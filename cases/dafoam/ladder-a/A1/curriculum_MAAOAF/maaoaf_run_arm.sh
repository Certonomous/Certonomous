#!/usr/bin/env bash
# =============================================================================
# PERMISSION: NOT_FROZEN -- DRAFT.  NOT COMMITTED BY ITS AUTHOR.  NOT RUNNABLE
# UNTIL THE FREEZE PLACEHOLDERS ARE REPLACED (G-FREEZE.0 refuses, first
# executable statement).
#
# MAAOAF -- MA288 COMPRESSIBLE-PRIMAL INITIALISATION LADDER -- ARM LAUNCHER
#
# Runs ONE arm (R0|N1|N2|N3) of the ladder registered in
#   cases/dafoam/ladder-a/A1/curriculum_MAAOAF/PREREGISTRATION.md
#
# DERIVED FROM cases/dafoam/ladder-a/A5/curriculum_A5P2/a5p2_run_arm.sh,
# carrying its LA.0-LA.4 launch discipline verbatim in behaviour: the
# first-artifact witness, the forbidden decoy, refusal codes 88/89/90, the
# `launched: false reason=[...]` ledger token, the killed-and-READ-BACK
# refusal path, stderr never discarded, and the recorded pre-launch mtime
# capture compared by STRICT increase with no slack term.
#
# THREE THINGS ARE DIFFERENT HERE AND EACH IS A MEASURED HAZARD, NOT A STYLE
# CHOICE:
#
#  (1) THE WITNESS IS AMBIGUOUS ON ARM N2 UNLESS ITS OUTPUT IS DIVERTED.
#      Measured in this image on a scratch copy of the MA288 case:
#      potentialFoam prints `ExecutionTime = 45.66 s` and `End` BEFORE the
#      primal solver is ever invoked.  The registered witness `^ExecutionTime = `
#      would therefore fire on the INITIALISER, not the solver -- the same
#      class of false witness as `^Time = `.  N2's potentialFoam output is
#      REDIRECTED TO A FILE inside the container so that `docker logs` carries
#      solver output only, and LA.0c ASSERTS THAT REDIRECT IS PRESENT.
#
#  (2) THE 0/ RESET IS REMOVED FROM THE IN-CONTAINER PROGRAM.
#      MAAOA's shipped maaoa_cmd.sh runs `rm -rf 0 && cp -r 0.orig 0` at
#      container start.  That destroys the host-side age datum before the
#      solver runs and would make CLAUDE.md rule 4's age guard unreadable.
#      This runner stages 0/ FROM 0.orig ON THE HOST and touches the datum
#      last; the container program never resets 0/.
#
#  (3) THE AGE DATUM IS 0/T, NOT 0/U.
#      Measured: potentialFoam REWRITES 0/U (it wrote 0/U.gz on the probe) and
#      leaves 0/T and 0/p untouched.  A 0/U datum would therefore be strictly
#      later on N2 than on every other arm, and the age guard would not mean
#      the same thing across the ladder.  0/T is touched last at staging and
#      is written by nothing but the solver.
#
# AND ONE COLLISION THAT WOULD HAVE SILENTLY ABORTED TWO ARMS:
#      maaoa_runScript_comp.py carries a self-assert over the md5 of the
#      A1WR physics block, and `daOptions` is INSIDE that block.  Editing
#      daOptions in place raises AOAC_ABORT and the arm never starts.  Every
#      daOptions change this runner makes is therefore applied as an
#      ASSIGNMENT PLACED AFTER the block's closing marker and after the
#      self-assert, so the hashed bytes are untouched and the physics-
#      continuity claim survives.  The AOAC_PHYSICS_MD5_PASS line is read back
#      out of the log as proof.
# =============================================================================
set -uo pipefail

# ===========================================================================
# G-FREEZE.0 -- A DRAFT MUST NOT BE RUNNABLE BY ACCIDENT.
# Every constant PREREGISTRATION.md must fix is written as the unfrozen token
# plus an uppercase slot name.  This guard greps THIS FILE for that shape and
# refuses.  It ASSERTS ITS OWN TRIP COUNT: a grep that matches nothing and
# reports success is the planted zero this lab keeps paying for.
#
# INHERITED REPAIR (A5P2, supervisor, 2026-09-10).  The counting pattern must
# require a SUFFIX and the threshold must be >0.  A bare-token pattern with a
# >1 threshold counts this guard and its own prose and REFUSES A CORRECTLY
# FROZEN FILE -- an off-by-one that blocks only the frozen case, which trains
# a reader to bypass the guard.  Bare self-references are invisible to the
# suffixed pattern; one unfilled slot trips it.
#
# INHERITED REPAIR 2 (same supervisor, five minutes later).  The slot names
# are DESCRIBED here and NEVER WRITTEN LITERALLY.  The first version of this
# comment spelled them out, so the guard matched its own documentation and
# refused a frozen file (measured: 3).  The slots are: the run root, the
# image tag, the image id, the staged instrument's md5, and the cpuset map.
# This failure is invisible to reading and appears only on execution, which
# is why the guard is exercised in BOTH directions before freeze.
# ===========================================================================
UNFROZEN_TOKENS=$(grep -cE '__MAAOAF_UNFROZEN__[A-Z0-9_]+' "${BASH_SOURCE[0]}" || true)
if [ "${UNFROZEN_TOKENS:-0}" -gt 0 ]; then
  echo "ABORT G-FREEZE.0 this file still carries $UNFROZEN_TOKENS unfrozen placeholders."
  echo "  MAAOAF's registered root, image, image id, staged-instrument md5 and"
  echo "  cpuset map are fixed in"
  echo "  cases/dafoam/ladder-a/A1/curriculum_MAAOAF/PREREGISTRATION.md at its"
  echo "  freeze commit.  A launcher that ran on placeholders would produce a"
  echo "  row no pre-registration covers.  REFUSED."
  exit 3
fi

ITEM=MAAOAF
PREFIX=maaoaf

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (filled at the freeze commit).  The values the supervisor
# was handed, for reference, are in PREREGISTRATION.md -- not duplicated here,
# because a second copy is a second thing that can drift.
# ---------------------------------------------------------------------------
REGISTERED_BASE=/home/ubuntu/certonomous-runs/MAAOAF-ma288-init
IMG=dafoam-idwarp-rot:v1
IMG_ID_EXPECT=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
MD5_RUNSCRIPT_SRC_EXPECT=bd22df020be42fbd2eef14cbc25182f7
CPUSET_R0=8
CPUSET_N1=9
CPUSET_N2=10
CPUSET_N3=11
# NOTE, inherited from A5P2 and still true: a file CANNOT check its own md5 --
# writing the hash into the file changes the hash.  There is NO md5-of-this-
# runner slot.  This runner's md5 and the grader's are recorded in
# PREREGISTRATION.md at the freeze commit and verified by the SUPERVISOR
# against the committed blob (CLAUDE.md rule 2).  What this script CAN and
# does check is the md5 of the instrument it STAGES, a different file.

RANKS=1                  # PREREG 2: np = 1, as the sweep ran
MEM=3g                   # as the sweep ran (CHAIN_LEDGER.tsv mem column)
TMO=1800                 # s, in-container deadline: the per-arm wall cap
LAUNCH_BUDGET_S=600      # witness budget; strict minority of TMO, asserted
END_TIME=500             # PREREG 2: 500 iterations, every arm
# PREREG 5 reconciliation, stated because two caps could otherwise disagree:
# the ITEM cap is 60.0 core-min.  np = 1, so 15.0 core-min == 900 s wall, and
# 4 arms x 15.0 == 60.0 exactly.  CAP_COREMIN is the BINDING budget and the
# runaway guard kills on it; TMO=1800 s is the in-container backstop that
# fires only if the host-side guard is itself dead.  Worst arm is N2 at
# 11.50 + 0.76 (measured potentialFoam) = 12.26, so 15.0 carries 22 % headroom.
CAP_COREMIN=15.0

BASE="${BASE:-$REGISTERED_BASE}"
ARM="${1:-}"
case "$ARM" in
  R0|N1|N2|N3) : ;;
  *) echo "usage: $0 <R0|N1|N2|N3>"; exit 3 ;;
esac
eval "CPUSET=\$CPUSET_$ARM"

# ===========================================================================
# G-ROOT.1 -- the registered root, NORMALISED, and never another item's tree.
# ===========================================================================
BASE_REAL=$(readlink -f "$BASE" 2>/dev/null || echo "$BASE")
REG_REAL=$(readlink -f "$REGISTERED_BASE" 2>/dev/null || echo "$REGISTERED_BASE")
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE '$BASE_REAL' is not the registered root '$REG_REAL'."
  exit 6
fi
# G-ROOT.2 -- forbidden roots.  MAAOAF READS the graded MAAOA sweep and the
# A1WR mesh and must never write into either.
for FORBIDDEN in \
    /home/ubuntu/certonomous-runs/MAAOA \
    /home/ubuntu/certonomous-runs/A1WR ; do
  F_REAL=$(readlink -f "$FORBIDDEN" 2>/dev/null || echo "$FORBIDDEN")
  case "$BASE_REAL/" in
    "$F_REAL"/*) echo "ABORT G-ROOT.2 BASE is inside forbidden root $F_REAL"; exit 6 ;;
  esac
  [ "$BASE_REAL" = "$F_REAL" ] && { echo "ABORT G-ROOT.2 BASE IS forbidden root $F_REAL"; exit 6; }
done

# The MA288 case tree that PRODUCED tonight's graded failure is the staging
# source and is READ-ONLY to this item.  R0 is a reproduction control, so it
# must be staged from the bytes that failed, not rebuilt from a skeleton.
SRC_CASE=/home/ubuntu/certonomous-runs/MAAOA/MA288/case
SRC_RUNSCRIPT=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/fixed_lift_mach_sweep/maaoa_runScript_comp.py
[ -d "$SRC_CASE/0.orig" ]            || { echo "ABORT staging source missing: $SRC_CASE/0.orig"; exit 6; }
[ -f "$SRC_CASE/constant/polyMesh/points.gz" ] || { echo "ABORT staging source missing the mesh"; exit 6; }
[ -f "$SRC_RUNSCRIPT" ]              || { echo "ABORT registered instrument missing: $SRC_RUNSCRIPT"; exit 6; }

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
echo "MAAOAF_IMAGE arm=$ARM img=$IMG id=$GOT_DIGEST pinned_by=hash"

# ===========================================================================
# STAGING.  Copies OUT of the graded MA288 tree; that tree is never written.
# 0/ is built on the HOST from 0.orig (see header note 2).
# ===========================================================================
rm -rf "$WORK"; mkdir -p "$WORK"
cp -a "$SRC_CASE/0.orig"   "$WORK/0.orig"
cp -a "$SRC_CASE/constant" "$WORK/constant"
cp -a "$SRC_CASE/system"   "$WORK/system"
cp -a "$SRC_CASE/FFD"      "$WORK/FFD"
cp    "$SRC_RUNSCRIPT"     "$WORK/runScript.py"
rm -rf "$WORK/0"; cp -a "$WORK/0.orig" "$WORK/0"

# G-SRC-MD5 -- the PROVENANCE of the instrument, pinned BEFORE the arm's
# change is applied.  Pinning after the patch would pin the patch, not the
# thing the pre-registration names.
GOT_MD5_SRC=$(md5sum "$WORK/runScript.py" | awk '{print $1}')
if [ "$GOT_MD5_SRC" != "$MD5_RUNSCRIPT_SRC_EXPECT" ]; then
  echo "ABORT G-SRC-MD5 the staged runScript.py md5 is $GOT_MD5_SRC, not the"
  echo "  registered $MD5_RUNSCRIPT_SRC_EXPECT.  This arm would run an"
  echo "  instrument the pre-registration does not describe.  REFUSED."
  exit 8
fi
echo "MAAOAF_SRC_MD5 arm=$ARM runScript.py(pre-patch)=$GOT_MD5_SRC pinned=yes"

# ---------------------------------------------------------------------------
# BASELINE, identical on every arm and registered as such (PREREG 2):
#   endTime 4000 -> 500
#   writeInterval 4000 -> 500.  NOT COSMETIC: with writeControl timeStep and
#     writeInterval 4000, an endTime of 500 writes NO fields at all, there is
#     no 500/ directory, and rule 4's age guard would have nothing to read.
#   printInterval -> 1, appended AFTER the hashed physics block (header note).
# ---------------------------------------------------------------------------
sed -i "s/^endTime .*/endTime         $END_TIME;/"             "$WORK/system/controlDict"
sed -i "s/^writeInterval .*/writeInterval   $END_TIME;/"       "$WORK/system/controlDict"

# THE ANCHOR IS A LITERAL STRING AND IS MATCHED LITERALLY -- grep -F and
# awk's index(), never a regexp.  MEASURED, 2026-09-11, twice, in dry test:
# the anchor text contains '(' , so as a regexp it is an unmatched group.
# `awk -v anc='^print\("AOAC...'` STRIPS the backslash in the -v assignment
# ("escape sequence \( treated as plain (") and then FATALS on the dynamic
# regexp, and `awk ... && mv` short-circuits, so the append SILENTLY NO-OPS
# and the arm stages as an unpatched duplicate of R0.  G-DEADLEVER below does
# catch it -- but a guard catching a bug this file could simply not have is
# not a reason to keep the bug.  No regexp can serve both grep -E and awk -v
# here; a literal serves both.
PATCH_ANCHOR_LIT='print("AOAC_PHYSICS_MD5_PASS'
grep -qF "$PATCH_ANCHOR_LIT" "$WORK/runScript.py" || {
  echo "ABORT the daOptions patch anchor is not in the staged instrument; the"
  echo "  append-after-the-hashed-block strategy cannot be applied safely."
  exit 8; }
append_daoption() {     # $1 = a single python line, inserted after the anchor
  # index($0,anc)==1 gives the '^' semantics without a regexp.
  awk -v ins="$1" -v anc="$PATCH_ANCHOR_LIT" '
    { print }
    !done && index($0, anc) == 1 { print ""; print ins; done=1 }
  ' "$WORK/runScript.py" > "$WORK/runScript.py.new" \
    && mv "$WORK/runScript.py.new" "$WORK/runScript.py" \
    || { echo "ABORT append_daoption failed to rewrite the staged instrument."; exit 8; }
}
append_daoption 'daOptions["printInterval"] = 1  # MAAOAF baseline: the grader REFUSES a sampled Bounding census'

apply_one_change() {
  case "$ARM" in
    R0) echo "none -- R0 IS the reproduction control (PREREG 2)" ;;
    N1) append_daoption 'daOptions["primalVarBounds"] = {"pMax": 1e9, "pMin": 1e2, "UMax": 1e5, "UMin": -1e5, "eMax": 1e9, "eMin": -1e9, "rhoMax": 1e3, "rhoMin": 1e-3}'
        echo "daOptions primalVarBounds widened off the DAFoam defaults" ;;
    N2) echo "potentialFoam -writePhi runs before the primal (applied in the container program)" ;;
    N3) sed -i 's|^\( *div(phi,U) *\)bounded Gauss linearUpwindV grad(U);|\1bounded Gauss upwind;|' \
            "$WORK/system/fvSchemes"
        echo "fvSchemes div(phi,U) linearUpwindV grad(U) -> upwind" ;;
  esac
}
CHANGE=$(apply_one_change)

# ---------------------------------------------------------------------------
# G-DEADLEVER -- Case Protocol: every setting the registration CLAIMS is
# present in the file the solver reads.  A sed or an awk that matched nothing
# is a SILENT no-op that would produce a duplicate of R0 under another arm's
# name.  THE ARM'S OWN CHANGE IS READ BACK OUT OF THE STAGED FILES.
# ---------------------------------------------------------------------------
RS="$WORK/runScript.py"; FVS="$WORK/system/fvSchemes"; CD="$WORK/system/controlDict"
assert_in()  { grep -qE "$2" "$1" || { echo "ABORT G-DEADLEVER arm=$ARM: expected /$2/ in $(basename "$1") and it is NOT there.  The change did not apply."; exit 8; }; }
assert_out() { grep -qE "$2" "$1" && { echo "ABORT G-DEADLEVER arm=$ARM: /$2/ is STILL in $(basename "$1"); the change did not take."; exit 8; }; return 0; }

# baseline, every arm
assert_in "$CD" "^endTime +$END_TIME;"
assert_in "$CD" "^writeInterval +$END_TIME;"
assert_in "$RS" '^daOptions\["printInterval"\] = 1'
# the patch MUST sit after the hashed block, or the instrument self-aborts
python3 - "$RS" <<'PYEOF' || { echo "ABORT G-DEADLEVER a daOptions patch landed INSIDE the hashed physics block; the instrument would raise AOAC_ABORT and the arm would never start."; exit 8; }
import sys, re
src = open(sys.argv[1]).read()
end = src.index("# ---- A1WR_PHYSICS" "_END ----")
for m in re.finditer(r'^daOptions\[', src, re.M):
    if m.start() < end:
        sys.exit(1)
PYEOF

case "$ARM" in
  R0) assert_out "$RS"  '^daOptions\["primalVarBounds"\]'
      assert_in  "$FVS" 'div\(phi,U\) +bounded Gauss linearUpwindV grad\(U\);' ;;
  N1) assert_in  "$RS"  '^daOptions\["primalVarBounds"\] = \{"pMax": 1e9'
      assert_in  "$FVS" 'div\(phi,U\) +bounded Gauss linearUpwindV grad\(U\);' ;;
  N2) assert_out "$RS"  '^daOptions\["primalVarBounds"\]'
      assert_in  "$FVS" 'div\(phi,U\) +bounded Gauss linearUpwindV grad\(U\);'
      [ -f "$WORK/0/Phi" ] || [ -f "$WORK/0/Phi.gz" ] && { echo "ABORT G-DEADLEVER a 0/Phi already exists at staging; N2's initialisation would not be the thing under test."; exit 8; }
      : ;;
  N3) assert_in  "$FVS" 'div\(phi,U\) +bounded Gauss upwind;'
      assert_out "$FVS" 'div\(phi,U\) +bounded Gauss linearUpwindV'
      assert_out "$RS"  '^daOptions\["primalVarBounds"\]' ;;
esac
echo "MAAOAF_ONE_CHANGE arm=$ARM change=[$CHANGE] verified_in_staged_files=yes"

# THE AGE DATUM.  0/T is touched LAST at staging (header note 3: potentialFoam
# rewrites 0/U and would make N2's datum incomparable).  It dates the run
# allowed to produce the answer (CLAUDE.md rule 4) and anchors the mtime
# corroborator.
touch "$WORK/0/T"
AGE_DATUM=$(stat -c %Y "$WORK/0/T")

# ===========================================================================
# THE IN-CONTAINER PROGRAM.  No 0/ reset (header note 2).  N2's initialiser
# writes to a FILE, never to stdout (header note 1 / LA.0c).
# ===========================================================================
{
  echo 'set -o pipefail'
  echo "cd /mnt/$ARM"
  if [ "$ARM" = N2 ]; then
    echo "potentialFoam -writePhi > /mnt/$ARM/potentialFoam.log 2>&1; PF_RC=\$?"
    echo "echo \"MAAOAF_POTENTIALFOAM_RC: \$PF_RC\""
    echo "if [ \"\$PF_RC\" -ne 0 ]; then echo 'MAAOAF_INIT_FAILED potentialFoam did not succeed; the primal is NOT run and this arm is BLOCKED, not GATE FAIL.'; echo 'MAAOAF_SOLVER_RC: 91'; exit 91; fi"
  fi
  echo "mpirun --allow-run-as-root -np $RANKS python runScript.py -task trim 2>&1"
  echo "echo \"MAAOAF_SOLVER_RC: \$?\""
} > "$CMDFILE"

# LA.0c -- ASSERT N2's INITIALISER CANNOT BECOME THE LAUNCH WITNESS.
# Measured in this image: potentialFoam prints `ExecutionTime = 45.66 s` and
# `End` before the solver exists.  If its output ever reaches stdout, the
# registered witness fires on the initialiser and the launch assertion is a
# lie.  This is asserted, not trusted.
if [ "$ARM" = N2 ]; then
  grep -qE "^potentialFoam -writePhi > /mnt/$ARM/potentialFoam\.log 2>&1;" "$CMDFILE" || {
    echo "ABORT LA.0c N2's potentialFoam output is not redirected to a file."
    echo "  It prints 'ExecutionTime = ' before the solver runs and would"
    echo "  satisfy the registered launch witness with no solver started."
    exit 9; }
  # POST-COMPUTE REPAIR 2026-09-11 (supervisor).  The previous form was
  #     grep -qE '^potentialFoam .*[^>]$'
  # which tests "the LINE does not END in >" as a proxy for "no redirect".
  # That is false for every redirect followed by more shell, and the staged
  # line is exactly that:
  #     potentialFoam -writePhi > /mnt/N2/potentialFoam.log 2>&1; PF_RC=$?
  # It ends in `$?`, so the guard MATCHED A CORRECTLY REDIRECTED COMMAND and
  # ABORTED N2 -- the one arm predicted most likely to work never ran
  # (measured: exit 9, no container).  Same shape as A5P2's G-FREEZE.0
  # off-by-one: a guard whose only victim is the CORRECT case.
  # The test is now what it always meant: a potentialFoam invocation with NO
  # redirect operator ANYWHERE on its line.
  if grep -E '^potentialFoam ' "$CMDFILE" | grep -qv '>'; then
    echo "ABORT LA.0c a potentialFoam invocation without a redirect is present."; exit 9; fi
  echo "MAAOAF_LA0C arm=N2 initialiser_output=redirected_to_file witness_unambiguous=yes"
fi

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

# LA.0b -- ASSERT THE DECOY IS NOT THE WITNESS.  A successor editing these two
# variables must not be able to quietly reintroduce the false witness.
# HONEST NOTE ON PROVENANCE, because a carried reason that no longer holds is
# worse than none: A5P2's decoy is decomposePar's `Time = 0`, printed 583
# lines before the solver's first step at np = 4.  MAAOAF runs np = 1 and
# NEVER decomposes, so THAT source of the decoy is absent here.  The guard is
# kept because the decoy is cheap and because this item has its OWN false
# witness -- N2's potentialFoam -- handled at LA.0c above.
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
# Disjoint from this family's solver codes (0, 1, 91 init-failed, 97 recorded-
# with-error, 124/137 timeout, 125 docker).  LIMIT, STATED: nothing prevents a
# future solver exiting 88/89/90 itself, which is why the LEDGER carries an
# explicit `launched: false reason=<r>` TOKEN and the grader reads the token.
# ===========================================================================
la_assert_launch() {    # $1 = cid  $2 = budget s  $3 = scratch dir
  local cid="$1" budget="$2" tmp="$3"
  local logf="$tmp/la.log" errf="$tmp/la.stderr" t0 el st
  # TWO COUNTERS, NOT ONE.  With one, a successful inspect resets the tally of
  # failed log reads every tick, so a permanently broken log reader never
  # reaches the retry threshold and is reported as wedged (89) instead of
  # unreadable (90) -- "I could not look" reported as "I looked and saw
  # nothing".  Each reader clears only its own count.
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
# solver started: pre-existing STAGED files satisfy it.  Any absolute-time
# comparison, and any slack term, has that hole.  Required form, implemented
# here: capture before the container starts; WRITE THE CAPTURE TO DISK so a
# later reader can see what was compared against; assert a STRICT increase.
# NO SLACK TERM EXISTS IN THIS FILE and none may be added.
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
# A zero-row capture would make the witness vacuous (every file would read as
# NEW), so the row count is ASSERTED non-zero.
# ===========================================================================
LAUNCH_PRE="$BASE/${ARM}_${STAMP}.launch_pre.tsv"
PRE_ROWS=$(la_capture_pre "$WORK" "$LAUNCH_PRE")
test "${PRE_ROWS:-0}" -gt 0 || {
  echo "ABORT LA.1b the before-launch capture of $WORK is EMPTY; the mtime"
  echo "  witness would call every file NEW and confirm a launch that never happened"
  exit 5; }
echo "MAAOAF_LAUNCH_PRECAPTURE arm=$ARM capture=$(basename "$LAUNCH_PRE") rows=$PRE_ROWS staging_anchor_epoch=$AGE_DATUM comparison=strict_increase slack=none"

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
     echo MAAOAF_CONTAINER_UID: \$(id -u) && \
     echo MAAOAF_DEADLINE_IN_CONTAINER_S: $TMO && \
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
echo "MAAOAF_CONTAINER_ID arm=$ARM name=$NAME cid=$CID launched_claim=NOT_YET_ASSERTED"

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
echo "MAAOAF_LAUNCH_MTIME_WITNESS arm=$ARM result=$LA_MTIME capture=$(basename "$LAUNCH_PRE") rows=$PRE_ROWS gating=no evidence=[$(printf '%s' "${LA_MTIME_EVIDENCE:-none}" | tr '\n' ';' | head -c 300)]"
if [ "$LA_RC" -eq 0 ] && [ "$LA_MTIME" = "unchanged_since_capture" ]; then
  echo "MAAOAF_LAUNCH_CONTRADICTION arm=$ARM the log witness fired but NOT ONE FILE in $WORK is strictly newer than the recorded capture.  A grader must treat this row as suspect." \
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
    echo "MAAOAF_LAUNCH_REFUSED arm=$ARM rc=$LA_RC -- THE SOLVER'S FIRST ARTIFACT NEVER APPEARED.  This row is NOT A RESULT and no grading may read it."
    echo "MAAOAF_LAUNCH_READER_STDERR arm=$ARM: $(tr '\n' ' ' < "$LA_TMP/la.stderr" | head -c 600)"
  } | tee -a "$BASE/ledger.txt"
  sudo -n docker rm "$CID" >/dev/null 2>&1
  rm -f "$PIDFILE"
  exit "$LA_RC"
fi
echo "MAAOAF_LAUNCH_ASSERTED arm=$ARM launched: true reason=[$LA_REASON] waited_s=$LA_WAITED_S budget_s=$LAUNCH_BUDGET_S mtime_witness=$LA_MTIME precapture=$(basename "$LAUNCH_PRE") precapture_rows=$PRE_ROWS cid=$CID solver_call_seen=$LA_CORROBORATED" \
  | tee -a "$BASE/ledger.txt"

# ===========================================================================
# THE RUNAWAY GUARD.  T0 was set BEFORE the launch wait, so the launch wait --
# and, on N2, the 45.66 s initialiser -- are inside the graded wall and cannot
# be spent for free.
# ===========================================================================
while :; do
  ST=$(la_state "$CID" "$LA_TMP/la.stderr")
  [ "$ST" = "true" ] || break
  EL=$(( $(date -u +%s) - T0 ))
  COREMIN=$(python3 -c "print('%.3f' % ($EL*$RANKS/60.0))")
  OVER=$(python3 -c "print(1 if $COREMIN > $CAP_COREMIN else 0)")
  if [ "$OVER" = "1" ]; then
    KILLED=$(la_kill "$CID" "$LA_TMP/la.stderr")
    echo "MAAOAF_CAP_EXCEEDED arm=$ARM elapsed_s=$EL core_min=$COREMIN cap=$CAP_COREMIN container_kill=$KILLED -- an overrun STOPS the run; it does not get a new budget (CLAUDE.md rule 12).  This row is NOT A RESULT." \
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
SOLVER_RC=$(grep -a '^MAAOAF_SOLVER_RC: ' "$LOG" | tail -1 | awk '{print $2}')
sudo -n docker rm "$CID" >/dev/null 2>&1
sudo -n chown -R "$(id -u):$(id -g)" "$WORK" 2>>"$LA_TMP/la.stderr" || true

# G-PHYS READ-BACK.  The instrument's own md5 self-assert must have PASSED in
# the log.  Its absence means the physics block moved and the arm is not the
# physics the pre-registration names.
PHYS=$(grep -ac '^AOAC_PHYSICS_MD5_PASS ' "$LOG")
[ "${PHYS:-0}" -ge 1 ] || echo "MAAOAF_G_PHYS_ABSENT arm=$ARM the instrument's AOAC_PHYSICS_MD5_PASS line is NOT in the log -- treat this row as suspect."

# G-SAMPLE READ-BACK, pre-empting the grader's refusal so a wasted arm is
# named at once rather than at grading time.
PI=$(grep -aoE '^ *printInterval +[0-9]+;' "$LOG" | head -1 | grep -oE '[0-9]+')
[ "${PI:-0}" = "1" ] || echo "MAAOAF_G_SAMPLE_FAIL arm=$ARM the solver's own dict dump reads printInterval=${PI:-UNREAD}, not 1.  The Bounding census would be a SAMPLE and the grader will REFUSE this log."

# N2 READ-BACK: the initialiser actually ran and actually initialised.
if [ "$ARM" = N2 ]; then
  PFRC=$(grep -a '^MAAOAF_POTENTIALFOAM_RC: ' "$LOG" | tail -1 | awk '{print $2}')
  PFOK=$(grep -ac 'Calculating potential flow' "$WORK/potentialFoam.log" 2>/dev/null || echo 0)
  PHI=$( [ -f "$WORK/0/Phi" ] || [ -f "$WORK/0/Phi.gz" ] && echo present || echo ABSENT )
  echo "MAAOAF_N2_INIT arm=N2 potentialFoam_rc=${PFRC:-UNREAD} calculating_potential_flow_lines=$PFOK zero_Phi=$PHI"
  [ "$PHI" = present ] || echo "MAAOAF_N2_DEADLEVER arm=N2 no 0/Phi after the run -- the registered initialisation did NOT take and this arm is NOT N2."
fi

# THE AGE GUARD (CLAUDE.md rule 4): every field at endTime must be NEWER than
# the case's own staged 0/T, touched last at staging.
NEWER=$(find "$WORK" -path "*/$END_TIME/*" -type f -newermt "@$AGE_DATUM" | wc -l)
TOTAL=$(find "$WORK" -path "*/$END_TIME/*" -type f | wc -l)
echo "MAAOAF_AGE_GUARD arm=$ARM fields_at_${END_TIME}=$TOTAL newer_than_staging=$NEWER age_datum_epoch=$AGE_DATUM datum_file=0/T"

{
  echo "ARM=$ARM ITEM=$ITEM IMG=$IMG DIGEST=$GOT_DIGEST change=[$CHANGE] launched: true reason=[$LA_REASON] wall_s=$WALL core_min=$COREMIN cap_core_min=$CAP_COREMIN kernel_rc=$KRC oomkilled=$OOM solver_rc=${SOLVER_RC:-UNREAD} phys_md5_pass=${PHYS:-0} print_interval=${PI:-UNREAD} age_datum=$AGE_DATUM fields_at_${END_TIME}=$TOTAL newer_than_staging=$NEWER log=$(basename "$LOG") stamp=$STAMP"
} | tee -a "$BASE/ledger.txt"

echo ""
echo "MAAOAF arm $ARM finished.  GRADE IT WITH THE REGISTERED GRADER, WHICH IS"
echo "THE ONLY THING ENTITLED TO A VERDICT:"
echo "  python3 <repo>/cases/dafoam/ladder-a/A1/curriculum_MAAOAF/grade_maaoaf.py $LOG"
echo "  (it REFUSES any log whose dict dump is not printInterval 1, and it runs"
echo "   its planted control in BOTH directions before it will speak.)"

rm -f "$PIDFILE"
exit 0
