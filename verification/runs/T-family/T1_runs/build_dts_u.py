#!/usr/bin/env python3
"""Build the UNHEATED-UPSTREAM ladders registered at
DIAGNOSTIC_PREDICTION.md:786 ("NEXT TEST, REGISTERED BEFORE IT IS BUILT,
2026-08-21", frozen at commit 6a0d7f45d5bc19a3fa06fffac4a20c2a3ecbf82c):

    D_Ts_Re25_U_c/m/f   (Re =  25, Pe = 17.75)
    L_Ts_U_c/m/f        (Re = 100, Pe = 71.00)

THE REGISTERED DESIGN, QUOTED FROM THE FROZEN TEXT AND NOT PARAPHRASED:
"the parabolic inlet moved to x = -10 D, the wall ADIABATIC for -10 D < x < 0
and at 310 K for x > 0, T_in = 300 K at the upstream inlet, stations unchanged
(measured from x = 0)".  Six cases.

Every other quantity is the parent chain's, byte-for-byte where a byte copy is
possible: `constant/` and `system/fvSchemes`, `system/fvSolution` are COPIED
from the corresponding parent case (D_Ts_Re25_<lvl> for the Re = 25 ladder,
L_Ts_<lvl> for the Re = 100 ladder), so nu, Pr, the turbulence dictionary, the
zero gravity vector and every scheme and solver setting are inherited and not
retyped.  `system/controlDict` is copied and ONE line is changed: endTime.

WHAT THIS BUILDER REGISTERS THAT THE FROZEN TEXT DID NOT, all of it BEFORE any
of the six run directories exists (CLAUDE.md rule 2 permits a pre-first-compute
amendment; the amendment appended to DIAGNOSTIC_PREDICTION.md states the
condition and names the six directories that do not exist):

  * MESH.  The parent radial ladder nr = 20 / 32 / 51 is UNCHANGED.  The axial
    count becomes nx = 12 nr = 240 / 384 / 612 over the 60 D domain, so the
    axial cell size is uniform across x = 0 (the plane whose conduction flux
    the registered predictions read), the upstream 10 D is an EXACT integer
    number of cells (nx/6 = 40 / 64 / 102), and the ladder's own level ratios
    are exactly the parent's (1.6 and 1.59375, the parent's nr ratios).
  * endTime 40000 against the parent's 30000.  Ground: the domain is 1.2x
    longer, so the same convergence per unit length needs about 1.2x the
    iterations; 40000 is 1.33x and leaves margin.  writeInterval 2000, kept
    STRICTLY less than endTime (L-140).
  * TWO WALL PATCHES.  `wall_adiabatic` (zeroGradient T) for -10 D < x < 0 and
    `wall_hot` (fixedValue 310 K) for x > 0.  The 300 K / 310 K corner the
    registered text exists to remove is gone by construction.

THE INLET.  u_x(r_c) = s * 2 U_b (1 - (r_c/R_wall)^2) evaluated at the mesh's
OWN inlet face centroids, with the single scalar s chosen so the DISCRETE flow
rate is exact: sum_f u_f A_f == U_b sum_f A_f.  R_wall is max y over the mesh
points (analyse_t1c.wall_radius's rule).  This is build_d_ts_p.py's
construction, re-derived here from the mesh this builder wrote.

NO `assert` (L-332).  Every refusal is sys.exit(2) or a REFUSE return.
It writes dictionaries, `0.orig/` and NOTHING ELSE; it NEVER writes `0/` and it
NEVER writes a time directory.

Usage: python3 build_dts_u.py [--root DIR] [--cases NAME ...] [--selftest]
Exit: 0 ok, 2 REFUSAL.
"""
import argparse
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXIT_OK, EXIT_REFUSE = 0, 2

# ---- registered constants, inherited from build_t1c.py -----------------------
D = 0.02
R = D / 2.0
NU = 1.5e-05
WEDGE_DEG = 5.0
T_IN = 300.0
T_WALL = 310.0
X_UP = -10.0 * D                 # -0.2 m, the registered upstream inlet plane
X_DN = +50.0 * D                 # +1.0 m, the parent outlet plane, unchanged
END_TIME = 40000
WRITE_INTERVAL = 2000
NR = {"c": 20, "m": 32, "f": 51}          # parent radial ladder, UNCHANGED
LADDERS = (("D_Ts_Re25_U", 25.0, "D_Ts_Re25_{lvl}"),
           ("L_Ts_U", 100.0, "L_Ts_{lvl}"))
