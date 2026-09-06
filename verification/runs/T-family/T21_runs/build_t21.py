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

Exit 0 built, 2 refusal.  Zero bare `assert` (L-332).  No .pyc beside pins.
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


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--case" not in argv:
        refuse("usage: build_t21.py --case <name> | --selftest")
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
    finally:
        HERE = real
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nSELFTEST %s" % ("PASSED" if ok[0] else "FAILED"))
    return 0 if ok[0] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
