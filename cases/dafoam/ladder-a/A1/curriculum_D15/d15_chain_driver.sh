#!/usr/bin/env bash
# D15 chain driver -- DERIVED from curriculum_D5/d5_chain_driver.sh (Addendum 2,
# md5 89c9b7e7e43e7dd12d1c551dadfa80c8) with the REGISTERED DELTAS listed in
# PREREGISTRATION.md section 7 and recorded in d15_chain_driver_DELTAS_from_d5.diff:
#   (1) item names, run root, launcher, pidfile, MD5s; the IMAGE is chosen PER
#       ARM from the arm name (MESH and *-S on the SHIPPED image, *-P on the
#       PATCHED image) -- this item BUYS BOTH ROWS (the two-row rule);
#   (2) AGGREGATE in the WAIT-AND-RETRY form (UPDATE F), unchanged; the cap
#       used is this item's 4 GiB per arm;
#   (3) ALREADY_BOUGHT: unchanged;
#   (4) ROOT STAGING: the run root does not exist at freeze (the freeze
#       condition); the FIRST fire creates it (mode 777, L-251), copies the
#       SHIPPED TUTORIAL INPUTS read-only from /home/ubuntu/dafoam-tutorials
#       (0.orig, FFD, constant, system, profiles, genAirFoilMesh.py,
#       preProcessing.sh) into base/, overlays the REGISTERED decomposeParDict
#       (numberOfSubdomains 2), copies the two instruments from this case
#       directory, and md5-asserts EVERY staged input (tutorial files included:
#       the tutorial checkout is not frozen by this repo, so its bytes are);
#       the ledger opens with an exact `ITEM=D15` line and a STAGED line
#       (D5-DRIVER-DEF-1 corrected form, inherited);
#   (5) STATUS.<arm> opened at preflight and appended, unchanged; H5 floor 8.0
#       GiB (4g + 4 GiB headroom, the D4-SHIPPED 4.4 rule at this cap);
#   (6) the FROZEN GRADER runs on the artefacts at chain end (zero compute) so
#       the item closes with no agent alive (the D14-M form); its rc is
#       INFRASTRUCTURE (L-342), never the verdict.
# Runs the named arms IN ORDER through the frozen launcher and STOPS AT THE
# FIRST NON-ZERO rc.  Started ONLY detached (the queue runner's own form, or
#   setsid nohup bash d15_chain_driver.sh MESH X-S F-S X-P F-P > <root>/chain_launch.out 2>&1 &
# ) so it is its own session leader and outlives the agent that started it.
# Before each arm: launcher md5; the WINDOWED H5 gate (45 samples over 60 s,
# refuse on ANY sample below the floor); ALREADY_BOUGHT; AGGREGATE wait-and-retry.
# cwd is the CASE directory, never the run root (G-ROOT.5 b).
# Permission for detached launches: bc0e687e (Sanaa, boarded verbatim).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d15_run_arm.sh"
GRADER="$HERE/d15_grade.py"
IMG_SHIPPED=dafoam/opt-packages:latest
IMG_PATCHED=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic
TUT_SRC=/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/subsonic
PERMISSION=bc0e687e
H5_FLOOR_GIB=8.0; H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6
AGG_POLL_S=30; AGG_BOUND_S=14400
# The launcher and grader are FROZEN (PREREGISTRATION.md section 7/8);
# asserted before EVERY arm so a mid-chain edit cannot change what runs.
MD5_LAUNCHER=796a2de5b894e8fcdbfab99af6fbf09d
MD5_GRADER=b429ec89e7a738647081783b8b755711
MD5_RUNSCRIPT=6537fa7641c4ccb20056f60f96f63b11
MD5_XF=8a664a976de77c5fe7c3fed5746be4de
MD5_DECOMP=68ecc827562886fb43c3aedb0627b344
# the shipped tutorial's INPUT bytes, frozen here because the checkout is not
MD5_TUT_RUNSCRIPT=6537fa7641c4ccb20056f60f96f63b11
MD5_TUT_GEN=681f10659eb90457fca13fc933008b93
MD5_TUT_PREPROC=e25c8f8c32886112e3f9591196c695ad
MD5_TUT_PS=51dfed28e1bdb4cd33e0d8d7dabd586a
MD5_TUT_SS=4a6b8ef4501494c7693b71e88a2eabbf
MD5_TUT_FFD=6ddf378b028d03d8a18270488bee1759
test $# -ge 1 || { echo "ABORT usage: d15_chain_driver.sh <ARM...>"; exit 64; }
ARMS="$*"; STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/d15_driver.pid"
cd "$HERE" || exit 4
echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before staging"; exit 4; }
echo "$MD5_GRADER  $GRADER" | md5sum -c - || { echo "ABORT grader md5 drifted before staging"; exit 4; }
# ---- (4) ROOT STAGING on the first fire only ------------------------------
if [ ! -d "$BASE" ]; then
  test -d "$TUT_SRC" || { echo "ABORT tutorial source absent: $TUT_SRC"; exit 4; }
  { echo "$MD5_TUT_RUNSCRIPT  $TUT_SRC/runScript.py"; echo "$MD5_TUT_GEN  $TUT_SRC/genAirFoilMesh.py"; echo "$MD5_TUT_PREPROC  $TUT_SRC/preProcessing.sh";
    echo "$MD5_TUT_PS  $TUT_SRC/profiles/NACA0012PS.profile"; echo "$MD5_TUT_SS  $TUT_SRC/profiles/NACA0012SS.profile"; echo "$MD5_TUT_FFD  $TUT_SRC/FFD/wingFFD.xyz"; } | md5sum -c - \
    || { echo "ABORT tutorial input md5 drifted (the checkout moved under this item; nothing staged)"; exit 4; }
  mkdir -p "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
  chmod 777 "$BASE" || { echo "ABORT chmod 777 $BASE (L-251)"; exit 4; }
  mkdir -p "$BASE/base" || exit 4
  cp -a "$TUT_SRC/0.orig" "$TUT_SRC/FFD" "$TUT_SRC/constant" "$TUT_SRC/system" "$TUT_SRC/profiles" "$TUT_SRC/genAirFoilMesh.py" "$TUT_SRC/preProcessing.sh" "$BASE/base/" || { echo "ABORT copy tutorial inputs"; exit 4; }
  rm -rf "$BASE/base/constant/polyMesh" 2>/dev/null
  cp -a "$HERE/d15_decomposeParDict" "$BASE/base/system/decomposeParDict" || { echo "ABORT overlay decomposeParDict"; exit 4; }
  cp -a "$HERE/d15_runScript.py" "$HERE/d15_xf.py" "$BASE/" || { echo "ABORT copy instruments"; exit 4; }
  # D5-DRIVER-DEF-1 corrected form, inherited: identity on its own line;
  # staging metadata on a line that does not start with ITEM=.
  echo "ITEM=D15" > "$BASE/ledger.txt"
  echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) tut_src=$TUT_SRC tut_commit=$(git -C "$TUT_SRC" rev-parse HEAD 2>/dev/null || echo NOT_MEASURED) permission=$PERMISSION" >> "$BASE/ledger.txt"
  echo "D15_ROOT_STAGED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ) mode=$(stat -c '%a' "$BASE") permission=$PERMISSION"