CASES = [("%s_%s" % (tag, lvl), tag, Re, parent.format(lvl=lvl), lvl)
         for tag, Re, parent in LADDERS for lvl in ("c", "m", "f")]


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def nx_of(lvl):
    """Axial cells over the 60 D domain, and the upstream/downstream split."""
    nx = 12 * NR[lvl]
    return nx, nx // 6, nx - nx // 6


def header(cls, obj, loc):
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            "    class       %s;\n    location    \"%s\";\n    object      %s;\n}\n\n"
            % (cls, loc, obj))


# --------------------------------------------------------------- the mesh
def block_mesh(lvl):
    nx, nup, ndn = nx_of(lvl)
    nr = NR[lvl]
    half = math.radians(WEDGE_DEG / 2.0)
    rw = R * math.cos(half)
    dz = R * math.sin(half)
    v = [(X_UP, 0.0, 0.0), (0.0, 0.0, 0.0), (X_DN, 0.0, 0.0),
         (X_UP, rw, -dz), (0.0, rw, -dz), (X_DN, rw, -dz),
         (X_UP, rw, +dz), (0.0, rw, +dz), (X_DN, rw, +dz)]
    L = [header("dictionary", "blockMeshDict", "system"),
         "scale 1;\n\nvertices\n(\n"]
    for (x, y, z) in v:
        L.append("    (%.8f      %.10f      %.10f)\n" % (x, y, z))
    L.append(");\n\nblocks\n(\n")
    # the parent's vertex order: (axis_in axis_out back_out back_in
    #                             axis_in axis_out front_out front_in)
    L.append("    hex (0 1 4 3 0 1 7 6) (%d %d 1) simpleGrading (1 1 1)\n" % (nup, nr))
    L.append("    hex (1 2 5 4 1 2 8 7) (%d %d 1) simpleGrading (1 1 1)\n" % (ndn, nr))
    L.append(");\n\nedges ();\n\nboundary\n(\n")
    L.append("    inlet          { type patch; faces ( (0 3 6 0) ); }\n")
    L.append("    outlet         { type patch; faces ( (2 5 8 2) ); }\n")
    L.append("    wall_adiabatic { type wall;  faces ( (3 4 7 6) ); }\n")
    L.append("    wall_hot       { type wall;  faces ( (4 5 8 7) ); }\n")
    L.append("    front          { type wedge; faces ( (0 1 7 6) (1 2 8 7) ); }\n")
    L.append("    back           { type wedge; faces ( (0 1 4 3) (1 2 5 4) ); }\n")
    L.append("    axis           { type empty; faces ( ); }\n")
    L.append(");\n\nmergePatchPairs ();\n")
    return "".join(L)


# ------------------------------------------------ a self-contained polyMesh reader
def _list_body(path):
    txt = open(path, errors="replace").read()
    m = re.search(r"\n(\d+)\s*\n\(\s*\n(.*)\n\)\s*\n", txt, re.S)
    if not m:
        refuse("could not parse a FoamFile list in %s" % path)
    return int(m.group(1)), m.group(2)


def read_points(path):
    n, body = _list_body(path)
    pts = [tuple(float(x) for x in t.split()) for t in re.findall(r"\(([^()]*)\)", body)[:n]]
    if len(pts) != n:
        refuse("points: declared %d, parsed %d in %s" % (n, len(pts), path))
    return pts


def read_faces(path):
    n, body = _list_body(path)
    out = []
    for k, t in re.findall(r"(\d+)\s*\(([^()]*)\)", body)[:n]:
        ids = [int(x) for x in t.split()]
        if len(ids) != int(k):
            refuse("face declares %s vertices and lists %d in %s" % (k, len(ids), path))
        out.append(ids)
    if len(out) != n:
        refuse("faces: declared %d, parsed %d in %s" % (n, len(out), path))
    return out


