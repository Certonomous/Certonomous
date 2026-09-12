#!/usr/bin/env bash
# Curriculum D6R2C arm launcher.
#
# DERIVED from cases/dafoam/ladder-a/A2/curriculum_D6R2/d6r2_run_arm.sh
# (md5 715a2b9c42519b2ad25e9deeadb6351c).  The G-ROOT.1/2/3 guards, the digest
# pin, the G-COLD guard, the age datum, the delivered-core sampler and the
# ledger row are that file's design, carried here.  The REGISTERED DELTAS are
# listed in PREREGISTRATION.md section 2 and reproduced at the head of each
# block below.  There is exactly one departure from the parent's numerics:
# NONE.  Every delta is a launch-hygiene delta from Sanaa's 2026-09-12 items.
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call.  Every step
# gates explicitly with `|| { echo ABORT...; exit N; }`.
set -uo pipefail

ITEM=D6R2C
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable
BASE="${BASE:-$REGISTERED_BASE}"
SRC=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C

# ---- G-ROOT.1 -- BASE must be THIS item's registered root, normalised -------
BASE_REAL=$(realpath -m "$BASE"); REG_REAL=$(realpath -m "$REGISTERED_BASE")
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
  echo "  given: $BASE_REAL"; echo "  registered: $REG_REAL"; exit 3
fi

# ---- G-ROOT.2 -- NAME the roots this file must never write.  The D6R2 root is
# ---- FIRST in the list and is the reason the list exists here: D6R2's O_mp
# ---- holds the ROOT-OWNED artefacts of the run that died at 17:32:57Z, and
# ---- this item exists because that run is NOT inherited.  Staging over it
# ---- would destroy the census's own evidence.
FORBIDDEN_ROOTS="/home/ubuntu/certonomous-runs/CURRICULUM-D6R2-a2-wing-multipoint-transonic
/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D6RACC2-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D6RF12-a2-wing-fd-nutilda-repair
/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density
/home/ubuntu/certonomous-runs/A3GC-L2R
/home/ubuntu/certonomous-runs/A3GC-L1"
while IFS= read -r forb; do
  [ -z "$forb" ] && continue
  if [ "$BASE_REAL" = "$(realpath -m "$forb")" ]; then
    echo "ABORT G-ROOT.2 BASE resolves to ANOTHER ITEM'S RUN ROOT: $forb"; exit 3
  fi
done <<< "$FORBIDDEN_ROOTS"

# ---- G-ROOT.3 -- the ledger must belong to this item and to no other -------
if [ -f "$BASE/ledger.txt" ]; then
  FOREIGN=$(grep -a "^ITEM=" "$BASE/ledger.txt" 2>/dev/null | grep -av "^ITEM=$ITEM$" | head -1)
  if [ -n "$FOREIGN" ]; then
    echo "ABORT G-ROOT.3 ledger at $BASE/ledger.txt carries another item: $FOREIGN"; exit 3
  fi
fi
echo "D6R2C_G_ROOT_PASS item=$ITEM base=$BASE_REAL"

# ===========================================================================
# REGISTERED DELTA L1 -- SANAA LAUNCH ITEM 6: AS UBUNTU, NEVER ROOT.
# The parent ran `--user 0:0` and `mpirun --allow-run-as-root`; the census
# records 3,456 root-owned files written into D6R2's run root as a result.
# uid 1000 is `ubuntu` INSIDE this image as well as on the host (verified by
# execution: `id` in dafoam-idwarp-rot:v1 as -u 1000 prints uid=1000(ubuntu)).
# /home/dafoamuser is mode 0750 owned by uid 1002, so uid 1000 cannot source
# loadDAFoam.sh without gid 1002 as a SUPPLEMENTARY group.  --group-add 1002
# gives traverse; the PRIMARY gid stays 1000, so every file this run writes is
# ubuntu:ubuntu on the host.  HOME is set because uid 1000 has no home in the
# image and numpy/matplotlib/openmdao write caches into $HOME.
# ===========================================================================
RUN_UID=1000
RUN_GID=1000
EXTRA_GID=1002

# ---- REGISTERED DELTA L2 -- SANAA LAUNCH ITEM 7 + item 3 of the D6R2 brief:
# ---- the footprint is DECLARED and CHECKED against free RAM before start.
MEM_FOOTPRINT_GB=17
MEM_LIMIT=20g
RANKS=4
CPUSET=2,3,4,5

