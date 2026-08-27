#!/bin/bash
# =============================================================================
# F12 ARM E -- THE FIRST PRESSURE SOLVE.  TWO-ARM LAUNCHER (E1, E2).
#
# Registered at verification/campaign/F12_FIRST_PRESSURE_SOLVE_PREREGISTRATION.md
#   frozen at commit 86af0a31, blob 2bb885c6c969f70e21551ec479a0742ae9f953eb,
#   frozen body = lines 1-176,
#   sha256 ac6a74e3259eac7e779f970315bc16411b0e8b0a981e372e822689dbfe806788.
# This script is the instrument that freeze's section 8 says must exist before
# anything runs.  Its own git blob is pinned INSIDE the pre-registration's
# pre-compute amendment and is re-checked below, so rule 2's "the frozen file
# IS the file that ran" is checkable in both directions.
#
# THIS ARM GRADES NOTHING.  It moves no gate, threshold, band, cap or label.
# F12 rung 1 stands NOT A RESULT; rungs 2-5 stand BLOCKED.  Rung 2's
# rate_calibration_gate() interlock is not invoked, not imported, not read
# around and not edited here.  No verdict-vocabulary word is emitted by this
# script or by its reader.
#
# -----------------------------------------------------------------------------
# THE 30-SECOND PER-ARM `timeout` IS A HANG DETECTOR, NOT A BUDGET TRACKER.
# -----------------------------------------------------------------------------
# Registered estimate 0.0795 core-min; registered cap 0.50 core-min; the ratio
# is 6.3x and the freeze states openly WHY: ClockTime has integer-second
# resolution, so quantisation alone is +/-0.0167 core-min per arm = 42% of the
# whole estimate.  A 1.5x cap on a five-second arm would abort on rounding.
# The cap is set from the wall-clock envelope, never from the estimate, and it
# exists to kill a hang.  DO NOT READ THE 6.3x RATIO AS SLOPPY COSTING -- it is
# quantisation, and the freeze says so in section 6.  The cap is NEVER raised;
# a kill leaves an incomplete arm and an incomplete arm is REFUSED.
# -----------------------------------------------------------------------------
#
# E2's CONFIGURATION IS A MEASUREMENT INSTRUMENT AND MAY NEVER BE CARRIED INTO
# ANY GRADED RUN.  That is enforced structurally, not by prose: E2's case is
# built only under a path containing the token E2_INSTRUMENT_NEVER_GRADE, the
# script REFUSES if that token is absent from the path it is about to write,
# and a DO_NOT_GRADE marker file is written into E2's case root and evidence
# directory before the solver is allowed to start.
#
# `set -e` is NOT relied upon: every step captures its status explicitly.
set -u

REPO=/home/ubuntu/Certonomous
SRC=$REPO/verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79
INSTR=$REPO/verification/runs/F12_runs/first_pressure_solve_instrument_2026-08-27
READER=$INSTR/readers/analyse_first_pressure_solve.py
SELF=$INSTR/run_arms_e.sh
PREREG=$REPO/verification/campaign/F12_FIRST_PRESSURE_SOLVE_PREREGISTRATION.md
PREREG_REL=verification/campaign/F12_FIRST_PRESSURE_SOLVE_PREREGISTRATION.md

# Section 7 of the freeze names THIS repository path as the Arm E run directory
# and records it ABSENT.  It is created ONLY here, by the launcher, at the
# moment compute begins.  That makes the absence condition a real invariant:
# if this path exists, compute has happened.
REC=$REPO/verification/runs/F12_runs/first_pressure_solve_2026-08-27
# Transient case trees live OUTSIDE the repository, as every other F12 arm's do.
ROOT=/home/ubuntu/certonomous-runs/F12_first_pressure_solve_2026-08-27

PREREG_FROZEN_BODY_LINES=176
PREREG_FROZEN_BODY_SHA=ac6a74e3259eac7e779f970315bc16411b0e8b0a981e372e822689dbfe806788
PREREG_FROZEN_BLOB=2bb885c6c969f70e21551ec479a0742ae9f953eb

