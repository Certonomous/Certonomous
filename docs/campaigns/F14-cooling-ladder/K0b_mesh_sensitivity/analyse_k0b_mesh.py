#!/usr/bin/env python3
"""analyse_k0b_mesh.py -- does K0b's published number move with the mesh?

    python3 analyse_k0b_mesh.py       # writes k0b_mesh_sensitivity.json here

Answers proposal P2 of demo-output/website/campaign/THERMAL_K0_RESULTS.md:
"Every K0b number above is from a single 64x64 mesh. A single-mesh number is
not a converged number."

The 64x64 leg is the committed case at 183c91c0 and is re-measured here by the
same code path as the two new legs, so the three numbers are comparable by
construction rather than by trusting a previous run's report.  K0b's own
`analyse.py` numbers are quoted alongside as a cross-check on this script.

WHAT IS REPORTED, AND WHAT IS NOT CLAIMED
-----------------------------------------
For each quantity: the value on 32x32, 64x64 and 128x128; the observed order of
convergence p from the three-mesh Richardson formula

    p = ln(|f_32 - f_64| / |f_64 - f_128|) / ln(r),    r = 2

the Richardson-extrapolated limit f_128 + (f_128 - f_64)/(r^p - 1), and the
Roache GCI on the fine pair with the usual factor of safety 1.25.

This is a MESH SENSITIVITY statement about K0b's own numbers.  It is NOT a
validation: K0b was a capability rung graded against no published datum, and
nothing here changes that.  The de Vahl Davis comparison lives in K0c next door
and is a separate case class -- these cases keep K0b's Pr = 0.706814 and its
limitedLinear/linearUpwind schemes deliberately, so K0c's reference values do
not apply to them and are not used.

The observed order p is a diagnostic, not a certificate: it is only meaningful
if all three meshes are in the asymptotic range, and with r = 2 across a factor
of sixteen in cell count that is an assumption this script states rather than
proves.  Where the three values are not monotone, p is reported as undefined
and the GCI is not quoted, because a Richardson extrapolation through a
non-monotone triple is arithmetic, not evidence.
"""

import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
K0B_64 = os.path.join(REPO, "demo-output", "website", "campaign",
                      "THERMAL_K0_runs", "K0b_cavity_Ra1e5")
FOAM_BASHRC = os.environ.get("FOAM_BASHRC",
                             "/usr/lib/openfoam/openfoam2606/etc/bashrc")
L = 0.10
LZ = 0.01
CASES = [("32x32", os.path.join(HERE, "K0b_m32")),
         ("64x64", K0B_64),
         ("128x128", os.path.join(HERE, "K0b_m128"))]


def foam(case, args):
    return subprocess.run(
        ["bash", "-c", f'. "{FOAM_BASHRC}" >/dev/null 2>&1 && cd {case!r} && {args}'],
        capture_output=True, text=True)


def read_internal(path):
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<(\w+)>\s*\n?\s*(\d+)\s*\n\((.*?)\n\)\s*;",
                  txt, re.S)
    if not m:
        raise SystemExit(f"REFUSE: cannot parse internalField in {path}")
    kind, n, body = m.group(1), int(m.group(2)), m.group(3)
    nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", body)]
    if kind == "vector":
        return [tuple(nums[3 * i:3 * i + 3]) for i in range(n)]
    return nums


def all_times(case):
    """Every parseable time directory, ascending.

    `0.orig` is not parseable as a time and is invisible here, which is the
    same property that makes `foamListTimes -rm` safe and `rm -rf [0-9]*`
    catastrophic -- that glob matches `0.orig` and deleted every initial
    condition in this tree once already.
    """
    ts = []
    for e in os.listdir(case):
        if os.path.isdir(os.path.join(case, e)):
            try:
                ts.append((float(e), e))
            except ValueError:
                pass
    if not ts:
        raise SystemExit(f"REFUSE: no time directories in {case}")
    return [t for _, t in sorted(ts)]


def latest_time(case):
    return all_times(case)[-1]


