#!/usr/bin/env bash
# =============================================================================
# PERMISSION: NOT_FROZEN -- DRAFT.  NOT COMMITTED BY ITS AUTHOR.  NOT RUNNABLE
# UNTIL THE FREEZE PLACEHOLDERS ARE REPLACED (G-FREEZE.0 refuses, first
# executable statement).
#
# A5P -- U-BEND PRIMAL PLATEAU-BREAKING LADDER -- ARM LAUNCHER
#
# Runs ONE arm (P0|P1|P2|P3|P4) of the ladder frozen in
#   cases/dafoam/ladder-a/A5/curriculum_A5P/PREREGISTRATION.md
#
# DERIVED FROM cases/dafoam/ladder-a/A6/curriculum_D8G/d8g_run_arm.sh.DRAFT,
# carrying its LA.0-LA.4 launch discipline verbatim in behaviour.  That
# discipline exists because of three measured failures:
#
#  (1) cfd's scripts/case_protocol_stage4_run.py reported LAUNCHED on a Popen
#      return alone while the solver had already aborted.
#  (2) ALL 58 cases/dafoam/**/*_run_arm.sh launchers assert CONTAINER STATE
#      ONLY.  A container can report Running while the shell inside it is
#      still in decomposePar, or while python has raised and the shell is
#      winding down.
#  (3) THE OBVIOUS WITNESS IS A FALSE ONE.  `^Time = ` DOES NOT PROVE THE
#      SOLVER STARTED: measured on the D8R producer's graded arm log
#      /home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/O-P_20260827T223101Z_1595223.log
#      decomposePar prints `Time = 0` at line 142, 19 lines before its own
#      `End` and 583 lines before the solver's first completed step.  Over
#      that file `^Time = ` occurs 1617 times and `^ExecutionTime` 1616 -- the
#      difference is exactly decomposePar's line.
#
# THE REGISTERED LAUNCH WITNESS IS THEREFORE `^ExecutionTime = ` (LA.0).
# `^Time = ` is registered as the FORBIDDEN DECOY and is asserted to be so.
#
# A5P-SPECIFIC NOTE.  A5's primal is 3.3-31 s of solver time on 4,800 cells,
# so the launch wait is a LARGE fraction of the run.  T0 is set BEFORE the
# launch wait (inherited from D8G LA.3) so that wait is inside the graded wall
# and cannot be spent for free.
# =============================================================================
set -uo pipefail

# ===========================================================================
# G-FREEZE.0 -- A DRAFT MUST NOT BE RUNNABLE BY ACCIDENT.
# Every constant PREREGISTRATION.md must fix is written as __A5P_UNFROZEN__.
# This guard greps THIS FILE for that token and refuses.  It ASSERTS ITS OWN
# TRIP COUNT: a grep that matches nothing and reports success is the planted
# zero this lab keeps paying for.  The guard's own line contains the token, so
# the threshold is >1, exactly as in the D8G reference.
# ===========================================================================
UNFROZEN_TOKENS=$(grep -c '__A5P_UNFROZEN__' "${BASH_SOURCE[0]}" || true)
if [ "${UNFROZEN_TOKENS:-0}" -gt 1 ]; then
  echo "ABORT G-FREEZE.0 this file still carries $UNFROZEN_TOKENS unfrozen placeholders."
  echo "  A5P's registered root, image digest, cpuset and instrument md5s are"
  echo "  fixed in cases/dafoam/ladder-a/A5/curriculum_A5P/PREREGISTRATION.md at"
  echo "  its freeze commit.  A launcher that ran on placeholders would produce a"
  echo "  row no pre-registration covers.  REFUSED."
  exit 3
fi

ITEM=A5P
PREFIX=a5p

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (filled at the freeze commit)
# ---------------------------------------------------------------------------
REGISTERED_BASE=/home/ubuntu/certonomous-runs/A5P-ubend-plateau          # /home/ubuntu/certonomous-runs/A5P-ubend-plateau
IMG=dafoam/opt-packages:latest                       # dafoam/opt-packages:latest
IMG_ID_EXPECT=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc          # sha256:9d45679d...
CPUSET=12-15
# NOTE, and it is a correction to the D8G-shaped slot list: a file CANNOT
# check its own md5 -- writing the hash into the file changes the hash.  There
# is therefore NO md5-of-this-runner slot here.  This runner's md5 and the
# grader's are recorded in PREREGISTRATION.md at the freeze commit and are
# verified by the SUPERVISOR against the committed blob (CLAUDE.md rule 2),
# not by this script.  What this script CAN and DOES check is the md5 of the
# instrument it STAGES, which is a different file from itself.
MD5_RUNSCRIPT_EXPECT=06fb0ed4228d9927992a12a2fb68055c

