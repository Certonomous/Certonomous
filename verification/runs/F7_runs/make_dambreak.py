#!/usr/bin/env python3
"""Generate a Martin & Moyce square-column dam-break case for interFoam,
matched to the reference setup of Leakey, Glenis & Hewett (arXiv:2108.08769,
Sec 3.3.2): domain 15a wide x 1.25a tall, all four boundaries walls, square
water column a x a in the corner, g = (0,-9.81,0), rho_water=1000,
rho_air=1, instantaneous release.

One knob per flag so every rung of a ladder differs in exactly one variable.

  make_dambreak.py --out DIR --res 32            # dx=dy=a/32
  make_dambreak.py --out DIR --res 32 --calpha 0 # interface compression off
  make_dambreak.py --out DIR --res 32 --sigma 0  # surface tension off (matches ref)

Reference paper is inviscid and has no surface tension and no interface
compression; --calpha 0 --sigma 0 --inviscid reproduces its physical model as
closely as interFoam allows.
"""
import argparse
import os
import shutil

A = 0.05715           # m, Martin & Moyce a = 2 1/4 in
DOMAIN_L = 15.0       # in units of a
DOMAIN_H = 1.25       # in units of a  (paper's own domain)

HEAD = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       %s;
    object      %s;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

"""


def w(path, cls, obj, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(HEAD % (cls, obj))
        f.write(body)
        f.write("\n// *********************************************************************** //\n")


def blockmesh(nx, ny):
    return """a       %(a)s;
convertToMeters 1;

