"""ROUTE PROBE -- NOT AN M6 MESH. See ROUTE_PROBE_NOT_AN_M6_MESH.md.

Answers one question: does pyHyp, given a capped multi-patch surface, produce a
volume that clears openness, face pyramids, boundary closure, non-orthogonality and
skewness?
"""
import sys, numpy as np

# ---------------------------------------------------------------------------
# GEOMETRY-AGNOSTIC COINCIDENT-POINT CHECK. It knows nothing about wings.
# WHY IT EXISTS: a zero-length edge surfaces as NaN in a quality column while pyHyp
# still prints "Normals are consistent" and "Topology complete" -- BOTH topology
# checks pass straight over it. So the check cannot read a log. It scans arrays and
# REFUSES with a nonzero exit before the extruder is invoked.
# ---------------------------------------------------------------------------
def coincident_points(patch, tol=1e-12):
    """patch: (ni, nj, 3). Returns count of adjacent-point pairs closer than tol."""
    d_i = np.linalg.norm(np.diff(patch, axis=0), axis=2)
    d_j = np.linalg.norm(np.diff(patch, axis=1), axis=2)
    return int((d_i < tol).sum() + (d_j < tol).sum())

def check(patches, tol=1e-12):
    tot = sum(coincident_points(p, tol) for p in patches)
    return tot

def planted_control(patches, tol=1e-12):
    """Inject a duplicate into a copy of a known-good patch; the checker MUST see it."""
    base = check(patches, tol)
    q = [p.copy() for p in patches]
    q[0][1, 0, :] = q[0][0, 0, :]                 # plant ONE duplicated point
    planted = check(q, tol)
    return base, planted, planted > base

from cgnsutilities.cgnsutilities import readGrid
g = readGrid("/data/A3-onera-m6-adjoint-coarse/m6_surfaceMesh_fine.cgns")
patches = [b.coords[:, :, 0, :].copy() for b in g.blocks]
print(f"  patches: {len(patches)}  shapes {[p.shape for p in patches]}", flush=True)

base, planted, ok = planted_control(patches)
print(f"  PLANTED CONTROL: clean surface -> {base} coincident pairs; "
      f"with ONE duplicate planted -> {planted}")
print(f"  CONTROL {'PASSES -- the checker is shown able to SEE the defect' if ok else 'FAILS'}")
if not ok:
    print("  REFUSED: a checker not shown able to see the defect is not a checker.")
    sys.exit(3)
if base > 0:
    print(f"  REFUSED: {base} coincident point pairs in the input surface.")
    sys.exit(4)
print("  surface is free of coincident points -> proceeding to extrusion", flush=True)

from pyhyp import pyHyp
opts = {
    # fileType is an ENUM for the input path only; `patches` supplies the surface.
    # With "CGNS" pyHyp still tries to open inputFile and dies on cgio_open_file.
    "inputFile": "", "fileType": "PLOT3D", "patches": patches,
    "unattachedEdgesAreSymmetry": True, "outerFaceBC": "farfield",
    "autoConnect": True, "BC": {}, "families": "wall",
    "N": 33, "s0": 1.0e-4, "marchDist": 12.0,
    "ps0": -1.0, "pGridRatio": -1.0, "cMax": 0.1,
    "epsE": 1.0, "epsI": 2.0, "theta": 3.0,
    "volCoef": 0.25, "volBlend": 0.0005, "volSmoothIter": 100,
    "kspRelTol": 1e-4,
}
h = pyHyp(options=opts)
h.run()
h.writeCGNS("/work/ROUTE_PROBE_vol.cgns")
print("  EXTRUSION COMPLETE", flush=True)
