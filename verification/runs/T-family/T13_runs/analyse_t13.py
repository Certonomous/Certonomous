#!/usr/bin/env python3
"""T13 -- the FROZEN comparator.  Natural convection in a vertical slot,
conduction regime (Batchelor 1954 parallel flow), Ra_L = 100, laminar,
buoyantBoussinesqSimpleFoam, 2-D, EXACT tier.

WHAT IS GRADED, AND HOW (T13_PREREGISTRATION.md sections 5-6):
  G1   v(xi*)/u_ref at mid-height, 4-point Lagrange at xi* = 1/2 - sqrt(3)/6,
       against 1/(72 sqrt 3): Roache triple, rule 5, band +-1.5e-3 relative.
  G1b  xi_max, the location of the maximum upflow from the cubic through the
       four cells around it, against xi*: Roache triple, band +-1.5e-4.
  G2   RMS over the mid-height row of (T - T_lin)/dT: ABSOLUTE FLOOR 1e-6.
  G3   Nu_L from the half-cell wall gradient, both walls: ABSOLUTE FLOOR 2e-4.
  G2 and G3 are EXACT-CLASS rows: the linear T lies in the null space of the
  scheme's truncation error, so their triples are EXACT / DEGENERATE by
  construction and rule 5 (2) would return NOT A RESULT for a row that cannot
  be wrong by discretisation.  Their triple states are PRINTED; their verdict
  is the floor, after gate (1).

GATE (1) -- every level must pass, else every row is NOT A RESULT:
  C_CONV  initial residuals of Uy, T, p_rgh <= 1e-6 at EVERY iteration of the
          final 10 percent.  Ux is a degenerate (~0) channel whose normalised
          residual is noise: REPORTED, never gated (L-338).
  C_PLAT  |G1(endTime) - G1(endTime - writeInterval)| / G1 <= 1e-7.
  W0      y-invariance mirror, rows just above / below mid-height, <= 1e-6.
  W1      END-EFFECT WITNESS, rows at H/2 +- L, 2L, 4L vs the graded row,
          <= 1e-6 in v (per u_ref phi_max) and T (per dT): exceeding it means
          the level is not in the parallel-flow regime the exact solution
          describes, and the rung says so instead of grading.
  C_RA    the constants are READ FROM THE CASE FILES and printed (L-331) and
          Ra_L recomputed from them must be 100.
  C_ORDER the graded row's T must fall from hot to cold with slope -dT/L: a
          transposed cell ordering shows a constant row and is REFUSED.

THE OBSERVED-ORDER FLOORS ARE THE SHARED NAMES (MESH_STANDARD.md section 10.5,
chief ruling 01967a7b): STAGNANT_FLOOR and P_MIN are IMPORTED from
scripts/roache_triple.py and this file defines neither; the triple arithmetic
is roache_triple.gci_equal itself.  The registered JSON carries the same two
numbers and this file REFUSES if import and registration disagree.

PLANTED-ZERO CONTROLS (rule 3), sized per reader (L-340): a point plant for
the point readers G1 / G1b / G3 / W1, an ALL-ROW plant for the RMS reader G2;
both arms; a measured detection ladder; refusal on a blind or noisy reader.

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2) and
fires identically under python3 -O.  The verdict is written by apply_gate()
and by nothing else.  Exit: 0 graded, 2 REFUSAL.
"""
import argparse
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import exact_t13 as EX                                              # noqa: E402
from roache_triple import STAGNANT_FLOOR, P_MIN, FS, gci_equal      # noqa: E402

LEVELS = ("c", "m", "f")
CASES = {lv: "T13_VS_%s" % lv for lv in LEVELS}
REFINEMENT = 2.0
DIM = 2
PLANT_REL = 1.234e-03          # the family's plant, as a fraction of the reader's scale
CONV_FLOOR = 1.0e-6
PLAT_FLOOR = 1.0e-7
WITNESS_FLOOR = 1.0e-6
RA_TOL = 1.0e-9
EXIT_OK, EXIT_REFUSE = 0, 2

ROOT = HERE                    # --root DIR for the selftest's forged tree


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def load_registered():
    p = os.path.join(HERE, "T13_registered.json")
    if not os.path.isfile(p):
        refuse("no T13_registered.json beside this comparator")
    reg = json.load(open(p))
    fl = reg.get("roache_floors", {})
    if fl.get("STAGNANT_FLOOR") != STAGNANT_FLOOR or fl.get("P_MIN") != P_MIN:
        refuse("registered floors %r disagree with the imported roache_triple "
               "STAGNANT_FLOOR=%r P_MIN=%r (MESH_STANDARD 10.5: one name, one number)"
               % (fl, STAGNANT_FLOOR, P_MIN))
    return reg


# ------------------------------------------------------------ case identity
def dict_value(path, key, vec=False):
    if not os.path.isfile(path):
        refuse("missing %s" % path)
    txt = open(path).read()
    if vec:
        m = re.search(r"^\s*%s\s+\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)\s*;" % key, txt, re.M)
        if not m:
            refuse("%s states no vector %s" % (path, key))
        return tuple(float(m.group(k)) for k in (1, 2, 3))
    m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % key, txt, re.M)
    if not m:
        refuse("%s states no %s" % (path, key))
    return float(m.group(1))


