"""Solve one parametric wing with VSPAERO — runs inside the OpenVSP python.

This script executes under the interpreter that can import ``openvsp`` (in
production: the WSL system python with the OpenVSP release on PYTHONPATH). It
is deliberately standalone — no imports from ``chief_engineer`` — because the
lab process and the solver process are different pythons on different
filesystems. The seam between them is two JSON files in the working directory:

    job.json     the design: span, area, sweep, taper, cl_target, re_cref
    result.json  the solved polar and the point matched to the target CL

The wing is built from the section driver group (span / area / taper), so the
planform the solver sees is exactly the planform the job asked for. The alpha
sweep brackets the cruise lift coefficient; the matched point is interpolated
from the solved polar, never extrapolated silently — extrapolation is flagged.
A surface mesh (``wing.stl``) is exported for the control-room viewport.
"""
from __future__ import annotations

import json
import math
import os
import sys

import openvsp as vsp


def solve(job: dict) -> dict:
    span = float(job["span"])
    area = float(job["area"])
    sweep = float(job.get("sweep", 27.5))
    taper = float(job.get("taper", 0.3))
    cl_target = float(job.get("cl_target", 0.5))
    re_cref = float(job.get("re_cref", 4.0e7))
    mach = float(job.get("mach", 0.0))
    alpha_lo = float(job.get("alpha_start", 0.0))
    alpha_hi = float(job.get("alpha_end", 8.0))
    alpha_n = int(job.get("alpha_npts", 5))

    vsp.VSPCheckSetup()
    vsp.ClearVSPModel()

    wid = vsp.AddGeom("WING")
    vsp.SetDriverGroup(wid, 1, vsp.SPAN_WSECT_DRIVER, vsp.AREA_WSECT_DRIVER,
                       vsp.TAPER_WSECT_DRIVER)
    vsp.SetParmVal(wid, "Span", "XSec_1", span / 2.0)
    vsp.SetParmVal(wid, "Area", "XSec_1", area / 2.0)
    vsp.SetParmVal(wid, "Taper", "XSec_1", taper)
    vsp.SetParmVal(wid, "Sweep", "XSec_1", sweep)
    # Optional four-series airfoil shaping (e.g. NACA 4412: camber 0.04 at
    # 0.4 chord, 12% thickness), applied to root and tip sections when given.
    for name, parm in (("camber", "Camber"), ("camber_loc", "CamberLoc"),
                       ("thick_chord", "ThickChord")):
        if name in job:
            for group in ("XSecCurve_0", "XSecCurve_1"):
                vsp.SetParmVal(wid, parm, group, float(job[name]))
    vsp.Update()

    built = {
        "span": vsp.GetParmVal(wid, "TotalSpan", "WingGeom"),
        "area": vsp.GetParmVal(wid, "TotalArea", "WingGeom"),
        "root_chord": vsp.GetParmVal(wid, "Root_Chord", "XSec_1"),
        "tip_chord": vsp.GetParmVal(wid, "Tip_Chord", "XSec_1"),
    }

    vsp.WriteVSPFile(os.path.join(os.getcwd(), "wing.vsp3"))

    an = "VSPAEROComputeGeometry"
    vsp.SetAnalysisInputDefaults(an)
    vsp.ExecAnalysis(an)

    an = "VSPAEROSweep"
    vsp.SetAnalysisInputDefaults(an)
    vsp.SetDoubleAnalysisInput(an, "AlphaStart", [alpha_lo])
    vsp.SetDoubleAnalysisInput(an, "AlphaEnd", [alpha_hi])
    vsp.SetIntAnalysisInput(an, "AlphaNpts", [alpha_n])
    vsp.SetDoubleAnalysisInput(an, "MachStart", [mach])
    vsp.SetIntAnalysisInput(an, "MachNpts", [1])
    vsp.SetDoubleAnalysisInput(an, "ReCref", [re_cref])
    vsp.SetIntAnalysisInput(an, "RefFlag", [0])
    vsp.SetDoubleAnalysisInput(an, "Sref", [area])
    vsp.SetDoubleAnalysisInput(an, "bref", [span])
    vsp.SetDoubleAnalysisInput(an, "cref", [area / span])
    vsp.Update()
    vsp.ExecAnalysis(an)

    polar_id = vsp.FindLatestResultsID("VSPAERO_Polar")
    polar = {}
    for key in ("Alpha", "CLtot", "CDi", "CDo", "CDtot", "L_D", "E"):
        polar[key] = list(vsp.GetDoubleResults(polar_id, key))

    alphas, cls = polar["Alpha"], polar["CLtot"]

    def interp(ys: list[float], x: float, xs: list[float]) -> float:
        for i in range(len(xs) - 1):
            if xs[i] <= x <= xs[i + 1]:
                t = (x - xs[i]) / (xs[i + 1] - xs[i] or 1.0)
                return ys[i] + t * (ys[i + 1] - ys[i])
        # Outside the swept range: extend from the nearest segment.
        if x < xs[0]:
            i = 0
        else:
            i = len(xs) - 2
        t = (x - xs[i]) / (xs[i + 1] - xs[i] or 1.0)
        return ys[i] + t * (ys[i + 1] - ys[i])

    # Export the surface for the control-room viewport only after the solve:
    # ExportFile adds a MeshGeom to the model, which corrupts the geometry
    # pass if it happens first.
    vsp.ExportFile(os.path.join(os.getcwd(), "wing.stl"), vsp.SET_ALL,
                   vsp.EXPORT_STL)

    if alpha_n == 1 and len(alphas) == 1:
        # A single-point run is a direct solve, not a sweep: return the solved
        # point as the polar, with no interpolated cruise point.
        return {"built": built, "polar": polar, "matched": None,
                "stl": "wing.stl", "solver": "VSPAERO",
                "solver_version": vsp.GetVSPVersion()}

    if len(alphas) < 2 or max(cls) <= min(cls):
        raise RuntimeError(
            f"sweep returned no usable polar ({len(alphas)} points)")

    extrapolated = not (min(cls) <= cl_target <= max(cls))
    alpha_at = interp(alphas, cl_target, cls)
    matched = {
        "alpha": alpha_at,
        "cl": cl_target,
        "cdi": interp(polar["CDi"], cl_target, cls),
        "cdo_wing": interp(polar["CDo"], cl_target, cls),
        "span_efficiency": interp(polar["E"], cl_target, cls)
        if all(math.isfinite(v) for v in polar["E"]) else None,
        "extrapolated": extrapolated,
    }

    return {"built": built, "polar": polar, "matched": matched,
            "stl": "wing.stl", "solver": "VSPAERO",
            "solver_version": vsp.GetVSPVersion()}


def main() -> int:
    with open("job.json", encoding="utf-8") as handle:
        job = json.load(handle)
    try:
        result = solve(job)
    except Exception as exc:  # the lab reads the failure, not a stack trace
        with open("result.json", "w", encoding="utf-8") as handle:
            json.dump({"error": f"{type(exc).__name__}: {exc}"}, handle)
        return 1
    with open("result.json", "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
