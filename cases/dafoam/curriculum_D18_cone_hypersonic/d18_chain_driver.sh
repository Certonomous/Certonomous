#!/usr/bin/env bash
# D18 chain driver -- DERIVED from curriculum_D16/d16_chain_driver.sh (itself from
# D15's and curriculum_D5/d5_chain_driver.sh, Addendum 2) with the REGISTERED DELTAS in
# PREREGISTRATION.md section 7 and d18_chain_driver_DELTAS_from_d16.diff (item
# names, the Cone_Supersonic tutorial source and its NINETEEN input md5s, per-arm
# memory caps and H5 floors -- X arms 8g / floor 12.0, the G-CPUSET overlap
# wait-and-retry, the CHAIN_DONE marker of D5 Addendum 3); the D5 lineage:
#   (1) item names, run root, launcher, pidfile, MD5s; the IMAGE is chosen PER
#       ARM from the arm name (MESH and *-S on the SHIPPED image, *-P on the
#       PATCHED image) -- this item BUYS BOTH ROWS (the two-row rule);
#   (2) AGGREGATE in the WAIT-AND-RETRY form (UPDATE F), unchanged; the cap
#       used is the ARM's registered cap (X 8 GiB, MESH/F 4 GiB);
#   (3) ALREADY_BOUGHT: unchanged;
#   (4) ROOT STAGING: the run root does not exist at freeze (the freeze
#       condition); the FIRST fire creates it (mode 777, L-251), copies the
#       SHIPPED TUTORIAL INPUTS read-only from /home/ubuntu/dafoam-tutorials
#       (0.orig, FFD, constant, system, preProcessing.sh) into base/,
#       overlays the REGISTERED decomposeParDict
#       (numberOfSubdomains 2), copies the two instruments from this case
#       directory, and md5-asserts EVERY staged input (tutorial files included:
#       the tutorial checkout is not frozen by this repo, so its bytes are);
#       the ledger opens with an exact `ITEM=D18` line and a STAGED line
#       (D5-DRIVER-DEF-1 corrected form, inherited);
#   (5) STATUS.<arm> opened at preflight and appended, unchanged; H5 floor PER
#       ARM = cap + 4 GiB headroom (the D4-SHIPPED 4.4 rule): X arms 12.0, others 8.0;
#   (5b) G-CPUSET: a LIVE container whose cpuset shares a core with this item's
#       registered cpuset -> WAIT-AND-RETRY (same form and bound as the aggregate
#       guard), so G12's delivered-cores floor is never failed by a disclosed
#       placement overlap (D8R 0,1,12,15 vs this item's 12,15);
#   (7) CHAIN_DONE (D5 Addendum 3 A3.5 form): one line appended on EVERY exit of a
#       started chain, so a later item can wait on it with no agent alive;
#   (6) the FROZEN GRADER runs on the artefacts at chain end (zero compute) so
#       the item closes with no agent alive (the D14-M form); its rc is
#       INFRASTRUCTURE (L-342), never the verdict.
# Runs the named arms IN ORDER through the frozen launcher and STOPS AT THE
# FIRST NON-ZERO rc.  Started ONLY detached (the queue runner's own form, or
#   setsid nohup bash d18_chain_driver.sh MESH X-S F-S X-P F-P > <root>/chain_launch.out 2>&1 &
# ) so it is its own session leader and outlives the agent that started it.
# Before each arm: launcher md5; the WINDOWED H5 gate (45 samples over 60 s,
# refuse on ANY sample below the floor); ALREADY_BOUGHT; AGGREGATE wait-and-retry.
# cwd is the CASE directory, never the run root (G-ROOT.5 b).
# Permission for detached launches: bc0e687e (Sanaa, boarded verbatim).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d18_run_arm.sh"
GRADER="$HERE/d18_grade.py"
IMG_SHIPPED=dafoam/opt-packages:latest
IMG_PATCHED=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic
TUT_SRC=/home/ubuntu/dafoam-tutorials/Cone_Supersonic
CPUSET_REGISTERED=12,15
PERMISSION=bc0e687e
H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6
AGG_POLL_S=30; AGG_BOUND_S=14400
# The launcher and grader are FROZEN (PREREGISTRATION.md section 7/8);
# asserted before EVERY arm so a mid-chain edit cannot change what runs.
MD5_LAUNCHER=1fd05704a7ef0ede0057c9b18283c775
MD5_GRADER=e4ade11ed9e3db18d2c4988b30e929b4
MD5_RUNSCRIPT=e6f0baf0e07a4ede7bff555e5e0ed332
MD5_XF=3e63a9fa945bc6d7b3196e1e3e084a7f
MD5_MACH=d6a5b389f0976801416bfd81909e0176   # d18_mach_agreement.py -- G-MACH, NEW in D18
MD5_DECOMP=68ecc827562886fb43c3aedb0627b344
# the shipped tutorial's INPUT bytes (NINETEEN files), frozen here because the checkout is not
MD5_TUT_RUNSCRIPT=8621862522cf2af72f381f0d97660b8a
MD5_TUT_PREPROC=124bd4bf27703b905d7591a189315c4d
MD5_TUT_FFD=99ec61c51bdcb1a4157cd3dcf7a86e9d
MD5_TUT_GENFFD=4c5a915092828df5725e25b9f708436d
MD5_TUT_BLOCKMESH=4bf634cee452845faafc44245d2d84b7
MD5_TUT_MIRROR=e2db0b7fbe75a9a08edf8ae6760edc16
MD5_TUT_CONTROL=33fbb919fd56d7e7668f732c3b298942
MD5_TUT_FVSCHEMES=5d01f5517b2c0411b98558d455d1a45d
MD5_TUT_FVSOLUTION=a7762882ea049b515126be40c093c14e
MD5_TUT_THERMO=a62f70974ab7f2685d8fb9550a1a875e
MD5_TUT_TURB=5b8c8055045e4959a21649d262a21e3a
MD5_TUT_T=c2f4edd5bb25a426d01160e799414e82
MD5_TUT_U=3e7c37d4546eba3794f59c913166e0ec
MD5_TUT_P=9ffd0533f963b8a4df583c9f9e478c16
MD5_TUT_NUT=12890bb5c94c52094b1681eee793c451
MD5_TUT_NUTILDA=63d469c0c0664758bb3305b42bfe3412
MD5_TUT_ALPHAT=8d593908bb79ff352b7775014e182b10
MD5_TUT_FREESTREAM=0241c0990332263be51366eb13990797
tut_md5_list() {
  # every tutorial input this item consumes, by md5; $1 = the directory holding them
  echo "$MD5_TUT_RUNSCRIPT  $1/runScript.py"; echo "$MD5_TUT_PREPROC  $1/preProcessing.sh"
  echo "$MD5_TUT_FFD  $1/FFD/FFD.xyz"; echo "$MD5_TUT_GENFFD  $1/FFD/genFFD.py"
  echo "$MD5_TUT_BLOCKMESH  $1/system/blockMeshDict"; echo "$MD5_TUT_MIRROR  $1/system/mirrorMeshDict"
  echo "$MD5_TUT_CONTROL  $1/system/controlDict"; echo "$MD5_TUT_FVSCHEMES  $1/system/fvSchemes"
  echo "$MD5_TUT_FVSOLUTION  $1/system/fvSolution"; echo "7840874dda64adbf21da62119ad0ee5d  $1/system/decomposeParDict"
  echo "$MD5_TUT_THERMO  $1/constant/thermophysicalProperties"; echo "$MD5_TUT_TURB  $1/constant/turbulenceProperties"
  echo "$MD5_TUT_T  $1/0.orig/T"; echo "$MD5_TUT_U  $1/0.orig/U"; echo "$MD5_TUT_P  $1/0.orig/p"
  echo "$MD5_TUT_NUT  $1/0.orig/nut"; echo "$MD5_TUT_NUTILDA  $1/0.orig/nuTilda"; echo "$MD5_TUT_ALPHAT  $1/0.orig/alphat"
  echo "$MD5_TUT_FREESTREAM  $1/0.orig/include/freestreamConditions"
}
test $# -ge 1 || { echo "ABORT usage: d18_chain_driver.sh <ARM...>"; exit 64; }
ARMS="$*"; STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/d18_driver.pid"
cd "$HERE" || exit 4
echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before staging"; exit 4; }
echo "$MD5_GRADER  $GRADER" | md5sum -c - || { echo "ABORT grader md5 drifted before staging"; exit 4; }
# ---- (4) ROOT STAGING on the first fire only ------------------------------
if [ ! -d "$BASE" ]; then
  test -d "$TUT_SRC" || { echo "ABORT tutorial source absent: $TUT_SRC"; exit 4; }
  tut_md5_list "$TUT_SRC" | md5sum -c - \
    || { echo "ABORT tutorial input md5 drifted (the checkout moved under this item; nothing staged)"; exit 4; }
  mkdir -p "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
  chmod 777 "$BASE" || { echo "ABORT chmod 777 $BASE (L-251)"; exit 4; }
  mkdir -p "$BASE/base" || exit 4
  cp -a "$TUT_SRC/0.orig" "$TUT_SRC/FFD" "$TUT_SRC/constant" "$TUT_SRC/system" "$TUT_SRC/preProcessing.sh" "$BASE/base/" || { echo "ABORT copy tutorial inputs"; exit 4; }
  rm -rf "$BASE/base/constant/polyMesh" 2>/dev/null
  cp -a "$HERE/d18_decomposeParDict" "$BASE/base/system/decomposeParDict" || { echo "ABORT overlay decomposeParDict"; exit 4; }
  # ---- D18's ONE REGISTERED DELTA, staged the same way the decomposeParDict overlay is:
  # ---- the tutorial's own file is md5-asserted by tut_md5_list ABOVE and then REPLACED.
  cp -a "$HERE/d18_freestreamConditions" "$BASE/base/0.orig/include/freestreamConditions" || { echo "ABORT overlay freestreamConditions"; exit 4; }
  cp -a "$HERE/d18_runScript.py" "$HERE/d18_xf.py" "$HERE/d18_mach_agreement.py" "$BASE/" || { echo "ABORT copy instruments"; exit 4; }
  # D5-DRIVER-DEF-1 corrected form, inherited: identity on its own line;
  # staging metadata on a line that does not start with ITEM=.
  echo "ITEM=D18" > "$BASE/ledger.txt"
  echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) tut_src=$TUT_SRC tut_commit=$(git -C "$TUT_SRC" rev-parse HEAD 2>/dev/null || echo NOT_MEASURED) permission=$PERMISSION" >> "$BASE/ledger.txt"
  echo "D18_ROOT_STAGED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ) mode=$(stat -c '%a' "$BASE") permission=$PERMISSION"
