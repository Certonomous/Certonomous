#!/usr/bin/env bash
# D4 ACCEPTANCE-PRIMAL STAGING -- LIMIT 1 of the D4-DEF-4 ruling.
#
# WHY A NEW DIRECTORY AND NOT `F/`.  `F/` holds arm F's crash evidence, and
# VERIFICATION_CHARTER.md 2d.1 condition (4) requires the pre-repair values to
# be preserved.  `F/d4_endpoint_dvs.json` is therefore NEVER TOUCHED: the
# acceptance primal gets its own tree, `ACC/`, and arm F's re-run will get a
# third, `F2/`.  Nothing is rewritten anywhere.
#
# AND `F/` IS NOT RE-RUNNABLE IN PLACE, which is a MEASUREMENT and not a
# preference.  The crashed arm F rewrote `F/processor*/0/{U,T,nuTilda}.gz` at
# 21:13 -- DAFoam wrote the initial fields with the corrupted `patchV`, i.e. a
# 10 m/s freestream instead of 100 m/s.  A re-run in place would start from
# those fields.  (It did NOT corrupt the mesh: `F/processor0/0/polyMesh`
# contains only an empty `sets/`, and `F/constant/polyMesh/points.gz` still
# hashes to 0fb1935a9b8781b73ac4ccb136e3ec68 -- identical to `base/` and `O/`.)
#
# THE UNDEFORMED REFERENCE MESH IS THE SAME IN ALL THREE TREES, MEASURED.
# This matters more than it looks.  IDWarp and DVGeo take their REFERENCE
# geometry from the mesh on disk at `prob.setup()`.  Had arm O left a DEFORMED
# mesh in `constant/polyMesh`, applying the endpoint design variables to a tree
# copied from `O/` would DOUBLE-DEFORM the wing and the acceptance primal would
# fail to reproduce arm O's objective FOR A REASON THAT HAS NOTHING TO DO WITH
# D4-DEF-4 -- a false negative that would have withdrawn a correct diagnosis.
# It does not arise: `md5sum */constant/polyMesh/points.gz` is
# 0fb1935a9b8781b73ac4ccb136e3ec68 for base, O and F alike, mtime 2026-07-28,
# untouched by any arm.  The confound is ELIMINATED BY MEASUREMENT, not assumed
# away, and this comment is where that measurement is recorded.
#
# THE AGE DATUM.  `cp -a` PRESERVES mtimes, so the staged tree carries arm O's
# timestamps and arm O's own datum keeps meaning exactly what it meant.  A
# SECOND, STRICTLY LATER datum `.d4_stage_ACC_copy_epoch` dates THIS arm, and
# `d4_endpoint_physical.py --age-datum` refuses any artifact not strictly newer
# than it.  An age guard keyed to the carried-over datum would pass every
# arm-O artifact in the tree; a guard that cannot fail is not a guard.
#
# `set -e` does NOT gate at the top level and `( set -e; ... )` does not either.
# Every step gates explicitly with || { echo ABORT...; exit N; }.
set -uo pipefail

BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
CASE=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D4
SRC="$BASE/O"
DST="$BASE/ACC"
EV="$BASE/ACC_STAGING_EVIDENCE.txt"

: > "$EV"
say() { echo "$*" | tee -a "$EV"; }

say "D4_STAGE_ACC utc=$(date -u +%Y%m%dT%H%M%SZ)"

# ---- (a) COPY, NEVER MOVE.  Source must exist and must survive. ----------
test -d "$SRC" || { say "ABORT (a) source $SRC absent"; exit 5; }
test -f "$SRC/OptView.hst" || { say "ABORT (a) $SRC/OptView.hst absent -- no endpoint to read"; exit 5; }
test ! -e "$DST" || { say "ABORT (a) destination $DST already exists -- refusing to overwrite evidence"; exit 5; }
say "D4_STAGE_ACC (a) OK src=$SRC exists, OptView.hst present, dst=$DST does not exist"

