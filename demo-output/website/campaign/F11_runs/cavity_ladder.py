"""F11 -- 2D lid-driven cavity verification ladder.

Reference: Ghia, U., Ghia, K.N., Shin, C.T. (1982). "High-Re solutions for
incompressible flow using the Navier-Stokes equations and a multigrid
method." Journal of Computational Physics, 48(3), 387-411.
DOI 10.1016/0021-9991(82)90058-4.

ACCESS NOTE, checked before any run (per this campaign's own standard --
see F5a's Re 1000/2000/3900 gates): the primary JCP article is PAYWALLED.
Checked directly via the Unpaywall API on 2026-07-30:
    is_oa: false, has_repository_copy: false, oa_locations: []
No legitimate open-access copy exists. The tabulated u(y) and v(x)
centerline values used below are therefore taken from a secondary,
publicly-hosted transcription of the paper's own Table I / Table II
(u-velocity along the vertical centerline x=0.5, v-velocity along the
horizontal centerline y=0.5), the same class of substitution F5a made for
its Re=2000 Zdravkovich gate when the primary source was unavailable --
disclosed here in the same way, not silently upgraded to look like a
primary-source point gate.

Cross-check performed before trusting the transcription: the u- and
v-velocity tables came from two INDEPENDENTLY hosted gists (different
authors), and the Re=100/Re=1000 columns used here (this ladder's two
rungs) are internally smooth and monotonic-where-expected with no
outliers -- unlike the Re=400 and Re=3200/10000 columns in the same two
tables, which visibly carry transcription defects (Re=400 x=0.9063 is
flagged "probably wrong" in the original paper per the v-velocity gist's
own note; Re=3200 x=0.4531 and Re=10000 x=0.5 in the u-table carry an
obvious sign/digit slip). Those defects are in Reynolds-number columns
NOT used by this ladder and are recorded here so the next reader does not
have to rediscover them -- Re=100 and Re=1000 are the clean columns.

Definitions checked, matching this project's standing "check the
definitions" discipline: Re = U_lid * L / nu with L = cavity side length,
U_lid = lid speed (both 1 in the nondimensional setup used here, so
nu = 1/Re exactly); Ghia's own coordinate convention has the lid at y=1
moving in +x, no-slip on the other three walls, u tabulated along the
vertical line x=0.5 and v along the horizontal line y=0.5 -- reproduced
exactly here, including sampling AT x=0.5 / y=0.5, not near it.

Solver-family note: 2D lid-driven cavity flow at Re<=1000 is a genuinely
STEADY, LAMINAR flow (no turbulence closure is physically appropriate --
using one here would be the exact L-11 mistake this project has already
paid for once, on the F5a cylinder ladder's Re 3900 rung). simpleFoam,
laminar, is used throughout.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

# ---------------------------------------------------------------------------
# Reference data: Ghia, Ghia & Shin (1982), Table I (u along x=0.5) and
# Table II (v along y=0.5). Re=100 and Re=1000 columns only (this ladder's
# two rungs) -- the columns independently verified clean, see module
# docstring. Boundary rows (y=0, y=1 for u; x=0, x=1 for v) are the
# boundary conditions themselves, not internal-field predictions, and are
# EXCLUDED from the gate (trivially satisfied by construction, would
# artificially inflate agreement) but kept here for completeness / sanity
# check.
# ---------------------------------------------------------------------------

U_ALONG_X05: dict[int, list[tuple[float, float]]] = {
    100: [
        (1.0000, 1.00000), (0.9766, 0.84123), (0.9688, 0.78871),
        (0.9609, 0.73722), (0.9531, 0.68717), (0.8516, 0.23151),
        (0.7344, 0.00332), (0.6172, -0.13641), (0.5000, -0.20581),
        (0.4531, -0.21090), (0.2813, -0.15662), (0.1719, -0.10150),
        (0.1016, -0.06434), (0.0703, -0.04775), (0.0625, -0.04192),
        (0.0547, -0.03717), (0.0000, 0.00000),
    ],
    1000: [
        (1.0000, 1.00000), (0.9766, 0.65928), (0.9688, 0.57492),
        (0.9609, 0.51117), (0.9531, 0.46604), (0.8516, 0.33304),
        (0.7344, 0.18719), (0.6172, 0.05702), (0.5000, -0.06080),
        (0.4531, -0.10648), (0.2813, -0.27805), (0.1719, -0.38289),
        (0.1016, -0.29730), (0.0703, -0.22220), (0.0625, -0.20196),
        (0.0547, -0.18109), (0.0000, 0.00000),
    ],
}

V_ALONG_Y05: dict[int, list[tuple[float, float]]] = {
    100: [
        (1.00000, 0.00000), (0.9688, -0.05906), (0.9609, -0.07391),
        (0.9531, -0.08864), (0.9453, -0.10313), (0.9063, -0.16914),
        (0.8594, -0.22445), (0.8047, -0.24533), (0.5000, 0.05454),
        (0.2344, 0.17527), (0.2266, 0.17507), (0.1563, 0.16077),
        (0.0938, 0.12317), (0.0781, 0.10890), (0.0703, 0.10091),
        (0.0625, 0.09233), (0.0000, 0.00000),
    ],
    1000: [
        (1.00000, 0.00000), (0.9688, -0.21388), (0.9609, -0.27669),
        (0.9531, -0.33714), (0.9453, -0.39188), (0.9063, -0.51500),
        (0.8594, -0.42665), (0.8047, -0.31966), (0.5000, 0.02526),
        (0.2344, 0.32235), (0.2266, 0.33075), (0.1563, 0.37095),
        (0.0938, 0.32627), (0.0781, 0.30353), (0.0703, 0.29012),
        (0.0625, 0.27485), (0.0000, 0.00000),
    ],
}

THICKNESS = 0.1
Z_MID = THICKNESS / 2.0


def _foam_header(cls: str, obj: str, location: str | None = None) -> str:
    loc = f'    location    "{location}";\n' if location else ""
    return (
        "FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
        f"    class       {cls};\n{loc}    object      {obj};\n}}\n\n"
    )


def block_mesh_dict(n: int, grading_ratio: float = 8.0) -> str:
    """Unit square cavity, single block, symmetric double-grading (fine at
    BOTH ends of each direction, coarse in the middle) in x and y -- all
    four walls carry a real BC (three no-slip, one moving-lid), so
    resolution belongs at every wall, not just one. ``n`` must be even (the
    grading splits 50/50). z is ``empty`` (2D case), thickness arbitrary
    (THICKNESS) since the empty patch makes it geometrically inert.
    """
    if n % 2 != 0:
        raise ValueError(f"n={n} must be even for symmetric double-grading")
    r = grading_ratio
    inv_r = 1.0 / r
    grad_1d = f"( (0.5 0.5 {r:.6g}) (0.5 0.5 {inv_r:.6g}) )"
    t = THICKNESS
    return _foam_header("dictionary", "blockMeshDict", "system") + f"""
