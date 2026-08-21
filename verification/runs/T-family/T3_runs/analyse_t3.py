#!/usr/bin/env python3
"""
T3 comparator -- heated backward-facing step at Vogel and Eaton (1985)
conditions, kOmegaSST low-Re, Stanton number on the heated wall.

WRITTEN AND COMMITTED BEFORE ANY CASE EXISTED (Charter 2d).  At the moment of
writing the run tree held T3_CONTRACT.md, the builder, the mesh check, the
runner, the marker and the secondary digitisation; no case directory, no
STATUS file and no DONE marker.  The enforcement test is the one Charter 2d
names: this file's commit timestamp against the earliest DONE marker in
this directory, and the sha256 of this file at analysis time (written into
gate_t3.json) against the committed blob.

THE REFERENCE IS READ FROM FILES, NEVER TYPED HERE.
  * T3_reference_primary.json -- Vogel and Eaton (1985) values with their
    stated uncertainty.  NOT OBTAINED at the time of writing.  While it does
    not exist every graded row is BLOCKED, and the comparator says so rather
    than grading against something else.  Its format, fixed here so that no
    later choice can shape it:
        {"rows": {"G1": {"value": ..., "uncertainty": ..., "units": ...},
                  "G2": ..., "G3": ..., "G4": ...},
         "digitised": true|false,
         "provenance": ...}
    The band is the stated uncertainty; if "digitised" is true the
    digitisation increment (from the secondary file) is added in quadrature.
  * T3_secondary_digitisation.json -- Smirnov et al. (2016), Figure 9, a
    REPRODUCTION of the Vogel and Eaton symbols in an open paper, digitised
    by digitise_t3_secondary.py.  It states no experimental uncertainty and
    ARMS NO BAND.  Its values are printed beside every graded row as
    REPORTED information only.

THE T1b FLAW IS NOT REPEATED (T1b_RESULTS.md section 8, docket D440): a
graded row whose grid triple is not CONVERGING returns NOT A RESULT, with the
fine value and the triple printed beside it, and never PASS -- whether or not
a band exists.  The verdict reads the triple state before it reads the band.

WHAT THIS COMPARATOR CANNOT SEE, stated because a check that overstates its
reach is worse than none:
  * whether the experiment's inlet boundary layer, free-stream turbulence or
    aspect ratio are reproduced.  The inlet is uniform and the flow is 2D;
    the D_m arm measures the sensitivity to the inlet layer and nothing here
    can say which layer the experiment had beyond its quoted delta/H.
  * anything about the heat-transfer closure OTHER than through Prt on this
    one geometry at this one Reynolds number.  The P_m arm separates Prt 1.0
    from 0.85; it does not rank closures.
  * the primary data.  Until T3_reference_primary.json exists every graded
    row is BLOCKED, and the secondary's digitisation increment (half a
    symbol width) is a resolution, not an uncertainty.
  * three-dimensionality.  The secondary's own 3D RANS differs from its 2D
    RANS by about 4 % in the recirculation zone; a 2D calculation cannot
    see that.
  * the outlet.  Only the O_m arm can, and only at the 1 % level registered.

Behaviour (contract T3_CONTRACT.md, pre-registration T3_PREREGISTRATION.md):
  exit 2 (REFUSE) unless DONE.<case> exists for all eight cases, the
  planted-zero control passes and the secondary JSON parses; exit 1 if any
  graded row is GATE FAIL; exit 0 otherwise.  --selftest exercises the
  verdict logic on synthetic numbers without any case and exits 0 only if
  every check passes.
"""
import datetime
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T1_DIR = os.path.normpath(os.path.join(HERE, "..", "T1_runs"))
sys.path.insert(0, T1_DIR)
import analyse_t1c as T1C                                   # noqa: E402

# ---- registered constants (contract and pre-registration) ------------------
CASES = ["R_c", "R_m", "R_f", "P_m", "C_lam_m", "W_m", "D_m", "O_m"]
LADDER = {"c": "R_c", "m": "R_m", "f": "R_f"}
LEVELS = ("c", "m", "f")
FS = 1.25                              # Roache safety factor, three levels
PLANT = 1.234e-03                      # K, planted-zero control perturbation
STATIONS_H = (1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20)
PEAK_XMIN_H = 1.5                      # St_peak searched at x/H >= this
XR_IGNORE_H = 0.5                      # crossings below this are the corner eddy
OUTLET_INDEP_TOL = 0.01                # |St_20H(O_m) - St_20H(R_m)| / St_20H(R_m)
PRT_PROVISIONAL_FLOOR = 0.03           # registered provisional separation floor
CLAM_FLOOR = 0.25                      # trivial baseline must differ by more
HEAT_BALANCE_TOL_PCT = 0.5             # guard, reported, never tallied
WF_YPLUS_FLOOR = 30.0                  # wall-function validity floor
USD_PER_CORE_HOUR = 0.0513
N_PROCS = 1
SECONDARY_JSON = os.path.join(HERE, "T3_secondary_digitisation.json")
PRIMARY_JSON = os.path.join(HERE, "T3_reference_primary.json")
GATE_JSON = os.path.join(HERE, "gate_t3.json")
VERDICTS = ("PASS", "GATE FAIL", "NOT A RESULT", "BLOCKED", "REPORTED", "PENDING")
GRADED = {"G1": "St_peak", "G2": "x_peak_H", "G3": "St_10H", "G4": "St_20H"}
EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2
NUM = r"[-+0-9.eE]+"


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def case_val(case_dir, key):
    """Numeric value of a CASE.txt key (the first token; units follow it)."""
    return float(T1C.case_txt(case_dir, key).split()[0])


# ---------------------------------------------------------------------------
# polyMesh readers.  Nothing about the format is assumed beyond what the T1
# readers already rely on: an ASCII FoamFile header, a count, an opening
# parenthesis on its own line, one entry per line.
# ---------------------------------------------------------------------------
def _list_body(path):
    """Text of the top-level list in an ASCII OpenFOAM file: after the count
    line and the '(' that follows it.  Returns (count, body)."""
    txt = open(path, errors="replace").read()
    m = re.search(r"\n(\d+)\s*\n\(\s*\n", txt)
    if not m:
        refuse(f"cannot find the list header in {path}")
    return int(m.group(1)), txt[m.end():]


def read_points(case_dir):
    n, body = _list_body(os.path.join(case_dir, "constant", "polyMesh", "points"))
    pts = [tuple(float(v) for v in s.split())
           for s in re.findall(r"\(([^)]*)\)", body)[:n]]
    if len(pts) != n:
        refuse(f"points: expected {n}, parsed {len(pts)} in {case_dir}")
    return pts


def read_faces(case_dir):
    n, body = _list_body(os.path.join(case_dir, "constant", "polyMesh", "faces"))
    faces = [tuple(int(v) for v in s.split())
             for k, s in re.findall(r"(\d+)\(([^)]*)\)", body)[:n]]
    if len(faces) != n:
        refuse(f"faces: expected {n}, parsed {len(faces)} in {case_dir}")
    return faces


def read_labels(case_dir, name):
    n, body = _list_body(os.path.join(case_dir, "constant", "polyMesh", name))
    vals = [int(v) for v in re.findall(r"-?\d+", body)[:n]]
    if len(vals) != n:
        refuse(f"{name}: expected {n}, parsed {len(vals)} in {case_dir}")
    return vals


def owner_note_ncells(case_dir):
    txt = open(os.path.join(case_dir, "constant", "polyMesh", "owner"),
               errors="replace").read(4000)
    m = re.search(r'note\s+"[^"]*nCells:(\d+)', txt)
    if not m:
        refuse(f"no nCells note in polyMesh/owner of {case_dir}")
    return int(m.group(1))