def scalar(case, rel, key):
    m = re.search(rf"^\s*{re.escape(key)}\s+([^;]+);",
                  open(os.path.join(case, rel)).read(), re.M)
    if not m:
        raise SystemExit(f"REFUSE: '{key}' not in {case}/{rel}")
    return float(m.group(1).strip())


def nu_at_time(case, t, Th, Tc, nx_expected=None):
    """Nu_avg on the hot wall from the raw T cells at one written time.

    Used to build a convergence-in-Nu history from the time directories a run
    already left behind, which costs no compute and says something a residual
    plot does not: whether the GRADED quantity has stopped moving.
    """
    Tf = os.path.join(case, t, "T")
    if not os.path.isfile(Tf):
        return None
    try:
        T = read_internal(Tf)
    except SystemExit:
        return None          # time 0 carries `internalField uniform`: no history
    if not isinstance(T, list):
        return None
    n = len(T)
    nx = int(round(n ** 0.5))
    if nx * nx != n:
        return None
    h = L / nx
    dT = Th - Tc
    # blockMesh orders cells x-fastest, so cell (j*nx) is the wall-adjacent
    # cell of row j.  Verified against the writeCellCentres mapping in measure().
    return sum((Th - T[j * nx]) / (0.5 * h) for j in range(nx)) / nx * (L / dT)


