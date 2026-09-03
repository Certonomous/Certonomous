#!/usr/bin/env bash
# Curriculum D6RF arm launcher -- F_mp (the FD bright line on the composite J)
# and REF_off (the off-design reference).  The two arms D6R registered and never
# bought.
#
# DERIVED from curriculum_D6R/d6r_run_arm.sh (md5 243f0f631719edf7ae354410276b3cfd)
# with the registered deltas of D6RF PREREGISTRATION.md ADDENDUM 1.  Everything
# not named there is D6R's shape.  THE DELTAS, enumerated:
#   1  two arms, not four; caps 480.0 / 190.0 (section 4d), deadlines 7110/2760
#   2  F_mp gets ITS OWN ARM DIRECTORY, staged as a COPY of D6R's O_mp with the
#      optimiser's output time directories DROPPED (section 2a, S1-S8).  D6R ran
#      F_mp IN PLACE inside O_mp/ -- D6RF-DEF-2, which is D4's arm F2, rc=1 at
#      56 s on `renameSolution ... already exists`.
#   3  THE UNITS GATE, at both of its call sites (rule 14) -- D6RF-DEF-1
#   4  FORBIDDEN_ROOTS ENUMERATED FROM DISK at launch rather than carried as a
#      frozen list, with D6R's preserved root named explicitly at the head
#   5  exactly ONE executable `rm -rf`, targeting $BASE/REF_off and nothing else;
#      F_mp REFUSES on a pre-existing arm directory instead of removing it
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call and
# `( set -e; ... )` does not gate either.  Every step below gates explicitly
# with `|| { echo ABORT...; exit N; }`.
#
# NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives the arm
# and the KERNEL's verdict is read, not the harness's.
#
# REGISTERED EXIT CODES:
#   0   the arm's own rc, from docker inspect .State.ExitCode
#   3   G-ROOT refusal (wrong base, a forbidden root, a live arm, a live driver)
#   4   identity / staging failure (an md5, the image digest, a copy)
#   5   G-COLD or a section 2a staging assertion
#   7   UNITS REFUSAL, HOST SIDE -- distinct, and never a default
#   64  usage / unknown arm
#   65  cap arithmetic
#   77  UNITS REFUSAL, IN CONTAINER (arrives as the container's own ExitCode)
set -uo pipefail

ITEM=D6RF
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF-a2-wing-multipoint-fd
BASE="${BASE:-$REGISTERED_BASE}"
PERMISSION=bc0e687e

BASE_REAL=$(realpath -m "$BASE")
REG_REAL=$(realpath -m "$REGISTERED_BASE")
D6R_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint
D4_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
RUNS_DIR=/home/ubuntu/certonomous-runs

# ---- G-ROOT.2a -- THE NAMED HEAD, AND IT IS TESTED FIRST ON PURPOSE.
# D6R's preserved root is THIS item's READ-ONLY SOURCE, so it is the one wrong
# base a reader is most likely to supply, and the abort must SAY WHOSE evidence
# it just protected rather than emit the generic refusal.  Ordering matters:
# G-ROOT.1 below would catch this base too, with a message that names nothing.
# A guard that fires with the wrong message is a guard nobody learns from.
if [ "$BASE_REAL" = "$(realpath -m "$D6R_ROOT")" ]; then
  echo "ABORT G-ROOT.2a BASE resolves to D6R'S PRESERVED RUN ROOT: $D6R_ROOT"
  echo "  That directory holds arm O_mp's 2,257.933 core-min of GRADED evidence"
  echo "  (ledger.txt ARM=O_mp rc=0) and is THIS ITEM'S READ-ONLY SOURCE for"
  echo "  F_mp's OptView.hst.  This launcher stages by copying OUT of it and, for"
  echo "  REF_off, by removing an arm directory.  Writing there would destroy the"
  echo "  evidence this item depends on.  REFUSED."
  exit 3
fi