def read_boundary(case_dir):
    """patch name -> dict(type, nFaces, startFace)."""
    txt = open(os.path.join(case_dir, "constant", "polyMesh", "boundary"),
               errors="replace").read()
    body = txt[txt.index("FoamFile"):]
    body = body[body.index("}") + 1:]          # past the FoamFile dict
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^{}]*)\}", body):
        name, blk = m.group(1), m.group(2)
        t = re.search(r"\btype\s+(\w+)\s*;", blk)
        nf = re.search(r"\bnFaces\s+(\d+)\s*;", blk)
        sf = re.search(r"\bstartFace\s+(\d+)\s*;", blk)
        if t and nf and sf:
            out[name] = dict(type=t.group(1), nFaces=int(nf.group(1)),
                             startFace=int(sf.group(1)))
    if not out:
        refuse(f"no patches parsed from polyMesh/boundary in {case_dir}")
    return out


def face_centre_area(face, pts):
    """Centre (mean of vertices) and area (|0.5 sum p_i x p_i+1| about the
    centre, exact for planar polygons) of one face."""
    P = [pts[i] for i in face]
    n = len(P)
    c = tuple(sum(p[k] for p in P) / n for k in range(3))
    ax = ay = az = 0.0
    for i in range(n):
        a = tuple(P[i][k] - c[k] for k in range(3))
        b = tuple(P[(i + 1) % n][k] - c[k] for k in range(3))
        ax += a[1] * b[2] - a[2] * b[1]
        ay += a[2] * b[0] - a[0] * b[2]
        az += a[0] * b[1] - a[1] * b[0]
    return c, 0.5 * math.sqrt(ax * ax + ay * ay + az * az)


# ---------------------------------------------------------------------------
# field readers: the boundaryField of a patch, with an owner-cell fallback
# ---------------------------------------------------------------------------
def patch_block(path, patch):
    """The text inside `patch { ... }` of the boundaryField, anchored at the
    four-space indent OpenFOAM writes, so 'inlet' never matches 'inletOutlet'
    and 'wall' never matches 'heatedWall'."""
    txt = open(path, errors="replace").read()
    i = txt.find("boundaryField")
    if i < 0:
        return None
    m = re.search(r"\n    " + re.escape(patch) + r"\s*\n?\s*\{(.*?)\n    \}",
                  txt[i:], re.S)
    return m.group(1) if m else None


def read_patch_field(path, patch, n_faces, fallback=None, vector=False):
    """Values on a patch as a list of length n_faces.

    Reads the `value` entry (uniform or nonuniform).  When the patch carries
    NO value entry -- ESI v2606 writes fixedGradient and zeroGradient without
    one (the T1c lesson) -- `fallback` decides: a list of owner-cell values
    (already gathered for this patch) is used and the source is reported as
    'owner-cells'; None refuses, because for a wall nut or alphat the owner
    value is not the wall value and silently using it would be wrong.
    Returns (values, source)."""
    blk = patch_block(path, patch)
    if blk is None:
        refuse(f"patch {patch} absent from {path}")
    kind = "vector" if vector else "scalar"
    mv = re.search(r"\bvalue\s+nonuniform\s+List<" + kind + r">\s*\n?\s*(\d+)\s*\(",
                   blk, re.S)
    if mv:
        n = int(mv.group(1))
        body = blk[mv.end():]
        if vector:
            vals = [tuple(float(x) for x in s.split())
                    for s in re.findall(r"\(([^)]*)\)", body)[:n]]
        else:
            vals = [float(x) for x in re.findall(NUM, body)[:n]]
        if len(vals) != n or n != n_faces:
            refuse(f"patch {patch} in {path}: {len(vals)} values parsed, "
                   f"{n} declared, {n_faces} faces")
        return vals, "value"
    mu = re.search(r"\bvalue\s+uniform\s+(\([^)]*\)|" + NUM + r")\s*;", blk)
    if mu:
        v = mu.group(1)
        val = (tuple(float(x) for x in v.strip("()").split()) if v.startswith("(")
               else float(v))
        return [val] * n_faces, "value-uniform"
    if fallback is None:
        refuse(f"patch {patch} in {path} carries no value entry and no "
               "fallback is admissible for this field")
    if len(fallback) != n_faces:
        refuse(f"owner fallback for {patch} in {path}: {len(fallback)} != {n_faces}")
    return list(fallback), "owner-cells"


def iterative_convergence_vector(case_dir, field="U", tol=1e-6):
    """T1C.iterative_convergence for a vector field: the largest change in
    any component relative to the range of the magnitude."""
    ts = sorted((d for d in os.listdir(case_dir)
                 if re.fullmatch(r"\d+(\.\d+)?", d) and float(d) != 0.0),
                key=float)
    if len(ts) < 2:
        return dict(state="UNJUDGED", why=f"only {len(ts)} checkpoint(s)")
    a = T1C.read_internal(os.path.join(case_dir, ts[-2], field), vector=True)
    b = T1C.read_internal(os.path.join(case_dir, ts[-1], field), vector=True)
    if len(a) != len(b):
        return dict(state="UNJUDGED", why="checkpoint sizes differ")
    dmax = max(abs(x[k] - y[k]) for x, y in zip(a, b) for k in range(3))
    mags = [math.sqrt(sum(c * c for c in v)) for v in b]
    rng = max(mags) - min(mags)
    rel = dmax / rng if rng > 0 else 0.0
    return dict(state="CONVERGED" if rel <= tol else "NOT_CONVERGED",
                max_change=dmax, field_range=rng, relative=rel,
                between=(ts[-2], ts[-1]), tol=tol)


# ---------------------------------------------------------------------------
# planted-zero control (analyse_pesweep.py, carried across)
# ---------------------------------------------------------------------------
def plant_into_T(path):
    """Add PLANT to the first internal value of a T file, IN PLACE, and read
    the file back from disk to prove the plant landed.  Returns (before, after)."""
    txt = open(path).read().split("\n")
    start = None
    for i in range(len(txt) - 2):
        if txt[i].strip().isdigit() and txt[i + 1].strip() == "(":
            start = i + 2
            break
    if start is None:
        raise RuntimeError(f"cannot locate the internal field in {path}")
    before = float(txt[start].strip())
    txt[start] = repr(before + PLANT)
    open(path, "w").write("\n".join(txt))
    back = float(open(path).read().split("\n")[start].strip())
    if abs((back - before) - PLANT) > 1e-12:
        raise RuntimeError(f"the plant did not land: {before} -> {back}")
    return before, back


