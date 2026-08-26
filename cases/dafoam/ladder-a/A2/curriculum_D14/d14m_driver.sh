#!/usr/bin/env bash
# =============================================================================
# CURRICULUM D14-M -- pyHyp MESH REGENERATION of the MACH wing (D4's mesh), the first
# registered rung of curriculum row D14.  DETACHED DRIVER + LAUNCHER in one file.
# Started by the queue runner (or by hand) as:  bash d14m_driver.sh MESH
# from the CASE directory (never the run root, G-ROOT.5 b).  Family: D4-SHIPPED
# Addendum 2 (8b91be2b) -- G-ROOT.1-.5 from birth, windowed H5, aggregate memory
# wait-and-retry, explicit cpuset, `docker run -d` with NO --rm, the deadline INSIDE
# the container, rc from `docker inspect .State.ExitCode` written into STATUS.MESH by
# this driver (never the $? of a setsid/timeout line), one ledger row, then the frozen
# comparator run on the artifacts.  No `assert` (L-332).  Permission: bc0e687e.
#
# ORDER OF GUARDS, all before a single core-second is spent:
#   G-ROOT.1  BASE is this item's registered run root (normalised)
#   G-ROOT.2  BASE resolves to no other item's root (named list)
#   A5        the run root does not already exist (a bought arm is never re-staged)
#   G-ROOT.3  (if a ledger exists) it carries ITEM=CURRICULUM-D14M
#   G-ROOT.4  no ARM=MESH rc=0 ledger row (ALREADY_BOUGHT)
#   G-ROOT.5  no RUNNING container with prefix d14m_; no live driver pidfile holding the root
#   G14-0     THE NAMED CONTAMINANT CHECK (d14m_contaminant_check.py, rc 2 refuses)
#   instrument md5s, image digest, H5 window, aggregate wait-and-retry
# D14M_SELFTEST_ROOT=<dir>: guards run against that sacrificial root with a BOGUS image
# name and the driver exits 40 after the guard block -- no staging, no container.
# =============================================================================
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ITEM="CURRICULUM-D14M"
BASE_REGISTERED="/home/ubuntu/certonomous-runs/CURRICULUM-D14M-a2-wing-remesh"
REF="/home/ubuntu/certonomous-runs/A2-mach-wing"                 # D4's baseline mesh and its generator inputs
TUT="/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing"          # system/ and constant/ dictionaries
IMG="dafoam/opt-packages:latest"
ID_EXPECT="sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"   # SHIPPED row, DAFOAM_CHARTER 6/11
PREFIX="d14m_"
CPUSET="14"; MEM="4g"; TMO=900                                    # registered: cpu 14, 4 GiB, 900 s deadline INSIDE the container
CAP_CORE_MIN="15.0"; CEILING_CORE_MIN="30.0"                       # report-only guards (COMPUTE_BUDGET_CHARTER); TMO is what stops it
H5_FLOOR_GIB=14.0; H5_SAMPLES=45; H5_WINDOW_S=60; AGG_CEILING_GIB=30.6; AGG_BOUND_S=14400
MD5_TARBALL="92956aa0e4cb9b17fa063bd95e8f78ba"                     # mdolab_wing_surface_mesh.cgns.tar.gz
MD5_GEN="dab5e959187ab2e2bfb4e2c0ded0feb6"                         # genWingMesh.py (D4's generator, byte-identical to the tutorial's)
MD5_CONTAM="28ce514d6683948f0883e4a5278c7f5a"; MD5_GRADER="c2a8cadb3d7863697412e6741cdea51e"; MD5_AGG="709ab0b98ef0302a3a3a318588f9493f"   # filled at freeze (see PREREGISTRATION.md section 4)
PERMISSION=bc0e687e
ARM="${1:-}"
[ "$ARM" = "MESH" ] || { echo "ABORT usage: d14m_driver.sh MESH"; exit 64; }
SELFTEST_ROOT="${D14M_SELFTEST_ROOT:-}"
if [ -n "$SELFTEST_ROOT" ]; then BASE="$SELFTEST_ROOT"; IMG="no-such-image:d14m-selftest"; else BASE="$BASE_REGISTERED"; fi
utc () { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd "$HERE" || exit 4
echo "D14M_DRIVER start=$(utc) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ') cwd=$(pwd) arm=$ARM base=$BASE selftest=${SELFTEST_ROOT:+yes} permission=$PERMISSION"

# ---- G-ROOT.1
NB=$(realpath -m "$BASE")
if [ -z "$SELFTEST_ROOT" ]; then
  [ "$NB" = "$BASE_REGISTERED" ] || { echo "ABORT G-ROOT.1 BASE $NB is not this item's registered run root $BASE_REGISTERED"; exit 3; }
else
  case "$NB" in /home/ubuntu/certonomous-runs/_d14m_selftest_*) ;; *) echo "ABORT G-ROOT.1 selftest root must be a sacrificial _d14m_selftest_* root: $NB"; exit 3;; esac
