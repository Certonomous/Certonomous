#!/usr/bin/env bash
# Curriculum D6R-ACC2 arm launcher -- THE ACC_mp ARM OF D6R RE-RUN AT A CORRECTLY
# ANCHORED CAP.  DERIVED BY ASSERTED SUBSTITUTION from curriculum_D6R/d6r_run_arm.sh
# md5 243f0f631719edf7ae354410276b3cfd; the substitution set is enumerated in
# d6ra2_derive.py and the whole delta is d6ra2_run_arm_DELTAS_from_d6r.diff.
# Everything not in that set is D6R's bytes.
#
# WHY: D6R-PREREG-DEF-1.  ACC_mp's 30.0 core-min cap traced to D6's `3.0 x 3`
# anchor, and C-94 (docs/COST_CALIBRATION.md:170) is a 45-SECOND ACCEPTANCE PRIMAL
# on an ALREADY-DECOMPOSED tree with no adjoint and no colouring.  The registered
# program is `compute_totals` on a COLD staged copy at np=4, which must first
# COLOUR the Jacobian three times.  Two independent measurements put that at
# 112.4 and 107.4 core-min -- the arm needed ~4.7x its deadline and ~3.7x its cap
# and COULD NOT HAVE FINISHED, not on a slow day and not on an empty box.
#
# DERIVED from curriculum_D5/d5_run_arm.sh (itself the D4-SHIPPED Addendum-2
# launcher d4s_run_arm.sh @ 8b91be2b plus D5's registered deltas) with ONLY the
# registered deltas of D6R PREREGISTRATION.md section 7, recorded in
# d6r_run_arm_DELTAS_from_d6.diff.  Everything else is the family's bytes.
#
# CAP DISCIPLINE (the failure this file exists not to repeat).  A peer lane
# registered a 3.0 core-min cap and its launcher enforced 6.0 by copy-forward
# with no assertion.  Here the caps are NOT arguments.  They are constants in
# the table below, the table is reproduced verbatim in PREREGISTRATION.md
# section 4, this file's md5 is frozen there, and the launcher ASSERTS that the
# wall timeout it is about to enforce equals CAP_CORE_MIN*60/4 to the second.
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call and
# `( set -e; ... )` does not gate either.  Every step below gates explicitly
# with `|| { echo ABORT...; exit N; }`.
#
# NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives the
# arm and the KERNEL's verdict is read, not the harness's.
set -uo pipefail

# ===========================================================================
# D4-LAUNCHER-DEF-1 -- THE DEFECT THIS FILE EXISTS NOT TO REPEAT.
# `curriculum_D4/d4_run_arm.sh` hardcodes BASE at the PATCHED item's run root
# and runs an UNGUARDED `sudo -n rm -rf "$WORK"` for every arm except F.
# THE REPAIR IS NOT "CHANGE THE CONSTANT".  The WRONG CONSTANT MUST REFUSE, and
# the guard below is DRIVEN in d6r_groot5_selftest.sh and shown to abort.
# ===========================================================================
ITEM=D6RACC2
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6RACC2-a2-wing-multipoint
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
# ---- so the abort says WHOSE evidence it just protected.
# ENUMERATED FROM DISK AT FREEZE (2026-08-27T23:0xZ), not carried forward:
# D6 inherited names for roots that DO NOT EXIST (CURRICULUM-D14-a2-wing-remesh;
# the real one is D14M) and omitted D4S-F3S, D8R and eleven others.  An inert
# entry in a list whose job is to NAME whose evidence was protected is exactly
# the class of defect this lab records.  G-ROOT.1 above already refuses any base
# that is not D6R's own; this list makes the abort SAY WHOSE root it just
# refused, so it is worth nothing unless the names are real.
FORBIDDEN_ROOTS="/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv
/home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality
/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt
/home/ubuntu/certonomous-runs/CURRICULUM-D12-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D13-a1-basin-restart
/home/ubuntu/certonomous-runs/CURRICULUM-D14M-a2-wing-remesh
/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic
/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic
/home/ubuntu/certonomous-runs/CURRICULUM-D17-cone-supersonic
/home/ubuntu/certonomous-runs/CURRICULUM-D1Cprime-a1-shipped-endpoint
/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab
/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density
/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D7F-a3-m6-fd
/home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd
/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt
/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv
/home/ubuntu/certonomous-runs/CURRICULUM-D9-a5-ubend-opt
/home/ubuntu/certonomous-runs/CURRICULUM-D9-a5-ubend-opt-REPLICATE-REP_20260825T191118Z
/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12"
while IFS= read -r forb; do
  [ -z "$forb" ] && continue
  if [ "$BASE_REAL" = "$(realpath -m "$forb")" ]; then
    echo "ABORT G-ROOT.2 BASE resolves to ANOTHER ITEM'S RUN ROOT: $forb"
    echo "  That directory holds a graded row.  This launcher stages by"
    echo "  removing the arm directory, so writing there would destroy it.  REFUSED."
    exit 3
  fi
