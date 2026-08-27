#!/usr/bin/env python3
"""build_t5.py -- ONE parametric recipe for every T5 case (prereg S5.4, S15).

Registration: docs/campaigns/T-family/T5_PREREGISTRATION.md, frozen at 0fcbb92e.
Owed by S16.11 item 1.  Writes every case of the registered default ladder from a
single recipe with ONE refinement factor R = 1.6 applied to EVERY direction
INCLUDING the first wall layer (S5.4), so the three levels are geometrically
similar and the triple is a true refinement.

CASES (names are the comparator's: analyse_t5.py LEVELS -> T5_CUBE_{c,m,f})
    X_2d        2-D developing-channel precursor, simpleFoam (S5.3)
    T5_CUBE_c   coarse   conjugate, kOmegaSST, Pr_t 0.85, solid laplacian harmonic
    T5_CUBE_m   medium   idem
    T5_CUBE_f   fine     idem
    P_m         medium, Pr_t 0.50 (S8 DP)
    L_m         medium, laminar (S8 DC)
    S_m         medium, fluid-only, constant-T cube surface (S8 DS) -- surface
                temperature is a PARAMETER supplied after T5_CUBE_m has run
                (area-averaged conjugate surface temperature); this builder writes
                the case only when --s-m-tsurf is given, and refuses otherwise.
    H_c         coarse, solid laplacian `Gauss linear` (S5.6 DH)

GEOMETRY (S2.2, S5.2): H = 15 mm, cube front face at x = 0, floor y = 0, symmetry
plane z = 0 (half domain); x/H in [-8, 20], y/H in [0, 3.4], z/H in [0, 5].
Epoxy shell d = 1.5 mm inside the cube on its five exposed faces and its bottom;
the copper core is NOT meshed -- its boundary is patch `core`, T = 348.15 K
(INTERPRETATION 3/4).

MESH: blockMesh, a Cartesian block lattice 5 x 5 x 3 with the core block omitted;
cellZones `air` / `epoxy` set per block; the cube faces are named through
faceZones and `splitMeshRegions -cellZonesOnly -useFaceZones` so the region
interface patches carry the comparator's wall names (YPLUS_WALLS):
cube_front cube_top cube_rear cube_side_n (cube_side_s does NOT EXIST on a half
domain -- see CASE.txt; that is a finding, not a build choice), floor, roof.

DISCIPLINE: no `assert` carries a guard (L-332); every refusal is a raise or
sys.exit(2), driven under `python3 -O` in --selftest.  Solver libs are inserted
through scripts/foam_libs.py and RE-VERIFIED at every call site (rule 14) with a
raise, not an assert (S16.2).  Geometric constants are NEVER trusted from this
file's inputs: check_t5_mesh.py reads them back from polyMesh/points.
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
try:
    import foam_libs  # noqa: E402
except ImportError as exc:      # explicit, never silent
    sys.stderr.write("REFUSED: scripts/foam_libs.py not importable: %s\n" % exc)
    sys.exit(2)

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

# ---------------- REGISTERED CONSTANTS (prereg section cited) ----------------
H = 0.015            # m, S2.2
DELTA = 0.0015       # m, epoxy shell, S2.2
D_CH = 3.4 * H       # channel height, S2.2
L_UP, L_DN, W = 8.0 * H, 20.0 * H, 5.0 * H      # S5.2
R = 1.6              # refinement factor, S5.4, every direction
FIRST_LAYER_C = 0.128e-3          # m, coarse first fluid layer on the cube, S5.4
U_B = 4.47                        # m/s, S2.3
NU = 1.510e-05                    # m2/s, S2.3 (derived)
T_IN = 293.65                     # K, S7.1
T_CORE = 348.15                   # K, S4
P_ABS = 1.0e5                     # Pa
RHO = P_ABS / (287.0 * T_IN)      # perfect gas at inlet state
MU = NU * RHO
PR = 0.71                         # S2.3
CP_AIR = 1006.0
K_EPOXY = 0.24                    # W/mK, S2.2
RHO_EPOXY, CP_EPOXY = 1200.0, 1000.0   # steady: enter no result
PRT_DEFAULT, PRT_ARM = 0.85, 0.50      # S8
ENDTIME, WRITE_INT, PURGE = 5000, 1000, 3    # S5.5
LEVELS = {"c": 0, "m": 1, "f": 2}
YPLUS_WALLS = ("cube_front", "cube_top", "cube_rear", "cube_side_n", "floor", "roof")
SOLVER_LIB = "libfieldFunctionObjects.so"

# base (coarse) cell counts per block slab; every level = round(base * R**lvl)
BASE_X = [24, 2, 9, 2, 32]       # [-8H,0] [0,d] [d,H-d] [H-d,H] [H,20H]
Y1 = 0.0005                      # floor sub-station so the floor grading is monotone across the shell
BASE_Y = [2, 1, 9, 2, 20]        # [0,Y1] [Y1,d] [d,H-d] [H-d,H] [H,3.4H]
BASE_Z = [5, 2, 16]              # [0,H/2-d] [H/2-d,H/2] [H/2,5H]
# X_2d precursor (S5.3, S11: 3.0e4 cells): 80 H long channel, D = 3.4 H
X2D_LEN = 80.0 * H
X2D_NX, X2D_NY = 300, 100
X2D_FIRST = 0.05e-3


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def counts(lvl):
    f = R ** lvl
    return ([max(1, int(round(n * f))) for n in BASE_X],
            [max(1, int(round(n * f))) for n in BASE_Y],
            [max(1, int(round(n * f))) for n in BASE_Z])


# ---------------- grading helpers (numbers, never blockMesh's guesses) ------
def growth_ratio(first, n, length):
    """q such that first*(q^n-1)/(q-1) = length; q=1 when uniform."""
    if n <= 1:
        return 1.0
    if abs(first * n - length) / length < 1e-9:
        return 1.0
    lo, hi = (1.0000001, 50.0) if first * n < length else (0.02, 0.9999999)
    for _ in range(200):
        q = 0.5 * (lo + hi)
        s = first * (q ** n - 1.0) / (q - 1.0)
        if (s < length) == (first * n < length):
            lo = q
        else:
            hi = q
    return 0.5 * (lo + hi)


def grade_one_sided(first, n, length, fine_at_end):
    """Single-section geometric grading; expansion = last/first."""
    q = growth_ratio(first, n, length)
    e = q ** (n - 1)
    return "%.6g" % (1.0 / e if fine_at_end else e)


def grade_two_sided(first, n, length):
    """Multi-grading: fine at both ends.  Two equal halves."""
    n1 = n // 2
    n2 = n - n1
    q1 = growth_ratio(first, n1, 0.5 * length)
    q2 = growth_ratio(first, n2, 0.5 * length)
    return "((0.5 %.6g %.6g) (0.5 %.6g %.6g))" % (
        n1 / float(n), q1 ** (n1 - 1), n2 / float(n), 1.0 / q2 ** (n2 - 1))


def grade_upstream(first, n, length, near_frac=0.25, near_cells_frac=0.6):
    """Inflow slab: uniform far section, geometric near section fine at x=0."""
    n_near = max(2, int(round(n * near_cells_frac)))
    n_far = max(1, n - n_near)
    l_near = near_frac * length
    q = growth_ratio(first, n_near, l_near)
    return "((%.6g %.6g 1) (%.6g %.6g %.6g))" % (
        1.0 - near_frac, n_far / float(n), near_frac, n_near / float(n),
        1.0 / q ** (n_near - 1))


def grade_downstream(first, n, length, near_frac=0.25, near_cells_frac=0.6):
    n_near = max(2, int(round(n * near_cells_frac)))
    n_far = max(1, n - n_near)
    l_near = near_frac * length
    q = growth_ratio(first, n_near, l_near)
    return "((%.6g %.6g %.6g) (%.6g %.6g 1))" % (
        near_frac, n_near / float(n), q ** (n_near - 1),
        1.0 - near_frac, n_far / float(n))


# ---------------- OpenFOAM file helpers -------------------------------------
def hdr(cls, obj, loc="system"):
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class %s;\n"
            "    location \"%s\";\n    object %s;\n}\n\n" % (cls, loc, obj))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


# ---------------- blockMeshDict for the 3-D cube cases ----------------------
def block_mesh_3d(lvl):
    nx, ny, nz = counts(lvl)
    first = FIRST_LAYER_C / R ** lvl
    X = [-L_UP, 0.0, DELTA, H - DELTA, H, L_DN]
    Y = [0.0, Y1, DELTA, H - DELTA, H, D_CH]
    Z = [0.0, 0.5 * H - DELTA, 0.5 * H, W]
    gx = [grade_upstream(first, nx[0], L_UP), "1", "1", "1",
          grade_downstream(first, nx[4], L_DN - H)]
    gy = [grade_one_sided(first, ny[0], Y1, fine_at_end=False), "1", "1", "1",
          grade_two_sided(first, ny[4], D_CH - H)]
    gz = ["1", "1", grade_downstream(first, nz[2], W - 0.5 * H)]
    verts = []
    vid = {}
    for k, z in enumerate(Z):
        for j, y in enumerate(Y):
            for i, x in enumerate(X):
                vid[(i, j, k)] = len(verts)
                verts.append((x, y, z))
    blocks = []
    NI, NJ, NK = len(X) - 1, len(Y) - 1, len(Z) - 1
    def is_cube(i, j, k): return i in (1, 2, 3) and j in (0, 1, 2, 3) and k in (0, 1)
    def is_core(i, j, k): return (i, j, k) == (2, 2, 0)
    for k in range(NK):
        for j in range(NJ):
            for i in range(NI):
                if is_core(i, j, k):
                    continue
                zone = "epoxy" if is_cube(i, j, k) else "air"
                v = [vid[(i, j, k)], vid[(i + 1, j, k)], vid[(i + 1, j + 1, k)], vid[(i, j + 1, k)],
                     vid[(i, j, k + 1)], vid[(i + 1, j, k + 1)], vid[(i + 1, j + 1, k + 1)], vid[(i, j + 1, k + 1)]]
                blocks.append("    hex (%s) %s (%d %d %d) simpleGrading (%s %s %s)"
                              % (" ".join(map(str, v)), zone, nx[i], ny[j], nz[k], gx[i], gy[j], gz[k]))
    # boundary faces
    def face(i0, j0, k0, i1, j1, k1, i2, j2, k2, i3, j3, k3):
        return "(%d %d %d %d)" % (vid[(i0, j0, k0)], vid[(i1, j1, k1)], vid[(i2, j2, k2)], vid[(i3, j3, k3)])
    P = {n: [] for n in ("inlet", "outlet", "floor", "cube_bottom", "roof", "symmetry", "side", "core")}
    for k in range(NK):
        for j in range(NJ):
            P["inlet"].append(face(0, j, k, 0, j, k + 1, 0, j + 1, k + 1, 0, j + 1, k))
            P["outlet"].append(face(NI, j, k, NI, j + 1, k, NI, j + 1, k + 1, NI, j, k + 1))
    for k in range(NK):
        for i in range(NI):
            nm = "cube_bottom" if is_cube(i, 0, k) else "floor"
            P[nm].append(face(i, 0, k, i + 1, 0, k, i + 1, 0, k + 1, i, 0, k + 1))
            P["roof"].append(face(i, NJ, k, i, NJ, k + 1, i + 1, NJ, k + 1, i + 1, NJ, k))
    for j in range(NJ):
        for i in range(NI):
            if not is_core(i, j, 0):
                P["symmetry"].append(face(i, j, 0, i, j + 1, 0, i + 1, j + 1, 0, i + 1, j, 0))
            P["side"].append(face(i, j, NK, i + 1, j, NK, i + 1, j + 1, NK, i, j + 1, NK))
    # core: the faces of the omitted block (2,2,0)
    i, j, k = 2, 2, 0
    P["core"] += [face(i, j, k, i, j, k + 1, i, j + 1, k + 1, i, j + 1, k),          # x = d
                  face(i + 1, j, k, i + 1, j + 1, k, i + 1, j + 1, k + 1, i + 1, j, k + 1),  # x = H-d
                  face(i, j, k, i + 1, j, k, i + 1, j, k + 1, i, j, k + 1),          # y = d
                  face(i, j + 1, k, i, j + 1, k + 1, i + 1, j + 1, k + 1, i + 1, j + 1, k),  # y = H-d
                  face(i, j, k + 1, i + 1, j, k + 1, i + 1, j + 1, k + 1, i, j + 1, k + 1)]  # z = H/2-d
    types = dict(inlet="patch", outlet="patch", floor="wall", cube_bottom="wall", roof="wall",
                 symmetry="symmetryPlane", side="patch", core="wall")
    bnd = []
    for n, fl in P.items():
        bnd.append("    %s { type %s; faces (\n%s\n    ); }" % (n, types[n], "\n".join("        " + f for f in fl)))
    return (hdr("dictionary", "blockMeshDict") + "scale 1;\n\nvertices\n(\n" +
            "\n".join("    (%.9g %.9g %.9g)" % v for v in verts) +
            "\n);\n\nblocks\n(\n" + "\n".join(blocks) + "\n);\n\nedges ();\n\nboundary\n(\n" +
            "\n".join(bnd) + "\n);\n\nmergePatchPairs ();\n")


def topo_set_dict():
    """faceZones on the four exposed cube faces (half domain: one side)."""
    e = 1e-6
    boxes = {
        "cube_front": (-e, -e, -e, e, H + e, 0.5 * H + e),
        "cube_rear": (H - e, -e, -e, H + e, H + e, 0.5 * H + e),
        "cube_top": (-e, H - e, -e, H + e, H + e, 0.5 * H + e),
        "cube_side_n": (-e, -e, 0.5 * H - e, H + e, H + e, 0.5 * H + e),
    }
    acts = []
    for n, b in boxes.items():
        acts.append("    { name %sSet; type faceSet; action new; source boxToFace; "
                    "box (%.9g %.9g %.9g) (%.9g %.9g %.9g); }" % ((n,) + b))
        acts.append("    { name %s; type faceZoneSet; action new; source setToFaceZone; faceSet %sSet; }" % (n, n))
    return hdr("dictionary", "topoSetDict") + "actions\n(\n" + "\n".join(acts) + "\n);\n"


# ---------------- dictionaries: 3-D conjugate cases --------------------------
def control_dict(case, solver, regions):
    fos = ""
    if "air" in regions:
        fos = """
