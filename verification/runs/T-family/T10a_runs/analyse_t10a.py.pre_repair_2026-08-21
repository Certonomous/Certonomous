#!/usr/bin/env python3
"""
T10a comparator -- view-factor radiation enclosures against exact
surface-to-surface theory (EXACT tier).

WRITTEN AND FROZEN BEFORE ANY CASE HAS SOLVED (Charter 2d).  At the moment
this file is frozen the run tree holds meshes and view-factor matrices
(blockMesh, checkMesh, viewFactorsGen / createViewFactors are mesh-side
preprocessing) and NO time directory other than 0.orig; the registered values
live in T10a_registered.json beside it and are re-derived two independent
ways by exact_t10a.py at every run -- this comparator REFUSES TO RUN if the
two derivations disagree or if the JSON copies disagree with them.

Registered rows (T10a_PREREGISTRATION.md), every value net flux LEAVING the
surface in W/m2, graded against sigma_OF (the sigma the solver uses, READ
from etc/controlDict):

  S0  inner sphere    3374.471705        S1  outer sphere    -843.617926
  B0  box floor       6484.920941        B1  box ceiling    -3265.532221
  B2  box x-walls    -1254.691645        B3  box y-walls    -1964.697075

OpenFOAM's qr is the net flux INTO the wall (viewFactor.C assembles
C q = b with b_i = -sigma T_i^4 + sum_j F_ij sigma T_j^4); the comparator
flips the sign once, here, and a sign disagreeing with both the code reading
and the physics is a GATE FAIL, not a convention.

THE BAND IS DERIVED, NEVER CHOSEN: three levels at nominal ratio 1.6 in
radiating-face edge count, Roache GCI at Fs = 1.25 on the finest, using the
SAME gci() as T1c and T9a (imported from T1_runs/analyse_t1c.py).  The
verdict order on every graded row is BINDING and registered:

  1. a level that is not iteratively CONVERGED (qr identical value for value
     between the last two written checkpoints)      -> NOT A RESULT
  2. a level whose closure guard voids the run       -> NOT A RESULT
  3. a grid triple that is not CONVERGING
     (OSCILLATORY, STAGNANT, DIVERGENT or EXACT)     -> NOT A RESULT, never PASS
  4. armed band below the quadrature floor measured by the GaussQuadTol 0.001
     twin on that row                                -> GATE REACHED (reported, not graded)
  5. armed band not below one tenth of the row's C2 departure (Charter 2c
     discrimination)                                 -> GATE REACHED (reported, not graded)
  6. deviation <= band -> PASS, else GATE FAIL.

CONTROLS, each of which MUST FAIL if the rung is sound: C1 black-body
reference, C1-live (S_C1 solved with eps = 1: must NOT reproduce S_f, else the
emissivity dictionary is unread and the sphere rows are VOID/BLOCKED), C2
parallel-plate network (spheres), C2 cube matrix (box), C2b opposite-only
(reported), C3a radiation-off zero field, C3b the solved uniform-300 K box.

CARRIED FORWARD, because each was paid for once: every geometric constant is
READ from constant/polyMesh (points, faces, boundary), the view factors are
READ from the constant/F the utility wrote (never from its inputs), writeInterval
< endTime (L-140), convergence from written checkpoints with a live planted
1.234e-03 control (L-141), stale writes refused by runner and marker (L-143).

WHAT THIS COMPARATOR CANNOT SEE: participating media, spectral or non-grey
behaviour, any coupling to convection or conduction (every wall T is imposed
and the fluid is an inert carrier), a grey NON-symmetric enclosure (no exact
answer exists), and faceAgglomerate (bypassed by registration).
"""
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T1_DIR = os.path.abspath(os.path.join(HERE, "..", "T1_runs"))
sys.path.insert(0, HERE)
sys.path.insert(0, T1_DIR)
import exact_t10a as EXACT          # noqa: E402
import analyse_t1c as T1            # noqa: E402  (gci, FS = 1.25, R = 1.6)

REG = json.load(open(os.path.join(HERE, "T10a_registered.json")))
FS, R_REFINE = REG["grid"]["Fs"], REG["grid"]["r"]
if (FS, R_REFINE) != (T1.FS, T1.R_REFINE):
    print(f"REFUSE: registered Fs/r {FS}/{R_REFINE} differ from analyse_t1c's "
          f"{T1.FS}/{T1.R_REFINE}")
    sys.exit(2)
gci = T1.gci

CLOSURE_TOL = REG["guards"]["closure"]["threshold_rel"]
DISC_FACTOR = REG["discrimination"]["factor"]
PLANT = REG["planted_control_value"]
LEVELS = ("c", "m", "f")
GROUP = "viewFactorWall"
SCRATCH = os.environ.get("T10A_SCRATCH",
                         "/tmp/claude-1000/-home-ubuntu/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad")

PASS, GATE_REACHED, GATE_FAIL = "PASS", "GATE REACHED", "GATE FAIL"
NOT_A_RESULT, BLOCKED, PENDING = "NOT A RESULT", "BLOCKED", "PENDING"
EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print(msg)
    sys.exit(EXIT_REFUSE)


# ---------------------------------------------------------------------------
# OpenFOAM ascii readers.  Everything geometric comes through here.
# ---------------------------------------------------------------------------
def _body(path):
    txt = open(path, errors="replace").read()
    if re.search(r"format\s+binary\s*;", txt[:2000]):
        refuse(f"REFUSE: {path} is binary; this comparator reads ascii only")
    i = txt.find("FoamFile")
    i = txt.find("}", i) + 1
    body = txt[i:]
    body = re.sub(r"//[^\n]*", "", body)
    return body


def read_points(case):
    pts = [tuple(float(x) for x in m.groups()) for m in
           re.finditer(r"\(\s*([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\s*\)",
                       _body(os.path.join(case, "constant", "polyMesh", "points")))]
    if not pts:
        refuse(f"REFUSE: cannot parse points in {case}")
    return pts


def read_faces(case):
    body = _body(os.path.join(case, "constant", "polyMesh", "faces"))
    m = re.search(r"(\d+)\s*\(", body)
    n = int(m.group(1))
    faces = [[int(v) for v in mm.group(2).split()] for mm in
             re.finditer(r"(\d+)\s*\(([\d\s]+)\)", body[m.end():])]
    if len(faces) != n:
        refuse(f"REFUSE: faces file in {case} declares {n}, parsed {len(faces)}")
    return faces


