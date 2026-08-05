"""Generate an in-house periodic-hill (ERCOFTAC UFR 3-30 / Breuer) blockMeshDict.

Geometry is the published ERCOFTAC piecewise-cubic hill profile (hill height
h = 28 mm, one flank spanning 0 <= x <= 54 mm), nondimensionalised by h, with
domain Lx = 9h, Ly = 3.035h, streamwise-cyclic.  Nothing here is copied from
the benchmark's shipped mesh: the shipped mesh is used ONLY as an independent
check of this profile (see verify_profile()).

Usage: make_ph_mesh.py <case_dir> <nx> <ny> <first_dy>
"""
import sys, math
import numpy as np

H_MM = 28.0
FLANK_MM = 54.0
LX = 9.0
LY = 3.035

# ERCOFTAC UFR 3-30 published hill polynomial, x and y in mm, six segments.
COEFF = [
    (0.0,  9.0, (2.800000000000e+01,  0.000000000000e+00,  6.775070969851e-03, -2.124527775800e-03)),
    (9.0, 14.0, (2.507355893131e+01,  9.754803562315e-01, -1.016116352781e-01,  1.889794677828e-03)),
    (14.0, 20.0, (2.579601052357e+01,  8.206693007457e-01, -9.055370274339e-02,  1.626510569859e-03)),
    (20.0, 30.0, (4.046435022819e+01, -1.379581654948e+00,  1.945884504128e-02, -2.070318932190e-04)),
    (30.0, 40.0, (1.792461334664e+01,  8.743920332081e-01, -5.567361123058e-02,  6.277731764683e-04)),
    (40.0, 54.0, (5.639011190988e+01, -2.010520359035e+00,  1.644919857549e-02,  2.674976141766e-05)),
]


def hill_mm(x):
    """Hill height in mm at streamwise station x (mm), 0 <= x <= 54."""
    for lo, hi, c in COEFF:
        if x <= hi:
            y = c[0] + c[1] * x + c[2] * x ** 2 + c[3] * x ** 3
            return min(H_MM, max(0.0, y))
    return 0.0


def y_bottom(x):
    """Lower-wall height in hill units at x/h in [0, 9]."""
    flank = FLANK_MM / H_MM  # 1.928571...
    if x <= flank:
        return hill_mm(x * H_MM) / H_MM
    if x >= LX - flank:
        return hill_mm((LX - x) * H_MM) / H_MM
    return 0.0


def verify_profile(wall_xy_path):
    """Independent check: our polynomial vs the benchmark's shipped wall points."""
    wp = np.loadtxt(wall_xy_path)
    err = np.array([abs(y_bottom(x) - y) for x, y in wp])
    return float(err.max()), float(err.mean())


def wall_polyline(n_flank=600, n_flat=60):
    xs = list(np.linspace(0.0, FLANK_MM / H_MM, n_flank, endpoint=False))
    xs += list(np.linspace(FLANK_MM / H_MM, LX - FLANK_MM / H_MM, n_flat, endpoint=False))
    xs += list(np.linspace(LX - FLANK_MM / H_MM, LX, n_flank))
    xs = sorted(set(round(x, 12) for x in xs))
    return [(x, y_bottom(x)) for x in xs][1:-1]  # blockMesh supplies the end vertices


def grading_for_first_cell(height, ncells_half, first_dy):
    """Expansion ratio (last/first cell) for a half-height with a target first cell."""
    def total(r):
        if abs(r - 1.0) < 1e-12:
            return first_dy * ncells_half
        return first_dy * (r ** ncells_half - 1.0) / (r - 1.0)
    lo, hi = 1.0, 1.5
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if total(mid) < height:
            lo = mid
        else:
            hi = mid
    r = 0.5 * (lo + hi)
    return r ** (ncells_half - 1)


HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
| Certonomous in-house periodic-hill mesh, ERCOFTAC UFR 3-30 geometry         |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale   1;

vertices
(
    (0    1      -0.1)
    ({LX} 1      -0.1)
    ({LX} {LY}   -0.1)
    (0    {LY}   -0.1)
    (0    1       0.1)
    ({LX} 1       0.1)
    ({LX} {LY}    0.1)
    (0    {LY}    0.1)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1)
    simpleGrading (1 (({half} {half} {exp})({half} {half} {inv})) 1)
);

edges
(
    polyLine 0 1
    (
{pl0}
    )
    polyLine 4 5
    (
{pl1}
    )
);

boundary
(
    bottomWall
    {{
        type wall;
        faces ((0 1 5 4));
    }}
    topWall
    {{
        type wall;
        faces ((3 7 6 2));
    }}
    inlet
    {{
        type cyclic;
        neighbourPatch outlet;
        transform translational;
        separationVector (-{LX} 0 0);
        faces ((0 4 7 3));
    }}
    outlet
    {{
        type cyclic;
        neighbourPatch inlet;
        transform translational;
        separationVector ({LX} 0 0);
        faces ((1 2 6 5));
    }}
    frontAndBack
    {{
        type empty;
        faces ((0 3 2 1) (4 5 6 7));
    }}
);

// ************************************************************************* //
"""


def main():
    case, nx, ny, first_dy = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    assert ny % 2 == 0, "ny must be even for a symmetric two-sided grading"
    height = LY - 0.0  # grade against the tallest column (flat section); crest columns
    exp = grading_for_first_cell(height / 2.0, ny // 2, first_dy)
    pts = wall_polyline()
    pl0 = "\n".join("        ({:.10f} {:.10f} -0.1)".format(x, y) for x, y in pts)
    pl1 = "\n".join("        ({:.10f} {:.10f}  0.1)".format(x, y) for x, y in pts)
    txt = HEADER.format(LX=LX, LY=LY, nx=nx, ny=ny, half=0.5,
                        exp="{:.8f}".format(exp), inv="{:.8f}".format(1.0 / exp),
                        pl0=pl0, pl1=pl1)
    with open(case + "/system/blockMeshDict", "w") as fh:
        fh.write(txt)
    print("nx={} ny={} cells={} expansion={:.4f} target_first_dy={}".format(
        nx, ny, nx * ny, exp, first_dy))


if __name__ == "__main__":
    main()
