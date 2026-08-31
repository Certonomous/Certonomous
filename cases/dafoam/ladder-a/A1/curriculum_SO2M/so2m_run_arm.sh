#!/usr/bin/env bash
# Curriculum SO-1a arm launcher -- NACA0012 INCOMPRESSIBLE (DASimpleFoam)
# drag-min-at-fixed-lift, the FD-VERIFIED GRADIENT RUNG of Sanaa's shape-
# optimisation ladder SO-1.  TWO ROWS (shipped + patched), adjoint X + central-FD
# table F on BOTH the objective CD and the equality constraint CL.
#
# DERIVED from `cases/dafoam/ladder-a/A1/curriculum_D15/d15_run_arm.sh`
# (md5 796a2de5b894e8fcdbfab99af6fbf09d) with the REGISTERED DELTAS listed in
# PREREGISTRATION.md section 7 and recorded in so2m_run_arm_DELTAS_from_d15.diff:
# item/root names; the INCOMPRESSIBLE tutorial as the source; forbidden roots
# extended with D15's, D16's, D17's, AV-1's and AV-2's; RANKS 1 ON EVERY ARM
# (DAFOAM_CHARTER.md section 5, serial before parallel); cpuset 9; the cap table;
# the staged instruments; the arm commands.  Container-printed strings (D4S_*)
# are inherited UNCHANGED so the grader greps what the launcher writes.
#
# THE AGE-GUARD DATUM IS RESOLVED BY EXISTENCE HERE TOO, AND ITS NAME IS RECORDED.
# AV-1 and AV-2 both returned NOT A RESULT on 2026-08-27 with every physics
# artefact intact because a frozen grader pinned the datum to the NAME `0/U` while
# this tutorial's `writeCompression on` rewrites it as `0/U.gz` on a serial arm.
# This launcher resolves the datum over BOTH names and writes the one it used to
# `.so2m_age_datum_ref` beside the epoch, so the grader is not left inferring it.
#
# CAP DISCIPLINE (the failure this file exists not to repeat).  A peer lane
# today registered a 3.0 core-min cap and its launcher enforced 6.0 by
# copy-forward with no assertion.  Here the caps are NOT arguments.  They are
# constants in the table below, the table is reproduced verbatim in
# PREREGISTRATION.md §8, this file's md5 is frozen there, and the launcher
# ASSERTS that the wall timeout it is about to enforce equals CAP_CORE_MIN*60/RANKS
# to the second.  A cap that disagrees aborts the arm before the container runs.
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call and
# `( set -e; ... )` does not gate either.  Every step below gates explicitly
# with `|| { echo ABORT...; exit N; }`.
#
# 8.2: NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives
# the arm and the KERNEL's verdict is read, not the harness's.
set -uo pipefail

# ===========================================================================
# D4-LAUNCHER-DEF-1 -- THE DEFECT THIS FILE EXISTS NOT TO REPEAT.
#
# `curriculum_D4/d4_run_arm.sh` hardcodes BASE at the PATCHED item's run root
# (:25, no override), sets WORK="$BASE/$ARM" (:136) and runs an UNGUARDED
# `sudo -n rm -rf "$WORK"` (:139) for every arm except F.  Firing the SHIPPED
# row through it would have deleted
#   /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O
# -- 5,085 files, 384 MB, holding OptView.hst and opt_IPOPT.txt: THE ARTIFACTS
# D4's ACCEPTED `GATE REACHED` RESTS ON -- and appended its rows to the same
# ledger (:282), leaving two items interleaved in one file so that NEITHER row
# could be graded cleanly afterwards.  EIGHT launcher files in that directory
# carry the same hardcoded BASE.
#
# THE REPAIR IS NOT "CHANGE THE CONSTANT".  A constant that is merely different
# is one careless edit from being the same again.  The WRONG CONSTANT MUST
# REFUSE, and the guard below is DRIVEN AGAINST THE REAL D4 ROOT in
# `d4s_launcher_guard_selftest.sh` and shown to abort.  A guard not shown to
# fire is ceremony -- and this is the guard standing between a re-fire and
# 384 MB of irreplaceable graded evidence.
# ===========================================================================
ITEM=SO2M
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient
BASE="${BASE:-$REGISTERED_BASE}"

