#!/usr/bin/env bash
# =============================================================================
# A1WRT UNIT LAUNCHER -- the wall-resolved alpha-tail, incompressible only.
#
#   alpha12_symmetry   U1   `symmetry`, COLD, alpha = 12          cap  361 core-min
#   tail_empty         U2+U3 `empty`, COLD alpha=12 then 13..18   cap 2943 core-min
#
# ONE UNIT = ONE CONTAINER = ONE PROCESS = np 1 on ONE cpuset core, carried
# unchanged from A1WR (Addendum A section 13.5, Addendum B sections 14.2/14.3).
# The in-container program is A1WR's own `a1wr_cmd.sh`, INHERITED BY MD5 AND NOT
# MODIFIED: U1 is its COLD mode with a one-element alpha list, U2+U3 its
# CONTINUED mode with seven.  Nothing about the discretisation, the numerics or
# the build moves -- changing any of them would make the tail non-comparable to
# the alpha 0..12 body it extends, the two-variable trap A1WR refused four times.
#
# DERIVED from curriculum_D6RF/d6rf_run_arm.sh, which is this family's standard.
# THE DELTAS, enumerated, so a reader does not have to diff to find them:
#   1  two units, not two arms; caps 361.0 / 2943.0 and an ITEM CEILING of 3304.0
#      asserted BEFORE EVERY UNIT against the ledger's own accumulated spend
#   2  THE FRAME ALLOWANCE IS 300 s, NOT 90 AND NOT 60.  See the cap frame below:
#      this lineage's constant is registered at PREREGISTRATION section 4.4 and
#      differs from D6R/D6RF (90) and from A1/D19 (60).  It is re-derived here at
#      run time and back-checked; it is never trusted from a table.
#   3  G-PATCH clauses 1 and 2 host-side, PRE-PRIMAL, through
#      a1wrt_patch_assert.py -- the `empty` unit's whole reason for existing.
#      Clause 3 (the solver's own `Mesh has N solution (non-empty) directions`
#      line) is read AFTER, by a1wrt_read.py, because it is a MEASUREMENT the
#      solver makes about itself and cannot be taken before it runs.
#   4  G-OCC RECORDS AND QUEUES.  IT NEVER REFUSES.  G-QUIET's refuse-to-launch
#      form is ruled out of this family (dafoam-supervisor, 2026-09-03).
#   5  NO `rm -rf` OF ANY KIND IS EXECUTED BY THIS FILE.  A pre-existing unit
#      directory is REFUSED, never removed; recovery is an explicit `mv`.
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call, and
# `( set -e; ... )` does not gate either.  Every step gates explicitly with
# `|| { echo ABORT...; exit N; }`.
#
# NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives the unit
# and the KERNEL's verdict is read, not the harness's.  NOTHING here reads `$?`
# of a `setsid` or a `timeout` line: the setsid parent returns 0 for EVERY
# outcome, which is why the rc is taken from `docker inspect` below and why the
# deadline lives INSIDE the container.
#
# REGISTERED EXIT CODES:
#   0   the unit's own rc, from docker inspect .State.ExitCode
#   3   G-ROOT refusal (wrong base, another item's root, a live unit, a live driver)
#   4   identity / staging failure (an md5, the image digest, a copy)
#   5   G-COLDSTART or a staging assertion
#   6   controlDict REFUSAL -- distinct, and it is a1wrt_controldict.py's own
#       RC_CD_REFUSAL, so the launcher and the instrument agree on one number
#   7   G-PATCH REFUSAL -- distinct, and never a default
#   64  usage / unknown unit
#   65  cap arithmetic, or the ITEM CEILING
# =============================================================================
set -uo pipefail

ITEM=A1WRT
REGISTERED_BASE=/home/ubuntu/certonomous-runs/A1WRT
BASE="${BASE:-$REGISTERED_BASE}"
BASE_REAL=$(realpath -m "$BASE")
REG_REAL=$(realpath -m "$REGISTERED_BASE")
RUNS_DIR=/home/ubuntu/certonomous-runs
A1WR_ROOT=/home/ubuntu/certonomous-runs/A1WR
MESH_SRC="$A1WR_ROOT/L3"
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

RANKS=1
ENDTIME=4000
PRIMAL_TOL=1e-8          # primalMinResTol, CARRIED UNCHANGED.  Not relaxed here
                         # and not relaxable: PREREGISTRATION section 7's closing
                         # clause forbids it by name, and G-REPRO's comparison
                         # against A1WR's own alpha=12 series is only valid at it.

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER section 6)
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35

# ---- FROZEN INSTRUMENTS, inherited unchanged from the A1WR freeze -----------
MD5_RUNSCRIPT=d48f48c5e2e41e86981acbf6feccb3c4     # a1wr_runScript_incomp.py
MD5_CMD=eba014f2c538611d2249c3fcf9b3ddd7           # a1wr_cmd.sh
MD5_IDWARP=85f59e87253e0a71a813f64ca6e4c425        # libidwarp.so, in-container
A1WR_CASE_DIR=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar
# ---- THE FFD, AND WHY IT IS TAKEN FROM `sweep_I` AND NOT FROM ANYWHERE ELSE --
# The producer loads `FFD/wingFFD.xyz` relative to its own cwd (a1wr_cmd.sh:29
# `cd /mnt/case`, and this launcher mounts `-v $WORK:/mnt/case`), so the staged
# copy must land at `$WORK/FFD/wingFFD.xyz` and nowhere else.  MEASURED, not
# assumed: `FFD/wingFFD.xyz` is the ONLY external file the producer opens --
# a1wr_runScript_incomp.py has exactly one such reference, at :129.
#
# THE CENSUS, SCOPED -- AND THE SCOPE IS THE POINT.  Within A1WR'S OWN RUN ROOT
# there are THIRTEEN wingFFD.xyz files and ALL THIRTEEN carry md5
# 6ddf378b028d03d8a18270488bee1759: its TEN STAGE12 unit cases (sweep_I, sweep_C,
# cold_{I,C}_{4,14,17}, probe_I, probe_C), TWO in STAGE12_failed_meshcheck and
# ONE in STAGE12_failed_staging.  The incompressible SKELETON A1WR's driver
# copies from (a1wr_chain_driver.sh:33, SKEL_I) carries the same md5, making
# FOURTEEN.  These bytes are NOT globally unique and this comment does not claim
# they are: box-wide there are 484 files of this name carrying NINE distinct
# md5s, because a different geometry gets a different FFD.  The claim is the
# scoped one -- inside the item A1WRT is being compared against, the FFD does not
# vary -- and it is the only one the one-variable argument needs.  So the CHOICE
# of path cannot move a byte today, and it is made on provenance instead:
#   `sweep_I/case` IS the alpha 0..12 incompressible sweep this item's tail
#   extends -- driver line 239, CONTINUED, tol 1.0e-8, endTime 4000, the exact
#   configuration G-REPRO compares against.  These are the bytes the BODY's
#   numbers were produced with, not a template they were copied from.
# It is also INSIDE A1WR's preserved run root, which this launcher already
# treats as its single read-only source (MESH_SRC, and G-ROOT.1a names it).
# SKEL_I would be a SECOND external source, and it is a live curriculum
# directory another item may restage; the preserved root is the stabler pin.
FFD_SRC="$A1WR_ROOT/STAGE12/sweep_I/case/FFD/wingFFD.xyz"
MD5_FFD=6ddf378b028d03d8a18270488bee1759
# ---- THIS ITEM'S OWN INSTRUMENT, pinned by the freeze -----------------------
# Pinned AND DRIVEN below.  A declared-but-unused hash is decoration that reads
# like a guard, which is the same defect class as an unreachable check.
MD5_PATCH_ASSERT=7f3a2c8e70684daba975ac9a2ee50385
# The controlDict DERIVER.  S6 WRITES this item's control dictionary with it and
# reads it back with it, so it is an instrument of the same standing as the patch
# asserter and is pinned and DRIVEN at S0b on the same argument.
MD5_CONTROLDICT=a77c9bac486dce940707bdf9c00e1a6b   # a1wrt_controldict.py

