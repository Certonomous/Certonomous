#!/usr/bin/env python3
"""
T9a comparator -- composite wall and fin efficiency against closed-form theory.

WRITTEN AND COMMITTED BEFORE ANY CASE EXISTED (Charter 2d, prediction-first).
At the moment this file is frozen the run tree holds no case directory, no
builder and no mesh; the registered values it grades against live in
T9a_registered.json, armed alongside it.

Registered rows (T9a_PREREGISTRATION.md):

  R0  wall  q''            19.502682 W/m2          (dT / sum(L/k), exact)
  R1  wall  T interface 1  348.781082 K
  R2  wall  T interface 2  300.024378 K
  R3  fin   efficiency     0.8332367               (tanh(mL)/mL, mL = 0.790569)
  R4  fin   tip ratio      0.7523781               (1/cosh(mL))

THE BAND IS DERIVED, NEVER CHOSEN: three mesh levels at nominal ratio 1.6,
Roache GCI at Fs = 1.25 on the finest.  An oscillatory, stagnant or divergent
triple arms no band and the row is NOT A RESULT.

THE FIN REFERENCE'S OWN VALIDITY IS PART OF THE REGISTRATION.  The fin
equation is one-dimensional and valid to O(Bi) = 0.025 %.  If the armed band
on a fin row comes out BELOW 0.025 %, that row is REPORTED AND NOT GRADED
(verdict GATE REACHED): below the floor the disagreement measures the fin
equation's one-dimensionality, not this lab's solver.

CONTROLS, each of which MUST FAIL if the rung is sound:
  C1  the finest wall q'' graded against the ARITHMETIC MEAN conductivity.
  C2  the finest fin efficiency graded against eta = 1.
  C3  a uniform-temperature solid (Charter 2c): the solved uniform wall case
      W_C3, plus a synthetic uniform field pushed through the fin pipeline.

CARRIED FORWARD, because they were paid for once:
  * every geometric constant is READ FROM THE MESH (constant/polyMesh/points),
    never taken from the builder -- assuming D/2 in T1c cost 9 % of Nu;
  * convergence is judged by comparing the last two WRITTEN checkpoints,
    never by residualControl (L-141), possible because writeInterval is
    strictly less than endTime (L-140);
  * the reference constants are re-derived here two independent ways
    (exact_t9a.py) and this comparator REFUSES TO RUN if they disagree.

WHAT THIS COMPARATOR CANNOT SEE, stated so the check does not overstate its
reach: nothing about conjugate coupling (both fluids are boundary conditions,
the coupled interface is T9b), nothing about any turbulence or thermal
closure (there is no fluid), and nothing about contact resistance,
anisotropic or temperature-dependent conductivity, all excluded by
construction.
"""
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_t9a as EXACT          # noqa: E402

REG = json.load(open(os.path.join(HERE, "T9a_registered.json")))
FS = REG["grid"]["Fs"]
R_REFINE = REG["grid"]["r"]
FLOOR_PCT = REG["fin"]["model_error_floor_pct"]

WALL_LEVELS = {"c": "W_c", "m": "W_m", "f": "W_f"}
FIN_LEVELS = {"c": "F_c", "m": "F_m", "f": "F_f"}
ALL_CASES = list(WALL_LEVELS.values()) + ["W_C3"] + list(FIN_LEVELS.values())
LEVELS = ("c", "m", "f")

# the fixed verdict vocabulary (REPORTING_CHARTER.md section "Rules" item 5)
PASS, GATE_REACHED, GATE_FAIL = "PASS", "GATE REACHED", "GATE FAIL"
NOT_A_RESULT, BLOCKED, PENDING = "NOT A RESULT", "BLOCKED", "PENDING"

EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print(msg)
    sys.exit(EXIT_REFUSE)


def foam(case_dir, cmd):
    return subprocess.run(
        f"source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1 && "
        f"cd {case_dir} && {cmd}",
        shell=True, executable="/bin/bash", capture_output=True, text=True)


