#!/usr/bin/env bash
# D4 ARM-F STAGING -- added by the arm-O lane 2026-08-25 under a dated departure.
#
# WHY IT EXISTS.  d4_run_arm.sh:136 derives WORK="$BASE/$ARM", so arm F resolves
# to $BASE/F -- a directory NO ARM CREATES.  Arm O's tree is $BASE/O.  Run as
# written, arm F aborts at exit 5 having computed nothing, while the comment on
# that very line states the intent that arm F operate on ARM O'S TREE.  The
# $BASE/$ARM convention silently defeats the documented intent.
#
#
# ---------------------------------------------------------------------------
# FILED INTO THE CASE DIRECTORY 2026-08-25T21:11Z by the arm-F lane.
# This script was written by the arm-O lane and left UNTRACKED in the run root,
# where no reader of the repository could see it.  RESULTS.md 9 cited it as the
# first half of the command pair that unblocks the rung while the file existed
# nowhere in git.  This filing supplies it.  The arm-O lane's text is preserved
# VERBATIM; the ONLY addition is this header block, and the script had NEVER
# BEEN RUN when it was made (no F_STAGING_EVIDENCE.txt existed), so no result
# anywhere depends on the earlier bytes.  md5 as written by the arm-O lane:
# 8b3ffbd8e07e01b4914edddebc8c9bc3.
#
# THE AGE DATUM AFTER STAGING -- stated explicitly, because staging is the one
# operation that can silently destroy its meaning (CLAUDE.md rule 4).
#
# Arm O's datum is $BASE/O/.d4_age_datum = 1787681557.  The FROZEN launcher
# wrote it at arm O's stage time as `stat -c %Y` of O/0/U, after touching 0/*
# last, and it MEANS: "arm O's cold start -- every artifact arm O produced must
# be strictly newer than this epoch."
#
# `cp -a` PRESERVES mtimes.  So after this script runs:
#   * F/0/U carries mtime 1787681557                    -- UNCHANGED
#   * F/.d4_age_datum reads 1787681557                  -- UNCHANGED
# The copied datum therefore still equals `stat -c %Y` of the copied 0/U, and
# arm O's datum means after staging exactly what it meant before it.  Nothing
# is re-derived, nothing is re-touched, nothing is back-dated: staging writes
# no new 0/ mtime at all.  That is why (c) below pins `cp -a` and says so.
#
# AND THAT DATUM IS NOT SUFFICIENT FOR ARM F.  This is the point.  Every
# artifact under F/ that ARM O produced -- OptView.hst, opt_IPOPT.txt,
# processor*/, reports/, dRdWColoring_4.bin -- is ALREADY strictly newer than
# 1787681557.  An age guard keyed to the carried-over datum would pass all of
# them while they were produced by a DIFFERENT ARM.  A guard that cannot fail
# is not a guard.
#
# Arm F therefore gets a SECOND, STRICTLY LATER datum: .d4_stage_F_copy_epoch,
# the UTC epoch of this copy, written by step (c).  Arm F's OWN answer
# artifacts -- d4_endpoint_dvs.json, d4_major_history.json, d4_fd_endpoint.json
# and d4_fd_endpoint.jsonl -- must be strictly newer than THAT epoch, or they
# did not come from arm F and are not arm F's evidence.
#
# The two data live in two separate files precisely so they can never be
# conflated: 1787681557 dates ARM O, the copy epoch dates ARM F.  Grading arm F
# against arm O's datum is the failure this block exists to prevent.
# ---------------------------------------------------------------------------
# THE FROZEN LAUNCHER IS NOT EDITED (md5 399957c6..., PREREGISTRATION.md 9a).
# This script SATISFIES the launcher's own stated precondition instead.  It
# alters NO gate, threshold, cap or label.
#
# `set -e` does NOT gate at the top level and `( set -e; ... )` does not either.
# Every step gates explicitly with || { echo ABORT...; exit N; }.
set -uo pipefail

BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
SRC="$BASE/O"
DST="$BASE/F"
EV="$BASE/F_STAGING_EVIDENCE.txt"

: > "$EV"
say() { echo "$*" | tee -a "$EV"; }