else
  echo "D15_ROOT_PRESENT base=$BASE (not re-staged)"
fi
{ echo "$MD5_RUNSCRIPT  $BASE/d15_runScript.py"; echo "$MD5_XF  $BASE/d15_xf.py"; echo "$MD5_DECOMP  $BASE/base/system/decomposeParDict";
  echo "$MD5_TUT_GEN  $BASE/base/genAirFoilMesh.py"; echo "$MD5_TUT_PREPROC  $BASE/base/preProcessing.sh";
  echo "$MD5_TUT_PS  $BASE/base/profiles/NACA0012PS.profile"; echo "$MD5_TUT_SS  $BASE/base/profiles/NACA0012SS.profile"; echo "$MD5_TUT_FFD  $BASE/base/FFD/wingFFD.xyz"; } | md5sum -c - || { echo "ABORT staged instrument/input md5"; exit 4; }
test -f "$BASE/base/0.orig/U" || { echo "ABORT staged base/ has no 0.orig/U"; exit 4; }
if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."; exit 3
  fi
fi
echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"' EXIT
echo "D15_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] permission=$PERMISSION"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) permission=$PERMISSION" >> "$STATUS"
mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
cap_mem_gib() { echo 4; }   # every arm 4g (PREREGISTRATION.md section 4)
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
  # ---- H5: a WINDOW of MemAvailable, every sample above the floor
  H5_FILE="$BASE/${ARM}_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"; BELOW=0; N=0; MIN=999; MAX=0
  STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))")
  for _ in $(seq 1 $H5_SAMPLES); do
    s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"
    MIN=$(python3 -c "print(min($MIN,$s))"); MAX=$(python3 -c "print(max($MAX,$s))")
    [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1))
    sleep "$STEP"
  done
  echo "D15_H5_WINDOW arm=$ARM n=$N window_s=$H5_WINDOW_S floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAX samples_below_floor=$BELOW file=$(basename "$H5_FILE")"
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
    AGG=$(python3 "$HERE/d15_aggregate_memory.py" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
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
  echo "D15_AGGREGATE arm=$ARM waited=$WAITED $AGG"
  echo "D15_DRIVER arm=$ARM image=$IMG begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID permission=$PERMISSION"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "D15_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN aggregate_waited_s=$WAITED permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=$rc; break; fi
done
[ "$CHAIN_RC" -eq 0 ] && echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
# ---- (6) the FROZEN grader on the artefacts (zero compute); its rc is INFRASTRUCTURE (L-342)
GSTAMP=$(date -u +%Y%m%dT%H%M%SZ)
if echo "$MD5_GRADER  $GRADER" | md5sum -c - > /dev/null; then
  python3 "$GRADER" --root "$BASE" --out "$BASE/D15_grade_${GSTAMP}.json" > "$BASE/D15_grade_${GSTAMP}.out" 2>&1; GRC=$?
  echo "grader_rc=$GRC stamp=$GSTAMP out=D15_grade_${GSTAMP}.json note=comparator-exit-status-NOT-the-verdict" >> "$STATUS"
else
  echo "grader_rc=NOT_RUN stamp=$GSTAMP note=grader-md5-drifted-at-chain-end" >> "$STATUS"
fi
echo "D15_DRIVER end=$(date -u +%Y%m%dT%H%M%SZ) chain_rc=$CHAIN_RC"
exit "$CHAIN_RC"