# ---- G-ROOT.1 -- BASE must be THIS item's registered root, normalised, so a
# ---- trailing slash, a `.`, a `..` or a symlink cannot walk around the check.
BASE_REAL=$(realpath -m "$BASE")
REG_REAL=$(realpath -m "$REGISTERED_BASE")
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
  echo "  given:      $BASE_REAL"
  echo "  registered: $REG_REAL"
  echo "  D4-LAUNCHER-DEF-1: a launcher pointed at another item's run root"
  echo "  deletes that item's graded arms.  REFUSED before any staging."
  exit 3
fi

# ---- G-ROOT.2 -- and NAME the roots that must never be written by this file,
# ---- so the abort says WHOSE evidence it just protected rather than only that
# ---- something did not match.  Explicit, because the specific message is what
# ---- a future reader in a hurry actually acts on.
FORBIDDEN_ROOTS="/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-R-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density
/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D14-a2-wing-remesh
/home/ubuntu/certonomous-runs/CURRICULUM-D14M-a2-wing-remesh
/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd
/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D13-a1-basin-restart
/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic
/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic
/home/ubuntu/certonomous-runs/CURRICULUM-D17-cone-supersonic
/home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv
/home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality
/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient
/home/ubuntu/certonomous-runs/CURRICULUM-SO1b-a1-naca0012-dragmin-opt
/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt
/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-postopt
/home/ubuntu/certonomous-runs/CURRICULUM-SO1cR-a1-naca0012-postopt
/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient
/home/ubuntu/certonomous-runs/CURRICULUM-SO3a-a1-naca0012-multipoint
/home/ubuntu/certonomous-runs/A2-mach-wing
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible
/home/ubuntu/dafoam-tutorials
/home/ubuntu/certonomous-runs
/home/ubuntu/Certonomous"
while IFS= read -r forb; do
  [ -z "$forb" ] && continue
  if [ "$BASE_REAL" = "$(realpath -m "$forb")" ]; then
    echo "ABORT G-ROOT.2 BASE resolves to ANOTHER ITEM'S RUN ROOT: $forb"
    echo "  That directory holds a graded row.  This launcher stages by"
    echo "  That launcher stages by removing the arm directory, so writing"
    echo "  there would destroy it.  REFUSED."
    exit 3
  fi
done <<< "$FORBIDDEN_ROOTS"

# ---- G-ROOT.3 -- the LEDGER must belong to this item and to no other.  A root
# ---- can be correct and its ledger still be a foreign one moved in.  D15
# ---- REGISTERED DELTA: this item BUYS BOTH ROWS, so a ROW=SHIPPED row is NOT
# ---- foreign here; only a foreign ITEM= line refuses.
if [ -f "$BASE/ledger.txt" ]; then
  FOREIGN_ITEM=$(grep -a "^ITEM=" "$BASE/ledger.txt" 2>/dev/null | grep -av "^ITEM=$ITEM$" | head -1)
  if [ -n "$FOREIGN_ITEM" ]; then
    echo "ABORT G-ROOT.3 the ledger at $BASE/ledger.txt carries another item: $FOREIGN_ITEM"
    echo "  Appending here would interleave two items' rows in one file and"
    echo "  neither row could be graded cleanly afterwards.  REFUSED."
    exit 3
  fi
fi
echo "D4S_G_ROOT_PASS item=$ITEM base=$BASE_REAL ledger_clean=yes"

# ---- REGISTERED CPU PLACEMENT (PREREGISTRATION.md §5b, verbatim) ---------
# `mpirun` inside a `--cpus=N` container binds rank 0 to the FIRST CORE OF THE
# HOST TOPOLOGY.  Concurrent containers then land on the same host core and
# throughput collapses as 1/N while the box reports itself idle -- MEASURED by
# the D13 lane 2026-08-25: affinity=0 on all three concurrent arms, 0.250 cores
# delivered against a 1.0-core quota, host 61 % idle, throughput moved 4x on a
# control that changed only the sibling count.  `--cpus=4` does NOT hand out
# four distinct cores.  So: PIN, and MEASURE the placement rather than infer it
# from the flag that was passed.
#
# SO-1a REGISTERED DELTA (PREREGISTRATION.md section 5): cpuset 9, ONE core,
# because every arm runs at np = 1.  DISCLOSED OVERLAP: 9 sits inside
# D4-SHIPPED's registered 5,6,7,9.  At np = 1 the grader's delivered-cores floor
# does not apply (so2m_grade.py g_placement: dl_ok is True when ARM_RANKS == 1),
# so an overlap costs WALL TIME and cannot fail G12 -- it is reported as a cost
# exposure in PREREGISTRATION.md section 4, never silently re-pinned.
CPUSET=9

