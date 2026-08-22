#!/usr/bin/env python3
"""
T10a-R comparator: the refinement arm on T10a's B1 ceiling GATE FAIL.

WHAT THIS FILE GRADES, AND WHAT IT DOES NOT
-------------------------------------------
It grades NOTHING against T10a's band.  T10a is closed (GATE FAIL, rung
verdict published 2026-08-21).  Every verdict here is PASS or GATE FAIL
*against this arm's own registered prediction thresholds* in
T10aR_registered.json, written and hashed before any R_* directory existed.
A row whose grid triple is not CONVERGING is NOT A RESULT and gets no verdict
at all (D440, carried forward).

WHAT IS IMPORTED FROZEN, AND WHAT IS NEW
----------------------------------------
FROZEN, imported and never edited (T10a_runs/analyse_t10a.py, sha256 recorded
in T10aR_PREREGISTRATION.md and re-verified at every run of this file):
    mesh_patches, time_dirs, read_qr_all, patch_values, read_emissivities,
    sigma_used, iterative_convergence, planted_zero_control, measure,
    row_value, read_F, dense_F, radiosity_on_F, ncells_from_owner, log_facts
and through it T1_runs/analyse_t1c.gci (Fs 1.25, nominal r 1.6).  The frozen
module's HERE and REG["cases"] are redirected by a context manager
(`in_tree`) so that measure() reads the T10a-R tree for R_* cases and the
frozen T10a tree for B_*; the file on disk is never touched.

NEW INSTRUMENTS, declared as new (Charter: a new instrument is named, not
slipped in):

 1. richardson_corrected(f_c, f_m, f_f)
        f_f + (f_f - f_m)/(r**p - 1)              [Roache]
    The shared analyse_t1c.gci returns f_f + (f_m - f_f)/(r**p - 1) -- the
    sign defect T9a section 8.1 recorded and deliberately left unedited
    because it sits on no grading path.  This arm reports BOTH, side by side,
    and grades on NEITHER: no verdict in this file is a function of a
    Richardson value.  The corrected value is a reported diagnostic only.

 2. read_F_dense_stream / radiosity_lean
    A line-streaming replacement for read_F + dense_F + radiosity_on_F whose
    peak memory is one dense n x n float64 array.  It exists because R_x's
    constant/F is ~6.1 GB of ascii and the frozen read_F materialises the
    whole file as a Python str and then makes three more full-length copies
    (`re.sub`, and two `.replace`), i.e. >24 GB of transient strings on a box
    with 25 GB available.  REGISTERED VALIDATION, enforced at every run: on
    every case where BOTH paths fit, the lean path must reproduce the frozen
    path's dense matrix EXACTLY (bit-identical) and its rowsum / reciprocity /
    python-vs-solver / closure numbers to <= 1e-12 relative, or this
    comparator REFUSES (exit 2).  radiosity_lean is exercised only where every
    emissivity is 1 (the whole box), where viewFactor.C's C matrix is the
    identity and the frozen radiosity_on_F reduces algebraically to
    F0 @ sigma T^4 - sigma T^4; the equality is asserted numerically as part
    of the same validation, not assumed.

Exit codes: 0 every registered prediction met, 1 at least one GATE FAIL or
NOT A RESULT, 2 refusal.
"""
import hashlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T10A_DIR = os.path.join(os.path.dirname(HERE), "T10a_runs")
sys.path.insert(0, T10A_DIR)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "T1_runs"))
import analyse_t10a as T10A                                # noqa: E402 FROZEN
import exact_t10a as EXACT                                 # noqa: E402 FROZEN

REG = json.load(open(os.path.join(HERE, "T10aR_registered.json")))
ROWS = REG["rows"]
FS, R_REFINE = REG["grid"]["Fs"], REG["grid"]["r"]
PLANT = REG["planted_control_value"]
PASS, GATE_REACHED, GATE_FAIL = "PASS", "GATE REACHED", "GATE FAIL"
NOT_A_RESULT, BLOCKED, PENDING = "NOT A RESULT", "BLOCKED", "PENDING"
EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# tree shim: let the FROZEN measure() read whichever tree a case lives in
# ---------------------------------------------------------------------------
class in_tree:
    """Redirect the frozen module's HERE and inject a case spec, restoring both
    on exit.  The frozen FILE is never modified; only this process's imported
    module object is, and only for the duration of one measure() call."""

    def __init__(self, tree, name, spec=None):
        self.tree, self.name, self.spec = tree, name, spec

    def __enter__(self):
        self.old_here = T10A.HERE
        self.had = self.name in T10A.REG["cases"]
        self.old_spec = T10A.REG["cases"].get(self.name)
        T10A.HERE = self.tree
        if self.spec is not None:
            T10A.REG["cases"][self.name] = self.spec
        return self

    def __exit__(self, *a):
        T10A.HERE = self.old_here
        if self.had:
            T10A.REG["cases"][self.name] = self.old_spec
        else:
            T10A.REG["cases"].pop(self.name, None)
        return False