# ---- G-ROOT.1 -- BASE must be THIS item's registered root, normalised, so a
# ---- trailing slash, a `.`, a `..` or a symlink cannot walk around the check.
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
  echo "  given:      $BASE_REAL"
  echo "  registered: $REG_REAL"
  echo "  D4-LAUNCHER-DEF-1: a launcher pointed at another item's run root"
  echo "  deletes that item's graded arms.  REFUSED before any staging."
  # AND NAME IT, if the given base is a run root this box actually holds.
  if [ -d "$RUNS_DIR" ] && [ -d "$BASE_REAL" ]; then
    case "$BASE_REAL" in
      "$RUNS_DIR"/*) echo "  THE ROOT JUST PROTECTED: $BASE_REAL -- it holds another item's rows." ;;
    esac
  fi
  exit 3
fi

# ---- G-ROOT.2 -- the belt to G-ROOT.1's braces.  THE LIST IS ENUMERATED FROM
# DISK AT EVERY LAUNCH, never carried forward: D6's own frozen list named roots
# that DO NOT EXIST and omitted eleven that do, and an inert entry in a list
# whose whole job is to NAME whose evidence was protected is exactly the class
# of defect this lab records.  Reading the directory cannot go stale.
if [ -d "$RUNS_DIR" ]; then
  while IFS= read -r forb; do
    [ -z "$forb" ] && continue
    [ "$forb" = "$REG_REAL" ] && continue
    if [ "$BASE_REAL" = "$forb" ]; then
      echo "ABORT G-ROOT.2 BASE resolves to ANOTHER ITEM'S RUN ROOT: $forb"
      echo "  That directory holds a graded row.  This launcher stages by"
      echo "  removing the arm directory, so writing there would destroy it.  REFUSED."
      exit 3
    fi
  done <<< "$(find "$RUNS_DIR" -maxdepth 1 -mindepth 1 -type d -exec realpath -m {} \; 2>/dev/null)"
fi

# ---- G-ROOT.3 -- the LEDGER must belong to this item and to no other.
if [ -f "$BASE/ledger.txt" ]; then
  FOREIGN_ITEM=$(grep -a "^ITEM=" "$BASE/ledger.txt" 2>/dev/null | grep -av "^ITEM=$ITEM$" | head -1)
  if [ -n "$FOREIGN_ITEM" ]; then
    echo "ABORT G-ROOT.3 the ledger at $BASE/ledger.txt carries another item: $FOREIGN_ITEM"
    echo "  Appending here would interleave two items' rows in one file.  REFUSED."
    exit 3
  fi
  if grep -aq "ROW=SHIPPED" "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT G-ROOT.3 the ledger at $BASE/ledger.txt already carries SHIPPED rows."
    echo "  This launcher writes the PATCHED row only (D6R's registered delta,"
    echo "  the row D4 was GRADED on, C-97).  REFUSED."
    exit 3
  fi
fi
echo "D6RF_G_ROOT_PASS item=$ITEM base=$BASE_REAL ledger_clean=yes"

RANKS=4
# ---- REGISTERED CPU PLACEMENT (PREREGISTRATION.md section 4g) -------------
# `mpirun` inside a `--cpus=N` container binds rank 0 to the FIRST CORE OF THE
# HOST TOPOLOGY; concurrent containers land on the same core (MEASURED by the
# D13 lane 2026-08-25).  So: PIN, and MEASURE the placement.  2,3,4,14 is D6R's
# set, measured DISJOINT at freeze from the only live container on this box
# (cpuset 1).  Core 0 is the default landing core the defect names; not used.
CPUSET=2,3,4,14

container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d6rf_" | tr '\n' ',' | sed 's/,$//'
}

# ---- D6RF REGISTERED CAP TABLE (PREREGISTRATION.md section 4d) ------------
# BOTH ARMS ANCHORED ON MEASUREMENTS OF THE PROGRAMS THEY ACTUALLY RUN.
#   F_mp    155.70 core-min  =  D4 arm F3 (47.267 MEASURED, f3_ledger.txt, the
#                               only FD-endpoint arm that has ever succeeded
#                               here) x the MEASURED multipoint factor 3.2949
#                               (= D6RACC2 ACC_mp 119.933 / D4 P2 36.4)
#   REF_off  60.07 core-min  =  the multipoint findFeasibleDesign trim MEASURED
#                               at 833 s in D6R's own O_mp log (line 2115 ->
#                               ClockTime = 833 s at line 10842) x 4/60 = 55.53,
#                               plus one closing multipoint primal 4.54
# CAPS by max(3.0 x estimate, 1.25 x (4/3) x estimate) -- the MAX of two risks,
# NEVER their product:  F_mp max(467.1, 259.5) -> 480.0
#                       REF_off max(180.2, 100.1) -> 190.0
#   arm      estimate    cap      deadline(s)   compute window (core-min)
#   F_mp      155.70    480.0        7110            480.0
#   REF_off    60.07    190.0        2760            190.0
# D6R registered REF_off at a 40.0 cap and a 510 s deadline against a program
# MEASURED at 55.53 core-min / 833 s -- D6RF-DEF-3.  It could not have finished.
cap_core_min() {
  case "$1" in
    F_mp)    echo 480.0 ;;
    REF_off) echo 190.0 ;;
    *)  echo "" ;;
  esac
}
# MEMORY: 20g, NEVER 8g.  The D4-SHIPPED ACC arm was OOM-killed by its 8g cgroup
# (rc=137, 16:56:28Z 2026-08-26), and D6RACC2 measured OOMKilled=false for the
# identical multipoint program at 20g, so 20g is a MEASURED floor, not a guess.
cap_memory() {
  case "$1" in
    F_mp|REF_off) echo 20g ;;
    *) echo "" ;;
  esac
}

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER 6) -----
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc

# ---- FROZEN INSTRUMENT HASHES (PREREGISTRATION.md sections 7a and 7b) -----
MD5_RUNSCRIPT6=93edb4a231e13a7af065368f61a468ef
MD5_FD=7491c3a73c232fb6744990fd8109fd63
MD5_EXTRACT6=1743dd4232a7f06785f71be2f285f08d
MD5_REFOFF=ad67bbeb0c7b502262ebf5d4e8fa21cd
MD5_EXTRACT4=ee7d3c99fd716da23779cb651961918e
MD5_RUNSCRIPT4=2906d52a5dbed2bacbaeaf85a37d3fe8
MD5_LOCUS4=e63df1845771c3e67457443918f5b82e
MD5_PHYS4=74c35c80bb4d395cf8939d851bc6b3f9
MD5_LOCUS6=341189ca866f302a7e1bba8eefad3a57
MD5_PHYS6=ea0a83410c773f753a7750eb3becefdf
MD5_UNITS=40993d949e44aae3f80bf1a3d2cf4998
# D4's PATCHED optimiser history, staged READ-ONLY into REF_off/ as OptView.hst
MD5_D4_HST=0d956d6ccbc010402915710f662d3b11
D4_HST_SRC="$D4_ROOT/O/OptView.hst"
# THE UNDEFORMED REFERENCE MESH.  Section 2a S3: the double-deformation confound
# that killed D4's arm F is eliminated BY MEASUREMENT, not by assumption.
MD5_REF_MESH=0fb1935a9b8781b73ac4ccb136e3ec68

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: d6rf_run_arm.sh <F_mp|REF_off> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: d6rf_run_arm.sh <F_mp|REF_off> <image>"; exit 64; }
# THE ARM GUARD IS AN EQUALITY, NOT A PREFIX MATCH.
case "$ARM" in
  F_mp|REF_off) : ;;
  *) echo "ABORT arm '$ARM' is not one of this item's two REGISTERED arms (F_mp, REF_off)."
     echo "  A third arm is a separate item with its own registration.  REFUSED."
     exit 64 ;;
esac

# ---- G-ROOT.5 -- A LIVE ARM IS NEVER RE-STAGED.  Two live readings, BEFORE
# ---- any destructive act.
LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d6rf_${ARM}_" 2>/dev/null | grep "^d6rf_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  echo "  Re-staging would remove the live arm directory under it.  REFUSED."
  exit 3
fi
PIDFILE="$BASE/d6rf_driver.pid"
if [ -f "$PIDFILE" ]; then
  DPID=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$DPID" ] && kill -0 "$DPID" 2>/dev/null; then
    ANCESTOR=no; p=$$
    for _ in $(seq 1 64); do
      if [ "$p" = "$DPID" ]; then ANCESTOR=yes; break; fi
      p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
      if [ -z "$p" ] || [ "$p" = "0" ]; then break; fi
    done
    DCWD=$(readlink -f "/proc/$DPID/cwd" 2>/dev/null)
    if [ "$ANCESTOR" = "no" ] || [ "$DCWD" = "$BASE_REAL" ]; then
      echo "ABORT G-ROOT.5 driver pidfile $PIDFILE names LIVE pid $DPID (ancestor_of_this_launcher=$ANCESTOR cwd=$DCWD)."
      echo "  Another driver owns this run root, or a process sits inside it.  REFUSED."
      exit 3
    fi
  fi
fi
echo "D6RF_G_ROOT5_PASS arm=$ARM live_same_arm_containers=none driver_pidfile=$([ -f "$PIDFILE" ] && echo present_owner_is_ancestor_or_stale || echo absent)"

CAP=$(cap_core_min "$ARM")
MEM=$(cap_memory "$ARM")
test -n "$CAP" || { echo "ABORT unknown arm $ARM -- no registered cap"; exit 64; }
test -n "$MEM" || { echo "ABORT unknown arm $ARM -- no registered memory cap"; exit 64; }

# ===========================================================================
# THE CAP FRAME.  D6-CAP-FRAME-1 (L-371) is repaired the D4S-F3SR way and the
# cap DOES NOT MOVE -- the enforced deadline moves DOWN by a bounded allowance.
# THE D19T IDENTITY IS EXECUTED HERE, EVERY LAUNCH, AND `TMO > 0` IS ASSERTED:
# D19T was frozen, md5-pinned, gate-checked and launched TWICE and no check ever
# executed its own cap arithmetic -- `int(CAP*60/RANKS) - 60` gave its MESH arm
# TMO = 0 s and no D19T arm could ever run.
# THIS LINEAGE'S REGISTERED RESERVE IS 90, NOT 60.  All three lineage constants
# are recorded in PREREGISTRATION.md section 4e so a successor does not read the
# difference as drift:  D6R/D6RF 90 (d6r_run_arm.sh:251);  A1/D19 60
# (d19o_run_arm.sh:153);  SO3 180 (so3_run_arm.sh:208).  90 is the stricter of
# the two this lineage could take, and it is the one registered.
FRAME_ALLOWANCE_S=90
KILL_GRACE_S=60
# THE ASSERTION INVERTS AND RE-ADDS THE ALLOWANCE, so no edit to it can silently
# widen the cap: (TMO + FRAME_ALLOWANCE_S) * RANKS / 60 == CAP.
TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)) - $FRAME_ALLOWANCE_S)") || { echo "ABORT tmo calc"; exit 65; }
test "$TMO" -gt 0 || { echo "ABORT D19T IDENTITY: frame allowance ${FRAME_ALLOWANCE_S}s consumes the whole ${CAP} core-min cap at $RANKS ranks; TMO=$TMO"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % (($TMO+$FRAME_ALLOWANCE_S)*$RANKS/60.0))") || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
cap, back = $CAP, $BACKCHECK
if abs(cap-back) > 0.02:
    sys.stderr.write('ABORT CAP MISMATCH registered=%r enforced_plus_allowance=%r\n' % (cap, back)); sys.exit(1)
" || { echo "ABORT enforced cap + frame allowance != registered cap"; exit 65; }
echo "D6RF_CAP_FRAME arm=$ARM registered_core_min=$CAP ranks=$RANKS deadline_in_container_s=$TMO frame_allowance_s=$FRAME_ALLOWANCE_S kill_grace_s=$KILL_GRACE_S worst_case_host_core_min=$BACKCHECK enforced_in_frame=container graded_in_frame=host_bracket_T0_T1"
echo "D4_CAP_ASSERT arm=$ARM registered_core_min=$CAP ranks=$RANKS enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM"

# ---- host state, read before ranks are claimed ---------------------------
MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D6RF_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 run root mode $(stat -c '%a' "$BASE")"; exit 4; }

# ---- staged-instrument identity, re-asserted before EVERY launch ---------
echo "$MD5_RUNSCRIPT6  $BASE/d6r_opt_runScript.py" | md5sum -c - || { echo "ABORT d6r_opt_runScript.py md5"; exit 4; }
echo "$MD5_FD  $BASE/d6r_fd_endpoint.py"           | md5sum -c - || { echo "ABORT d6r_fd_endpoint.py md5"; exit 4; }
echo "$MD5_EXTRACT6  $BASE/d6r_extract_endpoint.py"| md5sum -c - || { echo "ABORT d6r_extract_endpoint.py md5"; exit 4; }
echo "$MD5_REFOFF  $BASE/d6r_ref_off.py"           | md5sum -c - || { echo "ABORT d6r_ref_off.py md5"; exit 4; }
echo "$MD5_EXTRACT4  $BASE/d4_extract_endpoint.py" | md5sum -c - || { echo "ABORT d4_extract_endpoint.py md5"; exit 4; }
echo "$MD5_RUNSCRIPT4  $BASE/d4_opt_runScript.py"  | md5sum -c - || { echo "ABORT d4_opt_runScript.py md5"; exit 4; }
echo "$MD5_LOCUS4  $BASE/d4_endpoint_locus.py"     | md5sum -c - || { echo "ABORT d4_endpoint_locus.py md5"; exit 4; }
echo "$MD5_PHYS4  $BASE/d4_endpoint_physical.py"   | md5sum -c - || { echo "ABORT d4_endpoint_physical.py md5"; exit 4; }
echo "$MD5_LOCUS6  $BASE/d6rf_endpoint_locus.py"   | md5sum -c - || { echo "ABORT d6rf_endpoint_locus.py md5"; exit 4; }
echo "$MD5_PHYS6  $BASE/d6rf_endpoint_physical.py" | md5sum -c - || { echo "ABORT d6rf_endpoint_physical.py md5"; exit 4; }
echo "$MD5_UNITS  $BASE/d6rf_units_assert.py"      | md5sum -c - || { echo "ABORT d6rf_units_assert.py md5"; exit 4; }

# ---- image identity by DIGEST, resolved from the local store -------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1)       WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  dafoam/opt-packages:latest) WANT=$IMG_SHIPPED_DIGEST; ROW=SHIPPED ;;
  *) echo "ABORT image $IMG is not a registered row"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }
test "$ROW" = "PATCHED" || {
  echo "ABORT G-ROW D6RF is registered PATCHED-ONLY (the row D4 was GRADED on, C-97); got ROW=$ROW ($IMG)."
  echo "  The SHIPPED row is NOT bought here; a second row is a separate item."
  exit 4; }
echo "D6RF_G_ROW_PASS row=$ROW digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d6rf_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"
STAGE_EVID="$BASE/${ARM}_STAGING_EVIDENCE.txt"

# ===========================================================================
# STAGING.  PREREGISTRATION.md section 2a, frozen BEFORE this file was written.
# Every step aborts the arm rather than degrading, and prints its own evidence
# line into $STAGE_EVID.
# ===========================================================================
stage_say() { echo "$*"; echo "$*" >> "$STAGE_EVID"; }
: > "$STAGE_EVID"
stage_say "D6RF_STAGE arm=$ARM utc=$(date -u +%Y%m%dT%H%M%SZ) base=$BASE_REAL permission=$PERMISSION"

if [ "$ARM" = "F_mp" ]; then
  # ------------------------------------------------------------------ S1
  SRC="$D6R_ROOT/O_mp"
  test -d "$SRC" || { stage_say "ABORT S1 source absent: $SRC"; exit 5; }
  test -f "$SRC/OptView.hst" || { stage_say "ABORT S1 no OptView.hst under $SRC -- there is no endpoint to read"; exit 5; }
  # THE DESTINATION MUST BE ABSENT.  F_mp has NO `rm -rf`: a re-fire finds a
  # stale arm directory and REFUSES rather than removing 1.1 GB that may hold a
  # partial result.  Recovery is an explicit archive (`mv`), never an implicit
  # delete -- the S-29 pattern.
  if [ -e "$WORK" ]; then
    stage_say "ABORT S1 $WORK already exists.  F_mp does not remove an arm directory."
    stage_say "  A re-fire needs the partial root ARCHIVED by mv, not deleted here."
    exit 5
  fi
  stage_say "D6RF_STAGE_F_mp (S1) OK src=$SRC exists, OptView.hst present, dst=$WORK does not exist"
  # ------------------------------------------------------------------ S3
  # THE DOUBLE-DEFORMATION CONFOUND, ELIMINATED BY MEASUREMENT.  D4's arm F died
  # on `Mesh quality error!`; its F3 repair recorded the same md5 on both sides.
  test -f "$BASE/base/constant/polyMesh/points.gz" || { stage_say "ABORT S3 no reference mesh at $BASE/base"; exit 5; }
  BASE_MESH_MD5=$(md5sum "$BASE/base/constant/polyMesh/points.gz" | cut -d' ' -f1)
  test "$BASE_MESH_MD5" = "$MD5_REF_MESH" || { stage_say "ABORT S3 base reference mesh md5 $BASE_MESH_MD5 != registered $MD5_REF_MESH"; exit 5; }
  for mp in mp04 mp05 mp06; do
    test -f "$SRC/$mp/constant/polyMesh/points.gz" || { stage_say "ABORT S3 $SRC/$mp has no reference mesh"; exit 5; }
    M=$(md5sum "$SRC/$mp/constant/polyMesh/points.gz" | cut -d' ' -f1)
    test "$M" = "$MD5_REF_MESH" || {
      stage_say "ABORT S3 $mp reference mesh md5 $M != registered $MD5_REF_MESH"
      stage_say "  The source's UNDEFORMED reference mesh has MOVED, so an FD"
      stage_say "  perturbation would warp from an already-deformed mesh -- the"
      stage_say "  double-deformation confound that killed D4's arm F.  REFUSED."
      exit 5; }
  done
  stage_say "D6RF_STAGE_F_mp (S3) OK undeformed reference mesh md5 $MD5_REF_MESH on base and on mp04 mp05 mp06 -- double-deformation confound eliminated by MEASUREMENT"
  # ------------------------------------------------------------------ S4
  SRC_HST_MD5=$(md5sum "$SRC/OptView.hst" | cut -d' ' -f1)
  SRC_TIMEDIRS=$(ls -d "$SRC"/mp04/processor0/* 2>/dev/null | wc -l)
  stage_say "D6RF_STAGE_F_mp (S4) source pre-copy: OptView.hst md5=$SRC_HST_MD5, entries under mp04/processor0 = $SRC_TIMEDIRS"
  cp -a "$SRC" "$WORK" || { stage_say "ABORT S4 stage copy of $SRC failed"; exit 4; }
  COPY_EPOCH=$(date -u +%s); echo "$COPY_EPOCH" > "$WORK/.d6rf_copy_epoch"
  POST_HST_MD5=$(md5sum "$SRC/OptView.hst" | cut -d' ' -f1)
  POST_TIMEDIRS=$(ls -d "$SRC"/mp04/processor0/* 2>/dev/null | wc -l)
  test "$POST_HST_MD5" = "$SRC_HST_MD5" || { stage_say "ABORT S4 SOURCE CHANGED during the copy: OptView.hst md5 $SRC_HST_MD5 -> $POST_HST_MD5"; exit 5; }
  test "$POST_TIMEDIRS" = "$SRC_TIMEDIRS" || { stage_say "ABORT S4 SOURCE CHANGED during the copy: mp04/processor0 entries $SRC_TIMEDIRS -> $POST_TIMEDIRS"; exit 5; }
  stage_say "D6RF_STAGE_F_mp (S4) OK cp -a (mtimes PRESERVED), copy_epoch=$COPY_EPOCH, SOURCE INTACT after the copy"
  # ------------------------------------------------------------------ S5
  # DROP THE OPTIMISER'S OUTPUTS FROM THE COPY.  D6RF-DEF-2: pyDAFoam's
  # renameSolution refuses to move onto an existing directory -- D4's arm F2,
  # rc=1 at 56 s.  `0` is KEPT (initial fields and the restart state); so are
  # constant/, system/, FFD/, dRdWColoring_4.bin and OptView.hst.
  # `0` and `0.orig` are KEPT and must never match: `0.orig` carries letters, so
  # the numeric test below excludes it, and `0` is excluded by name.  A bare
  # `0.*` glob would have deleted `0.orig` -- the pristine initial-condition
  # backup -- which is why the test is a NAME TEST and not a glob.
  is_time_dir() {
    case "$1" in
      0|"") return 1 ;;
      *[!0-9.]*) return 1 ;;
      *.*.*) return 1 ;;
      *) return 0 ;;
    esac
  }
  count_time_dirs() {   # $1 = the tree to count under
    local n=0 d b
    for d in "$1"/mp04/* "$1"/mp05/* "$1"/mp06/* \
             "$1"/mp04/processor*/* "$1"/mp05/processor*/* "$1"/mp06/processor*/*; do
      [ -d "$d" ] || continue
      b=$(basename "$d")
      is_time_dir "$b" && n=$((n+1))
    done
    echo "$n"
  }
  BEFORE_DROP=$(count_time_dirs "$WORK")
  DROPPED=0
  for d in "$WORK"/mp04/* "$WORK"/mp05/* "$WORK"/mp06/* \
           "$WORK"/mp04/processor*/* "$WORK"/mp05/processor*/* "$WORK"/mp06/processor*/*; do
    [ -d "$d" ] || continue
    is_time_dir "$(basename "$d")" || continue
    rm -rf "$d" || { stage_say "ABORT S5 could not drop $d"; exit 5; }
    DROPPED=$((DROPPED+1))
  done
  for mp in mp04 mp05 mp06; do
    rm -rf "$WORK/$mp/postProcessing" 2>/dev/null
  done
  rm -rf "$WORK/reports" 2>/dev/null
  rm -rf "$WORK/postProcessing" 2>/dev/null
  rm -f  "$WORK/mphys.html" "$WORK/opt_IPOPT.txt" "$WORK/d6r_cmd.sh" 2>/dev/null
  REMAIN=$(count_time_dirs "$WORK")
  test "$REMAIN" -eq 0 || { stage_say "ABORT S5 $REMAIN output time directories remain in the COPY (required 0, dropped $DROPPED of $BEFORE_DROP)"; exit 5; }
  # `0` and `0.orig` SURVIVED, and that is asserted rather than assumed.
  for mp in mp04 mp05 mp06; do
    test -f "$WORK/$mp/0/U" || { stage_say "ABORT S5 $mp/0/U was dropped -- the initial fields are KEPT, not swept"; exit 5; }
    test -d "$WORK/$mp/0.orig" || { stage_say "ABORT S5 $mp/0.orig was dropped -- the pristine backup is KEPT, not swept"; exit 5; }
    test -f "$WORK/$mp/processor0/0/U" || { stage_say "ABORT S5 $mp/processor0/0/U was dropped -- the decomposed restart state is KEPT"; exit 5; }
  done
  # AND THE SOURCE IS ASSERTED INTACT: D6R's evidence is not touched.
  SRC_REMAIN=$(ls -d "$SRC"/mp04/processor0/0.* 2>/dev/null | wc -l)
  test "$SRC_REMAIN" -gt 1 || { stage_say "ABORT S5 SOURCE INTACT assertion FAILED: only $SRC_REMAIN pseudo-time dirs remain under $SRC/mp04/processor0 (required > 1) -- D6R's evidence may have been touched"; exit 5; }
  test -f "$WORK/OptView.hst" || { stage_say "ABORT S5 OptView.hst was dropped from the copy"; exit 5; }
  test -f "$WORK/mp04/dRdWColoring_4.bin" || { stage_say "ABORT S5 the cached colouring was dropped from the copy -- the cap is priced with it present"; exit 5; }
  stage_say "D6RF_STAGE_F_mp (S5) OK dropped $DROPPED of $BEFORE_DROP output time directories from the COPY, $REMAIN remain (required 0); 0/, 0.orig/ and processor*/0/ KEPT and asserted; OptView.hst and dRdWColoring_4.bin KEPT; SOURCE INTACT ($SRC_REMAIN pseudo-time dirs still under $SRC/mp04/processor0)"
  # ------------------------------------------------------------------ S6
  cp -a "$BASE/d6r_extract_endpoint.py" "$BASE/d6r_fd_endpoint.py" \
        "$BASE/d6r_opt_runScript.py" "$BASE/d6rf_endpoint_locus.py" \
        "$BASE/d6rf_endpoint_physical.py" "$BASE/d6rf_units_assert.py" \
        "$WORK/" || { stage_say "ABORT S6 stage instruments"; exit 4; }
  { echo "$MD5_EXTRACT6  $WORK/d6r_extract_endpoint.py"
    echo "$MD5_FD  $WORK/d6r_fd_endpoint.py"
    echo "$MD5_RUNSCRIPT6  $WORK/d6r_opt_runScript.py"
    echo "$MD5_LOCUS6  $WORK/d6rf_endpoint_locus.py"
    echo "$MD5_PHYS6  $WORK/d6rf_endpoint_physical.py"
    echo "$MD5_UNITS  $WORK/d6rf_units_assert.py"; } | md5sum -c - || { stage_say "ABORT S6 staged instrument md5 in the arm directory"; exit 4; }
  stage_say "D6RF_STAGE_F_mp (S6) OK six instruments staged, every md5 asserted"
  # ------------------------------------------------------------------ S7
  UNITS_RUNSCRIPT=d6r_opt_runScript.py
  DVFILE=d6r_endpoint_dvs.json
  for p in d6rf_endpoint_dvs_PHYSICAL.json d6r_endpoint_dvs_DRIVERSCALED.json \
           d6r_endpoint_dvs.json d6r_major_history.json d6r_fd_endpoint.json \
           d6r_fd_endpoint.jsonl; do
    rm -f "$WORK/$p"
  done
  stage_say "D6RF_STAGE_F_mp (S7) OK this arm's six registered products swept from the copy"
