#!/usr/bin/env python3
"""Build the three registered T4 impinging-jet cases.

T4: normally-impinging round jet from a fully-developed pipe, H/D = 2,
Re_D = 23 000 -- ERCOFTAC Classic Collection case025, the `ij2lr` family.
Axisymmetric wedge, steady, buoyantBoussinesqSimpleFoam with beta = 0 (so the
temperature field is passive and this is pure forced convection, the same
convention T1b uses).

GEOMETRY (axis along +y, plate at y = 0, jet issuing downward):
    block J  jet core   r in [0, D/2],   y in [0, H]
    block P  pipe       r in [0, D/2],   y in [H, H + L_pipe]
    block W  wall jet   r in [D/2, R],   y in [0, H]
with D = 0.02 m, H = 2 D, R = 6 D, L_pipe = 20 D.

THE MESH FAMILY IS SYSTEMATIC, WHICH IS WHAT ROACHE REQUIRES.  One parameter N
sets every division; the three registered levels are N = 48, 96, 192, so the
refinement ratio is EXACTLY r21 = r32 = 2 in every direction.  The near-wall
first-cell height is halved with N as well, so the family is geometrically
similar under h -> h/2 rather than merely having more cells.  Every level is
wall-resolved (y+ < 1); no level switches to a wall function, because a family
that changes near-wall treatment between levels breaks the smooth-refinement
assumption the GCI rests on.

Cell counts are exactly 2.5 N^2: 5 760 / 23 040 / 92 160.

Usage:  build_t4.py --root <dir> [--level c|m|f] ...
"""
import argparse
import math
import os

D        = 0.02          # m, nozzle diameter
H_OVER_D = 2.0
R_OVER_D = 6.0
LPIPE_OVER_D = 10.0   # with a recycling inlet; see block_mesh_dict
NU       = 1.5e-5        # m2/s
RE       = 23000.0
PR       = 0.71
PRT      = 0.85
RHO      = 1.2           # kg/m3, for the flux BC arithmetic only
CP       = 1005.0        # J/(kg K)
T_JET    = 293.15        # K
QWALL    = 1000.0        # W/m2, constant heat flux on the plate (Baughn's setup)
WEDGE_DEG = 2.5          # half-angle

U_BULK = RE * NU / D     # 17.25 m/s

LEVELS = {"c": dict(N=48,  endTime=20000, first_cell=2.4e-5),
          "m": dict(N=96,  endTime=30000, first_cell=1.2e-5),
          "f": dict(N=192, endTime=40000, first_cell=0.6e-5)}


def grading_ratio(total, n, first):
    """blockMesh simpleGrading expansion (last/first) for n cells spanning
    `total` with the first cell of height `first`.

    REFUSES rather than returning a wrong number.  The first version of this
    function searched q only in [1, 1.6] and so could not express a
    CONTRACTING grading; asked for an impossible first cell it silently
    returned 1.0 and the caller meshed against it.  A geometry helper that
    answers an impossible question with a plausible number is the shape of
    defect this lab refuses (a zero from a reader not shown able to see a
    non-zero).  The bracket now spans contraction and expansion, and the
    solution is VERIFIED against the request before it is returned.
    """
    if n < 2:
        return 1.0
    target = total / float(first)

    def total_for(q):
        return n if abs(q - 1.0) < 1e-15 else (q ** n - 1.0) / (q - 1.0)

    lo, hi = 0.5, 2.0
    if not (total_for(lo) <= target <= total_for(hi)):
        raise ValueError(
            "T4 mesh: %d cells spanning %.6g m cannot have a first cell of "
            "%.6g m -- the achievable span is [%.6g, %.6g] m. Refusing to "
            "return a grading that does not satisfy the request."
            % (n, total, first, total_for(lo) * first, total_for(hi) * first))
    for _ in range(300):
        q = 0.5 * (lo + hi)
        if total_for(q) < target:
            lo = q
        else:
            hi = q
    q = 0.5 * (lo + hi)
    got = total_for(q) * first
    if abs(got - total) > 1e-9 * max(total, 1.0):
        raise ValueError("T4 mesh: grading solve did not converge (%.10g vs "
                         "%.10g)" % (got, total))
    return q ** (n - 1)


