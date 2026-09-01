#!/usr/bin/env python3
"""READ-ONLY diagnostic on the already-solved T23G levels.

Opens nothing for writing inside the run tree.  Computes, from the polyMesh and
the endTime fields that are already on disk:

  * cell volumes (divergence theorem over the face loop of each cell)
  * the core's VOLUME-AVERAGED temperature          -- Sanaa 2026-09-01 (d)
  * the housing surface heat flux on housing_to_fluid  -- Sanaa 2026-09-01 (d)
  * y+ on every fluid wall patch                     -- Sanaa 2026-09-01 "record y+"
  * first-cell wall-normal spacing per patch, per level  (mesh similarity, (b))

No solver is launched and no file in the run tree is written.
"""
import os
import re
import sys
import math

ROOT = "/home/ubuntu/Certonomous/verification/runs/T-family/T23G_runs"
LEVELS = ["T23G_C", "T23G_M", "T23G_F"]
ENDTIME = "10000"

NU = 1.8e-05 / 1.2          # fluid kinematic viscosity, m2/s  (mu/rho, both const)
KAPPA_HOUSING = 167.0       # W/m K, constIso


# --------------------------------------------------------------------------
# OpenFOAM ASCII readers.  Deliberately small and explicit.
# --------------------------------------------------------------------------

def _strip_header(txt):
    i = txt.find("// * * *")
    j = txt.find("\n", i)
    return txt[j + 1:]


def read_scalar_list(path):
    """A labelList / scalarField file: <n>\n(\n v\n v\n ... )"""
    txt = _strip_header(open(path).read())
    m = re.search(r"(\d+)\s*\(", txt)
    n = int(m.group(1))
    body = txt[m.end():]
    end = body.index(")")
    vals = body[:end].split()
    assert len(vals) == n, (path, len(vals), n)
    return [float(v) for v in vals]


def read_points(path):
    txt = _strip_header(open(path).read())
    m = re.search(r"(\d+)\s*\(", txt)
    n = int(m.group(1))
    body = txt[m.end():]
    pts = re.findall(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)", body)
    pts = pts[:n]
    assert len(pts) == n, (path, len(pts), n)
    return [(float(a), float(b), float(c)) for a, b, c in pts]


def read_faces(path):
    txt = _strip_header(open(path).read())
    m = re.search(r"(\d+)\s*\(", txt)
    n = int(m.group(1))
    body = txt[m.end():]
    faces = []
    i = 0
    L = len(body)
    while len(faces) < n:
        j = body.index("(", i)
        cnt = int(body[i:j].split()[-1])
        k = body.index(")", j)
        idx = [int(x) for x in body[j + 1:k].split()]
        assert len(idx) == cnt
        faces.append(idx)
        i = k + 1
    return faces


def read_boundary(path):
    txt = _strip_header(open(path).read())
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^}]*)\}", txt):
        name, blk = m.group(1), m.group(2)
        nf = re.search(r"nFaces\s+(\d+)", blk)
        sf = re.search(r"startFace\s+(\d+)", blk)
        ty = re.search(r"type\s+(\w+)", blk)
        if nf and sf:
            out[name] = dict(nFaces=int(nf.group(1)),
                             startFace=int(sf.group(1)),
                             type=ty.group(1) if ty else "?")
    return out