# ---- REGISTERED DELTA L3 -- SANAA BOX HYGIENE ITEM 18.  Load above core count
# ---- is a defect; swap use above zero for solver jobs is a defect.  BOTH STOP
# ---- NEW LAUNCHES.  This is a LAUNCH precondition -- it refuses to START.  It
# ---- is NOT a cap and it NEVER stops a running solver (Sanaa 2026-09-12 #17).
NCPU=$(nproc)
LOAD1=$(awk '{print $1}' /proc/loadavg)
SWAPUSED_KB=$(awk '/^SwapTotal:/{t=$2}/^SwapFree:/{f=$2}END{print t-f}' /proc/meminfo)
MEMAVAIL_GB=$(awk '/MemAvailable/{printf "%.2f", $2/1048576}' /proc/meminfo)
if [ "$(python3 -c "print(1 if $LOAD1 > $NCPU else 0)")" = "1" ]; then
  echo "ABORT G-LOAD (Sanaa item 18) load1=$LOAD1 > nproc=$NCPU. New launches stop until cleared."
  exit 18
fi
if [ "$SWAPUSED_KB" -gt 0 ]; then
  echo "ABORT G-SWAP (Sanaa item 18) swap in use: ${SWAPUSED_KB} kB > 0. New launches stop until cleared."
  exit 18
fi
if [ "$(python3 -c "print(1 if $MEMAVAIL_GB < $MEM_FOOTPRINT_GB else 0)")" = "1" ]; then
  echo "ABORT G-MEM (Sanaa item 7) MemAvailable ${MEMAVAIL_GB} GiB < declared footprint ${MEM_FOOTPRINT_GB} GiB."
  exit 19
fi
echo "D6R2C_G_BOX_PASS load1=$LOAD1/$NCPU swap_used_kB=$SWAPUSED_KB memavail_GiB=$MEMAVAIL_GB footprint_GiB=$MEM_FOOTPRINT_GB"

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER 6) ------
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
MD5_RUNSCRIPT=0558fb194b013b54c725d3d49a9dd0a1

# ---- arms.  cap_core_min is REGISTERED and REPORTS; it never kills. --------
# CAPS ARE 3.00x THE REGISTERED ESTIMATE (PREREGISTRATION.md section 8).  They
# REPORT.  A crossing grades the row NOT A RESULT and the cap is NEVER RAISED;
# NOTHING KILLS ON IT (Sanaa 2026-09-12 directive #17 read with her item 7).
cap_core_min() {
  case "$1" in
    KR_REF)  echo  420.0 ;;  # 3.00 x 140.0 = 4 majors x 31.258 + findFeasibleDesign
    KR_KILL) echo  234.0 ;;  # 3.00 x  78.0 = 2 majors x 31.258 + findFeasibleDesign
    KR_RES)  echo  420.0 ;;  # 3.00 x 140.0 -- the replayed majors are cached, so this is slack
    O_mp)    echo 2359.5 ;;  # 3.00 x 786.5 = 25 majors x 31.258 + 5 preamble
    ARM0_4R) echo   45.0 ;;  # 3.00 x  15.0
    ARM0_2R) echo   60.0 ;;  # 3.00 x  20.0
    *) echo "" ;;
  esac
}
# ARM 0 IS A 2-VS-4 RANK COMPARISON, so its rank count is NOT the item's 4.
arm_ranks() { case "$1" in ARM0_2R) echo 2 ;; *) echo 4 ;; esac; }
arm_max_iter() {
  case "$1" in
    KR_REF|KR_KILL|KR_RES) echo 4 ;;
    O_mp) echo 25 ;;
    *) echo "" ;;
  esac
}

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: d6r2c_run_arm.sh <KR_REF|KR_KILL|KR_RES|O_mp|ARM0_4R|ARM0_2R> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: d6r2c_run_arm.sh <arm> <image>"; exit 64; }
CAP=$(cap_core_min "$ARM")
test -n "$CAP" || { echo "ABORT unknown arm $ARM"; exit 64; }
# the cost unit is core-minutes = wall_s x THIS ARM'S ranks / 60 (rule 12)
RANKS_COST=$(arm_ranks "$ARM")