# For containerised MPI the conditioning variable is CONCURRENT CONTAINERS, not
# loadavg -- `uptime` will lie.  Censused before and after every arm.
container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^so2m_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md §4, verbatim) ---------------
#   arm    ranks  core-min cap   in-container wall   memory cap
#   MESH     1        5.0            300 s              4g
#   X-S      1       12.0            720 s              4g
#   X-P      1       12.0            720 s              4g
#   G-S      1       25.0           1500 s              4g
#   G-P      1       25.0           1500 s              4g
# THE COMMENT AND THE OPERATIVE CONSTANTS BELOW AGREE, and the SELFTEST DRIVES
# that agreement against the FROZEN GRADER's CAPS table.  SO-2a shipped with this
# comment STALE at X 10.0 while its operative constant read 12.0; that was
# REPORTED rather than edited because its file was frozen.  Here it is correct at
# the freeze, and the five caps sum to the registered ceiling 79.0 (gate G10).
cap_core_min() {
  case "$1" in
    MESH)     echo 5.0 ;;
    X-S|X-P)  echo 12.0 ;;
    G-S|G-P)  echo 25.0 ;;
    *)  echo "" ;;
  esac
}
cap_memory() {
  case "$1" in
    MESH|X-S|X-P|G-S|G-P) echo 4g ;;
    *) echo "" ;;
  esac
}
# np = 1 ON EVERY ARM by registration: DAFOAM_CHARTER.md section 5 (serial before
# parallel), and A4's 16,600x decomposition effect is removed from the chain.
ranks_of() {
  case "$1" in
    MESH|X-S|X-P|G-S|G-P) echo 1 ;;
    *) echo "" ;;
  esac
}

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER §11) ---
# PATCHED IDWarp : dafoam-idwarp-rot:v1
#   sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
# SHIPPED (stock): dafoam/opt-packages:latest
#   sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc

# ---- FROZEN INSTRUMENT HASHES (PREREGISTRATION.md §7, verbatim) ----------
MD5_RUNSCRIPT=ae4a73429dd6972dc804b76d9a44aa05   # so2m_runScript.py = byte copy of the shipped INCOMPRESSIBLE tutorial runScript.py
MD5_XM=19c9eb89f6d12d93b22be96a65320650                                 # so2m_xm.py (RULING 1 repair 2026-08-31; was 2bf45db9197c49d37bed30e55f6ff2ef)
MD5_DECOMP=e6f1b0060944bc86d6dff56480ad2bd4      # so2m_decomposeParDict (numberOfSubdomains 1, scotch)

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: so2m_run_arm.sh <MESH|X-S|G-S|X-P|G-P> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: so2m_run_arm.sh <MESH|X-S|G-S|X-P|G-P> <image>"; exit 64; }
RANKS=$(ranks_of "$ARM"); test -n "$RANKS" || { echo "ABORT arm $ARM carries no registered rank count"; exit 64; }

# ---- G-ROOT.5 (ADDENDUM 2) -- A LIVE ARM IS NEVER RE-STAGED.  G-ROOT.1-.3
# ---- see only ledger rows; a queue-runner re-firing this launcher on a
# ---- RUNNING arm would pass them and reach `rm -rf "$WORK"` (the shape the
# ---- D7FR lane found at d7fr_run_arm.sh:319).  Two live readings, taken
# ---- BEFORE any destructive act:
# ----   (a) a RUNNING container carrying this item's prefix and this arm;
# ----   (b) a driver pidfile in the run root naming a LIVE pid that is not an
# ----       ancestor of this process (a second driver), or whose cwd is the
# ----       run root.  A stale pidfile (dead pid) does not block.
LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^so2m_${ARM}_" 2>/dev/null | grep "^so2m_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  echo "  Re-staging would remove the live arm directory under it.  REFUSED."
  exit 3
fi
PIDFILE="$BASE/so2m_driver.pid"
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
    if [ "$ANCESTOR" = "no" ] || [ "$DCWD" = "$(realpath -m "$BASE")" ]; then
      echo "ABORT G-ROOT.5 driver pidfile $PIDFILE names LIVE pid $DPID (ancestor_of_this_launcher=$ANCESTOR cwd=$DCWD)."
      echo "  Another driver owns this run root, or a process sits inside it.  REFUSED."
      exit 3
    fi
  fi
