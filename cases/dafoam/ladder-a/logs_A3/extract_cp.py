#!/usr/bin/env python3
"""
Extract surface Cp on the 'wing' patch at the 7 AGARD/TMR eta stations
(eta = 0.20, 0.44, 0.65, 0.80, 0.90, 0.96, 0.99), from the DAFoam/OpenFOAM
solution written by foamToVTK (VTK/A3-onera-m6-transonic_<time>/boundary/wing.vtp).

Uses a true geometric cutting plane (vtkCutter) at z = eta * b_semi, which
correctly captures the full chordwise x-c sweep at each station regardless of
local mesh face density (avoids band-selection artifacts of naive z-banding).

Root chord and semispan taken from Destarac & Dumont, "ONERA M6 Wing Test-Case,
Original and TMR" (NASA TMR): root chord c_root = 0.8059 m, semispan b = 1.1963 m.
Freestream state taken from this case's own thermophysicalProperties + runScript.py
BCs (U0, p0, T0) -- NOT re-derived from the solution, so this is not circular.
"""
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np
import json
import sys

vtp_path = sys.argv[1]
out_json = sys.argv[2]

# ---- freestream / case constants (must match runScript.py + thermophysicalProperties) ----
U0 = 291.6
p0 = 101325.0
T0 = 300.0
molWeight = 28.97
Cp_gas = 1005.0
Ru = 8314.4621
R = Ru / molWeight
gamma = Cp_gas / (Cp_gas - R)
a_inf = (gamma * R * T0) ** 0.5
M_inf = U0 / a_inf
rho_inf = p0 / (R * T0)
q_inf = 0.5 * rho_inf * U0 * U0

c_root = 0.8059
b_semi = 1.1963

print(f"gamma={gamma:.6f} R={R:.4f} a_inf={a_inf:.4f} M_inf={M_inf:.6f} rho_inf={rho_inf:.6f} q_inf={q_inf:.4f}")

reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(vtp_path)
reader.Update()
poly = reader.GetOutput()
print(f"n_cells={poly.GetNumberOfCells()} n_points={poly.GetNumberOfPoints()}")

c2p = vtk.vtkCellDataToPointData()
c2p.SetInputData(poly)
c2p.PassCellDataOff()
c2p.Update()
poly_pt = c2p.GetOutput()

stations = [0.20, 0.44, 0.65, 0.80, 0.90, 0.96, 0.99]
result = {
    "freestream": {
        "U0": U0, "p0": p0, "T0": T0, "gamma": gamma, "R_specific": R,
        "a_inf": a_inf, "M_inf": M_inf, "rho_inf": rho_inf, "q_inf": q_inf,
        "c_root": c_root, "b_semi": b_semi,
    },
    "stations": {}
}

for eta in stations:
    z_cut = eta * b_semi
    plane = vtk.vtkPlane()
    plane.SetOrigin(0.0, 0.0, z_cut)
    plane.SetNormal(0.0, 0.0, 1.0)
    cutter = vtk.vtkCutter()
    cutter.SetInputData(poly_pt)
    cutter.SetCutFunction(plane)
    cutter.Update()
    cut = cutter.GetOutput()
    n_pts = cut.GetNumberOfPoints()
    if n_pts == 0:
        result["stations"][str(eta)] = {"n_points": 0}
        print(f"eta={eta}: NO INTERSECTION")
        continue
    pts = vtk_to_numpy(cut.GetPoints().GetData())
    p_pt = vtk_to_numpy(cut.GetPointData().GetArray("p"))
    x = pts[:, 0]
    y = pts[:, 1]
    z = pts[:, 2]
    Cp_vals = (p_pt - p0) / q_inf

    x_le = x.min()
    x_te = x.max()
    local_chord = x_te - x_le
    xoc = (x - x_le) / local_chord if local_chord > 1e-9 else x * 0

    # separate upper/lower surface by sign of y at each x (approx: use point order via y-sign
    # relative to local mean camber -- simplest robust split: for each x, upper=max y, lower=min y
    order = np.argsort(xoc)
    result["stations"][str(eta)] = {
        "n_points": int(n_pts),
        "z_cut_target": float(z_cut),
        "z_actual_mean": float(z.mean()),
        "z_actual_std": float(z.std()),
        "x_le": float(x_le), "x_te": float(x_te), "local_chord": float(local_chord),
        "xoc": xoc[order].tolist(),
        "cp": Cp_vals[order].tolist(),
        "y": y[order].tolist(),
    }
    print(f"eta={eta}: n={n_pts} local_chord={local_chord:.4f} x_le={x_le:.4f} x_te={x_te:.4f} "
          f"z_std={z.std():.6f} Cp range [{Cp_vals.min():.3f},{Cp_vals.max():.3f}]")

with open(out_json, "w") as f:
    json.dump(result, f, indent=1)
print("wrote", out_json)
