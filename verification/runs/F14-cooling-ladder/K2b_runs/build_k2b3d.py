#!/usr/bin/env python3
"""build_k2b3d.py -- the K2b 3D COARSE PROBE, F14 cooling ladder.

    python3 build_k2b3d.py           # writes K2b3D_probe beside this file

WHAT THIS IS FOR, AND WHAT IT IS NOT FOR
----------------------------------------
`K2b_PILOT_RESULTS.md` section 9 closes with one open number.  The 2D pilot
measured this machine at **4.8e5 cell.iter/(core.s)** on turbulent SST, against
the 1.0e5 K2a section 10 planned with -- but K2a's figure is 2.7e5 derated by an
**assumed** factor of 2.7 for "3D + turbulence", and the pilot could not measure
a derate it never ran in 3D.  The two readings put the 3D graded pair at
580 core-minutes and at 1,570 core-minutes respectively, and the whole
authorisation question sits between them.

**This case exists to collapse that range and nothing else.**  200 outer
iterations on the spec's own 3D coarse module, timed.  It is NOT a result, it is
NOT converged, it grades nothing, and no quantity it prints may be quoted as a
measurement of the module.  Its single output is a rate in
cell.iterations per core-second.

WHY IT IS THE REAL MODULE AND NOT A CHEAPER STAND-IN
-----------------------------------------------------
A derate measured on a simplified case would not be the derate.  This builds the
full spec-section-2 default layout -- N = 4 racks, per-rack `rack_i_in` /
`rack_i_out` face pairs each carrying `outletMappedUniformInlet`, four supply
tiles, a ceiling return, k-omega SST with wall functions -- so the per-iteration
work is the work the graded run would do.

AND IT CARRIES THE ONE THING THE 2D SLICE STRUCTURALLY COULD NOT
-----------------------------------------------------------------
The pilot's finding was that a balanced, contained 2D slice reports theta = 0.0071
because the tile delivers exactly what the rack draws and there is no deficit to
make up -- the recirculation index is dead on arrival there.  In 3D the rack row
is 2.4 m of a 3.6 m domain, so the end margins (`L_end` = 0.60 m at each end)
are OPEN: air can travel from the hot aisle to the cold aisle around the ends of
the row, with no provisioning imbalance at all.  That path does not exist in the
slice.  This case is built BALANCED (n_t = N, tile supply = rack demand) for
exactly that reason: at 200 iterations it cannot say what theta becomes, but it
is the geometry in which the question is answerable, and the graded 3D run will
answer it.

CELL COUNT AGAINST THE SPEC
---------------------------
K2a section 6 puts the 3D coarse mesh at ~0.20 M cells at a 60 mm base cell and
says a build departing by more than 2x re-prices the rung.  This mesh is
**132,840 cells** at a ~60 mm cell with the divisions chosen to land exactly on
every geometric boundary -- 0.66x the spec's figure, inside the band.  The
difference is the unmeshed rack void (23,760 cells), which the spec's round
number did not subtract.  Rates are per cell.iteration, so the count does not
bias the derate.
"""

import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_k2b as B                       # one table, not two

NAME = "K2b3D_probe"
END_TIME, WRITE_INTERVAL = 200, 200

# ---- the interval edges.  Every patch boundary is one of these. -------------
XS = [0.0, 0.6, 1.2, 1.8, 2.4, 3.0, 3.6]    # L_end, 4 racks of W_r, L_end
YS = [0.0, 0.6, B.W_CA, B.W_CA + B.D_R, 2.6, 3.2, B.W_CA + B.D_R + B.W_HA]
ZS = [0.0, B.H_R, B.H_ROOM]
NXD = [10, 10, 10, 10, 10, 10]              # ~60 mm
NYD = [10, 10, 18, 5, 10, 5]
NZD = [33, 12]
RACK_XI = (1, 2, 3, 4)                      # x-intervals occupied by the row
RACK_YI, RACK_ZI = 2, 0
TILE_YI, RETURN_YI = 1, 4
N_RACKS = len(RACK_XI)

