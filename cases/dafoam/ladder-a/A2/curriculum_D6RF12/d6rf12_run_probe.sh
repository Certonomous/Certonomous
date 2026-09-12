#!/usr/bin/env bash
# D6RF12 probe launcher.  D6RF11's launcher, carried, with EXACTLY ONE addition:
# the knobs 7-8 installer after install_config.  No frozen file is edited.
#
# NO CAP OF ANY KIND: no `timeout`, no `docker stop`, no ceiling that stops
# (Sanaa's NO-CAP ruling).  MEMORY CONTAINMENT KEPT.  rc is captured from the
# KERNEL via `docker inspect`, INSIDE the detached wrapper -- never from the
# status of the setsid line, which returns 0 for every outcome.
set -uo pipefail

ITEM=D6RF12
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF12-a2-wing-fd-nutilda-repair
SRC=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd/F_mp
SCHEMES=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF10-a2-wing-convergence-probe/P_conv/d6rf7_fvSchemes_LIMITED
SCHEMES_MD5=fbca617a0808c56113a34d156c5890b9
KNOBS=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6RF12/d6rf12_install_knobs78.py
IMG=dafoam-idwarp-rot:v1
WANT=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
RANKS=4                 # UNCHANGED from D6RF11 -- changing ranks would confound the comparison
CPUSET=5,6,7,8          # free of every live pin at launch (2,3,4,14 and 9 are taken)
MEM=20g
ARM=F_probe
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d6rf12_${ARM}_${STAMP}"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- G-ROOT: never stage over another item's graded row -------------------
for forb in /home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd \
            /home/ubuntu/certonomous-runs/CURRICULUM-D6RF10-a2-wing-convergence-probe \
            /home/ubuntu/certonomous-runs/CURRICULUM-D6RF11-a2-wing-fd-simplec-probe \
            /home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint \
            /home/ubuntu/certonomous-runs/CURRICULUM-D6R2-a2-wing-multipoint-transonic; do
  [ "$(realpath -m "$BASE")" = "$(realpath -m "$forb")" ] && { echo "ABORT G-ROOT BASE is $forb"; exit 3; }
done
LIVE=$(docker ps --format '{{.Names}}' 2>/dev/null | grep "^d6rf12_${ARM}_" | head -1)
[ -n "$LIVE" ] && { echo "ABORT G-ROOT.5 a live container already carries this arm: $LIVE"; exit 3; }

mkdir -p "$BASE" || { echo "ABORT mkdir BASE"; exit 4; }
chmod 777 "$BASE"
W="$BASE/$ARM"
[ -e "$W" ] && { echo "ABORT G-COLD $W already exists -- refusing to re-stage"; exit 5; }