RANKS=4                                       # PREREG 3.0 (decomposeParDict:18)
MEM=16g
TMO=900                                       # PREREG 7: in-container deadline
LAUNCH_BUDGET_S=180                           # PREREG 7: witness budget
END_TIME=5000                                 # PREREG 3.0
CAP_COREMIN=16.5                              # PREREG 6: 3 x the 5.5 estimate

BASE="${BASE:-$REGISTERED_BASE}"
ARM="${1:-}"
case "$ARM" in
  P0|P1|P2|P3|P4) : ;;
  *) echo "usage: $0 <P0|P1|P2|P3|P4>"; exit 3 ;;
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
# G-ROOT.2 -- forbidden roots.  A5P must never write into an item it reads.
for FORBIDDEN in \
    /home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5_work \
    /home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv \
    /home/ubuntu/certonomous-runs/A4-ahmed-body ; do
  F_REAL=$(readlink -f "$FORBIDDEN" 2>/dev/null || echo "$FORBIDDEN")
  case "$BASE_REAL/" in
    "$F_REAL"/*) echo "ABORT G-ROOT.2 BASE is inside forbidden root $F_REAL"; exit 6 ;;
  esac
done
# The LIVE A5 case tree is READ-ONLY to this item.  Staging copies out of it;
# nothing is ever written back into it.
LIVE_CASE=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss
[ -d "$LIVE_CASE" ] || { echo "ABORT the live A5 case tree is missing: $LIVE_CASE"; exit 6; }

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
NAME="${PREFIX}_${ARM}_${STAMP}_$$"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"
CMDFILE="$WORK/${PREFIX}_cmd.sh"
mkdir -p "$BASE" || { echo "ABORT cannot create $BASE"; exit 6; }

# G-ROOT.5 -- refuse if an arm of this item is already live.
PIDFILE="$BASE/.${PREFIX}_${ARM}.pid"
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
  echo "ABORT G-ROOT.5 arm $ARM already has a live driver (pid $(cat "$PIDFILE"))."
  exit 6
fi
echo $$ > "$PIDFILE"

# ===========================================================================
# G-IMG -- the image is pinned BY HASH.  The tag is not the identity
# (TOOLCHAIN_INVENTORY.md §11).  stderr is NOT discarded.
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
echo "A5P_IMAGE arm=$ARM img=$IMG id=$GOT_DIGEST pinned_by=hash"

# ===========================================================================
# STAGING.  Copies OUT of the live case; the live case is never written.
# Applies EXACTLY ONE numerical change per arm (PREREG 3.2-3.5), by rewriting
# the tightened fvSolution.  Every arm shares the same baseline (PREREG 3.0).
# ===========================================================================
rm -rf "$WORK"; mkdir -p "$WORK"
cp -a "$LIVE_CASE/0"        "$WORK/0"
cp -a "$LIVE_CASE/0.orig"   "$WORK/0.orig"
cp -a "$LIVE_CASE/constant" "$WORK/constant"
cp -a "$LIVE_CASE/system"   "$WORK/system"
cp -a "$LIVE_CASE/FFD"      "$WORK/FFD" 2>/dev/null || true
cp    "$LIVE_CASE/runScript.py" "$WORK/runScript.py"

# BASELINE: the tightened fvSolution becomes the live one (PREREG 3.0).
cp "$LIVE_CASE/system/fvSolution.tightened_2026-07-30" "$WORK/system/fvSolution"
rm -f "$WORK/system/fvSolution.tightened_2026-07-30"
# BASELINE: endTime 5000, uniform across all five arms.
sed -i "s/^endTime .*/endTime         $END_TIME;/" "$WORK/system/controlDict"

