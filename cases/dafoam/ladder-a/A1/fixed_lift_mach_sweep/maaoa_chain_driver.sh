#!/usr/bin/env bash
# =============================================================================
# MAAOA -- FIXED-LIFT (Ma, AoA) SWEEP CHAIN DRIVER. One detached process,
# launched by the queue daemon; it outlives every agent (Sanaa 2026-09-02:
# "even if the fleet dies, they still run").
#
# THE DEPENDENCY LIVES HERE, NOT IN ANY AGENT: this driver launches NO solver
# until A1WR's Stage-1 y+ gate file exists and reads verdict PASS -- the fine
# grid (A1WR L3) is only "fine" once the probe has measured it wall-resolved.
# On GATE FAIL or REFUSED it exits BLOCKED, spend 0.0 -- a registered outcome.
#
# Governed by MAAOA_PREREGISTRATION.md (frozen with this file). np = 1 per
# point; pool of SIX one-core cpusets {2..7} so cores 0-1 never carry a pin
# (filming headroom); OMP_NUM_THREADS=1; per-point deadline INSIDE the
# container (7,200 s = the 120 core-min per-point cap; rule 12 -- an overrun
# STOPS the run); MemAvailable floor 6.0 GiB before each launch, so this item
# self-staggers behind A1WR's peak hour instead of overcommitting the box.
# =============================================================================
set -uo pipefail

HERE="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/fixed_lift_mach_sweep"
A1WR_GATE="/home/ubuntu/certonomous-runs/A1WR/STAGE12/stage1_gate.json"
RUN="/home/ubuntu/certonomous-runs/MAAOA"
MESH="/home/ubuntu/certonomous-runs/A1WR/L3/constant/polyMesh"
SKEL_I="/home/ubuntu/certonomous-runs/CURRICULUM-AOAI-a1-naca0012-alpha-polar-incompressible/case"
SKEL_C="/home/ubuntu/certonomous-runs/CURRICULUM-AOAC-a1-naca0012-alpha-polar-compressible/case"
IMG="dafoam-idwarp-rot:v1"
IMG_DIGEST_WANT="2927768a16ac"

POINT_TMO=7200            # s in-container = per-point cap 120 core-min at np=1
WAIT_DEADLINE_S=43200     # 12 h bound on the gate wait
MEM_FLOOR_KB=6291456      # 6.0 GiB
MEM_WAIT_BOUND_S=43200
CORES="2 3 4 5 6 7"
ITEM_CAP_MIN=900

# The registered points: label|arm|U0|alpha0. M = U0 / 347.1904 (a at T0=300 K
# from the READ constants: gamma 1.4, R 287.0028, T0 300 -- A1WR amendment 1).
POINTS="MA288|C|100.0|4.0
MA400|C|138.8762|4.0
MA500|C|173.5952|4.0
MA600|C|208.3142|3.0
MA650|C|225.6738|3.0
MA685|C|237.8254|2.0
INCOMP|I|10.0|4.0"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
STATUS="$HERE/STATUS.MAAOA_chain"
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*"; }

# --- G-ROOT ------------------------------------------------------------------
if [ -e "$RUN" ]; then
  say "MAAOA_ABORT G-ROOT: run root already exists: $RUN"
  echo "rc=6 phase=G-ROOT utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATUS"; exit 6
fi

# --- G-SRC + FREEZE ----------------------------------------------------------
for f in maaoa_runScript_incomp.py maaoa_runScript_comp.py maaoa_cmd.sh \
         maaoa_read.py MAAOA_MD5.txt; do
  test -f "$HERE/$f" || { say "MAAOA_ABORT G-SRC instrument absent: $f"; echo "rc=5 phase=G-SRC" > "$STATUS"; exit 5; }
done
( cd "$HERE" && md5sum -c MAAOA_MD5.txt --quiet ) \
  || { say "MAAOA_ABORT G-FREEZE: instrument drifted from MAAOA_MD5.txt"; echo "rc=4 phase=G-FREEZE" > "$STATUS"; exit 4; }