fi
echo "D14M_G_ROOT1_PASS base=$NB"
# ---- G-ROOT.2 -- the roots this file must never write
for forb in "$REF" /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin /home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin \
            /home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd /home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady \
            /home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady /home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2-cylinder-unsteady \
            /home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady "$TUT" /home/ubuntu/certonomous-runs /home/ubuntu/Certonomous "$HERE"; do
  [ "$NB" = "$(realpath -m "$forb")" ] && { echo "ABORT G-ROOT.2 BASE resolves to ANOTHER ITEM'S ROOT: $forb"; exit 3; }
done
echo "D14M_G_ROOT2_PASS"
# ---- A5 / G-ROOT.3 / G-ROOT.4
if [ -z "$SELFTEST_ROOT" ] && [ -e "$BASE" ]; then
  if [ -f "$BASE/ledger.txt" ]; then
    FI=$(grep -m1 '^ITEM=' "$BASE/ledger.txt" | cut -d= -f2)
    [ "$FI" = "$ITEM" ] || { echo "ABORT G-ROOT.3 the ledger at $BASE carries another item: $FI"; exit 3; }
    grep -aEq "^ARM=MESH( .*)? rc=0 " "$BASE/ledger.txt" && { echo "ABORT G-ROOT.4 ALREADY_BOUGHT: ARM=MESH rc=0 row exists; a second record for one run is the defect"; exit 3; }
  fi
  echo "REFUSE A5: run root already exists: $BASE -- a completed or partial arm is not deleted to re-run it. Inspect it, do not clear it."; exit 6
fi
if [ -n "$SELFTEST_ROOT" ] && [ -f "$BASE/ledger.txt" ]; then
  FI=$(grep -m1 '^ITEM=' "$BASE/ledger.txt" | cut -d= -f2)
  [ "$FI" = "$ITEM" ] || { echo "ABORT G-ROOT.3 the ledger at $BASE carries another item: $FI"; exit 3; }
  grep -aEq "^ARM=MESH( .*)? rc=0 " "$BASE/ledger.txt" && { echo "ABORT G-ROOT.4 ALREADY_BOUGHT: ARM=MESH rc=0 row exists; a second record for one run is the defect"; exit 3; }
fi
echo "D14M_G_ROOT3_4_PASS"
# ---- G-ROOT.5
LIVE=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep "^$PREFIX" | head -3 | tr '\n' ',' | sed 's/,$//')
[ -n "$LIVE" ] && { echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix: [$LIVE]. REFUSED."; exit 3; }
PIDFILE="$BASE/d14m_driver.pid"
if [ -f "$PIDFILE" ]; then
  DPID=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$DPID" ] && kill -0 "$DPID" 2>/dev/null; then
    ANCESTOR=no; p=$$
    for _ in $(seq 1 64); do [ "$p" = "$DPID" ] && { ANCESTOR=yes; break; }; p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' '); { [ -z "$p" ] || [ "$p" = "0" ]; } && break; done
    DCWD=$(readlink -f "/proc/$DPID/cwd" 2>/dev/null)
    if [ "$ANCESTOR" = "no" ] || [ "$DCWD" = "$NB" ]; then echo "ABORT G-ROOT.5 driver pidfile $PIDFILE names LIVE pid $DPID (ancestor=$ANCESTOR cwd=$DCWD). REFUSED."; exit 3; fi
  fi
