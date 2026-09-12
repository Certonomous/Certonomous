from paraview.simple import *
import sys, os
CASE = sys.argv[1]; OUT = sys.argv[2]; SHA = sys.argv[3]
paraview.simple._DisableFirstRenderCameraReset()

PATCHES = {
    "lid":      ((0.85, 0.20, 0.15), 1.0,  "lid  y=1  fixedValue U=(1 0 0)  1 m/s"),
    "floor":    ((0.35, 0.40, 0.48), 1.0,  "floor  y=0  noSlip"),
    "sideXmin": ((0.55, 0.60, 0.66), 1.0,  "sideXmin  x=0  noSlip"),
    "sideXmax": ((0.55, 0.60, 0.66), 1.0,  "sideXmax  x=1  noSlip"),
    "wallZmin": ((0.45, 0.50, 0.57), 1.0,  "wallZmin  z=0  noSlip (cube end wall)"),
    "symmetry": ((0.10, 0.42, 0.80), 0.30, "symmetry  z=0.5  symmetryPlane (cube mid-span)"),
}

def new_view(w, h):
    v = CreateRenderView()
    v.ViewSize = [w, h]
    v.Background = [1, 1, 1]; v.Background2 = [1, 1, 1]
    v.UseColorPaletteForBackground = 0
    v.OrientationAxesVisibility = 1
    v.OrientationAxesLabelColor = [0, 0, 0]
    v.CameraPosition = [3.313, 2.211, 2.343]
    v.CameraFocalPoint = [0.894, 0.500, -0.135]
    v.CameraViewUp = [0, 1, 0]
    v.CameraParallelProjection = 0
    return v

def label(v, txt, pos, size=13, colour=(0, 0, 0), bold=0):
    t = Text(); t.Text = txt
    d = Show(t, v); d.Color = list(colour); d.FontSize = size; d.Bold = bold
    d.WindowLocation = "Any Location"; d.Position = pos
    return t

def reader():
    r = OpenFOAMReader(FileName=CASE)
    r.MeshRegions = ["patch/" + p for p in PATCHES]
    r.CellArrays = []
    r.UpdatePipeline()
    return r

# ---------------------------------------------------------------- (a) geometry
v = new_view(1920, 1440)
for name, (col, opac, _t) in PATCHES.items():
    r = OpenFOAMReader(FileName=CASE); r.MeshRegions = ["patch/" + name]; r.CellArrays = []
    d = Show(r, v); d.Representation = "Surface"
    d.AmbientColor = list(col); d.DiffuseColor = list(col); d.Opacity = opac
    d.ColorArrayName = [None, ""]
    e = ExtractSurface(Input=r); fe = FeatureEdges(Input=e)
    fe.BoundaryEdges = 1; fe.FeatureEdges = 0; fe.NonManifoldEdges = 0; fe.ManifoldEdges = 0
    de = Show(fe, v); de.DiffuseColor = [0, 0, 0]; de.AmbientColor = [0, 0, 0]
    de.LineWidth = 2.0; de.ColorArrayName = [None, ""]

label(v, "VMFL078  -  Ansys Fluid Dynamics Verification Manual 2026 R1, printed p.223", (0.030, 0.955), 20, bold=1)
label(v, "3-D lid-driven cubic cavity, Re = 1000  -  GEOMETRY AND BOUNDARY CONDITIONS", (0.030, 0.925), 16)
y = 0.780
label(v, "half domain modelled:  1 m x 1 m x 0.5 m,", (0.620, y + 0.075), 15, bold=1)
label(v, "symmetry at mid-span  ->  unit cube", (0.620, y + 0.042), 15, bold=1)
for name, (col, _o, txt) in PATCHES.items():
    label(v, txt, (0.620, y), 14, colour=col, bold=1); y -= 0.040
label(v, "rho = 1 kg/m3    mu = 0.001 kg/m-s", (0.620, y - 0.020), 14)
label(v, "U_lid = 1 m/s    ->    Re = 1000", (0.620, y - 0.055), 14)
label(v, "laminar, steady (simpleFoam)", (0.620, y - 0.090), 14)
label(v, "record sha " + SHA, (0.200, 0.020), 12, colour=(0.4, 0.4, 0.4))
Render(v)
SaveScreenshot(os.path.join(OUT, "VMFL078_geometry_%s.png" % SHA), v,
               ImageResolution=[1920, 1440], TransparentBackground=0)
print("wrote geometry")

# ------------------------------------------------------------------- (b) L3 mesh
v2 = new_view(1920, 1440)
r = reader()
d = Show(r, v2); d.Representation = "Surface With Edges"
d.AmbientColor = [0.88, 0.90, 0.93]; d.DiffuseColor = [0.88, 0.90, 0.93]
d.EdgeColor = [0.10, 0.12, 0.16]; d.LineWidth = 0.35; d.Opacity = 1.0
d.ColorArrayName = [None, ""]

lid = OpenFOAMReader(FileName=CASE); lid.MeshRegions = ["patch/lid"]; lid.CellArrays = []
dl = Show(lid, v2); dl.Representation = "Surface With Edges"
dl.AmbientColor = [0.96, 0.72, 0.66]; dl.DiffuseColor = [0.96, 0.72, 0.66]
dl.EdgeColor = [0.72, 0.42, 0.34]; dl.LineWidth = 0.30; dl.ColorArrayName = [None, ""]

label(v2, "VMFL078  -  LEVEL L3 MESH (finest of the r = 2 family)", (0.030, 0.955), 20, bold=1)
label(v2, "128 x 128 x 64 hexahedra  =  1,048,576 cells   |   uniform, simpleGrading (1 1 1)", (0.030, 0.925), 16)
label(v2, "dy at the lid = 1/128 = 0.0078 m", (0.030, 0.895), 14)
label(v2, "lid (y = 1) shaded  -  moving wall, 1 m/s in +x", (0.620, 0.760), 15, colour=(0.70, 0.25, 0.15), bold=1)
label(v2, "grid family, r = 2", (0.620, 0.700), 15, bold=1)
label(v2, "   L1    32 x 32 x 16", (0.620, 0.662), 14)
label(v2, "   L2    64 x 64 x 32", (0.620, 0.626), 14)
label(v2, "   L3   128 x 128 x 64   <- shown", (0.620, 0.590), 14, bold=1)
label(v2, "graded level for limb B", (0.620, 0.520), 15, bold=1)
label(v2, "(agreement with Figure .78.2):  L3", (0.620, 0.484), 14)
label(v2, "gate line", (0.620, 0.420), 15, bold=1)
label(v2, "   x = 0.5, z = 0.5, y = 0.005 .. 0.995", (0.620, 0.384), 14)
label(v2, "   201 frozen probes, cellPoint", (0.620, 0.348), 14)
label(v2, "record sha " + SHA, (0.200, 0.020), 12, colour=(0.4, 0.4, 0.4))
Render(v2)
SaveScreenshot(os.path.join(OUT, "VMFL078_L3_mesh_%s.png" % SHA), v2,
               ImageResolution=[1920, 1440], TransparentBackground=0)
print("wrote mesh")
