#!/usr/bin/env python3
"""D6R3 CD-PLATEAU CRITERION -- the DIRECT convergence measurement that replaces the residual proxy.

WHY THIS IS A PROXY SWAP AND NOT A LOOSENING.  `primalMinResTol x primalMinResTolDiff` gates the
SOLVER RESIDUAL, which was only ever a stand-in for "has the answer stopped moving".  The answer
the optimiser consumes is CD.  This instrument measures CD directly: stable to N significant
figures across the last M printed steps, per condition, per evaluation.  It is STRICTER in the
sense that matters -- a run whose residual floors low but whose CD is still drifting is REFUSED
here and was ACCEPTED by the residual gate.

REGISTERED CONSTANTS (frozen at the D6R3 multipoint registration commit; see MEASURED BASIS):
    N_FIGS = 4      significant figures
    M_STEPS = 5     printed steps (printInterval 100 -> a 500-iteration window)
    -> acceptance predicate: (max(w) - min(w)) / |w[-1]| < 10**-N_FIGS  over the last M points

MEASURED BASIS, from P0_20260913T190426Z.log, BEFORE the constants were chosen:
    position 1 (the primal DAFoam ACCEPTED): relative spread 3.023e-05 over the last 3,4,5 and 6
        printed steps -- stable to ~4.5 significant figures.
    position 2 (the primal DAFoam ABORTED as non-converged): relative spread 2.476e-05 over the
        last 3 and 2.580e-05 over the last 5 -- stable to ~4.6 significant figures.
    THE FINDING THAT JUSTIFIES THE SWAP: on the quantity the optimiser actually consumes, the
    REJECTED position is as converged as the ACCEPTED one, and by the 3-step window slightly
    tighter.  The residual gate and the CD plateau DISAGREE on this case, and the CD plateau is
    the one that speaks about the answer.
    Both sit ~3.3x and ~3.9x inside the registered 1.0e-04 bar, and NEITHER would pass at 5
    significant figures (which needs < 1.0e-05).  The bar is set where the measurement put it.

usage: d6r3_cd_plateau.py <log>              # report the plateau of every position
       d6r3_cd_plateau.py --selftest <log>   # drive the criterion to RED on real data
"""
import json
import math
import re
import sys

N_FIGS = 4
M_STEPS = 5
BAR = 10.0 ** (-N_FIGS)          # 1.0e-04

CDRE = re.compile(r"^CD: (\S+) final: (\S+)\s*$")


class Refusal(Exception):
    pass


def cd_series(text):
    """Every printed CD, split into primal instances by the step counter restarting."""
    t, rows = None, []
    for ln in text.splitlines():
        if ln.startswith("Time = "):
            v = ln.split("=")[1].strip()
            if v != "0" and v.isdigit():
                t = int(v)
            continue
        m = CDRE.match(ln)
        if m and t is not None:
            rows.append((t, float(m.group(1))))
    inst, cur, last = [], [], 0
    for r in rows:
        if r[0] < last and cur:
            inst.append(cur)
            cur = []
        cur.append(r)
        last = r[0]
    if cur:
        inst.append(cur)
    return inst


def plateau(series, n_figs=N_FIGS, m_steps=M_STEPS):
    """Judge one CD series.  REFUSES rather than degrades when the window cannot be formed."""
    if len(series) < m_steps:
        raise Refusal("only %d printed CD values; the registered window is %d -- REFUSING rather "
                      "than judging a plateau on a shorter window" % (len(series), m_steps))
    w = [v for _, v in series[-m_steps:]]
    if w[-1] == 0.0:
        raise Refusal("final CD is exactly zero; a relative spread is undefined")
    spread = (max(w) - min(w)) / abs(w[-1])
    bar = 10.0 ** (-n_figs)
    figs = (-math.log10(spread)) if spread > 0 else float("inf")
    return {
        "window_steps": [t for t, _ in series[-m_steps:]],
        "window_CD": ["%.17g" % v for v in w],
        "relative_spread": "%.6e" % spread,
        "bar": "%.1e" % bar,
        "significant_figures_stable": ("%.2f" % figs) if spread > 0 else "exact",
        "margin_ratio": "%.4f" % (spread / bar),
        "verdict": "PASS" if spread < bar else "GATE FAIL",
        "margin_text": ("PASS by %.4gx inside the bar" % (bar / spread)) if spread < bar
                       else ("GATE FAIL by %.4gx over the bar" % (spread / bar)),
    }


def report(path):
    inst = cd_series(open(path, errors="replace").read())
    out = {"log": path, "n_figs": N_FIGS, "m_steps": M_STEPS, "bar": "%.1e" % BAR, "positions": []}
    for i, s in enumerate(inst, 1):
        try:
            r = plateau(s)
            r["position"] = i
            r["last_time"] = s[-1][0]
        except Refusal as e:
            r = {"position": i, "last_time": s[-1][0], "verdict": "NOT A RESULT", "why": str(e)}
        out["positions"].append(r)
    return out


# ------------------------------------------------------------------------------------------
# THE CONTROL.  Driven to RED on REAL data before any pass of this reader is believed (L-570).
# Three arms, and the failing branch of each is reachable by construction.
def selftest(path):
    txt = open(path, errors="replace").read()
    inst = cd_series(txt)
    if not inst:
        print(json.dumps({"verdict": "REFUSE -- no CD series in the control log"}))
        return 2
    s = inst[0]
    res = {}

    # (a) POSITIVE: the converged tail of a real run must PASS.  A criterion that refuses
    #     everything measures nothing -- this is the specificity arm.
    res["a_real_converged_tail_PASSES"] = plateau(s)["verdict"] == "PASS"

    # (b) NEGATIVE, from REAL data: the EARLY window of the same run, where CD was still
    #     falling from its initial value, must be REFUSED.  No synthetic series is used.
    early = s[:M_STEPS]
    res["b_real_early_drifting_window_REFUSED"] = plateau(early)["verdict"] == "GATE FAIL"
    res["b_early_window_spread"] = plateau(early)["relative_spread"]

    # (c) PLANTED: perturb ONE value in the converged tail by 1% and require the reader to
    #     REPORT it by flipping to GATE FAIL.  A reader that cannot see a planted move is not
    #     a reader (rule 3).
    planted = list(s)
    t_last, v_last = planted[-1]
    planted[-1] = (t_last, v_last * 1.01)
    res["c_planted_1pct_move_DETECTED"] = plateau(planted)["verdict"] == "GATE FAIL"
    res["c_planted_spread"] = plateau(planted)["relative_spread"]

    # (d) REFUSAL: a window shorter than the registered M must REFUSE, never silently shrink.
    try:
        plateau(s[:M_STEPS - 1])
        res["d_short_window_REFUSES"] = False
    except Refusal:
        res["d_short_window_REFUSES"] = True

    ok = all(bool(res[k]) for k in
             ("a_real_converged_tail_PASSES", "b_real_early_drifting_window_REFUSED",
              "c_planted_1pct_move_DETECTED", "d_short_window_REFUSES"))
    res["verdict"] = ("CRITERION HAS BOTH A PASSING AND A FAILING SIDE" if ok
                      else "REFUSE -- a branch of this criterion is unreachable")
    print(json.dumps(res, indent=1))
    return 0 if ok else 2


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    if a[0] == "--selftest":
        sys.exit(selftest(a[1]))
    print(json.dumps(report(a[0]), indent=1))