GOT=$(docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
[ "$GOT" = "$WANT" ] || { echo "ABORT digest mismatch got=$GOT want=$WANT"; exit 4; }
echo "D6RF12_IMAGE_OK row=PATCHED image=$IMG digest=$GOT"

# ---- stage from D6RF3's pristine arm, EXACTLY as D6RF11 did ---------------
[ -d "$SRC" ] || { echo "ABORT source stage $SRC absent"; exit 4; }
cp -a "$SRC" "$W" || { echo "ABORT stage copy"; exit 4; }
rm -f "$W/d6rf3_fd_endpoint.jsonl" "$W/d6rf3_fd_endpoint.json" 2>/dev/null
rm -rf "$W/__pycache__" 2>/dev/null
rm -rf "$W"/processor* "$W"/mp04/processor* "$W"/mp05/processor* "$W"/mp06/processor* 2>/dev/null
for f in d6rf3_extract_endpoint.py d6rf3_endpoint_physical.py d6rf3_units_assert.py \
         d6rf3_fd_endpoint.py d6rf3_opt_runScript.py d6rf3_endpoint_dvs_PHYSICAL.json; do
  a=$(md5sum "$SRC/$f" | cut -d' ' -f1); b=$(md5sum "$W/$f" | cut -d' ' -f1)
  [ "$a" = "$b" ] || { echo "ABORT instrument $f md5 $a != $b across the copy"; exit 4; }
  echo "D6RF12_INSTRUMENT_OK $f md5=$a"
done
cp -a "$SCHEMES" "$W/d6rf7_fvSchemes_LIMITED" || { echo "ABORT fvSchemes stage"; exit 4; }
echo "$SCHEMES_MD5  $W/d6rf7_fvSchemes_LIMITED" | md5sum -c - || { echo "ABORT fvSchemes md5"; exit 4; }
cp -a "$KNOBS" "$W/d6rf12_install_knobs78.py" || { echo "ABORT knobs installer stage"; exit 4; }
echo "D6RF12_KNOBS_STAGED md5=$(md5sum "$W/d6rf12_install_knobs78.py" | cut -d' ' -f1)"

touch "$W/0"/* || { echo "ABORT age datum"; exit 5; }
AGE=$(stat -c '%Y' "$W/0/U"); echo "$AGE" > "$W/.d6rf12_age_datum"
echo "D6RF12_G_COLD OK age_datum_epoch=$AGE"

# ---- container command: D6RF11's, plus the knobs 7-8 install on all 4 sites
CMDFILE="$W/d6rf12_cmd.sh"
sed -n '/^install_config() {/,/^}$/p' \
  /home/ubuntu/certonomous-runs/CURRICULUM-D6RF10-a2-wing-convergence-probe/P_conv/d6rf10_cmd_R3.sh \
  > "$CMDFILE" || { echo "ABORT could not carry install_config"; exit 4; }
grep -q 'a swap that swapped nothing' "$CMDFILE" || { echo "ABORT install_config carried WITHOUT its zero-site refusal"; exit 4; }
{
  echo 'set -o pipefail'
  echo "install_config R3 DARhoSimpleCFoam 12 0.70 0.70 2000 $SCHEMES_MD5 || exit 5"
  echo '# --- KNOBS 7-8, THE nuTilda REPAIR.  Six values, two blocks, all four sites,'
  echo '# --- each read BACK FROM DISK by the installer.  A swap that swapped nothing exits 5.'
  echo 'for sd in system mp04/system mp05/system mp06/system; do'
  echo '  python d6rf12_install_knobs78.py "$sd/fvSolution" || exit 5'
  echo 'done'
  echo "python d6rf3_endpoint_physical.py --age-datum $AGE && \\"
  echo 'python d6rf3_units_assert.py d6rf3_endpoint_dvs.json --runscript d6rf3_opt_runScript.py && \\'
  echo "mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python d6rf3_fd_endpoint.py"
} >> "$CMDFILE"
grep -q timeout "$CMDFILE" && { echo "ABORT a timeout survived into the cmdfile"; exit 9; }
echo "D6RF12_CMDFILE md5=$(md5sum "$CMDFILE" | cut -d' ' -f1)"

MEMAVAIL=$(awk '/MemAvailable/{printf "%.2f", $2/1048576}' /proc/meminfo)
LOAD1=$(awk '{print $1}' /proc/loadavg)
echo "D6RF12_HOST_PRE MemAvailable_GiB=$MEMAVAIL load1=$LOAD1 cpuset=$CPUSET ranks=$RANKS"

CID=$(docker run -d --name "$NAME" \
    --user 0:0 --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D6RF12_CONTAINER_UID: \$(id -u) && \
     echo D6RF12_DEADLINE_IN_CONTAINER_S: NONE_NO_CAP && \
     bash /mnt/$ARM/d6rf12_cmd.sh" 2>"$BASE/${ARM}_${STAMP}.runerr") \
  || { echo "ABORT could not start container: $(head -c 300 "$BASE/${ARM}_${STAMP}.runerr")"; exit 4; }
echo "$CID" | grep -qE '^[0-9a-f]{12,64}$' || { echo "ABORT docker run returned no cid: $CID"; exit 4; }
echo "$CID" > "$BASE/${ARM}_${STAMP}.cid"
echo "D6RF12_LAUNCHED cid=$CID name=$NAME stamp=$STAMP ranks=$RANKS cpuset=$CPUSET cwd=$W mem=$MEM"

# ---- RECORDER, detached.  rc captured INSIDE the wrapper.  Records only. ----
setsid bash -c '
  BASE="'"$BASE"'"; ARM="'"$ARM"'"; STAMP="'"$STAMP"'"; NAME="'"$NAME"'"; LOG="'"$LOG"'"
  ITEM="'"$ITEM"'"; IMG="'"$IMG"'"; DIG="'"$GOT"'"; MEM="'"$MEM"'"; CPUSET="'"$CPUSET"'"
  RANKS='"$RANKS"'; MEMPRE="'"$MEMAVAIL"'"
  T0=$(date -u +%s)
  docker logs -f "$NAME" >> "$LOG" 2>&1 &
  rc=$(docker wait "$NAME" 2>/dev/null)
  INSPECT=$(docker inspect --format "{{.State.ExitCode}} {{.State.OOMKilled}}" "$NAME" 2>/dev/null)
  T1=$(date -u +%s); WALL=$((T1-T0))
  CM=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
  MEMPOST=$(awk "/MemAvailable/{printf \"%.2f\", \$2/1048576}" /proc/meminfo)
  echo "$rc" > "$BASE/D6RF12_ARM_RC.txt"
  {
   echo "ITEM=$ITEM"
   echo "ARM=$ARM ROW=PATCHED IMG=$IMG DIGEST=$DIG rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CM registered_prediction_core_min=95.0 cap=NONE_NO_CAP memory=$MEM inspect(exit,oomkilled)=[$INSPECT] memavail_pre_GiB=$MEMPRE memavail_post_GiB=$MEMPOST cpuset=$CPUSET log=$(basename "$LOG") stamp=$STAMP"
  } >> "$BASE/ledger.txt"
  echo "rc=$rc wall_s=$WALL core_min=$CM inspect(exit,oomkilled)=[$INSPECT]" > "$BASE/STATUS.$ARM"
' < /dev/null > "$BASE/${ARM}_${STAMP}.watcher.out" 2>&1 &
echo "D6RF12_WATCHER_DETACHED (records only; cannot signal, kill or renice)"
