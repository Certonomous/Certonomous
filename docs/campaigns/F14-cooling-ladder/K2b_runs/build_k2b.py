#!/usr/bin/env python3
"""build_k2b.py -- the K2b-pilot 2D rack-row slice, F14 cooling ladder.

    python3 build_k2b.py                 # writes every case beside this file
    python3 build_k2b.py K2bP_coarse     # or only the named ones

WHAT THIS BUILDS
----------------
`K2a_RACK_ROW_MODULE_SPEC.md` section 6 specifies the pilot in one sentence:

    A 2D vertical-slice pilot (x = const through one rack: cold aisle, rack,
    hot aisle) is specified alongside as K2b-pilot: same BCs collapsed to the
    slice, 42 k / 95 k cell pair. It exists to shake down the BC coupling, the
    monitor wiring and the heat-balance path at ~1/15 the cost before the 3D
    module burns anything, and it is a capability case in the K0a/K0b sense --
    never a result.

Everything else below is the spec's own section 2 (geometry), section 3 (the BC
table, every surface), section 4 (Boussinesq admissibility), section 7 (what is
measured) and section 9 (numerics), collapsed onto a slice of thickness W_r --
one rack pitch -- so that the per-slice flows ARE the per-rack flows and no
scaling factor is introduced anywhere.

The slice is a y-z plane. y runs cold aisle -> rack -> hot aisle, z is vertical,
x is the row direction and carries exactly one cell with `empty` end patches.

  z=2.70  +---------------------------------------------+ ceiling / RETURN
          |                     .....RETURN.....        |
  z=2.00  +--------------+#####+----------------------- +
          |  cold aisle  #RACK#      hot aisle          |
          |              #####|                         |
          |  rack_in --> #####| --> rack_out            |
  z=0.00  +-----[TILE]---+####+-------------------------+ floor
          y=0          0.6  1.2   2.3   2.6  3.2      3.5

The rack interior (1.2 <= y <= 2.3, 0 <= z <= 2.0) is NOT meshed: it is a void
whose front face is `rack_in`, whose rear face is `rack_out` and whose top is a
`rack_top` wall.  That IS the modelling abstraction of spec section 1 -- a rack
is an inlet face plus an outlet face -- and nothing about a server exists in
this case.

THE ONE PLACE THIS BUILD DEPARTS FROM THE SPEC'S OWN TEXT, AND IT IS THE SPEC
THAT IS WRONG
-----------------------------------------------------------------------------
Spec section 3.3 says of `outletMappedUniformInlet`:

    The face-averaging in the BC is area-weighted (`gWeightedAverage` over
    `magSf` in the source); the *graded* rack-inlet temperature in Section 7 is
    computed by function object as the mass-flow-weighted average of the same
    face, and on a patch with uniform imposed normal flow the two coincide up
    to the nonuniformity of the solved face flux -- the analyser must print
    both once and show their difference is below the gate resolution.

Read in the v2606 source this session
(`.../derived/outletMappedUniformInlet/outletMappedUniformInletFvPatchField.txx`,
`updateCoeffs()`, lines 319-353) the BC has TWO branches and the area-weighted
one is the FALLBACK:

    const scalar sumOutletPhi = gSum(outletPhi);
    if (sumOutletPhi > SMALL)
        mapField.append(gSum(outletPhi*outletFld)/sumOutletPhi*fraction + offset);
    else
        mapField.append(gWeightedAverage(outlet.magSf(), outletFld));

So in normal operation the BC is MASS-FLUX-WEIGHTED, identical in kind to the
graded quantity of section 7, and the units-of-averaging dispute the spec set
out to close does not arise.  The spec's mandated "print both once" check is
still done, because it is now a check of something else and something worse:

**the fallback branch silently drops the offset.**  If the rack front face ever
stops carrying net outflow -- reversed flow, a mis-signed flowRate, a first
iteration before phi exists -- the rack rear inlet is handed the plain average
of the front face with NO +dT, and a rack that adds no heat looks exactly like a
converged rack.  `T_rack_out_area - T_rack_in_area == dT` read from the SOLVER'S
OWN LOG is therefore the reachability control for this boundary condition, and
it can fail: it reads 0.000 K on the fallback branch.

PROPERTIES: THE LAB'S OWN PAIR, NOT THE SPEC'S RECALLED PAIR
------------------------------------------------------------
Spec section 2.1 derives P_i for reporting at RECALLED rho = 1.177 kg/m3,
cp = 1006 J/kg/K.  `scripts/heat_balance.py` reads rho and cp from the case's
`constant/thermalAuditProperties`, and every case on this ladder that the
auditor has ever been calibrated against (K0c C3, KV1a/b/c) carries
rho0 = 1.1614, cp0 = 1007.0 -- rho.cp = 1169.5298 J/m3/K.  This build uses the
LAB'S pair, so that the audited watts and the reported watts are the same watts,
and reports the 1.24 % gap against the spec's recalled pair rather than hiding
it.  The Boussinesq solve never sees either: the primitive parameter is dT_rack,
exactly as spec section 2.1 requires.

WHAT THE CASES ARE
------------------
  K2bP_coarse   the pilot, spec defaults, dT_rack = 12.0 K.   46,400 cells.
  K2bP_fine     same case at 1.5x per direction.             104,400 cells.
  K2bP_C1_g0    control C1: gravity off.  Restart twin of the coarse case.
  K2bP_C2_dT13  control C2: the dT plant moved +10 % to 13.2 K.  Restart twin.
  K2bP_C3_plant control C3: a planted volumetric source of known watts in the
                room, the KV1a recovery test on THIS geometry, sized to THIS
                ledger.  Runs with its negative twin K2bP_C3b_noplant.  Restart twin.

The three controls are built as RESTART twins: they are byte-identical to the
coarse case except for the one dictionary each perturbs, and they start from the
coarse case's converged field rather than from scratch, which is what makes them
affordable inside the authorised 60 core-minutes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# THE ONE TABLE EVERY NUMBER BELOW COMES FROM.
# Fluid: K0c_runs/Ra1e5_m128/constant/transportProperties at HEAD (spec 2.1).
# Geometry and flows: spec section 2.1 defaults, unchanged.
# ---------------------------------------------------------------------------
NU = 1.589461e-05          # m2/s      K0c dictionary
BETA = 3.333333333e-03     # 1/K       K0c dictionary
TREF = 300.0               # K         K0c dictionary; also the audit datum
PR = 0.71
PRT = 0.85
RHO0 = 1.1614              # kg/m3     thermalAuditProperties, KV1/K0c lineage
CP0 = 1007.0               # J/kg/K    thermalAuditProperties, KV1/K0c lineage
G = 9.81

W_R = 0.60                 # rack width  = the slice thickness (one rack pitch)
D_R = 1.10                 # rack depth
H_R = 2.00                 # rack height
W_CA = 1.20                # cold aisle width
W_HA = 1.20                # hot aisle width
H_ROOM = 2.70              # ceiling height
S_T = 0.60                 # tile pitch

QV_RACK = 0.35             # m3/s per rack  (spec default)
QV_TILE = 0.35             # m3/s per tile  (balance default, n_t = N)
DT_RACK = 12.0             # K              (spec default, 5-20 K band)
T_SUP = 289.0              # K              (spec default)
I_SUP = 0.10               # supply turbulence intensity, midpoint of the 5-20 % sweep
I_RACK = 0.10              # rack exhaust turbulence intensity, spec default
L_SUP = 0.1 * S_T          # mixing length at the tile, spec 3.2
L_RACK = 0.1 * H_R         # mixing length at the rack exhaust, spec 3.3

# Control C3: a planted volumetric source, KV1a's test on THIS geometry.
# `scalarSemiImplicitSource` on T is KINEMATIC: `volumeMode absolute` takes the
# total over the cell set in K.m3/s, so watts = rho.cp.S -- the same arithmetic
# as KV1a and K0c's C3.
#
# THE SIZE IS NOT KV1a's, AND THE REASON IS THE WHOLE POINT OF THE CONTROL.
# KV1a planted 5.000e-03 W into a duct whose ledger carried 0.146 W, so the
# plant was 3.4 % of the ledger and its recovery was a real measurement.  This
# room's ledger carries 4.9e3 W.  The same 5 mW here is 1.0e-06 of the ledger --
# nine orders below the 0.5 % closure band and utterly invisible.  It would have
# been recovered "successfully" by an instrument that returned zero, which is
# KV1b's degenerate-control defect in a new costume: a control that passes while
# proving nothing because nothing it does can move the number it reads.
# The plant is therefore sized to this ledger at 500.000 W, ~10 % of the rack
# load, so that a 0.1 % recovery error is 0.5 W and the control can fail.
Q_PLANT_W = 500.000
RHO_CP = RHO0 * CP0
S_PLANT = Q_PLANT_W / RHO_CP

# y and z interval edges.  Every patch boundary in the slice is one of these.
YS = [0.0, 0.6, W_CA, W_CA + D_R, 2.6, 3.2, W_CA + D_R + W_HA]
ZS = [0.0, H_R, H_ROOM]
RACK_I = 2                 # y-interval index of the rack void (lower level only)
TILE_I = 1                 # y-interval index of the supply tile in the floor
RETURN_I = 4               # y-interval index of the ceiling return

A_TILE = S_T * W_R                      # 0.36 m2
A_RACK_FACE = H_R * W_R                 # 1.20 m2
A_RETURN = (YS[5] - YS[4]) * W_R        # 0.36 m2
U_TILE = QV_TILE / A_TILE
U_RACK = QV_RACK / A_RACK_FACE
P_RACK_LAB = RHO_CP * QV_RACK * DT_RACK           # W, lab property pair
P_RACK_SPEC = 1.177 * 1006.0 * QV_RACK * DT_RACK  # W, spec's recalled pair

K_SUP = 1.5 * (I_SUP * U_TILE) ** 2
OM_SUP = K_SUP ** 0.5 / (0.09 ** 0.25 * L_SUP)
K_RACK = 1.5 * (I_RACK * U_RACK) ** 2
OM_RACK = K_RACK ** 0.5 / (0.09 ** 0.25 * L_RACK)

MONITOR_INTERVAL = 50      # physics_rules.yaml thermal.monitor_sample_interval_iterations

HDR = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "{loc}";
    object      {obj};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

"""
FOOT = "\n// ************************************************************************* //\n"