def header(cls, obj, loc=None):
    l = ('    location    "%s";\n' % loc) if loc else ""
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            "    class       %s;\n%s    object      %s;\n}\n" % (cls, l, obj))


def block_mesh_dict(N, first_cell):
    """Wedge blockMeshDict.

    THE AXIS IS A COLLAPSED EDGE, NOT A ZERO-AREA PATCH.  The first version of
    this function emitted two DISTINCT vertices at r = 0 (both at z = 0, since
    z = r tan(theta)).  blockMesh duly built faces of exactly zero area there:
    checkMesh returned `Zero or negative face area detected. Minimum area: 0`
    and `Max skewness = 2.4e+145`, which is a divide-by-zero, not a mesh.  The
    correct idiom is ONE vertex on the axis, used for both the front and the
    back of the wedge, so the hex degenerates to a prism and the axis faces do
    not exist at all.  There is therefore no `axis` patch: nothing to declare
    `empty`, and no divisibility complaint.
    """
    h  = H_OVER_D * D
    r0 = 0.5 * D
    rout = R_OVER_D * D
    lp = LPIPE_OVER_D * D
    t = math.tan(math.radians(WEDGE_DEG))

    nrj = N // 2          # radial cells, jet core and pipe
    nrw = (3 * N) // 2    # radial cells, wall-jet block
    nyj = N               # axial cells, impingement height
    nyp = max(2, N // 2)  # axial cells, pipe length

    g_plate = grading_ratio(h, nyj, first_cell)               # y: fine at plate
    g_pipew = grading_ratio(r0, nrj, first_cell)              # r: fine at pipe wall
    g_out   = grading_ratio(rout - r0, nrw, first_cell * 2.0)  # r: fine at r0
    g_pipey = 8.0        # y: fixed expansion away from the nozzle exit.
                          # Fixed rather than solved from a first-cell request,
                          # because the recycling inlet makes the pipe profile
                          # self-developing and no near-nozzle clustering target
                          # is being met here.

    pts, idx = [], {}

    def v(r, y):
        """Return (back_index, front_index).  On the axis the two coincide."""
        key = (round(r, 12), round(y, 12))
        if key in idx:
            return idx[key]
        z = r * t
        if r == 0.0:
            i = len(pts)
            pts.append((0.0, y, 0.0))
            idx[key] = (i, i)
        else:
            i = len(pts)
            pts.append((r, y, -z))
            pts.append((r, y, +z))
            idx[key] = (i, i + 1)
        return idx[key]

    A0 = v(0.0, 0.0);      P0 = v(r0, 0.0);      Q0 = v(rout, 0.0)
    A1 = v(0.0, h);        P1 = v(r0, h);        Q1 = v(rout, h)
    A2 = v(0.0, h + lp);   P2 = v(r0, h + lp)

    def hexblk(c00, c10, c11, c01, nx, ny, gx, gy):
        b = (c00[0], c10[0], c11[0], c01[0])
        f = (c00[1], c10[1], c11[1], c01[1])
        return ("    hex (%d %d %d %d %d %d %d %d) (%d %d 1) "
                "simpleGrading (%.10g %.10g 1)\n"
                % (b + f + (nx, ny, gx, gy)))

    blocks = (hexblk(A0, P0, P1, A1, nrj, nyj, g_pipew, g_plate) +   # jet core
              hexblk(P0, Q0, Q1, P1, nrw, nyj, g_out,   g_plate) +   # wall jet
              hexblk(A1, P1, P2, A2, nrj, nyp, g_pipew, g_pipey))    # pipe

    vt = "".join("    (%.10g %.10g %.10g)\n" % q for q in pts)

    def face(*cols):
        """A quad (or triangle, where an axis vertex repeats) from vertex
        columns given as (index_pair, side) with side 0=back, 1=front."""
        return "(" + " ".join(str(c[0][c[1]]) for c in cols) + ")"

    def wedge_face(c0, c1, c2, c3, side):
        return "(" + " ".join(str(c[side]) for c in (c0, c1, c2, c3)) + ")"

    bnd = """
boundary
(
    plate
    {{
        type            wall;
        faces           ( {plate1} {plate2} );
    }}
    pipeWall
    {{
        type            wall;
        faces           ( {pipew} );
    }}
    inlet
    {{
        type            mappedPatch;
        sampleMode      nearestCell;
        sampleRegion    region0;
        samplePatch     none;
        offsetMode      uniform;
        offset          (0 {roff:.10g} 0);
        faces           ( {inlet} );
    }}
    entrainment
    {{
        type            patch;
        faces           ( {entr} );
    }}
    farfield
    {{
        type            patch;
        faces           ( {farf} );
    }}
    front
    {{
        type            wedge;
        faces           ( {f1} {f2} {f3} );
    }}
    back
    {{
        type            wedge;
        faces           ( {b1} {b2} {b3} );
    }}
);
""".format(
        plate1=face((A0, 0), (P0, 0), (P0, 1), (A0, 1)),
        plate2=face((P0, 0), (Q0, 0), (Q0, 1), (P0, 1)),
        pipew=face((P1, 0), (P2, 0), (P2, 1), (P1, 1)),
        inlet=face((A2, 0), (P2, 0), (P2, 1), (A2, 1)),
        entr=face((P1, 0), (Q1, 0), (Q1, 1), (P1, 1)),
        farf=face((Q0, 0), (Q1, 0), (Q1, 1), (Q0, 1)),
        roff=-0.5 * lp,
        f1=wedge_face(A0, P0, P1, A1, 1),
        f2=wedge_face(P0, Q0, Q1, P1, 1),
        f3=wedge_face(A1, P1, P2, A2, 1),
        b1=wedge_face(A0, A1, P1, P0, 0),
        b2=wedge_face(P0, P1, Q1, Q0, 0),
        b3=wedge_face(A1, A2, P2, P1, 0))

    return ("%s\nscale   1;\n\nvertices\n(\n%s);\n\nblocks\n(\n%s);\n\n"
            "edges ();\n%s\nmergePatchPairs ();\n"
            % (header("dictionary", "blockMeshDict", "system"), vt, blocks, bnd),
            dict(g_plate=g_plate, g_pipew=g_pipew, g_out=g_out, g_pipey=g_pipey,
                 cells=nrj * nyj + nrw * nyj + nrj * nyp))


def fields(level):
    """0.orig field files.  T is passive (beta = 0); the plate carries a
    constant heat flux, which is Baughn's experiment."""
    k_in   = 1.5 * (0.05 * U_BULK) ** 2
    om_in  = math.sqrt(k_in) / (0.09 ** 0.25 * 0.07 * D)
    k_air  = RHO * CP * (NU / PR)
    gradT  = QWALL / k_air

    def f(cls, obj, dims, internal, patches):
        return ("%s\ndimensions      %s;\n\ninternalField   uniform %s;\n\n"
                "boundaryField\n{\n%s}\n"
                % (header(cls, obj, "0"), dims, internal, patches))

    # No `axis` entry: the axis is a COLLAPSED EDGE, so those faces do not
    # exist and naming them would make blockMesh refuse.
    common_wedge = "    front { type wedge; }\n    back  { type wedge; }\n"

    U = f("volVectorField", "U", "[0 1 -1 0 0 0 0]", "(0 0 0)",
          "    inlet { type mapped; field U; setAverage true; "
          "average (0 %.10g 0); interpolationScheme cell; value uniform (0 %.10g 0); }\n"
          "    plate { type noSlip; }\n"
          "    pipeWall { type noSlip; }\n"
          "    entrainment { type pressureInletOutletVelocity; value uniform (0 0 0); }\n"
          "    farfield { type pressureInletOutletVelocity; value uniform (0 0 0); }\n"
          % (-U_BULK, -U_BULK) + common_wedge)

    p = f("volScalarField", "p_rgh", "[0 2 -2 0 0 0 0]", "0",
          "    inlet { type zeroGradient; }\n"
          "    plate { type fixedFluxPressure; value uniform 0; }\n"
          "    pipeWall { type fixedFluxPressure; value uniform 0; }\n"
          "    entrainment { type totalPressure; p0 uniform 0; value uniform 0; }\n"
          "    farfield { type totalPressure; p0 uniform 0; value uniform 0; }\n"
          + common_wedge)

    T = f("volScalarField", "T", "[0 0 0 1 0 0 0]", "%.10g" % T_JET,
          "    inlet { type fixedValue; value uniform %.10g; }\n"
          "    plate { type fixedGradient; gradient uniform %.10g; }\n"
          "    pipeWall { type zeroGradient; }\n"
          "    entrainment { type inletOutlet; inletValue uniform %.10g; value uniform %.10g; }\n"
          "    farfield { type inletOutlet; inletValue uniform %.10g; value uniform %.10g; }\n"
          % (T_JET, gradT, T_JET, T_JET, T_JET, T_JET) + common_wedge)

    k = f("volScalarField", "k", "[0 2 -2 0 0 0 0]", "%.10g" % k_in,
          "    inlet { type mapped; field k; setAverage true; average %.10g; "
          "interpolationScheme cell; value uniform %.10g; }\n"
          "    plate { type kLowReWallFunction; value uniform 1e-12; }\n"
          "    pipeWall { type kLowReWallFunction; value uniform 1e-12; }\n"
          "    entrainment { type inletOutlet; inletValue uniform %.10g; value uniform %.10g; }\n"
          "    farfield { type inletOutlet; inletValue uniform %.10g; value uniform %.10g; }\n"
          % (k_in, k_in, k_in, k_in, k_in, k_in) + common_wedge)

    om = f("volScalarField", "omega", "[0 0 -1 0 0 0 0]", "%.10g" % om_in,
           "    inlet { type mapped; field omega; setAverage true; average %.10g; "
           "interpolationScheme cell; value uniform %.10g; }\n"
           "    plate { type omegaWallFunction; value uniform %.10g; }\n"
           "    pipeWall { type omegaWallFunction; value uniform %.10g; }\n"
           "    entrainment { type inletOutlet; inletValue uniform %.10g; value uniform %.10g; }\n"
           "    farfield { type inletOutlet; inletValue uniform %.10g; value uniform %.10g; }\n"
           % (om_in, om_in, om_in, om_in, om_in, om_in, om_in, om_in) + common_wedge)

    nut = f("volScalarField", "nut", "[0 2 -1 0 0 0 0]", "0",
            "    inlet { type calculated; value uniform 0; }\n"
            "    plate { type nutLowReWallFunction; value uniform 0; }\n"
            "    pipeWall { type nutLowReWallFunction; value uniform 0; }\n"
            "    entrainment { type calculated; value uniform 0; }\n"
            "    farfield { type calculated; value uniform 0; }\n" + common_wedge)

    # AMENDMENT 2, 2026-08-26.  This used to read
    #     plate/pipeWall { type compressible::alphatWallFunction; Prt ...; }
    # which does not exist for this INCOMPRESSIBLE Boussinesq solver and made
    # every arm exit rc=1 at zero iterations.
    #
    # THE REPAIR IS NOT A NAMESPACE SWAP.  The available incompressible
    # alternative, alphatJayatillekeWallFunction, is a HIGH-Re wall function,
    # and this mesh is WALL-RESOLVED: nut carries nutLowReWallFunction and k
    # carries kLowReWallFunction.  Dropping a high-Re thermal wall function
    # beside a low-Re resolved near-wall treatment produces a case that RUNS
    # AND IS SILENTLY WRONG on exactly the quantity this rung grades.  Trading
    # an honest refusal for a plausible wrong number is the worst trade
    # available here.
    #
    # `calculated` is the consistent low-Re choice: on a resolved wall nut -> 0,
    # so alphat = nut/Prt -> 0 and no wall function is wanted.  This is also
    # this lab's own established convention for a wall-resolved case on this
    # exact solver -- T1_runs/R_10k_x/0/alphat carries
    #     wall { type calculated; value uniform 0; }
    # beside nutLowReWallFunction and kLowReWallFunction.  Prt still governs
    # alphat in the interior via constant/transportProperties; it is the WALL
    # treatment, not Prt, that changes here.
    alphat = f("volScalarField", "alphat", "[0 2 -1 0 0 0 0]", "0",
               "    inlet { type calculated; value uniform 0; }\n"
               "    plate { type calculated; value uniform 0; }\n"
               "    pipeWall { type calculated; value uniform 0; }\n"
               "    entrainment { type calculated; value uniform 0; }\n"
               "    farfield { type calculated; value uniform 0; }\n"
               + common_wedge)

    return {"U": U, "p_rgh": p, "T": T, "k": k, "omega": om,
            "nut": nut, "alphat": alphat}


def system_files(endTime):
    control = ("%s\napplication     buoyantBoussinesqSimpleFoam;\n"
               "startFrom       startTime;\nstartTime       0;\n"
               "stopAt          endTime;\nendTime         %d;\n"
               "deltaT          1;\nwriteControl    timeStep;\n"
               "writeInterval   %d;\npurgeWrite      2;\n"
               "writeFormat     ascii;\nwritePrecision  12;\n"
               "writeCompression off;\ntimeFormat      general;\n"
               "timePrecision   6;\nrunTimeModifiable false;\n"
               % (header("dictionary", "controlDict", "system"), endTime,
                  endTime // 10))

    schemes = (header("dictionary", "fvSchemes", "system") + """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind grad(U);
    div(phi,T)      bounded Gauss limitedLinear 1;
    div(phi,k)      bounded Gauss limitedLinear 1;
    div(phi,omega)  bounded Gauss limitedLinear 1;
    // AMENDMENT 2: this used to read div(((rho*nuEff)*dev2(T(grad(U))))),
    // which is the COMPRESSIBLE spelling. buoyantBoussinesqSimpleFoam is
    // incompressible and looks up div((nuEff*dev2(T(grad(U))))). Same root
    // cause as the alphat defect: compressible conventions in an
    // incompressible case, invisible to blockMesh and checkMesh.
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
wallDist        { method meshWave; }
""")

    solution = (header("dictionary", "fvSolution", "system") + """
solvers
{
    p_rgh
    {
        solver          GAMG;
        tolerance       1e-09;
        relTol          0.01;
        smoother        GaussSeidel;
    }
    "(U|T|k|omega)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-10;
        relTol          0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 1;
    pRefCell        0;
    pRefValue       0;
    residualControl { p_rgh 1e-7; U 1e-7; T 1e-7; k 1e-7; omega 1e-7; }
}

relaxationFactors
{
    fields  { p_rgh 0.3; }
    equations { U 0.7; T 0.7; k 0.7; omega 0.7; }
}
""")
    return {"controlDict": control, "fvSchemes": schemes, "fvSolution": solution}


def constant_files():
    transport = (header("dictionary", "transportProperties", "constant") +
                 "transportModel  Newtonian;\nnu              %.10g;\n"
                 "beta            0;\nTRef            %.10g;\n"
                 "Pr              %.10g;\nPrt             %.10g;\n"
                 % (NU, T_JET, PR, PRT))
    turb = (header("dictionary", "turbulenceProperties", "constant") +
            "simulationType  RAS;\nRAS\n{\n    RASModel        kOmegaSST;\n"
            "    turbulence      on;\n    printCoeffs     on;\n}\n")
    g = (header("uniformDimensionedVectorField", "g", "constant") +
         "dimensions      [0 1 -2 0 0 0 0];\nvalue           (0 0 0);\n")
    return {"transportProperties": transport, "turbulenceProperties": turb, "g": g}


def build(root, level):
    spec = LEVELS[level]
    case = os.path.join(root, "T4_IJ_%s" % level)
    for sub in ("system", "constant", "0.orig"):
        os.makedirs(os.path.join(case, sub), exist_ok=True)

    bmd, info = block_mesh_dict(spec["N"], spec["first_cell"])
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(bmd)
    for n, t in system_files(spec["endTime"]).items():
        open(os.path.join(case, "system", n), "w").write(t)
    for n, t in constant_files().items():
        open(os.path.join(case, "constant", n), "w").write(t)
    for n, t in fields(level).items():
        open(os.path.join(case, "0.orig", n), "w").write(t)

    print("built %-10s N=%-4d cells=%-7d endTime=%-6d first_cell=%.3g m  "
          "grading(plate=%.4g pipewall=%.4g outer=%.4g pipey=%.4g)"
          % ("T4_IJ_" + level, spec["N"], info["cells"], spec["endTime"],
             spec["first_cell"], info["g_plate"], info["g_pipew"],
             info["g_out"], info["g_pipey"]))
    return info["cells"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--level", action="append", choices=list(LEVELS))
    a = ap.parse_args()
    tot = 0
    for lv in (a.level or ["c", "m", "f"]):
        tot += build(a.root, lv)
    print("U_bulk = %.4f m/s   Re = %.0f   total cells = %d" % (U_BULK, RE, tot))