fi
echo "D14M_G_ROOT5_PASS live_prefix_containers=none driver_pidfile=$([ -f "$PIDFILE" ] && echo present_stale_or_ancestor || echo absent)"
# ---- G14-0 THE NAMED CONTAMINANT CHECK, on the generator FILE that will be staged
python3 "$HERE/d14m_contaminant_check.py" "$REF/genWingMesh.py" --json "$HERE/G14-0_$(date -u +%Y%m%dT%H%M%SZ).json"; crc=$?
[ "$crc" -eq 0 ] || { echo "ABORT G14-0 contaminant check refused (rc=$crc). NOTHING LAUNCHED."; exit 2; }
python3 "$HERE/d14m_contaminant_check.py" "$REF/genWingMesh.py" --plant > /dev/null; prc=$?
[ "$prc" -eq 0 ] || { echo "ABORT G14-0 planted control did not fire (rc=$prc); a gate not shown able to refuse is ceremony. NOTHING LAUNCHED."; exit 2; }
echo "D14M_G14_0_PASS planted_control=fired"
# ---- instruments and inputs, by md5
for pair in "$MD5_TARBALL $REF/mdolab_wing_surface_mesh.cgns.tar.gz" "$MD5_GEN $REF/genWingMesh.py" "$MD5_CONTAM $HERE/d14m_contaminant_check.py" "$MD5_GRADER $HERE/d14m_grade.py" "$MD5_AGG $HERE/d14m_aggregate_memory.py"; do
  echo "$pair" | md5sum -c --quiet - 2>/dev/null || { echo "ABORT instrument/input md5 drifted: $pair"; exit 4; }
done
echo "D14M_MD5_PASS"
if [ -n "$SELFTEST_ROOT" ]; then echo "D14M_SELFTEST_GUARDS_PASSED (no staging, no container; bogus image $IMG)"; exit 40; fi
# ---- image identity = digest (DAFOAM_CHARTER 6/11)
GOT_ID=$(sudo -n docker image inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
[ "$GOT_ID" = "$ID_EXPECT" ] || { echo "ABORT image id '$GOT_ID' != registered '$ID_EXPECT'"; exit 4; }
# ---- H5 window
mem_gib () { awk '/MemAvailable/{printf "%.2f", $2/1048576}' /proc/meminfo; }
STEP=$(python3 -c "print('%.3f' % ($H5_WINDOW_S/float($H5_SAMPLES)))"); BELOW=0; N=0; MIN=999; MAXV=0
mkdir -p "$BASE" || exit 4; chmod 777 "$BASE"; H5_FILE="$BASE/MESH_h5_window_$(date -u +%Y%m%dT%H%M%SZ).txt"
for _ in $(seq 1 $H5_SAMPLES); do s=$(mem_gib); N=$((N+1)); echo "$(date -u +%s) $s" >> "$H5_FILE"; MIN=$(python3 -c "print(min($MIN,$s))"); MAXV=$(python3 -c "print(max($MAXV,$s))"); [ "$(python3 -c "print(1 if $s < $H5_FLOOR_GIB else 0)")" = "1" ] && BELOW=$((BELOW+1)); sleep "$STEP"; done
echo "D14M_H5_WINDOW n=$N floor_GiB=$H5_FLOOR_GIB min_GiB=$MIN max_GiB=$MAXV below=$BELOW"
STATUS="$BASE/STATUS.MESH"; echo "preflight stamp=$(date -u +%Y%m%dT%H%M%SZ) driver_pid=$$ permission=$PERMISSION" > "$STATUS"
if [ "$BELOW" -gt 0 ] || [ "$N" -ne "$H5_SAMPLES" ]; then echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) note=H5_REFUSED below=$BELOW min_GiB=$MIN" >> "$STATUS"; echo "ABORT H5 $BELOW of $N samples below $H5_FLOOR_GIB GiB. REFUSED."; exit 6; fi
# ---- aggregate wait-and-retry
echo "$$" > "$PIDFILE"; trap 'rm -f "$PIDFILE"' EXIT
WAITED=0; AGG_SERIES="$BASE/MESH_aggregate_series.txt"
while true; do
  AGG=$(python3 "$HERE/d14m_aggregate_memory.py" 4 "$AGG_CEILING_GIB"); echo "$(date -u +%s) $AGG" >> "$AGG_SERIES"
  [ "$(printf '%s' "$AGG" | python3 -c "import sys,json; print(1 if json.load(sys.stdin).get('ok') else 0)")" = "1" ] && break
  if [ "$WAITED" -ge "$AGG_BOUND_S" ]; then echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) note=AGGREGATE_BLOCKED_AT_BOUND waited=$WAITED" >> "$STATUS"; echo "ABORT AGGREGATE still over $AGG_CEILING_GIB GiB after ${WAITED}s. BLOCKED."; exit 6; fi
  echo "AGGREGATE_WAIT waited=$WAITED stamp=$(date -u +%Y%m%dT%H%M%SZ) $AGG" >> "$STATUS"; sleep 30; WAITED=$((WAITED+30))
