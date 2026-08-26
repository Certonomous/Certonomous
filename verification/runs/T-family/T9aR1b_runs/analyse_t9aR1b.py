#!/usr/bin/env python3
"""T9a-R1b -- the FROZEN one-row comparator.  T9a's wall levels with the
harmonic interface scheme; the graded row is R1 (interface-1 temperature),
exactly the row T9a GATE FAILed.

THE REFERENT is derived here from the series-resistance law (a three-layer
plane wall in steady conduction carries one flux: q = dT / SUM(L_i/k_i),
T_i1 = T_hot - q L_1/k_1) and CROSS-CHECKED against T9a's registered
348.781082 K to 1e-6 K.

THE GATE follows T9a's registered rule for the row (analyse_t9a.grade_triple,
T9a_PREREGISTRATION.md): the band is the triple's own GCI (Fs = 1.25,
r_eff from cell counts, dim 1), convergence-gated by rule 5 -- and T9a's own
handling of an EXACT triple (analyse_t9a.py:223, "a zero band grades only a
literally exact value") is made operational here as the ABSOLUTE FLOOR
|T_i1 - exact| <= 1e-6 K, registered because a piecewise-linear exact solution
lies in the null space of the harmonic scheme's truncation error, so the
triple is predicted EXACT at round-off (scratch: 3e-12 K).  No band is widened:
T9a's R1 band was 0.9 mK; this floor is 900x tighter.

ROACHE FLOORS ARE IMPORTED (MESH_STANDARD.md 10.5): STAGNANT_FLOOR, P_MIN, FS,
gci_unequal from scripts/roache_triple.py; this file defines none.

L-342: refuses only on PHYSICS-CRITICAL facts (DONE markers, fields, the
parent-derived geometry, the referent).  NO assert (L-332).  Exit 0 / 2.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
from roache_triple import STAGNANT_FLOOR, P_MIN, FS, PLANT, gci_unequal, refinement_ratio   # noqa: E402

LEVELS = ("c", "m", "f")
CASES = {lv: "W1b_%s" % lv for lv in LEVELS}
EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def load_registered(root=None):
    p = os.path.join(root or HERE, "T9aR1b_registered.json")
    if not os.path.isfile(p):
        refuse("no T9aR1b_registered.json")
    reg = json.load(open(p))
    fl = reg.get("roache_floors", {})
    if fl.get("STAGNANT_FLOOR") != STAGNANT_FLOOR or fl.get("P_MIN") != P_MIN:
        refuse("registered floors %r disagree with the imported STAGNANT_FLOOR=%r P_MIN=%r" % (fl, STAGNANT_FLOOR, P_MIN))
    return reg


def exact(wall):
    ks = [l["k"] for l in wall["layers"]]; Ls = [l["L"] for l in wall["layers"]]
    sumR = sum(L / k for L, k in zip(Ls, ks))
    q = (wall["T_hot"] - wall["T_cold"]) / sumR
    Ti1 = wall["T_hot"] - q * Ls[0] / ks[0]
    if abs(Ti1 - wall["T_i1_registered_T9a"]) > 1e-6:
        refuse("derived T_i1 %.9f disagrees with T9a's registered %.6f" % (Ti1, wall["T_i1_registered_T9a"]))
    if abs(q - wall["q_registered_T9a"]) > 1e-6:
        refuse("derived q %.9f disagrees with T9a's registered %.6f" % (q, wall["q_registered_T9a"]))
    return q, Ti1


def case_meta(root, case):
    p = os.path.join(root, case, "CASE.txt")
    if not os.path.isfile(p):
        refuse("no CASE.txt for %s" % case)
    return dict(re.findall(r"^([A-Za-z_0-9]+)=(.*)$", open(p).read(), re.M))


def latest_time(d):
    ts = [t for t in os.listdir(d) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0]
    return max(ts, key=float) if ts else None


def read_internal(path):
    """THE PRODUCTION READER (T and DT)."""
    if not os.path.isfile(path):
        return None
    m = re.search(r"internalField\s+nonuniform[^(]*\(\s*(.*?)\n\)", open(path).read(), re.S)
    return [float(v) for v in m.group(1).split()] if m else None


def centres(wall, cells):
    Cx, x0 = [], 0.0
    for l, n in zip(wall["layers"], cells):
        Cx += [x0 + (i + 0.5) * l["L"] / n for i in range(n)]
        x0 += l["L"]
    return Cx


def layer_of(wall, x):
    x0 = 0.0
    for i, l in enumerate(wall["layers"]):
        x0 += l["L"]
        if x < x0:
            return i
    return len(wall["layers"]) - 1


def measure(root, case, wall, cells):
    """T_i1 by the PARENT's reader form (analyse_t9a.measure_wall.iface_T):
    conductance-weighted mean of the two cells adjacent to the interface face.
    The DT field is checked cell by cell against the layer map (C_MAP)."""
    d = os.path.join(root, case)
    t = latest_time(d)
    if t is None:
        refuse("%s has no time directory beyond 0" % case)
    T = read_internal(os.path.join(d, t, "T"))
    DT = read_internal(os.path.join(d, t, "DT"))
    if T is None or DT is None:
        refuse("%s: T or DT unreadable at time %s" % (case, t))
    Cx = centres(wall, cells)
    if len(T) != len(Cx):
        refuse("%s: %d cells on disk, %d from the registered layer counts" % (case, len(T), len(Cx)))
    ks = [l["k"] for l in wall["layers"]]
    for i, x in enumerate(Cx):
        if abs(DT[i] - ks[layer_of(wall, x)]) > 1e-9 * ks[layer_of(wall, x)]:
            refuse("%s: cell %d at x=%.6g carries DT=%g, layer map says %g (C_MAP)" % (case, i, x, DT[i], ks[layer_of(wall, x)]))
    xi = wall["layers"][0]["L"]
    iL = max(i for i in range(len(Cx)) if Cx[i] < xi)
    iR = min(i for i in range(len(Cx)) if Cx[i] > xi)
    wL = ks[layer_of(wall, Cx[iL])] / (xi - Cx[iL]); wR = ks[layer_of(wall, Cx[iR])] / (Cx[iR] - xi)
    Ti1 = (wL * T[iL] + wR * T[iR]) / (wL + wR)
    q_hot = ks[0] * (wall["T_hot"] - T[0]) / Cx[0]
    return dict(time=t, n=len(T), T_i1=Ti1, q_hot=q_hot, iL=iL, iR=iR, T=T)


def converged(root, case, floor):
    """Gate (1): the last two written checkpoints agree in T to `floor` K (the
    parent's checkpoint form, L-140/L-141) and the log carries End."""
    d = os.path.join(root, case)
    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log) or not re.search(r"^End\s*$", open(log, errors="replace").read(), re.M):
        return False, None, "no End line"
    ts = sorted((t for t in os.listdir(d) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0), key=float)
    if len(ts) < 2:
        return False, None, "fewer than two written checkpoints"
    a = read_internal(os.path.join(d, ts[-2], "T")); b = read_internal(os.path.join(d, ts[-1], "T"))
    if a is None or b is None:
        return False, None, "checkpoint T unreadable"
    mv = max(abs(x - y) for x, y in zip(a, b))
    return (mv <= floor), mv, ("" if mv <= floor else "T moved %.3e K between the last two checkpoints > %.1e" % (mv, floor))


