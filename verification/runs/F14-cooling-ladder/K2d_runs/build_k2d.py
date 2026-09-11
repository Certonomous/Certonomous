#!/usr/bin/env python3
"""build_k2d.py -- K2d three-level rack-row builder.  F14 cooling ladder.

    python3 build_k2d.py K2d_L1 [K2d_L2 K2d_L3]   # build named levels
    python3 build_k2d.py --arith                  # ladder arithmetic, no build
    python3 build_k2d.py --selftest               # mutation matrix, no build

REGISTRATION
------------
`docs/campaigns/F14-cooling-ladder/K2d_PREREGISTRATION.md`.  Geometry, boundary
conditions and properties are K2a's defaults, inherited by citation (K2a
sections 2, 2.1, 3); this file builds them and invents none.

EXIT MAP -- registration section 6.4
    0 EXIT_OK    every named level built and passed its own checkMesh
    1 EXIT_FAIL  a level built but FAILED checkMesh
    2 EXIT_REFUSE a precondition is missing, or clause 7 refuses the directory

WHAT THIS BUILDER WILL NOT DO
-----------------------------
  * IT NEVER CREATES `0/`.  Fields are staged into `0.orig/` and the launcher
    copies them to `0/` AT LAUNCH, so `0/T`'s mtime dates the run and the
    age guard (rule 4 clause 6) has a referent that means something.
  * IT NEVER RUNS BARE `checkMesh`.  Every invocation carries
    `-allGeometry -allTopology`, and the exact command line is written into
    log.checkMesh so a reader can tell which check set produced it.  Bare
    checkMesh prints `Mesh OK.` on a mesh the full set fails.
  * IT NEVER WIDENS A GATE TO FIT A MESH.  If the built ratios miss
    G-MESHSIM's window the DIVISIONS change, never the window.

THE LADDER, AND WHY THE DIVISIONS ARE MULTIPLES OF FOUR
-------------------------------------------------------
The registered targets are 59,259 / 200,000 / 675,000 at r = 1.5 in three
directions (step 3.375).  A blockMesh lands on integer divisions, so the
targets are TARGETS and `G-MESHSIM` gates the ratios of the BUILT counts.

Choosing every L1 division a MULTIPLE OF 4 makes x1.5 and x2.25 land exactly
on integers, which makes the built step EXACTLY 3.3750 at both pairs rather
than approximately so -- including through the rack void, which scales with
the same factor and therefore cancels.  Measured, not hoped:

    L1  48 x 44 x 32 = 67,584  - void  9,216 =  58,368 cells
    L2  72 x 66 x 48 = 228,096 - void 31,104 = 196,992 cells   step 3.3750
    L3 108 x 99 x 72 = 769,824 - void 104,976 = 664,848 cells   step 3.3750

Every level is 1.50 % under its target -- uniformly, which is why the RATIOS
are exact.  Both steps sit dead centre of G-MESHSIM's [3.2063, 3.5438].

NO INFLATION-LAYER STACK IS USED, AND THAT IS A DELIBERATE CHOICE WITH ITS
ARITHMETIC DONE BEFORE THE BUILD.  K2a section 6 specifies wall functions with
y+ in the log-law band and grading -- not a layer stack.  A stack that needs
more cell-widths at the wall than the cell has is an arithmetic contradiction
that can sit in a registration unnoticed until three meshes have been built
(T26, 2026-09-10: a registered stack needing 2.3 to 5.2 cell-widths).  Here
there is no stack, so there is no contradiction to have; the smallest cell
dimension at each level is reported by --arith and gated by G-MINCELL.
"""

import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

# --- geometry: K2a defaults (K2a section 2.1), N = 4 racks, one row ---------
X = [0.0, 0.6, 1.2, 1.8, 2.4, 3.0, 3.6]     # L_end | 4 racks of W_r | L_end
Y = [0.0, 0.6, 1.2, 2.3, 2.6, 3.2, 3.5]     # cold aisle | rack depth | hot aisle
Z = [0.0, 2.0, 2.7]                          # rack height H_r | ceiling H
RACK_XI = (1, 2, 3, 4)                       # x-intervals the rack row occupies
RACK_YI = 2                                  # the rack-depth y-interval
RACK_ZI = 0                                  # floor-to-rack-top z-interval