def read_boundary(case):
    body = _body(os.path.join(case, "constant", "polyMesh", "boundary"))
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^{}]*)\}", body):
        name, blk = m.group(1), m.group(2)
        t = re.search(r"type\s+(\w+)\s*;", blk)
        nf = re.search(r"nFaces\s+(\d+)\s*;", blk)
        sf = re.search(r"startFace\s+(\d+)\s*;", blk)
        g = re.search(r"inGroups\s+\d*\s*\(([^)]*)\)", blk)
        if not (t and nf and sf):
            continue
        out[name] = dict(type=t.group(1), nFaces=int(nf.group(1)),
                         startFace=int(sf.group(1)),
                         groups=g.group(1).split() if g else [])
    if not out:
        refuse(f"REFUSE: cannot parse boundary in {case}")
    return out


def ncells_from_owner(case):
    txt = open(os.path.join(case, "constant", "polyMesh", "owner"),
               errors="replace").read(3000)
    m = re.search(r"nCells:\s*(\d+)", txt)
    return int(m.group(1))


def face_geometry(points, face):
    """Area vector (outward per face ordering), area, centre -- the same
    triangle-fan decomposition OpenFOAM's primitiveMesh uses."""
    n = len(face)
    p = [points[i] for i in face]
    c0 = [sum(q[d] for q in p) / n for d in range(3)]
    sf = [0.0, 0.0, 0.0]
    cw = [0.0, 0.0, 0.0]
    asum = 0.0
    for k in range(n):
        a, b = p[k], p[(k + 1) % n]
        u = [a[d] - c0[d] for d in range(3)]
        v = [b[d] - c0[d] for d in range(3)]
        cr = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
              u[0] * v[1] - u[1] * v[0]]
        at = 0.5 * math.sqrt(sum(x * x for x in cr))
        ct = [(a[d] + b[d] + c0[d]) / 3 for d in range(3)]
        for d in range(3):
            sf[d] += 0.5 * cr[d]
            cw[d] += at * ct[d]
        asum += at
    area = math.sqrt(sum(x * x for x in sf))
    centre = [cw[d] / asum for d in range(3)] if asum > 0 else c0
    return sf, area, centre


def mesh_patches(case):
    """Geometry of every viewFactorWall patch, READ FROM THE MESH."""
    pts = read_points(case)
    faces = read_faces(case)
    bnd = read_boundary(case)
    out = {}
    order = []
    for name, b in bnd.items():          # boundary-file order == patch index order
        if GROUP not in b["groups"]:
            continue
        areas, centres, normals, vert = [], [], [], set()
        for fi in range(b["startFace"], b["startFace"] + b["nFaces"]):
            sf, a, c = face_geometry(pts, faces[fi])
            areas.append(a)
            centres.append(c)
            normals.append([x / a for x in sf])
            vert.update(faces[fi])
        out[name] = dict(areas=areas, centres=centres, normals=normals,
                         vertices=[pts[i] for i in vert], nFaces=b["nFaces"])
        order.append(name)
    if not out:
        refuse(f"REFUSE: {case} has no patch in group {GROUP}")
    return out, order, pts


