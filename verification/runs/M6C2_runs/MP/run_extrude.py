"""M6C2 multi-patch capped hyperbolic extrusion -- ONE level.

THE SURFACE IS HANDED TO pyHyp IN MEMORY via `patches`. Two tools in this image are
broken for the file path and a planted control proved each (M6C1 Addendum 1 A1.4):
`cgns_utils plot3d2cgns` cannot read the output of its own sibling `cgns2plot3d`,
and the `cgnsutilities` CGNS writer rejects a 2-D zone whose dims match the
reference file's exactly. `patches` needs neither.

THE COINCIDENT-POINT SCAN RUNS AGAIN HERE, ON THE ARRAYS pyHyp WILL ACTUALLY SEE.
It already ran in `make_level.py` on the arrays as built. It runs a SECOND time on
the arrays as READ BACK FROM THE FILE, because the thing that must be free of
zero-length edges is what the extruder receives, not what the writer intended -- and
a formatted write-then-read at 15 significant digits is exactly where two points a
few 1e-16 apart become one.
"""
import sys, numpy as np

def read_plot3d(path):
    t = open(path).read().split()
    nb = int(t[0]); p = 1; dims = []
    for _ in range(nb):
        dims.append((int(t[p]), int(t[p+1]), int(t[p+2]))); p += 3
    out = []
    for (a, b, c) in dims:
        n = a*b*c
        arr = np.array(t[p:p+3*n], dtype=float); p += 3*n
        X = np.zeros((a, b, 3))
        for k in range(3):
            X[:, :, k] = arr[k*n:(k+1)*n].reshape(a, b, order="F")
        out.append(X)
    return out

def coincident(p, tol=1e-12):
    di = np.linalg.norm(np.diff(p, axis=0), axis=2)
    dj = np.linalg.norm(np.diff(p, axis=1), axis=2)
    return int((di < tol).sum() + (dj < tol).sum())

def scan(ps, tol=1e-12):
    return sum(coincident(p, tol) for p in ps)

surf, out, N, s0, marchDist = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
patches = read_plot3d(surf)
print(f"  patches read back from {surf}: {len(patches)}  shapes {[p.shape for p in patches]}", flush=True)

base = scan(patches)
q = [p.copy() for p in patches]; q[0][1, 0, :] = q[0][0, 0, :]
planted = scan(q)
print(f"  PLANT: clean {base} coincident pairs; one duplicate planted -> {planted}")
if not planted > base:
    print("  REFUSED (3): the coincident-point reader was not shown able to see a duplicate.")
    sys.exit(3)
if base > 0:
    print(f"  REFUSED (4): {base} coincident point pairs AFTER the file round-trip.")
    sys.exit(4)
print("  control passes; surface is clean after the round-trip -> extruding", flush=True)

from pyhyp import pyHyp
opts = {
    "inputFile": "", "fileType": "PLOT3D", "patches": patches,
    "unattachedEdgesAreSymmetry": True, "outerFaceBC": "farfield",
    "autoConnect": True, "BC": {}, "families": "wall",
    "N": N, "s0": s0, "marchDist": marchDist,
    "ps0": -1.0, "pGridRatio": -1.0, "cMax": 0.1,
    "epsE": 1.0, "epsI": 2.0, "theta": 3.0,
    "volCoef": 0.25, "volBlend": 0.0005, "volSmoothIter": 100,
    "kspRelTol": 1e-4,
}
print(f"  pyHyp: N={N} s0={s0:g} marchDist={marchDist:g}", flush=True)
h = pyHyp(options=opts)
h.run()
h.writeCGNS(out)
print("  EXTRUSION COMPLETE", flush=True)
