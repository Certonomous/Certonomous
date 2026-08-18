#!/usr/bin/env python3
"""
Parametric generator for a 2D hypersonic-cylinder rhoCentralFoam case
(Billig standoff + modified-Newtonian surface-Cp gates), same non-dimensional
gas as F3_runs/make_wedge_case.py: gamma=1.4, mu=0 (inviscid), a=1 at T=1, so
the OpenFOAM inlet velocity magnitude U IS the Mach number directly.

Geometry (revision 2 -- see git history / F4 report Sec. "mesh design
iteration" for why): a SINGLE polar ("pie-slice") O-grid block, half-domain
(upper half, y>=0, symmetryPlane on the centreline ahead of the nose),
covering the windward face of a circular cylinder of radius R=1 centred at
the origin, flow in +x:
    r in [R, R_top]           (R_top: farfield radius, see domain_size())
    theta in [0, THETA_MAX_DEG]   (theta measured from the stagnation point)
  bottom edge (r=R, arc)          -> cylinder wall
  top edge (r=R_top, arc)         -> farfield (fixedValue freestream)
  left edge (theta=0, straight)   -> symmetryPlane (upstream axis)
  right edge (theta=THETA_MAX_DEG, straight) -> outlet (zeroGradient)

Revision 1 used a 2-block topology (flat upstream rectangle + a block with a
curved bottom but FLAT top), mirroring F3's wedge case. checkMesh flagged it
badly: max non-orthogonality 87.7 deg (144 severely non-orthogonal faces,
threshold 70), max skewness 5.14 (8 highly skew faces) -- the curved-bottom/
flat-top block distorts badly away from the shared vertical edge. Switching
to a true polar block (concentric arcs top and bottom, straight radial
sides) makes every internal face orthogonal by construction; checkMesh
confirms this below (see log.checkMesh in each case dir). This is the kind
of "did the geometry choice actually work" iteration the F3 methodology
calls for -- documented here rather than silently discarded.

Because the whole outer arc is engineered (via the Billig correlation, see
domain_size()) to stay strictly on the pre-shock side of the predicted bow
shock, the ENTIRE outer arc can carry a single fixedValue freestream
condition (not just a small "inlet" sliver) -- it really is undisturbed
freestream everywhere along it, verified pointwise against Billig's shock
shape at case-generation time (see the "farfield outer-arc pre-shock margin"
printout in build output).
"""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(__file__))
from billig_theory import billig_delta_over_R, billig_shock_x_of_y

R = 1.0
THETA_MAX_DEG = 75.0   # windward cutoff angle from the stagnation point
R_TOP_OVER_R = 1.7     # farfield radius, see domain_size() safety-margin check

RES = {
    "coarse": (50, 20),
    "medium": (100, 40),
    "fine":   (200, 80),
}   # (n_theta, n_r)

RADIAL_GRADING = 8.0  # simpleGrading expansion ratio, finer cells at the wall


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def foam_header(cls, obj):
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    object      {obj};
}}
"""


def domain_size(M, verbose=False):
    """A priori box sizing from the Billig correlation (module docstring):
    engineering domain sizing only, NOT part of the gate itself -- the gate
    compares the CFD's own independently detected shock/Cp against Billig/
    modified-Newtonian, this function just decides how big to mesh."""
    R_top = R_TOP_OVER_R * R
    theta_max = math.radians(THETA_MAX_DEG)
    delta_est = billig_delta_over_R(M) * R
    worst_margin = 1e9
    for th_deg in range(0, int(THETA_MAX_DEG) + 1):
        th = math.radians(th_deg)
        xp, yp = -R_top * math.cos(th), R_top * math.sin(th)
        sx = billig_shock_x_of_y(yp, R, M)
        worst_margin = min(worst_margin, sx - xp)
    if verbose:
        print(f"  M={M}: delta_est/R={delta_est:.4f}  R_top/R={R_TOP_OVER_R}  "
              f"outer-arc worst pre-shock margin(x)={worst_margin:.4f} (must be >0)")
    if worst_margin <= 0:
        raise RuntimeError(f"M={M}: outer farfield arc is NOT safely pre-shock "
                            f"(margin={worst_margin:.4f}); increase R_TOP_OVER_R")
    return R_top, delta_est, worst_margin


def make_case(case_dir, M, res_level, end_time_abs=6.0, nWrites=8):
    """end_time_abs: absolute non-dimensional end time (a=1 units), NOT scaled
    by M. Empirically (coarse-mesh M=6 convergence check, see F4 report Sec.
    "endTime / steady-state convergence"), the stagnation-region subsonic
    pocket relaxes on an O(domain-size/soundspeed) ~ O(1) timescale that is
    much longer than the freestream-advection Ltot/M estimate used in F3 --
    using an M-scaled flowthrough count badly under-ran the true settling
    time at high M. A single fixed absolute endTime (checked against a
    longer run that revealed a late-time FPE instability past t~8.4 on the
    coarse M=6 mesh -- see report) is used for every case instead, with
    multiple late-time snapshots written for an explicit convergence check."""
    theta_max = math.radians(THETA_MAX_DEG)
    R_top, delta_est, margin = domain_size(M, verbose=True)

    ntheta, nr = RES[res_level]
    z = 0.005  # thin 2D slab, same convention as F3 wedge/cone cases

    def pt(r, th, zz):
        return (-r * math.cos(th), r * math.sin(th), zz)

    V0 = pt(R, 0.0, -z);          V1 = pt(R, theta_max, -z)
    V2 = pt(R_top, theta_max, -z); V3 = pt(R_top, 0.0, -z)
    V0b = pt(R, 0.0, z);          V1b = pt(R, theta_max, z)
    V2b = pt(R_top, theta_max, z); V3b = pt(R_top, 0.0, z)

    verts = [V0, V1, V2, V3, V0b, V1b, V2b, V3b]
    vtxt = "\n".join(f"    ({v[0]:.12f} {v[1]:.12f} {v[2]:.12f})" for v in verts)

    theta_mid = theta_max / 2.0
    midWallF = pt(R, theta_mid, -z);      midWallB = pt(R, theta_mid, z)
    midFarF = pt(R_top, theta_mid, -z);   midFarB = pt(R_top, theta_mid, z)

    block = f"hex (0 1 2 3 4 5 6 7) ({ntheta} {nr} 1) simpleGrading (1 {RADIAL_GRADING} 1)"

    blockMeshDict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "blockMeshDict")}
scale 1;

vertices
(
{vtxt}
);

blocks
(
    {block}
);

edges
(
    arc 0 1 ({midWallF[0]:.12f} {midWallF[1]:.12f} {midWallF[2]:.12f})
    arc 4 5 ({midWallB[0]:.12f} {midWallB[1]:.12f} {midWallB[2]:.12f})
    arc 3 2 ({midFarF[0]:.12f} {midFarF[1]:.12f} {midFarF[2]:.12f})
    arc 7 6 ({midFarB[0]:.12f} {midFarB[1]:.12f} {midFarB[2]:.12f})
);

boundary
(
    cylinder
    {{
        type wall;
        faces ((0 1 5 4));
    }}
    outlet
    {{
        type patch;
        faces ((1 2 6 5));
    }}
    farfield
    {{
        type patch;
        faces ((2 3 7 6));
    }}
    bottom
    {{
        type symmetryPlane;
        faces ((3 0 4 7));
    }}
    defaultFaces
    {{
        type empty;
        faces ();
    }}
);

mergePatchPairs
(
);
"""
    write(f"{case_dir}/system/blockMeshDict", blockMeshDict)

    def bcfile(cls, obj, dim, internal, inlet_val, wall_type):
        return f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header(cls, obj)}