done
echo "D14M_AGGREGATE waited=$WAITED $AGG"
# ---- stage inputs (copies only; REF is never written)
W="$BASE/MESH"; mkdir -p "$W" || exit 4
cp -a "$REF/mdolab_wing_surface_mesh.cgns.tar.gz" "$REF/genWingMesh.py" "$W/" && cp -a "$TUT/system" "$TUT/constant" "$W/" || { echo "ABORT staging copy"; exit 4; }
rm -rf "$W/constant/polyMesh" 2>/dev/null
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$; NAME="${PREFIX}MESH_${STAMP}"; LEDGER="$BASE/ledger.txt"
{ echo "ITEM=$ITEM"; echo "ARM_PLAN=MESH"; echo "IMAGE=$IMG"; echo "IMAGE_ID=$GOT_ID"; echo "CPUSET=$CPUSET MEM=$MEM TMO_IN_CONTAINER_S=$TMO CAP_CORE_MIN=$CAP_CORE_MIN CEILING_CORE_MIN=$CEILING_CORE_MIN";
  echo "INPUT_TARBALL_MD5=$MD5_TARBALL GEN_MD5=$MD5_GEN"; echo "REF_BASELINE=$REF/checkMesh.log"; echo "STAMP=$STAMP STARTED_UTC=$(utc) permission=$PERMISSION"; } >> "$LEDGER"
cat > "$W/d14m_cmd.sh" <<'EOF'
set -uo pipefail; cd /mnt/MESH
t () { echo "D14M_T $1 $(date -u +%s)"; }
t begin
tar xzf mdolab_wing_surface_mesh.cgns.tar.gz || exit 11
md5sum mdolab_wing_surface_mesh.cgns
cgns_utils coarsen mdolab_wing_surface_mesh.cgns surfaceMesh.cgns > logCoarsen.txt 2>&1 || exit 12
t coarsen_done
python genWingMesh.py > logMeshGeneration.txt 2>&1 || exit 13
t pyhyp_done
plot3dToFoam -noBlank volumeMesh.xyz >> logMeshGeneration.txt 2>&1 || exit 14
autoPatch 60 -overwrite >> logMeshGeneration.txt 2>&1 || exit 15
createPatch -overwrite >> logMeshGeneration.txt 2>&1 || exit 16
renumberMesh -overwrite >> logMeshGeneration.txt 2>&1 || exit 17
t foam_utils_done
checkMesh > checkMesh.log 2>&1; echo "D14M_CHECKMESH_RC $?"
checkMesh -allGeometry -allTopology > checkMesh_allGeometry.log 2>&1; echo "D14M_CHECKMESH_ALLGEOMETRY_RC $?"
t checkmesh_done
sha256sum constant/polyMesh/points* 2>/dev/null
echo "D14M_CMD_END rc=0"
EOF
echo "D14M_CMDFILE md5=$(md5sum "$W/d14m_cmd.sh" | cut -d' ' -f1) deadline_in_container_s=$TMO"
touch "$W/AGE_DATUM"; echo "AGE_DATUM stage=MESH mtime=$(stat -c %Y "$W/AGE_DATUM")" >> "$LEDGER"
MA0=$(mem_gib); T0=$(date -u +%s)
sudo -n docker run -d --name "$NAME" --user 0:0 --cpus=1 --cpuset-cpus="$CPUSET" --memory="$MEM" --memory-swap="$MEM" --oom-score-adj=500 \
  -v "$BASE":/mnt -w /mnt/MESH "$IMG" bash -lc "source /home/dafoamuser/dafoam/loadDAFoam.sh && echo D14M_DEADLINE_IN_CONTAINER_S: $TMO && timeout -k 30 $TMO bash /mnt/MESH/d14m_cmd.sh" > /dev/null 2>&1 \
  || { echo "rc=125 stamp=$(date -u +%Y%m%dT%H%M%SZ) note=DOCKER_RUN_D_FAILED" >> "$STATUS"; echo "ABORT docker run -d failed"; exit 5; }