def read_boundary(path):
    txt = open(path, errors="replace").read()
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^{}]*)\}", txt):
        nf = re.search(r"nFaces\s+(\d+)\s*;", m.group(2))
        sf = re.search(r"startFace\s+(\d+)\s*;", m.group(2))
        if nf and sf:
            out[m.group(1)] = dict(nFaces=int(nf.group(1)), startFace=int(sf.group(1)))
    return out


def face_area_centroid(pts, ids):
    """Newell area vector and the area-weighted centroid of a planar polygon."""
    n = len(ids)
    c0 = [sum(pts[i][k] for i in ids) / n for k in range(3)]
    ax = ay = az = 0.0
    cx = cy = cz = 0.0
    tot = 0.0
    for j in range(n):
        p = pts[ids[j]]
        q = pts[ids[(j + 1) % n]]
        u = (p[0] - c0[0], p[1] - c0[1], p[2] - c0[2])
        v = (q[0] - c0[0], q[1] - c0[1], q[2] - c0[2])
        nx_ = u[1] * v[2] - u[2] * v[1]
        ny_ = u[2] * v[0] - u[0] * v[2]
        nz_ = u[0] * v[1] - u[1] * v[0]
        a = 0.5 * math.sqrt(nx_ * nx_ + ny_ * ny_ + nz_ * nz_)
        ax += 0.5 * nx_; ay += 0.5 * ny_; az += 0.5 * nz_
        tc = [(c0[k] + p[k] + q[k]) / 3.0 for k in range(3)]
        cx += a * tc[0]; cy += a * tc[1]; cz += a * tc[2]
        tot += a
    if tot <= 0.0:
        refuse("degenerate face")
    return (ax, ay, az), (cx / tot, cy / tot, cz / tot)


def inlet_profile(case, Re):
    """u_x at every inlet face centroid, PATCH FACE ORDER, exact discrete flow."""
    pm = os.path.join(case, "constant", "polyMesh")
    pts = read_points(os.path.join(pm, "points"))
    faces = read_faces(os.path.join(pm, "faces"))
    bnd = read_boundary(os.path.join(pm, "boundary"))
    if "inlet" not in bnd:
        refuse("no inlet patch in %s" % pm)
    rw = max(p[1] for p in pts)
    ub = Re * NU / D
    s0, n = bnd["inlet"]["startFace"], bnd["inlet"]["nFaces"]
    areas, prof = [], []
    for f in range(s0, s0 + n):
        A, C = face_area_centroid(pts, faces[f])
        a = math.sqrt(A[0] ** 2 + A[1] ** 2 + A[2] ** 2)
        rc = math.hypot(C[1], C[2])
        areas.append(a)
        prof.append(2.0 * ub * (1.0 - (rc / rw) ** 2))
    num = ub * sum(areas)
    den = sum(u * a for u, a in zip(prof, areas))
    if den <= 0.0:
        refuse("inlet quadrature is non-positive; the profile cannot be scaled")
    s = num / den
    return [s * u for u in prof], areas, s, rw, ub


# -------------------------------------------------------------- the fields
def field_U(prof, ub):
    return (header("volVectorField", "U", "0") +
            "dimensions      [0 1 -1 0 0 0 0];\ninternalField   uniform (%.17g 0 0);\n"
            "boundaryField\n{\n"
            "    inlet   { type fixedValue; value nonuniform List<vector>\n%d\n(\n%s\n)\n; }\n"
            "    outlet         { type zeroGradient; }\n"
            "    wall_adiabatic { type noSlip; }\n"
            "    wall_hot       { type noSlip; }\n"
            "    front   { type wedge; }\n    back    { type wedge; }\n}\n"
            % (ub, len(prof), "\n".join("(%.17g 0 0)" % u for u in prof)))


def field_T():
    return (header("volScalarField", "T", "0") +
            "dimensions      [0 0 0 1 0 0 0];\ninternalField   uniform %g;\n"
            "boundaryField\n{\n"
            "    inlet          { type fixedValue; value uniform %g; }\n"
            "    outlet         { type zeroGradient; }\n"
            "    wall_adiabatic { type zeroGradient; }\n"
            "    wall_hot       { type fixedValue; value uniform %g; }\n"
            "    front   { type wedge; }\n    back    { type wedge; }\n}\n"
            % (T_IN, T_IN, T_WALL))