vertices
(
    (0                  0                    0)
    (#calc "%(L)s*$a"   0                    0)
    (#calc "%(L)s*$a"   #calc "%(H)s*$a"     0)
    (0                  #calc "%(H)s*$a"     0)
    (0                  0                    #calc "$a/%(nx)d")
    (#calc "%(L)s*$a"   0                    #calc "$a/%(nx)d")
    (#calc "%(L)s*$a"   #calc "%(H)s*$a"     #calc "$a/%(nx)d")
    (0                  #calc "%(H)s*$a"     #calc "$a/%(nx)d")
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (%(nx)d %(ny)d 1) simpleGrading (1 1 1)
);

edges ();

boundary
(
    leftWall  { type wall; faces ( (0 4 7 3) ); }
    rightWall { type wall; faces ( (1 2 6 5) ); }
    lowerWall { type wall; faces ( (0 1 5 4) ); }
    atmosphere{ type wall; faces ( (3 7 6 2) ); }
    defaultFaces { type empty; faces ( (0 3 2 1) (4 5 6 7) ); }
);

mergePatchPairs ();
""" % dict(a=A, L=DOMAIN_L, H=DOMAIN_H, nx=nx, ny=ny)


SETFIELDS = """defaultFieldValues
(
    volScalarFieldValue alpha.water 0
);

regions
(
    boxToCell
    {
        box (0 0 -1) (%(a)s %(a)s 1);
        fieldValues ( volScalarFieldValue alpha.water 1 );
    }
);
""" % dict(a=A)


ALPHA0 = """dimensions      [0 0 0 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    "(leftWall|rightWall|lowerWall|atmosphere)" { type zeroGradient; }
    defaultFaces { type empty; }
}
"""

P0 = """dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    "(leftWall|rightWall|lowerWall|atmosphere)" { type fixedFluxPressure; value uniform 0; }
    defaultFaces { type empty; }
}
"""


def u0(slip):
    wall = "slip" if slip else "noSlip"
    return """dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);

boundaryField
{
    "(leftWall|rightWall|lowerWall|atmosphere)" { type %s; }
    defaultFaces { type empty; }
}
""" % wall


def transport(sigma, nu_w, nu_a):
    return """phases          (water air);

water { transportModel Newtonian; nu %g; rho 1000; }
air   { transportModel Newtonian; nu %g; rho 1;    }

sigma           %g;
""" % (nu_w, nu_a, sigma)


def fvschemes():
    return """ddtSchemes      { default Euler; }

gradSchemes     { default Gauss linear; }

divSchemes
{
    div(rhoPhi,U)    Gauss linearUpwind grad(U);
    div(phi,alpha)   Gauss vanLeer;
    div(phirb,alpha) Gauss linear;
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
"""


def fvsolution(calpha, nsub, ncorr):
    return """solvers
{
    "alpha.water.*"
    {
        nAlphaCorr      %(ncorr)d;
        nAlphaSubCycles %(nsub)d;
        cAlpha          %(calpha)g;

        MULESCorr       yes;
        nLimiterIter    5;

        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-8;
        relTol          0;
    }

    "pcorr.*"  { solver PCG; preconditioner DIC; tolerance 1e-5;  relTol 0; }
    p_rgh      { solver PCG; preconditioner DIC; tolerance 1e-07; relTol 0.05; }
    p_rghFinal { $p_rgh; relTol 0; }
    U          { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-06; relTol 0; }
}

PIMPLE
{
    momentumPredictor   no;
    nOuterCorrectors    1;
    nCorrectors         3;
    pRefCell            0;
    pRefValue           0;
    nNonOrthogonalCorrectors 0;
}

relaxationFactors { equations { ".*" 1; } }
""" % dict(calpha=calpha, nsub=nsub, ncorr=ncorr)


def controldict(end_time, write_interval, maxco, maxalphaco, dt0):
    return """application     interFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         %(end)g;
deltaT          %(dt0)g;

writeControl    adjustableRunTime;
writeInterval   %(wi)g;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable no;

adjustTimeStep  yes;
maxCo           %(maxco)g;
maxAlphaCo      %(maxalphaco)g;
maxDeltaT       0.01;
""" % dict(end=end_time, dt0=dt0, wi=write_interval, maxco=maxco,
           maxalphaco=maxalphaco)


def decompose(nranks):
    return """numberOfSubdomains %d;
method          simple;
coeffs { n (%d 1 1); }
""" % (nranks, nranks)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--res", type=int, required=True,
                   help="cells per a in x (dx=a/res)")
    p.add_argument("--yres", type=int, default=None,
                   help="cells per a in y (dy=a/yres); defaults to --res. "
                        "Lets vertical resolution of the thin leading film be "
                        "varied independently of streamwise resolution.")
    p.add_argument("--calpha", type=float, default=1.0)
    p.add_argument("--sigma", type=float, default=0.07)
    p.add_argument("--nsub", type=int, default=1, help="nAlphaSubCycles")
    p.add_argument("--nalphacorr", type=int, default=2)
    p.add_argument("--maxco", type=float, default=0.5)
    p.add_argument("--maxalphaco", type=float, default=0.5)
    p.add_argument("--slip", action="store_true")
    p.add_argument("--inviscid", action="store_true",
                   help="nu -> 1e-12 for both phases (reference paper ignores viscosity)")
    p.add_argument("--endtime", type=float, default=0.8)
    p.add_argument("--writeinterval", type=float, default=0.025)
    p.add_argument("--ranks", type=int, default=4)
    args = p.parse_args()

    yres = args.yres or args.res
    nx = int(round(DOMAIN_L * args.res))
    ny_f = DOMAIN_H * yres
    ny = int(round(ny_f))
    assert abs(ny - ny_f) < 1e-9, "1.25*yres must be an integer (multiple of 4)"

    out = args.out
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    nu_w, nu_a = (1e-12, 1e-12) if args.inviscid else (1e-6, 1.48e-5)

    w(out + "/system/blockMeshDict", "dictionary", "blockMeshDict", blockmesh(nx, ny))
    w(out + "/system/setFieldsDict", "dictionary", "setFieldsDict", SETFIELDS)
    w(out + "/system/fvSchemes", "dictionary", "fvSchemes", fvschemes())
    w(out + "/system/fvSolution", "dictionary", "fvSolution",
      fvsolution(args.calpha, args.nsub, args.nalphacorr))
    w(out + "/system/controlDict", "dictionary", "controlDict",
      controldict(args.endtime, args.writeinterval, args.maxco, args.maxalphaco,
                  1e-4 * 20.0 / max(args.res, yres)))
    w(out + "/system/decomposeParDict", "dictionary", "decomposeParDict",
      decompose(args.ranks))
    w(out + "/constant/transportProperties", "dictionary", "transportProperties",
      transport(args.sigma, nu_w, nu_a))
    w(out + "/constant/g", "uniformDimensionedVectorField", "g",
      "dimensions      [0 1 -2 0 0 0 0];\nvalue           (0 -9.81 0);\n")
    w(out + "/constant/turbulenceProperties", "dictionary", "turbulenceProperties",
      "simulationType  laminar;\n")
    w(out + "/0.orig/alpha.water", "volScalarField", "alpha.water", ALPHA0)
    w(out + "/0.orig/p_rgh", "volScalarField", "p_rgh", P0)
    w(out + "/0.orig/U", "volVectorField", "U", u0(args.slip))

    with open(out + "/CASE_PROVENANCE.txt", "w") as f:
        f.write("generated by make_dambreak.py\n")
        f.write("args: %s\n" % vars(args))
        f.write("mesh: %d x %d = %d cells, dx=a/%d dy=a/%d, domain %ga x %ga\n"
                % (nx, ny, nx * ny, args.res, yres, DOMAIN_L, DOMAIN_H))
    print("%s: %d x %d = %d cells (dx=a/%d, dy=a/%d)"
          % (out, nx, ny, nx * ny, args.res, yres))


if __name__ == "__main__":
    main()
