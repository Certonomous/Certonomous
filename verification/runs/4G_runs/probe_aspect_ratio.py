"""Aspect-ratio probe used for roadmap 4G.

Reads OpenFOAM's own `aspectRatio` field (written by `checkMesh -writeAllFields`)
together with cell centres (`postProcess -func writeCellCentres`) and reports the
global maximum, its location, and the maximum restricted to a region of interest.

The point of the region restriction: on every wall-resolved grid examined in 4G the
global maximum sits in the far field, while the near field -- the only part the forces
depend on -- is orders of magnitude healthier. See
`demo-output/website/campaign/4G_tmr_mesh_aspect_ratio.md`.

IMPORTANT, on reading the numbers
--------------------------------
`checkMesh`'s aspect ratio is NOT the same quantity on 2D and 3D meshes.
`primitiveMeshTools::cellClosedness` gates its directional loop on `meshD[dir] == 1`
(`meshD` = `geometricD()`), so an `empty`-patched 2D mesh EXCLUDES the span and reports
pure in-plane stretching, while a 3D mesh INCLUDES it and additionally takes a
volume-based branch. Check which you have before comparing::

    grep "geometric (non-empty" log.checkMesh

Regenerating every mesh 4G measured (the meshes themselves are not committed; ~309 MB)
--------------------------------------------------------------------------------------
Flat plate (5 rungs) and bump (3 rungs), from the workflow's own generators::

    import sys; sys.path.insert(0, "/home/ubuntu/Certonomous/sdk")
    from workflows import tmr_verification as T
    from pathlib import Path
    root = Path("/tmp/ar")
    for lv in list(T.LEVELS) + list(T.FINEST_LEVELS):
        T.write_case(root / "flatplate", lv)
    for lv in T.BUMP_LEVELS:
        T.write_bump_case(root / "bump", lv)

then in each case directory::

    openfoam2606 -c "blockMesh; checkMesh -allGeometry -writeAllFields; \
                     postProcess -func writeCellCentres"

NASA's own TMR grids (models/tmr/naca0012/grids/n0012_{113-33,225-65,449-129}.p3dfmt)::

    openfoam2606 -c "plot3dToFoam -noBlank grid.p3dfmt; autoPatch 80 -overwrite"
    # then set the two span patches (those whose nFaces == nCells) to empty:
    openfoam2606 -c "foamDictionary -entry entry0/<patch>/type -set empty \
                     constant/polyMesh/boundary"
    openfoam2606 -c "checkMesh -allGeometry -writeAllFields; \
                     postProcess -func writeCellCentres"

Note the NACA meshes put the span on **y**, so the in-plane coordinates are (Cx, Cz),
not (Cx, Cy). The flat-plate and bump meshes put the span on z; in-plane is (Cx, Cy).

Fields land in `0/` when the case has one and in `constant/` when it does not, and may
be gzipped -- `read_scalar` handles all three.
"""

import gzip
import re
from pathlib import Path


def read_scalar(path):
    """Read an OpenFOAM ASCII volScalarField internalField, gzipped or not."""
    p = Path(path)
    text = p.read_text() if p.exists() else gzip.open(str(p) + ".gz", "rt").read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(", text)
    if not m:
        raise ValueError(f"no nonuniform scalar list in {p}")
    start = m.end()
    return [float(x) for x in text[start:text.index(")", start)].split()]


def field_dir(case):
    """Metric fields land in 0/ or constant/ depending on whether the case has a 0/."""
    case = Path(case)
    for sub in ("0", "constant"):
        d = case / sub
        if (d / "aspectRatio").exists() or (d / "aspectRatio.gz").exists():
            return d
    raise FileNotFoundError(f"no aspectRatio field under {case}")


def analyse(case, label, span="z", region=None, region_label="region"):
    """Report max aspect ratio, its location, and the max inside `region`.

    `span` is the empty/one-cell direction, so the in-plane pair is the other two.
    `region` is a predicate on the in-plane (a, b) coordinates.
    """
    d = field_dir(case)
    ar = read_scalar(d / "aspectRatio")
    cx, cy, cz = (read_scalar(d / f"C{c}") for c in "xyz")
    a, b = {"z": (cx, cy), "y": (cx, cz), "x": (cy, cz)}[span]

    n = len(ar)
    i = max(range(n), key=lambda j: ar[j])
    print(f"\n### {label}  ({n} cells, span={span})")
    print(f"  max aspect ratio = {ar[i]:.4f}  at ({a[i]:.6g}, {b[i]:.6g})")
    for thr in (1e3, 1e4, 1e5, 1e6, 1e7):
        c = sum(1 for v in ar if v > thr)
        if c:
            print(f"    cells above {thr:.0g}: {c} ({100.0 * c / n:.1f}%)")
    if region is not None:
        sel = [j for j in range(n) if region(a[j], b[j])]
        if sel:
            print(f"    within {region_label}: {len(sel)} cells, "
                  f"max = {max(ar[j] for j in sel):.1f}")
    return ar, a, b


if __name__ == "__main__":
    import math
    import sys

    root = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ar")

    for lv in ("coarse", "medium", "fine", "finer", "finest"):
        p = root / "flatplate" / lv
        if p.exists():
            analyse(p, f"flatplate/{lv}", span="z")
    for lv in ("coarse", "medium", "fine"):
        p = root / "bump" / lv
        if p.exists():
            # the bump wall is only x in [0, 1.5]; everything else is symmetry plane
            analyse(p, f"bump/{lv}", span="z",
                    region=lambda x, y: 0.0 <= x <= 1.5,
                    region_label="bump wall band x in [0, 1.5]")
    for lv, nodes in (("coarse", "113x33"), ("medium", "225x65"), ("fine", "449x129")):
        p = root / "nasa" / lv
        if p.exists():
            # NASA C-grid: span is y, so in-plane is (x, z); forces come from r < 1 chord
            analyse(p, f"NASA TMR NACA0012 {nodes}", span="y",
                    region=lambda x, z: math.hypot(x, z) < 1.0,
                    region_label="1 chord of the airfoil")
