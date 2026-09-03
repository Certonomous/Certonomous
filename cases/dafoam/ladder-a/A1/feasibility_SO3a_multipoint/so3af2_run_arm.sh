#!/usr/bin/env bash
# SO-3aF2 LAUNCHER -- one arm per invocation.  MESH | XM.
#
# `FEASIBILITY_PREREGISTRATION.md` (FROZEN 2026-08-31) governs.  Nothing here may
# move a prediction, a band, a cap or a label; this file carries the section 6
# NO-LAUNCH branches, the md5 pin block, the cpuset guard and the ledger row, and
# nothing else.
#
# EVERY VARIABLE THIS FILE REFERENCES IS ASSIGNED IN IT.  Under `set -u` an
# undefined name dies as a bash error with NO abort text of its own, on a file
# whose whole discipline is that its refusals name themselves -- the A1WRT defect
# (board S-42 section 1) and the SO-3D-R launcher defect of the same evening.  A
# mechanical sweep of this file's own bytes is part of the pin census.
#
# THE FOUR NO-LAUNCH BRANCHES, section 6, each writing its NAMED file and exiting
# with its NAMED rc.  All four read BLOCKED, never NOT A RESULT: a branch that
# fires is the launcher declining to start, not a measurement that failed.
#
#   NL-1 ROOT      run root exists, or a live container holds the so3af2_ prefix
#                  -> NOLAUNCH_ROOT.txt      rc 3   BLOCKED
#   NL-2 PRODUCER  staged producer md5 wrong, OR the forbidden gradient token
#                  appears ANYWHERE in it
#                  -> NOLAUNCH_PRODUCER.txt  rc 4   BLOCKED
#   NL-3 FREEZE    the reader's md5 is not the value pinned at freeze
#                  -> NOLAUNCH_FREEZE.txt    rc 5   BLOCKED
#   NL-4 MEM       a BOUNDED poll on live MemAvailable against the 6.0 GiB floor
#                  expires (bound 3600 s), terminating NON-ZERO
#                  -> NOLAUNCH_MEM.txt       rc 6   BLOCKED
#
# ON NL-3 AND THE THING A FILE CANNOT DO, STATED RATHER THAN FUDGED: section 6
# NL-3 names "the reader's OR LAUNCHER's md5".  A file cannot contain its own md5
# -- writing the value changes the value.  This launcher therefore checks the
# READER's pin here, SELF-HASHES and writes its own md5 into the ledger and the
# NOLAUNCH files so a grader can compare, and its own pin is verified from
# OUTSIDE by `so3af2_pin_selftest.sh` against the value registered in the
# pre-registration's Stage-2 amendment.  The half NL-3 can enforce in-process is
# enforced here; the half it cannot is enforced by a second instrument and named.
#
# SUBMISSIONS PARKED.  This file sends, files, uploads and posts nothing.

set -uo pipefail

# ---------------------------------------------------------------------------
# IDENTITY AND REGISTERED CONSTANTS
# ---------------------------------------------------------------------------
ITEM=SO3aF2
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility
PREFIX=so3af2_
STAMP="$(date -u +%Y-%m-%dT%H%M%SZ)"
SELF_MD5="$(md5sum "$0" | cut -d' ' -f1)"

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER.md section 6:
# ---- a version string is not an identity).  SHIPPED ONLY -- section 1 registers
# ---- that the PATCHED row is not run and that its absence is a stated scope
# ---- limit, not an omission to be discovered.
IMG_SHIPPED=dafoam/opt-packages:latest
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc

# ---- MD5 PIN BLOCK.  Every `MD5_*=` line here is ENUMERATED out of this file's
# ---- own bytes by so3af2_pin_selftest.sh and mapped to a registered target; a
# ---- pin added here with no target FAILS that census.  "Every pin is driven"
# ---- is a COUNT, never a claim (the SO-1c defect: twelve pins, four driven).
MD5_READER=d5f4149d43abe3a165ffe7e653b78bee     # so3af2_read.py, pinned at the 2026-08-31 freeze, section 8
MD5_PRODUCER=4359b9b7c04a81b9e56231481f4e0ccb                   # so3af2_runScript.py, pinned at the Stage-2 amendment

# ---- THE FORBIDDEN TOKEN, section 6 NL-2 second clause: the structural half of
# ---- the no-gradient promise.  Written by construction so this file does not
# ---- itself contain the literal it forbids -- otherwise a scan of the launcher
# ---- would trip on the launcher.
FORBIDDEN_TOKEN="compute""_totals"

# ---- CAPS, section 7.  core-minutes.  An overrun STOPS the run.
CAP_MESH=3.0
CAP_XM=6.0
CEILING=9.0
MEM_FLOOR_GIB=6.0
MEM_CAP=4g
RANKS=1
POLL_BOUND_S=3600
POLL_INTERVAL_S=15
FORBIDDEN_CORE=9      # held by SO-2MR; must never be taken (section 7)

