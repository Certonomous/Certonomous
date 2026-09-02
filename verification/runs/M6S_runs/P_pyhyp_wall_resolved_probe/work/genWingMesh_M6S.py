"""M6S-P probe deck.  Derived from /home/ubuntu/dafoam-tutorials/Onera_M6_Wing/genWingMesh.py
(read-only parameter source, prereg §10).  Three parameters move and no others:
  N        65      -> 93     (pyHyp node count; 92 cell layers against the stock 64)
  s0       1.0e-4  -> 1.319e-06   (REQUESTED; registered as an INPUT, never a measurement)
  surface  6,240-face fine -> the 1,560-face coarsening
"""
from pyhyp import pyHyp

fileName = "surfaceMesh.cgns"

options = {
    "inputFile": fileName,
    "fileType": "CGNS",
    "unattachedEdgesAreSymmetry": True,
    "outerFaceBC": "farfield",
    "autoConnect": True,
    "BC": {},
    "families": "wall",
    "N": 93,
    "s0": 1.319e-06,
    "marchDist": 12.0,
    "ps0": -1.0,
    "pGridRatio": -1.0,
    "cMax": 0.1,
    "epsE": 1.0,
    "epsI": 2.0,
    "theta": 3.0,
    "volCoef": 0.25,
    "volBlend": 0.0005,
    "volSmoothIter": 100,
    "kspreltol": 1e-4,
}

hyp = pyHyp(options=options)
hyp.run()
hyp.writePlot3D("volumeMesh.xyz")
