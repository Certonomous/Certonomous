#!/usr/bin/env python3
"""T10aR2 comparator: the 2LI ladder (H-3(a), second refinement arm on T10a's B1).

WHAT THIS FILE GRADES, AND WHAT IT DOES NOT.  It grades NOTHING against T10a's
band; T10a (GATE FAIL) and T10a-R (GATE FAIL, 5/4/0) are closed and unchanged.
Every verdict here is PASS or GATE FAIL against a prediction registered in
T10aR2_registered.json (rows RR1-RR7), written before any R2_* case iterated.
A row that is a function of the grid triple (RR2, RR5) is NOT A RESULT unless
the triple is CONVERGING (rule 5, D440); the single-level rows (RR3, RR4, RR6,
RR7) and the identity row RR1 carry the triple state printed beside them.

WHY A NEW READER.  The parent's frozen analyse_t10aR.py (git blob printed at
every run) hard-codes the case list ("B_m", "B_f", "R_x", "R_q", "R_s") and the
row table RX*/RQ*/RS* of T10aR_registered.json; it cannot take the R2_c/R2_m/R2_f
levels (the analyse_t3.py -> analyse_t3_rff.py situation, T3_R_FF AMENDMENT 1).
So this file IMPORTS the frozen analyse_t10aR (and through it the frozen
analyse_t10a, exact_t10a and analyse_t1c.gci) and reuses, by name:
    R.in_tree            the tree shim (frozen HERE / REG["cases"] redirected in
                         this process only, restored on exit -- proved below)
    R.richardson_corrected     NEW INSTRUMENT 1 of T10a-R, reported never graded
    R.read_F_dense_stream, R.radiosity_lean, R.reciprocity_max_defect_blocked,
    R.F_diagnostics_lean, R.validate_lean_against_frozen
                         NEW INSTRUMENT 2 of T10a-R with its REGISTERED refusal
                         (lean == frozen bit-identically where both fit)
    T10A.measure / row_value / mesh_patches / time_dirs / read_qr_all /
    sigma_used / iterative_convergence / planted_zero_control / gci
                         the frozen T10a readers; gci is analyse_t1c.gci
                         (Fs 1.25, nominal r 1.6), the parent's own instrument.
R.tree_of / R.spec_of / R.case_dir are redirected in-process by `r2_names`
(same shape as in_tree, restored on exit, proved in --selftest) so that the
frozen lean-F instruments read THIS tree for R2_*; no frozen file is written.

OBSERVED-ORDER FLOORS -- THE SHARED NAMES (MESH_STANDARD.md section 10.5,
chief ruling 01967a7b).  STAGNANT_FLOOR (0 < p < 0.5 -> STAGNANT) and P_MIN
(|p| < 0.05 -> DEGENERATE) are IMPORTED from scripts/roache_triple.py and
defined nowhere here.  The frozen analyse_t1c.gci the parent used already
carries the 0.5 floor as its own STAGNANT branch; this file DRIVES that branch
at p = 0.49 / 0.51 at every run and REFUSES if the frozen floor is not the
shared one, and it labels |p| < P_MIN as DEGENERATE beside it.  Verdicts are
equivalent to the parent's (its RX2 p = 0.685 was CONVERGING and stays so).

NO `assert` STATEMENT APPEARS IN THIS FILE (L-332).  Every refusal is
sys.exit(2).  --selftest drives the refusals under python3 AND python3 -O.

Exit codes: 0 graded, 1 selftest failed, 2 REFUSAL.
"""
import ast
import atexit
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T10A_DIR = os.path.join(os.path.dirname(HERE), "T10a_runs")
T10AR_DIR = os.path.join(os.path.dirname(HERE), "T10aR_runs")
SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE)))), "scripts")
if "T10A_SCRATCH" not in os.environ:          # the frozen planted control needs a scratch root
    _scr = tempfile.mkdtemp(prefix="t10aR2_scratch_")
    os.environ["T10A_SCRATCH"] = _scr
    atexit.register(shutil.rmtree, _scr, True)
