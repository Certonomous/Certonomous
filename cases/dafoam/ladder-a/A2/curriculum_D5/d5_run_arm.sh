#!/usr/bin/env bash
# Curriculum D4 arm launcher -- MACH wing constrained CD minimisation at fixed CL.
#
# Derived from `cases/dafoam/ladder-a/A1/curriculum_D2/d2_run_arm.sh` (this
# family's proven container pattern) with the registered changes: D4's own run
# root, np=4 instead of np=1, a per-arm CAP TABLE that is INTERNAL to this file,
# and a decomposition-determinism arm.
#
# CAP DISCIPLINE (the failure this file exists not to repeat).  A peer lane
# today registered a 3.0 core-min cap and its launcher enforced 6.0 by
# copy-forward with no assertion.  Here the caps are NOT arguments.  They are
# constants in the table below, the table is reproduced verbatim in
# PREREGISTRATION.md §8, this file's md5 is frozen there, and the launcher
# ASSERTS that the wall timeout it is about to enforce equals CAP_CORE_MIN*60/4
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
ITEM=D5
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density
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
/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D14-a2-wing-remesh
/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady"
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
# ---- can be correct and its ledger still be a foreign one moved in; the row
# ---- format carries ROW=PATCHED|SHIPPED, so a PATCHED row in this item's
# ---- ledger is proof the two have been interleaved.
if [ -f "$BASE/ledger.txt" ]; then
  FOREIGN_ITEM=$(grep -a "^ITEM=" "$BASE/ledger.txt" 2>/dev/null | grep -av "^ITEM=$ITEM$" | head -1)
  if [ -n "$FOREIGN_ITEM" ]; then
    echo "ABORT G-ROOT.3 the ledger at $BASE/ledger.txt carries another item: $FOREIGN_ITEM"
    echo "  Appending here would interleave two items' rows in one file and"
    echo "  neither row could be graded cleanly afterwards.  REFUSED."
    exit 3
  fi
  if grep -aq "ROW=SHIPPED" "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT G-ROOT.3 the ledger at $BASE/ledger.txt already carries SHIPPED rows."
    echo "  This launcher writes the PATCHED row only (D5 REGISTERED DELTA: the graded D4 row).  REFUSED."
    exit 3
  fi
fi
echo "D4S_G_ROOT_PASS item=$ITEM base=$BASE_REAL ledger_clean=yes"
RANKS=4

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
# Cores 5,6,7,9 were measured idle at freeze time (2026-08-25 ~17:45Z) and
# 5,6,7 sit OUTSIDE the host-affinity mask 8-15 of the only live sibling
# container (d8_opt, A6 CRM, 1.0-core quota).  Cores 1,2,3,4,8,12,14 carried
# native peer load and 0 is the default landing core the defect names.
# D5 REGISTERED DELTA (PREREGISTRATION.md section 5b): 8,10,11,13 -- DISJOINT from every
# live container cpuset read via docker inspect at freeze (W2R on 12), from the D4-SHIPPED
# registered set 5,6,7,9 (its chain may be re-fired there) and from D6's 2,3,4,14.
CPUSET=8,10,11,13

# For containerised MPI the conditioning variable is CONCURRENT CONTAINERS, not
# loadavg -- `uptime` will lie.  Censused before and after every arm.
container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d4_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md §8, verbatim) ---------------
#   arm   core-min cap    memory cap
#   P1        5.0             4g
#   P2       55.0            12g
#   O       620.0            12g
#   F       120.0            12g
# D5 REGISTERED CAP TABLE (PREREGISTRATION.md section 4): per density d in {48,192}
cap_core_min() {
  # D5 ADDENDUM 3 (pre-compute for the r3 re-fire, 2026-08-26): ACC48/ACC192
  # 10.0 -> 60.0 core-min (deadline 150 s -> 900 s at 4 ranks).  ACC48 r2 was
  # cut by its own in-container deadline at 162 s while still colouring the
  # Jacobian (rc=124, 10.8 core-min WASTE, C-row in docs/COST_CALIBRATION.md):
  # the 10.0 anchor (D4 ACC, C-94) priced a 45 s acceptance primal, not
  # compute_totals on 48 FFD DVs (D5-PREREG-DEF-1, the D4S-LAUNCHER-DEF-2
  # class).  The 10.0 row is STRUCK; every other cap is unmoved.
  case "$1" in
    O48|O192)     echo 800.0 ;;
    ACC48|ACC192) echo 60.0 ;;
    F48|F192)     echo 120.0 ;;
    *)  echo "" ;;
  esac
}
cap_memory() {
  # D5 ADDENDUM 1 (pre-compute, 2026-08-26): EVERY arm 12g, never 8g -- the
  # D4-SHIPPED ACC arm (compute_totals, the same shape as ACC48/ACC192) was
  # OOM-killed by its 8g container cgroup (rc=137 at 16:56:28Z); the 8g row
  # in the table above is STRUCK by that addendum.
  case "$1" in
    O48|O192|ACC48|ACC192|F48|F192) echo 12g ;;
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

