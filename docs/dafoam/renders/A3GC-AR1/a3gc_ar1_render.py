# A3GC-AR1 geometry + mesh render.  READ-ONLY on the graded tree: the mesh is a
# COPY under scratch and ParaView reads only that copy.  Camera is FITTED TO THE
# SUBJECT on every frame -- the prior M6 set wasted 35-45 % of frame on white
# margin on five of ten stills, and a tight parallel-projection fit is the fix.
from paraview.simple import *
import os, sys, json

CASE, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
W, H = 1600, 1100
ASPECT = float(W) / float(H)

wing = OpenFOAMReader(registrationName="wing", FileName=os.path.join(CASE, "case.foam"))
wing.MeshRegions = ["patch/wing"]; wing.CellArrays = []; wing.UpdatePipeline()
vol = OpenFOAMReader(registrationName="vol", FileName=os.path.join(CASE, "case.foam"))
vol.MeshRegions = ["internalMesh"]; vol.CellArrays = []; vol.UpdatePipeline()
wb = wing.GetDataInformation().GetBounds()
fb = vol.GetDataInformation().GetBounds()
NW, NV = wing.GetDataInformation().GetNumberOfCells(), vol.GetDataInformation().GetNumberOfCells()
print("wing faces", NW, "volume cells", NV)

v = GetActiveViewOrCreate("RenderView")
v.ViewSize = [W, H]
v.UseColorPaletteForBackground = 0
v.Background = [1.0, 1.0, 1.0]
v.OrientationAxesVisibility = 0
v.CameraParallelProjection = 1

def fit(b, direction, up, pad=1.03):
    """Tight parallel fit.  Computes the on-screen half-extents of `b` in the
    camera frame directly and sets CameraParallelScale from the binding one,
    rather than letting ResetCamera pad the frame."""
    import math
    c = [(b[0]+b[1])/2.0, (b[2]+b[3])/2.0, (b[4]+b[5])/2.0]
    d = [b[1]-b[0], b[3]-b[2], b[5]-b[4]]
    n = math.sqrt(sum(x*x for x in direction)); fwd = [x/n for x in direction]
    # screen up = up orthogonalised against fwd; screen right = fwd x up
    du = sum(up[i]*fwd[i] for i in range(3))
    u = [up[i]-du*fwd[i] for i in range(3)]
    nu = math.sqrt(sum(x*x for x in u)); u = [x/nu for x in u]
    r = [fwd[1]*u[2]-fwd[2]*u[1], fwd[2]*u[0]-fwd[0]*u[2], fwd[0]*u[1]-fwd[1]*u[0]]
    half_u = 0.5*sum(abs(u[i])*d[i] for i in range(3))
    half_r = 0.5*sum(abs(r[i])*d[i] for i in range(3))
    scale = max(half_u, half_r/ASPECT) * pad
    dist = 4.0 * max(d) + 1.0
    v.CameraFocalPoint = c
    v.CameraPosition = [c[i]+fwd[i]*dist for i in range(3)]
    v.CameraViewUp = u
    v.CameraParallelScale = scale
    Render()

frames = []
def shot(name, caption):
    p = os.path.join(OUT, name)
    SaveScreenshot(p, v, ImageResolution=[W, H], TransparentBackground=0)
    frames.append({"file": name, "caption": caption})
    print("WROTE", p)

dw = Show(wing, v)
dw.Representation = "Surface"
dw.DiffuseColor = [0.60, 0.65, 0.72]; dw.AmbientColor = [0.2, 0.22, 0.26]

# 1 -- planform, looking along -y (thickness axis); span is z, chord is x
fit(wb, direction=(0, 1, 0), up=(0, 0, 1))
shot("01_AR1_wing_surface_planform.png",
     "ONERA M6 wing, AR1 c2 patch -- %d quad faces, registered 6,240. Planform." % NW)

# 2 -- surface mesh, oblique
dw.Representation = "Surface With Edges"
dw.EdgeColor = [0.08, 0.09, 0.12]; dw.LineWidth = 1.0
fit(wb, direction=(0.50, 0.66, -0.56), up=(0, 0, 1))
shot("02_AR1_wing_surface_mesh_oblique.png",
     "The same patch with its quad edges -- the surface discretisation AR1 actually ran.")

# 3 -- leading edge, forward 25 % of chord, inboard 45 % of span
lb = [wb[0], wb[0] + 0.25*(wb[1]-wb[0]), wb[2], wb[3], wb[4], wb[4] + 0.45*(wb[5]-wb[4])]
fit(lb, direction=(0.28, 0.80, -0.53), up=(0, 0, 1))
shot("03_AR1_wing_leadingedge_mesh.png",
     "Leading-edge region -- chordwise clustering on the c2 surface.")

# 4 -- the boundary layer: spanwise cut at eta = 0.65 through the volume mesh
Hide(wing, v)
zc = wb[4] + 0.65*(wb[5]-wb[4])
sl = Slice(registrationName="bl", Input=vol)
sl.SliceType = "Plane"; sl.SliceType.Origin = [0, 0, zc]; sl.SliceType.Normal = [0, 0, 1]
sl.UpdatePipeline()
dsl = Show(sl, v); dsl.Representation = "Surface With Edges"
dsl.DiffuseColor = [0.93, 0.945, 0.97]; dsl.EdgeColor = [0.06, 0.08, 0.13]; dsl.LineWidth = 0.6
ch = wb[1]-wb[0]
ab = [wb[0]-0.10*ch, wb[1]+0.16*ch, -0.26*ch, 0.26*ch, zc, zc]
fit(ab, direction=(0, 0, -1), up=(0, 1, 0))
shot("04_AR1_boundary_layer_mesh_eta065.png",
     "Volume mesh on the eta = 0.65 cut -- the 64 wall-normal layers (pyHyp N=65, s0=1.0e-4, r=1.1674) that are the whole point of AR1. %d cells in the domain." % NV)

# 5 -- wall-normal zoom on the leading edge at the same station
nb = [wb[0]-0.012*ch, wb[0]+0.115*ch, -0.046*ch, 0.046*ch, zc, zc]
fit(nb, direction=(0, 0, -1), up=(0, 1, 0))
shot("05_AR1_boundary_layer_zoom_LE.png",
     "Wall-normal zoom at the leading edge, same cut -- first cell s0 = 1.0e-4, constant growth r = 1.1674.")

# 6 -- domain extent, so marchDist is on record
Hide(sl, v)
dv = Show(vol, v); dv.Representation = "Outline"; dv.AmbientColor = [0.35, 0.37, 0.42]
dw2 = Show(wing, v); dw2.Representation = "Surface"; dw2.DiffuseColor = [0.16, 0.40, 0.72]
fit(fb, direction=(0.45, 0.55, -0.70), up=(0, 0, 1))
shot("06_AR1_domain_extent.png",
     "Full computational domain, marchDist = 12.0 -- %d cells, with the wing at true relative scale." % NV)

json.dump({"frames": frames, "wing_faces": NW, "volume_cells": NV,
           "wing_bounds": list(wb), "domain_bounds": list(fb),
           "image_resolution": [W, H]},
          open(os.path.join(OUT, "_frames.json"), "w"), indent=1)
print("FRAMES", len(frames))