def field_p_rgh():
    return (header("volScalarField", "p_rgh", "0") +
            "dimensions      [0 2 -2 0 0 0 0];\ninternalField   uniform 0;\n"
            "boundaryField\n{\n"
            "    inlet          { type zeroGradient; }\n"
            "    outlet         { type fixedValue; value uniform 0; }\n"
            "    wall_adiabatic { type zeroGradient; }\n"
            "    wall_hot       { type zeroGradient; }\n"
            "    front   { type wedge; }\n    back    { type wedge; }\n}\n")


def field_alphat():
    return (header("volScalarField", "alphat", "0") +
            "dimensions      [0 2 -1 0 0 0 0];\ninternalField   uniform 0;\n"
            "boundaryField\n{\n"
            "    inlet          { type calculated; value uniform 0; }\n"
            "    outlet         { type calculated; value uniform 0; }\n"
            "    wall_adiabatic { type fixedValue; value uniform 0; }\n"
            "    wall_hot       { type fixedValue; value uniform 0; }\n"
            "    front   { type wedge; }\n    back    { type wedge; }\n}\n")


# --------------------------------------------------------------- the build
def build(root, name, tag, Re, parent, lvl, foam_bashrc="/usr/lib/openfoam/openfoam2606/etc/bashrc"):
    case = os.path.join(root, name)
    par = os.path.join(root, parent)
    if os.path.isdir(os.path.join(case, "0")):
        print("REFUSE: %s already has a 0/ directory" % case)
        return EXIT_REFUSE
    if any(re.fullmatch(r"\d+(\.\d+)?", n) and float(n) != 0.0
           for n in (os.listdir(case) if os.path.isdir(case) else [])):
        print("REFUSE: %s already has a solution time directory" % case)
        return EXIT_REFUSE
    if not os.path.isdir(par):
        print("REFUSE: parent case %s is absent; this builder inherits rather than retypes" % par)
        return EXIT_REFUSE
    os.makedirs(os.path.join(case, "system"), exist_ok=True)
    os.makedirs(os.path.join(case, "constant"), exist_ok=True)
    os.makedirs(os.path.join(case, "0.orig"), exist_ok=True)
    for f in ("g", "transportProperties", "turbulenceProperties"):
        shutil.copy2(os.path.join(par, "constant", f), os.path.join(case, "constant", f))
    for f in ("fvSchemes", "fvSolution"):
        shutil.copy2(os.path.join(par, "system", f), os.path.join(case, "system", f))
    cd = open(os.path.join(par, "system", "controlDict")).read()
    cd2 = re.sub(r"^(\s*endTime\s+)\d+(\s*;)", r"\g<1>%d\g<2>" % END_TIME, cd, flags=re.M)
    cd2 = re.sub(r"^(\s*writeInterval\s+)\d+(\s*;)", r"\g<1>%d\g<2>" % WRITE_INTERVAL, cd2, flags=re.M)
    if cd2 == cd:
        print("REFUSE: the parent controlDict carries no endTime line to amend")
        return EXIT_REFUSE
    open(os.path.join(case, "system", "controlDict"), "w").write(cd2)
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(block_mesh(lvl))

    env = os.environ.copy()
    rc = subprocess.call(["bash", "-lc",
                          "set +u; . %s >/dev/null 2>&1; blockMesh -case %s > %s/log.blockMesh 2>&1"
                          % (foam_bashrc, case, case)], env=env)
    if rc != 0 or not os.path.isfile(os.path.join(case, "constant", "polyMesh", "owner")):
        print("REFUSE: blockMesh failed for %s (rc %s)" % (name, rc))
        return EXIT_REFUSE
    subprocess.call(["bash", "-lc",
                     "set +u; . %s >/dev/null 2>&1; checkMesh -case %s > %s/log.checkMesh.build 2>&1"
                     % (foam_bashrc, case, case)], env=env)

    prof, areas, s, rw, ub = inlet_profile(case, Re)
    q = sum(u * a for u, a in zip(prof, areas))
    qref = ub * sum(areas)
    if abs(q - qref) / qref > 1e-12:
        print("REFUSE: %s inlet discrete flow rate is off by %.3e relative" % (name, abs(q - qref) / qref))
        return EXIT_REFUSE
    open(os.path.join(case, "0.orig", "U"), "w").write(field_U(prof, ub))
    open(os.path.join(case, "0.orig", "T"), "w").write(field_T())
    open(os.path.join(case, "0.orig", "p_rgh"), "w").write(field_p_rgh())
    open(os.path.join(case, "0.orig", "alphat"), "w").write(field_alphat())

    nx, nup, ndn = nx_of(lvl)
    cells = NR[lvl] * nx
    open(os.path.join(case, "CASE.txt"), "w").write(
        "# unheated-upstream arm, registered DIAGNOSTIC_PREDICTION.md:786 "
        "(frozen 6a0d7f45d5bc19a3fa06fffac4a20c2a3ecbf82c)\n"
        "case %s\nladder %s\nlevel %s\nparent %s\nsolver buoyantBoussinesqSimpleFoam\n"
        "Re %.10g -\nU_bulk %.17g m/s\nnu %.10g m2/s\nPr 0.71 -\nD %.10g m\nR_wall %.12g m\n"
        "x_inlet %.10g m\nx_heat_start 0 m\nx_outlet %.10g m\n"
        "nr %d -\nnx %d -\nnx_upstream %d -\nnx_downstream %d -\ncells %d -\n"
        "T_in %g K\nT_wall_hot %g K\nwall_upstream adiabatic\n"
        "endTime %d -\nwriteInterval %d -\ninlet_scale_s %.17g -\nnProcs 1 -\n"
        % (name, tag, lvl, parent, Re, ub, NU, D, rw, X_UP, X_DN,
           NR[lvl], nx, nup, ndn, cells, T_IN, T_WALL, END_TIME, WRITE_INTERVAL, s))
    print("built %-16s  %d cells (nr %d x nx %d = %d up + %d dn), U_b %.6g m/s, s = %.12f"
          % (name, cells, NR[lvl], nx, nup, ndn, ub, s))
    return EXIT_OK