UNIT="${1:-}"; IMG="${2:-}"
usage() { echo "ABORT usage: a1wrt_run_unit.sh <alpha12_symmetry|tail_empty> <image>"; exit 64; }
test -n "$UNIT" || usage
test -n "$IMG"  || usage
# THE UNIT GUARD IS AN EQUALITY, NOT A PREFIX MATCH.
case "$UNIT" in
  alpha12_symmetry|tail_empty) : ;;
  *) echo "ABORT unit '$UNIT' is not one of this item's two REGISTERED units."
     echo "  Eight points, three units, two containers (section 2.1).  A third"
     echo "  unit is a separate item with its own pre-registration.  REFUSED."
     exit 64 ;;
esac

# ---- the registered per-unit table ------------------------------------------
case "$UNIT" in
  alpha12_symmetry) CAP=361.0;  WANT_PATCH=symmetry; MODE=COLD;      ALPHAS="12" ;;
  tail_empty)       CAP=2943.0; WANT_PATCH=empty;    MODE=CONTINUED; ALPHAS="12 13 14 15 16 17 18" ;;
esac
DECLARED=$(set -- $ALPHAS; echo $#)
ITEM_CEILING=3304.0
MEM=8g
CPUSET="${A1WRT_CPUSET:-10}"

# =============================================================================
# G-ROOT.  Nothing below this block writes anything.
# =============================================================================
# ORDERING IS LOAD-BEARING AND IS THE FIRST THING TO READ HERE.
# G-ROOT.1 below is an EQUALITY against this item's own root, so it refuses every
# wrong base on its own -- which means any check placed AFTER it can never fire.
# An earlier form of this file put the A1WR-specific and enumerated-root guards
# after G-ROOT.1: both were unreachable, and pointing the launcher at A1WR's own
# root produced the generic "not this item's registered run root" instead of the
# message that says WHOSE evidence was just protected.  D6RF's own comment names
# the class -- "a guard that fires with the wrong message is a guard nobody
# learns from" -- and the same caller-side test applies to a guard as to a zero:
# a check that cannot be reached is indistinguishable from a check that does not
# exist.  THE SPECIFIC GUARDS THEREFORE RUN FIRST; the general one is the floor.
#
# G-ROOT.1a -- A1WR'S OWN ROOT IS THIS ITEM'S READ-ONLY SOURCE.  It holds the L3
# mesh both units stage from and the alpha 0..12 sweep this tail extends, and it
# is the one wrong base a reader is most likely to supply.
if [ "$BASE_REAL" = "$(realpath -m "$A1WR_ROOT")" ]; then
  echo "ABORT G-ROOT.1a BASE resolves to A1WR'S PRESERVED RUN ROOT: $A1WR_ROOT"
  echo "  That directory holds the L3 mesh this item stages from and the alpha"
  echo "  0..12 sweep this item's tail extends -- the body the whole item exists"
  echo "  to continue.  It is READ-ONLY here.  REFUSED."
  exit 3
fi
# G-ROOT.2 -- ENUMERATED FROM DISK at every launch and never carried as a frozen
# list: D6's frozen list named roots that do not exist and omitted eleven that
# do.  Reading the directory cannot go stale.  This fires BEFORE G-ROOT.1 so the
# refusal can NAME the item whose evidence it just protected.
if [ -d "$RUNS_DIR" ]; then
  while IFS= read -r forb; do
    [ -z "$forb" ] && continue
    [ "$forb" = "$REG_REAL" ] && continue
    if [ "$BASE_REAL" = "$forb" ]; then
      echo "ABORT G-ROOT.2 BASE resolves to ANOTHER ITEM'S RUN ROOT: $forb"
      echo "  THE ROOT JUST PROTECTED: $forb -- it holds another item's rows,"
      echo "  and this launcher would have staged a unit directory inside it."
      echo "  REFUSED before any staging."
      exit 3
    fi
  done <<< "$(find "$RUNS_DIR" -maxdepth 1 -mindepth 1 -type d -exec realpath -m {} \; 2>/dev/null)"
fi
# G-ROOT.1 -- THE FLOOR.  Everything the two specific guards did not name.
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
  echo "  given:      $BASE_REAL"
  echo "  registered: $REG_REAL"
  echo "  D4-LAUNCHER-DEF-1: a launcher pointed at another item's run root"
  echo "  writes into that item's graded arms.  REFUSED before any staging."
  exit 3
fi
# G-ROOT.3 -- the LEDGER must belong to this item and to no other.
LEDGER="$BASE/ledger.txt"
if [ -f "$LEDGER" ]; then
  FOREIGN=$(grep -a "^ITEM=" "$LEDGER" 2>/dev/null | grep -av "^ITEM=$ITEM$" | head -1)
  if [ -n "$FOREIGN" ]; then
    echo "ABORT G-ROOT.3 the ledger at $LEDGER carries another item: $FOREIGN"
    exit 3
  fi
fi
# G-ROOT.4 -- THE RUN ROOT ABSENCE, ASSERTED BY EXECUTION.  On the FIRST fire the
# whole root must be absent; that is the condition PREREGISTRATION section 0
# names and re-checks, and it is re-checked HERE because that check was taken at
# freeze time and is stale the moment it was written.
if [ ! -e "$BASE" ]; then
  echo "A1WRT_G_ROOT4 run root ABSENT (checked by execution, not asserted): $BASE"
  mkdir -p "$BASE" || { echo "ABORT cannot create $BASE"; exit 3; }
  chmod 777 "$BASE" 2>/dev/null
  echo "ITEM=$ITEM" > "$LEDGER"
else
  echo "A1WRT_G_ROOT4 run root PRESENT: $BASE -- a later unit of a live item"
fi
WORK="$BASE/$UNIT"
# G-ROOT.5 -- A UNIT DIRECTORY IS NEVER RE-STAGED AND NEVER REMOVED.  This file
# executes NO `rm -rf`.  A re-fire finds the stale directory and REFUSES; the
# recovery is an explicit archive (`mv`), never an implicit delete.  A1WRT's own
# registration requires the guard to refuse a case where `0` or a time dir
# already exists, and the S-29 pattern is the reason it is a refusal.
if [ -e "$WORK" ]; then
  echo "ABORT G-ROOT.5 $WORK already exists.  This launcher does not remove a"
  echo "  unit directory: it may hold a partial result whose ledger row stands."
  echo "  A re-fire needs it ARCHIVED by mv, not deleted here.  REFUSED."
  exit 3
fi
# G-ROOT.6 -- a LIVE container for this unit is never re-staged under.
LIVE=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^a1wrt_${UNIT}_" 2>/dev/null | grep "^a1wrt_${UNIT}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE" ]; then
  echo "ABORT G-ROOT.6 a RUNNING container already carries this unit: [$LIVE]  REFUSED."
  exit 3
fi
echo "A1WRT_G_ROOT_PASS item=$ITEM unit=$UNIT base=$BASE_REAL work_absent=yes live_same_unit=none"

# =============================================================================
# THE CAP FRAME.  RE-DERIVED AT RUN TIME AND BACK-CHECKED.  NEVER TRUSTED FROM
# A TABLE -- D19T was frozen, md5-pinned, gate-checked and launched TWICE with a
# deadline of exactly 0 s because nobody ever executed this arithmetic.
#
# THIS LINEAGE'S REGISTERED RESERVE IS 300, NOT 90 AND NOT 60.  All three
# constants live in this family and the difference is REGISTERED, not drift:
#   A1WRT      300  (PREREGISTRATION section 4.4; 3.2x the MEASURED 93.85 s
#                    container start on `a1wr_sweep_I`)
#   D6R/D6RF    90  (d6r_run_arm.sh:251)
#   A1/D19      60  (d19o_run_arm.sh:153)
# A supervisor handed this lane the 60 s form for THIS item on 2026-09-03; it is
# not this item's registered form and is not used.  The assertion below INVERTS
# and RE-ADDS the allowance, so no edit to it can silently widen the cap.
# =============================================================================
FRAME_ALLOWANCE_S=300
KILL_GRACE_S=60
TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)) - $FRAME_ALLOWANCE_S)") \
  || { echo "ABORT tmo calc"; exit 65; }