apply_one_change() {
  case "$ARM" in
    P0) echo "none -- P0 IS the baseline (PREREG 3.1)" ;;
    P1) sed -i 's/^\( *consistent  *\)false;/\1yes;/' "$WORK/system/fvSolution"
        echo "SIMPLE/consistent false -> yes (SIMPLEC)" ;;
    P2) sed -i '0,/^\( *nNonOrthogonalCorrectors  *\)0;/s//\12;/' "$WORK/system/fvSolution"
        echo "SIMPLE/nNonOrthogonalCorrectors 0 -> 2" ;;
    P3) sed -i 's/^\( *"(p|p_rgh)"  *\)0\.30;/\10.70;/' "$WORK/system/fvSolution"
        echo "relaxationFactors/fields (p|p_rgh) 0.30 -> 0.70" ;;
    P4) sed -i 's/^\( *\)"(U|T|e|h|nuTilda|k|epsilon|omega)" 0\.70;/\1"(U|T|e|h|k|epsilon|omega)" 0.70;\n\1nuTilda                        0.0;/' \
            "$WORK/system/fvSolution"
        echo "relaxationFactors/equations nuTilda 0.70 -> 0.0 (turbulence frozen, DIAGNOSTIC)" ;;
  esac
}
CHANGE=$(apply_one_change)

# ---------------------------------------------------------------------------
# G-DEADLEVER -- Case Protocol §2: every setting the registration CLAIMS is
# present in the file the solver reads.  A sed that matched nothing is a
# SILENT no-op that would produce a duplicate of P0 under another arm's name.
# THE ARM'S OWN CHANGE IS READ BACK OUT OF THE STAGED FILE.
# ---------------------------------------------------------------------------
FVS="$WORK/system/fvSolution"
assert_in()  { grep -qE "$1" "$FVS" || { echo "ABORT G-DEADLEVER arm=$ARM: expected /$1/ in the staged fvSolution and it is NOT there. The one change did not apply."; exit 8; }; }
assert_out() { grep -qE "$1" "$FVS" && { echo "ABORT G-DEADLEVER arm=$ARM: /$1/ is STILL in the staged fvSolution; the change did not take."; exit 8; }; return 0; }
# every arm: the baseline must be the tightened one
assert_in  '^ *residualControl'
assert_in  'relTol +0\.01'
assert_in  'tolerance +1e-10'
assert_in  'nSweeps +2'
grep -qE "^endTime +$END_TIME;" "$WORK/system/controlDict" || { echo "ABORT G-DEADLEVER endTime is not $END_TIME"; exit 8; }
case "$ARM" in
  P0) assert_in  '^ *consistent +false;'
      assert_in  '^ *nNonOrthogonalCorrectors +0;'
      assert_in  '"\(p\|p_rgh\)" +0\.30;' ;;
  P1) assert_in  '^ *consistent +yes;';  assert_out '^ *consistent +false;' ;;
  P2) assert_in  '^ *nNonOrthogonalCorrectors +2;' ;;
  P3) assert_in  '"\(p\|p_rgh\)" +0\.70;'; assert_out '"\(p\|p_rgh\)" +0\.30;' ;;
  P4) assert_in  '^ *nuTilda +0\.0;';    assert_out '\(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega\)" 0\.70;' ;;
esac
echo "A5P_ONE_CHANGE arm=$ARM change=[$CHANGE] verified_in_staged_file=yes"

# G-STAGED-MD5 -- the instrument this arm actually stages is pinned by hash.
# A staged file that differs from the registered one means the arm is running
# something the pre-registration does not describe.
GOT_MD5_RUNSCRIPT=$(md5sum "$WORK/runScript.py" | awk '{print $1}')
if [ "$GOT_MD5_RUNSCRIPT" != "$MD5_RUNSCRIPT_EXPECT" ]; then
  echo "ABORT G-STAGED-MD5 staged runScript.py md5 is $GOT_MD5_RUNSCRIPT, not the"
  echo "  registered $MD5_RUNSCRIPT_EXPECT.  The arm would run an instrument the"
  echo "  pre-registration does not describe.  REFUSED."
  exit 8
fi
echo "A5P_STAGED_MD5 arm=$ARM runScript.py=$GOT_MD5_RUNSCRIPT pinned=yes"