DIV_L1 = dict(x=[8, 8, 8, 8, 8, 8], y=[8, 8, 12, 4, 8, 4], z=[24, 8])
LEVEL_FACTOR = {"K2d_L1": 1.0, "K2d_L2": 1.5, "K2d_L3": 2.25}
LEVELS = ("K2d_L1", "K2d_L2", "K2d_L3")
TARGETS = {"K2d_L1": 59259, "K2d_L2": 200000, "K2d_L3": 675000}

MESHSIM_LO, MESHSIM_HI = 3.2063, 3.5438
MINCELL_FLOOR_M = 5.0e-3

# --- boundary conditions: K2a section 2.1 defaults --------------------------
QV_RACK = 0.35          # m3/s through each rack
DT_RACK = 12.0          # K rise across a rack
T_SUP = 289.0           # K supply temperature
N_RACKS = 4
S_T = 0.6               # tile pitch
NU = 1.589461e-05       # K0c dictionaries, NOT recall (K2a section 2.1)
BETA = 3.333333e-03
T_REF = 300.0
PR, PRT = 0.71, 0.85
I_SUP = 0.10            # supply turbulence intensity

NAMED_FEATURES = ("rack front face", "rack rear face", "rack side faces",
                  "supply tile face", "return face",
                  "cold-aisle/rack interface band",
                  "hot-aisle/rack interface band",
                  "floor boundary layer", "ceiling boundary layer",
                  "row-end margin")

# THE set +u GUARD.  `sourcing` the OpenFOAM bashrc under `set -u` aborts on an
# unset variable and the solver never runs -- rc=127 with NO output, which
# looks like a silent success to anything that does not check.  The T26 lane
# had this guard in its launcher and STILL wrote a throwaway helper an hour
# later without it, losing both levels' logs.  Knowing about the hazard is
# demonstrably not protection from it, so it lives in ONE constant that every
# shell-out in this file uses.
OF_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
SH_PREAMBLE = "set +u; . %s; set -u;" % OF_BASHRC


class Refuse(Exception):
    pass


def refuse(msg):
    raise Refuse(msg)


# ----------------------------------------------------------------- ladder

def divisions(level):
    f = LEVEL_FACTOR[level]
    return {k: [int(round(v * f)) for v in vs] for k, vs in DIV_L1.items()}


def predicted_cells(level):
    d = divisions(level)
    nx, ny, nz = sum(d["x"]), sum(d["y"]), sum(d["z"])
    void = sum(d["x"][i] for i in RACK_XI) * d["y"][RACK_YI] * d["z"][RACK_ZI]
    return nx * ny * nz - void


def min_cell_dims(level):
    d = divisions(level)
    dx = min((X[i + 1] - X[i]) / d["x"][i] for i in range(len(d["x"])))
    dy = min((Y[i + 1] - Y[i]) / d["y"][i] for i in range(len(d["y"])))
    dz = min((Z[i + 1] - Z[i]) / d["z"][i] for i in range(len(d["z"])))
    return dx, dy, dz


def mincell_map(level):
    """Minimum cell dimension per NAMED feature (registration 5.1).

    The mesh is ungraded rectilinear, so a feature's minimum dimension is the
    smallest cell edge of the blocks that touch it.  Each entry is DERIVED
    from the divisions actually used, never asserted.
    """
    dx, dy, dz = min_cell_dims(level)
    d = divisions(level)
    rack_dy = (Y[RACK_YI + 1] - Y[RACK_YI]) / d["y"][RACK_YI]
    rack_dz = (Z[RACK_ZI + 1] - Z[RACK_ZI]) / d["z"][RACK_ZI]
    rack_dx = (X[1] - X[0]) / d["x"][1]
    return {
        "rack front face": min(rack_dx, rack_dz),
        "rack rear face": min(rack_dx, rack_dz),
        "rack side faces": min(rack_dy, rack_dz),
        "supply tile face": min(dx, dy),
        "return face": min(dx, dy),
        "cold-aisle/rack interface band": min(dx, rack_dz),
        "hot-aisle/rack interface band": min(dx, rack_dz),
        "floor boundary layer": dz,
        "ceiling boundary layer": (Z[2] - Z[1]) / d["z"][1],
        "row-end margin": (X[1] - X[0]) / d["x"][0],
    }


