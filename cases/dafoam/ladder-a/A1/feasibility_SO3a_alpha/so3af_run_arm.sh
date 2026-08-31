#!/usr/bin/env bash
# =============================================================================
# SO-3a ALPHA FEASIBILITY -- host-side arm driver.
#
# UNREGISTERED FEASIBILITY RUNG (prereg=FEASIBILITY, Sanaa 2026-08-31, ruling
# quoted at etc/sessions/2026-08-31T1513Z_sanaa_freeze_clock_and_so3_ruling.md:5
# -- "no freeze required for feasibility/physics rungs, never was").
# ITS OUTPUTS ARE NEVER GRADEABLE AS VERDICTS. It answers one physics question:
# do the three alphas SO-3a registered actually solve on this mesh, and is the
# top angle still attached?
#
# PRIMAL ONLY. No adjoint, no optimiser, no FFD deformation.
# =============================================================================
set -uo pipefail

ITEM="SO3aF"
HERE="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/feasibility_SO3a_alpha"
ROOT="/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility"
SRC_MESH="/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient/MESH"

# LITERAL script paths, set ONCE and NEVER reassigned from their own output.
# so1br_chain_driver.sh:83 and :206 set a variable to a SCRIPT PATH and then
# overwrote it with that script's OUTPUT, so the call worked exactly once and
# was guaranteed to fail on every later arm -- four hours of polling to a FALSE
# BLOCKED record. These three names are read-only after this point.
readonly RUNSCRIPT_SRC="$HERE/so3af_runScript.py"
readonly CMD_SRC="$HERE/so3af_cmd.sh"
readonly READER_SRC="$HERE/so3af_read.py"

IMG="dafoam/opt-packages:latest"
IMG_DIGEST="sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"
CPUSET="15"            # core 9 is SO1bR's registered placement and is unmovable.
RANKS=1
MEM="4g"
CAP_CORE_MIN="8.0"
TMO=480                # in-container deadline, s = cap*60/ranks. Survives host shell death.
MEM_FLOOR_KB=6291456   # 6.0 GiB, from D13's MEASURED 1.70 GiB peak RSS on this case + headroom
MEM_WAIT_BOUND_S=3600
MEM_POLL_S=30
ALPHAS="3.13918623195176 5.13918623195176 7.13918623195176"
DECLARED=3

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*"; }

say "SO3AF_DRIVER start item=$ITEM pid=$$ cpuset=$CPUSET ranks=$RANKS declared_alphas=$DECLARED"
say "SO3AF_PREREG=FEASIBILITY -- UNREGISTERED rung; outputs NOT gradeable as verdicts"

# --- G-ROOT: the run root must not already exist -------------------------
if [ -e "$ROOT" ]; then
  say "SO3AF_ABORT G-ROOT: run root already exists: $ROOT"
  exit 6
fi

# --- G-SRC: every input asserted present AT THE POINT OF USE --------------
for f in "$RUNSCRIPT_SRC" "$CMD_SRC" "$READER_SRC"; do
  test -f "$f" || { say "SO3AF_ABORT G-SRC instrument absent: $f"; exit 5; }
done
test -f "$SRC_MESH/constant/polyMesh/points.gz" || { say "SO3AF_ABORT G-SRC source mesh absent: $SRC_MESH"; exit 5; }
test -d "$SRC_MESH/0.orig" || { say "SO3AF_ABORT G-SRC 0.orig absent in source mesh"; exit 5; }
say "SO3AF_G_SRC_PASS all instruments and the source mesh present"

# --- G-IMG: the image exists and carries the digest we name ---------------
GOT_DIGEST="$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}{{.Id}}' "$IMG" 2>/dev/null)"
test -n "$GOT_DIGEST" || { say "SO3AF_ABORT G-IMG image not present: $IMG"; exit 4; }
case "$GOT_DIGEST" in
  *9d45679d*) say "SO3AF_G_IMG_PASS $IMG carries the SHIPPED digest 9d45679d" ;;
  *) say "SO3AF_ABORT G-IMG digest mismatch: expected $IMG_DIGEST, inspect gave $GOT_DIGEST"; exit 4 ;;
esac

# --- G-CPUSET: refuse a collision with a live container -------------------
for c in $(sudo -n docker ps -q 2>/dev/null); do
  used="$(sudo -n docker inspect -f '{{.HostConfig.CpusetCpus}}' "$c" 2>/dev/null)"
  nm="$(sudo -n docker inspect -f '{{.Name}}' "$c" 2>/dev/null)"
  case ",$used," in
    *",$CPUSET,"*) say "SO3AF_ABORT G-CPUSET core $CPUSET already held by $nm (cpuset=$used)"; exit 3 ;;
  esac
done
say "SO3AF_G_CPUSET_PASS core $CPUSET free against every live container"

# --- WAIT ON THE TRANSIENT QUANTITY, BOUNDED, TERMINATING NON-ZERO --------
# W3 put a ONE-SHOT BLOCK on the transient quantity and silently lost 20 of 33
# declared stages, while its own wait sat on a stable quantity that never
# failed. The wait belongs on the thing that actually moves -- live
# MemAvailable -- and running out of patience must be an ERROR, not a pass.
WAITED=0
while true; do
  AVAIL_KB="$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)"
  if [ -z "$AVAIL_KB" ]; then say "SO3AF_ABORT cannot read MemAvailable"; exit 7; fi
  if [ "$AVAIL_KB" -ge "$MEM_FLOOR_KB" ]; then
    say "SO3AF_MEM_OK avail_kb=$AVAIL_KB floor_kb=$MEM_FLOOR_KB waited_s=$WAITED"
    break
  fi
  if [ "$WAITED" -ge "$MEM_WAIT_BOUND_S" ]; then
    say "SO3AF_ABORT MEM WAIT EXCEEDED bound_s=$MEM_WAIT_BOUND_S avail_kb=$AVAIL_KB floor_kb=$MEM_FLOOR_KB"
    exit 7
  fi
  say "SO3AF_MEM_WAIT avail_kb=$AVAIL_KB < floor_kb=$MEM_FLOOR_KB waited_s=$WAITED"
  sleep "$MEM_POLL_S"; WAITED=$((WAITED + MEM_POLL_S))