# every patch of the slice, in the order the dictionaries list them
WALLS = ["floor", "ceiling", "wall_cold", "wall_hot", "rack_top"]
OPEN = ["tile", "return", "rack_in", "rack_out"]


def w(case, rel, cls, obj, body):
    path = os.path.join(case, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(HDR.format(cls=cls, loc=os.path.dirname(rel), obj=obj) + body + FOOT)


# ---------------------------------------------------------------------------
# mesh
# ---------------------------------------------------------------------------
def block_mesh_dict(h):
    """Multi-block rectilinear slice at uniform cell size h.  No snappyHexMesh:
    the geometry is axis-aligned throughout (spec section 6)."""
    ny = [int(round((YS[i + 1] - YS[i]) / h)) for i in range(len(YS) - 1)]
    nz = [int(round((ZS[j + 1] - ZS[j]) / h)) for j in range(len(ZS) - 1)]
    for n, lab in [(ny, "y"), (nz, "z")]:
        if any(v <= 0 for v in n):
            raise SystemExit(f"cell size {h} does not divide the {lab} intervals")

    NY, NZ = len(YS), len(ZS)
    xs = [0.0, W_R]

    def vid(i, j, k):
        return k * (NY * NZ) + j * NY + i

    verts = []
    for k, x in enumerate(xs):
        for j, z in enumerate(ZS):
            for i, y in enumerate(YS):
                verts.append(f"    ({x:.6f} {y:.6f} {z:.6f})   // {vid(i,j,k)}")

    active = [(i, j) for j in range(NZ - 1) for i in range(NY - 1)
              if not (j == 0 and i == RACK_I)]

    def corners(i, j):
        return dict(
            v0=vid(i, j, 0), v1=vid(i, j, 1), v2=vid(i + 1, j, 1), v3=vid(i + 1, j, 0),
            v4=vid(i, j + 1, 0), v5=vid(i, j + 1, 1), v6=vid(i + 1, j + 1, 1),
            v7=vid(i + 1, j + 1, 0))

    blocks = []
    for i, j in active:
        c = corners(i, j)
        blocks.append(
            "    hex ({v0} {v1} {v2} {v3} {v4} {v5} {v6} {v7}) "
            "(1 {n_y} {n_z}) simpleGrading (1 1 1)".format(n_y=ny[i], n_z=nz[j], **c))

    # face builders, each ordered so the right-hand normal points OUT of the
    # domain.  Verified by hand against the vertex numbering above.
    def f_bot(i, j):
        c = corners(i, j); return f"({c['v0']} {c['v3']} {c['v2']} {c['v1']})"

    def f_top(i, j):
        c = corners(i, j); return f"({c['v4']} {c['v5']} {c['v6']} {c['v7']})"

    def f_ylo(i, j):
        c = corners(i, j); return f"({c['v0']} {c['v1']} {c['v5']} {c['v4']})"

    def f_yhi(i, j):
        c = corners(i, j); return f"({c['v3']} {c['v7']} {c['v6']} {c['v2']})"

    def f_xlo(i, j):
        c = corners(i, j); return f"({c['v0']} {c['v4']} {c['v7']} {c['v3']})"

    def f_xhi(i, j):
        c = corners(i, j); return f"({c['v1']} {c['v2']} {c['v6']} {c['v5']})"

    pf = {p: [] for p in WALLS + OPEN + ["frontAndBack"]}
    # floor level, z = 0: tile under the cold aisle, floor elsewhere; nothing
    # under the rack, whose footprint is not fluid.
    for i in range(NY - 1):
        if i == RACK_I:
            continue
        pf["tile" if i == TILE_I else "floor"].append(f_bot(i, 0))
    # ceiling level, z = H: the return over the hot aisle, ceiling elsewhere
    for i in range(NY - 1):
        pf["return" if i == RETURN_I else "ceiling"].append(f_top(i, 1))
    # the rack top is a wall, and it is the floor of the block that sits on it
    pf["rack_top"].append(f_bot(RACK_I, 1))
    # the two rack faces, the whole point of the module
    pf["rack_in"].append(f_yhi(RACK_I - 1, 0))
    pf["rack_out"].append(f_ylo(RACK_I + 1, 0))
    # end walls of the aisles
    for j in range(NZ - 1):
        pf["wall_cold"].append(f_ylo(0, j))
        pf["wall_hot"].append(f_yhi(NY - 2, j))
    # the two-dimensionalising pair
    for i, j in active:
        pf["frontAndBack"].append(f_xlo(i, j))
        pf["frontAndBack"].append(f_xhi(i, j))

    def blk(name, ptype, faces):
        fl = "\n            ".join(faces)
        return (f"    {name}\n    {{\n        type {ptype};\n"
                f"        faces\n        (\n            {fl}\n        );\n    }}")

    bnd = [blk(p, "wall", pf[p]) for p in WALLS]
    bnd += [blk(p, "patch", pf[p]) for p in OPEN]
    bnd += [blk("frontAndBack", "empty", pf["frontAndBack"])]

    ncells = sum(ny[i] * nz[j] for i, j in active)
    return "\n".join([
        f"// cells: {ncells}   cell size {h} m   blocks {len(active)}",
        "scale   1;", "", "vertices", "(", "\n".join(verts), ");", "",
        "blocks", "(", "\n".join(blocks), ");", "", "edges();", "",
        "boundary", "(", "\n".join(bnd), ");", ""]), ncells


# ---------------------------------------------------------------------------
# function objects -- spec section 7, at the monitor cadence of section 8
# ---------------------------------------------------------------------------
def _sfv(name, patch, operation, fields, weight=None):
    wf = f"        weightField     {weight};\n" if weight else ""
    return f"""    {name}
    {{
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            {patch};
        operation       {operation};
        fields          ({fields});
{wf}        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval {MONITOR_INTERVAL};
        writeControl    timeStep;
        writeInterval   {MONITOR_INTERVAL};
    }}"""


def functions_block(sample=True):
    fos = []
    # --- the graded quantity, spec section 7 row 1: MASS-FLOW-WEIGHTED T over
    # the rack front face.  This is the S13 monitored quantity for the module
    # (with N = 1 in the slice, T_in,max == T_in,1).
    fos.append(_sfv("T_rack_in_mdot", "rack_in", "weightedAverage", "T", "phi"))
    # --- the area-weighted twin of the same face.  Spec section 3.3 mandates
    # printing both; see the module docstring for what the comparison now means.
    fos.append(_sfv("T_rack_in_area", "rack_in", "areaAverage", "T"))
    # --- the rack exhaust face, both weightings.  The DIFFERENCE of the area
    # rows is the offset readback: it must equal dT_rack, and it reads 0 on the
    # BC's fallback branch.
    fos.append(_sfv("T_rack_out_area", "rack_out", "areaAverage", "T"))
    fos.append(_sfv("T_rack_out_mdot", "rack_out", "weightedAverage", "T", "phi"))
    fos.append(_sfv("T_tile_area", "tile", "areaAverage", "T"))
    fos.append(_sfv("T_return_mdot", "return", "weightedAverage", "T", "phi"))
    # --- mass ledger: sum(phi) on every open patch.  The enthalpy ledger rests
    # on this (physics_rules thermal, heat_balance_open_case_gates_mass_imbalance).
    for p in OPEN:
        fos.append(_sfv(f"phi_{p}", p, "sum", "phi"))
    # --- spec section 4's admissibility instrument, wired into every run.
    fos.append(f"""    Tspan
    {{
        type            fieldMinMax;
        libs            (fieldFunctionObjects);
        fields          (T U);
        location        true;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval {MONITOR_INTERVAL};
        writeControl    timeStep;
        writeInterval   {MONITOR_INTERVAL};
    }}""")
    # --- spec section 6: y+ is MEASURED and reported per case, never assumed.
    fos.append("""    yplus
    {
        type            yPlus;
        libs            (fieldFunctionObjects);
        writeControl    writeTime;
        executeControl  writeTime;
        log             true;
    }""")
    if sample:
        # --- spec section 7, last row: vertical profiles up both aisle midplanes.
        fos.append(f"""    aisleProfiles
    {{
        type            sets;
        libs            (sampling);
        writeControl    writeTime;
        executeControl  writeTime;
        interpolationScheme cellPoint;
        setFormat       raw;
        fields          (T U);
        sets
        (
            coldAisleMid
            {{
                type    uniform;
                axis    z;
                start   ({W_R/2:.4f} {W_CA/2:.4f} 0.02);
                end     ({W_R/2:.4f} {W_CA/2:.4f} {H_ROOM-0.02:.4f});
                nPoints 68;
            }}
            hotAisleMid
            {{
                type    uniform;
                axis    z;
                start   ({W_R/2:.4f} {(YS[3]+YS[6])/2:.4f} 0.02);
                end     ({W_R/2:.4f} {(YS[3]+YS[6])/2:.4f} {H_ROOM-0.02:.4f});
                nPoints 68;
            }}
        );
    }}""")
    return "\n".join(fos)


def control_dict(end_time, write_interval, start_from="startTime", start_time=0):
    return f"""application     buoyantBoussinesqSimpleFoam;
startFrom       {start_from};
startTime       {start_time};
stopAt          endTime;
endTime         {end_time};
deltaT          1;
writeControl    timeStep;
writeInterval   {write_interval};
purgeWrite      0;
writeFormat     ascii;
writePrecision  10;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;

functions
{{
{functions_block()}
}}
"""


FV_SCHEMES = """ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
}

// K0c's committed divSchemes, extended with the turbulence entries the SST
// model needs (spec section 9).  div(phi,U) and div(phi,T) are second-order
// limited rather than K0c's plain `bounded Gauss linear`: this module has
// opposing jets and a 12 K step across the rack face, and an unlimited central
// scheme on that produces undershoots that the Boussinesq span check would
// then report as a physics breach.
divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss limitedLinearV 1;
    div(phi,T)      bounded Gauss limitedLinear 1;
    div(phi,k)      bounded Gauss limitedLinear 1;
    div(phi,omega)  bounded Gauss limitedLinear 1;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

wallDist
{
    method          meshWave;
}
"""

# residualControl is deliberately far below anything this case will reach, so it
# can never stop the run before S13 is satisfied.  That is K0c's L-89 written
# into the dictionary rather than re-learned (spec section 9).
FV_SOLUTION = """solvers
{
    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-09;
        relTol          0.01;
    }

    "(U|T|k|omega)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-11;
        relTol          0.01;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;

    residualControl
    {
        p_rgh           1e-09;
        U               1e-10;
        T               1e-10;
    }
}

relaxationFactors
{
    fields
    {
        p_rgh           0.3;
    }
    equations
    {
        U               0.5;
        T               0.5;
        "(k|omega)"     0.5;
    }
}
"""


# ---------------------------------------------------------------------------
# fields -- spec section 3, every surface
# ---------------------------------------------------------------------------
def _walls(entry):
    return "\n".join(f"    {p}\n    {{\n{entry}\n    }}" for p in WALLS)


def field_U(qv_tile=QV_TILE):
    return f"""dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{{
{_walls("        type            noSlip;")}
    tile
    {{
        type            flowRateInletVelocity;
        volumetricFlowRate constant {qv_tile};
        value           uniform (0 0 0);
    }}
    return
    {{
        type            pressureInletOutletVelocity;
        value           uniform (0 0 0);
    }}
    rack_in
    {{
        type            flowRateOutletVelocity;
        volumetricFlowRate constant {QV_RACK};
        value           uniform (0 0 0);
    }}
    rack_out
    {{
        type            flowRateInletVelocity;
        volumetricFlowRate constant {QV_RACK};
        value           uniform (0 0 0);
    }}
    frontAndBack
    {{
        type            empty;
    }}
}}
"""


def field_p_rgh():
    ffp = "        type            fixedFluxPressure;\n        value           uniform 0;"
    return f"""dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
{_walls(ffp)}
    tile
    {{
{ffp}
    }}
    rack_in
    {{
{ffp}
    }}
    rack_out
    {{
{ffp}
    }}
    return
    {{
        type            fixedValue;
        value           uniform 0;
    }}
    frontAndBack
    {{
        type            empty;
    }}
}}
"""


def field_T(dt_rack):
    return f"""dimensions      [0 0 0 1 0 0 0];

internalField   uniform {T_SUP};

boundaryField
{{
{_walls("        type            zeroGradient;")}
    tile
    {{
        type            fixedValue;
        value           uniform {T_SUP};
    }}
    return
    {{
        type            inletOutlet;
        inletValue      uniform {T_SUP};
        value           uniform {T_SUP};
    }}
    rack_in
    {{
        type            zeroGradient;
    }}
    rack_out
    {{
        // THE LOAD-BEARING ROW.  dT = P/(mdot.cp) with dT specified directly,
        // mdot pinned by the paired flowRateOutletVelocity on rack_in.  No cp
        // ever enters the Boussinesq case.  Offset dropped silently if rack_in
        // ever loses net outflow -- see build_k2b.py's docstring.
        type            outletMappedUniformInlet;
        outlets
        {{
            rack_in
            {{
                fraction    constant 1;
                offset      constant {dt_rack};
            }}
        }}
        value           uniform {T_SUP + dt_rack};
    }}
    frontAndBack
    {{
        type            empty;
    }}
}}
"""


def field_k(qv_tile=QV_TILE):
    k_sup = 1.5 * (I_SUP * qv_tile / A_TILE) ** 2
    return f"""dimensions      [0 2 -2 0 0 0 0];

internalField   uniform {k_sup:.6e};

boundaryField
{{
{_walls(f"        type            kqRWallFunction;{chr(10)}        value           uniform {k_sup:.6e};")}
    tile
    {{
        type            turbulentIntensityKineticEnergyInlet;
        intensity       {I_SUP};
        value           uniform {k_sup:.6e};
    }}
    rack_out
    {{
        type            turbulentIntensityKineticEnergyInlet;
        intensity       {I_RACK};
        value           uniform {K_RACK:.6e};
    }}
    rack_in
    {{
        type            zeroGradient;
    }}
    return
    {{
        type            inletOutlet;
        inletValue      uniform {k_sup:.6e};
        value           uniform {k_sup:.6e};
    }}
    frontAndBack
    {{
        type            empty;
    }}
}}
"""


def field_omega(qv_tile=QV_TILE):
    k_sup = 1.5 * (I_SUP * qv_tile / A_TILE) ** 2
    om_sup = k_sup ** 0.5 / (0.09 ** 0.25 * L_SUP)
    return f"""dimensions      [0 0 -1 0 0 0 0];

internalField   uniform {om_sup:.6e};

boundaryField
{{
{_walls(f"        type            omegaWallFunction;{chr(10)}        value           uniform {om_sup:.6e};")}
    tile
    {{
        type            turbulentMixingLengthFrequencyInlet;
        mixingLength    {L_SUP};
        value           uniform {om_sup:.6e};
    }}
    rack_out
    {{
        type            turbulentMixingLengthFrequencyInlet;
        mixingLength    {L_RACK};
        value           uniform {OM_RACK:.6e};
    }}
    rack_in
    {{
        type            zeroGradient;
    }}
    return
    {{
        type            inletOutlet;
        inletValue      uniform {om_sup:.6e};
        value           uniform {om_sup:.6e};
    }}
    frontAndBack
    {{
        type            empty;
    }}
}}
"""


def field_nut(nut_wall='nutkWallFunction'):
    calc = "        type            calculated;\n        value           uniform 0;"
    return f"""dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
{_walls("        type            " + nut_wall + ";" + chr(10) + "        value           uniform 0;")}
{chr(10).join(f"    {p}{chr(10)}    {{{chr(10)}{calc}{chr(10)}    }}" for p in OPEN)}
    frontAndBack
    {{
        type            empty;
    }}
}}
"""


def field_alphat():
    calc = "        type            calculated;\n        value           uniform 0;"
    jay = (f"        type            alphatJayatillekeWallFunction;\n"
           f"        Prt             {PRT};\n        value           uniform 0;")
    return f"""dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
{_walls(jay)}
{chr(10).join(f"    {p}{chr(10)}    {{{chr(10)}{calc}{chr(10)}    }}" for p in OPEN)}
    frontAndBack
    {{
        type            empty;
    }}
}}
"""


# ---------------------------------------------------------------------------
def build(name, h, end_time, write_interval, dt_rack=DT_RACK, gravity=True,
          plant=False, seed_from=None, qv_tile=QV_TILE,
          nut_wall="nutkWallFunction"):
    case = os.path.join(HERE, name)
    bmd, ncells = block_mesh_dict(h)
    w(case, "system/blockMeshDict", "dictionary", "blockMeshDict", bmd)
    w(case, "system/controlDict", "dictionary", "controlDict",
      control_dict(end_time, write_interval,
                   "latestTime" if seed_from else "startTime"))
    w(case, "system/fvSchemes", "dictionary", "fvSchemes", FV_SCHEMES)
    w(case, "system/fvSolution", "dictionary", "fvSolution", FV_SOLUTION)
    w(case, "constant/transportProperties", "dictionary", "transportProperties",
      f"""transportModel  Newtonian;

nu              {NU:.6e};
beta            {BETA:.9e};
TRef            {TREF:.1f};
Pr              {PR:.6f};
Prt             {PRT};
""")
    w(case, "constant/thermalAuditProperties", "dictionary", "thermalAuditProperties",
      f"rho0            {RHO0};\ncp0             {CP0};\n")
    w(case, "constant/turbulenceProperties", "dictionary", "turbulenceProperties",
      """simulationType  RAS;

RAS
{
    RASModel        kOmegaSST;
    turbulence      on;
    printCoeffs     on;
}
""")
    w(case, "constant/g", "uniformDimensionedVectorField", "g",
      "dimensions      [0 1 -2 0 0 0 0];\nvalue           (0 0 %s);\n"
      % (f"-{G}" if gravity else "0"))
    if plant:
        w(case, "constant/fvOptions", "dictionary", "fvOptions",
          f"""roomPlant
{{
    type            scalarSemiImplicitSource;
    selectionMode   all;
    volumeMode      absolute;
    sources
    {{
        T           ({S_PLANT:.12e} 0);
    }}
}}
""")
    else:
        fo = os.path.join(case, "constant/fvOptions")
        if os.path.exists(fo):
            os.remove(fo)

    w(case, "0.orig/U", "volVectorField", "U", field_U(qv_tile))
    w(case, "0.orig/p_rgh", "volScalarField", "p_rgh", field_p_rgh())
    w(case, "0.orig/T", "volScalarField", "T", field_T(dt_rack))
    w(case, "0.orig/k", "volScalarField", "k", field_k(qv_tile))
    w(case, "0.orig/omega", "volScalarField", "omega", field_omega(qv_tile))
    w(case, "0.orig/nut", "volScalarField", "nut", field_nut(nut_wall))
    w(case, "0.orig/alphat", "volScalarField", "alphat", field_alphat())

    with open(os.path.join(case, "CASE.txt"), "w") as fh:
        fh.write(
            f"case               {name}\n"
            f"kind               {'RESTART TWIN of ' + seed_from if seed_from else 'primary'}\n"
            f"slice              y-z, thickness {W_R} m (one rack pitch), empty frontAndBack\n"
            f"domain             {YS[-1]} m (y) x {ZS[-1]} m (z)\n"
            f"rack void          y [{YS[RACK_I]}, {YS[RACK_I+1]}]  z [0, {H_R}]\n"
            f"cell size          {h} m\n"
            f"cells              {ncells}\n"
            f"solver             buoyantBoussinesqSimpleFoam\n"
            f"turbulence         kOmegaSST, Prt {PRT}\n"
            f"nut wall treatment {nut_wall}\n"
            f"gravity            {'-%s m/s2 in z' % G if gravity else '0 (control C1)'}\n"
            f"Qv_rack            {QV_RACK} m3/s   U_face {U_RACK:.4f} m/s\n"
            f"Qv_tile            {qv_tile} m3/s   U_tile {qv_tile/A_TILE:.4f} m/s\n"
            f"provisioning       {100.0*qv_tile/QV_RACK:.1f} % of rack demand\n"
            f"dT_rack            {dt_rack} K\n"
            f"T_sup              {T_SUP} K\n"
            f"TRef (audit datum) {TREF} K\n"
            f"beta.dT_rack       {BETA*dt_rack:.6f}   (limit 0.1 on the DOMAIN span)\n"
            f"dT_dom limit       {0.1/BETA:.4f} K\n"
            f"P_rack (lab rho.cp {RHO_CP:.4f})  {RHO_CP*QV_RACK*dt_rack:.1f} W\n"
            f"P_rack (spec 1.177*1006)          {1.177*1006.0*QV_RACK*dt_rack:.1f} W\n"
            f"Re_tile            {U_TILE*S_T/NU:.4g}\n"
            f"Re_rack            {U_RACK*W_R/NU:.4g}\n"
            f"Ri_tile            {G*BETA*dt_rack*S_T/U_TILE**2:.4g}\n"
            f"Ri_rack            {G*BETA*dt_rack*H_R/U_RACK**2:.4g}\n"
            f"Ra_H               {G*BETA*dt_rack*H_ROOM**3/(NU*(NU/PR)):.4g}\n"
            f"planted_source     {Q_PLANT_W if plant else 0.0} W"
            f"  (S {S_PLANT if plant else 0.0:.12e} K.m3/s)\n"
            f"endTime            {end_time}\n")
    return case, ncells


CASES = {
    # name              h        end   write  dT      g      plant  seed
    # endTime values are the AUTHORISED-BUDGET caps, not convergence promises.
    #
    # THE RATE IS MEASURED TWICE AND THE TWO DISAGREE, WHICH IS THE USEFUL PART.
    # A 100-iteration probe read 2.70e5 cell.iter/(core.s) -- the spec section
    # 10 planning rate exactly.  The full 5,000-iteration coarse case read
    # 5.22e5, and the 5,000-iteration under case 4.81e5.  The probe is
    # pessimistic by ~1.9x because mesh construction, wallDist and the first
    # matrix assembly are amortised over 100 iterations instead of 5,000.  A
    # SHORT PROBE IS THEREFORE THE WRONG INSTRUMENT FOR PRICING A LONG RUN, and
    # every figure below is priced at the measured long-run rate of 4.8e5.
    #   coarse  46,400 x 9,000 / 4.8e5  =  870 s = 14.5 core-min
    #   fine   104,400 x 4,000 / 4.8e5  =  870 s = 14.5 core-min
    #   each control 46,400 x 800 / 4.8e5 = 77 s = 1.3 core-min
    # 9,000 on the coarse rather than 5,000 because at 5,000 its S13 monitor
    # passed at 0.0014 % while the HEAT BALANCE still read 0.5244 % and failed:
    # the graded quantity had stopped moving and the energy field had not.
    #  name              h        end  write  dT       g      plant  seed          Qv_tile
    "K2bP_coarse":     (0.0125,  9000,  500,  DT_RACK, True,  False, None,          QV_TILE),
    # THE FINE MESH'S endTime IS A BUDGET LINE AND IT IS LABELLED AS ONE.
    # 1,500 iterations is not a convergence claim: the 1/N^2 argument in
    # physics_rules.yaml section 1 puts a 1.5x refinement at ~2.25x the coarse
    # mesh's iterations, i.e. ~20,000 here, which is ~95 core-minutes for this
    # mesh alone against a 60 core-minute authorisation for the whole pilot.
    # The fine mesh is therefore a BUILD-AND-COST demonstration and grades
    # nothing; comparing it against the coarse mesh at unequal convergence would
    # be reporting iteration error as mesh error, the exact error K0c's Ra = 1e3
    # pair would have made.
    "K2bP_fine":       (1/120.0, 1500,  500,  DT_RACK, True,  False, None,          QV_TILE),
    # THE RECIRCULATION BED.  The balanced slice above supplies exactly what the
    # rack draws and is therefore CONTAINED: theta comes out at 7e-04 and the
    # recirculation index has nothing to bite on -- KV1b's degenerate-control
    # defect wearing a new face.  Under-provisioning the tile is spec section
    # 9's own sensitivity parameter ("tile/rack flow imbalance +/-30%"), and at
    # 70 % the rack must draw 30 % of its air from the room, so theta MUST move.
    # The three controls are seeded from THIS case, not from the balanced one,
    # for exactly the same reason: a gravity-off twin of a case with no
    # stratification to collapse would prove nothing.
    "K2bP_under":      (0.0125,  5000,  500,  DT_RACK, True,  False, None,          0.245),
    "K2bP_C1_g0":      (0.0125,   800,  400,  DT_RACK, False, False, "K2bP_under",  0.245),
    "K2bP_C2_dT13":    (0.0125,   800,  400,  13.2,    True,  False, "K2bP_under",  0.245),
    # C3 AND ITS TWIN RUN LONG, AND THE REASON IS THE FIRST RUN'S RESULT.
    # At 800 iterations the recovery read 315.57 W of a planted 500.000 W and
    # was still climbing -- moving, therefore not degenerate, and not landed
    # either. 5,000 iterations each under a 20 core-minute authorisation to
    # finish it. writeInterval 500 so the recovery has ten points and the
    # TWIN-DIFFERENCE NOISE FLOOR can be measured rather than assumed: the
    # governed recovery tolerance is 0.1 % = 0.5 W, and this case's own ledger
    # carries several watts of wobble, so whether the tolerance is reachable
    # here at all is itself a measurement.
    "K2bP_C3_plant":   (0.0125,  5000,  500,  DT_RACK, True,  True,  "K2bP_under",  0.245),
    # C3's NEGATIVE TWIN, and it is not optional.  KV1 established that a
    # positive control run without its negative twin cannot tell "the instrument
    # recovered the plant" from "the instrument returns that number for
    # anything".  C3b is byte-identical to C3 except that `constant/fvOptions`
    # does not exist, starts from the same seed and runs the same 800
    # iterations, so the recovered plant is the DIFFERENCE of two ledgers taken
    # at the same convergence state and the common closure error subtracts out.
    "K2bP_C3b_noplant":(0.0125,  5000,  500,  DT_RACK, True,  False, "K2bP_under",  0.245),
    # ---- THE WALL-TREATMENT PAIR (2026-08-18) -------------------------------
    # K2a section 6 specifies wall functions with y+ in 30-300. MEASURED on this
    # module: y+ averages 2.9-9.1, and REFINING MAKES IT WORSE (3.3-5.4 on the
    # fine mesh). These two cases resolve which treatment is correct, and they
    # do it by changing ONE THING: the `nut` wall function type. Same mesh, same
    # dictionaries, same seed, same iteration count as `K2bP_under`, so anything
    # that moves between them moves because of the wall treatment and nothing
    # else. Coarsening the mesh to reach y+ >= 30 would also have changed the
    # interior resolution, which changes the answer for a second reason and
    # would have converted a precondition into a calibration.
    #   K2bP_under      nutkWallFunction        -- assumes the log law; INVALID
    #                                              at the measured y+
    #   K2bP_WSpalding  nutUSpaldingWallFunction -- Spalding's law, continuous
    #                                              through the buffer layer, VALID
    #                                              at the measured y+
    #   K2bP_WLowRe     nutLowReWallFunction     -- nut = 0 at the wall, i.e. the
    #                                              viscous sublayer is resolved
    "K2bP_WSpalding":  (0.0125,  5000,  500,  DT_RACK, True,  False, None,          0.245),
    "K2bP_WLowRe":     (0.0125,  5000,  500,  DT_RACK, True,  False, None,          0.245),
}


def main(argv):
    want = argv[1:] or list(CASES)
    print(f"rho.cp             = {RHO_CP:.4f} J/m3/K")
    print(f"U_tile             = {U_TILE:.4f} m/s   Re_tile = {U_TILE*S_T/NU:.4g}")
    print(f"U_rack face        = {U_RACK:.4f} m/s   Re_rack = {U_RACK*W_R/NU:.4g}")
    print(f"P_rack (lab)       = {P_RACK_LAB:.1f} W   (spec recalled pair "
          f"{P_RACK_SPEC:.1f} W, {100*(P_RACK_SPEC-P_RACK_LAB)/P_RACK_LAB:+.2f} %)")
    print(f"beta.dT_rack       = {BETA*DT_RACK:.6f}   domain span limit "
          f"{0.1/BETA:.4f} K")
    print(f"k/omega supply     = {K_SUP:.6e} / {OM_SUP:.6e}")
    print(f"k/omega rack       = {K_RACK:.6e} / {OM_RACK:.6e}")
    for name in want:
        if name not in CASES:
            raise SystemExit(f"unknown case {name}")
        h, end, wi, dt, g, plant, seed, qvt = CASES[name]
        nw = {"K2bP_WSpalding": "nutUSpaldingWallFunction",
              "K2bP_WLowRe": "nutLowReWallFunction"}.get(name, "nutkWallFunction")
        case, n = build(name, h, end, wi, dt, g, plant, seed, qvt, nw)
        print(f"built {name:16s} {n:7d} cells  dT {dt:5.2f} K  "
              f"g {'on ' if g else 'off'}  plant {str(plant):5s} "
              f"Qv_tile {qvt:.4f} ({100*qvt/QV_RACK:.0f} %)  {nw}"
              + (f"  seed {seed}" if seed else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