RUNGS="attempt2_medium_workshop_M0.734_a2.79 attempt2_fine_workshop_M0.734_a2.79 attempt2_medium_tape_M0.730_a2.79 attempt2_medium_farfield2x_M0.734_a2.79"

CAP_WALL_S=30          # HANG DETECTOR (see banner above), per arm
CAP_CORE_MIN=0.50      # registered cap, both arms, 1 rank -- NEVER raised
RANKS=1

# The 18 files that must not change between rung 1 and an arm.  controlDict is
# deliberately NOT in this list: it carries the registered output-control delta.
MUST_NOT_CHANGE="system/fvSolution system/fvSchemes system/blockMeshDict system/decomposeParDict \
0/T 0/U 0/p 0/k 0/omega 0/nut 0/alphat \
constant/thermophysicalProperties constant/turbulenceProperties \
constant/polyMesh/points constant/polyMesh/faces constant/polyMesh/owner \
constant/polyMesh/neighbour constant/polyMesh/boundary"

MESH_FILES="constant/polyMesh/points constant/polyMesh/faces constant/polyMesh/owner constant/polyMesh/neighbour"

# ---- 0. THE FREEZE MUST BE THE FILE THAT RAN, AND SO MUST THIS INSTRUMENT ---
BODY=$(head -$PREREG_FROZEN_BODY_LINES $PREREG | sha256sum | cut -d' ' -f1)
[ "$BODY" = "$PREREG_FROZEN_BODY_SHA" ] || { echo "ABORT: FROZEN BODY (lines 1-$PREREG_FROZEN_BODY_LINES) CHANGED: $BODY"; exit 1; }
DISK_BLOB=$(cd $REPO && git hash-object $PREREG_REL)
HEAD_BLOB=$(cd $REPO && git rev-parse HEAD:$PREREG_REL)
[ "$DISK_BLOB" = "$HEAD_BLOB" ] || { echo "ABORT: prereg on disk != HEAD ($DISK_BLOB vs $HEAD_BLOB)"; exit 1; }

# The pre-compute amendment pins the grading path by blob.  Read those pins OUT
# of the frozen document and require the files on disk to match them.  A file
# cannot contain its own hash, so the pin lives in the document and the check
# lives here -- the loop closes without self-reference.
L_BLOB=$(cd $REPO && git hash-object verification/runs/F12_runs/first_pressure_solve_instrument_2026-08-27/run_arms_e.sh)
R_BLOB=$(cd $REPO && git hash-object verification/runs/F12_runs/first_pressure_solve_instrument_2026-08-27/readers/analyse_first_pressure_solve.py)
L_SHA=$(sha256sum $SELF | cut -d' ' -f1)
R_SHA=$(sha256sum $READER | cut -d' ' -f1)
grep -q "launcher git-blob \`$L_BLOB\`" $PREREG || { echo "ABORT: launcher blob $L_BLOB is NOT the blob pinned in the pre-registration"; exit 1; }
grep -q "reader git-blob \`$R_BLOB\`"   $PREREG || { echo "ABORT: reader blob $R_BLOB is NOT the blob pinned in the pre-registration"; exit 1; }
grep -q "launcher sha256 \`$L_SHA\`"    $PREREG || { echo "ABORT: launcher sha256 $L_SHA is NOT the sha256 pinned in the pre-registration"; exit 1; }
grep -q "reader sha256 \`$R_SHA\`"      $PREREG || { echo "ABORT: reader sha256 $R_SHA is NOT the sha256 pinned in the pre-registration"; exit 1; }
L_HEAD=$(cd $REPO && git rev-parse HEAD:verification/runs/F12_runs/first_pressure_solve_instrument_2026-08-27/run_arms_e.sh)
R_HEAD=$(cd $REPO && git rev-parse HEAD:verification/runs/F12_runs/first_pressure_solve_instrument_2026-08-27/readers/analyse_first_pressure_solve.py)
[ "$L_BLOB" = "$L_HEAD" ] || { echo "ABORT: launcher on disk != HEAD"; exit 1; }
[ "$R_BLOB" = "$R_HEAD" ] || { echo "ABORT: reader on disk != HEAD"; exit 1; }

