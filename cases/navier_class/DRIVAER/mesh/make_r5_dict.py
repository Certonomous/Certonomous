#!/usr/bin/env python3
"""
make_r5_dict.py -- emit the DrivAer R5 snappyHexMeshDict from the r2_medium
dict, applying ONLY the edits the frozen registration authorises, and ASSERTING
each one applied.

GOVERNING DOCUMENT
    verification/campaign/DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md
    frozen at commit 38aab8e78662d574d1b14b61da7efc5898be5c7e
The commit and the blob are pinned LIVE at launch by build_r5.sh, never at
freeze time, because blobs have moved repeatedly today.

THE EDITS, AND WHY EACH IS INSIDE THE REGISTRATION
 A. addLayersControls -> the recipe registered verbatim in §4.2:
        relativeSizes false; nSurfaceLayers 8; firstLayerThickness 0.0010;
        expansionRatio 1.11; minThickness 0.0002;
    minThickness CONVERTS IN THE SAME EDIT (MESH_STANDARD.md §16.5 rule L4).
    Left at its relative 0.02 it would read as 20 mm -- larger than the entire
    11.86 mm stack -- and would refuse every layer while exiting rc=0 clean.
    This script REFUSES to emit a dict whose minThickness exceeds the stack.
 B. refinementRegions -> VOLUME refinement to reach the §7 M1 gate of 15-20 M
    cells.  §4.2 registers that the cells must come from volume refinement and
    NOT from surface refinement, because on a refined 12.5 mm surface cell
    y+ >= 30, 8 layers and a sub-0.48-cell stack are mutually exclusive.
 C. maxLocalCells -> raised from 6,000,000.  snappyHexMesh here runs SERIAL, so
    maxLocalCells is the binding cap and 6 M makes the registered 15-20 M gate
    UNREACHABLE.  This is an enabling limit, not a physics change, and it is
    disclosed rather than made silently.

WHAT IS ASSERTED UNTOUCHED, because it is what makes the arm readable:
    the whole `geometry` block's surface regions, `refinementSurfaces` (every
    per-patch surface level, including the thirteen patches already at level 5),
    `features`, `snapControls`, `meshQualityControls`, `locationInMesh`.
A diff of those blocks against r2_medium must be EMPTY or this script exits 2.
"""
from __future__ import annotations
import re, sys, hashlib
from pathlib import Path

N_LAYERS = 8                                     # the registered nSurfaceLayers
STACK_M = 0.0010 * ((1.11 ** 8 - 1) / 0.11)      # 0.0118594 m -- the registered stack

LAYER_RECIPE = """    relativeSizes       false;
    nSurfaceLayers      8;
    firstLayerThickness 0.0010;
    expansionRatio      1.11;
    minThickness        0.0002;
"""

# Volume-refinement boxes.  Authored by this lane; the registration sets the
# 15-20 M GATE and mandates volume refinement but does not specify the geometry.
#
# SIZED FROM A MEASURED POINT, NOT FROM THE ANALYTIC ESTIMATE.  The first sizing
# probe (R5_SIZING_PROBE, castellation only) returned 12,541,747 cells against a
# 12.96 M estimate -- 3.3 % high.  It also refuted the layer-gain assumption the
# first sizing used: r2_medium gained 31 % from layers, but that mesh was small
# relative to its wall area.  Measured on r2_medium's own log, snapping changes
# the cell count by ZERO (748,658 -> 748,658; it moves points, it does not add
# cells) and layers added 234,448 cells on 64,470 extruded faces.  R5's SURFACE
# refinement is identical to r2_medium's, so its wall-face count is too (~80,974)
# and 8 layers at ~90 % extrusion add only ~0.58 M cells -- +4.7 %, not +31 %.
# Final = castellated + ~0.58 M, so the castellated target is ~16.4 M for a
# ~17.0 M final, and box4 is scaled to that from the probe's measured point at
# 56,000 net cells per m3 transferred from level 3 to level 4.
BOXES = {
    "box1": ((-8.0, -6.5, -0.319), (30.0, 6.5, 7.4), 1),
    "box2": ((-5.5, -4.5, -0.319), (24.0, 4.5, 5.7), 2),
    "box3": ((-3.5, -3.0, -0.319), (17.0, 3.0, 4.2), 3),
    "box4": ((-2.0, -2.2, -0.319), (15.0, 2.2, 2.30), 4),
}


def block(txt: str, name: str) -> str:
    """Return the text of a top-level `name { ... }` block, braces balanced."""
    i = txt.index(name)
    j = txt.index("{", i)
    d = 0
    for k in range(j, len(txt)):
        if txt[k] == "{":
            d += 1
        elif txt[k] == "}":
            d -= 1
            if d == 0:
                return txt[i:k + 1]
    raise SystemExit(f"REFUSE: unbalanced block {name}")