def latest_time(case):
    ts = [d for d in os.listdir(case)
          if re.fullmatch(r"\d+(\.\d+)?", d) and float(d) != 0.0]
    if not ts:
        refuse(f"REFUSE: {case} has no written time directory.")
    return max(ts, key=float)


def read_internal(path, ncells=None):
    """Scalar internalField; a collapsed 'uniform' entry is expanded to ncells."""
    txt = open(path, errors="replace").read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?(\d+)\s*\(",
                  txt)
    if m:
        n = int(m.group(1))
        vals = [float(v) for v in
                re.findall(r"[-0-9.eE+]+", txt[m.end():])[:n]]
        if len(vals) != n:
            refuse(f"REFUSE: short internalField in {path}")
        return vals
    m2 = re.search(r"internalField\s+uniform\s+([-0-9.eE+]+)\s*;", txt)
    if m2:
        v = float(m2.group(1))
        return [v] * (ncells if ncells else 1)
    refuse(f"REFUSE: cannot parse internalField in {path}")


def boundary_blocks(path):
    """Return {patchName: blockText} from a field file's boundaryField."""
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
    out = {}
    k = 0
    while True:
        m = re.search(r"([A-Za-z_][\w.]*)\s*\{", body[k:])
        if not m:
            break
        name = m.group(1)
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


def patch_uniform(block, key, path, patch):
    m = re.search(re.escape(key) + r"\s+uniform\s+([-0-9.eE+]+)\s*;", block)
    if not m:
        refuse(f"REFUSE: no uniform '{key}' on patch {patch} in {path}")
    return float(m.group(1))


def read_points(case):
    """All mesh points, READ FROM THE MESH.  Never from the builder."""
    p = os.path.join(case, "constant", "polyMesh", "points")
    if not os.path.isfile(p):
        refuse(f"REFUSE: no polyMesh/points in {case}")
    txt = open(p, errors="replace").read()
    pts = [tuple(float(x) for x in m.groups()) for m in
           re.finditer(r"\(\s*([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\s*\)",
                       txt)]
    if not pts:
        refuse(f"REFUSE: cannot parse points in {case}")
    return pts


def cell_centres(case, t):
    for func in ("writeCellCentres", "writeCellVolumes"):
        if not os.path.isfile(os.path.join(case, t, "V" if "Volumes" in func
                                           else "Cx")):
            r = foam(case, f"postProcess -func {func} -time {t} "
                           f"> log.{func} 2>&1")
            if r.returncode != 0:
                refuse(f"REFUSE: {func} failed in {case}")
    Cx = read_internal(os.path.join(case, t, "Cx"))
    Cy = read_internal(os.path.join(case, t, "Cy"))
    V = read_internal(os.path.join(case, t, "V"))
    return Cx, Cy, V


def iterative_convergence(case, field="T", tol=1e-6):
    """Compare the last two written checkpoints (L-141, mirrored from T1c).

    residualControl is NOT consulted: across T1c and T1b it never once fired
    while byte-identical checkpoints proved convergence directly, and one
    unconverged case impersonated a discretisation failure until the written
    fields were compared."""
    ts = sorted((d for d in os.listdir(case)
                 if re.fullmatch(r"\d+(\.\d+)?", d) and float(d) != 0.0),
                key=float)
    if len(ts) < 2:
        return dict(state="UNJUDGED",
                    why=f"only {len(ts)} checkpoint(s) on disk; need two")
    n = None
    a = read_internal(os.path.join(case, ts[-2], field), n)
    b = read_internal(os.path.join(case, ts[-1], field), len(a))
    if len(a) != len(b):
        a = read_internal(os.path.join(case, ts[-2], field), len(b))
    if len(a) != len(b):
        return dict(state="UNJUDGED", why="checkpoint sizes differ")
    dmax = max(abs(x - y) for x, y in zip(a, b))
    rng = max(b) - min(b)
    rel = dmax / rng if rng > 0 else 0.0
    return dict(state="CONVERGED" if rel <= tol else "NOT_CONVERGED",
                max_change=dmax, field_range=rng, relative=rel,
                between=(ts[-2], ts[-1]), tol=tol)


