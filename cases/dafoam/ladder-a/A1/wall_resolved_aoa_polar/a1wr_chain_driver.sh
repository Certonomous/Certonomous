#!/usr/bin/env bash
# =============================================================================
# A1WR STAGES 1-2 -- THE CHAIN DRIVER. One detached process, launched by the
# queue daemon (scripts/queue_runner.py); it outlives every agent and session.
# Sanaa's order 2026-09-02 ~19:00Z: "These runs must either be launched or
# queued, such that even if the fleet dies, they still run."
#
# THE STAGE-1 -> STAGE-2 GATING LIVES HERE, IN THIS PROCESS, NOT IN ANY AGENT:
# a1wr_stage1_gate.py takes the launch decision from bytes on disk
# (A1WR_PREREGISTRATION.md section 5: "If Stage 1 measures y+max >= 1 on either
# arm, Stage 2 does not launch").
#
# Governed by A1WR_PREREGISTRATION.md v1.1 + Addenda A-C. Registered layout
# (Addendum A section 13.6, Addendum B section 14.2): np = 1 EVERY unit; one
# explicit ONE-CORE cpuset per concurrent unit; OMP_NUM_THREADS=1 exported and
# recorded; the continued sweeps stay SERIAL BY DESIGN (that serialisation IS
# the continuation) and only distinct units run concurrently.
#
# Caps (section 7.4, CLOSED, not raised): Stage 1 <= 120 core-min (2 units x
# 3,600 s in-container deadline); Stage 2 <= 800 core-min PER ARM, allocated
# sweep 37,200 s + 3 colds x 3,300 s = 785 core-min < 800; the duplicate
# G-CONCURRENCY-BITS point launches ONLY if the incompressible arm's measured
# spend + its 55-min bound stays <= 800. An overrun STOPS the run: the
# deadline sits INSIDE each container (`timeout` around the python), so it
# survives the death of this driver, of the daemon and of every agent.
# =============================================================================
set -uo pipefail

HERE="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar"
ROOT="/home/ubuntu/certonomous-runs/A1WR"
RUN="$ROOT/STAGE12"
MESH="$ROOT/L3/constant/polyMesh"
SKEL_I="/home/ubuntu/certonomous-runs/CURRICULUM-AOAI-a1-naca0012-alpha-polar-incompressible/case"
SKEL_C="/home/ubuntu/certonomous-runs/CURRICULUM-AOAC-a1-naca0012-alpha-polar-compressible/case"

# THE PATCHED BUILD -- Sanaa 2026-09-02 ~19:40Z: "The patching needs to happen
# (parallelization transpose fix)". The D19-family PATCHED row's image,
# identity re-measured at enqueue (D19M records):
IMG="dafoam-idwarp-rot:v1"
IMG_DIGEST_WANT="2927768a16ac"

PROBE_TMO=3600     # s, in-container; 2 x 3600 s = 120.0 core-min = the Stage-1 cap
SWEEP_TMO=37200    # s = 620 core-min at np=1
COLD_TMO=3300      # s = 55 core-min
MEM_FLOOR_KB=4194304   # 4.0 GiB -- the registered launch floor (section 7.4)
MEM_WAIT_BOUND_S=7200
ARM_CAP_MIN=800

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
STATUS="$HERE/STATUS.A1WR_chain"
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*"; }
note() { say "$*" >> "$STATUS.log"; say "$*"; }

mkdir -p "$RUN" 2>/dev/null
LEDGER="$RUN/CHAIN_LEDGER.tsv"

# --- G-ROOT: stages 1-2 run once. -------------------------------------------
if [ -e "$RUN/probe_I" ] || [ -e "$RUN/sweep_I" ]; then
  say "A1WR_ABORT G-ROOT: stage 1/2 unit directories already exist under $RUN"
  echo "rc=6 phase=G-ROOT utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATUS"; exit 6
fi