else
  # ---------------------------------------------------------- REF_off, cold
  # THE ONLY EXECUTABLE `rm -rf` IN THIS FILE, and every guard above precedes
  # it.  It targets $BASE/REF_off and nothing else; $BASE has already been
  # proved to be this item's own registered root (G-ROOT.1), not any other
  # item's (G-ROOT.2, enumerated from disk), and not D6R's (the named head).
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/base" "$WORK" || { stage_say "ABORT stage copy"; exit 4; }
  for mp in mp04 mp05 mp06; do
    cp -a "$BASE/base" "$WORK/$mp" || { stage_say "ABORT stage $mp copy"; exit 4; }
    test -n "$(ls -d "$WORK/$mp"/processor* 2>/dev/null)" && { stage_say "ABORT G-COLD $mp processor* present"; exit 5; }
  done
  for bad in "$WORK/reports" "$WORK/OptView.hst" "$WORK/opt_IPOPT.txt" \
             "$WORK/dRdWColoring_4.bin" "$WORK/d6r_ref_off.json" \
             "$WORK/d4_endpoint_dvs.json" "$WORK/d4_endpoint_dvs_PHYSICAL.json"; do
    test -e "$bad" && { stage_say "ABORT G-COLD $bad exists"; exit 5; }
  done
  test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { stage_say "ABORT G-COLD processor* present"; exit 5; }
  test -n "$(ls -d "$WORK"/[0-9]*.[0-9]* 2>/dev/null)" && { stage_say "ABORT G-COLD time dir present"; exit 5; }
  test -f "$WORK/0/U" || { stage_say "ABORT G-COLD 0/U missing"; exit 5; }
  cp -a "$BASE/d4_extract_endpoint.py" "$BASE/d4_opt_runScript.py" \
        "$BASE/d4_endpoint_locus.py" "$BASE/d4_endpoint_physical.py" \
        "$BASE/d6r_opt_runScript.py" "$BASE/d6r_ref_off.py" \
        "$BASE/d6rf_endpoint_locus.py" "$BASE/d6rf_units_assert.py" \
        "$WORK/" || { stage_say "ABORT stage instruments"; exit 4; }
  { echo "$MD5_EXTRACT4  $WORK/d4_extract_endpoint.py"
    echo "$MD5_RUNSCRIPT4  $WORK/d4_opt_runScript.py"
    echo "$MD5_LOCUS4  $WORK/d4_endpoint_locus.py"
    echo "$MD5_PHYS4  $WORK/d4_endpoint_physical.py"
    echo "$MD5_RUNSCRIPT6  $WORK/d6r_opt_runScript.py"
    echo "$MD5_REFOFF  $WORK/d6r_ref_off.py"
    echo "$MD5_LOCUS6  $WORK/d6rf_endpoint_locus.py"
    echo "$MD5_UNITS  $WORK/d6rf_units_assert.py"; } | md5sum -c - || { stage_say "ABORT staged instrument md5 in the arm directory"; exit 4; }
  # D4's PATCHED history, staged READ-ONLY, md5-asserted, BEFORE the datum so
  # the age guard dates it as an INPUT (the grader exempts it by md5).
  echo "$MD5_D4_HST  $D4_HST_SRC" | md5sum -c - || { stage_say "ABORT D4 OptView.hst md5 (source changed)"; exit 4; }
  cp "$D4_HST_SRC" "$WORK/OptView.hst" || { stage_say "ABORT stage D4 history"; exit 4; }
  stage_say "D6RF_D4_HST_STAGED arm=$ARM md5=$(md5sum "$WORK/OptView.hst" | cut -d' ' -f1) source=$D4_HST_SRC"
  UNITS_RUNSCRIPT=d4_opt_runScript.py
  DVFILE=d4_endpoint_dvs.json
  rm -f "$WORK/d4_endpoint_dvs.json" "$WORK/d4_endpoint_dvs_PHYSICAL.json" \
        "$WORK/d4_endpoint_dvs_DRIVERSCALED.json" "$WORK/d6r_ref_off.json" \
        "$WORK/d4_major_history.json"
  stage_say "D6RF_STAGE_REF_off OK cold copy, G-COLD asserted, eight instruments staged with every md5, D4 history read-only"
