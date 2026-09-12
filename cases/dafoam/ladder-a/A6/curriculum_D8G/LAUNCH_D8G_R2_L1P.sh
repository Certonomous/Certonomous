#!/bin/bash
# =============================================================================
# D8G L1-P (R2) -- THE R3 REPAIR PACKAGE, RE-RUN UNDER ITS REGISTERED ARM ID.
# Frozen registration: PREREGISTRATION.md ADDENDUM 7 + 8 + **ADDENDUM 9**.
#
# WHY THIS FILE EXISTS.  LAUNCH_D8G_R1.sh produced a completed rc=0 arm that
# d8g_grade.py REFUSED.  ADDENDUM 9 records FOUR defects between that launcher
# and a graded row; the arm id was only the first and NOT the binding one.
# This file fixes all four and changes NOTHING ELSE.
#
#   1. ARM=L1-P            -- the id fixed at d8g_grade.py:212.  Was L1-P-R1.
#   2. THE CANONICAL ROW   -- d8g_run_arm.sh:1010, field for field, so LEDGER_RE
#                             (d8g_grade.py:367) can parse it.  R1 wrote a
#                             seven-field stub with `inspect(exit,oom)` for
#                             `inspect(exit,oomkilled)` and no IMG/DIGEST/
#                             cap_core_min/enforced_*/memory/cpuset.  THIS, NOT
#                             THE ARM ID, IS WHAT REFUSED R1.
#   3. --cpuset-cpus=0,1,12,15 -- the set G12 gates on (d8g_grade.py:333).
#                             R1's --cpus=4 is a share limit that writes no
#                             cpuset and matches no registered set.
#   4. DIGEST CAPTURED AT LAUNCH from the image itself -- G9 gates the toolchain
#                             on it (d8g_grade.py:1369).  R1 recorded none.
#
# ADDENDUM 9 sec 9.6, AND READ IT BEFORE SPENDING: g_completion() walks ALL TEN
# ARMS_REQUIRED.  A single-arm run CANNOT produce an item verdict -- grade() will
# refuse at G1 on the nine absent arms.  What this run banks is ONE OF THE TEN,
# CORRECTLY RECORDED.  That is the only claim made for it.
#
# --- NO CAP OF ANY KIND (Sanaa 2026-09-12: "NO RUN GETS STOPPED BC OF A TIME OR
#     BUDGET CAP", fourth ruling).  Absent by construction: `timeout -k`,
#     cap_core_min->TMO, the rc=124/137 path, LAUNCH_BUDGET_S, la_kill(), exit 88.
# --- MEMORY CONTAINMENT KEPT (ADDENDUM 8): --memory/--memory-swap/--oom-score-adj.
#     A ceiling that cannot bind a healthy run is a seatbelt, not a cap.  L1 is
#     5,568 cells at a predicted ~0.09 GiB RSS against 6 GiB -- ~67x the need.
# =============================================================================
set -e
BASE=${1:?usage: LAUNCH_D8G_R2_L1P.sh <FRESH_RUN_ROOT>}
ARM=L1-P
ROW=D8G-R2
WORK=$BASE/$ARM
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
IMG=dafoam-idwarp-rot:v1
MEM=6g
CPUSET=0,1,12,15                       # d8g_grade.py:333 CPUSET_REGISTERED -- G12 reads this
CAP=46.977                             # CAPS["L1-P"]; RECORDED AS A NUMBER, NOT A STOP

# ---- G-ROOT: a FRESH root.  Neither existing root may be reused: both hold graded
# ---- evidence and rule 4's age guard dates a run by its own 0/.
case "$BASE" in
  */CURRICULUM-D8G-a6-grid-triple|*/CURRICULUM-D8G-R1-a6-grid-triple)
    echo "ABORT G-ROOT refusing to write into a root that holds graded evidence: $BASE"; exit 6;;
esac
test -e "$BASE/ledger.txt" && { echo "ABORT G-ROOT ledger already present in $BASE"; exit 6; }

# ---- STAGING IS A PRECONDITION AND IS NOT GUESSED AT.  This launcher REFUSES an
# ---- unstaged arm rather than inventing one.
for need in "$WORK/0/U" "$WORK/system/controlDict" "$WORK/constant/polyMesh/points.gz" \
            "$WORK/d8g_of.py" "$WORK/d8g_runScript.py"; do
  test -e "$need" || { echo "ABORT STAGING missing $need -- stage $ARM from base_L1 first (ADDENDUM 7)"; exit 7; }
done

# ---- G-COLD: refuse a case that could silently warm-start ---------------------
for bad in "$WORK/reports" "$WORK/d8g_P.json" "$WORK/d8g_P.jsonl" "$WORK/OptView.hst"; do
  test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }; done
