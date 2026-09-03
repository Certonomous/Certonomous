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
# ---- THE MESH ARM'S STAGING SOURCE.  See ADDENDUM 1.  The MESH arm previously
# ---- staged NOTHING: it created an empty directory, mounted it, and told a
# ---- container to run a script that was never put there (rc=127, measured
# ---- 2026-09-03T21:48:15Z).  The source below is SO-3aR2's own pre-mesh
# ---- skeleton -- the same lineage this item's producer is derived from -- and
# ---- it is pinned by a MANIFEST md5 over sorted relative paths and content
# ---- hashes, asserted on BOTH SIDES of the copy.
MESH_SRC=/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient/base
MD5_MESH_SRC_MANIFEST=b7bf0eca3185b7d9af93e61ca122201b

# ---- what the MESH arm must find in its working directory before a container
# ---- is created.  DERIVED FROM `preProcessing.sh`'s OWN BYTES, not guessed from
# ---- the error message: it runs `python genAirFoilMesh.py`, then plot3dToFoam,
# ---- autoPatch, createPatch and renumberMesh (which read system/), then
# ---- `cp -r 0.orig 0`.  rc=127 named the FIRST missing thing; this names the set.
MESH_REQUIRES="preProcessing.sh genAirFoilMesh.py profiles system constant 0.orig"

# ---- THE DAFoam ENVIRONMENT LOADER, DERIVED FROM A1WR'S OWN DRIVER BYTES.
# ---- ADDENDUM 3. The arm command never sourced the environment, so the MESH arm
# ---- exited rc=127 a second time -- `preProcessing.sh` ran and stopped at its own
# ---- first guard. `bash -lc` does NOT supply it: a non-interactive login shell
# ---- reads /etc/profile and the first of ~/.bash_profile / ~/.bash_login /
# ---- ~/.profile, NOT ~/.bashrc where a DAFoam image's environment hangs.
# ---- The path is DERIVED from `a1wr_chain_driver.sh` -- the driver that
# ---- successfully ran the alpha sweep this ladder is built on -- rather than
# ---- retyped, so a future divergence there cannot silently split the two.
A1WR_DRIVER=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar/a1wr_chain_driver.sh
MD5_A1WR_DRIVER=9bff59b63509e76d5dfa373a42a47074
MD5_ATTR_CENSUS=2fd479d881f63b529605b3a45d0154f3
MD5_ENV_ASSERT=a5b7fcae05aab420d94623582d45f897
MD5_READER=d5f4149d43abe3a165ffe7e653b78bee     # so3af2_read.py, pinned at the 2026-08-31 freeze, section 8
MD5_PRODUCER=c268633f67e6d2c785feec2ebfc7326c                   # so3af2_runScript.py, pinned at the Stage-2 amendment

# ---- THE FORBIDDEN TOKEN, section 6 NL-2 second clause: the structural half of
# ---- the no-gradient promise.  Written by construction so this file does not
# ---- itself contain the literal it forbids -- otherwise a scan of the launcher
# ---- would trip on the launcher.
FORBIDDEN_TOKEN="compute""_totals"

# ---- CAPS, section 7.  core-minutes.  An overrun STOPS the run.
CAP_MESH=3.0
CAP_XM=6.0
# ---- ADDENDUM 8. The ATTRCENSUS arm: a bounded DIAGNOSTIC that asks the live
# ---- solver object which attribute holds a residual history, instead of the
# ---- producer guessing a fifth name. IT SCORES NOTHING and writes no graded
# ---- artefact. Capped WELL UNDER the 6.0 the XM arm did not approach: XM ran
# ---- three primals to its refusal for 0.3500 core-min MEASURED, and this arm
# ---- runs the same three plus an enumeration.
CAP_ATTRCENSUS=2.0
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
  ATTRCENSUS) CAP="$CAP_ATTRCENSUS" ;;
  *) echo "ABORT usage: so3af2_run_arm.sh <MESH|XM|ATTRCENSUS>"; exit 64 ;;
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
ENV_ASSERT="$HERE/so3af2_env_assert.sh"
ATTR_CENSUS="$HERE/so3af2_attr_census.py"
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
# THE ENVIRONMENT LOADER -- resolved from A1WR's driver, uniqueness ASSERTED
# ---------------------------------------------------------------------------
[ -f "$A1WR_DRIVER" ] || nolaunch NOLAUNCH_ENV.txt 11 \
  "A1WR driver $A1WR_DRIVER is absent -- the loader path is DERIVED from it and this launcher will not retype it"