ARM="${1:-}"
case "$ARM" in
  MESH) CAP="$CAP_MESH" ;;
  XM)   CAP="$CAP_XM" ;;
  *) echo "ABORT usage: so3af2_run_arm.sh <MESH|XM>"; exit 64 ;;
esac

nolaunch() {   # nolaunch <file> <rc> <reason...>
  local f="$1"; local rc="$2"; shift 2
  local dest="$HERE/$f"
  [ -d "$BASE" ] && dest="$BASE/$f"
  {
    echo "ITEM=$ITEM ARM=$ARM STAMP=$STAMP"
    echo "BRANCH=${f%.txt} rc=$rc reading=BLOCKED"
    echo "launcher_md5=$SELF_MD5"
    echo "reason: $*"
    echo "NO CONTAINER WAS STARTED BY THIS INVOCATION."
  } > "$dest"
  echo "SO3AF2_NOLAUNCH branch=${f%.txt} rc=$rc reading=BLOCKED reason: $*"
  exit "$rc"
}

# ---------------------------------------------------------------------------
# NL-3 FREEZE -- the pinned instruments, checked BEFORE anything else is read
# ---------------------------------------------------------------------------
READER="$HERE/so3af2_read.py"
[ -f "$READER" ] || nolaunch NOLAUNCH_FREEZE.txt 5 "reader absent at $READER"
GOT_READER="$(md5sum "$READER" | cut -d' ' -f1)"
[ "$GOT_READER" = "$MD5_READER" ] || nolaunch NOLAUNCH_FREEZE.txt 5 \
  "reader md5 $GOT_READER != pinned $MD5_READER"
echo "SO3AF2_NL3_PASS reader_md5=$GOT_READER launcher_md5=$SELF_MD5"

# ---------------------------------------------------------------------------
# NL-2 PRODUCER -- md5, AND the forbidden token ANYWHERE in the staged bytes
# ---------------------------------------------------------------------------
PRODUCER="$HERE/so3af2_runScript.py"
[ -f "$PRODUCER" ] || nolaunch NOLAUNCH_PRODUCER.txt 4 "producer absent at $PRODUCER"
GOT_PRODUCER="$(md5sum "$PRODUCER" | cut -d' ' -f1)"
[ "$GOT_PRODUCER" = "$MD5_PRODUCER" ] || nolaunch NOLAUNCH_PRODUCER.txt 4 \
  "producer md5 $GOT_PRODUCER != pinned $MD5_PRODUCER"
TOKEN_HITS="$(grep -c -- "$FORBIDDEN_TOKEN" "$PRODUCER" || true)"
[ "$TOKEN_HITS" = "0" ] || nolaunch NOLAUNCH_PRODUCER.txt 4 \
  "the forbidden gradient token appears $TOKEN_HITS time(s) in the staged producer; \
section 3 makes the no-gradient promise STRUCTURAL and section 6 NL-2 enforces it over the WHOLE FILE"
echo "SO3AF2_NL2_PASS producer_md5=$GOT_PRODUCER forbidden_token_hits=0"

# ---------------------------------------------------------------------------
# NL-1 ROOT -- the run root, and any live container holding this item's prefix
# ---------------------------------------------------------------------------
if [ -e "$BASE" ] && [ "$ARM" = "MESH" ]; then
  nolaunch NOLAUNCH_ROOT.txt 3 "run root $BASE already exists at the FIRST arm; \
archive by mv, never delete -- an existing root means this is not the run allowed to produce the answer"
fi
LIVE="$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -c "^$PREFIX" || true)"
[ "$LIVE" = "0" ] || nolaunch NOLAUNCH_ROOT.txt 3 \
  "$LIVE live container(s) already hold the $PREFIX prefix"
echo "SO3AF2_NL1_PASS root_ok=yes live_prefix_containers=0"

# ---------------------------------------------------------------------------
# NL-4 MEM -- a BOUNDED poll that TERMINATES NON-ZERO, never block-and-continue
# ---------------------------------------------------------------------------
WAITED=0
while : ; do
  MEMAVAIL_GIB="$(awk '/MemAvailable/{printf "%.2f", $2/1048576.0}' /proc/meminfo)"
  BELOW="$(awk -v a="$MEMAVAIL_GIB" -v f="$MEM_FLOOR_GIB" 'BEGIN{print (a<f)?1:0}')"
  [ "$BELOW" = "0" ] && break
  if [ "$WAITED" -ge "$POLL_BOUND_S" ]; then
    nolaunch NOLAUNCH_MEM.txt 6 "MemAvailable ${MEMAVAIL_GIB} GiB stayed below the \
${MEM_FLOOR_GIB} GiB floor for the whole ${POLL_BOUND_S} s bound; the poll TERMINATES NON-ZERO \
rather than blocking and continuing"
  fi
  sleep "$POLL_INTERVAL_S"
  WAITED=$((WAITED + POLL_INTERVAL_S))
done
echo "SO3AF2_NL4_PASS MemAvailable_GiB=$MEMAVAIL_GIB floor=$MEM_FLOOR_GIB waited_s=$WAITED"

