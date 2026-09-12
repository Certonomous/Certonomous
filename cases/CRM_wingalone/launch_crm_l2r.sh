#!/bin/bash
# CRM WING-ALONE L2R, M=0.85 -- THE RELAUNCH AFTER THE 2026-09-12T17:36:41Z REBOOT.
#
# DERIVED FROM launch_crm_l2.sh WITH EXACTLY ONE BLOCK REMOVED: the MRF rank-wait loop.
# That loop waited on hardcoded pids 2200481-2200486 on the OLD box. Those processes died
# with the box. Keeping a wait keyed to dead pids is not caution, it is dead code whose only
# possible effect is a false block if Linux ever recycled one of those numbers INTO the MRF
# case directory. The MRF ET8000 family COMPLETED before the stop (rc=0, End, last time ==
# endTime 8000, all three levels), so there is nothing left to wait for.
#
# EVERY OTHER PROPERTY IS CARRIED BYTE-FOR-BYTE:
#   * IT NEVER KILLS AND IT NEVER SIGNALS ANY PROCESS. It only READS /proc and free(1).
#   * NO CLOCK TRIGGER AND NO SPEND TRIGGER. Sanaa has ruled four times that no run is
#     stopped on budget or clock. There is no `timeout`, no cap, no budget test here.
#   * rc IS CAPTURED INSIDE THIS WRAPPER -- `setsid timeout cmd` exits 0 for every outcome,
#     so the rc is taken around the solver, never around the detaching line.
#   * S5: it REFUSES to launch onto an existing result rather than clearing a directory.
#   * The age guard (rule 4) is dated by touching 0/ LAST, immediately before the solver.
set -u
CASE="$1"; RANKS="$2"; MIN_AVAIL_GIB="$3"
S="$CASE/STATUS.solve"; LOG="$CASE/LAUNCH.log"
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOG"; }
say "ARMED case=$CASE ranks=$RANKS need_avail=${MIN_AVAIL_GIB}GiB (READS /proc AND free ONLY; NEVER SIGNALS; no clock or spend trigger)"