def read_field(path):
    """Returns (internal list, {patch: ('uniform'|'nonuniform', data)}) for a
    volScalarField or volVectorField in ASCII."""
    txt = open(path).read()
    body = _strip_header(txt)
    vec = "volVectorField" in txt

    def parse_block(s):
        s = s.strip()
        if s.startswith("uniform"):
            rest = s[len("uniform"):].strip().rstrip(";")
            if vec:
                v = [float(x) for x in rest.strip("()").split()]
                return ("uniform", tuple(v))
            return ("uniform", float(rest))
        m = re.search(r"nonuniform[^\d]*(\d+)\s*\(", s)
        if not m:
            m2 = re.search(r"nonuniform\s+List<\w+>\s*0\s*\(\s*\)", s)
            if m2:
                return ("nonuniform", [])
            return ("other", s[:60])
        n = int(m.group(1))
        rest = s[m.end():]
        if vec:
            trip = re.findall(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)", rest)[:n]
            return ("nonuniform", [(float(a), float(b), float(c)) for a, b, c in trip])
        end = rest.index(")")
        vals = [float(x) for x in rest[:end].split()]
        assert len(vals) == n
        return ("nonuniform", vals)

    mi = re.search(r"internalField\s+", body)
    bstart = body.index("boundaryField")
    internal = parse_block(body[mi.end():bstart])

    # boundary blocks: brace-match
    bf = {}
    s = body[bstart:]
    o = s.index("{")
    depth = 0
    i = o
    while True:
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    inner = s[o + 1:i]
    j = 0
    while True:
        m = re.compile(r"([\w.\"]+)\s*\{").search(inner, j)
        if not m:
            break
        name = m.group(1)
        d = 1
        k = m.end()
        while d:
            if inner[k] == "{":
                d += 1
            elif inner[k] == "}":
                d -= 1
            k += 1
        blk = inner[m.end():k - 1]
        mv = re.search(r"\bvalue\s+", blk)
        if mv:
            bf[name] = parse_block(blk[mv.end():])
        else:
            bf[name] = ("no-value", blk[:60])
        j = k
    return internal, bf


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------

def face_geom(pts, f):
    """OpenFOAM's face centre / area vector (fan decomposition about the
    average point).  Matches primitiveMeshFaceCentresAndAreas.C."""
    n = len(f)
    if n == 3:
        a, b, c = (pts[i] for i in f)
        ctr = ((a[0] + b[0] + c[0]) / 3.0, (a[1] + b[1] + c[1]) / 3.0,
               (a[2] + b[2] + c[2]) / 3.0)
        u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        ar = (0.5 * (u[1] * v[2] - u[2] * v[1]),
              0.5 * (u[2] * v[0] - u[0] * v[2]),
              0.5 * (u[0] * v[1] - u[1] * v[0]))
        return ctr, ar
    sx = sy = sz = 0.0
    for i in f:
        p = pts[i]
        sx += p[0]; sy += p[1]; sz += p[2]
    pAvg = (sx / n, sy / n, sz / n)
    ctr = [0.0, 0.0, 0.0]
    ar = [0.0, 0.0, 0.0]
    asum = 0.0
    for i in range(n):
        p1 = pts[f[i]]
        p2 = pts[f[(i + 1) % n]]
        c = ((p1[0] + p2[0] + pAvg[0]) / 3.0, (p1[1] + p2[1] + pAvg[1]) / 3.0,
             (p1[2] + p2[2] + pAvg[2]) / 3.0)
        u = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
        v = (pAvg[0] - p1[0], pAvg[1] - p1[1], pAvg[2] - p1[2])
        n_ = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
              u[0] * v[1] - u[1] * v[0])
        a = math.sqrt(n_[0] ** 2 + n_[1] ** 2 + n_[2] ** 2)
        for k in range(3):
            ctr[k] += a * c[k]
            ar[k] += 0.5 * n_[k]
        asum += a
    if asum > 1e-300:
        ctr = [x / asum for x in ctr]
    else:
        ctr = list(pAvg)
    return tuple(ctr), tuple(ar)