# ---------------------------------------------------------------------------
# THE CPUSET GUARD -- fixed against LIVE containers at arm time, refused on
# collision.  Section 7: core 9 is held by SO-2MR and must not be taken.  This is
# a READING of the box now, never a constant chosen when the freeze was written.
# ---------------------------------------------------------------------------
TAKEN="$(sudo -n docker ps -q 2>/dev/null | while read -r c; do
           sudo -n docker inspect --format '{{.HostConfig.CpusetCpus}}' "$c" 2>/dev/null
         done | tr ',' '\n' | tr -d ' ' | grep -E '^[0-9]+$' | sort -un | tr '\n' ' ')"
NPROC="$(nproc)"
CPUSET=""
for c in $(seq 0 $((NPROC - 1))); do
  [ "$c" = "$FORBIDDEN_CORE" ] && continue
  case " $TAKEN " in *" $c "*) continue ;; esac
  CPUSET="$c"; break
done
[ -n "$CPUSET" ] || nolaunch NOLAUNCH_ROOT.txt 3 \
  "no free core: taken=[$TAKEN] forbidden=$FORBIDDEN_CORE nproc=$NPROC"
echo "SO3AF2_CPUSET cpuset=$CPUSET taken=[$TAKEN] forbidden=$FORBIDDEN_CORE"

# ---------------------------------------------------------------------------
# IMAGE IDENTITY BY DIGEST
# ---------------------------------------------------------------------------
GOT_DIGEST="$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG_SHIPPED" 2>/dev/null | sed 's/.*@//')"
[ -n "$GOT_DIGEST" ] || nolaunch NOLAUNCH_FREEZE.txt 5 "cannot read the digest of $IMG_SHIPPED"
[ "$GOT_DIGEST" = "$IMG_SHIPPED_DIGEST" ] || nolaunch NOLAUNCH_FREEZE.txt 5 \
  "image digest $GOT_DIGEST != registered $IMG_SHIPPED_DIGEST"
echo "SO3AF2_IMAGE_OK row=SHIPPED image=$IMG_SHIPPED digest=$GOT_DIGEST"

# ---------------------------------------------------------------------------
# STAGE AND RUN
# ---------------------------------------------------------------------------
mkdir -p "$BASE/$ARM"
LEDGER="$BASE/ledger.txt"
NAME="${PREFIX}${ARM}_${STAMP}"
T0="$(date +%s)"

if [ "$ARM" = "MESH" ]; then
  CMD="cd /mnt/MESH && ./preProcessing.sh > checkMesh.log 2>&1 && checkMesh >> checkMesh.log 2>&1"
else
  cp "$PRODUCER" "$BASE/XM/so3af2_runScript.py"
  CMD="cd /mnt/XM && python so3af2_runScript.py -task run_model > XM.log 2>&1"
fi

sudo -n docker run -d --name "$NAME" \
  --user 0:0 --cpus=$RANKS --cpuset-cpus="$CPUSET" \
  --memory=$MEM_CAP --memory-swap=$MEM_CAP --oom-score-adj=500 \
  -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG_SHIPPED" bash -lc "$CMD" > /dev/null
RC_START=$?
[ "$RC_START" = "0" ] || nolaunch NOLAUNCH_ROOT.txt 3 "docker run returned $RC_START"

sudo -n docker wait "$NAME" > /dev/null 2>&1
RC="$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$NAME" 2>/dev/null)"
[ -n "$RC" ] || RC=255
T1="$(date +%s)"
WALL=$((T1 - T0))
CORE_MIN="$(awk -v w="$WALL" -v r="$RANKS" 'BEGIN{printf "%.4f", w*r/60.0}')"

sudo -n docker logs "$NAME" > "$BASE/${ARM}_${STAMP}.container.log" 2>&1 || true
sudo -n docker inspect --format \
  '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.StartedAt}} {{.State.FinishedAt}} {{.HostConfig.CpusetCpus}} {{.HostConfig.Memory}}' \
  "$NAME" > "$BASE/${ARM}_${STAMP}.inspect.txt" 2>&1 || true

# ---- the cap: an overrun STOPS the item; it does not get a new budget --------
OVER="$(awk -v c="$CORE_MIN" -v k="$CAP" 'BEGIN{print (c>k)?1:0}')"
{
  echo "ITEM=$ITEM ARM=$ARM STAMP=$STAMP rc=$RC wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP ceiling=$CEILING cpuset=$CPUSET mem=$MEM_CAP row=SHIPPED digest=$GOT_DIGEST launcher_md5=$SELF_MD5 reader_md5=$GOT_READER producer_md5=$GOT_PRODUCER memavail_GiB=$MEMAVAIL_GIB cap_exceeded=$OVER"
} >> "$LEDGER"

echo "SO3AF2_ARM_DONE arm=$ARM rc=$RC wall_s=$WALL core_min=$CORE_MIN cap=$CAP cap_exceeded=$OVER"
[ "$OVER" = "0" ] || { echo "ABORT CAP: $ARM spent $CORE_MIN core-min against a cap of $CAP. The run STOPS; it does not get a new budget."; exit 8; }
exit "$RC"