fi

# ===========================================================================
# THE UNITS GATE, CALL SITE 1 OF 2 (CLAUDE.md rule 14 -- a lesson is not applied
# until EVERY call site asserts it).  HOST SIDE, at staging: if an endpoint
# design-variable file survived the product sweep above, it is graded HERE and
# a refusal is rc 7, distinct.  A MISSING MARKER IS A REFUSAL, NEVER A DEFAULT.
# ===========================================================================
if [ -e "$WORK/$DVFILE" ]; then
  stage_say "D6RF_UNITS_CALLSITE_1 arm=$ARM an endpoint artefact SURVIVED the sweep: $WORK/$DVFILE -- grading it before anything else runs"
  python3 "$WORK/d6rf_units_assert.py" "$WORK/$DVFILE" --runscript "$WORK/$UNITS_RUNSCRIPT"
  UR=$?
  if [ "$UR" -ne 0 ]; then
    stage_say "ABORT UNITS (call site 1, host) arm=$ARM file=$WORK/$DVFILE assert_rc=$UR"
    stage_say "  A design vector that cannot prove it is PHYSICAL is never handed"
    stage_say "  to the mesh deformer.  D4 arm F: no marker, 62 of 96 shape"
    stage_say "  components outside [-1,1], max |value| 6.024592, rc=1 at 15 s."
    exit 7
  fi
