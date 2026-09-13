#!/bin/bash
# DRIVAER R5 -- build the wall-function RANS mesh registered by
#   verification/campaign/DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md
# frozen at 38aab8e78662d574d1b14b61da7efc5898be5c7e.
#
# THE PIN IS TAKEN LIVE AT LAUNCH, NEVER AT FREEZE TIME.  Blobs have moved
# repeatedly today, so this wrapper re-reads the blob sha from the frozen commit
# AT LAUNCH and records it beside the run; a stale freeze-time pin would prove
# nothing.  If the blob has moved since the freeze the wrapper REFUSES.
#
# STAGE `probe` = castellation only (snap false, addLayers false): a cheap
# sizing measurement against the section-7 M1 gate of 15-20 M cells, so that
# gate is not decided by a guess.  STAGE `full` = the graded build.
#
# rc is captured INSIDE this wrapper: `setsid timeout cmd` exits 0 for every
# outcome, so an rc read around the setsid line is meaningless.
# NEVER deletes anything; REFUSES an existing run root.
set -u
STAGE="$1"; NP="${2:-16}"
REPO=/home/ubuntu/Certonomous
D=$REPO/verification/runs/navier_class/DRIVAER
SRC=$D/r2_medium
FREEZE=38aab8e78662d574d1b14b61da7efc5898be5c7e
PREREG=verification/campaign/DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md

case "$STAGE" in
  probe) R=$D/R5_SIZING_PROBE ;;
  full)  R=$D/r5_wallfunction ;;
  *) echo "REFUSE: stage must be probe|full"; exit 2 ;;
esac
[ -e "$R" ] && { echo "REFUSE: $R exists. A guard is satisfied by MOVING the case, never by disabling the guard."; exit 2; }

cd "$REPO" || exit 2
# ---- LIVE PIN ---------------------------------------------------------------
BLOB_FREEZE=$(git rev-parse "$FREEZE:$PREREG" 2>/dev/null) || { echo "REFUSE: cannot read the frozen registration blob"; exit 2; }
BLOB_NOW=$(git rev-parse "HEAD:$PREREG" 2>/dev/null) || { echo "REFUSE: registration missing at HEAD"; exit 2; }
if [ "$BLOB_FREEZE" != "$BLOB_NOW" ]; then
  echo "REFUSE: the registration blob has MOVED since the freeze."
  echo "        freeze $FREEZE -> $BLOB_FREEZE"
  echo "        HEAD    $(git rev-parse HEAD) -> $BLOB_NOW"
  echo "        A gate that can move after compute is not a gate.  NOTHING LAUNCHED."
  exit 2
fi

# ---- memory gate (hardware, not budget: caps were lifted, RAM was not) -------
AVAIL=$(free -g | awk '/^Mem:/{print $7}'); CEIL=$(( AVAIL - 8 ))
PRED_GIB=${PRED_GIB:-120}
echo "MEMORY GATE: available=${AVAIL} GiB ceiling=${CEIL} GiB predicted=${PRED_GIB} GiB"
if [ "$PRED_GIB" -gt "$CEIL" ]; then
  echo "BLOCKED: predicted peak ${PRED_GIB} GiB exceeds available-8 = ${CEIL} GiB. NOTHING LAUNCHED."; exit 3
fi

mkdir -p "$R/system" "$R/constant/triSurface"
for f in blockMeshDict meshQualityDict surfaceFeatureExtractDict; do cp -p "$SRC/system/$f" "$R/system/$f"; done
for f in controlDict fvSchemes fvSolution; do
  s="$SRC/system/$f"; [ -f "$SRC/system/$f.meshbuild" ] && s="$SRC/system/$f.meshbuild"
  cp -p "$s" "$R/system/$f"
  grep -q '#include' "$R/system/$f" && { echo "REFUSE: $f carries an #include -- solver dict, not a mesh-build dict"; exit 2; }
done
ln -s /home/ubuntu/certonomous-runs/navier_class/DRIVAER/drivaerml_r7a5c094/run_466/drivaer_466.stl \
      "$R/constant/triSurface/drivaer_466.stl"

python3 "$REPO/cases/navier_class/DRIVAER/mesh/make_r5_dict.py" \
        "$SRC/system/snappyHexMeshDict" "$R/system/snappyHexMeshDict" > "$R/DICT_GENERATION.txt" 2>&1
RCD=$?; cat "$R/DICT_GENERATION.txt"
[ $RCD -eq 0 ] || { echo "REFUSE: dict generation failed rc=$RCD"; exit 2; }

if [ "$STAGE" = "probe" ]; then
  sed -i 's/^snap  *true;/snap            false;/; s/^addLayers  *true;/addLayers       false;/' "$R/system/snappyHexMeshDict"
  grep -E "^(castellatedMesh|snap|addLayers)" "$R/system/snappyHexMeshDict" > "$R/PROBE_PHASES.txt"
fi

{ echo "stage=$STAGE"; echo "ranks=$NP"; echo "launch_utc=$(date -u +%FT%TZ)";
  echo "repo_HEAD_at_launch=$(git rev-parse HEAD)";
  echo "prereg_freeze_commit=$FREEZE";
  echo "prereg_blob_LIVE_AT_LAUNCH=$BLOB_NOW";
  echo "prereg_blob_at_freeze=$BLOB_FREEZE";
  echo "blob_pin_verified_live=yes";
  echo "snappyHexMeshDict_sha256=$(sha256sum "$R/system/snappyHexMeshDict" | cut -d' ' -f1)";
  echo "source_level=r2_medium (h0=0.4 m, surface cell 25.0 mm at level 4)";
  echo "build_procedure=PARALLEL np=$NP -- the R1/R2 family built SERIAL; disclosed, not silent";
} > "$R/RUN_PIN.txt"
cat "$R/RUN_PIN.txt"

{ echo "# R5 vs r2_medium -- the registered edits, proven by diff"
  diff -u --label a/r2_medium/system/snappyHexMeshDict --label b/R5/system/snappyHexMeshDict \
       "$SRC/system/snappyHexMeshDict" "$R/system/snappyHexMeshDict"
} > "$R/THE_ONE_CHANGE.diff" 2>&1

S=$(date +%s)
bash "$REPO/cases/navier_class/DRIVAER/mesh/run_build.sh" medium "$R" "$NP" > "$R/launcher.out" 2>&1
RC=$?
E=$(date +%s); W=$((E-S))
echo "$RC" > "$R/RUN_RC"
awk -v w="$W" -v n="$NP" 'BEGIN{printf "wall_s=%d\nranks=%d\ncore_min=%.2f\n", w, n, w*n/60.0}' > "$R/RUN_META.txt"
if [ "$RC" = "137" ] || [ "$RC" = "143" ]; then
  echo "rc=$RC: KILLED FROM OUTSIDE (OOM, operator or session end) -- NOT A RESULT, and NOT a cap stop; no spend cap is armed." > "$R/EXTERNAL_KILL.txt"
fi
echo "build_r5 $STAGE done rc=$RC wall=${W}s core_min=$(awk -v w=$W -v n=$NP 'BEGIN{printf "%.1f", w*n/60}')" | tee -a "$R/launcher.out"
exit $RC