# ---- 1. RULE-2 / RULE-4 PRE-GUARDS -----------------------------------------
if [ -e "$REC" ]; then echo "ABORT: $REC ALREADY EXISTS -- compute has already occurred on Arm E; this launcher runs ONCE"; exit 1; fi
if [ -e "$ROOT" ]; then echo "ABORT: $ROOT ALREADY EXISTS -- rule 4 guard"; exit 1; fi
for d in $RUNGS; do
  if [ -e "$REPO/verification/runs/F12_runs/$d" ]; then echo "ABORT: registered rung dir $d EXISTS"; exit 1; fi
done

mkdir -p $REC/evidence $ROOT || { echo "ABORT: mkdir"; exit 1; }
echo "FREEZE OK  frozen body (1-$PREREG_FROZEN_BODY_LINES) $BODY | HEAD blob $HEAD_BLOB (frozen at 86af0a31 as $PREREG_FROZEN_BLOB)" | tee $REC/evidence/freeze_verified.txt
{ echo "launcher git-blob $L_BLOB sha256 $L_SHA"
  echo "reader   git-blob $R_BLOB sha256 $R_SHA"
  echo "both matched the pins carried in the pre-registration AND HEAD"; } | tee $REC/evidence/grading_path_verified.txt
echo "PRE-ASSERT: rungs 2-5 ABSENT (test -e, this invocation) at $(date -u +%FT%TZ)" | tee $REC/evidence/rung_absence_before.txt

find $SRC -type f | sort | xargs sha256sum 2>/dev/null | sha256sum > $REC/evidence/rung1_fingerprint_before.txt
[ -s $REC/evidence/rung1_fingerprint_before.txt ] || { echo "ABORT: rung1 fingerprint empty"; exit 1; }

# ---- 2. GEOMETRY CASE (cell centres) ---------------------------------------
# writeCellCentres is run in a SEPARATE case so that E1's and E2's case trees
# contain nothing but the registered dictionaries and the solver's own output.
# Its mesh identity to rung 1 is asserted, so its 0/C describes the arms' mesh.
GEOM=$ROOT/geom
build_geom () {
  if [ -e "$GEOM" ]; then echo "ABORT[geom]: exists"; return 1; fi
  mkdir -p $GEOM || return 1
  cp -a $SRC/0 $SRC/constant $SRC/system $GEOM/ || return 1
  rm -f $GEOM/system/controlDict.orig
  ( cd $GEOM && setsid bash -c 'timeout 60 openfoam2606 postProcess -func writeCellCentres -time 0 > log.writeCellCentres 2>&1; echo $? > RC_geom.txt; sync' )
  local rc; rc=$(cat $GEOM/RC_geom.txt 2>/dev/null)
  case "$rc" in ''|*[!0-9]*) echo "ABORT[geom]: RC_geom.txt missing/empty/non-integer"; return 1;; esac
  [ "$rc" = "0" ] || { echo "ABORT[geom]: writeCellCentres rc=$rc"; return 1; }
  [ -f "$GEOM/0/C" ] || { echo "ABORT[geom]: 0/C not written"; return 1; }
  cp $GEOM/0/C $REC/evidence/cellCentres_C || return 1
  cp $GEOM/log.writeCellCentres $REC/evidence/log.writeCellCentres || return 1
  # C4 limb: the geometry case's mesh IS rung 1's mesh.
  : > $REC/evidence/mesh_identity.txt
  local nbad=0
  for f in $MESH_FILES; do
    local a b
    a=$(sha256sum $SRC/$f 2>/dev/null | cut -d' ' -f1)
    b=$(sha256sum $GEOM/$f 2>/dev/null | cut -d' ' -f1)
    if [ -n "$a" ] && [ "$a" = "$b" ]; then echo "MESH IDENTICAL geom $f $a" >> $REC/evidence/mesh_identity.txt
    else echo "MESH DIFFERS   geom $f src=$a arm=$b" >> $REC/evidence/mesh_identity.txt; nbad=$((nbad+1)); fi
  done
  [ "$nbad" = "0" ] || { echo "ABORT[geom]: mesh differs from rung 1 in $nbad files"; return 1; }
  echo "geom: 0/C written; mesh identical to rung 1 in all 4 polyMesh files"
  return 0
}