def gci(f_coarse, f_med, f_fine):
    """Observed order and Roache GCI on the finest level.

    Refuses to invent an order: OSCILLATORY, STAGNANT and DIVERGENT triples
    arm no band (registered).  An EXACT triple (the medium and fine levels
    byte-identical) arms a band of literal zero -- it is none of the three
    registered no-band states, and a zero band grades only a literally exact
    match."""
    e21 = f_med - f_fine
    e32 = f_coarse - f_med
    if e21 == 0.0:
        return dict(state="EXACT", GCI_pct=0.0)
    if e32 / e21 < 0.0:
        return dict(state="OSCILLATORY")
    p = math.log(abs(e32 / e21)) / math.log(R_REFINE)
    if p <= 0.0:
        return dict(state="DIVERGENT", order=p)
    if p < 0.5:
        return dict(state="STAGNANT", order=p)
    den = R_REFINE ** p - 1.0
    return dict(state="CONVERGING", order=p,
                GCI_pct=100.0 * FS * abs(e21 / f_fine) / den,
                richardson=f_fine + e21 / den)


# ---------------------------------------------------------------------------
# wall measurement
# ---------------------------------------------------------------------------
def wall_layer_of(x):
    x1 = REG["wall"]["interfaces_x"][0]
    x2 = REG["wall"]["interfaces_x"][1]
    return 0 if x < x1 else (1 if x < x2 else 2)


def measure_wall(case):
    """q'' at both faces and the two interface temperatures, geometry from
    the mesh."""
    t = latest_time(case)
    pts = read_points(case)
    xs_pts = sorted(set(round(p[0], 12) for p in pts))
    x_hot, x_cold = xs_pts[0], xs_pts[-1]
    thick = x_cold - x_hot
    if abs(thick - REG["wall"]["total_thickness"]) > 1e-9:
        refuse(f"REFUSE: {case} total thickness {thick} is not the registered "
               f"{REG['wall']['total_thickness']}")
    for xi in REG["wall"]["interfaces_x"]:
        if min(abs(v - xi) for v in xs_pts) > 1e-9:
            refuse(f"REFUSE: {case} has no mesh face at the registered "
                   f"interface x = {xi}")

    Cx, _, V = cell_centres(case, t)
    n = len(Cx)
    T = read_internal(os.path.join(case, t, "T"), n)
    DT = read_internal(os.path.join(case, t, "DT"), n)
    ks = [ly["k"] for ly in REG["wall"]["layers"]]
    for i in range(n):
        kreg = ks[wall_layer_of(Cx[i])]
        if abs(DT[i] - kreg) / kreg > 1e-9:
            refuse(f"REFUSE: {case} cell at x = {Cx[i]:.6g} carries "
                   f"DT = {DT[i]} where the registered layer map says {kreg}")

    blocks = boundary_blocks(os.path.join(case, t, "T"))
    if "hot" not in blocks or "cold" not in blocks:
        refuse(f"REFUSE: {case} T has no hot/cold patches")
    T_hot = patch_uniform(blocks["hot"], "value", case, "hot")
    T_cold = patch_uniform(blocks["cold"], "value", case, "cold")

    order = sorted(range(n), key=lambda i: Cx[i])
    i0, iN = order[0], order[-1]
    d_hot = Cx[i0] - x_hot
    d_cold = x_cold - Cx[iN]
    q_hot = ks[0] * (T_hot - T[i0]) / d_hot
    q_cold = ks[2] * (T[iN] - T_cold) / d_cold
    q_mean = 0.5 * (q_hot + q_cold)
    closure = abs(q_hot - q_cold) / max(abs(q_mean), 1e-30)

    def iface_T(xi):
        left = [i for i in order if Cx[i] < xi]
        right = [i for i in order if Cx[i] > xi]
        iL = max(left, key=lambda i: Cx[i])
        iR = min(right, key=lambda i: Cx[i])
        wL = ks[wall_layer_of(Cx[iL])] / (xi - Cx[iL])
        wR = ks[wall_layer_of(Cx[iR])] / (Cx[iR] - xi)
        return (wL * T[iL] + wR * T[iR]) / (wL + wR)

    return dict(time=t, n_cells=n, thickness=thick,
                T_hot=T_hot, T_cold=T_cold,
                q_hot=q_hot, q_cold=q_cold, q=q_mean,
                heat_balance_closure=closure,
                T_i1=iface_T(REG["wall"]["interfaces_x"][0]),
                T_i2=iface_T(REG["wall"]["interfaces_x"][1]))