class Mesh(object):
    def __init__(self, case, region):
        pm = os.path.join(case, "constant", region, "polyMesh")
        self.points = read_points(os.path.join(pm, "points"))
        self.faces = read_faces(os.path.join(pm, "faces"))
        self.owner = [int(x) for x in read_scalar_list(os.path.join(pm, "owner"))]
        self.neigh = [int(x) for x in read_scalar_list(os.path.join(pm, "neighbour"))]
        self.boundary = read_boundary(os.path.join(pm, "boundary"))
        self.nCells = max(max(self.owner), max(self.neigh)) + 1
        self.fc = [None] * len(self.faces)
        self.fa = [None] * len(self.faces)
        for i, f in enumerate(self.faces):
            self.fc[i], self.fa[i] = face_geom(self.points, f)
        self._cell_geom()

    def _cell_geom(self):
        n = self.nCells
        # estimated centre = average of face centres
        cEst = [[0.0, 0.0, 0.0] for _ in range(n)]
        cnt = [0] * n
        def add(c, i):
            cEst[c][0] += self.fc[i][0]; cEst[c][1] += self.fc[i][1]
            cEst[c][2] += self.fc[i][2]; cnt[c] += 1
        for i in range(len(self.faces)):
            add(self.owner[i], i)
            if i < len(self.neigh):
                add(self.neigh[i], i)
        for c in range(n):
            for k in range(3):
                cEst[c][k] /= cnt[c]
        V = [0.0] * n
        ctr = [[0.0, 0.0, 0.0] for _ in range(n)]
        def acc(c, i, sgn):
            fcv = self.fc[i]; fav = self.fa[i]
            d = (fcv[0] - cEst[c][0], fcv[1] - cEst[c][1], fcv[2] - cEst[c][2])
            pyr3Vol = sgn * (fav[0] * d[0] + fav[1] * d[1] + fav[2] * d[2])
            if pyr3Vol < 0:
                pyr3Vol = max(pyr3Vol, -1e-300) if pyr3Vol > -1e-300 else pyr3Vol
            pc = (0.75 * fcv[0] + 0.25 * cEst[c][0],
                  0.75 * fcv[1] + 0.25 * cEst[c][1],
                  0.75 * fcv[2] + 0.25 * cEst[c][2])
            V[c] += pyr3Vol
            for k in range(3):
                ctr[c][k] += pyr3Vol * pc[k]
        for i in range(len(self.faces)):
            acc(self.owner[i], i, 1.0)
            if i < len(self.neigh):
                acc(self.neigh[i], i, -1.0)
        for c in range(n):
            if abs(V[c]) > 1e-300:
                for k in range(3):
                    ctr[c][k] /= V[c]
            else:
                ctr[c] = list(cEst[c])
            V[c] /= 3.0
        self.V = V
        self.C = ctr


# --------------------------------------------------------------------------

def expand(blockv, n, zero=None):
    kind, data = blockv
    if kind == "uniform":
        return [data] * n
    if kind == "nonuniform" and len(data) == n:
        return data
    # a block this reader cannot parse is REFUSED, never silently zeroed.
    raise ValueError("unparsed field block kind=%r n_expected=%d got=%r"
                     % (kind, n, str(data)[:80]))


