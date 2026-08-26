#!/usr/bin/env bash
# Curriculum D8R arm launcher -- A6 CRM wing-alone N=16, twist-only constrained drag
# minimisation TO CONVERGENCE, TWO ROWS (patched first, then shipped): optimisation
# arm O + endpoint central-FD table F per row.
#
# DERIVED from `cases/dafoam/ladder-a/A1/curriculum_D16/d16_run_arm.sh` (itself
# derived from D15's and D5's) with the REGISTERED DELTAS listed in PREREGISTRATION.md
# section 7 and recorded in d8r_run_arm_DELTAS_from_d16.diff (item names; NO MESH arm --
# every arm stages cold from D8's frozen mesh in base/; arms O-P F-P O-S F-S at 4 ranks;
# cpuset 0,1,12,15; the cap/memory table O 1000.0 / 14g, F 120.0 / 6g; the F arm
# consumes the same row's O endpoint; D8's, D16's and D17's roots forbidden); the D5 lineage:
# item/root names; forbidden roots; G-ROOT.3 accepts BOTH rows (this item BUYS
# both); arms MESH X-S F-S X-P F-P; RANKS 2 (MESH 1); cpuset 2,3; 4g; cap table;
# G-ROW derived from the arm suffix; the staged instruments; solver arms stage
# from the MESH arm's output; the arm commands.  Container-printed strings
# (D4S_*) are inherited UNCHANGED so the grader greps what the launcher writes.
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
ITEM=D8R
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv
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
/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt
/home/ubuntu/certonomous-runs/P2-a6-n16
/home/ubuntu/certonomous-runs/P3-a6-n16-ref
/home/ubuntu/certonomous-runs/P3-a6-n16-rem
/home/ubuntu/certonomous-runs/A2-mach-wing
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/transonic
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
# ---- can be correct and its ledger still be a foreign one moved in.  D8R
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
# D8R REGISTERED DELTA (PREREGISTRATION.md section 5): cpuset 0,1,12,15 -- the
# dafoam-supervisor's FIFTEENTH-session placement ("choose 4 ranks on 0,1,12,15 and
# disclose"); DISJOINT from D5 8,10,11,13, D4-SHIPPED 5,6,7,9, D15 2,3, D16 4,14,
# D6 2,3,4,14; INCLUDES core 0 and OVERLAPS D17's 12,15 -- both disclosed; the chain
# driver's G-CPUSET wait-and-retry refuses to start an arm while a live container
# shares a core.
CPUSET=0,1,12,15

# For containerised MPI the conditioning variable is CONCURRENT CONTAINERS, not
# loadavg -- `uptime` will lie.  Censused before and after every arm.
container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d8r_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md §4, verbatim) ---------------
#   arm    ranks  core-min cap   in-container wall   memory cap
#   O-P      4     1000.0          15000 s             14g   (carries the adjoint; D8 peak 9.97 GiB at np=1)
#   O-S      4     1000.0          15000 s             14g
#   F-P      4      120.0           1800 s              6g   (primals only)
#   F-S      4      120.0           1800 s              6g
# THE DEADLINE IS THE CAP WALL, and the cap was sized so the registered work fits
# inside it (D5-PREREG-DEF-1 / D4S-LAUNCHER-DEF-2 class): MAX_ITER 30 majors at D8's
# measured 888 s/major (np=1, LANE_REPORT.md section 8) scaled to 4 ranks at 50 %
# efficiency = 444 s/major -> 13,320 s + set-up < 15,000 s.
cap_core_min() {
  case "$1" in
    O-S|O-P)  echo 1000.0 ;;
    F-S|F-P)  echo 120.0 ;;
    *)  echo "" ;;
  esac
}
cap_memory() {
  case "$1" in
    O-S|O-P) echo 14g ;;
    F-S|F-P) echo 6g ;;
    *) echo "" ;;
  esac
}
ranks_of() {
  case "$1" in
    O-S|O-P|F-S|F-P) echo 4 ;;
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
MD5_RUNSCRIPT=28c7819487a025a5f6554d38062a2b66   # d8r_runScript.py = byte copy of D8's frozen arm runScript.py (opt/, d8_gen_arm.py output)
MD5_XF=5a399b427331ab8eab1fcdc1a243b3aa                                 # d8r_of.py (set at freeze)
MD5_DECOMP=1dbd9ead3f40a29f483444dc5fa1288b      # d8r_decomposeParDict (numberOfSubdomains 4, scotch; = D8 base's)
MD5_POINTS=11b84f0de5fdf2d3e947fee8cea412a9      # D8's frozen constant/polyMesh/points.gz (D8 PREREGISTRATION.md section 9)

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: d8r_run_arm.sh <O-P|F-P|O-S|F-S> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: d8r_run_arm.sh <O-P|F-P|O-S|F-S> <image>"; exit 64; }
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
LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d8r_${ARM}_" 2>/dev/null | grep "^d8r_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  echo "  Re-staging would remove the live arm directory under it.  REFUSED."
  exit 3