# ---------------------------------------------------------------------------
# fin measurement
# ---------------------------------------------------------------------------
def measure_fin(case, synthetic_T=None):
    """eta and tip ratio, geometry from the mesh.

    synthetic_T: if given (a constant), the measurement pipeline runs on a
    uniform field at that temperature instead of the solved one -- the C3
    trivial baseline for the fin, which cannot be a solved case because a
    fin held at T_inf = T_base has zero driving difference and eta is 0/0."""
    t = latest_time(case)
    pts = read_points(case)
    xs = sorted(set(round(p[0], 12) for p in pts))
    ys = sorted(set(round(p[1], 12) for p in pts))
    zs = sorted(set(round(p[2], 12) for p in pts))
    L = xs[-1] - xs[0]
    th = ys[-1] - ys[0]
    W = zs[-1] - zs[0]
    if abs(L - REG["fin"]["L"]) > 1e-9 or abs(th - REG["fin"]["t"]) > 1e-9:
        refuse(f"REFUSE: {case} mesh extents L = {L}, t = {th} are not the "
               f"registered {REG['fin']['L']} x {REG['fin']['t']}")

    Cx, Cy, V = cell_centres(case, t)
    n = len(Cx)
    T = read_internal(os.path.join(case, t, "T"), n)
    if synthetic_T is not None:
        T = [synthetic_T] * n

    k = REG["fin"]["k"]
    h = REG["fin"]["h"]
    blocks = boundary_blocks(os.path.join(case, t, "T"))
    for p in ("base", "tip", "top", "bottom"):
        if p not in blocks:
            refuse(f"REFUSE: {case} T has no patch '{p}'")
    T_b = patch_uniform(blocks["base"], "value", case, "base")
    T_inf = patch_uniform(blocks["top"], "refValue", case, "top")
    T_inf2 = patch_uniform(blocks["bottom"], "refValue", case, "bottom")
    if T_inf != T_inf2:
        refuse(f"REFUSE: {case} top/bottom refValue differ")
    for p in ("top", "bottom"):
        if patch_uniform(blocks[p], "refGradient", case, p) != 0.0:
            refuse(f"REFUSE: {case} patch {p} refGradient is not 0")
    fv = {p: patch_uniform(blocks[p], "valueFraction", case, p)
          for p in ("top", "bottom")}

    xcs = sorted(set(round(v, 12) for v in Cx))
    ycs = sorted(set(round(v, 12) for v in Cy))
    dxs = [b - a for a, b in zip(xcs, xcs[1:])]
    dys = [b - a for a, b in zip(ycs, ycs[1:])]
    if dxs and (max(dxs) - min(dxs)) / max(dxs) > 1e-6:
        refuse(f"REFUSE: {case} x spacing is not uniform")
    if dys and (max(dys) - min(dys)) / max(dys) > 1e-6:
        refuse(f"REFUSE: {case} y spacing is not uniform")
    dx = L / len(xcs)
    dy = th / len(ycs)

    # the mixed valueFraction encodes k/(h d); d is READ FROM THE MESH here
    d_wall_bot = ycs[0] - ys[0]
    d_wall_top = ys[-1] - ycs[-1]
    for p, d in (("top", d_wall_top), ("bottom", d_wall_bot)):
        f_exp = 1.0 / (1.0 + k / (h * d))
        if abs(fv[p] - f_exp) / f_exp > 1e-6:
            refuse(f"REFUSE: {case} patch {p} valueFraction {fv[p]:.10e} "
                   f"disagrees with 1/(1 + k/(h d)) = {f_exp:.10e} for the "
                   f"mesh-read d = {d:.6e}")

    # base heat flow: the discrete FV boundary flux, per base-adjacent cell
    base_cells = [i for i in range(n) if abs(Cx[i] - xcs[0]) < 1e-12]
    d_base = xcs[0] - xs[0]
    Q_base = sum(k * (T_b - T[i]) / d_base * (dy * W) for i in base_cells)

    # convective heat flow over both Robin faces, T_face from the written BC
    Q_conv = 0.0
    for p, row_y, d in (("top", ycs[-1], d_wall_top),
                        ("bottom", ycs[0], d_wall_bot)):
        cells = [i for i in range(n) if abs(Cy[i] - row_y) < 1e-12]
        f = fv[p]
        for i in cells:
            T_face = f * T_inf + (1.0 - f) * T[i]
            Q_conv += h * (T_face - T_inf) * (dx * W)
    closure = abs(Q_base - Q_conv) / max(abs(Q_base), 1e-30)

    theta_b = T_b - T_inf
    eta = Q_base / (2.0 * h * L * W * theta_b)
    tip_cells = [i for i in range(n) if abs(Cx[i] - xcs[-1]) < 1e-12]
    T_tip = (sum(T[i] * V[i] for i in tip_cells) /
             sum(V[i] for i in tip_cells))
    tip_ratio = (T_tip - T_inf) / theta_b
    return dict(time=t, n_cells=n, L=L, t_fin=th, W=W,
                nx=len(xcs), ny=len(ycs),
                T_base=T_b, T_inf=T_inf,
                Q_base=Q_base, Q_conv=Q_conv, heat_balance_closure=closure,
                eta=eta, tip_ratio=tip_ratio)