test -n "$(ls -d $WORK/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
for d in $WORK/*/; do n=$(basename "$d"); case "$n" in
  0|0.orig|FFD|system|constant) ;; [0-9]*) echo "ABORT G-COLD time dir $n"; exit 5;; esac; done

# ---- RULE 4 AGE GUARD: 0/ is touched LAST, so it dates the run allowed to answer
touch "$WORK/0"/*
AGE=$(stat -c '%Y' "$WORK/0/U"); echo "$AGE" > "$WORK/.d8g_age_datum"
echo "D8G_R2_G_COLD OK arm=$ARM age_datum_epoch=$AGE"

# ---- DEFECT 4 FIX: the image DIGEST, read from the image, never hardcoded -----
GOT_DIGEST=$(docker image inspect "$IMG" -f '{{.Id}}' 2>/dev/null)
echo "$GOT_DIGEST" | grep -qE '^sha256:[0-9a-f]{64}$' || { echo "ABORT could not read image digest: $GOT_DIGEST"; exit 8; }
echo "D8G_R2_DIGEST $IMG -> $GOT_DIGEST"

# ---- host pre-state, for the row's infrastructure fields ----------------------
MEMAVAIL_GIB=$(awk '/MemAvailable/ {printf "%.2f", $2/1048576}' /proc/meminfo)
SIBLINGS_PRE=$(docker ps --format '{{.Names}}' 2>/dev/null | tr '\n' ',' | sed 's/,$//')

# ---- THE ARM COMMAND.  mpirun is the LAST line, so the container's exit code is
# ---- the solver's own and nothing else's.
cat > "$WORK/d8g_cmd.sh" <<CMD
echo "D4S_MPIRUN_EPOCH: \$(date -u +%s) iso=\$(date -u +%Y-%m-%dT%H:%M:%SZ) arm=$ARM"
mpirun --allow-run-as-root -np 4 --bind-to core --report-bindings -x PYTHONPATH python d8g_of.py -mode P -level L1
CMD
grep -q timeout "$WORK/d8g_cmd.sh" && { echo "ABORT a timeout survived into the cmdfile"; exit 9; }
echo "CMDFILE md5=$(md5sum $WORK/d8g_cmd.sh | cut -d' ' -f1)"

# ---- LAUNCH.  Containment intact, deadline absent, cpuset REGISTERED. ---------
NAME=d8g_${ARM}_${STAMP}
LOG=$BASE/${ARM}_${STAMP}.log
CID=$(docker run -d --name "$NAME" \
    --user 0:0 --cpuset-cpus="$CPUSET" --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4S_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4S_IDWARP_IMPORTED_FROM:\",p); print(\"D4S_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     bash /mnt/$ARM/d8g_cmd.sh" 2> "$BASE/${ARM}_${STAMP}.runerr") \
  || { echo "ABORT could not start container: $(head -c 400 "$BASE/${ARM}_${STAMP}.runerr")"; exit 4; }
echo "$CID" | grep -qE '^[0-9a-f]{12,64}$' || { echo "ABORT docker run returned no cid: $CID"; exit 4; }
echo "$CID" > $BASE/${ARM}_${STAMP}.cid
echo "D8G_R2_LAUNCHED cid=$CID name=$NAME stamp=$STAMP ranks=4 cwd=$WORK mem=$MEM cpuset=$CPUSET"

# ---- RECORDER.  setsid-detached.  rc captured INSIDE the wrapper from the
# ---- CONTAINER'S OWN exit status -- never from the setsid line, which returns 0
# ---- for every outcome.  Starts nothing, signals nothing, kills nothing.
# ---- DEFECT 2 FIX: the row below is d8g_run_arm.sh:1010's canonical form.
# ---- enforced_wall_s / enforced_core_min are written 0 -- the HONEST value under
# ---- NO-CAP: no deadline was enforced.  Nothing in the comparator gates either.
setsid bash -c '
  BASE="'"$BASE"'"; ARM="'"$ARM"'"; ROW="'"$ROW"'"; STAMP="'"$STAMP"'"; NAME="'"$NAME"'"
  LOG="'"$LOG"'"; IMG="'"$IMG"'"; DIG="'"$GOT_DIGEST"'"; MEM="'"$MEM"'"
  CPUSET="'"$CPUSET"'"; CAP="'"$CAP"'"; MEMPRE="'"$MEMAVAIL_GIB"'"; SIBPRE="'"$SIBLINGS_PRE"'"
  T0=$(date -u +%s)
  docker logs -f "$NAME" >> "$LOG" 2>&1 &
  RC=$(docker wait "$NAME" 2>/dev/null)
  INSPECT=$(docker inspect -f "{{.State.ExitCode}} {{.State.OOMKilled}}" "$NAME" 2>/dev/null)
  T1=$(date -u +%s); WALL=$((T1-T0))
  CM=$(python3 -c "print(\"%.3f\" % ($WALL*4/60.0))")
  MEMPOST=$(awk "/MemAvailable/ {printf \"%.2f\", \$2/1048576}" /proc/meminfo)
  SIBPOST=$(docker ps --format "{{.Names}}" 2>/dev/null | tr "\n" "," | sed "s/,\$//")
  printf "ARM=%s ROW=%s IMG=%s DIGEST=%s rc=%s wall_s=%s ranks=4 core_min=%s cap_core_min=%s enforced_wall_s=0 enforced_core_min=0 memory=%s inspect(exit,oomkilled)=[%s] memavail_pre_GiB=%s memavail_post_GiB=%s cpuset=%s delivered_cores_mean=[NOT_MEASURED] siblings_pre=[%s] siblings_post=[%s] log=%s stamp=%s\n" \
    "$ARM" "$ROW" "$IMG" "$DIG" "$RC" "$WALL" "$CM" "$CAP" "$MEM" "$INSPECT" \
    "$MEMPRE" "$MEMPOST" "$CPUSET" "$SIBPRE" "$SIBPOST" "$(basename "$LOG")" "$STAMP" >> "$BASE/ledger.txt"
  echo "rc=$RC wall_s=$WALL core_min=$CM inspect(exit,oomkilled)=[$INSPECT]" > "$BASE/STATUS.$ARM"
' < /dev/null > "$BASE/${ARM}_${STAMP}.watcher.out" 2>&1 &
echo "D8G_R2_WATCHER_DETACHED (records only; cannot signal, kill or renice)"
