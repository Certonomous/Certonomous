#!/usr/bin/env bash
# D6R-ACC2 driver -- ONE ARM, ACC_mp, at a correctly anchored cap.  DERIVED BY
# ASSERTED SUBSTITUTION from curriculum_D6R/d6r_chain_driver.sh; the substitution
# set is enumerated in d6ra2_derive.py and the whole delta is
# d6ra2_chain_driver_DELTAS_from_d6r.diff.  The INSTRUMENTS ARE D6R'S OWN, staged
# from curriculum_D6R/ under their frozen md5s: the PROGRAM IS UNCHANGED and only
# the cap moved.  Original D6R header follows.
# D6R chain driver -- DERIVED from curriculum_D6/d6r_chain_driver.sh @ b4ddca65
# (Addendum 3 form, CHAIN_DONE trap FROM BIRTH), itself derived from
# curriculum_D5/d5_chain_driver.sh (itself the
# D4-SHIPPED Addendum-2 driver @ 8b91be2b plus D5's registered deltas: aggregate
# WAIT-AND-RETRY per UPDATE F, ALREADY_BOUGHT, root staging, STATUS opened-and-
# appended) with ONLY the registered deltas of D6R PREREGISTRATION.md section 7:
#   item names, run root, launcher md5, the D6R instruments (no FFD boxes -- D6
#   keeps D4's 6x2x8), every arm at 20g with the H5 floor at 24.0 GiB (cap +
#   4 GiB headroom, D4-SHIPPED section 4.4; the multipoint memory exposure is
#   registered in section 4 and P7), arms O_mp ACC_mp F_mp REF_off.
# Never 8g: the D4-SHIPPED ACC arm was OOM-killed by its 8g cgroup (rc=137,
# 16:56:28Z 2026-08-26).
# Runs the named arms IN ORDER through the frozen launcher and STOPS AT THE
# FIRST NON-ZERO rc.  Started ONLY detached (the queue runner's own form, or
#   setsid nohup bash d6r_chain_driver.sh O_mp ACC_mp F_mp REF_off > <root>/chain_launch.out 2>&1 &
# ).  rc per arm = the launcher's exit = docker inspect .State.ExitCode, written
# HERE into STATUS.<arm>; nothing trusts $? of a setsid/timeout line.
# cwd is the CASE directory, never the run root (G-ROOT.5 b).
# Permission for detached launches: bc0e687e (Sanaa, boarded verbatim).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d6ra2_run_arm.sh"
IMG=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6RACC2-a2-wing-multipoint
D4_BASE_SRC=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/base
D4_CASE_DIR="$HERE/../curriculum_D4"
# THE INSTRUMENTS ARE D6R'S, READ FROM D6R'S OWN CASE DIRECTORY UNDER THE SAME
# FROZEN md5s ASSERTED BELOW.  Copying them into this item would create a second
# copy of a frozen file, which is the drift this lab records.
D6R_CASE_DIR="$HERE/../curriculum_D6R"
PERMISSION=bc0e687e
H5_FLOOR_GIB=24.0; H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6
AGG_POLL_S=30; AGG_BOUND_S=14400
H5_RETRY_S=60; H5_BOUND_S=14400   # D6R ADDENDUM 2: H5 in the WAIT-AND-RETRY form (re-take the 60 s window every 60 s, bounded 4 h); the loop below was found on disk uncommitted from lane Q1 (17:49:14Z) with these two names unbound -- completed and registered here
MD5_LAUNCHER=a561ab9309559680305c9ddb0fcc1d7b
MD5_RUNSCRIPT=93edb4a231e13a7af065368f61a468ef
MD5_FD=7491c3a73c232fb6744990fd8109fd63
MD5_EXTRACT6=1743dd4232a7f06785f71be2f285f08d
MD5_REFOFF=ad67bbeb0c7b502262ebf5d4e8fa21cd
MD5_EXTRACT4=ee7d3c99fd716da23779cb651961918e
test $# -ge 1 || { echo "ABORT usage: d6ra2_chain_driver.sh ACC_mp"; exit 64; }
# A STRENGTHENING: this item registers EXACTLY ONE arm.  Any other argument list
# REFUSES before the launcher md5 is even read, so no second arm can be bought.
test "$*" = "ACC_mp" || { echo "ABORT D6RACC2 registers EXACTLY the arm list [ACC_mp]; got [$*]."; exit 64; }
ARMS="$*"; STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/d6ra2_driver.pid"
cd "$HERE" || exit 4
echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before staging"; exit 4; }
# ---- ROOT STAGING on the first fire only ----------------------------------
if [ ! -d "$BASE" ]; then
  test -d "$D4_BASE_SRC" || { echo "ABORT D4 base source absent: $D4_BASE_SRC"; exit 4; }
  mkdir -p "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
  chmod 777 "$BASE" || { echo "ABORT chmod 777 $BASE (L-251)"; exit 4; }
  cp -a "$D4_BASE_SRC" "$BASE/base" || { echo "ABORT copy base/"; exit 4; }
  cp -a "$D6R_CASE_DIR/d6r_opt_runScript.py" "$D6R_CASE_DIR/d6r_fd_endpoint.py" "$D6R_CASE_DIR/d6r_extract_endpoint.py" "$D6R_CASE_DIR/d6r_ref_off.py" "$D4_CASE_DIR/d4_extract_endpoint.py" "$BASE/" || { echo "ABORT copy instruments"; exit 4; }
  # ADDENDUM 1 (D5-DRIVER-DEF-1, inherited): G-ROOT.3 accepts ONLY an exact
  # `ITEM=D6` line; the `ITEM=D6R staged=...` form was refused by D5's launcher
  # on its first runner fire (17:43:47Z, rc=3, zero compute).  Identity on its
  # own line; staging metadata on a line that does not start with ITEM=.
  echo "ITEM=D6RACC2" > "$BASE/ledger.txt"
  echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) base_src=$D4_BASE_SRC permission=$PERMISSION" >> "$BASE/ledger.txt"
  echo "D6R_ROOT_STAGED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ) mode=$(stat -c '%a' "$BASE") permission=$PERMISSION"