def planted_zero_control(root, case, wall, cells, idx):
    tmp = tempfile.mkdtemp(prefix="t9ar1b_pz_")
    try:
        dst = os.path.join(tmp, case)
        shutil.copytree(os.path.join(root, case), dst, symlinks=True)
        if os.path.realpath(dst).startswith(os.path.realpath(os.path.join(root, case))):
            refuse("planted-zero control: scratch copy resolved inside the case tree")
        base = measure(tmp, case, wall, cells)
        again = measure(tmp, case, wall, cells)
        if base["T_i1"] != again["T_i1"]:
            refuse("planted-zero control NEGATIVE ARM FAILED: reader is NOISY")
        p = os.path.join(dst, base["time"], "T")
        lines = open(p).read().splitlines(True)
        start = None
        for i, ln in enumerate(lines):
            if "internalField" in ln and "nonuniform" in ln:
                for j in range(i, min(i + 5, len(lines))):
                    if lines[j].strip() == "(":
                        start = j + 1; break
                break
        if start is None:
            refuse("planted-zero control: internalField not located structurally")
        before = float(lines[start + idx].strip())
        seen, floor = {}, None
        for mag in (1.0, 1e-1, 1e-2, PLANT, 1e-4, 1e-5, 1e-6, 1e-7):
            lines[start + idx] = "%.17g\n" % (before + mag)
            open(p, "w").write("".join(lines))
            d = abs(measure(tmp, case, wall, cells)["T_i1"] - base["T_i1"])
            seen[mag] = d
            if d > 0:
                floor = mag
        if floor is None:
            refuse("planted-zero control POSITIVE ARM FAILED: reader is BLIND")
        if seen[PLANT] < 0.1 * PLANT:
            refuse("planted-zero control: registered plant %.3g moved T_i1 by only %.3g (< 0.1 plant)" % (PLANT, seen[PLANT]))
        print("planted-zero control R1 PASS: plant %.6g K in cell %d (adjacent to interface 1), recovered %.6g K, floor %.1g"
              % (PLANT, idx, seen[PLANT], floor))
        return dict(status="PASS", plant=PLANT, cell=idx, recovered=seen[PLANT], demonstrated_detection_floor=floor,
                    ladder={"%g" % k: v for k, v in seen.items()})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def apply_gate(dev_K, tr, gate1_ok, gate1_why, floor_K):
    """The ONLY verdict-writing function.  Rule 5 order; T9a's row rule:
    CONVERGING -> band = its own GCI (absolute, K); EXACT -> the registered
    absolute floor (T9a's 'literally exact' made operational); any other
    state -> NOT A RESULT."""
    if not gate1_ok:
        return "NOT A RESULT", None, "gate (1): " + gate1_why
    st = tr["state"]
    if st == "CONVERGING":
        band = tr["GCI_abs"]
        return ("PASS" if dev_K <= band else "GATE FAIL"), band, "band = the triple's own GCI (T9a rule)"
    if st == "EXACT":
        return ("PASS" if dev_K <= floor_K else "GATE FAIL"), floor_K, "EXACT triple: T9a's zero band made operational as the registered floor %.1e K" % floor_K
    return "NOT A RESULT", None, "gate (2): triple is %s%s (STAGNANT_FLOOR=%g, P_MIN=%g)" % (
        st, (" (p = %.3e)" % tr["order"]) if tr.get("order") is not None else "", STAGNANT_FLOOR, P_MIN)


