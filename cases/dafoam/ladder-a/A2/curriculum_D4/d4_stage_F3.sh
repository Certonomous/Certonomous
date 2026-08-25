#!/usr/bin/env bash
# D4 ARM-F RE-RUN STAGING, SECOND ATTEMPT (F3) -- carries the D4-DEF-6 repair.
#
# WHY F3 EXISTS.  Arm F2 ran with CORRECT UNITS and still failed, rc=1 at 3.733
# core-min, and the failure is NOT the D4-DEF-4 repair.  Both baseline primals
# converged and reproduced the acceptance primal's CD to ALL 17 DIGITS
# (0.021130918911049287); eta_raw came out at 3.81e-15.  The arm then died in
# `prob.compute_totals` with, from the log verbatim:
#
#     pyDAFoam Error: /mnt/F2/processor1/0.0001 already exists, moving failed!
#
# `DASolver.renameSolution(solution_counter)` (pyDAFoam.py:1543) renames the
# endTime write to a pseudo-time `0.000N`, counting from 1.  `cp -a O F2`
# carried across ARM O'S 84 PSEUDO-TIME DIRECTORIES `0.0001 .. 0.0082` and
# `1000`, so the very first rename collided.  THAT IS D4-DEF-6.
#
# AND IT IS INHERITED FROM `d4_stage_F.sh`, WHICH MEANS ARM F COULD NEVER HAVE
# COMPLETED EVEN WITH CORRECT UNITS.  The original arm F crashed on mesh quality
# 15 s in -- before the adjoint -- so D4-DEF-4 MASKED D4-DEF-6.  Two independent
# blockers on one arm, and fixing only the first would have bought a second
# crash at a higher price.  This is exactly why the ruling made a solve, not an
# argument, the precondition of the freeze.
#
# THE REPAIR, and what it may and may not touch.  Step (f) removes ARM O'S
# OUTPUT TIME DIRECTORIES FROM THE COPY ONLY.  It removes no input: `0/`,
# `constant/`, `system/`, `OptView.hst` and `dRdWColoring_4.bin` all stay, so
# the arm keeps the colouring its 53.0 core-min prediction was priced on.  It
# removes nothing from `O/`, and step (f) ASSERTS that afterwards.  This brings
# the staged tree into line with the FROZEN launcher's OWN cold-start standard,
# which refuses any arm whose work dir already carries `processor*` outputs, a
# time directory or `reports/` -- a standard arm F was exempted from by the
# `$BASE/$ARM` convention and should not have been.
#
# NO GATE, THRESHOLD, BAND, CAP OR LABEL MOVES.
#
# ACC-1 PASSED at 2026-08-25T21:53Z: CD = 0.021130918911049287 against arm O's
# IPOPT objective 2.1125978108239574e-02, rel_CD = 2.3387e-04 inside the band
# 1.0e-3 registered BEFORE the primal ran.  The D4-DEF-4 repair is FROZEN and
# this is the arm it unblocks.
#
# WHY A NEW DIRECTORY AND NOT `F/`.  `F/` holds arm F's crash evidence, and
# VERIFICATION_CHARTER.md 2d.1 condition (4) requires the pre-repair values to
# be preserved.  `F/d4_endpoint_dvs.json` is therefore NEVER TOUCHED: the
# acceptance primal took its own tree `ACC/`, and this re-run takes a THIRD,
# `F2/`.  Nothing is rewritten anywhere and `F/` is never opened for writing.
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
# SECOND, STRICTLY LATER datum `.d4_stage_F3_copy_epoch` dates THIS arm, and
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
DST="$BASE/F3"
EV="$BASE/F3_STAGING_EVIDENCE.txt"

: > "$EV"
say() { echo "$*" | tee -a "$EV"; }

say "D4_STAGE_F3 utc=$(date -u +%Y%m%dT%H%M%SZ)"

# ---- (a) COPY, NEVER MOVE.  Source must exist and must survive. ----------
test -d "$SRC" || { say "ABORT (a) source $SRC absent"; exit 5; }
test -f "$SRC/OptView.hst" || { say "ABORT (a) $SRC/OptView.hst absent -- no endpoint to read"; exit 5; }
test ! -e "$DST" || { say "ABORT (a) destination $DST already exists -- refusing to overwrite evidence"; exit 5; }
say "D4_STAGE_F3 (a) OK src=$SRC exists, OptView.hst present, dst=$DST does not exist"

# ---- (b) THE ANSWER FILES MUST NOT PRE-EXIST. ---------------------------
N=$(find "$SRC" \( -name 'd4_endpoint_dvs*.json' -o -name 'd4_fd_endpoint.jsonl' -o -name 'd4_fd_endpoint.json*' \) 2>/dev/null | wc -l)
say "D4_STAGE_F3 (b) ASSERTION: count of pre-existing answer files under $SRC = $N (required 0)"
if [ "$N" -ne 0 ]; then
  find "$SRC" \( -name 'd4_endpoint_dvs*.json' -o -name 'd4_fd_endpoint.jsonl' -o -name 'd4_fd_endpoint.json*' \) 2>/dev/null | tee -a "$EV"
  say "ABORT (b) an answer file exists BEFORE the arm that must produce it"; exit 5
fi
say "D4_STAGE_F3 (b) OK"