else
  echo "D6R_ROOT_PRESENT base=$BASE (not re-staged)"
fi
{ echo "$MD5_RUNSCRIPT  $BASE/d6r_opt_runScript.py"; echo "$MD5_FD  $BASE/d6r_fd_endpoint.py"; echo "$MD5_EXTRACT6  $BASE/d6r_extract_endpoint.py"; echo "$MD5_REFOFF  $BASE/d6r_ref_off.py"; echo "$MD5_EXTRACT4  $BASE/d4_extract_endpoint.py"; } | md5sum -c - || { echo "ABORT staged instrument md5"; exit 4; }
test -f "$BASE/base/FFD/wingFFD.xyz" || { echo "ABORT staged base/ has no FFD/wingFFD.xyz"; exit 4; }
if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."; exit 3
  fi
fi
echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"; echo "chain_done stamp=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ arms=[$ARMS] last=[$(tail -n 1 "$STATUS" 2>/dev/null)] permission=$PERMISSION" >> "$BASE/CHAIN_DONE"' EXIT   # ADDENDUM 3: the D5 Addendum 3 A3.5 / D17 / D8R form
echo "D6R_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] permission=$PERMISSION"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) permission=$PERMISSION" >> "$STATUS"
mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
cap_mem_gib() { echo 20; }   # every D6R arm 20g (section 4); never 8g
for ARM in $ARMS; do
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before arm $ARM"; echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 4; }
  echo "preflight arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ permission=$PERMISSION" > "$BASE/STATUS.$ARM"
  if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT ALREADY_BOUGHT arm $ARM has an rc=0 ledger row; a second record for one run is the defect."
    echo "rc=3 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=ALREADY_BOUGHT permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=REFUSED_ALREADY_BOUGHT arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 3
  fi
  # ---- H5: a WINDOW of MemAvailable, every sample above the floor -- in the
  # ---- WAIT-AND-RETRY form (D6R ADDENDUM 2): a 24.0 GiB floor beside a running
  # ---- 12g sibling (D5) cannot clear at launch, and a one-shot refusal would
  # ---- discard the entry at zero compute (the W2-DEF-2 shape UPDATE F ruled
  # ---- against).  The window is re-taken every H5_RETRY_S until every sample
  # ---- clears, bounded H5_BOUND_S (D5's ceiling wall is 7.75 h); every wait is
  # ---- a line in STATUS.<arm>; refuse-and-BLOCK at the bound.  The floor and
  # ---- the any-sample rule are unchanged.
  H5_WAITED=0
  while true; do
    H5_FILE="$BASE/${ARM}_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"; BELOW=0; N=0; MIN=999; MAX=0
    STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))")
    for _ in $(seq 1 $H5_SAMPLES); do
      s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"
      MIN=$(python3 -c "print(min($MIN,$s))"); MAX=$(python3 -c "print(max($MAX,$s))")
      [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1))
      sleep "$STEP"
    done
    echo "D6R_H5_WINDOW arm=$ARM n=$N window_s=$H5_WINDOW_S floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAX samples_below_floor=$BELOW waited_s=$H5_WAITED file=$(basename "$H5_FILE")"
    if [ "$BELOW" -eq 0 ] && [ "$N" -eq "$H5_SAMPLES" ]; then break; fi
    if [ "$H5_WAITED" -ge "$H5_BOUND_S" ]; then
      echo "ABORT H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB after ${H5_WAITED}s of waiting.  BLOCKED."
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_BLOCKED_AT_BOUND waited=$H5_WAITED below=$BELOW min_GiB=$MIN permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_H5 arm=$ARM waited=$H5_WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 6
    fi
    echo "H5_WAIT waited=$H5_WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM below=$BELOW of=$N min_GiB=$MIN floor_GiB=$H5_FLOOR_GIB" >> "$BASE/STATUS.$ARM"
    sleep "$H5_RETRY_S"; H5_WAITED=$((H5_WAITED+H5_RETRY_S+H5_WINDOW_S))
  done
  # ---- AGGREGATE: WAIT-AND-RETRY (UPDATE F ruling)
  WAITED=0; AGG_SERIES="$BASE/${ARM}_aggregate_series.txt"
  while true; do
    AGG=$(python3 "$D6R_CASE_DIR/d6r_aggregate_memory.py" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
    echo "$(date -u +%s) $AGG" >> "$AGG_SERIES"
    if [ "$(printf '%s' "$AGG" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ]; then break; fi
    if [ "$WAITED" -ge "$AGG_BOUND_S" ]; then
      echo "ABORT AGGREGATE still over $AGG_CEILING_GIB GiB after ${WAITED}s.  BLOCKED.  Series: $(basename "$AGG_SERIES")"
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=AGGREGATE_BLOCKED_AT_BOUND waited=$WAITED series=$(basename "$AGG_SERIES") permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_AGGREGATE arm=$ARM waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; exit 6
    fi
    echo "AGGREGATE_WAIT waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM $AGG" >> "$BASE/STATUS.$ARM"
    sleep "$AGG_POLL_S"; WAITED=$((WAITED+AGG_POLL_S))
  done
  echo "D6R_AGGREGATE arm=$ARM waited=$WAITED $AGG"
  echo "D6R_DRIVER arm=$ARM begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID permission=$PERMISSION"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "D6R_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN aggregate_waited_s=$WAITED permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then
    # D6R REGISTERED DELTA (repair 1/3, PREREGISTRATION.md section 3a): the stop
    # line names the REGISTERED ARM ORDER and the arms that will NOT run, so the
    # grader reads the census from the driver's own record instead of inferring
    # it.  D6's grader REFUSED on an arm with no ledger row even though the
    # registration calls a chain stop a FINDING (PREREGISTRATION.md:115-117,:299)
    # -- the item could not grade one of its own registered paths (L-322).
    NOTRUN=""; seen=0
    for a in $ARMS; do
      if [ "$seen" = "1" ]; then NOTRUN="$NOTRUN $a"; fi
      if [ "$a" = "$ARM" ]; then seen=1; fi
    done
    echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc order=[$ARMS] not_run=[${NOTRUN# }] stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    exit "$rc"
  fi
done
echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
exit 0