# ---- (b) THE ANSWER FILES MUST NOT PRE-EXIST. ---------------------------
N=$(find "$SRC" \( -name 'd4_endpoint_dvs*.json' -o -name 'd4_accept_primal.json' -o -name 'd4_fd_endpoint.json*' \) 2>/dev/null | wc -l)
say "D4_STAGE_ACC (b) ASSERTION: count of pre-existing answer files under $SRC = $N (required 0)"
if [ "$N" -ne 0 ]; then
  find "$SRC" \( -name 'd4_endpoint_dvs*.json' -o -name 'd4_accept_primal.json' -o -name 'd4_fd_endpoint.json*' \) 2>/dev/null | tee -a "$EV"
  say "ABORT (b) an answer file exists BEFORE the arm that must produce it"; exit 5
fi
say "D4_STAGE_ACC (b) OK"

# ---- (c) THE REFERENCE MESH IS THE UNDEFORMED ONE, RE-ASSERTED HERE ------
# The comment above records the measurement; this is the assertion that makes
# it a guard rather than a note.  If arm O had left a deformed reference mesh,
# the acceptance primal could fail for a reason unrelated to D4-DEF-4.
MB=$(md5sum "$BASE/base/constant/polyMesh/points.gz" | cut -d' ' -f1)
MS=$(md5sum "$SRC/constant/polyMesh/points.gz" | cut -d' ' -f1)
say "D4_STAGE_ACC (c) reference mesh md5 base=$MB src=$MS"
test "$MB" = "$MS" || { say "ABORT (c) $SRC carries a DEFORMED reference mesh -- staging from it would double-deform the wing"; exit 5; }
say "D4_STAGE_ACC (c) OK -- undeformed reference mesh, double-deformation confound eliminated by measurement"

# ---- (d) COPY, with mtime semantics PINNED and a second datum written ----
say "D4_STAGE_ACC (d) mtime semantics = cp -a, PRESERVE"
COPY_EPOCH=$(date -u +%s)
cp -a "$SRC" "$DST" || { say "ABORT (d) copy failed"; exit 4; }
echo "$COPY_EPOCH" > "$DST/.d4_stage_ACC_copy_epoch" || { say "ABORT (d) cannot write copy datum"; exit 4; }
say "D4_STAGE_ACC (d) copied, copy_epoch=$COPY_EPOCH written to .d4_stage_ACC_copy_epoch"
say "D4_STAGE_ACC (d) arm O age datum carried over = $(cat "$DST/.d4_age_datum" 2>/dev/null || echo ABSENT)"

test -f "$SRC/OptView.hst" || { say "ABORT (a) source lost OptView.hst after copy"; exit 5; }
test -f "$SRC/opt_IPOPT.txt" || { say "ABORT (a) source lost opt_IPOPT.txt after copy"; exit 5; }
say "D4_STAGE_ACC (a) POST-COPY: source intact"

N2=$(find "$DST" \( -name 'd4_endpoint_dvs*.json' -o -name 'd4_accept_primal.json' -o -name 'd4_fd_endpoint.json*' \) 2>/dev/null | wc -l)
say "D4_STAGE_ACC (b) POST-COPY assertion: answer files under $DST = $N2 (required 0)"
[ "$N2" -eq 0 ] || { say "ABORT (b) answer file appeared in destination"; exit 5; }

# ---- (e) stage the REPAIR instruments into the run root ------------------
for f in d4_endpoint_locus.py d4_endpoint_physical.py d4_accept_primal.py d4_accept_compare.py; do
  cp -a "$CASE/$f" "$BASE/$f" || { say "ABORT (e) cannot stage $f"; exit 4; }
  say "D4_STAGE_ACC (e) staged $f md5 $(md5sum "$BASE/$f" | cut -d' ' -f1)"
done

say "D4_STAGE_ACC READY -- invoke d4_run_acc.sh <image> <cpuset>"