test "$TMO" -gt 0 || {
  echo "ABORT D19T IDENTITY: the ${FRAME_ALLOWANCE_S}s frame allowance consumes the"
  echo "  whole ${CAP} core-min cap at $RANKS rank(s); TMO=$TMO.  A unit whose"
  echo "  in-container deadline is not positive cannot run, and D19T proves that"
  echo "  is discovered here or not at all."
  exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % (($TMO+$FRAME_ALLOWANCE_S)*$RANKS/60.0))") \
  || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
cap, back = $CAP, $BACKCHECK
if abs(cap-back) > 0.02:
    sys.stderr.write('ABORT CAP MISMATCH registered=%r enforced_plus_allowance=%r\n' % (cap, back))
    sys.exit(1)
" || { echo "ABORT enforced cap + frame allowance != registered cap"; exit 65; }
echo "A1WRT_CAP_FRAME unit=$UNIT registered_core_min=$CAP ranks=$RANKS deadline_in_container_s=$TMO frame_allowance_s=$FRAME_ALLOWANCE_S kill_grace_s=$KILL_GRACE_S back_check_core_min=$BACKCHECK enforced_in_frame=container graded_in_frame=host_bracket_T0_T1"

# ---- THE ITEM CEILING, ASSERTED BEFORE EVERY UNIT --------------------------
# The per-unit cap protects the unit.  The ITEM CEILING protects the box from
# the item, and it is the figure a reader would otherwise have to add up by
# hand.  Spend so far is READ FROM THE LEDGER, and a ledger that exists but
# cannot be parsed is UNMEASURED -- which REFUSES, because an unknown prior
# spend plus this cap cannot be shown to fit under the ceiling.
SPENT=$(python3 -c "
import re, sys, os
p = '$LEDGER'
if not os.path.exists(p):
    print('0.0'); sys.exit()
tot = 0.0; rows = 0
try:
    for line in open(p, errors='replace'):
        m = re.search(r'\bcore_min=([0-9]+\.?[0-9]*)', line)
        if m:
            tot += float(m.group(1)); rows += 1
except Exception:
    print('UNMEASURED'); sys.exit()
print('%.3f' % tot)
" 2>/dev/null)
case "$SPENT" in
  ''|UNMEASURED)
    echo "ABORT ITEM CEILING: prior spend is UNMEASURED -- $LEDGER exists but could"
    echo "  not be parsed.  An unknown prior spend plus this unit's ${CAP} core-min"
    echo "  cap cannot be shown to fit under the ${ITEM_CEILING} ceiling, so this"
    echo "  refuses rather than assuming zero.  A zero that means 'could not read'"
    echo "  is a planted zero (CLAUDE.md rule 3)."
    exit 65 ;;
esac
python3 -c "
import sys
spent, cap, ceil = $SPENT, $CAP, $ITEM_CEILING
if spent + cap > ceil:
    sys.stderr.write('ABORT ITEM CEILING: %.3f core-min already spent + this unit\'s '
                     '%.1f cap = %.3f > the registered %.1f ceiling. An overrun '
                     'STOPS the run; it does not get a new budget.\n'
                     % (spent, cap, spent+cap, ceil))
    sys.exit(1)