A_RACK_FACE = (YS[1] - YS[0]) * 0          # placeholder, computed below
A_RACK_FACE = (XS[2] - XS[1]) * B.H_R       # 0.6 x 2.0 = 1.2 m2 per rack face
A_TILE_TOT = N_RACKS * B.S_T * B.S_T        # four 0.6 x 0.6 tiles
QV_TILE_TOT = N_RACKS * B.QV_TILE           # balanced: supply = total rack demand
U_TILE = QV_TILE_TOT / A_TILE_TOT
K_SUP = 1.5 * (B.I_SUP * U_TILE) ** 2
OM_SUP = K_SUP ** 0.5 / (0.09 ** 0.25 * B.L_SUP)

WALLS = ["floor", "ceiling", "wall_cold", "wall_hot", "wall_x0", "wall_x1",
         "rack_top", "rack_end"]
RACK_IN = [f"rack{r}_in" for r in range(N_RACKS)]
RACK_OUT = [f"rack{r}_out" for r in range(N_RACKS)]
OPEN = ["tile", "return"] + RACK_IN + RACK_OUT


def block_mesh_dict():
    NX, NY, NZ = len(XS), len(YS), len(ZS)
    def vid(i, j, k): return k * (NY * NX) + j * NX + i
    verts = [f"    ({x:.6f} {y:.6f} {z:.6f})"
             for k, z in enumerate(ZS) for j, y in enumerate(YS) for i, x in enumerate(XS)]
    def is_void(i, j, k): return (i in RACK_XI) and j == RACK_YI and k == RACK_ZI
    active = [(i, j, k) for k in range(NZ - 1) for j in range(NY - 1)
              for i in range(NX - 1) if not is_void(i, j, k)]

    def C(i, j, k):
        return dict(v0=vid(i,j,k),   v1=vid(i+1,j,k),   v2=vid(i+1,j+1,k),   v3=vid(i,j+1,k),
                    v4=vid(i,j,k+1), v5=vid(i+1,j,k+1), v6=vid(i+1,j+1,k+1), v7=vid(i,j+1,k+1))
    blocks = ["    hex ({v0} {v1} {v2} {v3} {v4} {v5} {v6} {v7}) ({a} {b} {c}) simpleGrading (1 1 1)"
              .format(a=NXD[i], b=NYD[j], c=NZD[k], **C(i, j, k)) for i, j, k in active]

    # faces ordered so the right-hand normal points OUT of the domain
    f_bot = lambda i,j,k: "({v0} {v3} {v2} {v1})".format(**C(i,j,k))
    f_top = lambda i,j,k: "({v4} {v5} {v6} {v7})".format(**C(i,j,k))
    f_ylo = lambda i,j,k: "({v0} {v1} {v5} {v4})".format(**C(i,j,k))
    f_yhi = lambda i,j,k: "({v3} {v7} {v6} {v2})".format(**C(i,j,k))
    f_xlo = lambda i,j,k: "({v0} {v4} {v7} {v3})".format(**C(i,j,k))
    f_xhi = lambda i,j,k: "({v1} {v2} {v6} {v5})".format(**C(i,j,k))

    pf = {p: [] for p in WALLS + OPEN}
    for i, j, k in active:
        if k == 0:                                    # floor level
            pf["tile" if (j == TILE_YI and i in RACK_XI) else "floor"].append(f_bot(i,j,k))
        if k == NZ - 2:                               # ceiling level
            pf["return" if (j == RETURN_YI and i in RACK_XI) else "ceiling"].append(f_top(i,j,k))
        if j == 0:            pf["wall_cold"].append(f_ylo(i,j,k))
        if j == NY - 2:       pf["wall_hot"].append(f_yhi(i,j,k))
        if i == 0:            pf["wall_x0"].append(f_xlo(i,j,k))
        if i == NX - 2:       pf["wall_x1"].append(f_xhi(i,j,k))
    # the rack row's own surfaces
    for n, i in enumerate(RACK_XI):
        pf[RACK_IN[n]].append(f_yhi(i, RACK_YI - 1, RACK_ZI))   # front, cold-aisle side
        pf[RACK_OUT[n]].append(f_ylo(i, RACK_YI + 1, RACK_ZI))  # rear, hot-aisle side
        pf["rack_top"].append(f_bot(i, RACK_YI, RACK_ZI + 1))   # the row's lid
    # THE ROW ENDS -- the 3D-only surfaces, and the reason this case exists
    pf["rack_end"].append(f_xhi(RACK_XI[0] - 1, RACK_YI, RACK_ZI))
    pf["rack_end"].append(f_xlo(RACK_XI[-1] + 1, RACK_YI, RACK_ZI))

    def blk(name, ptype):
        fl = "\n            ".join(pf[name])
        return (f"    {name}\n    {{\n        type {ptype};\n        faces\n"
                f"        (\n            {fl}\n        );\n    }}")
    bnd = [blk(p, "wall") for p in WALLS] + [blk(p, "patch") for p in OPEN]
    n = sum(NXD[i] * NYD[j] * NZD[k] for i, j, k in active)
    return "\n".join(["scale   1;", "", "vertices", "(", "\n".join(verts), ");", "",
                      "blocks", "(", "\n".join(blocks), ");", "", "edges();", "",
                      "boundary", "(", "\n".join(bnd), ");", ""]), n