# ---- 3. AN ARM -------------------------------------------------------------
run_arm () {
  ARM=$1              # E1 | E2
  ARMDIR=$2           # directory name under $ROOT
  CASE=$ROOT/$ARMDIR/case
  EV=$REC/evidence/$ARM
  mkdir -p $EV || return 1
  echo; echo "================= ARM $ARM ================="

  # E2 STRUCTURAL INTERLOCK -- the path itself must carry the never-grade token.
  if [ "$ARM" = "E2" ]; then
    case "$CASE" in
      *E2_INSTRUMENT_NEVER_GRADE*) : ;;
      *) echo "ABORT[E2]: refusing to build E2 under a path that does not carry the token E2_INSTRUMENT_NEVER_GRADE ($CASE)"; return 1 ;;
    esac
  fi

  # rule-4 guard: refuse a case where 0/ or a time dir already exists
  if [ -e "$CASE" ]; then echo "ABORT[$ARM]: $CASE already exists -- rule 4 guard"; return 1; fi
  mkdir -p $CASE || { echo "ABORT[$ARM]: mkdir"; return 1; }
  cp -a $SRC/0 $SRC/constant $SRC/system $CASE/ || { echo "ABORT[$ARM]: copy"; return 1; }
  rm -f $CASE/system/controlDict.orig
  NT=$(ls -d $CASE/[0-9]* 2>/dev/null | grep -v '/0$' | wc -l)
  [ "$NT" = "0" ] || { echo "ABORT[$ARM]: $NT time dirs already present"; return 1; }

  # ---- the controlDict output-control delta (section 2 of the freeze) ----
  cp $CASE/system/controlDict $ROOT/$ARMDIR/controlDict_BEFORE || { echo "ABORT[$ARM]: cd copy"; return 1; }
  sed -i -e 's/^endTime  *6000;/endTime         1;/' \
         -e 's/^writeInterval  *6000;/writeInterval   1;/' \
         -e 's/^purgeWrite  *1;/purgeWrite      0;/' $CASE/system/controlDict || { echo "ABORT[$ARM]: sed cd"; return 1; }
  grep -q '^writeCompression' $CASE/system/controlDict || \
    sed -i 's/^writeFormat  *ascii;/writeFormat     ascii;\nwriteCompression off;/' $CASE/system/controlDict
  diff $ROOT/$ARMDIR/controlDict_BEFORE $CASE/system/controlDict > $EV/controlDict_THE_ENTIRE_DELTA.diff
  grep -qE '^endTime +1;' $CASE/system/controlDict          || { echo "ABORT[$ARM]: endTime"; return 1; }
  grep -qE '^writeInterval +1;' $CASE/system/controlDict    || { echo "ABORT[$ARM]: writeInterval"; return 1; }
  grep -qE '^purgeWrite +0;' $CASE/system/controlDict       || { echo "ABORT[$ARM]: purgeWrite"; return 1; }
  grep -qE '^writeCompression +off;' $CASE/system/controlDict || { echo "ABORT[$ARM]: writeCompression"; return 1; }

  # ---- E2's ONE change: pMinFactor and pMaxFactor REMOVED, nothing else ----
  if [ "$ARM" = "E2" ]; then
    sed -i -e '/^    pMinFactor      0\.1;$/d' -e '/^    pMaxFactor      2;$/d' $CASE/system/fvSolution || { echo "ABORT[E2]: sed lever"; return 1; }
    grep -q 'pMinFactor' $CASE/system/fvSolution && { echo "ABORT[E2]: pMinFactor still present"; return 1; }
    grep -q 'pMaxFactor' $CASE/system/fvSolution && { echo "ABORT[E2]: pMaxFactor still present"; return 1; }
    diff $SRC/system/fvSolution $CASE/system/fvSolution > $EV/lever_THE_ENTIRE_DELTA.diff
    NCH=$(grep -c '^[<>]' $EV/lever_THE_ENTIRE_DELTA.diff)
    [ "$NCH" = "2" ] || { echo "ABORT[E2]: lever diff has $NCH changed lines, expected exactly 2"; return 1; }
    NDEL=$(grep -c '^< ' $EV/lever_THE_ENTIRE_DELTA.diff)
    NADD=$(grep -c '^> ' $EV/lever_THE_ENTIRE_DELTA.diff)
    [ "$NDEL" = "2" ] && [ "$NADD" = "0" ] || { echo "ABORT[E2]: lever diff is $NDEL deletions / $NADD additions, expected 2 / 0"; return 1; }
    grep -q '^<     pMinFactor      0\.1;$' $EV/lever_THE_ENTIRE_DELTA.diff || { echo "ABORT[E2]: the deleted lines are not pMinFactor/pMaxFactor"; return 1; }
    grep -q '^<     pMaxFactor      2;$'    $EV/lever_THE_ENTIRE_DELTA.diff || { echo "ABORT[E2]: the deleted lines are not pMinFactor/pMaxFactor"; return 1; }
    cat > $CASE/DO_NOT_GRADE_INSTRUMENT_ONLY.txt <<'MARK'
