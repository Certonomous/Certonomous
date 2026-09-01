#!/usr/bin/env bash
# =============================================================================
# SO-3 LAUNCHER SELFTEST.  Every leg is DRIVEN.  Nothing here is asserted in
# prose and nothing launches a container.
#
# THE HEADLINE IS (r1): THE C-188 CAP-FRAME REPAIR, DRIVEN RED AND GREEN ON
# C-188's OWN NUMBERS.  A repair that has only been described is a claim.
#
# It reaches the launcher's registered tables and pure functions through
# `--source-only`, which returns BEFORE every guard, every read and every
# destructive act.  No `docker`, no `rm`, no `sudo`.
# =============================================================================
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/so3_run_arm.sh"
test -f "$LAUNCHER" || { echo "ABORT launcher absent: $LAUNCHER"; exit 2; }

# shellcheck disable=SC1090
. "$LAUNCHER" --source-only

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); printf '  [OK ] %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  [FAIL] %s\n' "$1"; }
chk()  { if [ "$2" = "$3" ]; then ok "$1 ($2)"; else bad "$1: got [$2] want [$3]"; fi; }

DECLARED="MESH O-S XE-S FE-S O-P XE-P FE-P"

echo "SO-3 LAUNCHER SELFTEST"
echo
echo "(r1) THE C-188 CAP FRAME -- DRIVEN RED ON C-188's OWN NUMBERS, THEN GREEN"
echo "     C-188: D6 O_mp, cap 2000.0 core-min at ranks=4, deadline reached."
echo "     The ledger recorded 30,008 s wall = 2000.533 core-min against a 2000.0 cap."
python3 - "$CAP_MARGIN_S" "$CAP_KILL_GRACE_S" <<'PY'
import math, sys
MARGIN = int(sys.argv[1]); GRACE = int(sys.argv[2])
# C-188's MEASURED host-frame overhead on the non-grace path: 30,008 - 30,000 = 8 s.
OVERHEAD = 8
CAP, RANKS = 2000.0, 4
fails = 0

# --- THE RED LEG.  The ancestor's form, reproduced exactly, on C-188's numbers.
old_tmo = int(round(CAP * 60.0 / RANKS))
old_recorded_measured = (old_tmo + OVERHEAD) * RANKS / 60.0
old_recorded_worst = (old_tmo + GRACE + OVERHEAD) * RANKS / 60.0
print("     ancestor tmo=%d s -> C-188's MEASURED host wall %d s = %.3f core-min"
      % (old_tmo, old_tmo + OVERHEAD, old_recorded_measured))
if old_tmo != 30000:
    print("  [FAIL] the ancestor form does not reproduce C-188's 30,000 s deadline"); fails += 1
else:
    print("  [OK ] the ancestor's deadline is C-188's own 30,000 s")
if abs(old_recorded_measured - 2000.533) > 0.002:
    print("  [FAIL] the ancestor form does not reproduce C-188's recorded 2000.533 core-min: %.3f"
          % old_recorded_measured); fails += 1
else:
    print("  [OK ] REPRODUCED: the ancestor's frame records %.3f core-min against a 2000.0 cap "
          "-- C-188 EXACTLY, and it is an overrun BY CONSTRUCTION" % old_recorded_measured)
if old_recorded_measured <= CAP:
    print("  [FAIL] the ancestor form did not overrun; the red leg proves nothing"); fails += 1
else:
    print("  [OK ] RED: the ancestor's own backcheck asserted EQUALITY and therefore asserted "
          "the overrun into existence (%.3f > %.1f, and %.3f > %.1f in the worst case)"
          % (old_recorded_measured, CAP, old_recorded_worst, CAP))

# --- THE GREEN LEG.  The repaired form, on the same numbers.
new_tmo = int(math.floor(CAP * 60.0 / RANKS)) - MARGIN
new_recorded_worst = (new_tmo + GRACE + OVERHEAD) * RANKS / 60.0
new_backcheck = (new_tmo + MARGIN) * RANKS / 60.0
print("     repaired tmo=%d s -> worst-case host wall %d s = %.3f core-min"
      % (new_tmo, new_tmo + GRACE + OVERHEAD, new_recorded_worst))