def boundary_blocks(path):
    txt = open(path, errors="replace").read()
    i = txt.find("boundaryField")
    if i < 0:
        refuse(f"REFUSE: no boundaryField in {path}")
    i = txt.find("{", i)
    depth, j = 0, i
    while j < len(txt):
        if txt[j] == "{":
            depth += 1
        elif txt[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    body = txt[i + 1:j]
    out, k = {}, 0
    while True:
        m = re.search(r'("?[\w.*]+"?)\s*\{', body[k:])
        if not m:
            break
        name = m.group(1).strip('"')
        s = k + m.end() - 1
        depth, e = 0, s
        while e < len(body):
            if body[e] == "{":
                depth += 1
            elif body[e] == "}":
                depth -= 1
                if depth == 0:
                    break
            e += 1
        out[name] = body[s + 1:e]
        k = e + 1
    return out


def patch_values(path, patch, nfaces, key="value"):
    """The patch's scalar list, expanded if uniform."""
    blocks = boundary_blocks(path)
    if patch not in blocks:
        refuse(f"REFUSE: patch {patch} not in {path}")
    blk = blocks[patch]
    m = re.search(re.escape(key) + r"\s+nonuniform\s+List<scalar>\s*(\d+)\s*\(([^)]*)\)", blk)
    if m:
        n = int(m.group(1))
        vals = [float(v) for v in m.group(2).split()]
        if len(vals) != n or n != nfaces:
            refuse(f"REFUSE: {path} patch {patch}: {len(vals)} values, list says {n}, "
                   f"mesh says {nfaces}")
        return vals
    m = re.search(re.escape(key) + r"\s+uniform\s+([-0-9.eE+]+)\s*;", blk)
    if m:
        return [float(m.group(1))] * nfaces
    refuse(f"REFUSE: no '{key}' on patch {patch} in {path}")


def read_F(case):
    """constant/F and constant/globalFaceFaces as the utility WROTE them."""
    import numpy as np
    rows = []
    for name, dtype in (("F", float), ("globalFaceFaces", int)):
        p = os.path.join(case, "constant", name)
        if not os.path.isfile(p):
            refuse(f"REFUSE: {case} has no constant/{name}")
        body = _body(p).replace("(", " ").replace(")", " ")
        arr = np.fromstring(body, sep=" ")
        n = int(arr[0])
        pos, out = 1, []
        for i in range(n):
            k = int(arr[pos])
            out.append(arr[pos + 1:pos + 1 + k].astype(dtype))
            pos += 1 + k
        if pos != len(arr):
            refuse(f"REFUSE: {p} parsed {pos} tokens of {len(arr)}")
        rows.append(out)
    F, G = rows
    if len(F) != len(G) or any(len(a) != len(b) for a, b in zip(F, G)):
        refuse(f"REFUSE: {case} F and globalFaceFaces disagree in shape")
    return F, G


def dense_F(F, G, n):
    import numpy as np
    Fm = np.zeros((n, n))
    for i, (vals, idx) in enumerate(zip(F, G)):
        if len(idx) and (idx.max() >= n or idx.min() < 0):
            refuse("REFUSE: globalFaceFaces index out of range")
        Fm[i, idx] = vals
    return Fm


def read_emissivities(case, patch_names):
    p = os.path.join(case, "constant", "boundaryRadiationProperties")
    txt = open(p, errors="replace").read()
    txt = re.sub(r"//[^\n]*", "", txt)
    blocks = {}
    for m in re.finditer(r'("?[\w.*]+"?)\s*\{([^{}]*)\}', txt):
        blocks[m.group(1).strip('"')] = m.group(2)
    eps = {}
    for name in patch_names:
        blk = blocks.get(name, blocks.get(".*"))
        if blk is None:
            refuse(f"REFUSE: no boundaryRadiationProperties entry for {name} in {case}")
        if not re.search(r"type\s+lookup\s*;", blk):
            refuse(f"REFUSE: {name} in {case} is not 'type lookup'")
        e = re.search(r"emissivity\s+([-0-9.eE+]+)\s*;", blk)
        if not e:
            refuse(f"REFUSE: no emissivity for {name} in {case}")
        eps[name] = float(e.group(1))
    return eps


def sigma_used():
    host = EXACT.sigma_of_host()
    if host is None:
        refuse("REFUSE: cannot read the Stefan-Boltzmann constants from "
               f"{EXACT.OF_CONTROLDICT}; the comparator grades against the sigma "
               "the solver used and will not assume it")
    return host[0]


def radiosity_on_F(Fm, eps, T, sigma):
    """viewFactor.C's constant-emissivity assembly, exactly: diagonal ignored,
    C_ii = 1/eps_i, C_ij = (1 - 1/eps_j) F_ij, b_i = -sigma T_i^4 + sum_{j!=i}
    F_ij sigma T_j^4; returns qr (INTO the wall) per face."""
    import numpy as np
    n = Fm.shape[0]
    F0 = Fm.copy()
    np.fill_diagonal(F0, 0.0)
    inv = 1.0 / np.asarray(eps)
    C = (1.0 - inv)[None, :] * F0
    np.fill_diagonal(C, inv)
    sT4 = sigma * np.asarray(T) ** 4
    b = F0 @ sT4 - sT4
    return np.linalg.solve(C, b)


# ---------------------------------------------------------------------------
def time_dirs(case):
    return sorted((d for d in os.listdir(case)
                   if re.fullmatch(r"\d+(\.\d+)?", d) and float(d) != 0.0),
                  key=float)


def read_qr_all(path, geom, order):
    return {p: patch_values(path, p, geom[p]["nFaces"]) for p in order}


def iterative_convergence(case, geom, order):
    """The last two written checkpoints of qr, value for value (L-141).
    CONVERGED means max change 0.0 -- registered strict, because fixed-T walls
    fix qr after the first radiation solve and nothing may move it."""
    ts = time_dirs(case)
    if len(ts) < 2:
        return dict(state="UNJUDGED", why=f"only {len(ts)} checkpoint(s); need two")
    a = read_qr_all(os.path.join(case, ts[-2], "qr"), geom, order)
    b = read_qr_all(os.path.join(case, ts[-1], "qr"), geom, order)
    dmax = max(abs(x - y) for p in order for x, y in zip(a[p], b[p]))
    scale = max(abs(v) for p in order for v in b[p]) or 1.0
    return dict(state="CONVERGED" if dmax == 0.0 else "NOT_CONVERGED",
                max_change=dmax, scale=scale, relative=dmax / scale,
                between=(ts[-2], ts[-1]))


def planted_zero_control(qr_path, geom, order, plant=PLANT):
    """Plant `plant` into a SCRATCH copy of the earlier checkpoint by line
    index, read it back off disk through the same reader, and confirm the
    recovered maximum change EXACTLY equals the change the plant produced in
    float: expected = fl(old + plant) - old.  Requiring rec == plant to 1e-15
    would fail on rounding at the base value's ulp (old ~ 6.5e3 W/m2 has ulp
    9.1e-13, three orders above 1e-12*plant); requiring rec == expected is
    exact AND still fails when the reader is broken or the plant is swallowed
    (expected == 0 or far from plant).  The case tree is never touched.
    [Completed by the second instance 2026-08-21 before the freeze: the first
    instance's tolerance abs(rec - plant) <= 1e-12*plant was unsatisfiable.]"""
    tmp = tempfile.mkdtemp(prefix="t10a_plant_", dir=SCRATCH)
    try:
        lines = open(qr_path, errors="replace").read().split("\n")
        first = order[0]
        # locate the first patch block and its first value line
        start = next(i for i, l in enumerate(lines)
                     if re.match(r"\s*" + re.escape(first) + r"\s*$", l) or
                     re.match(r"\s*" + re.escape(first) + r"\s*\{", l))
        idx = None
        for i in range(start, len(lines)):
            if re.search(r"nonuniform\s+List<scalar>", lines[i]):
                j = i + 1
                while not re.fullmatch(r"\s*\(\s*", lines[j]):
                    j += 1
                idx = j + 1
                old = float(lines[idx])
                lines[idx] = repr(old + plant)
                break
            m = re.search(r"value\s+uniform\s+([-0-9.eE+]+)\s*;", lines[i])
            if m:
                old = float(m.group(1))
                lines[i] = lines[i].replace(m.group(1), repr(old + plant))
                idx = i
                break
        if idx is None:
            return dict(ok=False, why="no value to plant into")
        expected = (old + plant) - old      # the change the plant CAN produce
        pp = os.path.join(tmp, "qr")
        open(pp, "w").write("\n".join(lines))
        a = read_qr_all(qr_path, geom, order)
        b = read_qr_all(pp, geom, order)
        rec = max(abs(x - y) for p in order for x, y in zip(a[p], b[p]))
        ok = (rec == expected and expected > 0.0
              and abs(expected - plant) <= 1e-6 * plant)
        return dict(ok=ok, planted=plant, expected=expected, recovered=rec,
                    line=idx + 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def log_facts(case):
    out = {}
    lv = os.path.join(case, "log.viewFactorsGen")
    if not os.path.isfile(lv):
        lv = os.path.join(case, "log.createViewFactors")
    if os.path.isfile(lv):
        t = open(lv, errors="replace").read()
        out["generator"] = os.path.basename(lv)[4:]
        out["coarse_faces"] = (re.search(r"Total number of coarse faces:\s*(\d+)", t) or
                               [None, None])[1]
    ls = os.path.join(case, "log.solve")
    if os.path.isfile(ls):
        t = open(ls, errors="replace").read()
        m1 = re.search(r"Smoothing average delta\s*:\s*([-0-9.eE+]+)", t)
        m2 = re.search(r"Smoothing maximum delta\s*:\s*([-0-9.eE+]+)", t)
        out["smoothing_avg_delta"] = float(m1.group(1)) if m1 else None
        out["smoothing_max_delta"] = float(m2.group(1)) if m2 else None
        out["radiation_model"] = (re.search(r"Selecting radiationModel\s+(\w+)", t) or
                                  [None, None])[1]
    return out


# ---------------------------------------------------------------------------
def measure(case_name, sigma, want_F=True):
    """Everything the rows and guards need from one case, geometry from the
    mesh, view factors from the written F, qr from the last checkpoint."""
    case = os.path.join(HERE, case_name)
    spec = REG["cases"][case_name]
    geom, order, pts = mesh_patches(case)
    ts = time_dirs(case)
    if not ts:
        refuse(f"REFUSE: {case_name} has no written time directory")
    t = ts[-1]
    qr = read_qr_all(os.path.join(case, t, "qr"), geom, order)
    Tp = {p: patch_values(os.path.join(case, t, "T"), p, geom[p]["nFaces"]) for p in order}
    eps = read_emissivities(case, order)
    m = dict(case=case_name, time=t, n_cells=ncells_from_owner(case),
             patches={}, order=order, eps=eps)

    # ---- geometry read-back (refusals, T1c / L-142) ------------------------
    if spec["kind"] == "spheres":
        radii = {}
        for p in ("inner", "outer"):
            rs = [math.sqrt(x * x + y * y + z * z) for x, y, z in geom[p]["vertices"]]
            radii[p] = (min(rs), max(rs))
        r1 = 0.5 * sum(radii["inner"])
        r2 = 0.5 * sum(radii["outer"])
        for p, rr in (("inner", REG["spheres"]["r1"]), ("outer", REG["spheres"]["r2"])):
            lo, hi = radii[p]
            if max(abs(lo - rr), abs(hi - rr)) / rr > 1e-9:
                refuse(f"REFUSE: {case_name} patch {p} vertices span radii {lo:.12g}.."
                       f"{hi:.12g}, not the registered {rr}")
        m["geometry"] = dict(r1=r1, r2=r2,
                             A_inner_facet=sum(geom["inner"]["areas"]),
                             A_outer_facet=sum(geom["outer"]["areas"]),
                             A_inner_exact=4 * math.pi * r1 ** 2,
                             A_outer_exact=4 * math.pi * r2 ** 2)
        m["geometry"]["facet_deficit_inner"] = m["geometry"]["A_inner_facet"] / m["geometry"]["A_inner_exact"] - 1
        m["geometry"]["facet_deficit_outer"] = m["geometry"]["A_outer_facet"] / m["geometry"]["A_outer_exact"] - 1
    elif spec["kind"] == "box":
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        zs = [p[2] for p in pts]
        L = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
        Lr = (REG["box"]["Lx"], REG["box"]["Ly"], REG["box"]["Lz"])
        if max(abs(a - b) for a, b in zip(L, Lr)) > 1e-12:
            refuse(f"REFUSE: {case_name} extents {L} are not the registered {Lr}")
        for p in order:
            Ar = REG["box"]["patches"][p]["A"]
            if abs(sum(geom[p]["areas"]) - Ar) > 1e-10:
                refuse(f"REFUSE: {case_name} patch {p} area {sum(geom[p]['areas'])} != {Ar}")
        m["geometry"] = dict(Lx=L[0], Ly=L[1], Lz=L[2])
    else:
        m["geometry"] = dict(note="2D Hottel rectangle, reported only")

    # ---- per-patch rows ----------------------------------------------------
    tot_in = 0.0
    tot_abs = 0.0
    for p in order:
        A = geom[p]["areas"]
        Q_into = sum(a * q for a, q in zip(A, qr[p]))
        As = sum(A)
        m["patches"][p] = dict(n=len(A), area=As, Q_into=Q_into,
                               q_leaving=-Q_into / As, qr_into_mean=Q_into / As,
                               qr_min=min(qr[p]), qr_max=max(qr[p]),
                               T=sum(a * tt for a, tt in zip(A, Tp[p])) / As,
                               eps=eps[p])
        tot_in += Q_into
        tot_abs += sum(abs(a * q) for a, q in zip(A, qr[p]))
    m["closure_raw"] = abs(tot_in) / tot_abs if tot_abs > 0 else 0.0
    m["sum_Aq_into"] = tot_in
    m["max_abs_qr"] = max(abs(v) for p in order for v in qr[p])

    # ---- convergence and the planted control --------------------------------
    m["convergence"] = iterative_convergence(case, geom, order)
    if len(ts) >= 2:
        m["planted_control"] = planted_zero_control(os.path.join(case, ts[-2], "qr"), geom, order)
    else:
        m["planted_control"] = dict(ok=False, why="fewer than two checkpoints")

    # ---- the written F: row sums, reciprocity, python radiosity -------------
    if want_F:
        import numpy as np
        F, G = read_F(case)
        n = sum(geom[p]["nFaces"] for p in order)
        if len(F) != n:
            refuse(f"REFUSE: {case_name} F has {len(F)} rows, mesh has {n} {GROUP} faces")
        Fm = dense_F(F, G, n)
        A = np.concatenate([np.asarray(geom[p]["areas"]) for p in order])
        E = np.concatenate([np.full(geom[p]["nFaces"], eps[p]) for p in order])
        Tf = np.concatenate([np.asarray(Tp[p]) for p in order])
        rows = Fm.sum(axis=1)
        off = 0
        m["rowsum"] = {}
        for p in order:
            k = geom[p]["nFaces"]
            r = rows[off:off + k]
            m["rowsum"][p] = dict(min=float(r.min()), max=float(r.max()),
                                  mean=float(r.mean()),
                                  max_defect=float(np.abs(r - 1).max()))
            off += k
        AF = A[:, None] * Fm
        m["reciprocity_max_defect"] = float(np.abs(AF - AF.T).max())
        m["F_diag_max"] = float(np.abs(np.diag(Fm)).max())
        qpy = radiosity_on_F(Fm, E, Tf, sigma)
        qs = np.concatenate([np.asarray(qr[p]) for p in order])
        scale = float(np.abs(qs).max()) or 1.0
        m["python_vs_solver_max_rel"] = float(np.abs(qpy - qs).max() / scale)
        tot_py = float((A * qpy).sum())
        m["closure_F"] = abs(tot_py) / float(np.abs(A * qpy).sum())
        m["closure_excess"] = abs(m["closure_raw"] - m["closure_F"])
        m["python_patch_q_leaving"] = {}
        off = 0
        for p in order:
            k = geom[p]["nFaces"]
            m["python_patch_q_leaving"][p] = float(-(A[off:off + k] * qpy[off:off + k]).sum()
                                                   / A[off:off + k].sum())
            off += k
        m["void"] = m["closure_excess"] > CLOSURE_TOL
    else:
        m["void"] = False
    m["log"] = log_facts(case)
    return m


def row_value(m, patch):
    if isinstance(patch, list):
        vals = [m["patches"][p]["q_leaving"] for p in patch]
        return sum(vals) / len(vals)
    return m["patches"][patch]["q_leaving"]


# ---------------------------------------------------------------------------
def grade_row(tag, values, ref, conv_states, void_levels, twin_value,
              c2_departure_pct, quiet=False):
    """THE verdict function.  values/conv_states/void_levels keyed c, m, f."""
    row = dict(row=tag, reference=ref, value=values["f"], levels=dict(values),
               C2_departure_pct=c2_departure_pct)
    say = (lambda *a: None) if quiet else print
    unc = [l for l in LEVELS if conv_states[l] != "CONVERGED"]
    if unc:
        row.update(verdict=NOT_A_RESULT, graded=False,
                   why=f"levels {unc} not iteratively CONVERGED")
        say(f"    {tag}: NOT A RESULT -- {row['why']}")
        return row
    voided = [l for l in LEVELS if void_levels.get(l)]
    if voided:
        row.update(verdict=NOT_A_RESULT, graded=False,
                   why=f"levels {voided} VOID (closure guard)")
        say(f"    {tag}: NOT A RESULT -- {row['why']}")
        return row
    conv = gci(values["c"], values["m"], values["f"])
    row["grid_triple"] = conv
    row["convergence"] = conv["state"]
    if conv["state"] != "CONVERGING":
        row.update(verdict=NOT_A_RESULT, graded=False,
                   why=f"grid triple is {conv['state']}; no band is armed")
        say(f"    {tag}: NOT A RESULT -- {row['why']}")
        return row
    band = conv["GCI_pct"]
    dev = 100.0 * abs(values["f"] - ref) / abs(ref)
    row.update(band_pct=band, deviation_pct=dev, order=conv["order"])
    den = R_REFINE ** conv["order"] - 1.0
    row["richardson_corrected"] = values["f"] + (values["f"] - values["m"]) / den
    floor = None
    if twin_value is not None:
        floor = 100.0 * abs(twin_value - values["f"]) / abs(values["f"])
        row["quadrature_floor_pct"] = floor
    disc_limit = DISC_FACTOR * abs(c2_departure_pct)
    row["discrimination_limit_pct"] = disc_limit
    reasons = []
    if floor is not None and band < floor:
        reasons.append(f"band {band:.4g} % < quadrature floor {floor:.4g} % (GaussQuadTol twin)")
    if band >= disc_limit:
        reasons.append(f"band {band:.4g} % >= {DISC_FACTOR} x C2 departure {abs(c2_departure_pct):.4g} % (Charter 2c)")
    if reasons:
        row.update(verdict=GATE_REACHED, graded=False, why="; ".join(reasons))
        say(f"    {tag}: GATE REACHED -- REPORTED, NOT GRADED: {row['why']} "
            f"(deviation would have been {dev:.4f} %)")
        return row
    row.update(graded=True, verdict=PASS if dev <= band else GATE_FAIL)
    say(f"    {tag}: value {values['f']:.6f} vs {ref:.6f}: deviation {dev:.5f} %, "
        f"band (GCI, p = {conv['order']:.3f}) {band:.5f} %  -> {row['verdict']}")
    return row


# ---------------------------------------------------------------------------
def selftest():
    import numpy as np
    ok = True

    def t(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'OK  ' if cond else 'FAIL'} {name}{(' -- ' + detail) if detail else ''}")

    print("analyse_t10a.py --selftest: the verdict function, the readers, the plant")
    conv_ok = {l: "CONVERGED" for l in LEVELS}
    novoid = {l: False for l in LEVELS}
    big_c2 = 100.0
    # the reference sits EXACTLY on the fine value: under any band this is a
    # PASS, so the only thing that can stop it is the triple's state
    for name, triple in (("OSCILLATORY", (1.10, 0.96, 1.0)),
                         ("STAGNANT", (1.021, 1.010, 1.0)),
                         ("DIVERGENT", (1.030, 1.020, 1.0)),
                         ("EXACT", (1.010, 1.000, 1.0))):
        v = dict(zip(LEVELS, triple))
        st = gci(*triple)["state"]
        r = grade_row("X", v, 1.0, conv_ok, novoid, v["f"], big_c2, quiet=True)
        t(f"{name} triple, value on the reference -> NOT A RESULT",
          st == name and r["verdict"] == NOT_A_RESULT, f"gci state {st}, verdict {r['verdict']}")
    v = dict(c=1.10, m=1.04, f=1.015)
    r = grade_row("X", v, 1.0, conv_ok, novoid, v["f"], big_c2, quiet=True)
    t("CONVERGING, inside band -> PASS", r["verdict"] == PASS,
      f"band {r.get('band_pct', 0):.3f} %, dev {r.get('deviation_pct', 0):.3f} %")
    band = r["band_pct"]
    r2 = grade_row("X", v, 0.95, conv_ok, novoid, v["f"], big_c2, quiet=True)
    t("CONVERGING, outside band -> GATE FAIL", r2["verdict"] == GATE_FAIL,
      f"dev {r2.get('deviation_pct', 0):.3f} % > band {band:.3f} %")
    cs = dict(conv_ok)
    cs["m"] = "NOT_CONVERGED"
    r3 = grade_row("X", v, 1.0, cs, novoid, v["f"], big_c2, quiet=True)
    t("CONVERGING triple but level m not CONVERGED -> NOT A RESULT", r3["verdict"] == NOT_A_RESULT)
    vd = dict(novoid)
    vd["c"] = True
    r4 = grade_row("X", v, 1.0, conv_ok, vd, v["f"], big_c2, quiet=True)
    t("CONVERGING triple but level c VOID by closure -> NOT A RESULT", r4["verdict"] == NOT_A_RESULT)
    r5 = grade_row("X", v, 1.0, conv_ok, novoid, v["f"] * 1.05, big_c2, quiet=True)
    t("band below the GaussQuadTol-twin floor -> GATE REACHED", r5["verdict"] == GATE_REACHED,
      r5.get("why", ""))
    r6 = grade_row("X", v, 1.0, conv_ok, novoid, v["f"], 10.0, quiet=True)
    t("band not below 0.1 x C2 departure -> GATE REACHED (discrimination)",
      r6["verdict"] == GATE_REACHED, r6.get("why", ""))
    r7 = grade_row("X", v, 1.0, conv_ok, novoid, v["f"], 100.0, quiet=True)
    t("same row with a 100 % C2 departure is graded again", r7["graded"] is True)

    # the readers on a synthetic unit cube polyMesh
    tmp = tempfile.mkdtemp(prefix="t10a_selftest_", dir=SCRATCH)
    try:
        case = os.path.join(tmp, "cube")
        os.makedirs(os.path.join(case, "constant", "polyMesh"))
        os.makedirs(os.path.join(case, "10"))
        os.makedirs(os.path.join(case, "5"))
        hdr = lambda cls, obj: ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
                                f"    class {cls};\n    object {obj};\n}}\n")
        P = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
        open(os.path.join(case, "constant/polyMesh/points"), "w").write(
            hdr("vectorField", "points") + "8\n(\n" + "\n".join(f"({x} {y} {z})" for x, y, z in P) + "\n)\n")
        faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 4, 7, 3], [1, 2, 6, 5], [0, 1, 5, 4], [3, 7, 6, 2]]
        open(os.path.join(case, "constant/polyMesh/faces"), "w").write(
            hdr("faceList", "faces") + "6\n(\n" + "\n".join("4(" + " ".join(map(str, f)) + ")" for f in faces) + "\n)\n")
        names = ["floor", "ceiling", "x0", "x1", "y0", "y1"]
        open(os.path.join(case, "constant/polyMesh/boundary"), "w").write(
            hdr("polyBoundaryMesh", "boundary") + "6\n(\n" + "".join(
                f"{nm}\n{{\n    type wall;\n    inGroups 2(wall viewFactorWall);\n    nFaces 1;\n    startFace {i};\n}}\n"
                for i, nm in enumerate(names)) + ")\n")
        open(os.path.join(case, "constant/polyMesh/owner"), "w").write(
            hdr("labelList", "owner") + "// note: nCells: 1\n6\n(\n0\n0\n0\n0\n0\n0\n)\n")
        geom, order, pts = mesh_patches(case)
        t("boundary order and group read", order == names)
        t("unit-cube patch areas read as 1.0 from points+faces",
          all(abs(sum(geom[p]["areas"]) - 1.0) < 1e-14 for p in names))
        nrm = {p: geom[p]["normals"][0] for p in names}
        t("face normals point OUT of the domain (owner orientation)",
          nrm["floor"][2] < 0 and nrm["ceiling"][2] > 0 and nrm["x0"][0] < 0 and nrm["y1"][1] > 0)
        # the black box matrix written in the utility's own F / globalFaceFaces format
        ba = EXACT.box_matrix_closed_form()["F"]
        sigma = EXACT.sigma_from(EXACT.K_OF, EXACT.H_OF, EXACT.C_OF)
        rowsF, rowsG = [], []
        for p in names:
            idx = [j for j, q in enumerate(names) if q != p]
            rowsF.append("5(" + " ".join(f"{ba[p][names[j]]:.15g}" for j in idx) + ")")
            rowsG.append("5(" + " ".join(map(str, idx)) + ")")
        open(os.path.join(case, "constant/F"), "w").write(hdr("scalarListList", "F") + "6\n(\n" + "\n".join(rowsF) + "\n)\n")
        open(os.path.join(case, "constant/globalFaceFaces"), "w").write(hdr("labelListList", "globalFaceFaces") + "6\n(\n" + "\n".join(rowsG) + "\n)\n")
        F, G = read_F(case)
        Fm = dense_F(F, G, 6)
        t("F / globalFaceFaces parsed into a dense matrix with unit row sums",
          abs(Fm.sum(axis=1) - 1).max() < 1e-12)
        Tb = [REG["box"]["patches"][p]["T"] for p in names]
        q = radiosity_on_F(Fm, [1.0] * 6, Tb, sigma)
        refs = [REG["box"]["q_floor"], REG["box"]["q_ceiling"], REG["box"]["q_xwall"],
                REG["box"]["q_xwall"], REG["box"]["q_ywall"], REG["box"]["q_ywall"]]
        t("python radiosity in viewFactor.C's form returns -q_registered (INTO the wall) on the black box",
          max(abs(-q[k] - refs[k]) / abs(refs[k]) for k in range(6)) < 2e-9,
          f"max rel {max(abs(-q[k] - refs[k]) / abs(refs[k]) for k in range(6)):.1e}")
        # the grey two-surface network through the same assembly needs the
        # outer self-view, which the face-level assembly ignores by design
        sa = EXACT.spheres_closed_form(sigma)
        Fs = np.array([[0.0, 1.0], [0.25, 0.0]])
        q2 = radiosity_on_F(Fs, [0.6, 0.4], [600.0, 300.0], sigma)
        t("assembly ignores F_ii (planar faces): a 2-face sphere network WITHOUT F22 does NOT give the grey answer",
          abs(-q2[0] - sa["q1"]) / sa["q1"] > 1e-3,
          f"{-q2[0]:.3f} vs {sa['q1']:.3f}; the real S cases carry F22 as face-to-face terms")
        # qr files: two checkpoints, identical; then the plant
        def qr_file(vals_by_patch, uniform_patch=None):
            s = hdr("volScalarField", "qr") + "dimensions [1 0 -3 0 0 0 0];\ninternalField uniform 0;\nboundaryField\n{\n"
            for p in names:
                if p == uniform_patch:
                    s += f"    {p}\n    {{\n        type calculated;\n        value uniform {vals_by_patch[p][0]!r};\n    }}\n"
                else:
                    s += f"    {p}\n    {{\n        type calculated;\n        value nonuniform List<scalar> 1\n(\n{vals_by_patch[p][0]!r}\n)\n;\n    }}\n"
            return s + "}\n"
        vals = {p: [-refs[k]] for k, p in enumerate(names)}
        open(os.path.join(case, "5/qr"), "w").write(qr_file(vals))
        open(os.path.join(case, "10/qr"), "w").write(qr_file(vals))
        c = iterative_convergence(case, geom, order)
        t("identical checkpoints read as CONVERGED with max change 0.0",
          c["state"] == "CONVERGED" and c["max_change"] == 0.0)
        pc = planted_zero_control(os.path.join(case, "5/qr"), geom, order)
        t(f"planted {PLANT} recovered exactly through the reader (nonuniform)", pc["ok"],
          f"recovered {pc.get('recovered')}")
        open(os.path.join(case, "5/qr"), "w").write(qr_file(vals, uniform_patch="floor"))
        pc2 = planted_zero_control(os.path.join(case, "5/qr"), geom, order)
        t(f"planted {PLANT} recovered exactly through the reader (uniform entry)", pc2["ok"],
          f"recovered {pc2.get('recovered')}")
        vals2 = dict(vals)
        vals2["x1"] = [vals["x1"][0] + 3e-7]
        open(os.path.join(case, "10/qr"), "w").write(qr_file(vals2))
        c2 = iterative_convergence(case, geom, order)
        t("a 3e-7 change between checkpoints reads NOT_CONVERGED", c2["state"] == "NOT_CONVERGED")
        em = os.path.join(case, "constant", "boundaryRadiationProperties")
        open(em, "w").write(hdr("dictionary", "boundaryRadiationProperties") +
                            "".join(f"{p}\n{{\n    type lookup;\n    emissivity 0.6;\n    absorptivity 0.6;\n}}\n" for p in names))
        t("emissivities read per patch", all(v == 0.6 for v in read_emissivities(case, names).values()))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    t("sigma read from etc/controlDict equals the registered sigma_OF",
      abs(sigma_used() - REG["sigma"]["sigma_OF"]) / REG["sigma"]["sigma_OF"] < 1e-9)
    t("exact_t10a.py agrees with itself and with the registered decimals", EXACT.main(verbose=False) == 0)
    print("SELFTEST " + ("PASSED: every non-CONVERGING state returns NOT A RESULT with the "
                         "value on the reference; CONVERGING reaches PASS and GATE FAIL; "
                         "the readers and the plant work" if ok else "FAILED"))
    return 0 if ok else 1