fi
PIDFILE="$BASE/d8r_driver.pid"
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
echo "$MD5_RUNSCRIPT  $BASE/d8r_runScript.py"       | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_XF  $BASE/d8r_of.py"                     | md5sum -c - || { echo "ABORT of md5"; exit 4; }
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
# DAFOAM_CHARTER.md §11 makes the HASH the identity.  D16 REGISTERED DELTA (kept): the
# row is carried in the ARM NAME (-S shipped, -P patched; no MESH arm here), and a
# mismatch refuses.
case "$ARM" in
  *-S) WANT_ROW=SHIPPED ;;
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
NAME="d8r_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- stage a pristine copy for the arm ------------------------------------
# D8R REGISTERED DELTA: there is NO MESH arm -- the mesh is D8's frozen A6 N=16 mesh,
# staged read-only into base/ by the chain driver (points.gz md5 asserted).  EVERY arm
# stages a COLD copy of base/ (0/ present, constant/polyMesh present, no time dir, no
# processor*).  An F arm additionally needs the SAME ROW's O-arm artefact, copied in
# as d8r_O_endpoint.json; it REFUSES without it.
test -d "$BASE/base" || { echo "ABORT arm $ARM expects a staged base/ (the driver stages it on the first fire)"; exit 5; }
test -f "$BASE/base/constant/polyMesh/points.gz" || { echo "ABORT base/ carries no constant/polyMesh/points.gz"; exit 5; }
test -f "$BASE/base/0/U" || { echo "ABORT base/ carries no 0/U"; exit 5; }
echo "$MD5_POINTS  $BASE/base/constant/polyMesh/points.gz" | md5sum -c - || { echo "ABORT base mesh md5 (G-M2 at staging)"; exit 4; }
case "$ARM" in
  F-*) OARM="O-${ARM#F-}"
       test -f "$BASE/$OARM/d8r_O.json" || { echo "ABORT arm $ARM expects $OARM/d8r_O.json (the same row's optimisation endpoint)"; exit 5; }
       grep -aq "^ARM=$OARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null || { echo "ABORT arm $ARM: $OARM has no rc=0 ledger row"; exit 5; } ;;
esac
sudo -n rm -rf "$WORK" 2>/dev/null
cp -a "$BASE/base" "$WORK" || { echo "ABORT stage copy from base"; exit 4; }
rm -f "$WORK/runScript.py" "$WORK/logMeshGeneration.txt" "$WORK/volumeMesh.xyz" "$WORK/surfMesh.cgns" "$WORK/CRM_surfMesh.cgns.tar.gz" "$WORK/genWingMesh.py" "$WORK/preProcessing.sh" "$WORK/Allclean.sh" 2>/dev/null
cp -a "$BASE/d8r_runScript.py" "$BASE/d8r_of.py" "$WORK/" || { echo "ABORT stage instruments"; exit 4; }
case "$ARM" in
  F-*) cp -a "$BASE/$OARM/d8r_O.json" "$WORK/d8r_O_endpoint.json" || { echo "ABORT copy endpoint"; exit 4; }
       echo "D8R_ENDPOINT_STAGED arm=$ARM from=$OARM md5=$(md5sum "$WORK/d8r_O_endpoint.json" | cut -d' ' -f1)" ;;
esac
# COLD START, verified BEFORE the launch (D2 G8), and the AGE GUARD's datum:
# 0/ is touched LAST at stage time, so every artifact the run produces must
# be strictly newer than 0/U or it did not come from this run.
for bad in "$WORK/reports" "$WORK/d8r_O.json" "$WORK/d8r_F.json" "$WORK/d8r_F.jsonl" "$WORK/d8r_O.jsonl" "$WORK/OptView.hst" "$WORK/opt_IPOPT.txt" "$WORK/dRdWColoring_1.bin" "$WORK/dRdWColoring_4.bin"; do
  test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
done
test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
for d in "$WORK"/*/; do
  n=$(basename "$d")
  case "$n" in 0|0.orig) ;; [0-9]*) echo "ABORT G-COLD time dir present: $n"; exit 5 ;; esac
done
test -f "$WORK/0/U" || { echo "ABORT G-COLD 0/U missing"; exit 5; }
touch "$WORK/0"/* || { echo "ABORT age-guard datum"; exit 5; }
AGE_DATUM=$(stat -c '%Y' "$WORK/0/U")
echo "$AGE_DATUM" > "$WORK/.d8r_age_datum"
echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM datum_file=0/U"

case "$ARM" in
  O-S|O-P)  CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d8r_of.py -mode O" ;;
  F-S|F-P)  CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d8r_of.py -mode F" ;;
esac

# ---- ADDENDUM 2: the arm command goes to a FILE the container executes under
# ---- its OWN `timeout` at the registered cap wall (TMO), so the deadline is
# ---- INSIDE the container and survives every host shell.  `-k 60` escalates
# ---- TERM to KILL; the kernel exit code (124/137) is then the record.
CMDFILE="$WORK/d8r_cmd.sh"
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
     timeout -k 60 $TMO bash /mnt/$ARM/d8r_cmd.sh" > /dev/null 2>&1 \
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