def patch_value(path, patch, key="value"):
    txt = open(path).read()
    m = re.search(r"^\s*%s\s*\{[^}]*?%s\s+uniform\s+([0-9.eE+-]+)\s*;" % (patch, key), txt, re.M | re.S)
    if not m:
        refuse("%s: no `%s uniform` for patch %s" % (path, key, patch))
    return float(m.group(1))


def case_identity(case_dir):
    """Every constant the grade depends on, READ FROM THE CASE'S OWN FILES and
    printed BEFORE any comparison (L-331: state the operands first)."""
    bmd = open(os.path.join(case_dir, "system", "blockMeshDict")).read()
    mv = re.search(r"vertices\s*\(\s*\(0 0 0\)\s*\(([0-9.eE+-]+) 0 0\)\s*\(([0-9.eE+-]+)\s+([0-9.eE+-]+) 0\)", bmd)
    mb = re.search(r"hex\s*\([^)]*\)\s*\(\s*(\d+)\s+(\d+)\s+1\s*\)", bmd)
    if not mv or not mb:
        refuse("%s: blockMeshDict does not carry the registered single-block form" % case_dir)
    L = float(mv.group(1))
    H = float(mv.group(3))
    N, Ny = int(mb.group(1)), int(mb.group(2))
    tp = os.path.join(case_dir, "constant", "transportProperties")
    ident = dict(case=os.path.basename(case_dir), L=L, H=H, N=N, Ny=Ny, dx=L / N, dy=H / Ny,
                 nu=dict_value(tp, "nu"), Pr=dict_value(tp, "Pr"), beta=dict_value(tp, "beta"),
                 TRef=dict_value(tp, "TRef"),
                 g=-dict_value(os.path.join(case_dir, "constant", "g"), "value", vec=True)[1])
    t0 = os.path.join(case_dir, "0.orig", "T")
    ident["T_hot"] = patch_value(t0, "hot")
    ident["T_cold"] = patch_value(t0, "cold")
    ident["dT"] = ident["T_hot"] - ident["T_cold"]
    ident["u_ref"] = ident["g"] * ident["beta"] * ident["dT"] * L * L / ident["nu"]
    ident["Ra"] = ident["g"] * ident["beta"] * ident["dT"] * L ** 3 * ident["Pr"] / ident["nu"] ** 2
    ident["endTime"] = dict_value(os.path.join(case_dir, "system", "controlDict"), "endTime")
    ident["writeInterval"] = dict_value(os.path.join(case_dir, "system", "controlDict"), "writeInterval")
    if abs(ident["Ra"] - 100.0) > RA_TOL:
        refuse("%s: Ra_L recomputed from the case files is %.12g, not the registered 100"
               % (ident["case"], ident["Ra"]))
    if abs(ident["TRef"] - 0.5 * (ident["T_hot"] + ident["T_cold"])) > 1e-9:
        refuse("%s: TRef %.17g is not the antisymmetry point (T_hot+T_cold)/2" % (ident["case"], ident["TRef"]))
    if Ny % 2 or Ny < 10 * N:
        refuse("%s: Ny=%d must be even and >= 10 N for the witness rows" % (ident["case"], Ny))
    return ident


def latest_times(case_dir, n=2):
    ts = [t for t in os.listdir(case_dir) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0]
    ts = sorted(ts, key=float)
    return ts[-n:] if len(ts) >= n else None


# ------------------------------------------------------------- THE READERS
def locate_internal(lines):
    """(first value line index, count) located STRUCTURALLY."""
    for i, ln in enumerate(lines):
        if "internalField" in ln and "nonuniform" in ln:
            for j in range(i, min(i + 5, len(lines))):
                if lines[j].strip() == "(":
                    cnt = None
                    for k in range(i, j + 1):
                        mc = re.search(r"\b(\d+)\s*$", lines[k].strip())
                        if mc:
                            cnt = int(mc.group(1))
                    return j + 1, cnt
            return None, None
    return None, None


def read_field(case_dir, time, name, vector=False):
    """THE PRODUCTION READER for scalar and vector internalFields.  Every
    graded number and every planted control goes through this function."""
    p = os.path.join(case_dir, str(time), name)
    if not os.path.isfile(p):
        refuse("no %s at time %s in %s -- a missing number is not a zero" % (name, time, case_dir))
    lines = open(p).read().splitlines()
    start, cnt = locate_internal(lines)
    if start is None:
        if re.search(r"internalField\s+uniform", "\n".join(lines[:40])):
            refuse("%s at time %s is UNIFORM -- the solver wrote no solution into it" % (name, time))
        refuse("could not locate the internalField of %s STRUCTURALLY" % p)
    if cnt is None:
        refuse("%s: no element count before the list" % p)
    vals = []
    for k in range(start, start + cnt):
        s = lines[k].strip()
        if vector:
            m = re.fullmatch(r"\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)", s)
            if not m:
                refuse("%s line %d is not a vector: %r" % (p, k + 1, s))
            vals.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
        else:
            vals.append(float(s))
    return vals


def row_of(vals, N, j):
    return vals[j * N:(j + 1) * N]


def xi_centres(N):
    return [(i + 0.5) / N for i in range(N)]