fi
echo "D4S_G_ROOT5_PASS arm=$ARM live_same_arm_containers=none driver_pidfile=$([ -f "$PIDFILE" ] && echo present_owner_is_ancestor_or_stale || echo absent)"

CAP=$(cap_core_min "$ARM")
MEM=$(cap_memory "$ARM")
test -n "$CAP" || { echo "ABORT unknown arm $ARM -- no registered cap"; exit 64; }
test -n "$MEM" || { echo "ABORT unknown arm $ARM -- no registered memory cap"; exit 64; }

# THE ASSERTION.  The enforced wall timeout is DERIVED from the registered
# core-minute cap and the registered rank count, and is then re-checked
# against that cap by inverting the arithmetic.  There is no second number
# anywhere in this file that could drift from the first.
TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)))") || { echo "ABORT tmo calc"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % ($TMO*$RANKS/60.0))") || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
cap, back = $CAP, $BACKCHECK
if abs(cap-back) > 0.02:
    sys.stderr.write('ABORT CAP MISMATCH registered=%r enforced=%r\n' % (cap, back)); sys.exit(1)
" || { echo "ABORT enforced cap != registered cap"; exit 65; }
echo "D4_CAP_ASSERT arm=$ARM registered_core_min=$CAP ranks=$RANKS enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM"

# ---- host state, read before ranks are claimed ---------------------------
MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D4_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 run root mode $(stat -c '%a' "$BASE")"; exit 4; }

# ---- staged-instrument identity, re-asserted before EVERY launch ---------
echo "$MD5_RUNSCRIPT  $BASE/so2m_runScript.py"       | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_XM  $BASE/so2m_xm.py"                     | md5sum -c - || { echo "ABORT xf md5"; exit 4; }
echo "$MD5_DECOMP  $BASE/base/system/decomposeParDict" | md5sum -c - || { echo "ABORT decomposeParDict md5"; exit 4; }

# ---- image identity by DIGEST, resolved from the local store -------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1)    WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  dafoam/opt-packages:latest) WANT=$IMG_SHIPPED_DIGEST; ROW=SHIPPED ;;
  *) echo "ABORT image $IMG is not a registered row"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }

# ---- G-ROW.  THE ROW A RUN CLAIMS AND THE ROW IT RAN MUST BE THE SAME HASH.
# DAFOAM_CHARTER.md §11 makes the HASH the identity.  D15 REGISTERED DELTA: the
# row is carried in the ARM NAME (-S shipped, -P patched; MESH on shipped --
# mesh generation does not touch IDWarp), and a mismatch refuses.
case "$ARM" in
  MESH|*-S) WANT_ROW=SHIPPED ;;
  *-P)      WANT_ROW=PATCHED ;;
  *)        WANT_ROW="" ;;
esac
test "$ROW" = "$WANT_ROW" || {
  echo "ABORT G-ROW arm $ARM is registered on the $WANT_ROW row; got ROW=$ROW ($IMG)."
  echo "  A row a run claims and a row it ran must be the same hash.  REFUSED."
  exit 4; }
