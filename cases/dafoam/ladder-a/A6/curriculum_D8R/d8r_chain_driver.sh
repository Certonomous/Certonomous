#!/usr/bin/env bash
# D8R chain driver -- DERIVED from curriculum_D16/d16_chain_driver.sh (itself from
# D15's and curriculum_D5/d5_chain_driver.sh, Addendum 2) with the REGISTERED DELTAS in
# PREREGISTRATION.md section 7 and d8r_chain_driver_DELTAS_from_d16.diff (item names;
# the SOURCE is D8's frozen base/ tree (23 input md5s), not a tutorial checkout; no
# MESH arm; per-arm memory caps and H5 floors -- O arms 14g / floor 18.0, F arms 6g /
# floor 10.0; the G-CPUSET overlap wait-and-retry and the CHAIN_DONE marker of D5
# Addendum 3, both as in D8R's driver); the D5 lineage:
#   (1) item names, run root, launcher, pidfile, MD5s; the IMAGE is chosen PER
#       ARM from the arm name (*-S on the SHIPPED image, *-P on the PATCHED
#       image) -- this item BUYS BOTH ROWS (the two-row rule), PATCHED FIRST;
#   (2) AGGREGATE in the WAIT-AND-RETRY form (UPDATE F), unchanged; the cap
#       used is the ARM's registered cap (O 14 GiB, F 6 GiB);
#   (3) ALREADY_BOUGHT: unchanged;
#   (4) ROOT STAGING: the run root does not exist at freeze (the freeze
#       condition); the FIRST fire creates it (mode 777, L-251), copies D8's
#       FROZEN INPUTS read-only from CURRICULUM-D8-a6-twist-opt/base (0, FFD,
#       constant incl. the N=16 polyMesh, system, runScript.py) into base/,
#       overlays the REGISTERED decomposeParDict (numberOfSubdomains 4, the
#       same bytes), copies the two instruments from this case directory, and
#       md5-asserts EVERY staged input (D8's run root is outside git, so its
#       bytes are frozen here); the ledger opens with an exact `ITEM=D8R` line and a STAGED line
#       (D5-DRIVER-DEF-1 corrected form, inherited);
#   (5) STATUS.<arm> opened at preflight and appended, unchanged; H5 floor PER
#       ARM = cap + 4 GiB headroom (the D4-SHIPPED 4.4 rule): O arms 18.0, F arms 10.0;
#   (5b) G-CPUSET: a LIVE container whose cpuset shares a core with this item's
#       registered cpuset -> WAIT-AND-RETRY (same form and bound as the aggregate
#       guard), so G12's delivered-cores floor is never failed by a disclosed
#       placement overlap (this item's 0,1,12,15 vs D17's 12,15);
#   (7) CHAIN_DONE (D5 Addendum 3 A3.5 form): one line appended on EVERY exit of a
#       started chain, so a later item can wait on it with no agent alive;
#   (6) the FROZEN GRADER runs on the artefacts at chain end (zero compute) so
#       the item closes with no agent alive (the D14-M form); its rc is
#       INFRASTRUCTURE (L-342), never the verdict.
# Runs the named arms IN ORDER through the frozen launcher and STOPS AT THE
# FIRST NON-ZERO rc.  Started ONLY detached (the queue runner's own form, or
#   setsid nohup bash d8r_chain_driver.sh O-P F-P O-S F-S > <root>/chain_launch.out 2>&1 &
# ) so it is its own session leader and outlives the agent that started it.
# Before each arm: launcher md5; the WINDOWED H5 gate (45 samples over 60 s,
# refuse on ANY sample below the floor); ALREADY_BOUGHT; AGGREGATE wait-and-retry.
# cwd is the CASE directory, never the run root (G-ROOT.5 b).
# Permission for detached launches: bc0e687e (Sanaa, boarded verbatim).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d8r_run_arm.sh"
GRADER="$HERE/d8r_grade.py"
IMG_SHIPPED=dafoam/opt-packages:latest
IMG_PATCHED=dafoam-idwarp-rot:v1
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv
D8_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt/base   # READ-ONLY source; D8's root is G-ROOT.2-forbidden for writing
CPUSET_REGISTERED=0,1,12,15
PERMISSION=bc0e687e
H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6
AGG_POLL_S=30; AGG_BOUND_S=14400
# The launcher and grader are FROZEN (PREREGISTRATION.md section 7/8);
# asserted before EVERY arm so a mid-chain edit cannot change what runs.
MD5_LAUNCHER=95beeed3a5dad0d715f3f1b2836ab973
MD5_GRADER=3f6eafac2ad4897417521d00c1cc5f3e
MD5_RUNSCRIPT=28c7819487a025a5f6554d38062a2b66
MD5_XF=5a399b427331ab8eab1fcdc1a243b3aa
MD5_DECOMP=1dbd9ead3f40a29f483444dc5fa1288b
# D8's frozen base/ INPUT bytes (23 files), frozen here because the run root is outside git
tut_md5_list() {
  # every D8 base input this item consumes, by md5; $1 = the directory holding them
  echo "0de915d21166a91a9a54b37ab11214cf  $1/runScript.py"
  echo "8f10013191a33d5dd757affb8caa3cb8  $1/0/T"; echo "d298286a05f0b031f2a571211a79ef83  $1/0/U"; echo "d381ad50711abb780643b5544cc1ef0c  $1/0/alphat"
  echo "55ef53cbfe7ee5cec731e4d090a74292  $1/0/nuTilda"; echo "16be134ba7458c5e43a1fd9207856fa0  $1/0/nut"; echo "96fabd08064482aa037599de4cfd8b64  $1/0/p"
  echo "527a589ea4e074a711316d6e1ef2239a  $1/system/controlDict"; echo "5ef8b5ece78a1305cc9c5e2f85288924  $1/system/createPatchDict"
  echo "1dbd9ead3f40a29f483444dc5fa1288b  $1/system/decomposeParDict"; echo "bfe390aeb22f4e9d48eb23e2827ab3ab  $1/system/fvSchemes"; echo "36a8ad5cf2edd672b8aa752829647dfd  $1/system/fvSolution"
  echo "7d5ff100cd6fdf74249f788b4e783263  $1/constant/polyMesh/boundary"; echo "01003fa50e99eacae9e4078b1583b8aa  $1/constant/polyMesh/cellZones.gz"
  echo "c9c0f2a9389cdf8935e03c9f4597f39a  $1/constant/polyMesh/faceZones.gz"; echo "67dfa0dad772a8401dae83c1dc1a4bf2  $1/constant/polyMesh/faces.gz"
  echo "a52672f6e1fa4a2bc375178825eace87  $1/constant/polyMesh/neighbour.gz"; echo "ba0ca1bc910bad597225715f15ed5fb4  $1/constant/polyMesh/owner.gz"
  echo "dedc6402d08ae5fd038b0cff708fdd97  $1/constant/polyMesh/pointZones.gz"; echo "11b84f0de5fdf2d3e947fee8cea412a9  $1/constant/polyMesh/points.gz"
  echo "2f5e9885074efaa1988a6bdba5f6595f  $1/constant/thermophysicalProperties"; echo "03f244f2d9c2770c459f881404a904d4  $1/constant/turbulenceProperties"
  echo "905ade2c1120aee7e6517432cd8abbaf  $1/FFD/wingFFD.xyz"
}
test $# -ge 1 || { echo "ABORT usage: d8r_chain_driver.sh <ARM...>"; exit 64; }
ARMS="$*"; STATUS="$BASE/STATUS.chain"; PIDFILE="$BASE/d8r_driver.pid"
cd "$HERE" || exit 4
echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - || { echo "ABORT launcher md5 drifted before staging"; exit 4; }
echo "$MD5_GRADER  $GRADER" | md5sum -c - || { echo "ABORT grader md5 drifted before staging"; exit 4; }
# ---- (4) ROOT STAGING on the first fire only ------------------------------
if [ ! -d "$BASE" ]; then
  test -d "$D8_BASE" || { echo "ABORT D8 base absent: $D8_BASE"; exit 4; }
  tut_md5_list "$D8_BASE" | md5sum -c - \
    || { echo "ABORT D8 base input md5 drifted (the source moved under this item; nothing staged)"; exit 4; }
  mkdir -p "$BASE" || { echo "ABORT cannot create run root $BASE"; exit 4; }
  chmod 777 "$BASE" || { echo "ABORT chmod 777 $BASE (L-251)"; exit 4; }
  mkdir -p "$BASE/base" || exit 4
  cp -a "$D8_BASE/0" "$D8_BASE/FFD" "$D8_BASE/constant" "$D8_BASE/system" "$D8_BASE/runScript.py" "$BASE/base/" || { echo "ABORT copy D8 base inputs"; exit 4; }
  cp -a "$HERE/d8r_decomposeParDict" "$BASE/base/system/decomposeParDict" || { echo "ABORT overlay decomposeParDict"; exit 4; }
  cp -a "$HERE/d8r_runScript.py" "$HERE/d8r_of.py" "$BASE/" || { echo "ABORT copy instruments"; exit 4; }
  # D5-DRIVER-DEF-1 corrected form, inherited: identity on its own line;
  # staging metadata on a line that does not start with ITEM=.
  echo "ITEM=D8R" > "$BASE/ledger.txt"
  echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) d8_base=$D8_BASE points_md5=$(md5sum "$D8_BASE/constant/polyMesh/points.gz" | cut -d' ' -f1) permission=$PERMISSION" >> "$BASE/ledger.txt"
  echo "D8R_ROOT_STAGED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ) mode=$(stat -c '%a' "$BASE") permission=$PERMISSION"
