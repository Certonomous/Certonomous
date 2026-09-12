#!/bin/bash
# RENDER-ON-COMPLETION -- Sanaa's standing directive, 2026-09-12, byte-exact:
#   "whenever a run completes, i want the paraview visualization of its mesh saved ...
#    The paraview should show the coarse mesh (or medium mesh if the coarse isnt
#    converged). But all fields should be stored as the fine mesh result fields
#    (whenever we have it)."
#
# WHY THIS IS A SCRIPT AND NOT A ONE-OFF: "if a render step cannot run unattended it will
# not happen the next time nobody is awake", which is the same failure as an unarmed
# grader.  It is idempotent, it takes the case from argv, and it needs no terminal.
#
# IT NEVER TOUCHES THE GRADED TREE.  Outputs go to <case>/../RENDERS/, never inside the
# solve.  The renderer it calls proves the graded tree untouched by census hash and says
# so in its own output.  It runs NO solver and costs NO solver time.
#
# HEADLESS: `xvfb-run -a pvbatch`.  NEVER --force-offscreen-rendering -- the renderer
# REFUSES that flag because it aborts on this ParaView build (its own note, :88).
# Established by reading scripts/render_dmr_paraview.sh and render_jf1_paraview.sh,
# which already carry this pattern; not rediscovered by trial.
#
# 🔴 MESH ONLY, AND THAT IS A MEASURED LIMIT, NOT AN OVERSIGHT.  `--field` is a SILENT
# NO-OP on at least the DrivAer cases: the `--field p` output and the plain mesh output
# carry IDENTICAL hue histograms and a single hue bin.  Cause: the renderer does
# ColorBy(d, ("POINTS", field)) and OpenFOAM writes `p` as a CELL field.  The renderer's
# per-patch face-count guard cannot catch it -- colouring is not a geometry property.
# Evidence and the suggested fix:
#   verification/runs/navier_class/DRIVAER/RENDERS/_FIELD_FLAG_DEFECT_EVIDENCE/DEFECT.md
# UNTIL THAT IS FIXED THIS SCRIPT CLAIMS NO FIELD RENDER.  A picture captioned "surface
# pressure" that is a flat-shaded body is exactly the confident-looking wrong artifact the
# guard exists to prevent.
set -u
REPO=/home/ubuntu/Certonomous
CASE="${1:?usage: render_on_completion.sh <case-dir> <prefix> <up:x|y|z> <patch-selector> [time]}"
PREFIX="${2:?}"; UP="${3:?}"; SEL="${4:?}"; TIME="${5:-latest}"
OUT="$(dirname "$CASE")/RENDERS"

# ---- 1. REFUSE to render a run that has not completed. A render of a live or dead run
#         is a picture of a non-result, and it travels further than the verdict does.
RC=""
for f in "$CASE/rc" "$CASE/RC.txt" "$CASE/solve_rc"; do
  [ -f "$f" ] && { RC=$(tr -dc '0-9' < "$f" | head -c3); break; }
done
if [ -z "$RC" ]; then echo "REFUSED: $CASE carries no rc sidecar -- not a completed run."; exit 2; fi
if [ "$RC" != "0" ]; then echo "REFUSED: $CASE rc=$RC, not a completed run."; exit 2; fi
if ! grep -qE "^End$" "$CASE"/log.* 2>/dev/null; then
  echo "REFUSED: no 'End' line in $CASE/log.* -- not a completed run."; exit 2; fi

# ---- 2. patch selector: 'vehicle' derives the body patches FROM THE CASE'S OWN boundary
#         file (the same file the renderer's guard checks against), never from a hand list.
if [ "$SEL" = "vehicle" ]; then
  PATCHES=$(python3 - "$CASE" <<'PY'
import re,sys
t=open(sys.argv[1]+"/constant/polyMesh/boundary").read()
names=re.findall(r"^\s{4}(\w+)\s*$", t, re.M)
DOMAIN={"inlet","outlet","top","sideMinus","sidePlus","floorSlip","floorNoSlip"}
print(",".join([n for n in names if n not in DOMAIN and not n.startswith("CTRL_SURFACE")]))
PY
)
else
  PATCHES="$SEL"
fi
[ -n "$PATCHES" ] || { echo "REFUSED: empty patch selection for $CASE"; exit 2; }

mkdir -p "$OUT"
echo "RENDER $CASE -> $OUT/${PREFIX}_surface.png  (time=$TIME, up=$UP, $(echo "$PATCHES" | tr ',' '\n' | wc -l) patches)"
xvfb-run -a pvbatch "$REPO/scripts/render_openfoam_3d_paraview.py" \
  --case "$CASE" --out "$OUT" --prefix "$PREFIX" --time "$TIME" --up "$UP" \
  --patches "$PATCHES" --resolution 1920x1080 2>&1 | grep -E "WROTE|REFUSED|dimensional"
exit ${PIPESTATUS[0]}