if new_recorded_worst > CAP:
    print("  [FAIL] the repaired form STILL overruns: %.3f > %.1f" % (new_recorded_worst, CAP))
    fails += 1
else:
    print("  [OK ] GREEN: the repaired frame's WORST case is %.3f core-min, inside the %.1f cap "
          "with %.3f core-min to spare" % (new_recorded_worst, CAP, CAP - new_recorded_worst))
if new_backcheck > CAP + 1e-9:
    print("  [FAIL] the repaired backcheck INEQUALITY does not hold: %.6f > %.1f"
          % (new_backcheck, CAP)); fails += 1
else:
    print("  [OK ] the backcheck is an INEQUALITY over the WHOLE frame and holds: "
          "(tmo + margin) * ranks / 60 = %.6f <= %.1f" % (new_backcheck, CAP))
sys.exit(1 if fails else 0)
PY
if [ $? -eq 0 ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); echo "  [FAIL] (r1) C-188 frame"; fi

echo
echo "(r2) THE CAP FRAME ON EVERY DECLARED ARM, and the COMMENT TABLE parsed"
echo "     beside the CODE -- a comment that contradicts its own code is what a"
echo "     reviewer in a hurry reads."
for A in $DECLARED; do
  C=$(cap_core_min "$A"); R=$(ranks_of "$A")
  T=$(tmo_for "$C" "$R"); rc=$?
  if [ $rc -ne 0 ]; then bad "(r2) $A: tmo_for REFUSED at cap=$C ranks=$R"; continue; fi
  B=$(capframe_backcheck "$T" "$R" "$C"); rc=$?
  # The comment table's own wall figure for this arm, parsed out of the launcher.
  # Columns of the comment row `#   MESH     1        5.0            120 s   12g`:
  #   $1=#  $2=arm  $3=ranks  $4=cap  $5=wall  $6=s  $7=memory
  # The first draft of this leg read $3/$4 and reported every arm as a
  # disagreement between the comment and the code.  It was the LEG that was
  # wrong, and it is written out here because a check whose failure mode is a
  # column index is one a future reader will otherwise "fix" by editing the
  # comment table to match a mis-read.
  CT=$(grep -aE "^#   $A +$R +[0-9.]+ +[0-9]+ s" "$LAUNCHER" | awk '{print $5}' | head -1)
  CC=$(grep -aE "^#   $A +$R +[0-9.]+ +[0-9]+ s" "$LAUNCHER" | awk '{print $4}' | head -1)
  if [ $rc -ne 0 ]; then
    bad "(r2) $A: backcheck FAILED enforced=$B cap=$C"
  elif [ "$CT" != "$T" ]; then
    bad "(r2) $A: the COMMENT TABLE says wall=$CT s and the CODE derives $T s"
  elif [ "$CC" != "$C" ]; then
    bad "(r2) $A: the COMMENT TABLE says cap=$CC and the CODE says $C"
  else
    ok "(r2) $A ranks=$R cap=$C -> tmo=${T}s, enforced host-frame=$B core-min <= cap, comment table AGREES"
  fi
done

echo
echo "(r3) THE REFUSAL BRANCH.  A cap too small to carry the margin must REFUSE,"
echo "     and the registered remedy is to RAISE THE CAP -- lowering the margin"
echo "     is the move that re-creates C-188."
for BADCAP in 0.19 1.0 3.0 3.9; do
  if T=$(tmo_for "$BADCAP" 1); then
    bad "(r3) cap=$BADCAP core-min at ranks=1 was ACCEPTED with tmo=$T -- it must refuse"
  else
    ok "(r3) cap=$BADCAP core-min at ranks=1 REFUSED (margin ${CAP_MARGIN_S}s + min ${CAP_MIN_TMO_S}s needs >= 4.0)"
  fi