def wl(entry): return "\n".join(f"    {p}\n    {{\n{entry}\n    }}" for p in WALLS)


def main():
    case = os.path.join(HERE, NAME)
    bmd, n = block_mesh_dict()
    B.w(case, "system/blockMeshDict", "dictionary", "blockMeshDict", bmd)

    fos = "\n".join(
        [B._sfv(f"T_rack{r}_in_mdot", RACK_IN[r], "weightedAverage", "T", "phi") for r in range(N_RACKS)] +
        [B._sfv(f"T_rack{r}_out_area", RACK_OUT[r], "areaAverage", "T") for r in range(N_RACKS)] +
        [B._sfv(f"phi_{p}", p, "sum", "phi") for p in ("tile", "return") + tuple(RACK_IN) + tuple(RACK_OUT)] +
        [f"""    Tspan
    {{
        type            fieldMinMax;
        libs            (fieldFunctionObjects);
        fields          (T U);
        location        true;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval {B.MONITOR_INTERVAL};
        writeControl    timeStep;
        writeInterval   {B.MONITOR_INTERVAL};
    }}"""])
    B.w(case, "system/controlDict", "dictionary", "controlDict", f"""application     buoyantBoussinesqSimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {END_TIME};
deltaT          1;
writeControl    timeStep;
writeInterval   {WRITE_INTERVAL};
purgeWrite      0;
writeFormat     ascii;
writePrecision  10;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;

functions
{{
{fos}
}}
""")
    B.w(case, "system/fvSchemes", "dictionary", "fvSchemes", B.FV_SCHEMES)
    B.w(case, "system/fvSolution", "dictionary", "fvSolution", B.FV_SOLUTION)
    B.w(case, "constant/transportProperties", "dictionary", "transportProperties",
        f"transportModel  Newtonian;\n\nnu              {B.NU:.6e};\nbeta            {B.BETA:.9e};\n"
        f"TRef            {B.TREF:.1f};\nPr              {B.PR:.6f};\nPrt             {B.PRT};\n")
    B.w(case, "constant/thermalAuditProperties", "dictionary", "thermalAuditProperties",
        f"rho0            {B.RHO0};\ncp0             {B.CP0};\n")
    B.w(case, "constant/turbulenceProperties", "dictionary", "turbulenceProperties",
        "simulationType  RAS;\n\nRAS\n{\n    RASModel        kOmegaSST;\n"
        "    turbulence      on;\n    printCoeffs     on;\n}\n")
    B.w(case, "constant/g", "uniformDimensionedVectorField", "g",
        f"dimensions      [0 1 -2 0 0 0 0];\nvalue           (0 0 -{B.G});\n")

    rin = "\n".join(f"""    {p}
    {{
        type            flowRateOutletVelocity;
        volumetricFlowRate constant {B.QV_RACK};
        value           uniform (0 0 0);
    }}""" for p in RACK_IN)
    rout = "\n".join(f"""    {p}
    {{
        type            flowRateInletVelocity;
        volumetricFlowRate constant {B.QV_RACK};
        value           uniform (0 0 0);
    }}""" for p in RACK_OUT)
    B.w(case, "0.orig/U", "volVectorField", "U", f"""dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{{
{wl("        type            noSlip;")}
    tile
    {{
        type            flowRateInletVelocity;
        volumetricFlowRate constant {QV_TILE_TOT};
        value           uniform (0 0 0);
    }}
    return
    {{
        type            pressureInletOutletVelocity;
        value           uniform (0 0 0);
    }}
{rin}
{rout}
}}
""")
    ffp = "        type            fixedFluxPressure;\n        value           uniform 0;"
    B.w(case, "0.orig/p_rgh", "volScalarField", "p_rgh", f"""dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
{wl(ffp)}
    tile
    {{
{ffp}
    }}
{chr(10).join(f"    {p}{chr(10)}    {{{chr(10)}{ffp}{chr(10)}    }}" for p in RACK_IN + RACK_OUT)}
    return
    {{
        type            fixedValue;
        value           uniform 0;
    }}
}}
""")
    tmap = "\n".join(f"""    {RACK_OUT[r]}
    {{
        type            outletMappedUniformInlet;
        outlets
        {{
            {RACK_IN[r]}
            {{
                fraction    constant 1;
                offset      constant {B.DT_RACK};
            }}
        }}
        value           uniform {B.T_SUP + B.DT_RACK};
    }}""" for r in range(N_RACKS))
    B.w(case, "0.orig/T", "volScalarField", "T", f"""dimensions      [0 0 0 1 0 0 0];

internalField   uniform {B.T_SUP};

boundaryField
{{
{wl("        type            zeroGradient;")}
    tile
    {{
        type            fixedValue;
        value           uniform {B.T_SUP};
    }}
    return
    {{
        type            inletOutlet;
        inletValue      uniform {B.T_SUP};
        value           uniform {B.T_SUP};
    }}
{chr(10).join(f"    {p}{chr(10)}    {{{chr(10)}        type            zeroGradient;{chr(10)}    }}" for p in RACK_IN)}
{tmap}
}}
""")
    B.w(case, "0.orig/k", "volScalarField", "k", f"""dimensions      [0 2 -2 0 0 0 0];

internalField   uniform {K_SUP:.6e};

boundaryField
{{
{wl(f"        type            kqRWallFunction;{chr(10)}        value           uniform {K_SUP:.6e};")}
    tile
    {{
        type            turbulentIntensityKineticEnergyInlet;
        intensity       {B.I_SUP};
        value           uniform {K_SUP:.6e};
    }}
    return
    {{
        type            inletOutlet;
        inletValue      uniform {K_SUP:.6e};
        value           uniform {K_SUP:.6e};
    }}
{chr(10).join(f"    {p}{chr(10)}    {{{chr(10)}        type            zeroGradient;{chr(10)}    }}" for p in RACK_IN)}
{chr(10).join(f'''    {p}
    {{
        type            turbulentIntensityKineticEnergyInlet;
        intensity       {B.I_RACK};
        value           uniform {B.K_RACK:.6e};
    }}''' for p in RACK_OUT)}
}}
""")
    B.w(case, "0.orig/omega", "volScalarField", "omega", f"""dimensions      [0 0 -1 0 0 0 0];

internalField   uniform {OM_SUP:.6e};

boundaryField
{{
{wl(f"        type            omegaWallFunction;{chr(10)}        value           uniform {OM_SUP:.6e};")}
    tile
    {{
        type            turbulentMixingLengthFrequencyInlet;
        mixingLength    {B.L_SUP};
        value           uniform {OM_SUP:.6e};
    }}
    return
    {{
        type            inletOutlet;
        inletValue      uniform {OM_SUP:.6e};
        value           uniform {OM_SUP:.6e};
    }}
{chr(10).join(f"    {p}{chr(10)}    {{{chr(10)}        type            zeroGradient;{chr(10)}    }}" for p in RACK_IN)}
{chr(10).join(f'''    {p}
    {{
        type            turbulentMixingLengthFrequencyInlet;
        mixingLength    {B.L_RACK};
        value           uniform {B.OM_RACK:.6e};
    }}''' for p in RACK_OUT)}
}}
""")
    calc = "        type            calculated;\n        value           uniform 0;"
    B.w(case, "0.orig/nut", "volScalarField", "nut", f"""dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
{wl("        type            nutkWallFunction;" + chr(10) + "        value           uniform 0;")}
{chr(10).join(f"    {p}{chr(10)}    {{{chr(10)}{calc}{chr(10)}    }}" for p in OPEN)}
}}
""")
    jay = (f"        type            alphatJayatillekeWallFunction;\n"
           f"        Prt             {B.PRT};\n        value           uniform 0;")
    B.w(case, "0.orig/alphat", "volScalarField", "alphat", f"""dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
{wl(jay)}
{chr(10).join(f"    {p}{chr(10)}    {{{chr(10)}{calc}{chr(10)}    }}" for p in OPEN)}
}}
""")
    with open(os.path.join(case, "CASE.txt"), "w") as fh:
        fh.write(f"""case               {NAME}
kind               COST PROBE ONLY -- 200 iterations, not converged, grades nothing
purpose            measure the 3D+SST derate K2a section 10 assumed at 2.7 and never measured
domain             {XS[-1]} x {YS[-1]} x {ZS[-1]} m, full 3D (no empty patches)
racks              {N_RACKS}, x in [{XS[RACK_XI[0]]}, {XS[RACK_XI[-1]+1]}], per-rack face pairs
row ends           OPEN -- L_end {XS[1]} m each side; the 3D-only recirculation path
                   the 2D slice structurally cannot have
cells              {n}   (spec section 6 says ~0.20 M; 0.66x, inside the 2x band)
cell size          ~60 mm, divisions landing exactly on every geometric boundary
solver             buoyantBoussinesqSimpleFoam, kOmegaSST, Prt {B.PRT}
Qv_rack            {B.QV_RACK} m3/s each, U_face {B.QV_RACK/A_RACK_FACE:.4f} m/s
Qv_tile total      {QV_TILE_TOT} m3/s over {A_TILE_TOT:.2f} m2, U_tile {U_TILE:.4f} m/s
provisioning       {100.0*QV_TILE_TOT/(N_RACKS*B.QV_RACK):.1f} % (balanced, spec default n_t = N)
dT_rack            {B.DT_RACK} K   beta.dT {B.BETA*B.DT_RACK:.6f}
endTime            {END_TIME}
""")
    print(f"built {NAME}: {n} cells, {N_RACKS} racks, {len(XS)-1}x{len(YS)-1}x{len(ZS)-1} block grid")
    print(f"  U_tile {U_TILE:.4f} m/s   U_rack_face {B.QV_RACK/A_RACK_FACE:.4f} m/s")
    print(f"  at 4.8e5 cell.iter/core.s a 200-iteration probe costs "
          f"{n*END_TIME/4.8e5/60:.2f} core-min; at K2a's derated 1.0e5, {n*END_TIME/1.0e5/60:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