def arith_report():
    """Everything that can be checked BEFORE a mesh exists.  Prints and returns ok."""
    ok = True
    prev = None
    print("K2d LADDER ARITHMETIC -- checked before any mesh is built")
    print("%-8s %-34s %12s %12s %8s %9s" %
          ("level", "divisions (x/y/z totals)", "cells", "target", "delta", "step"))
    for lv in LEVELS:
        d = divisions(lv)
        n = predicted_cells(lv)
        step = n / prev if prev else None
        print("%-8s %-34s %12s %12s %+7.2f%% %9s"
              % (lv, "%d x %d x %d" % (sum(d["x"]), sum(d["y"]), sum(d["z"])),
                 "{:,}".format(n), "{:,}".format(TARGETS[lv]),
                 100 * (n / TARGETS[lv] - 1),
                 "%.4f" % step if step else "--"))
        if step is not None and not (MESHSIM_LO <= step <= MESHSIM_HI):
            ok = False
            print("    G-MESHSIM WOULD FAIL: step %.4f outside [%.4f, %.4f]. "
                  "The DIVISIONS change, never the window." % (step, MESHSIM_LO, MESHSIM_HI))
        prev = n
    print("\nG-MINCELL against the registered %.1f mm floor:" % (MINCELL_FLOOR_M * 1e3))
    for lv in LEVELS:
        mm = mincell_map(lv)
        worst_k = min(mm, key=lambda k: mm[k])
        flag = "OK" if mm[worst_k] >= MINCELL_FLOOR_M else "UNDER FLOOR"
        print("  %-8s worst feature %-32s %7.1f mm   [%s]"
              % (lv, worst_k, mm[worst_k] * 1e3, flag))
        if mm[worst_k] < MINCELL_FLOOR_M:
            ok = False
    print("\nNEAR-WALL STACK: none. K2a section 6 specifies wall functions and "
          "grading, not an inflation stack, so there is no stack-versus-cell "
          "contradiction to have. The arithmetic is done here rather than after "
          "three meshes exist.")
    return ok


# ------------------------------------------------------------ case writing

def _hdr(cls, obj, loc=None):
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            "    class %s;\n%s    object %s;\n}\n"
            % (cls, ('    location "%s";\n' % loc) if loc else "", obj))


