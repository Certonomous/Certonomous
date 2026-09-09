#!/usr/bin/env bash
# stage_m1c.sh -- M1-C staging wrapper.  FROZEN 2026-09-09 (§3 check-1 done, SOUND).
#
# STATUS: NOT FROZEN, NOT COMMITTED, NOT RUN by the drafting lane.  It stages the
# SIX capped M1 arms into a FRESH run root, from the read-only benchmark tree,
# using the frozen M1 stage_m1.py VERBATIM (no new staging logic here).  It MUST
# be run only AFTER the closure-supervisor has committed the M1-C pre-registration
# (SUPERVISION_CHARTER sec3 check 4), and it stages from whatever stage_m1.py blob
# that freeze commit fixes.
#
# rule-4 age guard: stage_m1.py touches 0/U LAST and its post-guard R6_no_time_dirs
# refuses any destination that already holds a time directory.  This wrapper NEVER
# writes into /home/ubuntu/closure-data/multimodel_sweep (the M1 evidence tree);
# it writes ONLY into the disjoint M1-C tree below.  It stages CLEAN from 0/ --
# it does NOT reuse the timed-out run dirs' output (there is none but 0/ anyway).
set -euo pipefail

STAGER="/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/M1_multimodel_sweep/stage_m1.py"
SRC="/home/ubuntu/closure-challenge-benchmark/data"        # read-only benchmark, M1's own --src-root
DST="/home/ubuntu/closure-data/m1c_completion"             # disjoint M1-C run root

# The six arms, PH_Breuer FIRST (matches the queue drop order and the cap table).
# arm:case
ARMS=(
  "kOmega:PH_Breuer"
  "kOmegaSST_null:PH_Breuer"
  "kOmega:AR_14_Ret_180"
  "kOmega:AR_7_Ret_180"
  "kOmega:AR_1_Ret_180"
  "kOmegaSST_null:AR_1_Ret_180"
)

DRYRUN=1
[ "${1:-}" = "--execute" ] && DRYRUN=0

for pair in "${ARMS[@]}"; do
  arm="${pair%%:*}"; case="${pair##*:}"
  dstdir="$DST/$arm/$case"
  # Fail-closed birth check BEFORE staging: destination must exist and hold no time dir.
  if [ -e "$dstdir/0" ] || ls -d "$dstdir"/[1-9]* >/dev/null 2>&1; then
    echo "REFUSE: $dstdir already holds 0/ or a time dir -- age guard; not staging" >&2
    exit 2
  fi
  if [ "$DRYRUN" = 1 ]; then
    echo "DRYRUN would stage: python3 $STAGER --src-root $SRC --dst-root $DST --arm $arm --case $case --execute"
  else
    echo "STAGING $arm/$case ..."
    python3 "$STAGER" --src-root "$SRC" --dst-root "$DST" --arm "$arm" --case "$case" --execute
  fi
done

[ "$DRYRUN" = 1 ] && echo "DRYRUN complete -- pass --execute to actually stage (post-freeze only)."