def selftest():
    import ast
    import tempfile
    fails = []
    print("build_dts_u selftest:")
    # (i) the registered mesh arithmetic
    ok = True
    for lvl in ("c", "m", "f"):
        nx, nup, ndn = nx_of(lvl)
        good = (nx == 12 * NR[lvl] and nup * 6 == nx and nup + ndn == nx)
        ok = ok and good
        print("    [%s] level %s: nr %d, nx %d = %d upstream (10 D) + %d downstream (50 D), %d cells"
              % ("ok " if good else "FAIL", lvl, NR[lvl], nx, nup, ndn, NR[lvl] * nx))
    r21 = nx_of("m")[0] / nx_of("c")[0]
    r32 = nx_of("f")[0] / nx_of("m")[0]
    good = (abs(r21 - NR["m"] / NR["c"]) < 1e-12 and abs(r32 - NR["f"] / NR["m"]) < 1e-12)
    ok = ok and good
    print("  [%s] the axial ladder ratios %.5f / %.5f EQUAL the parent's radial ratios exactly"
          % ("ok " if ok else "FAIL", r21, r32))
    if not ok:
        fails.append("mesh-arithmetic")
    # (ii) the dict: two blocks, two wall patches, the inlet plane at -10 D
    bm = block_mesh("c")
    good = (bm.count("hex (") == 2 and "wall_adiabatic" in bm and "wall_hot" in bm
            and ("%.8f" % X_UP) in bm and "type empty" in bm)
    print("  [%s] blockMeshDict: 2 blocks, wall_adiabatic + wall_hot, inlet plane x = %.3g m"
          % ("ok " if good else "FAIL", X_UP))
    if not good:
        fails.append("dict")
    # (iii) the guards fire
    tmp = tempfile.mkdtemp(prefix="dtsu_")
    try:
        d = os.path.join(tmp, "D_Ts_Re25_U_c")
        os.makedirs(os.path.join(d, "0"))
        rc = build(tmp, "D_Ts_Re25_U_c", "D_Ts_Re25_U", 25.0, "D_Ts_Re25_c", "c")
        good = (rc == EXIT_REFUSE)
        print("  [%s] existing 0/ -> REFUSE (rc %s)" % ("ok " if good else "FAIL", rc))
        if not good:
            fails.append("guard0")
        shutil.rmtree(d)
        os.makedirs(os.path.join(d, "30000"))
        rc = build(tmp, "D_Ts_Re25_U_c", "D_Ts_Re25_U", 25.0, "D_Ts_Re25_c", "c")
        good = (rc == EXIT_REFUSE)
        print("  [%s] existing solution time directory 30000/ -> REFUSE (rc %s)"
              % ("ok " if good else "FAIL", rc))
        if not good:
            fails.append("guardT")
        shutil.rmtree(d)
        os.makedirs(d)
        rc = build(tmp, "D_Ts_Re25_U_c", "D_Ts_Re25_U", 25.0, "NO_SUCH_PARENT", "c")
        good = (rc == EXIT_REFUSE)
        print("  [%s] absent parent case -> REFUSE (this builder inherits, it does not retype) (rc %s)"
              % ("ok " if good else "FAIL", rc))
        if not good:
            fails.append("guardP")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # (iv) the polyMesh reader agrees with the campaign's frozen reader on a PARENT mesh
    par = os.path.join(HERE, "L_Ts_c", "constant", "polyMesh")
    if os.path.isdir(par):
        sys.path.insert(0, HERE)
        try:
            import analyse_dts as DTS
            a = read_points(os.path.join(par, "points"))
            b = DTS.read_points(os.path.join(par, "points"))
            fa = read_faces(os.path.join(par, "faces"))
            fb = DTS.read_faces(os.path.join(par, "faces"))
            good = (a == b and fa == fb and len(a) > 0)
            print("  [%s] this file's polyMesh reader == analyse_dts's on L_Ts_c (%d points, %d faces) "
                  "-- two routes, one answer" % ("ok " if good else "FAIL", len(a), len(fa)))
            if not good:
                fails.append("reader")
        except Exception as e:                                    # noqa: BLE001
            print("  [FAIL] cross-check against analyse_dts raised %r" % (e,))
            fails.append("reader")
    else:
        print("  [FAIL] L_Ts_c is absent; the reader cross-check could not run")
        fails.append("reader")
    # (v) the exact-flow-rate solve, on a synthetic uniform annular patch
    rw = 0.0099904822
    ub = 0.075
    n = 20
    areas, prof = [], []
    for j in range(n):
        r0, r1 = rw * j / n, rw * (j + 1) / n
        areas.append(r1 * r1 - r0 * r0)
        rc_ = (2.0 / 3.0) * (r1 * r1 + r1 * r0 + r0 * r0) / (r1 + r0)
        prof.append(2.0 * ub * (1.0 - (rc_ / rw) ** 2))
    s = ub * sum(areas) / sum(u * a for u, a in zip(prof, areas))
    q = sum(s * u * a for u, a in zip(prof, areas))
    good = abs(q - ub * sum(areas)) / (ub * sum(areas)) < 1e-15
    print("  [%s] the inlet scale solve makes the DISCRETE flow rate exact (residual %.2e, s = %.9f)"
          % ("ok " if good else "FAIL", abs(q - ub * sum(areas)) / (ub * sum(areas)), s))
    if not good:
        fails.append("flowrate")
    src = open(__file__).read()
    n0 = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(src + "\nassert 1\n")))
    good = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (counter sees a planted assert: %d)"
          % ("ok " if good else "FAIL", n0, n1))
    if not good:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--cases", nargs="*", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    rc = 0
    for name, tag, Re, parent, lvl in CASES:
        if a.cases and name not in a.cases:
            continue
        rc = max(rc, build(os.path.abspath(a.root), name, tag, Re, parent, lvl))
    return rc


if __name__ == "__main__":
    sys.exit(main())