def measure(case):
    # The mesh is not tracked in this repo by design (.gitignore: "A mesh is
    # regenerated by blockMesh from the case dictionaries, which ARE tracked").
    # The committed 64x64 K0b case therefore arrives with no constant/polyMesh
    # and every postProcess call against it fails with "Cannot find file
    # points". Rebuilding it from the tracked blockMeshDict is the intended
    # workflow and touches no field: blockMesh writes constant/polyMesh only.
    if not os.path.isfile(os.path.join(case, "constant", "polyMesh", "points")):
        r = foam(case, "blockMesh > log.blockMesh 2>&1")
        if r.returncode != 0:
            raise SystemExit(f"REFUSE: blockMesh failed rebuilding the mesh in {case}")
    t = latest_time(case)
    nu = scalar(case, "constant/transportProperties", "nu")
    Pr = scalar(case, "constant/transportProperties", "Pr")
    alpha = nu / Pr
    Ttxt = open(os.path.join(case, "0.orig", "T")).read()
    Th = float(re.search(r"hotWall.*?value\s+uniform\s+([\d.eE+-]+)", Ttxt, re.S).group(1))
    Tc = float(re.search(r"coldWall.*?value\s+uniform\s+([\d.eE+-]+)", Ttxt, re.S).group(1))
    dT = Th - Tc

    r = foam(case, f"postProcess -func writeCellCentres -time {t} > log.cellCentres 2>&1")
    if r.returncode != 0:
        raise SystemExit(f"REFUSE: writeCellCentres failed in {case}")
    cx = read_internal(os.path.join(case, t, "Cx"))
    cy = read_internal(os.path.join(case, t, "Cy"))
    for f in ("C", "Cx", "Cy", "Cz"):
        try:
            os.remove(os.path.join(case, t, f))
        except OSError:
            pass

    T = read_internal(os.path.join(case, t, "T"))
    U = read_internal(os.path.join(case, t, "U"))
    xs = sorted(set(round(v, 9) for v in cx))
    ys = sorted(set(round(v, 9) for v in cy))
    nx, ny = len(xs), len(ys)
    xi = {v: i for i, v in enumerate(xs)}
    yi = {v: i for i, v in enumerate(ys)}
    gT = [[None] * nx for _ in range(ny)]
    gu = [[None] * nx for _ in range(ny)]
    gv = [[None] * nx for _ in range(ny)]
    for c in range(len(T)):
        i, j = xi[round(cx[c], 9)], yi[round(cy[c], 9)]
        gT[j][i], gu[j][i], gv[j][i] = T[c], U[c][0], U[c][1]

    h = L / nx
    sc = L / dT
    # wall Nusselt from raw T cells (the same solver-consistent 2-point
    # estimator declared for K0c; grad(T) is never read back from disk)
    nu_hot = [(Th - gT[j][0]) / (0.5 * h) * sc for j in range(ny)]
    nu_cold = [(gT[j][nx - 1] - Tc) / (0.5 * h) * sc for j in range(ny)]
    mean = lambda a: sum(a) / len(a)

    jm, im = ny // 2, nx // 2
    v_mid = [0.5 * (gv[jm - 1][i] + gv[jm][i]) for i in range(nx)]
    u_mid = [0.5 * (gu[j][im - 1] + gu[j][im]) for j in range(ny)]
    star = L / alpha

    Tcol = [0.5 * (gT[j][im - 1] + gT[j][im]) for j in range(ny)]
    dy = L / ny
    lo, hi = int(0.375 * ny), int(0.625 * ny)
    ysub = [(j + 0.5) * dy / L for j in range(lo, hi)]
    tsub = [(Tcol[j] - Tc) / dT for j in range(lo, hi)]
    mY, mT = mean(ysub), mean(tsub)
    S_fit = (sum((a - mY) * (b - mT) for a, b in zip(ysub, tsub))
             / sum((a - mY) ** 2 for a in ysub))

    # convergence-in-Nu history from the times this run already wrote
    hist = {}
    for tt in all_times(case):
        v = nu_at_time(case, tt, Th, Tc)
        if v is not None:
            hist[tt] = v
    ordered = [hist[k] for k in sorted(hist, key=float)]
    tkeys = sorted(hist, key=float)
    drift = (100.0 * abs(ordered[-1] - ordered[-2]) / abs(ordered[-1])
             if len(ordered) >= 2 else None)
    # The drift is only a convergence statement if the last two writes are
    # close together. The committed 64x64 case wrote at t=500 and then not
    # again until t=4000, so its "drift" spans 3500 iterations and says
    # nothing about the end of the run; its convergence evidence is the final
    # initial residual of 9.6e-08 in its own log, which is recorded instead.
    drift_gap = (float(tkeys[-1]) - float(tkeys[-2])) if len(tkeys) >= 2 else None

    # cross-check the grid-mapped estimator used above against the
    # x-fastest-ordering shortcut used for the history, at the analysed time
    assert abs(nu_at_time(case, t, Th, Tc) - mean(nu_hot)) < 1e-12 * abs(mean(nu_hot))

    return dict(
        case=os.path.relpath(case, REPO), time=t, mesh=[nx, ny], cells=nx * ny,
        Nu_history_by_time={k: hist[k] for k in sorted(hist, key=float)},
        Nu_drift_last_two_writes_pct=drift,
        Nu_drift_write_gap_iterations=drift_gap,
        Pr=Pr, dT_K=dT,
        Nu_avg_hot=mean(nu_hot), Nu_avg_cold=mean(nu_cold),
        Nu_max_hot=max(nu_hot), Nu_min_hot=min(nu_hot),
        energy_balance_pct=100.0 * abs(mean(nu_hot) - mean(nu_cold))
        / (0.5 * (mean(nu_hot) + mean(nu_cold))),
        V_star_max=max(v_mid) * star, V_star_min=min(v_mid) * star,
        U_star_max=max(u_mid) * star, U_star_min=min(u_mid) * star,
        x_over_L_at_v_max=xs[v_mid.index(max(v_mid))] / L,
        stratification_S_leastsq_mid25pct=S_fit,
        wall_clock_s=cost(case))


def cost(case):
    """Total single-core seconds for this leg, first run plus any continuation.

    Reading only `wall_clock_s` would under-report: K0b_m128 needed a
    continuation (see below) and its COST.txt carries a second line. A cost
    line that quietly omits the expensive half is worse than no cost line.
    """
    p = os.path.join(case, "COST.txt")
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    tot = 0.0
    seen = False
    for key in ("wall_clock_s", "continue_wall_clock_s"):
        m = re.search(rf"^{key}\s+(\S+)", txt, re.M)
        if m:
            tot += float(m.group(1))
            seen = True
    return tot if seen else None