def planted_zero_control(case_dir):
    """Copy the last two checkpoints' T files to a temp case, plant PLANT into
    the EARLIER one, read it back from disk, and run the convergence reader on
    the copy.  The reader must report max change >= PLANT (the real change
    may already exceed it; what is established is that a PLANT-sized
    difference is VISIBLE to the reader, so a zero it returns on the real
    case is a statement about the fields)."""
    ts = sorted((x for x in os.listdir(case_dir)
                 if re.fullmatch(r"\d+(\.\d+)?", x) and float(x) > 0), key=float)
    if len(ts) < 2:
        return dict(passed=False, why="fewer than two checkpoints")
    tmp = tempfile.mkdtemp(prefix="t3plant_")
    try:
        work = os.path.join(tmp, os.path.basename(case_dir))
        for t in ts[-2:]:
            os.makedirs(os.path.join(work, t))
            shutil.copy(os.path.join(case_dir, t, "T"), os.path.join(work, t, "T"))
        before, after = plant_into_T(os.path.join(work, ts[-2], "T"))
        c = T1C.iterative_convergence(work)
        seen = c.get("max_change", 0.0)
        return dict(passed=(seen >= PLANT - 1e-15), planted=PLANT,
                    read_back_delta=after - before, reader_max_change=seen,
                    reader_state=c.get("state"), between=ts[-2:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# grid convergence with unequal refinement ratios (Celik et al. 2008)
# ---------------------------------------------------------------------------
def gci_unequal(f_coarse, f_med, f_fine, r21, r32, fs=FS):
    """Observed order and GCI on the finest level for ratios r21 = h2/h1 and
    r32 = h3/h2 that need not be equal.  Same states as T1C.gci; when
    r21 == r32 the fixed-point iteration has q(p) = 0 and the result is
    T1C.gci's exactly (asserted in --selftest).

        p = | ln|e32/e21| + q(p) | / ln r21,
        q(p) = ln( (r21^p - s) / (r32^p - s) ),  s = sign(e32/e21)

    Returns dict(state=...) with order, GCI_pct, richardson when CONVERGING.
    """
    e21 = f_med - f_fine
    e32 = f_coarse - f_med
    if e21 == 0.0:
        return dict(state="EXACT", e21=e21, e32=e32)
    ratio = e32 / e21
    if ratio < 0.0:
        return dict(state="OSCILLATORY", e21=e21, e32=e32, ratio=ratio)
    p = math.log(abs(ratio)) / math.log(r21)
    if p <= 0.0:
        # with unequal ratios q(p) would need r^p - 1 > 0; the initial
        # estimate already says the error is not shrinking
        return dict(state="DIVERGENT", order=p, e21=e21, e32=e32)
    it = 0
    if r21 != r32:
        for it in range(1, 201):
            try:
                q = math.log((r21 ** p - 1.0) / (r32 ** p - 1.0))
            except ValueError:
                return dict(state="DIVERGENT", order=p, e21=e21, e32=e32,
                            iterations=it)
            p_new = abs(math.log(abs(ratio)) + q) / math.log(r21)
            if abs(p_new - p) < 1e-13:
                p = p_new
                break
            p = 0.5 * (p + p_new)            # damped; the map is a contraction
        else:
            return dict(state="NO_ORDER", order=p, e21=e21, e32=e32,
                        why="order iteration did not converge in 200 steps")
    if p <= 0.0:
        return dict(state="DIVERGENT", order=p, e21=e21, e32=e32, iterations=it)
    if p < 0.5:
        return dict(state="STAGNANT", order=p, e21=e21, e32=e32, iterations=it)
    den = r21 ** p - 1.0
    return dict(state="CONVERGING", order=p, e21=e21, e32=e32, iterations=it,
                GCI_pct=100.0 * fs * abs(e21 / f_fine) / den,
                GCI_abs=fs * abs(e21) / den,
                richardson=f_fine + e21 / den, r21=r21, r32=r32)


# ---------------------------------------------------------------------------
# small numerical helpers (standard library only)
# ---------------------------------------------------------------------------
def interp(xs, ys, x):
    """Linear interpolation on sorted xs; None outside the range."""
    if x < xs[0] or x > xs[-1]:
        return None
    import bisect
    i = bisect.bisect_left(xs, x)
    if i == 0:
        return ys[0]
    if xs[i] == x:
        return ys[i]
    x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def parabolic_peak(x, y, i):
    """Vertex of the parabola through points i-1, i, i+1; falls back to the
    discrete point when the vertex leaves the bracket."""
    x0, x1, x2 = x[i - 1], x[i], x[i + 1]
    y0, y1, y2 = y[i - 1], y[i], y[i + 1]
    d = (x0 - x1) * (x0 - x2) * (x1 - x2)
    if d == 0:
        return x1, y1, False
    A = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / d
    B = (x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0) + x0 * x0 * (y1 - y2)) / d
    C = (x1 * x2 * (x1 - x2) * y0 + x2 * x0 * (x2 - x0) * y1
         + x0 * x1 * (x0 - x1) * y2) / d
    if A >= 0:
        return x1, y1, False
    xv = -B / (2 * A)
    if not (x0 <= xv <= x2):
        return x1, y1, False
    return xv, A * xv * xv + B * xv + C, True


def column_at(Cx, Cy, x_target, y_lo, y_hi):
    """Indices of the cells in the cell column nearest x_target among cells
    with y in (y_lo, y_hi), sorted by y; plus the column's x."""
    cand = [i for i in range(len(Cx)) if y_lo < Cy[i] < y_hi]
    xs = sorted(set(round(Cx[i], 9) for i in cand))
    xsel = min(xs, key=lambda v: abs(v - x_target))
    idx = sorted((i for i in cand if round(Cx[i], 9) == xsel), key=lambda i: Cy[i])
    return idx, xsel


# ---------------------------------------------------------------------------
# measure one case
# ---------------------------------------------------------------------------
def measure(case_dir):
    name = os.path.basename(case_dir)
    t = T1C.latest_time(case_dir)
    r = T1C.foam(case_dir, "postProcess -func writeCellCentres -latestTime "
                           "> log.writeCellCentres 2>&1")
    if r.returncode != 0:
        refuse(f"writeCellCentres failed in {case_dir} (rc {r.returncode})")
    td = os.path.join(case_dir, t)
    Cx = T1C.read_internal(os.path.join(td, "Cx"))
    Cy = T1C.read_internal(os.path.join(td, "Cy"))
    T = T1C.read_internal(os.path.join(td, "T"))
    U = T1C.read_internal(os.path.join(td, "U"), vector=True)
    nC = len(T)
    if not (len(Cx) == len(Cy) == len(U) == nC):
        refuse(f"field sizes differ in {case_dir}/{t}")
    alphat = T1C.read_internal(os.path.join(td, "alphat"))
    nut_path = os.path.join(td, "nut")
    has_nut = os.path.isfile(nut_path)
    nut = T1C.read_internal(nut_path) if has_nut else [0.0] * nC
    if len(alphat) == 1:
        alphat = alphat * nC
    if len(nut) == 1:
        nut = nut * nC

    H = case_val(case_dir, "H")
    nu = case_val(case_dir, "nu")
    Pr = case_val(case_dir, "Pr")
    Prt = case_val(case_dir, "Prt")
    dTdn = case_val(case_dir, "dTdn_wall")
    T_in = case_val(case_dir, "T_in")
    U_in = case_val(case_dir, "U_in")
    endTime = case_val(case_dir, "endTime")
    alpha = nu / Pr

    # ---- geometry, READ ---------------------------------------------------
    pts = read_points(case_dir)
    faces = read_faces(case_dir)
    owner = read_labels(case_dir, "owner")
    bnd = read_boundary(case_dir)
    for p in ("heatedWall", "inlet", "outlet"):
        if p not in bnd:
            refuse(f"patch {p} absent from polyMesh/boundary in {case_dir}")
    nCells = owner_note_ncells(case_dir)
    if nCells != nC:
        refuse(f"owner note says {nCells} cells, fields have {nC} in {case_dir}")
    y_wall = min(p[1] for p in pts)
    y_top = max(p[1] for p in pts)
    if abs(y_wall) > 1e-12 * H:
        refuse(f"heated wall is at y = {y_wall!r}, not 0, in {case_dir}")

    def patch_faces(p):
        b = bnd[p]
        out = []
        for k in range(b["nFaces"]):
            fi = b["startFace"] + k
            c, A = face_centre_area(faces[fi], pts)
            out.append(dict(face=fi, owner=owner[fi], centre=c, area=A))
        return out

    hw = patch_faces("heatedWall")
    nH = len(hw)
    hw_owner = [f["owner"] for f in hw]
    # wall values of nut and alphat: the patch carries them (calculated 0 or a
    # wall function); no owner fallback is admissible for these
    nut_w = (read_patch_field(nut_path, "heatedWall", nH)[0] if has_nut
             else [0.0] * nH)
    alphat_w, alphat_src = read_patch_field(os.path.join(td, "alphat"),
                                            "heatedWall", nH)
    # T on the heated wall: fixedGradient writes no value; owner fallback
    T_w_patch, T_w_src = read_patch_field(os.path.join(td, "T"), "heatedWall",
                                          nH, fallback=[T[o] for o in hw_owner])

    # ---- U_ref at the centreline y = 3H, x = -3.3H ------------------------
    idx, x_col = column_at(Cx, Cy, -3.3 * H, H, y_top)
    ys = [Cy[i] for i in idx]
    ux = [U[i][0] for i in idx]
    U_ref = interp(ys, ux, 3.0 * H)
    if U_ref is None:
        refuse(f"cannot interpolate U at y = 3H in column x = {x_col} of {case_dir}")
    Re_ach = U_ref * H / nu

    # ---- delta99 at x = -3.8H, floor (y from H up) and top wall -----------
    idx, x_d = column_at(Cx, Cy, -3.8 * H, H, y_top)
    ys = [Cy[i] for i in idx]
    ux = [U[i][0] for i in idx]
    U_core = interp(ys, ux, 3.0 * H)

    def delta99(ys_, ux_, y_ref, sign):
        """Smallest distance from y_ref at which ux >= 0.99 U_core, walking
        away from the wall; crossing interpolated between cells."""
        target = 0.99 * U_core
        prev = None
        for y, u in zip(ys_, ux_):
            if u >= target:
                if prev is None:
                    return abs(y - y_ref), "first cell already >= 0.99 U_core"
                y0, u0 = prev
                yc = y0 + (y - y0) * (target - u0) / (u - u0)
                return abs(yc - y_ref), "interpolated"
            prev = (y, u)
        return None, "never reached 0.99 U_core"
    d99_floor, how_f = delta99(ys, ux, H, +1)
    d99_top, how_t = delta99(ys[::-1], ux[::-1], y_top, -1)

    # ---- per heated-wall face -------------------------------------------
    rows = []
    for k, f in enumerate(hw):
        o = f["owner"]
        d = Cy[o] - y_wall                      # READ wall-normal distance
        T_w = T[o] + dTdn * d
        aeff = alpha + alphat_w[k]
        q_kin = aeff * dTdn
        St = q_kin / (U_ref * (T_w - T_in)) if T_w != T_in else float("nan")
        tau = (nu + nut_w[k]) * U[o][0] / d
        Cf = tau / (0.5 * U_ref ** 2)
        yplus = d * math.sqrt(abs(tau)) / nu
        rows.append(dict(x=f["centre"][0], xH=f["centre"][0] / H, d=d, T_w=T_w,
                         T_owner=T[o], alphat_w=alphat_w[k], nut_w=nut_w[k],
                         alphaEff_w=aeff, q_kin=q_kin, St=St, tau_w=tau, Cf=Cf,
                         yplus=yplus, area=f["area"]))
    rows.sort(key=lambda r: r["x"])
    xH = [r["xH"] for r in rows]
    St_f = [r["St"] for r in rows]
    tau_f = [r["tau_w"] for r in rows]
    Cf_f = [r["Cf"] for r in rows]
    yp = [r["yplus"] for r in rows]

    # reattachment: negative-to-positive crossings of tau_w, x/H >= 0.5
    crossings = []
    for i in range(len(rows) - 1):
        if tau_f[i] < 0.0 <= tau_f[i + 1] and xH[i] >= XR_IGNORE_H:
            xc = xH[i] + (0.0 - tau_f[i]) * (xH[i + 1] - xH[i]) / (tau_f[i + 1] - tau_f[i])
            crossings.append(xc)
    x_R_H = crossings[-1] if crossings else None

    St_at = {f"{s:g}": interp(xH, St_f, float(s)) for s in STATIONS_H}
    Cf_15 = interp(xH, Cf_f, 15.0)
    cand = [i for i in range(len(rows)) if xH[i] >= PEAK_XMIN_H]
    ipk = max(cand, key=lambda i: St_f[i])
    if 0 < ipk < len(rows) - 1:
        x_pk, St_pk, refined = parabolic_peak(xH, St_f, ipk)
    else:
        x_pk, St_pk, refined = xH[ipk], St_f[ipk], False

    # ---- heat-balance ledger, kinematic units (m3 K / s) -----------------
    Q_wall = sum(r["alphaEff_w"] * dTdn * r["area"] for r in rows)
    led = dict(Q_wall=Q_wall)
    Q_adv = Q_cond = 0.0
    mass = {}
    for p in ("inlet", "outlet"):
        pf = patch_faces(p)
        n = len(pf)
        own = [f["owner"] for f in pf]
        phi_p, phi_src = read_patch_field(os.path.join(td, "phi"), p, n)
        T_p, T_src = read_patch_field(os.path.join(td, "T"), p, n,
                                      fallback=[T[o] for o in own])
        at_p, _ = read_patch_field(os.path.join(td, "alphat"), p, n,
                                   fallback=[alphat[o] for o in own])
        qa = qc = 0.0
        for k, f in enumerate(pf):
            o = own[k]
            c = f["centre"]
            d_f = math.sqrt((c[0] - Cx[o]) ** 2 + (c[1] - Cy[o]) ** 2)
            qa += phi_p[k] * (T_p[k] - T_in)
            # diffusive flux OUT of the domain: -alphaEff dT/dn_out A
            qc += -(alpha + at_p[k]) * (T_p[k] - T[o]) / d_f * f["area"]
        Q_adv += qa
        Q_cond += qc
        mass[p] = sum(phi_p)
        led[p] = dict(Q_adv=qa, Q_cond_out=qc, phi_sum=mass[p], n_faces=n,
                      phi_source=phi_src, T_source=T_src)
    led.update(Q_adv=Q_adv, Q_cond_boundary_out=Q_cond,
               mass_in=-mass["inlet"], mass_out=mass["outlet"],
               mass_imbalance_rel=((mass["outlet"] + mass["inlet"]) / abs(mass["inlet"])
                                   if mass["inlet"] else None))
    res = (Q_wall - Q_adv - Q_cond) / Q_wall if Q_wall else None
    led["closure_residual"] = res
    led["imbalance_pct"] = 100.0 * abs(Q_wall - Q_adv - Q_cond) / abs(Q_wall) if Q_wall else None
    led["within_tolerance"] = (led["imbalance_pct"] is not None
                               and led["imbalance_pct"] <= HEAT_BALANCE_TOL_PCT)
    dTb = Q_adv / mass["outlet"] if mass["outlet"] else None
    Tw20 = interp(xH, [r["T_w"] for r in rows], 20.0)
    led["bulk_temperature_rise_outlet"] = dTb
    led["Tw_minus_Tin_at_20H"] = (Tw20 - T_in) if Tw20 is not None else None
    led["ratio_bulk_rise_to_wall_excess_20H"] = ((dTb / (Tw20 - T_in))
                                                 if dTb is not None and Tw20 is not None
                                                 and Tw20 != T_in else None)

    conv_T = T1C.iterative_convergence(case_dir, "T")
    conv_U = iterative_convergence_vector(case_dir, "U")
    state = conv_T["state"]
    if state == "CONVERGED" and conv_U["state"] == "NOT_CONVERGED":
        state = "NOT_CONVERGED"
    if conv_T["state"] == "UNJUDGED" or conv_U["state"] == "UNJUDGED":
        state = "UNJUDGED"

    return dict(case=name, time=t, endTime=endTime, nCells=nCells,
                H=H, nu=nu, Pr=Pr, Prt=Prt, dTdn=dTdn, T_in=T_in, U_in=U_in,
                U_ref=U_ref, U_ref_column_x=x_col, Re_achieved=Re_ach,
                U_core_at_m3p8H=U_core, delta99_floor_H=(d99_floor / H if d99_floor else None),
                delta99_floor_how=how_f,
                delta99_top_H=(d99_top / H if d99_top else None), delta99_top_how=how_t,
                y_wall=y_wall, y_top=y_top, n_heated_faces=nH,
                T_wall_source=T_w_src, alphat_wall_source=alphat_src, has_nut=has_nut,
                St_peak=St_pk, x_peak_H=x_pk, peak_refined=refined,
                St_peak_discrete=St_f[ipk], x_peak_H_discrete=xH[ipk],
                St_at=St_at, St_10H=St_at["10"], St_20H=St_at["20"], Cf_15H=Cf_15,
                x_R_H=x_R_H, x_R_first_H=(crossings[0] if crossings else None),
                n_crossings=len(crossings), crossings_H=crossings,
                yplus_min=min(yp), yplus_max=max(yp), yplus_mean=sum(yp) / len(yp),
                yplus_frac_below_30=sum(1 for v in yp if v < WF_YPLUS_FLOOR) / len(yp),
                ledger=led, convergence_T=conv_T, convergence_U=conv_U,
                convergence_state=state,
                wall_profile=[dict(xH=r["xH"], St=r["St"], Cf=r["Cf"], yplus=r["yplus"],
                                   T_w=r["T_w"], d=r["d"]) for r in rows])


# ---------------------------------------------------------------------------
# verdict logic, pure functions (exercised by --selftest)
# ---------------------------------------------------------------------------
def triple_of(meas, key):
    return tuple(meas[l][key] for l in LEVELS)


def ratios_from_ncells(meas):
    Nc, Nm, Nf = (meas[l]["nCells"] for l in LEVELS)
    return math.sqrt(Nf / Nm), math.sqrt(Nm / Nc)


def band_for(prim_row, digitised, increment):
    unc = float(prim_row["uncertainty"])
    if digitised and increment:
        return math.sqrt(unc * unc + increment * increment)
    return unc


def graded_verdict(row_id, name, fine, triple, conv_states, gci, primary,
                   secondary=None, extra_not_a_result=None):
    """The ordered verdict for a graded row.

    (1) a level not CONVERGED         -> NOT A RESULT
    (2) triple not CONVERGING         -> NOT A RESULT   (BINDING; D440)
    (2b) extra_not_a_result given     -> NOT A RESULT   (G4 outlet test)
    (3) no primary row                -> BLOCKED, secondary deviation REPORTED
    (4) band = uncertainty (+ digitisation increment in quadrature)
        |fine - value| <= band        -> PASS else GATE FAIL
    """
    row = dict(row=row_id, quantity=name, value=fine, triple=list(triple),
               iterative_convergence=conv_states, grid=gci)
    if secondary is not None:
        row["secondary"] = secondary
        if secondary.get("value") is not None and fine is not None:
            row["deviation_from_secondary"] = fine - secondary["value"]
            row["deviation_from_secondary_rel"] = ((fine - secondary["value"])
                                                   / secondary["value"])
    bad = [l for l in LEVELS if conv_states.get(l) != "CONVERGED"]
    if bad:
        row.update(verdict="NOT A RESULT",
                   why="level " + ",".join(bad) + " not iteratively converged")
        return row
    if gci.get("state") != "CONVERGING":
        row.update(verdict="NOT A RESULT",
                   why=f"grid triple is {gci.get('state')}; no band can be armed",
                   order=gci.get("order"))
        return row
    row["GCI_pct"] = gci["GCI_pct"]
    row["richardson"] = gci["richardson"]
    row["order"] = gci["order"]
    if extra_not_a_result:
        row.update(verdict="NOT A RESULT", why=extra_not_a_result)
        return row
    if primary is None:
        row.update(verdict="BLOCKED",
                   why="reference NOT OBTAINED: Vogel and Eaton 1985 primary not "
                       "held; see T3_PREREGISTRATION.md section 2")
        return row
    prow = primary["rows"].get(row_id)
    if prow is None:
        row.update(verdict="BLOCKED",
                   why=f"primary file holds no row {row_id}")
        return row
    inc = (secondary or {}).get("increment")
    band = band_for(prow, bool(primary.get("digitised")), inc)
    dev = abs(fine - float(prow["value"]))
    row.update(reference=float(prow["value"]), reference_uncertainty=prow["uncertainty"],
               band=band, deviation=dev, units=prow.get("units"),
               verdict="PASS" if dev <= band else "GATE FAIL")
    return row


# ---------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------
def load_secondary():
    try:
        J = json.load(open(SECONDARY_JSON))
    except Exception as e:                       # noqa: BLE001
        refuse(f"secondary digitisation does not parse: {e}")
    d = J["derived_from_experiment"]
    sec = {"G1": dict(value=d["St_peak"]["value"], increment=d["St_peak"]["increment"]),
           "G2": dict(value=d["St_peak"]["x_peak_H"], increment=d["St_peak"]["x_increment"]),
           "G3": dict(value=d["St_10H"]["value"], increment=d["St_10H"]["increment"]),
           "G4": dict(value=d["St_20H"]["value"], increment=d["St_20H"]["increment"]),
           "M1": dict(value=d["x_R_H"]["value"], increment=d["x_R_H"]["increment"])}
    for v in sec.values():
        v["status"] = "SECONDARY (Smirnov et al. 2016 Fig. 9 reproduction); arms no band"
    return J, sec


def load_primary():
    if not os.path.isfile(PRIMARY_JSON):
        return None
    try:
        P = json.load(open(PRIMARY_JSON))
    except Exception as e:                       # noqa: BLE001
        refuse(f"{PRIMARY_JSON} exists but does not parse: {e}")
    if "rows" not in P:
        refuse(f"{PRIMARY_JSON} has no 'rows'")
    return P


def read_status(root, case):
    p = os.path.join(root, f"STATUS.{case}")
    if not os.path.isfile(p):
        return None
    s = open(p).read()
    m = re.search(r"rc=(\d+)\s+wall=(\d+)\s+checkMesh_rc=(\d+)", s)
    return dict(rc=int(m.group(1)), wall_s=int(m.group(2)),
                checkMesh_rc=int(m.group(3))) if m else dict(raw=s.strip())


def rel(a, b):
    return (a - b) / b if (a is not None and b) else None


def fmt(v, nd=6):
    if v is None:
        return "None"
    if isinstance(v, float):
        return f"{v:.{nd}g}"
    return str(v)


def main(argv):
    if "--selftest" in argv:
        return selftest()
    # --root DIR: grade a different run tree (used only to exercise this
    # comparator end-to-end on a scratch copy; the reference files are always
    # the ones beside this script and gate_t3.json is written under root)
    root = HERE
    if "--root" in argv:
        root = os.path.abspath(argv[argv.index("--root") + 1])
    gate_json = os.path.join(root, "gate_t3.json")
    t_start = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # ---- refusals ---------------------------------------------------------
    missing = [c for c in CASES if not os.path.isfile(os.path.join(root, f"DONE.{c}"))]
    if missing:
        refuse("no completion marker for " + ", ".join(missing))
    J_sec, SEC = load_secondary()
    PRIM = load_primary()
    pz = planted_zero_control(os.path.join(root, "R_m"))
    print(f"planted-zero control on R_m: {pz}")
    if not pz.get("passed"):
        refuse("planted-zero control failed: the convergence reader cannot see a "
               f"{PLANT} K difference; its zeros mean nothing")

    # ---- measurements -----------------------------------------------------
    M = {}
    for c in CASES:
        print(f"measuring {c} ...", flush=True)
        M[c] = measure(os.path.join(root, c))
    ladder = {l: M[LADDER[l]] for l in LEVELS}
    conv_states = {l: ladder[l]["convergence_state"] for l in LEVELS}
    r21, r32 = ratios_from_ncells(ladder)
    print(f"effective refinement ratios from nCells: r21 = {r21:.4f}, r32 = {r32:.4f}")
    if r21 <= 1.0 or r32 <= 1.0:
        refuse(f"the ladder does not refine: r21 = {r21:.4f}, r32 = {r32:.4f}")

    triples = {}
    for key in ("St_peak", "x_peak_H", "St_10H", "St_20H", "x_R_H", "Cf_15H"):
        tr = triple_of(ladder, key)
        if any(v is None for v in tr):
            triples[key] = dict(state="UNMEASURED", triple=list(tr))
        else:
            triples[key] = dict(gci_unequal(*tr, r21, r32), triple=list(tr))

    # ---- graded rows --------------------------------------------------------
    rows = []
    Rm, Om = M["R_m"], M["O_m"]
    out_dev = rel(Om["St_20H"], Rm["St_20H"])
    outlet_ok = out_dev is not None and abs(out_dev) <= OUTLET_INDEP_TOL
    for rid, key in GRADED.items():
        extra = None
        if rid == "G4" and not outlet_ok:
            extra = (f"outlet-independence test failed: |St_20H(O_m) - St_20H(R_m)|"
                     f"/St_20H(R_m) = {fmt(abs(out_dev) if out_dev is not None else None)}"
                     f" > {OUTLET_INDEP_TOL}")
        row = graded_verdict(rid, key, ladder["f"][key], triple_of(ladder, key),
                             conv_states, triples[key], PRIM, SEC[rid], extra)
        row["kind"] = "GRADE"
        rows.append(row)

    # ---- M1: reattachment, always REPORTED (attribution lever) ------------
    rows.append(dict(row="M1", kind="REPORTED", quantity="x_R_H",
                     value=ladder["f"]["x_R_H"], triple=list(triple_of(ladder, "x_R_H")),
                     grid=triples["x_R_H"], secondary=SEC["M1"],
                     first_crossing=ladder["f"]["x_R_first_H"],
                     n_crossings=ladder["f"]["n_crossings"],
                     verdict="REPORTED",
                     why="attribution lever: a momentum error is mesh or solver; "
                         "a Stanton error with correct momentum is the thermal closure"))

    # ---- discrimination rows ------------------------------------------------
    Pm, Cl, Wm, Dm = M["P_m"], M["C_lam_m"], M["W_m"], M["D_m"]
    band_G1 = next((r.get("band") for r in rows if r["row"] == "G1"), None)
    band_G3 = next((r.get("band") for r in rows if r["row"] == "G3"), None)
    sep_pk = abs(Pm["St_peak"] - Rm["St_peak"]) / Rm["St_peak"]
    sep_10 = abs(Pm["St_10H"] - Rm["St_10H"]) / Rm["St_10H"]
    if band_G1 is not None:
        sep_ok = abs(Pm["St_peak"] - Rm["St_peak"]) > band_G1
        label = "against the armed band"
    else:
        sep_ok = sep_pk > PRT_PROVISIONAL_FLOOR
        label = f"PROVISIONAL, against the registered floor {PRT_PROVISIONAL_FLOOR}"
    rows.append(dict(row="DP", kind="DISCRIMINATION", quantity="Prt 1.0 vs 0.85",
                     St_peak_P_m=Pm["St_peak"], St_peak_R_m=Rm["St_peak"],
                     separation_peak_rel=sep_pk, separation_10H_rel=sep_10,
                     band_G1=band_G1, band_G3=band_G3,
                     status=("SEPARATED" if sep_ok else "NOT SEPARATED") + " (" + label + ")",
                     P_m_convergence=Pm["convergence_state"], verdict="REPORTED"))

    dc = abs(Cl["St_peak"] - Rm["St_peak"]) / Rm["St_peak"]
    if Cl["convergence_state"] != "CONVERGED":
        dc_status = (f"NOT CONVERGED, UNMEASURED (not satisfied); St read at the last "
                     f"checkpoint {Cl['time']}")
    else:
        dc_status = ("SATISFIED" if dc > CLAM_FLOOR else "NOT SATISFIED") + \
                    f" (difference {dc:.3f} vs floor {CLAM_FLOOR})"
    rows.append(dict(row="DC", kind="DISCRIMINATION", quantity="trivial baseline C_lam_m",
                     St_peak_C_lam_m=Cl["St_peak"], St_peak_R_m=Rm["St_peak"],
                     difference_rel=dc, floor=CLAM_FLOOR,
                     C_lam_convergence=Cl["convergence_state"], status=dc_status,
                     verdict="REPORTED"))

    rows.append(dict(row="DW", kind="DISCRIMINATION", quantity="wall functions W_m vs R_m",
                     St_peak_diff_rel=rel(Wm["St_peak"], Rm["St_peak"]),
                     St_10H_diff_rel=rel(Wm["St_10H"], Rm["St_10H"]),
                     St_20H_diff_rel=rel(Wm["St_20H"], Rm["St_20H"]),
                     yplus_min=Wm["yplus_min"], yplus_max=Wm["yplus_max"],
                     yplus_mean=Wm["yplus_mean"],
                     frac_faces_yplus_below_30=Wm["yplus_frac_below_30"],
                     W_m_convergence=Wm["convergence_state"], verdict="REPORTED"))

    dd_shift = rel(Dm["St_peak"], Rm["St_peak"])
    rows.append(dict(row="DD", kind="DISCRIMINATION", quantity="thin inlet layer D_m vs R_m",
                     delta99_H_D_m=Dm["delta99_floor_H"], delta99_H_R_m=Rm["delta99_floor_H"],
                     St_peak_D_m=Dm["St_peak"], St_peak_R_m=Rm["St_peak"],
                     St_peak_shift_rel=dd_shift,
                     registered_prediction="St_peak(D_m) > St_peak(R_m)",
                     prediction_met=(dd_shift is not None and dd_shift > 0),
                     D_m_convergence=Dm["convergence_state"], verdict="REPORTED"))

    rows.append(dict(row="DO", kind="GUARD", quantity="outlet independence O_m vs R_m",
                     St_20H_diff_rel=out_dev, x_R_diff_H=(Om["x_R_H"] - Rm["x_R_H"]
                                                         if Om["x_R_H"] is not None
                                                         and Rm["x_R_H"] is not None else None),
                     criterion=OUTLET_INDEP_TOL, criterion_met=outlet_ok,
                     O_m_convergence=Om["convergence_state"], verdict="REPORTED"))

    for c in CASES:
        L = M[c]["ledger"]
        rows.append(dict(row=f"HB_{c}", kind="GUARD", quantity="heat balance",
                         case=c, closure_residual=L["closure_residual"],
                         imbalance_pct=L["imbalance_pct"], tolerance_pct=HEAT_BALANCE_TOL_PCT,
                         within_tolerance=L["within_tolerance"], verdict="REPORTED",
                         counted_in_tally=False))

    # ---- cost --------------------------------------------------------------
    cost = {}
    for c in CASES:
        st = read_status(root, c) or {}
        wall = st.get("wall_s")
        cost[c] = dict(wall_s=wall, nProcs=N_PROCS,
                       core_hours=(wall * N_PROCS / 3600.0 if wall is not None else None),
                       usd=(wall * N_PROCS / 3600.0 * USD_PER_CORE_HOUR if wall is not None else None),
                       predicted_core_s=case_val(os.path.join(root, c), "predicted_core_s"),
                       measured_core_s=(wall * N_PROCS if wall is not None else None))

    # ---- print --------------------------------------------------------------
    print("\n" + "=" * 78)
    print("T3 heated backward-facing step -- comparator output")
    print("=" * 78)
    print(f"{'case':10s} {'conv':14s} {'nCells':>8s} {'U_ref':>8s} {'Re_H':>8s} "
          f"{'St_peak':>9s} {'x_pk/H':>7s} {'St_10H':>9s} {'St_20H':>9s} {'x_R/H':>7s} "
          f"{'y+min':>6s} {'y+max':>6s} {'HB%':>7s}")
    for c in CASES:
        m = M[c]
        print(f"{c:10s} {m['convergence_state']:14s} {m['nCells']:8d} {m['U_ref']:8.4f} "
              f"{m['Re_achieved']:8.0f} {fmt(m['St_peak'],5):>9s} {fmt(m['x_peak_H'],4):>7s} "
              f"{fmt(m['St_10H'],5):>9s} {fmt(m['St_20H'],5):>9s} {fmt(m['x_R_H'],4):>7s} "
              f"{m['yplus_min']:6.2f} {m['yplus_max']:6.2f} "
              f"{fmt(m['ledger']['imbalance_pct'],3):>7s}")
    print(f"\nladder ratios r21 = {r21:.4f}, r32 = {r32:.4f}")
    for key, tr in triples.items():
        print(f"  {key:10s} triple {[fmt(v,6) for v in tr['triple']]}  state {tr['state']}"
              + (f"  p = {tr['order']:.3f}" if "order" in tr else "")
              + (f"  GCI_fine = {tr['GCI_pct']:.3f} %  RE = {fmt(tr['richardson'])}"
                 if tr.get("state") == "CONVERGING" else ""))
    print("\nrows")
    for r in rows:
        line = f"  {r['row']:8s} {r['verdict']:13s} {r.get('quantity','')}"
        if r["kind"] == "GRADE":
            line += (f"  fine = {fmt(r['value'])}  triple = {[fmt(v) for v in r['triple']]}"
                     f"  grid = {r['grid'].get('state')}")
            if "GCI_pct" in r:
                line += f"  GCI = {r['GCI_pct']:.3f} %"
            if "band" in r:
                line += f"  ref = {fmt(r['reference'])} +/- {fmt(r['band'])}  dev = {fmt(r['deviation'])}"
            if "deviation_from_secondary" in r:
                line += (f"  [SECONDARY, reported: {fmt(r['secondary']['value'])}"
                         f" +/- inc {fmt(r['secondary']['increment'],3)}, "
                         f"dev {fmt(r['deviation_from_secondary_rel']*100,3)} %]")
            if "why" in r:
                line += f"\n           -- {r['why']}"
        elif r["row"] == "M1":
            line += (f"  fine = {fmt(r['value'])}  triple = {[fmt(v) for v in r['triple']]}"
                     f"  grid = {r['grid'].get('state')}  crossings = {r['n_crossings']}"
                     f" (first {fmt(r['first_crossing'])})  [SECONDARY x_R/H = "
                     f"{fmt(r['secondary']['value'])} +/- {fmt(r['secondary']['increment'],3)}]")
        elif r["kind"] == "DISCRIMINATION":
            line += "  " + str(r.get("status", "")) + "  " + ", ".join(
                f"{k} = {fmt(v,4)}" for k, v in r.items()
                if isinstance(v, float) and k not in ("floor",))
        elif r["kind"] == "GUARD":
            if r["row"] == "DO":
                line += (f"  St_20H diff {fmt(r['St_20H_diff_rel'],4)}, x_R diff "
                         f"{fmt(r['x_R_diff_H'],4)} H, criterion {r['criterion']} "
                         f"{'MET' if r['criterion_met'] else 'NOT MET'}")
            else:
                line += (f"  {r['case']}: residual {fmt(r['closure_residual'],4)}, "
                         f"imbalance {fmt(r['imbalance_pct'],4)} % vs {r['tolerance_pct']} % "
                         f"-> {'within' if r['within_tolerance'] else 'OUTSIDE'} (never tallied)")
        print(line)
    print("\ncost")
    for c, k in cost.items():
        print(f"  {c:10s} wall {fmt(k['wall_s'])} s  core-h {fmt(k['core_hours'],4)}  "
              f"USD {fmt(k['usd'],3)}  predicted_core_s {fmt(k['predicted_core_s'])}  "
              f"measured {fmt(k['measured_core_s'])}")

    graded = [r for r in rows if r["kind"] == "GRADE"]
    fails = [r for r in graded if r["verdict"] == "GATE FAIL"]
    tally = {v: sum(1 for r in graded if r["verdict"] == v) for v in VERDICTS}
    print(f"\n{len(graded)} graded rows: " + ", ".join(f"{k} {v}" for k, v in tally.items() if v))
    if PRIM is None:
        print("PRIMARY NOT OBTAINED: no band is armed; a graded row that passes the "
              "convergence and triple gates is BLOCKED, and the secondary "
              "digitisation is printed for information only.")

    out = dict(rung="T3", generated_utc=t_start,
               finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               comparator_sha256=sha256(os.path.abspath(__file__)),
               secondary_sha256=sha256(SECONDARY_JSON),
               primary_sha256=(sha256(PRIMARY_JSON) if PRIM is not None else None),
               primary_present=PRIM is not None,
               done_markers={c: datetime.datetime.fromtimestamp(
                   os.path.getmtime(os.path.join(root, f"DONE.{c}")),
                   datetime.timezone.utc).isoformat() for c in CASES},
               planted_zero_control=pz, refinement_ratios=dict(r21=r21, r32=r32),
               Fs=FS, constants=dict(STATIONS_H=STATIONS_H, PEAK_XMIN_H=PEAK_XMIN_H,
                                     XR_IGNORE_H=XR_IGNORE_H, OUTLET_INDEP_TOL=OUTLET_INDEP_TOL,
                                     PRT_PROVISIONAL_FLOOR=PRT_PROVISIONAL_FLOOR,
                                     CLAM_FLOOR=CLAM_FLOOR, HEAT_BALANCE_TOL_PCT=HEAT_BALANCE_TOL_PCT,
                                     WF_YPLUS_FLOOR=WF_YPLUS_FLOOR, PLANT=PLANT),
               triples=triples, rows=rows, tally=tally,
               measurements={c: {k: v for k, v in M[c].items() if k != "wall_profile"}
                             for c in CASES},
               wall_profiles={c: M[c]["wall_profile"] for c in CASES},
               ledger={c: M[c]["ledger"] for c in CASES}, cost=cost,
               secondary_derived=J_sec["derived_from_experiment"])
    out["root"] = root
    with open(gate_json, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    print(f"wrote {gate_json}")
    return EXIT_FAIL if fails else EXIT_OK


# ---------------------------------------------------------------------------
# --selftest: the verdict logic on synthetic numbers, no case needed
# ---------------------------------------------------------------------------
def selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append(ok)
        print(f"  [{'ok' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))

    conv_ok = {l: "CONVERGED" for l in LEVELS}
    r = 1.6
    prim = {"rows": {"G1": dict(value=1.0, uncertainty=0.05, units="-")},
            "digitised": False}
    sec = dict(value=1.02, increment=0.01)

    print("(i) CONVERGING triple, PASS inside the band and GATE FAIL outside "
          "(mutation control: the fine value is moved)")
    tr = (1.10, 1.04, 1.01)
    g = gci_unequal(*tr, r, r)
    row = graded_verdict("G1", "St_peak", tr[2], tr, conv_ok, g, prim, sec)
    check("triple is CONVERGING", g["state"] == "CONVERGING", f"p = {g.get('order'):.3f}")
    check("inside band -> PASS", row["verdict"] == "PASS",
          f"dev {row.get('deviation')} band {row.get('band')}")
    tr2 = (1.29, 1.23, 1.20)
    g2 = gci_unequal(*tr2, r, r)
    row2 = graded_verdict("G1", "St_peak", tr2[2], tr2, conv_ok, g2, prim, sec)
    check("outside band -> GATE FAIL", row2["verdict"] == "GATE FAIL",
          f"dev {row2.get('deviation')} band {row2.get('band')}")
    prim_d = dict(prim, digitised=True)
    row3 = graded_verdict("G1", "St_peak", tr[2], tr, conv_ok, g, prim_d, sec)
    check("digitised primary widens the band in quadrature",
          abs(row3["band"] - math.hypot(0.05, 0.01)) < 1e-15, f"band {row3['band']}")

    print("(ii) DIVERGENT, STAGNANT, OSCILLATORY triples with the fine value "
          "inside the band -> NOT A RESULT every time (D440)")
    wide = {"rows": {"G1": dict(value=1.0, uncertainty=0.1, units="-")}, "digitised": False}
    for label, tr in (("DIVERGENT", (1.00, 1.02, 1.05)),
                      ("STAGNANT", (1.0, 1.03375, 1.06375)),
                      ("OSCILLATORY", (1.00, 1.10, 1.05))):
        g = gci_unequal(*tr, r, r)
        row = graded_verdict("G1", "St_peak", tr[2], tr, conv_ok, g, wide, sec)
        inside = abs(tr[2] - 1.0) <= 0.1
        check(f"{label}: state {g['state']}, inside band {inside} -> {row['verdict']}",
              g["state"] == label and inside and row["verdict"] == "NOT A RESULT",
              row.get("why", ""))
    conv_bad = dict(conv_ok, m="NOT_CONVERGED")
    g = gci_unequal(1.10, 1.04, 1.01, r, r)
    row = graded_verdict("G1", "St_peak", 1.01, (1.10, 1.04, 1.01), conv_bad, g, wide, sec)
    check("a level NOT_CONVERGED -> NOT A RESULT before any band",
          row["verdict"] == "NOT A RESULT" and "level m" in row["why"], row.get("why"))
    row = graded_verdict("G4", "St_20H", 1.01, (1.10, 1.04, 1.01), conv_ok, g, wide, sec,
                         extra_not_a_result="outlet-independence test failed")
    check("G4 outlet-independence failure -> NOT A RESULT", row["verdict"] == "NOT A RESULT")

    print("(iii) no primary file -> BLOCKED with the secondary deviation reported")
    row = graded_verdict("G1", "St_peak", 1.01, (1.10, 1.04, 1.01), conv_ok, g, None, sec)
    check("BLOCKED", row["verdict"] == "BLOCKED" and "NOT OBTAINED" in row["why"])
    check("secondary deviation carried as information",
          abs(row["deviation_from_secondary"] - (1.01 - 1.02)) < 1e-15)
    check("verdict vocabulary closed",
          all(v in VERDICTS for v in ("PASS", "GATE FAIL", "NOT A RESULT", "BLOCKED",
                                      "REPORTED", "PENDING")))

    print("(iv) gci_unequal with equal ratios reproduces T1C.gci to 1e-12")
    worst = 0.0
    same = True
    for tr in ((1.10, 1.04, 1.01), (1.0, 1.2, 1.3), (2.0, 1.5, 1.25), (1.0, 1.02, 1.05),
               (1.0, 1.03375, 1.06375), (1.0, 1.1, 1.05), (1.0, 1.0, 1.0), (3.1, 3.0, 3.0)):
        a = T1C.gci(*tr)
        b = gci_unequal(*tr, T1C.R_REFINE, T1C.R_REFINE)
        same &= a["state"] == b["state"]
        for k in ("order", "GCI_pct", "richardson"):
            if k in a:
                worst = max(worst, abs(a[k] - b[k]))
                same &= k in b
    check("states identical and numbers within 1e-12", same and worst <= 1e-12,
          f"max |diff| = {worst:.2e}")
    gu = gci_unequal(1.10, 1.04, 1.01, 1.5, 1.7)
    check("unequal ratios: iteration converges to a CONVERGING order",
          gu["state"] == "CONVERGING" and gu["iterations"] > 0,
          f"p = {gu['order']:.4f} after {gu['iterations']} iterations")
    # the converged p must satisfy Celik's equation
    p = gu["order"]
    resid = abs(p - abs(math.log(abs(gu["e32"] / gu["e21"]))
                        + math.log((1.5 ** p - 1) / (1.7 ** p - 1))) / math.log(1.5))
    check("fixed point satisfies the Celik equation", resid < 1e-10, f"residual {resid:.1e}")

    print("(v) planted-zero control machinery on a synthetic field file")
    tmp = tempfile.mkdtemp(prefix="t3self_")
    try:
        vals = [300.0 + 0.01 * i for i in range(50)]
        body = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class volScalarField;\n"
                "    object T;\n}\n\ndimensions [0 0 0 1 0 0 0];\n\n"
                "internalField   nonuniform List<scalar> \n50\n(\n"
                + "\n".join(repr(v) for v in vals) + "\n)\n;\n\nboundaryField\n{\n}\n")
        for t in ("18000", "20000"):
            os.makedirs(os.path.join(tmp, t))
            open(os.path.join(tmp, t, "T"), "w").write(body)
        c0 = T1C.iterative_convergence(tmp)
        check("identical checkpoints read as CONVERGED with zero change",
              c0["state"] == "CONVERGED" and c0["max_change"] == 0.0)
        pz = planted_zero_control(tmp)
        check("planted PLANT is read back from disk and seen by the reader",
              pz["passed"] and abs(pz["read_back_delta"] - PLANT) < 1e-12
              and abs(pz["reader_max_change"] - PLANT) < 1e-12, str(pz))
        orig = open(os.path.join(tmp, "18000", "T")).read()
        check("the control left the original file untouched",
              orig == body)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("(vi) interpolation and peak helpers")
    xs, ys = [0.0, 1.0, 2.0, 3.0], [0.0, 1.0, 0.0, -1.0]
    check("interp midpoint", abs(interp(xs, ys, 0.5) - 0.5) < 1e-15)
    check("interp outside -> None", interp(xs, ys, 4.0) is None)
    xv, yv, ok = parabolic_peak([0.0, 1.0, 2.0], [0.0, 1.0, 0.0], 1)
    check("parabolic peak through (0,0),(1,1),(2,0) is (1,1)",
          ok and abs(xv - 1.0) < 1e-12 and abs(yv - 1.0) < 1e-12)

    n_ok = sum(checks)
    print(f"\nselftest: {n_ok}/{len(checks)} checks passed")
    return EXIT_OK if n_ok == len(checks) else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
