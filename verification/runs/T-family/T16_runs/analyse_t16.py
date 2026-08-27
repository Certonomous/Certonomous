#!/usr/bin/env python3
"""T16 -- the FROZEN comparator.  DEVELOPING laminar MIXED CONVECTION in a
vertical parallel-plate channel with asymmetric isothermal walls, G = Gr/Re = 48,
Re = 100, laminar, buoyantBoussinesqSimpleFoam, 2-D, EXACT tier.

THE REFERENT IS DERIVED, NOT TRANSCRIBED.  `exact_t16.py` derives the fully
developed profile from the Boussinesq equations and re-derives it by an
independent RK4 route that REFUSES if the two disagree.  No paper is used, none
is on disk, and no number in this rung comes from one, so standing rule 15 has
nothing to bite on -- there is no retrieved artifact to title-page verify.

WHAT IS GRADED, AND HOW (T16_PREREGISTRATION.md sections 5-6), all on the
registered STATION row:
  G1   v(Y = 0.25)/U0, 4-point Lagrange at cell centres, against U(0.25) = 1.5
       exactly: Roache triple, rule 5, band registered RELATIVE.
  G1b  Y_max, the location of the maximum upflow from the cubic through the four
       cells around it, against (36 - sqrt(336))/48: Roache triple, band ABSOLUTE.
  G3   tau_hot / tau_cold from the half-cell wall gradients of v, against
       (6 + G/12)/(6 - G/12) = 5 exactly: Roache triple, band RELATIVE.
  G2   RMS over the station row of (T - T_lin)/dT: ABSOLUTE FLOOR.
  G2 is the ONE EXACT-CLASS row: the linear temperature field is an exact
  solution of the continuous problem FOR ANY VELOCITY FIELD (it has no y
  dependence, so u.grad(T) vanishes, it is harmonic in x, and it satisfies both
  wall Dirichlet conditions and both zeroGradient ends), so it lies in the null
  space of the scheme's truncation error, its triple is EXACT / DEGENERATE by
  construction, and rule 5 (2) would return NOT A RESULT for a row that cannot
  be wrong by discretisation.  Its triple state is PRINTED; its verdict is the
  floor, after gate (1).  G1, G1b and G3 are NOT exact-class: each carries a
  real second-order error that `exact_t16.discrete_expectation` predicts, and
  each is graded by rule 5 in full.

GATE (1) -- every level must pass, else every row is NOT A RESULT:
  C_CONV  initial residuals of Uy, T, p_rgh <= 1e-6 at EVERY iteration of the
          final 10 percent -- the family's floor, unweakened.  Ux is a
          near-degenerate cross-channel component whose normalised residual is
          noise: REPORTED, never gated (L-338).  The floor is registered because
          it was MEASURED REACHABLE on the disclosed scratch probe of this exact
          case (section 8 of the pre-registration): p_rgh 5.3e-03 at 1 600
          iterations -> 2.0e-05 -> 6.4e-06 -> 2.7e-06 -> 1.1e-06 -> 4.7e-07 by
          3 400 of the registered 10 000 at N = 20.  Three EARLIER probes stalled
          near 1e-02, and the cause is registered here because it is a physics
          statement about the case and not a numerical accident: p_rgh in this
          solver is p - rhok (g.h), so at a fixed height it varies ACROSS the
          channel wherever T does, and pinning the outlet at `fixedValue uniform
          0` forces a 1.73e-01 m2/s2 variation to zero.  The registered outlet
          is `prghPressure`, which is the consistent statement, and the residual
          collapse above is what changed when it was used.
  C_PLAT  |G1(endTime) - G1(endTime - writeInterval)| / G1 <= 1e-7.
  W1      THE DEVELOPMENT WITNESS, in THREE norms because they answer different
          questions.  Rows at the station -8b, -4b, +4b, +8b must agree with the
          station row (a) in the WHOLE-ROW max-norm of v/U0, floor 2e-4, which is
          dominated by the wall-adjacent cell; (b) ON THE GRADED READER ITSELF --
          the 4-point Lagrange at Y = 0.25 that G1 is -- floor 2e-5, an order of
          magnitude tighter, because that is the number the verdict depends on
          (MEASURED on the disclosed probe at 2.9e-06 over the full 8b span); and
          (c) in T/dT, floor 1e-6, where the field is exact.  This witness,
          and NOT an assumed entrance-length correlation, is what entitles the
          rung to compare a solve against a FULLY DEVELOPED closed form.  A
          level that fails it is not in the regime the referent describes, and
          the rung says so instead of grading.
  C_MASS  the station row's mean of v must equal U0: the referent normalises on
          the MEAN velocity, so a row whose mean is not U0 is not the profile
          the closed form describes.
  C_G     the constants are READ FROM THE CASE FILES and printed (L-331) and
          G = Gr/Re recomputed from them must be the registered 48, strictly
          below the DERIVED reversal threshold 72.
  C_ORDER the station row's T must fall from hot to cold with slope -dT per unit
          Y: a transposed cell ordering shows a constant row and is REFUSED.
  C_REV   NO REVERSED CELL on the station row (registered prediction P3): v > 0
          in every cell of it.  A reversed cell at G = 48, two thirds of the
          derived threshold, falsifies either the derivation or the solve.

THE OBSERVED-ORDER FLOORS ARE THE SHARED NAMES (MESH_STANDARD.md section 10.5,
chief ruling 01967a7b): STAGNANT_FLOOR and P_MIN are IMPORTED from
scripts/roache_triple.py and this file defines neither; the triple arithmetic is
roache_triple.gci_equal itself.  The registered JSON carries the same two
numbers and this file REFUSES if import and registration disagree.

PLANTED-ZERO CONTROLS (rule 3), SIZED PER READER (L-340): a POINT plant for the
point readers G1 / G1b / G3 / W1, and an ALL-ROW ALTERNATING-SIGN plant for the
RMS reader G2.  The sign alternation is the L-340 point made sharper than T13
made it: a reader that RMSs about a fitted line is blind to a constant offset by
construction, so the plant is shaped to what the reader can see rather than to
what is convenient to write.  Both arms; a measured detection ladder; refusal on
a blind or a noisy reader.

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2) and
fires identically under python3 -O.  The verdict is written by apply_gate() and
by nothing else.  Exit: 0 graded, 2 REFUSAL.
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
import exact_t16 as EX                                              # noqa: E402
from roache_triple import STAGNANT_FLOOR, P_MIN, FS, gci_equal      # noqa: E402

LEVELS = ("c", "m", "f")
CASES = {lv: "T16_MC_%s" % lv for lv in LEVELS}
REFINEMENT = 2.0
DIM = 2
PLANT_REL = 1.234e-03          # the family's plant, as a fraction of the reader's scale
CONV_FLOOR = 1.0e-6            # the family's floor, registered; MEASURED reachable, see below
PLAT_FLOOR = 1.0e-7
W1_FLOOR_V = 2.0e-4            # development witness, WHOLE-ROW max-norm in v/U0
W1_FLOOR_G = 2.0e-5            # development witness, ON THE GRADED READER G1 itself
W1_FLOOR_T = 1.0e-6            # development witness, in T/dT
MASS_FLOOR = 1.0e-6
G_TOL = 1.0e-9
EXIT_OK, EXIT_REFUSE = 0, 2

ROOT = HERE                    # --root DIR for the selftest's forged tree


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def load_registered(here=None):
    p = os.path.join(here or HERE, "T16_registered.json")
    if not os.path.isfile(p):
        refuse("no T16_registered.json beside this comparator")
    reg = json.load(open(p))
    fl = reg.get("roache_floors", {})
    if fl.get("STAGNANT_FLOOR") != STAGNANT_FLOOR or fl.get("P_MIN") != P_MIN:
        refuse("registered floors %r disagree with the imported roache_triple "
               "STAGNANT_FLOOR=%r P_MIN=%r (MESH_STANDARD 10.5: one name, one number)"
               % (fl, STAGNANT_FLOOR, P_MIN))
    ph = reg.get("physics", {})
    if abs(ph.get("G_mix", -1) - EX.G_REG) > 0.0:
        refuse("registered G_mix %r is not the referent's G_REG %r" % (ph.get("G_mix"), EX.G_REG))
    if abs(ph.get("G_reversal", -1) - EX.G_REVERSAL) > 0.0:
        refuse("registered reversal threshold %r is not the referent's DERIVED %r"
               % (ph.get("G_reversal"), EX.G_REVERSAL))
    if reg.get("grid_triple_absent"):
        refuse("T16 registers a THREE-LEVEL family; a registration claiming no triple is "
               "not this rung's")
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


def patch_vector(path, patch, key="value"):
    txt = open(path).read()
    m = re.search(r"^\s*%s\s*\{[^}]*?%s\s+uniform\s+\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)\s*;"
                  % (patch, key), txt, re.M | re.S)
    if not m:
        refuse("%s: no `%s uniform (...)` for patch %s" % (path, key, patch))
    return tuple(float(m.group(k)) for k in (1, 2, 3))


def case_identity(case_dir, reg):
    """Every constant the grade depends on, READ FROM THE CASE'S OWN FILES and
    printed BEFORE any comparison (L-331: state the operands first)."""
    bmd = open(os.path.join(case_dir, "system", "blockMeshDict")).read()
    mv = re.search(r"vertices\s*\(\s*\(0 0 0\)\s*\(([0-9.eE+-]+) 0 0\)\s*\(([0-9.eE+-]+)\s+([0-9.eE+-]+) 0\)", bmd)
    mb = re.search(r"hex\s*\([^)]*\)\s*\(\s*(\d+)\s+(\d+)\s+1\s*\)", bmd)
    if not mv or not mb:
        refuse("%s: blockMeshDict does not carry the registered single-block form" % case_dir)
    b = float(mv.group(1))
    H = float(mv.group(3))
    N, Ny = int(mb.group(1)), int(mb.group(2))
    tp = os.path.join(case_dir, "constant", "transportProperties")
    ident = dict(case=os.path.basename(case_dir), b=b, H=H, N=N, Ny=Ny, dx=b / N, dy=H / Ny,
                 nu=dict_value(tp, "nu"), Pr=dict_value(tp, "Pr"), beta=dict_value(tp, "beta"),
                 TRef=dict_value(tp, "TRef"),
                 g=-dict_value(os.path.join(case_dir, "constant", "g"), "value", vec=True)[1])
    t0 = os.path.join(case_dir, "0.orig", "T")
    u0f = os.path.join(case_dir, "0.orig", "U")
    ident["T_hot"] = patch_value(t0, "hot")
    ident["T_cold"] = patch_value(t0, "cold")
    ident["dT"] = ident["T_hot"] - ident["T_cold"]
    ident["U0"] = patch_vector(u0f, "inlet")[1]
    ident["Re"] = ident["U0"] * b / ident["nu"]
    ident["G_mix"] = ident["g"] * ident["beta"] * ident["dT"] * b * b / (ident["nu"] * ident["U0"])
    ident["endTime"] = dict_value(os.path.join(case_dir, "system", "controlDict"), "endTime")
    ident["writeInterval"] = dict_value(os.path.join(case_dir, "system", "controlDict"), "writeInterval")
    ph = reg["physics"]
    if abs(ident["G_mix"] - ph["G_mix"]) > G_TOL:
        refuse("%s: G = Gr/Re recomputed from the case files is %.12g, not the registered %.12g"
               % (ident["case"], ident["G_mix"], ph["G_mix"]))
    if not ident["G_mix"] < EX.G_REVERSAL:
        refuse("%s: G = %.12g is at or past the DERIVED reversal threshold %g; this rung "
               "registered an unreversed profile" % (ident["case"], ident["G_mix"], EX.G_REVERSAL))
    if abs(ident["Re"] - ph["Re"]) > 1e-9:
        refuse("%s: Re recomputed from the case files is %.12g, not the registered %.12g"
               % (ident["case"], ident["Re"], ph["Re"]))
    if abs(ident["TRef"] - ident["T_cold"]) > 1e-9:
        refuse("%s: TRef %.17g is not the COLD wall temperature %.17g -- the referent's theta is "
               "(T - T_c)/dT and the Boussinesq reference must be the same datum"
               % (ident["case"], ident["TRef"], ident["T_cold"]))
    if Ny != ph["aspect"] * N:
        refuse("%s: Ny=%d is not aspect(%d) x N(%d); the cells are registered SQUARE"
               % (ident["case"], Ny, ph["aspect"], N))
    ident["j_station"] = int(ph["station_gaps"]) * N
    ident["witness_rows"] = [(k, ident["j_station"] + k * N) for k in ph["witness_gaps"]]
    for k, j in ident["witness_rows"]:
        if not 0 <= j < Ny:
            refuse("%s: witness row %+d b maps to index %d, outside the mesh" % (ident["case"], k, j))
    if not 0 <= ident["j_station"] < Ny:
        refuse("%s: station row index %d is outside the mesh" % (ident["case"], ident["j_station"]))
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
    """THE PRODUCTION READER for scalar and vector internalFields.  Every graded
    number and every planted control goes through this function."""
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


def y_centres(N):
    return [(i + 0.5) / N for i in range(N)]


def readers(case_dir, time, ident):
    """All graded quantities and witnesses at one time, from disk."""
    N, Ny, j0 = ident["N"], ident["Ny"], ident["j_station"]
    U = read_field(case_dir, time, "U", vector=True)
    T = read_field(case_dir, time, "T")
    if len(U) != N * Ny or len(T) != N * Ny:
        refuse("%s at time %s: %d U / %d T cells, mesh has %d"
               % (ident["case"], time, len(U), len(T), N * Ny))
    Y = y_centres(N)
    U0, dT = ident["U0"], ident["dT"]
    vrow = [u[1] / U0 for u in row_of(U, N, j0)]
    trow = row_of(T, N, j0)
    out = dict(time=str(time), row_index=j0, row_y_over_b=(j0 + 0.5) / N)
    out["G1"] = EX.lagrange4(Y, vrow, EX.Y_STAR)
    out["G1b"] = EX.cubic_max_location(Y, vrow)
    # G3: the half-cell wall distance is the same at both walls and v vanishes on
    # both, so the ratio of the half-cell gradients IS the ratio of the first
    # cell values.  The half-cell distance is written out anyway so the reader is
    # readable as a gradient ratio and not as an accident of cancellation.
    half = 0.5 * ident["dx"]
    out["tau_hot"] = (vrow[0] - 0.0) / half
    out["tau_cold"] = (vrow[-1] - 0.0) / half
    out["G3"] = out["tau_hot"] / out["tau_cold"] if out["tau_cold"] != 0.0 else float("inf")
    tlin = [ident["T_hot"] - dT * y for y in Y]
    out["G2"] = math.sqrt(sum(((t - tl) / dT) ** 2 for t, tl in zip(trow, tlin)) / N)
    # C_MASS: the referent normalises on the MEAN, and the cells are uniform
    out["mass_mean"] = sum(vrow) / N
    out["mass_dev"] = abs(out["mass_mean"] - 1.0)
    # C_REV (prediction P3): no reversed cell on the station row
    out["v_min"] = min(vrow)
    out["reversed_cells"] = sum(1 for v in vrow if v <= 0.0)
    # C_ORDER: least-squares slope of T along the row must be -dT per unit Y
    ym = sum(Y) / N
    tm = sum(trow) / N
    slope = sum((y - ym) * (t - tm) for y, t in zip(Y, trow)) / sum((y - ym) ** 2 for y in Y)
    out["T_slope_rel"] = (slope / (-dT)) - 1.0
    out["T_monotone"] = all(trow[i] > trow[i + 1] for i in range(N - 1))

    def rowdiff(j):
        vr = [u[1] / U0 for u in row_of(U, N, j)]
        tr = row_of(T, N, j)
        # THREE numbers per witness row, because they answer different questions:
        # `v` is the WHOLE-ROW max-norm, which is dominated by the wall-adjacent
        # cell and is the loosest; `g` is the same comparison made ON THE GRADED
        # READER ITSELF (the 4-point Lagrange at Y = 0.25), which is what the
        # verdict actually depends on and is therefore gated an order of
        # magnitude tighter; `T` is exact and must be at round-off.
        vr = [u[1] / U0 for u in row_of(U, N, j)]
        return (max(abs(a - b) for a, b in zip(vr, vrow)),
                abs(EX.lagrange4(Y, vr, EX.Y_STAR) - out["G1"]) / abs(out["G1"]),
                max(abs(a - b) for a, b in zip(tr, trow)) / dT)

    w1 = {}
    for k, j in ident["witness_rows"]:
        w1["%+db" % k] = dict(zip(("v", "g", "T"), rowdiff(j)))
    out["W1"] = w1
    out["W1_v_max"] = max(d["v"] for d in w1.values())
    out["W1_g_max"] = max(d["g"] for d in w1.values())
    out["W1_T_max"] = max(d["T"] for d in w1.values())
    out["W1_max"] = max(out["W1_v_max"], out["W1_g_max"], out["W1_T_max"])
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
        return dict(ok=False, why="no residual lines for %s in the final 10 percent" % ",".join(missing),
                    worst=worst)
    bad = [f for f in gated if worst[f] > CONV_FLOOR]
    return dict(ok=not bad, worst=worst, n_iterations=n, window=len(tail),
                why=("initial residual of %s above %.0e in the final 10 percent"
                     % (",".join(bad), CONV_FLOOR)) if bad else "",
                Ux_reported_not_gated=worst["Ux"])


# ------------------------------------------------- planted-zero controls
def plant(case_copy, time, name, indices, deltas, vector_component=None):
    """Add deltas[k] to indices[k] IN PLACE, located STRUCTURALLY.  `deltas` is a
    list the same length as `indices`, so a plant can ALTERNATE IN SIGN -- the
    shape an RMS reader can see whatever it measures about (L-340)."""
    p = os.path.join(case_copy, str(time), name)
    lines = open(p).read().splitlines(True)
    start, cnt = locate_internal(lines)
    if start is None:
        refuse("plant: could not locate internalField of %s" % p)
    for idx, delta in zip(indices, deltas):
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
    """Both arms for EVERY reader, each plant sized AND SHAPED to ITS reader
    (rule 3, L-340).  G1 / G1b / G3 / W1 are point readers and get a point plant.
    G2 is an RMS over the whole row and gets an ALL-ROW ALTERNATING-SIGN plant: a
    constant offset is what an RMS-about-a-fit reader is blind to by
    construction, so the plant is shaped to the reader rather than to
    convenience.  A descending ladder is driven through the same production
    reader and the smallest visible magnitude is recorded; the registered plant
    must sit ABOVE that measured floor."""
    N, j0 = ident["N"], ident["j_station"]
    Y = y_centres(N)
    i_star = min(range(N), key=lambda i: abs(Y[i] - EX.Y_STAR))
    i_peak = min(range(N), key=lambda i: abs(Y[i] - EX.Y_MAX))
    j_wit = ident["witness_rows"][0][1]
    tmp = tempfile.mkdtemp(prefix="t16pz_")
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
                       "%.17g then %.17g. The reader is NOISY; every T16 number depending on "
                       "it is withdrawn, not re-graded." % (key, base[key], again[key]))
        row = [i + N * j0 for i in range(N)]
        alt = [1.0 if i % 2 == 0 else -1.0 for i in range(N)]
        specs = [  # (reader key, field, indices, signs, component, scale)
            ("G1", "U", [i_star + N * j0], [1.0], 1, ident["U0"]),
            ("G1b", "U", [i_peak + N * j0], [1.0], 1, ident["U0"]),
            ("G2", "T", row, alt, None, ident["dT"]),        # ALL-ROW ALTERNATING (L-340)
            ("G3", "U", [0 + N * j0], [1.0], 1, ident["U0"]),
            ("W1_max", "U", [i_star + N * j_wit], [1.0], 1, ident["U0"]),
        ]
        report = {}
        for key, field, idxs, signs, comp, scale in specs:
            seen, floor = {}, None
            for mag in (1.0, 1e-1, 1e-2, PLANT_REL, 1e-4, 1e-5, 1e-6, 1e-7):
                shutil.copy2(os.path.join(case_dir, str(time), field),
                             os.path.join(dst, str(time), field))
                line = plant(dst, time, field, idxs, [s * mag * scale for s in signs], comp)
                got = read(dst, time, ident)
                d = abs(got[key] - base[key])
                seen["%g" % mag] = d
                if d > 0.0:
                    floor = mag
            shutil.copy2(os.path.join(case_dir, str(time), field),
                         os.path.join(dst, str(time), field))
            if floor is None:
                refuse("planted-zero POSITIVE ARM FAILED for reader %s: no plant magnitude was "
                       "visible (field %s, %d cell(s) from line %d). The reader is BLIND and every "
                       "zero it has produced is worthless." % (key, field, len(idxs), line))
            if seen["%g" % PLANT_REL] == 0.0:
                refuse("planted-zero POSITIVE ARM FAILED for reader %s at the REGISTERED plant "
                       "%.4g x scale: invisible while %.4g x scale WAS visible"
                       % (key, PLANT_REL, floor))
            report[key] = dict(status="PASS", field=field, cells_planted=len(idxs), first_line=line,
                               shape=("ALL-ROW ALTERNATING SIGN" if len(idxs) > 1 else "POINT"),
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
    (1) any level not converged / not plateaued / not developed / not carrying
        the registered mean -> NOT A RESULT;
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
            refuse("no DONE.%s -- the whole rung is graded or none of it is. Run mark_done_t16.py; "
                   "if it says NOT DONE, that is the answer and this comparator does not overrule "
                   "it." % case)
    print("verifying the DERIVED analytic reference before any comparison:")
    r, f = EX.verify()
    if f:
        refuse("the referent's Route B does not verify: %s" % "; ".join(f))
    EX.selfcheck_readers()
    print("operands (L-331), read from each case's own files:")
    idents, times, reads, prev, conv = {}, {}, {}, {}, {}
    gate1_ok, gate1_why = True, []
    for lv in LEVELS:
        case = CASES[lv]
        d = os.path.join(root, case)
        ident = case_identity(d, reg)
        ts = latest_times(d, 2)
        if ts is None:
            refuse("%s has fewer than two written times beyond 0" % case)
        if abs(float(ts[-1]) - ident["endTime"]) > 1e-9:
            refuse("%s: latest time %s is not endTime %g" % (case, ts[-1], ident["endTime"]))
        idents[lv], times[lv] = ident, ts
        print("  %s: N=%d Ny=%d dx=%.4e nu=%.4e Pr=%.4g beta=%.6e TRef=%.4f T_hot=%.10f "
              "T_cold=%.10f g=%.3f U0=%.10f Re=%.8f G=Gr/Re=%.10f (reversal %g, margin %.4f) "
              "station row %d at y/b=%.3f times=%s"
              % (case, ident["N"], ident["Ny"], ident["dx"], ident["nu"], ident["Pr"], ident["beta"],
                 ident["TRef"], ident["T_hot"], ident["T_cold"], ident["g"], ident["U0"],
                 ident["Re"], ident["G_mix"], EX.G_REVERSAL, EX.G_REVERSAL / ident["G_mix"],
                 ident["j_station"], (ident["j_station"] + 0.5) / ident["N"], ts))
        r = readers(d, ts[-1], ident)
        r0 = readers(d, ts[-2], ident)
        reads[lv], prev[lv] = r, r0
        if not r["T_monotone"] or abs(r["T_slope_rel"]) > 1e-6:
            refuse("%s: C_ORDER -- the station row's T is not the hot-to-cold linear profile "
                   "(monotone %s, slope/(-dT) - 1 = %.3e); a transposed cell ordering or a field "
                   "that is not the solution" % (case, r["T_monotone"], r["T_slope_rel"]))
        c = iterative_convergence(d, ident["endTime"])
        conv[lv] = c
        plat = abs(r["G1"] - r0["G1"]) / abs(r["G1"]) if r["G1"] != 0.0 else float("inf")
        c["plateau_rel_change"] = plat
        c["plateau_ok"] = plat <= PLAT_FLOOR
        c["W1_v"], c["W1_g"], c["W1_T"] = r["W1_v_max"], r["W1_g_max"], r["W1_T_max"]
        c["W1_ok"] = (r["W1_v_max"] <= W1_FLOOR_V and r["W1_g_max"] <= W1_FLOOR_G
                      and r["W1_T_max"] <= W1_FLOOR_T)
        c["mass_dev"] = r["mass_dev"]
        c["mass_ok"] = r["mass_dev"] <= MASS_FLOOR
        c["reversed_cells"] = r["reversed_cells"]
        c["v_min"] = r["v_min"]
        print("  %s gate (1): C_CONV %s (worst final-10%% initial residuals %s; Ux REPORTED %s) | "
              "C_PLAT %s (%.3e) | W1 %s (row-max v %.3e / %.0e, GRADED READER g %.3e / %.0e, "
              "T %.3e / %.0e: %s) | C_MASS %s (%.3e) | C_REV %d reversed cell(s), min v/U0 %+.6f"
              % (case, "ok" if c["ok"] else "FAIL " + c["why"],
                 {k: ("%.2e" % v if v is not None else None) for k, v in c.get("worst", {}).items() if k != "Ux"},
                 ("%.2e" % c["Ux_reported_not_gated"]) if c.get("Ux_reported_not_gated") is not None else "n/a",
                 "ok" if c["plateau_ok"] else "FAIL", plat,
                 "ok" if c["W1_ok"] else "FAIL", r["W1_v_max"], W1_FLOOR_V, r["W1_g_max"],
                 W1_FLOOR_G, r["W1_T_max"], W1_FLOOR_T,
                 {k: "v %.1e g %.1e T %.1e" % (v["v"], v["g"], v["T"]) for k, v in r["W1"].items()},
                 "ok" if c["mass_ok"] else "FAIL", r["mass_dev"], r["reversed_cells"], r["v_min"]))
        for name, ok in (("C_CONV", c["ok"]), ("C_PLAT", c["plateau_ok"]), ("W1", c["W1_ok"]),
                         ("C_MASS", c["mass_ok"]), ("C_REV", c["reversed_cells"] == 0)):
            if not ok:
                gate1_ok = False
                gate1_why.append("%s fails %s" % (case, name))
    control = planted_zero_controls(os.path.join(root, CASES["f"]), times["f"][-1], idents["f"])
    for k, v in control.items():
        print("planted-zero control %s PASS: %s plant %.4g in %s (%d cell(s)), recovered %.4g, "
              "demonstrated detection floor %g x scale"
              % (k, v["shape"], v["plant"], v["field"], v["cells_planted"], v["recovered"],
                 v["demonstrated_detection_floor"]))

    rows = []
    G = reg["graded_rows"]
    specs = [
        ("G1", G["G1"]["quantity"], "G1", EX.U_STAR, G["G1"]["band_rel"], "rel", False),
        ("G1b", G["G1b"]["quantity"], "G1b", EX.Y_MAX, G["G1b"]["band_abs"], "abs", False),
        ("G3", G["G3"]["quantity"], "G3", EX.SHEAR_RATIO, G["G3"]["band_rel"], "rel", False),
        ("G2", G["G2"]["quantity"], "G2", 0.0, G["G2"]["floor_abs"], "abs", True),
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
                         extra=(dict(tau_hot=reads["f"]["tau_hot"], tau_cold=reads["f"]["tau_cold"])
                                if rid == "G3" else {})))
        print("%-3s fine=%.10e ref=%.10e dev=%+.3e%s band=[%.6e, %.6e] triple=(%.8e, %.8e, %.8e) %s "
              "-> %s%s"
              % (rid, vals["f"], ref, dev, (" (rel %+.3e)" % (dev / ref)) if ref else "", lo, hi,
                 vals["c"], vals["m"], vals["f"], fmt_tr(tr), verdict,
                 ("  [" + note + "]") if note else ""))
    if not gate1_ok:
        print("gate (1) FAILED: " + "; ".join(gate1_why))
    out = dict(rung="T16", solver="buoyantBoussinesqSimpleFoam laminar",
               G_mix=EX.G_REG, G_reversal=EX.G_REVERSAL, dim=DIM,
               refinement_ratio=REFINEMENT, factor_of_safety=FS,
               floors=dict(STAGNANT_FLOOR=STAGNANT_FLOOR, P_MIN=P_MIN, CONV_FLOOR=CONV_FLOOR,
                           PLAT_FLOOR=PLAT_FLOOR, W1_FLOOR_V=W1_FLOOR_V, W1_FLOOR_G=W1_FLOOR_G,
                           W1_FLOOR_T=W1_FLOOR_T,
                           MASS_FLOOR=MASS_FLOOR),
               identities={lv: idents[lv] for lv in LEVELS}, times=times,
               gate1=dict(ok=gate1_ok, why=gate1_why, per_level=conv),
               readers={lv: reads[lv] for lv in LEVELS}, planted_zero_controls=control, rows=rows)
    json.dump(out, open(json_out, "w"), indent=2, default=str)
    print("wrote %s" % json_out)
    return EXIT_OK


# ---------------------------------------------------------------- selftest
def _forge_case(root, lv, N, transpose=False, witness_bump=0.0, uniform_T=False,
                residual=1e-9, plateau_bump=0.0, g_mutant=False, mass_bump=0.0,
                reversal=False):
    """A synthetic finished case shaped like a T16 run: v from the 1-D discrete
    expectation at every row (so the forged ladder carries a REAL second-order
    error law and is developed by construction), T linear, dummies for
    p_rgh/phi, a log with residual lines, STATUS, DONE."""
    import build_t16 as B
    case = os.path.join(root, CASES[lv])
    Ny = B.ASPECT * N
    os.makedirs(os.path.join(case, "system"))
    os.makedirs(os.path.join(case, "constant"))
    os.makedirs(os.path.join(case, "0.orig"))
    os.makedirs(os.path.join(case, "0"))
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(B.block_mesh_dict(N, B.ASPECT))
    et = B.END_TIME[lv]
    open(os.path.join(case, "system", "controlDict"), "w").write(B.control_dict(et))
    for k, v in B.constant_files().items():
        if g_mutant and k == "transportProperties":
            v = v.replace("nu              %.17g" % B.NU, "nu              %.17g" % (B.NU * 1.01))
        open(os.path.join(case, "constant", k), "w").write(v)
    for k, v in B.fields().items():
        open(os.path.join(case, "0.orig", k), "w").write(v)
        open(os.path.join(case, "0", k), "w").write(v)
    Y, ph = EX.discrete_profile(N)
    j0 = B.STATION_B * N
    j_wit = j0 + B.WITNESS_B[0] * N

    def write_time(t, bump):
        td = os.path.join(case, str(t))
        os.makedirs(td)
        Uv, Tv = [], []
        for j in range(Ny):
            for i in range(N):
                ii, jj = (j % N, i) if transpose else (i, j)   # transpose: y-fastest ordering
                v = B.U0 * ph[ii] * (1.0 + bump)
                if witness_bump and jj == j_wit:
                    v *= (1.0 + witness_bump)
                if mass_bump and jj == j0:
                    v *= (1.0 + mass_bump)
                if reversal and ii == 0:
                    # C_REV arm: the wall-adjacent cell is flipped NEGATIVE IN
                    # EVERY ROW, station and witnesses alike, so the W1
                    # development witness stays at zero and this arm drives
                    # C_REV (and, unavoidably, C_MASS -- a reversed cell moves
                    # the row mean) rather than swamping W1's planted control.
                    v = -1.0e-9 * B.U0
                Uv.append("(0 %.17g 0)" % v)
                Tv.append("%.17g" % (B.T_HOT - B.DT * Y[ii]))
        def hdr(cls, obj):
            return B.head(cls, obj, str(t))
        open(os.path.join(td, "U"), "w").write(
            hdr("volVectorField", "U") + "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform "
            "List<vector> \n%d\n(\n%s\n)\n;\nboundaryField { }\n" % (N * Ny, "\n".join(Uv)))
        if uniform_T:
            open(os.path.join(td, "T"), "w").write(
                hdr("volScalarField", "T") + "dimensions [0 0 0 1 0 0 0];\ninternalField uniform 300;\n"
                "boundaryField { }\n")
        else:
            open(os.path.join(td, "T"), "w").write(
                hdr("volScalarField", "T") + "dimensions [0 0 0 1 0 0 0];\ninternalField nonuniform "
                "List<scalar> \n%d\n(\n%s\n)\n;\nboundaryField { }\n" % (N * Ny, "\n".join(Tv)))
        for f in ("p_rgh", "phi"):
            open(os.path.join(td, f), "w").write(hdr("volScalarField", f) + "internalField uniform 0;\n")
    write_time(et - et // 10, plateau_bump)
    write_time(et, 0.0)
    with open(os.path.join(case, "log.solve"), "w") as fh:
        for it in range(1, et + 1):
            r = residual if it > 0.9 * et else 1e-3
            fh.write("Time = %d\n" % it)
            for f in ("Ux", "Uy", "T", "p_rgh"):
                fh.write("solver:  Solving for %s, Initial residual = %.3e, Final residual = 1e-12, "
                         "No Iterations 1\n" % (f, 0.05 if f == "Ux" else r))
            fh.write("ExecutionTime = 1 s  ClockTime = 1 s\n\n")
        fh.write("End\n")
    open(os.path.join(root, "STATUS.%s" % CASES[lv]), "w").write("case=%s\nrc=0\ncapped=no\n" % CASES[lv])
    open(os.path.join(root, "DONE.%s" % CASES[lv]), "w").write("forged\n")


def selftest():
    import ast
    import subprocess
    import build_t16 as B
    fails = []
    reg = load_registered()
    print("analyse_t16 selftest:")
    # (i) the DERIVED reference verifies and the readers are exact on it
    r, f = EX.verify(quiet=True)
    ok = (r is not None and not f)
    print("  [%s] the referent's Route B verifies (B1 B2 B3 B4 B4b)" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("routeB")
    EX.selfcheck_readers()
    # (ii) the floors are the imports, and a mutant registration is refused
    fired = False
    tmpj = tempfile.mkdtemp(prefix="t16reg_")
    try:
        bad = dict(reg)
        bad["roache_floors"] = dict(reg["roache_floors"], P_MIN=0.5)
        json.dump(bad, open(os.path.join(tmpj, "T16_registered.json"), "w"))
        try:
            load_registered(here=tmpj)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmpj, ignore_errors=True)
    print("  [%s] registered P_MIN mutated to 0.5 -> REFUSE (import %g / %g is the one number)"
          % ("ok " if fired else "FAIL", STAGNANT_FLOOR, P_MIN))
    if not fired:
        fails.append("floors")
    # (ii-b) a registration whose G is not the referent's is refused
    fired = False
    tmpj = tempfile.mkdtemp(prefix="t16reg2_")
    try:
        bad = json.loads(json.dumps(reg))
        bad["physics"]["G_mix"] = 47.0
        json.dump(bad, open(os.path.join(tmpj, "T16_registered.json"), "w"))
        try:
            load_registered(here=tmpj)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmpj, ignore_errors=True)
    print("  [%s] registered G_mix mutated to 47 -> REFUSE (the referent's G_REG is the one number)"
          % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("gmix-reg")
    # (iii) rule 5 through apply_gate on synthetic triples, driven at the floors
    ref = EX.U_STAR
    width = reg["graded_rows"]["G1"]["band_rel"]
    lo, hi = ref * (1 - width), ref * (1 + width)

    def ladder(p, e_f=None):
        e_f = (0.4 * width * ref) if e_f is None else e_f
        return dict(f=ref + e_f, m=ref + e_f * 2 ** p, c=ref + e_f * 4 ** p)

    for label, vals, want, want_gci in (
            ("healthy p=2.000", ladder(2.0), "PASS", True),
            ("p=0.51 (just above STAGNANT_FLOOR)", ladder(0.51), "PASS", True),
            ("p=0.49 (just below STAGNANT_FLOOR) -> STAGNANT", ladder(0.49), "NOT A RESULT", False),
            ("p=0.01 (below P_MIN) -> DEGENERATE", ladder(0.01), "NOT A RESULT", False),
            ("oscillatory", dict(c=ref + 1e-4, m=ref - 1e-4, f=ref + 5e-5), "NOT A RESULT", False),
            ("divergent", ladder(-1.0), "NOT A RESULT", False),
            ("healthy p=2 but fine OUTSIDE the band", ladder(2.0, e_f=3.0 * width * ref), "GATE FAIL", True),
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
    print("  [%s] EXACT-class row with an EXACT triple -> floor verdict %s (state %s)"
          % ("ok " if ok else "FAIL", v, tr["state"]))
    if not ok:
        fails.append("exact-class")
    v, bv, note = apply_gate(3e-6, -1e-6, 1e-6, tr, True, "", True)
    ok = (v == "GATE FAIL")
    print("  [%s] EXACT-class row outside its floor -> %s" % ("ok " if ok else "FAIL", v))
    if not ok:
        fails.append("exact-class-fail")

    # (iv) THE VALUE CONTROL (N-T8): a forged ladder built from the 1-D discrete
    # expectation must grade PASS with p = 2 and the fine G1 equal to the model
    # THE FORGED LADDER IS BUILT AT REDUCED N (5 / 10 / 20 rather than the
    # registered 20 / 40 / 80).  The refinement ratio is still exactly 2, the
    # discrete model is exact at any N, and the error law is still h^2, so every
    # clause this selftest drives is driven identically -- while the forged tree
    # stays at 33 600 cells instead of 537 600 and the selftest runs in seconds.
    # The station and witness rows are indexed in GAPS, so they scale with N by
    # construction and no index is hard-coded.
    FORGE_N = {"c": 5, "m": 10, "f": 20}

    def run_forged(**kw):
        tmp = tempfile.mkdtemp(prefix="t16forge_")
        try:
            for lv in LEVELS:
                _forge_case(tmp, lv, FORGE_N[lv], **kw)
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
    exp = EX.discrete_expectation(FORGE_N["f"])
    rows = {r["row"]: r for r in res["rows"]} if res else {}
    # THE BAND IS THE REGISTERED ONE (sized on N = 80) while the forge runs at
    # N = 20, so the expected verdict is whatever the band ARITHMETIC gives for
    # the model value at the forged fine level -- computed here, never assumed.
    _g1 = reg["graded_rows"]["G1"]["band_rel"]
    want_g1 = "PASS" if abs(exp["G1_rel_err"]) <= _g1 else "GATE FAIL"
    ok = (code == 0 and rows
          and rows["G1"]["verdict"] == want_g1
          and abs(rows["G1"]["value_fine"] - exp["G1"]) < 1e-12
          # p is checked NEAR 2, not AT 2: the forged ladder runs at N = 5/10/20,
          # where the discrete error law is second order but not yet asymptotically
          # exact.  The EXACT check is the line above it -- the fine value equals
          # the 1-D model to 1e-12.
          and abs(rows["G1"]["observed_order"] - 2.0) < 0.15
          and rows["G2"]["verdict"] == "PASS"
          and abs(rows["G2"]["value_fine"]) < 1e-9
          and all(res["planted_zero_controls"][k]["status"] == "PASS"
                  for k in ("G1", "G1b", "G2", "G3", "W1_max")))
    print("  [%s] VALUE CONTROL: forged ladder from the 1-D model at N = %d/%d/%d grades G1 %s "
          "(the band arithmetic at that N) p=%s fine=%s == model %.10e to 1e-12; G2 triple %s "
          "(EXACT-class: state PRINTED, verdict by floor); 5 planted controls PASS"
          % ("ok " if ok else "FAIL", FORGE_N["c"], FORGE_N["m"], FORGE_N["f"], want_g1,
             ("%.4f" % rows["G1"]["observed_order"]) if rows else "?",
             ("%.10e" % rows["G1"]["value_fine"]) if rows else "?", exp["G1"],
             rows["G2"]["triple_state"] if rows else "?"))
    if not ok:
        fails.append("value-control")
    # THE REGISTRATION'S OWN LADDER CLAIM, as pure arithmetic on the DERIVED model
    # at the REGISTERED levels: the fine level must sit INSIDE each band and the
    # coarse and medium levels OUTSIDE it.  This is what the bands were sized to
    # say, and it is checked here rather than asserted in prose.
    import build_t16 as _B
    Ns = [_B.LEVELS[k] for k in ("c", "m", "f")]
    E = {r["N"]: r for r in EX.expectation_table(Ns)}
    gr = reg["graded_rows"]
    claims = [
        ("G1", "G1_rel_err", gr["G1"]["band_rel"]),
        ("G1b", "G1b_abs_err", gr["G1b"]["band_abs"]),
        ("G3", "G3_rel_err", gr["G3"]["band_rel"]),
    ]
    lad_ok = True
    for rid, key, w in claims:
        inside_f = abs(E[Ns[2]][key]) <= w
        outside_cm = abs(E[Ns[0]][key]) > w and abs(E[Ns[1]][key]) > w
        lad_ok = lad_ok and inside_f and outside_cm
        print("      %-4s band %.3e: derived c %.3e / m %.3e / f %.3e -> f INSIDE %s, "
              "c and m OUTSIDE %s" % (rid, w, abs(E[Ns[0]][key]), abs(E[Ns[1]][key]),
                                      abs(E[Ns[2]][key]), inside_f, outside_cm))
    print("  [%s] LADDER CLAIM: every registered band admits the DERIVED fine level and "
          "excludes the coarse and medium ones" % ("ok " if lad_ok else "FAIL"))
    if not lad_ok:
        fails.append("ladder-claim")
    # (v) gate (1) arms, one at a time
    for label, kw in (
            ("W1 development witness bumped 1e-4 on a witness row -> gate (1)", dict(witness_bump=1e-4)),
            ("final-10%% residual 1e-3, above the registered 1e-4 floor -> gate (1)", dict(residual=1e-3)),
            ("G1 moved 1e-5 between the last two writes -> gate (1)", dict(plateau_bump=1e-5)),
            ("station row mean scaled 1e-4 off U0 -> C_MASS gate (1)", dict(mass_bump=1e-4)),
            ("one REVERSED cell on the station row -> C_REV gate (1)", dict(reversal=True))):
        code, res = run_forged(**kw)
        ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"])
              and not res["gate1"]["ok"])
        print("  [%s] %s -> NOT A RESULT x4" % ("ok " if ok else "FAIL", label))
        if not ok:
            fails.append(label)
    # (vi) refusals: transposed ordering, uniform T, G mutant
    for label, kw in (("transposed (y-fastest) cell ordering -> C_ORDER REFUSE", dict(transpose=True)),
                      ("uniform T at endTime -> REFUSE", dict(uniform_T=True)),
                      ("nu mutated 1 percent in transportProperties -> C_G REFUSE", dict(g_mutant=True))):
        code, res = run_forged(**kw)
        ok = (code == EXIT_REFUSE)
        print("  [%s] %s (exit %s)" % ("ok " if ok else "FAIL", label, code))
        if not ok:
            fails.append(label)
    # (vii) the planted-zero controls, both arms, on a forged case
    tmp = tempfile.mkdtemp(prefix="t16blind_")
    try:
        _forge_case(tmp, "c", FORGE_N["c"])
        d = os.path.join(tmp, CASES["c"])
        ident = case_identity(d, reg)
        t = latest_times(d, 1)[-1]
        good = readers(d, t, ident)

        def blind(case_dir, time, ident):
            return dict(good)                       # returns the same numbers whatever is on disk

        fired = False
        try:
            planted_zero_controls(d, t, ident, read=blind)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        print("  [%s] BLIND reader mutant (ignores the plant) -> planted-zero control REFUSES"
              % ("ok " if fired else "FAIL"))
        if not fired:
            fails.append("blind")
        rep = planted_zero_controls(d, t, ident)
        ok = (all(rep[k]["status"] == "PASS" for k in rep)
              and rep["G2"]["cells_planted"] == FORGE_N["c"]
              and rep["G2"]["shape"] == "ALL-ROW ALTERNATING SIGN")
        print("  [%s] real reader: 5/5 planted controls PASS; G2's plant covers all %d row cells "
              "and ALTERNATES IN SIGN (L-340)"
              % ("ok " if ok else "FAIL", rep["G2"]["cells_planted"]))
        if not ok:
            fails.append("real-reader")
        # L-340 SHARPENED: a CONSTANT all-row plant is what an RMS-about-a-fit
        # reader would be blind to.  Drive it, and record what THIS reader does.
        base = readers(d, t, ident)
        dst = tempfile.mkdtemp(prefix="t16const_")
        try:
            cp = os.path.join(dst, CASES["c"])
            shutil.copytree(d, cp)
            N = ident["N"]
            idxs = [i + N * ident["j_station"] for i in range(N)]
            plant(cp, t, "T", idxs, [PLANT_REL * ident["dT"]] * N, None)
            got = readers(cp, t, ident)
            seen = abs(got["G2"] - base["G2"])
            print("  [--] L-340 DISCLOSURE: a CONSTANT all-row plant of %.4g K moves this G2 reader "
                  "by %.3e (it measures RMS about the REGISTERED linear profile, not about a fit, "
                  "so it does see a constant); the registered plant ALTERNATES anyway, so the "
                  "control does not depend on that property holding"
                  % (PLANT_REL * ident["dT"], seen))
        finally:
            shutil.rmtree(dst, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # (viii) the live tree today: DONE markers absent -> REFUSE (both interpreters)
    for flag in ((), ("-O",)):
        r = subprocess.run([sys.executable, *flag, os.path.abspath(__file__), "--json", os.devnull],
                           capture_output=True, text=True)
        ok = (r.returncode == EXIT_REFUSE and "no DONE." in r.stdout)
        print("  [%s] live tree, python3 %s: no DONE markers -> exit %d %s"
              % ("ok " if ok else "FAIL", " ".join(flag) or "", r.returncode,
                 r.stdout.strip().splitlines()[0][:60] if r.stdout.strip() else ""))
        if not ok:
            fails.append("live-refuse")
    n_assert = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)"
          % ("ok " if ok else "FAIL", n_assert, planted))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=HERE, help="run tree (selftest use)")
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t16.json"))
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    reg = load_registered()
    return grade(os.path.abspath(a.root), a.json, reg)


if __name__ == "__main__":
    sys.exit(main())
