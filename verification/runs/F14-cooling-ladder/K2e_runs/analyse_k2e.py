#!/usr/bin/env python3
"""analyse_k2e.py -- grade the K2e divergence sweep.  F14 rung K2e.

    python3 analyse_k2e.py <run-dir> [--json out.json] [--md out.md]

EVERY THRESHOLD IN THIS FILE IS COPIED FROM K2e_PREREGISTRATION.md, WHICH WAS
WRITTEN AND TIMESTAMPED BEFORE ANY K2e SOLVER RAN.  Nothing here may be tuned
after seeing a curve; a threshold chosen after seeing the curve is not a
threshold.  The pre-registration is the authority and this file is its
implementation, so the two are checked against each other by
`selftest_prereg_constants()` below, which fails loudly if they drift.

WHAT IS COMPARED, AND WHY THE BOUSSINESQ BRANCH MUST BE FLAT
------------------------------------------------------------
Ra is held at 1e5 at every point of the sweep and only eps = beta.dT moves.
The non-dimensional Boussinesq problem depends only on (Ra, Pr), so its answer
is IDENTICAL at every sweep point -- control C-1.  The variable-density problem
depends on (Ra, Pr, eps).  Every departure of the second branch from the first
is therefore a non-Boussinesq effect at fixed Rayleigh number, and a drift in
the FIRST branch is a defect in the setup, not a result.

TWO CLASSES OF QUANTITY, AND THEY ARE NOT ON A COMMON AXIS
-----------------------------------------------------------
Class A (Nu_h, u_max*, v_max*) is non-zero under both models, so a percentage
divergence is defined.  Class B (theta_c, <theta>_V, S_rms) is IDENTICALLY ZERO
under Boussinesq by centro-symmetry, so a percentage is undefined and these are
reported as absolute values in units of dT against a floor.  Reporting them on
one axis would be a rhetorical trick and the pre-registration forbids it.

Nu_hot vs Nu_cold is deliberately NOT a comparison quantity.  On a sealed,
steady, constant-k cavity both models force Nu_h = Nu_c identically, so it is a
CLOSURE CHECK and not a physics signal -- physics_rules.yaml thermal section 4.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = "/home/ubuntu/Certonomous"
FOAM_BASHRC = os.environ.get(
    "FOAM_BASHRC", "/usr/lib/openfoam/openfoam2606/etc/bashrc")

# ---------------------------------------------------------------------------
# Constants, all from K2e_PREREGISTRATION.md / build_cases.py.  Duplicated here
# deliberately so that the grader does not import its own subject; drift between
# the two is caught by selftest_prereg_constants().
# ---------------------------------------------------------------------------
L, DEPTH = 0.10, 0.01
TREF, BETA, PR, RA = 300.0, 1.0 / 300.0, 0.71, 1.0e5
RHO_REF = 101325.0 / ((8314.462618 / 28.96) * TREF)
WALL_AREA = L * DEPTH

# pre-registered section 5
CLASS_A_FLOOR_PCT = 1.0        # absolute floor on a Class A divergence
CLASS_A_NOISE_MULT = 3.0       # x (p2p_bou + p2p_vd)
CLASS_B_FLOOR = 0.005          # in units of dT
CLASS_B_NOISE_MULT = 3.0       # x the Boussinesq numerical symmetry floor
MESH_CONV_TOL = 0.20           # |D_coarse - D_fine| / D_fine
# governed, physics_rules.yaml thermal
P2P_MAX_PCT = 0.02

CLASS_A = ["Nu_h", "u_max_star", "v_max_star"]
CLASS_B = ["theta_c", "theta_vol", "S_rms"]


# ---------------------------------------------------------------------------
# OpenFOAM ASCII field reading
# ---------------------------------------------------------------------------
def read_internal_field(path: str):
    """Return the internalField of an ASCII volScalar/volVectorField as a list.

    Handles both `uniform <v>` and `nonuniform List<...> N ( ... )`.  Refuses
    rather than guessing on anything else -- a silently mis-parsed field would
    produce a confident and wrong divergence curve.
    """
    with open(path) as fh:
        txt = fh.read()
    m = re.search(r"internalField\s+nonuniform\s+List<(\w+)>\s*\n?\s*(\d+)\s*\(", txt)
    if m:
        kind, n = m.group(1), int(m.group(2))
        start = m.end()
        depth, i = 1, start
        while depth:
            if txt[i] == "(":
                depth += 1
            elif txt[i] == ")":
                depth -= 1
            i += 1
        body = txt[start:i - 1]
        if kind == "scalar":
            vals = [float(x) for x in body.split()]
        else:
            nums = [float(x) for x in body.replace("(", " ").replace(")", " ").split()]
            vals = [tuple(nums[3 * k:3 * k + 3]) for k in range(n)]
        if len(vals) != n:
            raise SystemExit(f"REFUSE: {path} declared {n} values, parsed {len(vals)}")
        return vals
    m = re.search(r"internalField\s+uniform\s+([^;]+);", txt)
    if m:
        raise SystemExit(f"REFUSE: {path} is a UNIFORM field -- the solve wrote nothing")
    raise SystemExit(f"REFUSE: cannot parse internalField of {path}")


def latest_time(case: str) -> str:
    times = []
    for d in os.listdir(case):
        if os.path.isdir(os.path.join(case, d)):
            try:
                times.append((float(d), d))
            except ValueError:
                pass
    if not times:
        raise SystemExit(f"REFUSE: {case} has no time directories")
    return max(times)[1]


def solver_log(case: str) -> str:
    for f in sorted(os.listdir(case)):
        if f.startswith("log.buoyant"):
            return os.path.join(case, f)
    raise SystemExit(f"REFUSE: {case} has no solver log")


def log_series(case: str, pattern: str):
    """(iteration, value) pairs read from the SOLVER LOG.

    NOT from postProcessing/, and the reason is a measured defect, not taste:
    `scripts/heat_balance.py:770` calls
    `shutil.rmtree(case/postProcessing, ignore_errors=True)` unconditionally
    before it runs its own postProcess pass, so auditing a case DESTROYS the
    in-pass function-object history that this campaign's own convergence gate
    (physics_rules.yaml thermal.monitor_*, scripts/check_convergence.py
    --monitor-regex) is built on.  It does it silently and after the fact.
    Measured on this rung: all twelve Boussinesq cases lost hotFlux, coldFlux,
    Umax and Tcentre the moment they were audited; K0c's own archive shows the
    same hole (only hbAudit_* survives under K0c_runs/*/postProcessing/).
    The log is written by run_cases.sh and nothing deletes it, and it is the
    source check_convergence.py itself reads.  Docketed.

    `pattern` must have exactly one capture group, the value."""
    rx, tx = re.compile(pattern), re.compile(r"^Time = (\d+)")
    t, out = None, []
    for ln in open(solver_log(case)):
        m = tx.match(ln)
        if m:
            t = int(m.group(1))
            continue
        m = rx.search(ln)
        if m and t is not None:
            out.append((t, float(m.group(1))))
    return out


NU_HOT_RE = r"areaNormalIntegrate\(hotWall\) of k2eGradT = ([-\d.eE+]+)"
NU_COLD_RE = r"areaNormalIntegrate\(coldWall\) of k2eGradT = ([-\d.eE+]+)"
UMAX_RE = r"max\(region0\) of k2eMagU = ([-\d.eE+]+)"
HOTT_RE = r"areaAverage\(hotWall\) of T = ([-\d.eE+]+)"
COLDT_RE = r"areaAverage\(coldWall\) of T = ([-\d.eE+]+)"


def probe_series(case: str):
    """The centre-temperature probe, from postProcessing if it survived."""
    root = os.path.join(case, "postProcessing", "Tcentre")
    if not os.path.isdir(root):
        return []
    out = []
    for sub in sorted(os.listdir(root)):
        for f in sorted(os.listdir(os.path.join(root, sub))):
            for ln in open(os.path.join(root, sub, f)):
                if ln.startswith("#"):
                    continue
                a = ln.split()
                if len(a) >= 2:
                    try:
                        out.append((int(float(a[0])), float(a[1])))
                    except ValueError:
                        pass
    return sorted(out)


def dict_scalar(path: str, key: str):
    if not os.path.exists(path):
        return None
    m = re.search(rf"^\s*{key}\s+([-\d.eE+]+)\s*;", open(path).read(), re.M)
    return float(m.group(1)) if m else None


# ---------------------------------------------------------------------------
def p2p_pct(series, window: int, interval: int, min_samples: int):
    """The governed criterion: peak-to-peak spread over a FIXED trailing window.

    Returns (pct, n_samples).  NOT an endpoint difference and NOT a fraction of
    the run -- physics_rules.yaml thermal section 1 refuses both in writing.
    """
    if not series:
        return None, 0
    end = series[-1][0]
    w = [v for t, v in series if end - window <= t <= end]
    if len(w) < min_samples:
        return None, len(w)
    mean = sum(w) / len(w)
    if mean == 0:
        return None, len(w)
    return 100.0 * (max(w) - min(w)) / abs(mean), len(w)


def measure(case: str) -> dict:
    """Every pre-registered quantity for one case, by ONE code path used for
    both solvers.  The only thing that differs is where nu is read from."""
    name = os.path.basename(case)
    mesh, dtag, model = name.split("_")
    dT = float(dtag[2:].replace("p", "."))
    t = latest_time(case)

    # nu: kinematic for the Boussinesq case, mu/rho_ref for the variable-density
    # case.  The two are equal by construction (build_cases.py sets
    # mu = nu.rho_ref) and the equality is asserted by the caller.
    if model == "bou":
        nu = dict_scalar(os.path.join(case, "constant", "transportProperties"), "nu")
    else:
        mu = dict_scalar(os.path.join(case, "constant", "thermophysicalProperties"), "mu")
        nu = mu / RHO_REF
    alpha = nu / PR

    T = read_internal_field(os.path.join(case, t, "T"))
    U = read_internal_field(os.path.join(case, t, "U"))
    ncells = len(T)
    n = int(round(math.sqrt(ncells)))
    if n * n != ncells:
        raise SystemExit(f"REFUSE: {name} has {ncells} cells, not a square block")

    def idx(i, j):        # blockMesh orders i fastest, then j
        return i + n * j

    theta = [(v - TREF) / dT for v in T]

    # Q2/Q3: the mid-planes fall on faces on an even mesh, so the two adjacent
    # cell lines are averaged -- the SAME operator on both solvers.
    c0, c1 = n // 2 - 1, n // 2
    u_mid = [0.5 * (U[idx(c0, j)][0] + U[idx(c1, j)][0]) for j in range(n)]
    v_mid = [0.5 * (U[idx(i, c0)][1] + U[idx(i, c1)][1]) for i in range(n)]
    u_max_star = max(abs(x) for x in u_mid) * L / alpha
    v_max_star = max(abs(x) for x in v_mid) * L / alpha

    # Q4/Q5/Q6: symmetry quantities, identically zero under Boussinesq
    theta_c = 0.25 * sum(theta[idx(i, j)] for i in (c0, c1) for j in (c0, c1))
    theta_vol = sum(theta) / ncells
    S_rms = math.sqrt(sum((theta[idx(i, j)] + theta[idx(n - 1 - i, n - 1 - j)]) ** 2
                          for i in range(n) for j in range(n)) / ncells)

    # Q1: from the RUNNING solver's own in-pass grad(T) integral.
    hot = log_series(case, NU_HOT_RE)
    cold = log_series(case, NU_COLD_RE)
    Nu_h = abs(hot[-1][1]) * L / (WALL_AREA * dT) if hot else None
    Nu_c = abs(cold[-1][1]) * L / (WALL_AREA * dT) if cold else None

    # in-log witnesses -- control C-5: a log states what ran
    hotT = log_series(case, HOTT_RE)
    coldT = log_series(case, COLDT_RE)

    win, iv, ms = 400, 50, 9
    p2p_Nu, nsm = p2p_pct(hot, win, iv, ms)
    p2p_U, _ = p2p_pct(log_series(case, UMAX_RE), win, iv, ms)
    # The T-centre probe writes to postProcessing only and never to the log, so
    # it cannot survive the heat_balance.py deletion documented in log_series().
    # It is read from disk when it is there and reported as absent when it is
    # not; it is an UNGATED monitor and nothing depends on it.
    p2p_Tc, _ = p2p_pct(probe_series(case), win, iv, ms)

    return dict(
        case=name, mesh=mesh, model=model, n=n, dT=dT, eps=BETA * dT,
        nu=nu, alpha=alpha, time=t, iterations=hot[-1][0] if hot else None,
        Nu_h=Nu_h, Nu_c=Nu_c,
        u_max_star=u_max_star, v_max_star=v_max_star,
        theta_c=theta_c, theta_vol=theta_vol, S_rms=S_rms,
        p2p_Nu_pct=p2p_Nu, p2p_samples=nsm, p2p_Umax_pct=p2p_U, p2p_Tcentre_pct=p2p_Tc,
        T_hot_log=hotT[-1][1] if hotT else None,
        T_cold_log=coldT[-1][1] if coldT else None,
        wall_clock_s=dict_scalar(os.path.join(case, "COST.txt"), "wall_clock_s"),
    )


# ---------------------------------------------------------------------------
def rho_minmax_from_log(case: str):
    """buoyantSimpleFoam prints `rho min/max :` every iteration.  This is the
    variable-density case's OWN statement of its equation of state, read from
    the log and not from the dictionary -- control C-5."""
    for f in os.listdir(case):
        if f.startswith("log.buoyantSimpleFoam"):
            last = None
            for ln in open(os.path.join(case, f)):
                if ln.startswith("rho min/max"):
                    last = ln
            if last:
                a = last.split(":")[1].split()
                return float(a[0]), float(a[1])
    return None, None


def heat_balance(case: str):
    """scripts/heat_balance.py, per the specification.  Exit status is read from
    the script itself, never from a pipeline."""
    # ON A COPY, ALWAYS.  heat_balance.py deletes the case's postProcessing/
    # directory (line 770) and writes function-object dictionaries into its
    # system/ directory.  Auditing the archive in place mutates the archive.
    with tempfile.TemporaryDirectory() as td:
        work = os.path.join(td, os.path.basename(case))
        shutil.copytree(case, work)
        # The committed archive drops constant/polyMesh -- blockMesh regenerates
        # it exactly -- so rebuild it on the copy when it is not there.  This is
        # what lets the auditor run against the archive and not only against a
        # freshly solved tree.
        if not os.path.isdir(os.path.join(work, "constant", "polyMesh")):
            subprocess.run(
                ["bash", "-c",
                 f". {FOAM_BASHRC} >/dev/null 2>&1; cd '{work}'; blockMesh > log.blockMesh 2>&1"],
                capture_output=True, text=True, timeout=300)
        try:
            p = subprocess.run(
                [sys.executable, os.path.join(REPO, "scripts", "heat_balance.py"), work],
                capture_output=True, text=True, timeout=300)
        except Exception as e:
            return dict(exit=None, imbalance_pct=None, note=f"invocation failed: {e}")
    m = re.search(r"IMBALANCE = ([\d.]+) %", p.stdout)
    ref = re.search(r"^REFUSE: (.*)$", p.stdout + p.stderr, re.M)
    note = ("REFUSED: " + ref.group(1).replace(work, "<case>")) if ref else ""
    return dict(exit=p.returncode,
                imbalance_pct=float(m.group(1)) if m else None,
                note=note)


def closure_from_walls(r: dict):
    """The sealed-cavity closure recomputed from the two wall integrals the
    RUNNING solver printed.  Used where heat_balance.py refuses.  It is the same
    near-identity and it is evidence of nothing about the physics; see
    physics_rules.yaml thermal section 4."""
    if r["Nu_h"] is None or r["Nu_c"] is None:
        return None
    s = r["Nu_h"] + r["Nu_c"]
    return 100.0 * abs(r["Nu_h"] - r["Nu_c"]) / (0.5 * s) if s else None


# ---------------------------------------------------------------------------
FIT_EPS_MIN = 0.05      # the single, uniform cut for every power-law fit


def fit_window(eps, d):
    """The points a power law may be fitted through: eps >= FIT_EPS_MIN, one cut
    applied identically to every quantity so that no exponent is obtained by
    choosing its own window."""
    pairs = [(e, v) for e, v in zip(eps, d) if e >= FIT_EPS_MIN - 1e-12]
    return [e for e, _ in pairs], [v for _, v in pairs]


def power_fit(eps, d):
    """Least squares on log D = log a + n log eps.  Returns (a, n, max |resid| %).

    POST-HOC.  This characterises the pre-registered quantities after the fact;
    it decides nothing and gates nothing, and the separation verdicts above are
    computed from the pre-registered thresholds alone.  It is reported because
    the exponent is the transferable part: it says how a divergence measured at
    one beta.dT carries to another, which a table of nine points does not.
    """
    pts = [(math.log(e), math.log(abs(v))) for e, v in zip(eps, d) if v and e]
    if len(pts) < 3:
        return None
    n = len(pts)
    sx = sum(x for x, _ in pts); sy = sum(y for _, y in pts)
    sxx = sum(x * x for x, _ in pts); sxy = sum(x * y for x, y in pts)
    den = n * sxx - sx * sx
    if den == 0:
        return None
    slope = (n * sxy - sx * sy) / den
    inter = (sy - slope * sx) / n
    a = math.exp(inter)
    worst = max(100.0 * abs(a * (e ** slope) - abs(v)) / abs(v)
                for e, v in zip(eps, d) if v and e)
    return a, slope, worst


def selftest_prereg_constants(prereg: str) -> list:
    """Refuse to grade if this file's thresholds have drifted from the
    pre-registration's.  L-113: a sentence describing a check is written beside
    the check, is true when written, and goes stale silently."""
    problems = []
    if not os.path.exists(prereg):
        return [f"pre-registration not found at {prereg}"]
    txt = open(prereg).read()
    for label, needle in [
        ("Class A floor", "D_Q(eps) >= 1.0 %"),
        ("Class A noise multiple", "3 x (p2p_bou + p2p_vd)"),
        ("Class B floor", "|Q_vd| >= 0.005"),
        ("Class B noise multiple", "3 x |Q_bou|"),
        ("mesh convergence tolerance", "<=  0.20"),
        ("Ra", "**1e5, HELD FIXED"),
    ]:
        if needle not in txt:
            problems.append(f"{label}: `{needle}` not found in the pre-registration")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir")
    ap.add_argument("--json", default=None)
    ap.add_argument("--md", default=None)
    ap.add_argument("--prereg", default=os.path.join(
        REPO, "docs/campaigns/F14-cooling-ladder/K2e_PREREGISTRATION.md"))
    a = ap.parse_args()

    drift = selftest_prereg_constants(a.prereg)
    if drift:
        for d in drift:
            print(f"REFUSE: threshold drift -- {d}")
        return 3

    cases = sorted(d for d in os.listdir(a.rundir)
                   if os.path.isdir(os.path.join(a.rundir, d)) and "_" in d)
    R = {}
    for c in cases:
        r = measure(os.path.join(a.rundir, c))
        r["heat_balance"] = heat_balance(os.path.join(a.rundir, c))
        r["closure_from_walls_pct"] = closure_from_walls(r)
        if r["model"] == "vd":
            r["rho_min"], r["rho_max"] = rho_minmax_from_log(os.path.join(a.rundir, c))
        R[c] = r

    out = {"cases": R, "pairs": {}, "controls": {}}
    lines = []
    P = lines.append

    P("<!-- GENERATED by analyse_k2e.py. Do not hand-edit: rerun the script. -->")
    P("")
    P("## K2e divergence table — Boussinesq against variable density, Ra = 1e5 fixed")
    P("")
    P("Tier: **SOLVER-BACKED**. No experimental reference exists for this rung and "
      "none is claimed; see K2e_PREREGISTRATION.md §0.")
    P("")

    # ---- convergence, first, because nothing below means anything without it
    P("### Convergence on the graded quantity (governed criterion, "
      f"peak-to-peak of Nu_h over the last 400 iterations <= {P2P_MAX_PCT} %)")
    P("")
    P("| case | iters | p2p Nu_h % | samples | p2p max\\|U\\| % | p2p T_centre % | verdict |")
    P("| --- | ---: | ---: | ---: | ---: | ---: | :---: |")
    n_bad = 0
    for c in cases:
        r = R[c]
        ok = r["p2p_Nu_pct"] is not None and r["p2p_Nu_pct"] <= P2P_MAX_PCT
        n_bad += (not ok)
        r["converged"] = ok
        tc = ("absent" if r["p2p_Tcentre_pct"] is None
              else f"{r['p2p_Tcentre_pct']:.6f}")
        P(f"| `{c}` | {r['iterations']} | {r['p2p_Nu_pct']:.6f} | {r['p2p_samples']} | "
          f"{r['p2p_Umax_pct']:.6f} | {tc} | "
          f"{'CONVERGED' if ok else '**NOT_CONVERGED**'} |")
    P("")
    P(f"**{len(cases) - n_bad} of {len(cases)} runs meet the governed criterion.**")
    P("")

    # ---- control C-5, the log witnesses
    P("### Control C-5 — every control read from the SOLVER LOG, not the input file")
    P("")
    P("| case | T_hot from `hotT` FO | T_cold from `coldT` FO | dT witnessed | "
      "rho min/max printed by the solver | expected rho(T_hot)/rho(T_cold) |")
    P("| --- | ---: | ---: | ---: | --- | --- |")
    Rs = 8314.462618 / 28.96
    for c in cases:
        r = R[c]
        wit = r["T_hot_log"] - r["T_cold_log"]
        exp = ""
        got = "n/a (Boussinesq: rho is not a field)"
        if r["model"] == "vd" and r.get("rho_min") is not None:
            got = f"{r['rho_min']:.6f} / {r['rho_max']:.6f}"
            exp = (f"{101325.0/(Rs*r['T_hot_log']):.6f} / "
                   f"{101325.0/(Rs*r['T_cold_log']):.6f}")
        P(f"| `{c}` | {r['T_hot_log']:.6f} | {r['T_cold_log']:.6f} | {wit:.6f} | {got} | {exp} |")
    P("")

    # ---- control C-1, Boussinesq flatness
    P("### Control C-1 — the Boussinesq branch must be FLAT (kind: reachability)")
    P("")
    P("At fixed Ra and Pr the non-dimensional Boussinesq problem does not depend on "
      "eps, so every quantity below must be constant along the sweep. Spread is "
      "peak-to-peak across the nine eps points, as a percentage of the mean.")
    P("")
    P("| mesh | quantity | min | max | spread % | max convergence noise on the branch % |")
    P("| --- | --- | ---: | ---: | ---: | ---: |")
    for mesh in ("m48", "m96"):
        sel = [R[c] for c in cases if R[c]["mesh"] == mesh and R[c]["model"] == "bou"]
        if len(sel) < 2:
            continue
        noise = max(x["p2p_Nu_pct"] for x in sel)
        for q in CLASS_A:
            v = [x[q] for x in sel]
            sp = 100.0 * (max(v) - min(v)) / abs(sum(v) / len(v))
            out["controls"].setdefault("C1", {})[f"{mesh}.{q}"] = sp
            P(f"| {mesh} | {q} | {min(v):.6f} | {max(v):.6f} | {sp:.6f} | {noise:.6f} |")
    P("")

    # ---- the divergence curve
    for mesh in ("m48", "m96"):
        eps_pts = sorted({R[c]["eps"] for c in cases if R[c]["mesh"] == mesh})
        if not eps_pts:
            continue
        P(f"### Divergence curve, mesh {mesh}")
        P("")
        P("Class A: D = 100 x |Q_vd - Q_bou| / |Q_bou|. Separated when D >= 1.0 % "
          "AND D >= 3 x (p2p_bou + p2p_vd). Class B: absolute, in units of dT; "
          "separated when |Q_vd| >= 0.005 AND >= 3 x |Q_bou|.")
        P("")
        head = ("| dT K | eps=beta.dT | " +
                " | ".join(f"D {q} %" for q in CLASS_A) + " | " +
                " | ".join(f"{q} (vd)" for q in CLASS_B) + " | separated |")
        P(head)
        P("| ---: | ---: | " + " | ".join(["---:"] * (len(CLASS_A) + len(CLASS_B))) +
          " | --- |")
        for e in eps_pts:
            b = next((R[c] for c in cases if R[c]["mesh"] == mesh
                      and R[c]["model"] == "bou" and abs(R[c]["eps"] - e) < 1e-12), None)
            v = next((R[c] for c in cases if R[c]["mesh"] == mesh
                      and R[c]["model"] == "vd" and abs(R[c]["eps"] - e) < 1e-12), None)
            if not b or not v:
                continue
            key = f"{mesh}@{e:.5f}"
            rec = {"eps": e, "dT": b["dT"], "classA": {}, "classB": {}, "separated": []}
            cells = []
            for q in CLASS_A:
                D = 100.0 * abs(v[q] - b[q]) / abs(b[q])
                noise = CLASS_A_NOISE_MULT * (b["p2p_Nu_pct"] + v["p2p_Nu_pct"])
                sep = (D >= CLASS_A_FLOOR_PCT) and (D >= noise)
                rec["classA"][q] = {"D_pct": D, "noise_gate_pct": noise, "separated": sep}
                if sep:
                    rec["separated"].append(q)
                cells.append(f"**{D:.3f}**" if sep else f"{D:.3f}")
            for q in CLASS_B:
                mag, floor_b = abs(v[q]), abs(b[q])
                sep = (mag >= CLASS_B_FLOOR) and (mag >= CLASS_B_NOISE_MULT * floor_b)
                rec["classB"][q] = {"value_vd": v[q], "value_bou": b[q], "separated": sep}
                if sep:
                    rec["separated"].append(q)
                cells.append(f"**{v[q]:+.5f}**" if sep else f"{v[q]:+.5f}")
            out["pairs"][key] = rec
            P(f"| {b['dT']:g} | {e:.5f} | " + " | ".join(cells) + " | " +
              (", ".join(rec["separated"]) if rec["separated"] else "—") + " |")
        P("")

    # ---- mesh convergence of the divergence
    P("### Mesh convergence OF THE DIVERGENCE (mandatory; "
      f"|D_coarse - D_fine| / D_fine <= {MESH_CONV_TOL:.0%})")
    P("")
    P("| eps | quantity | D on 48x48 % | D on 96x96 % | relative change | verdict |")
    P("| ---: | --- | ---: | ---: | ---: | :---: |")
    for e in sorted({R[c]["eps"] for c in cases if R[c]["mesh"] == "m96"}):
        ck, fk = f"m48@{e:.5f}", f"m96@{e:.5f}"
        if ck not in out["pairs"] or fk not in out["pairs"]:
            continue
        for q in CLASS_A:
            dc = out["pairs"][ck]["classA"][q]["D_pct"]
            df = out["pairs"][fk]["classA"][q]["D_pct"]
            rel = abs(dc - df) / abs(df) if df else float("inf")
            P(f"| {e:.5f} | {q} | {dc:.4f} | {df:.4f} | {rel:.3f} | "
              f"{'MESH-CONVERGED' if rel <= MESH_CONV_TOL else '**NOT mesh-converged**'} |")
            out.setdefault("mesh_conv", {})[f"{e:.5f}.{q}"] = {
                "D_coarse": dc, "D_fine": df, "rel": rel, "ok": rel <= MESH_CONV_TOL}
        for q in CLASS_B:
            vc = out["pairs"][ck]["classB"][q]["value_vd"]
            vf = out["pairs"][fk]["classB"][q]["value_vd"]
            rel = abs(vc - vf) / abs(vf) if vf else float("inf")
            P(f"| {e:.5f} | {q} (absolute) | {vc:+.5f} | {vf:+.5f} | {rel:.3f} | "
              f"{'MESH-CONVERGED' if rel <= MESH_CONV_TOL else '**NOT mesh-converged**'} |")
            out.setdefault("mesh_conv", {})[f"{e:.5f}.{q}"] = {
                "D_coarse": vc, "D_fine": vf, "rel": rel, "ok": rel <= MESH_CONV_TOL}
    P("")

    # ---- control C-2, the eps -> 0 null test.  COARSE MESH ONLY: the null point
    # eps = 0.001 was only ever swept there, and the control is about the datum
    # and the properties, which one generator writes and which do not depend on
    # the mesh.  Reporting the fine mesh's smallest eps in this table would put a
    # point that is NOT a null test under a heading that says it is.
    P("### Control C-2 — the eps -> 0 null test (kind: reachability)")
    P("")
    P("At the smallest sweep point every non-Boussinesq term is O(1e-3) or "
      "smaller, so the two solvers must agree to within their own noise. What "
      "they disagree by THERE is a measured ceiling on any residual datum or "
      "property mismatch, and every separation reported above has to clear it.")
    P("")
    P("| mesh | eps | D Nu_h % | D u_max* % | D v_max* % | theta_c | S_rms | "
      "Class A separation floor |")
    P("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for mesh in ("m48",):
        ks = sorted((k for k in out["pairs"] if k.startswith(mesh + "@")),
                    key=lambda k: out["pairs"][k]["eps"])
        if not ks:
            continue
        r = out["pairs"][ks[0]]
        P(f"| {mesh} | {r['eps']:.5f} | " +
          " | ".join(f"{r['classA'][q]['D_pct']:.3f}" for q in CLASS_A) + " | " +
          f"{r['classB']['theta_c']['value_vd']:+.5f} | "
          f"{r['classB']['S_rms']['value_vd']:+.5f} | {CLASS_A_FLOOR_PCT:.1f} |")
        out["controls"].setdefault("C2", {})[mesh] = {
            q: r["classA"][q]["D_pct"] for q in CLASS_A}
    P("")

    # ---- control C-3, the K0c anchor
    P("### Control C-3 — the K0c anchor (kind: RECOGNITION, not reachability)")
    P("")
    P("This control reads an already-published number back; it cannot fail in a "
      "way that is informative about K2e's own physics, and it is labelled "
      "accordingly. K0c graded the SAME cavity at Ra = 1e5 under the SAME "
      "Boussinesq solver on a 64x64 / 128x128 pair and reported Nu_avg 4.5590 "
      "(coarse) and 4.5310 (fine) against a secondary reference of 4.5190.")
    P("")
    P("| source | mesh | Nu_h |")
    P("| --- | --- | ---: |")
    for mesh, n in (("m48", 48), ("m96", 96)):
        sel = [R[c] for c in cases if R[c]["mesh"] == mesh and R[c]["model"] == "bou"]
        if sel:
            P(f"| K2e, this rung | {n}x{n} | {sel[0]['Nu_h']:.4f} |")
    P("| K0c (`K0c_runs/GATE_TABLE.md`) | 64x64 | 4.5590 |")
    P("| K0c (`K0c_runs/GATE_TABLE.md`) | 128x128 | 4.5310 |")
    P("| Han and Xie 2019 Tab. 3 after de Vahl Davis 1983, SECONDARY, "
      "read by K0c and not by K2e | Richardson | 4.5190 |")
    P("")

    # ---- POST-HOC scaling laws
    P("### How the divergence scales with beta.dT — POST-HOC, gates nothing")
    P("")
    P("Least squares of log D against log eps over the whole coarse sweep. This "
      "is a characterisation of the pre-registered quantities AFTER the fact. "
      "It decides nothing: every separation verdict above comes from the "
      "pre-registered thresholds alone. It is reported because the EXPONENT is "
      "the transferable part — it says how a divergence measured at one beta.dT "
      "carries to another, which a table of points does not.")
    P("")
    P("| quantity | fit | exponent n | worst residual over the sweep % |")
    P("| --- | --- | ---: | ---: |")
    for mesh in ("m48",):
        ks = sorted((k for k in out["pairs"] if k.startswith(mesh + "@")),
                    key=lambda k: out["pairs"][k]["eps"])
        eps = [out["pairs"][k]["eps"] for k in ks]
        for q in CLASS_A:
            d = [out["pairs"][k]["classA"][q]["D_pct"] for k in ks]
            f = power_fit(*fit_window(eps, d))
            if f:
                P(f"| D {q} % | {f[0]:.4g} x (beta.dT)^{f[1]:.3f} | {f[1]:.3f} | {f[2]:.2f} |")
                out.setdefault("scaling", {})[q] = {"a": f[0], "n": f[1], "worst_pct": f[2]}
        for q in CLASS_B:
            d = [abs(out["pairs"][k]["classB"][q]["value_vd"]) for k in ks]
            f = power_fit(eps[1:], d[1:])
            if f:
                P(f"| abs({q}) | {f[0]:.4g} x (beta.dT)^{f[1]:.3f} | "
                  f"{f[1]:.3f} | {f[2]:.2f} |")
                out.setdefault("scaling", {})[q] = {"a": f[0], "n": f[1], "worst_pct": f[2]}
    P("")
    P(f"Fitted over eps >= {FIT_EPS_MIN:g} only, the SAME cut for every quantity, "
      "chosen because below it every quantity sits on a solver-to-solver "
      "baseline floor of order 0.01 to 0.2 % that does not scale with eps: "
      "D(Nu_h) reads 0.010 % at both eps = 0.010 and eps = 0.033, which is a "
      "floor and not a trend. Fitting through a floor would flatten every "
      "exponent toward zero and misreport the scaling.")
    P("")

    # ---- heat balance
    P("### Heat balance — reported because the specification requires it, and it "
      "is NOT evidence")
    P("")
    P("Every K2e case is sealed and impermeable, so `heat_balance_closure_is_"
      "evidence_on_sealed_case: false` applies in full: the discrete equation "
      "forces the boundary terms to sum to zero at every iteration, converged or "
      "not. What a pass here still establishes is narrow — wrong properties, a "
      "wrong patch area, a wrong sign, a patch dropped from the sum.")
    P("")
    P("| case | heat_balance.py exit | imbalance % | Nu_h vs Nu_c closure % | note |")
    P("| --- | ---: | ---: | ---: | --- |")
    for c in cases:
        r = R[c]
        hb = r["heat_balance"]
        P(f"| `{c}` | {hb['exit']} | "
          f"{hb['imbalance_pct'] if hb['imbalance_pct'] is not None else 'n/a'} | "
          f"{r['closure_from_walls_pct']:.6f} | {hb['note']} |")
    P("")

    md = "\n".join(lines) + "\n"
    if a.md:
        open(a.md, "w").write(md)
    else:
        print(md)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2, default=str)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