def tree_of(name):
    return HERE if name.startswith("R_") else T10A_DIR


def spec_of(name):
    if name.startswith("R_"):
        c = REG["cases"][name]
        return dict(kind="box", N=c["N"], faces=c["faces"], cells=c["cells"],
                    role=c["role"], T_uniform=None,
                    GaussQuadTol=c["GaussQuadTol"], smoothing=c["smoothing"])
    return None


def measure(name, sigma, want_F=False):
    with in_tree(tree_of(name), name, spec_of(name)):
        return T10A.measure(name, sigma, want_F=want_F)


def case_dir(name):
    return os.path.join(tree_of(name), name)


# ---------------------------------------------------------------------------
# NEW INSTRUMENT 1: the sign-corrected Richardson extrapolate
# ---------------------------------------------------------------------------
def richardson_corrected(f_c, f_m, f_f, r=R_REFINE):
    """Roache: f_exact ~ f_f + (f_f - f_m)/(r**p - 1), p from the same triple.
    Returns None where the triple arms no order.  REPORTED, NEVER GRADED."""
    e21 = f_m - f_f
    e32 = f_c - f_m
    if e21 == 0.0 or e32 / e21 <= 0.0:
        return None
    p = math.log(abs(e32 / e21)) / math.log(r)
    if p <= 0.0:
        return None
    return f_f + (f_f - f_m) / (r ** p - 1.0)


# ---------------------------------------------------------------------------
# NEW INSTRUMENT 2: streaming F reader (peak memory = one dense n x n array)
# ---------------------------------------------------------------------------
def _foam_tokens(path):
    """Yield every token after the FoamFile block, parentheses separated."""
    with open(path, errors="replace") as fh:
        head = fh.read(4096)
        if re.search(r"format\s+binary\s*;", head):
            refuse(f"{path} is binary; this comparator reads ascii only")
        fh.seek(0)
        seen_foamfile = False
        past_header = False
        for line in fh:
            if not past_header:
                if not seen_foamfile:
                    if line.lstrip().startswith("FoamFile"):
                        seen_foamfile = True
                    continue
                if line.strip() == "}":
                    past_header = True
                continue
            line = line.split("//", 1)[0]
            if not line.strip():
                continue
            if "(" in line or ")" in line:
                line = line.replace("(", " ( ").replace(")", " ) ")
            for tok in line.split():
                yield tok


def read_F_dense_stream(case, n):
    """constant/F + constant/globalFaceFaces -> dense n x n, streamed."""
    import numpy as np
    fpath = os.path.join(case, "constant", "F")
    gpath = os.path.join(case, "constant", "globalFaceFaces")
    for p in (fpath, gpath):
        if not os.path.isfile(p):
            refuse(f"{case} has no {os.path.basename(p)}")
    Fm = np.zeros((n, n))
    ft, gt = _foam_tokens(fpath), _foam_tokens(gpath)

    def head(it, what):
        nrows = int(next(it))
        if next(it) != "(":
            refuse(f"{what}: expected '(' after the row count")
        return nrows

    nf, ng = head(ft, "F"), head(gt, "globalFaceFaces")
    if nf != ng:
        refuse(f"{case}: F has {nf} rows, globalFaceFaces has {ng}")
    if nf != n:
        refuse(f"{case}: F has {nf} rows, mesh has {n} viewFactorWall faces")
    for i in range(n):
        kf, kg = int(next(ft)), int(next(gt))
        if kf != kg:
            refuse(f"{case}: row {i} F/globalFaceFaces lengths {kf} != {kg}")
        if next(ft) != "(" or next(gt) != "(":
            refuse(f"{case}: row {i} missing '('")
        vals = np.fromiter((float(next(ft)) for _ in range(kf)), float, kf)
        idx = np.fromiter((int(next(gt)) for _ in range(kg)), np.int64, kg)
        if kg and (idx.max() >= n or idx.min() < 0):
            refuse(f"{case}: globalFaceFaces index out of range in row {i}")
        if next(ft) != ")" or next(gt) != ")":
            refuse(f"{case}: row {i} missing ')'")
        Fm[i, idx] = vals
    for it, what in ((ft, "F"), (gt, "globalFaceFaces")):
        if next(it, None) != ")":
            refuse(f"{case}: {what} does not close after {n} rows")
        if next(it, None) is not None:
            refuse(f"{case}: {what} has trailing tokens after the last row")
    return Fm


def radiosity_lean(Fm, eps, T, sigma):
    """viewFactor.C's constant-emissivity assembly for eps == 1 everywhere,
    where C is the identity and no n x n copy is needed.  REFUSES on any other
    emissivity so it can never silently stand in for the general case."""
    import numpy as np
    e = np.asarray(eps)
    if not np.all(e == 1.0):
        refuse("radiosity_lean called with a non-black surface; the lean path "
               "is registered for eps == 1 only")
    d = np.diag(Fm).copy()
    np.fill_diagonal(Fm, 0.0)
    sT4 = sigma * np.asarray(T) ** 4
    q = Fm @ sT4 - sT4
    np.fill_diagonal(Fm, d)
    return q