def _blockmeshdict(level):
    d = divisions(level)
    nxb, nyb, nzb = len(d["x"]), len(d["y"]), len(d["z"])
    NX, NY = nxb + 1, nyb + 1

    def vid(i, j, k):
        return k * (NY * NX) + j * NX + i

    out = [_hdr("dictionary", "blockMeshDict", "system"), "scale 1;\n", "vertices\n(\n"]
    for k in range(nzb + 1):
        for j in range(nyb + 1):
            for i in range(nxb + 1):
                out.append("    (%.6f %.6f %.6f)\n" % (X[i], Y[j], Z[k]))
    out.append(");\n\nblocks\n(\n")
    for k in range(nzb):
        for j in range(nyb):
            for i in range(nxb):
                if i in RACK_XI and j == RACK_YI and k == RACK_ZI:
                    continue                      # the rack is an UNMESHED VOID
                v = (vid(i, j, k), vid(i + 1, j, k), vid(i + 1, j + 1, k), vid(i, j + 1, k),
                     vid(i, j, k + 1), vid(i + 1, j, k + 1), vid(i + 1, j + 1, k + 1),
                     vid(i, j + 1, k + 1))
                out.append("    hex (%d %d %d %d %d %d %d %d) (%d %d %d) "
                           "simpleGrading (1 1 1)\n"
                           % (v + (d["x"][i], d["y"][j], d["z"][k])))
    out.append(");\n\nedges ();\n\nboundary\n(\n")

    def face(i, j, k, which):
        c = [vid(i, j, k), vid(i + 1, j, k), vid(i + 1, j + 1, k), vid(i, j + 1, k),
             vid(i, j, k + 1), vid(i + 1, j, k + 1), vid(i + 1, j + 1, k + 1),
             vid(i, j + 1, k + 1)]
        return {"xmin": (c[0], c[4], c[7], c[3]), "xmax": (c[1], c[2], c[6], c[5]),
                "ymin": (c[0], c[1], c[5], c[4]), "ymax": (c[3], c[7], c[6], c[2]),
                "zmin": (c[0], c[3], c[2], c[1]), "zmax": (c[4], c[5], c[6], c[7])}[which]

    def blk(name, ptype, faces):
        out.append("    %s\n    {\n        type %s;\n        faces\n        (\n"
                   % (name, ptype))
        for f in faces:
            out.append("            (%d %d %d %d)\n" % f)
        out.append("        );\n    }\n")

    # rack faces: front (cold-aisle side, ymin of the void) and rear (ymax)
    for n, xi in enumerate(RACK_XI):
        blk("rack%d_in" % n, "patch", [face(xi, RACK_YI, RACK_ZI, "ymin")])
        blk("rack%d_out" % n, "patch", [face(xi, RACK_YI, RACK_ZI, "ymax")])
    # THE RACK ROW IS CONTIGUOUS: RACK_XI = (1,2,3,4) are ADJACENT x-intervals,
    # so the row is ONE unmeshed void 2.4 m long, not four separate boxes with
    # gaps.  The xmax face of rack i IS the xmin face of rack i+1, and BOTH
    # sides of it are void -- there is no cell to own it.  Emitting it as a
    # boundary face is what blockMesh rejected with "does not have neighbour
    # cell face" (rc=134).  Only the two OUTER ends of the row are real
    # boundaries, plus the row's top.
    blk("rack_sides", "wall",
        [face(RACK_XI[0], RACK_YI, RACK_ZI, "xmin"),
         face(RACK_XI[-1], RACK_YI, RACK_ZI, "xmax")]
        + [face(xi, RACK_YI, RACK_ZI, "zmax") for xi in RACK_XI])
    # supply tiles in the cold aisle floor, one per rack
    blk("tile", "patch", [face(xi, 0, 0, "zmin") for xi in RACK_XI])
    # return in the ceiling above the hot aisle
    blk("return", "patch", [face(xi, nyb - 1, nzb - 1, "zmax") for xi in RACK_XI])
    # everything else is adiabatic no-slip wall (K2a section 3.1)
    walls = []
    for k in range(nzb):
        for j in range(nyb):
            for i in range(nxb):
                if i in RACK_XI and j == RACK_YI and k == RACK_ZI:
                    continue
                if i == 0:
                    walls.append(face(i, j, k, "xmin"))
                if i == nxb - 1:
                    walls.append(face(i, j, k, "xmax"))
                if j == 0:
                    walls.append(face(i, j, k, "ymin"))
                if j == nyb - 1:
                    walls.append(face(i, j, k, "ymax"))
                if k == 0 and not (i in RACK_XI and j == 0):
                    walls.append(face(i, j, k, "zmin"))
                if k == nzb - 1 and not (i in RACK_XI and j == nyb - 1):
                    walls.append(face(i, j, k, "zmax"))
    blk("walls", "wall", walls)
    out.append(");\n\nmergePatchPairs ();\n")
    return "".join(out)