print('A1WRT_ITEM_CEILING spent_core_min=%.3f + unit_cap=%.1f = %.3f <= ceiling=%.1f OK'
      % (spent, cap, spent+cap, ceil))
" || exit 65

# =============================================================================
# G-OCC.  IT RECORDS, AND IT QUEUES.  IT NEVER REFUSES.
#
# G-QUIET's refuse-to-launch form is ruled OUT of this family: a non-physics gate
# that blocks a run is exactly what Sanaa named on 2026-09-03 ~22:00Z, and an
# idle box is the failure.  So an occupancy this item cannot afford makes it
# WAIT, briefly and boundedly, and then LAUNCH ANYWAY with the mismatch RECORDED
# AS A PREDICTION -- her ~21:00Z rule: pre-registration predicts, the monitor
# watches, the grader judges afterward on the certificate.
#
# AND THE CENSUS IS SHOWN ABLE TO RETURN A NON-EMPTY ANSWER BEFORE AN EMPTY ONE
# IS ACCEPTED (rule 3 applied to a census): a census that cannot see a running
# container is not evidence that none is running.  This launcher's OWN container
# does not exist yet, so the proof uses the docker daemon's total count.
# =============================================================================
census() { sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^a1wrt_" | tr '\n' ',' | sed 's/,$//'; }
CENSUS_RC_PROBE=$(sudo -n docker ps -aq 2>/dev/null | wc -l)
CENSUS_LIVE=$(sudo -n docker ps -q 2>/dev/null | wc -l)
if ! sudo -n docker info >/dev/null 2>&1; then
  CENSUS_STATE=UNMEASURED
else
  CENSUS_STATE=MEASURED
fi
SIBLINGS_PRE=$(census)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
echo "A1WRT_OCC_CENSUS state=$CENSUS_STATE daemon_containers_total=$CENSUS_RC_PROBE daemon_containers_running=$CENSUS_LIVE siblings_pre=[$SIBLINGS_PRE] MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD"
if [ "$CENSUS_STATE" = "UNMEASURED" ]; then
  echo "A1WRT_OCC the container census is UNMEASURED (the docker daemon did not answer)."
  echo "  This is RECORDED, not treated as an empty box: an empty census from a"
  echo "  reader that cannot see anything is not evidence that nothing is running."
  echo "  G-OCC does not refuse, so the unit proceeds with the gap on the record."
fi
# The refusal POINT is still computed and printed, because the arithmetic is the
# finding even when it never fires: break-even s/it = TMO / (DECLARED*ENDTIME).
BREAKEVEN=$(python3 -c "print('%.5f' % ($TMO/float($DECLARED*$ENDTIME)))")
XSOLO=$(python3 -c "print('%.3f' % ($BREAKEVEN/0.4615))")
echo "A1WRT_OCC_ARITHMETIC unit=$UNIT iterations=$((DECLARED*ENDTIME)) deadline_s=$TMO break_even_s_per_it=$BREAKEVEN = ${XSOLO}x the MEASURED 0.4615 s/it solo rate; the worst occupancy ever measured on this box is 3.859x"
QUEUE_POLLS=0
QUEUE_MAX=60          # 60 x 30 s = 30 min, BOUNDED.  Waiting forever is idling.
while [ "$(python3 -c "print(1 if $CENSUS_LIVE >= 8 else 0)")" = "1" ] && [ "$QUEUE_POLLS" -lt "$QUEUE_MAX" ]; do
  QUEUE_POLLS=$((QUEUE_POLLS+1))
  echo "A1WRT_OCC_QUEUED poll=$QUEUE_POLLS/$QUEUE_MAX running=$CENSUS_LIVE -- QUEUEING, not refusing"
  sleep 30
  CENSUS_LIVE=$(sudo -n docker ps -q 2>/dev/null | wc -l)
done
if [ "$QUEUE_POLLS" -ge "$QUEUE_MAX" ]; then
  echo "A1WRT_OCC_PREDICTION unit=$UNIT the box stayed at >= 8 containers for the whole"
  echo "  ${QUEUE_MAX}-poll queue window.  LAUNCHING ANYWAY with the mismatch RECORDED:"
  echo "  predicted cost will exceed the solo estimate; the grader compares predicted"
  echo "  against actual at the MEASURED occupancy on the certificate.  Queueing is"
  echo "  not blocking, and neither is this."
fi

# =============================================================================
# STAGING.  Every step aborts rather than degrading and writes its own evidence.
# =============================================================================
STAGE_EVID="$BASE/${UNIT}_STAGING_EVIDENCE.txt"
stage_say() { echo "$*"; echo "$*" >> "$STAGE_EVID"; }
: > "$STAGE_EVID"
stage_say "A1WRT_STAGE unit=$UNIT utc=$(date -u +%Y%m%dT%H%M%SZ) base=$BASE_REAL want_patch=$WANT_PATCH mode=$MODE alphas=[$ALPHAS] declared=$DECLARED"

# ---- S0: THE PATCH INSTRUMENT IS ITSELF PINNED AND DRIVEN, HERE, EVERY LAUNCH
# Its md5 is asserted against the freeze, and then its OWN controls are driven on
# this box at this moment -- not trusted from a selftest that passed once at
# freeze time.  A reader whose controls have not been shown to fire is not
# evidence (CLAUDE.md rule 3), and G-PATCH is the gate the `empty` unit exists
# for.  If the instrument cannot prove itself, no primal runs.
if [ "$MD5_PATCH_ASSERT" != "PIN_AT_FREEZE" ]; then
  echo "$MD5_PATCH_ASSERT  $HERE/a1wrt_patch_assert.py" | md5sum -c - \
    || { stage_say "ABORT S0 a1wrt_patch_assert.py md5 != the freeze pin -- the"
         stage_say "  G-PATCH instrument has MOVED since the registration froze it."
         exit 4; }
else
  stage_say "A1WRT_STAGE (S0) NOTE the patch instrument md5 is UNPINNED in this"
  stage_say "  launcher (placeholder PIN_AT_FREEZE).  The selftest below still"
  stage_say "  runs and still gates; the PIN is what a freeze adds, and its"
  stage_say "  absence is REPORTED here rather than passed over silently."
fi
python3 "$HERE/a1wrt_patch_assert.py" --selftest >> "$STAGE_EVID" 2>&1 || {
  stage_say "ABORT S0 the G-PATCH instrument FAILED ITS OWN CONTROLS on this box."
  stage_say "  A reading from an instrument whose controls do not fire is not"
  stage_say "  evidence, so no primal runs.  See $STAGE_EVID."
  exit 7; }
stage_say "A1WRT_STAGE (S0) OK a1wrt_patch_assert.py drove its own controls on this box, this launch, and passed"

# ---- S0b: THE controlDict DERIVER GETS THE SAME TREATMENT --------------------
# S6 no longer ASSERTS an inherited controlDict; it WRITES one and reads it back
# THROUGH THE SAME CODE.  That shape is only as good as the code: a broken
# deriver would write bad bytes and its own read-back would agree with them.
# The patch instrument is pinned and driven at S0 for exactly this reason and
# the deriver is a frozen instrument of the same standing, so it is pinned and
# driven here.  An instrument trusted because it passed once at freeze time is
# not evidence about this box at this moment (CLAUDE.md rule 3).
echo "$MD5_CONTROLDICT  $HERE/a1wrt_controldict.py" | md5sum -c - \
  || { stage_say "ABORT S0b a1wrt_controldict.py md5 != the freeze pin -- the"
       stage_say "  controlDict DERIVER has MOVED since the registration froze it."
       stage_say "  S6 writes this item's control dictionary with it, so a moved"
       stage_say "  deriver is a moved run.  REFUSED."
       exit 4; }
python3 "$HERE/a1wrt_controldict.py" --selftest >> "$STAGE_EVID" 2>&1 || {
  stage_say "ABORT S0b the controlDict DERIVER FAILED ITS OWN CONTROLS on this box."
  stage_say "  S6 would write the control dictionary with it and read it back with"
  stage_say "  it.  See $STAGE_EVID.  No primal runs."
  exit 6; }
stage_say "A1WRT_STAGE (S0b) OK a1wrt_controldict.py md5 == pin and drove its own controls on this box, this launch"

# ---- S1: the mesh source, verified BEFORE it is copied ----------------------
test -d "$MESH_SRC" || { stage_say "ABORT S1 mesh source absent: $MESH_SRC"; exit 5; }
test -f "$MESH_SRC/constant/polyMesh/points.gz" || { stage_say "ABORT S1 no mesh under $MESH_SRC"; exit 5; }
# THE SOURCE IS ASSERTED `symmetry` BEFORE ANY COPY.  If A1WR's L3 mesh has been
# converted in place by some other lane, this item's U1 is no longer A1WR's own
# configuration and G-REPRO's one-variable comparison is void.
python3 "$HERE/a1wrt_patch_assert.py" --verify "$MESH_SRC" --want symmetry >> "$STAGE_EVID" 2>&1 || {
  stage_say "ABORT S1 G-PATCH: the A1WR L3 SOURCE mesh is not 'symmetry' on disk."
  stage_say "  U1 exists to reproduce A1WR's OWN configuration.  If the source has"
  stage_say "  moved, the cold-vs-continued comparison moves two variables and"
  stage_say "  measures neither.  REFUSED before any copy."
  exit 7; }
stage_say "A1WRT_STAGE (S1) OK mesh source $MESH_SRC verified 'symmetry' at all 16 registered sites"

# ---- S2: the cold copy ------------------------------------------------------
cp -a "$MESH_SRC" "$WORK" || { stage_say "ABORT S2 stage copy of $MESH_SRC failed"; exit 4; }
stage_say "A1WRT_STAGE (S2) OK cp -a $MESH_SRC -> $WORK"

# ---- S3: G-COLDSTART, ON DISK, BEFORE THE FIRST PRIMAL ----------------------
# A1WR's killed `sweep_I/case/0/` was left carrying a NONUNIFORM 130,304-cell `U`
# under an alpha=13 inlet beside a UNIFORM p, nut and nuTilda -- a mixed state a
# naive restart would have consumed silently.  `a1wr_cmd.sh` resets `0/` from
# `0.orig/` as its first act in the container, so `0.orig` IS the cold state and
# is what is asserted here.  EVERY FIELD IS COUNTED: 7 expected, 7 inspected.
COLD=$(python3 -c "
import re, sys, os
d = '$WORK/0.orig'
fields = ['U','p','nut','nuTilda','k','omega','epsilon']
seen = 0; bad = []
for f in fields:
    p = os.path.join(d, f)
    if not os.path.isfile(p):
        print('UNMEASURED missing 0.orig/%s' % f); sys.exit()
    try:
        t = open(p, errors='replace').read()
    except OSError:
        print('UNMEASURED unreadable 0.orig/%s' % f); sys.exit()
    m = re.search(r'internalField\s+(\S+)', t)
    if not m:
        print('UNMEASURED no internalField in 0.orig/%s' % f); sys.exit()
    seen += 1
    if m.group(1) != 'uniform':
        bad.append('%s=%s' % (f, m.group(1)))
if seen != len(fields):
    print('UNMEASURED inspected %d of %d fields' % (seen, len(fields))); sys.exit()
print(('NONUNIFORM ' + ' '.join(bad)) if bad else 'UNIFORM seen=%d/%d' % (seen, len(fields)))
" 2>/dev/null)
case "$COLD" in
  UNIFORM*) stage_say "A1WRT_G_COLDSTART OK $COLD -- every 0.orig field read back from disk and asserted uniform" ;;
  UNMEASURED*)
    stage_say "ABORT S3 G-COLDSTART $COLD"
    stage_say "  A field this check could not read is UNMEASURED, never counted as"
    stage_say "  uniform.  It refuses rather than reporting a zero it cannot defend."
    exit 5 ;;
  *)
    stage_say "ABORT S3 G-COLDSTART $COLD -- a nonuniform initial field is not a cold start."
    exit 5 ;;