def analyse(case):
    out = {}
    # ---- core volume-averaged T ------------------------------------------
    mc = Mesh(case, "core")
    Ti, _ = read_field(os.path.join(case, ENDTIME, "core", "T"))
    Tc = expand(Ti, mc.nCells)
    Vtot = sum(mc.V)
    out["core_cells"] = mc.nCells
    out["core_V"] = Vtot
    out["core_volavg_T"] = sum(v * t for v, t in zip(mc.V, Tc)) / Vtot
    out["core_maxT"] = max(Tc)

    # ---- housing: volume-avg T and the surface heat flux on housing_to_fluid
    mh = Mesh(case, "housing")
    Thi, Thb = read_field(os.path.join(case, ENDTIME, "housing", "T"))
    Th = expand(Thi, mh.nCells)
    Vh = sum(mh.V)
    out["housing_cells"] = mh.nCells
    out["housing_volavg_T"] = sum(v * t for v, t in zip(mh.V, Th)) / Vh
    out["housing_maxT"] = max(Th)

    pname = None
    for k in mh.boundary:
        if "fluid" in k:
            pname = k
    b = mh.boundary[pname]
    nf, sf = b["nFaces"], b["startFace"]
    Tw = expand(Thb[pname], nf)
    Q = 0.0
    Aatot = 0.0
    dsum = 0.0
    for i in range(nf):
        fi = sf + i
        c = mh.owner[fi]
        fa = mh.fa[fi]
        A = math.sqrt(fa[0] ** 2 + fa[1] ** 2 + fa[2] ** 2)
        d = (mh.fc[fi][0] - mh.C[c][0], mh.fc[fi][1] - mh.C[c][1],
             mh.fc[fi][2] - mh.C[c][2])
        # wall-normal distance = |d . n|
        nhat = (fa[0] / A, fa[1] / A, fa[2] / A)
        dn = abs(d[0] * nhat[0] + d[1] * nhat[1] + d[2] * nhat[2])
        gradn = (Tw[i] - Th[c]) / dn            # outward normal derivative
        Q += -KAPPA_HOUSING * gradn * A          # W leaving the solid through the patch
        Aatot += A
        dsum += dn * A
    out["housing_patch"] = pname
    out["housing_patch_nFaces"] = nf
    out["housing_patch_area"] = Aatot
    out["housing_wall_heat_W"] = Q
    out["housing_wall_flux_Wm2"] = Q / Aatot
    out["housing_first_cell_dn"] = dsum / Aatot
    out["housing_patch_areaAvg_T"] = sum(Tw[i] * math.sqrt(sum(x*x for x in mh.fa[sf+i]))
                                         for i in range(nf)) / Aatot

    # ---- y+ on the fluid walls -------------------------------------------
    mf = Mesh(case, "fluid")
    Ui, Ub = read_field(os.path.join(case, ENDTIME, "fluid", "U"))
    Uc = expand(Ui, mf.nCells)
    nuti, nutb = read_field(os.path.join(case, ENDTIME, "fluid", "nut"))
    nutc = expand(nuti, mf.nCells)
    yp = {}
    for pn, pb in mf.boundary.items():
        if pb["type"] not in ("wall", "mappedWall"):
            continue
        nf, sf = pb["nFaces"], pb["startFace"]
        # noSlip carries no `value` entry; U_wall is IDENTICALLY zero by the
        # boundary condition's own definition, so it is named here, not guessed.
        if Ub[pn][0] == "no-value" and "noSlip" in str(Ub[pn][1]):
            Uw = [(0.0, 0.0, 0.0)] * nf
        else:
            Uw = expand(Ub[pn], nf)
        nutw = expand(nutb[pn], nf)
        vals = []
        ds = []
        for i in range(nf):
            fi = sf + i
            c = mf.owner[fi]
            fa = mf.fa[fi]
            A = math.sqrt(fa[0] ** 2 + fa[1] ** 2 + fa[2] ** 2)
            nhat = (fa[0] / A, fa[1] / A, fa[2] / A)
            d = (mf.fc[fi][0] - mf.C[c][0], mf.fc[fi][1] - mf.C[c][1],
                 mf.fc[fi][2] - mf.C[c][2])
            y = abs(d[0] * nhat[0] + d[1] * nhat[1] + d[2] * nhat[2])
            uc = Uc[c]
            uw = Uw[i] if isinstance(Uw[i], tuple) else (0.0, 0.0, 0.0)
            rel = (uc[0] - uw[0], uc[1] - uw[1], uc[2] - uw[2])
            dot = rel[0] * nhat[0] + rel[1] * nhat[1] + rel[2] * nhat[2]
            tang = (rel[0] - dot * nhat[0], rel[1] - dot * nhat[1],
                    rel[2] - dot * nhat[2])
            Ut = math.sqrt(tang[0] ** 2 + tang[1] ** 2 + tang[2] ** 2)
            nuEff = NU + (nutw[i] if not isinstance(nutw[i], tuple) else 0.0)
            tau = nuEff * Ut / y                 # tau_w / rho
            utau = math.sqrt(max(tau, 0.0))
            vals.append(y * utau / NU)
            ds.append(y)
        if vals:
            yp[pn] = dict(min=min(vals), max=max(vals),
                          avg=sum(vals) / len(vals), n=len(vals),
                          y1_min=min(ds), y1_max=max(ds),
                          y1_avg=sum(ds) / len(ds))
    out["yplus"] = yp
    out["fluid_cells"] = mf.nCells
    return out


