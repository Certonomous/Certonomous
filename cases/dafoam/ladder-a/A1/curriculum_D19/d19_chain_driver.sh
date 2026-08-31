#!/usr/bin/env bash
# ===========================================================================
# D19 CHAIN DRIVER -- PHASE 1 ONLY.  THIS FILE LAUNCHES NO OPTIMISER.
# ===========================================================================
#
# PHASE 2 IS NOT WIRED HERE, DELIBERATELY, AND THIS IS A DEPARTURE FROM THE
# REGISTERED DRIVER DESIGN THAT IS DISCLOSED RATHER THAN SILENT.
#
# PREREGISTRATION.md section 2 describes a driver that "evaluates phase 1's gates
# and launches phase 2's arms ONLY on `G19-1a PASS` and `G19-1b PASS` and
# `G19-1d PASS`".  The brief that built this file withholds authorisation for
# phase 2: phase 2 is gated on phase 1's registered branch AND on the
# dafoam-supervisor's own read of this instrument.  So this driver implements the
# strictly MORE CONSERVATIVE half: it runs phase 1, grades phase 1, writes
# `STATUS.D19_chain = PHASE1_COMPLETE_PHASE2_NOT_LAUNCHED_NOT_AUTHORISED`, and
# STOPS.
#
# This moves NO gate, NO threshold, NO cap and NO label.  A driver that launches
# phase 2 NEVER cannot produce a result the registration forbids -- it can only
# fail to produce one the registration would have allowed.  Withholding a launch
# is always available; granting one is not.  Launching phase 2 is the
# dafoam-supervisor's call and requires its own dispatch.
#
# DERIVED from `curriculum_D15/d15_chain_driver.sh` (md5
# 89c9b7e7e43e7dd12d1c551dadfa80c8 lineage) with these registered deltas:
#   (1) item names, run root, launcher, grader, pidfile, MD5s;
#   (2) PATCHED IMAGE ON EVERY ARM (PREREGISTRATION.md section 3: phase 1 is
#       "PATCHED image only"), including MESH -- D15 ran MESH on SHIPPED, and the
#       MESH arm's byte-identity assertion against D15's mesh is what makes that
#       difference a measurement instead of an assumption;
#   (3) THE SELECTOR STEP: between S2 and S1 the driver runs
#       `d19_select_step.py` on the HOST -- zero compute, pure arithmetic -- and
#       STOPS THE CHAIN if it refuses.  S1 cannot run without it, because S1's
#       step is the selector's output and is not a constant anywhere;
#   (4) the phase-1 ESTIMATE is written to the run root BEFORE the first arm
#       fires (rule 12: every run is costed before it runs);
#   (5) NO PHASE 2 BRANCH.  See the block above.
#
# Started ONLY detached, so it outlives the agent that started it:
#   setsid nohup bash d19_chain_driver.sh MESH X2 S2 S1 > <root>/chain_launch.out 2>&1 &
# NOTE `setsid timeout cmd` returns 0 for EVERY outcome, so rc is captured INSIDE
# this script, never around the setsid line.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d19_run_arm.sh"
GRADER="$HERE/d19_grade.py"
SELECTOR="$HERE/d19_select_step.py"
PRECOND="$HERE/d19_precondition.py"
IMG_PATCHED=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D19-a1-naca0012-subsonic-opt
TUT_SRC=/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/subsonic
H5_FLOOR_GIB=8.0; H5_SAMPLES=45; H5_WINDOW_S=60
AGG_POLL_S=30; AGG_BOUND_S=14400; AGG_CEILING_GIB=30.6