GOT_A1WR="$(md5sum "$A1WR_DRIVER" | cut -d' ' -f1)"
[ "$GOT_A1WR" = "$MD5_A1WR_DRIVER" ] || nolaunch NOLAUNCH_ENV.txt 11 \
  "A1WR driver md5 $GOT_A1WR != pinned $MD5_A1WR_DRIVER -- the source of the loader path has changed and the two items may have diverged"
# TAKE THE FIRST MATCH IS THE TRAP THIS FAMILY KEEPS PAYING FOR (D6RF-BLOCKING-1).
# The DISTINCT values are counted and anything but exactly one REFUSES.
LOADER_SET="$(grep -oE 'source [^ "]*loadDAFoam\.sh' "$A1WR_DRIVER" | awk '{print $2}' | sort -u)"
LOADER_N="$(printf '%s\n' "$LOADER_SET" | grep -c . || true)"
[ "$LOADER_N" = "1" ] || nolaunch NOLAUNCH_ENV.txt 11 \
  "expected exactly ONE distinct loader path in $A1WR_DRIVER, found $LOADER_N: [$(printf '%s ' $LOADER_SET)]"
LOADER="$LOADER_SET"
[ -f "$ENV_ASSERT" ] || nolaunch NOLAUNCH_ENV.txt 11 "environment assertion $ENV_ASSERT is absent"
GOT_ENV="$(md5sum "$ENV_ASSERT" | cut -d' ' -f1)"
[ "$GOT_ENV" = "$MD5_ENV_ASSERT" ] || nolaunch NOLAUNCH_ENV.txt 11 \
  "environment assertion md5 $GOT_ENV != pinned $MD5_ENV_ASSERT"
echo "SO3AF2_LOADER_DERIVED loader=$LOADER from=$A1WR_DRIVER a1wr_md5=$GOT_A1WR distinct=1 env_assert_md5=$GOT_ENV"

# ---------------------------------------------------------------------------
# STAGE AND RUN
# ---------------------------------------------------------------------------
# A MANIFEST over a tree: sorted relative paths AND content hashes, so a moved
# file, a renamed file and a changed byte are all visible. A plain `md5sum *`
# would not see a path change at all.
tree_manifest() { ( cd "$1" && find . -type f | sort | xargs md5sum ) | md5sum | cut -d' ' -f1; }

mkdir -p "$BASE"
WORK="$BASE/$ARM"

if [ "$ARM" = "MESH" ]; then
  # ---- the source, asserted BEFORE the copy -------------------------------
  [ -d "$MESH_SRC" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
    "MESH staging source $MESH_SRC is not a directory. UNMEASURED, not assumed."
  SRC_MANIFEST="$(tree_manifest "$MESH_SRC")"
  [ "$SRC_MANIFEST" = "$MD5_MESH_SRC_MANIFEST" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
    "MESH staging source manifest $SRC_MANIFEST != pinned $MD5_MESH_SRC_MANIFEST. \
The source tree is not the one this item registered; a copy from it would stage unknown bytes."

  # ---- G-COLD: the source must NOT already carry what MESH exists to make ---
  # ---- Staging the answer is worse than staging nothing: it would produce a
  # ---- mesh arm that inherits a mesh and reports success.
  [ -e "$MESH_SRC/constant/polyMesh" ] && nolaunch NOLAUNCH_STAGING.txt 9 \
    "G-COLD: $MESH_SRC already carries constant/polyMesh -- that is the OUTPUT this arm exists to produce"
  [ -e "$MESH_SRC/0" ] && nolaunch NOLAUNCH_STAGING.txt 9 \
    "G-COLD: $MESH_SRC already carries 0/ -- preProcessing.sh creates it from 0.orig"

  [ -e "$WORK" ] && nolaunch NOLAUNCH_STAGING.txt 9 \
    "$WORK already exists. Archive by mv, never delete -- an existing arm directory means this is not the run allowed to produce the answer."
  cp -a "$MESH_SRC" "$WORK" || nolaunch NOLAUNCH_STAGING.txt 9 "cp -a from $MESH_SRC to $WORK failed"

  # ---- the same manifest, asserted AFTER the copy --------------------------
  DST_MANIFEST="$(tree_manifest "$WORK")"
  [ "$DST_MANIFEST" = "$MD5_MESH_SRC_MANIFEST" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
    "staged manifest $DST_MANIFEST != source manifest $MD5_MESH_SRC_MANIFEST -- the copy did not reproduce the tree"
  echo "SO3AF2_STAGED arm=MESH src=$MESH_SRC manifest=$DST_MANIFEST files=$(find "$WORK" -type f | wc -l)"
else
  # =========================================================================
  # THE XM ARM -- ADDENDUM 6.  It previously staged ONE FILE into an otherwise
  # empty directory (ADDENDUM 1 finding 1).  What it actually needs is a FULL
  # CASE PER OPERATING POINT plus the FFD, and the paths must match the FROZEN
  # reader's own expressions, because a wrong path here does not refuse -- it
  # produces a plausible F3 MISS on a separation that actually worked, which is
  # a confident wrong answer and the one thing this item cannot recover cheaply.
  #
  # EVERY REQUIREMENT BELOW IS DERIVED FROM THE PRODUCER'S OR THE READER'S OWN
  # BYTES.  Nothing is transcribed: a literal in two files is a divergence
  # waiting to happen, and this item has already paid for one.
  # =========================================================================
  mkdir -p "$WORK"

  # ---- XM consumes MESH's OUTPUT.  Its absence REFUSES BY NAME. ------------
  MESH_OUT="$BASE/MESH"
  [ -d "$MESH_OUT" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
    "XM requires the MESH arm's output at $MESH_OUT and it is not there -- arm MESH has not run"
  [ -f "$MESH_OUT/constant/polyMesh/boundary" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
    "$MESH_OUT carries no constant/polyMesh/boundary -- the mesh MESH exists to produce is absent"
  { [ -f "$MESH_OUT/0/U" ] || [ -f "$MESH_OUT/0/U.gz" ]; } || nolaunch NOLAUNCH_STAGING.txt 9 \
    "$MESH_OUT carries neither 0/U nor 0/U.gz -- preProcessing.sh's 'cp -r 0.orig 0' did not land"

  # ---- THE FFD, DERIVED FROM THE PRODUCER'S OWN REFERENCE ------------------
  # Uniqueness COUNTED, never take-the-first-match (D6RF-BLOCKING-1).
  # ⚠ THE TRAILING QUOTE MUST BE STRIPPED. A first draft ended the sed at
  # `s/.*file="//` and yielded `FFD/wingFFD.xyz"` -- WITH the closing quote --
  # so the existence check below tested a path that can never exist and this arm
  # would have REFUSED ON EVERY LAUNCH, FOREVER. Caught on the host before any
  # container, by driving the derivation instead of trusting it.
  FFD_SET="$(grep -oE 'OM_DVGEOCOMP\(file="[^"]+"' "$PRODUCER" | sed 's/.*file="//; s/"$//' | sort -u)"
  FFD_N="$(printf '%s\n' "$FFD_SET" | grep -c . || true)"
  [ "$FFD_N" = "1" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
    "expected exactly ONE OM_DVGEOCOMP file reference in the producer, found $FFD_N: [$(printf '%s ' $FFD_SET)]"
  FFD_REL="$FFD_SET"
  FFD_DIR="$(dirname "$FFD_REL")"

  # ---- THE PER-POINT DIRECTORIES, DERIVED FROM THE FROZEN READER ------------
  # These names are the reader's, not the launcher's: the reader's F3 reads them
  # and scores MISS if they are not where it looks.
  RD_DECL="$(grep -cE '^RUN_DIRS = \[' "$READER" || true)"
  [ "$RD_DECL" = "1" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
    "expected exactly ONE list-literal RUN_DIRS declaration in the frozen reader, found $RD_DECL"
  RUN_DIRS_LIST="$(grep -oE '^RUN_DIRS = \[[^]]*\]' "$READER" | grep -oE '"[^"]+"' | tr -d '"')"
  RD_N="$(printf '%s\n' "$RUN_DIRS_LIST" | grep -c . || true)"
  [ "$RD_N" -ge 1 ] || nolaunch NOLAUNCH_STAGING.txt 9 "the frozen reader's RUN_DIRS is empty"

  # ---- THE CASE PATH, DERIVED FROM THE READER'S OWN read_run_dirs CALL ------
  CASE_SEG="$(grep -oE 'read_run_dirs\(os\.path\.join\(root, "[^"]+", "[^"]+"\)\)' "$READER" \
              | grep -oE '"[^"]+"' | tr -d '"' | tail -1)"
  [ -n "$CASE_SEG" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
    "could not derive the case-directory segment from the frozen reader's read_run_dirs call"
  CASE_DIR="$WORK/$CASE_SEG"
  [ -e "$CASE_DIR" ] && nolaunch NOLAUNCH_STAGING.txt 9 \
    "$CASE_DIR already exists -- archive by mv, never delete"
  mkdir -p "$CASE_DIR"

  cp -a "$MESH_OUT/$FFD_DIR" "$CASE_DIR/" || nolaunch NOLAUNCH_STAGING.txt 9 \
    "could not stage $FFD_DIR from $MESH_OUT"
  [ -f "$CASE_DIR/$FFD_REL" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
    "$CASE_DIR/$FFD_REL is absent after staging -- the producer reads it relative to its own cwd"

  # ---- ONE FULL CASE COPY PER OPERATING POINT, each G-COLD ----------------
  for mp in $RUN_DIRS_LIST; do
    cp -a "$MESH_OUT" "$CASE_DIR/$mp" || nolaunch NOLAUNCH_STAGING.txt 9 "could not stage $mp from $MESH_OUT"
    rm -f "$CASE_DIR/$mp/so3af2_cmd.sh" "$CASE_DIR/$mp/checkMesh.log" \
          "$CASE_DIR/$mp/logMeshGeneration.txt" "$CASE_DIR/$mp/volumeMesh.xyz" \
          "$CASE_DIR/$mp/surfaceMesh.xyz" 2>/dev/null
    # G-COLD, per point: no decomposition, no time directory but 0 and 0.orig,
    # and the initial field actually present. A warm start is silent otherwise.
    [ -n "$(ls -d "$CASE_DIR/$mp"/processor* 2>/dev/null)" ] && nolaunch NOLAUNCH_STAGING.txt 9 \
      "G-COLD $mp: processor* directories present -- this is not a cold case"
    for d in "$CASE_DIR/$mp"/*/; do
      n="$(basename "$d")"
      case "$n" in
        0|0.orig|constant|system|FFD|profiles) ;;
        [0-9]*) nolaunch NOLAUNCH_STAGING.txt 9 "G-COLD $mp: time directory $n present -- this is not a cold case" ;;
      esac
    done
    { [ -f "$CASE_DIR/$mp/0/U" ] || [ -f "$CASE_DIR/$mp/0/U.gz" ]; } || nolaunch NOLAUNCH_STAGING.txt 9 \
      "G-COLD $mp: neither 0/U nor 0/U.gz is present"
    [ -f "$CASE_DIR/$mp/constant/polyMesh/boundary" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
      "G-COLD $mp: constant/polyMesh/boundary is absent -- the point has no mesh"
  done

  # THE TWO SOLVER ARMS SHARE THIS STAGING AND DIFFER ONLY IN WHICH INSTRUMENT
  # RUNS. Duplicating it would be the sibling-branch defect this item has already
  # produced twice -- a pattern applied to one branch and not the one beside it.
  cp "$PRODUCER" "$WORK/so3af2_runScript.py"
  if [ "$ARM" = "ATTRCENSUS" ]; then
    [ -f "$ATTR_CENSUS" ] || nolaunch NOLAUNCH_STAGING.txt 9 "attribute census instrument absent at $ATTR_CENSUS"
    GOT_AC="$(md5sum "$ATTR_CENSUS" | cut -d' ' -f1)"
    [ "$GOT_AC" = "$MD5_ATTR_CENSUS" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
      "attribute census md5 $GOT_AC != pinned $MD5_ATTR_CENSUS"
    cp "$ATTR_CENSUS" "$WORK/so3af2_attr_census.py"
  fi
  # THE READER IS STAGED BESIDE THE PRODUCER because the producer DERIVES its
  # output paths from the reader's own expressions (ADDENDUM 2) rather than
  # transcribing them. Its md5 was verified against the pin at NL-3 above.
  cp "$READER" "$WORK/so3af2_read.py"
  echo "SO3AF2_STAGED arm=$ARM case=$CASE_SEG ffd=$FFD_REL run_dirs=[$(printf '%s ' $RUN_DIRS_LIST)] points=$RD_N files=$(find "$WORK" -type f | wc -l)"
  echo "SO3AF2_STAGING_PRECONDITION_PASS arm=$ARM derived_from=producer+frozen_reader ffd_refs=1 run_dirs_decls=1 case_seg=$CASE_SEG"
fi

# ---------------------------------------------------------------------------
# THE STAGING PRECONDITION -- rc 9, and it is NOT a fifth NO-LAUNCH branch.
#
# Section 6's taxonomy of FOUR branches and their rcs 3/4/5/6 is UNCHANGED in
# what it refuses; this assert has its OWN rc, distinct from those four, from the
# producer's exit 7 and from the cap's exit 8. It can only ever refuse MORE, never
# less, which is the ground on which it is lawful after a container has run.
#
# ALL FOUR EXISTING GUARDS CHECK AN INSTRUMENT, NOT AN INPUT -- producer md5,
# forbidden token, reader pin, image digest. A guard set that checks every
# instrument and no input will happily launch a container into an empty
# directory, and on 2026-09-03 it did.
# ---------------------------------------------------------------------------
MISSING=""
FOUND=""
for req in $MESH_REQUIRES; do
  if [ "$ARM" = "MESH" ] && [ ! -e "$WORK/$req" ]; then
    MISSING="$MISSING $req"
  elif [ "$ARM" = "MESH" ]; then
    FOUND="$FOUND $req"
  fi
done
if [ "$ARM" = "MESH" ]; then
  [ -z "$MISSING" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
    "STAGING PRECONDITION: the MESH arm invokes ./preProcessing.sh, which needs [$MESH_REQUIRES]; \
MISSING from $WORK:$MISSING. rc=127 names the FIRST missing thing, never the last, so this names the SET."
  [ -x "$WORK/preProcessing.sh" ] || nolaunch NOLAUNCH_STAGING.txt 9 \
    "STAGING PRECONDITION: $WORK/preProcessing.sh is present but NOT EXECUTABLE; \
the arm invokes it as ./preProcessing.sh and bash would answer 126, not 127."
  echo "SO3AF2_STAGING_PRECONDITION_PASS arm=MESH found=[$FOUND] executable=preProcessing.sh files=$(find "$WORK" -type f | wc -l)"
fi

LEDGER="$BASE/ledger.txt"
NAME="${PREFIX}${ARM}_${STAMP}"
T0="$(date +%s)"

cp "$ENV_ASSERT" "$BASE/so3af2_env_assert.sh"
if [ "$ARM" = "MESH" ]; then
  cat > "$WORK/so3af2_cmd.sh" <<'ARMCMD'
cd /mnt/MESH && ./preProcessing.sh > checkMesh.log 2>&1 && checkMesh >> checkMesh.log 2>&1
ARMCMD
else
  # THE ARM'S OWN COMMAND, derived from $ARM rather than hard-coded, so a third
  # arm cannot inherit the second's working directory.
  if [ "$ARM" = "ATTRCENSUS" ]; then
    ARM_ENTRY=so3af2_attr_census.py
  else
    ARM_ENTRY=so3af2_runScript.py
  fi
  printf 'cd /mnt/%s && python %s -task run_model > %s.log 2>&1\n' \
    "$ARM" "$ARM_ENTRY" "$ARM" > "$WORK/so3af2_cmd.sh"
fi
# ---- BOTH ARMS GO THROUGH THE ENVIRONMENT ASSERTION.  Repairing MESH and
# ---- rediscovering this on XM is the sibling-branch defect this item has
# ---- already produced twice; the two arms differ ONLY in their command file.
CMD="bash /mnt/so3af2_env_assert.sh $LOADER bash /mnt/$ARM/so3af2_cmd.sh"

sudo -n docker run -d --name "$NAME" \
  --user 0:0 --cpus=$RANKS --cpuset-cpus="$CPUSET" \
  --memory=$MEM_CAP --memory-swap=$MEM_CAP --oom-score-adj=500 \
  -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG_SHIPPED" bash -lc "$CMD" > /dev/null
RC_START=$?
# A FAILED `docker run` IS NOT THE NL-1 ROOT BRANCH AND MUST NOT WEAR ITS rc.
# An earlier version reused NOLAUNCH_ROOT.txt / rc 3 here, so "the run root
# already exists" and "the container could not be started" were indistinguishable
# to any reader of the rc. Its own file, its own rc 10, distinct from the four
# registered NO-LAUNCH rcs (3/4/5/6), from the staging precondition (9), from the
# producer's residual refusal (7) and from the cap (8).
[ "$RC_START" = "0" ] || nolaunch NOLAUNCH_DOCKER.txt 10 \
  "docker run returned $RC_START -- the container could not be STARTED. This is NOT NL-1 ROOT \
and does not mean the run root exists; it means the daemon refused or the invocation was malformed."

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