done
# AND THE BOUNDARY, DRIVEN IN BOTH DIRECTIONS.  A guard that refuses everything
# is not a guard.
if T=$(tmo_for 4.0 1); then ok "(r3) cap=4.0 at ranks=1 ACCEPTED with tmo=${T}s -- the boundary is exactly where the arithmetic puts it"
else bad "(r3) cap=4.0 at ranks=1 was refused; the guard refuses at the boundary it should accept"; fi
if T=$(tmo_for 3.999 1); then bad "(r3) cap=3.999 accepted (tmo=$T) -- the guard is one step too generous"
else ok "(r3) cap=3.999 at ranks=1 REFUSED -- the boundary is sharp"; fi

echo
echo "(r4) THE REGISTERED TABLES ARE TOTAL OVER THE DECLARED ARMS AND EMPTY"
echo "     OTHERWISE.  A row is READ FROM A TABLE, never derived from a name"
echo "     suffix: SO-1c died at its second arm because one call site of a row"
echo "     label was repaired and two were not."
for A in $DECLARED; do
  miss=""
  [ -n "$(cap_core_min "$A")" ] || miss="$miss cap"
  [ -n "$(cap_memory   "$A")" ] || miss="$miss mem"
  [ -n "$(ranks_of     "$A")" ] || miss="$miss ranks"
  [ -n "$(row_of       "$A")" ] || miss="$miss row"
  if [ -n "$miss" ]; then bad "(r4) $A has no registered:$miss"; else ok "(r4) $A is total across cap/mem/ranks/row"; fi
done
# THE UNDECLARED ARM.  `Q-S` would have matched a `*-S` suffix glob and been
# handed the SHIPPED row.  It must fall through to empty everywhere.
for A in Q-S Q-P X-S F-P O-X XE FE --source-only; do
  if [ -z "$(row_of "$A")" ] && [ -z "$(cap_core_min "$A")" ] && [ -z "$(ranks_of "$A")" ]; then
    ok "(r4) undeclared arm [$A] falls through to EMPTY in every table"
  else
    bad "(r4) undeclared arm [$A] was answered: row=[$(row_of "$A")] cap=[$(cap_core_min "$A")] ranks=[$(ranks_of "$A")]"
  fi
done

echo
echo "(r5) np = 1 ON EVERY ARM.  DAFOAM section 5 forbids carrying an FD"
echo "     reference across np, and SO-3aR2's table -- the only reason this"
echo "     optimisation is admissible -- was measured at np = 1."
NP_BAD=0
for A in $DECLARED; do
  [ "$(ranks_of "$A")" = "1" ] || { bad "(r5) $A is registered at ranks=$(ranks_of "$A"), not 1"; NP_BAD=1; }
done
[ "$NP_BAD" -eq 0 ] && ok "(r5) all 7 declared arms are registered at ranks=1"

echo
echo "(r6) THE ENDPOINT ARMS' OPTIMUM SOURCE, AS A TABLE.  Section 9 requires"
echo "     the FD check AT THE FINAL DESIGN POINT, and it must be THIS row's."
chk "(r6) xopt_arm_of XE-S" "$(xopt_arm_of XE-S)" "O-S"
chk "(r6) xopt_arm_of FE-S" "$(xopt_arm_of FE-S)" "O-S"
chk "(r6) xopt_arm_of XE-P" "$(xopt_arm_of XE-P)" "O-P"
chk "(r6) xopt_arm_of FE-P" "$(xopt_arm_of FE-P)" "O-P"
chk "(r6) xopt_arm_of MESH (not an endpoint arm)" "$(xopt_arm_of MESH)" ""
chk "(r6) xopt_arm_of O-S  (not an endpoint arm)" "$(xopt_arm_of O-S)" ""
chk "(r6) xopt_arm_of Q-S  (undeclared)"          "$(xopt_arm_of Q-S)" ""
# AND THE ROW AGREEMENT, WHICH IS THE POINT: an endpoint arm's optimum source
# must sit on the SAME ROW as the endpoint arm.
for A in XE-S FE-S XE-P FE-P; do
  S=$(xopt_arm_of "$A")
  if [ "$(row_of "$A")" = "$(row_of "$S")" ]; then
    ok "(r6) $A ($(row_of "$A")) reads $S ($(row_of "$S")) -- same row"
  else
    bad "(r6) $A is on row $(row_of "$A") but reads $S which is on row $(row_of "$S")"
  fi