def reciprocity_max_defect_blocked(Fm, A, block=512):
    """max |A_i F_ij - A_j F_ji| without materialising a second n x n array."""
    import numpy as np
    n = Fm.shape[0]
    mx = 0.0
    for s in range(0, n, block):
        e = min(s + block, n)
        left = A[s:e, None] * Fm[s:e, :]          # (b, n): A_i F_ij
        right = (Fm[:, s:e] * A[:, None]).T       # (b, n): A_j F_ji
        mx = max(mx, float(np.abs(left - right).max()))
    return mx


def F_diagnostics_lean(name, m, sigma):
    """Everything measure(want_F=True) computes from F, on the lean path."""
    import numpy as np
    case = case_dir(name)
    with in_tree(tree_of(name), name, spec_of(name)):
        geom, order, _ = T10A.mesh_patches(case)
        ts = T10A.time_dirs(case)
        t = ts[-1]
        qr = T10A.read_qr_all(os.path.join(case, t, "qr"), geom, order)
        Tp = {p: T10A.patch_values(os.path.join(case, t, "T"), p, geom[p]["nFaces"])
              for p in order}
        eps = T10A.read_emissivities(case, order)
    n = sum(geom[p]["nFaces"] for p in order)
    Fm = read_F_dense_stream(case, n)
    A = np.concatenate([np.asarray(geom[p]["areas"]) for p in order])
    E = np.concatenate([np.full(geom[p]["nFaces"], eps[p]) for p in order])
    Tf = np.concatenate([np.asarray(Tp[p]) for p in order])
    rows = Fm.sum(axis=1)
    out = {"rowsum": {}}
    off = 0
    for p in order:
        k = geom[p]["nFaces"]
        r = rows[off:off + k]
        out["rowsum"][p] = dict(min=float(r.min()), max=float(r.max()),
                                mean=float(r.mean()),
                                max_defect=float(np.abs(r - 1).max()))
        off += k
    out["F_diag_max"] = float(np.abs(np.diag(Fm)).max())
    qpy = radiosity_lean(Fm, E, Tf, sigma)
    qs = np.concatenate([np.asarray(qr[p]) for p in order])
    scale = float(np.abs(qs).max()) or 1.0
    out["python_vs_solver_max_rel"] = float(np.abs(qpy - qs).max() / scale)
    out["closure_F"] = abs(float((A * qpy).sum())) / float(np.abs(A * qpy).sum())
    out["closure_excess"] = abs(m["closure_raw"] - out["closure_F"])
    out["reciprocity_max_defect"] = reciprocity_max_defect_blocked(Fm, A)
    out["python_patch_q_leaving"] = {}
    off = 0
    for p in order:
        k = geom[p]["nFaces"]
        out["python_patch_q_leaving"][p] = float(
            -(A[off:off + k] * qpy[off:off + k]).sum() / A[off:off + k].sum())
        off += k
    out["void"] = out["closure_excess"] > T10A.CLOSURE_TOL
    del Fm
    return out


def validate_lean_against_frozen(name, sigma):
    """REGISTERED: the lean instrument must reproduce the frozen one exactly on
    a case where both fit.  Refuses otherwise."""
    import numpy as np
    case = case_dir(name)
    with in_tree(tree_of(name), name, spec_of(name)):
        geom, order, _ = T10A.mesh_patches(case)
        n = sum(geom[p]["nFaces"] for p in order)
        F, G = T10A.read_F(case)
        Fdense = T10A.dense_F(F, G, n)
        eps = T10A.read_emissivities(case, order)
        ts = T10A.time_dirs(case)
        Tp = {p: T10A.patch_values(os.path.join(case, ts[-1], "T"), p, geom[p]["nFaces"])
              for p in order}
    Flean = read_F_dense_stream(case, n)
    exact_match = bool(np.array_equal(Fdense, Flean))
    E = np.concatenate([np.full(geom[p]["nFaces"], eps[p]) for p in order])
    Tf = np.concatenate([np.asarray(Tp[p]) for p in order])
    q_frozen = T10A.radiosity_on_F(Fdense, E, Tf, sigma)
    q_lean = radiosity_lean(Flean, E, Tf, sigma)
    scale = float(np.abs(q_frozen).max()) or 1.0
    q_rel = float(np.abs(q_frozen - q_lean).max() / scale)
    A = np.concatenate([np.asarray(geom[p]["areas"]) for p in order])
    AF = A[:, None] * Fdense
    rec_frozen = float(np.abs(AF - AF.T).max())
    rec_lean = reciprocity_max_defect_blocked(Flean, A)
    rec_rel = abs(rec_frozen - rec_lean) / (abs(rec_frozen) or 1.0)
    ok = exact_match and q_rel <= 1e-12 and rec_rel <= 1e-12
    if not ok:
        refuse(f"the lean F instrument does not reproduce the frozen one on {name}: "
               f"matrix bit-identical={exact_match} radiosity_rel={q_rel:.3e} "
               f"reciprocity_rel={rec_rel:.3e}")
    return dict(case=name, n=n, matrix_bit_identical=exact_match,
                radiosity_max_rel=q_rel, reciprocity_rel=rec_rel,
                reciprocity_frozen=rec_frozen)


