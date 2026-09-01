#!/usr/bin/env bash
# Regenerate the JF1 jet-flap act's ParaView panels from the solved case.
#
# THE CASE IS NOT NAMED HERE. IT IS READ FROM THE ACT.
#
# It used to be a default written into this file, and that default was WRONG:
# it named the C_mu = 0.10 case while the act's on-screen cell count cites the
# C_mu = 0.20 case. Nothing was false on screen at the time, because nothing
# yet compared the two; the moment the display grew an assertion that the
# panel's provenance must match the count the act prints, the mismatch surfaced
# on its first run.  Re-rendering from the cited case repaired the symptom and
# left the cause: a default that is right today and wrong tomorrow, waiting for
# the next person to regenerate.
#
# So the case and the expected cell count now come from the SAME declaration
# the act cites -- MeshPlan.cell_count, its source and its value -- and this
# script fails rather than falling back to any default. An explicit case may
# still be passed as $1, and it must AGREE with the act: an override that can
# silently disagree is the defect this paragraph exists to remove.
#
# --expect-cells closes the render end of the same guard: the campaign also
# holds a 46,180-cell C-mesh on a reference area 100x different, and the two
# must never share a screen or a caption.
#
# ParaView 5.11.2 (the distro build at /usr/bin/pvbatch) under a virtual
# framebuffer.  The official 5.13.2 osmesa tarball under /home/ubuntu/tools
# segfaults at Render on this box with both swr and llvmpipe -- do not use it.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# The act's own declaration, read once. `set -e` turns any failure here -- a
# broken import, an unreadable run tree -- into a stopped regeneration rather
# than a render of whatever a default happened to name.
DECL="$(python3 - "$REPO" <<'PY'
import sys
from pathlib import Path

repo = Path(sys.argv[1])
sys.path.insert(0, str(repo / "sdk"))
from workflows.jet_flap_act import JetFlapAct          # noqa: E402

count = JetFlapAct().mesh_plan().cell_count
source = Path(count.source)
if source.name != "polyMesh":
    raise SystemExit(f"the act cites {source}, which is not a polyMesh")
cells = "".join(ch for ch in str(count.value) if ch.isdigit())
if not cells:
    raise SystemExit(f"the act's cell count {count.value!r} carries no digits")
print(source.parent.parent)
print(cells)
PY
)"
CASE_DECLARED="$(printf '%s\n' "$DECL" | sed -n 1p)"
EXPECT_CELLS="$(printf '%s\n' "$DECL" | sed -n 2p)"

CASE="${1:-$CASE_DECLARED}"
if [ "$(cd "$CASE" && pwd)" != "$(cd "$CASE_DECLARED" && pwd)" ]; then
    echo "REFUSED: the case passed on the command line is not the case the act" >&2
    echo "  cites for the cell count it puts on screen, so the panels rendered" >&2
    echo "  here would disagree with that number." >&2
    echo "  passed: $CASE" >&2
    echo "  act    : $CASE_DECLARED" >&2
    echo "  To render some other case deliberately, call" >&2
    echo "  scripts/render_openfoam_paraview.py directly; it is the general" >&2
    echo "  tool and makes no claim about what is on the act's screen." >&2
    exit 2
fi
OUT="${2:-$CASE/paraview}"
TIME="${3:-latest}"

echo "rendering the act's own case, $EXPECT_CELLS cells expected: $CASE"

xvfb-run -a pvbatch "$REPO/scripts/render_openfoam_paraview.py" \
    --case "$CASE" --out "$OUT" --time "$TIME" \
    --body-patch airfoil --zoom-patch jetSlot \
    --expect-cells "$EXPECT_CELLS" --panels all --theme dark

# The planted-zero control, re-proved on every regeneration: the blank check has
# to produce BOTH verdicts here, or no "the render is fine" it reports is worth
# anything.  It writes into <out>/_selftest and exits 2 if either verdict is
# missing, which -euo pipefail turns into a failed regeneration.
xvfb-run -a pvbatch "$REPO/scripts/render_openfoam_paraview.py" \
    --case "$CASE" --out "$OUT" --time "$TIME" \
    --body-patch airfoil --zoom-patch jetSlot \
    --expect-cells "$EXPECT_CELLS" --selftest