else
  stage_say "D6RF_UNITS_CALLSITE_1 arm=$ARM no endpoint artefact survived the sweep (expected on a first fire); call site 2 grades the one the wrapper writes"
fi

# ---- THE AGE DATUM IS WRITTEN LAST (section 2a S8, CLAUDE.md rule 4) ------
touch "$WORK/0"/* || { stage_say "ABORT S8 age-guard datum"; exit 5; }
AGE_DATUM=$(stat -c '%Y' "$WORK/0/U")
echo "$AGE_DATUM" > "$WORK/.d4_age_datum"
stage_say "D6RF_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM (every registered product must be strictly newer)"

# ===========================================================================
# THE ARM COMMAND.  THE UNITS GATE IS CALL SITE 2 OF 2 AND IT SITS BETWEEN THE
# WRAPPER THAT WRITES THE DESIGN VECTOR AND THE mpirun THAT CONSUMES IT.  `&&`
# chaining means a units refusal (rc 77) propagates as the container's own
# ExitCode and THE MESH IS NEVER TOUCHED.
# ===========================================================================
case "$ARM" in
  F_mp)    CMD="python d6rf_endpoint_physical.py --age-datum $AGE_DATUM && python d6rf_units_assert.py d6r_endpoint_dvs.json --runscript d6r_opt_runScript.py && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d6r_fd_endpoint.py" ;;
  REF_off) CMD="python d4_endpoint_physical.py --age-datum $AGE_DATUM && python d6rf_units_assert.py d4_endpoint_dvs.json --runscript d4_opt_runScript.py && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d6r_ref_off.py" ;;
esac
case "$CMD" in
  *d6rf_units_assert.py*) : ;;
  *) echo "ABORT the arm command for $ARM does not invoke the units gate; call site 2 is missing (rule 14)"; exit 7 ;;
esac

CMDFILE="$WORK/d6rf_cmd.sh"
printf '%s\n' "$CMD" > "$CMDFILE" || { echo "ABORT cmd file"; exit 4; }
echo "D6RF_CMDFILE arm=$ARM md5=$(md5sum "$CMDFILE" | cut -d' ' -f1) deadline_in_container_s=$TMO units_gate=present"

CPUSAMPLE="$BASE/${ARM}_${STAMP}.cpu.jsonl"
# DELIVERED CORES ARE MEASURED, NOT INFERRED FROM THE QUOTA FLAG.  Passive
# reader; an absent sample file is reported NOT_MEASURED, never as a pass.
(
  for _ in $(seq 1 100000); do
    cid=$(sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | head -1)
    if [ -n "$cid" ]; then break; fi
    sleep 1
  done
  cg=""
  for cand in /sys/fs/cgroup/system.slice/docker-${cid}*.scope/cpu.stat \
              /sys/fs/cgroup/cpu/docker/${cid}*/cpuacct.usage; do
    if [ -e "$cand" ]; then cg="$cand"; break; fi
  done
  if [ -z "$cg" ]; then echo '{"delivered_cores":null,"note":"cgroup path not found"}' >> "$CPUSAMPLE"; exit 0; fi
  prev=""; prevt=""
  while sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | grep -q .; do
    now=$(date +%s.%N)
    if [ "$(basename "$cg")" = "cpu.stat" ]; then
      u=$(awk '/^usage_usec/{print $2}' "$cg" 2>/dev/null)
      t=$(awk '/^throttled_usec/{print $2}' "$cg" 2>/dev/null)
      n=$(awk '/^nr_throttled/{print $2}' "$cg" 2>/dev/null)
    else
      u=$(( $(cat "$cg" 2>/dev/null || echo 0) / 1000 )); t=0; n=0
    fi
    if [ -n "$prev" ] && [ -n "$u" ]; then
      python3 -c "