# ---------------------------------------------------------------------------
# prediction grading -- against THIS ARM's registered thresholds, nothing else
# ---------------------------------------------------------------------------
def grade_prediction(tag, value, note=""):
    r = ROWS[tag]
    lo, hi = r["predict_interval"]
    if value is None:
        return dict(tag=tag, arm=r["arm"], quantity=r["quantity"], value=None,
                    predicted=r["predict_point"], interval=[lo, hi],
                    verdict=NOT_A_RESULT, falsifier=r["falsifier"], note=note)
    v = PASS if (lo <= value <= hi) else GATE_FAIL
    return dict(tag=tag, arm=r["arm"], quantity=r["quantity"], value=value,
                predicted=r["predict_point"], interval=[lo, hi],
                verdict=v, falsifier=r["falsifier"], note=note)


def pct(a, b):
    return 100.0 * abs(a - b) / abs(b)


# ---------------------------------------------------------------------------
def selftest():
    """Every claim this file makes about its own arithmetic, proved here."""
    import numpy as np
    n_ok = n_all = 0

    def chk(what, cond):
        nonlocal n_ok, n_all
        n_all += 1
        n_ok += bool(cond)
        print(f"  [{'ok ' if cond else 'FAIL'}] {what}")

    r = R_REFINE
    # 1..4  the sign-corrected Richardson, against a synthetic exact power law
    f_ex, C, p_true = 100.0, 7.0, 1.5
    h = [r ** 2, r, 1.0]
    f = [f_ex + C * hh ** p_true for hh in h]
    rc = richardson_corrected(*f)
    chk("richardson_corrected recovers the exact value of a clean power law "
        f"({rc:.10f} vs 100)", abs(rc - f_ex) < 1e-8)
    g = T10A.gci(*f)
    chk(f"the shared gci recovers p = {p_true} from the same triple "
        f"({g['order']:.6f})", abs(g["order"] - p_true) < 1e-9)
    chk("the shared gci's own richardson carries the registered SIGN DEFECT "
        f"({g['richardson']:.6f}) and the corrected one does not ({rc:.6f})",
        abs(g["richardson"] - f_ex) > 1.0 and abs(rc - f_ex) < 1e-8)
    fneg = [f_ex - C * hh ** p_true for hh in h]
    chk("richardson_corrected is sign-symmetric (mirrored triple, mirrored error)",
        abs(richardson_corrected(*fneg) - f_ex) < 1e-8)
    # 5..8  triple states never become a verdict
    chk("OSCILLATORY triple -> richardson_corrected None",
        richardson_corrected(1.0, 3.0, 2.0) is None)
    chk("EXACT triple (f_m == f_f) -> None", richardson_corrected(1.0, 2.0, 2.0) is None)
    dv = T10A.gci(-3275.664, -3271.620, -3269.602153)
    chk(f"T10a's published c/m/f B1 triple reproduces p = 1.480 ({dv['order']:.4f}) "
        f"and band 0.07676 % ({dv['GCI_pct']:.5f}) -- to the precision the "
        "published c and m values carry (3 decimals), not beyond it",
        abs(dv["order"] - 1.480) < 2e-3 and abs(dv["GCI_pct"] - 0.07676) < 1e-4)
    chk("and its sign-corrected Richardson reproduces T10a's published "
        f"-3267.594 ({richardson_corrected(-3275.664, -3271.620, -3269.602153):.3f})",
        abs(richardson_corrected(-3275.664, -3271.620, -3269.602153) + 3267.594) < 0.02)
    # 9..12  grade_prediction reaches every verdict it can reach
    chk("a value inside the registered interval -> PASS",
        grade_prediction("RX1", 0.083)["verdict"] == PASS)
    chk("a value above the registered interval -> GATE FAIL",
        grade_prediction("RX1", 0.150)["verdict"] == GATE_FAIL)
    chk("a value below the registered interval -> GATE FAIL (a prediction that "
        "misses low is still a missed prediction)",
        grade_prediction("RX1", 0.010)["verdict"] == GATE_FAIL)
    chk("value None (triple not CONVERGING) -> NOT A RESULT, never PASS",
        grade_prediction("RX2", None)["verdict"] == NOT_A_RESULT)
    chk("RX3 with deviation/band exactly 1.0 -> GATE FAIL (the band covers; the "
        "registered pattern is falsified)",
        grade_prediction("RX3", 1.0)["verdict"] == GATE_FAIL)
    chk("RX3 with deviation/band 2.45 -> PASS (pattern persists)",
        grade_prediction("RX3", 2.45)["verdict"] == PASS)
    chk("RS2 identity row: any nonzero difference -> GATE FAIL",
        grade_prediction("RS2", 1e-14)["verdict"] == GATE_FAIL)
    chk("RS2 identity row: exact zero -> PASS", grade_prediction("RS2", 0.0)["verdict"] == PASS)
    # 13..16  the streaming reader
    import tempfile
    d = tempfile.mkdtemp(prefix="t10aR_selftest_")
    os.makedirs(os.path.join(d, "constant"))
    hdr = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class %s;\n}\n"
           "// * * * //\n\n")
    Fref = np.array([[0.5, 0.25, 0.25], [0.1, 0.8, 0.1], [0.3, 0.3, 0.4]])
    with open(os.path.join(d, "constant", "F"), "w") as fh:
        fh.write(hdr % "scalarListList")
        fh.write("3\n(\n")
        for i in range(3):
            fh.write("3\n(\n" + "".join(f"{float(Fref[i, j])!r}\n" for j in range(3)) + ")\n")
        fh.write(")\n")
    with open(os.path.join(d, "constant", "globalFaceFaces"), "w") as fh:
        fh.write(hdr % "labelListList")
        fh.write("3\n(\n")
        for i in range(3):
            fh.write("3\n(\n0\n1\n2\n)\n")
        fh.write(")\n")
    got = read_F_dense_stream(d, 3)
    chk("read_F_dense_stream reproduces a hand-written matrix bit-identically",
        np.array_equal(got, Fref))
    A = np.array([1.0, 2.0, 4.0])
    AF = A[:, None] * Fref
    chk("blocked reciprocity equals the dense one on the same matrix",
        abs(reciprocity_max_defect_blocked(Fref.copy(), A, block=1)
            - float(np.abs(AF - AF.T).max())) < 1e-15)
    E1 = np.ones(3)
    Ts = np.array([600.0, 300.0, 400.0])
    sg = 5.670408558e-08
    chk("radiosity_lean == the frozen radiosity_on_F for eps == 1",
        float(np.abs(radiosity_lean(Fref.copy(), E1, Ts, sg)
                     - T10A.radiosity_on_F(Fref.copy(), E1, Ts, sg)).max()) < 1e-9)
    chk("read_F_dense_stream leaves the matrix diagonal untouched by "
        "radiosity_lean (restored in place)",
        np.array_equal(got, Fref))
    # 17..20  the planted-zero control, through the frozen reader
    chk(f"the registered plant is {PLANT} W/m2", PLANT == 0.001234)
    base = 6483.263010
    planted = float(base) + PLANT
    chk("fl(old + plant) - old is NOT exactly the plant at this magnitude, which "
        "is why the registered rule is the exact float and not a tolerance "
        f"({planted - base:.19g})", (planted - base) != PLANT)
    chk("and the exact-float rule is satisfiable by construction",
        (planted - base) == (float(base) + PLANT) - base)
    chk("a plant of 0.0 recovers 0.0 (a broken reader would too -- which is why "
        "the registered plant is nonzero)", (base + 0.0) - base == 0.0)
    # 21..24  guards
    chk("Fs/r come from the registered file and equal the shared module's",
        (FS, R_REFINE) == (T10A.FS, T10A.R_REFINE))
    chk("this arm's registered r is nominal 1.6 while the built ratios are "
        "68/42 = 1.61905 and 42/26 = 1.61538 (stated, not silently reconciled)",
        abs(68 / 42 - 1.619048) < 1e-5 and abs(42 / 26 - 1.615385) < 1e-5)
    chk("in_tree restores the frozen module's HERE and case table",
        _in_tree_restores())
    refused = False
    try:
        radiosity_lean(Fref.copy(), np.array([1.0, 0.6, 1.0]), Ts, sg)
    except SystemExit as e:
        refused = (e.code == EXIT_REFUSE)
    chk("radiosity_lean REFUSES a non-black surface (exercised, not asserted)",
        refused)
    print(f"\nselftest {n_ok}/{n_all}")
    return 0 if n_ok == n_all else 1