scale   1;

vertices
(
    (0 0 0)
    (1 0 0)
    (1 1 0)
    (0 1 0)
    (0 0 {t})
    (1 0 {t})
    (1 1 {t})
    (0 1 {t})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({n} {n} 1)
    simpleGrading
    (
        {grad_1d}
        {grad_1d}
        1
    )
);

edges ();

boundary
(
    movingWall {{ type wall; faces ((3 7 6 2)); }}
    fixedWalls {{ type wall; faces ((0 4 7 3) (2 6 5 1) (1 5 4 0)); }}
    frontAndBack {{ type empty; faces ((0 3 2 1) (4 5 6 7)); }}
);
"""


def _points_block(points: Sequence[tuple[float, float, float]]) -> str:
    return "\n".join(f"        ({x:.6f} {y:.6f} {z:.6f})" for x, y, z in points)


def control_dict(max_iter: int) -> str:
    u_points = [(0.5, y, Z_MID) for y, _ in U_ALONG_X05[1000]]
    v_points = [(x, 0.5, Z_MID) for x, _ in V_ALONG_Y05[1000]]
    return _foam_header("dictionary", "controlDict", "system") + f"""
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {max_iter};
deltaT          1;
writeControl    timeStep;
writeInterval   {max_iter};
purgeWrite      1;
writeFormat     ascii;
writePrecision  10;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;

functions
{{
    centerlineProfiles
    {{
        type            sets;
        libs            (sampling);
        executeControl  onEnd;
        writeControl    onEnd;
        setFormat       raw;
        interpolationScheme cellPoint;
        fields          (U);
        sets
        {{
            uAlongX05
            {{
                type    cloud;
                axis    xyz;
                points
                (
{_points_block(u_points)}
                );
            }}
            vAlongY05
            {{
                type    cloud;
                axis    xyz;
                points
                (
{_points_block(v_points)}
                );
            }}
        }}
    }}
}}
"""


def fv_schemes() -> str:
    return _foam_header("dictionary", "fvSchemes", "system") + """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
laplacianSchemes { default Gauss linear corrected; }
snGradSchemes   { default corrected; }