else
  echo "D18_ROOT_PRESENT base=$BASE (not re-staged)"
fi
{ echo "$MD5_RUNSCRIPT  $BASE/d18_runScript.py"; echo "$MD5_XF  $BASE/d18_xf.py"; echo "$MD5_DECOMP  $BASE/base/system/decomposeParDict";
  echo "2c18bb481b762706ab03bbbac3a91a4d  $BASE/base/0.orig/include/freestreamConditions";
  tut_md5_list "$BASE/base" | grep -v "/runScript.py$" | grep -v "/system/decomposeParDict$" \
                            | grep -v "/0.orig/include/freestreamConditions$"; } | md5sum -c - || { echo "ABORT staged instrument/input md5"; exit 4; }
echo "$MD5_MACH  $BASE/d18_mach_agreement.py" | md5sum -c - >/dev/null || { echo "ABORT G-MACH instrument md5 drifted"; exit 4; }
test -f "$BASE/base/0.orig/U" || { echo "ABORT staged base/ has no 0.orig/U"; exit 4; }
# ---- G-MACH (NEW in D18, PREREGISTRATION.md sec.3). D18's ONE REGISTERED DELTA is carried
# ---- INDEPENDENTLY by the BC file the solver reads and by the producer that normalises the
# ---- objective. Disagreement produces a plausible CD that is wrong by the square of a ratio
# ---- WITH EVERY OTHER CHECK IN THIS FAMILY PASSING. Asserted on the STAGED bytes, before any
# ---- arm container, on every driver invocation -- not only at first staging.
MACHOUT=$(python3 "$BASE/d18_mach_agreement.py" --bc "$BASE/base/0.orig/include/freestreamConditions" --producer "$BASE/d18_runScript.py"); MACHRC=$?
echo "$MACHOUT" | tee -a "$BASE/ledger.txt"
[ "$MACHRC" = "0" ] || { echo "ABORT G-MACH refused (rc=$MACHRC); NOTHING RUN"; exit 4; }
if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."; exit 3
  fi