def readers(case_dir, time, ident):
    """All graded quantities and witnesses at one time, from disk."""
    N, Ny = ident["N"], ident["Ny"]
    j0 = Ny // 2
    U = read_field(case_dir, time, "U", vector=True)
    T = read_field(case_dir, time, "T")
    if len(U) != N * Ny or len(T) != N * Ny:
        refuse("%s at time %s: %d U / %d T cells, mesh has %d" % (ident["case"], time, len(U), len(T), N * Ny))
    xi = xi_centres(N)
    uref, dT, L = ident["u_ref"], ident["dT"], ident["L"]
    vrow = [u[1] / uref for u in row_of(U, N, j0)]
    trow = row_of(T, N, j0)
    out = dict(time=str(time), row_index=j0, row_y=(j0 + 0.5) * ident["dy"])
    out["G1"] = EX.lagrange4(xi, vrow, EX.XI_STAR)
    out["G1b"] = EX.cubic_max_location(xi, vrow)
    tlin = [ident["T_hot"] - dT * x for x in xi]
    out["G2"] = math.sqrt(sum(((t - tl) / dT) ** 2 for t, tl in zip(trow, tlin)) / N)
    half = 0.5 * ident["dx"]
    out["Nu_hot"] = (ident["T_hot"] - trow[0]) / half * L / dT
    out["Nu_cold"] = (trow[-1] - ident["T_cold"]) / half * L / dT
    out["G3"] = max(abs(out["Nu_hot"] - EX.NU_EXACT), abs(out["Nu_cold"] - EX.NU_EXACT))
    # C_ORDER: least-squares slope of T along the row must be -dT/L
    xm = sum(xi) / N
    tm = sum(trow) / N
    slope = sum((x - xm) * (t - tm) for x, t in zip(xi, trow)) / sum((x - xm) ** 2 for x in xi)
    out["T_slope_rel"] = (slope / (-dT)) - 1.0          # 0 when the slope is -dT per unit xi
    out["T_monotone"] = all(trow[i] > trow[i + 1] for i in range(N - 1))
    # W0 and W1: rows compared with the graded row, per the readers' scales
    def rowdiff(j):
        vr = [u[1] / uref for u in row_of(U, N, j)]
        tr = row_of(T, N, j)
        return (max(abs(a - b) for a, b in zip(vr, vrow)) / EX.PHI_MAX,
                max(abs(a - b) for a, b in zip(tr, trow)) / dT)
    out["W0"] = dict(zip(("v", "T"), rowdiff(j0 - 1)))
    w1 = {}
    for k in (-4, -2, -1, 1, 2, 4):
        j = j0 + k * N
        if 0 <= j < Ny:
            w1["%+dL" % k] = dict(zip(("v", "T"), rowdiff(j)))
    out["W1"] = w1
    out["W1_max"] = max(max(d["v"], d["T"]) for d in w1.values())
    return out


# ------------------------------------------------- iterative convergence
def residual_history(case_dir):
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        return None, "no log.solve"
    hist = []
    cur = None
    with open(log, errors="replace") as fh:
        for line in fh:
            mt = re.match(r"^Time = ([0-9.eE+-]+)\s*$", line)
            if mt:
                cur = dict(it=float(mt.group(1)))
                hist.append(cur)
                continue
            if cur is None:
                continue
            ms = re.search(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)", line)
            if ms and ms.group(1) not in cur:
                cur[ms.group(1)] = float(ms.group(2))
    if not hist:
        return None, "no `Time =` lines in log.solve"
    return hist, ""


def iterative_convergence(case_dir, end_time):
    hist, why = residual_history(case_dir)
    if hist is None:
        return dict(ok=False, why=why)
    n = len(hist)
    tail = [h for h in hist if h["it"] > 0.9 * end_time]
    if not tail:
        return dict(ok=False, why="no iterations in the final 10 percent of endTime")
    worst = {}
    for f in ("Ux", "Uy", "T", "p_rgh"):
        vals = [h[f] for h in tail if f in h]
        worst[f] = max(vals) if vals else None
    gated = ("Uy", "T", "p_rgh")
    missing = [f for f in gated if worst[f] is None]
    if missing:
        return dict(ok=False, why="no residual lines for %s in the final 10 percent" % ",".join(missing), worst=worst)
    bad = [f for f in gated if worst[f] > CONV_FLOOR]
    return dict(ok=not bad, worst=worst, n_iterations=n, window=len(tail),
                why=("initial residual of %s above %.0e in the final 10 percent" % (",".join(bad), CONV_FLOOR)) if bad else "",
                Ux_reported_not_gated=worst["Ux"])


# ------------------------------------------------- planted-zero controls
def plant(case_copy, time, name, indices, delta, vector_component=None):
    """Add `delta` to the listed cell indices IN PLACE, located STRUCTURALLY."""
    p = os.path.join(case_copy, str(time), name)
    lines = open(p).read().splitlines(True)
    start, cnt = locate_internal(lines)
    if start is None:
        refuse("plant: could not locate internalField of %s" % p)
    for idx in indices:
        ln = lines[start + idx]
        if vector_component is None:
            lines[start + idx] = "%.17g\n" % (float(ln.strip()) + delta)
        else:
            m = re.fullmatch(r"\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)", ln.strip())
            if not m:
                refuse("plant: line %d of %s is not a vector" % (start + idx + 1, p))
            v = [float(m.group(k)) for k in (1, 2, 3)]
            v[vector_component] += delta
            lines[start + idx] = "(%.17g %.17g %.17g)\n" % tuple(v)
    open(p, "w").write("".join(lines))
    return start + indices[0] + 1