# THE AGE DATUM.  0/U is touched LAST at staging, so it dates the run allowed
# to produce the answer (CLAUDE.md rule 4 age guard).  It is also the staging
# anchor the mtime corroborator compares against.
touch "$WORK/0/U"
AGE_DATUM=$(stat -c %Y "$WORK/0/U")

cat > "$CMDFILE" <<CMDEOF
set -o pipefail
cd /mnt/$ARM
mpirun -np $RANKS python runScript.py -task=run_model 2>&1
echo "A5P_SOLVER_RC: \$?"
CMDEOF

# ===========================================================================
# LA.1 -- READERS THAT PRESERVE STDERR.
# The defect being repaired: every dafoam launcher writes
#   docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null
# so a daemon error, a sudo refusal and a typo'd name ALL read as the empty
# string and become "not running".  Here stderr is CAPTURED, and "could not
# look" is a THIRD return value that never collapses into either other one.
# THERE IS NO `2>/dev/null` ON ANY READER IN THIS FILE.
# ===========================================================================
: "${DOCKER:=sudo -n docker}"
: "${LAUNCH_WITNESS_RE:=^ExecutionTime = }"      # LA.0, registered
: "${LAUNCH_WITNESS_FORBIDDEN_RE:=^Time = }"     # the decomposePar decoy
: "${LAUNCH_CORROBORATOR_RE:=^Running Primal Solver}"
: "${LAUNCH_WITNESS_POLL_S:=5}"
: "${LAUNCH_READER_RETRIES:=6}"
: "${LAUNCH_KILL:=yes}"                          # L-540: a refusal KILLS

# LA.0b -- ASSERT THE DECOY IS NOT THE WITNESS.  A successor editing these two
# variables must not be able to quietly reintroduce the false witness.
if [ "$LAUNCH_WITNESS_RE" = "$LAUNCH_WITNESS_FORBIDDEN_RE" ]; then
  echo "ABORT LA.0b the launch witness has been set to the FORBIDDEN decoy"
  echo "  '$LAUNCH_WITNESS_FORBIDDEN_RE'.  decomposePar prints that 583 lines"
  echo "  before the solver's first step.  REFUSED."
  exit 9
fi
case "$LAUNCH_WITNESS_RE" in
  '^ExecutionTime = ') : ;;
  *) echo "ABORT LA.0b the launch witness is '$LAUNCH_WITNESS_RE', not the"
     echo "  registered '^ExecutionTime = '.  REFUSED."; exit 9 ;;
esac

la_state() {            # $1 = cid  $2 = stderr sink
  # echoes exactly one of: true | false | UNREADABLE
  local out rc
  out=$($DOCKER inspect --format '{{.State.Running}}' "$1" 2>>"$2"); rc=$?
  if [ "$rc" -ne 0 ]; then echo "UNREADABLE"; return 0; fi
  case "$out" in
    true|false) echo "$out" ;;
    *) printf 'la_state: inspect rc=0 but value was %q\n' "$out" >> "$2"
       echo "UNREADABLE" ;;
  esac
}

la_logs() {             # $1 = cid  $2 = destination
  # rc 0 = the log was read.  rc != 0 = COULD NOT LOOK; the destination holds
  # the client's own error text, DELIBERATELY not discarded.
  $DOCKER logs "$1" > "$2" 2>&1
}

