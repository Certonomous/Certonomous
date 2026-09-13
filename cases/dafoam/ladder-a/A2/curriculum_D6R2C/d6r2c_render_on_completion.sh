#!/usr/bin/env bash
# =====================================================================
# D6R2C -- RENDER ON COMPLETION.  **PREPARED.  ARMS BEHIND THE RUN.  LAUNCHES NOTHING.**
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
# ZERO SOLVER COMPUTE.  No container, no reconstructPar, no foamToVTK: D6R2C runs np=1, so
# every arm is already a reconstructed serial case and host pvbatch reads it directly.
#
# A RENDER IS NOT A GATE.  This script cannot change a verdict.  It exits 0 even when the
# render fails, and says so in the sidecar, so no wrapper can read a render failure as a
# run result.
#
# NEVER TOUCHES A RUNNING SOLVER.  It only reads, and it waits rather than polling hard.
# =====================================================================
set -u
BASE="${BASE:?BASE (the D6R2C run root) must be given explicitly}"
CASE_DIR=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C
RENDER_PY="$CASE_DIR/d6r2c_render.py"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
# OUT is overridable so a SECOND arming (a later arm, e.g. O_mp behind KR_REF) writes its
# own record instead of interleaving with the earlier arm's in one file.  say() appends, so
# the default never overwrote anything -- but two arms in one file is exactly how a fallback
# arm gets read as the optimum.  Default unchanged: no caller is broken.
OUT="${D6R2C_RENDER_OUT:-$BASE/D6R2C_RENDER.out}"
GRACE_GRADE_S=900            # bounded wait for a grade record AFTER the run has ended

# THE ARM PREFERENCE LIST, DEFINED ONCE.  It is consumed TWICE -- to pick the grade record to
# wait for, and to pick the arm to draw -- and those two must not be able to disagree.  Two
# copies of this list is precisely how a render ends up captioned with another arm's verdict.
# KR_RES, NOT KR_RESUME: the resumed arm on disk is $BASE/KR_RES, so the old spelling never
# matched any directory and the resumed arm would have been SILENTLY SKIPPED in favour of the
# KR_REF 4-major probe -- a worse state presented as the best available, with nothing said.
ARM_PREFERENCE="O_mp O KR_RES KR_REF"

say(){ printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$OUT"; }
say "D6R2C_RENDER_ARMED base=$BASE ppid=$PPID (1 == reparented to init)"

# --- 1. WAIT FOR THE RUN TO COMPLETE.  CHAIN_RC.txt is written by the launcher's own
#        detached wrapper AFTER the chain ends, which is the only honest "complete" signal.
for i in $(seq 1 20160); do [ -f "$BASE/CHAIN_RC.txt" ] && break; sleep 10; done
if [ ! -f "$BASE/CHAIN_RC.txt" ]; then say "D6R2C_RENDER_GAVE_UP_WAITING"; exit 0; fi
CHAIN_RC=$(cat "$BASE/CHAIN_RC.txt" 2>/dev/null)
say "D6R2C_RENDER_RUN_COMPLETE chain_rc=$CHAIN_RC"

# --- 2. ORDERED BEHIND THE GRADING, but never blocked by it: a run that completed and was
#        not graded still gets its picture, and the sidecar records which happened.
GRADE_JSON=""; VERDICT="NOT_GRADED_AT_RENDER_TIME"
for i in $(seq 1 $((GRACE_GRADE_S/15))); do
  # ARM-SCOPED, NOT A WILDCARD.  The old glob matched ANY *grade*.json anywhere under $BASE,
  # so a stale record left by a KR arm would have been read as THIS render's verdict and
  # printed beside the optimised shape.  A grade record belongs to this render only if it
  # NAMES THE ARM this render will draw -- $BASE/<ARM>_GRADE.json -- and nothing else is
  # accepted.  An absent record still costs only the bounded wait, then renders ungraded.
  G=""
  for cand in $ARM_PREFERENCE; do
    [ -d "$BASE/$cand" ] && { [ -s "$BASE/${cand}_GRADE.json" ] && G="$BASE/${cand}_GRADE.json"; break; }
  done
  [ -n "$G" ] && { GRADE_JSON="$G"; break; }
  sleep 15
done
if [ -n "$GRADE_JSON" ]; then
  VERDICT=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('verdict','?'))" "$GRADE_JSON" 2>/dev/null || echo "?")
  say "D6R2C_RENDER_GRADE_SEEN $GRADE_JSON verdict=$VERDICT"
else
  say "D6R2C_RENDER_NO_GRADE_AFTER_${GRACE_GRADE_S}s -- rendering anyway, sidecar says so"
fi

# --- 3. WHICH ARM CARRIES THE FINEST STATE.  E is the endpoint (the OPTIMISED state across
#        all three scenarios); B is the baseline.  Sanaa asked for the finest fields
#        available, so E is preferred and the fallback is RECORDED, never silent.
ARM=""; ARM_MEANING=""
for cand in $ARM_PREFERENCE; do
  [ -d "$BASE/$cand" ] && { ARM=$cand; break; }
done
case "$ARM" in
  O_mp|O) ARM_MEANING="the optimisation arm: fields at the FINAL design vector reached" ;;
  KR_RES)    ARM_MEANING="FALLBACK -- the resumed kill-and-resume arm, NOT a full optimisation" ;;
  KR_REF)    ARM_MEANING="FALLBACK -- the kill-and-resume REFERENCE, a 4-major probe, NOT the optimised state" ;;
  "")        say "D6R2C_RENDER_NO_ARM under $BASE"; exit 0 ;;
  # BEYOND THE TWO FIXES ASKED FOR, AND SAY SO.  Without this branch, an arm in
  # ARM_PREFERENCE with no label here renders with ARM_MEANING="" -- a picture of a fallback
  # state carrying an EMPTY caption, which is worse than the dead code being removed.
  *)         say "D6R2C_RENDER_ARM_UNLABELLED arm=$ARM -- ARM_PREFERENCE and the label table disagree; REFUSING rather than captioning a state with no meaning"; exit 0 ;;
esac
say "D6R2C_RENDER_ARM=$ARM ($ARM_MEANING)"

COPY="$BASE/D6R2C-RENDER-COPY-$STAMP"
mkdir -p "$COPY" || { say "D6R2C_RENDER_MKDIR_FAILED"; exit 0; }
HEAD_SHA=$(cd /home/ubuntu/Certonomous && git rev-parse HEAD 2>/dev/null || echo UNKNOWN)
IMAGES_TOTAL=0; SCEN_DONE=""

for mp in mp04 mp05 mp06; do
  SRC="$BASE/$ARM/$mp"
  [ -d "$SRC" ] || { say "D6R2C_RENDER_SCENARIO_ABSENT $mp"; continue; }
  cp -a "$SRC" "$COPY/$mp" || { say "D6R2C_RENDER_COPY_FAILED $mp"; continue; }
  # DECOMPOSED, AND DELIBERATELY NOT RECONSTRUCTED.  d6r2_render_prep.sh ran reconstructPar
  # in a container; ParaView reads processor* directly with CaseType='Decomposed Case', so no
  # reconstruct, no container and no solver binary runs at all.  Stricter on "zero solver
  # compute" than the precedent, and one fewer thing that can fail after the run is over.
  find "$COPY/$mp" -name '*.gz' -exec gunzip -q {} + 2>/dev/null
  TAG="D6R2C_${ARM}_${mp}_single-level_${STAMP}"
  # THE MEASURED FAILURE THIS ADDRESSES.  On copy 20260912T235607Z, mp05 produced 0 images
  # with rc=134 (SIGABRT) while mp04 and mp06 produced 6 each.  The abort is at 2.217s inside
  # vtkXOpenGLRenderWindow::CreateAWindow() -- "bad X server connection. DISPLAY=:99" -- i.e.
  # BEFORE any OpenFOAM reader exists, so it cannot be a field, a filter or a short input; the
  # mp05 copied tree is composition-identical to mp04/mp06 (same 13 entries, same 8 processor0
  # time dirs, same case.foam).  Mechanism: xvfb-run's clean_up() removes the Xauthority first
  # and kills Xvfb LAST, without waiting for it, so the next scenario's `-a` can re-select a
  # display the dying server still owns.  And xvfb-run defaults ERRORFILE=/dev/null, so Xvfb's
  # own reason was DISCARDED -- which is why render_mp05.log carries no diagnosis at all.
  #   -e   keeps that reason on disk instead of throwing it away.
  #   retry once, and settle after each scenario, so a lost display costs a retry, not a picture.
  # NEITHER CAN CHANGE A VERDICT.  A render is still not a gate and the wrapper still exits 0.
  RRC=0; N=0
  for attempt in 1 2; do
    timeout 1800 xvfb-run -a -e "$COPY/xvfb_${mp}_attempt${attempt}.err" \
      --server-args="-screen 0 1920x1440x24" \
      pvbatch "$RENDER_PY" --case "$COPY/$mp" --out "$COPY/png" --tag "$TAG" --decomposed \
      >> "$COPY/render_${mp}.log" 2>&1
    RRC=$?
    N=$(ls "$COPY/png/${TAG}"_*.png 2>/dev/null | wc -l)
    [ "$N" -gt 0 ] && break
    say "D6R2C_RENDER_SCENARIO_RETRY $mp attempt=$attempt rc=$RRC images=0 xvfb_err=$COPY/xvfb_${mp}_attempt${attempt}.err"
    sleep 20
  done
  sleep 5   # let this scenario's Xvfb finish dying before the next `-a` picks a server number
  IMAGES_TOTAL=$((IMAGES_TOTAL + N)); SCEN_DONE="$SCEN_DONE $mp"
  # THE rc IS NOT THE SUCCESS SIGNAL HERE AND SAYING SO IS NOT AN EXCUSE.  MEASURED on the
  # rehearsal: pvbatch prints `RENDER_REPORT ... images=8 errors=0`, writes every PNG, and
  # THEN exits 1 on `X Error ... GLXBadContext` during GL teardown under xvfb.  The work is
  # complete before the error occurs.  So the wrapper judges by the COUNTED IMAGES, which is
  # a measurement, and records the rc beside it rather than hiding it -- a reader who sees
  # rc=1 with images=8 must be able to tell which one means what.
  RCNOTE="rc_is_teardown_artifact_judge_by_images"
  [ "$N" -gt 0 ] || RCNOTE="NO_IMAGES_THIS_IS_A_REAL_RENDER_FAILURE"
  say "D6R2C_RENDER_SCENARIO $mp rc=$RRC images=$N note=$RCNOTE tag=$TAG"
done

# --- 4. THE SIDECAR.  Paths, ids and the honest level label, so the record can be read
#        without opening a single PNG -- and so nobody mistakes one mesh for a grid family.
python3 - "$COPY" "$BASE" "$ARM" "$ARM_MEANING" "$VERDICT" "$GRADE_JSON" "$HEAD_SHA" "$STAMP" "$IMAGES_TOTAL" "$CHAIN_RC" <<'PY' 2>>"$OUT"
import json, os, sys, glob
copy, base, arm, meaning, verdict, gjson, sha, stamp, ntot, chain_rc = sys.argv[1:11]
side = {
 "case_id": "D6R2C", "run_root": base, "render_copy": copy, "stamp_utc": stamp,
 "repo_head_at_render": sha, "chain_rc": chain_rc,
 "verdict_at_render_time": verdict, "grade_record": gjson or None,
 "arm_rendered": arm, "arm_meaning": meaning,
 "level_label": "single-level",
 "level_note": ("D6R2C IS AN OPTIMISATION ON ONE U-BEND MESH ACROSS THREE SCENARIOS AND HAS NO "
                "GRID FAMILY. Sanaa's instruction distinguishes a coarse/medium mesh from fine-mesh "
                "fields; THAT DISTINCTION HAS NO REFERENT HERE. Calling this mesh 'coarse' to match "
                "the shape of the instruction would be a label that looks compliant and is false."),
 "fields_are_from": ("the latest time of the arm above, i.e. the finest state this item has. There "
                     "is no finer mesh whose fields could be substituted."),
 "M_inf_note": ("The item id and its registration say TRANSONIC. Its own run script carries U0=100 "
                "and T0=300, giving M_inf = 0.288, and the rehearsal MEASURED a local Mach range of "
                "0.078-0.380 on a completed state -- NO SUPERSONIC REGION ANYWHERE. The render "
                "therefore shows Cp and local Mach and lets the data speak; it does NOT draw a shock "
                "that is not there. Reported to the supervisor, not resolved by this lane."),
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
p = os.path.join(copy, "D6R2C_RENDER_SIDECAR.json")
with open(p, "w") as f: json.dump(side, f, indent=2, sort_keys=True)
print("D6R2C_RENDER_SIDECAR %s images=%d" % (p, side["images_total"]))
PY

say "D6R2C_RENDER_DONE copy=$COPY images=$IMAGES_TOTAL scenarios=[$SCEN_DONE] verdict=$VERDICT"
exit 0   # DELIBERATE: a render is not a gate