import json
du=($u-$prev)/1e6; dt=$now-$prevt
print(json.dumps({'t':round($now,2),'delivered_cores':round(du/dt,4) if dt>0 else None,'throttled_usec':$t,'nr_throttled':$n}))
" >> "$CPUSAMPLE" 2>/dev/null
    fi
    prev=$u; prevt=$now
    sleep 15
  done
) &
SAMPLER=$!

T0=$(date -u +%s)
# rc CAPTURE IS CLOSED (docker inspect, no --rm).  The CAP lives INSIDE the
# container (`timeout -k 60 $TMO`) and survives shell death.  NOTHING here reads
# `$?` of a setsid or timeout line -- the setsid parent returns 0 for every
# outcome, which is why the rc is taken from the kernel below.
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$(basename "$WORK")" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4S_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4S_IDWARP_IMPORTED_FROM:\",p); print(\"D4S_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     echo D4S_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k $KILL_GRACE_S $TMO bash /mnt/$(basename "$WORK")/d6rf_cmd.sh" > /dev/null 2>&1 \
  || { echo "ABORT could not start container"; exit 4; }

# The cap is a RUNAWAY GUARD THAT REPORTS (Sanaa, 2026-08-25); the CEILING is
# the fleet safety stop (Sanaa, 2026-09-03 ~21:00Z): far above the estimate, not
# the estimate itself, and it stops the run gracefully regardless of trend.
CEILING=$(python3 -c "print('%.1f' % (3.0*$CAP))")
echo "D6RF_RUNAWAY_GUARD arm=$ARM cap_core_min=$CAP ceiling_core_min=$CEILING mode=report_then_graceful_stop_at_ceiling"
CAP_REPORTED=no; CEILING_HIT=no
while true; do
  RUNNING=$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)
  NOW=$(date -u +%s); EL=$((NOW-T0))
  CM=$(python3 -c "print(round($EL*$RANKS/60.0,3))")
  if [ "$RUNNING" != "true" ]; then break; fi
  if [ "$CAP_REPORTED" = "no" ] && [ "$(python3 -c "print(1 if $CM > $CAP else 0)")" = "1" ]; then
    CAP_REPORTED=yes
    echo "D6RF_CAP_CROSSED arm=$ARM core_min=$CM cap=$CAP ceiling=$CEILING action=REPORTED_RUN_CONTINUES supervisor_decides" | tee -a "$BASE/ledger.txt"
  fi
  if [ "$(python3 -c "print(1 if $CM > $CEILING else 0)")" = "1" ]; then
    CEILING_HIT=yes
    echo "D6RF_CEILING_HIT arm=$ARM core_min=$CM ceiling=$CEILING action=GRACEFUL_STOP" | tee -a "$BASE/ledger.txt"
    sudo -n docker stop -t 30 "$NAME" >/dev/null 2>&1
    break
  fi
  sleep 10