def planted_zero_controls(case_dir, time, ident, read=readers):
    """Both arms for EVERY reader, each plant sized to ITS reader (L-340):
    G1 / G1b / G3 / W1 are point readers and get a point plant; G2 is an RMS
    over N cells and gets an ALL-ROW plant.  A descending ladder is driven
    through the same production reader and the smallest visible magnitude is
    recorded; the registered plant must sit ABOVE that floor."""
    N, Ny = ident["N"], ident["Ny"]
    j0 = Ny // 2
    xi = xi_centres(N)
    i_star = min(range(N), key=lambda i: abs(xi[i] - EX.XI_STAR))
    tmp = tempfile.mkdtemp(prefix="t13pz_")
    try:
        dst = os.path.join(tmp, os.path.basename(case_dir))
        os.makedirs(dst)
        for sub in ("system", "constant", "0.orig"):
            shutil.copytree(os.path.join(case_dir, sub), os.path.join(dst, sub), symlinks=True)
        shutil.copytree(os.path.join(case_dir, str(time)), os.path.join(dst, str(time)))
        if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
            refuse("planted-zero control: scratch copy resolved INSIDE the case tree")
        base = read(dst, time, ident)
        again = read(dst, time, ident)
        for key in ("G1", "G1b", "G2", "G3", "W1_max"):
            if again[key] != base[key]:
                refuse("planted-zero NEGATIVE ARM FAILED on %s: identical bytes read back "
                       "%.17g then %.17g. The reader is NOISY; every T13 number depending "
                       "on it is withdrawn, not re-graded." % (key, base[key], again[key]))
        specs = [  # (reader key, field, indices, component, scale)
            ("G1", "U", [i_star + N * j0], 1, ident["u_ref"]),
            ("G1b", "U", [i_star + N * j0], 1, ident["u_ref"]),
            ("G2", "T", [i + N * j0 for i in range(N)], None, ident["dT"]),   # ALL-ROW plant (L-340)
            ("G3", "T", [0 + N * j0], None, ident["dT"]),
            ("W1_max", "U", [i_star + N * (j0 + N)], 1, ident["u_ref"]),
        ]
        report = {}
        for key, field, idxs, comp, scale in specs:
            seen, floor = {}, None
            for mag in (1.0, 1e-1, 1e-2, PLANT_REL, 1e-4, 1e-5, 1e-6, 1e-7):
                shutil.copy2(os.path.join(case_dir, str(time), field), os.path.join(dst, str(time), field))
                line = plant(dst, time, field, idxs, mag * scale, comp)
                got = read(dst, time, ident)
                d = abs(got[key] - base[key])
                seen["%g" % mag] = d
                if d > 0.0:
                    floor = mag
            shutil.copy2(os.path.join(case_dir, str(time), field), os.path.join(dst, str(time), field))
            if floor is None:
                refuse("planted-zero POSITIVE ARM FAILED for reader %s: no plant magnitude was "
                       "visible (field %s, %d cell(s) from line %d). The reader is BLIND and "
                       "every zero it has produced is worthless." % (key, field, len(idxs), line))
            if seen["%g" % PLANT_REL] == 0.0:
                refuse("planted-zero POSITIVE ARM FAILED for reader %s at the REGISTERED plant "
                       "%.4g x scale: invisible while %.4g x scale WAS visible" % (key, PLANT_REL, floor))
            report[key] = dict(status="PASS", field=field, cells_planted=len(idxs), first_line=line,
                               plant=PLANT_REL * scale, recovered=seen["%g" % PLANT_REL],
                               demonstrated_detection_floor=floor, ladder=seen)
        return report
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------- rule 5: the gate
def triple_of(vals):
    """roache_triple.gci_equal on (c, m, f) at r = 2, dim = 2."""
    return gci_equal(vals["c"], vals["m"], vals["f"], REFINEMENT, DIM, fs=FS)


def band_verdict(value, lo, hi):
    return "PASS" if lo <= value <= hi else "GATE FAIL"


def apply_gate(value, lo, hi, tr, gate1_ok, gate1_why, exact_class=False):
    """The ONLY function that writes a verdict.  Rule 5's fixed order:
    (1) any level not converged / not plateaued / not in regime -> NOT A RESULT;
    (2) triple not CONVERGING -> NOT A RESULT (EXACT-class rows skip (2): their
        floor is the verdict and the triple state is printed beside it);
    (3) the band.  The band verdict is computed FIRST and the final verdict is
    either it or NOT A RESULT -- the gate is one-way."""
    bv = band_verdict(value, lo, hi)
    if not gate1_ok:
        return "NOT A RESULT", bv, "gate (1): " + gate1_why
    if not exact_class and tr["state"] != "CONVERGING":
        p = tr.get("order")
        return ("NOT A RESULT", bv,
                "gate (2): triple is %s%s -- rule 5 makes a triple that is not CONVERGING NOT A "
                "RESULT whatever its value says (STAGNANT_FLOOR=%g, P_MIN=%g)"
                % (tr["state"], (" (p = %.3e)" % p) if p is not None else "", STAGNANT_FLOOR, P_MIN))
    return bv, bv, ""