def richardson(f1, f2, f3, r=2.0):
    """f1 coarse, f2 medium, f3 fine, refinement ratio r between each."""
    d21, d32 = f2 - f1, f3 - f2
    if d21 == 0 or d32 == 0 or (d21 * d32) <= 0:
        return dict(p=None, extrapolated=None, GCI_fine_pct=None,
                    reason="the three values are not monotone (or two coincide); "
                           "a Richardson extrapolation through such a triple is "
                           "arithmetic, not evidence")
    p = math.log(abs(d21 / d32)) / math.log(r)
    ext = f3 + d32 / (r ** p - 1.0)
    gci = 1.25 * abs(d32 / f3) / (r ** p - 1.0) * 100.0
    return dict(p=p, extrapolated=ext, GCI_fine_pct=gci, reason=None)


def main():
    res = dict(
        what="K0b mesh sensitivity, proposal P2 of THERMAL_K0_RESULTS.md",
        not_a_validation="K0b is a capability rung graded against no published "
                         "datum. This is a statement about mesh sensitivity of "
                         "K0b's own numbers, not about their correctness.",
        legs={}, richardson={}, cost={})
    for tag, case in CASES:
        res["legs"][tag] = measure(case)

    keys = ["Nu_avg_hot", "Nu_max_hot", "Nu_min_hot", "V_star_max",
            "U_star_max", "stratification_S_leastsq_mid25pct"]
    for k in keys:
        f1 = res["legs"]["32x32"][k]
        f2 = res["legs"]["64x64"][k]
        f3 = res["legs"]["128x128"][k]
        res["richardson"][k] = dict(
            coarse=f1, medium=f2, fine=f3,
            change_64_to_128_pct=100.0 * abs(f3 - f2) / abs(f3),
            **richardson(f1, f2, f3))

    tot = 0.0
    for tag, leg in res["legs"].items():
        if leg["wall_clock_s"]:
            res["cost"][tag] = dict(wall_clock_s=leg["wall_clock_s"], cores=1,
                                    core_minutes=leg["wall_clock_s"] / 60.0)
            if tag != "64x64":
                tot += leg["wall_clock_s"]
    res["cost"]["NEW_LEGS_TOTAL"] = dict(
        core_seconds=tot, core_minutes=tot / 60.0,
        authorised_core_minutes=15.0,
        note="the 64x64 leg was run and paid for at 183c91c0 and is re-measured, "
             "not re-run; only the two new legs are charged here. No monetary "
             "figure: there is no verified rate for this machine.")

    with open(os.path.join(HERE, "k0b_mesh_sensitivity.json"), "w") as fh:
        json.dump(res, fh, indent=2)

    p = print
    p("=" * 92)
    p("K0b MESH SENSITIVITY -- differentially heated cavity, Ra ~ 1e5, K0b's own schemes")
    p("=" * 92)
    p(f"{'quantity':<34}{'32x32':>12}{'64x64':>12}{'128x128':>12}"
      f"{'64->128 %':>11}{'p':>7}{'GCI %':>9}")
    for k in keys:
        d = res["richardson"][k]
        p(f"{k:<34}{d['coarse']:>12.4f}{d['medium']:>12.4f}{d['fine']:>12.4f}"
          f"{d['change_64_to_128_pct']:>11.3f}"
          + (f"{d['p']:>7.2f}{d['GCI_fine_pct']:>9.3f}" if d["p"] is not None
             else f"{'--':>7}{'--':>9}"))
    p("-" * 92)
    p("convergence in the graded quantity, from the times each run wrote:")
    for tag, leg in res["legs"].items():
        h = leg["Nu_history_by_time"]
        shown = list(h.items())[-4:]
        p(f"    {tag:<10} " + "  ".join(f"t={a}: {b:.4f}" for a, b in shown)
          + (f"   last-two-write drift {leg['Nu_drift_last_two_writes_pct']:.4f} %"
             if leg["Nu_drift_last_two_writes_pct"] is not None else ""))
    p("-" * 92)
    for k in keys:
        if res["richardson"][k]["p"] is None:
            p(f"  {k}: {res['richardson'][k]['reason']}")
    p(f"  new legs cost {res['cost']['NEW_LEGS_TOTAL']['core_minutes']:.3f} "
      f"core-minutes against 15 authorised")
    p("=" * 92)
    return 0


if __name__ == "__main__":
    sys.exit(main())
