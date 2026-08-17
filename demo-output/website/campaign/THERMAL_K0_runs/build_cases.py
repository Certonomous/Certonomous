#!/usr/bin/env python3
"""Build the K0a and K0b thermal capability cases and their control twins.

Rung K0 of the cooling ladder, campaign **F14**.

The campaign was dispatched as "F11", which was already taken by the lid-driven
cavity ladder. Ruled 2026-08-17: this campaign is F14, F11 keeps the cavity
ladder. Gate specifications live at `docs/campaigns/F14-cooling-ladder/`.
THERMAL_K0_PREREGISTRATION.md section 0 records the collision as still open --
it is a preregistration and its body is not editable after compute has run, so
the ruling is in a dated addendum at the foot of that file instead. The physics
name THERMAL_K0 never collided and does not change.

    python3 build_cases.py            # writes all four case trees next to this file

Case trees written:
    K0a_heated_box/             feasibility rung, 20x20, hot floor strip
    K0a_heated_box_g0/          control twin, g = 0  -> pure conduction
    K0b_cavity_Ra1e5/           physics rung, 64x64, differentially heated cavity
    K0b_cavity_g0/              control twin, g = 0  -> exact 1-D conduction,
                                used to calibrate scripts/heat_balance.py against
                                a closed-form answer

Initial fields live in `0.orig/` and are copied to `0/` by run_cases.sh. `0.orig/`
travels in git; `0/` and every later time directory do not (see .gitignore).
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Fluid properties -- air at 300 K, 1 atm. See PREREGISTRATION section 2 for the
# self-consistency re-derivation (nu = mu/rho, Pr = mu.cp/k, alpha = k/(rho.cp),
# and the check that nu/Pr == alpha to 6 significant figures).
# ---------------------------------------------------------------------------
RHO = 1.1614          # kg/m^3
CP = 1007.0           # J/(kg.K)
NU = 1.589461e-05     # m^2/s
PR = 0.706814         # -
PRT = 0.85            # - (unused: both rungs are laminar, nut = 0)
TREF = 300.0          # K
BETA = 1.0 / TREF     # 1/K
GRAV = 9.81           # m/s^2

L = 0.10              # m, cavity / box side
TH = 0.01             # m, out-of-plane thickness (one cell, `empty` patches)

# K0a
K0A_DT = 10.0
K0A_T_HOT = TREF + K0A_DT
K0A_T_COLD = TREF

# K0b -- dT solved backwards from Ra = 1.000e5
K0B_DT = 1.093066
K0B_T_HOT = TREF + K0B_DT / 2.0
K0B_T_COLD = TREF - K0B_DT / 2.0


def header(cls, obj, loc=None):
    locline = f'    location    "{loc}";\n' if loc else ""
    return (
        "/*--------------------------------*- C++ -*----------------------------------*\\\n"
        "| =========                 |                                                 |\n"
        "| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |\n"
        "|  \\\\    /   O peration     | Version:  v2606                                 |\n"
        "|   \\\\  /    A nd           | Website:  www.openfoam.com                      |\n"
        "|    \\\\/     M anipulation  |                                                 |\n"
        "\\*---------------------------------------------------------------------------*/\n"
        "FoamFile\n{\n"
        "    version     2.0;\n"
        "    format      ascii;\n"
        f"    class       {cls};\n"
        f"{locline}"
        f"    object      {obj};\n"
        "}\n"
        "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n"
    )


FOOT = "\n// ************************************************************************* //\n"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


# ---------------------------------------------------------------------------
# blockMeshDict
# ---------------------------------------------------------------------------

def blockmesh_k0a():
    """3 blocks in x so the floor can carry a discrete hot strip in [0.03, 0.07].

    Vertex index v(i,j,k) = i + 4*j + 8*k over
        x in (0, 0.03, 0.07, 0.10), y in (0, 0.10), z in (0, 0.01).
    Face vertex orders below were chosen so every boundary face normal points
    OUT of the domain; the heat-balance auditor's sign convention depends on it.
    """
    xs = [0.0, 0.03, 0.07, L]
    ys = [0.0, L]
    zs = [0.0, TH]
    verts = []
    for k in zs:
        for j in ys:
            for i in xs:
                verts.append(f"    ({i:.5f} {j:.5f} {k:.5f})")
    body = header("dictionary", "blockMeshDict", "system")
    body += "scale   1;\n\nvertices\n(\n" + "\n".join(verts) + "\n);\n\n"
    body += (
        "blocks\n(\n"
        "    hex (0 1 5 4 8 9 13 12) (6 20 1) simpleGrading (1 1 1)\n"
        "    hex (1 2 6 5 9 10 14 13) (8 20 1) simpleGrading (1 1 1)\n"
        "    hex (2 3 7 6 10 11 15 14) (6 20 1) simpleGrading (1 1 1)\n"
        ");\n\nedges();\n\n"
    )
    body += (
        "boundary\n(\n"
        "    hotSource\n    {\n        type wall;\n        faces ( (1 2 10 9) );\n    }\n"
        "    floorAdiabatic\n    {\n        type wall;\n        faces ( (0 1 9 8) (2 3 11 10) );\n    }\n"
        "    ceilingCold\n    {\n        type wall;\n        faces ( (4 12 13 5) (5 13 14 6) (6 14 15 7) );\n    }\n"
        "    sideWalls\n    {\n        type wall;\n        faces ( (0 8 12 4) (3 7 15 11) );\n    }\n"
        "    frontAndBack\n    {\n        type empty;\n"
        "        faces ( (0 4 5 1) (1 5 6 2) (2 6 7 3) (8 9 13 12) (9 10 14 13) (10 11 15 14) );\n    }\n"
        ");\n"
    )
    return body + FOOT


def blockmesh_k0b(n=64):
    body = header("dictionary", "blockMeshDict", "system")
    body += "scale   1;\n\nvertices\n(\n"
    for k in (0.0, TH):
        for j in (0.0, L):
            for i in (0.0, L):
                body += f"    ({i:.5f} {j:.5f} {k:.5f})\n"
    body += ");\n\n"
    body += f"blocks\n(\n    hex (0 1 3 2 4 5 7 6) ({n} {n} 1) simpleGrading (1 1 1)\n);\n\nedges();\n\n"
    body += (
        "boundary\n(\n"
        "    hotWall\n    {\n        type wall;\n        faces ( (0 4 6 2) );\n    }\n"
        "    coldWall\n    {\n        type wall;\n        faces ( (1 3 7 5) );\n    }\n"
        "    adiabaticWalls\n    {\n        type wall;\n        faces ( (0 1 5 4) (2 6 7 3) );\n    }\n"
        "    frontAndBack\n    {\n        type empty;\n        faces ( (0 2 3 1) (4 5 7 6) );\n    }\n"
        ");\n"
    )
    return body + FOOT


# ---------------------------------------------------------------------------
# constant/
# ---------------------------------------------------------------------------

def transport_properties():
    b = header("dictionary", "transportProperties", "constant")
    b += "transportModel  Newtonian;\n\n"
    b += f"nu              {NU:.6e};\n"
    b += f"beta            {BETA:.6e};\n"
    b += f"TRef            {TREF};\n"
    b += f"Pr              {PR:.6f};\n"
    b += f"Prt             {PRT};\n"
    return b + FOOT


def thermal_audit_properties():
    """Read by scripts/heat_balance.py only. OpenFOAM never opens this file.

    rho and cp do not appear in a Boussinesq transportProperties (the solver
    never needs them: it solves a kinematic temperature equation). They are
    required to turn a kinematic heat flux into WATTS, so they are declared
    here, next to the case, rather than passed on a command line where they
    would not travel with the case.
    """
    b = header("dictionary", "thermalAuditProperties", "constant")
    b += f"rho0            {RHO};\n"
    b += f"cp0             {CP};\n"
    return b + FOOT


def gravity(on=True):
    b = header("uniformDimensionedVectorField", "g", "constant")
    b += "dimensions      [0 1 -2 0 0 0 0];\n"
    b += f"value           (0 {-GRAV if on else 0.0} 0);\n"
    return b + FOOT


def turbulence_properties():
    b = header("dictionary", "turbulenceProperties", "constant")
    b += "simulationType  laminar;\n"
    return b + FOOT


# ---------------------------------------------------------------------------
# 0.orig/
# ---------------------------------------------------------------------------

def field_T(patches, internal):
    b = header("volScalarField", "T", "0")
    b += "dimensions      [0 0 0 1 0 0 0];\n\n"
    b += f"internalField   uniform {internal};\n\nboundaryField\n{{\n"
    for name, spec in patches:
        b += f"    {name}\n    {{\n{spec}    }}\n"
    b += "}\n"
    return b + FOOT


def field_U(wall_patches):
    b = header("volVectorField", "U", "0")
    b += "dimensions      [0 1 -1 0 0 0 0];\n\ninternalField   uniform (0 0 0);\n\nboundaryField\n{\n"
    for name in wall_patches:
        b += f"    {name}\n    {{\n        type            noSlip;\n    }}\n"
    b += "    frontAndBack\n    {\n        type            empty;\n    }\n}\n"
    return b + FOOT


def field_p_rgh(wall_patches):
    b = header("volScalarField", "p_rgh", "0")
    b += "dimensions      [0 2 -2 0 0 0 0];\n\ninternalField   uniform 0;\n\nboundaryField\n{\n"
    for name in wall_patches:
        b += f"    {name}\n    {{\n        type            fixedFluxPressure;\n        value           uniform 0;\n    }}\n"
    b += "    frontAndBack\n    {\n        type            empty;\n    }\n}\n"
    return b + FOOT


def field_alphat(wall_patches):
    b = header("volScalarField", "alphat", "0")
    b += "dimensions      [0 2 -1 0 0 0 0];\n\ninternalField   uniform 0;\n\nboundaryField\n{\n"
    for name in wall_patches:
        b += f"    {name}\n    {{\n        type            calculated;\n        value           uniform 0;\n    }}\n"
    b += "    frontAndBack\n    {\n        type            empty;\n    }\n}\n"
    return b + FOOT


# ---------------------------------------------------------------------------
# system/
# ---------------------------------------------------------------------------

def control_dict(end_time, write_interval):
    b = header("dictionary", "controlDict", "system")
    b += (
        "application     buoyantBoussinesqSimpleFoam;\n"
        "startFrom       startTime;\n"
        "startTime       0;\n"
        "stopAt          endTime;\n"
        f"endTime         {end_time};\n"
        "deltaT          1;\n"
        "writeControl    timeStep;\n"
        f"writeInterval   {write_interval};\n"
        "purgeWrite      0;\n"
        "writeFormat     ascii;\n"
        "writePrecision  10;\n"
        "writeCompression off;\n"
        "timeFormat      general;\n"
        "timePrecision   6;\n"
        "runTimeModifiable false;\n"
    )
    return b + FOOT


def fv_schemes(accurate):
    b = header("dictionary", "fvSchemes", "system")
    b += "ddtSchemes\n{\n    default         steadyState;\n}\n\n"
    b += "gradSchemes\n{\n    default         Gauss linear;\n}\n\n"
    b += "divSchemes\n{\n    default         none;\n"
    if accurate:
        b += "    div(phi,U)      bounded Gauss linearUpwind grad(U);\n"
        b += "    div(phi,T)      bounded Gauss limitedLinear 1;\n"
    else:
        b += "    div(phi,U)      bounded Gauss upwind;\n"
        b += "    div(phi,T)      bounded Gauss upwind;\n"
    b += "    div((nuEff*dev2(T(grad(U))))) Gauss linear;\n}\n\n"
    b += "laplacianSchemes\n{\n    default         Gauss linear corrected;\n}\n\n"
    b += "interpolationSchemes\n{\n    default         linear;\n}\n\n"
    b += "snGradSchemes\n{\n    default         corrected;\n}\n"
    return b + FOOT


def fv_solution():
    b = header("dictionary", "fvSolution", "system")
    b += (
        "solvers\n{\n"
        "    p_rgh\n    {\n        solver          PCG;\n        preconditioner  DIC;\n"
        "        tolerance       1e-10;\n        relTol          0.01;\n    }\n\n"
        '    "(U|T)"\n    {\n        solver          PBiCGStab;\n        preconditioner  DILU;\n'
        "        tolerance       1e-12;\n        relTol          0.01;\n    }\n}\n\n"
        "SIMPLE\n{\n    nNonOrthogonalCorrectors 0;\n    pRefCell        0;\n    pRefValue       0;\n\n"
        "    residualControl\n    {\n        p_rgh           1e-07;\n        U               1e-08;\n"
        "        T               1e-08;\n    }\n}\n\n"
        "relaxationFactors\n{\n    fields\n    {\n        p_rgh           0.7;\n    }\n"
        "    equations\n    {\n        U               0.3;\n        T               0.5;\n    }\n}\n"
    )
    return b + FOOT


# ---------------------------------------------------------------------------
# case assembly
# ---------------------------------------------------------------------------

def build_k0a(path, g_on):
    walls = ["hotSource", "floorAdiabatic", "ceilingCold", "sideWalls"]
    fixed = lambda v: f"        type            fixedValue;\n        value           uniform {v};\n"
    zg = "        type            zeroGradient;\n"
    tpatches = [
        ("hotSource", fixed(K0A_T_HOT)),
        ("floorAdiabatic", zg),
        ("ceilingCold", fixed(K0A_T_COLD)),
        ("sideWalls", zg),
        ("frontAndBack", "        type            empty;\n"),
    ]
    write(f"{path}/system/blockMeshDict", blockmesh_k0a())
    write(f"{path}/system/controlDict", control_dict(2000, 100))
    write(f"{path}/system/fvSchemes", fv_schemes(accurate=False))
    write(f"{path}/system/fvSolution", fv_solution())
    write(f"{path}/constant/transportProperties", transport_properties())
    write(f"{path}/constant/thermalAuditProperties", thermal_audit_properties())
    write(f"{path}/constant/g", gravity(g_on))
    write(f"{path}/constant/turbulenceProperties", turbulence_properties())
    write(f"{path}/0.orig/T", field_T(tpatches, K0A_T_COLD))
    write(f"{path}/0.orig/U", field_U(walls))
    write(f"{path}/0.orig/p_rgh", field_p_rgh(walls))
    write(f"{path}/0.orig/alphat", field_alphat(walls))


def build_k0b(path, g_on):
    walls = ["hotWall", "coldWall", "adiabaticWalls"]
    fixed = lambda v: f"        type            fixedValue;\n        value           uniform {v};\n"
    tpatches = [
        ("hotWall", fixed(f"{K0B_T_HOT:.6f}")),
        ("coldWall", fixed(f"{K0B_T_COLD:.6f}")),
        ("adiabaticWalls", "        type            zeroGradient;\n"),
        ("frontAndBack", "        type            empty;\n"),
    ]
    write(f"{path}/system/blockMeshDict", blockmesh_k0b(64))
    # writeInterval 10 so that C3 (auditor sensitivity on an unconverged field)
    # has a genuinely early snapshot to read.
    write(f"{path}/system/controlDict", control_dict(4000, 10))
    write(f"{path}/system/fvSchemes", fv_schemes(accurate=True))
    write(f"{path}/system/fvSolution", fv_solution())
    write(f"{path}/constant/transportProperties", transport_properties())
    write(f"{path}/constant/thermalAuditProperties", thermal_audit_properties())
    write(f"{path}/constant/g", gravity(g_on))
    write(f"{path}/constant/turbulenceProperties", turbulence_properties())
    write(f"{path}/0.orig/T", field_T(tpatches, TREF))
    write(f"{path}/0.orig/U", field_U(walls))
    write(f"{path}/0.orig/p_rgh", field_p_rgh(walls))
    write(f"{path}/0.orig/alphat", field_alphat(walls))


# ---------------------------------------------------------------------------
# Control C3b -- a PLANTED volumetric heat source of exactly known power.
#
# The boundary heat balance of a CLOSED, impermeable, steady case is very nearly
# an identity (see THERMAL_K0_RESULTS.md, C3): the discrete T equation conserves
# by construction whether or not the field has converged, so "imbalance ~ 0" on
# such a case does not demonstrate that the auditor can detect anything.
#
# This twin plants a source the auditor deliberately does not know about. At
# steady state the boundary fluxes must then sum to exactly -P, so the auditor
# is required to report a large, exactly predicted imbalance. It is the positive
# control for the auditor's failure-detection path, and it is also the physics
# every rack-row case will have: a box with power going into it.
#
# The T equation here is kinematic (K.m^3/s), so a power P in watts enters as
# Su = P / (rho.cp).
# ---------------------------------------------------------------------------
PLANT_POWER_W = 5.0e-3


def fv_options_heat_source(power_w):
    su = power_w / (RHO * CP)
    b = header("dictionary", "fvOptions", "constant")
    b += (
        "// PLANTED POSITIVE CONTROL for scripts/heat_balance.py.\n"
        f"// Total power P = {power_w:.6e} W, entered into the kinematic T equation as\n"
        f"//   Su = P/(rho.cp) = {power_w:.6e}/({RHO}*{CP}) = {su:.9e} K.m^3/s\n"
        "// volumeMode absolute => the value is the TOTAL over the selected cells.\n\n"
        "plantedHeatSource\n{\n"
        "    type            scalarSemiImplicitSource;\n"
        "    active          yes;\n"
        "    selectionMode   all;\n"
        "    volumeMode      absolute;\n"
        "    sources\n    {\n"
        f"        T           ({su:.9e} 0);\n"
        "    }\n}\n"
    )
    return b + FOOT


def build_k0a_source(path, g_on):
    build_k0a(path, g_on)
    write(f"{path}/constant/fvOptions", fv_options_heat_source(PLANT_POWER_W))


def main():
    for name, fn, g_on in (
        ("K0a_heated_box", build_k0a, True),
        ("K0a_heated_box_g0", build_k0a, False),
        ("K0a_heated_box_source", build_k0a_source, True),
        ("K0b_cavity_Ra1e5", build_k0b, True),
        ("K0b_cavity_g0", build_k0b, False),
    ):
        path = os.path.join(HERE, name)
        for sub in ("system", "constant", "0.orig"):
            shutil.rmtree(os.path.join(path, sub), ignore_errors=True)
        fn(path, g_on)
        print(f"built {name}  (g {'on' if g_on else 'OFF'})")


if __name__ == "__main__":
    main()