functions
{
    yPlus
    {
        type            yPlus;
        libs            (fieldFunctionObjects);
        region          air;
        writeControl    writeTime;
        writeInterval   1000;
    }
    wallHeatFlux
    {
        type            wallHeatFlux;
        libs            (fieldFunctionObjects);
        region          air;
        patches         (cube_front cube_top cube_rear cube_side_n floor roof);
        writeControl    writeTime;
        writeInterval   1000;
    }
}
"""
    elif solver == "simpleFoam":
        fos = """
functions
{
    yPlus
    {
        type            yPlus;
        libs            (fieldFunctionObjects);
        writeControl    writeTime;
        writeInterval   1000;
    }
}
"""
    return (hdr("dictionary", "controlDict") +
            "application     %s;\nstartFrom       startTime;\nstartTime       0;\nstopAt          endTime;\n"
            "endTime         %d;\ndeltaT          1;\nwriteControl    timeStep;\nwriteInterval   %d;\n"
            "purgeWrite      %d;\nwriteFormat     ascii;\nwritePrecision  10;\nwriteCompression off;\n"
            "timeFormat      general;\ntimePrecision   6;\nrunTimeModifiable false;\n%s"
            % (solver, ENDTIME, WRITE_INT, PURGE, fos))


def fv_schemes_air(laminar):
    turb = "" if laminar else ("    div(phi,k)      bounded Gauss linearUpwind grad(k);\n"
                               "    div(phi,omega)  bounded Gauss linearUpwind grad(omega);\n")
    return (hdr("dictionary", "fvSchemes", "system/air") +
            "ddtSchemes { default steadyState; }\ngradSchemes { default Gauss linear; }\n"
            "divSchemes\n{\n    default none;\n    div(phi,U)      bounded Gauss linearUpwind grad(U);\n"
            "    div(phi,h)      bounded Gauss linearUpwind grad(h);\n    div(phi,K)      bounded Gauss linear;\n"
            "%s    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;\n}\n"
            "laplacianSchemes { default Gauss linear corrected; }\ninterpolationSchemes { default linear; }\n"
            "snGradSchemes { default corrected; }\nwallDist { method meshWave; }\n" % turb)


def fv_schemes_epoxy(interface_scheme):
    return (hdr("dictionary", "fvSchemes", "system/epoxy") +
            "ddtSchemes { default steadyState; }\ngradSchemes { default Gauss linear; }\n"
            "divSchemes { default none; }\n"
            "laplacianSchemes\n{\n    default Gauss linear corrected;\n    laplacian(alpha,e) Gauss %s corrected;\n"
            "    laplacian(alpha,h) Gauss %s corrected;\n}\n"
            "interpolationSchemes { default linear; }\nsnGradSchemes { default corrected; }\n"
            % (interface_scheme, interface_scheme))


def fv_solution_air(laminar):
    return (hdr("dictionary", "fvSolution", "system/air") +
            "solvers\n{\n    rho { solver PCG; preconditioner DIC; tolerance 1e-8; relTol 0; }\n"
            "    p_rgh { solver GAMG; smoother GaussSeidel; tolerance 1e-8; relTol 0.01; }\n"
            "    \"(U|h|k|omega)\" { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0.05; }\n}\n"
            "SIMPLE\n{\n    momentumPredictor yes;\n    nNonOrthogonalCorrectors 0;\n    pRefCell 0;\n    pRefValue %g;\n}\n"
            "relaxationFactors\n{\n    fields { p_rgh 0.3; rho 1; }\n"
            "    equations { U 0.5; h 0.5; k 0.5; omega 0.5; }\n}\n" % P_ABS)


def fv_solution_epoxy():
    return (hdr("dictionary", "fvSolution", "system/epoxy") +
            "solvers\n{\n    \"(h|e)\" { solver PCG; preconditioner DIC; tolerance 1e-10; relTol 0.01; }\n}\n"
            "SIMPLE { nNonOrthogonalCorrectors 0; }\nrelaxationFactors { equations { \"(h|e)\" 0.9; } }\n")


def fv_solution_top():
    return hdr("dictionary", "fvSolution") + "PIMPLE { nOuterCorrectors 1; }\n"


def thermo_air():
    return (hdr("dictionary", "thermophysicalProperties", "constant/air") +
            "thermoType\n{\n    type heRhoThermo; mixture pureMixture; transport const; thermo hConst;\n"
            "    equationOfState perfectGas; specie specie; energy sensibleEnthalpy;\n}\n"
            "mixture\n{\n    specie { molWeight 28.966; }\n    thermodynamics { Cp %g; Hf 0; }\n"
            "    transport { mu %.6g; Pr %g; }\n}\n" % (CP_AIR, MU, PR))


def thermo_epoxy():
    return (hdr("dictionary", "thermophysicalProperties", "constant/epoxy") +
            "thermoType\n{\n    type heSolidThermo; mixture pureMixture; transport constIso; thermo hConst;\n"
            "    equationOfState rhoConst; specie specie; energy sensibleEnthalpy;\n}\n"
            "mixture\n{\n    specie { molWeight 100; }\n    thermodynamics { Hf 0; Cp %g; }\n"
            "    transport { kappa %g; }\n    equationOfState { rho %g; }\n}\n" % (CP_EPOXY, K_EPOXY, RHO_EPOXY))


def turbulence(laminar, prt):
    if laminar:
        return hdr("dictionary", "turbulenceProperties", "constant/air") + "simulationType laminar;\n"
    return (hdr("dictionary", "turbulenceProperties", "constant/air") +
            "simulationType RAS;\nRAS\n{\n    RASModel kOmegaSST;\n    turbulence on;\n    printCoeffs on;\n"
            "    kOmegaSSTCoeffs { Prt %g; }\n}\n" % prt)


def region_properties(regions):
    return (hdr("dictionary", "regionProperties", "constant") +
            "regions\n(\n    fluid (air)\n%s);\n" % ("    solid (epoxy)\n" if "epoxy" in regions else ""))


def g_file(loc):
    return (hdr("uniformDimensionedVectorField", "g", loc) +
            "dimensions [0 1 -2 0 0 0 0];\nvalue (0 0 0);\n")


def field(cls, name, dims, internal, entries, loc):
    body = "\n".join("    %s\n    {\n%s\n    }" % (p, "\n".join("        " + l for l in e)) for p, e in entries)
    return (hdr(cls, name, loc) + "dimensions %s;\n\ninternalField %s;\n\nboundaryField\n{\n%s\n}\n"
            % (dims, internal, body))


K_IN = 1.5 * (0.02 * U_B) ** 2                 # 2 % intensity placeholder for the precursor inlet
OMEGA_IN = K_IN ** 0.5 / (0.09 ** 0.25 * 0.07 * D_CH)


def air_fields(conjugate, laminar, prt, inlet_mapped, cube_faces, t_surf=None):
    """0.orig/air/*.  Cube faces: mappedWall interface (conjugate) or fixed T."""
    if inlet_mapped:
        u_in = ["type timeVaryingMappedFixedValue;", "setAverage off;", "offset (0 0 0);", "value uniform (%g 0 0);" % U_B]
        k_in = ["type timeVaryingMappedFixedValue;", "setAverage off;", "offset 0;", "value uniform %g;" % K_IN]
        w_in = ["type timeVaryingMappedFixedValue;", "setAverage off;", "offset 0;", "value uniform %g;" % OMEGA_IN]
    else:
        u_in = ["type fixedValue;", "value uniform (%g 0 0);" % U_B]
        k_in = ["type fixedValue;", "value uniform %g;" % K_IN]
        w_in = ["type fixedValue;", "value uniform %g;" % OMEGA_IN]
    walls = ["floor", "roof"] + cube_faces
    def per(default, special):
        out = [("inlet", special.get("inlet", default)), ("outlet", special.get("outlet", default)),
               ("symmetry", ["type symmetryPlane;"]), ("side", special.get("side", default))]
        for w in walls:
            out.append((w, special.get(w, special.get("wall", default))))
        return out
    zg = ["type zeroGradient;"]
    U = field("volVectorField", "U", "[0 1 -1 0 0 0 0]", "uniform (%g 0 0)" % U_B,
              per(["type noSlip;"], {"inlet": u_in, "outlet": ["type inletOutlet;", "inletValue uniform (0 0 0);", "value uniform (%g 0 0);" % U_B],
                                    "side": ["type slip;"]}), "0/air")
    if conjugate:
        cube_T = ["type compressible::turbulentTemperatureRadCoupledMixed;", "Tnbr T;", "kappaMethod fluidThermo;",
                  "qrNbr none;", "qr none;", "value uniform %g;" % T_IN]
    else:
        cube_T = ["type fixedValue;", "value uniform %g;" % t_surf]
    spec_T = {"inlet": ["type fixedValue;", "value uniform %g;" % T_IN],
              "outlet": ["type inletOutlet;", "inletValue uniform %g;" % T_IN, "value uniform %g;" % T_IN],
              "side": zg, "floor": zg, "roof": zg}
    for f in cube_faces:
        spec_T[f] = cube_T
    T = field("volScalarField", "T", "[0 0 0 1 0 0 0]", "uniform %g" % T_IN, per(zg, spec_T), "0/air")
    p = field("volScalarField", "p", "[1 -1 -2 0 0 0 0]", "uniform %g" % P_ABS,
              per(["type calculated;", "value uniform %g;" % P_ABS], {}), "0/air")
    p_rgh = field("volScalarField", "p_rgh", "[1 -1 -2 0 0 0 0]", "uniform %g" % P_ABS,
                  per(["type fixedFluxPressure;", "value uniform %g;" % P_ABS],
                      {"outlet": ["type fixedValue;", "value uniform %g;" % P_ABS], "side": zg}), "0/air")
    alphat_wall = ["type compressible::alphatWallFunction;", "Prt %g;" % prt, "value uniform 0;"]
    alphat = field("volScalarField", "alphat", "[1 -1 -1 0 0 0 0]", "uniform 0",
                   per(["type calculated;", "value uniform 0;"], {"wall": alphat_wall}), "0/air")
    nut = field("volScalarField", "nut", "[0 2 -1 0 0 0 0]", "uniform 0",
                per(["type calculated;", "value uniform 0;"], {"wall": ["type nutLowReWallFunction;", "value uniform 0;"]}), "0/air")
    k = field("volScalarField", "k", "[0 2 -2 0 0 0 0]", "uniform %g" % K_IN,
              per(zg, {"inlet": k_in, "outlet": ["type inletOutlet;", "inletValue uniform %g;" % K_IN, "value uniform %g;" % K_IN],
                       "wall": ["type fixedValue;", "value uniform 0;"]}), "0/air")
    omega = field("volScalarField", "omega", "[0 0 -1 0 0 0 0]", "uniform %g" % OMEGA_IN,
                  per(zg, {"inlet": w_in, "outlet": ["type inletOutlet;", "inletValue uniform %g;" % OMEGA_IN, "value uniform %g;" % OMEGA_IN],
                           "wall": ["type omegaWallFunction;", "blended true;", "value uniform %g;" % OMEGA_IN]}), "0/air")
    out = {"U": U, "T": T, "p": p, "p_rgh": p_rgh, "alphat": alphat}
    if not laminar:
        out.update({"nut": nut, "k": k, "omega": omega})
    return out


def epoxy_fields(cube_faces):
    entries = [("core", ["type fixedValue;", "value uniform %g;" % T_CORE]),
               ("cube_bottom", ["type zeroGradient;"]),
               ("symmetry", ["type symmetryPlane;"])]
    for f in cube_faces:
        entries.append((f, ["type compressible::turbulentTemperatureRadCoupledMixed;", "Tnbr T;",
                            "kappaMethod solidThermo;", "qrNbr none;", "qr none;", "value uniform %g;" % T_CORE]))
    T = field("volScalarField", "T", "[0 0 0 1 0 0 0]", "uniform %g" % T_CORE, entries, "0/epoxy")
    p = field("volScalarField", "p", "[1 -1 -2 0 0 0 0]", "uniform %g" % P_ABS,
              [(n, ["type symmetryPlane;"] if n == "symmetry" else ["type calculated;", "value uniform %g;" % P_ABS])
               for n, _ in entries], "0/epoxy")
    return {"T": T, "p": p}


# ---------------- the precursor X_2d ----------------------------------------
def block_mesh_2d():
    gy = grade_two_sided(X2D_FIRST, X2D_NY, D_CH)
    return (hdr("dictionary", "blockMeshDict") + "scale 1;\nvertices\n(\n"
            "    (0 0 0) (%g 0 0) (%g %g 0) (0 %g 0)\n    (0 0 0.001) (%g 0 0.001) (%g %g 0.001) (0 %g 0.001)\n);\n"
            "blocks ( hex (0 1 2 3 4 5 6 7) (%d %d 1) simpleGrading (1 %s 1) );\nedges ();\n"
            "boundary\n(\n    inlet { type patch; faces ((0 4 7 3)); }\n    outlet { type patch; faces ((1 2 6 5)); }\n"
            "    floor { type wall; faces ((0 1 5 4)); }\n    roof { type wall; faces ((3 7 6 2)); }\n"
            "    frontAndBack { type empty; faces ((0 3 2 1) (4 5 6 7)); }\n);\nmergePatchPairs ();\n"
            % (X2D_LEN, X2D_LEN, D_CH, D_CH, X2D_LEN, X2D_LEN, D_CH, D_CH, X2D_NX, X2D_NY, gy))


def x2d_fields():
    def per(default, special):
        return [("inlet", special.get("inlet", default)), ("outlet", special.get("outlet", default)),
                ("floor", special.get("wall", default)), ("roof", special.get("wall", default)),
                ("frontAndBack", ["type empty;"])]
    zg = ["type zeroGradient;"]
    return {
        "U": field("volVectorField", "U", "[0 1 -1 0 0 0 0]", "uniform (%g 0 0)" % U_B,
                   per(["type noSlip;"], {"inlet": ["type fixedValue;", "value uniform (%g 0 0);" % U_B],
                                          "outlet": ["type inletOutlet;", "inletValue uniform (0 0 0);", "value uniform (%g 0 0);" % U_B]}), "0"),
        "p": field("volScalarField", "p", "[0 2 -2 0 0 0 0]", "uniform 0",
                   per(zg, {"outlet": ["type fixedValue;", "value uniform 0;"]}), "0"),
        "nut": field("volScalarField", "nut", "[0 2 -1 0 0 0 0]", "uniform 0",
                     per(["type calculated;", "value uniform 0;"], {"wall": ["type nutLowReWallFunction;", "value uniform 0;"]}), "0"),
        "k": field("volScalarField", "k", "[0 2 -2 0 0 0 0]", "uniform %g" % K_IN,
                   per(zg, {"inlet": ["type fixedValue;", "value uniform %g;" % K_IN],
                            "outlet": ["type inletOutlet;", "inletValue uniform %g;" % K_IN, "value uniform %g;" % K_IN],
                            "wall": ["type fixedValue;", "value uniform 0;"]}), "0"),
        "omega": field("volScalarField", "omega", "[0 0 -1 0 0 0 0]", "uniform %g" % OMEGA_IN,
                       per(zg, {"inlet": ["type fixedValue;", "value uniform %g;" % OMEGA_IN],
                                "outlet": ["type inletOutlet;", "inletValue uniform %g;" % OMEGA_IN, "value uniform %g;" % OMEGA_IN],
                                "wall": ["type omegaWallFunction;", "blended true;", "value uniform %g;" % OMEGA_IN]}), "0"),
    }


def x2d_dicts():
    return {
        "system/fvSchemes": (hdr("dictionary", "fvSchemes") + "ddtSchemes { default steadyState; }\ngradSchemes { default Gauss linear; }\n"
                             "divSchemes\n{\n    default none;\n    div(phi,U) bounded Gauss linearUpwind grad(U);\n"
                             "    div(phi,k) bounded Gauss linearUpwind grad(k);\n    div(phi,omega) bounded Gauss linearUpwind grad(omega);\n"
                             "    div((nuEff*dev2(T(grad(U))))) Gauss linear;\n}\nlaplacianSchemes { default Gauss linear corrected; }\n"
                             "interpolationSchemes { default linear; }\nsnGradSchemes { default corrected; }\nwallDist { method meshWave; }\n"),
        "system/fvSolution": (hdr("dictionary", "fvSolution") + "solvers\n{\n    p { solver GAMG; smoother GaussSeidel; tolerance 1e-8; relTol 0.01; }\n"
                              "    \"(U|k|omega)\" { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0.05; }\n}\n"
                              "SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; }\n"
                              "relaxationFactors { equations { U 0.9; k 0.9; omega 0.9; \".*\" 0.9; } fields { p 0.9; } }\n"),
        "constant/transportProperties": hdr("dictionary", "transportProperties", "constant") + "transportModel Newtonian;\nnu %.6g;\n" % NU,
        "constant/turbulenceProperties": hdr("dictionary", "turbulenceProperties", "constant") +
                                         "simulationType RAS;\nRAS { RASModel kOmegaSST; turbulence on; printCoeffs on; }\n",
    }


# ---------------- libs: rule 14, verified at EVERY call site ----------------
def install_libs(control_dict):
    """Insert through foam_libs, then RE-READ FROM DISK and raise if absent."""
    try:
        foam_libs.ensure_libs(control_dict, SOLVER_LIB)
    except foam_libs.FoamLibsError as exc:
        refuse("foam_libs.ensure_libs failed on %s: %s" % (control_dict, exc))
    # THE CALL-SITE CHECK (rule 14).  A raise, never `assert` (S16.2 / L-332).
    try:
        have = foam_libs.assert_libs(control_dict, SOLVER_LIB)
    except foam_libs.FoamLibsError as exc:
        refuse("libs NOT VERIFIED on disk after insertion in %s: %s" % (control_dict, exc))
    if SOLVER_LIB not in have:
        refuse("libs read-back from %s lacks %s" % (control_dict, SOLVER_LIB))
    return have


# ---------------- meshing ---------------------------------------------------
def foam(cmd, case, log):
    full = "source %s >/dev/null 2>&1; cd %s && %s > %s 2>&1" % (FOAM_BASHRC, case, cmd, log)
    r = subprocess.run(["bash", "-c", full])
    if r.returncode != 0:
        refuse("%s failed in %s (rc %d); see %s" % (cmd.split()[0], case, r.returncode, log))


def numeric_time_dirs(case):
    return [d for d in os.listdir(case) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and d != "0"]


def prepare_dir(case, force):
    if os.path.isdir(case):
        if numeric_time_dirs(case) or os.path.exists(os.path.join(case, "log.solve")):
            refuse("%s carries solver output (time dirs or log.solve): a built-over run is destroyed evidence" % case)
        if not force:
            refuse("%s exists; pass --force to rebuild an UNRUN case" % case)
        shutil.rmtree(case)
    os.makedirs(case)


CASES = {
    # name: (level, laminar, prt, interface_scheme, conjugate, nProcs_registered, model_b_core_h)
    "T5_CUBE_c": (0, False, PRT_DEFAULT, "harmonic", True, 1, 0.76),
    "T5_CUBE_m": (1, False, PRT_DEFAULT, "harmonic", True, 1, 8.84),
    "T5_CUBE_f": (2, False, PRT_DEFAULT, "harmonic", True, 1, 38.47),
    "P_m": (1, False, PRT_ARM, "harmonic", True, 1, 8.84),
    "L_m": (1, True, PRT_DEFAULT, "harmonic", True, 1, 6.19),
    "S_m": (1, False, PRT_DEFAULT, "harmonic", False, 1, 8.15),
    "H_c": (0, False, PRT_DEFAULT, "linear", True, 1, 0.76),
}
CUBE_FACES = ["cube_front", "cube_top", "cube_rear", "cube_side_n"]


def build_cube_case(root, name, force, mesh=True, inlet_mapped=True, t_surf=None):
    if name not in CASES:
        refuse("unregistered case '%s'; registered: %s" % (name, " ".join(CASES)))
    lvl, laminar, prt, scheme, conjugate, nprocs, mb = CASES[name]
    if not conjugate and t_surf is None:
        refuse("%s (constant-T arm) needs --s-m-tsurf = area-averaged conjugate surface T from T5_CUBE_m (S8 DS); "
               "it is not built before T5_CUBE_m has run" % name)
    case = os.path.join(root, name)
    prepare_dir(case, force)
    regions = ["air"] + (["epoxy"] if conjugate else [])
    write(os.path.join(case, "system/blockMeshDict"), block_mesh_3d(lvl))
    write(os.path.join(case, "system/topoSetDict"), topo_set_dict())
    write(os.path.join(case, "system/controlDict"), control_dict(name, "chtMultiRegionSimpleFoam", regions))
    write(os.path.join(case, "system/fvSolution"), fv_solution_top())
    write(os.path.join(case, "system/fvSchemes"), hdr("dictionary", "fvSchemes") +
          "ddtSchemes { default steadyState; }\ngradSchemes { default Gauss linear; }\ndivSchemes { default none; }\n"
          "laplacianSchemes { default Gauss linear corrected; }\ninterpolationSchemes { default linear; }\nsnGradSchemes { default corrected; }\n")
    write(os.path.join(case, "system/air/fvSchemes"), fv_schemes_air(laminar))
    write(os.path.join(case, "system/air/fvSolution"), fv_solution_air(laminar))
    write(os.path.join(case, "constant/air/thermophysicalProperties"), thermo_air())
    write(os.path.join(case, "constant/air/turbulenceProperties"), turbulence(laminar, prt))
    write(os.path.join(case, "constant/air/g"), g_file("constant/air"))
    write(os.path.join(case, "constant/g"), g_file("constant"))
    write(os.path.join(case, "constant/air/radiationProperties"), hdr("dictionary", "radiationProperties", "constant/air") + "radiation off;\nradiationModel none;\n")
    if conjugate:
        write(os.path.join(case, "system/epoxy/fvSchemes"), fv_schemes_epoxy(scheme))
        write(os.path.join(case, "system/epoxy/fvSolution"), fv_solution_epoxy())
        write(os.path.join(case, "constant/epoxy/thermophysicalProperties"), thermo_epoxy())
        write(os.path.join(case, "constant/epoxy/g"), g_file("constant/epoxy"))
        write(os.path.join(case, "constant/epoxy/radiationProperties"), hdr("dictionary", "radiationProperties", "constant/epoxy") + "radiation off;\nradiationModel none;\n")
        for f, txt in epoxy_fields(CUBE_FACES).items():
            write(os.path.join(case, "0.orig/epoxy", f), txt)
    write(os.path.join(case, "constant/regionProperties"), region_properties(regions))
    write(os.path.join(case, "system/decomposeParDict"), hdr("dictionary", "decomposeParDict") + "numberOfSubdomains %d;\nmethod scotch;\n" % nprocs)
    for f, txt in air_fields(conjugate, laminar, prt, inlet_mapped, CUBE_FACES, t_surf).items():
        write(os.path.join(case, "0.orig/air", f), txt)
    install_libs(os.path.join(case, "system/controlDict"))
    nx, ny, nz = counts(lvl)
    with open(os.path.join(case, "CASE.txt"), "w") as fh:
        fh.write("case=%s\nlevel=%s\nregistration=T5_PREREGISTRATION.md@0fcbb92e\nsolver=chtMultiRegionSimpleFoam\n"
                 "laminar=%s\nPrt=%g\nsolid_laplacian=Gauss %s corrected\nconjugate=%s\nregistered_nProcs=%d\n"
                 "model_B_core_h=%g\nper_case_guard_core_min_3xModelB=%.1f\nR=%g\nfirst_layer_m=%.6g\n"
                 "block_counts_x=%s\nblock_counts_y=%s\nblock_counts_z=%s\n"
                 "NOTE=half domain (S5.2): patch cube_side_s does not exist; the comparator's YPLUS_WALLS names it (finding, see LAUNCH_RECORD.md)\n"
                 "inlet=%s\n"
                 % (name, "cmf"[lvl], laminar, prt, scheme, conjugate, nprocs, mb, 3 * mb * 60, R,
                    FIRST_LAYER_C / R ** lvl, nx, ny, nz,
                    "timeVaryingMappedFixedValue from constant/boundaryData/inlet (X_2d precursor, S5.3)" if inlet_mapped else "uniform"))
    if mesh:
        foam("blockMesh", case, "log.blockMesh")
        foam("topoSet", case, "log.topoSet")
        foam("splitMeshRegions -cellZonesOnly -useFaceZones -overwrite", case, "log.splitMeshRegions")
        if conjugate:
            rename_interface_patches(case)
        else:
            strip_solid_region(case)
        foam("checkMesh -allRegions -allTopology -allGeometry", case, "log.checkMesh")
        # the epoxy region gets no turbulence: drop the split-copied dictionaries it must not carry
        for junk in ("constant/epoxy/turbulenceProperties", "0/air", "0/epoxy", "0", "postProcessing"):
            pth = os.path.join(case, junk)
            if os.path.isdir(pth):
                shutil.rmtree(pth)
            elif os.path.isfile(pth):
                os.unlink(pth)
    return case


def rename_interface_patches(case):
    """splitMeshRegions names the interface `<zone>_air_to_epoxy` / `<zone>_epoxy_to_air`.
    The comparator's YPLUS_WALLS are the bare zone names, so both regions' boundary
    files are rewritten to `<zone>` and every mappedWall `samplePatch` follows.
    Verified by re-reading the bytes on disk; a name left behind is a refusal."""
    for reg, suffix, other_suffix in (("air", "_air_to_epoxy", "_epoxy_to_air"),
                                      ("epoxy", "_epoxy_to_air", "_air_to_epoxy")):
        b = os.path.join(case, "constant", reg, "polyMesh", "boundary")
        txt = open(b).read()
        for f in CUBE_FACES:
            txt = txt.replace(f + suffix, f).replace(f + other_suffix, f)
        open(b, "w").write(txt)
        back = open(b).read()
        for f in CUBE_FACES:
            if not re.search(r"^\s*%s\s*$" % re.escape(f), back, re.M):
                refuse("%s: patch %s absent after the interface rename" % (b, f))
            if (f + suffix) in back or (f + other_suffix) in back:
                refuse("%s: an un-renamed interface patch name survives for %s" % (b, f))


def strip_solid_region(case):
    """AMENDMENT 9: the S8 `DS` constant-`T` arm `S_m` is FLUID ONLY.

    `splitMeshRegions` has just cut the SAME two regions the conjugate cases
    use, so the epoxy CELLS are already absent from `constant/air/polyMesh`.
    This removes the solid region that was cut beside it and turns the four
    air-side interface patches into plain walls, so the cube surface carries
    the registered `fixedValue` `T` (`air_fields`'s existing non-conjugate
    branch, unchanged) instead of a coupled condition.

    Nothing else about the mesh moves: the same `blockMeshDict`, the same
    `topoSet` faceZones, the same split, the same cell count on the fluid
    side, and the same four patch NAMES the comparator's `YPLUS_WALLS` reads.
    Verified by re-reading the bytes on disk; a surviving `mappedWall`, a
    surviving sampling keyword, an un-renamed interface name or a surviving
    epoxy region is a refusal, not a warning."""
    b = os.path.join(case, "constant", "air", "polyMesh", "boundary")
    txt = open(b).read()
    for f in CUBE_FACES:
        txt = txt.replace(f + "_air_to_epoxy", f)
    # de-couple: inside a cube patch block only, mappedWall -> wall and the
    # sampling keywords go, because they name a neighbour region that is gone.
    DROP = ("sampleMode", "sampleRegion", "samplePatch", "offsetMode", "offset")
    out, cur = [], None
    for ln in txt.splitlines(True):
        s = ln.strip()
        if s in CUBE_FACES:
            cur = s
        elif cur is not None and s == "}":
            cur = None
        if cur is not None:
            w = s.split()
            if w[:2] == ["type", "mappedWall;"]:
                ln = ln.replace("mappedWall", "wall")
            elif w and w[0] in DROP:
                continue
        out.append(ln)
    open(b, "w").write("".join(out))
    for gone in ("constant/epoxy", "system/epoxy", "0.orig/epoxy", "0/epoxy",
                 "constant/cellToRegion", "constant/air/cellToRegion"):
        p = os.path.join(case, gone)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.isfile(p):
            os.unlink(p)
    write(os.path.join(case, "constant/regionProperties"), region_properties(["air"]))
    back = open(b).read()
    for f in CUBE_FACES:
        if not re.search(r"^\s*%s\s*$" % re.escape(f), back, re.M):
            refuse("%s: patch %s absent after the fluid-only strip" % (b, f))
        if (f + "_air_to_epoxy") in back:
            refuse("%s: an un-renamed interface patch name survives for %s" % (b, f))
    if "mappedWall" in back:
        refuse("%s: a mappedWall patch survives on the fluid-only arm" % b)
    for kw in ("sampleMode", "sampleRegion", "samplePatch"):
        if kw in back:
            refuse("%s: the sampling keyword %s survives on the fluid-only arm" % (b, kw))
    if os.path.exists(os.path.join(case, "constant", "epoxy")):
        refuse("%s: the epoxy region survives on the fluid-only arm" % case)


def build_x2d(root, force, mesh=True):
    case = os.path.join(root, "X_2d")
    prepare_dir(case, force)
    write(os.path.join(case, "system/blockMeshDict"), block_mesh_2d())
    write(os.path.join(case, "system/controlDict"), control_dict("X_2d", "simpleFoam", []))
    for p, t in x2d_dicts().items():
        write(os.path.join(case, p), t)
    for f, t in x2d_fields().items():
        write(os.path.join(case, "0.orig", f), t)
    install_libs(os.path.join(case, "system/controlDict"))
    with open(os.path.join(case, "CASE.txt"), "w") as fh:
        fh.write("case=X_2d\nrole=precursor inflow (S5.3), touches no h\nsolver=simpleFoam\nregistration=T5_PREREGISTRATION.md@0fcbb92e\n"
                 "registered_nProcs=1\nmodel_B_core_h=0.44\nper_case_guard_core_min_3xModelB=79.2\nnx=%d\nny=%d\nfirst_layer_m=%g\nlength_m=%g\n"
                 % (X2D_NX, X2D_NY, X2D_FIRST, X2D_LEN))
    if mesh:
        foam("blockMesh", case, "log.blockMesh")
        foam("checkMesh -allTopology -allGeometry", case, "log.checkMesh")
    return case


# ---------------- selftest: refusals DRIVEN under both interpreters ---------
def selftest():
    import tempfile
    fails = []
    tmp = tempfile.mkdtemp(prefix="t5_build_")
    me = os.path.abspath(__file__)
    def run(args):
        return subprocess.run([sys.executable, me] + args, capture_output=True, text=True)
    # arm 1: unregistered case name refuses
    p = run(["--root", tmp, "--case", "T5_CUBE_x", "--no-mesh"])
    (fails if not (p.returncode == 2 and "unregistered" in p.stderr) else []).append("unregistered case did not refuse")
    # arm 2: build over a case carrying a time dir refuses
    os.makedirs(os.path.join(tmp, "T5_CUBE_c", "1000"))
    p = run(["--root", tmp, "--case", "T5_CUBE_c", "--no-mesh", "--force"])
    (fails if not (p.returncode == 2 and "solver output" in p.stderr) else []).append("build over a run case did not refuse")
    shutil.rmtree(os.path.join(tmp, "T5_CUBE_c"))
    # arm 3: S_m without its parameter refuses
    p = run(["--root", tmp, "--case", "S_m", "--no-mesh"])
    (fails if not (p.returncode == 2 and "s-m-tsurf" in p.stderr) else []).append("S_m without T_surf did not refuse")
    # arm 4: dictionaries write (no mesh) and the libs call-site check passes
    p = run(["--root", tmp, "--case", "H_c", "--no-mesh"])
    (fails if p.returncode != 0 else []).append("H_c dictionary write failed: %s" % p.stderr[-300:])
    # arm 5: MUTATION -- strip the libs entry and require the call-site check to FIRE, under -O too
    cd = os.path.join(tmp, "H_c", "system", "controlDict")
    if os.path.isfile(cd):
        txt = open(cd).read()
        rcs = {}
        for tag, argv in (("python3", [sys.executable]), ("python3 -O", [sys.executable, "-O"])):
            q = subprocess.run(argv + [me, "--drive-libs-mutation", cd], capture_output=True, text=True)
            rcs[tag] = (q.returncode, "NOT VERIFIED" in q.stderr or "lacks" in q.stderr)
        if not all(v == (2, True) for v in rcs.values()):
            fails.append("libs call-site check did not fire under both interpreters: %r" % rcs)
        open(cd, "w").write(txt)
    # arm 6: the grading arithmetic reproduces the block length
    q = growth_ratio(FIRST_LAYER_C, 14, 0.25 * L_UP)
    s = FIRST_LAYER_C * (q ** 14 - 1) / (q - 1)
    (fails if abs(s - 0.25 * L_UP) > 1e-9 else []).append("growth_ratio does not close the length")
    shutil.rmtree(tmp, ignore_errors=True)
    for f in fails:
        print("FAILED: " + f)
    print("SELFTEST %s: 6 arms, %d FAILED (interpreter %s)" % ("PASS" if not fails else "FAIL", len(fails),
                                                                "-O" if not __debug__ else "plain"))
    return 1 if fails else 0


def _drive_libs_mutation(cd):
    """Simulate foam_libs succeeding while the disk holds no libs: the call-site check must refuse."""
    txt = open(cd).read()
    txt2 = re.sub(r"^libs\s*\([^)]*\)\s*;\s*$", "", txt, flags=re.M)
    open(cd, "w").write(txt2)
    foam_libs.ensure_libs = lambda *a, **k: [SOLVER_LIB]     # the insertion "succeeds" but writes nothing
    install_libs(cd)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--case", action="append", default=[], help="X_2d or a registered cube case; repeatable")
    ap.add_argument("--all-armable", action="store_true", help="X_2d T5_CUBE_c H_c T5_CUBE_m T5_CUBE_f P_m L_m")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-mesh", action="store_true")
    ap.add_argument("--uniform-inlet", action="store_true", help="scratch/smoke only: uniform inlet instead of the precursor map")
    ap.add_argument("--s-m-tsurf", type=float)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--drive-libs-mutation")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.drive_libs_mutation:
        return _drive_libs_mutation(a.drive_libs_mutation)
    names = list(a.case)
    if a.all_armable:
        names = ["X_2d", "T5_CUBE_c", "H_c", "T5_CUBE_m", "T5_CUBE_f", "P_m", "L_m"]
    if not names:
        ap.print_help()
        return 0
    for n in names:
        if n == "X_2d":
            c = build_x2d(a.root, a.force, mesh=not a.no_mesh)
        else:
            c = build_cube_case(a.root, n, a.force, mesh=not a.no_mesh,
                                inlet_mapped=not a.uniform_inlet, t_surf=a.s_m_tsurf)
        print("built " + c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