# ---- (c) THE REFERENCE MESH IS THE UNDEFORMED ONE, RE-ASSERTED HERE ------
# The comment above records the measurement; this is the assertion that makes
# it a guard rather than a note.  If arm O had left a deformed reference mesh,
# the acceptance primal could fail for a reason unrelated to D4-DEF-4.
MB=$(md5sum "$BASE/base/constant/polyMesh/points.gz" | cut -d' ' -f1)
MS=$(md5sum "$SRC/constant/polyMesh/points.gz" | cut -d' ' -f1)
say "D4_STAGE_F3 (c) reference mesh md5 base=$MB src=$MS"
test "$MB" = "$MS" || { say "ABORT (c) $SRC carries a DEFORMED reference mesh -- staging from it would double-deform the wing"; exit 5; }
say "D4_STAGE_F3 (c) OK -- undeformed reference mesh, double-deformation confound eliminated by measurement"

# ---- (d) COPY, with mtime semantics PINNED and a second datum written ----
say "D4_STAGE_F3 (d) mtime semantics = cp -a, PRESERVE"
COPY_EPOCH=$(date -u +%s)
cp -a "$SRC" "$DST" || { say "ABORT (d) copy failed"; exit 4; }
echo "$COPY_EPOCH" > "$DST/.d4_stage_F3_copy_epoch" || { say "ABORT (d) cannot write copy datum"; exit 4; }
say "D4_STAGE_F3 (d) copied, copy_epoch=$COPY_EPOCH written to .d4_stage_F3_copy_epoch"
say "D4_STAGE_F3 (d) arm O age datum carried over = $(cat "$DST/.d4_age_datum" 2>/dev/null || echo ABSENT)"

test -f "$SRC/OptView.hst" || { say "ABORT (a) source lost OptView.hst after copy"; exit 5; }
test -f "$SRC/opt_IPOPT.txt" || { say "ABORT (a) source lost opt_IPOPT.txt after copy"; exit 5; }
say "D4_STAGE_F3 (a) POST-COPY: source intact"

N2=$(find "$DST" \( -name 'd4_endpoint_dvs*.json' -o -name 'd4_fd_endpoint.jsonl' -o -name 'd4_fd_endpoint.json*' \) 2>/dev/null | wc -l)
say "D4_STAGE_F3 (b) POST-COPY assertion: answer files under $DST = $N2 (required 0)"
[ "$N2" -eq 0 ] || { say "ABORT (b) answer file appeared in destination"; exit 5; }

# ---- (e) stage the REPAIR instruments into the run root ------------------
for f in d4_endpoint_locus.py d4_endpoint_physical.py d4_fd_endpoint.py; do
  cp -a "$CASE/$f" "$BASE/$f" || { say "ABORT (e) cannot stage $f"; exit 4; }
  say "D4_STAGE_F3 (e) staged $f md5 $(md5sum "$BASE/$f" | cut -d' ' -f1)"
done

# ---- (f) THE D4-DEF-6 REPAIR: drop ARM O'S OUTPUT TIME DIRECTORIES ------
# Inputs are untouched.  A directory is removed only if its name parses as a
# number and is not the start time 0.  The count removed is ASSERTED NON-ZERO
# -- a repair that removes nothing is not a repair, it is a no-op wearing one.
NREM=0
for d in "$DST"/processor*/*/ "$DST"/*/; do
  b=$(basename "$d")
  case "$b" in
    0|constant|system|0.orig|FFD|postProcessing|reports) continue ;;
  esac
  if echo "$b" | grep -qE '^[0-9]+(\.[0-9]+)?$'; then
    rm -rf "$d" || { say "ABORT (f) cannot remove $d"; exit 4; }
    NREM=$((NREM+1))
  fi
done
if [ -e "$DST/reports" ]; then rm -rf "$DST/reports" || { say "ABORT (f) cannot remove reports"; exit 4; }; NREM=$((NREM+1)); fi
say "D4_STAGE_F3 (f) removed $NREM arm-O output directories from the COPY"
[ "$NREM" -gt 0 ] || { say "ABORT (f) removed ZERO directories -- a repair that removes nothing is a no-op, not a repair"; exit 5; }

# POST-ASSERTIONS.  None of these can pass by accident.
NLEFT=$(find "$DST" -maxdepth 2 -type d -regextype posix-extended -regex '.*/(processor[0-9]+/)?[0-9]+\.[0-9]+' ! -name '0' 2>/dev/null | wc -l)
say "D4_STAGE_F3 (f) pseudo-time directories remaining under $DST = $NLEFT (required 0)"
[ "$NLEFT" -eq 0 ] || { say "ABORT (f) pseudo-time directories survive -- renameSolution will collide again"; exit 5; }
test -f "$DST/processor0/0/U.gz" || { say "ABORT (f) the START-TIME FIELDS were removed -- the repair overreached"; exit 5; }
test -f "$DST/OptView.hst" || { say "ABORT (f) OptView.hst removed -- no endpoint to read"; exit 5; }
test -f "$DST/dRdWColoring_4.bin" || { say "ABORT (f) colouring removed -- the arm would be repriced"; exit 5; }
test -f "$DST/constant/polyMesh/points.gz" || { say "ABORT (f) reference mesh removed"; exit 5; }
NSRC=$(ls -d "$SRC"/processor0/[0-9]*/ 2>/dev/null | wc -l)
say "D4_STAGE_F3 (f) SOURCE INTACT assertion: time directories under $SRC/processor0 = $NSRC (required > 1, arm O's evidence is NOT touched)"
[ "$NSRC" -gt 1 ] || { say "ABORT (f) the source tree lost its time directories -- this script removed arm O's evidence"; exit 5; }
say "D4_STAGE_F3 (f) OK -- outputs dropped from the copy, inputs and source intact"

say "D4_STAGE_F3 READY -- invoke d4_run_F3.sh <image> <cpuset>"