done

echo
echo "(r7) G-ROOT.2's PROTECTED-ROOT LIST, DRIVEN AGAINST THE DISK."
echo "     A MECHANICAL RENAME MOVES TOKENS; IT CANNOT MAKE PROSE TRUE."
echo "     SO-3aR carried CURRICULUM-SO3aRF-... (absent); SO-3aR2's rename made"
echo "     it CURRICULUM-SO3aR2F-... (also absent) while its own comment called"
echo "     it a root that DOES exist.  Every entry is checked here, and a GHOST"
echo "     is PRINTED rather than passed over."
# `FORBIDDEN_ROOTS` is defined BELOW `--source-only` -- correctly, because it is
# read by a guard and every guard lives below the early return.  So it is PARSED
# OUT OF THE LAUNCHER'S OWN BYTES here rather than sourced, which is the stronger
# form anyway: this leg reads the same characters the guard reads.
FORBIDDEN_ROOTS=$(sed -n '/^FORBIDDEN_ROOTS="/,/"$/p' "$LAUNCHER" \
                  | sed -e 's/^FORBIDDEN_ROOTS="//' -e 's/"$//')
NROOT=0; NGHOST=0; NLIVE=0
while IFS= read -r r; do
  [ -z "$r" ] && continue
  NROOT=$((NROOT+1))
  if [ -d "$r" ]; then NLIVE=$((NLIVE+1)); printf '       LIVE  %s\n' "$r"
  else NGHOST=$((NGHOST+1)); printf '       GHOST %s\n' "$r"; fi
done <<< "$FORBIDDEN_ROOTS"
ok "(r7) $NROOT protected roots: $NLIVE on disk, $NGHOST ghosts -- both counts REPORTED"
# The one this item's ancestry got wrong, driven by name.
if [ -d /home/ubuntu/certonomous-runs/CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility ]; then
  case "$FORBIDDEN_ROOTS" in
    *CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility*)
      ok "(r7) the REAL feasibility root CURRICULUM-SO3aF-... exists AND is protected (neither ancestor protected it)" ;;
    *) bad "(r7) CURRICULUM-SO3aF-... exists on disk and is NOT in the protected list" ;;
  esac
else
  echo "       CURRICULUM-SO3aF-... not_on_disk -- LEG NOT EXERCISED"
fi
# And SO-3aR2's own graded run root, which this launcher's staging path would
# `rm -rf` if BASE ever resolved to it.
case "$FORBIDDEN_ROOTS" in
  *CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient*)
    ok "(r7) SO-3aR2's GRADED run root is protected (it holds a closed item verdict GATE FAIL)" ;;
  *) bad "(r7) SO-3aR2's graded run root is NOT protected" ;;
esac