# ---------------------------------------------------------------------------
def grade_triple(tag, label, m, key, ref, floor_pct=None):
    """One registered row: convergence-gated GCI band, then the verdict."""
    conv = gci(m["c"][key], m["m"][key], m["f"][key])
    row = dict(row=tag, quantity=label, reference=ref, value=m["f"][key],
               levels={l: m[l][key] for l in LEVELS},
               convergence=conv.get("state"))
    print(f"\n### {tag}  {label}   reference {ref:.7f}")
    for l in LEVELS:
        print(f"    {l}  {m[l][key]:.8f}")
    print(f"    grid triple: {conv}")
    if conv["state"] not in ("CONVERGING", "EXACT"):
        row.update(verdict=NOT_A_RESULT,
                   why=f"grid triple is {conv['state']}; no band can be armed")
        print(f"    {tag}: NOT A RESULT -- {conv['state']}")
        return row
    band = conv["GCI_pct"]
    dev = 100.0 * abs(m["f"][key] - ref) / abs(ref)
    row.update(band_pct=band, deviation_pct=dev, order=conv.get("order"))
    if floor_pct is not None and band < floor_pct:
        row.update(verdict=GATE_REACHED, graded=False,
                   why=f"the armed band {band:.4f} % lies below the fin "
                       f"equation's own {floor_pct} % one-dimensionality "
                       f"error (registered 3.1); the row is REPORTED, "
                       f"NOT GRADED")
        print(f"    {tag}: GATE REACHED -- band {band:.4f} % is below the "
              f"registered {floor_pct} % model-error floor; REPORTED, NOT "
              f"GRADED (deviation would have been {dev:.4f} %)")
        return row
    row.update(graded=True,
               verdict=PASS if dev <= band else GATE_FAIL)
    print(f"    {tag}: value {m['f'][key]:.8f}, deviation {dev:.5f} %, band "
          f"(GCI) {band:.5f} %  -> {row['verdict']}")
    return row