done <<< "$FORBIDDEN_ROOTS"

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
    echo "  This launcher writes the PATCHED row only (D6R REGISTERED DELTA: the graded D4 row).  REFUSED."
    exit 3
  fi
fi
echo "D4S_G_ROOT_PASS item=$ITEM base=$BASE_REAL ledger_clean=yes"
RANKS=4

# ---- REGISTERED CPU PLACEMENT (PREREGISTRATION.md section 5b) --------------
# `mpirun` inside a `--cpus=N` container binds rank 0 to the FIRST CORE OF THE
# HOST TOPOLOGY; concurrent containers land on the same core (MEASURED by the
# D13 lane 2026-08-25).  So: PIN, and MEASURE the placement.
# D6R REGISTERED DELTA: 2,3,4,14 -- DISJOINT from every live container cpuset read
# via docker inspect at freeze (W2R on 12), from D5's 8,10,11,13, and from the
# D4-SHIPPED registered set 5,6,7,9 (its chain may be re-fired there).  D7FR's
# 2,3,4,6 is released: its F-S and F-P arms are complete (STATUS.F-P rc=0
# 16:43:35Z) and no D7FR arm is outstanding.  Core 0 is the default landing
# core the defect names and is not used.
CPUSET=2,3,4,14

# For containerised MPI the conditioning variable is CONCURRENT CONTAINERS, not
# loadavg -- `uptime` will lie.  Censused before and after every arm.
container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d6r_" | tr '\n' ',' | sed 's/,$//'
}

