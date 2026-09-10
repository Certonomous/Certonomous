"""Medium-Lm y+~35 march of the CAPPED coarsen-x1 surface (buildable no-cluster path).
N=301 nodes = 300 layers (x8-triple medium end; s0=1e-4 march regime, respace to y+<1 after)."""
from pyhyp import pyHyp
opts = {"inputFile":"surfaceMesh_Lm.cgns","fileType":"CGNS","unattachedEdgesAreSymmetry":True,
  "outerFaceBC":"farfield","autoConnect":True,"BC":{},"families":"wall",
  "N":301,"s0":1.0e-4,"marchDist":12.0,"ps0":-1.0,"pGridRatio":-1.0,"cMax":0.1,
  "epsE":1.0,"epsI":2.0,"theta":3.0,"volCoef":0.25,"volBlend":0.0005,"volSmoothIter":100,"kspreltol":1e-4}
h=pyHyp(options=opts); h.run(); h.writeCGNS("volumeMesh_Lm_yp35.cgns")
print("MARCH_OK Lm")