def fmt_tr(tr):
    p = tr.get("order")
    g = tr.get("GCI_pct")
    return "%s p=%s GCI=%s" % (tr["state"], ("%.4f" % p) if p is not None else "n/a",
                               ("%.4e%%" % g) if g is not None else "REFUSED")


# ---------------------------------------------------------------- the grade
def grade(root, json_out, reg):
    for lv, case in CASES.items():
        if not os.path.isfile(os.path.join(root, "DONE.%s" % case)):
            refuse("no DONE.%s -- the whole rung is graded or none of it is. Run "
                   "mark_done_t13.py; if it says NOT DONE, that is the answer and "
                   "this comparator does not overrule it." % case)
    print("verifying the analytic reference before any comparison:")
    EX.verify()
    EX.selfcheck_readers()
    print("operands (L-331), read from each case's own files:")
    idents, times, reads, prev, conv = {}, {}, {}, {}, {}
    gate1_ok, gate1_why = True, []
    for lv, case in CASES.items():
        d = os.path.join(root, case)
        ident = case_identity(d)
        ts = latest_times(d, 2)
        if ts is None:
            refuse("%s has fewer than two written times beyond 0" % case)
        if abs(float(ts[-1]) - ident["endTime"]) > 1e-9:
            refuse("%s: latest time %s is not endTime %g" % (case, ts[-1], ident["endTime"]))
        idents[lv], times[lv] = ident, ts
        print("  %s: N=%d Ny=%d dx=%.4e nu=%.4e Pr=%.4g beta=%.6e TRef=%.4f T_hot=%.10f T_cold=%.10f "
              "g=%.3f Ra_L=%.10f u_ref=%.8e times=%s"
              % (case, ident["N"], ident["Ny"], ident["dx"], ident["nu"], ident["Pr"], ident["beta"],
                 ident["TRef"], ident["T_hot"], ident["T_cold"], ident["g"], ident["Ra"], ident["u_ref"], ts))
        r = readers(d, ts[-1], ident)
        r0 = readers(d, ts[-2], ident)
        reads[lv], prev[lv] = r, r0
        if not r["T_monotone"] or abs(r["T_slope_rel"]) > 1e-6:
            refuse("%s: C_ORDER -- the graded row's T is not the hot-to-cold linear profile "
                   "(monotone %s, slope/(-dT) - 1 = %.3e); a transposed cell ordering or a "
                   "field that is not the solution" % (case, r["T_monotone"], r["T_slope_rel"]))
        c = iterative_convergence(d, ident["endTime"])
        conv[lv] = c
        plat = abs(r["G1"] - r0["G1"]) / abs(r["G1"]) if r["G1"] != 0.0 else float("inf")
        c["plateau_rel_change"] = plat
        c["plateau_ok"] = plat <= PLAT_FLOOR
        w0 = max(r["W0"].values())
        c["W0"], c["W0_ok"] = w0, w0 <= WITNESS_FLOOR
        c["W1"], c["W1_ok"] = r["W1_max"], r["W1_max"] <= WITNESS_FLOOR
        print("  %s gate (1): C_CONV %s (worst final-10%% initial residuals %s; Ux REPORTED %s) | "
              "C_PLAT %s (%.3e) | W0 %s (%.3e) | W1 %s (%.3e: %s)"
              % (case, "ok" if c["ok"] else "FAIL " + c["why"],
                 {k: ("%.2e" % v if v is not None else None) for k, v in c.get("worst", {}).items() if k != "Ux"},
                 ("%.2e" % c["Ux_reported_not_gated"]) if c.get("Ux_reported_not_gated") is not None else "n/a",
                 "ok" if c["plateau_ok"] else "FAIL", plat, "ok" if c["W0_ok"] else "FAIL", w0,
                 "ok" if c["W1_ok"] else "FAIL", r["W1_max"],
                 {k: "v %.1e T %.1e" % (v["v"], v["T"]) for k, v in r["W1"].items()}))
        for name, ok in (("C_CONV", c["ok"]), ("C_PLAT", c["plateau_ok"]), ("W0", c["W0_ok"]), ("W1", c["W1_ok"])):
            if not ok:
                gate1_ok = False
                gate1_why.append("%s fails %s" % (case, name))
    control = planted_zero_controls(os.path.join(root, CASES["f"]), times["f"][-1], idents["f"])
    for k, v in control.items():
        print("planted-zero control %s PASS: plant %.4g in %s (%d cell(s)), recovered %.4g, "
              "demonstrated detection floor %g x scale"
              % (k, v["plant"], v["field"], v["cells_planted"], v["recovered"], v["demonstrated_detection_floor"]))

    rows = []
    G = reg["graded_rows"]
    specs = [
        ("G1", G["G1"]["quantity"], "G1", EX.PHI_MAX, G["G1"]["band_rel"], "rel", False),
        ("G1b", G["G1b"]["quantity"], "G1b", EX.XI_STAR, G["G1b"]["band_abs"], "abs", False),
        ("G2", G["G2"]["quantity"], "G2", 0.0, G["G2"]["floor_abs"], "abs", True),
        ("G3", G["G3"]["quantity"], "G3", 0.0, G["G3"]["floor_abs"], "abs", True),
    ]
    for rid, label, key, ref, width, kind, exact_class in specs:
        vals = {lv: reads[lv][key] for lv in LEVELS}
        tr = triple_of(vals)
        if kind == "rel":
            lo, hi = ref * (1 - width), ref * (1 + width)
        else:
            lo, hi = ref - width, ref + width
        verdict, bv, note = apply_gate(vals["f"], lo, hi, tr, gate1_ok, "; ".join(gate1_why), exact_class)
        dev = vals["f"] - ref
        rows.append(dict(row=rid, quantity=label, reference=ref, band=[lo, hi],
                         exact_class=exact_class, value_fine=vals["f"], triple=vals,
                         triple_state=tr["state"], observed_order=tr.get("order"),
                         gci_pct=tr.get("GCI_pct"), richardson_REPORTED_ONLY=tr.get("richardson"),
                         deviation=dev, rel_deviation=(dev / ref) if ref else None,
                         band_verdict=bv, verdict=verdict, note=note,
                         extra=(dict(Nu_hot=reads["f"]["Nu_hot"], Nu_cold=reads["f"]["Nu_cold"]) if rid == "G3" else {})))
        print("%-3s fine=%.10e ref=%.10e dev=%+.3e%s band=[%.6e, %.6e] triple=(%.8e, %.8e, %.8e) %s -> %s%s"
              % (rid, vals["f"], ref, dev, (" (rel %+.3e)" % (dev / ref)) if ref else "", lo, hi,
                 vals["c"], vals["m"], vals["f"], fmt_tr(tr), verdict, ("  [" + note + "]") if note else ""))
    if not gate1_ok:
        print("gate (1) FAILED: " + "; ".join(gate1_why))
    out = dict(rung="T13", solver="buoyantBoussinesqSimpleFoam laminar", Ra_L=100.0, dim=DIM,
               refinement_ratio=REFINEMENT, factor_of_safety=FS,
               floors=dict(STAGNANT_FLOOR=STAGNANT_FLOOR, P_MIN=P_MIN, CONV_FLOOR=CONV_FLOOR,
                           PLAT_FLOOR=PLAT_FLOOR, WITNESS_FLOOR=WITNESS_FLOOR),
               identities={lv: idents[lv] for lv in LEVELS}, times=times,
               gate1=dict(ok=gate1_ok, why=gate1_why, per_level=conv),
               readers={lv: reads[lv] for lv in LEVELS}, planted_zero_controls=control, rows=rows)
    json.dump(out, open(json_out, "w"), indent=2, default=str)
    print("wrote %s" % json_out)
    return EXIT_OK