else
  echo "D8R_ROOT_PRESENT base=$BASE (not re-staged)"
fi
{ echo "$MD5_RUNSCRIPT  $BASE/d8r_runScript.py"; echo "$MD5_XF  $BASE/d8r_of.py"; echo "$MD5_DECOMP  $BASE/base/system/decomposeParDict";
  tut_md5_list "$BASE/base"; } | md5sum -c - || { echo "ABORT staged instrument/input md5"; exit 4; }
test -f "$BASE/base/0/U" || { echo "ABORT staged base/ has no 0/U"; exit 4; }
if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    echo "ABORT another driver is live (pid $OLD, $PIDFILE).  Two records for one run is the defect."; exit 3
  fi
fi
echo "$$" > "$PIDFILE"
trap 'rm -f "$PIDFILE"; echo "chain_done stamp=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ arms=[$ARMS] last=[$(tail -n 1 "$STATUS" 2>/dev/null)] permission=$PERMISSION" >> "$BASE/CHAIN_DONE"' EXIT   # D5 Addendum 3 A3.5 form
echo "D8R_DRIVER start=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arms=[$ARMS] permission=$PERMISSION"
echo "chain=started arms=[$ARMS] pid=$$ stamp=$(date -u +%Y%m%dT%H%M%SZ) permission=$PERMISSION" >> "$STATUS"
mem_gib() { python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))"; }
cap_mem_gib() { case "$1" in O-S|O-P) echo 14 ;; *) echo 6 ;; esac; }   # O arms 14g (adjoint), F arms 6g (PREREGISTRATION.md section 4)
h5_floor_gib() { case "$1" in O-S|O-P) echo 18.0 ;; *) echo 10.0 ;; esac; }   # cap + 4 GiB headroom, per arm
img_of() { case "$1" in *-S) echo "$IMG_SHIPPED" ;; *-P) echo "$IMG_PATCHED" ;; *) echo "" ;; esac; }
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
  echo "D8R_H5_WINDOW arm=$ARM n=$N window_s=$H5_WINDOW_S floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAX samples_below_floor=$BELOW file=$(basename "$H5_FILE")"
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
    AGG=$(python3 "$HERE/d8r_aggregate_memory.py" "$(cap_mem_gib "$ARM")" "$AGG_CEILING_GIB")
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
  echo "D8R_AGGREGATE arm=$ARM waited=$WAITED $AGG"
  # ---- (5b) G-CPUSET: no LIVE container may share a core with this item's cpuset;
  # ---- WAIT-AND-RETRY in the aggregate guard's form (poll AGG_POLL_S, bound AGG_BOUND_S).
  CWAITED=0; CPU_SERIES="$BASE/${ARM}_cpuset_series.txt"; CPU_BLOCKED=no
  while true; do
    CPU=$(python3 "$HERE/d8r_cpuset_overlap.py" "$CPUSET_REGISTERED" "d8r_")
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
  echo "D8R_CPUSET arm=$ARM waited=$CWAITED $CPU"
  echo "D8R_DRIVER arm=$ARM image=$IMG begin=$(date -u +%Y%m%dT%H%M%SZ) ppid_now=$PPID permission=$PERMISSION"
  bash "$LAUNCHER" "$ARM" "$IMG" > "$BASE/${ARM}_launch.out" 2>&1
  rc=$?
  echo "D8R_DRIVER arm=$ARM end=$(date -u +%Y%m%dT%H%M%SZ) rc=$rc"
  echo "rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM source=launcher_exit=docker_inspect_ExitCode launch_out=${ARM}_launch.out h5_min_GiB=$MIN aggregate_waited_s=$WAITED cpuset_waited_s=$CWAITED permission=$PERMISSION" >> "$BASE/STATUS.$ARM"
  echo "arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
  if [ "$rc" -ne 0 ]; then echo "chain=STOPPED_AT_FIRST_NONZERO arm=$ARM rc=$rc stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"; CHAIN_RC=$rc; break; fi
done
[ "$CHAIN_RC" -eq 0 ] && echo "chain=COMPLETE stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
# ---- (6) the FROZEN grader on the artefacts (zero compute); its rc is INFRASTRUCTURE (L-342)
GSTAMP=$(date -u +%Y%m%dT%H%M%SZ)
if echo "$MD5_GRADER  $GRADER" | md5sum -c - > /dev/null; then
  python3 "$GRADER" --root "$BASE" --out "$BASE/D8R_grade_${GSTAMP}.json" > "$BASE/D8R_grade_${GSTAMP}.out" 2>&1; GRC=$?
  echo "grader_rc=$GRC stamp=$GSTAMP out=D8R_grade_${GSTAMP}.json note=comparator-exit-status-NOT-the-verdict" >> "$STATUS"
else
  echo "grader_rc=NOT_RUN stamp=$GSTAMP note=grader-md5-drifted-at-chain-end" >> "$STATUS"
fi
echo "D8R_DRIVER end=$(date -u +%Y%m%dT%H%M%SZ) chain_rc=$CHAIN_RC"
exit "$CHAIN_RC"