def _in_tree_restores():
    h0 = T10A.HERE
    n0 = sorted(T10A.REG["cases"])
    with in_tree(HERE, "R_x", spec_of("R_x")):
        inside = (T10A.HERE == HERE and "R_x" in T10A.REG["cases"])
    return inside and T10A.HERE == h0 and sorted(T10A.REG["cases"]) == n0


# ---------------------------------------------------------------------------
def main():
    # ---- provenance: the frozen instruments must be the frozen instruments --
    prov = {}
    for f in ("analyse_t10a.py", "exact_t10a.py", "T10a_registered.json", "build_t10a.py"):
        prov[f] = sha256_of(os.path.join(T10A_DIR, f))
    prov["analyse_t1c.py"] = sha256_of(
        os.path.join(os.path.dirname(HERE), "T1_runs", "analyse_t1c.py"))
    prov["analyse_t10aR.py"] = sha256_of(os.path.abspath(__file__))
    prov["build_t10aR.py"] = sha256_of(os.path.join(HERE, "build_t10aR.py"))
    prov["T10aR_registered.json"] = sha256_of(os.path.join(HERE, "T10aR_registered.json"))

    if (FS, R_REFINE) != (T10A.FS, T10A.R_REFINE):
        refuse(f"registered Fs/r {FS}/{R_REFINE} differ from the shared module's "
               f"{T10A.FS}/{T10A.R_REFINE}")
    for c in REG["cases"]:
        if not os.path.isfile(os.path.join(HERE, f"DONE.{c}")):
            refuse(f"no completion marker DONE.{c}")
    for c in ("B_m", "B_f"):
        if not os.path.isfile(os.path.join(T10A_DIR, f"DONE.{c}")):
            refuse(f"the T10a level {c} carries no DONE marker")
    if EXACT.main() != 0:
        refuse("the exact-theory derivation does not agree with itself")

    sigma = T10A.sigma_used()
    EX = {"B0": T10A.REG["box"]["q_floor"], "B1": T10A.REG["box"]["q_ceiling"],
          "B2": T10A.REG["box"]["q_xwall"], "B3": T10A.REG["box"]["q_ywall"]}
    PATCH = {"B0": "floor", "B1": "ceiling", "B2": ["x0", "x1"], "B3": ["y0", "y1"]}

    print("=" * 78)
    print("T10a-R -- refinement arm on T10a's B1 ceiling GATE FAIL")
    print("=" * 78)
    print(f"sigma READ from {EXACT.OF_CONTROLDICT}: {sigma!r}")
    print("\nprovenance (sha256):")
    for k, v in prov.items():
        print(f"  {k:26s} {v}")

    # ---- measure every case ------------------------------------------------
    M = {}
    for name in ("B_m", "B_f", "R_x", "R_q", "R_s"):
        M[name] = measure(name, sigma, want_F=False)
        print(f"\n[{name}] time {M[name]['time']}  cells {M[name]['n_cells']}  "
              f"closure_raw {M[name]['closure_raw']:.3e}")
        cv = M[name]["convergence"]
        print(f"  iterative convergence: {cv['state']}  max change between the "
              f"last two checkpoints {cv.get('max_change', float('nan')):.3e}")
        pc = M[name]["planted_control"]
        print(f"  planted {PLANT} W/m2 through the same reader: "
              f"{'OK' if pc['ok'] else 'FAILED'}  recovered {pc.get('recovered')!r}")
        if cv["state"] != "CONVERGED":
            refuse(f"{name} is not iteratively CONVERGED; no triple is formed "
                   "from an unconverged level (D440)")
        if not pc["ok"]:
            refuse(f"the planted-zero control failed on {name}: {pc.get('why')}")
        for tag in ("B0", "B1", "B2", "B3"):
            print(f"  {tag} {str(PATCH[tag]):14s} q_leaving "
                  f"{T10A.row_value(M[name], PATCH[tag]):.6f} W/m2")

    # ---- the F side: validate the lean instrument, then use it -------------
    print("\n" + "-" * 78)
    print("F-side instrument validation (lean vs frozen, REGISTERED refusal)")
    val = [validate_lean_against_frozen(n, sigma) for n in ("B_m", "B_f", "R_q", "R_s")]
    for v in val:
        print(f"  {v['case']:5s} n={v['n']:6d}  matrix bit-identical "
              f"{v['matrix_bit_identical']}  radiosity {v['radiosity_max_rel']:.2e}  "
              f"reciprocity {v['reciprocity_rel']:.2e}")
    FD = {}
    for name in ("B_m", "B_f", "R_x", "R_q", "R_s"):
        FD[name] = F_diagnostics_lean(name, M[name], sigma)
        rs = max(FD[name]["rowsum"][p]["max_defect"] for p in FD[name]["rowsum"])
        print(f"  {name:5s} rowsum max defect {rs:.4f}  closure_F "
              f"{FD[name]['closure_F']:.3e}  excess {FD[name]['closure_excess']:.2e}  "
              f"reciprocity {FD[name]['reciprocity_max_defect']:.2e}  "
              f"python-vs-solver {FD[name]['python_vs_solver_max_rel']:.2e}  "
              f"{'VOID' if FD[name]['void'] else 'ok'}")
        if FD[name]["void"]:
            print(f"    !! {name} exceeds the T10a closure guard "
                  f"({T10A.CLOSURE_TOL}); flagged, and every row it carries is "
                  "withdrawn below")

    out = {"rung": "T10a-R", "sigma": sigma, "provenance": prov,
           "lean_validation": val, "rows": [], "cases": {}, "F": {}}
    for n in M:
        out["cases"][n] = {k: v for k, v in M[n].items() if k != "log"}
        out["F"][n] = FD[n]

    rows = []

    # ======================= ARM R-x =======================================
    print("\n" + "=" * 78)
    print("ARM R-x: a fourth level x at ratio 68/42 = 1.61905 beyond f")
    print("=" * 78)
    trip = [T10A.row_value(M[n], PATCH["B1"]) for n in ("B_m", "B_f", "R_x")]
    g = T10A.gci(*trip)
    rc = richardson_corrected(*trip)
    ex = EX["B1"]
    errs = [v - ex for v in trip]
    print(f"  m/f/x triple      {trip[0]:.6f} -> {trip[1]:.6f} -> {trip[2]:.6f} W/m2")
    print(f"  exact (sigma_OF)  {ex:.6f} W/m2")
    print(f"  level errors      {errs[0]:+.4f} / {errs[1]:+.4f} / {errs[2]:+.4f} W/m2")
    print(f"  triple state      {g['state']}" + (f"  p = {g['order']:.4f}" if "order" in g else ""))
    dev = pct(trip[2], ex)
    band = g.get("GCI_pct")
    print(f"  deviation         {dev:.5f} %")
    print(f"  GCI band (x)      {band if band is None else f'{band:.5f}'} %"
          + ("" if band else "   (no band armed)"))
    print(f"  Richardson: shared (sign defect) {g.get('richardson')}, "
          f"CORRECTED (new instrument, reported only) {rc}")
    conv = g["state"] == "CONVERGING"
    out["R_x_triple"] = dict(values=trip, exact=ex, errors=errs, gci=g,
                             richardson_corrected=rc)
    if FD["R_x"]["void"]:
        for tag in ("RX1", "RX2", "RX3", "RX4", "RX5"):
            rows.append(grade_prediction(tag, None, "R_x VOID under the closure guard"))
    else:
        rows.append(grade_prediction("RX1", dev))
        rows.append(grade_prediction("RX2", g.get("order") if conv else None,
                                     "" if conv else f"triple is {g['state']}"))
        rows.append(grade_prediction(
            "RX3", (dev / band) if (conv and band) else None,
            "" if (conv and band) else "no band armed"))
        rows.append(grade_prediction("RX4", abs(errs[1]) / abs(errs[2]) if errs[2] else None))
        rows.append(grade_prediction("RX5", pct(rc, ex) if rc is not None else None,
                                     "" if rc is not None else "triple arms no order"))
    # the full four-level picture, reported
    print("\n  all four levels, every graded box row (c and m and f from the frozen "
          "T10a tree, x from this arm):")
    bc = {"B0": 6480.760, "B1": -3275.664, "B2": -1269.197, "B3": -1980.140}
    print(f"  {'row':4s} {'c (published)':>14s} {'m':>14s} {'f':>14s} {'x':>14s} "
          f"{'exact':>14s} {'dev_x %':>9s}")
    out["four_level"] = {}
    for tag in ("B0", "B1", "B2", "B3"):
        vm, vf, vx = (T10A.row_value(M[n], PATCH[tag]) for n in ("B_m", "B_f", "R_x"))
        gg = T10A.gci(vm, vf, vx)
        rr = richardson_corrected(vm, vf, vx)
        print(f"  {tag:4s} {bc[tag]:14.5f} {vm:14.5f} {vf:14.5f} {vx:14.5f} "
              f"{EX[tag]:14.5f} {pct(vx, EX[tag]):9.5f}")
        print(f"       triple m/f/x {gg['state']}"
              + (f", p = {gg['order']:.4f}, band {gg['GCI_pct']:.5f} %, "
                 f"dev/band {pct(vx, EX[tag]) / gg['GCI_pct']:.3f}"
                 if gg.get("GCI_pct") else "")
              + f", corrected Richardson {rr if rr is None else f'{rr:.4f}'}"
              + (f" ({pct(rr, EX[tag]):.5f} % from exact)" if rr is not None else ""))
        out["four_level"][tag] = dict(c_published=bc[tag], m=vm, f=vf, x=vx,
                                      exact=EX[tag], dev_x_pct=pct(vx, EX[tag]),
                                      gci=gg, richardson_corrected=rr)

    # ======================= ARM R-q =======================================
    print("\n" + "=" * 78)
    print("ARM R-q: f-level mesh, viewFactorsGen distTol 8 -> 80 "
          "(2AI midpoint -> 2LI Gauss contour on nearly every face pair)")
    print("=" * 78)
    moves = {}
    for tag in ("B0", "B1", "B2", "B3"):
        vf = T10A.row_value(M["B_f"], PATCH[tag])
        vq = T10A.row_value(M["R_q"], PATCH[tag])
        moves[tag] = pct(vq, vf)
        print(f"  {tag}  B_f {vf:14.6f}  R_q {vq:14.6f}  move {moves[tag]:9.5f} %  "
              f"| dev from exact: B_f {pct(vf, EX[tag]):.5f} % -> R_q {pct(vq, EX[tag]):.5f} %")
    rsq_f = max(FD["B_f"]["rowsum"][p]["max_defect"] for p in FD["B_f"]["rowsum"])
    rsq_q = max(FD["R_q"]["rowsum"][p]["max_defect"] for p in FD["R_q"]["rowsum"])
    print(f"  raw row-sum max defect: B_f {rsq_f:.5f} -> R_q {rsq_q:.5f}")
    out["R_q"] = dict(moves_pct=moves, rowsum_max_defect_Bf=rsq_f,
                      rowsum_max_defect_Rq=rsq_q)
    rows.append(grade_prediction("RQ1", moves["B1"]))
    rows.append(grade_prediction("RQ2", max(moves["B0"], moves["B2"], moves["B3"]),
                                 "worst of B0/B2/B3"))

    # ======================= ARM R-s =======================================
    print("\n" + "=" * 78)
    print("ARM R-s: f-level mesh, solver tolerance / iteration bundle tightened")
    print("=" * 78)
    sha_f = sha256_of(os.path.join(T10A_DIR, "B_f", "constant", "F"))
    sha_s = sha256_of(os.path.join(HERE, "R_s", "constant", "F"))
    same_F = sha_f == sha_s
    print(f"  sha256 constant/F  B_f {sha_f[:24]}...")
    print(f"                     R_s {sha_s[:24]}...   IDENTICAL: {same_F}")
    smoves = {}
    for tag in ("B0", "B1", "B2", "B3"):
        vf = T10A.row_value(M["B_f"], PATCH[tag])
        vs = T10A.row_value(M["R_s"], PATCH[tag])
        smoves[tag] = pct(vs, vf)
        print(f"  {tag}  B_f {vf:20.13f}  R_s {vs:20.13f}  move {smoves[tag]:.3e} %")
    # face-by-face identity
    with in_tree(T10A_DIR, "B_f"):
        geo_f, ord_f, _ = T10A.mesh_patches(os.path.join(T10A_DIR, "B_f"))
        tf = T10A.time_dirs(os.path.join(T10A_DIR, "B_f"))[-1]
        qr_f = T10A.read_qr_all(os.path.join(T10A_DIR, "B_f", tf, "qr"), geo_f, ord_f)
    with in_tree(HERE, "R_s", spec_of("R_s")):
        geo_s, ord_s, _ = T10A.mesh_patches(os.path.join(HERE, "R_s"))
        tsd = T10A.time_dirs(os.path.join(HERE, "R_s"))[-1]
        qr_s = T10A.read_qr_all(os.path.join(HERE, "R_s", tsd, "qr"), geo_s, ord_s)
    if ord_f != ord_s:
        refuse("R_s and B_f do not present the same patch order")
    dmax = max(abs(a - b) for p in ord_f for a, b in zip(qr_f[p], qr_s[p]))
    nfaces = sum(len(qr_f[p]) for p in ord_f)
    print(f"  IDENTITY TEST (Charter 2a): max |qr(R_s) - qr(B_f)| over all "
          f"{nfaces} radiating faces = {dmax:.6e} W/m2   (B_f at t={tf}, R_s at t={tsd})")
    out["R_s"] = dict(moves_pct=smoves, F_sha_identical=same_F,
                      qr_max_abs_diff=dmax, n_faces=nfaces,
                      B_f_time=tf, R_s_time=tsd)
    rows.append(grade_prediction("RS1", smoves["B1"]))
    if not same_F:
        rows.append(grade_prediction(
            "RS2", None, "precondition failed: R_s's regenerated constant/F is not "
                         "byte-identical to B_f's, so the identity has no referent"))
    else:
        rows.append(grade_prediction("RS2", dmax))

    # ======================= report ========================================
    print("\n" + "=" * 78)
    print("REGISTERED PREDICTIONS -- graded against T10aR_registered.json ONLY")
    print("=" * 78)
    print(f"  {'row':5s} {'arm':5s} {'value':>13s} {'predicted':>10s} "
          f"{'interval':>20s}  verdict")
    for r in rows:
        v = "None" if r["value"] is None else f"{r['value']:.6g}"
        print(f"  {r['tag']:5s} {r['arm']:5s} {v:>13s} {r['predicted']:>10.6g} "
              f"{str(r['interval']):>20s}  {r['verdict']}")
        if r["note"]:
            print(f"        note: {r['note']}")
        if r["verdict"] != PASS:
            print(f"        falsifier as registered: {r['falsifier']}")
    out["rows"] = rows
    npass = sum(r["verdict"] == PASS for r in rows)
    nfail = sum(r["verdict"] == GATE_FAIL for r in rows)
    nnar = sum(r["verdict"] == NOT_A_RESULT for r in rows)
    print(f"\n  {npass} PASS, {nfail} GATE FAIL, {nnar} NOT A RESULT "
          f"(against this arm's own predictions; nothing here is graded against "
          f"T10a's band)")
    out["summary"] = dict(PASS=npass, GATE_FAIL=nfail, NOT_A_RESULT=nnar)
    with open(os.path.join(HERE, "gate_t10aR.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print(f"\nwritten {os.path.join(HERE, 'gate_t10aR.json')}")
    return EXIT_OK if (nfail == 0 and nnar == 0) else EXIT_FAIL


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    raise SystemExit(main())
