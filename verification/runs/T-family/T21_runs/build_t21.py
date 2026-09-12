#!/usr/bin/env python3
"""build_t21.py -- build a T21 two-region conduction wedge case.

REGISTERED BY docs/campaigns/T-family/T21_PREREGISTRATION.md.

WHAT IT BUILDS.  A 2-D axisymmetric wedge (theta = 5 deg, one cell
circumferentially), two SOLID cellZones and zero fluid regions:
  core     r_bore=0.006 -> r_i=0.0335  (adiabatic bore, carries the source)
  housing  r_i=0.0335   -> r_o=0.0375  (aluminium shell, the graded drop)
axial 0 -> L=0.125.  Solver chtMultiRegionSimpleFoam v2606.

THE FOUR REGISTERED TRAPS, EACH HANDLED IN ONE PLACE:

  T-1 (S3.1) the solid energy equation is in ENTHALPY h, not T.  fvOptions
      writes `sources { h (Su Sp); }` on field h.  A source naming T is never
      matched and produces a SILENT uniform-T solid.  The comparator additionally
      greps log.solve for "but never used".

  T-2 (S3.2) the key injectionRate DOES NOT EXIST at v2606.  The `sources` form
      is used; injectionRateSuSp is the legacy spelling and is not written.

  T-3 (S3.3) volumeMode is MANDATORY and `absolute` divides the entered value by
      the measured zone volume.  volumeMode absolute is written, and Su is the
      TOTAL sector power P_sector in W (not W/m3), because absolute mode does the
      division.  The wrong value here is a SILENT error.

  T-4 (S3.4) the wedge power factor.  P_sector = P_full * theta/(2*pi) is
      computed ONCE, from a theta READ BACK FROM THE GENERATED blockMeshDict, by
      exact_t21.p_sector -- never typed as a literal.  The comparator recomputes
      theta from the mesh and refuses on a 1e-12 mismatch.

  T-5 (S3.1, collapsed axis) the core carries a 6 mm bore and does NOT reach the
      axis -- a collapsed-axis core gave 140 zero-area faces on T22's identical
      construction.  r_bore = 0.006.

  T-6 (S6.1) NO residualControl.  The full endTime is run; convergence is an
      assertion, never a stopping rule.  This family was killed by residualControl
      today (T19).

  T-7 (S6, age guard) 0/ is created from 0.orig/ by the LAUNCHER, which touches
      0/housing/T last.  This builder writes 0.orig/, never 0/.

  T-8 (S6 conjunct 6, the MESH-STAGE BYPRODUCT) splitMeshRegions writes its
      cellToRegion TOPOLOGY MAP into a directory named `0/`.  That map is not a
      field and not an answer -- it is part of the mesh -- but the age guard
      tests for the NAME `0`, and correctly so: the guard's strength is that it
      is crude and cannot be argued with.  So THE MESH STAGE RELOCATES ITS OWN
      BYPRODUCT, here, in code, as the named step --postsplit, before the
      physics stage ever runs.  The guard at physics():450 is UNCHANGED and
      still refuses any `0/` it is shown.  --postsplit RELOCATES (os.rename to
      constant/splitMeshRegions_byproduct/), NEVER DELETES, and REFUSES outright
      if `0/` holds one single file that is not a cellToRegion map -- so a real
      field planted in `0/` stops the mesh stage AND is then refused again by
      the unchanged guard.  Both refusals are exercised in --selftest.

Exit 0 built, 2 refusal.  Zero bare `assert` (L-332).  No .pyc beside pins.

Phases, in order:  --case <c>  (mesh dicts)  ->  blockMesh, splitMeshRegions
                   --postsplit <c>  (T-8, relocate the byproduct)
                   --physics <c>  (physics dicts into the split tree)
"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_t21 as X                                             # noqa: E402

# Registered geometry (T21_PREREGISTRATION.md S1 line 1, S8.1).
R_BORE = 0.006
R_I = 0.0335
R_O = 0.0375
L_AX = 0.125
THETA_DEG = 5.0
END_TIME = 3000

# The registered run set (S8.1): housing N_r, core N_r, N_z, theta_deg, P_full.
CASES = {
    "T21_CYL_c":     dict(hn=8,  cn=24, nz=20, theta=5.0, pw=100.0),
    "T21_CYL_m":     dict(hn=16, cn=48, nz=40, theta=5.0, pw=100.0),
    "T21_CYL_f":     dict(hn=32, cn=96, nz=80, theta=5.0, pw=100.0),
    "T21_CYL_W1":    dict(hn=32, cn=96, nz=80, theta=1.0, pw=100.0),
    "T21_CYL_P1000": dict(hn=32, cn=96, nz=80, theta=5.0, pw=1000.0),
    "T21_CYL_S10":   dict(hn=32, cn=96, nz=80, theta=5.0, pw=110.0),  # +10% planted
}
CASES_BASELINE = tuple(sorted(CASES))     # rule 14 baseline

MAT = {  # rho, cp, k  -- S1 line 1
    "core":    (7000.0, 450.0, 40.0),
    "housing": (2700.0, 900.0, 167.0),
}
FIELDS = ("T", "p")   # S6 conjunct 4: solid regions carry exactly T and p

# T-8: where the MESH stage puts splitMeshRegions' cellToRegion topology map.
# Under constant/ because it is mesh, not an answer.  NEVER deleted.
SPLIT_BYPRODUCT_DIR = os.path.join("constant", "splitMeshRegions_byproduct")
SPLIT_BYPRODUCT_OBJECT = "cellToRegion"

# ---- PHYSICS-DICT HALF (S3 heat source, S5.1 boundary, S6.2 g, S10 omissions) ----
T_OUTER = 288.0        # K, housing_outer fixedValue sink (S5.1)
T_INIT = 288.0         # K, uniform initial field (== the sink, a benign start)
P_DUMMY = 1.0e5        # Pa, solid p is a REQUIRED-but-INERT field (S6 conjunct 4)
SRC_NAME = "motorLoss"  # the registered source name; S9 S10 forge "...motorLoss...
                        # for field T but never used" so this name is load-bearing
# molWeight is INERT here: rhoConst sets density directly and molWeight does not
# enter steady solid conduction (S10 omission 7).  Documented, not defaulted.
MOLW = {"core": 55.0, "housing": 27.0}


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(2)


def cases_intact_or_refuse():
    """RULE 14 at every call site: the run set is inserted, never silently
    reduced.  A case dropped from CASES would ungrade the triple unseen."""
    for c in CASES_BASELINE:
        if c not in CASES:
            refuse("rule 14: registered case %r removed from CASES" % c)


HDR = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class %s;\n"
       "    object %s;\n}\n")


def _vertex(r, sign, z, a):
    return "    (%.10g %.10g %.10g)" % (r * math.cos(a), sign * r * math.sin(a), z)


def blockmeshdict(cn, hn, nz, theta_deg):
    """Two radial blocks (core r_bore->r_i, housing r_i->r_o), one cell
    circumferentially, symmetric about y=0.  Front/back are wedge patches; the
    r_i interface is INTERNAL and becomes a mapped patch after splitMeshRegions.
    theta is written here and read back by the comparator (T-4)."""
    a = math.radians(theta_deg) / 2.0
    rs = [R_BORE, R_I, R_O]
    v = []
    for sign in (-1.0, 1.0):            # back plane first, then front
        for r in rs:
            for z in (0.0, L_AX):
                v.append((r, sign, z))

    def idx(ri, sign_i, zi):
        return sign_i * 6 + ri * 2 + zi

    verts = "\n".join(_vertex(r, s, z, a) for (r, s, z) in v)
    # core block: r index 0->1 ; housing: 1->2. local (radial, circ, axial).
    def hexblk(r0, r1, zone, nr):
        b0, b1 = 0, 1   # back z0, back zL handled via idx
        vs = (idx(r0, 0, 0), idx(r1, 0, 0), idx(r1, 1, 0), idx(r0, 1, 0),
              idx(r0, 0, 1), idx(r1, 0, 1), idx(r1, 1, 1), idx(r0, 1, 1))
        return ("    hex (%d %d %d %d %d %d %d %d) %s (%d 1 %d) simpleGrading (1 1 1)"
                % (vs + (zone, nr, nz)))

    blocks = hexblk(0, 1, "core", cn) + "\n" + hexblk(1, 2, "housing", hn)

    # boundary faces (radial faces at r_bore, r_o; wedge front/back; empty ends)
    def face(ri, zi_pair, sign_pair):
        # a radial face spans circ (back->front) and axial; here helper builds
        # the four-vertex face for a constant-r surface over one axial cell strip
        pass

    boundary = """
    core_bore
    {{
        type wall;
        faces ( ({a} {b} {c} {d}) );
    }}
    housing_outer
    {{
        type wall;
        faces ( ({e} {f} {g} {h}) );
    }}
    wedge_front
    {{
        type wedge;
        faces ( ({i} {j} {k} {l}) ({m} {n} {o} {p}) );
    }}
    wedge_back
    {{
        type wedge;
        faces ( ({q} {r} {s} {t}) ({u} {vv} {w} {x}) );
    }}
    ends
    {{
        type wall;
        faces (
            ({e0} {e1} {e2} {e3}) ({e4} {e5} {e6} {e7})
            ({e8} {e9} {e10} {e11}) ({e12} {e13} {e14} {e15})
        );
    }}