def order(v):
    """Roache observed order for a constant refinement ratio r=2 triple
    (coarse, medium, fine)."""
    e32 = v[0] - v[1]
    e21 = v[1] - v[2]
    if e21 == 0 or e32 / e21 <= 0:
        return None, e32, e21
    return math.log(abs(e32 / e21)) / math.log(2.0), e32, e21


if __name__ == "__main__":
    res = {}
    for lv in LEVELS:
        sys.stderr.write("... %s\n" % lv)
        res[lv] = analyse(os.path.join(ROOT, lv))

    print("=" * 74)
    print("Y+ AND FIRST-CELL SPACING, computed from the fields on disk")
    print("=" * 74)
    pats = sorted(res[LEVELS[0]]["yplus"])
    for p in pats:
        print("\npatch %s" % p)
        print("  %-8s %8s %10s %10s %10s %12s" %
              ("level", "nFaces", "y+min", "y+avg", "y+max", "y1_avg[m]"))
        for lv in LEVELS:
            d = res[lv]["yplus"][p]
            print("  %-8s %8d %10.4f %10.4f %10.4f %12.4e" %
                  (lv, d["n"], d["min"], d["avg"], d["max"], d["y1_avg"]))
        r1 = res[LEVELS[0]]["yplus"][p]["y1_avg"] / res[LEVELS[1]]["yplus"][p]["y1_avg"]
        r2 = res[LEVELS[1]]["yplus"][p]["y1_avg"] / res[LEVELS[2]]["yplus"][p]["y1_avg"]
        print("  first-cell spacing refinement ratio  C/M = %.6f   M/F = %.6f"
              "   (similar mesh requires both = 2.000000)" % (r1, r2))

    print()
    print("=" * 74)
    print("SMOOTHER ORDER-STUDY QUANTITIES  (Sanaa 2026-09-01 candidate (d))")
    print("=" * 74)
    rows = [
        ("Q4  core volume-avg T  [K]", "core_volavg_T", 288.0),
        ("Q5  housing wall heat  [W]", "housing_wall_heat_W", 0.0),
        ("Q5b housing wall flux  [W/m2]", "housing_wall_flux_Wm2", 0.0),
        ("Q6  housing volume-avg T [K]", "housing_volavg_T", 288.0),
        ("Q1' housing max T      [K]", "housing_maxT", 288.0),
        ("Q3' core max T         [K]", "core_maxT", 288.0),
        ("Q2' housing patch areaAvg T [K]", "housing_patch_areaAvg_T", 288.0),
    ]
    print("%-32s %16s %16s %16s %9s" %
          ("quantity", LEVELS[0], LEVELS[1], LEVELS[2], "p"))
    for label, key, ref in rows:
        v = [res[lv][key] for lv in LEVELS]
        g = [x - ref for x in v]
        p, e32, e21 = order(g)
        print("%-32s %16.8f %16.8f %16.8f %9s" %
              (label, v[0], v[1], v[2], ("%.4f" % p) if p is not None else "n/a"))
        print("%-32s   e(C-M) = %12.6e   e(M-F) = %12.6e   ratio = %s" %
              ("", e32, e21, ("%.4f" % (e32 / e21)) if e21 else "inf"))

    print()
    print("=" * 74)
    print("MESH SIZES (from polyMesh, independently of checkMesh)")
    print("=" * 74)
    for lv in LEVELS:
        r = res[lv]
        print("  %-8s fluid %7d  housing %6d  core %6d   housing patch faces %4d "
              " area %.6e m2  first-cell dn %.4e m"
              % (lv, r["fluid_cells"], r["housing_cells"], r["core_cells"],
                 r["housing_patch_nFaces"], r["housing_patch_area"],
                 r["housing_first_cell_dn"]))