divSchemes
{
    default             none;
    div(phi,U)          bounded Gauss linearUpwind grad(U);
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
interpolationSchemes { default linear; }
wallDist        { method meshWave; }
"""


def fv_solution(tol_p: float = 1e-9, tol_u: float = 1e-10) -> str:
    return _foam_header("dictionary", "fvSolution", "system") + f"""
solvers
{{
    p
    {{
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       {tol_p};
        relTol          0.01;
    }}
    U
    {{
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       {tol_u};
        relTol          0.01;
    }}
}}

SIMPLE
{{
    nNonOrthogonalCorrectors 1;
    consistent      no;
    pRefCell        0;
    pRefValue       0;
    residualControl
    {{
        p               1e-08;
        U               1e-09;
    }}
}}

relaxationFactors
{{
    fields    {{ p 0.3; }}
    equations {{ U 0.7; }}
}}
"""


def transport_properties(re: float) -> str:
    nu = 1.0 / re
    return _foam_header("dictionary", "transportProperties", "constant") + f"""
transportModel  Newtonian;
nu              {nu:.10g};
"""


def turbulence_properties() -> str:
    return _foam_header("dictionary", "turbulenceProperties", "constant") + """
simulationType  laminar;
"""


def initial_fields() -> dict[str, str]:
    u = (_foam_header("volVectorField", "U", "0")
         + "dimensions      [0 1 -1 0 0 0 0];\n\n"
         + "internalField   uniform (0 0 0);\n\n"
         + "boundaryField\n{\n"
         + "    movingWall { type fixedValue; value uniform (1 0 0); }\n"
         + "    fixedWalls { type noSlip; }\n"
         + "    frontAndBack { type empty; }\n"
         + "}\n")
    p = (_foam_header("volScalarField", "p", "0")
         + "dimensions      [0 2 -2 0 0 0 0];\n\n"
         + "internalField   uniform 0;\n\n"
         + "boundaryField\n{\n"
         + "    movingWall { type zeroGradient; }\n"
         + "    fixedWalls { type zeroGradient; }\n"
         + "    frontAndBack { type empty; }\n"
         + "}\n")
    return {"U": u, "p": p}


def build_case(root: Path, re: float, n: int, max_iter: int = 3000,
               grading_ratio: float = 8.0) -> dict:
    root = Path(root)
    (root / "system").mkdir(parents=True, exist_ok=True)
    (root / "constant").mkdir(parents=True, exist_ok=True)
    (root / "0").mkdir(parents=True, exist_ok=True)

    (root / "system" / "blockMeshDict").write_text(block_mesh_dict(n, grading_ratio))
    (root / "system" / "controlDict").write_text(control_dict(max_iter))
    (root / "system" / "fvSchemes").write_text(fv_schemes())
    (root / "system" / "fvSolution").write_text(fv_solution())
    (root / "constant" / "transportProperties").write_text(transport_properties(re))
    (root / "constant" / "turbulenceProperties").write_text(turbulence_properties())
    for name, text in initial_fields().items():
        (root / "0" / name).write_text(text)

    return {"re": re, "n": n, "cells": n * n, "max_iter": max_iter,
            "grading_ratio": grading_ratio}


# ---------------------------------------------------------------------------
# Post-processing: parse the "raw" setFormat output and gate against Ghia.
# ---------------------------------------------------------------------------

def _parse_raw_xy_uvw(text: str) -> list[tuple[float, float, float, float, float, float]]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        try:
            x, y, z, ux, uy, uz = (float(p) for p in parts[:6])
        except ValueError:
            continue
        rows.append((x, y, z, ux, uy, uz))
    return rows


def find_sample_file(post_dir: Path, set_name: str) -> Path | None:
    """centerlineProfiles/<time>/<set_name>_U.xy"""
    candidates = sorted((post_dir / "centerlineProfiles").glob(f"*/{set_name}_U.xy"))
    return candidates[-1] if candidates else None


def gate_profile(sample_rows: list[tuple[float, float, float, float, float, float]],
                  ref: list[tuple[float, float]], component: str,
                  coord_index: int) -> dict:
    """Match each sampled row to the nearest reference coordinate (they are
    the SAME coordinates, sampled directly at Ghia's own points -- nearest
    match is just robust to any float/row-order slop from the sampler) and
    compute per-point and aggregate deviation. Boundary rows (y=0/1 or
    x=0/1) are excluded from the aggregate -- they are the imposed BC, not
    a solver prediction, and including them would inflate agreement
    artificially.
    """
    comp_idx = 3 if component == "u" else 4
    by_coord = {}
    for row in sample_rows:
        coord = row[coord_index]
        by_coord[round(coord, 4)] = row[comp_idx]

    points = []
    for coord, ref_val in ref:
        key = round(coord, 4)
        if key not in by_coord:
            # nearest-match fallback
            nearest = min(by_coord, key=lambda k: abs(k - coord))
            if abs(nearest - coord) > 1e-3:
                continue
            key = nearest
        measured = by_coord[key]
        is_boundary = coord in (0.0, 1.0)
        points.append({"coord": coord, "ref": ref_val, "measured": measured,
                        "boundary": is_boundary})

    interior = [p for p in points if not p["boundary"]]
    abs_errs = [abs(p["measured"] - p["ref"]) for p in interior]
    # normalize by the reference profile's own range (lid speed = 1 is the
    # natural velocity scale here; using it directly rather than a
    # percentage-of-value basis avoids blowup near ref~0 zero-crossings)
    max_abs_err = max(abs_errs) if abs_errs else float("nan")
    rms_abs_err = (sum(e * e for e in abs_errs) / len(abs_errs)) ** 0.5 if abs_errs else float("nan")
    return {"points": points, "n_interior": len(interior),
            "max_abs_err": max_abs_err, "rms_abs_err": rms_abs_err}