MD5_LAUNCHER=a3d449ef1e890d22c8e58e7db958a4f2
MD5_GRADER=b394db68525e6590d2269103bc0e8f44
MD5_SELECTOR=d65302e16a74c07f04cd3a11a6250108
MD5_PRECOND=c66fff1e4d07573d774523b5e39ad813
MD5_RUNSCRIPT=a5e18503ea29d0e37c3cf1668533cd34
MD5_XF=65c86d2c9b7b94dc905d78c89eb740a0
MD5_DECOMP=68ecc827562886fb43c3aedb0627b344
# the shipped tutorial's INPUT bytes, frozen here because the checkout is not
MD5_TUT_RUNSCRIPT=6537fa7641c4ccb20056f60f96f63b11
MD5_TUT_GEN=681f10659eb90457fca13fc933008b93
MD5_TUT_PREPROC=e25c8f8c32886112e3f9591196c695ad
MD5_TUT_PS=51dfed28e1bdb4cd33e0d8d7dabd586a
MD5_TUT_SS=4a6b8ef4501494c7693b71e88a2eabbf
MD5_TUT_FFD=6ddf378b028d03d8a18270488bee1759

test $# -ge 1 || { echo "ABORT usage: d19_chain_driver.sh <ARM...>"; exit 64; }
ARMS="$*"
for a in $ARMS; do
  case "$a" in
    MESH|X2|S2|S1) ;;
    *) echo "ABORT arm '$a' is not a PHASE 1 arm.  This driver runs phase 1 only and"
       echo "  will not launch an optimiser.  Registered phase-1 arms: MESH X2 S2 S1."
       exit 64 ;;
  esac
done
STATUS="$BASE/STATUS.D19_chain"; PIDFILE="$BASE/d19_driver.pid"
cd "$HERE" || exit 4

{ echo "$MD5_LAUNCHER  $LAUNCHER"; echo "$MD5_GRADER  $GRADER";
  echo "$MD5_SELECTOR  $SELECTOR"; echo "$MD5_PRECOND  $PRECOND"; } | md5sum -c - \
  || { echo "ABORT frozen instrument md5 drifted before staging"; exit 4; }

# ---- section 9 precondition: no D19 verdict without D15's SHIPPED GATE FAIL ----
python3 "$PRECOND" > /dev/null || { echo "ABORT G-PROV precondition refused before staging"; exit 7; }
echo "D19_PRECONDITION_OK travelling provenance readable"

# ---- ROOT STAGING on the first fire only ---------------------------------------
if [ ! -d "$BASE" ]; then
  test -d "$TUT_SRC" || { echo "ABORT tutorial source absent: $TUT_SRC"; exit 4; }
  { echo "$MD5_TUT_RUNSCRIPT  $TUT_SRC/runScript.py"; echo "$MD5_TUT_GEN  $TUT_SRC/genAirFoilMesh.py";
    echo "$MD5_TUT_PREPROC  $TUT_SRC/preProcessing.sh";
    echo "$MD5_TUT_PS  $TUT_SRC/profiles/NACA0012PS.profile";
    echo "$MD5_TUT_SS  $TUT_SRC/profiles/NACA0012SS.profile";
    echo "$MD5_TUT_FFD  $TUT_SRC/FFD/wingFFD.xyz"; } | md5sum -c - \
    || { echo "ABORT tutorial input md5 drifted (the checkout moved under this item; nothing staged)"; exit 4; }
  mkdir -p "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
  chmod 777 "$BASE" || { echo "ABORT chmod 777 $BASE (L-251)"; exit 4; }
  mkdir -p "$BASE/base" || exit 4
  cp -a "$TUT_SRC/0.orig" "$TUT_SRC/FFD" "$TUT_SRC/constant" "$TUT_SRC/system" \
        "$TUT_SRC/profiles" "$TUT_SRC/genAirFoilMesh.py" "$TUT_SRC/preProcessing.sh" \
        "$BASE/base/" || { echo "ABORT copy tutorial inputs"; exit 4; }
  rm -rf "$BASE/base/constant/polyMesh" 2>/dev/null
  # d15_decomposeParDict VERBATIM (PREREGISTRATION.md section 3).  NOTE: that file's
  # `method` is `scotch`, not the `simple` the registration's prose names; the
  # binding word is "verbatim", and reproducing D15 (G19-1a) requires D15's bytes.
  cp -a "$HERE/../curriculum_D15/d15_decomposeParDict" "$BASE/base/system/decomposeParDict" \
    || { echo "ABORT overlay decomposeParDict"; exit 4; }
  cp -a "$HERE/d19_runScript.py" "$HERE/d19_xf.py" "$BASE/" || { echo "ABORT copy instruments"; exit 4; }
  echo "ITEM=D19" > "$BASE/ledger.txt"
  echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) tut_src=$TUT_SRC phase=1 rows=PATCHED_ONLY" >> "$BASE/ledger.txt"
  # ---- (4) THE PHASE-1 ESTIMATE, REGISTERED BEFORE THE FIRST ARM FIRES ----------
  cat > "$BASE/PHASE1_COST_ESTIMATE.txt" <<EST