# ===========================================================================
# LA.2 -- THE ASSERTION.
#   0  witness seen                                  -> launched: true
#  88  container exited before any witness           -> never started
#  89  bounded wait elapsed, alive, no witness       -> wedged
#  90  the witness reader itself failed              -> could not look
# 88/89/90 are DISJOINT from every exit code this family's solver produces
# (0, 1, 124/137 from the in-container timeout, 125 docker).
# LIMIT, STATED: nothing prevents a future solver exiting 88/89/90 itself.
# That is why the LEDGER carries an explicit `launched: false reason=<r>`
# TOKEN and the grader reads the token, not the number alone.
# ===========================================================================
la_assert_launch() {    # $1 = cid  $2 = budget s  $3 = scratch dir
  local cid="$1" budget="$2" tmp="$3"
  local logf="$tmp/la.log" errf="$tmp/la.stderr" t0 el st
  # TWO COUNTERS, NOT ONE.  With a single counter a SUCCESSFUL inspect resets
  # the tally of FAILED log reads every tick, so a permanently broken log
  # reader never reaches the retry threshold and is reported as
  # never_started_wedged (89) instead of witness_reader_unreadable (90) --
  # exactly the conflation the rule forbids: "I could not look" reported as
  # "I looked and saw nothing".  Each reader clears only its own count.
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
        # The container is gone and no witness was seen.  ONE FINAL READ: the
        # last poll may have raced the final flush.  Only after that read comes
        # back witness-free is "never started" asserted.
        if la_logs "$cid" "$logf"; then
          LA_WITNESS_LINE=$(grep -anE "$LAUNCH_WITNESS_RE" "$logf" | head -1)
          if [ -n "$LA_WITNESS_LINE" ]; then
            LA_REASON="witness seen on the final read after ${el}s at log line ${LA_WITNESS_LINE%%:*}"
            return 0
          fi
        fi
        LA_REASON="never_started_container_exited after ${el}s with no ${LAUNCH_WITNESS_RE} line; decomposePar_decoy_seen=$LA_DECOY_SEEN solver_call_seen=$LA_CORROBORATED"
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
      LA_REASON="never_started_wedged: ${budget}s elapsed, container still Running, no ${LAUNCH_WITNESS_RE} line; decomposePar_decoy_seen=$LA_DECOY_SEEN solver_call_seen=$LA_CORROBORATED"
      return 89
    fi
    sleep "$LAUNCH_WITNESS_POLL_S"
  done
}

# ===========================================================================
# LA.1b -- THE mtime WITNESS: A STRICT INCREASE AGAINST A RECORDED CAPTURE.
# cfd's stage-4 repair (7d7fcebf) found a witness of the form
#     mtime >= t_launch - slack
# CONFIRMING A LAUNCH WHERE NO SOLVER STARTED: pre-existing STAGED files
# satisfied it.  Any absolute-time comparison, and any slack term, has that
# hole.  Required form, implemented here: capture before the container starts;
# WRITE THE CAPTURE TO DISK so a later reader can see what was compared
# against; assert a STRICT increase.  Not `>=`.  Not `>= t - slack`.  Not
# against wall-clock.  NO SLACK TERM EXISTS IN THIS FILE and none may be added:
# a witness needing slack is the wrong witness.
# ===========================================================================
la_capture_pre() {      # $1 = work dir, $2 = capture file.  echoes row count.
  : > "$2"
  find "$1" -type f -printf '%T@ %p\n' | sort > "$2"
  wc -l < "$2" | tr -d ' '
}