say "MAAOA_G_FREEZE_PASS instruments match MAAOA_MD5.txt"

GOT="$(sudo -n docker image inspect --format '{{.Id}}' "$IMG" 2>/dev/null)"
case "$GOT" in
  *${IMG_DIGEST_WANT}*) say "MAAOA_G_IMG_PASS $IMG is the PATCHED build" ;;
  *) say "MAAOA_ABORT G-IMG $IMG id '$GOT' does not carry $IMG_DIGEST_WANT"; echo "rc=4 phase=G-IMG" > "$STATUS"; exit 4 ;;
esac

# --- G-GATEDEP: wait for A1WR's probe verdict, bounded, terminating ----------
say "MAAOA_WAIT_BEGIN precondition=$A1WR_GATE deadline_s=$WAIT_DEADLINE_S"
WAITED=0
while true; do
  if [ -f "$A1WR_GATE" ]; then
    V="$(python3 -c "import json;print(json.load(open('$A1WR_GATE')).get('verdict','UNREADABLE'))" 2>/dev/null || echo UNREADABLE)"
    if [ "$V" = "PASS" ]; then
      say "MAAOA_GATEDEP_PASS A1WR stage-1 gate verdict PASS after ${WAITED}s -- L3 measured wall-resolved on both arms"
      break
    elif [ "$V" = "GATE FAIL" ] || [ "$V" = "REFUSED" ]; then
      say "MAAOA_BLOCKED A1WR stage-1 gate verdict '$V' -- the fine-grid premise failed; NOTHING LAUNCHED, spend 0.0 (registered outcome)"
      echo "rc=0 phase=BLOCKED-BY-A1WR-GATE verdict_upstream='$V' launched=NOTHING spend_core_min=0.0 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATUS"
      exit 0
    fi
  fi
  if [ "$WAITED" -ge "$WAIT_DEADLINE_S" ]; then
    say "MAAOA_BLOCKED gate file absent/unreadable at the ${WAIT_DEADLINE_S}s bound -- NOTHING LAUNCHED"
    echo "rc=6 phase=BLOCKED-WAIT-DEADLINE launched=NOTHING spend_core_min=0.0 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATUS"
    exit 6
  fi
  sleep 60; WAITED=$((WAITED + 60))
done

mkdir -p "$RUN/logs"
LEDGER="$RUN/CHAIN_LEDGER.tsv"
printf 'point\tarm\tU0\tmach_label\tcpuset\tmem\tomp\ttmo_s\tlaunch_utc\tloadavg\trc\toom\twall_s\tcore_min\tend_utc\n' > "$LEDGER"

stage_point() {  # label arm
  local name="$1" arm="$2" skel u
  u="$RUN/$name"
  [ "$arm" = "I" ] && skel="$SKEL_I" || skel="$SKEL_C"
  mkdir -p "$u/out" || return 1
  cp -r "$skel" "$u/case" || return 1
  rm -rf "$u/case/constant/polyMesh" "$u/case/0" "$u/case/postProcessing" \
         "$u/case/reports" "$u/case/mphys.html" "$u/case/case.foam" 2>/dev/null
  ( cd "$u/case" && for d in [0-9]* 0.[0-9]*; do [ -d "$d" ] && rm -rf "$d"; done ) 2>/dev/null
  cp -r "$MESH" "$u/case/constant/polyMesh" || return 1
  test -d "$u/case/0.orig" || return 1
  test -f "$u/case/FFD/wingFFD.xyz" || return 1
  if [ "$arm" = "I" ]; then cp "$HERE/maaoa_runScript_incomp.py" "$u/runScript.py"
  else cp "$HERE/maaoa_runScript_comp.py" "$u/runScript.py"; fi
  cp "$HERE/maaoa_cmd.sh" "$u/maaoa_cmd.sh" || return 1
  cat > "$u/case/system/controlDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         4000;
deltaT          1;
writeControl    timeStep;
writeInterval   4000;
purgeWrite      0;
writeFormat     ascii;
writePrecision  16;
writeCompression on;
timeFormat      general;
timePrecision   16;
runTimeModifiable true;
DebugSwitches { SolverPerformance 0; }
functions
{
    yPlus1
    {
        type            yPlus;
        libs            ("libfieldFunctionObjects.so");
        executeControl  writeTime;
        writeControl    writeTime;
        log             true;
    }
}
EOF
  return 0
}

