#!/usr/bin/env bash
# =============================================================================
# AOA POLAR -- host-side arm driver. ONE script, two arms, selected by $1.
#
#   AOAI  incompressible  DASimpleFoam     U=10   nu=1.5e-5   Re ~ 6.67e5
#   AOAC  compressible    DARhoSimpleFoam  U=100  mu=1.8e-5   Re ~ 6.54e6  M ~ 0.288
#
# UNREGISTERED FEASIBILITY RUNG (prereg tag FEASIBILITY). ITS OUTPUTS ARE NEVER
# GRADEABLE AS VERDICTS: a 19-point polar on ONE 4,032-cell grid has NO GRID
# TRIPLE, so under Sanaa's convergence-prerequisite doctrine of 2026-09-01
# (etc/sessions/2026-09-01T1545Z...) it cannot be a graded result. Registering
# it gated would have contradicted that doctrine. A band attaches when the wing
# convergence ladder lands.
#
# PRIMAL ONLY. No adjoint, no optimiser, no FFD deformation, no CL trim.
# =============================================================================
set -uo pipefail

ARM="${1:-}"
HERE="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/feasibility_aoa_polar"

case "$ARM" in
  AOAI)
    ROOT="/home/ubuntu/certonomous-runs/CURRICULUM-AOAI-a1-naca0012-alpha-polar-incompressible"
    SRC_MESH="/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient/MESH"
    readonly RUNSCRIPT_SRC="$HERE/aoa_runScript_incomp.py"
    CPUSET="14"
    ;;
  AOAC)
    ROOT="/home/ubuntu/certonomous-runs/CURRICULUM-AOAC-a1-naca0012-alpha-polar-compressible"
    SRC_MESH="/home/ubuntu/certonomous-runs/CURRICULUM-D19M-a1-naca0012-subsonic-multipoint/MESH"
    readonly RUNSCRIPT_SRC="$HERE/aoa_runScript_comp.py"
    CPUSET="15"
    ;;
  *) echo "AOA_ABORT usage: aoa_run_arm.sh AOAI|AOAC"; exit 2 ;;
esac

# LITERAL script paths, set ONCE and NEVER reassigned from their own output.
# so1br_chain_driver.sh:83/:206 set a variable to a SCRIPT PATH then overwrote
# it with that script's OUTPUT, so the call worked exactly once and was
# guaranteed to fail on every later arm -- four hours of polling to a FALSE
# BLOCKED record.
readonly CMD_SRC="$HERE/aoa_cmd.sh"
readonly READER_SRC="$HERE/aoa_read.py"

IMG="dafoam/opt-packages:latest"
IMG_DIGEST="sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"
RANKS=1
MEM="4g"
CAP_CORE_MIN="20.0"
TMO=1200                # in-container deadline, s = cap*60/ranks. THIS is what
                        # actually stops the arm, and it survives host shell death.
STAGE1_TMO=800
COLD_TMO=100
MEM_FLOOR_KB=6291456    # 6.0 GiB. Anchors: D13 MEASURED 1.70 GiB peak RSS on THIS
                        # 4,032-cell case at np=1, and D12R2 MEASURED 1.3461 GiB.
                        # The LARGER, case-specific anchor governs; 4g container
                        # cap is 2.35x it. The inherited 20g is NOT used.
MEM_WAIT_BOUND_S=3600
MEM_POLL_S=30

# THE SWEEP. 19 points, 1 degree increment, alpha = 0..18 inclusive, ASCENDING.
ALPHAS="0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18"
# THE COLD CONTROLS. Re-run from freestream in their own tree.
#   4  -- low, inside the expected-attached range: makes the instrument check
#         interpretable, because both branches should converge and agree there.
#   14, 17 -- high, inside the range where the registered expectation is that
#         steady convergence may fail: this is where path dependence would bite.
COLD_ALPHAS="4 14 17"
DECLARED=19
NCOLD=3

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*"; }

say "AOA_DRIVER start arm=$ARM pid=$$ cpuset=$CPUSET ranks=$RANKS declared=$DECLARED cold=$NCOLD"
say "AOA_PREREG=FEASIBILITY -- UNREGISTERED rung; outputs NOT gradeable as verdicts"
say "AOA_NO_STALL_CLAIM: no output of this arm may report a stall angle derived from"
say "  convergence behaviour. The reader enforces this fail-closed at exit 2 (G-STALL)."

# --- G-ROOT ------------------------------------------------------------------
if [ -e "$ROOT" ]; then
  say "AOA_ABORT G-ROOT: run root already exists: $ROOT"; exit 6
fi

# --- G-SRC: every input asserted present AT THE POINT OF USE ------------------
for f in "$RUNSCRIPT_SRC" "$CMD_SRC" "$READER_SRC"; do
  test -f "$f" || { say "AOA_ABORT G-SRC instrument absent: $f"; exit 5; }