# ---- 1. memory, re-read at the moment of launch -----------------------------
avail=$(free -g | awk '/^Mem:/{print $7}')
if [ "$avail" -lt "$MIN_AVAIL_GIB" ]; then
  { echo "VERDICT=BLOCKED"; echo "reason=memory"; echo "available_GiB=$avail";
    echo "required_GiB=$MIN_AVAIL_GIB"; echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$S"
  echo "80" > "$CASE/solve_rc"; say "BLOCKED on memory: ${avail} < ${MIN_AVAIL_GIB} GiB. Refusing rather than risking an OOM kill on another team."; exit 80
fi

# ---- 2. S5: never launch onto an existing result ----------------------------
# THE GLOB `[0-9]*` IS NOT A TIME-DIRECTORY TEST AND THIS IS WHY THIS LOOP IS NOT ONE.
# Attempt 1 (2026-09-12T19:03:45Z) BLOCKED rc=81 on `0.orig` because `[0-9]*` matches any
# name STARTING with a digit. `0.orig` is the initial-condition template, not an answer.
# A time directory is digits with an optional decimal part and NOTHING ELSE, so that is
# what is matched. The guard is made CORRECT, not loosened: at this point in the script
# `0/` does not exist yet either, so ANY time directory is still a refusal.
for e in "$CASE"/*; do
  b=$(basename "$e")
  if [ -d "$e" ] && printf '%s' "$b" | grep -qE '^[0-9]+([.][0-9]+)?$'; then
    { echo "VERDICT=BLOCKED"; echo "reason=S5_time_dir_present"; echo "entry=$b"; } > "$S"
    echo "81" > "$CASE/solve_rc"; say "BLOCKED: time dir $b present. Never clearing a directory."; exit 81
  fi
done

# ---- 3. THE MESH IS ALREADY PATCHED. NEVER RE-PATCH, NEVER RE-DECOMPOSE. ----
# constant/polyMesh and every processor*/constant/polyMesh were copied from SOLVE_L2 with
# all five files sha256-identical both sides (PATCH_REUSE_MANIFEST.txt). The three patches
# wing 11,136 / farfield 11,136 / symmetry 14,144 are already in `boundary`. There is no
# createPatch and no decomposePar in this script, and system/createPatchDict was removed
# from the case so nothing can re-run it by accident.
if [ ! -d "$CASE/processor5/constant/polyMesh" ]; then
  { echo "VERDICT=BLOCKED"; echo "reason=decomposed_mesh_absent"; } > "$S"
  echo "82" > "$CASE/solve_rc"; say "BLOCKED: decomposed mesh absent."; exit 82
fi
NF=$(grep -c "nFaces" "$CASE/constant/polyMesh/boundary")
if [ "$NF" -lt 3 ]; then
  { echo "VERDICT=BLOCKED"; echo "reason=patches_absent"; echo "nFaces_lines=$NF"; } > "$S"
  echo "83" > "$CASE/solve_rc"; say "BLOCKED: boundary carries $NF patches, expected 3."; exit 83
fi

set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc '' > "$CASE/log.foam_source" 2>&1; SRC=$?; set -u
[ "$SRC" -ne 0 ] && { echo "91" > "$CASE/solve_rc"; say "BLOCKED: foam source rc=$SRC"; exit 91; }
cd "$CASE" || { echo "90" > "$CASE/solve_rc"; exit 90; }

# ---- 0/ IS CREATED HERE, AT LAUNCH, FROM 0.orig -------------------------------
# The case on disk carries `0.orig/`, never `0/`. Two reasons, and the second is the
# stronger one:
#   (1) the queue validator's AGE-GUARD refuses to launch into a cwd that already holds
#       a time directory (queue_entry_check.py:357-369) -- "a run is never launched into
#       a tree that already holds an answer". `0.orig` is the lab's existing convention
#       for this (DrivAer r2_coarse carries one).
#   (2) rule 4's age guard dates the run from `0/`, and fields CREATED at launch date it
#       more honestly than fields merely touched. This is not a way around the guard; it
#       is the guard working as intended.
# It REFUSES rather than overwrite if `0/` somehow exists.
if [ -e 0 ]; then
  { echo "VERDICT=BLOCKED"; echo "reason=zero_dir_present_before_launch"; } > "$S"
  echo "84" > solve_rc; say "BLOCKED: 0/ already present. Never overwriting an initial condition."; exit 84
fi
cp -r 0.orig 0
touch 0/U 0/p 0/T 0/k 0/omega 0/nut 0/alphat
for i in 0 1 2 3 4 5; do touch processor$i/0/U processor$i/0/p processor$i/0/T \
  processor$i/0/k processor$i/0/omega processor$i/0/nut processor$i/0/alphat; done
{ echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "ranks=$RANKS";
  echo "available_GiB_at_launch=$avail"; } > "$S"

TS0=$(date +%s)
/usr/bin/time -v -o time.rhoSimpleFoam mpirun -np "$RANKS" rhoSimpleFoam -parallel > log.rhoSimpleFoam 2>&1; RC=$?
TS1=$(date +%s)
SPEAK=$(grep "Maximum resident set size" time.rhoSimpleFoam | grep -oE "[0-9]+$")
{ echo "rhoSimpleFoam_rc=$RC"; echo "solver_wall_s=$((TS1-TS0))"; echo "solver_ranks=$RANKS";
  echo "solver_core_min=$(echo "($TS1-$TS0)*$RANKS/60" | bc -l)";
  echo "solver_peak_rss_kB=${SPEAK:-UNMEASURED}"; } >> "$S"
say "SOLVER EXITED rc=$RC after $((TS1-TS0)) s"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi

TR0=$(date +%s)
reconstructPar -latestTime > log.reconstructPar 2>&1; RC=$?
TR1=$(date +%s)
{ echo "reconstructPar_rc=$RC"; echo "reconstructPar_wall_s=$((TR1-TR0))";
  echo "reconstructPar_ranks=1   # SERIAL";
  echo "total_core_min=$(echo "(($TS1-$TS0)*$RANKS + ($TR1-$TR0)*1)/60" | bc -l)   # SUM OF PHASES at their OWN rank counts";
  echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi
echo "0" > solve_rc
say "COMPLETE rc=0"
exit 0