mem_wait() {
  local waited=0 kb
  while true; do
    kb="$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)"
    [ -n "$kb" ] || return 1
    [ "$kb" -ge "$MEM_FLOOR_KB" ] && return 0
    [ "$waited" -ge "$MEM_WAIT_BOUND_S" ] && return 1
    sleep 30; waited=$((waited + 30))
  done
}

core_busy() {  # is this cpuset core held by a live container?
  local want="$1" c used
  for c in $(sudo -n docker ps -q 2>/dev/null); do
    used="$(sudo -n docker inspect -f '{{.HostConfig.CpusetCpus}}' "$c" 2>/dev/null)"
    case ",$used," in *",$want,"*) return 0 ;; esac
  done
  return 1
}

TOTAL_SPEND=0
declare -A CORE_OF T0_OF ARM_OF U0_OF LA_OF
ACTIVE=""

launch_point() {  # label arm U0 alpha0 core
  local name="$1" arm="$2" u0="$3" a0="$4" core="$5"
  stage_point "$name" "$arm" || { say "MAAOA_WARN staging failed for $name -- point recorded as NOT RUN"; return 1; }
  mem_wait || { say "MAAOA_WARN memory floor never cleared for $name -- point recorded as NOT RUN"; return 1; }
  local la; la="$(cut -d' ' -f1-3 /proc/loadavg)"
  local envu=()
  [ "$arm" = "C" ] && envu=(-e MAAOA_U0="$u0")
  sudo -n docker run -d --name "maaoa_${name}_${STAMP}" \
      --user 0:0 --cpus=1 --cpuset-cpus="$core" --memory=3g --memory-swap=3g \
      --oom-score-adj=500 \
      -e OMP_NUM_THREADS=1 "${envu[@]}" \
      -e MAAOA_MACH="$name" -e MAAOA_ALPHA0="$a0" -e MAAOA_TMO="$POINT_TMO" \
      -v "$RUN/$name":/mnt -w /mnt/case "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && timeout -k 60 $((POINT_TMO + 600)) bash /mnt/maaoa_cmd.sh" \
      > /dev/null 2>&1 || { say "MAAOA_WARN docker start failed for $name"; return 1; }
  CORE_OF[$name]="$core"; T0_OF[$name]="$(date -u +%s)"; ARM_OF[$name]="$arm"
  U0_OF[$name]="$u0"; LA_OF[$name]="$la"
  ACTIVE="$ACTIVE $name"
  say "MAAOA_LAUNCHED point=$name arm=$arm U0=$u0 cpuset=$core mem=3g omp=1 loadavg=$la"
  return 0
}

reap_done() {  # harvest finished containers; frees cores; returns freed count
  local name cn running rc oom t1 wall cm still=""
  for name in $ACTIVE; do
    cn="maaoa_${name}_${STAMP}"
    running="$(sudo -n docker inspect --format '{{.State.Running}}' "$cn" 2>/dev/null)"
    if [ "$running" = "true" ]; then still="$still $name"; continue; fi
    rc="$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$cn" 2>/dev/null)"
    oom="$(sudo -n docker inspect --format '{{.State.OOMKilled}}' "$cn" 2>/dev/null)"
    t1="$(date -u +%s)"; wall=$((t1 - ${T0_OF[$name]}))
    cm="$(python3 -c "print(round($wall/60.0, 4))")"
    TOTAL_SPEND="$(python3 -c "print(round($TOTAL_SPEND + $cm, 4))")"
    sudo -n docker logs "$cn" > "$RUN/logs/$name.docker.log" 2>&1
    printf '%s\t%s\t%s\t%s\t%s\t3g\t1\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$name" "${ARM_OF[$name]}" "${U0_OF[$name]}" "$name" "${CORE_OF[$name]}" \
      "$POINT_TMO" "$(date -u -d "@${T0_OF[$name]}" +%Y-%m-%dT%H:%M:%SZ)" "${LA_OF[$name]}" \
      "$rc" "$oom" "$wall" "$cm" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LEDGER"
    FREE_CORES="$FREE_CORES ${CORE_OF[$name]}"
    say "MAAOA_POINT_DONE point=$name rc=$rc oom=$oom wall_s=$wall core_min=$cm total=$TOTAL_SPEND"
  done
  ACTIVE="$still"
}

