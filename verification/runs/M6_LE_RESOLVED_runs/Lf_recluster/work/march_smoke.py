"""TASK-1 SMOKE: N=5 layers ONLY. The question is whether pyHyp autoConnect STITCHES the
re-clustered 9-zone surface, or repeats 'Unknown topology'. This is not a march."""
import sys, traceback
from pyhyp import pyHyp
inp, ftype, out = sys.argv[1], sys.argv[2], sys.argv[3]
opts = {"inputFile": inp, "fileType": ftype, "unattachedEdgesAreSymmetry": True,
        "outerFaceBC": "farfield", "autoConnect": True, "BC": {}, "families": "wall",
        "N": 5, "s0": 1.0e-4, "marchDist": 0.01, "ps0": -1.0, "pGridRatio": -1.0,
        "cMax": 0.1, "epsE": 1.0, "epsI": 2.0, "theta": 3.0, "volCoef": 0.25,
        "volBlend": 0.0005, "volSmoothIter": 100, "kspreltol": 1e-4}
try:
    h = pyHyp(options=opts); h.run(); h.writeCGNS(out)
    print("SMOKE_OK wrote", out)
except Exception:
    traceback.print_exc(); print("SMOKE_FAIL"); sys.exit(1)