say "D4_STAGE_F utc=$(date -u +%Y%m%dT%H%M%SZ)"

# ---- (a) COPY, NEVER MOVE.  Source must exist and must survive. ----------
test -d "$SRC" || { say "ABORT (a) source $SRC absent"; exit 5; }
test -f "$SRC/OptView.hst" || { say "ABORT (a) $SRC/OptView.hst absent -- no endpoint to read"; exit 5; }
test ! -e "$DST" || { say "ABORT (a) destination $DST already exists -- refusing to overwrite evidence"; exit 5; }
say "D4_STAGE_F (a) OK src=$SRC exists, OptView.hst present, dst=$DST does not exist"

# ---- (b) THE ANSWER FILE MUST NOT PRE-EXIST.  Supervisor condition (b). ---
# The grader's coherence check cannot distinguish "arm F computed this table"
# from "a table was already lying there".  An answer file present BEFORE the arm
# that is supposed to produce it is the exact shape of a false result.
N_FD=$(find "$SRC" -name 'd4_fd_endpoint.json' -o -name 'd4_fd_endpoint.jsonl' -o -name 'd4_endpoint_dvs.json' 2>/dev/null | wc -l)
say "D4_STAGE_F (b) ASSERTION: count of pre-existing answer files under $SRC = $N_FD (required 0)"
if [ "$N_FD" -ne 0 ]; then
  say "D4_STAGE_F (b) OFFENDING PATHS:"
  find "$SRC" -name 'd4_fd_endpoint.json' -o -name 'd4_fd_endpoint.jsonl' -o -name 'd4_endpoint_dvs.json' 2>/dev/null | tee -a "$EV"
  say "ABORT (b) an answer file exists BEFORE the arm that must produce it"
  exit 5
fi
say "D4_STAGE_F (b) OK -- no d4_fd_endpoint.json / .jsonl / d4_endpoint_dvs.json anywhere under $SRC"

# ---- (c) MTIME SEMANTICS, PINNED AND STATED. -----------------------------
# `cp -a` PRESERVES mtimes; plain `cp` resets them to now.  Either choice
# changes what the age guard MEANS.  We use `cp -a` (preserve), so the staged
# tree carries ARM O's timestamps, and we write a SEPARATE cold-start datum
# recording the COPY time so the two are never conflated.
say "D4_STAGE_F (c) mtime semantics = cp -a, PRESERVE (staged tree carries arm O's mtimes)"
COPY_EPOCH=$(date -u +%s)
cp -a "$SRC" "$DST" || { say "ABORT (c) copy failed"; exit 4; }
say "$COPY_EPOCH" > /dev/null
echo "$COPY_EPOCH" > "$DST/.d4_stage_F_copy_epoch" || { say "ABORT (c) cannot write copy datum"; exit 4; }
say "D4_STAGE_F (c) copied, copy_epoch=$COPY_EPOCH written to .d4_stage_F_copy_epoch"
say "D4_STAGE_F (c) arm O age datum carried over = $(cat "$DST/.d4_age_datum" 2>/dev/null || echo ABSENT)"

# The source must be UNHARMED by the copy.
test -f "$SRC/OptView.hst" || { say "ABORT (a) source lost OptView.hst after copy"; exit 5; }
test -f "$SRC/opt_IPOPT.txt" || { say "ABORT (a) source lost opt_IPOPT.txt after copy"; exit 5; }
say "D4_STAGE_F (a) POST-COPY: source intact -- OptView.hst and opt_IPOPT.txt still present in $SRC"

# The destination must NOT carry an answer file even after the copy.
N_FD2=$(find "$DST" -name 'd4_fd_endpoint.json' -o -name 'd4_fd_endpoint.jsonl' -o -name 'd4_endpoint_dvs.json' 2>/dev/null | wc -l)
say "D4_STAGE_F (b) POST-COPY assertion: answer files under $DST = $N_FD2 (required 0)"
[ "$N_FD2" -eq 0 ] || { say "ABORT (b) answer file appeared in destination"; exit 5; }

say "D4_STAGE_F READY -- invoke the FROZEN launcher unmodified: d4_run_arm.sh F dafoam-idwarp-rot:v1"