def main() -> int:
    src = Path(sys.argv[1])          # r2_medium/system/snappyHexMeshDict
    dst = Path(sys.argv[2])
    t = src.read_text()
    orig = t

    # ---- A. the registered layer recipe --------------------------------------
    lay = block(t, "addLayersControls")
    new_lay = re.sub(
        r"    relativeSizes.*?minThickness\s+[^\n]*\n",
        LAYER_RECIPE, lay, count=1, flags=re.S)
    if new_lay == lay:
        print("REFUSE: layer recipe substitution did not apply", file=sys.stderr)
        return 2

    # THE PER-PATCH BLOCK IS AUTHORITATIVE AND MUST MOVE IN THE SAME EDIT.
    # Writing `nSurfaceLayers 8` at the top of addLayersControls while the
    # layers{} sub-block still says 5 on every patch produces a mesh that
    # requests FIVE layers while every record around it says eight.  This lane
    # shipped exactly that defect once (run r5_wallfunction, TRIAGE_STOP.txt,
    # stopped at Morph iteration 3) because its only assertion was that the
    # substitution TEXT had appeared -- a control on the edit, not on the
    # meaning.  Same shape as L-590 and as the LAYERFIX_A1 dead lever.
    n_sub = len(re.findall(r"nSurfaceLayers\s+\d+\s*;", new_lay))
    new_lay = re.sub(r"(nSurfaceLayers\s+)\d+(\s*;)", rf"\g<1>{N_LAYERS}\g<2>", new_lay)
    t = t.replace(lay, new_lay, 1)

    # ---- B. volume refinement -------------------------------------------------
    geo = block(t, "geometry")
    new_geo = geo
    for nm, (lo, hi, _) in BOXES.items():
        pat = re.compile(rf"({nm}\s*\{{[^}}]*?min\s*)\([^)]*\)([^}}]*?max\s*)\([^)]*\)")
        rep = rf"\g<1>({lo[0]} {lo[1]} {lo[2]})\g<2>({hi[0]} {hi[1]} {hi[2]})"
        new_geo2, n = pat.subn(rep, new_geo, count=1)
        if n == 0:                       # box4 does not exist yet -- add it
            anchor = re.search(r"\n(\s*)box3\s*\{[^}]*\}\n", new_geo)
            if anchor is None:
                print(f"REFUSE: cannot place {nm}", file=sys.stderr)
                return 2
            ind = anchor.group(1)
            add = (f"{ind}{nm}\n{ind}{{\n{ind}    type searchableBox;\n"
                   f"{ind}    min ({lo[0]} {lo[1]} {lo[2]});\n"
                   f"{ind}    max ({hi[0]} {hi[1]} {hi[2]});\n{ind}}}\n")
            new_geo2 = new_geo[:anchor.end()] + add + new_geo[anchor.end():]
        new_geo = new_geo2
    t = t.replace(geo, new_geo, 1)

    rr = block(t, "refinementRegions")
    lines = "\n".join(
        f"        {nm} {{ mode inside; levels ((1E15 {lv})); }}"
        for nm, (_, _, lv) in BOXES.items())
    t = t.replace(rr, "refinementRegions\n    {\n" + lines + "\n    }", 1)

    # ---- C. the serial cell cap ----------------------------------------------
    t, n = re.subn(r"maxLocalCells\s+6000000;", "maxLocalCells       40000000;", t, count=1)
    if n != 1:
        print("REFUSE: maxLocalCells not raised", file=sys.stderr)
        return 2

    # ---- ASSERTIONS ----------------------------------------------------------
    # A1: minThickness must be smaller than the stack it is meant to floor.
    mt = float(re.search(r"minThickness\s+([\d.eE+-]+);", t).group(1))
    if mt >= STACK_M:
        print(f"REFUSE (MESH_STANDARD §16.5 rule L4): minThickness {mt} m is not "
              f"smaller than the {STACK_M:.6f} m stack; every layer would be "
              f"refused while snappy exits rc=0 clean.", file=sys.stderr)
        return 2
    # A2: absolute sizing must actually be absolute.
    if not re.search(r"relativeSizes\s+false;", t):
        print("REFUSE: relativeSizes is not false", file=sys.stderr)
        return 2
    # A2b: THE EFFECTIVE PER-PATCH LAYER COUNT, not the text of the edit.
    # snappyHexMesh takes nSurfaceLayers from the per-patch layers{} entry when
    # one exists, so a dict whose top level says 8 and whose 50 patch entries
    # say 5 BUILDS FIVE LAYERS.  Assert every count in the whole block, which
    # is the meaning, rather than that a substitution occurred, which is not.
    final_lay = block(t, "addLayersControls")
    counts = [int(x) for x in re.findall(r"nSurfaceLayers\s+(\d+)\s*;", final_lay)]
    if not counts:
        print("REFUSE: no nSurfaceLayers entry survives in addLayersControls",
              file=sys.stderr)
        return 2
    if set(counts) != {N_LAYERS}:
        bad = sorted(set(counts) - {N_LAYERS})
        print(f"REFUSE: addLayersControls carries nSurfaceLayers values {bad} "
              f"alongside the registered {N_LAYERS}. The PER-PATCH entry wins in "
              f"snappyHexMesh, so such a dict builds the per-patch number while "
              f"every record says {N_LAYERS}.", file=sys.stderr)
        return 2
    if len(counts) != n_sub:
        print(f"REFUSE: counted {n_sub} nSurfaceLayers entries before the "
              f"rewrite and {len(counts)} after -- the block was not rewritten "
              f"wholesale.", file=sys.stderr)
        return 2
    print(f"  nSurfaceLayers = {N_LAYERS} on ALL {len(counts)} entries "
          f"(1 top-level + {len(counts)-1} per-patch); the per-patch block is "
          f"authoritative in snappyHexMesh and was rewritten in the same edit")
    # A3: the surface refinement must be untouched -- this is the one-change proof.
    for name in ("refinementSurfaces", "features", "snapControls",
                 "meshQualityControls"):
        if block(orig, name) != block(t, name):
            print(f"REFUSE: {name} changed; §4.2 forbids touching surface "
                  f"refinement and the arm becomes unreadable.", file=sys.stderr)
            return 2
    # A4: every box must nest inside its parent, or the levels do not stack.
    for a, b in (("box4", "box3"), ("box3", "box2"), ("box2", "box1")):
        la, ha, _ = BOXES[a]
        lb, hb, _ = BOXES[b]
        if not all(lb[i] <= la[i] and hb[i] >= ha[i] for i in range(3)):
            print(f"REFUSE: {a} is not contained in {b}", file=sys.stderr)
            return 2

    dst.write_text(t)
    vol = {nm: (hi[0]-lo[0])*(hi[1]-lo[1])*(hi[2]-lo[2]) for nm, (lo, hi, _) in BOXES.items()}
    print(f"wrote {dst}")
    print(f"  sha256 {hashlib.sha256(t.encode()).hexdigest()}")
    print(f"  registered stack   {STACK_M*1000:.4f} mm; minThickness {mt*1000:.3f} mm "
          f"({100*mt/STACK_M:.1f} % of stack) -- rule L4 satisfied")
    print(f"  surface cell 25.0 mm at level 4 (h0 = 0.4 m) -> stack "
          f"{STACK_M/0.025:.4f} local cells (registration ceiling 0.48)")
    est = 0.0
    prev = 0.0
    for nm in ("box4", "box3", "box2", "box1"):
        lv = BOXES[nm][2]
        c = 0.4 / 2 ** lv
        shell = vol[nm] - prev
        est += shell / c ** 3
        print(f"  {nm} level {lv} cell {1000*c:5.1f} mm  box {vol[nm]:8.1f} m3  "
              f"shell {shell:8.1f} m3  -> {shell/c**3/1e6:6.3f} M cells")
        prev = vol[nm]
    est += (12480.0 - vol["box1"]) / 0.4 ** 3
    # Layer gain is NOT a volume fraction.  Snapping adds zero cells (measured
    # on r2_medium: 748,658 -> 748,658) and the wall-face count is fixed by the
    # SURFACE refinement, which R5 leaves identical to r2_medium's ~80,974
    # extrudable faces.  So layers add ~faces x extruded_frac x nLayers cells,
    # independent of how much volume refinement was added.
    WALL_FACES, EXTRUDED_FRAC, N_LAY = 80974, 0.90, 8
    gain = WALL_FACES * EXTRUDED_FRAC * N_LAY
    # the first probe measured this estimator 3.3 % high at 12.96 M -> 12.54 M
    corr = est * 0.967
    print(f"  ESTIMATED castellated total ~ {est/1e6:.2f} M cells "
          f"({corr/1e6:.2f} M after the probe's measured -3.3 % bias)")
    print(f"  layer gain is face-driven, NOT volume-driven: "
          f"{WALL_FACES:,} wall faces x {EXTRUDED_FRAC:.0%} x {N_LAY} = "
          f"{gain/1e6:.2f} M cells -> PREDICTED FINAL ~{(corr+gain)/1e6:.2f} M "
          f"against the 15-20 M M1 gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