done
test -f "$SRC_MESH/constant/polyMesh/points.gz" || { say "AOA_ABORT G-SRC source mesh absent: $SRC_MESH"; exit 5; }
test -d "$SRC_MESH/0.orig" || { say "AOA_ABORT G-SRC 0.orig absent in source mesh"; exit 5; }
say "AOA_G_SRC_PASS all instruments and the source mesh present"

# --- G-PHYS: the compressible arm's physics block, asserted BEFORE launch -----
if [ "$ARM" = "AOAC" ]; then
  PHYS_OK="$(python3 - "$RUNSCRIPT_SRC" <<'PY'
import hashlib, sys
src = open(sys.argv[1]).read()
B = "# ---- D19M_PHYSICS_BEGIN ----\n"; E = "# ---- D19M_PHYSICS_END ----"
if src.count(B) != 1 or src.count(E) != 1:
    print("MARKERS"); raise SystemExit
print(hashlib.md5(src.split(B)[1].split(E)[0].strip().encode()).hexdigest())
PY
)"
  if [ "$PHYS_OK" != "c66504acc57bd9ef009599e883d2ef3b" ]; then
    say "AOA_ABORT G-PHYS physics block md5 '$PHYS_OK' != D19M's c66504acc57bd9ef009599e883d2ef3b"
    exit 9
  fi
  say "AOA_G_PHYS_PASS physics block is D19M's, byte-identical (md5 $PHYS_OK)"
fi

# --- G-IMG -------------------------------------------------------------------
GOT_DIGEST="$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}{{.Id}}' "$IMG" 2>/dev/null)"
test -n "$GOT_DIGEST" || { say "AOA_ABORT G-IMG image not present: $IMG"; exit 4; }
case "$GOT_DIGEST" in
  *9d45679d*) say "AOA_G_IMG_PASS $IMG carries the SHIPPED digest 9d45679d" ;;
  *) say "AOA_ABORT G-IMG digest mismatch: expected $IMG_DIGEST, inspect gave $GOT_DIGEST"; exit 4 ;;
esac

# --- G-CPUSET: refuse a collision with a LIVE container ----------------------
for c in $(sudo -n docker ps -q 2>/dev/null); do
  used="$(sudo -n docker inspect -f '{{.HostConfig.CpusetCpus}}' "$c" 2>/dev/null)"
  nm="$(sudo -n docker inspect -f '{{.Name}}' "$c" 2>/dev/null)"
  case ",$used," in
    *",$CPUSET,"*) say "AOA_ABORT G-CPUSET core $CPUSET already held by $nm (cpuset=$used)"; exit 3 ;;
  esac
done
say "AOA_G_CPUSET_PASS core $CPUSET free against every live container"

# --- WAIT ON THE TRANSIENT QUANTITY, BOUNDED, TERMINATING NON-ZERO -----------
# W3 put a ONE-SHOT BLOCK on the transient quantity and silently lost 20 of 33
# declared stages, while its own wait sat on a stable quantity that never
# failed. The wait belongs on the thing that actually moves, and running out of
# patience must be an ERROR, not a pass.
WAITED=0
while true; do
  AVAIL_KB="$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)"
  if [ -z "$AVAIL_KB" ]; then say "AOA_ABORT cannot read MemAvailable"; exit 7; fi
  if [ "$AVAIL_KB" -ge "$MEM_FLOOR_KB" ]; then
    say "AOA_MEM_OK avail_kb=$AVAIL_KB floor_kb=$MEM_FLOOR_KB waited_s=$WAITED"; break
  fi
  if [ "$WAITED" -ge "$MEM_WAIT_BOUND_S" ]; then
    say "AOA_ABORT MEM WAIT EXCEEDED bound_s=$MEM_WAIT_BOUND_S avail_kb=$AVAIL_KB floor_kb=$MEM_FLOOR_KB"
    exit 7
  fi
  say "AOA_MEM_WAIT avail_kb=$AVAIL_KB < floor_kb=$MEM_FLOOR_KB waited_s=$WAITED"
  sleep "$MEM_POLL_S"; WAITED=$((WAITED + MEM_POLL_S))
done

# --- STAGE: copy only. The source run root is NEVER written. -----------------
mkdir -p "$ROOT/case" "$ROOT/case_cold" "$ROOT/out" || { say "AOA_ABORT cannot create run root"; exit 8; }
cp -r "$SRC_MESH/." "$ROOT/case/"      || { say "AOA_ABORT staging copy failed"; exit 8; }
cp -r "$SRC_MESH/." "$ROOT/case_cold/" || { say "AOA_ABORT cold staging copy failed"; exit 8; }
cp "$RUNSCRIPT_SRC" "$ROOT/aoa_runScript.py" || { say "AOA_ABORT cannot stage runScript"; exit 8; }
cp "$CMD_SRC"       "$ROOT/aoa_cmd.sh"       || { say "AOA_ABORT cannot stage cmd"; exit 8; }
# Any solved state that rode along in the copy is removed, in BOTH trees.
rm -rf "$ROOT/case/0" "$ROOT/case_cold/0" 2>/dev/null
test -d "$ROOT/case/0.orig" || { say "AOA_ABORT staged tree has no 0.orig"; exit 8; }
test -d "$ROOT/case_cold/0.orig" || { say "AOA_ABORT staged cold tree has no 0.orig"; exit 8; }
say "AOA_STAGED root=$ROOT mesh_from=$SRC_MESH (source not written)"
say "AOA_MD5 runScript=$(md5sum "$ROOT/aoa_runScript.py" | cut -d' ' -f1) cmd=$(md5sum "$ROOT/aoa_cmd.sh" | cut -d' ' -f1)"