E2 -- MEASUREMENT INSTRUMENT.  MAY NEVER BE CARRIED INTO ANY GRADED RUN.
pMinFactor and pMaxFactor have been REMOVED from the SIMPLE block so that
pressureControl does not limit and the written p at time 1 is the PRE-CLIP
field.  Removing a limiter to SEE a field is a measurement.  Removing it to
SURVIVE would be the anti-gaming clause's "parameter hunt" and is forbidden.
This case tree is not a candidate configuration, is not a repair, and is not a
tuning.  Nothing here may be copied into a rung, a ladder or any graded case.
Registered: verification/campaign/F12_FIRST_PRESSURE_SOLVE_PREREGISTRATION.md
section 2, blob 2bb885c6c969f70e21551ec479a0742ae9f953eb.
MARK
    cp $CASE/DO_NOT_GRADE_INSTRUMENT_ONLY.txt $EV/DO_NOT_GRADE_INSTRUMENT_ONLY.txt
    [ -f "$CASE/DO_NOT_GRADE_INSTRUMENT_ONLY.txt" ] || { echo "ABORT[E2]: marker not written"; return 1; }
  fi

  # ---- C5: per-file byte identity of the 18 dictionaries, PROVEN not asserted
  : > $EV/case_identity_18.txt
  N_OK=0; N_BAD=0; BADLIST=""
  for f in $MUST_NOT_CHANGE; do
    A=$(sha256sum $SRC/$f 2>/dev/null | cut -d' ' -f1)
    B=$(sha256sum $CASE/$f 2>/dev/null | cut -d' ' -f1)
    if [ -n "$A" ] && [ "$A" = "$B" ]; then echo "IDENTICAL $f $A" >> $EV/case_identity_18.txt; N_OK=$((N_OK+1));
    else echo "DIFFERS   $f src=$A arm=$B" >> $EV/case_identity_18.txt; N_BAD=$((N_BAD+1)); BADLIST="$BADLIST $f"; fi
  done
  echo "identical $N_OK / differ $N_BAD ; differing:$BADLIST" >> $EV/case_identity_18.txt
  if [ "$ARM" = "E1" ]; then
    [ "$N_OK" = "18" ] && [ "$N_BAD" = "0" ] || { echo "ABORT[E1]: identity $N_OK/18 differ $N_BAD ($BADLIST)"; return 1; }
    echo "E1 CASE IDENTITY 18/18 -- every physics dictionary byte-identical to rung 1, proven per file by sha256"
  else
    [ "$N_OK" = "17" ] && [ "$N_BAD" = "1" ] || { echo "ABORT[E2]: identity $N_OK/18 differ $N_BAD ($BADLIST)"; return 1; }
    [ "$BADLIST" = " system/fvSolution" ] || { echo "ABORT[E2]: the differing file is '$BADLIST', not system/fvSolution"; return 1; }
    echo "E2 CASE IDENTITY 17/18 -- the ONE differing file is system/fvSolution, differing in exactly 2 deleted lines"
  fi

  # ---- C4 limb: this arm's mesh IS rung 1's mesh ----
  for f in $MESH_FILES; do
    A=$(sha256sum $SRC/$f 2>/dev/null | cut -d' ' -f1)
    B=$(sha256sum $CASE/$f 2>/dev/null | cut -d' ' -f1)
    if [ -n "$A" ] && [ "$A" = "$B" ]; then echo "MESH IDENTICAL $ARM $f $A" >> $REC/evidence/mesh_identity.txt
    else echo "MESH DIFFERS   $ARM $f src=$A arm=$B" >> $REC/evidence/mesh_identity.txt; echo "ABORT[$ARM]: mesh differs"; return 1; fi
  done

  # ---- AGE GUARD: 0/T is touched LAST, so it dates the run ----
  touch $CASE/0/T || { echo "ABORT[$ARM]: touch 0/T"; return 1; }
  sync
  python3 -c "import os,sys;print(f'{os.stat(sys.argv[1]).st_mtime_ns}')" $CASE/0/T > $EV/age_guard_0T_mtime_ns.txt

  # ---- FIRE.  30 s timeout = HANG DETECTOR (see banner).  rc captured INSIDE
  #      the detached wrapper: `setsid <cmd>` returns 0 for every outcome.
  date -u +%FT%TZ > $EV/START_UTC.txt
  cat /proc/loadavg > $EV/CONTENTION_at_launch.txt
  T0=$(date +%s.%N)
  ( cd $CASE && setsid bash -c "timeout $CAP_WALL_S openfoam2606 rhoSimpleFoam > log.rhoSimpleFoam 2>&1; echo \$? > RC.txt; sync" )
  T1=$(date +%s.%N)
  python3 -c "print(f'{$T1-$T0:.6f}')" > $EV/WALL_S.txt
  cat /proc/loadavg > $EV/CONTENTION_at_end.txt
  date -u +%FT%TZ > $EV/END_UTC.txt
  sync

  RC=$(cat $CASE/RC.txt 2>/dev/null)
  case "$RC" in ''|*[!0-9]*) echo "REFUSED[$ARM]: RC.txt missing/empty/non-integer -- rc is NOT MEASURED"; return 1;; esac
  echo "$RC" > $EV/RC.txt
  if [ "$RC" = "124" ]; then
    echo "REFUSED[$ARM]: the ${CAP_WALL_S}s HANG DETECTOR fired (rc 124).  The arm is INCOMPLETE and is refused."
    echo "THE CAP IS NEVER RAISED." ; return 1
  fi

  # ---- cap watch, in the lab's unit ----
  W=$(cat $EV/WALL_S.txt)
  python3 -c "