# ---- D6R REGISTERED CAP TABLE (PREREGISTRATION.md section 4) ---------------
# RE-DERIVED FROM THE MEASURED ANCHOR, NOT INHERITED.  D6 registered O_mp at
# 2000.0 on a 6.389 core-min/major x 3-scenario model; C-188 (8262f123)
# MEASURED 31.258 core-min/major (2000.533 / 64 majors) -- 1.6308x the
# registered 19.167 -- at which rate D6's own 80-major point would have cost
# 2500.7 core-min, 25 % ABOVE its 2000.0 cap.  THAT CAP COULD NEVER HAVE BEEN
# MET.  D6R prices every arm from that measurement:
#   arm      predicted     cap     deadline(s)   compute window (core-min)
#   O_mp      2500.6      2900.0     43410            2894.0   80 x 31.258
#   ACC_mp     112.4       240.0      3510            2400.0   RE-ANCHORED, below
# D6R-ACC2's ACC_mp CAP IS NOT INHERITED AND NOT A COPY-FORWARD.  Two INDEPENDENT
# measurements of the program this arm actually runs:
#  (a) 1685.98 s, from the run's OWN logs: 75.10 s to the first colouring MEASURED
#      in ACC_mp's own log (`Calculating dRdW Coloring... 75.1 s`, i.e. start-up +
#      all three primals), plus three colourings MEASURED in O_mp's log at 419.08 /
#      425.85 / 425.61 s, plus two adjoint intervals MEASURED at 111.64 / 115.25 s
#      and a third INTERPOLATED at 113.45 s.  x4 ranks / 60 = 112.399 core-min.
#  (b) 107.4 core-min, from CURRICULUM-D5's ledger: ARM=ACC48 rc=0 wall_s=537
#      ranks=4 core_min=35.8 for ONE primal+adjoint pair on this same wing at np=4;
#      three pairs = 1611 s.  Over-counts start-up twice, so it is an upper bound
#      on the marginal scaling and a corroboration, not the primary.
#  The two agree to 4.65 %.  REGISTERED POINT 112.4, CAP 240.0 = 2.135x, whose
#  deadline inverts EXACTLY: (3510 + 90) * 4 / 60 = 240.000000, and 3510 s sits
#  BELOW rule 12's 3600 s stall convention so an arm that runs to its deadline is
#  never itself a stall row.
#   F_mp       231.2       300.0      4410             294.0   141.8 x 1.6308
#   REF_off     17.1        40.0       510              34.0   10.5 x 1.6308
# The three non-O arms never ran under D6, so their anchors are still the x3
# multipoint model C-188 measured short by 63 %; the SAME measured correction
# factor is applied to them and the residual exposure is named in section 4.
# THE OPTIMISER'S OWN max_iter (80) IS THE BINDING STOP, NOT THE CONTAINER
# DEADLINE: 80 x 31.258 = 2500.6 < 2894.0, so IPOPT terminates itself, the arm
# exits rc=0 and THE CHAIN CONTINUES -- which is what D6 could not do.
# MEMORY, registered as an EXPOSURE: one DAFoam solver at np=4 on this case
# held ~11.7 GB host-side (D4) and 9.263 GiB peak container RSS (A3 rung 2);
# three solvers in one process share the interpreter and libraries but not
# their Jacobians.  20g is the largest cap the 30.6 GiB aggregate ceiling
# admits beside an 8g sibling; an OOM kill (rc=137) is a REGISTERED OUTCOME
# (P7), stops the chain at the first arm, and is a finding about multipoint
# feasibility at np=4 on this box, not a wasted run.  Never 8g: the D4-SHIPPED
# ACC arm was OOM-killed by its 8g cgroup (rc=137, 16:56:28Z 2026-08-26).
cap_core_min() {
  case "$1" in
    O_mp)    echo 2900.0 ;;
    ACC_mp)  echo 240.0 ;;
    F_mp)    echo 300.0 ;;
    REF_off) echo 40.0 ;;
    *)  echo "" ;;
  esac
}
cap_memory() {
  case "$1" in
    O_mp|ACC_mp|F_mp|REF_off) echo 20g ;;
    *) echo "" ;;
  esac
}

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER 6) -----
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc

# ---- FROZEN INSTRUMENT HASHES (PREREGISTRATION.md section 7) ---------------
MD5_RUNSCRIPT=93edb4a231e13a7af065368f61a468ef
MD5_FD=7491c3a73c232fb6744990fd8109fd63
MD5_EXTRACT6=1743dd4232a7f06785f71be2f285f08d
MD5_REFOFF=ad67bbeb0c7b502262ebf5d4e8fa21cd
MD5_EXTRACT4=ee7d3c99fd716da23779cb651961918e
# D4's PATCHED optimiser history, staged READ-ONLY into REF_off/ as OptView.hst
# (D4's extractor reads that name); its md5 is asserted at staging and the
# grader exempts exactly this file, by md5, from the age guard (D7FR H4 form).
MD5_D4_HST=0d956d6ccbc010402915710f662d3b11
D4_HST_SRC=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O/OptView.hst

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: d6ra2_run_arm.sh ACC_mp <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: d6ra2_run_arm.sh ACC_mp <image>"; exit 64; }
test "$ARM" = "ACC_mp" || { echo "ABORT D6RACC2 registers EXACTLY ONE arm, ACC_mp; got '$ARM'.  A second arm is a separate item."; exit 64; }

# ---- G-ROOT.5 -- A LIVE ARM IS NEVER RE-STAGED.  Two live readings, taken
# ---- BEFORE any destructive act: (a) a RUNNING container carrying this
# ---- item's prefix and this arm; (b) a driver pidfile in the run root naming
# ---- a LIVE pid that is not an ancestor of this process, or whose cwd is the
# ---- run root.  A stale pidfile (dead pid) does not block.
LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d6ra2_${ARM}_" 2>/dev/null | grep "^d6ra2_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  echo "  Re-staging would remove the live arm directory under it.  REFUSED."
  exit 3