# --- G-SRC + FREEZE VERIFICATION: the frozen files are the files that run ----
for f in a1wr_runScript_incomp.py a1wr_runScript_comp.py a1wr_cmd.sh \
         a1wr_stage1_gate.py a1wr_read.py A1WR_STAGE12_MD5.txt; do
  test -f "$HERE/$f" || { say "A1WR_ABORT G-SRC instrument absent: $f"; echo "rc=5 phase=G-SRC" > "$STATUS"; exit 5; }
done
( cd "$HERE" && md5sum -c A1WR_STAGE12_MD5.txt --quiet ) \
  || { say "A1WR_ABORT G-FREEZE: an instrument drifted from its frozen md5 (A1WR_STAGE12_MD5.txt)"; echo "rc=4 phase=G-FREEZE" > "$STATUS"; exit 4; }
say "A1WR_G_FREEZE_PASS all instruments match A1WR_STAGE12_MD5.txt"
test -f "$MESH/points.gz" || { say "A1WR_ABORT G-SRC L3 mesh absent"; echo "rc=5 phase=G-SRC" > "$STATUS"; exit 5; }
for s in "$SKEL_I" "$SKEL_C"; do
  test -d "$s/0.orig" || { say "A1WR_ABORT G-SRC skeleton 0.orig absent: $s"; echo "rc=5 phase=G-SRC" > "$STATUS"; exit 5; }
done
grep -A2 '^    wing$' "$MESH/boundary" | grep -q 'type            wall' \
  || { say "A1WR_ABORT G-SRC wing patch is not type wall in L3 boundary"; echo "rc=5 phase=G-SRC" > "$STATUS"; exit 5; }

# --- G-IMG: the PATCHED image, by digest ------------------------------------
GOT="$(sudo -n docker image inspect --format '{{.Id}}' "$IMG" 2>/dev/null)"
case "$GOT" in
  *${IMG_DIGEST_WANT}*) say "A1WR_G_IMG_PASS $IMG is the PATCHED build ($GOT)" ;;
  *) say "A1WR_ABORT G-IMG $IMG id '$GOT' does not carry $IMG_DIGEST_WANT"; echo "rc=4 phase=G-IMG" > "$STATUS"; exit 4 ;;
esac

if [ ! -f "$LEDGER" ]; then
  printf 'unit\tarm\tmode\talphas\tcpuset\tmem\tomp\ttol\ttmo_s\tlaunch_utc\tloadavg_at_launch\trc\toom\twall_s\tcore_min\tend_utc\n' > "$LEDGER"
fi

mem_wait() {
  local waited=0
  while true; do
    local kb; kb="$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)"
    [ -n "$kb" ] || { say "A1WR_ABORT cannot read MemAvailable"; return 1; }
    [ "$kb" -ge "$MEM_FLOOR_KB" ] && { say "A1WR_MEM_OK avail_kb=$kb waited_s=$waited"; return 0; }
    [ "$waited" -ge "$MEM_WAIT_BOUND_S" ] && { say "A1WR_MEM_WAIT_EXCEEDED avail_kb=$kb"; return 1; }
    sleep 30; waited=$((waited + 30))
  done
}

cpuset_free() {  # refuse a collision with a LIVE container (d19m pattern)
  local want="$1" c used
  for c in $(sudo -n docker ps -q 2>/dev/null); do
    used="$(sudo -n docker inspect -f '{{.HostConfig.CpusetCpus}}' "$c" 2>/dev/null)"
    case ",$used," in *",$want,"*) return 1 ;; esac
  done
  return 0
}

