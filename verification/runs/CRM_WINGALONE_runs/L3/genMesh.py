from pyhyp import pyHyp
opts = {"inputFile":"surfMesh.cgns","fileType":"CGNS","unattachedEdgesAreSymmetry":True,
 "outerFaceBC":"farfield","autoConnect":True,"BC":{},"families":"wall",
 "N":209,"s0":1.0e-4,"marchDist":25*3.758151,
 "ps0":-1.0,"pGridRatio":1.03,"cMax":5.0,
 "epsE":1.0,"epsI":2.0,"theta":3.0,"volCoef":0.16,"volBlend":0.0005,
 "volSmoothIter":30,"kspRelTol":1e-4,"kspMaxIts":50,"kspSubspaceSize":50}
h = pyHyp(options=opts); h.run(); h.writePlot3D("volumeMesh.xyz")
print("PYHYP_WROTE volumeMesh.xyz")