""".format(
        # core_bore: constant r=r0 face (back r0 z0, back r0 zL, front r0 zL, front r0 z0)
        a=idx(0, 0, 0), b=idx(0, 0, 1), c=idx(0, 1, 1), d=idx(0, 1, 0),
        # housing_outer: r=r2
        e=idx(2, 0, 0), f=idx(2, 0, 1), g=idx(2, 1, 1), h=idx(2, 1, 0),
        # wedge_front (sign +1): core and housing, constant +a plane
        i=idx(0, 1, 0), j=idx(1, 1, 0), k=idx(1, 1, 1), l=idx(0, 1, 1),
        m=idx(1, 1, 0), n=idx(2, 1, 0), o=idx(2, 1, 1), p=idx(1, 1, 1),
        # wedge_back (sign -1)
        q=idx(0, 0, 0), r=idx(0, 0, 1), s=idx(1, 0, 1), t=idx(1, 0, 0),
        u=idx(1, 0, 0), vv=idx(1, 0, 1), w=idx(2, 0, 1), x=idx(2, 0, 0),
        # ends: z=0 and z=L for both blocks (adiabatic wall)
        e0=idx(0, 0, 0), e1=idx(1, 0, 0), e2=idx(1, 1, 0), e3=idx(0, 1, 0),
        e4=idx(1, 0, 0), e5=idx(2, 0, 0), e6=idx(2, 1, 0), e7=idx(1, 1, 0),
        e8=idx(0, 0, 1), e9=idx(1, 0, 1), e10=idx(1, 1, 1), e11=idx(0, 1, 1),
        e12=idx(1, 0, 1), e13=idx(2, 0, 1), e14=idx(2, 1, 1), e15=idx(1, 1, 1),
    )
    return (HDR % ("dictionary", "blockMeshDict")
            + "\nscale 1;\n\nvertices\n(\n" + verts + "\n);\n\n"
            + "blocks\n(\n" + blocks + "\n);\n\nedges ();\n\n"
            + "boundary\n(" + boundary + ");\n\nmergePatchPairs ();\n")


def theta_from_blockmeshdict(path):
    """Read theta back from the generated file (T-4): the two front vertices at
    r_o give the half-angle from atan2(y, x)."""
    import re
    txt = open(path).read()
    m = re.findall(r"\(\s*([-\d.eE]+)\s+([-\d.eE]+)\s+([-\d.eE]+)\s*\)", txt)
    best = None
    for x, y, z in m:
        x, y, z = float(x), float(y), float(z)
        r = math.hypot(x, y)
        if abs(r - R_O) < 1e-9 and y > 0:
            best = 2.0 * math.atan2(y, x)
    return best


def write(path, cls, obj, body):
    with open(path, "w") as fh:
        fh.write(HDR % (cls, obj) + body)


def build(case):
    cases_intact_or_refuse()                       # rule 14, call site 1
    if case not in CASES:
        refuse("unknown case %r; registered set is %s" % (case, CASES_BASELINE))
    spec = CASES[case]
    dst = os.path.join(HERE, case)
    if os.path.isdir(dst):
        for n in os.listdir(dst):
            if n == "0" or (n.replace(".", "", 1).isdigit() and n != "0.orig"):
                refuse("%s already holds %r -- a run tree is never built over an answer" % (dst, n))
    for sub in ("system", "constant", "0.orig"):
        os.makedirs(os.path.join(dst, sub), exist_ok=True)

    # top-level system files blockMesh/splitMeshRegions/solver read unconditionally
    # (T21 Amendment 1: a top-level system/fvSolution is MANDATORY, read on the
    # global registry before any region loop).  NO residualControl (T-6).
    write(os.path.join(dst, "system", "controlDict"), "dictionary", "controlDict",
          "\napplication chtMultiRegionSimpleFoam;\nstartFrom startTime;\n"
          "startTime 0;\nstopAt endTime;\nendTime %d;\ndeltaT 1;\n"
          "writeControl timeStep;\nwriteInterval %d;\npurgeWrite 0;\n"
          "writeFormat ascii;\nwritePrecision 12;\nwriteCompression off;\n"
          "timeFormat general;\ntimePrecision 6;\nrunTimeModifiable false;\n"
          % (END_TIME, END_TIME))
    write(os.path.join(dst, "system", "fvSchemes"), "dictionary", "fvSchemes",
          "\nddtSchemes { default steadyState; }\n"
          "gradSchemes { default Gauss linear; }\n"
          "divSchemes { default none; }\n"
          "laplacianSchemes { default none; }\n"
          "interpolationSchemes { default linear; }\n"
          "snGradSchemes { default corrected; }\n")
    write(os.path.join(dst, "system", "fvSolution"), "dictionary", "fvSolution",
          "\nsolvers {}\nSIMPLE { }\n")

    # blockMeshDict, then theta read BACK from it and P_sector from that (T-4)
    bmd = os.path.join(dst, "system", "blockMeshDict")
    open(bmd, "w").write(blockmeshdict(spec["cn"], spec["hn"], spec["nz"], spec["theta"]))
    theta_read = theta_from_blockmeshdict(bmd)
    if theta_read is None or abs(math.degrees(theta_read) - spec["theta"]) > 1e-6:
        refuse("theta read back from %s is %s, expected %g deg -- the one-place "
               "wedge-factor rule is broken" % (bmd, theta_read, spec["theta"]))
    p_sector = X.p_sector(spec["pw"], theta_read)   # THE single computation

    print("built %s: core %d + housing %d radial, %d axial; theta %.4f deg "
          "(read back); P_sector %.9f W" % (case, spec["cn"], spec["hn"],
          spec["nz"], math.degrees(theta_read), p_sector))
    cases_intact_or_refuse()                       # rule 14, call site 2
    return 0, p_sector, theta_read


# ===========================================================================
# THE PHYSICS-DICT HALF.
#
# WHY IT IS A SEPARATE PHASE (--physics) FROM THE MESH HALF (--case).
#   splitMeshRegions creates system/<region>/{fvSchemes,fvSolution} as EMPTY
#   STUBS -- measured: the on-disk post-split system/core/fvSchemes has empty
#   divSchemes/gradSchemes/laplacianSchemes.  A physics dict written BEFORE the
#   split would be clobbered.  So the physics half runs AFTER blockMesh +
#   splitMeshRegions, into the split tree.  The mesh half (build/--case) is
#   UNTOUCHED by this phase.
#
# THE ENTHALPY fvOptions TRAP (S3.1-3.4), avoided in ONE place each:
#   * field is h, NOT T           -> sources { h (Su Sp); }  (a T source is
#                                    silently never applied -> uniform solid)
#   * key is `sources`, NOT       -> the 2206+ form; injectionRate does not
#     injectionRate                  exist at v2606
#   * volumeMode absolute         -> Su is the TOTAL sector power in W; OpenFOAM
#                                    divides by the volume IT measured
#   * P_sector = P_full*theta/2pi -> computed from theta READ BACK from the
#                                    generated blockMeshDict via X.p_sector, the
#                                    single place; written at full double
#                                    precision so the comparator's 1e-12 check
#                                    round-trips.  Source lives in core ONLY.
#   fvOptions is read from constant/<region>/ (verified: fvOptions.C:50-83 tries
#   constant then system; absent in both -> NO_READ, a SILENT zero source).
# ===========================================================================

import re                                                          # noqa: E402


def read_region_patches(dst, region):
    """Return [(name, type), ...] for a split region, read from its own
    polyMesh/boundary.  The 0.orig boundaryField is generated FROM this, never
    hard-coded, so a patch the split produced can never be missing from the
    field (the classic 'boundaryField for patch X not found' first-launch
    fatal) and a patch that vanished can never linger in the field."""
    path = os.path.join(dst, "constant", region, "polyMesh", "boundary")
    txt = open(path).read()
    pats = []
    for name, ptype in re.findall(r"(\w+)\s*\{[^{}]*?\btype\s+(\w+)\s*;", txt, re.S):
        if name == "FoamFile":
            continue
        pats.append((name, ptype))
    return pats


def _classify(name, ptype):
    """Map a patch to its (T-kind, p-kind).  Registered semantics (S5.1, S8.1):
    wedge planes are wedge; the region interface is the solid-solid couple;
    housing_outer is the fixedValue 288 K sink; every other wall (core_bore,
    ends) is adiabatic."""
    if ptype == "wedge":
        return ("wedge", "wedge")
    if ptype == "mappedWall" or name.endswith("_to_core") or name.endswith("_to_housing"):
        return ("coupled", "calculated")
    if name == "housing_outer":
        return ("fixed", "calculated")
    return ("adiabatic", "calculated")   # core_bore, ends -- adiabatic walls


def _field_T(patches):
    parts = []
    for name, ptype in patches:
        kind = _classify(name, ptype)[0]
        if kind == "wedge":
            body = "        type wedge;\n"
        elif kind == "coupled":
            # solid-solid couple; the ONLY couple this rung exercises (S10 om.3)
            body = ("        type compressible::turbulentTemperatureRadCoupledMixed;\n"
                    "        Tnbr T;\n        kappaMethod solidThermo;\n"
                    "        qrNbr none;\n        qr none;\n"
                    "        value uniform %.10g;\n" % T_INIT)
        elif kind == "fixed":
            body = "        type fixedValue;\n        value uniform %.10g;\n" % T_OUTER
        else:
            body = "        type zeroGradient;\n"          # adiabatic (S8.1)
        parts.append("    %s\n    {\n%s    }\n" % (name, body))
    return ("dimensions [0 0 0 1 0 0 0];\n\ninternalField uniform %.10g;\n\n"
            "boundaryField\n{\n%s}\n" % (T_INIT, "".join(parts)))


def _field_p(patches):
    parts = []
    for name, ptype in patches:
        if _classify(name, ptype)[1] == "wedge":
            body = "        type wedge;\n"
        else:
            body = "        type calculated;\n        value uniform %.10g;\n" % P_DUMMY
        parts.append("    %s\n    {\n%s    }\n" % (name, body))
    return ("dimensions [1 -1 -2 0 0 0 0];\n\ninternalField uniform %.10g;\n\n"
            "boundaryField\n{\n%s}\n" % (P_DUMMY, "".join(parts)))


def _thermo(region):
    rho, cp, k = MAT[region]
    return ("\nthermoType\n{\n    type heSolidThermo;\n    mixture pureMixture;\n"
            "    transport constIso;\n    thermo hConst;\n"
            "    equationOfState rhoConst;\n    specie specie;\n"
            "    energy sensibleEnthalpy;\n}\n\n"
            "mixture\n{\n    specie { molWeight %.6g; }\n"
            "    transport { kappa %.10g; }\n"
            "    thermodynamics { Hf 0; Cp %.10g; }\n"
            "    equationOfState { rho %.10g; }\n}\n"
            % (MOLW[region], k, cp, rho))


def _fvoptions(p_sector):
    """The enthalpy source, core region only.  field h; `sources` form;
    volumeMode absolute; selectionMode all; Su = P_sector [W] at full double
    precision (S3.1-3.4).  A source named T here would be SILENT."""
    return ("\n%s\n{\n    type scalarSemiImplicitSource;\n    active true;\n"
            "    selectionMode all;\n    volumeMode absolute;\n"
            "    sources\n    {\n        h (%.17g 0);\n    }\n}\n"
            % (SRC_NAME, p_sector))


def _radiation():
    return "\nradiationModel none;\n"     # S10 omission 4, explicit not defaulted


def _region_fvschemes():
    return ("\nddtSchemes { default steadyState; }\n"
            "gradSchemes { default Gauss linear; }\n"
            "divSchemes { default none; }\n"
            "laplacianSchemes { default Gauss linear corrected; }\n"
            "interpolationSchemes { default linear; }\n"
            "snGradSchemes { default corrected; }\n")


def _region_fvsolution():
    # NO residualControl (T-6): the full endTime is run, convergence asserted.
    return ("\nsolvers\n{\n    h\n    {\n        solver PCG;\n"
            "        preconditioner DIC;\n        tolerance 1e-11;\n"
            "        relTol 0;\n    }\n}\n\n"
            "SIMPLE\n{\n    nNonOrthogonalCorrectors 0;\n}\n\n"
            "relaxationFactors\n{\n    equations\n    {\n        h 0.99;\n    }\n}\n")


def write_physics(dst, spec, p_sector, region_patches):
    """Write the physics dicts into an already-split two-region tree.  The mesh
    half is not read or written here."""
    for r in ("core", "housing"):
        if not region_patches.get(r):
            refuse("region %r has no patches -- the tree is not split" % r)
    # g -- MANDATORY even with zero fluid regions (S6.2; probe arm D fatal)
    write(os.path.join(dst, "constant", "g"), "uniformDimensionedVectorField", "g",
          "\ndimensions [0 1 -2 0 0 0 0];\nvalue (0 0 0);\n")
    # regionProperties -- fluid () / solid (core housing)
    write(os.path.join(dst, "constant", "regionProperties"), "dictionary",
          "regionProperties", "\nregions\n(\n    fluid ()\n    solid (core housing)\n);\n")
    for r in ("core", "housing"):
        os.makedirs(os.path.join(dst, "constant", r), exist_ok=True)
        os.makedirs(os.path.join(dst, "system", r), exist_ok=True)
        os.makedirs(os.path.join(dst, "0.orig", r), exist_ok=True)
        write(os.path.join(dst, "constant", r, "thermophysicalProperties"),
              "dictionary", "thermophysicalProperties", _thermo(r))
        write(os.path.join(dst, "constant", r, "radiationProperties"),
              "dictionary", "radiationProperties", _radiation())
        write(os.path.join(dst, "system", r, "fvSchemes"), "dictionary",
              "fvSchemes", _region_fvschemes())
        write(os.path.join(dst, "system", r, "fvSolution"), "dictionary",
              "fvSolution", _region_fvsolution())
        write(os.path.join(dst, "0.orig", r, "T"), "volScalarField", "T",
              _field_T(region_patches[r]))
        write(os.path.join(dst, "0.orig", r, "p"), "volScalarField", "p",
              _field_p(region_patches[r]))
    # THE SOURCE lives in core ONLY (S3.3); housing gets no fvOptions
    write(os.path.join(dst, "constant", "core", "fvOptions"), "dictionary",
          "fvOptions", _fvoptions(p_sector))
    return 0


def _is_split_byproduct(path):
    """True only for a file whose FoamFile header declares `object cellToRegion;`
    -- splitMeshRegions' topology map.  Read from the file, never inferred from
    its name (rule 15's habit applied to a case tree: a name can be false)."""
    try:
        head = open(path, errors="replace").read(4096)
    except OSError:
        return False
    return re.search(r"^\s*object\s+cellToRegion\s*;", head, re.M) is not None


def postsplit(case):
    """--postsplit phase (T-8), THE LAST STEP OF THE MESH STAGE.

    splitMeshRegions -cellZones -overwrite writes its cellToRegion map into a
    directory named `0/`.  This step relocates that byproduct to
    constant/splitMeshRegions_byproduct/ so that the physics stage's age guard
    -- which tests the NAME `0` and is deliberately not being softened -- is
    shown a genuinely clean tree.

    IT REFUSES, AND MOVES NOTHING, IF `0/` HOLDS ANYTHING ELSE.  One file that
    is not a cellToRegion map is enough.  That is what keeps this a repair of
    the mesh stage rather than a hole in the guard: a planted field stops here,
    and then stops again at physics().
    """
    cases_intact_or_refuse()
    if case not in CASES:
        refuse("unknown case %r; registered set is %s" % (case, CASES_BASELINE))
    dst = os.path.join(HERE, case)
    if not os.path.isdir(dst):
        refuse("%s does not exist -- run --case first" % dst)
    for r in ("core", "housing"):
        if not os.path.isfile(os.path.join(dst, "constant", r, "polyMesh", "boundary")):
            refuse("%s: region %r not split -- --postsplit runs AFTER blockMesh "
                   "+ splitMeshRegions" % (dst, r))
    # never relocate anything in a tree that already holds an answer
    for n in os.listdir(dst):
        if n != "0" and n != "0.orig" and n.replace(".", "", 1).isdigit():
            refuse("%s already holds time directory %r -- the mesh stage is over; "
                   "nothing is moved in a tree that holds an answer" % (dst, n))
    zero = os.path.join(dst, "0")
    dest = os.path.join(dst, SPLIT_BYPRODUCT_DIR)
    if not os.path.exists(zero):
        print("postsplit %s: no 0/ present -- nothing to relocate (byproduct dir "
              "exists: %s)" % (case, os.path.isdir(dest)))
        return 0
    if not os.path.isdir(zero):
        refuse("%s/0 is not a directory -- unrecognised; nothing moved" % dst)
    # PROVE every single file under 0/ is a cellToRegion map.  Any other file,
    # and the whole step refuses: it may be an answer, and this code does not
    # get to decide that it is not.
    found, offenders = [], []
    for root, _dirs, files in os.walk(zero):
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, zero)
            if f == SPLIT_BYPRODUCT_OBJECT and _is_split_byproduct(p):
                found.append(rel)
            else:
                offenders.append(rel)
    if offenders:
        refuse("%s/0 holds %d file(s) that are NOT splitMeshRegions cellToRegion "
               "maps: %s -- these may be ANSWERS.  Nothing was moved and nothing "
               "was deleted; the age guard stands and physics() will refuse this "
               "tree." % (dst, len(offenders), ", ".join(offenders[:8])))
    if not found:
        refuse("%s/0 holds no cellToRegion map at all -- unrecognised; nothing moved" % dst)
    if os.path.exists(dest):
        refuse("%s already exists -- nothing is ever overwritten or deleted here" % dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    os.rename(zero, dest)                       # RELOCATE.  Never delete.
    if os.path.exists(zero):
        refuse("0/ still present after the relocation -- refusing rather than "
               "reporting a move that did not happen")
    open(os.path.join(dest, "PROVENANCE.txt"), "w").write(
        "splitMeshRegions BYPRODUCT, relocated here by build_t21.py --postsplit\n"
        "(T-8).  Case: %s.  Contents when moved: %s.\n\n"
        "This is the cellToRegion TOPOLOGY MAP splitMeshRegions writes into a\n"
        "directory named 0/.  It is mesh, not a field and not an answer.  It was\n"
        "MOVED, not deleted, and every file in it was read and found to declare\n"
        "`object cellToRegion;` before the move.  The physics-stage age guard\n"
        "(CLAUDE.md rule 4) is UNCHANGED and still refuses any 0/ it is shown.\n"
        % (case, ", ".join(found)))
    print("postsplit %s: relocated %d cellToRegion map(s) (%s) to %s; 0/ is gone, "
          "nothing deleted" % (case, len(found), ", ".join(found), SPLIT_BYPRODUCT_DIR))
    return 0


def physics(case):
    """--physics phase: write the physics dicts into a split tree."""
    cases_intact_or_refuse()
    if case not in CASES:
        refuse("unknown case %r; registered set is %s" % (case, CASES_BASELINE))
    spec = CASES[case]
    dst = os.path.join(HERE, case)
    for r in ("core", "housing"):
        if not os.path.isfile(os.path.join(dst, "constant", r, "polyMesh", "boundary")):
            refuse("%s: region %r not split -- run blockMesh + splitMeshRegions "
                   "before --physics" % (dst, r))
    # age guard: physics is NEVER written over an answer (0/ or a time dir)
    for n in os.listdir(dst):
        if n == "0" or (n.replace(".", "", 1).isdigit() and n != "0.orig"):
            refuse("%s already holds %r -- physics is never written over an answer" % (dst, n))
    # theta read BACK from the generated blockMeshDict -> p_sector, one place (T-4)
    bmd = os.path.join(dst, "system", "blockMeshDict")
    theta_read = theta_from_blockmeshdict(bmd)
    if theta_read is None or abs(math.degrees(theta_read) - spec["theta"]) > 1e-6:
        refuse("theta read back from %s is %s, expected %g deg -- the one-place "
               "wedge-factor rule is broken" % (bmd, theta_read, spec["theta"]))
    p_sec = X.p_sector(spec["pw"], theta_read)
    patches = {r: read_region_patches(dst, r) for r in ("core", "housing")}
    write_physics(dst, spec, p_sec, patches)
    cases_intact_or_refuse()
    print("physics %s: source %s h=%.9f W on core (P_full %.1f, theta %.4f deg "
          "read back); housing_outer fixedValue %.1f K; core<->housing coupled; "
          "radiation none; g (0 0 0)"
          % (case, SRC_NAME, p_sec, spec["pw"], math.degrees(theta_read), T_OUTER))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--postsplit" in argv:
        return postsplit(argv[argv.index("--postsplit") + 1])
    if "--physics" in argv:
        return physics(argv[argv.index("--physics") + 1])
    if "--case" not in argv:
        refuse("usage: build_t21.py --case <name> | --postsplit <name> "
               "| --physics <name> | --selftest")
    return build(argv[argv.index("--case") + 1])[0]


def selftest():
    ok = [True]

    def chk(c, m):
        ok[0] = ok[0] and bool(c)
        print("  [%s] %s" % ("PASS" if c else "FAIL", m))

    print("build_t21 selftest -- MESH GENERATION AND THE WEDGE-FACTOR ROUND TRIP")
    import tempfile, shutil
    global HERE
    real = HERE
    tmp = tempfile.mkdtemp(prefix="t21_bt_")
    try:
        HERE = tmp
        sys.path.insert(0, real)
        _rc, ps, th = build("T21_CYL_c")
        chk(abs(math.degrees(th) - 5.0) < 1e-9, "theta round-trips through blockMeshDict at 5.000 deg")
        chk(abs(ps - 1.388888889) < 1e-9, "P_sector(100 W) = %.9f from the READ-BACK theta" % ps)
        # rule 14
        saved = dict(CASES)
        CASES.pop("T21_CYL_f")
        try:
            cases_intact_or_refuse(); chk(False, "rule 14 should have refused a dropped case")
        except SystemExit as e:
            chk(e.code == 2, "rule 14 REFUSES a dropped registered case (exit %s)" % e.code)
        CASES.update(saved)
        chk(os.path.isfile(os.path.join(tmp, "T21_CYL_c", "system", "blockMeshDict")),
            "blockMeshDict written")
        chk(not os.path.isdir(os.path.join(tmp, "T21_CYL_c", "0")),
            "no 0/ written -- the launcher makes it from 0.orig/ (T-7)")

        # -------- PHYSICS-DICT HALF, on SYNTHETIC patches (no mesh needed) ----
        print("  -- physics-dict half --")
        cdst = os.path.join(tmp, "T21_CYL_c")
        # the registered post-split patch set (measured from the proven mesh)
        syn = {
            "core":    [("core_bore", "wall"), ("wedge_front", "wedge"),
                        ("wedge_back", "wedge"), ("ends", "wall"),
                        ("core_to_housing", "mappedWall")],
            "housing": [("housing_outer", "wall"), ("wedge_front", "wedge"),
                        ("wedge_back", "wedge"), ("ends", "wall"),
                        ("housing_to_core", "mappedWall")],
        }
        ps = X.p_sector(100.0, math.radians(5.0))
        write_physics(cdst, CASES["T21_CYL_c"], ps, syn)

        fvo = open(os.path.join(cdst, "constant", "core", "fvOptions")).read()
        chk("scalarSemiImplicitSource" in fvo, "core fvOptions is scalarSemiImplicitSource")
        chk("volumeMode absolute" in fvo, "volumeMode absolute (Su is total W, S3.3)")
        chk("injectionRate" not in fvo, "injectionRate NOT written (does not exist at v2606, S3.2)")
        m = re.search(r"sources\s*\{\s*h\s*\(\s*([-\d.eE+]+)\s+0\s*\)", fvo)
        chk(m is not None, "source is on field h, `sources` form (S3.1) -- NOT on T")
        chk(m and abs(float(m.group(1)) - ps) == 0.0,
            "fvOptions Su round-trips EXACTLY to X.p_sector = %.12g W (anti-72x, S3.4)" % ps)
        chk("field T " not in fvo and "T (" not in fvo.replace("h (", ""),
            "no source on field T (a T source is the SILENT-zero trap, S3.1)")
        chk(not os.path.isfile(os.path.join(cdst, "constant", "housing", "fvOptions")),
            "housing has NO fvOptions -- the source is in core ONLY (S3.3)")

        th_c = open(os.path.join(cdst, "constant", "core", "thermophysicalProperties")).read()
        th_h = open(os.path.join(cdst, "constant", "housing", "thermophysicalProperties")).read()
        chk("energy sensibleEnthalpy" in th_c, "core energy sensibleEnthalpy (equation is in h)")
        chk("kappa 40" in th_c, "core kappa 40 W/mK (S1)")
        chk("kappa 167" in th_h, "housing kappa 167 W/mK (S1)")

        Th = open(os.path.join(cdst, "0.orig", "housing", "T")).read()
        Tc = open(os.path.join(cdst, "0.orig", "core", "T")).read()
        chk("fixedValue" in Th and "288" in Th, "housing_outer T fixedValue 288 K (S5.1)")
        chk("turbulentTemperatureRadCoupledMixed" in Th and
            "turbulentTemperatureRadCoupledMixed" in Tc,
            "core<->housing solid-solid couple on both sides")
        # every mesh patch appears in the field, and no extra (first-launch guard)
        for r in ("core", "housing"):
            names = {n for n, _ in syn[r]}
            Tf = open(os.path.join(cdst, "0.orig", r, "T")).read()
            got = set(re.findall(r"^    (\w+)\n    \{", Tf, re.M))
            chk(got == names, "%s/T boundaryField covers EXACTLY its mesh patches" % r)

        g = open(os.path.join(cdst, "constant", "g")).read()
        chk("value (0 0 0)" in g, "constant/g value (0 0 0) -- mandatory, zero (S6.2)")
        rp = open(os.path.join(cdst, "constant", "regionProperties")).read()
        chk("fluid ()" in rp and "solid (core housing)" in rp, "regionProperties fluid()/solid(core housing)")
        rad = open(os.path.join(cdst, "constant", "core", "radiationProperties")).read()
        chk("radiationModel none" in rad, "radiationModel none, explicit (S10 om.4)")
        fvsol = open(os.path.join(cdst, "system", "core", "fvSolution")).read()
        chk("residualControl" not in fvsol, "NO residualControl (T-6, the T19 killer)")

        # write_physics REFUSES on an unsplit region (empty patch list)
        try:
            write_physics(cdst, CASES["T21_CYL_c"], ps, {"core": [], "housing": syn["housing"]})
            chk(False, "write_physics should refuse an unsplit region")
        except SystemExit as e:
            chk(e.code == 2, "write_physics REFUSES an unsplit region (exit %s)" % e.code)

        # ---- T-8: THE MESH-STAGE BYPRODUCT RELOCATION, AND THE PROOF THAT
        # ---- THE AGE GUARD STILL FIRES AFTER IT.
        #
        # This block is the demonstration the guard repair is not allowed to be
        # believed without: the guard is NOT weakened, and a real field planted
        # in 0/ is refused TWICE -- once by the relocation step, which will not
        # touch it, and once by the unchanged physics() guard.
        print("  -- T-8 mesh-stage byproduct relocation + AGE-GUARD DEMONSTRATION --")
        MAP = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
               "    class volScalarField;\n    location \"0\";\n"
               "    object cellToRegion;\n}\ndimensions [0 0 0 0 0 0 0];\n"
               "internalField uniform 0;\n")
        FIELD_T = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
                   "    class volScalarField;\n    object T;\n}\n"
                   "dimensions [0 0 0 1 0 0 0];\ninternalField uniform 288;\n")

        def make_split_tree():
            """the post-splitMeshRegions shape: region polyMesh/boundary files,
            and a 0/ holding ONLY cellToRegion maps."""
            for r in ("core", "housing"):
                bd = os.path.join(cdst, "constant", r, "polyMesh")
                os.makedirs(bd, exist_ok=True)
                if not os.path.isfile(os.path.join(bd, "boundary")):
                    open(os.path.join(bd, "boundary"), "w").write("0()\n")
            shutil.rmtree(os.path.join(cdst, "0"), ignore_errors=True)
            shutil.rmtree(os.path.join(cdst, SPLIT_BYPRODUCT_DIR), ignore_errors=True)
            for rel in ("cellToRegion", "core/cellToRegion", "housing/cellToRegion"):
                p = os.path.join(cdst, "0", rel)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w").write(MAP)

        # (1) BEFORE the relocation the UNCHANGED guard already refuses -- this
        #     is the block the mesh stage exists to clear, and it is real.
        make_split_tree()
        try:
            physics("T21_CYL_c"); chk(False, "physics should refuse a tree holding 0/")
        except SystemExit as e:
            chk(e.code == 2, "UNCHANGED guard REFUSES the split tree's 0/ (exit %s)" % e.code)

        # (2) the mesh stage relocates its own byproduct; 0/ is gone, nothing deleted
        chk(postsplit("T21_CYL_c") == 0, "--postsplit relocates the cellToRegion byproduct")
        chk(not os.path.exists(os.path.join(cdst, "0")), "0/ no longer exists after --postsplit")
        for rel in ("cellToRegion", "core/cellToRegion", "housing/cellToRegion"):
            chk(os.path.isfile(os.path.join(cdst, SPLIT_BYPRODUCT_DIR, rel)),
                "byproduct PRESERVED at %s/%s (moved, never deleted)" % (SPLIT_BYPRODUCT_DIR, rel))
        chk(postsplit("T21_CYL_c") == 0, "--postsplit is idempotent: no 0/, nothing to do")

        # (3) PLANT A REAL FIELD IN 0/.  The relocation step must REFUSE it and
        #     must not move or delete it.
        shutil.rmtree(os.path.join(cdst, SPLIT_BYPRODUCT_DIR), ignore_errors=True)
        make_split_tree()
        planted = os.path.join(cdst, "0", "housing", "T")
        open(planted, "w").write(FIELD_T)
        try:
            postsplit("T21_CYL_c"); chk(False, "--postsplit should refuse a planted field")
        except SystemExit as e:
            chk(e.code == 2, "PLANTED 0/housing/T: --postsplit REFUSES (exit %s)" % e.code)
        chk(os.path.isfile(planted), "planted 0/housing/T STILL ON DISK -- nothing deleted")
        chk(os.path.isdir(os.path.join(cdst, "0")), "0/ still present -- nothing moved")

        # (4) AND THE GUARD ITSELF STILL FIRES.  This is the clause the repair
        #     is worthless without.
        try:
            physics("T21_CYL_c"); chk(False, "the age guard FAILED TO FIRE on a planted field")
        except SystemExit as e:
            chk(e.code == 2, "PLANTED 0/housing/T: THE AGE GUARD STILL FIRES (exit %s)" % e.code)

        # (5) and it fires on a numeric time directory too
        shutil.rmtree(os.path.join(cdst, "0"), ignore_errors=True)
        os.makedirs(os.path.join(cdst, "3000"), exist_ok=True)
        open(os.path.join(cdst, "3000", "T"), "w").write(FIELD_T)
        try:
            physics("T21_CYL_c"); chk(False, "the age guard FAILED TO FIRE on time dir 3000")
        except SystemExit as e:
            chk(e.code == 2, "PLANTED time directory 3000: THE AGE GUARD STILL FIRES (exit %s)" % e.code)
        try:
            postsplit("T21_CYL_c"); chk(False, "--postsplit should refuse a tree holding 3000/")
        except SystemExit as e:
            chk(e.code == 2, "PLANTED time directory 3000: --postsplit REFUSES (exit %s)" % e.code)
    finally:
        HERE = real
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nSELFTEST %s" % ("PASSED" if ok[0] else "FAILED"))
    return 0 if ok[0] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
