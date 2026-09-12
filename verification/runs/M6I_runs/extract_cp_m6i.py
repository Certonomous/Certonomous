#!/usr/bin/env python3
"""
extract_cp_m6i.py -- surface Cp at the SIX registered AGARD span stations from an M6I
level's reconstructed wing patch, in the exact schema the FROZEN grader
`scripts/grade_m6_agard_cp.py` (commit 4c931d97c) consumes.

  usage: extract_cp_m6i.py <wing.vtp> <out.json> [<freestream.json>]

AXES, AND WHY THE KEY IS CALLED "y".  The M6I grid runs SPAN ALONG y (root plane y = 0,
tip near y = b) and THICKNESS ALONG z (the wing occupies |z| <= 0.044).  The frozen
grader splits a section into upper and lower branches using a key literally named "y",
which it documents as "the y (thickness) coordinate carried in the file".  So this file
writes the VERTICAL coordinate -- M6I's z -- into the key "y", and the spanwise
coordinate into "y_span".  The grader is not edited to suit our axes; our axes are
written into the contract the grader already fixed.

REFUSES rather than degrading.  A station that cannot be cut, or a cut with too few
points to split into two branches, exits 2 and writes nothing.
"""
import json
import math
import os
import sys

import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

# ---- the six registered stations.  eta = 0.99 is EXCLUDED by the frozen
# pre-registration section 2 and is not extracted here either.
STATIONS = (0.20, 0.44, 0.65, 0.80, 0.90, 0.96)
MIN_POINTS_PER_STATION = 12      # the grader refuses a branch under 5; this is the
                                 # extractor's own earlier, louder refusal


def die(msg):
    print("REFUSE: %s" % msg, file=sys.stderr)
    sys.exit(2)


def main():
    if len(sys.argv) < 3:
        die("usage: extract_cp_m6i.py <wing.vtp> <out.json> [freestream.json]")
    vtp, out = sys.argv[1], sys.argv[2]
    fs_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "FREESTREAM_M6I.json")
    if not os.path.exists(vtp):
        die("no such vtp: %s" % vtp)
    if not os.path.exists(fs_path):
        die("no freestream constants at %s" % fs_path)

    # The freestream comes from the case's OWN registered constants file, written by
    # build_m6i_solve_chain.sh BEFORE any solve.  It is NOT re-derived from the
    # solution, so the Mach the grader checks in P2 cannot be back-fitted.
    fsd = json.load(open(fs_path))
    p_inf = float(fsd["p_inf"])
    q_inf = float(fsd["q_inf"])
    b_semi = float(fsd["b_semi"])

    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(vtp)
    reader.Update()
    poly = reader.GetOutput()
    if poly.GetNumberOfCells() == 0:
        die("wing patch carries no cells")

    c2p = vtk.vtkCellDataToPointData()
    c2p.SetInputData(poly)
    c2p.PassCellDataOff()
    c2p.Update()
    poly_pt = c2p.GetOutput()
    if poly_pt.GetPointData().GetArray("p") is None:
        die("no 'p' array on the wing patch")

    result = {
        "freestream": {
            "M_inf": float(fsd["M_inf"]),
            "alpha_deg": float(fsd["alpha_deg"]),
            "U_inf": float(fsd["U_inf"]),
            "p_inf": p_inf,
            "T_inf": float(fsd["T_inf"]),
            "rho_inf": float(fsd["rho_inf"]),
            "q_inf": q_inf,
            "gamma": float(fsd["gamma"]),
            "R_specific": float(fsd["R_specific"]),
            "Re_root_chord": float(fsd["Re_root_chord"]),
            "c_root": 1.0,
            "b_semi": b_semi,
            "source": "verification/runs/M6I_runs/FREESTREAM_M6I.json, written before "
                      "any solve; NOT re-derived from the solution",
            "axes": "x chordwise, y spanwise, z vertical. The station block key 'y' "
                    "carries the VERTICAL coordinate (M6I z), which is the grader's "
                    "thickness-coordinate contract; 'y_span' carries the span.",
        },
        "vtp": os.path.abspath(vtp),
        "stations": {},
    }

    for eta in STATIONS:
        y_cut = eta * b_semi
        plane = vtk.vtkPlane()
        plane.SetOrigin(0.0, y_cut, 0.0)
        plane.SetNormal(0.0, 1.0, 0.0)
        cutter = vtk.vtkCutter()
        cutter.SetInputData(poly_pt)
        cutter.SetCutFunction(plane)
        cutter.Update()
        cut = cutter.GetOutput()
        n = cut.GetNumberOfPoints()
        if n < MIN_POINTS_PER_STATION:
            die("station eta = %.2f cut gives %d points (< %d); refusing rather than "
                "grading a section the cut did not resolve" % (eta, n, MIN_POINTS_PER_STATION))
        pts = vtk_to_numpy(cut.GetPoints().GetData())
        p_pt = vtk_to_numpy(cut.GetPointData().GetArray("p"))
        x, ys, z = pts[:, 0], pts[:, 1], pts[:, 2]
        cp = (p_pt - p_inf) / q_inf
        x_le, x_te = float(x.min()), float(x.max())
        chord = x_te - x_le
        if chord <= 1e-9:
            die("station eta = %.2f has zero chordwise extent" % eta)
        xoc = (x - x_le) / chord
        order = np.argsort(xoc)
        result["stations"]["%g" % eta] = {
            "n_points": int(n),
            "y_cut_target": float(y_cut),
            "y_span_mean": float(ys.mean()),
            "y_span_std": float(ys.std()),
            "x_le": x_le, "x_te": x_te, "local_chord": float(chord),
            "xoc": [float(v) for v in xoc[order]],
            "cp": [float(v) for v in cp[order]],
            "y": [float(v) for v in z[order]],        # VERTICAL -- the grader's contract
            "y_span": [float(v) for v in ys[order]],
        }
        print("eta=%-5.2f n=%4d chord=%.5f x_le=%.5f x_te=%.5f y_std=%.3e "
              "Cp[%.4f, %.4f]" % (eta, n, chord, x_le, x_te, ys.std(),
                                  float(cp.min()), float(cp.max())))

    with open(out, "w") as f:
        json.dump(result, f, indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