def triple_of(vals, ns, roundoff_K):
    """roache_triple.gci_unequal at the cell-count ratios; a triple whose level
    differences are ALL below the registered round-off floor (|e21|, |e32| <
    roundoff_K) is EXACT -- T9a's byte-identical EXACT made operational for a
    scheme that reproduces the exact solution to 1e-12 K rather than to the
    bit.  Both e's are carried in the record either way."""
    r21 = refinement_ratio(ns["m"], ns["f"], 1)
    r32 = refinement_ratio(ns["c"], ns["m"], 1)
    e21, e32 = vals["m"] - vals["f"], vals["c"] - vals["m"]
    if max(abs(e21), abs(e32)) < roundoff_K:
        return dict(state="EXACT", e21=e21, e32=e32, r21=r21, r32=r32, dim=1, roundoff_floor_K=roundoff_K)
    return gci_unequal(vals["c"], vals["m"], vals["f"], r21, r32, 1, fs=FS)


def grade(root, json_out, reg):
    wall = reg["wall"]
    for lv, case in CASES.items():
        if not os.path.isfile(os.path.join(root, "DONE.%s" % case)):
            refuse("no DONE.%s -- the whole rung is graded or none of it is" % case)
    q_ex, Ti1_ex = exact(wall)
    print("referent: q = %.6f W/m2, T_i1 = %.9f K (derived; cross-checked to T9a's registered values)" % (q_ex, Ti1_ex))
    metas = {lv: case_meta(root, CASES[lv]) for lv in LEVELS}
    cells = {lv: [int(x) for x in metas[lv]["cells_per_layer"].split(",")] for lv in LEVELS}
    for lv in LEVELS:
        if cells[lv] != reg["cases"][CASES[lv]]["cells_per_layer"]:
            refuse("%s cells_per_layer %r != registered %r" % (CASES[lv], cells[lv], reg["cases"][CASES[lv]]["cells_per_layer"]))
        if metas[lv].get("laplacianSchemes") != "Gauss harmonic corrected":
            refuse("%s CASE.txt does not record the harmonic scheme" % CASES[lv])
        sch = open(os.path.join(root, CASES[lv], "system", "fvSchemes")).read()
        if "Gauss harmonic corrected" not in sch:
            refuse("%s fvSchemes on disk is not the registered harmonic scheme" % CASES[lv])
    ok1, why = {}, []
    for lv in LEVELS:
        o, mv, w = converged(root, CASES[lv], reg["controls"]["C_CONV"]["floor"])
        ok1[lv] = dict(ok=o, checkpoint_move_K=mv, why=w)
        if not o:
            why.append("%s: %s" % (lv, w))
        print("  level %s: checkpoint-converged %s (move %s K)" % (lv, o, ("%.3e" % mv) if mv is not None else "n/a"))
    gate1_ok = all(v["ok"] for v in ok1.values())
    ms = {lv: measure(root, CASES[lv], wall, cells[lv]) for lv in LEVELS}
    pz = planted_zero_control(root, CASES["f"], wall, cells["f"], ms["f"]["iL"])
    ns = {lv: ms[lv]["n"] for lv in LEVELS}
    vals = {lv: ms[lv]["T_i1"] for lv in LEVELS}
    tr = triple_of(vals, ns, reg["graded_rows"]["R1"]["exact_roundoff_K"])
    dev = abs(vals["f"] - Ti1_ex)
    verdict, band, note = apply_gate(dev, tr, gate1_ok, "; ".join(why), reg["graded_rows"]["R1"]["exact_floor_K"])
    print("R1 T_i1: c=%.9f m=%.9f f=%.9f exact=%.9f dev=%.3e K triple=%s p=%s band=%s -> %s [%s]"
          % (vals["c"], vals["m"], vals["f"], Ti1_ex, dev, tr["state"],
             ("%.4f" % tr["order"]) if tr.get("order") is not None else "n/a",
             ("%.3e K" % band) if band is not None else "none", verdict, note))
    q_rows = {lv: dict(q_hot=ms[lv]["q_hot"], rel_dev=(ms[lv]["q_hot"] - q_ex) / q_ex) for lv in LEVELS}
    print("R0 (REPORTED, not graded): q_hot rel dev " + ", ".join("%s %+.3e" % (lv, q_rows[lv]["rel_dev"]) for lv in LEVELS))
    out = dict(rung="T9a-R1b", parent="T9a", row="R1", reference_T_i1=Ti1_ex, values=vals, cells=ns,
               triple=dict(state=tr["state"], order=tr.get("order"), e21=tr["e21"], e32=tr["e32"], GCI_abs=tr.get("GCI_abs")),
               deviation_K=dev, band_K=band, verdict=verdict, note=note, gate1=ok1,
               floors=dict(STAGNANT_FLOOR=STAGNANT_FLOOR, P_MIN=P_MIN, source="scripts/roache_triple.py (imported)"),
               planted_zero_control=pz, R0_reported=q_rows)
    json.dump(out, open(json_out, "w"), indent=2)
    print("wrote %s" % json_out)
    return EXIT_OK