stage_unit() {  # stage_unit NAME ARM
  local name="$1" arm="$2" skel u
  u="$RUN/$name"
  [ "$arm" = "I" ] && skel="$SKEL_I" || skel="$SKEL_C"
  mkdir -p "$u/out" || return 1
  cp -r "$skel" "$u/case" || return 1
  rm -rf "$u/case/constant/polyMesh" "$u/case/0" "$u/case/postProcessing" \
         "$u/case/reports" "$u/case/mphys.html" "$u/case/case.foam" 2>/dev/null
  # any numeric/renamed time dirs that rode along in the copy are removed
  ( cd "$u/case" && for d in [0-9]* 0.[0-9]*; do [ -d "$d" ] && rm -rf "$d"; done ) 2>/dev/null
  cp -r "$MESH" "$u/case/constant/polyMesh" || return 1
  test -d "$u/case/0.orig" || return 1
  test -f "$u/case/FFD/wingFFD.xyz" || return 1
  if [ "$arm" = "I" ]; then cp "$HERE/a1wr_runScript_incomp.py" "$u/runScript.py"
  else cp "$HERE/a1wr_runScript_comp.py" "$u/runScript.py"; fi
  cp "$HERE/a1wr_cmd.sh" "$u/a1wr_cmd.sh" || return 1
  local et="$3"
  cat > "$u/case/system/controlDict" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         $et;
deltaT          1;
writeControl    timeStep;
writeInterval   $et;
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

launch_unit() {  # launch_unit NAME ARM MODE ALPHAS TOL TMO CPUSET MEM ENDTIME
  local name="$1" arm="$2" mode="$3" alphas="$4" tol="$5" tmo="$6" cpu="$7" mem="$8" et="$9"
  stage_unit "$name" "$arm" "$et" || { say "A1WR_ABORT staging failed for $name"; return 1; }
  cpuset_free "$cpu" || { say "A1WR_ABORT G-CPUSET core $cpu held by a live container ($name)"; return 1; }
  mem_wait || return 1
  local pps=""
  [ "$arm" = "I" ] && pps="simpleFoam" || pps="rhoSimpleFoam"
  local la; la="$(cut -d' ' -f1-3 /proc/loadavg)"
  sudo -n docker run -d --name "a1wr_${name}_${STAMP}" \
      --user 0:0 --cpus=1 --cpuset-cpus="$cpu" --memory="$mem" --memory-swap="$mem" \
      --oom-score-adj=500 \
      -e OMP_NUM_THREADS=1 \
      -e A1WR_MODE="$mode" -e A1WR_ALPHAS="$alphas" -e A1WR_TOL="$tol" \
      -e A1WR_TMO="$tmo" -e A1WR_PP_SOLVER="$pps" \
      -v "$RUN/$name":/mnt -w /mnt/case "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && timeout -k 60 $((tmo + 900)) bash /mnt/a1wr_cmd.sh" \
      > /dev/null 2>&1 || { say "A1WR_ABORT could not start container for $name"; return 1; }
  echo "$name|$arm|$mode|$alphas|$cpu|$mem|$tol|$tmo|$(date -u +%s)|$la" >> "$RUN/inflight.txt"
  say "A1WR_LAUNCHED unit=$name arm=$arm mode=$mode cpuset=$cpu mem=$mem tmo_s=$tmo omp=1 loadavg_at_launch=$la"
  return 0
}

wait_all() {  # waits for every name in inflight.txt; writes ledger rows; sets ARM spends
  local line name arm mode alphas cpu mem tol tmo t0 la cn running rc oom t1 wall cm
  while [ -s "$RUN/inflight.txt" ]; do
    local remaining=""
    while IFS='|' read -r name arm mode alphas cpu mem tol tmo t0 la; do
      cn="a1wr_${name}_${STAMP}"
      running="$(sudo -n docker inspect --format '{{.State.Running}}' "$cn" 2>/dev/null)"
      if [ "$running" = "true" ]; then
        remaining="${remaining}${name}|${arm}|${mode}|${alphas}|${cpu}|${mem}|${tol}|${tmo}|${t0}|${la}\n"
        continue
      fi
      rc="$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$cn" 2>/dev/null)"
      oom="$(sudo -n docker inspect --format '{{.State.OOMKilled}}' "$cn" 2>/dev/null)"
      t1="$(date -u +%s)"; wall=$((t1 - t0))
      cm="$(python3 -c "print(round($wall/60.0, 4))")"
      mkdir -p "$RUN/logs"; sudo -n docker logs "$cn" > "$RUN/logs/$name.docker.log" 2>&1
      printf '%s\t%s\t%s\t%s\t%s\t%s\t1\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$name" "$arm" "$mode" "$alphas" "$cpu" "$mem" "$tol" "$tmo" \
        "$(date -u -d "@$t0" +%Y-%m-%dT%H:%M:%SZ)" "$la" "$rc" "$oom" "$wall" "$cm" \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LEDGER"
      say "A1WR_UNIT_DONE unit=$name rc=$rc oom=$oom wall_s=$wall core_min=$cm"
      if [ "$arm" = "I" ]; then I_SPEND="$(python3 -c "print(round($I_SPEND + $cm, 4))")"
      else C_SPEND="$(python3 -c "print(round($C_SPEND + $cm, 4))")"; fi
    done < "$RUN/inflight.txt"
    printf "%b" "$remaining" > "$RUN/inflight.txt"
    [ -s "$RUN/inflight.txt" ] && sleep 20
  done
}

I_SPEND=0; C_SPEND=0
: > "$RUN/inflight.txt"
: > "$STATUS.log"
note "A1WR_CHAIN_BEGIN stamp=$STAMP pid=$$ img=$IMG"

# ============================= STAGE 1 -- THE y+ PROBE =======================
note "A1WR_STAGE1_BEGIN alpha=18 both arms, FIXED 1500 iterations, cap 120 core-min"
launch_unit probe_I I PROBE "18" "1e-30" "$PROBE_TMO" 8 4g 1500 || { echo "rc=1 phase=STAGE1-LAUNCH" > "$STATUS"; exit 1; }
launch_unit probe_C C PROBE "18" "1e-30" "$PROBE_TMO" 9 4g 1500 || { echo "rc=1 phase=STAGE1-LAUNCH" > "$STATUS"; exit 1; }
wait_all
note "A1WR_STAGE1_END spend_I=$I_SPEND spend_C=$C_SPEND core-min (cap 120 total)"

# ============================= THE GATE ======================================
python3 "$HERE/a1wr_stage1_gate.py" "$RUN/probe_I" "$RUN/probe_C" > "$RUN/stage1_gate.out" 2>&1
GRC=$?
note "A1WR_STAGE1_GATE rc=$GRC gate_json=$RUN/stage1_gate.json"
if [ "$GRC" -eq 3 ]; then
  note "A1WR_GATE_FAIL_STOP: measured y+max >= 1.0 -- Stage 2 DOES NOT LAUNCH (section 3.4). The wall-resolved claim is WITHDRAWN for the affected arm(s); the mesh is NOT re-cut. This is a REGISTERED outcome."
  echo "rc=0 phase=GATE-FAIL-STOP verdict='GATE FAIL' stage2=NOT-LAUNCHED utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATUS"
  exit 0
elif [ "$GRC" -ne 0 ]; then
  note "A1WR_GATE_REFUSED rc=$GRC: the y+ reading could not be trusted (rule 3 fail-closed). Stage 2 NOT launched. NOT A RESULT on Stage 1."
  echo "rc=2 phase=GATE-REFUSED stage2=NOT-LAUNCHED utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATUS"
  exit 2
fi
note "A1WR_GATE_PASS: y+max < 1.0 on both arms -- Stage 2 launches"

# ============================= STAGE 2 -- THE SWEEPS =========================
ALPHAS="0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18"
note "A1WR_STAGE2_BEGIN 8 concurrent np=1 units, cores 8-15, per-arm cap 800 core-min"
launch_unit sweep_I  I CONTINUED "$ALPHAS" "1.0e-8" "$SWEEP_TMO" 8  4g 4000 || { echo "rc=1 phase=STAGE2-LAUNCH" > "$STATUS"; exit 1; }
launch_unit sweep_C  C CONTINUED "$ALPHAS" "1.0e-8" "$SWEEP_TMO" 9  4g 4000 || { echo "rc=1 phase=STAGE2-LAUNCH" > "$STATUS"; exit 1; }
launch_unit cold_I_4  I COLD "4"  "1.0e-8" "$COLD_TMO" 10 3g 4000 || note "A1WR_WARN cold_I_4 failed to launch -- recorded, chain continues"
launch_unit cold_I_14 I COLD "14" "1.0e-8" "$COLD_TMO" 11 3g 4000 || note "A1WR_WARN cold_I_14 failed to launch"
launch_unit cold_I_17 I COLD "17" "1.0e-8" "$COLD_TMO" 12 3g 4000 || note "A1WR_WARN cold_I_17 failed to launch"
launch_unit cold_C_4  C COLD "4"  "1.0e-8" "$COLD_TMO" 13 3g 4000 || note "A1WR_WARN cold_C_4 failed to launch"
launch_unit cold_C_14 C COLD "14" "1.0e-8" "$COLD_TMO" 14 3g 4000 || note "A1WR_WARN cold_C_14 failed to launch"
launch_unit cold_C_17 C COLD "17" "1.0e-8" "$COLD_TMO" 15 3g 4000 || note "A1WR_WARN cold_C_17 failed to launch"
wait_all
note "A1WR_STAGE2_END spend_I=$I_SPEND spend_C=$C_SPEND core-min (cap $ARM_CAP_MIN per arm)"

# ============== G-CONCURRENCY-BITS -- the alone-copy of cold_I_4 =============
CAN_DUP="$(python3 -c "print('YES' if $I_SPEND + 55.0 <= $ARM_CAP_MIN else 'NO')")"
if [ "$CAN_DUP" = "YES" ]; then
  note "A1WR_DUP_BEGIN alone-copy of cold alpha=4 (I), no other A1WR unit in flight (Addendum B 14.3)"
  launch_unit dup_I_4 I COLD "4" "1.0e-8" "$COLD_TMO" 8 3g 4000 || note "A1WR_WARN dup_I_4 failed to launch -- G-CONCURRENCY-BITS then has no alone-copy and SAYS SO"
  wait_all
else
  note "A1WR_DUP_CAPSTOP: I-arm spend $I_SPEND + 55 would exceed the $ARM_CAP_MIN cap; the duplicate is NOT run and G-CONCURRENCY-BITS reports its own absence. A cap-stop is NOT A RESULT on that control."
fi

# ============================= THE READER ====================================
python3 "$HERE/a1wr_read.py" "$RUN" I > "$RUN/A1WR_I_read_${STAMP}.txt" 2>&1; RI=$?
python3 "$HERE/a1wr_read.py" "$RUN" C > "$RUN/A1WR_C_read_${STAMP}.txt" 2>&1; RC2=$?
note "A1WR_READER rc_I=$RI rc_C=$RC2"

# ============================= COST + STATUS =================================
TOTAL="$(python3 -c "print(round($I_SPEND + $C_SPEND, 4))")"
{
  echo "item=A1WR stages=1+2 stamp=$STAMP"
  echo "spend_I_core_min=$I_SPEND cap_per_arm=$ARM_CAP_MIN"
  echo "spend_C_core_min=$C_SPEND cap_per_arm=$ARM_CAP_MIN"
  echo "spend_total_core_min=$TOTAL registered_estimate_stage2=867.4 (424.5+442.9, section 13.2) stage1_estimate=65"
  echo "cost_basis=anchors MEASURED (section 7.2); scaling EXTRAPOLATED; dollars DERIVED at c7a.4xlarge \$0.0513/core-h owner-stated, NOT measured"
  echo "calibration_row=OWED to docs/COST_CALIBRATION.md at grading (rule 12); wall times above carry live-box contention -- attributed there, never absorbed"
} > "$RUN/COST_STAGE12.txt"
echo "rc=0 phase=COMPLETE spend_I=$I_SPEND spend_C=$C_SPEND reader_rc=$RI/$RC2 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATUS"
note "A1WR_CHAIN_END total_core_min=$TOTAL"
exit 0
