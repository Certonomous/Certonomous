#!/usr/bin/env python3
"""Build ONE registered T20 case from T20_registered.json.  Writes NO 0/ and NO
time directory -- the launcher arms 0/ from 0.orig/ and touches 0/<region>/T LAST,
so that file dates the run allowed to produce the answer (CLAUDE.md rule 4's age
guard).  A case directory that already exists is REFUSED, never cleaned.

EVERY PHYSICAL AND NUMERICAL VALUE COMES FROM T20_registered.json, which is itself
a transcription of the frozen pre-registration with a section citation beside each
number.  Nothing is typed in here from memory.  If a value is missing from the
JSON this script FAILS rather than defaulting -- a default is an unregistered
choice wearing a plausible face.

usage: build_t20.py --case T20_LC_c [--root <dir>]
"""
import argparse
import json
import os
import subprocess
import sys

SELF = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(SELF, "T20_registered.json")
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

HEAD = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                 |
|   \\\\  /    A nd           | T20 -- lumped-capacitance control (rung T20)    |
|    \\\\/     M anipulation  | BUILT BY build_t20.py FROM T20_registered.json  |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       %s;
    location    "%s";
    object      %s;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

"""

TAIL = "\n// ************************************************************************* //\n"


def need(d, k, where):
    if k not in d:
        sys.exit("REFUSE: %s is missing from %s in T20_registered.json -- a "
                 "default here would be an UNREGISTERED choice" % (k, where))
    return d[k]


def write(path, cls, loc, obj, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(HEAD % (cls, loc, obj))
        f.write(body)
        f.write(TAIL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--root", default=SELF)
    a = ap.parse_args()

    reg = json.load(open(REG))
    if a.case not in reg["cases"]:
        sys.exit("REFUSE: %s is not a registered T20 case in %s" % (a.case, REG))
    c = reg["cases"][a.case]
    ph = reg["physics"]
    nu = reg["numerics"]
    region = reg["region"]

    d = os.path.join(a.root, a.case)
    if os.path.exists(d):
        sys.exit("REFUSE: %s already exists. It is INSPECTED, never cleaned "
                 "(CLAUDE.md rule 10)." % d)

    nx, ny, nz = need(c, "nx", a.case), need(c, "ny", a.case), need(c, "nz", a.case)
    Lx, Ly, Lz = ph["Lx"], ph["Ly"], ph["Lz"]

    # ---------------------------------------------------------------- mesh
    v = [(0, 0, 0), (Lx, 0, 0), (Lx, Ly, 0), (0, Ly, 0),
         (0, 0, Lz), (Lx, 0, Lz), (Lx, Ly, Lz), (0, Ly, Lz)]
    write(os.path.join(d, "system", region, "blockMeshDict"),
          "dictionary", "system/" + region, "blockMeshDict",
          "scale   1;\n\nvertices\n(\n" +
          "".join("    (%.6f %.6f %.6f)\n" % p for p in v) +
          ");\n\nblocks\n(\n    hex (0 1 2 3 4 5 6 7) (%d %d %d) simpleGrading (1 1 1)\n);\n"
          "\nedges ();\n\n"
          "boundary\n(\n"
          # the two 100 mm faces -- the convecting pair, A = 2 x Lx x Lz
          "    channelFaceLo { type wall;  faces ( (0 1 5 4) ); }\n"
          "    channelFaceHi { type wall;  faces ( (3 7 6 2) ); }\n"
          # the two 30 mm faces -- adiabatic casing
          "    endLo         { type wall;  faces ( (0 4 7 3) ); }\n"
          "    endHi         { type wall;  faces ( (1 2 6 5) ); }\n"
          # 2-D planar
          "    front         { type empty; faces ( (4 5 6 7) ); }\n"
          "    back          { type empty; faces ( (0 3 2 1) ); }\n"
          ");\n\nmergePatchPairs ();\n" % (nx, ny, nz))

    # ------------------------------------------------------- regionProperties
    # ZERO FLUID REGIONS.  Upstream's own shipped test asset carries this exact
    # shape: applications/test/multiWorld/chtMultiRegionSimpleFoam/solid/
    # constant/regionProperties -> "regions ( fluid () solid (bottomSolid) );"
    write(os.path.join(d, "constant", "regionProperties"),
          "dictionary", "constant", "regionProperties",
          "regions\n(\n    fluid   ()\n    solid   (%s)\n);\n" % region)

    # ------------------------------------------------ solid thermophysical
    write(os.path.join(d, "constant", region, "thermophysicalProperties"),
          "dictionary", "constant/" + region, "thermophysicalProperties",
          "thermoType\n{\n"
          "    type            heSolidThermo;\n"
          "    mixture         pureMixture;\n"
          "    transport       constIso;\n"
          "    thermo          hConst;\n"
          "    equationOfState rhoConst;\n"
          "    specie          specie;\n"
          "    energy          sensibleEnthalpy;\n}\n\n"
          "mixture\n{\n"
          "    specie          { molWeight   50; }\n"
          "    transport       { kappa       %.10g; }\n"
          "    thermodynamics  { Hf          0; Cp %.10g; }\n"
          "    equationOfState { rho         %.10g; }\n}\n"
          % (ph["kappa"], ph["cp"], ph["rho"]))

    # -------------------------------------------------------------- fvOptions
    # volumeMode specific -> Su is in (equation dimensions)/volume.  The solid
    # energy equation is ddt(betav*rho, h) whose matrix dimensions are W, so
    # SuDims = eqn.dimensions()/dimVolume = W/m^3 (SemiImplicitSource.C).  The
    # registered q''' therefore enters as W/m^3 with no rho factor.
    write(os.path.join(d, "constant", region, "fvOptions"),
          "dictionary", "constant/" + region, "fvOptions",
          "volumetricHeatSource\n{\n"
          "    type            scalarSemiImplicitSource;\n"
          "    selectionMode   all;\n"
          "    volumeMode      specific;\n"
          "    sources\n    {\n"
          "        h\n        {\n"
          "            explicit    constant %.10g;\n"
          "            implicit    none;\n"
          "        }\n    }\n}\n" % ph["q_volumetric"])

    # ------------------------------------------------------------ controlDict
    write(os.path.join(d, "system", "controlDict"),
          "dictionary", "system", "controlDict",
          "application     %s;\n\n"
          "startFrom       startTime;\nstartTime       0;\n\n"
          "stopAt          endTime;\nendTime         %.10g;\n\n"
          "deltaT          %.10g;\n\n"
          "writeControl    %s;\nwriteInterval   %.10g;\n\npurgeWrite      0;\n\n"
          "writeFormat     %s;\nwritePrecision  %d;\nwriteCompression %s;\n\n"
          "timeFormat      %s;\ntimePrecision   %d;\n\n"
          "runTimeModifiable no;\n\n"
          "adjustTimeStep  %s;\n"
          % (reg["solver"], c["endTime"], c["deltaT"], nu["writeControl"],
             nu["writeInterval"], nu["writeFormat"], nu["writePrecision"],
             nu["writeCompression"], nu["timeFormat"], nu["timePrecision"],
             nu["adjustTimeStep"]))

    # ------------------------------------------- top-level fvSchemes/fvSolution
    write(os.path.join(d, "system", "fvSchemes"),
          "dictionary", "system", "fvSchemes",
          "ddtSchemes { default %s; }\ngradSchemes { default %s; }\n"
          "divSchemes { default none; }\nlaplacianSchemes { default none; }\n"
          "interpolationSchemes { default linear; }\nsnGradSchemes { default corrected; }\n"
          % (nu["ddtScheme"], nu["gradScheme"]))
    write(os.path.join(d, "system", "fvSolution"),
          "dictionary", "system", "fvSolution",
          "PIMPLE\n{\n    nOuterCorrectors %d;\n}\n" % nu["nOuterCorrectors"])

    # ------------------------------------------------ region fvSchemes/fvSolution
    write(os.path.join(d, "system", region, "fvSchemes"),
          "dictionary", "system/" + region, "fvSchemes",
          "ddtSchemes { default %s; }\ngradSchemes { default %s; }\n"
          "divSchemes { default none; }\n"
          "laplacianSchemes\n{\n    default             none;\n"
          "    laplacian(alpha,h)  %s;\n}\n"
          "interpolationSchemes { default linear; }\nsnGradSchemes { default corrected; }\n"
          % (nu["ddtScheme"], nu["gradScheme"], nu["laplacianScheme"]))
    write(os.path.join(d, "system", region, "fvSolution"),
          "dictionary", "system/" + region, "fvSolution",
          "solvers\n{\n"
          "    h\n    {\n        solver          %s;\n        preconditioner  %s;\n"
          "        tolerance       %.3g;\n        relTol          %.3g;\n    }\n"
          "    hFinal\n    {\n        $h;\n        tolerance       %.3g;\n        relTol          %.3g;\n    }\n}\n\n"
          "PIMPLE\n{\n    nNonOrthogonalCorrectors %d;\n"
          "    // REGISTERED at S6.2 and WRITTEN HERE VERBATIM, and INERT on this\n"
          "    // build: readSolidMultiRegionPIMPLEControls.H (v2606) reads ONLY\n"
          "    // nNonOrthogonalCorrectors from a solid region's PIMPLE dict, so\n"
          "    // this entry is silently ignored.  The operative control is the\n"
          "    // linear-solver tolerance above, which is registered in the same\n"
          "    // section.  Disclosed in T20_registered.json, not repaired here.\n"
          "    residualControl { h %.3g; }\n}\n"
          % (nu["h_linear_solver"], nu["h_preconditioner"], nu["h_tolerance"],
             nu["h_relTol"], nu["h_tolerance"], nu["h_relTol"],
             nu["nNonOrthogonalCorrectors"], nu["residualControl_h"]))

    # ------------------------------------------------------------- 0.orig
    o = os.path.join(d, "0.orig", region)
    write(os.path.join(o, "T"), "volScalarField", "0/" + region, "T",
          "dimensions      [0 0 0 1 0 0 0];\n\ninternalField   uniform %.10g;\n\n"
          "boundaryField\n{\n"
          "    \"channelFaceLo|channelFaceHi\"\n    {\n"
          "        type            externalWallHeatFluxTemperature;\n"
          "        mode            coefficient;\n"
          "        h               constant %.10g;\n"
          "        Ta              constant %.10g;\n"
          "        emissivity      0;\n"
          "        kappaMethod     solidThermo;\n"
          "        value           uniform %.10g;\n    }\n"
          "    \"endLo|endHi\"\n    {\n        type            zeroGradient;\n    }\n"
          "    \"front|back\"\n    {\n        type            empty;\n    }\n}\n"
          % (ph["T_initial"], ph["h_conv"], ph["T_inf"], ph["T_initial"]))
    # p is REQUIRED by basicThermo (basicThermo.C:300 lookupOrConstruct(mesh,"p")).
    # It is not solved in a solid region and nothing reads its value here.
    write(os.path.join(o, "p"), "volScalarField", "0/" + region, "p",
          "dimensions      [1 -1 -2 0 0 0 0];\n\ninternalField   uniform 1e5;\n\n"
          "boundaryField\n{\n"
          "    \"channelFaceLo|channelFaceHi|endLo|endHi\"\n    {\n        type            zeroGradient;\n    }\n"
          "    \"front|back\"\n    {\n        type            empty;\n    }\n}\n")

    # ------------------------------------------------------------- blockMesh
    env = "set +u; . %s >/dev/null 2>&1; set -u; " % FOAM_BASHRC
    cmd = env + "blockMesh -case %s -region %s -dict %s" % (
        d, region, os.path.join(d, "system", region, "blockMeshDict"))
    with open(os.path.join(d, "log.blockMesh"), "w") as lg:
        rc = subprocess.call(["bash", "-c", cmd], stdout=lg, stderr=subprocess.STDOUT)
    if rc != 0:
        sys.exit("REFUSE: blockMesh returned rc=%d; see %s/log.blockMesh" % (rc, d))
    owner = os.path.join(d, "constant", region, "polyMesh", "owner")
    if not os.path.isfile(owner):
        sys.exit("REFUSE: blockMesh returned 0 but %s does not exist" % owner)

    with open(os.path.join(d, "CASE.txt"), "w") as f:
        f.write("case=%s\nrung=T20\nprereg=%s\nprereg_commit=%s\n"
                "solver=%s\nregion=%s\ncells=%d (%dx%dx%d)\ndeltaT=%.10g\nendTime=%.10g\n"
                "steps=%d\nranks=%d\ntimeout_s=%d\npoint_core_min=%.4f\ncap_core_min=%.2f\n"
                "BUILT BY build_t20.py FROM T20_registered.json; every value carries its\n"
                "frozen-document section in that file.  NO 0/ AND NO TIME DIRECTORY IS\n"
                "WRITTEN HERE: the launcher arms 0/ from 0.orig/ and touches 0/%s/T last.\n"
                % (a.case, reg["prereg_path"], reg["prereg_commit"], reg["solver"],
                   region, c["cells"], nx, ny, nz, c["deltaT"], c["endTime"],
                   c["steps"], reg["ranks"], c["timeout_s"], c["point_core_min"],
                   c["cap_core_min"], region))
    print("built %s  (%d cells, dt %g, endTime %g, %d steps)"
          % (d, c["cells"], c["deltaT"], c["endTime"], c["steps"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
