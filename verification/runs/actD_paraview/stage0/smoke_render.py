OUT = '/home/ubuntu/Certonomous/verification/runs/actD_paraview/stage0/smoke.png'
# Stage 0 smoke frame. Deliberately trivial: this tests the
# ENGINE, not the case. A case-coupled render is G-PV7b's job, later.
print("SENTINEL_PY_OK", flush=True)
from paraview.simple import *
print("SENTINEL_IMPORT_OK", flush=True)
s = Sphere(ThetaResolution=64, PhiResolution=64)
d = Show(s)
d.Representation = "Surface With Edges"
v = GetActiveView()
v.ViewSize = [480, 360]
v.Background = [0.12, 0.14, 0.18]
ResetCamera()
Render()
print("SENTINEL_RENDER_OK", flush=True)
SaveScreenshot(OUT, v)
print("SENTINEL_SAVE_OK", flush=True)