sys.path.insert(0, T10AR_DIR)
sys.path.insert(0, T10A_DIR)
sys.path.insert(0, SCRIPTS)
import analyse_t10aR as R                                  # noqa: E402  FROZEN (T10a-R)
from roache_triple import STAGNANT_FLOOR, P_MIN            # noqa: E402  SHARED
T10A, EXACT = R.T10A, R.EXACT                              # FROZEN (T10a)

REG = json.load(open(os.path.join(HERE, "T10aR2_registered.json")))
ROWS = REG["rows"]
FS, R_REFINE = REG["grid"]["Fs"], REG["grid"]["r"]
PLANT = REG["planted_control_value"]
CASES = [k for k in REG["cases"] if k != "note"]
LEVEL = {"c": "R2_c", "m": "R2_m", "f": "R2_f"}
PARENT_2AI = {"c": "B_c", "m": "B_m", "f": "B_f"}
TWIN_2LI_F = "R_q"
PATCH = {"B0": "floor", "B1": "ceiling", "B2": ["x0", "x1"], "B3": ["y0", "y1"]}
PASS, GATE_FAIL, NOT_A_RESULT = "PASS", "GATE FAIL", "NOT A RESULT"
EXIT_OK, EXIT_SELFTEST_FAIL, EXIT_REFUSE = 0, 1, 2
TREE_OVERRIDE = {}          # selftest --smoke: case name -> tree root


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def git_blob(path):
    r = subprocess.run(["git", "hash-object", path], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "unavailable"


# ------------------------------------------------------------- the floors
_RF = REG["roache_floors"]
if (float(_RF["STAGNANT_FLOOR"]), float(_RF["P_MIN"])) != (STAGNANT_FLOOR, P_MIN):
    refuse("T10aR2_registered.json roache_floors %r disagree with scripts/roache_triple.py "
           "STAGNANT_FLOOR=%r P_MIN=%r" % (_RF, STAGNANT_FLOOR, P_MIN))
if (FS, R_REFINE) != (T10A.FS, T10A.R_REFINE):
    refuse("registered Fs/r %r/%r differ from the frozen module's %r/%r"
           % (FS, R_REFINE, T10A.FS, T10A.R_REFINE))


def frozen_floor_is_shared():
    """DRIVE the frozen analyse_t1c.gci at p = 0.49 and 0.51 (r = 1.6): its own
    STAGNANT branch must sit exactly where STAGNANT_FLOOR says."""
    lo = T10A.gci(1.0, 1.10, 1.10 + 0.10 / (R_REFINE ** (STAGNANT_FLOOR - 0.01)))["state"]
    hi = T10A.gci(1.0, 1.10, 1.10 + 0.10 / (R_REFINE ** (STAGNANT_FLOOR + 0.01)))["state"]
    return lo == "STAGNANT" and hi == "CONVERGING"


def state_of(g):
    """The frozen gci's state, with the shared DEGENERATE label applied beside it."""
    if "order" in g and abs(g["order"]) < P_MIN:
        return "DEGENERATE"
    return g["state"]


# ------------------------------------------------------------- tree routing
def tree_of(name):
    if name in TREE_OVERRIDE:
        return TREE_OVERRIDE[name]
    if name in CASES:
        return HERE
    if name == TWIN_2LI_F:
        return T10AR_DIR
    return T10A_DIR


def spec_of(name):
    if name in CASES:
        c = REG["cases"][name]
        return dict(kind="box", N=c["N"], faces=c["faces"], cells=c["cells"], role=c["role"],
                    T_uniform=None, GaussQuadTol=c["GaussQuadTol"], smoothing=c["smoothing"])
    if name == TWIN_2LI_F:
        return R.spec_of(name)
    return None


def case_dir(name):
    return os.path.join(tree_of(name), name)


class r2_names:
    """Redirect the frozen analyse_t10aR's routing helpers to THIS tree for the
    duration of one call; restored on exit (proved in --selftest)."""

    def __enter__(self):
        self.old = (R.tree_of, R.spec_of, R.case_dir)
        R.tree_of, R.spec_of, R.case_dir = tree_of, spec_of, case_dir
        return self

    def __exit__(self, *a):
        R.tree_of, R.spec_of, R.case_dir = self.old
        return False


def _shim_restores():
    o = (R.tree_of, R.spec_of, R.case_dir)
    with r2_names():
        inside = (R.tree_of is tree_of and R.case_dir("R2_c") == os.path.join(HERE, "R2_c"))
    return inside and (R.tree_of, R.spec_of, R.case_dir) == o


def measure(name, sigma):
    with R.in_tree(tree_of(name), name, spec_of(name)):
        return T10A.measure(name, sigma, want_F=False)


def qr_faces(name):
    d = case_dir(name)
    with R.in_tree(tree_of(name), name, spec_of(name)):
        geom, order, _ = T10A.mesh_patches(d)
        t = T10A.time_dirs(d)[-1]
        return T10A.read_qr_all(os.path.join(d, t, "qr"), geom, order), order, t


def f_diag(name, m, sigma):
    with r2_names():
        return R.F_diagnostics_lean(name, m, sigma)


def lean_validation(name, sigma):
    with r2_names():
        return R.validate_lean_against_frozen(name, sigma)


# ------------------------------------------------------------- grading
def grade_prediction(tag, value, note=""):
    r = ROWS[tag]
    lo, hi = r["predict_interval"]
    v = NOT_A_RESULT if value is None else (PASS if lo <= value <= hi else GATE_FAIL)
    return dict(tag=tag, quantity=r["quantity"], value=value, predicted=r["predict_point"],
                interval=[lo, hi], verdict=v, falsifier=r["falsifier"], note=note)


def pct(a, b):
    return 100.0 * abs(a - b) / abs(b)


def b1_rows(trip, exact, moves, identity_dmax, identity_note, rowsum_ratio, void):
    """The registered rows from the B1 2LI triple (c, m, f), the 2AI->2LI moves at
    c and m, the RR1 identity, and the F row-sum ratio.  Pure arithmetic: proved
    on the registered H1/H2 branches in --selftest."""
    g = T10A.gci(*trip)
    st = state_of(g)
    conv = (st == "CONVERGING")
    errs = [v - exact for v in trip]
    dev_f = pct(trip[2], exact)
    band = g.get("GCI_pct") if conv else None
    rows = []
    if void:
        for tag in ROWS:
            rows.append(grade_prediction(tag, None, "a level is VOID under the closure guard"))
        return rows, g, st, errs, dev_f, band
    rows.append(grade_prediction("RR1", identity_dmax, identity_note))
    rows.append(grade_prediction("RR2", g.get("order") if conv else None,
                                 "" if conv else "triple is %s" % st))
    rows.append(grade_prediction("RR3", dev_f, "triple %s" % st))
    rows.append(grade_prediction("RR4a", abs(errs[0]) / abs(errs[1]) if errs[1] else None, "triple %s" % st))
    rows.append(grade_prediction("RR4b", abs(errs[1]) / abs(errs[2]) if errs[2] else None, "triple %s" % st))
    rows.append(grade_prediction("RR5", (dev_f / band) if (conv and band) else None,
                                 "" if (conv and band) else "no band armed (triple %s)" % st))
    rows.append(grade_prediction("RR6a", moves["c"]))
    rows.append(grade_prediction("RR6b", moves["m"]))
    rows.append(grade_prediction("RR7", rowsum_ratio))
    return rows, g, st, errs, dev_f, band


# ------------------------------------------------------------- main
def grade(a):
    prov = {}
    for label, path in (("analyse_t10aR.py (frozen)", os.path.join(T10AR_DIR, "analyse_t10aR.py")),
                        ("analyse_t10a.py (frozen)", os.path.join(T10A_DIR, "analyse_t10a.py")),
                        ("exact_t10a.py (frozen)", os.path.join(T10A_DIR, "exact_t10a.py")),
                        ("analyse_t1c.py (frozen)", os.path.join(os.path.dirname(HERE), "T1_runs", "analyse_t1c.py")),
                        ("roache_triple.py (shared)", os.path.join(SCRIPTS, "roache_triple.py")),
                        ("analyse_t10aR2.py", os.path.abspath(__file__)),
                        ("T10aR2_registered.json", os.path.join(HERE, "T10aR2_registered.json"))):
        prov[label] = dict(sha256=sha256_of(path), git_blob=git_blob(path))
    print("T10aR2 comparator.  shared floors STAGNANT_FLOOR = %g, P_MIN = %g.  provenance:" % (STAGNANT_FLOOR, P_MIN))
    for k, v in prov.items():
        print("  %-32s sha256 %s  blob %s" % (k, v["sha256"], v["git_blob"]))
    if not frozen_floor_is_shared():
        refuse("the frozen analyse_t1c.gci floor is not STAGNANT_FLOOR = %g" % STAGNANT_FLOOR)
    for c in CASES:
        if not os.path.isfile(os.path.join(HERE, "DONE.%s" % c)):
            refuse("no completion marker DONE.%s (mark_done_t10aR2.py decides; this comparator does not overrule it)" % c)
    for c in ("B_c", "B_m", "B_f"):
        if not os.path.isfile(os.path.join(T10A_DIR, "DONE.%s" % c)):
            refuse("the frozen T10a level %s carries no DONE marker" % c)
    if not os.path.isfile(os.path.join(T10AR_DIR, "DONE.%s" % TWIN_2LI_F)):
        refuse("the frozen T10a-R twin %s carries no DONE marker" % TWIN_2LI_F)
    if EXACT.main() != 0:
        refuse("the exact-theory derivation does not agree with itself")

    sigma = T10A.sigma_used()
    EX = {"B0": T10A.REG["box"]["q_floor"], "B1": T10A.REG["box"]["q_ceiling"],
          "B2": T10A.REG["box"]["q_xwall"], "B3": T10A.REG["box"]["q_ywall"]}
    names = ["B_c", "B_m", "B_f", TWIN_2LI_F] + CASES
    M = {}
    for n in names:
        M[n] = measure(n, sigma)
        cv, pc = M[n]["convergence"], M[n]["planted_control"]
        print("[%s] time %s cells %d closure_raw %.3e  convergence %s (max change %s)  plant %s recovered %r"
              % (n, M[n]["time"], M[n]["n_cells"], M[n]["closure_raw"], cv["state"],
                 cv.get("max_change"), "OK" if pc["ok"] else "FAILED", pc.get("recovered")))
        if cv["state"] != "CONVERGED":
            refuse("%s is not iteratively CONVERGED; no triple is formed from an unconverged level (D440)" % n)
        if not pc["ok"]:
            refuse("the planted-zero control failed on %s: %s" % (n, pc.get("why")))
        for tag in PATCH:
            print("   %s %-14s q_leaving %.6f W/m2" % (tag, str(PATCH[tag]), T10A.row_value(M[n], PATCH[tag])))

    print("F-side: lean instrument validated against the frozen one (REGISTERED refusal), then used")
    val = [lean_validation(n, sigma) for n in CASES]
    for v in val:
        print("  %s n=%d bit-identical %s radiosity %.2e reciprocity %.2e"
              % (v["case"], v["n"], v["matrix_bit_identical"], v["radiosity_max_rel"], v["reciprocity_rel"]))
    FD = {n: f_diag(n, M[n], sigma) for n in CASES}
    rs = {}
    for n in CASES:
        rs[n] = max(FD[n]["rowsum"][p]["max_defect"] for p in FD[n]["rowsum"])
        print("  %s rowsum max defect %.6f closure_F %.3e excess %.2e reciprocity %.2e python-vs-solver %.2e %s"
              % (n, rs[n], FD[n]["closure_F"], FD[n]["closure_excess"], FD[n]["reciprocity_max_defect"],
                 FD[n]["python_vs_solver_max_rel"], "VOID" if FD[n]["void"] else "ok"))
    void = any(FD[n]["void"] for n in CASES)

    # RR1 identity: R2_f vs the frozen T10a-R R_q (same mesh, same distTol 80)
    sha_f = sha256_of(os.path.join(case_dir("R2_f"), "constant", "F"))
    sha_q = sha256_of(os.path.join(case_dir(TWIN_2LI_F), "constant", "F"))
    qr_f, ord_f, t_f = qr_faces("R2_f")
    qr_q, ord_q, t_q = qr_faces(TWIN_2LI_F)
    if ord_f != ord_q:
        refuse("R2_f and R_q do not present the same patch order")
    dmax = max(abs(x - y) for p in ord_f for x, y in zip(qr_f[p], qr_q[p]))
    nfaces = sum(len(qr_f[p]) for p in ord_f)
    same_F = (sha_f == sha_q)
    print("RR1 identity: sha256(F) R2_f %s... R_q %s... IDENTICAL %s; max |qr(R2_f) - qr(R_q)| over %d faces = %.6e W/m2 (t=%s / %s)"
          % (sha_f[:16], sha_q[:16], same_F, nfaces, dmax, t_f, t_q))
    identity = dmax if same_F else None
    identity_note = "" if same_F else "precondition failed: R2_f's constant/F is not byte-identical to R_q's; the identity has no referent"

    # the B1 2LI ladder and the registered rows
    trip = [T10A.row_value(M[LEVEL[l]], PATCH["B1"]) for l in ("c", "m", "f")]
    moves = {l: T10A.row_value(M[LEVEL[l]], PATCH["B1"]) - T10A.row_value(M[PARENT_2AI[l]], PATCH["B1"])
             for l in ("c", "m")}
    rows, g, st, errs, dev_f, band = b1_rows(trip, EX["B1"], moves, identity, identity_note,
                                             rs["R2_f"] / rs["R2_c"] if rs["R2_c"] else None, void)
    rc = R.richardson_corrected(*trip)
    print("B1 2LI triple c/m/f %.6f -> %.6f -> %.6f  exact %.6f  errors %+.4f / %+.4f / %+.4f  state %s%s"
          % (trip[0], trip[1], trip[2], EX["B1"], errs[0], errs[1], errs[2], st,
             ("  p = %.4f" % g["order"]) if "order" in g else ""))
    print("   dev_f %.5f %%  band %s %%  Richardson shared %s / corrected %s"
          % (dev_f, ("%.5f" % band) if band else "none", g.get("richardson"), rc))

    out = dict(rung="T10aR2", sigma=sigma, provenance=prov, STAGNANT_FLOOR=STAGNANT_FLOOR, P_MIN=P_MIN,
               floors_source="scripts/roache_triple.py (MESH_STANDARD.md section 10.5)",
               lean_validation=val, cases={n: {k: v for k, v in M[n].items() if k != "log"} for n in M},
               F={n: FD[n] for n in CASES},
               B1=dict(triple_2LI=trip, exact=EX["B1"], errors=errs, gci=g, state=st, dev_f_pct=dev_f,
                       band_pct=band, richardson_corrected=rc, moves_2AI_to_2LI=moves),
               identity=dict(F_sha_R2_f=sha_f, F_sha_R_q=sha_q, identical=same_F, qr_max_abs_diff=dmax,
                             n_faces=nfaces), reported={})
    # reported, never graded: B0/B2/B3 under the same ladder
    for tag in ("B0", "B2", "B3"):
        tr = [T10A.row_value(M[LEVEL[l]], PATCH[tag]) for l in ("c", "m", "f")]
        gg = T10A.gci(*tr)
        s2 = state_of(gg)
        d2 = pct(tr[2], EX[tag])
        out["reported"][tag] = dict(triple_2LI=tr, exact=EX[tag], state=s2, gci=gg, dev_f_pct=d2,
                                    dev_over_band=(d2 / gg["GCI_pct"]) if s2 == "CONVERGING" else None,
                                    richardson_corrected=R.richardson_corrected(*tr),
                                    moves_2AI_to_2LI={l: T10A.row_value(M[LEVEL[l]], PATCH[tag])
                                                      - T10A.row_value(M[PARENT_2AI[l]], PATCH[tag])
                                                      for l in ("c", "m", "f")})
        print("reported %s: 2LI triple %s state %s dev_f %.5f %% band %s" % (tag, ["%.4f" % v for v in tr], s2, d2, gg.get("GCI_pct")))

    print("REGISTERED PREDICTIONS -- graded against T10aR2_registered.json ONLY")
    for r in rows:
        v = "None" if r["value"] is None else "%.6g" % r["value"]
        print("  %-5s %13s  predicted %10.6g  %-20s  %s%s"
              % (r["tag"], v, r["predicted"], str(r["interval"]), r["verdict"],
                 ("  [" + r["note"] + "]") if r["note"] else ""))
        if r["verdict"] != PASS:
            print("        falsifier as registered: %s" % r["falsifier"])
    out["rows"] = rows
    out["summary"] = dict(PASS=sum(r["verdict"] == PASS for r in rows),
                          GATE_FAIL=sum(r["verdict"] == GATE_FAIL for r in rows),
                          NOT_A_RESULT=sum(r["verdict"] == NOT_A_RESULT for r in rows))
    print("  %(PASS)d PASS, %(GATE_FAIL)d GATE FAIL, %(NOT_A_RESULT)d NOT A RESULT (against this arm's own predictions)" % out["summary"])
    with open(a.json, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print("wrote %s" % a.json)
    return EXIT_OK


# ------------------------------------------------------------- selftest
def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def _h_branch(scale=None, shift=None):
    """The registered branches: H1 shifts every 2AI level by +1.504358 W/m2; H2
    scales every 2AI level error by 0.630."""
    pm = REG["parent_measured"]
    ex = pm["B1_exact_sigmaOF"]
    two_ai = pm["B1_2AI_c_m_f"]
    if shift is not None:
        return [v + shift for v in two_ai], ex, two_ai
    return [ex + scale * (v - ex) for v in two_ai], ex, two_ai


def selftest(a):
    ok_n = all_n = 0

    def chk(what, cond):
        nonlocal ok_n, all_n
        all_n += 1
        ok_n += bool(cond)
        print("  [%s] %s" % ("ok " if cond else "FAIL", what))

    me = os.path.abspath(__file__)
    chk("zero `assert` nodes in analyse_t10aR2.py (AST)", count_asserts(me) == 0)
    chk("the AST counter sees a planted assert", count_asserts.__globals__["ast"].parse("assert 1\n").body[0].__class__.__name__ == "Assert")
    chk("shared floors imported, not defined here: STAGNANT_FLOOR = 0.5, P_MIN = 0.05, and no local definition",
        (STAGNANT_FLOOR, P_MIN) == (0.5, 0.05) and not any(l.startswith(("P_MIN =", "STAGNANT_FLOOR =")) for l in open(me)))
    chk("the frozen analyse_t1c.gci floor DRIVEN at p = 0.49 -> STAGNANT and 0.51 -> CONVERGING (== STAGNANT_FLOOR)",
        frozen_floor_is_shared())
    dg = T10A.gci(1.0, 1.10, 1.10 + 0.10 / (R_REFINE ** 0.02))
    chk("|p| = 0.02 < P_MIN is labelled DEGENERATE beside the frozen state %r (both NOT A RESULT)" % dg["state"],
        state_of(dg) == "DEGENERATE")
    chk("the frozen module's Fs/r equal the registered 1.25/1.6", (FS, R_REFINE) == (1.25, 1.6) == (T10A.FS, T10A.R_REFINE))
    chk("r2_names restores the frozen analyse_t10aR routing helpers", _shim_restores())
    # the registered branches, as a VALUE control on the row arithmetic
    pm = REG["parent_measured"]
    ex = pm["B1_exact_sigmaOF"]
    h1, _, two_ai = _h_branch(shift=pm["Rq_move_from_Bf_W_m2"])
    mv = {"c": h1[0] - two_ai[0], "m": h1[1] - two_ai[1]}
    rows, g, st, errs, dev, band = b1_rows(h1, ex, mv, 0.0, "", 1.0, False)
    by = {r["tag"]: r for r in rows}
    chk("H1 (registered point): p = %.4f in [1.0, 2.0], band %.5f %%, dev/band %.3f, ratios %.3f / %.3f -> every row PASS"
        % (g["order"], band, dev / band, by["RR4a"]["value"], by["RR4b"]["value"]),
        all(r["verdict"] == PASS for r in rows) and abs(g["order"] - 1.4805) < 2e-3
        and abs(band - 0.07673) < 2e-4 and abs(dev / band - 1.024) < 5e-3)
    h2, _, _ = _h_branch(scale=0.630)
    mv2 = {"c": h2[0] - two_ai[0], "m": h2[1] - two_ai[1]}
    rows2, g2, st2, errs2, dev2, band2 = b1_rows(h2, ex, mv2, 0.0, "", 1.0, False)
    by2 = {r["tag"]: r for r in rows2}
    chk("H2 (the excluded branch): ratios %.3f / %.3f, dev/band %.2f, move_c %.2f -> RR4a, RR4b, RR5, RR6a GATE FAIL; RR2, RR3 PASS"
        % (by2["RR4a"]["value"], by2["RR4b"]["value"], by2["RR5"]["value"], by2["RR6a"]["value"]),
        all(by2[t]["verdict"] == GATE_FAIL for t in ("RR4a", "RR4b", "RR5", "RR6a"))
        and by2["RR2"]["verdict"] == PASS and by2["RR3"]["verdict"] == PASS)
    osc, _, _ = _h_branch(shift=0.0)
    osc = [osc[0], osc[2], osc[1]]
    rows3 = b1_rows(osc, ex, mv, 0.0, "", 1.0, False)[0]
    by3 = {r["tag"]: r for r in rows3}
    chk("an OSCILLATORY triple -> RR2 and RR5 NOT A RESULT, the single-level rows still graded",
        by3["RR2"]["verdict"] == NOT_A_RESULT and by3["RR5"]["verdict"] == NOT_A_RESULT and by3["RR3"]["verdict"] != NOT_A_RESULT)
    rows4 = b1_rows(h1, ex, mv, 0.0, "", 1.0, True)[0]
    chk("a VOID level (closure guard) withdraws every row -> NOT A RESULT x%d" % len(rows4),
        all(r["verdict"] == NOT_A_RESULT for r in rows4))
    chk("RR1 identity: exact 0 -> PASS; 1e-14 -> GATE FAIL; precondition failed (None) -> NOT A RESULT",
        grade_prediction("RR1", 0.0)["verdict"] == PASS and grade_prediction("RR1", 1e-14)["verdict"] == GATE_FAIL
        and grade_prediction("RR1", None)["verdict"] == NOT_A_RESULT)
    chk("RR5 at exactly 0.85 and 1.30 -> PASS (closed interval); 0.84 and 1.31 -> GATE FAIL",
        grade_prediction("RR5", 0.85)["verdict"] == PASS and grade_prediction("RR5", 1.30)["verdict"] == PASS
        and grade_prediction("RR5", 0.84)["verdict"] == GATE_FAIL and grade_prediction("RR5", 1.31)["verdict"] == GATE_FAIL)
    chk("richardson_corrected (frozen, reported only) on the H1 triple lands within 0.1 %% of exact (%.4f vs %.4f)"
        % (R.richardson_corrected(*h1), ex), pct(R.richardson_corrected(*h1), ex) < 0.1)
    if a.smoke:
        TREE_OVERRIDE["R2_c"] = a.smoke
        sigma = T10A.sigma_used()
        m = measure("R2_c", sigma)
        chk("SMOKE R2_c (2 iterations in scratch): iteratively %s (max change %s); planted %g W/m2 recovered %r"
            % (m["convergence"]["state"], m["convergence"].get("max_change"), PLANT, m["planted_control"].get("recovered")),
            m["convergence"]["state"] == "CONVERGED" and m["planted_control"]["ok"])
        v = lean_validation("R2_c", sigma)
        chk("SMOKE lean F reader == frozen reader on the 2LI F of R2_c (n=%d, bit-identical %s)" % (v["n"], v["matrix_bit_identical"]),
            v["matrix_bit_identical"])
        fd = f_diag("R2_c", m, sigma)
        rsm = max(fd["rowsum"][p]["max_defect"] for p in fd["rowsum"])
        chk("SMOKE 2LI F diagnostics on R2_c: rowsum max defect %.5f, python-vs-solver %.2e, closure excess %.2e (not VOID)"
            % (rsm, fd["python_vs_solver_max_rel"], fd["closure_excess"]), not fd["void"])
        TREE_OVERRIDE.pop("R2_c")
    for tag, extra in (("missing DONE", ["--drive-refusal", "missing-done"]),
                       ("floor mismatch", ["--drive-refusal", "floor-mismatch"]),
                       ("unconverged level", ["--drive-refusal", "unconverged"])):
        rcs = {}
        for name, argv in (("python3", [sys.executable, me]), ("python3 -O", [sys.executable, "-O", me])):
            p = subprocess.run(argv + extra + (["--smoke", a.smoke] if a.smoke else []), capture_output=True, text=True)
            rcs[name] = (p.returncode, "REFUSE" in p.stdout)
        chk("refusal '%s' FIRES (rc 2, REFUSE printed) under python3 AND python3 -O: %r" % (tag, rcs),
            all(v == (2, True) for v in rcs.values()))
    print("\nselftest %d/%d" % (ok_n, all_n))
    return EXIT_OK if ok_n == all_n else EXIT_SELFTEST_FAIL


def drive_refusal(which, a):
    """Sacrificial mutants that MUST refuse (used by --selftest under both interpreters)."""
    if which == "missing-done":
        d = tempfile.mkdtemp(prefix="t10aR2_nodone_")
        try:
            for c in CASES:
                if not os.path.isfile(os.path.join(d, "DONE.%s" % c)):
                    refuse("no completion marker DONE.%s" % c)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        return EXIT_OK
    if which == "floor-mismatch":
        T10A.gci = lambda *t: dict(state="CONVERGING", order=0.49)     # noqa: E731  a frozen floor that moved
        if not frozen_floor_is_shared():
            refuse("the frozen analyse_t1c.gci floor is not STAGNANT_FLOOR = %g" % STAGNANT_FLOOR)
        return EXIT_OK
    if which == "unconverged":
        cv = dict(state="NOT_CONVERGED", max_change=1.0)
        if a.smoke:
            TREE_OVERRIDE["R2_c"] = a.smoke
            T10A.iterative_convergence = lambda case, geom, order: dict(cv)     # noqa: E731  mutant
            cv = measure("R2_c", T10A.sigma_used())["convergence"]
        if cv["state"] != "CONVERGED":
            refuse("R2_c is not iteratively CONVERGED; no triple is formed from an unconverged level (D440)")
        return EXIT_OK
    refuse("unknown refusal drive %r" % which)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t10aR2.json"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--smoke", default=None, help="a scratch root holding a 2-checkpoint R2_c for the live reader controls")
    ap.add_argument("--drive-refusal", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.drive_refusal:
        return drive_refusal(a.drive_refusal, a)
    if a.selftest:
        return selftest(a)
    return grade(a)


if __name__ == "__main__":
    sys.exit(main())