fi
echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"; echo "chain_done stamp=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ arms=[$ARMS] last=[$(tail -n 1 "$STATUS" 2>/dev/null)] permission=$PERMISSION" >> "$BASE/CHAIN_DONE"' EXIT   # D5 Addendum 3 A3.5 form
echo "D18_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] permission=$PERMISSION"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) permission=$PERMISSION" >> "$STATUS"
mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
cap_mem_gib() { case "$1" in X-S|X-P) echo 8 ;; *) echo 4 ;; esac; }   # X arms 8g (adjoint), others 4g (PREREGISTRATION.md section 4)
h5_floor_gib() { case "$1" in X-S|X-P) echo 12.0 ;; *) echo 8.0 ;; esac; }   # cap + 4 GiB headroom, per arm
img_of() { case "$1" in MESH|*-S) echo "$IMG_SHIPPED" ;; *-P) echo "$IMG_PATCHED" ;; *) echo "" ;; esac; }
CHAIN_RC=0
for ARM in $ARMS; do
  IMG=$(img_of "$ARM"); test -n "$IMG" || { echo "ABORT arm $ARM names no registered row"; echo "chain=ABORT arm=$ARM reason=no_row stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=64; break; }
  echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before arm $ARM"; echo "chain=ABORT arm=$ARM reason=launcher_md5 stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=4; break; }
  # ---- (5) STATUS.<arm> is OPENED here (preflight line) and APPENDED from now
  # ---- on; the LAST line carries the rc.  Every AGGREGATE_WAIT is a line in it.
  echo "preflight arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ image=$IMG permission=$PERMISSION" > "$BASE/STATUS.$ARM"
  # ---- (3) ALREADY BOUGHT: a launcher-written rc=0 row for this arm means a
  # ---- re-fire would re-stage a graded arm.  REFUSED.
  if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT ALREADY_BOUGHT arm $ARM has an rc=0 ledger row; a second record for one run is the defect."
    echo "rc=3 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=ALREADY_BOUGHT permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=REFUSED_ALREADY_BOUGHT arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=3; break
  fi
  # ---- H5: a WINDOW of MemAvailable, every sample above the PER-ARM floor
  H5_FLOOR_GIB=$(h5_floor_gib "$ARM")
  H5_FILE="$BASE/${ARM}_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"; BELOW=0; N=0; MIN=999; MAX=0
  STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))")
  for _ in $(seq 1 $H5_SAMPLES); do
    s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"
    MIN=$(python3 -c "print(min($MIN,$s))"); MAX=$(python3 -c "print(max($MAX,$s))")
    [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1))
    sleep "$STEP"
  done
  echo "D18_H5_WINDOW arm=$ARM n=$N window_s=$H5_WINDOW_S floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAX samples_below_floor=$BELOW file=$(basename "$H5_FILE")"
  if [ "$BELOW" -gt 0 ] || [ "$N" -ne "$H5_SAMPLES" ]; then
    echo "ABORT H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB.  A batch that OOMs is worse than a batch that queues.  REFUSED."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=H5_REFUSED below=$BELOW min_GiB=$MIN permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
    echo "chain=STOPPED_H5 arm=$ARM stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=6; break
  fi
  # ---- (2) AGGREGATE: live container caps + this cap + host non-container RSS,
  # ---- WAIT-AND-RETRY (UPDATE F ruling): poll AGG_POLL_S, bounded AGG_BOUND_S;
  # ---- every wait written to STATUS.<arm>; refuse-and-BLOCK at the bound.
  WAITED=0; AGG_SERIES="$BASE/${ARM}_aggregate_series.txt"; AGG_BLOCKED=no
  while true; do
    AGG=$(python3 "$HERE/d18_aggregate_memory.py" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
    echo "$(date -u +%s) $AGG" >> "$AGG_SERIES"
    if [ "$(printf '%s' "$AGG" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ]; then break; fi
    if [ "$WAITED" -ge "$AGG_BOUND_S" ]; then
      echo "ABORT AGGREGATE still over $AGG_CEILING_GIB GiB after ${WAITED}s.  BLOCKED.  Series: $(basename "$AGG_SERIES")"
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=AGGREGATE_BLOCKED_AT_BOUND waited=$WAITED series=$(basename "$AGG_SERIES") permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_AGGREGATE arm=$ARM waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; AGG_BLOCKED=yes; break
    fi
    echo "AGGREGATE_WAIT waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM $AGG" >> "$BASE/STATUS.$ARM"
    sleep "$AGG_POLL_S"; WAITED=$((WAITED+AGG_POLL_S))
  done
  if [ "$AGG_BLOCKED" = "yes" ]; then CHAIN_RC=6; break; fi
  echo "D18_AGGREGATE arm=$ARM waited=$WAITED $AGG"
  # ---- (5b) G-CPUSET: no LIVE container may share a core with this item's cpuset;
  # ---- WAIT-AND-RETRY in the aggregate guard's form (poll AGG_POLL_S, bound AGG_BOUND_S).
  CWAITED=0; CPU_SERIES="$BASE/${ARM}_cpuset_series.txt"; CPU_BLOCKED=no
  while true; do
    CPU=$(python3 "$HERE/d18_cpuset_overlap.py" "$CPUSET_REGISTERED" "d18_")
    echo "$(date -u +%s) $CPU" >> "$CPU_SERIES"
    if [ "$(printf '%s' "$CPU" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ]; then break; fi
    if [ "$CWAITED" -ge "$AGG_BOUND_S" ]; then
      echo "ABORT G-CPUSET a live container still shares a core of $CPUSET_REGISTERED after ${CWAITED}s.  BLOCKED.  Series: $(basename "$CPU_SERIES")"
      echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=CPUSET_BLOCKED_AT_BOUND waited=$CWAITED series=$(basename "$CPU_SERIES") permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
      echo "chain=BLOCKED_CPUSET arm=$ARM waited=$CWAITED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CPU_BLOCKED=yes; break
    fi
    echo "CPUSET_WAIT waited=$CWAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM $CPU" >> "$BASE/STATUS.$ARM"
    sleep "$AGG_POLL_S"; CWAITED=$((CWAITED+AGG_POLL_S))
  done
  if [ "$CPU_BLOCKED" = "yes" ]; then CHAIN_RC=6; break; fi
  echo "D18_CPUSET arm=$ARM waited=$CWAITED $CPU"
  echo "D18_DRIVER arm=$ARM image=$IMG begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID permission=$PERMISSION"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "D18_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN aggregate_waited_s=$WAITED cpuset_waited_s=$CWAITED permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=$rc; break; fi
done
[ "$CHAIN_RC" -eq 0 ] && echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
# ---- (6) the FROZEN grader on the artefacts (zero compute); its rc is INFRASTRUCTURE (L-342)
GSTAMP=$(date -u +%Y%m%dT%H%M%SZ)
if echo "$MD5_GRADER  $GRADER" | md5sum -c - > /dev/null; then
  python3 "$GRADER" --root "$BASE" --out "$BASE/D18_grade_${GSTAMP}.json" > "$BASE/D18_grade_${GSTAMP}.out" 2>&1; GRC=$?
  echo "grader_rc=$GRC stamp=$GSTAMP out=D18_grade_${GSTAMP}.json note=comparator-exit-status-NOT-the-verdict" >> "$STATUS"
else
  echo "grader_rc=NOT_RUN stamp=$GSTAMP note=grader-md5-drifted-at-chain-end" >> "$STATUS"
fi
echo "D18_DRIVER end=$(date -u +%Y%m%dT%H%M%SZ) chain_rc=$CHAIN_RC"
exit "$CHAIN_RC"