say "MAAOA_CHAIN_BEGIN stamp=$STAMP pid=$$ img=$IMG cap_total=$ITEM_CAP_MIN core-min"
FREE_CORES="$CORES"
QUEUE="$POINTS"
LOOP_T0="$(date -u +%s)"
LOOP_BOUND_S=86400   # 24 h scheduler bound: running out of patience is an ERROR, not a pass
while [ -n "$QUEUE" ] || [ -n "${ACTIVE// /}" ]; do
  if [ $(( $(date -u +%s) - LOOP_T0 )) -ge "$LOOP_BOUND_S" ] && [ -z "${ACTIVE// /}" ]; then
    say "MAAOA_SCHEDULER_BOUND ${LOOP_BOUND_S}s reached with points still queued -- remaining points recorded NOT RUN: $(printf '%b' "$QUEUE" | cut -d'|' -f1 | tr '\n' ' ')"
    break
  fi
  # launch as many queued points as free cores + budget allow
  NEWQ=""
  while IFS='|' read -r label arm u0 a0; do
    [ -z "$label" ] && continue
    CAN="$(python3 -c "print('YES' if $TOTAL_SPEND + 120.0 <= $ITEM_CAP_MIN else 'NO')")"
    core="$(set -- $FREE_CORES; echo "${1:-}")"
    if [ "$CAN" = "NO" ]; then
      say "MAAOA_CAPSTOP point=$label NOT LAUNCHED: spend $TOTAL_SPEND + 120 would exceed the $ITEM_CAP_MIN cap -- NOT A RESULT on this point (G-CAPS)"
      continue
    fi
    if [ -z "$core" ]; then NEWQ="$NEWQ$label|$arm|$u0|$a0\n"; continue; fi
    if core_busy "$core"; then NEWQ="$NEWQ$label|$arm|$u0|$a0\n"; continue; fi
    FREE_CORES="$(set -- $FREE_CORES; shift; echo "$*")"
    launch_point "$label" "$arm" "$u0" "$a0" "$core" \
      || { FREE_CORES="$FREE_CORES $core"; say "MAAOA_POINT_NOT_RUN point=$label -- recorded"; }
  done <<< "$(printf '%b' "$QUEUE")"
  QUEUE="$(printf '%b' "$NEWQ")"
  sleep 30
  reap_done
done

python3 "$HERE/maaoa_read.py" "$RUN" > "$RUN/MAAOA_read_${STAMP}.txt" 2>&1
RRC=$?
say "MAAOA_READER rc=$RRC out=$RUN/MAAOA_read_${STAMP}.txt"

{
  echo "item=MAAOA stamp=$STAMP"
  echo "spend_total_core_min=$TOTAL_SPEND cap_total=$ITEM_CAP_MIN estimate=315"
  echo "cost_basis=anchors MEASURED (A1WR section 7.2/13.2); trim primal counts EXTRAPOLATED; dollars DERIVED at c7a.4xlarge \$0.0513/core-h owner-stated, NOT measured"
  echo "calibration_row=OWED to docs/COST_CALIBRATION.md at grading (rule 12); contention attributed separately"
} > "$RUN/COST_MAAOA.txt"
echo "rc=0 phase=COMPLETE spend_total=$TOTAL_SPEND reader_rc=$RRC utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATUS"
say "MAAOA_CHAIN_END total_core_min=$TOTAL_SPEND"
exit 0