fi
PIDFILE="$BASE/d6ra2_driver.pid"
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
# against that cap by inverting the arithmetic.
# ===========================================================================
# D6-CAP-FRAME-1 (L-371) -- THE DEFECT THIS BLOCK EXISTS NOT TO REPEAT.
# D6 enforced its cap as `timeout` INSIDE the container and graded CORE_MIN
# from a wall bracketed around `docker run` ON THE HOST.  Measured gap: host
# 30008 s against an enforced 30000 s = 8 s = 0.5333 core-min at 4 ranks, and
# the arm recorded 2000.533 against a 2000.0 cap -- IT EXCEEDED ITS OWN CAP BY
# OBEYING IT.  D6's own D4_CAP_ASSERT could not catch this: it derives TMO from
# the cap and re-checks by INVERTING THE SAME ARITHMETIC INSIDE ONE FRAME, so
# it passes on every run and never could.
# THE REPAIR IS THE D4S-F3SR ONE (ed9cda90) AND IT DOES NOT WIDEN THE CAP.
# The host bracket the grader reads STRICTLY CONTAINS the in-container
# `timeout` clock, so the ENFORCED DEADLINE MOVES DOWN by a bounded allowance:
#   10 s  docker run client + container create/start + in-container preamble
#         before `timeout` begins (MEASURED upper bound 3.3 s, D4S-F3S F-S)
#   60 s  `timeout -k 60` TERM->KILL escalation grace
#   10 s  the poll loop's `sleep 10` granularity on T1
#    5 s  `docker logs` of the arm log + `docker inspect` before T1
#   ----     (D6 MEASURED the whole of this at 8 s on a 10.7 MB log)
#   85 s  bounded; REGISTERED AT 90 s
FRAME_ALLOWANCE_S=90
# THE ASSERTION INVERTS AND RE-ADDS THE ALLOWANCE, so no edit to it can
# silently widen the cap: (TMO + FRAME_ALLOWANCE_S) * RANKS / 60 == CAP.
TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)) - $FRAME_ALLOWANCE_S)") || { echo "ABORT tmo calc"; exit 65; }
test "$TMO" -gt 0 || { echo "ABORT frame allowance $FRAME_ALLOWANCE_S consumes the whole cap"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % (($TMO+$FRAME_ALLOWANCE_S)*$RANKS/60.0))") || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
cap, back = $CAP, $BACKCHECK
if abs(cap-back) > 0.02:
    sys.stderr.write('ABORT CAP MISMATCH registered=%r enforced_plus_allowance=%r\n' % (cap, back)); sys.exit(1)
" || { echo "ABORT enforced cap + frame allowance != registered cap"; exit 65; }
echo "D4S_CAP_FRAME arm=$ARM registered_core_min=$CAP ranks=$RANKS deadline_in_container_s=$TMO frame_allowance_s=$FRAME_ALLOWANCE_S worst_case_host_core_min=$BACKCHECK enforced_in_frame=container graded_in_frame=host_bracket_T0_T1"
echo "D4_CAP_ASSERT arm=$ARM registered_core_min=$CAP ranks=$RANKS enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM"

# ---- host state, read before ranks are claimed ---------------------------
MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D4_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 run root mode $(stat -c '%a' "$BASE")"; exit 4; }

# ---- staged-instrument identity, re-asserted before EVERY launch ---------
echo "$MD5_RUNSCRIPT  $BASE/d6r_opt_runScript.py"    | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_FD  $BASE/d6r_fd_endpoint.py"             | md5sum -c - || { echo "ABORT fd md5"; exit 4; }
echo "$MD5_EXTRACT6  $BASE/d6r_extract_endpoint.py"  | md5sum -c - || { echo "ABORT extract6 md5"; exit 4; }
echo "$MD5_REFOFF  $BASE/d6r_ref_off.py"             | md5sum -c - || { echo "ABORT ref_off md5"; exit 4; }
echo "$MD5_EXTRACT4  $BASE/d4_extract_endpoint.py"  | md5sum -c - || { echo "ABORT extract4 md5"; exit 4; }

