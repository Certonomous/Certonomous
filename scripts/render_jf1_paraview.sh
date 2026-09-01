#!/usr/bin/env bash
# Regenerate the JF1 jet-flap act's ParaView panels from the solved case.
#
# THE CASE IS NAMED HERE AND NOWHERE ELSE, and it is the 39,984-cell O-mesh the
# five-row blowing sweep was integrated on.  The campaign also holds a
# 46,180-cell C-mesh on a reference area 100x different; the two must never
# share a screen or a caption, so --expect-cells makes the wrong grid a refusal
# rather than a mis-caption.
#
# ParaView 5.11.2 (the distro build at /usr/bin/pvbatch) under a virtual
# framebuffer.  The official 5.13.2 osmesa tarball under /home/ubuntu/tools
# segfaults at Render on this box with both swr and llvmpipe -- do not use it.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CASE="${1:-$REPO/verification/runs/JF1_jet_flap/JF1_L1_BLOWN_CMU010_A0}"
OUT="${2:-$CASE/paraview}"
TIME="${3:-latest}"

xvfb-run -a pvbatch "$REPO/scripts/render_openfoam_paraview.py" \
    --case "$CASE" --out "$OUT" --time "$TIME" \
    --body-patch airfoil --zoom-patch jetSlot \
    --expect-cells 39984 --panels all --theme dark

# The planted-zero control, re-proved on every regeneration: the blank check has
# to produce BOTH verdicts here, or no "the render is fine" it reports is worth
# anything.  It writes into <out>/_selftest and exits 2 if either verdict is
# missing, which -euo pipefail turns into a failed regeneration.
xvfb-run -a pvbatch "$REPO/scripts/render_openfoam_paraview.py" \
    --case "$CASE" --out "$OUT" --time "$TIME" \
    --body-patch airfoil --zoom-patch jetSlot \
    --expect-cells 39984 --selftest