la_mtime_witness() {    # $1 = work dir, $2 = the capture
  # rc 0 = at least one file is STRICTLY newer than its captured mtime, or did
  #        not exist at capture time.  rc 1 = nothing wrote -- staged files
  #        alone can NEVER satisfy this, because they are IN the capture at
  #        their own mtimes.
  LA_MTIME_EVIDENCE=$(find "$1" -type f -printf '%T@ %p\n' | sort | awk -v prefile="$2" '
    BEGIN { while ((getline l < prefile) > 0) { i=index(l," "); p=substr(l,i+1); pre[p]=substr(l,1,i-1)+0; seen[p]=1 } }
    { i=index($0," "); p=substr($0,i+1); m=substr($0,1,i-1)+0
      if (!(p in seen))    { print "NEW " p;                             n++ }
      else if (m > pre[p]) { print "ADVANCED " p " " pre[p] " -> " m;     n++ } }
    END { exit (n > 0 ? 0 : 1) }')
  return $?
}

# ===========================================================================
# LA.2b -- THE REFUSAL PATH KILLS THE CONTAINER (L-540).
# `timeout` around a docker CLIENT does not stop the CONTAINER.  A lane on
# this team leaked a container that ran 2,834 s against a 300 s timeout.  A
# launch refusal therefore KILLS, and RECORDS whether the kill succeeded --
# an unverified kill is not a kill.
# ===========================================================================
la_kill() {             # $1 = cid, $2 = stderr sink
  [ "$LAUNCH_KILL" = "yes" ] || { echo "not_attempted"; return 0; }
  if $DOCKER kill "$1" >/dev/null 2>>"$2"; then
    # READ BACK.  A kill that returns 0 and leaves the container Running is
    # the same false zero as a reader that cannot see a non-zero.
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
echo "A5P_LAUNCH_PRECAPTURE arm=$ARM capture=$(basename "$LAUNCH_PRE") rows=$PRE_ROWS staging_anchor_epoch=$AGE_DATUM comparison=strict_increase slack=none"

# THE WITNESS BUDGET must be a strict minority of the deadline: a launch wait
# as long as the cap is not a wait, it is the run.
python3 -c "
import sys
b, t = $LAUNCH_BUDGET_S, $TMO
if not (0 < b < 0.5*t):
    sys.stderr.write('ABORT LA budget %r is not a strict minority of deadline %r\n' % (b, t)); sys.exit(1)
" || { echo "ABORT LA.3 launch-witness budget vs deadline"; exit 65; }

# THE CONTAINER ID IS CAPTURED.  Names are reusable; ids are not.  Every
# reader below addresses the ID, never the name.
CIDFILE="$BASE/${ARM}_${STAMP}.cid"
RUNERR="$BASE/${ARM}_${STAMP}.runerr"
T0=$(date -u +%s)
CID=$(sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET \
    --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo A5P_CONTAINER_UID: \$(id -u) && \
     echo A5P_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k 60 $TMO bash /mnt/$ARM/${PREFIX}_cmd.sh" 2> "$RUNERR") \
  || { echo "ABORT could not start container: $(head -c 400 "$RUNERR")"; exit 4; }
# THE RUN COMMAND RETURNING IS NOT A WITNESS.  It has bought exactly one
# thing: an id to address.  Everything else is asserted below.
case "$CID" in
  [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]*) : ;;
  *) echo "ABORT docker run returned something that is not a container id: '$CID'"
     exit 4 ;;
esac
echo "$CID" > "$CIDFILE"
echo "A5P_CONTAINER_ID arm=$ARM name=$NAME cid=$CID launched_claim=NOT_YET_ASSERTED"

LA_TMP="$BASE/.la_${ARM}_${STAMP}"; mkdir -p "$LA_TMP"
la_assert_launch "$CID" "$LAUNCH_BUDGET_S" "$LA_TMP"; LA_RC=$?

# THE mtime WITNESS, evaluated against the RECORDED capture.  CORROBORATING,
# NOT GATING: DAFoam writes fields at writeInterval, hundreds of steps after
# launch, while processor*/ itself is created by decomposePar -- so as a GATE
# it would either fire on decomposePar (the same false witness as `^Time = `)
# or fire far too late.  The LOG witness gates.  But it is recorded on every
# arm, in both directions, because `launched: true` with NOTHING written since
# the capture is a contradiction a grader must be able to see.
if la_mtime_witness "$WORK" "$LAUNCH_PRE"; then
  LA_MTIME=advanced
else
  LA_MTIME=unchanged_since_capture
fi
echo "A5P_LAUNCH_MTIME_WITNESS arm=$ARM result=$LA_MTIME capture=$(basename "$LAUNCH_PRE") rows=$PRE_ROWS gating=no evidence=[$(printf '%s' "${LA_MTIME_EVIDENCE:-none}" | tr '\n' ';' | head -c 300)]"
if [ "$LA_RC" -eq 0 ] && [ "$LA_MTIME" = "unchanged_since_capture" ]; then
  echo "A5P_LAUNCH_CONTRADICTION arm=$ARM the log witness fired but NOT ONE FILE in $WORK is strictly newer than the recorded capture.  A grader must treat this row as suspect." \
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
    echo "ARM=$ARM ITEM=$ITEM IMG=$IMG DIGEST=$GOT_DIGEST change=[$CHANGE] launched: false reason=[$LA_REASON] launch_rc=$LA_RC waited_s=$LA_WAITED_S budget_s=$LAUNCH_BUDGET_S mtime_witness=$LA_MTIME precapture=$(basename "$LAUNCH_PRE") precapture_rows=$PRE_ROWS cid=$CID container_kill=$KILLED inspect(exit,oomkilled)=[$EXITCODE] decomposePar_decoy_seen=$LA_DECOY_SEEN solver_call_seen=$LA_CORROBORATED log=$(basename "$LOG") stamp=$STAMP"
    echo "A5P_LAUNCH_REFUSED arm=$ARM rc=$LA_RC -- THE SOLVER'S FIRST ARTIFACT NEVER APPEARED.  This row is NOT A RESULT and no grading may read it."
    echo "A5P_LAUNCH_READER_STDERR arm=$ARM: $(tr '\n' ' ' < "$LA_TMP/la.stderr" | head -c 600)"
  } | tee -a "$BASE/ledger.txt"
  sudo -n docker rm "$CID" >/dev/null 2>&1
  rm -f "$PIDFILE"
  exit "$LA_RC"