# ---- FROZEN INSTRUMENT HASHES (PREREGISTRATION.md §9, verbatim) ----------
MD5_RUNSCRIPT=fa1d91c82d11aacd0ae072652b346952
# D5 REGISTERED FFD MD5S (one per density; set at freeze from d5_gen_ffd.py output)
md5_ffd() { case "$1" in 48) echo 85a8bcd5d39f1b11a612ac0a39aee776 ;; 192) echo 8eb161df4c546d10d7fcb30132f58907 ;; *) echo "" ;; esac; }
MD5_FD=91b9f3526a39cb02eafbd5be504d7107   # d5_fd_endpoint.py (D5 REGISTERED DELTA: D4's FD instrument re-pointed at d5_opt_runScript.py)
MD5_EXTRACT=ee7d3c99fd716da23779cb651961918e

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: d5_run_arm.sh <O48|ACC48|F48|O192|ACC192|F192> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: d5_run_arm.sh <O48|ACC48|F48|O192|ACC192|F192> <image>"; exit 64; }
DENS="${ARM//[A-Z]/}"; case "$DENS" in 48|192) ;; *) echo "ABORT arm $ARM carries no registered density (48|192)"; exit 64;; esac

# ---- G-ROOT.5 (ADDENDUM 2) -- A LIVE ARM IS NEVER RE-STAGED.  G-ROOT.1-.3
# ---- see only ledger rows; a queue-runner re-firing this launcher on a
# ---- RUNNING arm would pass them and reach `rm -rf "$WORK"` (the shape the
# ---- D7FR lane found at d7fr_run_arm.sh:319).  Two live readings, taken
# ---- BEFORE any destructive act:
# ----   (a) a RUNNING container carrying this item's prefix and this arm;
# ----   (b) a driver pidfile in the run root naming a LIVE pid that is not an
# ----       ancestor of this process (a second driver), or whose cwd is the
# ----       run root.  A stale pidfile (dead pid) does not block.
LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d5_${ARM}_" 2>/dev/null | grep "^d5_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  echo "  Re-staging would remove the live arm directory under it.  REFUSED."
  exit 3
fi
PIDFILE="$BASE/d5_driver.pid"
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
echo "$MD5_RUNSCRIPT  $BASE/d5_opt_runScript.py"    | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_FD  $BASE/d5_fd_endpoint.py"             | md5sum -c - || { echo "ABORT fd md5"; exit 4; }
echo "$MD5_EXTRACT  $BASE/d4_extract_endpoint.py"   | md5sum -c - || { echo "ABORT extract md5"; exit 4; }

# ---- image identity by DIGEST, resolved from the local store -------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1)    WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  dafoam/opt-packages:latest) WANT=$IMG_SHIPPED_DIGEST; ROW=SHIPPED ;;
  *) echo "ABORT image $IMG is not a registered row"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }

# ---- G-ROW.  THIS ITEM BUYS THE SHIPPED ROW AND ONLY THE SHIPPED ROW. -----
# DAFOAM_CHARTER.md §11 makes the HASH the identity, so the row a run CLAIMS
# and the row it RAN must be the same hash or it does not run.  The patched
# row is already bought (curriculum_D4); re-running it here would put a second,
# younger record beside a graded one for the same question.
test "$ROW" = "PATCHED" || {
  echo "ABORT G-ROW D5 is registered PATCHED-ONLY (the row D4 was GRADED on, C-97); got ROW=$ROW ($IMG)."
  echo "  The SHIPPED row is NOT bought here; a second row is a separate item."
  exit 4; }
