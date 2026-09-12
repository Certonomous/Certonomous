#!/bin/bash
# =============================================================================
# D8G L1-P-R1 -- THE R3 REPAIR PACKAGE.
# Frozen registration: PREREGISTRATION.md ADDENDUM 7 + ADDENDUM 8.
#
# THIS FILE IS THE REGISTERED d8g_run_arm.sh:811 CONTAINER COMMAND WITH EXACTLY
# ONE THING REMOVED: the `timeout -k 60 $TMO` wrapper.  Everything else that
# command carried is reproduced, including the loadDAFoam source and the idwarp
# identity probe that d8g_of.py records as identity:{libidwarp_so_md5}.
#
# --- WHAT IS REMOVED, AND WHY (these are STOPS) ------------------------------
#   `timeout -k 60 $TMO`  in-container deadline + SIGKILL escalation
#   cap_core_min -> TMO   the wall derived from a core-minute budget
#   the rc=124/137 path   the kernel's verdict on a killed run
#   LAUNCH_BUDGET_S       the launch-witness clock
#   la_kill() / exit 88   the refusal branch that kills the container
# Sanaa, 2026-09-12: "NO RUN GETS STOPPED BC OF A TIME OR BUDGET CAP."
#
# --- WHAT IS RETAINED, AND WHY (these are CONTAINMENT, NOT CAPS) -------------
#   --memory 6g --memory-swap 6g   D8G's registered L1-P figure (section 5
#                                  predicts ~0.09 GiB RSS, so this is ~67x the
#                                  need and CANNOT bind a healthy run)
#   --oom-score-adj=500            makes D8G the PREFERRED OOM victim, so a
#                                  runaway here is killed BEFORE a sibling run
# A memory ceiling is neither a time cap nor a budget cap.  It cannot stop this
# run on spend or clock; it only contains a runaway on a shared box currently at
# ~11 GiB available with four live containers (A3GC-AR1, D6R2, A3GC L2, A3GC L1).
# Removing it would not have honoured the NO-CAP order -- it would have put four
# other teams' runs at risk under cover of it.  A limit that cannot bind a
# healthy run is a seatbelt, not a cap.
#
# --- TWO DEPARTURES FROM :811, EACH JUSTIFIED ON ITS OWN ---------------------
#   1. `docker` not `sudo -n docker`.  `ubuntu` is in the `docker` group, so the
#      client reaches the same daemon with the same rights and the host sudo is
#      pure surplus privilege.  Matches every sibling dafoam launch on this box.
#      Zero behavioural change: the container's own user is set by --user.
#   2. `--cpus=4` replaces `--cpuset-cpus=$CPUSET`.  A share limit, not a pin,
#      so D8G cannot take more than four cores' worth AND cannot land on top of
#      a sibling's pinned cores.  Neither form can kill anything.
#   `--user 0:0` is KEPT: it is the registered form (:812) and it is what
#   produced the graded evidence.  Changing it mid-item would change provenance
#   and risk the container being unable to write into /mnt.
#
# The watcher RECORDS ONLY -- it starts nothing, signals nothing, kills nothing
# and renices nothing.  No sibling run is touched in any way.
# The core-minute figure is a REPORTED ESTIMATE and stops nothing.
# =============================================================================
set -e
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D8G-R1-a6-grid-triple
ARM=L1-P-R1; WORK=$BASE/$ARM; STAMP=$(date -u +%Y%m%dT%H%M%SZ)
IMG=dafoam-idwarp-rot:v1
MEM=6g                      # D8G registered cap_memory L1-P (d8g_run_arm.sh:231)

# ---- G-COLD: refuse a case that could silently warm-start --------------------
for bad in "$WORK/reports" "$WORK/d8g_P.json" "$WORK/d8g_P.jsonl" "$WORK/OptView.hst"; do
  test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }; done