# ---- image identity by DIGEST, resolved from the local store -------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1)    WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  dafoam/opt-packages:latest) WANT=$IMG_SHIPPED_DIGEST; ROW=SHIPPED ;;
  *) echo "ABORT image $IMG is not a registered row"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }

# ---- G-ROW.  PATCHED ONLY -- the row D4 was graded on (C-97). -------------
test "$ROW" = "PATCHED" || {
  echo "ABORT G-ROW D6R is registered PATCHED-ONLY (the row D4 was GRADED on, C-97); got ROW=$ROW ($IMG)."
  echo "  The SHIPPED row is NOT bought here; a second row is a separate item."
  exit 4; }
echo "D4S_G_ROW_PASS row=$ROW digest=$GOT_DIGEST"
echo "D4_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d6ra2_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- stage a pristine copy of base/ for arms that need a cold case -------
# D6R REGISTERED DELTA: the multipoint model owns THREE full case copies mp04/
# mp05/ mp06/ under the arm directory (one DAFoamBuilder run_directory each);
# the FFD (D4's 6x2x8) and the instruments sit at the arm directory, which is
# the container's working directory.
if [ "$ARM" != "F_mp" ]; then
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/base" "$WORK" || { echo "ABORT stage copy"; exit 4; }
  for mp in mp04 mp05 mp06; do
    cp -a "$BASE/base" "$WORK/$mp" || { echo "ABORT stage $mp copy"; exit 4; }
    test -n "$(ls -d "$WORK/$mp"/processor* 2>/dev/null)" && { echo "ABORT G-COLD $mp processor* present"; exit 5; }
  done
  cp -a "$BASE/d6r_opt_runScript.py" "$BASE/d6r_fd_endpoint.py" "$BASE/d6r_extract_endpoint.py" "$BASE/d6r_ref_off.py" "$BASE/d4_extract_endpoint.py" "$WORK/" || { echo "ABORT stage instruments"; exit 4; }
  # COLD START, verified BEFORE the launch (D2 G8), and the AGE GUARD's datum:
  # 0/ is touched LAST at stage time, so every artifact the run produces must
  # be strictly newer than 0/U or it did not come from this run.
  for bad in "$WORK/reports" "$WORK/OptView.hst" "$WORK/opt_IPOPT.txt" "$WORK/dRdWColoring_4.bin" "$WORK/d6r_fd_endpoint.json" "$WORK/d6r_ref_off.json"; do
    test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
  done
  test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
  test -n "$(ls -d "$WORK"/[0-9]*.[0-9]* 2>/dev/null)" && { echo "ABORT G-COLD time dir present"; exit 5; }
  test -f "$WORK/0/U" || { echo "ABORT G-COLD 0/U missing"; exit 5; }
  if [ "$ARM" = "REF_off" ]; then
    # D6R REGISTERED DELTA: D4's PATCHED history staged READ-ONLY, md5-asserted,
    # BEFORE the datum so the age guard dates it as an input (exempt by md5).
    echo "$MD5_D4_HST  $D4_HST_SRC" | md5sum -c - || { echo "ABORT D4 OptView.hst md5 (source changed)"; exit 4; }
    cp "$D4_HST_SRC" "$WORK/OptView.hst" || { echo "ABORT stage D4 history"; exit 4; }
    echo "D6R_D4_HST_STAGED arm=$ARM md5=$(md5sum "$WORK/OptView.hst" | cut -d' ' -f1) source=$D4_HST_SRC"
  fi
  touch "$WORK/0"/* || { echo "ABORT age-guard datum"; exit 5; }
  AGE_DATUM=$(stat -c '%Y' "$WORK/0/U")
  echo "$AGE_DATUM" > "$WORK/.d4_age_datum"
  echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM"
else
  WORK="$BASE/O_mp"
  test -d "$WORK" || { echo "ABORT arm $ARM expects an existing $WORK from arm O_mp"; exit 5; }
  test -f "$WORK/OptView.hst" || { echo "ABORT arm F_mp: no OptView.hst to read an endpoint from"; exit 5; }
  cp -a "$BASE/d6r_fd_endpoint.py" "$BASE/d6r_extract_endpoint.py" "$WORK/" || { echo "ABORT stage F instruments"; exit 4; }
  rm -f "$WORK/d6r_fd_endpoint.json" "$WORK/d6r_fd_endpoint.jsonl" "$WORK/d6r_endpoint_dvs.json" "$WORK/d6r_major_history.json"
fi

case "$ARM" in
  O_mp)    CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d6r_opt_runScript.py -task run_driver -optimizer IPOPT" ;;
  ACC_mp)  CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d6r_opt_runScript.py -task compute_totals" ;;
  F_mp)    CMD="python d6r_extract_endpoint.py && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d6r_fd_endpoint.py" ;;
  REF_off) CMD="python d4_extract_endpoint.py && mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d6r_ref_off.py" ;;
esac

# ---- the arm command goes to a FILE the container executes under its OWN
# ---- `timeout` at the registered cap wall (TMO), so the deadline is INSIDE
# ---- the container and survives every host shell.  `-k 60` escalates TERM to
# ---- KILL; the kernel exit code (124/137) is then the record.
CMDFILE="$WORK/d6r_cmd.sh"
printf '%s\n' "$CMD" > "$CMDFILE" || { echo "ABORT cmd file"; exit 4; }
echo "D4S_CMDFILE arm=$ARM md5=$(md5sum "$CMDFILE" | cut -d' ' -f1) deadline_in_container_s=$TMO"
CPUSAMPLE="$BASE/${ARM}_${STAMP}.cpu.jsonl"
# DELIVERED CORES ARE MEASURED, NOT INFERRED FROM THE QUOTA FLAG.  Passive
# reader; an absent sample file is reported as NOT_MEASURED, never as a pass.
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
# rc CAPTURE is CLOSED (docker inspect, no --rm); the CAP lives INSIDE the
# container (`timeout -k 60 $TMO` below) and survives shell death; the host
# bookkeeping runs in d6r_chain_driver.sh, a setsid nohup session.
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$(basename "$WORK")" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4S_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4S_IDWARP_IMPORTED_FROM:\",p); print(\"D4S_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     echo D4S_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k 60 $TMO bash /mnt/$(basename "$WORK")/d6r_cmd.sh" > /dev/null 2>&1 \
  || { echo "ABORT could not start container"; exit 4; }

# The cap is a RUNAWAY GUARD THAT REPORTS (Sanaa, 2026-08-25).  A crossing is
# written to the ledger and CONTINUES; CEILING = 4 x CAP is a hard stop.
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

# ---- the KERNEL's verdict, read BEFORE the container is removed ----------
INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
# ---- D6-CAP-FRAME-1 REPAIR, SECOND HALF: THE CONTAINER'S OWN CLOCK, from the
# ---- kernel, read in the same inspect and BEFORE the rm.  This is the frame
# ---- the deadline is ENFORCED in; WALL (T0..T1) is the frame the cap is
# ---- GRADED in.  Recording both SEPARATES them on the record instead of
# ---- conflating them, and the grader BINDS the difference at G10 rather than
# ---- printing it -- a discrepancy nobody grades is worse than one never
# ---- computed.  Absent -> NOT_MEASURED (INFRASTRUCTURE, L-342); the gate then
# ---- falls back to the HOST bracket alone, which is the STRICTER reading, so
# ---- the fallback can never turn a failing cap into a pass.
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
echo "D4S_CONTAINER_CLOCK arm=$ARM started_at=$CSTART finished_at=$CFIN container_wall_s=$CWALL host_wall_s_bracket_T0_T1=$WALL"
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$WORK" 2>/dev/null

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/ledger.txt"
{
  echo "ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM inspect(exit,oomkilled)=[$INSPECT] container_wall_s=$CWALL frame_allowance_s=$FRAME_ALLOWANCE_S memavail_pre_GiB=$MEMAVAIL_GIB memavail_post_GiB=$MEMAVAIL_POST cpuset=$CPUSET delivered_cores_mean=[$DELIVERED] siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] log=$(basename "$LOG") stamp=$STAMP"
  grep -a "D4S_CONTAINER_UID\|D4S_IDWARP_SO_MD5\|D4S_DEADLINE_IN_CONTAINER_S" "$LOG" | head -3   # the strings the container prints
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc
