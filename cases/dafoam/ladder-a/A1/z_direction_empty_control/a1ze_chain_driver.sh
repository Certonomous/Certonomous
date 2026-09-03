#!/usr/bin/env bash
# =============================================================================
# A1ZE -- THE CHAIN DRIVER. ONE detached process, launched by the queue daemon
# (scripts/queue_runner.py); it outlives every agent and every session, per the
# detached-queue-runner ruling (Sanaa 2026-08-26). NO AGENT LAUNCHES IT.
#
# Governed by A1ZE_PREREGISTRATION.md, frozen at commit
# 03120e2244d52aee5dd79f7e0ea66b4b2940f7fd. This driver changes no gate, no
# threshold, no cap and no label; it executes them.
#
# FOUR ARMS, IN ORDER, IN THIS ONE PROCESS, STOPPING AT THE FIRST NON-ZERO rc:
#     Sc (coarse symmetry, control)  -> Ec (coarse empty, treatment)
#     S3 (L3 symmetry, control)      -> E3 (L3 empty, treatment)
# The coarse pair runs FIRST and is minutes: if the mechanism gates are going to
# resolve, they resolve cheaply, and a defect surfaces before 512 core-min of L3
# is committed. No wait-wrapper, no per-arm queue entries (the W2R lesson).
#
# EVERY rc IS CAPTURED INSIDE THE THING THAT PRODUCED IT: the container writes
# /mnt/out/rc.txt itself (a1ze_cmd.sh), and this driver reads the exit code from
# `docker inspect` BEFORE `docker rm`. Nothing here infers an rc from a wrapper:
# `setsid timeout cmd` exits 0 for every outcome, which is how a dead run has
# been reported alive before.
#
# WHAT STOPS THIS RUN, STRUCTURALLY (Sanaa 2026-09-03 ~21:00Z: something must be
# guaranteed to stop a run, and it should be a ceiling far above the estimate,
# not the estimate itself):
#   1. the per-arm TMO, INSIDE the container, so it survives the death of this
#      driver, of the daemon and of every agent;
#   2. the 370.0 core-min ITEM CEILING, checked BEFORE every arm. It sits below
#      the 532.0 cap sum by design, so the ceiling binds first.
#
# WHAT DOES NOT STOP THIS RUN: occupancy and memory. G-OCC QUEUES, IT NEVER
# REFUSES (Sanaa ~21:00Z "queue, don't launch -- queueing is not blocking";
# ~22:00Z "box should never be idle"). d19t_run_arm.sh's G-QUIET refuse-to-launch
# form is ruled out of this family and is NOT reproduced here.
# =============================================================================
set -uo pipefail

HERE="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/z_direction_empty_control"
REPO="/home/ubuntu/Certonomous"
ROOT="/home/ubuntu/certonomous-runs/A1ZE"
PREREG_COMMIT="03120e2244d52aee5dd79f7e0ea66b4b2940f7fd"

IMG="dafoam-idwarp-rot:v1"
IMG_DIGEST_WANT="2927768a16ac"

ITEM_CEILING_MIN=370.0
CAP_MARGIN_S=60
# arm : cap_core_min : tmo_s : ranks : alpha : planes : pair : cpuset
ARMS=(
  "Sc:9.0:480:1:4.0:symmetry:coarse:10"
  "Ec:9.0:480:1:4.0:empty:coarse:10"
  "S3:257.0:15360:1:12.0:symmetry:L3:11"
  "E3:257.0:15360:1:12.0:empty:L3:11"
)
ITERS=2000
# 4 GiB, NOT 3. Justified in A1ZE_PREREGISTRATION.md: peak RSS is UNMEASURED on
# this case family; what IS measured is A1WR's six COLD units running the same
# 130,304-cell L3 mesh at --memory=3g to iteration 1800 with OOMKilled=false on
# every row (CHAIN_LEDGER.tsv), and its two probes at --memory=4g, also
# OOMKilled=false. A non-OOM observation is an upper bound not reached, not a
# peak. 4g is the conservative size and is labelled a size, not a measurement.
MEM="4g"
MEM_FLOOR_KB=4194304

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
STATUS="$HERE/STATUS.A1ZE_chain"
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*"; }
note() { say "$*" >> "$STATUS.log"; say "$*"; }
fin() { echo "rc=$1 phase=$2 spend_core_min=${SPEND:-0} utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) pid=$$" > "$STATUS"; exit "$1"; }

SPEND=0
: > "$STATUS.log"
note "A1ZE_CHAIN_BEGIN stamp=$STAMP pid=$$ img=$IMG prereg=$PREREG_COMMIT"

# --- G-ROOT: asserted BY EXECUTION. This item runs once. ---------------------
if [ -e "$ROOT" ]; then
  note "A1ZE_ABORT G-ROOT: run root already exists: $ROOT"
  fin 6 G-ROOT
fi
note "A1ZE_ROOT_ABSENT_ASSERTED $ROOT does not exist"
mkdir -p "$ROOT" || fin 6 G-ROOT
LEDGER="$ROOT/ledger.txt"
{ echo "ITEM=A1ZE"; echo "PREREG_COMMIT=$PREREG_COMMIT"; echo "IMAGE=$IMG";
  echo "STAMP=$STAMP"; echo "ITEM_CEILING_CORE_MIN=$ITEM_CEILING_MIN"; } > "$LEDGER"

# --- G-FREEZE: the frozen files are the files that run -----------------------
for f in A1ZE_PREREGISTRATION.md a1ze_grade.py a1ze_stage.py a1ze_cmd.sh \
         a1ze_runScript.py A1ZE_INSTRUMENT_MD5.txt; do
  test -f "$HERE/$f" || { note "A1ZE_ABORT G-SRC instrument absent: $f"; fin 5 G-SRC; }
done
( cd "$HERE" && md5sum -c A1ZE_INSTRUMENT_MD5.txt --quiet ) \
  || { note "A1ZE_ABORT G-FREEZE: an instrument drifted from its frozen md5"; fin 4 G-FREEZE; }
# Rule 6, EXECUTED rather than asserted in prose: the registration carries a
# dated ADDENDUM appended at its foot, so the whole file is no longer the frozen
# blob -- but the FROZEN PORTION must still be byte-identical to it. That is
# exactly what "lines whose number changed above this section: 0" claims, and
# this is the check that proves the claim instead of believing it.
PREREG_REL="cases/dafoam/ladder-a/A1/z_direction_empty_control/A1ZE_PREREGISTRATION.md"
FROZEN_LINES=731
git -C "$REPO" show "$PREREG_COMMIT:$PREREG_REL" > "$ROOT/.prereg_frozen" 2>/dev/null \
  || { note "A1ZE_ABORT G-FREEZE cannot read the frozen blob at $PREREG_COMMIT"; fin 4 G-FREEZE; }
[ "$(wc -l < "$ROOT/.prereg_frozen")" = "$FROZEN_LINES" ] \
  || { note "A1ZE_ABORT G-FREEZE frozen blob is not $FROZEN_LINES lines"; fin 4 G-FREEZE; }
head -n "$FROZEN_LINES" "$HERE/A1ZE_PREREGISTRATION.md" > "$ROOT/.prereg_head"
cmp -s "$ROOT/.prereg_frozen" "$ROOT/.prereg_head" \
  || { note "A1ZE_ABORT G-FREEZE the FROZEN PORTION of the registration was edited -- rule 6"; fin 4 G-FREEZE; }
rm -f "$ROOT/.prereg_frozen" "$ROOT/.prereg_head"
note "A1ZE_G_FREEZE_PASS instruments match their pins; the registration's first $FROZEN_LINES lines are byte-identical to the blob at $PREREG_COMMIT (rule 6, executed)"

# --- the grader's own controls must be born BEFORE any compute is spent ------
python3 "$HERE/a1ze_grade.py" --selftest > "$ROOT/grader_selftest.out" 2>&1 \
  || { note "A1ZE_ABORT G-CONTROLS the frozen grader refused its own selftest"; fin 3 G-CONTROLS; }
note "A1ZE_G_CONTROLS_PASS $(grep -c '^CONTROL ' "$ROOT/grader_selftest.out") controls born, rc 0"

# --- G-IMG: the image, by digest --------------------------------------------
GOT="$(sudo -n docker image inspect --format '{{.Id}}' "$IMG" 2>/dev/null)"
case "$GOT" in
  *${IMG_DIGEST_WANT}*) note "A1ZE_G_IMG_PASS $IMG carries $IMG_DIGEST_WANT ($GOT)" ;;
  *) note "A1ZE_ABORT G-IMG $IMG id '$GOT' does not carry $IMG_DIGEST_WANT"; fin 4 G-IMG ;;
esac

# --- G-OCC: QUEUES, NEVER REFUSES -------------------------------------------
# Records occupancy and MemAvailable, then WAITS -- it never returns a refusal
# and never consumes the entry. Registration section 7.
occ_wait() {
  local waited=0 kb n la
  while true; do
    kb="$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)"
    [ -n "$kb" ] || { note "A1ZE_OCC cannot read MemAvailable -- waiting, not refusing"; sleep 30; waited=$((waited+30)); continue; }
    n="$(sudo -n docker ps -q 2>/dev/null | wc -l)"
    la="$(cut -d' ' -f1-3 /proc/loadavg)"
    if [ "$kb" -ge "$MEM_FLOOR_KB" ]; then
      note "A1ZE_OCC_LAUNCH arm=$1 containers=$n memavail_kb=$kb loadavg=$la waited_s=$waited"
      echo "OCC arm=$1 containers=$n memavail_kb=$kb loadavg=$la waited_s=$waited decision=LAUNCH" >> "$LEDGER"
      return 0
    fi
    if [ $((waited % 600)) -eq 0 ]; then
      note "A1ZE_OCC_QUEUE arm=$1 containers=$n memavail_kb=$kb (floor $MEM_FLOOR_KB) loadavg=$la waited_s=$waited -- QUEUED, still scheduled, NOT refused"
      echo "OCC arm=$1 containers=$n memavail_kb=$kb loadavg=$la waited_s=$waited decision=QUEUE" >> "$LEDGER"
    fi
    sleep 30; waited=$((waited+30))
  done
}

run_arm() {  # run_arm ARM CAP TMO RANKS ALPHA PLANES CPUSET
  local arm="$1" cap="$2" tmo="$3" ranks="$4" alpha="$5" planes="$6" cpu="$7"
  local u="$ROOT/$arm" cn="a1ze_${arm}_${STAMP}_$$"

  # G-CEIL, BEFORE the arm, on the cumulative spend. The structural stop.
  local over; over="$(python3 -c "print(1 if $SPEND >= $ITEM_CEILING_MIN else 0)")"
  if [ "$over" = "1" ]; then
    note "A1ZE_CEILING_STOP spend $SPEND core-min reached the item ceiling $ITEM_CEILING_MIN before arm $arm"
    echo "CEILING_STOP before=$arm spend_core_min=$SPEND ceiling=$ITEM_CEILING_MIN" >> "$LEDGER"
    return 70
  fi
  # G-BUDGET, re-derived here from the registered cap rather than trusted:
  # TMO = int(CAP*60/RANKS) - CAP_MARGIN_S, guard TMO > 0 and the exact back-check.
  local want back
  want="$(python3 -c "print(int($cap*60/$ranks) - $CAP_MARGIN_S)")"
  [ "$want" = "$tmo" ] || { note "A1ZE_ABORT G-BUDGET arm=$arm TMO $tmo != identity $want"; return 71; }
  [ "$tmo" -gt 0 ] || { note "A1ZE_ABORT G-BUDGET arm=$arm TMO $tmo <= 0 -- the D19T identity"; return 71; }
  back="$(python3 -c "print(round(($tmo + $CAP_MARGIN_S)*$ranks/60.0, 6))")"
  [ "$back" = "$(python3 -c "print(round(float($cap),6))")" ] \
    || { note "A1ZE_ABORT G-BUDGET arm=$arm back-check $back != cap $cap"; return 71; }
  note "A1ZE_G_BUDGET_PASS arm=$arm cap=$cap ranks=$ranks TMO=${tmo}s back-check=$back"

  occ_wait "$arm"

  local t0 la; t0="$(date -u +%s)"; la="$(cut -d' ' -f1-3 /proc/loadavg)"
  local mavail; mavail="$(python3 -c "print(round($(awk '/^MemAvailable:/{print $2}' /proc/meminfo)/1048576.0,4))")"
  sudo -n docker run -d --name "$cn" \
      --user 0:0 --cpus=1 --cpuset-cpus="$cpu" --memory="$MEM" --memory-swap="$MEM" \
      --oom-score-adj=500 \
      -e OMP_NUM_THREADS=1 \
      -e A1ZE_ARM="$arm" -e A1ZE_ALPHA="$alpha" -e A1ZE_PLANES="$planes" \
      -e A1ZE_ITERS="$ITERS" -e A1ZE_TMO="$tmo" \
      -v "$u":/mnt -w /mnt/case "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && bash /mnt/a1ze_cmd.sh" \
      > /dev/null 2>&1 \
    || { note "A1ZE_ABORT could not start container for $arm"; return 72; }
  note "A1ZE_LAUNCHED arm=$arm planes=$planes alpha=$alpha cpuset=$cpu mem=$MEM tmo_s=$tmo omp=1 loadavg=$la"

  while [ "$(sudo -n docker inspect --format '{{.State.Running}}' "$cn" 2>/dev/null)" = "true" ]; do
    sleep 20
  done
  # docker inspect BEFORE docker rm -- the exit code and the OOM flag do not
  # survive the removal, and a lost inspect is how an OOM has been read as a
  # clean exit before.
  local rc oom t1 wall cm
  rc="$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$cn" 2>/dev/null)"
  oom="$(sudo -n docker inspect --format '{{.State.OOMKilled}}' "$cn" 2>/dev/null)"
  t1="$(date -u +%s)"; wall=$((t1 - t0))
  cm="$(python3 -c "print(round($wall*$ranks/60.0, 4))")"
  mkdir -p "$ROOT/logs"
  sudo -n docker logs "$cn" > "$ROOT/logs/${arm}_${STAMP}.log" 2>&1
  sudo -n docker rm "$cn" > /dev/null 2>&1
  SPEND="$(python3 -c "print(round($SPEND + $cm, 4))")"
  printf 'STAGE=%s TASK=run_arm rc=%s wall_s=%s ranks=%s core_min=%s memavail_GiB=%s inspect=[%s|%s] log=%s\n' \
    "$arm" "$rc" "$wall" "$ranks" "$cm" "$mavail" "$rc" "$oom" "${arm}_${STAMP}.log" >> "$LEDGER"
  echo "SPENT_CORE_MIN=$SPEND of ceiling $ITEM_CEILING_MIN" >> "$LEDGER"

  # The in-container rc is the physics-critical one. The docker exit code is
  # infrastructure. Bookkeeping never voids physics -- but a MISSING in-container
  # rc is not bookkeeping, it means the unit program never reached its own end.
  local irc="ABSENT"
  [ -f "$u/out/rc.txt" ] && irc="$(tr -d '[:space:]' < "$u/out/rc.txt")"
  note "A1ZE_ARM_DONE arm=$arm docker_rc=$rc in_container_rc=$irc oom=$oom wall_s=$wall core_min=$cm cumulative=$SPEND"
  if [ "$cm" != "0" ] && [ "$(python3 -c "print(1 if $cm > $cap else 0)")" = "1" ]; then
    note "A1ZE_G_CAP_EXCEEDED arm=$arm $cm core-min over cap $cap -- recorded for the grader, which judges it"
    echo "G_CAP_EXCEEDED arm=$arm core_min=$cm cap=$cap" >> "$LEDGER"
  fi
  [ "$irc" = "0" ] || return 73
  [ "$rc" = "0" ]  || return 73
  return 0
}

# ============================= THE CHAIN =====================================
for pair in coarse L3; do
  note "A1ZE_STAGE_BEGIN pair=$pair -- staging BOTH arms in ONE invocation from the SAME sources"
  python3 "$HERE/a1ze_stage.py" --pair "$pair" --run-root "$ROOT" --repo "$REPO" \
      >> "$STATUS.log" 2>&1 \
    || { note "A1ZE_ABORT staging/one-variable assert REFUSED for pair=$pair"; fin 7 G-ONEVAR; }
  note "A1ZE_ONE_VARIABLE_PASS pair=$pair (see $STATUS.log for the file-by-file manifest)"

  for spec in "${ARMS[@]}"; do
    IFS=':' read -r a cap tmo ranks alpha planes apair cpu <<< "$spec"
    [ "$apair" = "$pair" ] || continue
    note "A1ZE_ARM_BEGIN $a planes=$planes alpha=$alpha cap=$cap TMO=${tmo}s"
    run_arm "$a" "$cap" "$tmo" "$ranks" "$alpha" "$planes" "$cpu"
    ARC=$?
    if [ "$ARC" != "0" ]; then
      note "A1ZE_CHAIN_STOP at arm $a rc=$ARC -- the chain stops at the first non-zero rc and grades what exists"
      python3 "$HERE/a1ze_grade.py" --root "$ROOT" > "$ROOT/A1ZE_grade_${STAMP}.out" 2>&1
      note "A1ZE_GRADED partial -> $ROOT/A1ZE_grade_${STAMP}.out"
      fin "$ARC" "ARM-$a"
    fi
  done
done

note "A1ZE_ALL_ARMS_COMPLETE spend=$SPEND core-min of ceiling $ITEM_CEILING_MIN"
python3 "$HERE/a1ze_grade.py" --root "$ROOT" > "$ROOT/A1ZE_grade_${STAMP}.out" 2>&1
GRC=$?
note "A1ZE_GRADED rc=$GRC -> $ROOT/A1ZE_grade_${STAMP}.out"
grep -E '^A1ZE_VERDICT' "$ROOT/A1ZE_grade_${STAMP}.out" | while read -r l; do note "$l"; done
fin 0 COMPLETE
