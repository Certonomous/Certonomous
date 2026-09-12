from paraview.simple import *
import os, sys, json, math
CASE, OUT = sys.argv[1], sys.argv[2]
W,H = 1600,1100; ASPECT=float(W)/float(H)
wing=OpenFOAMReader(FileName=CASE+"/case.foam"); wing.MeshRegions=["patch/wing"]; wing.CellArrays=[]; wing.UpdatePipeline()
vol =OpenFOAMReader(FileName=CASE+"/case.foam"); vol.MeshRegions=["internalMesh"]; vol.CellArrays=[]; vol.UpdatePipeline()
wb=wing.GetDataInformation().GetBounds(); z65=wb[4]+0.65*(wb[5]-wb[4])
aero=Slice(Input=wing); aero.SliceType="Plane"; aero.SliceType.Origin=[0,0,z65]; aero.SliceType.Normal=[0,0,1]; aero.UpdatePipeline()
ab=aero.GetDataInformation().GetBounds(); lc=ab[1]-ab[0]
v=GetActiveViewOrCreate("RenderView"); v.ViewSize=[W,H]
v.UseColorPaletteForBackground=0; v.Background=[1,1,1]; v.OrientationAxesVisibility=0; v.CameraParallelProjection=1
sl=Slice(Input=vol); sl.SliceType="Plane"; sl.SliceType.Origin=[0,0,z65]; sl.SliceType.Normal=[0,0,1]; sl.UpdatePipeline()
d=Show(sl,v); d.Representation="Surface With Edges"
d.DiffuseColor=[0.93,0.945,0.97]; d.EdgeColor=[0.06,0.08,0.13]; d.LineWidth=0.7
Render()                      # let the view do its automatic reset FIRST
cx,cy=ab[0],(ab[2]+ab[3])/2.0
halfx, halfy = 0.090*lc, 0.062*lc
want = max(halfy, halfx/ASPECT)*1.03
v.CameraFocalPoint=[cx+0.055*lc, cy, z65]
v.CameraPosition=[cx+0.055*lc, cy, z65+3.0]
v.CameraViewUp=[0,1,0]
v.CameraParallelScale=want
Render()
print("requested parallel scale %.6f, view reports %.6f" % (want, v.CameraParallelScale))
if abs(v.CameraParallelScale-want)/want > 1e-6:
    v.CameraParallelScale=want; Render()
    print("re-applied; view now %.6f" % v.CameraParallelScale)
SaveScreenshot(OUT+"/05_AR1_boundary_layer_zoom_LE.png", v, ImageResolution=[W,H])
print("WROTE 05  local chord %.5f  LE x %.5f" % (lc, ab[0]))