done

# --- STAGE: copy only. The SO-2a run root is NEVER written. ---------------
mkdir -p "$ROOT/case" "$ROOT/out" || { say "SO3AF_ABORT cannot create run root"; exit 8; }
cp -r "$SRC_MESH/." "$ROOT/case/" || { say "SO3AF_ABORT staging copy failed"; exit 8; }
cp "$RUNSCRIPT_SRC" "$ROOT/so3af_runScript.py" || { say "SO3AF_ABORT cannot stage runScript"; exit 8; }
cp "$CMD_SRC"       "$ROOT/so3af_cmd.sh"       || { say "SO3AF_ABORT cannot stage cmd"; exit 8; }
# Remove any solved state that rode along in the copy, so every alpha is cold.
rm -rf "$ROOT/case/0" 2>/dev/null
test -d "$ROOT/case/0.orig" || { say "SO3AF_ABORT staged tree has no 0.orig"; exit 8; }
say "SO3AF_STAGED root=$ROOT mesh_from=$SRC_MESH (source not written)"
say "SO3AF_MD5 runScript=$(md5sum "$ROOT/so3af_runScript.py" | cut -d' ' -f1) cmd=$(md5sum "$ROOT/so3af_cmd.sh" | cut -d' ' -f1)"

# --- LAUNCH: detached, no --rm, deadline INSIDE the container -------------
NAME="so3af_ALPHA_${STAMP}_$$"
T0="$(date -u +%s)"
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus="$CPUSET" --memory=$MEM --memory-swap=$MEM \
    --oom-score-adj=500 \
    -e SO3AF_ALPHAS="$ALPHAS" \
    -v "$ROOT":/mnt -w /mnt "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && timeout -k 60 $TMO bash /mnt/so3af_cmd.sh" \
    > /dev/null 2>&1 \
  || { say "SO3AF_ABORT could not start container"; exit 4; }
say "SO3AF_LAUNCHED container=$NAME cpuset=$CPUSET mem=$MEM deadline_in_container_s=$TMO"

# --- POLL, then read rc from the KERNEL'S OWN RECORD ----------------------
while true; do
  RUNNING="$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)"
  [ "$RUNNING" = "true" ] || break
  sleep 5
done
RC="$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$NAME" 2>/dev/null)"
OOM="$(sudo -n docker inspect --format '{{.State.OOMKilled}}' "$NAME" 2>/dev/null)"
T1="$(date -u +%s)"; WALL=$((T1 - T0))
CORE_MIN="$(python3 -c "print(round($WALL*$RANKS/60.0, 4))")"
sudo -n docker logs "$NAME" > "$ROOT/ALPHA_${STAMP}.log" 2>&1

# EXECUTED is counted from the container's own emitted markers, never assumed.
# `grep -c` PRINTS 0 AND EXITS 1 when there is no match, so `|| echo 0` appends a
# SECOND zero and the variable becomes the two-line string "0\n0". That is what put
# a stray bare 0 on its own line in STATUS.SO3aF and in the driver's COUNTS line on
# the 20260831T161116Z run. `|| true` keeps grep's own count and drops the exit.
EXECUTED="$(grep -c '^SO3AF_ALPHA_END .* rc=0' "$ROOT/ALPHA_${STAMP}.log" 2>/dev/null || true)"
CONVERGED="$(grep -c '^SO3AF_ALPHA_CONVERGED ' "$ROOT/ALPHA_${STAMP}.log" 2>/dev/null || true)"
EXECUTED="${EXECUTED:-0}"; CONVERGED="${CONVERGED:-0}"

{
  echo "item=$ITEM stamp=$STAMP container=$NAME"
  echo "rc=$RC source=docker_inspect_ExitCode oom_killed=$OOM"
  echo "wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP_CORE_MIN"
  echo "declared_alphas=$DECLARED executed_alphas=$EXECUTED converged_alphas=$CONVERGED"
  echo "prereg=FEASIBILITY note=UNREGISTERED-rung-outputs-not-gradeable-as-verdicts"
} > "$ROOT/STATUS.$ITEM"

say "SO3AF_COUNTS declared=$DECLARED executed=$EXECUTED converged=$CONVERGED rc=$RC oom=$OOM wall_s=$WALL core_min=$CORE_MIN"

# The reader is invoked by LITERAL path and asserted present at the point of use.
test -f "$READER_SRC" || { say "SO3AF_ABORT reader absent at point of use: $READER_SRC"; exit 5; }
python3 "$READER_SRC" "$ROOT" > "$ROOT/SO3aF_read_${STAMP}.txt" 2>&1
say "SO3AF_READER rc=$? out=$ROOT/SO3aF_read_${STAMP}.txt"

# --- No success token over a truncated program ----------------------------
if [ "$RC" = "0" ] && [ "$EXECUTED" -eq "$DECLARED" ]; then
  say "SO3AF_ARM_COMPLETE declared=$DECLARED executed=$EXECUTED converged=$CONVERGED"
  exit 0
fi
say "SO3AF_ARM_INCOMPLETE rc=$RC declared=$DECLARED executed=$EXECUTED -- NOT a completion"
exit 1