echo "D4S_G_ROW_PASS row=$ROW digest=$GOT_DIGEST"
echo "D4_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d5_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- stage a pristine copy of base/ for arms that need a cold case -------
if [ "${ARM:0:1}" != "F" ]; then
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/base" "$WORK" || { echo "ABORT stage copy"; exit 4; }
  cp -a "$BASE/d5_opt_runScript.py" "$BASE/d5_fd_endpoint.py" "$BASE/d4_extract_endpoint.py" "$WORK/" || { echo "ABORT stage instruments"; exit 4; }
  # D5 REGISTERED DELTA: the density's FFD box REPLACES base/FFD/wingFFD.xyz in the staged arm, md5-asserted
  echo "$(md5_ffd "$DENS")  $BASE/ffd/wingFFD_${DENS}.xyz" | md5sum -c - || { echo "ABORT FFD md5 for density $DENS"; exit 4; }
  cp -a "$BASE/ffd/wingFFD_${DENS}.xyz" "$WORK/FFD/wingFFD.xyz" || { echo "ABORT stage FFD"; exit 4; }
  echo "D5_FFD_STAGED arm=$ARM density=$DENS md5=$(md5sum "$WORK/FFD/wingFFD.xyz" | cut -d' ' -f1)"
  # COLD START, verified BEFORE the launch (D2 G8), and the AGE GUARD's datum:
  # 0/ is touched LAST at stage time, so every artifact the run produces must
  # be strictly newer than 0/U or it did not come from this run.
  for bad in "$WORK/reports" "$WORK/OptView.hst" "$WORK/opt_IPOPT.txt" "$WORK/dRdWColoring_4.bin" "$WORK/d5_fd_endpoint.json"; do
    test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
  done
  test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
  test -n "$(ls -d "$WORK"/[0-9]*.[0-9]* 2>/dev/null)" && { echo "ABORT G-COLD time dir present"; exit 5; }
  test -f "$WORK/0/U" || { echo "ABORT G-COLD 0/U missing"; exit 5; }
  touch "$WORK/0"/* || { echo "ABORT age-guard datum"; exit 5; }
  AGE_DATUM=$(stat -c '%Y' "$WORK/0/U")
  echo "$AGE_DATUM" > "$WORK/.d4_age_datum"
  echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM"
else
  WORK="$BASE/O${DENS}"
  test -d "$WORK" || { echo "ABORT arm $ARM expects an existing $WORK from arm O${DENS}"; exit 5; }
  test -f "$WORK/OptView.hst" || { echo "ABORT arm F: no OptView.hst to read an endpoint from"; exit 5; }
  cp -a "$BASE/d5_fd_endpoint.py" "$BASE/d4_extract_endpoint.py" "$WORK/" || { echo "ABORT stage F instruments"; exit 4; }
  rm -f "$WORK/d5_fd_endpoint.json" "$WORK/d5_fd_endpoint.jsonl" "$WORK/d4_endpoint_dvs.json" "$WORK/d4_major_history.json"
fi

# ---- D5 ADDENDUM 4 (2026-08-27), D5-LAUNCHER-DEF-1 -------------------------------
# THE CONTAINER'S WORKING DIRECTORY IS $WORK, NEVER $ARM.  For O/ACC arms the two
# coincide, because WORK="$BASE/$ARM" at :277.  For an F arm they DO NOT: PREREGISTRATION.md
# sec.2 REGISTERS the F arm's run directory as `O<density>/` -- "F runs in the O directory,
# the frozen F3 path" -- and the else-branch above reassigns WORK="$BASE/O${DENS}"
# accordingly.  The container line then used `-w /mnt/$ARM` and `bash /mnt/$ARM/d5_cmd.sh`,
# i.e. /mnt/F48, a directory THIS LAUNCHER NEVER CREATES (the cold-stage block is guarded
# by `[ "${ARM:0:1}" != "F" ]`).  Docker created it, empty and root-owned, through the
# `-v "$BASE":/mnt` bind, and the arm command file -- correctly written to O48/ and its md5
# correctly printed -- was not in it.  rc=127, 0.733 core-min, 2026-08-27T13:48:25Z.
# The registration was right and the launcher was wrong; the launcher is what changed.
WORKNAME="$(basename "$WORK")"
[ "$WORK" = "$BASE/$WORKNAME" ] || { echo "ABORT D5-LAUNCHER-DEF-1 WORK=$WORK is not directly under BASE=$BASE, so /mnt/$WORKNAME is not its path inside the container"; exit 4; }
[ -d "$WORK" ] || { echo "ABORT D5-LAUNCHER-DEF-1 WORK=$WORK does not exist on the host; the container would CREATE it empty and the arm command file would not be in it"; exit 4; }
echo "D5_WORKDIR arm=$ARM host_workdir=$WORK container_workdir=/mnt/$WORKNAME cmdfile=$WORK/d5_cmd.sh"

case "$ARM" in
  O48|O192)  CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d5_opt_runScript.py -task run_driver -optimizer IPOPT" ;;
  ACC48|ACC192) CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d5_opt_runScript.py -task compute_totals" ;;
  F48|F192) CMD="python d4_extract_endpoint.py && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d5_fd_endpoint.py" ;;
esac

# ---- ADDENDUM 2: the arm command goes to a FILE the container executes under
# ---- its OWN `timeout` at the registered cap wall (TMO), so the deadline is
# ---- INSIDE the container and survives every host shell.  `-k 60` escalates
# ---- TERM to KILL; the kernel exit code (124/137) is then the record.
CMDFILE="$WORK/d5_cmd.sh"
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
# WHAT `-d` + THE POLLER ACTUALLY CLOSES, AND WHAT IT DOES NOT.  STATED HERE
# BECAUSE A FROZEN DOCUMENT MUST NOT CARRY A FALSE LINE.
#
#   CLOSED -- rc CAPTURE.  `rc` is read from `docker inspect .State.ExitCode`,
#   the KERNEL'S OWN RECORD, which is what curriculum_D4/PREREGISTRATION.md
#   :256-257 registered and which only A3/curriculum_D7R/d7r_run_arm.sh ever
#   implemented.  `.State.OOMKilled` comes from the SAME inspect.  NO --rm, so
#   the record survives the container.  The frozen d4_run_arm.sh took `rc=$?`
#   from the docker CLI client and used the kernel's value for a ledger STRING
#   that no control flow consulted.
#
#   *** NOT CLOSED -- THE CAP DOES NOT SURVIVE SHELL DEATH.  REGISTERED OPEN. ***
#   A foreground `docker run` client is NOT the container's parent -- dockerd
#   is -- so containers ALREADY survived shell death and `-d` changes nothing
#   there.  What `timeout` provided was the CAP, and `timeout` lives in the
#   launching shell.  MOVING THE DEADLINE INTO THE POLLING LOOP BELOW MOVES IT
#   INTO THE SAME SHELL.  On shell death the outcome is identical in both
#   designs: THE CONTAINER RUNS ON, UNGUARDED, WITH NOTHING LEFT TO STOP IT.
#   `-d` is an improvement on rc capture and on not blocking the shell.  IT IS
#   NOT A CAP FIX and this file does not claim to be one.
#   Closing it properly needs the deadline somewhere that survives the shell --
#   inside the container's own entrypoint, or written to a file a later poller
#   can pick up and enforce.  NOT BUILT HERE.  Named, and left open.
#
#   ADDENDUM 2 (2026-08-26, after arm O realised exactly this exposure): the
#   deadline NOW LIVES INSIDE THE CONTAINER -- `timeout -k 60 $TMO` wraps the
#   arm command file on the `docker run` line below -- and the bookkeeping
#   runs in d4s_chain_driver.sh, a `setsid nohup` session that outlives the
#   agent.  The text above is kept as the record of what was open and why.
# ===========================================================================
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$WORKNAME" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4S_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4S_IDWARP_IMPORTED_FROM:\",p); print(\"D4S_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     echo D4S_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k 60 $TMO bash /mnt/$WORKNAME/d5_cmd.sh" > /dev/null 2>&1 \
  || { echo "ABORT could not start container"; exit 4; }

# The cap is a RUNAWAY GUARD THAT REPORTS (Sanaa, 2026-08-25), not a budget
# rigor is trimmed to fit.  A crossing is written to the ledger and CONTINUES;
# the supervisor decides.  CEILING = 4 x CAP is a hard stop so a genuine
# runaway is still bounded -- WHILE THIS SHELL LIVES (see the open exposure).
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
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$WORK" 2>/dev/null

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/ledger.txt"
{
  echo "ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM inspect(exit,oomkilled)=[$INSPECT] memavail_pre_GiB=$MEMAVAIL_GIB memavail_post_GiB=$MEMAVAIL_POST cpuset=$CPUSET delivered_cores_mean=[$DELIVERED] siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] log=$(basename "$LOG") stamp=$STAMP"
  grep -a "D4S_CONTAINER_UID\|D4S_IDWARP_SO_MD5\|D4S_DEADLINE_IN_CONTAINER_S" "$LOG" | head -3   # ADDENDUM 2: the strings the container prints
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc
