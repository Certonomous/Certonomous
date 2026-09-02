#!/usr/bin/env bash
# Regenerate the shock-reflection act's ParaView panels from the solved case.
#
# WHY THIS CASE NEEDS ITS OWN INVOCATION, AND IT IS NOT A STYLE CHOICE.
#
# The general renderer's default framing is an AIRFOIL framing: it opens the
# camera by fractions of the body patch's CHORD, which is correct for a body
# immersed in a far field and catastrophic when the "body" is the domain's own
# floor.  Measured on this case: the domain is 4.000 x 1.000 m, the wall patch
# runs x = 0.1667 .. 4.000 (chord 3.833), and the chord framing produces a
# 8.050 x 4.217 m window in which the channel covers 11.8% of the frame area --
# Sanaa's "thumbnail the size of a coin in an empty panel", 2026-09-01.  No ink
# check can see that: 11.8% of a frame is a great deal of ink.
#
# So this case is rendered with --frame domain (camera off the mesh's own
# bounds) and --geometry-mode domain (the STL-less drawing: domain outline,
# marked wall patch, and the initial shock line READ from the case's own
# setExprFieldsDict).  There is no STL here and there never was one worth
# drawing: the domain is a channel with a wall along part of its floor.
#
# THE CASE AND THE CELL COUNT COME FROM THE ACT, never from a default written
# here -- the JF1 script's default named the wrong case for a week and only a
# provenance assertion caught it.  An explicit case may be passed as $1 and it
# must AGREE with the act.
#
# THE ZOOM CENTRE COMES FROM THE CASE'S OWN LOCATOR, not from a typed guess:
# locator_result.json records where the Mach stem meets the wall at the final
# time, which is the "cells along the wall where the shock strikes" the act's
# meshing stage promises.
#
# ParaView 5.11.2 (the distro build at /usr/bin/pvbatch) under a virtual
# framebuffer.  The official 5.13.2 osmesa tarball under /home/ubuntu/tools
# segfaults at Render on this box with both swr and llvmpipe -- do not use it.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DECL="$(python3 - "$REPO" <<'PY'
import json
import math
import sys
from pathlib import Path

repo = Path(sys.argv[1])
sys.path.insert(0, str(repo / "sdk"))
from workflows.dmr_act import ShockReflectionAct         # noqa: E402

plan = ShockReflectionAct().mesh_plan()
source = Path(plan.cell_count.source)
if source.name != "polyMesh":
    raise SystemExit(f"the act cites {source}, which is not a polyMesh")
cells = "".join(ch for ch in str(plan.cell_count.value) if ch.isdigit())
if not cells:
    raise SystemExit(f"the act's cell count {plan.cell_count.value!r} carries no digits")
case = source.parent.parent

# The wall patch the act names as its body is the wall this drawing marks.
wall = plan.wall_patch or ""
if not wall:
    raise SystemExit("the act names no wall patch, so nothing could be marked")

# The zoom rectangle, centred on the MEASURED shock foot and given the same
# aspect as the wide frame, so the zoom fills its image exactly as the wide
# panel fills its own.  A zoom box with a different aspect would be letterboxed
# inside a frame this whole exercise exists to fill.
locator = case / "locator_result.json"
if not locator.is_file():
    raise SystemExit(f"{locator} is missing; the zoom centre would have to be guessed")
record = json.loads(locator.read_text())
final = max(record["locates"], key=lambda r: r["t"])
x_foot = float(final["jet"]["stem_wall_x"])

MARGIN = 0.02
with (case / "system" / "blockMeshDict").open() as handle:
    text = handle.read()
# The domain extent is read off the mesh by the renderer itself; here it is only
# needed to size the zoom, and the renderer's own bounds are the authority for
# everything that reaches an image.
xs, ys = [], []
for line in text.splitlines():
    line = line.strip()
    if line.startswith("(") and line.count("(") >= 1 and ";" not in line:
        for chunk in line.replace(")", " ) ").replace("(", " ( ").split(")"):
            parts = chunk.replace("(", " ").split()
            if len(parts) == 3:
                try:
                    x, y, _z = (float(p) for p in parts)
                except ValueError:
                    continue
                xs.append(x)
                ys.append(y)
if not xs:
    raise SystemExit(f"could not read vertices from {case/'system'/'blockMeshDict'}")
span_x = (max(xs) - min(xs)) * (1.0 + 2.0 * MARGIN)
span_y = (max(ys) - min(ys)) + 2.0 * MARGIN * max(max(xs) - min(xs), max(ys) - min(ys))
aspect = span_x / span_y

ZOOM_H = 0.25
zoom_w = ZOOM_H * aspect
ylo = -0.02
print(case)
print(cells)
print(wall)
print("%.6f,%.6f,%.6f,%.6f" % (x_foot - 0.5 * zoom_w, x_foot + 0.5 * zoom_w,
                               ylo, ylo + ZOOM_H))
# NO "m" ON THE EXTENT.  This is the classic DIMENSIONLESS double-Mach
# configuration (density 1.4 to 20 over a sound speed of one), and Sanaa's
# 2026-09-02 ~02:32Z order strikes every metre and second tag from its
# screens: a Mach 10 shock crossing "2 metres in 0.2 seconds" is 10 m/s.
# The lengths are reference units and the key states the bare numbers.
print("%.3f x %.3f" % (max(xs) - min(xs), max(ys) - min(ys)))
# The act's OWN rendering of the count, separators and all, so the key on the
# picture and the number on the screen beside it are the same string.
print(str(plan.cell_count.value))
PY
)"
CASE_DECLARED="$(printf '%s\n' "$DECL" | sed -n 1p)"
EXPECT_CELLS="$(printf '%s\n' "$DECL" | sed -n 2p)"
WALL_PATCH="$(printf '%s\n' "$DECL" | sed -n 3p)"
ZOOM_BOX="$(printf '%s\n' "$DECL" | sed -n 4p)"
DOMAIN="$(printf '%s\n' "$DECL" | sed -n 5p)"
CELLS_SHOWN="$(printf '%s\n' "$DECL" | sed -n 6p)"

CASE="${1:-$CASE_DECLARED}"
if [ "$(cd "$CASE" && pwd)" != "$(cd "$CASE_DECLARED" && pwd)" ]; then
    echo "REFUSED: the case passed on the command line is not the case the act" >&2
    echo "  cites for the cell count it puts on screen, so the panels rendered" >&2
    echo "  here would disagree with that number." >&2
    echo "  passed: $CASE" >&2
    echo "  act   : $CASE_DECLARED" >&2
    exit 2
fi
OUT="${2:-$CASE/paraview}"
TIME="${3:-latest}"
IC="$CASE/system/setExprFieldsDict"

echo "rendering the act's own case, $EXPECT_CELLS cells expected: $CASE"
echo "  domain $DOMAIN   wall patch $WALL_PATCH   zoom box $ZOOM_BOX"

# The key lines are NUMBERS, SYMBOLS AND UNITS, per Sanaa 2026-09-01; caption
# prose is the act's and is not written into an image.  Each is coloured to
# match the thing it names, which is what makes it a key rather than a label.
xvfb-run -a pvbatch "$REPO/scripts/render_openfoam_paraview.py" \
    --case "$CASE" --out "$OUT" --time "$TIME" \
    --frame domain --geometry-mode domain --domain-margin 0.02 \
    --resolution fit:2560 \
    --mark-patches "$WALL_PATCH" \
    --initial-condition "$IC" \
    --zoom-box "$ZOOM_BOX" \
    --annotate "text|$DOMAIN   ·   $CELLS_SHOWN cells" \
    --annotate "body|$WALL_PATCH" \
    --annotate "slot|t = 0   x = 1/6 + y/sqrt(3)" \
    --expect-cells "$EXPECT_CELLS" \
    --panels geometry,mesh,mesh_zoom --theme dark

# The planted-zero control, re-proved on every regeneration -- and it now also
# proves the INITIAL-CONDITION reader can produce both of its verdicts: a
# planted line read back to the last digit, and a dict declaring no
# discontinuity in x REFUSED.  Exits 2 if either verdict is missing, which
# -euo pipefail turns into a failed regeneration.
xvfb-run -a pvbatch "$REPO/scripts/render_openfoam_paraview.py" \
    --case "$CASE" --out "$OUT" --time "$TIME" \
    --frame domain --geometry-mode domain \
    --mark-patches "$WALL_PATCH" --initial-condition "$IC" \
    --expect-cells "$EXPECT_CELLS" --selftest