w=$W; r=$RANKS; cm=w*r/60.0
print(f'{cm:.6f}')" > $EV/CORE_MIN.txt
  CM=$(cat $EV/CORE_MIN.txt)
  echo "$ARM: rc=$RC wall=${W}s core-min=$CM (cap for BOTH arms $CAP_CORE_MIN core-min; the 30s timeout is a HANG DETECTOR, not a budget tracker)"

  cp $CASE/log.rhoSimpleFoam $EV/log.rhoSimpleFoam || { echo "ABORT[$ARM]: log copy"; return 1; }
  if [ -d "$CASE/1" ]; then
    mkdir -p $EV/time1
    for f in p U T rho phi; do
      [ -f "$CASE/1/$f" ] && cp $CASE/1/$f $EV/time1/$f
    done
    python3 -c "
import os,sys,json
c=sys.argv[1]; out={}
for f in ('p','U','T','rho','phi'):
    q=os.path.join(c,'1',f)
    out[f]=os.stat(q).st_mtime_ns if os.path.exists(q) else None
print(json.dumps(out))" $CASE > $EV/time1_mtime_ns.json
  fi
  echo "$ARM: times written = $(ls -d $CASE/[0-9]* 2>/dev/null | wc -l)"
  echo "$CASE" > $EV/CASE_PATH.txt

  # ---- C6 post-assert, this invocation ----
  find $SRC -type f | sort | xargs sha256sum 2>/dev/null | sha256sum > $EV/rung1_fingerprint_after.txt
  cmp -s $REC/evidence/rung1_fingerprint_before.txt $EV/rung1_fingerprint_after.txt \
    && echo "$ARM: RUNG-1 FINGERPRINT UNCHANGED" || { echo "ABORT[$ARM]: rung 1 CHANGED"; return 1; }
  for d in $RUNGS; do
    if [ -e "$REPO/verification/runs/F12_runs/$d" ]; then echo "ABORT[$ARM]: registered rung dir $d APPEARED"; return 1; fi
  done
  echo "$ARM: POST-ASSERT OK -- rungs 2-5 still ABSENT (test -e, this invocation)"
  return 0
}