def _forge(root, lv, cells, wall, dev_f=0.0, p=2.0, move=0.0, harmonic=True, offset=0.0):
    """Analytic piecewise-linear T at centres (+ a deviation scaled by level)."""
    case = CASES[lv]
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"), exist_ok=True); os.makedirs(os.path.join(d, "0"), exist_ok=True)
    open(os.path.join(d, "0", "T"), "w").write("x")
    open(os.path.join(d, "system", "fvSchemes"), "w").write("laplacianSchemes { default Gauss %s corrected; }\n" % ("harmonic" if harmonic else "linear"))
    open(os.path.join(d, "CASE.txt"), "w").write("case=%s\ncells_per_layer=%s\nlaplacianSchemes=Gauss %s corrected\n"
                                                 % (case, ",".join(map(str, cells)), "harmonic" if harmonic else "linear"))
    q, Ti1 = exact(wall)
    ks = [l["k"] for l in wall["layers"]]
    Cx = centres(wall, cells)
    scale = {"c": 4 ** p, "m": 2 ** p, "f": 1.0}[lv] * dev_f + offset
    T, DT = [], []
    for x in Cx:
        li = layer_of(wall, x); x0 = sum(l["L"] for l in wall["layers"][:li])
        Tface = wall["T_hot"] - q * sum(l["L"] / l["k"] for l in wall["layers"][:li])
        T.append(Tface - q * (x - x0) / ks[li] + scale); DT.append(ks[li])
    def fld(name, vals):
        return ("FoamFile{version 2.0; format ascii; class volScalarField; object %s;}\ndimensions [0 0 0 1 0 0 0];\n"
                "internalField   nonuniform List<scalar> \n%d\n(\n%s\n)\n;\nboundaryField{}\n" % (name, len(vals), "\n".join("%.17g" % v for v in vals)))
    for t, off in (("900", move), ("1000", 0.0)):
        os.makedirs(os.path.join(d, t), exist_ok=True)
        open(os.path.join(d, t, "T"), "w").write(fld("T", [v + off for v in T]))
        open(os.path.join(d, t, "DT"), "w").write(fld("DT", DT))
    open(os.path.join(d, "log.solve"), "w").write("ExecutionTime = 1 s\nEnd\n")
    open(os.path.join(root, "DONE.%s" % case), "w").write("done\n")