# --- LAUNCH: detached, no --rm, deadline INSIDE the container ---------------
NAME="aoa_${ARM}_${STAMP}_$$"
T0="$(date -u +%s)"
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus="$CPUSET" --memory=$MEM --memory-swap=$MEM \
    --oom-score-adj=500 \
    -e AOA_ALPHAS="$ALPHAS" \
    -e AOA_COLD_ALPHAS="$COLD_ALPHAS" \
    -e AOA_STAGE1_TMO="$STAGE1_TMO" \
    -e AOA_COLD_TMO="$COLD_TMO" \
    -e AOA_LEDGER="/mnt/out/LEDGER.tsv" \
    -v "$ROOT":/mnt -w /mnt "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && timeout -k 60 $TMO bash /mnt/aoa_cmd.sh" \
    > /dev/null 2>&1 \
  || { say "AOA_ABORT could not start container"; exit 4; }
say "AOA_LAUNCHED container=$NAME cpuset=$CPUSET mem=$MEM deadline_in_container_s=$TMO"

# --- POLL, then read rc from the KERNEL'S OWN RECORD -------------------------
while true; do
  RUNNING="$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)"
  [ "$RUNNING" = "true" ] || break
  sleep 5
done
RC="$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$NAME" 2>/dev/null)"
OOM="$(sudo -n docker inspect --format '{{.State.OOMKilled}}' "$NAME" 2>/dev/null)"
T1="$(date -u +%s)"; WALL=$((T1 - T0))
CORE_MIN="$(python3 -c "print(round($WALL*$RANKS/60.0, 4))")"
sudo -n docker logs "$NAME" > "$ROOT/ARM_${STAMP}.log" 2>&1

# EXECUTED counted from the container's OWN emitted markers, never assumed.
# `grep -c` prints 0 and EXITS 1 with no match; `|| echo 0` would append a
# second zero and make this a two-line string. `|| true` keeps grep's count.
EXECUTED="$(grep -c '^AOA_POINT_END ' "$ROOT/out/sweep.log" 2>/dev/null || true)"
COLDEXEC="$(grep -c '^AOA_COLD_END .* rc=0' "$ROOT/ARM_${STAMP}.log" 2>/dev/null || true)"
EXECUTED="${EXECUTED:-0}"; COLDEXEC="${COLDEXEC:-0}"

{
  echo "item=AOA arm=$ARM stamp=$STAMP container=$NAME"
  echo "rc=$RC source=docker_inspect_ExitCode oom_killed=$OOM"
  echo "wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP_CORE_MIN"
  echo "declared_points=$DECLARED executed_points=$EXECUTED"
  echo "cold_declared=$NCOLD cold_executed=$COLDEXEC"
  echo "alphas=[$ALPHAS]"
  echo "cold_alphas=[$COLD_ALPHAS]"
  echo "prereg=FEASIBILITY note=UNREGISTERED-rung-outputs-not-gradeable-as-verdicts"
  echo "no_stall_claim=ENFORCED-by-reader-G-STALL-exit-2"
} > "$ROOT/STATUS.$ARM"

say "AOA_COUNTS arm=$ARM declared=$DECLARED executed=$EXECUTED cold=$COLDEXEC/$NCOLD rc=$RC oom=$OOM wall_s=$WALL core_min=$CORE_MIN"

# The reader is invoked by LITERAL path and asserted present at the point of use.
test -f "$READER_SRC" || { say "AOA_ABORT reader absent at point of use: $READER_SRC"; exit 5; }
python3 "$READER_SRC" "$ROOT" > "$ROOT/AOA_${ARM}_read_${STAMP}.txt" 2>&1
RRC=$?
say "AOA_READER rc=$RRC out=$ROOT/AOA_${ARM}_read_${STAMP}.txt"
if [ "$RRC" -eq 2 ]; then
  say "AOA_READER_REFUSED rc=2 -- a control failed or G-STALL fired. NOT A RESULT."
fi

# --- No success token over a truncated program ------------------------------
if [ "$RC" = "0" ] && [ "$EXECUTED" -eq "$DECLARED" ] && [ "$COLDEXEC" -eq "$NCOLD" ] && [ "$RRC" -eq 0 ]; then
  say "AOA_ARM_COMPLETE arm=$ARM declared=$DECLARED executed=$EXECUTED cold=$COLDEXEC"
  exit 0
fi
say "AOA_ARM_INCOMPLETE arm=$ARM rc=$RC executed=$EXECUTED/$DECLARED cold=$COLDEXEC/$NCOLD reader_rc=$RRC -- NOT a completion"
exit 1