echo "D14M_LAUNCHED container=$NAME at=$(utc) cpuset=$CPUSET mem=$MEM"; echo "launched container=$NAME stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
# ---- poll the kernel record; the deadline lives inside the container
while [ "$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)" = "true" ]; do sleep 5; done
T1=$(date -u +%s); WALL=$((T1-T0)); MA1=$(mem_gib)
INS=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.StartedAt}} {{.State.FinishedAt}}' "$NAME" 2>/dev/null)
RC=$(echo "$INS" | awk '{print $1}'); OOM=$(echo "$INS" | awk '{print $2}')
sudo -n docker logs "$NAME" > "$BASE/MESH_${STAMP}.log" 2>&1
sudo -n chown -R ubuntu:ubuntu "$BASE" 2>/dev/null
CM=$(python3 -c "print(round($WALL/60.0,4))")
echo "ARM=MESH rc=${RC:-NOT_MEASURED} oom=${OOM:-NOT_MEASURED} wall_s=$WALL ranks=1 core_min=$CM container=$NAME memavail_GiB=$MA1 memavail_pre_GiB=$MA0 inspect=[$INS] cap_core_min=$CAP_CORE_MIN log=MESH_${STAMP}.log" >> "$LEDGER"
echo "rc=${RC:-NOT_MEASURED} stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=MESH source=docker_inspect_ExitCode oom=${OOM:-NOT_MEASURED} wall_s=$WALL core_min=$CM container=$NAME note=container-rc-NOT-a-verdict permission=$PERMISSION" >> "$STATUS"
[ "$RC" = "0" ] && [ -s "$W/checkMesh.log" ] && touch "$BASE/MESH_${STAMP}.log.ok.${STAMP}"
[ "$(python3 -c "print(1 if $CM > $CAP_CORE_MIN else 0)")" = "1" ] && echo "CAP_CROSSED core_min=$CM cap=$CAP_CORE_MIN (REPORTED, the in-container deadline is the stop)" | tee -a "$LEDGER"
# ---- the frozen comparator on the artifacts (zero compute); its rc is INFRASTRUCTURE
python3 "$HERE/d14m_grade.py" --root "$BASE" --out "$BASE/D14M_grade_${STAMP}.json" > "$BASE/D14M_grade_${STAMP}.out" 2>&1; GRC=$?
echo "grader_rc=$GRC stamp=$(date -u +%Y%m%dT%H%M%SZ) out=D14M_grade_${STAMP}.json note=comparator-exit-status-NOT-the-verdict" >> "$STATUS"
echo "D14M_DRIVER end=$(utc) container_rc=${RC:-NOT_MEASURED} wall_s=$WALL core_min=$CM grader_rc=$GRC"
exit 0