done
sudo -n docker logs "$NAME" > "$LOG" 2>&1
# THE KERNEL'S VERDICT, read BEFORE the container is removed.
rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$NAME" 2>/dev/null)
test -n "$rc" || rc=125
T1=$(date -u +%s)
WALL=$((T1-T0))
kill $SAMPLER 2>/dev/null; wait $SAMPLER 2>/dev/null
SIBLINGS_POST=$(container_census)
DELIVERED=$(python3 -c "
import json,sys,os
p='$CPUSAMPLE'
if not os.path.exists(p): print('NOT_MEASURED'); sys.exit()
v=[]; thr=0
for line in open(p):
    try: d=json.loads(line)
    except Exception: continue
    if d.get('delivered_cores') is not None: v.append(d['delivered_cores'])
    thr=max(thr, d.get('nr_throttled') or 0)
print('%s n=%d max_nr_throttled=%d' % (('%.4f'%(sum(v)/len(v)) if v else 'NOT_MEASURED'), len(v), thr))
" 2>/dev/null)

INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
# THE CONTAINER'S OWN KERNEL CLOCK, in the same inspect and BEFORE the rm.  This
# is the frame the deadline is ENFORCED in; WALL (T0..T1) is the frame the cap
# is GRADED in.  Recording both SEPARATES them instead of conflating them, and
# the grader BINDS the difference at G-CAPS.  Absent -> NOT_MEASURED
# (INFRASTRUCTURE, L-342); the gate then falls back to the HOST bracket alone,
# which is the STRICTER reading, so the fallback can never turn a failing cap
# into a pass.
CSTART=$(sudo -n docker inspect --format '{{.State.StartedAt}}' "$NAME" 2>/dev/null)
CFIN=$(sudo -n docker inspect --format '{{.State.FinishedAt}}' "$NAME" 2>/dev/null)
CWALL=$(python3 -c "
import datetime
def p(s):
    s = s.strip().replace('Z', '+00:00')
    i = s.find('.')
    if i >= 0:
        j = i + 1
        while j < len(s) and s[j].isdigit():
            j += 1
        if j - i > 7:
            s = s[:i + 7] + s[j:]
    return datetime.datetime.fromisoformat(s)
try:
    print(int(round((p('$CFIN') - p('$CSTART')).total_seconds())))
except Exception:
    print('NOT_MEASURED')
" 2>/dev/null)
test -n "$CWALL" || CWALL=NOT_MEASURED
echo "D6RF_CONTAINER_CLOCK arm=$ARM started_at=$CSTART finished_at=$CFIN container_wall_s=$CWALL host_wall_s_bracket_T0_T1=$WALL"
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$WORK" 2>/dev/null

# A UNITS REFUSAL IN THE CONTAINER IS NAMED ON THE RECORD, not left as a bare
# exit code a reader has to look up.
if [ "$rc" = "77" ]; then
  echo "D6RF_UNITS_REFUSAL_IN_CONTAINER arm=$ARM rc=77 -- call site 2 refused the design vector; THE MESH WAS NEVER TOUCHED.  See $(basename "$LOG") for the failing check." | tee -a "$BASE/ledger.txt"
fi

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/ledger.txt"
{
  echo "ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM inspect(exit,oomkilled)=[$INSPECT] container_wall_s=$CWALL frame_allowance_s=$FRAME_ALLOWANCE_S memavail_GiB=$MEMAVAIL_GIB memavail_pre_GiB=$MEMAVAIL_GIB memavail_post_GiB=$MEMAVAIL_POST cpuset=$CPUSET delivered_cores_mean=[$DELIVERED] siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] ceiling_hit=$CEILING_HIT log=$(basename "$LOG") stamp=$STAMP"
  grep -a "D4S_CONTAINER_UID\|D4S_IDWARP_SO_MD5\|D4S_DEADLINE_IN_CONTAINER_S\|D6RF_UNITS_PASS" "$LOG" | head -4
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc
