#!/usr/bin/env bash
# =====================================================================
# MP_A5R -- QUEUE LAUNCH WRAPPER.  **PREPARED, NEVER RUN BY THIS LANE.**
#
# WHY THIS FILE EXISTS AND IS NOT A SECOND LAUNCHER.  scripts/queue_runner.py
# launches an ARGV; it passes no environment.  mpa5r_stage_and_run.sh REFUSES to
# start unless BASE and CPUSET are given explicitly (:108-114), by design --
# "placement is registered, never defaulted".  This wrapper supplies exactly those
# two registered values and execs the frozen launcher.  IT ADDS NO PARAMETER, NO
# RESOURCE FLAG, NO CAP AND NO TIMEOUT, and it is the only thing standing between
# the queue and the frozen chain.
#
# ITEM 19 (Sanaa 2026-09-12): the runner is the only thing that launches.  Running
# this file by hand does not make a case, and nothing here should be read as
# permission to do so.
#
# REGISTERED PLACEMENT.  CPUSET=15, one core, the highest-numbered.  np=1, so the
# core guard (item 8) reads 1 solver rank.  15 is chosen because every OpenFOAM
# decomposition on this box is 0-based and contiguous from core 0, so the top core
# is the one least likely to be taken by a wave scheduled beside this item.
#
# BASE is a FRESH timestamped tree, computed here and never reused: the frozen
# launcher aborts if BASE exists (:119), and an interrupted tree is EVIDENCE and is
# never deleted (PREREGISTRATION Sec.5).
# =====================================================================
set -u

CASE_DIR=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_MP_A5R
LAUNCHER="$CASE_DIR/mpa5r_stage_and_run.sh"

# --- the launcher this wrapper may execute is PINNED.  A wrapper that will run
#     whatever is at the path is not a wrapper, it is a hole.  The pin is the
#     post-Addendum-2 hash and MUST be filled in by whoever applies the diff, in
#     the same commit.  UNFILLED, THIS WRAPPER REFUSES -- fail closed.
PIN="__FILL_IN_POST_ADDENDUM_2_MD5_OF_mpa5r_stage_and_run.sh__"
GOT=$(md5sum "$LAUNCHER" | awk '{print $1}')
if [ "$GOT" != "$PIN" ]; then
  echo "REFUSE [PIN] mpa5r_stage_and_run.sh md5 $GOT != registered pin $PIN.  NOT LAUNCHING."
  exit 90
fi

# --- Sanaa item 6, asserted HERE too, not only inside the launcher: if the
#     Addendum-2 uid repair is not in the file we are about to run, we do not run it.
grep -q -- '--user 0:0' "$LAUNCHER" && {
  echo "REFUSE [ROOT] the launcher still carries '--user 0:0'.  Sanaa 2026-09-12 item 6:"
  echo "               'As ubuntu.  Never root.  Container jobs included.'  NOT LAUNCHING."
  exit 91
}
grep -q -- '-u 1000:1000 --group-add 1002' "$LAUNCHER" || {
  echo "REFUSE [ROOT] the launcher does not carry the measured non-root spelling"
  echo "               -u 1000:1000 --group-add 1002.  NOT LAUNCHING."
  exit 91
}

# --- Sanaa checkpoint item 2, asserted on the run script that will actually run.
grep -q 'hist_file' "$CASE_DIR/mpa5r_run_script.py" || {
  echo "REFUSE [CHECKPOINT] mpa5r_run_script.py has no pyOptSparse hist_file; Sanaa item 2"
  echo "                    requires the optimisation to write its history and design vector"
  echo "                    every iteration AND be able to hot-start from them.  NOT LAUNCHING."
  exit 92
}

export CPUSET=15
export BASE="/home/ubuntu/certonomous-runs/CURRICULUM-MP_A5R-a5-ubend-multipoint-$(date -u +%Y%m%dT%H%M%SZ)"

echo "MP_A5R QUEUE LAUNCH  base=$BASE  cpuset=$CPUSET  launcher_md5=$GOT"
exec bash "$LAUNCHER"