def main():
    # ---- the reference must survive its own re-derivation, or nothing runs
    print("re-deriving the references (exact_t9a.py) ...")
    if EXACT.main() != 0:
        refuse("REFUSE: the exact-theory derivation does not agree with "
               "itself; no reference can be trusted until it does.")

    # third leg: the frozen JSON must match the derivation it was copied from
    wa = EXACT.wall_closed_form()
    fa = EXACT.fin_closed_form()
    for name, reg_v, drv_v, tol in (
            ("sum_R", REG["wall"]["sum_R"], wa["sum_R"], 1e-6),
            ("q", REG["wall"]["q"], wa["q"], 1e-6),
            ("T_i1", REG["wall"]["T_i1"], wa["T_i1"], 1e-8),
            ("T_i2", REG["wall"]["T_i2"], wa["T_i2"], 1e-8),
            ("eta", REG["fin"]["eta"], fa["eta"], 1e-6),
            ("tip_ratio", REG["fin"]["tip_ratio"], fa["tip_ratio"], 1e-6)):
        if abs(reg_v - drv_v) / abs(drv_v) > tol:
            refuse(f"REFUSE: registered {name} = {reg_v} disagrees with the "
                   f"derivation {drv_v}")

    # ---- completion markers: a case without one is not graded --------------
    missing = [c for c in ALL_CASES
               if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: rung is PENDING -- no completion marker for "
               + ", ".join(sorted(missing)))

    out = {"Fs": FS, "r": R_REFINE, "model_error_floor_pct": FLOOR_PCT,
           "rows": [], "controls": [], "cases": {}}

    # ---- iterative convergence gate, before any grid claim -----------------
    conv_all = {}
    for c in ALL_CASES:
        conv_all[c] = iterative_convergence(os.path.join(HERE, c))
        s = conv_all[c]
        print(f"  {c:6s} iterative convergence: {s['state']}"
              + (f"  (rel {s.get('relative', float('nan')):.2e} between "
                 f"{s.get('between')})" if "relative" in s else
                 f"  ({s.get('why')})"))
    out["iterative_convergence"] = conv_all
    bad = [c for c in ALL_CASES if conv_all[c]["state"] != "CONVERGED"]

    # ---- measurements ------------------------------------------------------
    mw = {l: measure_wall(os.path.join(HERE, WALL_LEVELS[l])) for l in LEVELS}
    mf = {l: measure_fin(os.path.join(HERE, FIN_LEVELS[l])) for l in LEVELS}
    mc3 = measure_wall(os.path.join(HERE, "W_C3"))
    for l in LEVELS:
        out["cases"][WALL_LEVELS[l]] = mw[l]
        out["cases"][FIN_LEVELS[l]] = mf[l]
    out["cases"]["W_C3"] = mc3

    print("\nheat-balance closure, every case (registered: reported always):")
    for c in ALL_CASES:
        cl = out["cases"][c]["heat_balance_closure"]
        print(f"  {c:6s} closure {cl:.3e}")

    # ---- registered rows ---------------------------------------------------
    def row_or_unconverged(tag, label, m, key, ref, cases, floor=None):
        unc = [l for l in LEVELS if conv_all[cases[l]]["state"] != "CONVERGED"]
        if unc:
            r = dict(row=tag, quantity=label, reference=ref,
                     value=m["f"][key], unconverged_levels=unc,
                     verdict=NOT_A_RESULT,
                     why="levels " + ",".join(unc) + " had not converged "
                         "iteratively; no grid claim can be made")
            print(f"\n### {tag}  {label}: NOT A RESULT -- unconverged "
                  f"levels {unc}")
            return r
        return grade_triple(tag, label, m, key, ref, floor)

    out["rows"].append(row_or_unconverged(
        "R0", "wall q'' [W/m2]", mw, "q", REG["wall"]["q"], WALL_LEVELS))
    out["rows"].append(row_or_unconverged(
        "R1", "wall interface T after layer 1 [K]", mw, "T_i1",
        REG["wall"]["T_i1"], WALL_LEVELS))
    out["rows"].append(row_or_unconverged(
        "R2", "wall interface T after layer 2 [K]", mw, "T_i2",
        REG["wall"]["T_i2"], WALL_LEVELS))
    out["rows"].append(row_or_unconverged(
        "R3", "fin efficiency", mf, "eta", REG["fin"]["eta"], FIN_LEVELS,
        floor=FLOOR_PCT))
    out["rows"].append(row_or_unconverged(
        "R4", "fin tip excess-temperature ratio", mf, "tip_ratio",
        REG["fin"]["tip_ratio"], FIN_LEVELS, floor=FLOOR_PCT))

    def band_of(tag):
        return next((r.get("band_pct") for r in out["rows"]
                     if r["row"] == tag), None)

    # ---- controls, each of which MUST FAIL ---------------------------------
    print(f"\n{'-'*70}\ncontrols (each MUST fail if the rung is sound):")
    ks = [ly["k"] for ly in REG["wall"]["layers"]]
    k_bar = sum(ks) / len(ks)
    dT = REG["wall"]["T_hot"] - REG["wall"]["T_cold"]
    q_c1 = k_bar * dT / REG["wall"]["total_thickness"]
    b0 = band_of("R0")
    c1_dev = 100.0 * abs(mw["f"]["q"] - q_c1) / q_c1
    c1_met = b0 is not None and c1_dev > b0
    out["controls"].append(dict(
        control="C1_arithmetic_mean_conductivity",
        value=mw["f"]["q"], graded_against=q_c1, deviation_pct=c1_dev,
        band_pct=b0, must="FAIL -- the mean-k rule is off by orders of "
        "magnitude at a 400x contrast", met=c1_met))
    print(f"  C1 wrong resistance rule: q'' = {mw['f']['q']:.4f} graded "
          f"against k_bar dT/L = {q_c1:.4f} -> deviation {c1_dev:.2f} % "
          f"vs band {b0}  -> "
          f"{'MET (fails, as it must)' if c1_met else 'NOT MET'}")

    b3 = band_of("R3")
    c2_dev = 100.0 * abs(mf["f"]["eta"] - 1.0) / 1.0
    c2_met = b3 is not None and c2_dev > b3
    out["controls"].append(dict(
        control="C2_perfect_fin",
        value=mf["f"]["eta"], graded_against=1.0, deviation_pct=c2_dev,
        band_pct=b3,
        must="FAIL -- eta = 1 is the infinite-conductivity limit, 20.0 % "
        "above the registered 0.8332 (measured from eta)", met=c2_met))
    print(f"  C2 perfect fin: eta = {mf['f']['eta']:.6f} graded against 1.0 "
          f"-> deviation {c2_dev:.2f} % vs band {b3}  -> "
          f"{'MET (fails, as it must)' if c2_met else 'NOT MET'}")

    # C3 wall: the SOLVED uniform case, graded against the wall references
    c3_rows = []
    for tag, key, ref in (("q''", "q", REG["wall"]["q"]),
                          ("T_i1", "T_i1", REG["wall"]["T_i1"]),
                          ("T_i2", "T_i2", REG["wall"]["T_i2"])):
        b = band_of({"q''": "R0", "T_i1": "R1", "T_i2": "R2"}[tag])
        dev = 100.0 * abs(mc3[key] - ref) / abs(ref)
        c3_rows.append(dict(quantity=tag, value=mc3[key], reference=ref,
                            deviation_pct=dev, band_pct=b,
                            fails=(b is not None and dev > b)))
    c3w_met = all(r["fails"] for r in c3_rows)
    out["controls"].append(dict(
        control="C3_uniform_wall_solved", rows=c3_rows,
        must="FAIL on every wall row -- a uniform-temperature solid carries "
        "no flux and the wrong interface temperatures", met=c3w_met))
    for r in c3_rows:
        print(f"  C3 wall {r['quantity']:5s}: {r['value']:.6f} vs "
              f"{r['reference']:.6f} -> {r['deviation_pct']:.3f} % vs band "
              f"{r['band_pct']}  -> {'fails' if r['fails'] else 'DOES NOT FAIL'}")
    print(f"  C3 wall overall -> "
          f"{'MET (all fail, as they must)' if c3w_met else 'NOT MET'}")

    # C3 fin: the SYNTHETIC uniform field through the identical pipeline
    ms = measure_fin(os.path.join(HERE, FIN_LEVELS["f"]),
                     synthetic_T=REG["fin"]["T_base"])
    c3f_rows = []
    for tag, key, ref, band_tag in (("eta", "eta", REG["fin"]["eta"], "R3"),
                                    ("tip", "tip_ratio",
                                     REG["fin"]["tip_ratio"], "R4")):
        b = band_of(band_tag)
        dev = 100.0 * abs(ms[key] - ref) / abs(ref)
        c3f_rows.append(dict(quantity=tag, value=ms[key], reference=ref,
                             deviation_pct=dev, band_pct=b,
                             fails=(b is not None and dev > b)))
    c3f_met = all(r["fails"] for r in c3f_rows)
    out["controls"].append(dict(
        control="C3_uniform_fin_synthetic", rows=c3f_rows,
        must="FAIL on both fin rows -- a uniform field at T_base has zero "
        "base flux (eta = 0) and a tip ratio of 1",
        met=c3f_met,
        note="synthetic because a solved uniform fin needs T_inf = T_base, "
             "which makes eta 0/0 and ungradeable"))
    for r in c3f_rows:
        print(f"  C3 fin {r['quantity']:4s}: {r['value']:.6f} vs "
              f"{r['reference']:.6f} -> {r['deviation_pct']:.3f} % vs band "
              f"{r['band_pct']}  -> {'fails' if r['fails'] else 'DOES NOT FAIL'}")
    print(f"  C3 fin overall -> "
          f"{'MET (both fail, as they must)' if c3f_met else 'NOT MET'}")

    # ---- verdict summary and exit ------------------------------------------
    with open(os.path.join(HERE, "gate_t9a.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)

    fails = [r for r in out["rows"] if r["verdict"] == GATE_FAIL]
    nres = [r for r in out["rows"] if r["verdict"] == NOT_A_RESULT]
    reported = [r for r in out["rows"] if r["verdict"] == GATE_REACHED]
    unmet = [c for c in out["controls"] if not c["met"]]
    print(f"\n{'-'*70}")
    print(f"  {len(out['rows'])} registered rows: "
          f"{sum(1 for r in out['rows'] if r['verdict'] == PASS)} PASS, "
          f"{len(fails)} GATE FAIL, {len(nres)} NOT A RESULT, "
          f"{len(reported)} GATE REACHED (reported, not graded)")
    print(f"  {len(out['controls'])} controls, {len(unmet)} NOT MET"
          + ("" if not unmet else " -- the rung is unsound: "
             + ", ".join(c["control"] for c in unmet)))
    if bad:
        print(f"  unconverged cases: {bad}")
    print("  GRADES NO TURBULENCE MODEL AND NO FLUID SOLUTION: both fluids "
          "are boundary conditions.  The coupled interface is T9b.")
    return EXIT_FAIL if (fails or unmet) else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