# ---------------------------------------------------------------- selftest
def _forge_case(root, lv, N, transpose=False, witness_bump=0.0, uniform_T=False,
                residual=1e-9, plateau_bump=0.0, ra_mutant=False):
    """A synthetic finished case shaped like a T13 run: U from the 1-D discrete
    expectation (so the forged ladder carries a REAL second-order error law),
    T linear, dummies for p_rgh/phi, a log with residual lines, STATUS, DONE."""
    import build_t13 as B
    case = os.path.join(root, CASES[lv])
    Ny = B.ASPECT * N
    os.makedirs(os.path.join(case, "system"))
    os.makedirs(os.path.join(case, "constant"))
    os.makedirs(os.path.join(case, "0.orig"))
    os.makedirs(os.path.join(case, "0"))
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(
        B.block_mesh_dict(lv) if N == B.LEVELS[lv] else B.block_mesh_dict(lv).replace(
            "(%d %d 1)" % (B.LEVELS[lv], B.ASPECT * B.LEVELS[lv]), "(%d %d 1)" % (N, Ny)))
    et = B.END_TIME[lv]
    open(os.path.join(case, "system", "controlDict"), "w").write(B.control_dict(lv))
    for k, v in B.constant_files().items():
        if ra_mutant and k == "transportProperties":
            v = v.replace("nu              %.17g" % B.NU, "nu              %.17g" % (B.NU * 1.01))
        open(os.path.join(case, "constant", k), "w").write(v)
    for k, v in B.fields(lv).items():
        open(os.path.join(case, "0.orig", k), "w").write(v)
        open(os.path.join(case, "0", k), "w").write(v)
    xi, ph = EX.discrete_profile(N)
    def write_time(t, bump):
        td = os.path.join(case, str(t))
        os.makedirs(td)
        Uv, Tv = [], []
        for j in range(Ny):
            for i in range(N):
                ii, jj = (j % N, i) if transpose else (i, j)   # transpose: y-fastest ordering
                v = B.U_REF * ph[ii] * (1.0 + bump)
                if witness_bump and jj == Ny // 2 + N:
                    v *= (1.0 + witness_bump)
                Uv.append("(0 %.17g 0)" % v)
                Tv.append("%.17g" % (B.T_HOT - B.DT * xi[ii]))
        hdr = lambda cls, obj: B.head(cls, obj, str(t))
        open(os.path.join(td, "U"), "w").write(hdr("volVectorField", "U") + "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> \n%d\n(\n%s\n)\n;\nboundaryField { }\n" % (N * Ny, "\n".join(Uv)))
        if uniform_T:
            open(os.path.join(td, "T"), "w").write(hdr("volScalarField", "T") + "dimensions [0 0 0 1 0 0 0];\ninternalField uniform 300;\nboundaryField { }\n")
        else:
            open(os.path.join(td, "T"), "w").write(hdr("volScalarField", "T") + "dimensions [0 0 0 1 0 0 0];\ninternalField nonuniform List<scalar> \n%d\n(\n%s\n)\n;\nboundaryField { }\n" % (N * Ny, "\n".join(Tv)))
        for f in ("p_rgh", "phi"):
            open(os.path.join(td, f), "w").write(hdr("volScalarField", f) + "internalField uniform 0;\n")
    write_time(et - et // 10, plateau_bump)
    write_time(et, 0.0)
    with open(os.path.join(case, "log.solve"), "w") as fh:
        for it in range(1, et + 1):
            r = residual if it > 0.9 * et else 1e-3
            fh.write("Time = %d\n" % it)
            for f in ("Ux", "Uy", "T", "p_rgh"):
                fh.write("solver:  Solving for %s, Initial residual = %.3e, Final residual = 1e-12, No Iterations 1\n"
                         % (f, 0.05 if f == "Ux" else r))
            fh.write("ExecutionTime = 1 s  ClockTime = 1 s\n\n")
        fh.write("End\n")
    open(os.path.join(root, "STATUS.%s" % CASES[lv]), "w").write("case=%s\nrc=0\ncapped=no\n" % CASES[lv])
    open(os.path.join(root, "DONE.%s" % CASES[lv]), "w").write("forged\n")


def selftest():
    import ast
    import build_t13 as B
    fails = []
    reg = load_registered()
    print("analyse_t13 selftest:")
    # (i) the analytic reference verifies and the readers are exact on it
    EX.verify()
    EX.selfcheck_readers()
    # (ii) the floors are the imports, and a mutant registration is refused
    fired = False
    try:
        bad = dict(reg)
        bad["roache_floors"] = dict(reg["roache_floors"], P_MIN=0.5)
        tmpj = tempfile.mkdtemp(prefix="t13reg_")
        json.dump(bad, open(os.path.join(tmpj, "T13_registered.json"), "w"))
        global HERE
        keep = HERE
        HERE = tmpj
        try:
            load_registered()
        finally:
            HERE = keep
            shutil.rmtree(tmpj, ignore_errors=True)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] registered P_MIN mutated to 0.5 -> REFUSE (import %g / %g is the one number)" % ("ok " if fired else "FAIL", STAGNANT_FLOOR, P_MIN))
    if not fired:
        fails.append("floors")
    # (iii) rule 5 through apply_gate on synthetic triples, driven at the floors
    ref = EX.PHI_MAX
    lo, hi = ref * (1 - 1.5e-3), ref * (1 + 1.5e-3)
    def ladder(p, e_f=5e-6):
        return dict(f=ref + e_f, m=ref + e_f * 2 ** p, c=ref + e_f * 4 ** p)
    for label, vals, want, want_gci in (
            ("healthy p=2.000", ladder(2.0), "PASS", True),
            ("p=0.51 (just above STAGNANT_FLOOR)", ladder(0.51), "PASS", True),
            ("p=0.49 (just below STAGNANT_FLOOR) -> STAGNANT", ladder(0.49), "NOT A RESULT", False),
            ("p=0.01 (below P_MIN) -> DEGENERATE", ladder(0.01), "NOT A RESULT", False),
            ("oscillatory", dict(c=ref + 1e-5, m=ref - 1e-5, f=ref + 5e-6), "NOT A RESULT", False),
            ("divergent", ladder(-1.0), "NOT A RESULT", False),
            ("healthy p=2 but fine OUTSIDE the band", ladder(2.0, e_f=2e-5), "GATE FAIL", True),
            ("gate (1) failed -> NOT A RESULT whatever the triple", ladder(2.0), "NOT A RESULT", True)):
        tr = triple_of(vals)
        g1ok = "gate (1)" not in label
        v, bv, note = apply_gate(vals["f"], lo, hi, tr, g1ok, "forced", False)
        has_gci = tr.get("GCI_pct") is not None
        ok = (v == want) and (has_gci == want_gci)
        print("  [%s] %-52s %s -> %s" % ("ok " if ok else "FAIL", label, fmt_tr(tr), v))
        if not ok:
            fails.append(label)
    # EXACT-class row: an EXACT triple is graded by its floor, not sent to NOT A RESULT
    tr = triple_of(dict(c=0.0, m=0.0, f=0.0))
    v, bv, note = apply_gate(0.0, -1e-6, 1e-6, tr, True, "", True)
    ok = (tr["state"] == "EXACT" and v == "PASS")
    print("  [%s] EXACT-class row with an EXACT triple -> floor verdict %s (state %s)" % ("ok " if ok else "FAIL", v, tr["state"]))
    if not ok:
        fails.append("exact-class")
    v, bv, note = apply_gate(3e-6, -1e-6, 1e-6, tr, True, "", True)
    ok = (v == "GATE FAIL")
    print("  [%s] EXACT-class row outside its floor -> %s" % ("ok " if ok else "FAIL", v))
    if not ok:
        fails.append("exact-class-fail")
    # (iv) THE VALUE CONTROL (N-T8): a forged ladder built from the 1-D discrete
    # expectation must grade PASS with p = 2 and the fine G1 equal to the model
    def run_forged(**kw):
        tmp = tempfile.mkdtemp(prefix="t13forge_")
        try:
            for lv in LEVELS:
                _forge_case(tmp, lv, B.LEVELS[lv], **kw)
            out = os.path.join(tmp, "gate.json")
            code = None
            try:
                code = grade(tmp, out, reg)
            except SystemExit as e:
                code = e.code
            res = json.load(open(out)) if os.path.isfile(out) else None
            return code, res
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    code, res = run_forged()
    exp = EX.discrete_expectation(B.LEVELS["f"])
    rows = {r["row"]: r for r in res["rows"]} if res else {}
    ok = (code == 0 and rows and rows["G1"]["verdict"] == "PASS"
          and abs(rows["G1"]["value_fine"] - exp["G1"]) < 1e-12
          and abs(rows["G1"]["observed_order"] - 2.0) < 1e-3
          and rows["G1b"]["verdict"] == "PASS" and rows["G2"]["verdict"] == "PASS" and rows["G3"]["verdict"] == "PASS"
          and abs(rows["G2"]["value_fine"]) < 1e-9 and abs(rows["G3"]["value_fine"]) < 1e-6
          and all(res["planted_zero_controls"][k]["status"] == "PASS" for k in ("G1", "G1b", "G2", "G3", "W1_max")))
    print("  [%s] VALUE CONTROL: forged ladder from the 1-D model grades G1 PASS p=%s fine=%s (model %.10e); G1b/G2/G3 PASS; G2 triple %s (EXACT-class: state PRINTED, verdict by floor; fine values at round-off); 5 planted controls PASS"
          % ("ok " if ok else "FAIL", ("%.4f" % rows["G1"]["observed_order"]) if rows else "?",
             ("%.10e" % rows["G1"]["value_fine"]) if rows else "?", exp["G1"], rows["G2"]["triple_state"] if rows else "?"))
    if not ok:
        fails.append("value-control")
    # (v) a witness violation on one level -> gate (1) -> NOT A RESULT on every row
    code, res = run_forged(witness_bump=1e-4)
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]) and not res["gate1"]["ok"])
    print("  [%s] end-effect witness W1 bumped 1e-4 on the +1L row -> gate (1) -> NOT A RESULT x4" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("witness")
    # (vi) not converged -> NOT A RESULT; not plateaued -> NOT A RESULT
    code, res = run_forged(residual=1e-5)
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]))
    print("  [%s] final-10%% residual 1e-5 > floor -> NOT A RESULT x4 (Ux at 5e-2 never gated)" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("conv")
    code, res = run_forged(plateau_bump=1e-5)
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]))
    print("  [%s] G1 moved 1e-5 between the last two writes -> NOT A RESULT x4" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("plateau")
    # (vii) refusals: transposed ordering, uniform T, Ra mutant, blind reader
    for label, kw in (("transposed (y-fastest) cell ordering -> C_ORDER REFUSE", dict(transpose=True)),
                      ("uniform T at endTime -> REFUSE", dict(uniform_T=True)),
                      ("nu mutated 1 percent in transportProperties -> C_RA REFUSE", dict(ra_mutant=True))):
        code, res = run_forged(**kw)
        ok = (code == EXIT_REFUSE)
        print("  [%s] %s (exit %s)" % ("ok " if ok else "FAIL", label, code))
        if not ok:
            fails.append(label)
    # blind reader: a mutant that ignores the field must make the planted control REFUSE
    tmp = tempfile.mkdtemp(prefix="t13blind_")
    try:
        _forge_case(tmp, "c", B.LEVELS["c"])
        d = os.path.join(tmp, CASES["c"])
        ident = case_identity(d)
        t = latest_times(d, 1)[-1]
        good = readers(d, t, ident)
        def blind(case_dir, time, ident):
            return dict(good)                       # returns the same numbers whatever is on disk
        fired = False
        try:
            planted_zero_controls(d, t, ident, read=blind)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        print("  [%s] BLIND reader mutant (ignores the plant) -> planted-zero control REFUSES" % ("ok " if fired else "FAIL"))
        if not fired:
            fails.append("blind")
        # the real reader on the same forge passes all five controls
        rep = planted_zero_controls(d, t, ident)
        ok = all(rep[k]["status"] == "PASS" for k in rep) and rep["G2"]["cells_planted"] == B.LEVELS["c"]
        print("  [%s] real reader: 5/5 planted controls PASS; G2's plant covers all %d row cells (L-340)" % ("ok " if ok else "FAIL", rep["G2"]["cells_planted"]))
        if not ok:
            fails.append("real-reader")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # (viii) the live tree today: DONE markers absent -> REFUSE (subprocess, both interpreters)
    import subprocess
    for flag in ((), ("-O",)):
        r = subprocess.run([sys.executable, *flag, os.path.abspath(__file__), "--json", os.devnull],
                           capture_output=True, text=True)
        ok = (r.returncode == EXIT_REFUSE and "no DONE." in r.stdout)
        print("  [%s] live tree, python3 %s: no DONE markers -> exit %d %s" % ("ok " if ok else "FAIL", " ".join(flag) or "", r.returncode, r.stdout.strip().splitlines()[0][:60] if r.stdout.strip() else ""))
        if not ok:
            fails.append("live-refuse")
    n_assert = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)" % ("ok " if ok else "FAIL", n_assert, planted))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=HERE, help="run tree (selftest use)")
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t13.json"))
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    reg = load_registered()
    return grade(os.path.abspath(a.root), a.json, reg)


if __name__ == "__main__":
    sys.exit(main())