# ---- 4. DRIVE --------------------------------------------------------------
# E1 is the control and is fired FIRST, by the invocation and not merely by
# ordering: the caller names the arms.
[ $# -ge 1 ] || { echo "usage: run_arms_e.sh E1|E2 [...]   (E1 first; E2 is an INSTRUMENT, never a graded configuration)"; exit 2; }
FAIL=0
build_geom || FAIL=1
if [ "$FAIL" = "0" ]; then
for A in "$@"; do
  case "$A" in
    E1) run_arm E1 E1 || FAIL=1 ;;
    E2) run_arm E2 E2_INSTRUMENT_NEVER_GRADE || FAIL=1 ;;
    *) echo "ABORT: unknown arm '$A'"; FAIL=1 ;;
  esac
  [ "$FAIL" = "0" ] || break
done
fi

# ---- 5. TOTAL COST, in the lab's unit --------------------------------------
python3 - "$REC" <<'PYCOST'
import os, sys
rec = sys.argv[1]; tot = 0.0; rows = []
for arm in ("E1", "E2"):
    p = os.path.join(rec, "evidence", arm, "CORE_MIN.txt")
    if os.path.exists(p):
        v = float(open(p).read().strip()); tot += v; rows.append(f"{arm} {v:.6f} core-min")
cap = 0.50
print("COST: " + "; ".join(rows) + f"; TOTAL {tot:.6f} core-min; registered estimate 0.079500; cap {cap:.2f}")
print(f"COST: ratio actual/predicted = {tot/0.0795:.3f}" if tot else "COST: no arm completed")
print("COST: dollars are DERIVED, NOT MEASURED ($0.0513/core-h, c7a.4xlarge, reported-by-owner;")
print("      the box cannot read its own billing, COMPUTE_BUDGET_CHARTER.md sec 5)")
print(f"COST: derived $ = {tot/60.0*0.0513:.8f}")
open(os.path.join(rec, "evidence", "CORE_MIN_TOTAL.txt"), "w").write(f"{tot:.6f}\n")
sys.exit(2 if tot > cap else 0)
PYCOST
COSTRC=$?
if [ "$COSTRC" != "0" ]; then
  echo "REFUSED: the registered cap of $CAP_CORE_MIN core-min was EXCEEDED.  An overrun STOPS the run; it does not get a new budget."
  FAIL=1
fi

echo; echo "RUNNER_EXIT=$FAIL"
echo "$FAIL" > $REC/evidence/RUNNER_RC.txt
sync
exit $FAIL