fi
echo "A5P_LAUNCH_ASSERTED arm=$ARM launched: true reason=[$LA_REASON] waited_s=$LA_WAITED_S budget_s=$LAUNCH_BUDGET_S mtime_witness=$LA_MTIME precapture=$(basename "$LAUNCH_PRE") precapture_rows=$PRE_ROWS cid=$CID solver_call_seen=$LA_CORROBORATED" \
  | tee -a "$BASE/ledger.txt"

# ===========================================================================
# THE RUNAWAY GUARD.  T0 was set BEFORE the launch wait, so the launch wait is
# inside the graded wall and cannot be spent for free.
# ===========================================================================
while :; do
  ST=$(la_state "$CID" "$LA_TMP/la.stderr")
  [ "$ST" = "true" ] || break
  EL=$(( $(date -u +%s) - T0 ))
  COREMIN=$(python3 -c "print('%.3f' % ($EL*$RANKS/60.0))")
  OVER=$(python3 -c "print(1 if $COREMIN > $CAP_COREMIN else 0)")
  if [ "$OVER" = "1" ]; then
    KILLED=$(la_kill "$CID" "$LA_TMP/la.stderr")
    echo "A5P_CAP_EXCEEDED arm=$ARM elapsed_s=$EL core_min=$COREMIN cap=$CAP_COREMIN container_kill=$KILLED -- an overrun STOPS the run; it does not get a new budget (CLAUDE.md rule 12).  This row is NOT A RESULT." \
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
# rc is READ FROM THE PROCESS, never inferred from a marker (Case Protocol §2).
SOLVER_RC=$(grep -a '^A5P_SOLVER_RC: ' "$LOG" | tail -1 | awk '{print $2}')
sudo -n docker rm "$CID" >/dev/null 2>&1
sudo -n chown -R "$(id -u):$(id -g)" "$WORK" 2>>"$LA_TMP/la.stderr" || true

# THE AGE GUARD (CLAUDE.md rule 4): every field at endTime must be NEWER than
# the case's own staged 0/U, which was touched last at staging.
NEWER=$(find "$WORK" -path "*/$END_TIME/*" -type f -newermt "@$AGE_DATUM" | wc -l)
TOTAL=$(find "$WORK" -path "*/$END_TIME/*" -type f | wc -l)
echo "A5P_AGE_GUARD arm=$ARM fields_at_${END_TIME}=$TOTAL newer_than_staging=$NEWER age_datum_epoch=$AGE_DATUM"

{
  echo "ARM=$ARM ITEM=$ITEM IMG=$IMG DIGEST=$GOT_DIGEST change=[$CHANGE] launched: true reason=[$LA_REASON] wall_s=$WALL core_min=$COREMIN cap_core_min=$CAP_COREMIN kernel_rc=$KRC oomkilled=$OOM solver_rc=${SOLVER_RC:-UNREAD} age_datum=$AGE_DATUM fields_at_${END_TIME}=$TOTAL newer_than_staging=$NEWER log=$(basename "$LOG") stamp=$STAMP"
} | tee -a "$BASE/ledger.txt"

echo ""
echo "A5P arm $ARM finished.  GRADE IT WITH THE FROZEN GRADER, WHICH IS THE"
echo "ONLY THING ENTITLED TO A VERDICT:"
echo "  python3 <repo>/cases/dafoam/ladder-a/A5/curriculum_A5P/a5p_grade.py \\"
echo "      --arm $ARM --log $LOG --case-dir $WORK --rc ${SOLVER_RC:-1} \\"
echo "      --end-time $END_TIME$([ "$ARM" = P0 ] && echo ' --baseline')"
echo "  (--case-dir is REQUIRED: a field check that did not run is not a pass.)"

rm -f "$PIDFILE"
exit 0