echo
echo "(r8) THE ARM COMMANDS.  Every declared arm has one; the O arms run the"
echo "     driver; the endpoint arms pass -xopt; nothing runs at np != 1."
for A in $DECLARED; do
  # The command table lives below `--source-only`, so it is READ from the file
  # rather than evaluated.  Reading it is the point: a reviewer checks the same
  # bytes the launcher executes.
  # MATCH THE WHOLE CASE LABEL, not just a label that STARTS with this arm.
  # The first draft matched `^  <arm>)` or `^  [A-Z|-]*\|?<arm>)`, which finds
  # `O-P` inside `O-S|O-P)` and MISSES `O-S` -- so three arms reported "no CMD
  # row" while their command was on the line above the one the pattern found.
  # A grep that only finds the LAST alternative of an alternation is a check
  # that grades half the table.
  L=$(grep -aE "^  ([A-Z|0-9-]*\|)?$A(\|[A-Z|0-9-]*)?\)" "$LAUNCHER" | grep -a 'CMD=' | head -1)
  if [ -z "$L" ]; then bad "(r8) $A has no CMD row in the launcher's command table"; continue; fi
  case "$A" in
    O-S|O-P)
      case "$L" in *"-task run_driver"*) ok "(r8) $A runs the optimiser (-task run_driver)";;
                   *) bad "(r8) $A does not run the driver: $L";; esac ;;
    XE-S|XE-P|FE-S|FE-P)
      case "$L" in *"-xopt so3_xopt.json"*) ok "(r8) $A passes -xopt -- section 9's endpoint check";;
                   *) bad "(r8) $A does not pass -xopt: $L";; esac ;;
    MESH) case "$L" in *checkMesh*) ok "(r8) MESH runs preProcessing + checkMesh";;
                       *) bad "(r8) MESH command unexpected: $L";; esac ;;
  esac
  case "$L" in
    *"-np \$RANKS"*|*checkMesh*) : ;;
    *) bad "(r8) $A does not take its rank count from the registered table: $L" ;;
  esac
done

echo
echo "(r9) THE STALL WATCHDOG IS ARMED ON THE O ARMS AND DECLARED ABSENT"
echo "     OTHERWISE.  A guard whose absence is invisible is worse than one that"
echo "     never fired."
if grep -aq 'SO3_STALLDOG arm=\$ARM armed=NO reason=detector_absent' "$LAUNCHER"; then
  ok "(r9) an absent detector is DECLARED (armed=NO with a reason), never silently skipped"
else
  bad "(r9) the launcher has no declared-absent branch for the stall watchdog"
fi
if grep -aq 'SO3_STALL_NOT_FIRED' "$LAUNCHER"; then
  ok "(r9) a watchdog that did NOT fire says so -- it is not read as convergence"
else
  bad "(r9) the launcher does not report a non-firing watchdog"
fi
if grep -aq 'python3 "\$BASE/so3_age_guard.py" pin' "$LAUNCHER" \
   && grep -aq 'so3_age_guard.py" verify' "$LAUNCHER"; then
  ok "(r9) the manifest age guard is PINNED pre-launch and VERIFIED post-run"
else
  bad "(r9) the manifest age guard is not both pinned and verified"
fi

echo
echo "(r10) THE ANCESTOR'S DEFECTIVE FORM IS PRESENT AS AN EXECUTABLE QUOTATION"
echo "      AND IS NEVER ON A LAUNCH PATH."
if [ "$(tmo_for_C188_DEFECTIVE_FORM 2000.0 4)" = "30000" ]; then
  ok "(r10) the quoted ancestor form reproduces C-188's 30,000 s deadline"
else
  bad "(r10) the quoted ancestor form gives $(tmo_for_C188_DEFECTIVE_FORM 2000.0 4), not 30000"
fi
# ANCHORED AT THE LINE START.  An unanchored `TMO=$(...` also matches
# `OLD_TMO=$(...`, which is the DIAGNOSTIC assignment this leg is supposed to
# tolerate -- so the first draft of this leg reported the quotation as being on
# a launch path when the only thing it had found was its own diagnostic.
N=$(grep -acE '^TMO=\$\(tmo_for_C188_DEFECTIVE_FORM' "$LAUNCHER" || true)
if [ "${N:-0}" -eq 0 ]; then
  ok "(r10) the defective form is NEVER assigned to TMO on any path"
else
  bad "(r10) the defective form reaches TMO on $N line(s) -- it is on a launch path"
fi

echo
echo "DRIVE $((PASS+FAIL)) checks, $FAIL fail"
[ "$FAIL" -eq 0 ] || exit 1