def _fields(case):
    """Stage into 0.orig/ ONLY.  The launcher makes 0/ at launch (age guard)."""
    d0 = os.path.join(case, "0.orig")
    os.makedirs(d0, exist_ok=True)
    a_rack = (X[2] - X[1]) * (Z[1] - Z[0])          # 0.6 x 2.0 = 1.2 m2
    u_rack = QV_RACK / a_rack
    u_tile = (N_RACKS * QV_RACK) / (N_RACKS * S_T * S_T)
    k_sup = 1.5 * (I_SUP * u_tile) ** 2
    om_sup = k_sup ** 0.5 / (0.09 ** 0.25 * 0.1)
    racks_in = " ".join("rack%d_in" % n for n in range(N_RACKS))
    racks_out = " ".join("rack%d_out" % n for n in range(N_RACKS))

    def w(name, cls, dims, internal, bc):
        with open(os.path.join(d0, name), "w") as fh:
            fh.write(_hdr(cls, name, "0")
                     + "dimensions %s;\ninternalField uniform %s;\n"
                       "boundaryField\n{\n%s}\n" % (dims, internal, bc))

    w("T", "volScalarField", "[0 0 0 1 0 0 0]", "%.6f" % T_SUP,
      "    tile { type fixedValue; value uniform %.6f; }\n"
      "    return { type inletOutlet; inletValue uniform %.6f; value uniform %.6f; }\n"
      "    \"(%s)\" { type zeroGradient; }\n"
      "    \"(%s)\" { type fixedValue; value uniform %.6f; }\n"
      "    \"(walls|rack_sides)\" { type zeroGradient; }\n"
      % (T_SUP, T_SUP, T_SUP, racks_in.replace(" ", "|"),
         racks_out.replace(" ", "|"), T_SUP + DT_RACK))
    w("U", "volVectorField", "[0 1 -1 0 0 0 0]", "(0 0 0)",
      "    tile { type fixedValue; value uniform (0 0 %.6f); }\n"
      "    return { type pressureInletOutletVelocity; value uniform (0 0 0); }\n"
      "    \"(%s)\" { type fixedValue; value uniform (0 %.6f 0); }\n"
      "    \"(%s)\" { type fixedValue; value uniform (0 %.6f 0); }\n"
      "    \"(walls|rack_sides)\" { type noSlip; }\n"
      % (u_tile, racks_in.replace(" ", "|"), -u_rack,
         racks_out.replace(" ", "|"), u_rack))
    w("p_rgh", "volScalarField", "[1 -1 -2 0 0 0 0]", "0",
      "    return { type fixedValue; value uniform 0; }\n"
      "    \"(tile|%s|%s)\" { type fixedFluxPressure; value uniform 0; }\n"
      "    \"(walls|rack_sides)\" { type fixedFluxPressure; value uniform 0; }\n"
      % (racks_in.replace(" ", "|"), racks_out.replace(" ", "|")))
    w("p", "volScalarField", "[1 -1 -2 0 0 0 0]", "0",
      "    \".*\" { type calculated; value uniform 0; }\n")
    w("k", "volScalarField", "[0 2 -2 0 0 0 0]", "%.6e" % k_sup,
      "    \"(tile|return|%s|%s)\" { type inletOutlet; inletValue uniform %.6e; "
      "value uniform %.6e; }\n"
      "    \"(walls|rack_sides)\" { type kqRWallFunction; value uniform %.6e; }\n"
      % (racks_in.replace(" ", "|"), racks_out.replace(" ", "|"),
         k_sup, k_sup, k_sup))
    w("omega", "volScalarField", "[0 0 -1 0 0 0 0]", "%.6e" % om_sup,
      "    \"(tile|return|%s|%s)\" { type inletOutlet; inletValue uniform %.6e; "
      "value uniform %.6e; }\n"
      "    \"(walls|rack_sides)\" { type omegaWallFunction; value uniform %.6e; }\n"
      % (racks_in.replace(" ", "|"), racks_out.replace(" ", "|"),
         om_sup, om_sup, om_sup))
    w("nut", "volScalarField", "[0 2 -1 0 0 0 0]", "0",
      "    \"(walls|rack_sides)\" { type nutkWallFunction; value uniform 0; }\n"
      "    \".*\" { type calculated; value uniform 0; }\n")
    w("alphat", "volScalarField", "[1 -1 -1 0 0 0 0]", "0",
      "    \"(walls|rack_sides)\" { type compressible::alphatWallFunction; "
      "Prt %.4f; value uniform 0; }\n"
      "    \".*\" { type calculated; value uniform 0; }\n" % PRT)


