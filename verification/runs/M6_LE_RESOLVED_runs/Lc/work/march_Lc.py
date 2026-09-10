"""Coarsest-Lc y+~35 hyperbolic march of the CAPPED surface (all 9 zones, autoConnect).
Provisional march params (lane, 2026-09-10; supervisor ratifies at freeze):
  s0=1.0e-4 (y+~65 regime, the M6SR-proven well-behaved first cell -> non-orth ~61),
  N=151 nodes = 150 cell layers (the intended x8-triple COARSE end; Lm=300, Lf=600),
  marchDist=12.0, gen_m6_gridb.driver_pyhyp_options smoothing set (own-family L2 clear).
The y+<1 first cell (s0=1.546335e-6) is applied AFTER, by respace_wallnormal.py (TOOL 2)."""
from pyhyp import pyHyp
opts = {
    "inputFile": "surfaceMesh_Lc_nocluster.cgns", "fileType": "CGNS",
    "unattachedEdgesAreSymmetry": True, "outerFaceBC": "farfield",
    "autoConnect": True, "BC": {}, "families": "wall",
    "N": 151, "s0": 1.0e-4, "marchDist": 12.0, "ps0": -1.0, "pGridRatio": -1.0,
    "cMax": 0.1, "epsE": 1.0, "epsI": 2.0, "theta": 3.0,
    "volCoef": 0.25, "volBlend": 0.0005, "volSmoothIter": 100, "kspreltol": 1e-4,
}
h = pyHyp(options=opts); h.run()
h.writeCGNS("volumeMesh_Lc_yp35.cgns")
print("MARCH_OK wrote volumeMesh_Lc_yp35.cgns")