# ---- G-LIVE -- a live arm is never re-staged ------------------------------
LIVE=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d6r2c_${ARM}_" 2>/dev/null | head -3 | tr '\n' ',')
if [ -n "$LIVE" ]; then echo "ABORT G-LIVE arm $ARM already running: $LIVE"; exit 3; fi

# ---- G-IMG ---------------------------------------------------------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
[ -n "$GOT_DIGEST" ] || GOT_DIGEST=$(sudo -n docker image inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
test "$GOT_DIGEST" = "$IMG_PATCHED_DIGEST" || {
  echo "ABORT G-IMG $IMG got=$GOT_DIGEST want=$IMG_PATCHED_DIGEST"; exit 4; }
echo "D6R2C_G_IMG_PASS digest=$GOT_DIGEST"

# ---- G-FREEZE -- the instrument that runs IS the frozen instrument --------
GOT_MD5=$(md5sum "$SRC/d6r2c_opt_runScript.py" | cut -d' ' -f1)
test "$GOT_MD5" = "$MD5_RUNSCRIPT" || {
  echo "ABORT G-FREEZE d6r2c_opt_runScript.py md5=$GOT_MD5 want=$MD5_RUNSCRIPT"; exit 4; }
echo "D6R2C_G_FREEZE_PASS runscript_md5=$GOT_MD5"

mkdir -p "$BASE" || { echo "ABORT mkdir base"; exit 4; }
# base/ is the pristine case.  It is COPIED from D6R2's base/ ONCE, READ-ONLY,
# and is the only thing this item takes from D6R2's root.
if [ ! -d "$BASE/base" ]; then
  cp -a /home/ubuntu/certonomous-runs/CURRICULUM-D6R2-a2-wing-multipoint-transonic/base "$BASE/base" \
    || { echo "ABORT could not seed base/"; exit 4; }
  echo "D6R2C_BASE_SEEDED md5sum_controlDict=$(md5sum "$BASE/base/system/controlDict" | cut -d' ' -f1)"
fi

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d6r2c_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"
MAXIT=$(arm_max_iter "$ARM")

# ---- stage ---------------------------------------------------------------
rm -rf "$WORK" 2>/dev/null
cp -a "$BASE/base" "$WORK" || { echo "ABORT stage copy"; exit 4; }
for mp in mp04 mp05 mp06; do
  cp -a "$BASE/base" "$WORK/$mp" || { echo "ABORT stage $mp"; exit 4; }
  test -n "$(ls -d "$WORK/$mp"/processor* 2>/dev/null)" && { echo "ABORT G-COLD $mp processor* present"; exit 5; }
done
cp -a "$SRC/d6r2c_opt_runScript.py" "$WORK/" || { echo "ABORT stage instrument"; exit 4; }

HOTARG=""
if [ "$ARM" = "KR_RES" ]; then
  # ---- REGISTERED DELTA L4 -- THE RESUME.  The killed arm's history and its
  # ---- cold x0 are staged as INPUTS, BEFORE the age datum is set, so the age
  # ---- guard dates them as inputs and not as this run's output.
  SRC_HST="$BASE/KR_KILL/OptView.hst"
  SRC_X0="$BASE/KR_KILL/d6r2c_x0.json"
  test -f "$SRC_HST" || { echo "ABORT KR_RES: no $SRC_HST to resume from"; exit 5; }
  test -f "$SRC_X0"  || { echo "ABORT KR_RES: no $SRC_X0 to check the resume against"; exit 5; }
  cp "$SRC_HST" "$WORK/hotstart.hst" || { echo "ABORT stage hotstart history"; exit 4; }
  cp "$SRC_X0"  "$WORK/d6r2c_x0.json" || { echo "ABORT stage x0"; exit 4; }
  echo "D6R2C_HOTSTART_STAGED md5_hst=$(md5sum "$WORK/hotstart.hst" | cut -d' ' -f1) md5_x0=$(md5sum "$WORK/d6r2c_x0.json" | cut -d' ' -f1)"
  HOTARG="-hotstart hotstart.hst"
fi

for bad in "$WORK/reports" "$WORK/OptView.hst" "$WORK/opt_IPOPT.txt" "$WORK/d6r2c_evals.jsonl"; do
  test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
done
test -f "$WORK/0/U" || { echo "ABORT G-COLD 0/U missing"; exit 5; }
touch "$WORK/0"/* || { echo "ABORT age-guard datum"; exit 5; }
AGE_DATUM=$(stat -c '%Y' "$WORK/0/U")
echo "$AGE_DATUM" > "$WORK/.d6r2c_age_datum"
echo "D6R2C_G_COLD_PASS arm=$ARM age_datum_epoch=$AGE_DATUM"

# ---- the command.  NO --allow-run-as-root: we are not root. ---------------
case "$ARM" in
  KR_REF|KR_KILL|KR_RES|O_mp)
     CMD="mpirun -np $RANKS --bind-to core --report-bindings -x PYTHONPATH -x HOME python d6r2c_opt_runScript.py -task run_driver -optimizer IPOPT -max_iter $MAXIT $HOTARG" ;;
  ARM0_4R)
     CMD="mpirun -np 4 --bind-to core --report-bindings -x PYTHONPATH -x HOME python d6r2c_opt_runScript.py -task compute_totals" ;;
  ARM0_2R)
     CMD="mpirun -np 2 --bind-to core --report-bindings -x PYTHONPATH -x HOME python d6r2c_opt_runScript.py -task compute_totals" ;;
esac
CMDFILE="$WORK/d6r2c_cmd.sh"
printf '%s\n' "$CMD" > "$CMDFILE" || { echo "ABORT cmd file"; exit 4; }
echo "D6R2C_CMD arm=$ARM max_iter=${MAXIT:-n/a} md5=$(md5sum "$CMDFILE" | cut -d' ' -f1)"
echo "D6R2C_CMD_TEXT $CMD"

T0=$(date -u +%s)
sudo -n docker run -d --name "$NAME" \
    --user ${RUN_UID}:${RUN_GID} --group-add ${EXTRA_GID} -e HOME=/tmp \
    --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM_LIMIT --memory-swap=$MEM_LIMIT --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D6R2C_CONTAINER_UID: \$(id -u) \$(id -un) GID: \$(id -g) GROUPS: \$(id -G) && \
     echo D6R2C_DEADLINE_IN_CONTAINER_S: NONE_NO_CAP_RULING_6f3abf8a3 && \
     bash /mnt/$ARM/d6r2c_cmd.sh" > /dev/null 2>&1 \
  || { echo "ABORT could not start container"; exit 4; }
echo "D6R2C_LAUNCHED name=$NAME arm=$ARM uid=${RUN_UID}:${RUN_GID}+${EXTRA_GID} ranks=$RANKS cpuset=$CPUSET mem=$MEM_LIMIT"

# ---- REGISTERED DELTA L5 -- THE KILL.  KR_KILL ALONE carries it, and it is
# ---- NOT a cap and NOT a stop rule: it IS the experiment Sanaa's Checkpoints
# ---- item 5 asks for.  SIGKILL, unhandled, at IPOPT major 2 -- the same class
# ---- of death as the 17:32:57Z exit 255 and as a reboot.
if [ "$ARM" = "KR_KILL" ]; then
 (
  for _ in $(seq 1 100000); do
    if [ -f "$WORK/opt_IPOPT.txt" ] && grep -qaE '^ +2 +[0-9]' "$WORK/opt_IPOPT.txt" 2>/dev/null; then
      sleep 20   # let the history flush the evaluations belonging to major 2
      echo "D6R2C_KILL_FIRING arm=KR_KILL trigger=IPOPT_major_2 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$BASE/ledger.txt"
      sudo -n docker kill -s KILL "$NAME" >/dev/null 2>&1
      exit 0
    fi
    sudo -n docker ps -q --filter "name=^${NAME}$" | grep -q . || exit 0
    sleep 5
  done
 ) &
 KILLER=$!
 echo "D6R2C_KILLER_ARMED pid=$KILLER trigger=IPOPT_major_2 signal=SIGKILL"
fi

# ---- REGISTERED DELTA L6 -- SANAA CHECKPOINTS ITEM 1: primal fields snapshot
# ---- every 30 min wall, LAST TWO KEPT, older purged.  The primal writes its
# ---- fields at the end of EVERY design major (controlDict writeInterval 1000
# ---- == endTime 1000), measured at 7.8 wall-min/major uncontended, so the
# ---- worst loss between field writes is one major, far inside 30 min.  This
# ---- rotator snapshots history + design vector + the latest primal fields on
# ---- the 30-min wall cadence she registered.
CKPT_INTERVAL_S=1800
(
  while sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | grep -q .; do
    sleep $CKPT_INTERVAL_S
    sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | grep -q . || break
    D="$WORK/ckpt/$(date -u +%Y%m%dT%H%M%SZ)"
    mkdir -p "$D" 2>/dev/null
    for f in OptView.hst opt_IPOPT.txt d6r2c_x0.json d6r2c_evals.jsonl; do
      [ -f "$WORK/$f" ] && cp -a "$WORK/$f" "$D/" 2>/dev/null
    done
    for mp in mp04 mp05 mp06; do
      for pd in "$WORK/$mp"/processor*; do
        [ -d "$pd" ] || continue
        t=$(ls -d "$pd"/[0-9]* 2>/dev/null | sort -V | tail -1)
        [ -n "$t" ] && { mkdir -p "$D/$mp/$(basename "$pd")" 2>/dev/null; cp -a "$t" "$D/$mp/$(basename "$pd")/" 2>/dev/null; }
      done
    done
    echo "D6R2C_CKPT $(basename "$D") bytes=$(du -sb "$D" 2>/dev/null | cut -f1)" >> "$BASE/ledger.txt"
    # LAST TWO KEPT, older PURGED (her words).
    ls -1d "$WORK"/ckpt/*/ 2>/dev/null | sort | head -n -2 | while read -r old; do rm -rf "$old"; done
  done
) &
CKPTER=$!
echo "D6R2C_CKPT_ROTATOR_ARMED pid=$CKPTER interval_s=$CKPT_INTERVAL_S keep=2"

# ---- the cap REPORTS; it never stops (Sanaa 2026-09-12 directive #17) -----
CAP_REPORTED=no
while true; do
  RUNNING=$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)
  NOW=$(date -u +%s); EL=$((NOW-T0))
  CM=$(python3 -c "print(round($EL*$RANKS_COST/60.0,3))")
  [ "$RUNNING" != "true" ] && break
  if [ "$CAP_REPORTED" = "no" ] && [ "$(python3 -c "print(1 if $CM > $CAP else 0)")" = "1" ]; then
    CAP_REPORTED=yes
    echo "D6R2C_CAP_CROSSED arm=$ARM core_min=$CM cap=$CAP action=REPORTED_RUN_CONTINUES_NOT_A_RESULT_AND_CAP_NEVER_RAISED" | tee -a "$BASE/ledger.txt"
  fi
  sleep 10
done
sudo -n docker logs "$NAME" > "$LOG" 2>&1
rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$NAME" 2>/dev/null); test -n "$rc" || rc=125
OOM=$(sudo -n docker inspect --format '{{.State.OOMKilled}}' "$NAME" 2>/dev/null)
T1=$(date -u +%s); WALL=$((T1-T0)); CORE_MIN=$(python3 -c "print(round($WALL*$RANKS_COST/60.0,3))")
kill $CKPTER 2>/dev/null; wait $CKPTER 2>/dev/null
[ -n "${KILLER:-}" ] && { kill $KILLER 2>/dev/null; wait $KILLER 2>/dev/null; }

# ---- OWNERSHIP PROOF.  Sanaa item 6 is not satisfied by a flag; it is
# ---- satisfied by the bytes on disk being ubuntu's.
ROOTOWNED=$(find "$WORK" -newermt "@$AGE_DATUM" \( -uid 0 -o -gid 0 \) 2>/dev/null | wc -l)
echo "D6R2C_OWNERSHIP arm=$ARM root_owned_files_written_by_this_run=$ROOTOWNED"

echo "ITEM=$ITEM" >> "$BASE/ledger.txt"
echo "ARM=$ARM rc=$rc oom=$OOM wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cost_ranks=$RANKS_COST cap_core_min=$CAP max_iter=${MAXIT:-n/a} hotstart=${HOTARG:-none} uid=${RUN_UID}:${RUN_GID} root_owned_new_files=$ROOTOWNED memavail_pre_GiB=$MEMAVAIL_GB load1_pre=$LOAD1 swap_pre_kB=$SWAPUSED_KB log=$(basename "$LOG") stamp=$STAMP" | tee -a "$BASE/ledger.txt"
exit 0