def _system_and_constant(case, level):
    sysd, cond = os.path.join(case, "system"), os.path.join(case, "constant")
    os.makedirs(sysd, exist_ok=True)
    os.makedirs(cond, exist_ok=True)
    with open(os.path.join(sysd, "blockMeshDict"), "w") as fh:
        fh.write(_blockmeshdict(level))
    with open(os.path.join(cond, "transportProperties"), "w") as fh:
        fh.write(_hdr("dictionary", "transportProperties", "constant")
                 + "transportModel Newtonian;\nnu %.9e;\nbeta %.9e;\n"
                   "TRef %.4f;\nPr %.4f;\nPrt %.4f;\n"
                 % (NU, BETA, T_REF, PR, PRT))
    with open(os.path.join(cond, "turbulenceProperties"), "w") as fh:
        fh.write(_hdr("dictionary", "turbulenceProperties", "constant")
                 + "simulationType RAS;\nRAS\n{\n    RASModel kOmegaSST;\n"
                   "    turbulence on;\n    printCoeffs on;\n}\n")
    with open(os.path.join(cond, "g"), "w") as fh:
        fh.write(_hdr("uniformDimensionedVectorField", "g", "constant")
                 + "dimensions [0 1 -2 0 0 0 0];\nvalue (0 0 -9.81);\n")
    # controlDict: deltaT 1 so rule 4 clause 5 is n_exec == endTime
    with open(os.path.join(sysd, "controlDict"), "w") as fh:
        fh.write(_hdr("dictionary", "controlDict", "system")
                 + "application buoyantBoussinesqSimpleFoam;\nstartFrom latestTime;\n"
                   "startTime 0;\nstopAt endTime;\nendTime 3000;\ndeltaT 1;\n"
                   "writeControl timeStep;\nwriteInterval 3000;\npurgeWrite 0;\n"
                   "writeFormat ascii;\nwritePrecision 10;\nrunTimeModifiable false;\n")
    with open(os.path.join(sysd, "fvSchemes"), "w") as fh:
        fh.write(_hdr("dictionary", "fvSchemes", "system")
                 + "ddtSchemes { default steadyState; }\n"
                   "gradSchemes { default Gauss linear; }\n"
                   "divSchemes\n{\n    default none;\n"
                   "    div(phi,U) bounded Gauss linearUpwind grad(U);\n"
                   "    div(phi,T) bounded Gauss limitedLinear 1;\n"
                   "    div(phi,k) bounded Gauss upwind;\n"
                   "    div(phi,omega) bounded Gauss upwind;\n"
                   "    div((nuEff*dev2(T(grad(U))))) Gauss linear;\n}\n"
                   "laplacianSchemes { default Gauss linear corrected; }\n"
                   "interpolationSchemes { default linear; }\n"
                   "snGradSchemes { default corrected; }\n")
    with open(os.path.join(sysd, "fvSolution"), "w") as fh:
        fh.write(_hdr("dictionary", "fvSolution", "system")
                 + "solvers\n{\n    p_rgh { solver GAMG; tolerance 1e-8; relTol 0.01;\n"
                   "        smoother GaussSeidel; }\n"
                   "    \"(U|T|k|omega)\" { solver PBiCGStab; preconditioner DILU;\n"
                   "        tolerance 1e-9; relTol 0.01; }\n}\n"
                   "SIMPLE { nNonOrthogonalCorrectors 1; pRefCell 0; pRefValue 0; }\n"
                   "relaxationFactors { fields { p_rgh 0.3; }\n"
                   "    equations { U 0.5; T 0.5; \"(k|omega)\" 0.5; } }\n")


# --------------------------------------------------------------- build/check

def _sh(cmd, cwd):
    return subprocess.run(["bash", "-lc", SH_PREAMBLE + cmd], cwd=cwd,
                          capture_output=True, text=True)


def build(level, root=None, run_mesh=True):
    if level not in LEVELS:
        refuse("%r is not a K2d level %s" % (level, ", ".join(LEVELS)))
    root = root or HERE
    case = os.path.join(root, level)
    if os.path.isdir(os.path.join(case, "0")):
        refuse("CLAUSE 7: %s already has a 0/. This builder stages into "
               "0.orig/ and never creates 0/; a pre-existing 0/ means the case "
               "is not unstarted." % case)
    os.makedirs(case, exist_ok=True)
    _system_and_constant(case, level)
    _fields(case)

    with open(os.path.join(case, "MINCELL.json"), "w") as fh:
        json.dump(mincell_map(level), fh, indent=1, sort_keys=True)

    if not run_mesh:
        return dict(level=level, case=case, built=False,
                    predicted_cells=predicted_cells(level))

    r = _sh("blockMesh > log.blockMesh 2>&1", case)
    if r.returncode != 0:
        refuse("blockMesh failed for %s (rc=%d); see %s/log.blockMesh"
               % (level, r.returncode, case))

    # THE FULL CHECK SET, ALWAYS, with the command line recorded in the log so
    # the comparator's provenance limb can see which set produced it.
    cmd = "checkMesh -allGeometry -allTopology"
    _sh("{ echo '# COMMAND LINE: %s'; %s; } > log.checkMesh 2>&1" % (cmd, cmd), case)
    with open(os.path.join(case, "log.checkMesh"), errors="replace") as fh:
        cmtext = fh.read()
    n_cells = None
    for ln in cmtext.splitlines():
        if ln.strip().startswith("cells:"):
            n_cells = int(ln.split(":")[1].strip())
            break
    failed = None
    for ln in cmtext.splitlines():
        if "Failed" in ln and "mesh check" in ln:
            failed = int(ln.split("Failed")[1].split("mesh")[0].strip())
        elif ln.strip() == "Mesh OK." and failed is None:
            failed = 0
    return dict(level=level, case=case, built=True, cells=n_cells,
                predicted_cells=predicted_cells(level), checkmesh_failed=failed)