dimensions      {dim};

internalField   uniform {internal};

boundaryField
{{
    cylinder
    {{
        type            {wall_type};
    }}
    outlet
    {{
        type            zeroGradient;
    }}
    farfield
    {{
        type            fixedValue;
        value           uniform {inlet_val};
    }}
    bottom
    {{
        type            symmetryPlane;
    }}
    defaultFaces
    {{
        type            empty;
    }}
}}
"""

    write(f"{case_dir}/0/U", bcfile("volVectorField", "U", "[0 1 -1 0 0 0 0]",
                                     f"({M} 0 0)", f"({M} 0 0)", "slip"))
    write(f"{case_dir}/0/p", bcfile("volScalarField", "p", "[1 -1 -2 0 0 0 0]",
                                     "1", "1", "zeroGradient"))
    write(f"{case_dir}/0/T", bcfile("volScalarField", "T", "[0 0 0 1 0 0 0]",
                                     "1", "1", "zeroGradient"))

    endTime = end_time_abs

    controlDict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "controlDict")}
application     rhoCentralFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {endTime:.6f};
deltaT          1e-6;
writeControl    runTime;
writeInterval   {endTime/nWrites:.6f};
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
adjustTimeStep  yes;
maxCo           0.3;
maxDeltaT       1e-3;
"""
    write(f"{case_dir}/system/controlDict", controlDict)

    fvSchemes = f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "fvSchemes")}
fluxScheme          Kurganov;
ddtSchemes {{ default Euler; }}
gradSchemes {{ default Gauss linear; }}
divSchemes {{ default none; div(tauMC) Gauss linear; }}
laplacianSchemes {{ default Gauss linear corrected; }}
interpolationSchemes
{{
    default         linear;
    reconstruct(rho) vanLeer;
    reconstruct(U)  vanLeerV;
    reconstruct(T)  vanLeer;
}}
snGradSchemes {{ default corrected; }}
"""
    write(f"{case_dir}/system/fvSchemes", fvSchemes)

    fvSolution = f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "fvSolution")}
solvers
{{
    "(rho|rhoU|rhoE)" {{ solver diagonal; }}
    U
    {{
        solver smoothSolver; smoother GaussSeidel; nSweeps 2;
        tolerance 1e-09; relTol 0.01;
    }}
    h {{ $U; tolerance 1e-10; relTol 0; }}
}}
"""
    write(f"{case_dir}/system/fvSolution", fvSolution)

    thermo = f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "thermophysicalProperties")}
thermoType
{{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleInternalEnergy;
}}
mixture
{{
    specie {{ molWeight 11640.3; }}
    thermodynamics {{ Cp 2.5; Hf 0; }}
    transport {{ mu 0; Pr 1; }}
}}
"""
    write(f"{case_dir}/constant/thermophysicalProperties", thermo)

    write(f"{case_dir}/constant/turbulenceProperties", f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "turbulenceProperties")}
simulationType laminar;
""")

    meta = dict(case_dir=case_dir, M=M, res_level=res_level, R=R,
                theta_max_deg=THETA_MAX_DEG, R_top=R_top, delta_billig_est=delta_est,
                preshock_margin=margin, endTime=endTime, ntheta=ntheta, nr=nr)
    return meta


if __name__ == "__main__":
    case_dir, M, res_level = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    meta = make_case(case_dir, M, res_level)
    print(meta)