def selftest():
    import ast
    fails = []
    reg = load_registered()
    wall = reg["wall"]
    print("analyse_t9aR1b selftest:")
    fired = False
    tmpj = tempfile.mkdtemp(prefix="t9ar1b_reg_")
    try:
        bad = dict(reg); bad["roache_floors"] = dict(reg["roache_floors"], P_MIN=0.5)
        json.dump(bad, open(os.path.join(tmpj, "T9aR1b_registered.json"), "w"))
        try:
            load_registered(tmpj)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmpj, ignore_errors=True)
    print("  [%s] registered P_MIN mutated -> REFUSE (import is the one number)" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("floors")
    fired = False
    try:
        exact(dict(wall, T_i1_registered_T9a=wall["T_i1_registered_T9a"] + 1e-3))
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] referent cross-check: T9a value planted 1 mK wrong -> REFUSE" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("xcheck")
    cells = {lv: reg["cases"][CASES[lv]]["cells_per_layer"] for lv in LEVELS}
    def run_forged(**kw):
        tmp = tempfile.mkdtemp(prefix="t9ar1b_forge_")
        try:
            for lv in LEVELS:
                _forge(tmp, lv, cells[lv], wall, **kw)
            out = os.path.join(tmp, "gate.json"); code = None
            try:
                code = grade(tmp, out, reg)
            except SystemExit as e:
                code = e.code
            return code, (json.load(open(out)) if os.path.isfile(out) else None)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    for label, kw, want in (("exact field on all levels (EXACT triple) -> floor -> PASS", {}, "PASS"),
                            ("exact + 2e-6 K offset on all levels (EXACT, above floor) -> GATE FAIL", dict(dev_f=2e-6, p=0.0), "GATE FAIL"),
                            ("second-order deviation 1e-4 K at f, consistent ladder (CONVERGING) -> inside its own GCI -> PASS", dict(dev_f=1e-4, p=2.0), "PASS"),
                            ("CONVERGING ladder on top of a 1e-3 K constant error -> GCI band cannot cover it -> GATE FAIL", dict(dev_f=1e-4, p=2.0, offset=1e-3), "GATE FAIL"),
                            ("checkpoints move 1e-6 K -> gate (1) -> NOT A RESULT", dict(move=1e-6), "NOT A RESULT"),
                            ("oscillating deviation -> OSCILLATORY -> NOT A RESULT", dict(dev_f=1e-4, p=-1.0), None)):
        code, res = run_forged(**kw)
        v = res["verdict"] if res else None
        ok = (code == 0 and res is not None and (v == want if want else v == "NOT A RESULT"))
        print("  [%s] %-70s -> %s (%s)" % ("ok " if ok else "FAIL", label, v, res["triple"]["state"] if res else "?"))
        if not ok:
            fails.append(label)
    code, res = run_forged(harmonic=False)
    ok = (code == EXIT_REFUSE)
    print("  [%s] case built with the parent's linear scheme -> REFUSE (exit %s)" % ("ok " if ok else "FAIL", code))
    if not ok:
        fails.append("scheme")
    fired = False
    try:
        grade(HERE, os.path.join(tempfile.gettempdir(), "t9ar1b_never.json"), reg)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] live tree, no DONE markers -> REFUSE" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("live")
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (planted control: %d)" % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t9aR1b.json"))
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return grade(a.root, a.json, load_registered())


if __name__ == "__main__":
    sys.exit(main())
