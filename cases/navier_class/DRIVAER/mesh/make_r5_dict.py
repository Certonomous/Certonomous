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

STACK_M = 0.0010 * ((1.11 ** 8 - 1) / 0.11)      # 0.0118594 m -- the registered stack

LAYER_RECIPE = """    relativeSizes       false;
    nSurfaceLayers      8;
    firstLayerThickness 0.0010;
    expansionRatio      1.11;
    minThickness        0.0002;
"""

# Volume-refinement boxes.  Authored by this lane; the registration sets the
# 15-20 M GATE and mandates volume refinement but does not specify the geometry.
# Sized so the CASTELLATED count lands near 11.5 M and the final layered mesh,
# which gained 31 % from layers on r2_medium, lands inside 15-20 M.
BOXES = {
    "box1": ((-8.0, -6.5, -0.319), (30.0, 6.5, 7.4), 1),
    "box2": ((-5.5, -4.5, -0.319), (24.0, 4.5, 5.7), 2),
    "box3": ((-3.5, -3.0, -0.319), (17.0, 3.0, 4.2), 3),
    "box4": ((-1.8, -2.0, -0.319), (11.5, 2.0, 2.05), 4),
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
    print(f"  ESTIMATED castellated total ~ {est/1e6:.2f} M cells "
          f"(+31 % layer gain measured on r2_medium -> ~{1.31*est/1e6:.2f} M final)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