echo "D4S_G_ROW_PASS row=$ROW digest=$GOT_DIGEST"
echo "D4_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="so2m_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- stage a pristine copy for the arm ------------------------------------
# D15 REGISTERED DELTA: MESH stages from base/ (the tutorial's inputs, no mesh);
# every solver arm stages a COLD copy of the MESH arm's OUTPUT (mesh + 0/), so
# all four gradient arms run on ONE mesh generated once inside the SHIPPED image.
if [ "$ARM" = "MESH" ]; then
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/base" "$WORK" || { echo "ABORT stage copy"; exit 4; }
  test -e "$WORK/constant/polyMesh" && { echo "ABORT G-COLD MESH: base/ already carries constant/polyMesh"; exit 5; }
  test -e "$WORK/0" && { echo "ABORT G-COLD MESH: base/ already carries 0/"; exit 5; }
  # DATUM BY EXISTENCE (AV-1/AV-2, 2026-08-27): accept either registered name and
  # RECORD the one used, so the grader is not left inferring it from a hard-coded
  # string that `writeCompression on` can invalidate.
  if   [ -f "$WORK/0.orig/U" ];    then DATUM_NAME=0.orig/U
  elif [ -f "$WORK/0.orig/U.gz" ]; then DATUM_NAME=0.orig/U.gz
  else echo "ABORT G-COLD neither 0.orig/U nor 0.orig/U.gz is present"; exit 5; fi
  touch "$WORK/0.orig"/* || { echo "ABORT age-guard datum"; exit 5; }
  AGE_DATUM=$(stat -c '%Y' "$WORK/$DATUM_NAME")
  echo "$AGE_DATUM" > "$WORK/.so2m_age_datum"
  echo "$DATUM_NAME" > "$WORK/.so2m_age_datum_ref"
  echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM datum_file=$DATUM_NAME resolved_by=EXISTENCE"
else
  test -d "$BASE/MESH" || { echo "ABORT arm $ARM expects an existing MESH/ from arm MESH"; exit 5; }
  test -f "$BASE/MESH/constant/polyMesh/boundary" || { echo "ABORT arm $ARM: MESH/ carries no constant/polyMesh/boundary"; exit 5; }
  { [ -f "$BASE/MESH/0/U" ] || [ -f "$BASE/MESH/0/U.gz" ]; } || { echo "ABORT arm $ARM: MESH/ carries neither 0/U nor 0/U.gz"; exit 5; }
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/MESH" "$WORK" || { echo "ABORT stage copy from MESH"; exit 4; }
  rm -f "$WORK/so2m_cmd.sh" "$WORK/checkMesh.log" "$WORK/logMeshGeneration.txt" "$WORK/volumeMesh.xyz" "$WORK/surfaceMesh.xyz" "$WORK/.so2m_age_datum" "$WORK/.so2m_age_datum_ref" 2>/dev/null
  cp -a "$BASE/so2m_runScript.py" "$BASE/so2m_xm.py" "$WORK/" || { echo "ABORT stage instruments"; exit 4; }
  # COLD START, verified BEFORE the launch (D2 G8), and the AGE GUARD's datum:
  # 0/ is touched LAST at stage time, so every artifact the run produces must
  # be strictly newer than 0/U or it did not come from this run.
  for bad in "$WORK/reports" "$WORK/so2m_X.json" "$WORK/so2m_F.json" "$WORK/so2m_F.jsonl" "$WORK/so2m_X.jsonl" "$WORK/dRdWColoring_2.bin"; do
    test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
  done
  test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
  for d in "$WORK"/*/; do
    n=$(basename "$d")
    case "$n" in 0|0.orig) ;; [0-9]*) echo "ABORT G-COLD time dir present: $n"; exit 5 ;; esac
  done
  if   [ -f "$WORK/0/U" ];    then DATUM_NAME=0/U
  elif [ -f "$WORK/0/U.gz" ]; then DATUM_NAME=0/U.gz
  else echo "ABORT G-COLD neither 0/U nor 0/U.gz is present"; exit 5; fi
  touch "$WORK/0"/* || { echo "ABORT age-guard datum"; exit 5; }
  AGE_DATUM=$(stat -c '%Y' "$WORK/$DATUM_NAME")
  echo "$AGE_DATUM" > "$WORK/.so2m_age_datum"
  echo "$DATUM_NAME" > "$WORK/.so2m_age_datum_ref"
  echo "SO2M_WRITE_COMPRESSION $(grep -a writeCompression "$WORK/system/controlDict" 2>/dev/null | head -1 | tr -d ';')"
  echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM datum_file=$DATUM_NAME resolved_by=EXISTENCE"
fi

case "$ARM" in
  MESH)     CMD="bash preProcessing.sh && checkMesh > checkMesh.log 2>&1; echo SO2M_CHECKMESH_RC \$?; sha256sum constant/polyMesh/points* ; grep -a 'cells:' checkMesh.log" ;;
  X-S|X-P)  CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python so2m_xm.py -mode X" ;;
  G-S|G-P)  CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python so2m_xm.py -mode G" ;;
esac

# ---- ADDENDUM 2: the arm command goes to a FILE the container executes under
# ---- its OWN `timeout` at the registered cap wall (TMO), so the deadline is
# ---- INSIDE the container and survives every host shell.  `-k 60` escalates
# ---- TERM to KILL; the kernel exit code (124/137) is then the record.
CMDFILE="$WORK/so2m_cmd.sh"
printf '%s\n' "$CMD" > "$CMDFILE" || { echo "ABORT cmd file"; exit 4; }
echo "D4S_CMDFILE arm=$ARM md5=$(md5sum "$CMDFILE" | cut -d' ' -f1) deadline_in_container_s=$TMO"
CPUSAMPLE="$BASE/${ARM}_${STAMP}.cpu.jsonl"
# DELIVERED CORES ARE MEASURED, NOT INFERRED FROM THE QUOTA FLAG.  This sampler
# polls the container's own cgroup cpu.stat and writes cores-delivered to a
# FILE.  It is a passive reader: it starts nothing, kills nothing, and its
# failure cannot change a verdict -- an absent sample file is reported as
# NOT_MEASURED, never as a passing placement gate.
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
import json,sys
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
# ===========================================================================
# rc CAPTURE IS CLOSED: `rc` is read from `docker inspect .State.ExitCode`,
# the KERNEL'S OWN RECORD; `.State.OOMKilled` from the SAME inspect; NO --rm
# until the record is read.  THE CAP LIVES INSIDE THE CONTAINER: `timeout -k 60
# $TMO` wraps the arm command file on the `docker run` line below, so the
# deadline survives every host shell (the D4-SHIPPED Addendum 2 form, inherited
# from d5_run_arm.sh unchanged).  The host poller REPORTS a crossing and
# hard-stops only at 4x cap, while this shell lives.
# ===========================================================================
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4S_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4S_IDWARP_IMPORTED_FROM:\",p); print(\"D4S_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     echo D4S_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k 60 $TMO bash /mnt/$ARM/so2m_cmd.sh" > /dev/null 2>&1 \
  || { echo "ABORT could not start container"; exit 4; }

# The cap is a RUNAWAY GUARD THAT REPORTS (Sanaa, 2026-08-25), not a budget
# rigor is trimmed to fit.  A crossing is written to the ledger and CONTINUES;
# the supervisor decides.  CEILING = 4 x CAP is a hard stop so a genuine
# runaway is still bounded -- WHILE THIS SHELL LIVES (the in-container timeout
# is the cap that survives shell death).
CEILING=$(python3 -c "print('%.1f' % (4.0*$CAP))")
echo "D4S_RUNAWAY_GUARD arm=$ARM cap_core_min=$CAP ceiling_core_min=$CEILING mode=report_then_stop_at_ceiling"
CAP_REPORTED=no; CEILING_HIT=no
while true; do
  RUNNING=$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)
  NOW=$(date -u +%s); EL=$((NOW-T0))
  CM=$(python3 -c "print(round($EL*$RANKS/60.0,3))")
  if [ "$RUNNING" != "true" ]; then break; fi
  if [ "$CAP_REPORTED" = "no" ] && [ "$(python3 -c "print(1 if $CM > $CAP else 0)")" = "1" ]; then
    CAP_REPORTED=yes
    echo "D4S_CAP_CROSSED arm=$ARM core_min=$CM cap=$CAP ceiling=$CEILING action=REPORTED_RUN_CONTINUES supervisor_decides" | tee -a "$BASE/ledger.txt"
  fi
  if [ "$(python3 -c "print(1 if $CM > $CEILING else 0)")" = "1" ]; then
    CEILING_HIT=yes
    echo "D4S_CEILING_HIT arm=$ARM core_min=$CM ceiling=$CEILING action=HARD_STOP" | tee -a "$BASE/ledger.txt"
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
v=[]
thr=0
for line in open(p):
    try: d=json.loads(line)
    except Exception: continue
    if d.get('delivered_cores') is not None: v.append(d['delivered_cores'])
    thr=max(thr, d.get('nr_throttled') or 0)
print('%s n=%d max_nr_throttled=%d' % (('%.4f'%(sum(v)/len(v)) if v else 'NOT_MEASURED'), len(v), thr))
" 2>/dev/null)

# ---- the KERNEL's verdict, read BEFORE the container is removed (8.2) ----
INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
echo "$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.StartedAt}} {{.State.FinishedAt}} {{.HostConfig.CpusetCpus}} {{.HostConfig.Memory}}' "$NAME" 2>/dev/null) $GOT_DIGEST" > "$BASE/${ARM}_${STAMP}.inspect.txt"   # the surviving kernel record (the grader's L-342 fallback)
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$WORK" 2>/dev/null

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/ledger.txt"
{
  echo "ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM inspect(exit,oomkilled)=[$INSPECT] memavail_pre_GiB=$MEMAVAIL_GIB memavail_post_GiB=$MEMAVAIL_POST cpuset=$CPUSET delivered_cores_mean=[$DELIVERED] siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] log=$(basename "$LOG") stamp=$STAMP"
  grep -a "D4S_CONTAINER_UID\|D4S_IDWARP_SO_MD5\|D4S_DEADLINE_IN_CONTAINER_S" "$LOG" | head -3   # the strings the container prints
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc
