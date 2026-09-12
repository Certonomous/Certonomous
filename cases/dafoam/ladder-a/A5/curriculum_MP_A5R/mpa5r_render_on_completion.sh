#!/usr/bin/env bash
# =====================================================================
# MP_A5R -- RENDER ON COMPLETION.  **PREPARED.  ARMS BEHIND THE RUN.  LAUNCHES NOTHING.**
#
# Sanaa 2026-09-12 ~20:30Z: "whenever a run completes, i want the paraview visualization
# of its mesh saved. (when the run is complete). ... this way we dont generate the
# paraview in one go tmr."
#
# THE GRADED TREE IS NEVER TOUCHED.  Every step reads the arm and writes only into a COPY.
# The precedent is d6r2_render_prep.sh, and the reason it exists is that D6RF10 lost its
# graded fields to its own successor.  Here even the `case.foam` handle ParaView needs is
# written into the copy, never beside the graded fields.
#
# ZERO SOLVER COMPUTE.  No container, no reconstructPar, no foamToVTK: MP_A5R runs np=1, so
# every arm is already a reconstructed serial case and host pvbatch reads it directly.
#
# A RENDER IS NOT A GATE.  This script cannot change a verdict.  It exits 0 even when the
# render fails, and says so in the sidecar, so no wrapper can read a render failure as a
# run result.
#
# NEVER TOUCHES A RUNNING SOLVER.  It only reads, and it waits rather than polling hard.
# =====================================================================
set -u
BASE="${BASE:?BASE (the MP_A5R run root) must be given explicitly}"
CASE_DIR=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_MP_A5R
RENDER_PY="$CASE_DIR/mpa5r_render.py"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT="$BASE/MPA5R_RENDER.out"
GRACE_GRADE_S=900            # bounded wait for a grade record AFTER the run has ended

say(){ printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$OUT"; }
say "MPA5R_RENDER_ARMED base=$BASE ppid=$PPID (1 == reparented to init)"

# --- 1. WAIT FOR THE RUN TO COMPLETE.  CHAIN_RC.txt is written by the launcher's own
#        detached wrapper AFTER the chain ends, which is the only honest "complete" signal.
for i in $(seq 1 20160); do [ -f "$BASE/CHAIN_RC.txt" ] && break; sleep 10; done
if [ ! -f "$BASE/CHAIN_RC.txt" ]; then say "MPA5R_RENDER_GAVE_UP_WAITING"; exit 0; fi
CHAIN_RC=$(cat "$BASE/CHAIN_RC.txt" 2>/dev/null)
say "MPA5R_RENDER_RUN_COMPLETE chain_rc=$CHAIN_RC"

# --- 2. ORDERED BEHIND THE GRADING, but never blocked by it: a run that completed and was
#        not graded still gets its picture, and the sidecar records which happened.
GRADE_JSON=""; VERDICT="NOT_GRADED_AT_RENDER_TIME"
for i in $(seq 1 $((GRACE_GRADE_S/15))); do
  G=$(ls -t "$BASE"/*grade*.json "$BASE"/mpa5r_grade*.json 2>/dev/null | head -1)
  [ -n "$G" ] && { GRADE_JSON="$G"; break; }
  sleep 15
done
if [ -n "$GRADE_JSON" ]; then
  VERDICT=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('verdict','?'))" "$GRADE_JSON" 2>/dev/null || echo "?")
  say "MPA5R_RENDER_GRADE_SEEN $GRADE_JSON verdict=$VERDICT"
else
  say "MPA5R_RENDER_NO_GRADE_AFTER_${GRACE_GRADE_S}s -- rendering anyway, sidecar says so"
fi

# --- 3. WHICH ARM CARRIES THE FINEST STATE.  E is the endpoint (the OPTIMISED state across
#        all three scenarios); B is the baseline.  Sanaa asked for the finest fields
#        available, so E is preferred and the fallback is RECORDED, never silent.
ARM=""; ARM_MEANING=""
if [ -d "$BASE/E" ]; then ARM=E; ARM_MEANING="endpoint: the OPTIMISED state at the final design vector"
elif [ -d "$BASE/B" ]; then ARM=B; ARM_MEANING="FALLBACK -- arm E absent, so these are BASELINE fields, NOT the optimised state"
else say "MPA5R_RENDER_NO_ARM -- neither E nor B exists under $BASE"; exit 0; fi
say "MPA5R_RENDER_ARM=$ARM ($ARM_MEANING)"

COPY="$BASE/MPA5R-RENDER-COPY-$STAMP"
mkdir -p "$COPY" || { say "MPA5R_RENDER_MKDIR_FAILED"; exit 0; }
HEAD_SHA=$(cd /home/ubuntu/Certonomous && git rev-parse HEAD 2>/dev/null || echo UNKNOWN)
IMAGES_TOTAL=0; SCEN_DONE=""

for mp in mp0 mp1 mp2; do
  SRC="$BASE/$ARM/$mp"
  [ -d "$SRC" ] || { say "MPA5R_RENDER_SCENARIO_ABSENT $mp"; continue; }
  cp -a "$SRC" "$COPY/$mp" || { say "MPA5R_RENDER_COPY_FAILED $mp"; continue; }
  find "$COPY/$mp" -name '*.gz' -exec gunzip -q {} + 2>/dev/null
  TAG="MP_A5R_${ARM}_${mp}_single-level_${STAMP}"
  timeout 1800 xvfb-run -a --server-args="-screen 0 1920x1440x24" \
    pvbatch "$RENDER_PY" --case "$COPY/$mp" --out "$COPY/png" --tag "$TAG" \
    >> "$COPY/render_${mp}.log" 2>&1
  RRC=$?
  N=$(ls "$COPY/png/${TAG}"_*.png 2>/dev/null | wc -l)
  IMAGES_TOTAL=$((IMAGES_TOTAL + N)); SCEN_DONE="$SCEN_DONE $mp"
  # THE rc IS NOT THE SUCCESS SIGNAL HERE AND SAYING SO IS NOT AN EXCUSE.  MEASURED on the
  # rehearsal: pvbatch prints `RENDER_REPORT ... images=8 errors=0`, writes every PNG, and
  # THEN exits 1 on `X Error ... GLXBadContext` during GL teardown under xvfb.  The work is
  # complete before the error occurs.  So the wrapper judges by the COUNTED IMAGES, which is
  # a measurement, and records the rc beside it rather than hiding it -- a reader who sees
  # rc=1 with images=8 must be able to tell which one means what.
  RCNOTE="rc_is_teardown_artifact_judge_by_images"
  [ "$N" -gt 0 ] || RCNOTE="NO_IMAGES_THIS_IS_A_REAL_RENDER_FAILURE"
  say "MPA5R_RENDER_SCENARIO $mp rc=$RRC images=$N note=$RCNOTE tag=$TAG"
done

# --- 4. THE SIDECAR.  Paths, ids and the honest level label, so the record can be read
#        without opening a single PNG -- and so nobody mistakes one mesh for a grid family.
python3 - "$COPY" "$BASE" "$ARM" "$ARM_MEANING" "$VERDICT" "$GRADE_JSON" "$HEAD_SHA" "$STAMP" "$IMAGES_TOTAL" "$CHAIN_RC" <<'PY' 2>>"$OUT"
import json, os, sys, glob
copy, base, arm, meaning, verdict, gjson, sha, stamp, ntot, chain_rc = sys.argv[1:11]
side = {
 "case_id": "MP_A5R", "run_root": base, "render_copy": copy, "stamp_utc": stamp,
 "repo_head_at_render": sha, "chain_rc": chain_rc,
 "verdict_at_render_time": verdict, "grade_record": gjson or None,
 "arm_rendered": arm, "arm_meaning": meaning,
 "level_label": "single-level",
 "level_note": ("MP_A5R IS AN OPTIMISATION ON ONE U-BEND MESH ACROSS THREE SCENARIOS AND HAS NO "
                "GRID FAMILY. Sanaa's instruction distinguishes a coarse/medium mesh from fine-mesh "
                "fields; THAT DISTINCTION HAS NO REFERENT HERE. Calling this mesh 'coarse' to match "
                "the shape of the instruction would be a label that looks compliant and is false."),
 "fields_are_from": ("the latest time of the arm above, i.e. the finest state this item has. There "
                     "is no finer mesh whose fields could be substituted."),
 "images": sorted(os.path.basename(p) for p in glob.glob(os.path.join(copy, "png", "*.png"))),
 "images_total": int(ntot),
 "exit_code_note": ("pvbatch exits 1 under xvfb on a GLXBadContext during GL TEARDOWN, AFTER "
                   "every image is written and after its own report prints errors=0. MEASURED on "
                   "the rehearsal. Success here is judged by IMAGES COUNTED ON DISK, not by rc; "
                   "images_total==0 with scenarios present is the real failure signal."),
 "render_is_not_a_gate": ("A render failure NEVER changes this run's verdict. This file records "
                          "what was rendered; the verdict lives in the grade record."),
 "graded_tree_untouched": ("Every render read the arm and wrote only into render_copy, including the "
                           "case.foam handle ParaView requires."),
}
p = os.path.join(copy, "MPA5R_RENDER_SIDECAR.json")
with open(p, "w") as f: json.dump(side, f, indent=2, sort_keys=True)
print("MPA5R_RENDER_SIDECAR %s images=%d" % (p, side["images_total"]))
PY

say "MPA5R_RENDER_DONE copy=$COPY images=$IMAGES_TOTAL scenarios=[$SCEN_DONE] verdict=$VERDICT"
exit 0   # DELIBERATE: a render is not a gate