esac
# No time directory and no processor directory may exist in a cold case.  The
# test is a NAME TEST, never a `0.*` GLOB: `0.orig` must survive and a bare
# `0.*` glob would sweep it -- the pristine initial-condition backup.
is_time_dir() {
  case "$1" in
    0|"") return 1 ;;
    *[!0-9.]*) return 1 ;;     # `0.orig` carries letters and is excluded HERE
    *.*.*) return 1 ;;
    *) return 0 ;;
  esac
}
NTIME=0
for d in "$WORK"/*; do
  [ -d "$d" ] || continue
  is_time_dir "$(basename "$d")" && { stage_say "ABORT S3 time directory $(basename "$d") exists in a cold case"; NTIME=$((NTIME+1)); }
done
test "$NTIME" -eq 0 || exit 5
test -z "$(ls -d "$WORK"/processor* 2>/dev/null)" || { stage_say "ABORT S3 processor* present in a cold case"; exit 5; }
test -d "$WORK/0.orig" || { stage_say "ABORT S3 0.orig was swept -- the pristine backup is KEPT, and the name test exists to keep it"; exit 5; }
stage_say "A1WRT_STAGE (S3) OK cold: no time dir, no processor*, 0.orig present"

# ---- S4: G-PATCH clauses 1 and 2, PRE-PRIMAL --------------------------------
# THE `empty` UNIT IS CONVERTED HERE AND READ BACK; THE `symmetry` UNIT IS
# ASSERTED UNCHANGED.  Both go through the SAME instrument, so the two units are
# graded on the same reading of the same bytes.
if [ "$WANT_PATCH" = "empty" ]; then
  python3 "$HERE/a1wrt_patch_assert.py" --convert "$WORK" --want empty >> "$STAGE_EVID" 2>&1 || {
    stage_say "ABORT S4 G-PATCH conversion to 'empty' failed or did not read back"; exit 7; }
  stage_say "A1WRT_STAGE (S4) OK converted to 'empty' and READ BACK through the same verifier"
else
  python3 "$HERE/a1wrt_patch_assert.py" --verify "$WORK" --want symmetry >> "$STAGE_EVID" 2>&1 || {
    stage_say "ABORT S4 G-PATCH: the staged copy is not 'symmetry'"; exit 7; }
  stage_say "A1WRT_STAGE (S4) OK staged copy asserted 'symmetry', UNCONVERTED"
fi
# AND THE OTHER IDENTITY IS ASSERTED ABSENT.  A verifier that only ever confirms
# what it was told to expect cannot distinguish a converted case from one it
# failed to read.  This is the same bytes, the same reader, the opposite answer.
if python3 "$HERE/a1wrt_patch_assert.py" --verify "$WORK" \
     --want "$([ "$WANT_PATCH" = "empty" ] && echo symmetry || echo empty)" >/dev/null 2>&1; then
  stage_say "ABORT S4 G-PATCH: the staged case verifies as BOTH identities, which is"
  stage_say "  impossible.  The verifier is not discriminating and its PASS above is"
  stage_say "  therefore not evidence.  REFUSED."
  exit 7
fi
stage_say "A1WRT_STAGE (S4) OK the opposite identity REFUSES on the same bytes -- the verifier discriminates"

# ---- S5: the instruments, md5-asserted before they are staged ---------------
echo "$MD5_RUNSCRIPT  $A1WR_CASE_DIR/a1wr_runScript_incomp.py" | md5sum -c - \
  || { stage_say "ABORT S5 a1wr_runScript_incomp.py md5 -- the producer has MOVED"; exit 4; }
echo "$MD5_CMD  $A1WR_CASE_DIR/a1wr_cmd.sh" | md5sum -c - \
  || { stage_say "ABORT S5 a1wr_cmd.sh md5 -- the unit program has MOVED"; exit 4; }
cp "$A1WR_CASE_DIR/a1wr_runScript_incomp.py" "$BASE/runScript.py" || { stage_say "ABORT S5 stage runScript"; exit 4; }
cp "$A1WR_CASE_DIR/a1wr_cmd.sh"              "$BASE/cmd.sh"       || { stage_say "ABORT S5 stage cmd"; exit 4; }
echo "$MD5_RUNSCRIPT  $BASE/runScript.py" | md5sum -c - || { stage_say "ABORT S5 staged runScript md5"; exit 4; }
echo "$MD5_CMD  $BASE/cmd.sh"             | md5sum -c - || { stage_say "ABORT S5 staged cmd md5"; exit 4; }
stage_say "A1WRT_STAGE (S5) OK producer and unit program staged, every md5 asserted on BOTH sides of the copy"

# ---- S5b: THE FFD, WITHOUT WHICH THE PRODUCER CANNOT BUILD ITS MODEL --------
# `a1wr_runScript_incomp.py:129` does OM_DVGEOCOMP(file="FFD/wingFFD.xyz"), so the
# FFD is a HARD INPUT of the producer this item inherits unchanged -- and the L3
# MESH DIRECTORY HAS NO FFD/.  A1WR never hit this because its driver stages from
# a case SKELETON and overlays L3's polyMesh; A1WRT stages from the mesh
# directory, which carries the mesh and the fields but not the case furniture.
# MEASURED: all THIRTEEN wingFFD.xyz files under A1WR's own run root, and the
# SKELETON its driver copies from, carry md5 6ddf378b028d03d8a18270488bee1759 --
# so staging it here moves no variable: it RESTORES an input A1WR always had.
# The source, the scope of that census and the reason for that source are
# registered at FFD_SRC above.
# THIS DEFECT WAS MASKED BY S6: the launch aborted on the controlDict first and
# never reached the primal, where this would have failed inside the container.
test -f "$FFD_SRC" || { stage_say "ABORT S5b the FFD source is absent: $FFD_SRC -- the producer loads it at runScript:129 and cannot build its model without it"; exit 5; }
echo "$MD5_FFD  $FFD_SRC" | md5sum -c - >> "$STAGE_EVID" 2>&1 \
  || { stage_say "ABORT S5b FFD md5 -- the geometry parametrisation has MOVED from what A1WR ran"; exit 4; }
mkdir -p "$WORK/FFD" || { stage_say "ABORT S5b cannot mkdir $WORK/FFD"; exit 5; }
cp "$FFD_SRC" "$WORK/FFD/wingFFD.xyz" || { stage_say "ABORT S5b stage FFD"; exit 4; }
echo "$MD5_FFD  $WORK/FFD/wingFFD.xyz" | md5sum -c - >> "$STAGE_EVID" 2>&1 \
  || { stage_say "ABORT S5b staged FFD md5 -- the copy did not land intact"; exit 4; }
stage_say "A1WRT_STAGE (S5b) OK FFD staged from $FFD_SRC (A1WR's own alpha 0..12 incompressible sweep case), md5 $MD5_FFD asserted on BOTH sides of the copy"

# ---- S6: the controlDict is now DERIVED AND WRITTEN, THEN READ BACK ---------
# WHY THIS CHANGED, AND IT IS NOT A WEAKENING.  S6 previously asserted the
# INHERITED controlDict and refused on a mismatch.  It fired for real on
# 2026-09-03T19:38:15Z, at 11 s and ~0 core-min, on
# `endTime=1000, registered 4000`: the L3 mesh directory's controlDict is
# MESH-GENERATION LEFTOVER, while A1WR's real run cases carry endTime 4000
# because A1WR's driver WRITES the controlDict per unit (a1wr_chain_driver.sh
# stage_unit, the heredoc with `endTime $et`).  Inheriting it meant running 1,000
# iterations and reporting them against a 4,000-iteration registration -- the
# two-variable trap, introduced by the staging itself.
#
# So A1WRT now WRITES the controlDict, exactly as A1WR does, by DERIVING IT FROM
# A1WR'S OWN HEREDOC BYTES rather than authoring one -- retyping it would let a
# later divergence in A1WR's template silently split the two items.  The derived
# bytes are asserted byte-identical to the controlDict A1WR's driver ACTUALLY
# WROTE for the alpha sweep this item extends.
#
# AND S6 ITSELF IS UNCHANGED IN SHAPE AND STILL RUNS -- AFTER the write, as a
# READ-BACK, the same shape as the rc artefact: write, read back, assert.  It is
# NOT weakened to "we wrote it, so it must be right", and every branch it had
# (unreadable endTime is UNMEASURED and refuses; a wrong value refuses naming
# section 7) is carried inside a1wrt_controldict.py and driven by its controls.
python3 "$HERE/a1wrt_controldict.py" --write "$WORK" >> "$STAGE_EVID" 2>&1 || {
  stage_say "ABORT S6 the controlDict could not be DERIVED from A1WR's driver, or"
  stage_say "  did not read back as written.  See $STAGE_EVID.  No primal runs on a"
  stage_say "  control dictionary this item cannot show is A1WR's own."
  exit 6; }
stage_say "A1WRT_STAGE (S6) OK controlDict DERIVED from a1wr_chain_driver.sh's own heredoc with endTime=$ENDTIME, written, and READ BACK through the same verifier"
# The read-back, again, in THIS shell, so the launcher's own record carries the
# three values rather than pointing at another file for them.
CD="$WORK/system/controlDict"
test -f "$CD" || { stage_say "ABORT S6 no controlDict at $CD after the write"; exit 5; }
GOT_ET=$(grep -aoE '^\s*endTime\s+[0-9]+\s*;' "$CD" | grep -oE '[0-9]+' | head -1)
test -n "$GOT_ET" || { stage_say "ABORT S6 controlDict carries no readable endTime -- UNMEASURED, not assumed to be $ENDTIME"; exit 5; }
test "$GOT_ET" = "$ENDTIME" || { stage_say "ABORT S6 controlDict endTime=$GOT_ET, registered $ENDTIME.  The iteration budget is FROZEN (section 7): a different endTime is a NEW rung with its own pre-registration."; exit 5; }
GOT_WI=$(grep -aoE '^\s*writeInterval\s+[0-9]+\s*;' "$CD" | grep -oE '[0-9]+' | head -1)
GOT_DT=$(grep -aoE '^\s*deltaT\s+[0-9.]+\s*;' "$CD" | grep -oE '[0-9.]+' | head -1)
test -n "$GOT_WI" || { stage_say "ABORT S6 writeInterval UNMEASURED"; exit 5; }
test -n "$GOT_DT" || { stage_say "ABORT S6 deltaT UNMEASURED"; exit 5; }
test "$GOT_WI" = "$ENDTIME" || { stage_say "ABORT S6 writeInterval=$GOT_WI, registered $ENDTIME -- the endTime state would not be written and the age guard would have nothing to date"; exit 5; }
test "$GOT_DT" = "1" || { stage_say "ABORT S6 deltaT=$GOT_DT, registered 1"; exit 5; }
stage_say "A1WRT_STAGE (S6) OK endTime=$GOT_ET writeInterval=$GOT_WI deltaT=$GOT_DT, all three read back from disk and asserted"

# ---- S7: the image, BY DIGEST -----------------------------------------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { stage_say "ABORT S7 cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1) WANT_DIGEST=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  *) stage_say "ABORT S7 image $IMG is not this item's registered row.  A1WRT runs"
     stage_say "  the PATCHED build ONLY -- the build confound against the coarse"
     stage_say "  sweeps' SHIPPED image is registered and is not widened here."
     exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT_DIGEST" || { stage_say "ABORT S7 digest mismatch $IMG got=$GOT_DIGEST want=$WANT_DIGEST"; exit 4; }
stage_say "A1WRT_G_IMG_PASS row=$ROW digest=$GOT_DIGEST"

# ---- S8: THE AGE DATUM IS WRITTEN LAST (CLAUDE.md rule 4) -------------------
# `0/T` is the thermal family's datum; this family's is `0.orig`, because
# `a1wr_cmd.sh` builds `0/` FROM it inside the container.  Touching it last means
# every field the run writes is strictly newer than the state the run was
# allowed to start from, and the age guard can tell the two apart.
touch "$WORK/0.orig"/* || { stage_say "ABORT S8 age-guard datum"; exit 5; }
AGE_DATUM=$(stat -c '%Y' "$WORK/0.orig/U")
echo "$AGE_DATUM" > "$WORK/.a1wrt_age_datum"
stage_say "A1WRT_AGE_DATUM unit=$UNIT epoch=$AGE_DATUM (every registered product must be strictly newer)"

# =============================================================================
# THE UNIT.  The deadline lives INSIDE the container so the cap stops the run
# even if the driver, the daemon and every agent die.  A1WR's own kill is the
# argument: its driver was polling healthily at 02:24:58Z and the box went down
# seven seconds later.
# =============================================================================
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="a1wrt_${UNIT}_${STAMP}"
LOG="$BASE/${UNIT}_${STAMP}.log"
OUT="$BASE/$UNIT/out"
mkdir -p "$OUT" || { stage_say "ABORT cannot mkdir $OUT"; exit 5; }

T0=$(date -u +%s)
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus="$CPUSET" \
    --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -e OMP_NUM_THREADS=1 \
    -e A1WR_MODE="$MODE" -e A1WR_ALPHAS="$ALPHAS" \
    -e A1WR_TOL="$PRIMAL_TOL" -e A1WR_TMO="$TMO" \
    -v "$WORK":/mnt/case -v "$OUT":/mnt/out \
    -v "$BASE/runScript.py":/mnt/runScript.py:ro \
    -v "$BASE/cmd.sh":/mnt/cmd.sh:ro \
    -w /mnt "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo A1WRT_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); m=hashlib.md5(open(so,\"rb\").read()).hexdigest(); print(\"A1WRT_IDWARP_SO_MD5:\",m); assert m==\"$MD5_IDWARP\", \"G-FREEZE libidwarp md5 mismatch\"' && \
     echo A1WRT_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k $KILL_GRACE_S $TMO bash /mnt/cmd.sh" > /dev/null 2>&1 \
  || { stage_say "ABORT could not start container"; exit 4; }

# The cap REPORTS; the CEILING is the fleet safety stop (Sanaa 2026-09-03
# ~21:00Z): far above the estimate, not the estimate itself, and it stops the run
# gracefully regardless of residual trend.
CEILING=$(python3 -c "print('%.1f' % (3.0*$CAP))")
echo "A1WRT_RUNAWAY_GUARD unit=$UNIT cap_core_min=$CAP fleet_ceiling_core_min=$CEILING mode=report_then_graceful_stop_at_ceiling"
CAP_REPORTED=no; CEILING_HIT=no
while true; do
  RUNNING=$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)
  NOW=$(date -u +%s); EL=$((NOW-T0))
  CM=$(python3 -c "print(round($EL*$RANKS/60.0,3))")
  [ "$RUNNING" != "true" ] && break
  if [ "$CAP_REPORTED" = "no" ] && [ "$(python3 -c "print(1 if $CM > $CAP else 0)")" = "1" ]; then
    CAP_REPORTED=yes
    echo "A1WRT_CAP_CROSSED unit=$UNIT core_min=$CM cap=$CAP ceiling=$CEILING action=REPORTED_RUN_CONTINUES supervisor_decides" | tee -a "$LEDGER"
  fi
  if [ "$(python3 -c "print(1 if $CM > $CEILING else 0)")" = "1" ]; then
    CEILING_HIT=yes
    echo "A1WRT_CEILING_HIT unit=$UNIT core_min=$CM ceiling=$CEILING action=GRACEFUL_STOP" | tee -a "$LEDGER"
    sudo -n docker stop -t 30 "$NAME" >/dev/null 2>&1
    break
  fi
  sleep 10
done

sudo -n docker logs "$NAME" > "$LOG" 2>&1
# THE KERNEL'S VERDICT, READ BEFORE THE CONTAINER IS REMOVED.
rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$NAME" 2>/dev/null)
test -n "$rc" || rc=125
INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
CSTART=$(sudo -n docker inspect --format '{{.State.StartedAt}}' "$NAME" 2>/dev/null)
CFIN=$(sudo -n docker inspect --format '{{.State.FinishedAt}}' "$NAME" 2>/dev/null)
T1=$(date -u +%s); WALL=$((T1-T0))
CWALL=$(python3 -c "
import datetime
def p(s):
    s = s.strip().replace('Z', '+00:00')
    i = s.find('.')
    if i >= 0:
        j = i + 1
        while j < len(s) and s[j].isdigit(): j += 1
        if j - i > 7: s = s[:i+7] + s[j:]
    return datetime.datetime.fromisoformat(s)
try: print(int(round((p('$CFIN') - p('$CSTART')).total_seconds())))
except Exception: print('NOT_MEASURED')
" 2>/dev/null)
test -n "$CWALL" || CWALL=NOT_MEASURED
echo "A1WRT_CONTAINER_CLOCK unit=$UNIT started_at=$CSTART finished_at=$CFIN container_wall_s=$CWALL host_wall_s_bracket_T0_T1=$WALL"
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$WORK" "$OUT" 2>/dev/null

# ---- THE rc ARTEFACT THE FROZEN GRADER READS -------------------------------
# a1wrt_read.py:965-966 reads `<run>/tail_empty/out/rc` and treats its ABSENCE as
# a REFUSAL, not as a pass -- rule 4 requires rc = 0 and the reader will not
# print a verdict against a clause it never checked.  The grader is FROZEN
# (registration commit a62d8d75), so it is this launcher's job to write what the
# grader reads.  Discovered by reading the frozen reader rather than by watching
# a graded run refuse at exit 2.
#
# THE VALUE IS THE KERNEL'S, taken from `docker inspect` above and never from
# `$?` of a `timeout` or `setsid` line.  It is written for BOTH units even though
# the grader currently reads only the tail's: a unit directory that cannot say
# how its own container exited is not self-describing.
printf '%s\n' "$rc" > "$OUT/rc" || { echo "ABORT cannot write $OUT/rc"; exit 4; }
RC_BACK=$(cat "$OUT/rc" 2>/dev/null)
test "$RC_BACK" = "$rc" || { echo "ABORT rc artefact did not land: wrote '$rc', read back '$RC_BACK'"; exit 4; }
echo "A1WRT_RC_ARTEFACT unit=$UNIT path=$OUT/rc value=$RC_BACK (read back and asserted; the frozen grader REFUSES on its absence)"

# ---- the ledger row.  IT LANDS AFTER THE UNIT AND SURVIVES THE KILL. --------
CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
SIBLINGS_POST=$(census)
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
# THE POINT COUNT IS READ FROM THE LOG, and a log that cannot be read reports
# NOT_MEASURED rather than 0 -- a truncated sweep and an unreadable log are
# different facts and the grader is entitled to which one happened.
if [ -s "$OUT/sweep.log" ]; then
  EXEC=$(grep -ac '^AOA_POINT_END ' "$OUT/sweep.log" 2>/dev/null); EXEC="${EXEC:-0}"
else
  EXEC=NOT_MEASURED
fi
{
  echo "ITEM=$ITEM"
  echo "UNIT=$UNIT ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP item_ceiling_core_min=$ITEM_CEILING enforced_wall_s=$TMO frame_allowance_s=$FRAME_ALLOWANCE_S back_check_core_min=$BACKCHECK memory=$MEM inspect(exit,oomkilled)=[$INSPECT] container_wall_s=$CWALL patch_identity=$WANT_PATCH mode=$MODE declared=$DECLARED point_end_markers=$EXEC age_datum=$AGE_DATUM cpuset=$CPUSET memavail_pre_GiB=$MEMAVAIL_GIB memavail_post_GiB=$MEMAVAIL_POST siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] occ_queue_polls=$QUEUE_POLLS ceiling_hit=$CEILING_HIT log=$(basename "$LOG") stamp=$STAMP"
  grep -a "A1WRT_CONTAINER_UID\|A1WRT_IDWARP_SO_MD5\|A1WRT_DEADLINE_IN_CONTAINER_S\|Mesh has .* solution" "$LOG" | head -5
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
echo "NOTE: this launcher does not GRADE.  a1wrt_read.py is the frozen grading"
echo "  path and reads G-PATCH clause 3, G-COMPLETE, G-CAPS, G-REPRO and"
echo "  G-PATCHPAIR off these logs afterward."
exit $rc