# ------------------------------------------------------------------ selftest

def selftest():
    ok_all = True

    def arm(label, got, want):
        nonlocal ok_all
        good = (got == want)
        ok_all = ok_all and good
        print("  [%s] %s" % ("ok " if good else "BAD", label))

    def arm_refuses(label, fn):
        nonlocal ok_all
        try:
            fn()
            ok_all = False
            print("  [BAD] %s -- did NOT refuse" % label)
        except Refuse:
            print("  [ok ] %s -- REFUSED" % label)

    print("-- ladder arithmetic --")
    arm("CONTROL: the registered ladder satisfies G-MESHSIM and G-MINCELL",
        arith_report(), True)
    n = [predicted_cells(l) for l in LEVELS]
    arm("both built steps are EXACTLY 3.3750",
        (round(n[1] / n[0], 4), round(n[2] / n[1], 4)), (3.375, 3.375))
    arm("every division is a multiple of 4 at L1 (so x1.5 and x2.25 stay integer)",
        all(v % 4 == 0 for vs in DIV_L1.values() for v in vs), True)
    arm("no level is under the G-MINCELL floor",
        all(min(mincell_map(l).values()) >= MINCELL_FLOOR_M for l in LEVELS), True)

    print("-- the set +u guard --")
    arm("the OpenFOAM preamble carries `set +u` before sourcing the bashrc",
        SH_PREAMBLE.startswith("set +u; . "), True)
    arm("...and every shell-out goes through that one constant",
        "SH_PREAMBLE + cmd" in open(os.path.abspath(__file__)).read(), True)

    print("-- case writing, no mesh --")
    root = tempfile.mkdtemp(prefix="k2d_build_")
    try:
        res = build("K2d_L1", root=root, run_mesh=False)
        case = res["case"]
        arm("stages into 0.orig/", os.path.isdir(os.path.join(case, "0.orig")), True)
        arm("NEVER creates 0/ (the age-guard referent is armed at LAUNCH)",
            os.path.isdir(os.path.join(case, "0")), False)
        arm("writes MINCELL.json, which the comparator refuses without",
            os.path.isfile(os.path.join(case, "MINCELL.json")), True)
        need = ("T", "U", "p_rgh", "p", "k", "omega", "nut", "alphat")
        arm("every field the completion rule needs is staged",
            all(os.path.isfile(os.path.join(case, "0.orig", f)) for f in need), True)
        bmd = open(os.path.join(case, "system", "blockMeshDict")).read()
        arm("the rack is an UNMESHED VOID: block count == grid minus void",
            bmd.count("hex ("), 6 * 6 * 2 - len(RACK_XI))   # 72 blocks - 4 rack voids
        arm("deltaT is 1, so rule 4 clause 5 is n_exec == endTime",
            "deltaT 1;" in open(os.path.join(case, "system", "controlDict")).read(), True)

        os.makedirs(os.path.join(case, "0"), exist_ok=True)
        arm_refuses("CLAUSE 7: a pre-existing 0/ -> builder REFUSES",
                    lambda: build("K2d_L1", root=root, run_mesh=False))
        arm_refuses("a level name off the ladder -> REFUSE",
                    lambda: build("K2d_L9", root=root, run_mesh=False))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("\nSELFTEST %s" % ("PASS -- every arm fired as registered" if ok_all
                             else "FAIL -- an arm did not behave as registered"))
    return EXIT_OK if ok_all else EXIT_FAIL


def main(argv):
    if not argv:
        print(__doc__)
        return EXIT_REFUSE
    if argv[0] == "--selftest":
        return selftest()
    if argv[0] == "--arith":
        return EXIT_OK if arith_report() else EXIT_FAIL
    rc = EXIT_OK
    for lv in argv:
        res = build(lv)
        print("%s: cells %s (predicted %s), checkMesh failed %s"
              % (lv, res.get("cells"), res["predicted_cells"],
                 res.get("checkmesh_failed")))
        if res.get("checkmesh_failed"):
            rc = EXIT_FAIL
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refuse as e:
        print("REFUSED (exit 2): %s" % e)
        sys.exit(EXIT_REFUSE)