D19 PHASE 1 -- COST REGISTERED BEFORE LAUNCH (CLAUDE.md rule 12)
stamp=$(date -u +%Y%m%dT%H%M%SZ)
unit=core-minutes (wall_s x ranks / 60)
  arm   ranks   predicted   cap
  MESH    1        0.2       5.0
  X2      2        1.8      20.0
  S2      2        5.7      90.0
  S1      1        1.0      25.0
  PHASE 1 TOTAL     8.7     140.0
basis: PREREGISTRATION.md section 3 and section 10, whose per-primal figure is
  D15's own frozen ledger (F-P 3.433 core-min over 30 perturbed primals at np=2
  => ~0.113 core-min per perturbed primal).  S2 is 50 perturbed primals => 5.7.
item ceiling (both phases) 280.0 core-min.
dollars DERIVED at the owner-stated c7a.4xlarge \$0.0513/core-h: predicted
  \$0.0074 for phase 1.  DERIVED, NOT MEASURED -- the box cannot read its own
  billing (COMPUTE_BUDGET_CHARTER.md section 5).
STOP RULE: an arm exceeding its cap STOPS.  An overrun does not get a new budget.
PHASE 2 IS NOT AUTHORISED BY THIS DRIVER AND IS NOT COSTED HERE.
EST
  echo "D19_ROOT_STAGED base=$BASE mode=$(stat -c '%a' "$BASE")"
  echo "D19_PHASE1_ESTIMATE_REGISTERED 8.7 core-min predicted / 140.0 cap"
else
  echo "D19_ROOT_PRESENT base=$BASE (not re-staged)"
fi

{ echo "$MD5_RUNSCRIPT  $BASE/d19_runScript.py"; echo "$MD5_XF  $BASE/d19_xf.py";
  echo "$MD5_DECOMP  $BASE/base/system/decomposeParDict";
  echo "$MD5_TUT_GEN  $BASE/base/genAirFoilMesh.py";
  echo "$MD5_TUT_PREPROC  $BASE/base/preProcessing.sh";
  echo "$MD5_TUT_PS  $BASE/base/profiles/NACA0012PS.profile";
  echo "$MD5_TUT_SS  $BASE/base/profiles/NACA0012SS.profile";
  echo "$MD5_TUT_FFD  $BASE/base/FFD/wingFFD.xyz"; } | md5sum -c - \
  || { echo "ABORT staged instrument/input md5"; exit 4; }
test -f "$BASE/base/0.orig/U" || { echo "ABORT staged base/ has no 0.orig/U"; exit 4; }

if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."
    exit 3
  fi
fi
echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"' EXIT
echo "D19_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] phase=1"
echo "chain=started phase=1 arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) phase2=NOT_WIRED" >> "$STATUS"

mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
CHAIN_RC=0
for ARM in $ARMS; do
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || {
    echo "ABORT launcher md5 drifted before arm $ARM"
    echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    CHAIN_RC=4; break; }
  echo "preflight arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ image=$IMG_PATCHED row=PATCHED" > "$BASE/STATUS.$ARM"

  if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT ALREADY_BOUGHT arm $ARM has an rc=0 ledger row; a second record for one run is the defect."
    echo "rc=3 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=ALREADY_BOUGHT" >> "$BASE/STATUS.$ARM"
    echo "chain=REFUSED_ALREADY_BOUGHT arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    CHAIN_RC=3; break
  fi

  # ---- (3) THE SELECTOR runs on the HOST between S2 and S1 ---------------------
  if [ "$ARM" = "S1" ]; then
    echo "$MD5_SELECTOR  $SELECTOR" | md5sum -c - || {
      echo "ABORT selector md5 drifted"; CHAIN_RC=4; break; }
    python3 "$SELECTOR" --selftest > "$BASE/selector_selftest.out" 2>&1 || {
      echo "ABORT selector SELFTEST refused -- its controls do not fire; no selection is emitted"
      echo "chain=STOPPED_SELECTOR_SELFTEST stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
      CHAIN_RC=2; break; }
    python3 "$SELECTOR" --fd "$BASE/S2/d19_S.json" --out "$BASE/d19_selected_step.json" \
        > "$BASE/selector.out" 2>&1
    SRC=$?
    cat "$BASE/selector.out"
    if [ "$SRC" -ne 0 ]; then
      echo "ABORT selector refused on the real sweep (rc=$SRC); S1 has no registered step to run."
      echo "chain=STOPPED_SELECTOR arm=S1 rc=$SRC stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
      CHAIN_RC=$SRC; break
    fi
    echo "selector=OK stamp=$(date -u +%Y%m%dT%H%M%SZ) out=d19_selected_step.json" >> "$STATUS"
  fi

  # ---- H5: a WINDOW of MemAvailable, every sample above the floor --------------
  H5_FILE="$BASE/${ARM}_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"; BELOW=0; N=0; MIN=999
  STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))")
  for _ in $(seq 1 $H5_SAMPLES); do
    s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"
    MIN=$(python3 -c "print(min($MIN,$s))")
    [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1))
    sleep "$STEP"
  done
  echo "D19_H5_WINDOW arm=$ARM n=$N floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN samples_below_floor=$BELOW"
  if [ "$BELOW" -gt 0 ] || [ "$N" -ne "$H5_SAMPLES" ]; then
    echo "ABORT H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB.  A batch that OOMs is worse than a batch that queues."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_REFUSED below=$BELOW min_GiB=$MIN" >> "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_H5 arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    CHAIN_RC=6; break
  fi

  echo "D19_DRIVER arm=$ARM image=$IMG_PATCHED begin=$(date -u +%Y%m%dT%H%M%SZ)"
  bash "$LAUNCHER" "$ARM" "$IMG_PATCHED" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "D19_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then
    echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    CHAIN_RC=$rc; break
  fi
done

[ "$CHAIN_RC" -eq 0 ] && echo "chain=PHASE1_ARMS_COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"

# ---- the FROZEN grader on the artefacts (zero compute); rc is INFRASTRUCTURE (L-342)
GSTAMP=$(date -u +%Y%m%dT%H%M%SZ)
if echo "$MD5_GRADER  $GRADER" | md5sum -c - > /dev/null; then
  python3 "$GRADER" --root "$BASE" --out "$BASE/D19_phase1_grade_${GSTAMP}.json" \
      > "$BASE/D19_phase1_grade_${GSTAMP}.out" 2>&1
  GRC=$?
  echo "grader_rc=$GRC stamp=$GSTAMP out=D19_phase1_grade_${GSTAMP}.json note=comparator-exit-status-NOT-the-verdict" >> "$STATUS"
else
  echo "grader_rc=NOT_RUN stamp=$GSTAMP note=grader-md5-drifted-at-chain-end" >> "$STATUS"
fi

# ===========================================================================
# THE END OF THE LINE.  NO PHASE 2 BRANCH EXISTS IN THIS FILE.
# ===========================================================================
echo "chain=PHASE1_COMPLETE_PHASE2_NOT_LAUNCHED_NOT_AUTHORISED stamp=$(date -u +%Y%m%dT%H%M%SZ) chain_rc=$CHAIN_RC" >> "$STATUS"
echo "D19_DRIVER end=$(date -u +%Y%m%dT%H%M%SZ) chain_rc=$CHAIN_RC phase2=NOT_LAUNCHED"
echo "PHASE 2 IS NOT LAUNCHED BY THIS DRIVER.  Phase 2 requires the registered"
echo "branch of PREREGISTRATION.md section 2 AND the dafoam-supervisor's own read"
echo "of the phase-1 instrument.  Nothing here starts an optimiser."
exit "$CHAIN_RC"