test -n "$(ls -d $WORK/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
for d in $WORK/*/; do n=$(basename "$d"); case "$n" in
  0|0.orig|FFD|system|constant) ;; [0-9]*) echo "ABORT G-COLD time dir $n"; exit 5;; esac; done
test -f "$WORK/0/U" || { echo "ABORT G-COLD 0/U missing"; exit 5; }

# ---- RULE 4 AGE GUARD: 0/ is touched LAST, so it dates the run allowed to answer
touch "$WORK/0"/*
AGE=$(stat -c '%Y' "$WORK/0/U"); echo "$AGE" > "$WORK/.d8g_age_datum"
echo "D8G_R1_G_COLD OK arm=$ARM age_datum_epoch=$AGE"

# ---- THE ARM COMMAND.  mpirun is the LAST line, so the container's exit code
# ---- is the solver's own and nothing else's.
cat > "$WORK/d8g_cmd.sh" <<'CMD'
echo "D4S_MPIRUN_EPOCH: $(date -u +%s) iso=$(date -u +%Y-%m-%dT%H:%M:%SZ) arm=L1-P-R1"
mpirun --allow-run-as-root -np 4 --bind-to core --report-bindings -x PYTHONPATH python d8g_of.py -mode P -level L1
CMD
grep -q timeout "$WORK/d8g_cmd.sh" && { echo "ABORT a timeout survived into the cmdfile"; exit 9; }
echo "CMDFILE md5=$(md5sum $WORK/d8g_cmd.sh | cut -d' ' -f1)"

# ---- LAUNCH.  The :811 command, containment intact, deadline removed. --------
NAME=d8g_${ARM}_${STAMP}
LOG=$BASE/${ARM}_${STAMP}.log
CID=$(docker run -d --name "$NAME" \
    --user 0:0 --cpus=4 --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4S_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4S_IDWARP_IMPORTED_FROM:\",p); print(\"D4S_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     bash /mnt/$ARM/d8g_cmd.sh" 2> "$BASE/${ARM}_${STAMP}.runerr") \
  || { echo "ABORT could not start container: $(head -c 400 "$BASE/${ARM}_${STAMP}.runerr")"; exit 4; }
echo "$CID" | grep -qE '^[0-9a-f]{12,64}$' || { echo "ABORT docker run returned no cid: $CID"; exit 4; }
echo "$CID" > $BASE/${ARM}_${STAMP}.cid
echo "D8G_R1_LAUNCHED cid=$CID name=$NAME stamp=$STAMP ranks=4 cwd=$WORK mem=$MEM"

# ---- RECORDER.  setsid-detached.  rc is captured INSIDE the wrapper, from the
# ---- CONTAINER'S OWN exit status -- never from the status of the setsid line,
# ---- which returns 0 for every outcome.  This loop starts nothing and kills
# ---- nothing; if it dies the solver is unaffected and docker inspect still
# ---- holds the authoritative exit code.  OOMKilled is recorded so the kernel's
# ---- verdict is READ rather than inferred.
setsid bash -c '
  BASE="'"$BASE"'"; ARM="'"$ARM"'"; STAMP="'"$STAMP"'"; NAME="'"$NAME"'"; LOG="'"$LOG"'"
  T0=$(date -u +%s)
  docker logs -f "$NAME" >> "$LOG" 2>&1 &
  RC=$(docker wait "$NAME" 2>/dev/null)                  # <-- rc INSIDE the wrapper
  INSP=$(docker inspect -f "{{.State.ExitCode}}|{{.State.OOMKilled}}" "$NAME" 2>/dev/null)
  T1=$(date -u +%s); WALL=$((T1-T0))
  CM=$(python3 -c "print(\"%.3f\" % ($WALL*4/60.0))")
  printf "ARM=%s ROW=D8G-R1 rc=%s inspect(exit,oom)=[%s] wall_s=%s ranks=4 core_min=%s stamp=%s log=%s\n" \
    "$ARM" "$RC" "$INSP" "$WALL" "$CM" "$STAMP" "$(basename "$LOG")" >> "$BASE/ledger.txt"
  echo "rc=$RC wall_s=$WALL core_min=$CM inspect(exit,oom)=[$INSP]" > "$BASE/STATUS.$ARM"
' < /dev/null > "$BASE/${ARM}_${STAMP}.watcher.out" 2>&1 &
echo "D8G_R1_WATCHER_DETACHED (records only; cannot signal, kill or renice)"