# ---------------------------------------------------------------------------
def main():
    if "--selftest" in sys.argv:
        return selftest()

    print("re-deriving the references (exact_t10a.py) ...")
    if EXACT.main(verbose=False) != 0:
        refuse("REFUSE: the exact-theory derivation does not agree with itself; "
               "no reference can be trusted until it does.")
    sigma = sigma_used()
    ref = EXACT.references(sigma)
    for name, reg_v, drv_v in (
            ("S0", REG["rows"]["S0"]["reference"], ref["spheres"]["q1"]),
            ("S1", REG["rows"]["S1"]["reference"], ref["spheres"]["q2"]),
            ("B0", REG["rows"]["B0"]["reference"], ref["box_q"]["floor"]),
            ("B1", REG["rows"]["B1"]["reference"], ref["box_q"]["ceiling"]),
            ("B2", REG["rows"]["B2"]["reference"], ref["box_q"]["x0"]),
            ("B3", REG["rows"]["B3"]["reference"], ref["box_q"]["y0"]),
            ("sigma", REG["sigma"]["sigma_OF"], sigma)):
        if abs(reg_v - drv_v) / abs(drv_v) > 2e-9:
            refuse(f"REFUSE: registered {name} = {reg_v} disagrees with the derivation {drv_v}")
    print(f"  sigma used by the solver (etc/controlDict): {sigma:.9e}")

    missing = [c for c in REG["required_markers"]
               if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: rung is PENDING -- no completion marker for " + ", ".join(missing))
    optional = [c for c in REG["optional_cases"] if os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]

    out = dict(Fs=FS, r=R_REFINE, sigma=sigma, closure_tol=CLOSURE_TOL,
               discrimination_factor=DISC_FACTOR, rows=[], controls=[], cases={})

    # ---- measurements -----------------------------------------------------
    M = {}
    for c in REG["required_markers"] + optional:
        print(f"\nmeasuring {c} ...")
        M[c] = measure(c, sigma, want_F=True)
        m = M[c]
        conv = m["convergence"]
        print(f"  time {m['time']}, {m['n_cells']} cells; convergence {conv['state']}"
              + (f" (max change {conv['max_change']:.3e} of scale {conv['scale']:.4g} between {conv['between']})"
                 if "max_change" in conv else f" ({conv.get('why')})"))
        pc = m["planted_control"]
        print(f"  planted-zero control: {'recovered ' + repr(pc.get('recovered')) if pc.get('ok') else 'FAILED ' + str(pc)}")
        for p in m["order"]:
            pp = m["patches"][p]
            print(f"  {p:8s} n {pp['n']:5d}  A {pp['area']:.8f}  q_leaving {pp['q_leaving']:14.6f}"
                  f"  T {pp['T']:.1f}  eps {pp['eps']}"
                  + (f"  rowsum max defect {m['rowsum'][p]['max_defect']:.3e}" if "rowsum" in m else ""))
        if "closure_F" in m:
            print(f"  closure raw {m['closure_raw']:.3e}  from-F {m['closure_F']:.3e}  "
                  f"excess {m['closure_excess']:.3e} (tol {CLOSURE_TOL})  "
                  f"reciprocity max defect {m['reciprocity_max_defect']:.3e}  "
                  f"python-vs-solver max rel {m['python_vs_solver_max_rel']:.3e}"
                  + ("  -> VOID" if m["void"] else ""))
        if m["geometry"].get("facet_deficit_inner") is not None:
            g = m["geometry"]
            print(f"  faceting deficit inner {g['facet_deficit_inner']:+.3e} outer {g['facet_deficit_outer']:+.3e}")
        if m["log"]:
            print(f"  log: {m['log']}")
        out["cases"][c] = m
        if not pc.get("ok"):
            refuse(f"REFUSE: the planted-zero control failed on {c}; a zero from this reader is not evidence")

    # ---- rows ---------------------------------------------------------------
    print(f"\n{'-' * 70}\nregistered rows")
    twin_of = {"S": "S_f_q", "B": "B_f_q"}
    smooth_of = {"S": "S_f_s", "B": "B_f_s"}
    for tag, spec in REG["rows"].items():
        lv = REG["levels"]["spheres" if spec["case_prefix"] == "S" else "box"]
        vals = {l: row_value(M[lv[l]], spec["patch"]) for l in LEVELS}
        conv = {l: M[lv[l]]["convergence"]["state"] for l in LEVELS}
        void = {l: M[lv[l]]["void"] for l in LEVELS}
        twin = row_value(M[twin_of[spec["case_prefix"]]], spec["patch"])
        print(f"\n### {tag}  {spec['quantity']}   reference {spec['reference']:.6f}")
        for l in LEVELS:
            print(f"    {l}  {vals[l]:.8f}   ({lv[l]})")
        print(f"    GaussQuadTol 0.001 twin {twin:.8f}   smoothing-true twin "
              f"{row_value(M[smooth_of[spec['case_prefix']]], spec['patch']):.8f}")
        r = grade_row(tag, vals, spec["reference"], conv, void, twin, spec["C2_departure_pct"])
        r["quantity"] = spec["quantity"]
        r["smoothing_twin_value"] = row_value(M[smooth_of[spec["case_prefix"]]], spec["patch"])
        if isinstance(spec["patch"], list):
            a, b = (M[lv["f"]]["patches"][p]["q_leaving"] for p in spec["patch"])
            r["pair_values_f"] = [a, b]
            r["pair_asymmetry_rel"] = abs(a - b) / abs(0.5 * (a + b))
            print(f"    pair symmetry guard (finest): {a:.6f} / {b:.6f}, rel {r['pair_asymmetry_rel']:.2e}")
        if "grid_triple" in r:
            print(f"    grid triple: {r['grid_triple']}")
        out["rows"].append(r)

    def band_of(tag):
        return next((r.get("band_pct") for r in out["rows"] if r["row"] == tag), None)

    def row_of(tag):
        return next(r for r in out["rows"] if r["row"] == tag)

    # ---- controls -----------------------------------------------------------
    print(f"\n{'-' * 70}\ncontrols (each MUST fail if the rung is sound)")
    ctl = out["controls"]

    def plant_against(name, tag, value, against, must="FAIL", note=""):
        b = band_of(tag)
        dev = 100.0 * abs(value - against) / abs(against)
        met = (b is not None and dev > b) if must == "FAIL" else None
        ctl.append(dict(control=name, row=tag, value=value, graded_against=against,
                        deviation_pct=dev, band_pct=b, must=must, met=met, note=note))
        print(f"  {name:28s} {tag}: {value:.4f} vs {against:.4f} -> {dev:.2f} % vs band {b}"
              f"  -> {'MET (fails, as it must)' if met else ('NOT MET' if met is False else 'reported')}")

    q1f = M["S_f"]["patches"]["inner"]["q_leaving"]
    plant_against("C1_black_body", "S0", q1f, ref["C1_black"])
    plant_against("C2_parallel_plate", "S0", q1f, ref["C2_plate"])
    q2f = M["S_f"]["patches"]["outer"]["q_leaving"]
    plant_against("C2_parallel_plate", "S1", q2f, -ref["C2_plate"])
    # C1-live
    q1c1 = M["S_C1"]["patches"]["inner"]["q_leaving"]
    b0 = band_of("S0")
    repro = 100.0 * abs(q1c1 - q1f) / abs(q1f)
    reproduces = b0 is not None and repro <= b0
    dev_black = 100.0 * abs(q1c1 - ref["C1_black"]) / ref["C1_black"]
    dev_grey = 100.0 * abs(q1c1 - REG["rows"]["S0"]["reference"]) / REG["rows"]["S0"]["reference"]
    c1l = dict(control="C1_live_S_C1", value=q1c1, S_f_value=q1f,
               departure_from_S_f_pct=repro, band_pct=b0, reproduces_S_f=reproduces,
               deviation_from_black_pct=dev_black, lands_in_band_on_black=(b0 is not None and dev_black <= b0),
               deviation_from_grey_pct=dev_grey, must="FAIL against grey; NOT reproduce S_f",
               met=(b0 is not None and dev_grey > b0 and not reproduces))
    ctl.append(c1l)
    print(f"  C1_live_S_C1: eps = 1 run gives {q1c1:.4f}; S_f gave {q1f:.4f} ({repro:.2f} % apart, band {b0});"
          f" vs black {ref['C1_black']:.3f}: {dev_black:.3f} %; vs grey: {dev_grey:.2f} %"
          f"  -> {'MET' if c1l['met'] else 'NOT MET'}"
          + ("  ** S_C1 REPRODUCES S_f: EMISSIVITY DICTIONARY NOT READ -- SPHERE ROWS VOID, BLOCKED **"
             if reproduces else ""))
    blocked = reproduces
    # C2 box, C2b
    cube_q = ref["C2_cube_q"]
    opp_q = ref["C2b_opposite_q"]
    patch_of = {"B0": "floor", "B1": "ceiling", "B2": "x0", "B3": "y0"}
    for tag, p in patch_of.items():
        spec = REG["rows"][tag]
        vf = row_value(M["B_f"], spec["patch"])
        plant_against("C2_cube_matrix", tag, vf, cube_q[p])
        plant_against("C2b_opposite_only", tag, vf, opp_q[p], must="REPORTED")
    # C3a: a zero field through the pipeline
    for tag in REG["rows"]:
        plant_against("C3a_radiation_off_zero", tag, 0.0, REG["rows"][tag]["reference"])
    # C3b: the solved uniform box
    for tag, p in patch_of.items():
        spec = REG["rows"][tag]
        v = row_value(M["B_C3"], spec["patch"])
        plant_against("C3b_uniform_box_solved", tag, v, spec["reference"],
                      note=f"B_C3 max|qr| {M['B_C3']['max_abs_qr']:.3e} W/m2 against sigma T^4 = {sigma * 300 ** 4:.1f}")
    print(f"  B_C3 max |qr| over every face: {M['B_C3']['max_abs_qr']:.3e} W/m2 (must be zero to round-off)")

    # ---- reported: Hottel ---------------------------------------------------
    if "H_2d" in M:
        h = REG["hottel_2d_reported_only"]
        print(f"\n{'-' * 70}\nT10a-3 Hottel 2D rectangle (REPORTED ONLY, identity under Charter 2a, not counted)")
        for p, rf in (("floor", h["q_floor"]), ("ceiling", h["q_ceiling"]), ("x0", h["q_wall"]), ("x1", h["q_wall"])):
            v = M["H_2d"]["patches"][p]["q_leaving"]
            print(f"  {p:8s} {v:.6f} vs {rf:.6f}: {100 * abs(v - rf) / abs(rf):.2e} %")
        out["hottel_reported"] = {p: M["H_2d"]["patches"][p]["q_leaving"] for p in M["H_2d"]["order"]}

    # ---- summary --------------------------------------------------------------
    with open(os.path.join(HERE, "gate_t10a.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    rows = out["rows"]
    n = {v: sum(1 for r in rows if r["verdict"] == v) for v in (PASS, GATE_FAIL, NOT_A_RESULT, GATE_REACHED)}
    unmet = [c for c in ctl if c.get("met") is False]
    print(f"\n{'-' * 70}")
    print(f"  {len(rows)} registered rows: {n[PASS]} PASS, {n[GATE_FAIL]} GATE FAIL, "
          f"{n[NOT_A_RESULT]} NOT A RESULT, {n[GATE_REACHED]} GATE REACHED (reported, not graded)")
    print(f"  {len(ctl)} control rows, {len(unmet)} NOT MET"
          + ("" if not unmet else " -- the rung is unsound: " + ", ".join(f"{c['control']}/{c.get('row')}" for c in unmet)))
    if blocked:
        print("  RUNG BLOCKED: the emissivity dictionary is not read (C1-live); sphere rows are VOID")
    bad = [c for c in M if M[c]["convergence"]["state"] != "CONVERGED"]
    if bad:
        print(f"  unconverged cases: {bad}")
    voided = [c for c in M if M[c].get("void")]
    if voided:
        print(f"  VOID runs (closure guard): {voided}")
    print("  GRADES NO PARTICIPATING MEDIUM, NO SPECTRAL EFFECT, NO CONVECTION AND NO CONJUGATE COUPLING.")
    return EXIT_FAIL if (n[GATE_FAIL] or unmet or blocked) else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
